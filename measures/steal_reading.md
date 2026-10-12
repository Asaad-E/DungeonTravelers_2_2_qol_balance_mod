# Reverse Engineering of Steal (Robo) in Dungeon Travelers 2-2

## Overview & Entry Point

The Steal action is implemented in `Battle::CBattle::_Steal` at `0x44fde0` [code].
It is an entry in the virtual method table of `Battle::CBattle` at `.rdata:0x6c9bb4` [code], alongside `0x44a850` (Physical Attack, "物理攻撃の計算") and `0x44d370` (Spell Attack, "魔法攻撃の計算") [code].
At the beginning of the function, it logs the debug string `'%s : 盗むの計算\n'` (`0x6536b4`) at `0044fe1c` [code].

The action handles two distinct modes based on the effect carried by the active command:
- **Gold Steal**: Activated by Effect 60 (`0x3C`) [code].
- **Item Steal**: Activated by Effect 61 (`0x3D`) [code].

---

## 1. What is Stolen (Item Steal Resolution)

When an Item Steal action succeeds its hit check, the game does **not** read any dedicated "steal" slot [code].
Instead, at `004504bf`, `_Steal` invokes `0x558180`—the exact same function that calculates defeat loot drops—passing argument `[ebp + 0x10] = 1` [code].

### Proving Assembly Instructions
```x86asm
; In Battle::CBattle::_Steal (0x44fde0):
004503bd  mov      eax, dword ptr [eax]              ; [code] eax = EnemyStatusData in memory
004503bf  mov      eax, dword ptr [eax + 0x54]       ; [code] file offset 0x3C (memory 0x54): flags
004503c2  shr      eax, 0xf                          ; [code] shift right 15 bits
004503c5  test     al, 1                             ; [code] test Bit 15 (can_steal flag)
004503c7  je       0x4505d5                          ; [code] if 0, branch: "You can't steal from this monster!" (String 0x5A)
004503cd  cmp      byte ptr [esi + 0x154], 0         ; [code] esi = enemy unit object; check if item already stolen
004503d4  je       0x450438                          ; [code] if 0, not yet stolen -> proceed to success roll check
                                                     ;        if != 0, branch: "Can't steal what isn't there." (String 0x59)
...
; Success branch in _Steal:
004504a9  mov      ecx, dword ptr [ebx + 0x10]
004504ac  push     1                                 ; [code] arg 3: FLAG = 1 (Steal mode!)
004504ae  call     0x4e45d0                          ; [code] get dungeon/floor context
004504b3  push     eax                               ; [code] arg 2: floor context
004504b4  mov      eax, dword ptr [ebp + 0x14]
004504b7  lea      ecx, [ebp + 0x14]                 ; [code] ecx = out_item pointer
004504ba  mov      edx, esi                          ; [code] edx = enemy unit object
004504bc  push     dword ptr [eax + 0x10]            ; [code] arg 1: thief unit
004504bf  call     0x558180                          ; [code] calls loot resolution function with FLAG = 1!
004504c4  add      esp, 0xc
004504c7  test     al, al                            ; [code] check if item was returned
004504c9  je       0x45067e                          ; [code] if al == 0, assertion error ("Battle::CBattle::_Steal error.\n")
00450508  mov      byte ptr [esi + 0x154], 1         ; [code] MARK ITEM AS STOLEN on enemy unit
00450523  mov      dword ptr [ebp + 0x14], 0x54      ; [code] String 0x54: "Stole a %name!"
```

### Inner Logic of `0x558180` when called with `FLAG = 1`
```x86asm
; In 0x558180:
005581d0  cmp      byte ptr [ebp + 0x10], 0          ; [code] check if FLAG == 0 (Drop) or != 0 (Steal)
005581d4  xorps    xmm0, xmm0
005581d7  movss    dword ptr [ebp - 0x18], xmm0      ; [code] equipment drop bonus = 0.0f
005581dc  movss    dword ptr [ebp - 0x1c], xmm0      ; [code] treasure hunt bonus = 0.0f
005581e8  mov      ecx, dword ptr [eax + 0x80]       ; [code] file offset 0x68 (memory 0x80): item_count (0-2)
005581f1  jne      0x55828b                          ; [code] JUMPS TO 0x55828b: SKIPS Treasure Hunt & Enchantment 276!
...
; Stage 1 weight sum and "Nothing" slot handling:
00558383  cmp      ebx, 0x64                         ; [code] ebx = sum of positive item and equipment drop probabilities
00558386  jae      0x558392
00558388  cmp      byte ptr [ebp + 0x10], 0          ; [code] check FLAG
0055838c  mov      byte ptr [ebp + 0x13], 1          ; [code] sets "add nothing slot" flag
00558390  je       0x558396                          ; [code] if FLAG == 0, jump and keep flag = 1
00558392  mov      byte ptr [ebp + 0x13], 0          ; [code] if FLAG != 0 (STEAL), FORCE flag = 0!
...
00558417  cmp      byte ptr [ebp + 0x13], 0
0055841b  je       0x558427                          ; [code] SKIPS ADDING THE "NOTHING" SLOT (100 - ebx)!
0055842c  call     0x505ad0                          ; [code] rolls strictly among the actual candidate drop items/equipment!
```

### Detailed Answers to Questions 1a–1e
- **1a. Fields read**:
  It reads **both** the regular item entries at file offset `0x6C` / `0x74` (chances at `0x70` / `0x78`) and the equipment drop at file offset `0x7C` (with slots from `0x84` onward) [code]. There is no separate "steal item" field in `EnemyStatusData`.
- **1b. Selection mechanism & weights**:
  Stage 1 rolls a weighted selection (`0x505ad0`) among all positive drop probabilities of that enemy: Item 0 (chance `0x70`), Item 1 (chance `0x78`), and Equipment (chance `0x7C`) [code]. Crucially, because `[ebp + 0x13] = 0`, the "nothing" slot (`100 - sum`) is **omitted** [code]. The probabilities of candidate items are simply normalized by their positive sum. If Equipment is picked, Stage 2 rolls a second weighted selection (`0x505ad0`) among the candidate equipment slots using their weights at `0x8C`, `0x98`, `0xA4` [code].
- **1c. Disproving `enemy_data.py`**:
  `tools/enemy_data.py` previously guessed: `"0x84 what can be stolen from it: a flag, an id at 0x88, a chance in percent at 0x8C (the steal code reads 0x84)"`. This is **refuted** [code]. `_Steal` never accesses `0x84`. `0x84` is the type flag of Equipment Slot 0. If an enemy has consumable items at `0x6C`/0x74, Item Steal can steal those consumable items, not just the equipment piece.
- **1d. Zone table pieces (`flag == 1`)**:
  **Yes**, a zone table equipment piece can be stolen [code]. If the Stage 2 roll picks an equipment slot with `flag == 1`, `0x558180` executes `0055862f call 0x555c70` using the floor context passed by `_Steal` (`004504b3`), uniformly picking an eligible piece from the floor's equipment table.
- **1e. Can it fail with "nothing to steal" on the first try?**:
  **No**, for any enemy that is stealable (Bit 15 = 1), `_Steal` cannot roll "nothing" on a successful hit check because the "nothing" slot is bypassed [code], and all 381 stealable enemies in vanilla data have at least one candidate with positive probability [code]. However:
  - If Bit 15 is 0: it immediately branches to `004505d5`, displaying String 0x5A (`"You can't steal from this monster!"`) without rolling [code].
  - If the enemy has already been robbed of an item (`[esi + 0x154] == 1`): it branches to `004503d6`, displaying String 0x59 (`"Can't steal what isn't there."`) [code].
  - If the hit check fails: it branches to `00450441`, displaying String 0x58 (`"Failure!"`) [code].

### One-Sentence Conclusion
When Item Steal succeeds, the game runs the enemy's regular loot drop function (`0x558180`) with the empty "nothing" roll disabled, conducting a weighted lottery exclusively among the enemy's regular items and equipment slots.

---

## 2. Execution Frequency and Independence from Defeat Drops

### Proving Assembly Instructions
```x86asm
; In Battle::CBattle::_Steal (0x44fde0):
; Gold check & flag set:
0045014d  cmp      byte ptr [edi + 0x155], 0         ; [code] checks gold stolen flag on enemy
00450154  jne      0x4502eb                          ; [code] if 1 -> String 0x56 ("Can't steal gold that isn't there.")
...
00450235  mov      byte ptr [edi + 0x155], al        ; [code] al = 1; SETS gold stolen flag ONLY ON SUCCESSFUL STEAL
...
; Item check & flag set:
004503cd  cmp      byte ptr [esi + 0x154], 0         ; [code] checks item stolen flag on enemy
004503d4  je       0x450438                          ; [code] if 0 -> proceeds to roll
...
00450508  mov      byte ptr [esi + 0x154], 1         ; [code] SETS item stolen flag ONLY ON SUCCESSFUL STEAL
```

```x86asm
; In battle victory defeat drop handler (0x43a4a0 / 0x43aab6):
0043aaa3  mov      edx, dword ptr [ebx + 0x14]       ; [code] edx = enemy unit object
0043aaa6  lea      ecx, [ebp + 0x14]
0043aaa9  push     0                                 ; [code] FLAG = 0 (Normal defeat drop mode!)
0043aaab  push     esi                               ; [code] floor context
0043aaac  push     dword ptr [ebp + 0xc]             ; [code] killer unit
0043aab6  call     0x558180                          ; [code] defeat drop roll
```

### Detailed Answers
1. **Where flags are tested and set**:
   - `0x154` (item) and `0x155` (gold) are bytes stored at offsets `0x154` and `0x155` of the active combat unit structure [code].
   - They are tested at `004503cd` and `0045014d` [code].
   - They are set to `1` at `00450508` and `00450235` **strictly upon success** [code].
   - If a steal attempt fails the probability roll (`00450438` or `00450183`), the flags are **not set** [code], allowing future attempts in subsequent turns.
2. **Independence from Defeat Drops**:
   The defeat drop routine (`0x43aab6`) passes `FLAG = 0` to `0x558180` and **never inspects `0x154` or `0x155`** [code].
   Furthermore, `0x558180` does not read `0x154` anywhere [code].
   Therefore, **stealing an item or gold from an enemy does NOT remove or reduce its drops upon death** [code]. The defeat drop is completely independent; a player can steal an item and receive another copy of that same item (or equipment) when the enemy dies.

### One-Sentence Conclusion
The unit bytes `0x154` (item) and `0x155` (gold) are set to 1 only upon a successful steal, enforcing a limit of one item and one gold steal per enemy instance, while defeat drops never check these flags and remain completely independent.

---

## 3. Modifiers of Steal Success Chance and Result

### Formula in Code (`0x44fde0`)
```
ratio        = (thief_DEX + 50) / (target_AGI + 50)
base_chance  = 0.5 * ratio * skill_effect_value
final_chance = min(0.95, max(0.05, base_chance))
success      = rand(0..99) < int(final_chance * 100)
```

### Proving Assembly Instructions
```x86asm
0044fe2c  mov      edx, 0x3c                         ; [code] effect 60 (Gold Steal)
0044fe33  call     0x47e340                          ; [code] read effect 60
...
0044fe55  mov      edx, 0x3d                         ; [code] effect 61 (Item Steal)
0044fe5c  call     0x47e340                          ; [code] read effect 61
...
0044fe85  push     5                                 ; [code] stat 5 = AGI
0044fe8c  mov      ecx, dword ptr [edi + 0x10]       ; [code] target unit
0044fe91  call     dword ptr [eax + 0x34]            ; [code] target AGI
0044fe97  push     4                                 ; [code] stat 4 = DEX
0044fe99  mov      ecx, dword ptr [eax + 0x10]       ; [code] thief unit
0044fe9e  call     dword ptr [eax + 0x34]            ; [code] thief DEX
0044febc  addss    xmm0, dword ptr [0x6d94e0]        ; [code] float 50.0f -> (thief DEX + 50)
0044fee0  addss    xmm0, dword ptr [0x6d94e0]        ; [code] float 50.0f -> (target AGI + 50)
0044fee8  divss    xmm1, xmm0                        ; [code] ratio
0044feec  movss    xmm0, dword ptr [0x6d92ec]        ; [code] float 0.05f (5% minimum floor)
0044fef4  mulss    xmm1, dword ptr [0x6d9348]        ; [code] float 0.5f
0044fefc  mulss    xmm1, dword ptr [ebp + 0x10]      ; [code] * skill_effect_value
0044ff01  maxss    xmm0, xmm1                        ; [code] clamp >= 0.05
0044ff05  movss    xmm1, dword ptr [0x6d9384]        ; [code] float 0.95f (95% maximum ceiling)
0044ff0d  minss    xmm1, xmm0                        ; [code] clamp <= 0.95
0044ff16  call     0x490790                          ; [code] roll random integer in [0, 99]
0044ff31  cmp      eax, ecx                          ; [code] compare roll with int(final_chance * 100)
```

### Complete Inventory of Modifiers
1. **Skills & Effects**:
   - **Effect 60 (Gold Steal)**: Carried by player skill `Gold Steal` (Technique ID 29, `TechniqueSkillData_0029.bin`) [code].
     - Values per Level (Lv 1–5): `0.40, 0.45, 0.50, 0.57, 0.64` [code].
   - **Effect 61 (Item Steal)**: Carried by player skill `Item Steal` (Technique ID 30, `TechniqueSkillData_0030.bin`) [code].
     - Values per Level (Lv 1–5): `0.30, 0.35, 0.40, 0.45, 0.50` [code].
   - **Effect 62 (Gold Factor)**: Carried exclusively by enemy steal attacks (`EnemyAttackData_0665`, `0666`, `0671`, `0672`, `1865`, `1866`, `1867`, `2197`, `2198`) with values ranging from `0.03` to `0.15` [code]. If an action lacks Effect 62, the factor defaults to `1.0f` [code].
2. **Enchantments**:
   - **Enchantment 276 ("Equipment drop rate UP")**: **Does NOT affect Steal** [code]. Skipped by `005581f1 jne 0x55828b`.
   - **Treasure Hunt (Effect 270)**: **Does NOT affect Steal** [code]. Skipped by `005581f1 jne 0x55828b`.
   - Neither the success roll nor the item weights receive any bonus from these enchantments.
3. **Target Status Conditions**:
   - `_Steal` **never checks** sleep, paralysis, freeze, silence, stun, or slow [code].
   - Target status only influences Steal indirectly if it alters DEX or AGI (e.g. Petrification halves target AGI in `vtable + 0x34` calculation, which improves the thief's steal chance) [code].
4. **Enemy Flags (`EnemyStatusData` offset 0x3C, memory 0x54)**:
   - **Bit 15 (`0x8000`)**: The definitive **Steal Immunity bit** [code]. If clear (0), Item Steal fails unconditionally before rolling, outputting Message 0x5A (`"You can't steal from this monster!"`) [code]. All fixed story/postgame bosses have this bit cleared [code].

### One-Sentence Conclusion
Steal success is governed strictly by the thief's DEX, target's AGI, and skill effect value clamped between 5% and 95%, completely ignoring drop enchantments and ailments, while enemies with Bit 15 cleared at file offset `0x3C` are totally immune to item theft.

---

## 4. Enemy Gold Theft from the Party

### Proving Assembly Instructions
```x86asm
; In Battle::CBattle::_Steal (0x44fde0):
0044ff79  cmp      byte ptr [edi + 0x78], 0          ; [code] edi + 0x78 == 1 when target is a party member
0044ff7d  je       0x450132                          ; [code] if target is an enemy, branch to player steal
; Enemy stealing from party:
0044ffa8  mov      ecx, dword ptr [0x71fc24]         ; [code] global party inventory/gold manager
0044ffb0  call     dword ptr [eax + 0x4c]            ; [code] get party gold
0044ffbf  cvtdq2ps xmm0, xmm0
0044ffc2  mulss    xmm0, dword ptr [ebp + 0xc]       ; [code] multiply by Effect 62 factor (0.03 - 0.15)
0044ffc7  cvttss2si ebx, xmm0                        ; [code] ebx = int(party_gold * factor)
0044ffd0  neg      eax
0044ffd3  call     dword ptr [edx + 0x48]            ; [code] deduct gold from party
0044fffb  mov      ecx, dword ptr [esi + 0x158]      ; [code] esi = enemy unit object; read carried stolen gold
00450001  add      ecx, ebx                          ; [code] add newly stolen gold
0045000b  mov      dword ptr [esi + 0x158], edx      ; [code] store updated sum at [enemy + 0x158] (capped at 999,999,999)
00450026  mov      dword ptr [ebp + 0x14], 0x55      ; [code] String 0x55: "Some gold was stolen from you!"
```
```x86asm
; In battle victory reward function (0x43a4a0):
0043aa73  add      eax, dword ptr [ecx + 0x158]      ; [code] when enemy falls, add carried stolen gold back to victory gold pool!
```

### One-Sentence Conclusion
When an enemy uses a steal attack on a party member, it deducts `int(party_gold * effect_62)` from the party, stores it in its own unit buffer at `+0x158`, and returns all of it to the victory gold pool upon defeat.

---

## 5. Data Tables and Population Analysis

Data extracted using [`scratch/generate_steal_table.py`](file:///c:/Users/user/Personal/Physics/DungeonTraveler2-2/scratch/generate_steal_table.py).

### Global Population Metrics
- **Total enemies in game**: 516 [code].
- **Enemies with Bit 15 set (Item Steal enabled)**: **381** [code].
- **Enemies with Bit 15 clear (Item Steal immune)**: **135** (all story bosses, subquest bosses, and superbosses) [code].
- **Enemies with Bit 15 set but no items to steal**: **0** [code]. Every stealable enemy has at least one valid candidate.
- **Pieces only obtainable via steal (`p_drop == 0`)**: **0** [code]. Every stealable item and equipment piece is also present in that enemy's defeat loot table.

---

### The 30 Items / Equipment with Lowest Conditional Steal Probability

When Item Steal succeeds, the roll is normalized across the enemy's positive drop chances. The 30 candidate items with the lowest conditional probability `P(piece | steal success)` across the entire game are:

| # | Enemy ID | Enemy Name | Level | Stolen Item / Equipment | Type | Steal Prob (Given Success) | Defeat Drop Prob |
|:---:|:---:|:---|:---:|:---|:---:|:---:|:---:|
| 1 | 6 | Garasha | 51 | Chief's Special (339) | Fixed Equip | **1.818%** | 0.800% |
| 2 | 236 | Thor | 84 | Mjolnir (223) | Fixed Equip | **2.170%** | 1.020% |
| 3 | 65 | Shanina | 67 | Degtyaryov (340) | Fixed Equip | **2.586%** | 1.500% |
| 4 | 212 | Cat's Eye | 50 | Red Jacket (656) | Fixed Equip | **2.758%** | 0.910% |
| 5 | 236 | Thor | 84 | Jarngreipr (764) | Fixed Equip | **2.894%** | 1.360% |
| 6 | 732 | Knuckle Saint | 84 | Hero Scarf (761) | Fixed Equip | **3.103%** | 0.900% |
| 7 | 933 | Peach Jam | 24 | Banango Armor (667) | Fixed Equip | **3.750%** | 1.200% |
| 8 | 349 | Okiku | 52 | Avoid Mantle (649) | Fixed Equip | **4.174%** | 1.920% |
| 9 | 273 | Jeweler | 9 | Dull Sword (2) | Fixed Equip | **4.286%** | 3.000% |
| 10 | 273 | Jeweler | 9 | Zone Table Kind 0 | Zone Equip | **4.286%** | 3.000% |
| 11 | 66 | Roland | 88 | Devil Musket (341) | Fixed Equip | **4.310%** | 2.500% |
| 12 | 210 | Neko Baba | 12 | Cat Ears (605) | Fixed Equip | **4.535%** | 1.950% |
| 13 | 217 | Ama Neko | 46 | Water Deity Ring (709) | Fixed Equip | **4.535%** | 1.950% |
| 14 | 0 | Medic | 11 | Nurse Cap (582) | Fixed Equip | **4.884%** | 2.100% |
| 15 | 207 | Little Mermaid | 90 | Phantom Menace (324) | Fixed Equip | **5.073%** | 2.080% |
| 16 | 207 | Little Mermaid | 90 | Cohuleen Druith (227) | Fixed Equip | **5.073%** | 2.080% |
| 17 | 405 | Tiamat | 93 | Dark Daimyo (713) | Fixed Equip | **5.077%** | 2.640% |
| 18 | 176 | Flower Fairy | 11 | Opera Gloves (750) | Fixed Equip | **5.122%** | 2.100% |
| 19 | 222 | Appler Knight | 47 | Iron Rice Cracker (749) | Fixed Equip | **5.233%** | 2.250% |
| 20 | 834 | Hibagon | 28 | Fumukami Mitama (722) | Fixed Equip | **5.233%** | 2.250% |
| 21 | 348 | Karakuri Puppet | 29 | Puppet Manual (473) | Fixed Equip | **5.333%** | 2.400% |
| 22 | 81 | Seraph | 97 | Garb of Rose (684) | Fixed Equip | **5.417%** | 3.250% |
| 23 | 107 | Apsaras | 27 | Dancing Turban (593) | Fixed Equip | **5.463%** | 2.240% |
| 24 | 474 | Scathach | 82 | Gae Bolg (169) | Fixed Equip | **5.543%** | 2.550% |
| 25 | 939 | Persibang | 40 | Zone Table Kind 2 | Zone Equip | **5.556%** | 2.000% |
| 26 | 199 | Huggy | 46 | Muscle Barbell (751) | Fixed Equip | **5.581%** | 2.400% |
| 27 | 336 | Death Bringer | 49 | Blessed Sword (24) | Fixed Equip | **5.714%** | 2.400% |
| 28 | 345 | Enkky | 85 | Ayamur Magna (230) | Fixed Equip | **5.714%** | 2.400% |
| 29 | 171 | Namahage | 32 | Namahage Cleaver (135) | Fixed Equip | **5.795%** | 2.550% |
| 30 | 172 | Boze | 43 | Spike Shield (535) | Fixed Equip | **5.795%** | 2.550% |

---

### Very Powerful Enemies (Ranges 504–632 and 972–989)

#### Superbosses (IDs 972–989)
All 10 superbosses in this range have **Bit 15 = 0** [code]. They are **immune to Item Steal**:
- `972 Tenerezza (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `973 Tenerezza (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `975 Lolo (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `976 Lolo (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `978 Magna Meretrix (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `979 Magna Meretrix (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `982 Adon (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `985 Samson (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `988 Crom Cruach (Lv99)`: Immune (`0x3C bit 15 = 0`).
- `989 Crom Cruach (Lv99)`: Immune (`0x3C bit 15 = 0`).

#### Wandering Superbosses
As reported in community guides (e.g. GameFAQs Very Powerful Enemies), only four wandering superbosses allow Item Steal [code]:
- `81 Seraph (Lv97)`: **Can Steal** [code]
  - Item: `Fruit of the World Tree` (ID 55): Steal 20.83% | Drop 12.50%
  - Item: `Grand Holy Water` (ID 51): Steal 37.50% | Drop 22.50%
  - Fixed Equip: `Garb of Rose` (ID 684): Steal **5.42%** | Drop **3.25%**
  - Fixed Equip: `Amenonuhoko` (ID 171): Steal **5.42%** | Drop **3.25%**
  - Zone Equip: `Table Kind 3`: Steal **30.83%** | Drop **18.50%**
- `184 Fudo Myouou (Lv97)`: **Can Steal** [code]
  - Item: `Sake of the Gods` (ID 59): Steal 30.77% | Drop 20.00%
  - Item: `Fumirul Nectar` (ID 25): Steal 30.77% | Drop 20.00%
  - Fixed Equip: `Kurikara Sword` (ID 39): Steal **5.77%** | Drop **3.75%**
  - Fixed Equip: `Demon King Shield` (ID 546): Steal **5.77%** | Drop **3.75%**
  - Zone Equip: `Table Kind 3`: Steal **26.92%** | Drop **17.50%**
- `390 Zahhak (Lv98)`: **Can Steal** [code]
  - Item: `Fumirul Nectar` (ID 25): Steal 31.25% | Drop 20.00%
  - Item: `Dragon Meat` (ID 588): Steal 31.25% | Drop 20.00%
  - Fixed Equip: `Gungnir` (ID 170): Steal **5.86%** | Drop **3.75%**
  - Fixed Equip: `Sacred Dragon Staff` (ID 477): Steal **5.86%** | Drop **3.75%**
  - Zone Equip: `Table Kind 3`: Steal **25.78%** | Drop **16.50%**
- `892 Jormungandr (Lv98)`: **Can Steal** [code]
  - Item: `Fumirul Nectar` (ID 25): Steal 31.25% | Drop 20.00%
  - Item: `Dragon Meat` (ID 588): Steal 31.25% | Drop 20.00%
  - Fixed Equip: `Gungnir` (ID 170): Steal **5.86%** | Drop **3.75%**
  - Fixed Equip: `Yggdrasil Robe` (ID 683): Steal **5.86%** | Drop **3.75%**
  - Zone Equip: `Table Kind 3`: Steal **25.78%** | Drop **16.50%**
- `17 Odin (Lv99)`: Immune (`0x3C bit 15 = 0`) [code].
- `144 Asmodeus (Lv99)`: Immune (`0x3C bit 15 = 0`) [code].
- `444 Carmilla (Lv98)`: Immune (`0x3C bit 15 = 0`) [code].

#### Therian Kings & Mercenaries (Range 504–632)
Of the 84 enemies in range 504–632:
- **58 enemies** have Bit 15 = 1 (stealable) [code]. Full loot breakdown available in [`vpe_steal_report.txt`](file:///c:/Users/user/Personal/Physics/DungeonTraveler2-2/scratch/vpe_steal_report.txt).
- **26 enemies** have Bit 15 = 0 (immune, including boss Therians like Mandra Prince 504, Mandra Princess 511, Mil the Overlord 542, Gam the Wise 548, Zouchou Kuma 549, Hana the Waterfall 555, Bishamon Peggy 556) [code].

---

## 6. Data Levers to Modify Steal Probability

All levers exist as data fields in archive parameters; **no binary/executable patch is needed** to modify steal probabilities [code].

### Summary of Levers in Data Files

| Target Property | File | Offset in File (Memory) | Type | Vanilla Range | Direct Impact on Steal | Impact on Defeat Drop |
|:---|:---|:---|:---:|:---:|:---|:---|
| **Steal Immunity** | `EnemyStatusData.bin` | `0x3C` (`0x54`) | uint32 (bit 15) | 0 or 1 | Setting bit 15 to 1 enables Steal on an immune boss | **None**. Defeat drop ignores bit 15 |
| **Thief Hit Chance** | `TechniqueSkillData_0030.bin` | `0x40` | float | `0.30`–`0.50` | Higher float increases overall Steal success check (up to 95% cap) | **None** |
| **Target AGI** | `EnemyStatusData.bin` | `0x30` (`0x48`) | int32 | 1–999 | Lowering target AGI raises the success check | May affect turn order / evasion |
| **Equipment Share in Steal** | `EnemyStatusData.bin` | `0x7C` (`0x94`) | int32 | 0–100 | Raising `0x7C` increases equipment share vs consumable items in Stage 1 | **Coupled**: directly raises defeat equipment drop chance |
| **Piece Share in Equipment** | `EnemyStatusData.bin` | `0x8C`, `0x98`, `0xA4` (`0xA4`, `0xB0`, `0xBC`) | int32 | 5–100 | Raising a slot's weight increases its share among equipment options | **Coupled**: directly raises that piece's share in defeat drop |
| **Consumable Dilution** | `EnemyStatusData.bin` | `0x70`, `0x78` (`0x88`, `0x90`) | int32 | 0–100 | Lowering item drop chances to 0 removes them from Steal lottery, boosting equipment share to 100% | **Coupled**: lowers or removes consumable drops on death |

### Coupling Summary
To increase the probability of stealing a specific equipment piece from an enemy without touching the executable:
1. **Enable theft** by setting Bit 15 of `EnemyStatusData + 0x3C` to 1 (if currently 0) [code].
2. **Raise the slot weight** at `0x8C` / `0x98` / `0xA4` [code]. Note that this **couples directly** with the defeat drop: the piece will also drop more frequently upon defeat.
3. **Raise the base equipment chance** at `0x7C` or **lower consumable chances** at `0x70`/`0x78` to concentrate the Stage 1 lottery on equipment [code].

---

## 7. Contradictions & Corrections with Previous Documentation

1. **`FORMULAS.md` Section 12.16**:
   - *Previous statement*: Function address cited as `0x44fd60` [code].
   - *Correction*: The true function start is `0x44fde0` (`0x44fd60` is within the epilogue/ret of `0x44fbb0` / `CBattleBase::GetZoneRevision`) [code].
   - *Previous statement*: `chance = 0.5 * (DEX + 50) / (AGI + 50) * (value of effect 60 + value of effect 61)` [code].
   - *Correction*: Effect 60 and 61 are checked in mutual exclusion (`0044fe3c` branches past effect 61 if effect 60 exists; lines `0044ff42` and `0045036a` branch to separate Gold and Item execution paths). Their values are never summed together [code].
   - *Previous statement*: `item: the item of the steal fields of the enemy record; once per enemy (0x154)` [code].
   - *Correction*: There are no dedicated steal fields. The item is drawn dynamically via `0x558180` across the enemy's regular drop items and equipment slots with the "nothing" slot suppressed [code].
2. **`tools/enemy_data.py` Line 26**:
   - *Previous statement*: `0x84 what can be stolen from it: a flag, an id at 0x88, a chance in percent at 0x8C (the steal code reads 0x84)` [code].
   - *Correction*: Offset `0x84` is simply Equipment Slot 0 (flag at `0x84`, fixed ID / zone kind at `0x88`, weight at `0x8C`). The steal code never reads `0x84` directly; it calls `0x558180` [code].
   - *Previous statement*: `bits 0, 1, 15 not decoded` at offset `0x3C` [code].
   - *Correction*: Bit 15 is decoded as the `can_steal` item flag (checked at `004503c5`) [code].

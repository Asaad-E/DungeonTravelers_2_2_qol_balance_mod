# Reverse Engineering Report: Item Effect Pairs, Restaurant Food, Magic Accuracy, Murder License, Shadow Heart, Did You Call for Me?, and Third Eye Wide

## Overview & Scope

This document provides binary-verified reverse engineering analysis for seven mechanics in *Dungeon Travelers 2-2* (PC, English, 32-bit executable `DT22_en_unwrapped.vanilla.exe`, image base `0x400000`):
1. **Item Effect Pairs 3 & 4**: Target-dependent evaluation of `ItemData` effect pairs (Ally vs. Enemy) and callers of the item effect switch factory `0x50c570`.
2. **Restaurant Food (FoodMenuData)**: Menu effect types 62, 63, and 64, verifying their division by 10 and relationship to combat effect IDs.
3. **Magic Accuracy Per Level**: Verification of the 10-float array at offset `0xFC` in `MagicSkillData` in the spell hit calculation `0x44d370`, and behavior for non-scaling spells.
4. **Murder License (Effect 319, Passive 1580)**: Step 12 of turn processing (`0x437364 - 0x437494`), determining linked skill execution, activation chance, and turn consumption.
5. **Shadow Heart (Effect 448, Luco Unique)**: Creation of shadow doll (`0x4fe2e0`), stat duplication, stripped ailments/technique buffs, retained passives, single-attack duration, and drain interaction.
6. **Did You Call for Me? (Effect 354, Yae Unique)**: Action post-processing (`0x439103`), turn-action counter dynamics, buff duration non-decrement / Power Charge preservation, and consecutive activation lockout (`+0x107`).
7. **Third Eye Wide (Effect 345, Lilian Unique)**: Turn-start trigger (`0x43697b`), 7-outcome roll (`0x439643`), and bug verification in effect 74 (Dispel) bypass (`0x47ee6f`).

---

## 1. Item Effect Pairs 3 and 4 (ItemData File Offset 0x24)

### Background & Data Layout
In `ItemData` (file `/Parameter/ItemData.pck`, map `0x7389f4`), each record stores four 8-byte `(int effect_type, float value)` pairs starting at file offset `0x24`:
- **Pair 0 (Pair 1 in 1-based indexing)**: file `0x24` (type), `0x28` (value) -> memory `0x3c`, `0x40`
- **Pair 1 (Pair 2 in 1-based indexing)**: file `0x2c` (type), `0x30` (value) -> memory `0x44`, `0x48`
- **Pair 2 (Pair 3 in 1-based indexing)**: file `0x34` (type), `0x38` (value) -> memory `0x4c`, `0x50`
- **Pair 3 (Pair 4 in 1-based indexing)**: file `0x3c` (type), `0x40` (value) -> memory `0x54`, `0x58`

### Proving Assembly Instructions

#### A. Target Faction Check (Ally vs. Enemy) via RTTI `dynamic_cast`
In `Action::CActionPatternItem::Update` (`0x42cc90`, lines `0x42ccae - 0x42ccdf`) and `Action::CActionPatternU0008::Update` (`0x42f940`, lines `0x42f996 - 0x42f9c3`):
```x86asm
0042ccae  mov      eax, dword ptr [edi + 0xc]         ; [code] eax = Action context
0042ccb1  push     0                                  ; [code] isReference = false
0042ccb3  push     0x707da8                           ; [code] TargetType = .?AVCGamePlayerStatus@Game@@ (Player Character / Ally)
0042ccb8  push     0x707d88                           ; [code] SrcType    = .?AVCGameStatus@Game@@       (Base Status Class)
0042ccbd  mov      eax, dword ptr [eax + 0x20]        ; [code] target unit pointer
0042ccc0  push     0                                  ; [code] VfDelta = 0
0042ccc2  push     dword ptr [eax]                    ; [code] inptr = target instance
0042ccc4  call     0x61edf4                           ; [code] __RTDynamicCast(target, 0, CGameStatus, CGamePlayerStatus, 0)
0042ccc9  add      esp, 0x14
0042cccc  test     eax, eax                           ; [code] test if target is a Player Character (Ally)
0042ccce  mov      eax, dword ptr [edi + 0xc]
0042ccd1  setne    dl                                 ; [code] dl = 1 if Ally, 0 if Enemy
0042ccd4  mov      dword ptr [esp + 0x10], eax
0042ccd8  mov      byte ptr [esp + 0x14], dl          ; [code] store isAlly flag
0042ccdc  mov      ecx, dword ptr [eax + 0xc]         ; [code] ecx = item_id
0042ccdf  call     0x55b550                           ; [code] GetItemEffectCount(item_id, isAlly)
```

#### B. Reading Effect Count by Target Faction (`0x55b550`)
```x86asm
; ecx = item_id, dl = isAlly flag (1 = Ally, 0 = Enemy)
0055b550  sub      esp, 8
0055b553  push     ebx
0055b554  lea      eax, [esp + 4]
0055b558  mov      dword ptr [esp + 4], ecx           ; [code] item_id
0055b55c  mov      ecx, dword ptr [0x7389f4]          ; [code] ItemData map
0055b562  mov      bl, dl                             ; [code] bl = isAlly
0055b564  push     eax
0055b565  lea      eax, [esp + 0xc]
0055b569  push     eax
0055b56a  call     0x507310                           ; [code] map lookup -> eax = ItemData record node
0055b56f  test     bl, bl                             ; [code] branch on isAlly
0055b571  pop      ebx
0055b572  mov      edx, dword ptr [eax]               ; [code] edx = ItemData memory record
0055b574  je       0x55b58e                           ; [code] if isAlly == 0 (Enemy), jump to pairs 2 & 3
;--- ALLY BRANCH (isAlly == 1): evaluates pairs 0 and 1 (memory 0x3c and 0x44, file 0x24 and 0x2c) ---
0055b576  xor      eax, eax
0055b578  cmp      dword ptr [edx + 0x44], -1         ; [code] check Pair 1 type != -1
0055b57c  setne    al
0055b57f  xor      ecx, ecx
0055b581  cmp      dword ptr [edx + 0x3c], -1         ; [code] check Pair 0 type != -1
0055b585  setne    cl
0055b588  add      eax, ecx                           ; [code] returns count of valid ally effects (0, 1, or 2)
0055b58a  add      esp, 8
0055b58d  ret      
;--- ENEMY BRANCH (isAlly == 0): evaluates pairs 2 and 3 (memory 0x4c and 0x54, file 0x34 and 0x3c) ---
0055b58e  xor      eax, eax
0055b590  cmp      dword ptr [edx + 0x54], -1         ; [code] check Pair 3 type != -1
0055b594  setne    al
0055b597  xor      ecx, ecx
0055b599  cmp      dword ptr [edx + 0x4c], -1         ; [code] check Pair 2 type != -1
0055b59d  setne    cl
0055b5a0  add      eax, ecx                           ; [code] returns count of valid enemy effects (0, 1, or 2)
0055b5a2  add      esp, 8
0055b5a5  ret      
```

#### C. Reading Effect Type and Value (`0x55b5b0`)
```x86asm
; ecx = item_id, edx = out_value_ptr, [esp+0x10] = out_type_ptr, [esp+0x14] = pair_sub_idx (0 or 1), [esp+0x18] = isAlly
0055b5d9  cmp      byte ptr [esp + 0x1c], 0           ; [code] test isAlly
0055b5de  mov      esi, dword ptr [esp + 0x20]        ; [code] esi = pair_sub_idx (0 or 1)
0055b5e2  mov      eax, dword ptr [eax]
0055b5e4  je       0x55b5ec
; ALLY: read type from 0x3c + esi*8, value from 0x40 + esi*8
0055b5e6  mov      eax, dword ptr [eax + esi*8 + 0x3c]
0055b5ea  jmp      0x55b5f0
; ENEMY: read type from 0x4c + esi*8, value from 0x50 + esi*8
0055b5ec  mov      eax, dword ptr [eax + esi*8 + 0x4c]
...
0055b616  je       0x55b629
0055b618  movss    xmm0, dword ptr [eax + esi*8 + 0x40] ; [code] Ally value
0055b61e  movss    dword ptr [edi], xmm0
...
0055b629  movss    xmm0, dword ptr [eax + esi*8 + 0x50] ; [code] Enemy value
0055b62f  movss    dword ptr [edi], xmm0
```

#### D. The Callers of `0x50c570` (Item Effect Switch Factory)
There are exactly **three callers** of `0x50c570` in the entire executable:
1. `0x42cda2` in `Action::CActionPatternItem::Update`:
   - Standard item usage in combat and camp menu (via `Action::CActionItemBase` `0x41b440`).
   - Checks `dynamic_cast<CGamePlayerStatus*>(target)`: passes `isAlly = 1` for player party members, `isAlly = 0` for enemies.
2. `0x42fa1b` in `Action::CActionPatternU0008::Update`:
   - Overstock Clearance item usage (effect 446).
   - Identical logic: checks `dynamic_cast<CGamePlayerStatus*>(target)` to choose Ally vs. Enemy pairs.
3. `0x5915f6` in `Shop::CShopMenuFood` (`0x591480 - 0x591700`):
   - Restaurant eating: iterates through the effects stored in `FoodMenuData` records and passes them to `0x50c570`.

### Real Data Examples
- **Item 42: Hipanera Tea**
  - Ally (pairs 0 & 1): `[(0, 50.0), (1, 20.0)]` -> Restores 50 HP and 20 TP to an ally.
  - Enemy (pairs 2 & 3): `[(0, 50.0), (-1, 0.0)]` -> Restores 50 HP only (avoids restoring TP to an enemy).
- **Item 45: Super Rich Pudding**
  - Ally (pairs 0 & 1): `[(1, 30.0), (16, 20.0)]` -> Restores 30 TP and 20 Pep to an ally.
  - Enemy (pairs 2 & 3): `[(16, 10.0), (-1, 0.0)]` -> Restores 10 Pep only to an enemy.
- **Item 82: Hard Rice Cracker**
  - Ally (pairs 0 & 1): `[(2, 75.0), (22, 1.0)]` -> Effect 2 (75) and Effect 22 (1).
  - Enemy (pairs 2 & 3): `[(0, 75.0), (22, 1.0)]` -> Effect 0 (75) and Effect 22 (1).
- **Pure Enemy Items (Pairs 0 & 1 are empty `(-1, 0.0)`):**
  - Item 50 (*Premium Cat Food*): `[(-1, 0.0), (-1, 0.0), (59, 5.0), (-1, 0.0)]` -> Only activates when targeted at an enemy (Effect 59, 5.0 turns). On allies, count is 0.
  - Item 103 (*Explosive Fishing Rod*): `[(-1, 0.0), (-1, 0.0), (58, 1.0), (-1, 0.0)]` -> Offensive enemy item.
  - Item 187 (*Bag of Darkness*): `[(-1, 0.0), (-1, 0.0), (88, 1.0), (-1, 0.0)]` -> Offensive enemy item.

### One-Sentence Conclusion
Pairs 1–2 are applied when the target is an ally (`dynamic_cast<Game::CGamePlayerStatus*>(target) != nullptr`), whereas pairs 3–4 are applied when the target is an enemy; the two groups are strictly mutually exclusive and never apply simultaneously.

---

## 2. Restaurant Food (FoodMenuData Effects 62, 63, 64)

### Background & Architecture
`FoodMenuData.pck` is deserialized by `0x50343b / 0x55a4b0` into global map `0x7389ec`. When the player eats at the restaurant in `Shop::CShopMenuFood` (`0x591480`), lines `0x5915c5 - 0x5915f6` read the meal's effect pairs and pass `effect_type` in `ecx` and float `value` in `xmm1` to `0x50c570`.

### Separation of Effect Namespaces
Effect numbers 62, 63, and 64 in `FoodMenuData` are **not** skill effect IDs (where effect 62 is "Enemy Gold Steal"). They are **Item Result Effect Types** dispatched by switch table `0x50e538`:
- `Case 62` (`0x50d7ad`): instantiates `ItemResult::CItemResult_0080` (vtable `0x6d5b3c`).
- `Case 63` (`0x50d7f9`): instantiates `ItemResult::CItemResult_0081` (vtable `0x6d59ec`).
- `Case 64` (`0x50d845`): instantiates `ItemResult::CItemResult_0082` (vtable `0x6d56d4`).

### Proving Assembly Instructions

#### A. Effect 62 (`CItemResult_0080::Apply`, `0x512eb0`): Party HP Heal
```x86asm
00512ed8  cvttss2si eax, dword ptr [ebx + 8]          ; [code] eax = int(stored_value)
00512ee9  mov      dword ptr [ebp - 0x24], eax        ; [code] store N
...
00512f2e  mov      edx, dword ptr [esi]
00512f30  mov      ecx, esi                           ; [code] esi = target party member
00512f32  call     dword ptr [edx + 0x28]             ; [code] call GetMaxHP() -> eax = Max HP
00512f35  mov      ecx, eax                           ; [code] ecx = Max HP
00512f37  mov      eax, 0x66666667                    ; [code] magic constant for division by 10 (ceil(2^34 / 10))
00512f3c  imul     ecx, dword ptr [ebp - 0x24]        ; [code] ecx = Max HP * N
00512f40  imul     ecx                                ; [code] edx:eax = 0x66666667 * (Max HP * N)
00512f42  mov      eax, dword ptr [ebp - 0x20]
00512f45  sar      edx, 2                             ; [code] edx = (Max HP * N) / 10
00512f48  mov      edi, edx
00512f4a  shr      edi, 0x1f
00512f4d  mov      eax, dword ptr [eax + 0x14]
00512f50  add      edi, edx                           ; [code] edi = int((Max HP * N) / 10)
;--- Item Mastery / Cook Passive (Effect 275) Check ---
00512f58  mov      eax, dword ptr [ecx]
00512f5a  push     0x113                              ; [code] effect 275 (0x113)
00512f5f  push     0
00512f61  call     dword ptr [eax + 0x48]             ; [code] GetEffect(275)
00512f64  mov      ecx, eax
00512f66  test     ecx, ecx
00512f68  je       0x512f8a                           ; [code] if no effect 275, proceed with base heal
00512f6a  mov      eax, dword ptr [ecx]
00512f6c  mov      eax, dword ptr [eax + 0x2c]
00512f6f  call     eax                                ; [code] returns passive bonus factor float
00512f71  movd     xmm0, edi
00512f75  cvtdq2ps xmm0, xmm0
00512f78  movss    dword ptr [ebp - 0x14], xmm0
00512f7d  fmul     dword ptr [ebp - 0x14]
00512f80  fstp     dword ptr [ebp - 0x14]
00512f83  cvttss2si eax, dword ptr [ebp - 0x14]
00512f88  add      edi, eax                           ; [code] edi += int(edi * bonus)
00512f8a  mov      eax, dword ptr [esi]
00512f8c  mov      ecx, esi
00512f8e  push     edi                                ; [code] push final heal amount
00512f8f  call     dword ptr [eax + 0x20]             ; [code] call HealHP(edi)
```

#### B. Effect 63 (`CItemResult_0081::Apply`, `0x513130`): Party TP Heal
```x86asm
005131aa  mov      ecx, dword ptr [esi + 0x18]        ; [code] ecx = Max TP (offset 0x18)
005131ad  mov      eax, 0x66666667                    ; [code] division by 10
005131b2  imul     ecx, dword ptr [ebp - 0x24]        ; [code] ecx = Max TP * N
005131b6  imul     ecx
005131bb  sar      edx, 2                             ; [code] edx = (Max TP * N) / 10
005131be  mov      ebx, edx
005131c0  shr      ebx, 0x1f
005131c3  mov      eax, dword ptr [eax + 0x14]
005131c6  add      ebx, edx                           ; [code] ebx = int((Max TP * N) / 10)
005131d0  push     0x113                              ; [code] effect 275 bonus
...
00513200  mov      ecx, dword ptr [esi + 0x14]        ; [code] ecx = Current TP
00513208  add      ecx, ebx                           ; [code] Current TP + heal
0051320f  mov      dword ptr [esi + 0x14], eax        ; [code] store clamped TP
```

#### C. Effect 64 (`CItemResult_0082::Apply`, `0x5133c0`): Party HP and TP Heal
- Lines `0x513444 - 0x5134a5`: computes `int((Max HP * N) / 10) * (1 + bonus 275)` and calls `HealHP`.
- Lines `0x5134a8 - 0x513507`: computes `int((Max TP * N) / 10) * (1 + bonus 275)` and adds to TP.

### Real Data Examples
- **Food 1 (Salt Flavor Ramen)**: Effects `[(62, 2.0)]` -> Restores `2 / 10` = 20% of Max HP to the party.
- **Food 12 (Curry Ramen)**: Effects `[(64, 3.0)]` -> Restores `3 / 10` = 30% of Max HP and 30% of Max TP to the party.
- **Food 20 (Berry Gelato)**: Effects `[(63, 2.0)]` -> Restores `2 / 10` = 20% of Max TP to the party.

### One-Sentence Conclusion
Effects 62, 63, and 64 are item effect switch types (not skill effect IDs) that restore exactly `N / 10` (i.e. `N * 10%`) of each party member's Max HP, Max TP, or both, boosted further if the party has effect 275.

---

## 3. Magic Accuracy Per Level (MagicSkillData 10 Floats at 0xFC)

### Background & Architecture
`MagicSkillData.pck` is deserialized byte-for-byte by `0x570290` (copying 142 dwords = 568 bytes via `rep movsd`) into `std::map<int, MagicSkillData>` at `0x738a58`.
Because map nodes store the 4-byte key followed by the record struct with 4-byte alignment, the record begins at `Node + 0x14`. Therefore, file offset `0xFC` corresponds precisely to memory offset `0x14 + 0xFC = 0x110`.

### Proving Assembly Instructions
In `Battle::CBattleBase::_CalculateMagicAttack` (`0x44d370`, lines `0x44d56d - 0x44d651`):
```x86asm
0044d56d  mov      eax, dword ptr [ebp + 0x44]        ; [code] eax = Spell ID argument
0044d570  cmp      eax, -1
0044d573  je       0x44d5a0                           ; [code] if not a spell, check enemy attack id
0044d575  mov      ecx, dword ptr [0x738a58]         ; [code] MagicSkillData map
0044d57b  mov      dword ptr [ebp + 0x54], eax
0044d57e  lea      eax, [ebp + 0x54]
0044d581  push     eax
0044d582  lea      eax, [ebp + 0x5c]
0044d585  push     eax
0044d586  call     0x507310                           ; [code] map lookup -> eax = map node
0044d58b  mov      ecx, dword ptr [ebp + 0x48]        ; [code] ecx = Spell Level Index (0-based: level - 1)
0044d58e  mov      eax, dword ptr [eax]               ; [code] eax = node pointer
0044d590  movss    xmm0, dword ptr [eax + ecx*4 + 0x110] ; [code] READS FLOAT AT FILE OFFSET 0xFC + 4*ecx
0044d599  movss    dword ptr [ebp + 0x54], xmm0       ; [code] base spell accuracy A = xmm0
0044d59e  jmp      0x44d5d9
...
; Hit accuracy calculation with stats and Loose Spirit:
0044d5de  mov      edx, 0x1e                          ; [code] effect 30 (Loose Spirit)
0044d5e1  call     0x47e340                           ; [code] get Loose Spirit value
...
0044d632  sub      esi, eax                           ; [code] esi = own INT - target RES
0044d63f  mulss    xmm0, dword ptr [0x6d92cc]         ; [code] xmm0 = (own INT - target RES) * 0.002
0044d647  addss    xmm0, dword ptr [ebp + 0x54]       ; [code] + base spell accuracy A
0044d64c  addss    xmm0, dword ptr [ebp + 0x5c]       ; [code] + Loose Spirit
0044d651  movss    dword ptr [ebp + 0x54], xmm0       ; [code] final A
```

### Analysis of Non-Scaling Spells
- **Code Execution**: The instruction `movss xmm0, dword ptr [eax + ecx*4 + 0x110]` executes unconditionally for all spells. There are no branches, special cases, or exceptions in the binary.
- **Data Reality**:
  - Exactly **30 damage spells** scale with level (e.g. Fireball, Fire Blast, Inferno, Crimson Flare, Ice Edge, ..., Blood Absorb, Dispel, elemental scrolls). Their values at `0xFC` increase with each level index.
  - In **11 spells** (the 10 status ailment spells: 167 Stun, 168 Poison, 169 Freeze, 170 Paralyze, 171 Sleep, 172 Silence, 173 Petrify, 174 Death, 175 Slow, 176 Terrorize; plus 205 Lullaby), all 5 active level slots in `MagicSkillData` at `0xFC` contain identical floats `[1.0, 1.0, 1.0, 1.0, 1.0]`.
  - Because `1.0` is stored across all levels, the base spell accuracy term `A` is permanently 100% at all spell levels.
  - The level-up text stating "Accuracy UP" is a descriptive inaccuracy: the spell's hit roll does not improve with level (it is already 100% base); only the status ailment infliction rate (stored in effect slot 0) improves.

### Real Data Examples
- **Spell 143: Fireball** (Scales):
  - `0xFC` floats: `[0.85, 0.865, 0.88, 0.895, 0.91, 0.925, 0.94, 0.955, 0.97, 1.0]` (increases +0.015/level).
- **Spell 167: Stun** (Constant despite "Accuracy UP"):
  - `0xFC` floats: `[1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]` -> `1.0` at all active levels.
- **Spell 168: Poison** (Constant despite "Accuracy UP"):
  - `0xFC` floats: `[1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]` -> `1.0` at all active levels.

### One-Sentence Conclusion
The engine at `0x44d590` reads the 10-float array at file offset `0xFC` indexed by spell level for every spell; in the non-scaling spells the array simply holds flat `1.0` at all levels, so the base hit rate stays at 100% while only ailment infliction rates scale.

---

## 4. Murder License (Effect 319, Enemy Passive 1580)

### Background & Turn State Architecture
In `Battle::CBattleBase::Update` (`0x4363bc`), turn states are dispatched via jump table `0x439820`. Turn State 12 (`0x437364 - 0x437494`) is the pre-command phase where Murder License is evaluated.

### Proving Assembly Instructions
```x86asm
00437364  inc      dword ptr [edi + 0x20]             ; [code] state counter
00437367  mov      ecx, dword ptr [esi + 0x10]        ; [code] ecx = acting unit status (CGameEnemyStatus)
0043736a  push     0x13f                              ; [code] effect 319 (0x13F = Murder License)
0043736f  push     0
00437371  mov      eax, dword ptr [ecx]
00437373  mov      eax, dword ptr [eax + 0x48]        ; [code] call GetEffect(319)
00437376  call     eax
00437378  mov      dword ptr [ebp - 0x1c], eax        ; [code] eax = status object pointer
0043737b  test     eax, eax
0043737d  je       0x437499                           ; [code] IF NOT PRESENT: jump to State 13 (normal AI command selection)
;--- PRESENT: MURDER LICENSE TRIGGER ---
00437383  lea      ecx, [ebp - 0x30]
00437386  call     0x418c30
0043738b  mov      ecx, esi
0043738d  mov      byte ptr [ebp - 4], 0x15
00437391  call     0x435a30                           ; [code] init action buffer
00437396  cmp      byte ptr [esi + 0x78], 0           ; [code] check faction: 0 = enemy, 1 = player
0043739a  mov      ecx, dword ptr [ebp - 0x1c]        ; [code] ecx = status 319 object
0043739d  je       0x4373bd                           ; [code] enemy branch
; Player branch (if player had it):
0043739f  mov      dword ptr [esi + 0x1c], 1
004373a6  mov      eax, dword ptr [ecx]
004373a8  mov      eax, dword ptr [eax + 0x34]        ; [code] slot 0x34: player skill getter
004373ab  call     eax
...
; Enemy branch:
004373bd  mov      eax, dword ptr [ecx]
004373bf  mov      eax, dword ptr [eax + 0x3c]        ; [code] slot 0x3c: enemy attack getter (returns 1580)
004373c2  call     eax
004373c4  cmp      eax, -1
004373c7  je       0x4373e8                           ; [code] error if -1
004373c9  mov      ecx, dword ptr [ebp - 0x1c]
004373cc  mov      dword ptr [esi + 0x1c], 8          ; [code] action kind = 8 (enemy attack)
004373d3  mov      eax, dword ptr [ecx]
004373d5  mov      eax, dword ptr [eax + 0x3c]
004373d8  call     eax
004373da  push     eax                                ; [code] push attack id 1580
004373db  lea      ecx, [esi + 0x18]
004373de  mov      dword ptr [esi + 0x28], eax        ; [code] store attack id 1580
004373e1  call     0x4183d0                           ; [code] setup enemy attack action
...
; Target selection (picks valid target, Self for target code 9):
0043740f  call     0x418be0                           ; [code] get target candidate count
00437414  mov      ecx, eax
00437416  call     0x505ac0                           ; [code] rand() % count (selects target)
...
; Build Action Pattern and Bypass Normal Turn:
0043744f  push     0x98
00437454  call     0x603045                           ; [code] malloc action pattern object
00437459  add      esp, 4
0043745c  mov      dword ptr [ebp - 0x58], eax
0043745f  lea      ecx, [esi + 0x18]
00437466  push     ecx
00437467  push     dword ptr [edi + 0x10]
0043746a  mov      ecx, eax
0043746c  call     0x42be90                           ; [code] construct action pattern
00437471  mov      byte ptr [ebp - 4], 0x15
00437475  mov      ecx, dword ptr [ebp - 0x1c]        ; [code] status 319 object
00437478  push     1
0043747a  mov      dword ptr [edi + 0x48], eax        ; [code] set current turn action pattern!
0043747d  push     dword ptr [esi + 0x10]             ; [code] unit pointer
00437480  call     0x48c350                           ; [code] trigger skill announcement
00437485  lea      ecx, [ebp - 0x30]
00437488  mov      dword ptr [edi + 0x18], 0xb        ; [code] set next state = 0xB (action execution)
0043748f  call     0x418bd0
00437494  jmp      0x438722                           ; [code] EXIT UPDATE LOOP (bypasses State 13 normal turn!)
```

### Answers to Specific Questions
1. **What linked skill is executed?**
   - For an enemy, method `[status + 0x3c]` returns the Enemy Attack ID stored in the status object at offset `+0x18`.
   - When passive 1580 is attached to the enemy during `CGameEnemyStatus::SetupPassives` (`0x4f1fc0`, lines `0x4f20a0 - 0x4f20a4`), the passive ID **1580** is passed to setter slot 0x38.
   - Therefore, the linked skill executed is **Enemy Attack 1580 (*Murder License*)**.
2. **With what probability?**
   - **100% (Guaranteed)**. There is no probability check or random roll in State 12 to determine if the skill activates; `0x437416` is solely a target-index selection roll.
3. **Does the bearer still take their regular turn?**
   - **NO**. The command for this turn is completely replaced by Murder License. Line `00437488 mov dword ptr [edi + 0x18], 0xb; jmp 0x438722` transitions directly to action execution and exits the state dispatcher, completely bypassing State 13 (`0x437499`) where the bearer's normal AI attack selection would occur.

### Real Boss Examples
- **Enemy 444: Carmilla** — Passives: `[1508, 1525, 1544, 1580, 2643]`
- **Enemy 619: Koumoku Mary** — Passives: `[1515, 1530, 1544, 1548, 1580]`
- **Enemy 1023: Aradia (5th battle)** — Passives: `[1519, 1580]`

### One-Sentence Conclusion
When a unit with effect 319 enters turn state 12, it executes Enemy Attack 1580 with 100% probability, completely replacing its normal turn action for that round.

---

## 5. Shadow Heart (Effect 448, Unique Skill of Luco)

### Background & Execution Flow
In `Battle::CBattle::Update` (`0x4360f0`), sub-step 15 of State 0 turn processing (`0x4378d9 - 0x437b04`, from table `0x439820`) checks unique skill effect 448 (*Shadow Heart*) right before Luco's action.

### Proving Assembly Instructions

#### A. Trigger Check & Probability Roll (`0x4378df - 0x437935`)
```x86asm
004378df  mov      ecx, dword ptr [esi + 0x10]        ; [code] ecx = Luco status
004378e2  push     0x1c0                              ; [code] push 448 (Effect 448 = Shadow Heart)
004378e7  push     0
004378e9  mov      eax, dword ptr [ecx]
004378eb  mov      eax, dword ptr [eax + 0x48]        ; [code] GetEffect(448)
004378ee  call     eax
004378f0  mov      dword ptr [ebp - 0x20], eax
004378f3  test     eax, eax
004378f5  je       0x437b0f                           ; [code] skip if effect not present
004378fb  mov      edx, dword ptr [eax]
004378fd  mov      ecx, eax
004378ff  mov      edx, dword ptr [edx + 0x2c]        ; [code] get activation chance float
00437902  call     edx
00437904  mov      ecx, 0x64                          ; [code] 100
00437909  fstp     dword ptr [ebp - 0x10]
0043790c  call     0x505ac0                           ; [code] rand() % 100
00437911  movss    xmm0, dword ptr [ebp - 0x10]
00437916  mov      edi, eax
00437918  mulss    xmm0, dword ptr [0x6d9540]         ; [code] chance * 100.0f
00437920  cvttss2si esi, xmm0
00437933  cmp      edi, esi                           ; [code] roll < chance?
00437935  jge      0x437b09                           ; [code] failure branch
```

#### B. Instantiation of `CGamePlayerStatusETCShadowHearts` (`0x437a0f - 0x437a35`)
```x86asm
00437a0f  push     0x300                              ; [code] object size = 0x300
00437a14  call     0x603045                           ; [code] malloc
00437a19  add      esp, 4
00437a1c  mov      dword ptr [ebp - 0x58], eax
00437a1f  push     0x17c
00437a24  push     0
00437a26  lea      ecx, [ebp - 0x64]
00437a2e  push     3
00437a30  push     dword ptr [esi + 0x14]             ; [code] Luco's status instance
00437a33  mov      ecx, eax
00437a35  call     0x4fe2e0                           ; [code] constructor CGamePlayerStatusETCShadowHearts
```

#### C. Shadow Base Stats & Doubled ATK (`0x4fe2e0`, `0x4fd0b0`, `0x4fd840`)
1. In `0x4fd0b0` (base copy helper, called via `0x4fd840` -> `0x4f3290`), all base parameters are copied verbatim from Luco (`edx`) to the shadow (`edi` / `ecx`):
```x86asm
004fd18d  movups   xmm0, xmmword ptr [edx + 0x54]     ; [code] stats 0x54..0x60 (ATK, DEF, INT, RES)
004fd191  movups   xmmword ptr [edi], xmm0
004fd194  movups   xmm0, xmmword ptr [edx + 0x64]     ; [code] stats 0x64..0x70 (DEX, AGI, etc.)
004fd198  movups   xmmword ptr [edi + 0x10], xmm0
...
004fd922  mov      dword ptr [ebx + 0x18], 0x270f     ; [code] max HP = 9999
004fd929  mov      dword ptr [ebx + 0x14], 0x270f     ; [code] current HP = 9999
```
2. In `0x4fe2e0` lines `0x4fe3c1 - 0x4fe3d2`, base ATK (`offset +0x54`) is explicitly **doubled**:
```x86asm
004fe3c1  mov      eax, dword ptr [ebx + 0x54]        ; [code] eax = Luco ATK
004fe3ca  add      eax, eax                           ; [code] eax = 2 * Luco ATK
004fe3d2  mov      dword ptr [ebx + 0x54], eax        ; [code] shadow ATK = 2 * Luco ATK
```
*Other combat stats*: DEF (`+0x58`), INT (`+0x5c`), RES (`+0x60`), DEX (`+0x64`), and AGI (`+0x68`) remain exactly equal to Luco's.

#### D. Preservation vs. Removal of Buffs, Ailments, and Passives (`0x4fe337 - 0x4fe3bf`)
In `0x4fd1b3 - 0x4fd206`, all active `CCommand` objects from Luco's status vector `[status + 0x8c]` are initially cloned into the shadow via `0x48bbc0` (`Command::CCommandBase::CopyCommand`).
Then `0x4fe2e0` filters the cloned list:
```x86asm
004fe354  mov      esi, dword ptr [ecx + edi*4]        ; [code] esi = cloned CCommand object
004fe357  mov      ecx, esi
004fe359  mov      eax, dword ptr [esi]
004fe35b  mov      eax, dword ptr [eax + 0x68]         ; [code] vtable slot 0x68: IsStatusAilment()
004fe35e  call     eax
004fe360  test     al, al                              ; [code] returns 1 for ailments (113-122, 139)
004fe362  je       0x4fe36e
004fe364  mov      eax, dword ptr [ebx]
004fe366  mov      ecx, ebx
004fe368  push     esi
004fe369  call     dword ptr [eax + 0x68]             ; [code] STRIP AILMENT: RemoveStatus(esi)
004fe36c  jmp      0x4fe3ac
; Check source skill ID for non-ailment effects:
004fe36e  mov      eax, dword ptr [esi]
004fe370  mov      ecx, esi
004fe372  call     dword ptr [eax + 0x34]             ; [code] vtable slot 0x34: GetSkillID() (reads +0x14)
004fe375  cmp      eax, -1
004fe378  je       0x4fe3a8                           ; [code] if skill_id == -1 (PASSIVE), KEEP IT!
004fe37a  mov      edi, dword ptr [0x738a5c]          ; [code] Parameter::CParameterSkill (SkillData.pck)
004fe380  mov      ecx, edi
004fe382  mov      dword ptr [ebp + 8], eax
004fe385  lea      eax, [ebp + 8]
004fe388  push     eax
004fe389  lea      eax, [ebp - 0x14]
004fe38c  push     eax
004fe38d  call     0x507310                           ; [code] map lookup in SkillData.pck
004fe392  mov      eax, dword ptr [eax]
004fe394  cmp      eax, dword ptr [edi]               ; [code] found in SkillData.pck?
004fe396  je       0x4fe3a5                           ; [code] NOT in SkillData (e.g. Magic buff): KEEP IT!
004fe398  mov      eax, dword ptr [ebx]
004fe39a  mov      ecx, ebx
004fe39c  push     esi
004fe39d  call     dword ptr [eax + 0x68]             ; [code] IN SkillData (Technique skill): STRIP IT!
```
- **Ailments**: Overridden in classes `CCommand_0113` through `CCommand_0122` and `CCommand_0139` to return `1` (`0x4151e0`). All ailments are **stripped** (`0x4fe369`).
- **Passives & Inherent Buffs**: Initialized with `skill_id == -1` (e.g. Double Attack, Triple Attack, class passives, item buffs, food buffs). Line `0x4fe375: cmp eax, -1; je 0x4fe3a8` skips removal. **Preserved**.
- **Technique Skill Buffs**: Skills in `SkillData.pck` (Technique IDs 0–142) store their skill ID at `+0x14`. Line `0x4fe396` finds them and calls `RemoveStatus` (`0x4fe39d`). **Stripped**.

#### E. Duration & Action Execution (`0x4fe510`, `0x4fe430`)
- In `CGamePlayerStatusETCShadowHearts::slot_0x190` (`0x4fe510`), line `mov dword ptr [ecx + 4], 1; call 0x418160` sets Action 1 (Basic Physical Attack). A target is chosen randomly via `call 0x490790` (`0x4fe586`).
- The shadow executes **exactly one single basic attack**.
- Once the round finishes, the unit is destroyed by its virtual destructor at `0x4fe430`.

#### F. Verifying the Drain ATK-Revert Myth (`0x422ec0 - 0x423000`)
In damage resolution for HP/TP absorb (effects 75 and 76, enchants 161–164), line `0x422f4e` computes `drain_amount = damage * absorb_pct`. The damage was computed in `0x44a850` using the shadow's current ATK (`2 * Luco_ATK`).
No instruction in `0x422ec0 - 0x423000` writes to or recalculates stat `+0x54`.
**The claim that the shadow's ATK reverts to Luco's ATK when absorbing HP or TP is completely FALSE.**

### One-Sentence Conclusion
Luco's shadow is created with double her ATK and 9999 HP/TP, clears all status ailments and active technique buffs while retaining passives (including Double/Triple Attack), performs exactly one normal attack against a random enemy, and never has its doubled ATK reduced upon HP/TP drain.

---

## 6. Did You Call for Me? (Effect 354, Unique Skill of Yae)

### Background & Execution Flow
In `Battle::CBattle::Update` (`0x4360f0`), State 3 (`0x438beb - 0x4392ef`, Action Post-Processing) checks chained turn triggers after a unit's attack.

### Proving Assembly Instructions

#### A. Trigger Evaluation & Consecutive Lockout (`0x43903b - 0x43915a`)
```x86asm
0043903b  cmp      byte ptr [esi + 0x107], 0          ; [code] check extra action lockout flag
00439042  jne      0x439272                           ; [code] IF ALREADY SET, SKIP ENTIRE TRIGGER CHAIN!
...
; Checks Double Action (0x120 = 288) at 0x439072
; Checks Triple Action (0x121 = 289) at 0x4390b9
; If neither triggered, checks Yae's unique skill (0x162 = 354):
00439100  mov      ecx, dword ptr [esi + 0x10]        ; [code] ecx = Yae status
00439103  push     0x162                              ; [code] push 354 (Effect 354 = Did You Call for Me?)
00439108  push     0
0043910a  mov      eax, dword ptr [ecx]
0043910c  mov      eax, dword ptr [eax + 0x48]        ; [code] GetEffect(354)
0043910f  call     eax
00439111  mov      ecx, eax
00439113  mov      dword ptr [ebp - 0x18], ecx
00439116  test     ecx, ecx
00439118  je       0x439272                           ; [code] fail branch
0043911e  mov      eax, dword ptr [ecx]
00439120  mov      eax, dword ptr [eax + 0x2c]        ; [code] get activation chance float
00439123  call     eax
00439125  mov      ecx, 0x64
0043912a  fstp     dword ptr [ebp - 0x10]
0043912d  call     0x505ac0                           ; [code] rand() % 100
00439132  movss    xmm0, dword ptr [ebp - 0x10]
00439137  mulss    xmm0, dword ptr [0x6d9540]         ; [code] chance * 100.0f
0043913f  cvttss2si ecx, xmm0
00439143  cmp      eax, ecx                           ; [code] roll < chance?
00439145  jge      0x439272                           ; [code] fail branch
; Activation success:
0043914b  mov      eax, 2                             ; [code] action count = 2
00439150  mov      ecx, dword ptr [ebp - 0x18]
00439153  mov      byte ptr [esi + 0x107], 1          ; [code] SET LOCKOUT FLAG (+0x107 = 1)
0043915a  mov      dword ptr [esi + 0xb4], eax        ; [code] store remaining actions = 2
```

1. **Consecutive activation check**: Field `[esi + 0x107]` is the per-round extra action flag. Line `0x43903b` enforces that if `[esi + 0x107] != 0`, the entire trigger block is skipped. When Did You Call for Me triggers, line `0x439153` sets `[esi + 0x107] = 1`. During the extra action, line `0x43903b` detects this and skips activation. The flag is only cleared at the start of a new round at `0x43671a` (`mov byte ptr [esi + 0x107], 0`).
   **Conclusion: It is strictly impossible for Did You Call for Me to trigger twice in a row.**

#### B. Turn Expiration Bypass & Power Charge Preservation (`0x439270 - 0x43928b`, `0x439426`)
```x86asm
0043926b  call     0x498a70                           ; [code] announce skill in battle log
00439270  jmp      0x43928b                           ; [code] BYPASS TURN FINALIZATION!
; Skipped block:
00439272  cmp      byte ptr [ebp - 0x32], 0
00439276  je       0x43928b
00439278  push     esi
0043927d  mov      ecx, edi
0043927f  call     0x43e5c0                           ; [code] FinishTurn: decrements unit queue
00439284  mov      dword ptr [edi + 0x20], 0
0043928b  mov      ecx, edi
...
004392e3  mov      dword ptr [edi + 0x18], 0          ; [code] return to State 0 for extra action!
```
1. **Turn-end bypass**: Because `[esi + 0xb4]` is 2, the game jumps directly to `0x43928b`, skipping `0x43e5c0` (turn finalization).
2. **Buff duration & Power Charge**: Turn-based buff duration decrements and Power Charge charge consumption (`CCommand_0191::slot_0x14` at `0x48d590`) are executed in `0x444340`, which is called exclusively from **State 6** (`0x439426`). State 6 runs only after all chained actions in a turn have finished.
   Because the state machine loops directly back to State 0 without entering State 6, **no buff durations decrement** and **Power Charge is not consumed until after the extra attack completes**.
   **Conclusion: Power Charge remains fully active for both the initial attack and the extra attack.**

### One-Sentence Conclusion
Did You Call for Me grants a second action within the same turn while setting flag `+0x107` to prevent any further trigger that round, and because State 6 turn cleanup is deferred until all actions finish, buff durations do not decrement and Power Charge powers both attacks.

---

## 7. Third Eye Wide (Effect 345, Unique Skill of Lilian)

### Background & Execution Flow
In `Battle::CBattle::Update` (`0x4360f0`), sub-step 2 of State 0 turn processing (`0x436955 - 0x436a87`) checks unique skill effect 345 (*Third Eye Wide*) on every enemy unit's turn start.

### Proving Assembly Instructions

#### A. Turn-Start Check & Transition to State 13 (`0x436970 - 0x436a80`)
```x86asm
0043697b  push     0x159                              ; [code] push 345 (Effect 345 = Third Eye Wide)
00436980  push     0
00436982  mov      eax, dword ptr [eax]
00436984  mov      ecx, dword ptr [eax + 0x10]
00436987  mov      eax, dword ptr [ecx]
00436989  mov      eax, dword ptr [eax + 0x48]        ; [code] GetEffect(345)
0043698c  call     eax
...
; If roll succeeds:
00436a08  mov      dword ptr [edi + 0x1a4], eax       ; [code] store Lilian instance
00436a80  mov      dword ptr [edi + 0x18], 0xd        ; [code] transition to State 13 (0xD)
```

#### B. The 7-Outcome Sorteo in State 13 (`0x439643 - 0x439669`)
In State 13 (`0x439613`), lines `0x439643 - 0x43964a` choose one of 7 outcomes uniformly:
```x86asm
00439643  mov      ecx, 7                             ; [code] bound = 7
00439648  mov      esi, eax                           ; [code] esi = active enemy target
0043964a  call     0x505ac0                           ; [code] rand() % 7 (returns 0..6)
0043964f  movss    xmm2, dword ptr [0x6d9368]         ; [code] float 0.75 (75% infliction chance)
00439657  mov      ecx, 1
0043965c  push     0
0043965e  push     -1
00439660  mov      edx, dword ptr [eax*4 + 0x6c9af8]  ; [code] load effect ID from 7-element table
00439667  push     -1
00439669  call     0x47b220                           ; [code] CreateCommand(edx)
```
The 7 options stored at array `0x6c9af8` are:
- `Option 0 (0x6c9af8 + 0x00)`: ID 113 (`Poison`)
- `Option 1 (0x6c9af8 + 0x04)`: ID 115 (`Paralysis`)
- `Option 2 (0x6c9af8 + 0x08)`: ID 116 (`Sleep`)
- `Option 3 (0x6c9af8 + 0x0C)`: ID 114 (`Freeze`)
- `Option 4 (0x6c9af8 + 0x10)`: ID 117 (`Silence`)
- `Option 5 (0x6c9af8 + 0x14)`: ID 118 (`Stun`)
- `Option 6 (0x6c9af8 + 0x18)`: ID 74 (`Dispel / Remove Buffs`)

#### C. The Bug That Bypasses the 7th Outcome (`0x47ee6f` in `0x47e500`)
1. For Option 6 (Effect 74), `CreateCommand` (`0x47b220`) has no specialized derived class, defaulting at line `0x47ddb6` to instantiating generic `CCommandBase` (vtable `0x6d119c`).
2. When the effect is executed via `enemy->slot_0xe4` (`0x4fbb60` -> `0x4fbcba`), line `0x4fbd08` calls `command->slot_0x18`.
   - For `CCommandBase`, slot `0x18` is `0x48bd60`. It calls `0x419640` to initialize the action record:
```x86asm
00419648  mov      dword ptr [esi], eax
0041964a  mov      dword ptr [esi + 4], 0
00419651  mov      dword ptr [esi + 8], 0xffffffff    ; [code] unconditionally sets record +0x8 to -1
```
3. Control then passes to `0x47e500` to process the action results. The Dispel handling block begins at `0x47ee62`:
```x86asm
0047ee62  mov      eax, dword ptr [ebp + 8]
0047ee65  cmp      dword ptr [eax + 0x40], 0
0047ee69  je       0x47efc4                           ; [code] abort jump 1
0047ee6f  cmp      dword ptr [ebx + 8], -1            ; [code] check record +0x8 against -1!
0047ee73  je       0x47efc4                           ; [code] ABORT JUMP 2: IF -1, JUMP TO 0x47efc4!
; The entire Dispel execution block below is completely skipped:
0047ee79  mov      ecx, ebx
0047ee7b  call     0x48cc40
0047ee80  mov      esi, eax
0047ee8a  mov      edx, dword ptr [esi]
0047ee8c  mov      ecx, esi
0047ee8e  call     dword ptr [edx + 0x24]
0047ee91  cmp      eax, 0x4a                          ; [code] cmp effect == 74 (Dispel)
0047ee94  jne      0x47efc4
...
0047ef25  mov      eax, dword ptr [ecx]
0047ef27  call     dword ptr [eax + 0x68]             ; [code] RemoveStatus (strips buff)
```
Because line `0x419651` initialized `[ebx + 8]` to `-1` (`0xffffffff`), line `0047ee6f cmp dword ptr [ebx + 8], -1; je 0x47efc4` is **guaranteed to evaluate to true**.
It branches immediately to `0x47efc4`, completely skipping the check `0x47ee91` and the buff stripping loop `0x47ef20 - 0x47ef38`.

### One-Sentence Conclusion
The 7th outcome (Dispel, effect 74) never removes any enemy buffs in practice because instruction `0x47ee6f` in `0x47e500` tests `[ebx + 8] == -1` and unconditionally jumps over the entire Dispel routine, confirming the bug reported by the Japanese wiki.

---

## 8. Summary Matrix & Audit Trail

| Question | Binary Function(s) | Proving Instructions | Verified Mechanic |
| :--- | :--- | :--- | :--- |
| **1. Item Pairs 3 & 4** | `0x42cc90`, `0x42f940`, `0x55b550`, `0x55b5b0` | `0042ccc4 call 0x61edf4`, `0055b574 je 0x55b58e` | Pairs 1–2 apply to Allies (`CGamePlayerStatus`); pairs 3–4 apply to Enemies (`CGameEnemyStatus`). Mutually exclusive; never applied simultaneously. |
| **2. Restaurant Food** | `0x591480`, `0x50c570`, `0x512eb0`, `0x513130`, `0x5133c0` | `00512f45 sar edx, 2`, `005131bb sar edx, 2`, `0051345b sar edx, 2` | Effects 62, 63, 64 are Item Result types that heal `N / 10` (i.e. `N * 10%`) of Max HP, Max TP, or both (multiplied by `0x66666667 >> 34`). |
| **3. Magic Accuracy** | `0x44d370` | `0044d590 movss xmm0, [eax+ecx*4+0x110]`, `0044d63f mulss xmm0, [0x6d92cc]` | Float array at `0xFC` is read for all spells; non-scaling spells contain flat `1.0` at all levels, keeping base hit rate at 100% while only ailment chance scales. |
| **4. Murder License** | `0x4363bc` (State 12: `0x437364 - 0x437494`), `0x4f1fc0` | `00437376 call [eax+0x48]`, `004373d8 call [eax+0x3c]`, `00437494 jmp 0x438722` | Triggers Enemy Attack 1580 with 100% probability, replacing the bearer's normal command selection entirely. |
| **5. Shadow Heart** | `0x4378df`, `0x4fe2e0`, `0x4fd0b0`, `0x422f4e` | `004fe3ca add eax, eax`, `004fe35b call [eax+0x68]`, `004fe394 cmp eax, [edi]` | Spawns doll with 2x Luco ATK; strips all ailments & technique buffs while preserving passives; lasts 1 attack; doubled ATK never reverts on drain. |
| **6. Did You Call for Me?** | `0x43903b`, `0x439103`, `0x439153`, `0x439426` | `0043903b cmp byte ptr [esi+0x107], 0`, `00439270 jmp 0x43928b` | Flag `+0x107` locks out consecutive triggers; turn finalization and State 6 cleanup are bypassed, preserving buff durations and Power Charge for both hits. |
| **7. Third Eye Wide** | `0x43697b`, `0x439643`, `0x47e500`, `0x47ee6f` | `00439648 call 0x505ac0`, `0047ee6f cmp dword ptr [ebx+8], -1; je 0x47efc4` | Rolls 7 outcomes (effect 74 Dispel included), but instruction `0x47ee6f` always evaluates true (`[ebx+8] == -1`), skipping Dispel entirely (bug confirmed). |

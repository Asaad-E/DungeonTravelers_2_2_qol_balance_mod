# Equipment Drop Mechanism and Rare Drop Rates in Dungeon Travelers 2-2

## Overview & Architecture

When an enemy is defeated in battle, its loot is resolved by `0x558180` (called at `0x43aab6` and `0x4504bf`).
The loot roll occurs in two distinct stages:
1. **Stage 1 (`0x558180`, lines `0x558180 - 0x55845c`)**: A weighted roll among regular item drops (0 to 2 items defined at `EnemyStatusData + 0x68`), the equipment drop (chance at `EnemyStatusData + 0x7C`), and an empty roll ("nothing", weight `max(0, 100 - sum_of_weights)`).
   - Treasure Hunt (passive effect 270) adds `int(TreasureHunt * 100)` to all positive chances (`0x5581ff - 0x558211`).
   - Equipment Drop Rate UP (enchantment 276 on killer) adds `20 * pieces` exclusively to the equipment drop chance (`0x55824e - 0x55827e`).
2. **Stage 2 (`0x558517 - 0x558702`)**: If the equipment drop is selected in Stage 1, the game resolves which piece of equipment is granted using the enemy's candidate equipment slots defined from `EnemyStatusData + 0x80`.

---

## 1. What Exactly is the Word at Offset 0x80?

### Function Address
- `0x558180` (lines `0x558517 - 0x5586fa`).

### Proving Assembly Instructions
```x86asm
00558517  mov      esi, dword ptr [eax + 0x98]       ; [code] eax = EnemyStatusData in memory (offset in file = 0x98 - 0x18 = 0x80)
0055851d  mov      dword ptr [ebp - 0x2c], esi       ; [code] store slot count N
00558520  test     esi, esi                          ; [code] check if N == 0
00558522  je       0x558510                          ; [code] if 0, branch to drop nothing
...
0055853d  lea      edx, [esi*4]                      ; [code] edx = N * 4 bytes
00558544  mov      ecx, 0x10
00558549  call     0x5c2660                          ; [code] malloc(N * 4): allocates temporary weights array
00558553  mov      dword ptr [ebp + 0x10], eax       ; [code] store weights array pointer
...
; Loop reading weights for the N slots (esi = 0 .. N-1, edi increments by 0xC each step):
00558570  mov      ecx, dword ptr [0x7389d8]         ; [code] EnemyStatusData map
00558576  lea      eax, [ebp - 0x30]
0055857e  call     0x507310                          ; [code] map lookup
00558586  lea      edi, [edi + 0xc]                  ; [code] edi += 12 bytes per slot
00558589  mov      eax, dword ptr [eax]
0055858b  mov      eax, dword ptr [edi + eax + 0x98] ; [code] reads weight from memory (eax + 0x98 + 0xC*(esi+1))
                                                     ;        slot 0: file 0x8C; slot 1: file 0x98; slot 2: file 0xA4
00558592  mov      dword ptr [ecx + esi*4], eax      ; [code] store weight in array
00558595  inc      esi
00558596  cmp      esi, ebx
00558598  jb       0x558570
...
005585a0  mov      edx, dword ptr [ebp - 0x2c]       ; [code] count of weights N
005585a3  mov      esi, dword ptr [ebp + 0x10]       ; [code] array of weights
005585a6  mov      ecx, esi
005585a8  call     0x505ad0                          ; [code] weighted selection roll (returns winning slot k in eax)
...
005585b3  mov      dword ptr [ebp - 0x2c], eax       ; [code] k = winning slot index (0, 1, or 2)
005585c4  call     0x507310                          ; [code] reload EnemyStatusData
005585cc  mov      eax, dword ptr [eax]
005585ce  lea      ecx, [ecx + ecx*2]                ; [code] ecx = k * 3 (dword offset = k * 12 bytes)
005585d1  cmp      dword ptr [eax + ecx*4 + 0x9c], 0 ; [code] check slot flag: memory 0x9c + k*12 (file 0x84 + k*12)
005585d9  je       0x558699                          ; [code] if flag == 0 -> Fixed equipment piece
                                                     ;        if flag != 0 -> Zone equipment draw (call 0x555c70)
```

### Analysis of the Data Structure
In `EnemyStatusData`:
- `0x80`: 32-bit integer indicating the **number of candidate equipment slots** (0, 1, 2, or 3).
- Following `0x80`, each slot `k` consists of 12 bytes (three 32-bit integers):
  - `Slot 0`: `0x84` (flag), `0x88` (equip_id or kind), `0x8C` (weight).
  - `Slot 1`: `0x90` (flag), `0x94` (equip_id or kind), `0x98` (weight).
  - `Slot 2`: `0x9C` (flag), `0xA0` (equip_id or kind), `0xA4` (weight).
- If `flag == 0`:
  `005586c0`: `mov eax, dword ptr [eax + ecx*4 + 0xa0]` reads the value at `0x88 + k*12` as a **fixed equipment ID**, and `005586e9 call 0x4e0bf0` creates that exact equipment item.
- If `flag == 1`:
  `0055860d`: `push dword ptr [eax + edx*4 + 0xa0]` pushes the value at `0x88 + k*12` as the **zone drop kind** (column 0, 1, 2, or 3 of the floor table), passing it to `0x555c70` along with the cell's zone index.

### One-Sentence Conclusion
The word at file offset `0x80` is the **number of candidate equipment slots** (0 to 3) defined for the enemy, which determines how many 12-byte `(flag, id_or_kind, weight)` tuples are read from `0x84` onward for a weighted draw.

---

## 2. How Equipment is Chosen from the Zone Table

### Function Address
- `0x555c70` (`Dungeon::SelectZoneEquipment`).

### Proving Assembly Instructions
```x86asm
; Arguments: [ebp + 8] = out struct, [ebp + 0xc] = zone index, [ebp + 0x10] = drop kind (0-3)
00555c7b  imul     esi, dword ptr [ebp + 0xc], 0xd0   ; [code] zone offset = zone_idx * 0xD0 (ZONE_SIZE)
00555c94  mov      eax, dword ptr [edi + 4]
00555c97  mov      eax, dword ptr [eax + 0xa0]        ; [code] zone array pointer (ZONE_POINTER = 0xA0)
00555c9d  mov      ebx, dword ptr [eax + esi + 0x68]  ; [code] ebx = EQUIPMENT_COUNT (offset 0x68 of zone)
...
00555cb3  lea      edx, [ebx*4]
00555cbf  call     0x5c2660                           ; [code] malloc(ebx * 4): candidate indices buffer
...
; Loop through all ebx equipment records of the zone (each 36 bytes / 0x24):
00555ce7  mov      eax, dword ptr [eax + edi + 0x70]  ; [code] equipment records pointer (EQUIPMENT_POINTER = 0x70)
00555cf1  mov      edi, dword ptr [ebp + 0x10]        ; [code] edi = drop kind k (0-3)
00555cf4  add      eax, esi                           ; [code] current record pointer (esi += 0x24 each step)
00555cf6  cmp      dword ptr [eax + edi*8 + 4], 0     ; [code] checks min_level for kind k: record + 4 + k*8
00555cff  jle      0x555d09                           ; [code] if min_level <= 0, candidate excluded
00555d01  mov      eax, dword ptr [esp + 0x14]        ; [code] candidate buffer
00555d05  mov      dword ptr [eax + edx*4], ecx       ; [code] candidate_buffer[matching_count] = record_idx
00555d08  inc      edx                                ; [code] matching_count++
00555d09  inc      ecx
00555d0a  add      esi, 0x24                          ; [code] advance to next 36-byte equipment record
00555d0d  cmp      ecx, ebx
00555d0f  jb       0x555ce0
...
; Uniform selection among all matching pieces:
00555d15  mov      ecx, dword ptr [0x816ce8]          ; [code] RNG instance
00555d1b  push     edx                                ; [code] push matching_count
00555d1c  call     0x490790                           ; [code] uniform random integer in [0, matching_count - 1]
00555d21  mov      ebx, dword ptr [esp + 0x14]
00555d30  mov      eax, dword ptr [ebx + eax*4]       ; [code] selected record index
00555d33  lea      edx, [eax + eax*8]; shl edx, 2     ; [code] edx = selected_idx * 36 (0x24)
00555d4e  mov      eax, dword ptr [edx + eax]         ; [code] reads equipment ID at record + 0x00
00555d51  mov      dword ptr [esp + 0x20], eax        ; [code] store chosen equipment ID
...
; Upgrade level selection between min_level and max_level:
00555d88  lea      eax, [eax + ecx*8]                 ; [code] record + k*8
00555d8b  mov      esi, dword ptr [eax + edx + 4]     ; [code] esi = min_level
00555d8f  mov      eax, dword ptr [eax + edx + 8]     ; [code] eax = max_level
00555d9b  mov      ecx, dword ptr [0x816ce8]
00555da1  sub      eax, esi                           ; [code] diff = max_level - min_level
00555da3  inc      eax                                ; [code] span = diff + 1
00555da4  push     eax
00555da5  call     0x490790                           ; [code] uniform random integer in [0, span - 1]
00555daa  add      eax, esi                           ; [code] final_level = min_level + random_offset
00555dac  mov      dword ptr [esp + 0x24], eax        ; [code] store upgrade level
```

### One-Sentence Conclusion
Inside the zone table, every equipment piece with `min_level > 0` for the specified kind has **equal weight** (`1 / matching_count`), and its upgrade level is chosen **uniformly at random** between `min_level` and `max_level` inclusive.

---

## 3. Where the "1%" or "2%" in Guides Comes From

### Findings from the Executable and Data
1. **No Hardcoded 1% or 2% Constants**:
   There is no constant `1%` or `2%` anywhere in the executable's drop logic (`0x558180` or `0x555c70`), nor does any enemy status file contain a literal 1 or 2 as an equipment drop chance.
2. **Mathematical Compound Result of Regular Mobs**:
   For regular enemies that possess a rare fixed equipment drop alongside zone drops:
   - **Garasha (ID 6)**:
     - Stage 1 equipment drop chance (`0x7C`): `16%`.
     - Stage 2 slot weights: Slot 0 (Chief's Special, equip ID 339) weight `5`, Slot 1 (Zone kind 0) weight `95`.
     - Exact drop probability: `16% * (5 / 100) = 0.8%` (frequently rounded to **~1%** in player guides).
   - **Thor (ID 236)**:
     - `0x7C`: `17%`. Slot 0 (equip 223) weight `6`, Slot 1 (equip 764) weight `8`, Slot 2 (zone) weight `86`.
     - Exact drop probabilities: `17% * 6% = 1.02%` (**~1%**) and `17% * 8% = 1.36%` (**~1%**).
   - **Shanina (ID 65)**:
     - `0x7C`: `25%`. Slot 1 (equip 340) weight `6` -> `25% * 6% = 1.5%` (**~1-2%**).
   - **Knuckle Saint (ID 732)**:
     - `0x7C`: `15%`. Slot 1 (equip 761) weight `6` -> `15% * 6% = 0.9%` (**~1%**).
   - **Cat's Eye (ID 212)**:
     - `0x7C`: `13%`. Slot 0 (equip 656) weight `7` -> `13% * 7% = 0.91%` (**~1%**).
   - **Floor Table Dilution**:
     Drawing from the zone table (e.g. Garasha's Slot 1) divides the probability across the ~15 to 29 valid pieces (`1 / N`), yielding `16% * 95% * (1 / 16) = 0.95%` (~1%) for any single piece from the floor table.
3. **The Boss Misconception**:
   In older tooling (e.g. `mod_project/scratch/check_rare_drops.py`), `EnemyStatusData + 0x80` was mistakenly interpreted as a percentage drop rate because its values were `1` and `2`:
   ```python
   # From mod_project/scratch/check_rare_drops.py:
   if eq and eq[1] in [1, 2] and e.get('level', 0) >= 50:
       rare_drops.append((e['id'], e['name'], e['level'], eq[0], eq[1]))
   ```
   In reality, `0x80` is the **slot count**!
   For the 13 fixed bosses (Overdue, Azathoth, Last Judgment, etc.), `0x80 = 1` simply means they have **1 slot**, and that single slot has weight `100`, with `0x7C = 100`.
   Thus, **their rare equipment drop is 100% guaranteed upon defeat in the vanilla binary**, not 1% or 2%.

### One-Sentence Conclusion
The "1%" or "2%" cited in guides is not a data field, but rather the mathematical product of the two-stage roll `P(equipment) * (slot_weight / total_weight)` for standard rare mobs (e.g., Garasha's `16% * 5% = 0.8%`), compounded by a community misconception that confused the slot count word at `0x80` (values 1 and 2) with a percentage.

---

## 4. Data Levers to Increase Rare Equipment Drop Probability

### Available Data Fields in `EnemyStatusData.bin`
1. **`0x7C` (int32)**: Base Equipment Drop Chance in percent.
   - Evaluated in Stage 1 at `00558331`.
   - Used range across game enemies: `0` to `100` (e.g. 100 on bosses, 60 on Crom Cruach, 30 on riders, 16 on Garasha/Ryoma).
2. **`0x8C` (int32)**: Weight of Slot 0 in Stage 2.
   - Evaluated in Stage 2 at `0055858b` and `005585a8`.
   - Used range across game enemies: `5` to `100`.
3. **`0x98` (int32)**: Weight of Slot 1 in Stage 2 (for multi-slot enemies).

### Analysis of the 15 Target Enemies
- **13 Bosses** (Overdue, Azathoth, Last Judgment, Hell's Angel, Samael, Melek Taus, Sukuna-Hikona, Genbu, Iktomi, Murasaki Shikibu, Qitian Dasheng, Nuwa, Kuchinawa):
  - In vanilla data, they have `item_count = 0` at `0x68`, `0x7C = 100`, and `0x80 = 1` slot with `weight = 100` (at `0x8C`) for their fixed equipment item (`flag = 0`).
  - Their drop probability is already `100% * (100 / 100) = 100%`.
  - **There is no data lever to raise their drop chance because it is already guaranteed (100%) in vanilla.**
- **Garasha (ID 6)**:
  - Rare piece: **Chief's Special** (Equip ID 339).
  - Current data: `0x7C = 16`, `0x80 = 2`, Slot 0 weight (`0x8C`) = `5`, Slot 1 weight (`0x98`) = `95`.
  - Current probability: `16% * (5 / 100) = 0.8%`.
  - Levers:
    - Increase Slot 0 weight at `0x8C` from `5` to `50` (or `100`).
    - Increase base equipment chance at `0x7C` from `16` to `50` (or `100`).
- **Ryoma (ID 7)**:
  - Rare piece: **Sudarshana** (Equip ID 418).
  - Current data: `0x7C = 16`, `0x80 = 2`, Slot 0 weight (`0x8C`) = `20`, Slot 1 weight (`0x98`) = `80`.
  - Current probability: `16% * (20 / 100) = 3.2%`.
  - Levers:
    - Increase Slot 0 weight at `0x8C` from `20` to `50` (or `100`).
    - Increase base equipment chance at `0x7C` from `16` to `50` (or `100`).

---

## 5. Summary Table for the 15 Enemies

| Enemy ID | Enemy Name | Rare Equipment Item | Current Data & Weights | Current Drop Rate | Proposed Data Lever & Value | Status / Notes |
|:---:|:---|:---|:---|:---:|:---|:---|
| **331** | Overdue | Mimic Helm (612) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **751** | Azathoth | Dark Crown (610) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **862** | Last Judgment | Conclusive Trumpet (524) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **921** | Hell's Angel | Galvorn Armor (678) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **951** | Samael | Angel Halo (616) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **955** | Melek Taus | God Destroyer (118) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **775** | Sukuna-Hikona | Sukunahikona Bow (297) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **801** | Genbu | Souryu Oven Mitts (756) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **712** | Iktomi | Wasp Chanchanko (664) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **722** | Murasaki Shikibu | Murasaki's Sleeves (673) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **848** | Qitian Dasheng | Ruyi Jingu Bang (193) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **887** | Nuwa | White Mask (611) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **890** | Kuchinawa | Kuchinawa's Cleaver (139) | `0x7C=100`, `0x80=1`, Slot 0 wt (`0x8C`)=100 | **100%** | *No data lever* (already 100%) | [code] 100% guaranteed drop |
| **6** | Garasha | Chief's Special (339) | `0x7C=16`, `0x80=2`, Slot 0 wt (`0x8C`)=5, Slot 1 wt (`0x98`)=95 | **0.8%** | `0x8C`: change from `5` to `50` (or `100`), and/or `0x7C`: change from `16` to `50` (or `100`) | [code] Multi-slot mob drop; [inference] proposed reasonable buff: `0x8C = 50`, `0x7C = 50` (25% total drop) |
| **7** | Ryoma | Sudarshana (418) | `0x7C=16`, `0x80=2`, Slot 0 wt (`0x8C`)=20, Slot 1 wt (`0x98`)=80 | **3.2%** | `0x8C`: change from `20` to `50` (or `100`), and/or `0x7C`: change from `16` to `50` (or `100`) | [code] Multi-slot mob drop; [inference] proposed reasonable buff: `0x8C = 50`, `0x7C = 50` (25% total drop) |

### Notation Tags
- **[code]**: Directly verified in the disassembly of `DT22_en_unwrapped.exe` (`0x558180`, `0x555c70`, `0x505ad0`) and extracted from `EnemyStatusData.bin` records.
- **[inference]**: The proposed replacement numbers (e.g., 50 or 100) are recommended tuning options within vanilla data ranges; the mathematical explanation for the guides' "1%" and "2%" is deduced by reconciling code drop rates with player guide terminology and the prior tooling artifact (`check_rare_drops.py`).

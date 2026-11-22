# M11 — Unit Build, Growth, Unarmed Rank, Caps & EXP/SP Curves (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x43a4a0..0x55d89b`)**
> Target executable: `backups/exe/DT22_en_unwrapped.vanilla.exe` (x86-32, image base `0x400000`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`).
> Raw data sources: `backups/ClassLevelData.pck`, `backups/ClassData.pck`, `backups/Character/Character.pck`, `backups/WeaponRankData.pck`, `backups/EquipmentData.pck`, `backups/EnchantData.pck`, `backups/LvExpSkptData.pck`, `backups/Enemy/Enemy.pck`.
> Rounding notation: `trunc0(x)` = SSE `cvttss2si` / `__ftol2_sse` (`0x61d550`, truncation toward zero); `round_f32_to_i32(x)` = helper `0x61e650`; signed integer division via magic multiplier `imul; sar; shr 0x1f; add` = truncation toward zero (`/`).

---

## 1. Character/Class Base Stats, Level Growth, Class Change & Crown Reset

### M11.01 `ClassLevelData.pck`, `ClassData.pck`, `Character.pck` Binary Layouts & `GetClassLevelID` (`0x5545b0`)

- **Binary VA(s):** `0x5545b0..0x55477b` (`Parameter::CParameterClassLevel::GetClassLevelID` + 32-entry jump table `0x5546fc`), `0x5540a0..0x5540ff` (`ClassLevelData` loader `[0x7389c0]`), `0x553a70..0x553c25` (`ClassData` loader `[0x7389bc]`), `0x4f5650..0x4f5c11` (`Character` initialization from `[0x7389b8]` / `[0x738a08]`)
- **Calls:** `0x507310` (RB-tree lookup), `0x554210` (RB-tree insert)
- **CalledBy:** `M11.02` (`0x4f5d82`), `M11.03`, `M11.06` (`0x4f5572`)
- **Typed Pseudocode:**
```text
// 1. Canonical 14-stat vector layout shared across CGameStatusBase (+0x1c Base, +0x54 Cur):
//    idx 0 (+0x1c/+0x54): ATK          idx 6  (+0x34/+0x6c): Slash Resist
//    idx 1 (+0x20/+0x58): DEF          idx 7  (+0x38/+0x70): Stab Resist
//    idx 2 (+0x24/+0x5c): INT          idx 8  (+0x3c/+0x74): Bash Resist
//    idx 3 (+0x28/+0x60): RES          idx 9  (+0x40/+0x78): Fire Resist
//    idx 4 (+0x2c/+0x64): DEX          idx 10 (+0x44/+0x7c): Water Resist
//    idx 5 (+0x30/+0x68): AGI          idx 11 (+0x48/+0x80): Wind Resist
//    (MaxHP = +0x10, CurHP = +0x0c)    idx 12 (+0x4c/+0x84): Earth Resist
//    (MaxTP = +0x18, CurTP = +0x14)    idx 13 (+0x50/+0x88): Lightning Resist
//
// 2. ClassLevelData.pck ([0x7389c0]): 38 records (IDs 0..37), 3,172 bytes (0xc64, 0x319 dwords) each:
//    +0x000: u32 classLevelId (0..37)
//    +0x004 + (lv - 1) * 0x20 (for lv in 1..99):
//        u32[8] = { HP, TP, ATK, DEF, INT, RES, DEX, AGI }
//    Loaded verbatim into RB-tree node (size 0xc78) at node+0x14 (key at node+0x10).
//    Therefore for 1-based lv, node + (lv << 5) - 8 = HP, -4 = TP, +0..+0x14 = ATK..AGI.
//
// 3. ClassData.pck ([0x7389bc]): 49 records (IDs 0..31 playable, 32..48 NPC/Summon/Guest):
//    +0x00: u32 classId               +0x10: u32 fullNameOffset
//    +0x08: u32 shortCodeOffset       +0x20: u32 tier (1, 2, or 3)
//    +0x24: u32 unarmedRankId (1..5)  -> copied verbatim to RB-tree node+0x3c (0x553ac8)
//
// 4. Character/Character.pck: 19 nested .pck entries (0000.pck..0018.pck), each containing:
//    - InitialData.bin ([0x7389b8], 64 bytes): +0x00 charId, +0x04 initClassId (node+0x18),
//      +0x08 initPrevClassId (node+0x1c), +0x0c initExp (node+0x20),
//      +0x10/+0x14.. initial equipment IDs & forge levels.
//    - PlayerStatusData.bin ([0x738a08], 144 bytes): +0x00 charId, +0x04 tier1BaseClassId (node+0x18),
//      +0x3c..+0x5c f32 motivation delta table (node+0x50 + eventIdx*4).

function CParameterClassLevel_GetClassLevelID(nowClass: u32, prevClass: u32) -> u32:
    // 0x5545b0..0x5546e2: 32-entry jump table at 0x5546fc; asserts if nowClass > 31 (0x1f).
    // Six Tier-3 classes have dual Tier-2 parents and select distinct growth tables via prevClass:
    //   nowClass == 4  (Samurai):          prevClass == 1 (PL) -> 4;  prevClass == 2 (BE) -> 5;  else -> 4
    //   nowClass == 10 (Treasure Hunter):  prevClass == 7 (AR) -> 11; prevClass == 8 (AS) -> 12; else -> 11
    //   nowClass == 17 (Magical Princess): prevClass == 13 (SO)-> 19; prevClass == 14 (EN)-> 20; else -> 19
    //   nowClass == 18 (Sage):             prevClass == 14 (EN)-> 21; prevClass == 15 (PR)-> 22; else -> 21
    //   nowClass == 24 (Mistress):         prevClass == 21 (BD)-> 28; prevClass == 22 (DN)-> 29; else -> 28
    //   nowClass == 30 (Papillon):         prevClass == 27 (DM)-> 35; prevClass == 28 (TS)-> 36; else -> 35
    // All other 26 playable classes map 1-to-1 to their fixed table ID in 0..37.
    // RNG calls: 0.
    return CLASS_LEVEL_ID_MAP[nowClass, prevClass]
```

| `nowClass` | Code & Name | `prevClass` | `ClassLevelID` | `nowClass` | Code & Name | `prevClass` | `ClassLevelID` |
|---:|---|---:|---:|---:|---|---:|---:|
| `0` | `FT` Fighter | any | `0` | `17` | `MP` Magical Princess | `13` (`SO`) / `14` (`EN`) | `19` / `20` |
| `1` | `PL` Paladin | any | `1` | `18` | `SG` Sage | `14` (`EN`) / `15` (`PR`) | `21` / `22` |
| `2` | `BE` Berserker | any | `2` | `19` | `BS` Bishop | any | `23` |
| `3` | `VL` Valkyrie | any | `3` | `20` | `MA` Maid | any | `24` |
| `4` | `SA` Samurai | `1` (`PL`) / `2` (`BE`) | `4` / `5` | `21` | `BD` Bard | any | `25` |
| `5` | `DL` Dark Lord | any | `6` | `22` | `DN` Dancer | any | `26` |
| `6` | `SC` Scout | any | `7` | `23` | `DI` Diva | any | `27` |
| `7` | `AR` Archer | any | `8` | `24` | `MI` Mistress | `21` (`BD`) / `22` (`DN`) | `28` / `29` |
| `8` | `AS` Assassin | any | `9` | `25` | `ET` Etoile | any | `30` |
| `9` | `SN` Sniper | any | `10` | `26` | `SP` Spieler | any | `31` |
| `10` | `TH` Treasure Hunter | `7` (`AR`) / `8` (`AS`) | `11` / `12` | `27` | `DM` Doll Master | any | `32` |
| `11` | `KN` Kunoichi | any | `13` | `28` | `TS` Trickster | any | `33` |
| `12` | `MU` Magic User | any | `14` | `29` | `SS` Soul Summoner | any | `34` |
| `13` | `SO` Sorceress | any | `15` | `30` | `PA` Papillon | `27` (`DM`) / `28` (`TS`) | `35` / `36` |
| `14` | `EN` Enchantress | any | `16` | `31` | `JO` Joker | any | `37` |
| `15` | `PR` Priestess | any | `17` | — | — | — | — |
| `16` | `WT` Witch | any | `18` | — | — | — | — |

- **Program Evidence:**
```asm
005545b0  cmp      ecx, 0x1f
005545b3  ja       0x5546e3
005545b9  jmp      dword ptr [ecx*4 + 0x5546fc]
005545d5  cmp      edx, 1
005545d8  jne      0x5545e0
005545da  mov      eax, 4
005545df  ret      
005545e0  xor      eax, eax
005545e2  cmp      edx, 2
005545e5  sete     al
005545e8  add      eax, 4
005545eb  ret      
005540e0  mov      ecx, 0x319
005540e9  rep movsd dword ptr es:[edi], dword ptr [esi]
00553ac8  movq     xmm0, qword ptr [edi + 0x20]
```

---

### M11.02 Player Stat Recalculation Spine (`0x4f7c00`) & Base + Growth + Crown Formula (`0x4f5d60`)

- **Binary VA(s):** `0x4f7c00..0x4f7c69` (`CGamePlayerStatus::Recalculate`, `vtable+0x108`), `0x4f5d60..0x4f5f9a` (`CGamePlayerStatusBase::_CalculateBaseParameter`, `vtable+0x104`)
- **Calls:** `0x5545b0` (`M11.01`), `0x4f7c70` (`M11.04`), `0x4f6530` (`M11.05`), `0x4f8270` (`M11.08`), `0x4fbdd0` (`M11.09`), `0x4f8fe0` (`M11.09`), `0x4fc620` (`M11.09`)
- **CalledBy:** `SetLevel` (`0x4f97c9`), `SetHP` (`0x4f9810`), `AddHP` (`0x4f9847`), `AddTP` (`0x4f98a4`), `ClassChange` (`0x4f4f0c`), `_SetupEnchant` (`0x4f6487` / `0x4f7bef`), `AddMotivation` (`0x4f542d`), `AddStatus` (`M00.08`)
- **Typed Pseudocode:**
```text
function CGamePlayerStatus_Recalculate(this: CGamePlayerStatus*):
    // 0x4f7c00..0x4f7c69 (vtable+0x108): Early-out if temporary/locked flag is active.
    if this.vtable_0x16c() != 0 or this.lockRecalcFlag_0x160 != 0:
        return
    this.vtable_0x104_CalculateBaseParameter()             // Stage 1: 0x4f5d60 (Base + Growth + Crown)
    baseMaxHp: i32 = this.maxHp                            // [this+0x10] saved in edi
    baseMaxTp: i32 = this.maxTp                            // [this+0x18] saved in esi
    this.vtable_0x18c_CalculateParameterSpecialty()        // Stage 2: 0x4f7c70 (Class Specialty, pre-equip Cur==Base!)
    this._CalculateParameterEquipment()                    // Stage 3: 0x4f6530 (Equipment + Passives 243/298)
    this.vtable_0x180_CalculateParameterEnchant(baseMaxHp, baseMaxTp) // Stage 4: 0x4f8270 (Enchants)
    this.vtable_0x10c_CalculateParameterStatus(baseMaxHp, baseMaxTp)  // Stage 5: 0x4fbdd0 (Statuses + DualWield 256)
    this._CalculatePartySkillSynergy()                     // Stage 6: 0x4f8fe0 (Party-Skill passives 360..377/405/415)
    this.vtable_0x110_ClampParameter()                     // Stage 7: 0x4fc620 (Hard caps + 416..423 overwrites)
    // RNG calls: 0.

function CGamePlayerStatusBase_CalculateBaseParameter(this: CGamePlayerStatusBase*):
    // 0x4f5d60..0x4f5f9a (vtable+0x104):
    nowClass: u32  = this.vtable_0x13c(0)                  // [this+0xa0]
    prevClass: u32 = this.prevClassId                      // [this+0xa4]
    tableId: u32   = GetClassLevelID(nowClass, prevClass)  // 0x5545b0
    row: ClassLevelRow* = ClassLevelData_0x7389c0[tableId]
    lv: u32        = this.level                            // [this+0x04] (1..99)
    crown: i32     = this.crownBonus                       // [this+0x120] (0..50)
    // charBonus[0..15] lives at [this+0xdc .. this+0x118] (persistent book/sub-event flat bonuses):
    this.maxHp = row.lv[lv].hp + this.charBonusHp_0xdc + crown          // [this+0x10]
    this.maxTp = row.lv[lv].tp + this.charBonusTp_0xe0 + crown          // [this+0x18]
    for i in 0..5:                                                      // ATK, DEF, INT, RES, DEX, AGI
        val: i32 = row.lv[lv].stat[i] + this.charBonusStat[i] + crown   // [this+0xe4+i*4]
        this.baseStat[i] = val                                          // [this+0x1c+i*4]
        this.curStat[i]  = val                                          // [this+0x54+i*4]
    for r in 6..13:                                                     // 8 Resistances (Slash..Lightning)
        val: i32 = this.charBonusResist[r - 6] + crown                  // [this+0xfc+(r-6)*4] + crown!
        this.baseStat[r] = val                                          // [this+0x1c+r*4]
        this.curStat[r]  = val                                          // [this+0x54+r*4]
    // NOTE: Crown bonus ([this+0x120], 0..50) is added to MaxHP, MaxTP, ALL 6 stats, AND ALL 8 resistances!
    if cmd81 = this.vtable_0x48_GetCommand(0, 0x51):       // Command 81 (Pep Freeze)
        this.motivation_0xd8 = cmd81.vtable_0x2c_GetVal()  // Overwrites [this+0xd8] f32
    // RNG calls: 0.
```
- **Program Evidence:**
```asm
004f7c1f  call     dword ptr [eax + 0x104]
004f7c29  mov      edi, dword ptr [ebx + 0x10]
004f7c2c  mov      esi, dword ptr [ebx + 0x18]
004f7c2f  call     dword ptr [eax + 0x18c]
004f7c37  call     0x4f6530
004f7c42  call     dword ptr [eax + 0x180]
004f7c4e  call     dword ptr [eax + 0x10c]
004f7c56  call     0x4f8fe0
004f7c62  jmp      dword ptr [eax + 0x110]
004f5d82  call     0x5545b0
004f5da4  mov      esi, dword ptr [ebp + 4]
004f5dab  mov      ebp, dword ptr [ebp + 0x120]
004f5db3  shl      esi, 5
004f5dba  mov      eax, dword ptr [esi + eax - 8]
004f5dbe  add      eax, dword ptr [ecx + 0xdc]
004f5dc4  add      eax, ebp
004f5dc6  mov      dword ptr [ecx + 0x10], eax
004f5efe  mov      eax, dword ptr [ebx + 0xfc]
004f5f04  add      eax, ebp
004f5f06  mov      dword ptr [ebx + 0x6c], eax
```

---

### M11.03 Class Change (`0x4f4e80`), Level Reset (`0x4f5650` / `0x523727` / `0x5245d0`) & Crown Reset Steps (`0x4f94f0`, Vanilla `X09..X12`)

- **Binary VA(s):** `0x4f4e80..0x4f4f15` (`CGamePlayerStatusBase::SetClass`, `vtable+0x140`), `0x523727..0x5237bf` (`CMenuLevelReset` candidate levels), `0x5245d0..0x524630` (Guild level-reset executor), `0x4f7680..0x4f76f0` (`CGamePlayerStatus::Reset`, `vtable+0x168`), `0x4f5650..0x4f5c0f` (`CGamePlayerStatusBase::_Reset`), `0x4f94f0..0x4f9552` (`CGamePlayerStatus::_AddCrown`, `vtable+0x188`; Vanilla `X09..X12` at `0x4f9502..0x4f952c`)
- **Calls:** `0x55c100` (`M11.10`), `0x4f94f0` (`vtable+0x188`), `0x4f7ac0` (`M11.07`), `0x4f7c00` (`M11.02`), `0x4f55f0` (reset counter)
- **CalledBy:** Guild Class Change UI (`0x51defc`), Guild Level Reset UI (`0x52461e`), Character init (`0x4f7786`)
- **Typed Pseudocode:**
```text
function CGamePlayerStatusBase_SetClass(this: CGamePlayerStatusBase*, newClassId: u32):
    // 0x4f4e80..0x4f4f15 (vtable+0x140):
    oldClass: u32 = this.vtable_0x13c(0)
    if newClassId != oldClass:
        this.prevClassId = oldClass                        // [this+0xa4] = oldClass
        this.nowClassId  = newClassId                      // [this+0xa0] = newClassId
    this.vtable_0x160_UnlockClassSkills(this.nowClassId)   // 0x4f7320
    this.classHistoryBitmask_0x140_0x144 |= (1u64 << newClassId)
    this.vtable_0x108_Recalculate()                        // 0x4f7c00
    // RNG calls: 0.

function CMenuLevelReset_BuildTargetLevels(curLevel: u32) -> list<u32>:
    // 0x523727..0x5237bf:
    targets = []
    if curLevel >  1:  targets.push(1)                     // cmp esi, 1; jbe skip (strict > 1)
    if curLevel >= 15: targets.push(15)                    // 0x0f (jb skip -> allows Lv15 -> Lv15!)
    if curLevel >= 30: targets.push(30)                    // 0x1e
    if curLevel >= 50: targets.push(50)                    // 0x32
    if curLevel >= 75: targets.push(75)                    // 0x4b
    if curLevel >= 90: targets.push(90)                    // 0x5a
    return targets

function ExecuteLevelReset(player: CGamePlayerStatus*, targetLevel: u32):
    // 0x524604..0x52462a -> 0x4f7680 -> 0x4f5650(isReset=true, oldLevel):
    oldLevel: u32 = player.vtable_0x10_GetLevel()
    player.vtable_0x0c_SetLevel(targetLevel)               // Sets [player+0x04] = targetLevel & recalcs
    // Inside 0x4f5650(isReset=1, oldLevel) (0x4f5a49..0x4f5baa):
    player.exp = LvExpSkptData_GetTotalExp(player.level)   // 0x55c100 -> [player+0x08]
    player.nowClassId  = PlayerStatusData_0x738a08[player.charId].tier1BaseClass // [player+0xa0]
    player.prevClassId = 0xffffffffu32                     // [player+0xa4] = -1
    player.learnedSkills.clear()                           // [player+0xc4] = [player+0xc0]
    player.vtable_0x188_AddCrown(oldLevel)                 // 0x4f94f0 (X09..X12)
    player.vtable_0x6c_ClearStatuses(0, 0)
    player.vtable_0x160_UnlockClassSkills(player.nowClassId)
    // Rebuild available SP from scratch (0x4f5b27..0x4f5b87):
    spSum: u32 = 0
    for lv in 1 .. player.level:                           // inclusive 1..targetLevel
        spSum += LvExpSkptData_0x7389fc[lv].spDelta        // [node+0x1c]
    player.availableSp = player.bonusSp_0x11c + spSum      // [player+0x124] (unclamped on reset)
    player.vtable_0x178_SetupEnchant()                     // 0x4f7ac0
    player.vtable_0x108_Recalculate()                      // 0x4f7c00
    player.curHp = player.maxHp; player.curTp = player.maxTp
    player.vtable_0x164_IncResetCount(1)                   // 0x4f55f0: [player+0x138] sat_add 1
    // Note: Trophy 0x2a (42) triggers in 0x4f76a1..0x4f76e6 if crown crosses from < 50 to >= 50.
    // RNG calls: 0.

function CGamePlayerStatus_AddCrown(this: CGamePlayerStatus*, oldLevel: u32):
    // 0x4f94f0..0x4f9552 (vtable+0x188): Vanilla X09..X12 bytes live at 0x4f9502..0x4f9530.
    // Uses UNSIGNED subtraction & unsigned jb comparisons!
    diff: u32 = oldLevel - this.level                      // [esp+4] - [ecx+4]
    if      diff >= 98: this.crownBonus += 5               // 0x62 (e.g. Lv99 -> Lv1: diff=98)
    else if diff >= 89: this.crownBonus += 4               // 0x59 (e.g. Lv90 -> Lv1: diff=89) [X09]
    else if diff >= 79: this.crownBonus += 3               // 0x4f (e.g. Lv80 -> Lv1: diff=79) [X10]
    else if diff >= 69: this.crownBonus += 2               // 0x45 (e.g. Lv70 -> Lv1: diff=69) [X11]
    else if diff >= 59: this.crownBonus += 1               // 0x3b (e.g. Lv60 -> Lv1: diff=59) [X12]
    if this.crownBonus > 50:                               // signed cmovg against 0x32 (50)
        this.crownBonus = 50                               // [this+0x120] hard cap = 50
    // Crown grants NO extra SP directly; it adds +crownBonus (0..50) to HP, TP, 6 stats, and 8 resists (M11.02).
    // RNG calls: 0.
```
- **Program Evidence:**
```asm
004f94f0  mov      eax, dword ptr [esp + 4]
004f94f4  sub      eax, dword ptr [ecx + 4]
004f94f7  cmp      eax, 0x62
004f94fa  jb       0x4f9505
004f94fc  add      dword ptr [ecx + 0x120], 5
004f9505  cmp      eax, 0x59
004f950a  add      dword ptr [ecx + 0x120], 4
004f9513  cmp      eax, 0x4f
004f9518  add      dword ptr [ecx + 0x120], 3
004f9521  cmp      eax, 0x45
004f9526  add      dword ptr [ecx + 0x120], 2
004f952f  cmp      eax, 0x3b
004f9534  inc      dword ptr [ecx + 0x120]
004f9540  mov      edx, 0x32
004f9545  cmp      eax, edx
004f9547  cmovg    eax, edx
004f954a  mov      dword ptr [ecx + 0x120], eax
00523729  cmp      esi, 1
0052372c  jbe      0x523741
00523741  cmp      esi, 0xf
00523759  cmp      esi, 0x1e
00523771  cmp      esi, 0x32
00523789  cmp      esi, 0x4b
005237a1  cmp      esi, 0x5a
```

---

## 2. Class Modifiers Table (`0x4f81e8` / `.rdata` `0x6d3b64..0x6d40a0`)

### M11.04 Class Specialty Modifiers (`_CalculateParameterSpecialty` `0x4f7c70`, Jump Table `0x4f81e8` & `.rdata` `0x6d3b64..0x6d40a0`)

- **Binary VA(s):** `0x4f7c70..0x4f81e5` (`Game::CGamePlayerStatus::_CalculateParameterSpecialty`, `vtable+0x18c`), `0x4f81e8..0x4f8267` (32-entry jump table), `0x6d3b64..0x6d40ab` (38 `.rdata` specialty arrays, 12 bytes per entry)
- **Calls:** `0x61edf4` (`dynamic_cast<CGameArticleEquipment>`), `0x507310` (`EquipmentData` `[0x7389e0]`), `0x4e12a0..0x4e1570` (`M11.05`), `vtable+0x34` (CurStat), `vtable+0x48(0, 0x1c1)` (Command `449` Yearning), `vtable+0xf0(0x108)` (Enchant `264`)
- **CalledBy:** **Sole call site:** `0x4f7c2f` inside `CGamePlayerStatus::Recalculate` (`M11.02`, Stage 2 — runs BEFORE `_CalculateParameterEquipment`, so `vtable+0x34` holds `BaseStat` = `ClassLevel + charBonus + crown`!). Zero other code references exist to `0x6d3b64..0x6d40ab`.
- **Typed Pseudocode:**
```text
// Binary layout of each 12-byte entry in .rdata 0x6d3b64..0x6d40ab:
//   struct SpecialtyEntry_s {
//       u32 slot;      // +0x00: 0=Mainhand, 1=Offhand(Shield), 2=Head, 3=Body, 4=Accessory
//       u32 subType;   // +0x04: for slot==0 matches EquipmentData+0x68 (weapon subtype); 0xffffffff otherwise
//       f32 rate;      // +0x08: base specialty fraction (e.g. 0.01f .. 0.05f)
//   };
// Weapon subtype IDs (EquipmentData+0x68): 0=Sword, 1=Dagger, 2=Axe, 3=Lance, 4=Mace, 5=Staff,
//   6=Tome, 7=Bow, 8=Katana/Tantou, 9=Darts/Thrown, 10=Whip, 11=Fan/Ougi, 12=Megaphone, 13=Instrument/Charumera.

function CGamePlayerStatus_CalculateParameterSpecialty(this: CGamePlayerStatus*):
    // 0x4f7c70..0x4f81a6 (vtable+0x18c):
    nowClass: u32 = this.vtable_0x13c(0)                   // Asserts if > 31 (0x1f)
    (entries: SpecialtyEntry_s*, count: u32) = LookupTable_0x4f81e8(nowClass, this.prevClassId_0xa4)
    // Note: For dual-parent Tier-3 classes (4, 10, 17, 18, 24, 30), if prevClassId matches neither
    // valid parent, count remains 0 (no specialty bonus applied).
    delta: i32[14] = { 0, ..., 0 }
    for k in 0 .. count - 1:
        e: SpecialtyEntry_s = entries[k]
        eq: CGameArticleEquipment* = dynamic_cast<CGameArticleEquipment>(this.equipSlot[e.slot]) // [this+e.slot*4+0xa8]
        if eq == null: continue
        if e.slot == 0:
            if EquipmentData_0x7389e0[eq.itemId].weaponSubType_0x68 != e.subType: continue
        else if e.slot == 1:
            if EquipmentData_0x7389e0[eq.itemId].equipType_0x38 != 1: continue // Must be Shield (type 1)
        else if e.slot not in {2, 3, 4}:
            assert("error.")
        // Effective rate & floor (0x4f7f6f..0x4f8012):
        cmd449Val: f32 = 0.0f
        if c = this.vtable_0x48_GetCommand(0, 0x1c1):      // Command 449 (Yearning)
            cmd449Val = c.vtable_0x2c_GetVal()
        rate: f32 = e.rate + cmd449Val * 0.01f             // 0x6d92d4 = 0.01f
        if this.vtable_0xf0_GetEnchantCount(0x108) != 0:   // Enchant 264 (Class weapon modifier 2% UP)
            rate += 0.02f                                  // 0x6d92e0 = 0.02f
        minBonus: i32 = trunc0(cmd449Val)                  // Floor = trunc0(cmd449Val) (0 if absent)
        // Applies ONLY to primary stats i = 0..5 (ATK, DEF, INT, RES, DEX, AGI) where eq.GetStat(i) > 0:
        for i in 0..5:
            eqStat: i32 = eq.GetStat(i)                    // 0x4e12a0..0x4e1570 (base + forge)
            if eqStat > 0:                                 // jle skip (0 or negative equip stat gets 0 bonus)
                // Because Stage 2 runs before Stage 3, vtable_0x34(i) == BaseStat[i] (pre-equip)!
                combined: i32 = this.vtable_0x34_GetCurStat(i) + eqStat
                raw: i32 = trunc0(f32(combined) * rate)
                delta[i] += max(minBonus, raw)             // cmovge
    for i in 0..13:
        this.curStat[i] += delta[i]                        // [this+0x54+i*4]
    // RNG calls: 0.
```

| `nowClass` | `prev` | `.rdata` VA | `N` | Specialty Entries `(slot, subType, rate)` |
|---:|---:|---|---:|---|
| `0` (`FT`) | — | `0x6d3b88` | 1 | `(0, 0:Sword, 0.01f)` |
| `1` (`PL`) | — | `0x6d3f38` | 3 | `(0, 0:Sword, 0.02f)`, `(0, 3:Lance, 0.03f)`, `(1, Shield, 0.02f)` |
| `2` (`BE`) | — | `0x6d3fbc` | 2 | `(0, 0:Sword, 0.02f)`, `(0, 2:Axe, 0.02f)` |
| `3` (`VL`) | — | `0x6d3b64` | 3 | `(0, 0:Sword, 0.03f)`, `(0, 3:Lance, 0.05f)`, `(1, Shield, 0.03f)` |
| `4` (`SA`) | `1` (`PL`) | `0x6d3bf4` | 3 | `(0, 0:Sword, 0.02f)`, `(1, Shield, 0.02f)`, `(0, 8:Katana, 0.03f)` |
| `4` (`SA`) | `2` (`BE`) | `0x6d3c6c` | 3 | `(0, 0:Sword, 0.02f)`, `(0, 2:Axe, 0.02f)`, `(0, 8:Katana, 0.03f)` |
| `5` (`DL`) | — | `0x6d3c3c` | 2 | `(0, 0:Sword, 0.02f)`, `(0, 2:Axe, 0.05f)` |
| `6` (`SC`) | — | `0x6d4040` | 2 | `(0, 1:Dagger, 0.01f)`, `(0, 7:Bow, 0.01f)` |
| `7` (`AR`) | — | `0x6d3f20` | 2 | `(0, 1:Dagger, 0.02f)`, `(0, 7:Bow, 0.03f)` |
| `8` (`AS`) | — | `0x6d4034` | 1 | `(0, 1:Dagger, 0.03f)` |
| `9` (`SN`) | — | `0x6d3ba0` | 2 | `(0, 1:Dagger, 0.02f)`, `(0, 7:Bow, 0.05f)` |
| `10` (`TH`) | `7` (`AR`) | `0x6d3f80` | 2 | `(0, 1:Dagger, 0.03f)`, `(0, 7:Bow, 0.03f)` |
| `10` (`TH`) | `8` (`AS`) | `0x6d3c90` | 3 | `(0, 1:Dagger, 0.05f)`, `(0, 7:Bow, 0.02f)`, `(0, 10:Whip, 0.03f)` |
| `11` (`KN`) | — | `0x6d3fec` | 3 | `(0, 1:Dagger, 0.03f)`, `(0, 8:Katana, 0.03f)`, `(0, 9:Darts, 0.02f)` |
| `12` (`MU`) | — | `0x6d3b94` | 1 | `(0, 5:Staff, 0.01f)` |
| `13` (`SO`) | — | `0x6d3efc` | 1 | `(0, 5:Staff, 0.02f)` |
| `14` (`EN`) | — | `0x6d4010` | 1 | `(0, 6:Tome, 0.02f)` |
| `15` (`PR`) | — | `0x6d4088` | 1 | `(0, 4:Mace, 0.02f)` |
| `16` (`WT`) | — | `0x6d3ecc` | 1 | `(0, 5:Staff, 0.05f)` |
| `17` (`MP`) | `13` (`SO`) | `0x6d3fd4` | 2 | `(0, 5:Staff, 0.02f)`, `(0, 0:Sword, 0.04f)` |
| `17` (`MP`) | `14` (`EN`) | `0x6d3cd8` | 2 | `(0, 6:Tome, 0.02f)`, `(0, 0:Sword, 0.04f)` |
| `18` (`SG`) | `14` (`EN`) | `0x6d401c` | 2 | `(0, 5:Staff, 0.02f)`, `(0, 6:Tome, 0.05f)` |
| `18` (`SG`) | `15` (`PR`) | `0x6d4070` | 2 | `(0, 5:Staff, 0.03f)`, `(0, 6:Tome, 0.03f)` |
| `19` (`BS`) | — | `0x6d3bb8` | 2 | `(0, 5:Staff, 0.02f)`, `(0, 4:Mace, 0.03f)` |
| `20` (`MA`) | — | `0x6d3be8` | 1 | `(4, Acc, 0.02f)` |
| `21` (`BD`) | — | `0x6d3eb4` | 2 | `(4, Acc, 0.02f)`, `(0, 12:Megaphone, 0.02f)` |
| `22` (`DN`) | — | `0x6d3c54` | 2 | `(4, Acc, 0.02f)`, `(0, 13:Instrument, 0.03f)` |
| `23` (`DI`) | — | `0x6d3bd0` | 2 | `(4, Acc, 0.02f)`, `(0, 12:Megaphone, 0.04f)` |
| `24` (`MI`) | `21` (`BD`) | `0x6d3c18` | 3 | `(4, Acc, 0.02f)`, `(0, 12:Megaphone, 0.02f)`, `(0, 10:Whip, 0.03f)` |
| `24` (`MI`) | `22` (`DN`) | `0x6d3f5c` | 3 | `(4, Acc, 0.02f)`, `(0, 13:Instrument, 0.02f)`, `(0, 10:Whip, 0.03f)` |
| `25` (`ET`) | — | `0x6d3f08` | 2 | `(4, Acc, 0.02f)`, `(0, 13:Instrument, 0.04f)` |
| `26` (`SP`) | — | `0x6d4094` | 2 | `(0, 1:Dagger, 0.01f)`, `(0, 9:Darts, 0.01f)` |
| `27` (`DM`) | — | `0x6d3cb4` | 3 | `(0, 1:Dagger, 0.01f)`, `(0, 9:Darts, 0.01f)`, `(0, 5:Staff, 0.01f)` |
| `28` (`TS`) | — | `0x6d3e9c` | 2 | `(0, 1:Dagger, 0.02f)`, `(0, 9:Darts, 0.02f)` |
| `29` (`SS`) | — | `0x6d4058` | 2 | `(0, 0:Sword, 0.03f)`, `(0, 5:Staff, 0.03f)` |
| `30` (`PA`) | `27` (`DM`) | `0x6d3f98` | 3 | `(0, 1:Dagger, 0.01f)`, `(0, 5:Staff, 0.02f)`, `(0, 11:Fan, 0.03f)` |
| `30` (`PA`) | `28` (`TS`) | `0x6d3ed8` | 3 | `(0, 1:Dagger, 0.02f)`, `(0, 9:Darts, 0.02f)`, `(0, 11:Fan, 0.03f)` |
| `31` (`JO`) | — | `0x6d3e84` | 2 | `(0, 10:Whip, 0.03f)`, `(0, 2:Axe, 0.04f)` |

- **Program Evidence:**
```asm
004f7c85  cmp      eax, 0x1f
004f7c88  ja       0x4f81a7
004f7c8e  jmp      dword ptr [eax*4 + 0x4f81e8]
004f7f25  cmp      ecx, dword ptr [eax + 0x68]
004f7f50  cmp      dword ptr [eax + 0x38], 1
004f7f78  push     0x1c1
004f7fa4  mulss    xmm0, dword ptr [0x6d92d4]    ; float 0.01
004f7fb0  push     0x108
004f7fd1  addss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
004f800e  cvttss2si ebp, xmm0
004f8012  call     0x4e12a0
004f8025  call     dword ptr [edx + 0x34]
004f8028  add      eax, dword ptr [esp + 0x1c]
004f8035  mulss    xmm0, dword ptr [esp + 0x10]
004f803b  cvttss2si ecx, xmm0
004f803f  cmp      ecx, ebp
004f8041  cmovge   eax, ecx
```

---

## 3. Equipment Aggregation, Weapon/Unarmed Rank, Dual-Wield/Sealbook, `%` Modifiers & Hard Caps

### M11.05 Equipment Stat Aggregation, Forge Growth (`0x4e12a0..0x4e15ef`) & Passives `243`/`298` (`0x4f6530`)

- **Binary VA(s):** `0x4e12a0..0x4e15ef` (`CGameArticleEquipment::GetATK/DEF/INT/RES/DEX/AGI`), `0x4f6530..0x4f6695` (`Game::CGamePlayerStatusBase::_CalculateParameterEquipment`)
- **Calls:** `0x507310` (`EquipmentData` `[0x7389e0]`), `0x61edf4` (`dynamic_cast`), `vtable+0x48` (Commands `0xf3` = 243, `0x12a` = 298)
- **CalledBy:** `M11.02` (`0x4f7c37`), `M11.04` (`0x4f8012..0x4f8139`)
- **Typed Pseudocode:**
```text
// EquipmentData.pck ([0x7389e0]) struct offsets (raw .pck offset + 0x18 RB-tree header):
//   +0x38 (raw +0x20): u32 equipType (0=Weapon, 1=Shield, 2=Hat, 3=Armor, 4=Accessory)
//   +0x3c..+0x50 (raw +0x24..+0x38): i32[6] baseStats { ATK, DEF, INT, RES, DEX, AGI }
//   +0x54 (raw +0x3c): f32 forgeGrowth (SINGLE shared float for ALL 6 stats!)
//   +0x64 (raw +0x4c): u32 weaponRankId (0..11; 0xffffffff for non-weapons)
//   +0x68 (raw +0x50): u32 weaponSubType (0..20 weapons; 21..24 Shield/Hat/Armor/Acc)

function CGameArticleEquipment_GetStat(this: CGameArticleEquipment*, statIdx: u32) -> i32:
    // 0x4e12a0 (ATK), 0x4e1330 (DEF), 0x4e13c0 (INT), 0x4e1450 (RES), 0x4e14e0 (DEX), 0x4e1570 (AGI):
    param = EquipmentData_0x7389e0[this.itemId]            // [this+0x70]
    base: i32 = param.baseStats[statIdx]                   // [param+0x3c + statIdx*4]
    if base == 0:
        return 0                                           // Zero base stat NEVER scales with forgeLevel!
    forgeLv: u32 = this.forgeLevel                         // [this+0x74] (u32 -> f64 -> f32)
    return base + trunc0(f32(forgeLv) * param.forgeGrowth_0x54)

function CGamePlayerStatusBase_CalculateParameterEquipment(this: CGamePlayerStatusBase*):
    // 0x4f6530..0x4f667c: Iterates all 6 equipment slots (0=Mainhand, 1=Offhand, 2=Head, 3=Body, 4=Acc, 5=Sealbook).
    for slot in 0..5:
        item = this.equipSlot[slot]                        // [this + slot*4 + 0xa8]
        if item == null: continue
        if !item.vtable_0x18_IsEquipment():
            if !item.vtable_0x1c_IsSealScroll(): assert("error.")
            continue                                       // Sealbook contributes 0 direct stats (enchants only)
        eq = dynamic_cast<CGameArticleEquipment>(item)
        if slot == 1 and EquipmentData_0x7389e0[eq.itemId].equipType_0x38 == 0:
            continue                                       // Dual-wield offhand WEAPON skipped here! (See M11.09 cmd 256)
        // Weapon Attack Modifier passives 243 (0xf3) + 298 (0x12a) summed as float:
        rate: f32 = 0.0f
        if c243 = this.vtable_0x48_GetCommand(0, 0xf3):  rate += c243.vtable_0x2c_GetVal()
        if c298 = this.vtable_0x48_GetCommand(0, 0x12a): rate += c298.vtable_0x2c_GetVal()
        // NOTE: Binary applies `rate` ONLY to ATK (stat 0, +0x54) and RES (stat 3, +0x60) across ALL slots 0..4!
        //       DEF (+0x58), INT (+0x5c), DEX (+0x64), AGI (+0x68) are added unscaled!
        atk: i32 = eq.GetATK(); this.curStat[0] += atk + trunc0(f32(atk) * rate)
        this.curStat[1] += eq.GetDEF()
        this.curStat[2] += eq.GetINT()
        res: i32 = eq.GetRES(); this.curStat[3] += res + trunc0(f32(res) * rate)
        this.curStat[4] += eq.GetDEX()
        this.curStat[5] += eq.GetAGI()
    // RNG calls: 0.
```
- **Program Evidence:**
```asm
004e12c6  mov      esi, dword ptr [eax + 0x3c]
004e12c9  test     esi, esi
004e12cb  je       0x4e1317
004e1304  mulss    xmm0, dword ptr [ecx + 0x54]
004e1309  cvttss2si eax, xmm0
004e130d  add      eax, esi
004f6579  cmp      ebx, 1
004f657c  jne      0x4f65a6
004f659c  cmp      dword ptr [eax + 0x38], 0
004f65a0  je       0x4f666c
004f65ab  push     0xf3
004f65d6  push     0x12a
004f65f8  call     0x4e12a0
004f6604  mulss    xmm0, dword ptr [esp + 0xc]
004f660a  cvttss2si ecx, xmm0
004f660e  add      ecx, eax
004f6610  add      dword ptr [edi + 0x54], ecx
004f662c  call     0x4e1450
004f6638  mulss    xmm0, dword ptr [esp + 0xc]
004f6644  add      dword ptr [edi + 0x60], ecx
```

---

### M11.06 Weapon Rank, Unarmed Rank (`ClassData+0x24` / `0x4f5585`) & Enchant `263` (`0x4f54d0`)

- **Binary VA(s):** `0x4f54d0..0x4f55e7` (`CGamePlayerStatusBase::GetWeaponRank`, `vtable+0xf4`; unarmed lookup at `0x4f5556..0x4f55df`)
- **Calls:** `0x61edf4` (`dynamic_cast`), `0x507310` (`EquipmentData` `[0x7389e0]`, `ClassData` `[0x7389bc]`, `WeaponRankData` `[0x738a94]`), `vtable+0x13c` (`GetClassId`), `vtable+0xf0(0x107)` (Enchant `263`)
- **CalledBy:** `CBattle::_SetTime` (`0x4499d0`, ATB turn recovery speed)
- **Typed Pseudocode:**
```text
function CGamePlayerStatusBase_GetWeaponRank(this: CGamePlayerStatusBase*) -> f32:
    // 0x4f54d0..0x4f55e7 (vtable+0xf4):
    mainhand = this.equipSlot[0]                           // [this+0xa8]
    if mainhand != null:
        eq = dynamic_cast<CGameArticleEquipment>(mainhand)
        eqParam = EquipmentData_0x7389e0[eq.itemId]
        if eqParam.equipType_0x38 != 0:                    // Non-weapon in slot 0
            return 1.0f                                    // 0x6d938c = 1.0f (A+)
        rankId: u32 = eqParam.weaponRankId_0x64
        return WeaponRankData_0x738a94[rankId].mult_0x28   // raw .pck +0x10 -> node+0x28
    // Unarmed branch (0x4f5556..0x4f55df):
    classId: u32 = this.vtable_0x13c(0)
    rankId: u32  = ClassData_0x7389bc[classId].unarmedRankId_0x3c // ClassData.pck +0x24
    mult: f32    = WeaponRankData_0x738a94[rankId].mult_0x28
    if this.vtable_0xf0_GetEnchantCount(0x107) != 0:       // Enchant 263 (A-rank speed when unarmed)
        mult = WeaponRankData_0x738a94[1].mult_0x28        // Forced to Rank 1 ("A" = 1.20f, 0x3f99999a)
    return mult
    // RNG calls: 0.
```

**`WeaponRankData.pck` Complete Table (12 ranks, `32` bytes/record, float at `+0x10` / node `+0x28`):**

| Rank ID | Label | `f32` Multiplier | IEEE-754 Hex | Rank ID | Label | `f32` Multiplier | IEEE-754 Hex |
|---:|---|---:|---|---:|---|---:|---|
| `0` | `A+` | `1.00f` | `0x3f800000` | `6` | `D+` | `2.15f` | `0x4009999a` |
| `1` | `A` | `1.20f` | `0x3f99999a` | `7` | `D` | `2.30f` | `0x40133333` |
| `2` | `B+` | `1.40f` | `0x3fb33333` | `8` | `E+` | `2.45f` | `0x401ccccd` |
| `3` | `B` | `1.60f` | `0x3fcccccd` | `9` | `E` | `2.60f` | `0x40266666` |
| `4` | `C+` | `1.80f` | `0x3fe66666` | `10` | `F+` | `2.75f` | `0x40300000` |
| `5` | `C` | `2.00f` | `0x40000000` | `11` | `F` | `2.90f` | `0x4039999a` |

**`ClassData.pck +0x24` Unarmed Rank IDs (Playable Classes `0..31`; NPC/Summon `32..48` all = `1` (`A`, `1.20f`)):**

| Rank ID (`mult`) | Playable Class IDs |
|---|---|
| `1` (`A`, `1.20f`) | `11` (`KN`) |
| `2` (`B+`, `1.40f`) | `8` (`AS`), `10` (`TH`), `24` (`MI`), `31` (`JO`) |
| `3` (`B`, `1.60f`) | `6` (`SC`), `7` (`AR`), `9` (`SN`), `17` (`MP`), `23` (`DI`), `25` (`ET`), `28` (`TS`), `30` (`PA`) |
| `4` (`C+`, `1.80f`) | `1` (`PL`), `2` (`BE`), `3` (`VL`), `4` (`SA`), `5` (`DL`), `16` (`WT`), `18` (`SG`), `19` (`BS`), `21` (`BD`), `22` (`DN`), `27` (`DM`), `29` (`SS`) |
| `5` (`C`, `2.00f`) | `0` (`FT`), `12` (`MU`), `13` (`SO`), `14` (`EN`), `15` (`PR`), `20` (`MA`), `26` (`SP`) |

- **Program Evidence:**
```asm
004f54d8  mov      eax, dword ptr [esi + 0xa8]
004f54de  test     eax, eax
004f54e0  je       0x4f5556
004f5515  cmp      dword ptr [eax + 0x38], 0
004f5519  jne      0x4f553f
004f5536  mov      eax, dword ptr [eax + 0x64]
004f553f  movss    xmm0, dword ptr [0x6d938c]    ; float 1
004f5558  call     dword ptr [eax + 0x13c]
004f557f  mov      eax, dword ptr [eax + 0x3c]
004f5595  push     0x107
004f559e  movss    xmm0, dword ptr [eax + 0x28]
004f55ab  call     dword ptr [eax + 0xf0]
004f55b1  test     eax, eax
004f55b3  je       0x4f55df
004f55b5  mov      dword ptr [esp + 4], 1
004f55d4  movss    xmm0, dword ptr [eax + 0x28]
```

---

### M11.07 Enchantment Collection, Dual-Wield Offhand Filter, Stacking & Party-Leader Sealbook (`0x4f62c0`, `0x4f64b0`, `0x4f7ac0`, `0x4f5470`)

- **Binary VA(s):** `0x4f62c0..0x4f64a5` (`CGamePlayerStatusBase::_SetupEnchant`), `0x4f64b0..0x4f652d` (`_AddEnchant`, `vtable+0x17c`), `0x4f7ac0..0x4f7bf4` (`CGamePlayerStatus::_SetupEnchant`, `vtable+0x178`), `0x4f5470..0x4f54cd` (`GetEnchantCount`, `vtable+0xf0`)
- **Calls:** `0x507310` (`EquipmentData` `[0x7389e0]`, `EnchantData` `[0x7389d0]`, `SealScrollData` `[0x738a14]`), `vtable+0x17c` (`0x4f64b0`), `vtable+0x108` (`M11.02`)
- **CalledBy:** Equipment change, Sealbook change, Level Reset (`0x4f5b89`), Party-leader Sealbook equip
- **Typed Pseudocode:**
```text
function CGamePlayerStatus_SetupEnchant(this: CGamePlayerStatus*):
    // 0x4f7ac0..0x4f7bf4 (vtable+0x178) -> calls base 0x4f62c0 then appends Party-Leader Sealbook:
    // 1. Base _SetupEnchant (0x4f62c0..0x4f6487):
    this.activeEnchants_0x12c.clear()
    for slot in 0..5:                                      // 0=Main, 1=Offhand, 2=Head, 3=Body, 4=Acc, 5=Sealbook
        item = this.equipSlot[slot]
        if item == null: continue
        if item.vtable_0x18_IsEquipment():
            eq = dynamic_cast<CGameArticleEquipment>(item)
            isOffhandWeapon: bool = (slot == 1 and EquipmentData_0x7389e0[eq.itemId].equipType_0x38 == 0)
            for enchId in eq.enchants_0x84:
                if isOffhandWeapon:
                    // DUAL-WIELD OFFHAND ENCHANT GATE (0x4f6362..0x4f6385):
                    // Only enchants with bit 7 (0x80) set in EnchantData+0x38 apply from an offhand weapon!
                    if ((EnchantData_0x7389d0[enchId].flags_0x38 >> 7) & 1) == 0:
                        continue
                this.vtable_0x17c_AddEnchant(enchId)       // 0x4f64b0
        else if item.vtable_0x1c_IsSealScroll():
            sb = dynamic_cast<CGameArticleSealScroll>(item)
            sbParam = SealScrollData_0x738a14[sb.itemId]
            for k in 0 .. sbParam.enchantCount_0x34 - 1:
                this.vtable_0x17c_AddEnchant(sbParam.enchantIds_0x38[k])
    // 2. Party-Leader Shared Sealbook (0x4f7ad0..0x4f7be5):
    if GameManager.IsActivePartyMember(this.GetMemberId()):
        sharedSb = GameManager.partySharedSlot_0x13f0.sealbook_0xbc
        if sharedSb != null:
            sb = dynamic_cast<CGameArticleSealScroll>(sharedSb)
            sbParam = SealScrollData_0x738a14[sb.itemId]
            for k in 0 .. sbParam.enchantCount_0x34 - 1:
                // Appends directly to activeEnchants_0x12c (stacking still gated by EnchantData+0x38 bit 0
                // inside GetEnchantCount 0x4f5470 and _CalculateParameterEnchant 0x4f8311).
                this.activeEnchants_0x12c.push_back(sbParam.enchantIds_0x38[k])
    this.vtable_0x108_Recalculate()                        // 0x4f7c00

function CGamePlayerStatusBase_AddEnchant(this: CGamePlayerStatusBase*, enchId: u32):
    // 0x4f64b0..0x4f652d (vtable+0x17c):
    if enchId in this.activeEnchants_0x12c:
        if (EnchantData_0x7389d0[enchId].flags_0x38 & 1) == 0: return // Non-stackable (bit 0 == 0)
    this.activeEnchants_0x12c.push_back(enchId)

function CGamePlayerStatusBase_GetEnchantCount(this: CGamePlayerStatusBase*, enchId: u32) -> u32:
    // 0x4f5470..0x4f54cd (vtable+0xf0):
    stacks: bool = (EnchantData_0x7389d0[enchId].flags_0x38 & 1) != 0
    count: u32 = 0
    for id in this.activeEnchants_0x12c:
        if id == enchId:
            count++
            if !stacks: break                              // Non-stackable returns at most 1
    return count
    // RNG calls: 0.
```
- **Program Evidence:**
```asm
004f6334  cmp      dword ptr [esp + 0x10], 1
004f635c  cmp      dword ptr [eax + 0x38], 0
004f6360  jne      0x4f6387
004f637d  mov      eax, dword ptr [eax + 0x38]
004f6380  shr      eax, 7
004f6383  test     al, 1
004f6385  je       0x4f6393
004f638d  call     dword ptr [eax + 0x17c]
004f64fc  mov      al, byte ptr [eax + 0x38]
004f64ff  and      al, 1
004f6501  je       0x4f6526
004f5499  mov      bl, byte ptr [eax + 0x38]
004f54a2  and      bl, 1
004f54b8  inc      edx
004f54b9  test     bl, bl
004f54bb  je       0x4f54c5
```

---

### M11.08 Equipment & Sealbook Enchant Stat/Resistance Modifiers (`_CalculateParameterEnchant` `0x4f8270`)

- **Binary VA(s):** `0x4f8270..0x4f8fd3` (`CGamePlayerStatus::_CalculateParameterEnchant`, `vtable+0x180`)
- **Calls:** `0x507310` (`EnchantData` `[0x7389d0]`), `vtable+0x30` (`GetBaseParam`), `vtable+0x34` (`GetCurParam`), `[0x71fc24]->vtable+0x164` (`IsFrontRow`), `[0x71fc24]->vtable+0x16c` (`IsBackRow`)
- **CalledBy:** `M11.02` (`0x4f7c42`, Stage 4 — runs AFTER Base, Specialty, and Equipment, BEFORE Statuses/Dual-Wield)
- **Typed Pseudocode:**
```text
function CGamePlayerStatus_CalculateParameterEnchant(this: CGamePlayerStatus*, baseMaxHp: i32, baseMaxTp: i32):
    // 0x4f8270..0x4f8fd3 (vtable+0x180):
    seenNonStack = set<u32>()
    dHp: i32 = 0; dTp: i32 = 0; dStat: i32[14] = { 0, ..., 0 }
    for enchId in this.activeEnchants_0x12c:
        // Deduplicates non-stacking enchants (bit 0 == 0 in EnchantData+0x38) locally (0x4f8311..0x4f8335):
        if (EnchantData_0x7389d0[enchId].flags_0x38 & 1) == 0:
            if enchId in seenNonStack: continue
            seenNonStack.insert(enchId)
        // Dispatch across all 78 stat/resistance enchant IDs (see complete table below):
        //   - IDs 0..23: percentage of BASE stat (baseMaxHp, baseMaxTp, or vtable+0x30(idx)):
        //       UP:     +max(4, base / 10)   (signed trunc0 div by 10 via 0x66666667 sar 2)
        //       MiniUP: +max(2, base / 20)   (signed trunc0 div by 20 via 0x66666667 sar 3)
        //       DOWN:   -max(0, base / 10)   (cmovs 0)
        //   - IDs 24..28: flat +1 / +3 / +6 / +9 / +12 to all 6 primary stats (0..5).
        //   - IDs 222..225, 281: row-conditional % of CURRENT stat (vtable+0x34, includes Base+Specialty+Equip!):
        //       222 (0xde) Front: ATK += trunc0(f32(CurATK) * 0.08f)
        //       223 (0xdf) Front: ATK += CurATK / 25; DEF += CurDEF / 25        (0x51eb851f sar 3)
        //       224 (0xe0) Back:  INT += trunc0(f32(CurINT) * 0.08f)
        //       225 (0xe1) Back:  INT += CurINT / 25; RES += CurRES / 25        (0x51eb851f sar 3)
        //       281 (0x119) Back: DEX += CurDEX / 50; AGI += CurAGI / 50        (0x51eb851f sar 4)
        //   - IDs 88..119, 310..356: flat deltas to resistances dStat[6..13].
    // Intermediate Enchant Clamps (0x4f842c..0x4f84ae):
    hpCap: i32 = baseMaxHp / 2                             // cdq; sub; sar 1
    this.maxHp += clamp(dHp, -hpCap, +hpCap)               // [this+0x10]
    tpCap: i32 = baseMaxTp / 2
    this.maxTp += clamp(dTp, -tpCap, +tpCap)               // [this+0x18]
    for i in 0..5:
        this.curStat[i] += dStat[i]                        // Primary stat enchant deltas unclamped here
    for r in 6..13:
        this.curStat[r] += clamp(dStat[r], -100, +100)     // Resistance enchant deltas clamped to [-100, +100]
    // RNG calls: 0.
```

**Complete Table of All 78 Stat/Resistance Enchants in `0x4f8270..0x4f8fd3`:**

| Enchant ID (Hex) | Target Field(s) | Exact Delta Formula |
|---|---|---|
| `0 / 1 / 2` (`0x00..0x02`) | `MaxHP` | `+max(4, baseMaxHp/10)` / `+max(2, baseMaxHp/20)` / `-max(0, baseMaxHp/10)` |
| `3 / 4 / 5` (`0x03..0x05`) | `MaxTP` | `+max(4, baseMaxTp/10)` / `+max(2, baseMaxTp/20)` / `-max(0, baseMaxTp/10)` |
| `6 / 7 / 8` (`0x06..0x08`) | `ATK` (`0`) | `+max(4, BaseATK/10)` / `+max(2, BaseATK/20)` / `-max(0, BaseATK/10)` |
| `9 / 10 / 11` (`0x09..0x0b`) | `DEF` (`1`) | `+max(4, BaseDEF/10)` / `+max(2, BaseDEF/20)` / `-max(0, BaseDEF/10)` |
| `12 / 13 / 14` (`0x0c..0x0e`) | `INT` (`2`) | `+max(4, BaseINT/10)` / `+max(2, BaseINT/20)` / `-max(0, BaseINT/10)` |
| `15 / 16 / 17` (`0x0f..0x11`) | `RES` (`3`) | `+max(4, BaseRES/10)` / `+max(2, BaseRES/20)` / `-max(0, BaseRES/10)` |
| `18 / 19 / 20` (`0x12..0x14`) | `DEX` (`4`) | `+max(4, BaseDEX/10)` / `+max(2, BaseDEX/20)` / `-max(0, BaseDEX/10)` |
| `21 / 22 / 23` (`0x15..0x17`) | `AGI` (`5`) | `+max(4, BaseAGI/10)` / `+max(2, BaseAGI/20)` / `-max(0, BaseAGI/10)` |
| `24..28` (`0x18..0x1c`) | `ATK..AGI` (`0..5`) | `+1` (`24`), `+3` (`25`), `+6` (`26`), `+9` (`27`), `+12` (`28`) to all 6 stats |
| `88 / 89 / 90` (`0x58..0x5a`) | `Fire` (`9`) | `+20` / `+10` / `-20` |
| `91 / 92 / 93` (`0x5b..0x5d`) | `Water` (`10`) | `+20` / `+10` / `-20` |
| `94 / 95 / 96` (`0x5e..0x60`) | `Wind` (`11`) | `+20` / `+10` / `-20` |
| `97 / 98 / 99` (`0x61..0x63`) | `Earth` (`12`) | `+20` / `+10` / `-20` |
| `100 / 101 / 102` (`0x64..0x66`) | `Lightning` (`13`) | `+20` / `+10` / `-20` |
| `103 / 104 / 105 / 106` (`0x67..0x6a`) | All 5 Elem (`9..13`) | `+50` / `+15` / `+7` / `-15` |
| `107 / 108 / 109` (`0x6b..0x6d`) | `Slash` (`6`) | `+20` / `+10` / `-20` |
| `110 / 111 / 112` (`0x6e..0x70`) | `Stab` (`7`) | `+20` / `+10` / `-20` |
| `113 / 114 / 115` (`0x71..0x73`) | `Bash` (`8`) | `+20` / `+10` / `-20` |
| `116 / 117 / 118 / 119` (`0x74..0x77`) | All 3 Phys (`6..8`) | `+25` / `+10` / `+5` / `-10` |
| `222` (`0xde`) | `ATK` (`0`, Front Row) | `+trunc0(f32(CurATK) * 0.08f)` |
| `223` (`0xdf`) | `ATK, DEF` (Front Row) | `+(CurATK / 25)`, `+(CurDEF / 25)` |
| `224` (`0xe0`) | `INT` (`2`, Back Row) | `+trunc0(f32(CurINT) * 0.08f)` |
| `225` (`0xe1`) | `INT, RES` (Back Row) | `+(CurINT / 25)`, `+(CurRES / 25)` |
| `281` (`0x119`) | `DEX, AGI` (Back Row) | `+(CurDEX / 50)`, `+(CurAGI / 50)` |
| `310 / 311 / 312` (`0x136..0x138`) | `Fire` (`9`) | `+100` / `+50` / `-50` |
| `315 / 316 / 317` (`0x13b..0x13d`) | `Water` (`10`) | `+100` / `+50` / `-50` |
| `320 / 321 / 322` (`0x140..0x142`) | `Wind` (`11`) | `+100` / `+50` / `-50` |
| `325 / 326 / 327` (`0x145..0x147`) | `Earth` (`12`) | `+100` / `+50` / `-50` |
| `330 / 331 / 332` (`0x14a..0x14c`) | `Lightning` (`13`) | `+100` / `+50` / `-50` |
| `335 / 336` (`0x14f..0x150`) | All 5 Elem (`9..13`) | `+75` / `-30` |
| `340 / 341 / 342` (`0x154..0x156`) | `Slash` (`6`) | `+100` / `+50` / `-50` |
| `345 / 346 / 347` (`0x159..0x15b`) | `Stab` (`7`) | `+100` / `+50` / `-50` |
| `350 / 351 / 352` (`0x15e..0x160`) | `Bash` (`8`) | `+100` / `+50` / `-50` |
| `355 / 356` (`0x163..0x164`) | All 3 Phys (`6..8`) | `+50` / `-20` |

- **Program Evidence:**
```asm
004f8311  test     byte ptr [eax + 0x38], 1
004f835b  mov      eax, 0x66666667
004f8360  imul     dword ptr [ebp + 8]
004f8368  sar      edx, 2
004f8372  cmp      eax, 4
004f8375  cmovl    eax, ecx
004f8437  sar      eax, 1
004f8439  cmp      esi, eax
004f843b  cmovg    esi, eax
004f8497  cmp      eax, 0x64
004f849a  cmovg    eax, esi
004f849d  cmp      eax, -0x64
004f84a0  cmovl    eax, edi
004f8bde  mulss    xmm0, dword ptr [0x6d9300]    ; float 0.08
004f8c31  mov      eax, 0x51eb851f
004f8c3a  sar      edx, 3
004f8d7e  sar      edx, 4
```

---

### M11.09 Status/Passive `%` Modifiers (`0x4fbdd0`), Dual-Wield Offhand (`256`), Party-Skill Synergy (`0x4f8fe0`) & Hard Caps (`0x4fc620`)

- **Binary VA(s):** `0x4fbdd0..0x4fc610` (`CGameStatusBase::_CalculateParameterStatus`, `vtable+0x10c`), `0x4f8fe0..0x4f94e6` (Party-Skill Synergy bonuses), `0x4fc620..0x4fc889` (`CGameStatusBase::_ClampParameter`, `vtable+0x110`)
- **Calls:** `0x47e340` (`FINDER` on `[this+0x8c]`), `vtable+0x30` (`GetBaseParam`), `vtable+0x34` (`GetCurParam`), `vtable+0x48` (`GetCommand`), `vtable+0x50` (`HasStatus`), `0x61d550` (`__ftol2_sse`), `0x507310` (`EquipmentData` `[0x7389e0]`)
- **CalledBy:** `CGamePlayerStatus::Recalculate` (`M11.02`, Stages 5–7), `CGameEnemyStatus::Recalculate` (`M11.15`, Stages 2–3)
- **Typed Pseudocode:**
```text
function CGameStatusBase_CalculateParameterStatus(this: CGameStatusBase*, baseMaxHp: i32, baseMaxTp: i32):
    // 0x4fbdd0..0x4fc610 (vtable+0x10c): Shared by BOTH players and enemies!
    dHp: i32 = 0; dStat: i32[14] = { 0, ..., 0 }
    // 1. Primary stat % buffs/debuffs (41..46 / 0x29..0x2e) applied to CurStat (vtable+0x34):
    for i in 0..5:                                         // 0x29=ATK, 0x2a=DEF, 0x2b=INT, 0x2c=RES, 0x2d=DEX, 0x2e=AGI
        if c = FindCommand(this.statuses_0x8c, 0x29 + i):
            dStat[i] += trunc0(f32(this.vtable_0x34_GetCurStat(i)) * c.val)
    // 2. Command 48 (0x30, Trump Card, 0x4fbfb4..0x4fc019):
    if c48 = this.vtable_0x48_GetCommand(0, 0x30):
        dStat[1] = -10000                                  // 0xffffd8f0 OVERWRITES dStat[DEF] (forces DEF -> 0 at clamp)
        dStat[0] += trunc0(f32(this.vtable_0x34_GetCurStat(1)) * c48.val) // Adds CurDEF * val to ATK
    // 3. Status 120 (0x78, Petrification, 0x4fc01d..0x4fc050):
    if this.vtable_0x50_HasStatus(0x78):
        dStat[1] += this.vtable_0x30_GetBaseStat(1) / 2    // +BaseDEF / 2 (trunc0)
        dStat[5] -= this.vtable_0x30_GetBaseStat(5) / 2    // -BaseAGI / 2 (trunc0)
    // 4. Flat Resistance & MaxHP statuses (0x4fc050..0x4fc26b):
    if c169 = GetCommand(0, 0xa9):  for r in 9..13: dStat[r] += trunc0(c169.val) // Elemental resists (Fire..Lightning)
    if c172 = GetCommand(0, 0xac):  dHp = trunc0(f32(baseMaxHp) * c172.val)      // MaxHP %
    if c184 = GetCommand(0, 0xb8):  dStat[7] += trunc0(c184.val)                 // Stab Resist
    if c185 = GetCommand(0, 0xb9):  dStat[6] += trunc0(c185.val)                 // Slash Resist
    if c186 = GetCommand(0, 0xba):  dStat[8] += trunc0(c186.val)                 // Bash Resist
    // First-match exclusive all-6-stat % group: 189 (0xbd) -> 193 (0xc1) -> 194 (0xc2):
    if c = GetCommand(0, 0xbd) ?? GetCommand(0, 0xc1) ?? GetCommand(0, 0xc2):
        for i in 0..5: dStat[i] += trunc0(f32(this.curStat[i]) * c.val)
    if HasStatus(0xc0):                                    // Status 192 (All Resistances 100):
        for r in 6..13: dStat[r] += 10000                  // SIMD paddd [0x6d9e10] = {10000,10000,10000,10000}
    // First-match elemental resist group: 202 (0xca, Hopak) -> 341 (0x155, Emaciating Geas):
    if c = GetCommand(0, 0xca) ?? GetCommand(0, 0x155):
        for r in 9..13: dStat[r] += trunc0(c.val)
    if c248 = GetCommand(0, 0xf8):                         // Command 248 (Resistance):
        for r in 9..13: dStat[r] += trunc0(c248.val)
    // 5. DUAL WIELD / LEFTY BONUS — Passive 256 (0x100, 0x4fc26f..0x4fc5c5):
    if c256 = this.vtable_0x48_GetCommand(0, 0x100):
        ps = dynamic_cast<CGamePlayerStatusBase>(this)
        eq = dynamic_cast<CGameArticleEquipment>(ps.equipSlot[1]) // Offhand [ps+0xac]
        if eq != null and EquipmentData_0x7389e0[eq.itemId].equipType_0x38 == 0:
            mult: f32 = c256.vtable_0x2c_GetVal()
            for i in 0..5:                                 // ATK..AGI
                base: i32 = EquipmentData_0x7389e0[eq.itemId].baseStats[i]
                val: i32  = (base == 0) ? 0 : base + trunc0(f32(eq.forgeLevel) * EquipmentData_0x7389e0[eq.itemId].forgeGrowth_0x54)
                dStat[i] += trunc0(f32(val) * mult)
    // Apply deltas (0x4fc5c5..0x4fc609):
    this.maxHp = max(1, this.maxHp + dHp)
    this.maxTp = max(1, this.maxTp)
    for i in 0..13: this.curStat[i] += dStat[i]

function CGamePlayerStatus_CalculatePartySkillSynergy(this: CGamePlayerStatus*):
    // 0x4f8fe0..0x4f94e6 (Stage 6, players only): Scales 20 party-skill passives by p = f32([0x71fc24]->vtable+0x234()).
    // Each active passive clamps its floor-0 result to 1 (if 0 -> 1) and caps at its constant ceiling:
    //   360(0x168): HP  += clamp1(trunc0(p*2.0f), 100)       370(0x172): Bash  += clamp1(trunc0(p*0.4f), 20)
    //   361(0x169): ATK += clamp1(trunc0(p*0.65f), 32)       371(0x173): DEX   += clamp1(trunc0(p*0.65f), 32)
    //   362(0x16a): TP  += clamp1(trunc0(p), 50); Fire += clamp1(trunc0(p*0.4f), 20)
    //   363(0x16b): Slash += clamp1(trunc0(p*0.5f), 25)      372(0x174): Water, Earth += clamp1(trunc0(p*0.4f), 20)
    //   364(0x16c): INT += clamp1(trunc0(p*0.4f), 20)        373(0x175): Lightning += clamp1(trunc0(p), 50)
    //   365(0x16d): DEF += clamp1(trunc0(p*0.5f), 25)        374(0x176): Wind += clamp1(p*0.4f, 20); AGI += clamp1(p*0.2f, 10)
    //   366(0x16e): AGI += clamp1(trunc0(p*0.4f), 20)        375(0x177): Bash += clamp1(p*0.2f, 10); Earth += clamp1(p*0.4f, 20)
    //   367(0x16f): Stab += clamp1(trunc0(p*0.4f), 20)       376(0x178): Lightning += clamp1(p*0.4f, 20); HP += clamp1(p, 50)
    //   368(0x170): HP, TP += clamp1(trunc0(p), 50)          377(0x179): Fire += clamp1(p*0.2f, 10); ATK += clamp1(p*0.4f, 20)
    //   369(0x171): RES += clamp1(trunc0(p*0.4f), 20)        405(0x195): TP += clamp1(p, 50); Fire += clamp1(p*0.4f, 20)
    //                                                        415(0x19f): DEX, AGI += clamp1(trunc0(p*0.4f), 20)

function CGameStatusBase_ClampParameter(this: CGameStatusBase*):
    // 0x4fc620..0x4fc889 (vtable+0x110, Stage 7): FINAL HARD CAPS!
    this.maxHp = max(1, this.maxHp + this.tempMaxHpDelta_0x98) // NO 9999 upper cap on MaxHP!
    this.curHp = min(this.curHp, this.maxHp)
    this.maxTp = max(1, this.maxTp)                            // NO 9999 upper cap on MaxTP!
    this.curTp = min(this.curTp, this.maxTp)
    for i in 0..5:                                             // ATK, DEF, INT, RES, DEX, AGI
        this.curStat[i] = clamp(this.curStat[i], 0, 9999)      // [0, 0x270f]
    for r in 6..13:                                            // Slash, Stab, Bash, Fire, Water, Wind, Earth, Lightning
        this.curStat[r] = clamp(this.curStat[r], -100, +100)   // [0xffffff9c, 0x64]
    // POST-CLAMP DIRECT OVERWRITES (0x4fc76f..0x4fc887):
    // Commands 416..423 (0x1a0..0x1a7, Fixed Resistances) overwrite curStat[6..13] directly via __ftol2_sse (0x61d550)!
    for k in 0..7:
        if c = this.vtable_0x48_GetCommand(0, 0x1a0 + k):
            this.curStat[6 + k] = trunc0(c.vtable_0x2c_GetVal())
    // RNG calls: 0.
```
- **Program Evidence:**
```asm
004fbe01  mov      edx, 0x29
004fbff4  mov      esi, dword ptr [esp + 0x38]
004fbfef  mov      ebx, 0xffffd8f0
004fc01d  push     0x78
004fc036  sar      eax, 1
004fc1be  movaps   xmm1, xmmword ptr [0x6d9e10]
004fc26f  push     0x100
004fc2db  cmp      dword ptr [eax + 0x38], 0
004fc353  mulss    xmm0, dword ptr [eax + 0x54]
004fc375  cvttss2si eax, xmm0
004fc629  mov      edx, dword ptr [esi + 0x98]
004fc62f  add      edx, dword ptr [esi + 0x10]
004fc637  cmovle   edx, edi
004fc649  mov      edx, 0x270f
004fc66b  cmp      ecx, edx
004fc66d  cmovg    ecx, edx
004fc6c7  mov      edx, 0xffffff9c
004fc6cf  mov      ecx, 0x64
004fc6d9  cmovl    eax, edx
004fc6de  cmovg    eax, ecx
004fc709  push     0x1a0
004fc781  call     0x61d550
004fc786  mov      dword ptr [esi + 0x6c], eax
```

---

## 4. EXP, SP & Level Curves, Gold & Drops

### M11.10 `LvExpSkptData.pck` Layout, Cumulative EXP/SP Curves (`0x55c100`, `0x4f5610`) & Level-Up SP Cap (`0x448560`)

- **Binary VA(s):** `0x55c100..0x55c1ac` (`Parameter::CParameterLvExpSkpt::GetTotalExp`), `0x4f97e0..0x4f97f1` (`CGameStatusBase::SetExp`, `vtable+0x14`), `0x4f5610..0x4f5646` (`CGamePlayerStatusBase::RecalcLevelFromExp`, `vtable+0x128`), `0x448560..0x448635` (`CBattleResult` level-up SP grant)
- **Calls:** `0x55c100`, `vtable+0x0c` (`SetLevel` -> `M11.02`), `vtable+0x128` (`0x4f5610`)
- **CalledBy:** `CBattleResult::Update` (`0x444457`, `0x4444b2`), `CGamePlayerStatusBase::_Reset` (`0x4f5699`, `0x4f5a4c`, `M11.03`)
- **Typed Pseudocode:**
```text
// LvExpSkptData.pck ([0x7389fc]): 99 entries (levels 1..99), 12 bytes each:
//   struct LvExpSkptEntry_s { u32 level; u32 expDelta; u32 spDelta; };
//   Stored in RB-tree node: key/level at +0x10/+0x14, expDelta at +0x18, spDelta at +0x1c.
//   Totals across Lv 1..99: Total EXP to Lv99 = 3,042,158; Total SP Lv 1..99 = 685.

function CParameterLvExpSkpt_GetTotalExp(targetLv: u32) -> u32:
    // 0x55c100..0x55c1ac:
    if targetLv < 1 or targetLv > maxLevel_99: return 0
    total: u32 = 0
    for lv in 1 .. targetLv:
        total += LvExpSkptData_0x7389fc[lv].expDelta       // [node+0x18]
    return total

function CGameStatusBase_SetExp(this: CGameStatusBase*, exp: u32):
    // 0x4f97e0..0x4f97f1 (vtable+0x14):
    this.exp = min(exp, 9999999u32)                        // Hard EXP cap = 0x98967f (9,999,999)

function CGamePlayerStatusBase_RecalcLevelFromExp(this: CGamePlayerStatusBase*):
    // 0x4f5610..0x4f5646 (vtable+0x128):
    curExp: u32 = this.exp                                 // [this+0x08]
    lv: u32 = 1; prevLv: u32 = 1; req: u32 = 0
    do:
        prevLv = lv
        lv++
        req = GetTotalExp(lv)                              // 0x55c100
    while req <= curExp and lv < 99                        // 0x63
    finalLv: u32 = (req > curExp) ? prevLv : lv            // cmova esi, ebp
    this.vtable_0x0c_SetLevel(finalLv)                     // Sets [this+0x04] = finalLv & calls Recalculate()

function CBattleResult_ApplyLevelUp(member: CGamePlayerStatus*):
    // 0x448583..0x448633:
    oldLv: u32 = member.vtable_0x10_GetLevel()
    member.vtable_0x128_RecalcLevelFromExp()               // Updates [member+0x04] to newLv & recalcs stats
    newLv: u32 = member.vtable_0x10_GetLevel()
    for lv in oldLv + 1 .. newLv:
        member.availableSp = min(999u32, member.availableSp + LvExpSkptData_0x7389fc[lv].spDelta) // cap 0x3e7 = 999!
    // RNG calls: 0.
```

**`LvExpSkptData.pck` Key Milestones (Exact Vanilla Table):**

| Level | `expDelta` | Cumulative EXP | `spDelta` | Cumulative SP |
|---:|---:|---:|---:|---:|
| `1` | `0` | `0` | `3` | `3` |
| `2` | `120` | `120` | `1` | `4` |
| `10` | `662` | `2,931` | `1` | `12` |
| `15` | `1,486` | `8,554` | `2` | `18` |
| `30` | `6,474` | `65,882` | `3` | `52` |
| `33` | `8,347` | `89,336` | `4` | `62` |
| `95` | `91,876` | `2,653,365` | `16` | `617` |
| `99` | `100,442` | `3,042,158` | `18` | `685` |

- **Program Evidence:**
```asm
004f97e0  mov      edx, 0x98967f
004f97e5  cmp      dword ptr [esp + 4], edx
004f97e9  cmovbe   edx, dword ptr [esp + 4]
004f97ee  mov      dword ptr [ecx + 8], edx
004f5625  call     0x55c100
004f562c  cmp      ecx, edi
004f562e  ja       0x4f5635
004f5630  cmp      esi, 0x63
004f5633  jb       0x4f5620
004f563b  cmova    esi, ebp
004f563f  call     dword ptr [eax + 0xc]
004485c4  mov      edi, 0x3e7
00448604  mov      ecx, dword ptr [ecx + 0x1c]
00448610  add      eax, ecx
00448612  cmp      eax, 0x3e7
00448617  cmova    eax, edi
0044861b  mov      dword ptr [edx + 0x124], eax
```

---

### M11.11 Per-Kill EXP Level-Gap Scaling (`CBattle::_AddExp` `0x450710`, Vanilla `X01..X08` & Enchant `270`)

- **Binary VA(s):** `0x43a947..0x43a9b2` (caller inside `CBattleBase::_KillUnit`), `0x450710..0x450828` (`CBattle::_AddExp`, `CBattle` `vtable+0x5c`; Vanilla `X01..X08` bytes at `0x450781..0x450815`)
- **Calls:** `vtable+0x10` (`GetLevel`), `vtable+0xf0(0x10e)` (Enchant `270`), `0x61e650` (`round_f32_to_i32`)
- **CalledBy:** `CBattleBase::_KillUnit` (`0x43a9a5`) whenever an enemy unit dies (called for ALL player party units, `aliveOnly = false` via `0x43e6d0(vec, row=0, sort=0, isPlayer=1, aliveOnly=0)` — excludes Dolls `2000..2999`, Summons `3000..3999`, `>=4000`).
- **Typed Pseudocode:**
```text
function CBattleBase_AwardKillExp(this: CBattleBase*, killedEnemyUnit: BattleUnit_s*):
    // 0x43a947..0x43a9b2:
    playerUnits = this._CollectUnits(rowFilter=0, sort=0, isPlayerSide=1, aliveOnly=0) // 0x43e6d0
    baseExp: f32 = f32(killedEnemyUnit.status.vtable_0x18_GetExp()) // u32 -> f64 -> f32
    for u in playerUnits:
        this.vtable_0x5c_AddExp(u, killedEnemyUnit, baseExp)       // 0x450710

function CBattle_AddExp(this: CBattle*, playerUnit: BattleUnit_s*, enemyUnit: BattleUnit_s*, baseExp: f32):
    // 0x450710..0x450828 (CBattle vtable+0x5c):
    diff: i32 = i32(playerUnit.status.vtable_0x10_GetLevel()) - i32(enemyUnit.status.vtable_0x10_GetLevel())
    hasEnch270: bool = (playerUnit.status.vtable_0xf0_GetEnchantCount(0x10e) != 0) // Enchant 270
    // Exact vanilla level-gap multipliers (X01..X08 cover the diff < 0 branches at 0x450781..0x450815):
    if      diff >=  5 and diff <=  9: mult = 0.90f        // [0x6d937c] (lea eax,[esi-5]; cmp eax,4; ja)
    else if diff >= 10:                mult = 0.85f        // [0x6d9374]
    else if diff >= -4 and diff <= -1: mult = hasEnch270 ? 1.15f : 1.00f // [0x6d939c] / [0x6d938c] (X01/X06)
    else if diff >= -9 and diff <= -5: mult = hasEnch270 ? 1.30f : 1.10f // [0x6d93a8] / [0x6d9398] (X02/X05)
    else if diff >= -19 and diff <= -10: mult = hasEnch270 ? 1.50f : 1.25f // [0x6d93bc] / [0x6d93a4] (X03/X07)
    else if diff <= -20:               mult = hasEnch270 ? 1.75f : 1.25f // [0x6d93c8] / [0x6d93a4] (X04/X08)
    else:                              mult = 1.00f        // diff in 0..4 ([0x6d938c])
    playerUnit.accumExp_0xec += round_f32_to_i32(baseExp * mult) // 0x61e650 -> [playerUnit+0xec]
    // RNG calls: 0.
```

| `diff = PlayerLv - EnemyLv` | Vanilla Base Mult (`.rdata` VA) | With Enchant `270` (`0x10e`) (`.rdata` VA) | Branch VA |
|---|---|---|---|
| `diff >= +10` | `0.85f` (`0x6d9374`) | `0.85f` (`0x6d9374`) | `0x45074b..0x450758` |
| `+5 <= diff <= +9` | `0.90f` (`0x6d937c`) | `0.90f` (`0x6d937c`) | `0x450736..0x450746` |
| `0 <= diff <= +4` | `1.00f` (`0x6d938c`) | `1.00f` (`0x6d938c`) | `0x45072c` (default) |
| `-4 <= diff <= -1` | `1.00f` (`0x6d938c`) | `1.15f` (`0x6d939c`) | `0x45075d..0x450785`, `0x450803` |
| `-9 <= diff <= -5` | `1.10f` (`0x6d9398`) | `1.30f` (`0x6d93a8`) | `0x45078a..0x4507ae`, `0x4507f9` |
| `-19 <= diff <= -10` | `1.25f` (`0x6d93a4`) | `1.50f` (`0x6d93bc`) | `0x4507b0..0x4507d4`, `0x45080d` |
| `diff <= -20` | `1.25f` (`0x6d93a4`) | `1.75f` (`0x6d93c8`) | `0x4507d6..0x4507f7`, `0x45080d` |

- **Program Evidence:**
```asm
00450734  sub      esi, eax
00450736  lea      eax, [esi - 5]
00450739  cmp      eax, 4
0045073e  movss    xmm0, dword ptr [0x6d937c]    ; float 0.9
0045074b  cmp      esi, 0xa
00450750  movss    xmm0, dword ptr [0x6d9374]    ; float 0.85
00450768  push     0x10e
0045077d  movss    xmm0, dword ptr [0x6d939c]    ; float 1.15
004507a6  movss    xmm0, dword ptr [0x6d93a8]    ; float 1.3
004507cc  movss    xmm0, dword ptr [0x6d93bc]    ; float 1.5
004507ef  movss    xmm0, dword ptr [0x6d93c8]    ; float 1.75
004507f9  movss    xmm0, dword ptr [0x6d9398]    ; float 1.1
00450803  movss    xmm0, dword ptr [0x6d938c]    ; float 1
0045080d  movss    xmm0, dword ptr [0x6d93a4]    ; float 1.25
00450815  mulss    xmm0, dword ptr [esp + 0x14]
0045081b  call     0x61e650
00450820  add      dword ptr [edi + 0xec], eax
```

---

### M11.12 Victory EXP Split & Multipliers (`CBattleResult::_Initialize` `0x445830`, Passive `218`, Status `157`, Enchant `275`)

- **Binary VA(s):** `0x43935d..0x4393e5` (Outer State 5 Paean `218` read), `0x445830..0x445aa5` (`CBattleResult::_Initialize`), `0x4443bd..0x4444b7` (`CBattleResult::Update` EXP application)
- **Calls:** `0x43afc0` (player member list), `0x443c30` (`CBattleResult` ctor), `0x61e650` (`round_f32_to_i32`), `0x448560` (`M11.10`)
- **CalledBy:** `M00.02` / `M00.09` (Outer States 5 & 6 in `CBattleBase::Update`)
- **Typed Pseudocode:**
```text
function CBattleBase_EnterVictory(this: CBattleBase*):
    // 0x43935d..0x4393e5 (Outer State 5):
    party = this._GetPartyStatuses(isPlayer=1, sort=0, aliveOnly=0) // 0x43af10
    bonus218: f32 = 0.0f
    // Reads Command 218 (0xda, Paean) from party[0] (party-wide song/aura):
    if c218 = party[0].vtable_0x48_GetCommand(0, 0xda):
        bonus218 = c218.vtable_0x2c_GetVal()
    this.result = new CBattleResult(this.battleInfo, &this.rewards_0x4c, this.flag14, 0, bonus218)

function CBattleResult_Initialize(this: CBattleResult*, bonus218: f32):
    // 0x4458a2..0x445aa5:
    aliveParty = this.battle._GetPlayerList(isPlayer=1, sort=0, aliveOnly=1) // 0x43afc0 -> excludes dead/Dolls/Summons
    allParty   = this.battle._GetPlayerList(isPlayer=1, sort=0, aliveOnly=0)
    aliveCount: f32 = f32(u32(aliveParty.size()))          // u32 -> f64 -> f32
    for member in allParty:
        unit = this.battle.vtable_0x34_GetUnit(member)
        baseShare: f32 = f32(u32(unit.accumExp_0xec)) / aliveCount // [0x4459bf]
        exp: f32 = baseShare + (baseShare * bonus218)      // [0x4459c7..0x4459cc]
        if member.vtable_0x50_HasStatus(0x9d):             // Status 157 (Experience UP): doubles EXP
            exp = exp + exp                                // [0x4459ed]
        if member.vtable_0xf0_GetEnchantCount(0x113) != 0: // Enchant 275 (Double EXP): doubles EXP again (x4 total!)
            exp = exp + exp                                // [0x445a1e]
        entry.startExp  = f32(u32(member.vtable_0x18_GetExp()))
        entry.targetExp = entry.startExp + exp             // [0x445a29]
    // Later in CBattleResult::Update (0x4443bd..0x4444b7):
    //   if !member.vtable_0xe8_IsAlive(): SKIP! Dead members receive 0 EXP on victory (even though accumExp > 0).
    //   For alive members: sets member.SetExp(round_f32_to_i32(entry.targetExp)) and invokes ApplyLevelUp (0x448560).
    // Gold award at 0x44647a..0x446488: GameManager.vtable_0x48_AddGold(this.rewards.gold_0x0c).
    // RNG calls: 0.
```
- **Program Evidence:**
```asm
00439380  push     0xda
0043938e  call     eax
004458b5  call     0x43afc0
00445997  push     0x9d
004459bf  divss    xmm0, dword ptr [ebp - 0x18]
004459c7  mulss    xmm1, dword ptr [ebp - 0x2c]
004459cc  addss    xmm1, xmm0
004459ed  addss    xmm0, xmm1
00445a06  push     0x113
00445a1e  addss    xmm1, xmm1
00445a29  addss    xmm1, dword ptr [ebp - 0x74]
004443c5  mov      eax, dword ptr [eax + 0xe8]
004443cb  call     eax
004443cd  test     al, al
004443cf  je       0x4444db
00444427  call     0x61e650
0044442f  call     dword ptr [edi + 0x14]
00446488  call     dword ptr [edx + 0x48]
```

---

### M11.13 Battle Gold & Enemy Drop Calculations (`0x43a9be..0x43ab08`, `0x558180`, `0x505ad0`)

- **Binary VA(s):** `0x43a9be..0x43ab08` (Gold & Drop dispatch in `CBattleBase::_KillUnit`), `0x558180..0x558650` (`Parameter::CParameterEnemy::DropItem`), `0x505ad0..0x505b50` (weighted RNG picker)
- **Calls:** `0x4e4dd0` (party passive sum: `0x10f` = 271 Gold, `0x10e` = 270 Drop), `0x61e650` (`round_f32_to_i32`), `0x505ad0` (`GlobalRng_0x816ce8.Rand(totalWeight)` via `0x490790`), `0x555c70` (equipment/sealbook treasure generator)
- **CalledBy:** `CBattleBase::_KillUnit` (`0x43a4a0`) on each enemy death; `0x558180` is also called with `isSteal = 1` from `_Steal` (`0x44fde0`)
- **Typed Pseudocode:**
```text
function CBattleBase_AwardKillGoldAndDrop(this: CBattleBase*, enemyUnit: BattleUnit_s*, killer: CGameStatusBase*):
    // 1. Gold Calculation (0x43a9be..0x43aa7c):
    enemyParam = EnemyData_0x7389d8[enemyUnit.status.enemyId_0x9c]
    baseGold: u32 = enemyParam.gold_0x50
    goldMult: f32 = 1.0f                                   // Default [ebp-0x1c] = 1.0f (0x43a795)
    if c67 = enemyUnit.status.vtable_0x48_GetCommand(0, 0x43):  // Command 67 (Gold Drop Rate UP on enemy)
        goldMult = c67.vtable_0x2c_GetVal()                // REPLACES 1.0f!
    if enemyUnit.status.vtable_0x48_GetCommand(0, 0x1ac) != null: // Command 428 (Quadruple Money on enemy)
        baseGold = max(100u32, baseGold << 2)              // shl esi, 2; floor 100 (0x64)
    partyBonus271: f32 = SumPartyPassive(0x10f)            // 0x4e4dd0: Passive 271 (Gold Drop Rate Modifier)
    totalGold: i32 = round_f32_to_i32(f32(baseGold) * (goldMult + partyBonus271)) + enemyUnit.status.extraGold_0x158
    this.rewards_0x4c.gold_0x58 += totalGold

    // 2. Enemy Drop Calculation (0x43aaa3 -> 0x558180(outItem, enemyStatus, killer, floorFlag, isSteal=0)):
    itemRateBonus: f32 = 0.0f                              // [ebp-0x1c]
    equipOnlyBonus: f32 = 0.0f                             // [ebp-0x18]
    if !isSteal:
        itemRateBonus = SumPartyPassive(0x10e) * 100.0f    // 0x4e4dd0: Passive 270 (Item Drop Rate Modifier) * 100
        if c68 = enemyStatus.vtable_0x48_GetCommand(0, 0x44): // Status 68 (Equipment Drop Rate UP)
            equipOnlyBonus = c68.vtable_0x2c_GetVal()
        if killer != null:
            cnt276: u32 = killer.vtable_0xf0_GetEnchantCount(0x114) // Enchant 276 (Equipment drop rate UP)
            equipOnlyBonus += f32(cnt276 * 20u32)          // +20 per stack (non-stackable bit0=0 -> +20)
    weights: u32[] = []
    totalWeight: u32 = 0
    // Regular item drop slots (N = [enemyParam+0x80], entry { itemId +0x84+i*8, weight +0x88+i*8 }):
    for i in 0 .. enemyParam.itemDropCount_0x80 - 1:
        w: u32 = enemyParam.itemDrops[i].weight
        if w != 0: w += round_f32_to_i32(itemRateBonus)    // Boosted by Passive 270 only
        weights.push(w); totalWeight += w
    // Equipment / Treasure drop slot ([enemyParam+0x94]):
    eqW: u32 = enemyParam.equipDropWeight_0x94
    if eqW != 0: eqW += round_f32_to_i32(equipOnlyBonus + itemRateBonus) // Boosted by 270 + 68 + Enchant 276!
    weights.push(eqW); totalWeight += eqW
    // No-Drop sentinel (only when totalWeight < 100 AND !isSteal):
    hasNoDrop: bool = (totalWeight < 100u32 and !isSteal)
    if hasNoDrop:
        weights.push(100u32 - totalWeight)
    // Weighted RNG roll (1 RNG draw via 0x505ad0 -> GlobalRng_0x816ce8.Rand(sum(weights))):
    //   prefix[k] = sum_{j=0..k} weights[j]; returns smallest k with roll < prefix[k] (jb).
    pick: u32 = WeightedPick_0x505ad0(weights)             // RNG calls: 1 (+1 if treasure sub-table picked)
    if pick < enemyParam.itemDropCount_0x80:
        spawn FixedItem(enemyParam.itemDrops[pick].itemId)
    else if pick == enemyParam.itemDropCount_0x80:
        // Rolls 2nd WeightedPick_0x505ad0 over [enemyParam+0x98] equipment/treasure entries at +0x9c (stride 0xc)
        spawn TreasureItem(0x555c70)
    else:
        return noDrop
```
- **Program Evidence:**
```asm
0043a9e3  push     0x43
0043aa0e  push     0x1ac
0043aa1e  shl      esi, 2
0043aa21  mov      eax, 0x64
0043aa26  cmp      esi, eax
0043aa28  cmovb    esi, eax
0043aa33  push     0x10f
0043aa38  call     0x4e4dd0
0043aa66  call     0x61e650
0043aa79  add      dword ptr [edi + 0x58], eax
005581ff  push     0x10e
00558204  call     0x4e4dd0
00558211  mulss    xmm1, dword ptr [0x6d9540]    ; float 100
0055821d  push     0x44
00558250  push     0x114
0055825b  lea      eax, [eax + eax*4]
0055825e  shl      eax, 2
00558383  cmp      ebx, 0x64
00558386  jae      0x558392
0055841d  mov      eax, 0x64
00558422  sub      eax, ebx
0055842c  call     0x505ad0
00505b35  call     0x490790
00505b40  cmp      eax, dword ptr [ebx + esi*4]
00505b43  jb       0x505b4a
```

---

## 5. Motivation (`0x4f5440`) & Battle-Entry Enemy/Unit Initialization

### M11.14 Motivation / Pep System (`0x4f5410`, `0x4f5440`, `0x4f69e0`, `[70..130]`)

- **Binary VA(s):** `0x4f5410..0x4f5432` (`AddMotivation`), `0x4f5440..0x4f5451` (`GetMotivation`), `0x4f69e0..0x4f6a89` (`_ClampMotivation`), `0x55d870..0x55d89b` (`GetMotivationDelta` from `PlayerStatusData.bin` `[0x738a08]`), `0x44ccc2..0x44cd1f` (Positive Trance `440` / `X17`), `0x4234e5..0x423505` (per-hit delta), `0x43a6a8..0x43a6cf` (player death delta), `0x43abc8..0x43abef` (enemy kill delta)
- **Calls:** `0x4f69e0`, `vtable+0xf0` (Enchants `201`, `200`, `195`), `vtable+0x48(0, 0x51)` (Command `81` Pep Freeze), `vtable+0x108` (`M11.02`)
- **CalledBy:** `CalcPhysicalAttack` (`0x44ccc9`, Positive Trance `440` / `X17`), `CActionPatternBase::_Task` (`0x423500`), `CBattleBase::_KillUnit` (`0x43a6c6`, `0x43abe6`), party condition evaluator (`0x560ad1`)
- **Typed Pseudocode:**
```text
// Motivation ([this+0xd8], f32) initializes to 100.0f (0x42c80000) in CGamePlayerStatusBase::_Reset (0x4f569f).
// Per-character motivation deltas live in PlayerStatusData.bin ([0x738a08]) as f32[] at node+0x50 (raw +0x3c):
//   idx 0 (+0x50): Enemy kill bonus (applied to killer in CBattleBase::_KillUnit at 0x43abd1)
//   idx 1 (+0x54): Player KO penalty (applied to fallen member in CBattleBase::_KillUnit at 0x43a6b9)
//   idx 5 (+0x64): Combat action/hit delta (queried via 0x55d870(charId, 5) at 0x4234ef -> AddMotivation)

function CGamePlayerStatusBase_ClampMotivation(this: CGamePlayerStatusBase*):
    // 0x4f69e0..0x4f6a89: Exact clamp & override precedence order!
    m: f32 = min(130.0f, max(70.0f, this.motivation_0xd8)) // 0x6d950c = 70.0f, 0x6d956c = 130.0f
    this.motivation_0xd8 = m
    if this.vtable_0xf0_GetEnchantCount(0xc9) != 0:        // Enchant 201: Pep fixed at minimum
        this.motivation_0xd8 = 70.0f                       // 0x428c0000
    if this.vtable_0xf0_GetEnchantCount(0xc8) != 0:        // Enchant 200: Pep will not drop below 100
        this.motivation_0xd8 = max(100.0f, this.motivation_0xd8) // 0x6d9540 = 100.0f
    if this.vtable_0xf0_GetEnchantCount(0xc3) != 0:        // Enchant 195: Pep fixed at maximum (overrides 201 & 200!)
        this.motivation_0xd8 = 130.0f                      // 0x43020000
    if c81 = this.vtable_0x48_GetCommand(0, 0x51):         // Command 81 (Pep Freeze): highest priority override!
        this.motivation_0xd8 = c81.vtable_0x2c_GetVal()

function CGamePlayerStatusBase_AddMotivation(this: CGamePlayerStatusBase*, delta: f32):
    // 0x4f5410..0x4f5432:
    this.motivation_0xd8 += delta
    this._ClampMotivation()                                // 0x4f69e0
    this.vtable_0x108_Recalculate()                        // 0x4f7c00

function CGamePlayerStatusBase_GetMotivation(this: CGamePlayerStatusBase*) -> f32:
    // 0x4f5440..0x4f5451:
    this._ClampMotivation()                                // 0x4f69e0
    return this.motivation_0xd8

function ApplyPositiveTrance440(attacker: CGamePlayerStatusBase*, dmg: i32, cmd440Val: f32) -> i32:
    // 0x44ccb2..0x44cd1f (Command 440 / 0x1b8, Vanilla X17 threshold 100.0f at 0x44ccd2 -> [0x6d9540]):
    mot: f32 = attacker.GetMotivation()                    // 0x4f5440
    if mot < 100.0f: return dmg                            // comiss xmm0, 100.0f; jb skip
    // Exact x87/SSE sequence: ((mot - 100.0f) / cmd440Val) / 100.0f:
    bonusRate: f32 = ((mot - 100.0f) / cmd440Val) / 100.0f
    return dmg + trunc0(f32(dmg) * bonusRate)
    // RNG calls: 0.
```
- **Program Evidence:**
```asm
004f5440  push     esi
004f5441  mov      esi, ecx
004f5443  call     0x4f69e0
004f5448  movss    xmm0, dword ptr [esi + 0xd8]
004f69e0  movss    xmm1, dword ptr [0x6d950c]    ; float 70
004f69e8  movss    xmm0, dword ptr [0x6d956c]    ; float 130
004f69f3  push     0xc9
004f69f8  maxss    xmm1, dword ptr [esi + 0xd8]
004f6a02  minss    xmm0, xmm1
004f6a18  mov      dword ptr [esi + 0xd8], 0x428c0000
004f6a26  push     0xc8
004f6a35  movss    xmm0, dword ptr [0x6d9540]    ; float 100
004f6a51  push     0xc3
004f6a60  mov      dword ptr [esi + 0xd8], 0x43020000
004f6a6e  push     0x51
0044ccc9  call     0x4f5440
0044ccce  movss    xmm1, dword ptr [0x6d9540]    ; float 100
0044ccd6  comiss   xmm0, xmm1
0044ccd9  jb       0x44cd2a
0044cd0e  mulss    xmm0, dword ptr [ebp + 0x10]
0044cd13  cvttss2si eax, xmm0
```

---

### M11.15 Battle-Entry Enemy Construction from `Enemy.pck` (`0x4f05d0`, `0x4f25f0`, `0x4f2820`, `0x4f1fc0`, `0x4f2150`)

- **Binary VA(s):** `0x4f05d0..0x4f07cc` (`CGameEnemyStatus::CGameEnemyStatus`), `0x4f1fc0..0x4f2112` (`CGameEnemyStatus::InitStatuses`, `vtable+0x58`), `0x4f2150..0x4f2178` (`CGameEnemyStatus::GetWeaponRank`, `vtable+0xf4`), `0x4f25f0..0x4f2813` (`CGameEnemyStatus::_CalculateBaseParameter`, `vtable+0x104`), `0x4f2820..0x4f2845` (`CGameEnemyStatus::Recalculate`, `vtable+0x108`)
- **Calls:** `0x507310` (`EnemyData` `[0x7389d8]`, `EnemyAttackData` `[0x7389d4]`), `0x47b220` (`CCommand` factory), `vtable+0x54` (`AddStatus` `0x4f9930`), `0x4fbdd0` (`M11.09`), `0x4fc620` (`M11.09`)
- **CalledBy:** Battle encounter construction (`CBattleBase::_Initialize` `M00.01`), Summon/reinforcement spawns
- **Typed Pseudocode:**
```text
// Enemy/Enemy.pck: 516 nested .pck entries (0000.pck..), each holding EnemyAIData.bin + EnemyStatusData.bin.
// EnemyStatusData.bin loaded into RB-tree [0x7389d8] (node offset = raw .bin offset + 0x18):
//   +0x2c (raw +0x14): u32 level                  +0x50 (raw +0x38): u32 gold
//   +0x30 (raw +0x18): i32 maxHp                  +0x5c (raw +0x44): f32 weaponRankMult (direct float!)
//   +0x34..+0x48 (raw +0x1c..+0x30): i32[6] { ATK, DEF, INT, RES, DEX, AGI }
//   +0x4c (raw +0x34): u32 exp                    +0x60..+0x7c (raw +0x48..+0x64): i32[8] { Slash..Lightning }
//   +0x80: u32 itemDropCount; +0x84: {itemId, weight}[]; +0x94: equipDropWeight; +0x98/+0x9c: treasure table
//   +0x108: u32 innateSkillCount; +0x10c: u32[] innate EnemyAttackData IDs

function CGameEnemyStatus_Construct(this: CGameEnemyStatus*, enemyId: u32, unitId: u32, flagA4: u8, flagA5: u8):
    // 0x4f05d0..0x4f07cc: Zero dynamic level/rank/floor scaling! All stats read verbatim from EnemyStatusData.bin.
    this.vtable   = 0x6d36e4
    this.enemyId  = enemyId                                // [this+0x9c]
    this.unitId   = unitId                                 // [this+0xa0]
    this.exp      = EnemyData_0x7389d8[enemyId].exp_0x4c   // [this+0x08]
    this.curTp    = 0; this.maxTp = 0                      // Zero-initialized by CGameStatusBase ctor (0x4f6afa)
    this.vtable_0x58_InitStatuses()                        // 0x4f1fc0: applies innate statuses/passives FIRST
    this.vtable_0x108_Recalculate()                        // 0x4f2820: Base -> StatusMods -> Clamp
    this.curHp    = this.maxHp                             // [this+0x0c] = [this+0x10] (post-status MaxHP!)
    // CurTP remains 0 while MaxTP is clamped to 1 by _ClampParameter (0x4fc64e).
    // RNG calls: 0.

function CGameEnemyStatus_InitStatuses(this: CGameEnemyStatus*):
    // 0x4f1fc0..0x4f2112 (vtable+0x58):
    eParam = EnemyData_0x7389d8[this.enemyId]
    for k in 0 .. eParam.innateSkillCount_0x108 - 1:
        atkId: u32 = eParam.innateSkillIds_0x10c[k]
        atkParam   = EnemyAttackData_0x7389d4[atkId]
        for j in 0 .. atkParam.cmdCount_0x60 - 1:
            cmdId: u32 = atkParam.cmds[j].cmdId_0x64       // stride 0x0c
            val: f32   = atkParam.cmds[j].val_0x68
            cmd = CCommand_Create(sourceType=2, cmdId, val, -1, -1, 0) // 0x47b220
            cmd.SetCaster(this.unitId)
            if this.vtable_0xbc_IsIncapacitated() and cmd.vtable_0x8c_IsBlockedByCC():
                delete cmd
            else:
                this.vtable_0x54_AddStatus(cmd)            // 0x4f9930

function CGameEnemyStatus_CalculateBaseParameter(this: CGameEnemyStatus*):
    // 0x4f25f0..0x4f2813 (vtable+0x104): Direct copy with ZERO level/rank scaling.
    eParam = EnemyData_0x7389d8[this.enemyId]
    this.level = eParam.level_0x2c                         // [this+0x04]
    this.maxHp = eParam.maxHp_0x30                         // [this+0x10] (maxTp NOT written here!)
    for i in 0..5:
        this.baseStat[i] = this.curStat[i] = eParam.stats_0x34[i]     // ATK, DEF, INT, RES, DEX, AGI
    for r in 6..13:
        this.baseStat[r] = this.curStat[r] = eParam.resists_0x60[r-6] // Slash..Lightning

function CGameEnemyStatus_Recalculate(this: CGameEnemyStatus*):
    // 0x4f2820..0x4f2845 (vtable+0x108):
    this.vtable_0x104_CalculateBaseParameter()             // 0x4f25f0
    this.vtable_0x10c_CalculateParameterStatus(this.maxHp, this.maxTp) // 0x4fbdd0 (M11.09)
    this.vtable_0x110_ClampParameter()                     // 0x4fc620 (M11.09: MaxHP>=1, MaxTP>=1, [0..9999], [-100..+100])

function CGameEnemyStatus_GetWeaponRank(this: CGameEnemyStatus*) -> f32:
    // 0x4f2150..0x4f2178 (vtable+0xf4):
    return EnemyData_0x7389d8[this.enemyId].weaponRankMult_0x5c // Direct float (not a rank ID!)
```
- **Program Evidence:**
```asm
004f0794  mov      eax, dword ptr [eax + 0x4c]
004f0797  mov      dword ptr [edi + 8], eax
004f079c  call     dword ptr [eax + 0x58]
004f07a3  call     dword ptr [eax + 0x108]
004f07a9  mov      eax, dword ptr [edi + 0x10]
004f07b0  mov      dword ptr [edi + 0xc], eax
004f2621  mov      eax, dword ptr [eax + 0x2c]
004f2624  mov      dword ptr [ebx + 4], eax
004f263a  mov      eax, dword ptr [eax + 0x30]
004f263d  mov      dword ptr [ebx + 0x10], eax
004f2661  mov      eax, dword ptr [eax + 0x34]
004f2664  mov      dword ptr [ebx + 0x54], eax
004f2667  mov      dword ptr [ebx + 0x1c], eax
004f2721  mov      eax, dword ptr [eax + 0x60]
004f2724  mov      dword ptr [ebx + 0x6c], eax
004f2825  call     dword ptr [eax + 0x104]
004f2835  call     dword ptr [eax + 0x10c]
004f2840  jmp      dword ptr [eax + 0x110]
004f2172  fld      dword ptr [eax + 0x5c]
```

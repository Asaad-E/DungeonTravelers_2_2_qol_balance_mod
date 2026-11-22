# Module M03 — Magical Damage (`CBattle::CalcMagicalAttack` & Callees)

Clean-room binary specification derived directly from `backups/exe/DT22_en_unwrapped.vanilla.exe` (x86-32 PE, image base `0x400000`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`).

## Scope & Calling Context

- **Primary Function:** `CBattle::CalcMagicalAttack` (`0x44d370..0x44f18c`, `CBattle` vtable `0x6c9b60` slot `+0x50` at `0x6c9bb0`).
- **Calling Convention:** `__thiscall` (`ecx = CBattle* this`, `ret 0x20`, 8 stack parameters relative to `ebp = esp - 0x38`):
  `[ebp+0x40]` `outResPtr: TaskResult**`, `[ebp+0x44]` `skillId: i32` (`-1` if not in `[0x738a58]`), `[ebp+0x48]` `skillLevel: i32`, `[ebp+0x4c]` `itemId: i32`, `[ebp+0x50]` `target: BattleUnit_s*` (`edi`), `[ebp+0x54]` `targetCmds: Vec<CCommand*>*`, `[ebp+0x58]` `actor: BattleUnit_s*` (`ebx`), `[ebp+0x5c]` `actorCmds: Vec<CCommand*>*`.
- **Command-List Merging Prologue (`0x44d3f4..0x44d56c`):**
  - `targetMergedCmds` (`[ebp+0x1c]`): copies `targetCmds`, appends `target->status->vt+0x4c()` active statuses, calls `vt+0x18` on each original `targetCmds[i]`, then merges duplicate command IDs across the split via `0x43e970` (summing `vt+0x2c()` into the earlier command via `vt+0x28`).
  - `actorMergedCmds` (`[ebp+0x28]`): copies `actorCmds`, checks if any original entry has `vt+0x7c() == true` (Weapon Element `{325..329}`), appends `actor->status->vt+0x40(i)` while **skipping** any `vt+0x7c() == true` status if `actorCmds` already had one, then merges duplicates via `0x43e970`.
- **Hit Rate (`0x44d56d..0x44db96`):** Computes `hitRate: f32` in `[ebp+0x54]` (consumed at `0x44ed91` in `M03.04`).
- **Shared Primitives:**
  - `FindCmd(&vec, id)` (`0x47e340`): first `CCommand*` with `vt+0x24() == id` or `nullptr`; value via `vt+0x2c() -> f32`. `FindCmdIdx(&vec, id)` (`0x48cbf0`): index or `-1`.
  - `status->vt+0xf0(enchId)`: `CGameEnemyStatus` (`0x4d4dd0`) always returns `0`; `CGamePlayerStatus` / `CGamePlayerStatusETCDoll` / `CGamePlayerStatusOtherETCDoll` (`0x4f5470`) counts matches in `[status+0x12c..0x130]`, stopping at `1` if bit 0 of `[enchTable[0x7389d0][enchId]+0x38]` (`stacks`) is `0`.
  - `status->vt+0x34(idx)` (`0x4f98d0`): `i32 [status + idx*4 + 0x54]` (`2=INT, 3=RES, 6=Slash, 7=Pierce, 8=Blunt, 9=Fire, 10=Water, 11=Wind, 12=Earth, 13=Lightning`).
  - `GlobalRng.Rand(n)` (`0x490790` on `[0x816ce8]`): uniform integer in `[0, n-1]`. `trunc0(x)` (`cvttss2si` / `0x61e650` `__ftol3`): truncation toward zero.

---

### M03.01 Base Magic Damage Formula

- **Binary VA(s):** `0x44db97..0x44e011`, `0x44e438..0x44e6da`, `0x44e81e..0x44e835` (`CBattle::CalcMagicalAttack`), `0x44fbb0..0x44fdd2` (`CBattle::_CalcFieldElementRevision`), `0x4489f0..0x448a46` (Earth/Lightning tile helpers)
- **Calls:** `0x507310` (tables `[0x738a58]` skill, `[0x738a54]` enemy attack), `0x61e650` (`__ftol3` `trunc0`), `0x490790` (`GlobalRng::Rand`), `0x44fbb0` (`_CalcFieldElementRevision`), `0x47e340` (`FindCmd`), `0x61edf4` (`__RTDynamicCast`), `0x435c10` (`Action_s` copy), `0x415f50` / `0x416260` / `0x416570` / `0x416880` / `0x416b90`, `0x4489f0`, `0x448a20`, `CGameStatus::vt+0x34` (`0x4f98d0`), `CGameStatus::vt+0xf0` (`0x4f5470` / `0x4d4dd0`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x42195c` via `CBattle::vt+0x50`)
- **Typed Pseudocode:**
```text
// 1. Spell Swing Roll (0x44db97..0x44dc1c)
voidedFlag: u8 = 0
swing: f32 = 0.0f
if skillId != -1:
    skillData = Table[0x738a58].Find(skillId)
    swingRange: u32 = trunc0_u32(skillData.swingFloat_0x13c * 100.0f) // 0x61e650
    roll: i32 = GlobalRng.Rand(2 * swingRange + 1) // [0, 2*swingRange]
    swing = (f32(roll) - f32(swingRange)) / 100.0f // [-swingRange/100, +swingRange/100]

// 2. Base Stat: INT (2) vs RES Substitution 47 (0x2f) (0x44dc1d..0x44dca3)
stat: f32 = f32(actor.status.GetStat(2)) // INT
if FindCmd(actorMergedCmds, 47 /* 0x2f RES-Based Damage */) != null:
    stat = f32(actor.status.GetStat(3)) // RES
baseStatTerm: f32 = (swing + 2.0f) * stat // 0x6d93f8 = 2.0f

// 3. Dungeon Zone / Field Element Factor (0x44dca8..0x44dd24 -> 0x44fbb0)
if actor.action.type_0x1c == 4:
    savedAction = actor.action
    actor.action.type_0x1c = 2; actor.action.id_0x20 = skillId
    fieldScaledStat: f32 = CBattle__CalcFieldElementRevision(this, actor, mode=0, baseStatTerm)
    actor.action = savedAction
else:
    fieldScaledStat = CBattle__CalcFieldElementRevision(this, actor, mode=0, baseStatTerm)

function CBattle__CalcFieldElementRevision(this: CBattle*, actor: BattleUnit_s*, isPhysical: u8, inputVal: f32) -> f32:
    dungeon = dynamic_cast<CGameModeDungeon*>(this.owner_0x10.mode_0x08) // 0x708c78 -> 0x708c3c
    if dungeon == null or dungeon.map_0x08 == null:
        return 1.0f * inputVal
    tile = dungeon.map_0x08.tiles_0x130 + dungeon.map_0x08.tileIdx_0x134 * 0x230
    z1: i32 = tile.zoneA_0x08; z2: i32 = tile.zoneB_0x0c
    zoneMult: f32 = 1.0f
    if isPhysical != 0:
        if z1 == 3 or z2 == 3: zoneMult = this.physZoneBoost_0x1e4
        if z1 == 5 or z2 == 5: zoneMult *= this.physZoneWeaken_0x1ec
    else: // Magical (mode == 0)
        if z1 == 4 or z2 == 4: zoneMult = this.magZoneBoost_0x1e8
        if z1 == 6 or z2 == 6: zoneMult *= this.magZoneWeaken_0x1f0
    elemMatch: bool = false
    if   IsAttrFire(&actor.action):      elemMatch = (z1 == 7  or z2 == 7)
    elif IsAttrWater(&actor.action):     elemMatch = (z1 == 8  or z2 == 8)
    elif IsAttrWind(&actor.action):      elemMatch = (z1 == 9  or z2 == 9)
    elif IsAttrEarth(&actor.action):     elemMatch = (z1 == 10 or z2 == 10) // 0x4489f0
    elif IsAttrLightning(&actor.action): elemMatch = (z1 == 11 or z2 == 11) // 0x448a20
    if elemMatch:
        zoneMult *= this.elemZoneMult_0x1f4
    return zoneMult * inputVal

// 4. Spell Power (1) & Doll Magic Power Bonus (286 / enchants 304, 305) (0x44dd25..0x44de6c)
spellPower: f32 = CmdValOr0(targetMergedCmds, 1 /* 0x01 Magic Attack */)
isDoll: bool =
    (dynamic_cast<CGamePlayerStatusETCDoll*>(actor.status) != null) or      // 0x7086d0
    (dynamic_cast<CGamePlayerStatusOtherETCDoll*>(actor.status) != null) or // 0x708634
    (dynamic_cast<CGameEnemyStatusETCDoll*>(actor.status) != null)          // 0x708608
if isDoll:
    dollBonusCmd: f32 = CmdValOr0(actorMergedCmds, 286 /* 0x11e Doll Bonus */)
    e304: u32 = actor.status.GetEnchant(304 /* 0x130, stacks */)
    e305: u32 = actor.status.GetEnchant(305 /* 0x131, stacks */)
    dollEnch: f32 = min(0.05f, f32(e304) * 0.02f + f32(e305) * 0.01f)
    spellPower += dollBonusCmd * 500.0f + dollEnch * 500.0f // 0x6d9640 = 500.0f

// 5. Magic Mastery (244), Power Mods (195, 335, EnemyAttack+0x58), & INT Enchants (37, 38) (0x44de6d..0x44dfe9)
mastery: f32 = CmdValOr0(actorMergedCmds, 244 /* 0xf4 Magic Attack Modifier */)
powerMod: f32 = CmdValOr0(actorMergedCmds, 195 /* 0xc3 Waltz */)
              + CmdValOr0(actorMergedCmds, 335 /* 0x14f Fascinating Geas */)
if actor.action.type_0x1c == 0:
    powerMod += Table[0x738a54].Find(actor.action.id_0x20).magPowerBonus_0x58
e37: u32 = actor.status.GetEnchant(37 /* 0x25 Magic attack UP, stacks */)
e38: u32 = actor.status.GetEnchant(38 /* 0x26 Magic attack MiniUP, stacks */)
magAtkEnch: f32 = 1.0f + min(50.0f, f32(e37) * 4.0f + f32(e38) * 2.0f) * 0.01f

offenseBase: f32 = (fieldScaledStat + spellPower * (1.0f + mastery) * (1.0f + powerMod)) * magAtkEnch

// 6. Fantasia (212) & Element Boost (M03.02) (0x44dfea..0x44e437)
fantasia: f32 = CmdValOr0(actorMergedCmds, 212 /* 0xd4 Fantasia */)
offense: f32 = offenseBase * (1.0f + fantasia) * (1.0f + elemBoostCapped)

// 7. Target Magic Defense: RES * 1.5, Status Mods, & RES Enchants (41, 42) (0x44e438..0x44e66d)
mdefStatus: f32 =
    CmdValOr0(targetMergedCmds, 163 /* 0xa3 Magic Defense */) +
    CmdValOr0(targetMergedCmds, 196 /* 0xc4 Samba */) +
    CmdValOr0(targetMergedCmds, 205 /* 0xcd Faded Blossoms */) +
    CmdValOr0(targetMergedCmds, 336 /* 0x150 Alluring Geas */) +
    CmdValOr0(targetMergedCmds, 213 /* 0xd5 Hymn */) +
    CmdValOr0(targetMergedCmds, 220 /* 0xdc Nocturne */) +
    CmdValOr0(targetMergedCmds, 223 /* 0xdf Kotodama Blessing */)
e41: u32 = target.status.GetEnchant(41 /* 0x29 Magic defense UP, stacks */)
e42: u32 = target.status.GetEnchant(42 /* 0x2a Magic defense MiniUP, stacks */)
mdefEnch: f32 = 1.0f + min(50.0f, f32(e41) * 4.0f + f32(e42) * 2.0f) * 0.01f
res: f32 = f32(target.status.GetStat(3)) // RES
defense: f32 = res * 1.5f * (1.0f + mdefStatus) * mdefEnch
rawDiff: f32 = offense - defense // NOT clamped >= 0 here

// 8. Post-Subtraction Magic Attack Buffs (27, 173) (0x44e66e..0x44e6da, applied at 0x44e81e..0x44e835)
postMagAtk: f32 = CmdValOr0(actorMergedCmds, 27 /* 0x1b */) + CmdValOr0(actorMergedCmds, 173 /* 0xad */)
afterMagAtk: f32 = rawDiff * (1.0f + postMagAtk) // passed to M03.02 cuts & elemMult
```
- **Key Invariants:**
  - `_CalcFieldElementRevision` scales ONLY `(2.0f + swing) * stat`; `spellPower` is unaffected by dungeon zone multipliers.
  - `Magic Mastery (244)` and `Waltz (195) + Fascinating Geas (335) + EnemyAttack+0x58` multiply ONLY `spellPower` (including Doll `+500` bonuses), NOT `fieldScaledStat`.
  - `Magic Attack Enchants (37/38)` (`4%/2%`, cap `+50%`) multiply `(fieldScaledStat + scaledSpellPower)`, while `Magic Attack Buffs (27/173)` apply **after** subtracting `defense`.
- **Program Evidence:**
```asm
0044dbc3  movss    xmm0, dword ptr [eax + 0x13c]
0044dbd3  call     0x61e650
0044dbda  lea      ecx, [esi*2 + 1]
0044dbe8  call     0x490790
0044dc58  cmp      eax, 0x2f
0044dc80  push     3
0044dc97  addss    xmm0, dword ptr [0x6d93f8]    ; float 2
0044dcb3  call     0x44fbb0
0044dd25  mov      edx, 1
0044dd4e  push     0x7086d0
0044dd6f  push     0x708634
0044dd8a  push     0x708608
0044dda8  mov      edx, 0x11e
0044ddd2  push     0x130
0044dde7  push     0x131
0044de19  movss    xmm1, dword ptr [0x6d92ec]    ; float 0.05
0044de26  mulss    xmm2, dword ptr [0x6d9640]    ; float 500
0044de6d  mov      edx, 0xf4
0044de94  mov      edx, 0xc3
0044dec8  mov      edx, 0x14f
0044df1f  addss    xmm0, dword ptr [eax + 0x58]
0044df2c  push     0x25
0044df39  push     0x26
0044df80  mov      edx, 0xd4
0044dfdc  addss    xmm2, dword ptr [ebp + 0x34]
0044dfe1  mulss    xmm2, xmm1
0044e411  mov      edx, 0xa3
0044e45f  mov      edx, 0xc4
0044e490  mov      edx, 0xcd
0044e4c1  mov      edx, 0x150
0044e4f2  mov      edx, 0xd5
0044e523  mov      edx, 0xdc
0044e554  mov      edx, 0xdf
0044e583  push     0x29
0044e595  push     0x2a
0044e626  mulss    xmm0, dword ptr [0x6d93bc]    ; float 1.5
0044e65d  subss    xmm1, xmm0
0044e612  mov      edx, 0x1b
0044e695  mov      edx, 0xad
0044fc89  movss    xmm1, dword ptr [esi + 0x1e8]
0044fcb4  mulss    xmm1, dword ptr [esi + 0x1f0]
0044fd70  mulss    xmm1, dword ptr [esi + 0x1f4]
```

---

### M03.02 Element Boost, Elemental Resistance Multiplier, and Magic Damage Cuts

- **Binary VA(s):** `0x44e011..0x44e437`, `0x44e6cb..0x44e86b` (`CBattle::CalcMagicalAttack`), `0x44f5d0..0x44f715` (`CBattle::_CalcElementRevision`)
- **Calls:** `0x415f50` (`IsAttributeFire`), `0x416260` (`IsAttributeWater`), `0x416570` (`IsAttributeWind`), `0x416880` (`IsAttributeEarth`), `0x416b90` (`IsAttributeLightning`), `0x415410` (`IsAttributeSlash`), `0x415710` (`IsAttributePierce`), `0x415a10` (`IsAttributeBlunt`), `0x47e340` (`FindCmd`), `0x44f5d0` (`_CalcElementRevision`), `CGameStatus::vt+0x34` (`0x4f98d0`), `CGameStatus::vt+0xf0` (`0x4f5470` / `0x4d4dd0`)
- **CalledBy:** `CBattle::CalcMagicalAttack` (`0x44e846` for `_CalcElementRevision`; also `CBattle::CalcPhysicalAttack` `0x44bcd0`)
- **Typed Pseudocode:**
```text
// 1. Element Boost (0x44e011..0x44e437)
// Tested on actor.action ([actor+0x18]) in strict mutually-exclusive order:
//   Fire      (0x415f50): cmd 325 (0x145), ench 78 (0x4e), ench 251 (0xfb)
//   Water     (0x416260): cmd 326 (0x146), ench 79 (0x4f), ench 252 (0xfc)
//   Wind      (0x416570): cmd 328 (0x148), ench 80 (0x50), ench 253 (0xfd)
//   Earth     (0x416880): cmd 329 (0x149), ench 81 (0x51), ench 254 (0xfe)
//   Lightning (0x416b90): cmd 327 (0x147), ench 82 (0x52), ench 255 (0xff)
rawElemBoost: f32 = 0.0f
if matchedElem != None:
    if FindCmd(actorMergedCmds, matchedElem.weaponElemCmd) != null:
        rawElemBoost = 0.2f
    // BOTH magicBuffEnch (78..82) AND bothSidesEnch (251..255) are queried on BOTH target AND actor!
    // All 10 enchants have stacks=False (0 or 1 for players; 0 for enemies).
    rawElemBoost += f32(target.status.GetEnchant(matchedElem.magicBuffEnch)) * 0.2f
    rawElemBoost += f32(actor.status.GetEnchant(matchedElem.magicBuffEnch))  * 0.2f
    rawElemBoost += f32(target.status.GetEnchant(matchedElem.bothSidesEnch)) * 0.2f
    rawElemBoost += f32(actor.status.GetEnchant(matchedElem.bothSidesEnch))  * 0.2f

elemBoostCapped: f32 = min(0.4f, rawElemBoost) // 0x6d9334 = 0.4f
offense: f32 = offenseBase * (1.0f + fantasia) * (1.0f + elemBoostCapped) // max 1.4f

// 2. Magic Damage Cuts: Status 183 & Enchants 68/69/70/71 (0x44e6cb..0x44e845)
magicBarrier: f32 = CmdValOr0(targetMergedCmds, 183 /* 0xb7 Magic Barrier */) // negative float
e68: u32 = target.status.GetEnchant(68 /* 0x44 Received magic dmg DOWN, stacks */)
e69: u32 = target.status.GetEnchant(69 /* 0x45 Received magic dmg MiniDOWN, stacks */)
e70: u32 = target.status.GetEnchant(70 /* 0x46 Received dmg DOWN, stacks */)
e71: u32 = target.status.GetEnchant(71 /* 0x47 Received dmg MiniDOWN, stacks */)
enchCut: f32 = max(-0.25f, -(f32(e68)*0.1f + f32(e69)*0.05f + f32(e70)*0.08f + f32(e71)*0.04f))
// Magic Barrier (183) stacks ADDITIVELY with capped enchCut (outside the -0.25f enchant cap)
afterCut: f32 = rawDiff * (1.0f + postMagAtk) * (1.0f + enchCut + magicBarrier)

// 3. Elemental Resistance Multiplier (0x44e846 -> 0x44f5d0..0x44f715)
function CBattle__CalcElementRevision(target: BattleUnit_s*, actor: BattleUnit_s*) -> f32:
    resist: f32 = 0.0f
    if   IsAttrFire(&actor.action):      resist = f32(target.status.GetStat(9))
    elif IsAttrWater(&actor.action):     resist = f32(target.status.GetStat(10))
    elif IsAttrWind(&actor.action):      resist = f32(target.status.GetStat(11))
    elif IsAttrEarth(&actor.action):     resist = f32(target.status.GetStat(12))
    elif IsAttrLightning(&actor.action): resist = f32(target.status.GetStat(13))
    elif IsAttrSlash(&actor.action):     resist = f32(target.status.GetStat(6))
    elif IsAttrPierce(&actor.action):    resist = f32(target.status.GetStat(7))
    elif IsAttrBlunt(&actor.action):     resist = f32(target.status.GetStat(8))
    return (100.0f - resist * 0.5f) * 0.01f // unclamped

rawMagicDmg: f32 = afterCut * CBattle__CalcElementRevision(target, actor) // [ebp+0x18]
```
- **Key Invariants:**
  - Both personal magic-buff enchants (`78..82`) and both-sides enchants (`251..255`) are queried on **both** `target` (`[edi+0x10]`) and `actor` (`[ebx+0x10]`), each adding `+0.2f`, capped at `+0.4f`.
  - Weapon Element IDs are `325=Fire`, `326=Water`, `327=Lightning`, `328=Wind`, `329=Earth`.
  - Enchant cuts `68/69/70/71` (`-10%/-5%/-8%/-4%`) share a `-0.25f` floor (`0x6d978c`); Magic Barrier (`183`) is added outside that cap (`1.0f + enchCut + magicBarrier`).
  - `_CalcElementRevision` returns `(100.0f - resist * 0.5f) * 0.01f` with no clamp (`resist=100 -> 0.5x`, `resist=-100 -> 1.5x`, `resist=200 -> 0.0x`, non-elemental `-> 1.0x`).
- **Program Evidence:**
```asm
0044e019  call     0x415f50
0044e026  mov      edx, 0x145
0044e037  movss    xmm0, dword ptr [0x6d9324]    ; float 0.2
0044e044  mov      ecx, dword ptr [edi + 0x10]
0044e047  push     0x4e
0044e051  mov      ecx, dword ptr [ebx + 0x10]
0044e054  push     0x4e
0044e088  mov      ecx, dword ptr [edi + 0x10]
0044e08b  push     0xfb
0044e0c2  push     0xfb
0044e2e9  mov      ecx, dword ptr [ebx + 0x10]
0044e409  movss    xmm0, dword ptr [0x6d9334]    ; float 0.4
0044e41e  minss    xmm0, xmm1
0044e6ee  cmp      eax, 0xb7
0044e72e  push     0x44
0044e73e  push     0x45
0044e779  push     0x46
0044e7b4  push     0x47
0044e812  movss    xmm0, dword ptr [0x6d978c]    ; float -0.25
0044e81a  maxss    xmm0, xmm1
0044e82b  addss    xmm0, dword ptr [ebp + 0x5c]
0044e846  call     0x44f5d0
0044f6f5  mulss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0044f6fe  movss    xmm0, dword ptr [0x6d9540]    ; float 100
0044f706  subss    xmm0, xmm1
0044f70a  mulss    xmm0, dword ptr [0x6d92d4]    ; float 0.01
```

---

### M03.03 Additive `other` Modifiers (`[ebp+0x44]`)

- **Binary VA(s):** `0x44e857..0x44e87f`, `0x44e8ea..0x44eb24`, `0x44eb59..0x44ed7f`, `0x44ee09..0x44ee28` (`CBattle::CalcMagicalAttack`), `0x557d40..0x557dc6` (enemy race `0`/`3` helpers), `0x46ad40..0x46ad49` (`CGameWork::GetPartyCount`)
- **Calls:** `0x507310` (`[0x7389d8]` EnemyData), `0x557d40` (`IsEnemyRace0`), `0x557da0` (`IsEnemyRace3`), `0x47e340` (`FindCmd`), `CGameStatus::vt+0xf0` (`0x4f5470` / `0x4d4dd0`), `CGameWork::vt+0x148` (`0x46ad40`), `CGameStatus::vt+0x24` (`0x48be10`), `CGameStatus::vt+0x28` (`0x469ef0`), `CGameStatus::vt+0x10` (`0x495b20`)
- **CalledBy:** `CBattle::CalcMagicalAttack` (`0x44e857..0x44ee28`)
- **Typed Pseudocode:**
```text
other: f32 = 0.0f // [ebp+0x44]

if target.isPlayer_0x78 != 0:
    if actor.isPlayer_0x78 == 0:
        // Case A: Enemy attacking Player -> RaceGuard ONLY (ADDITIVE into `other`!) (0x44e8ea..0x44eb20)
        // Enemy race = [Table[0x7389d8].Find([actor.data_0x14 + 0x9c]) + 0x28]:
        //   8 (Demon) -> (227/0xe3, 228/0xe4)   7 (Apparition) -> (229/0xe5, 230/0xe6)
        //   6 (Magic) -> (231/0xe7, 232/0xe8)   4 (Human)      -> (233/0xe9, 234/0xea)
        //   5 (Undead)-> (235/0xeb, 236/0xec)   9 (Dragon)     -> (237/0xed, 238/0xee)
        //   2 (Beast) -> (239/0xef, 240/0xf0)   0 (Fruit, 0x557d40) -> (241/0xf1, 242/0xf2)
        //   3 (Therian, 0x557da0) -> (243/0xf3, 244/0xf4)
        if racePair != None:
            e5:  u32 = target.status.GetEnchant(racePair.oddEnch5Pct)   // stacks=False -> 0 or 1
            e10: u32 = target.status.GetEnchant(racePair.evenEnch10Pct) // stacks=False -> 0 or 1
            other = 0.0f - f32(e5) * 0.05f - f32(e10) * 0.1f            // max -0.15f
    // Else (Player vs Player): jumps to Limit Field (0x44ed53); `other` remains 0.0f.
else:
    // Case C: Target is Enemy (target.isPlayer_0x78 == 0) (0x44eb59..0x44ed50)
    // 1. Effect 88 (0x58 Big Damage to Undead, Demons, and Apparitions)
    targetRace: i32 = Table[0x7389d8].Find(target.data_0x14.enemyId_0x9c).race_0x28
    if targetRace == 5 /* Undead */ or targetRace == 8 /* Demon */ or targetRace == 7 /* Apparition */:
        other = CmdValOr0(actorMergedCmds, 88 /* 0x58 */) + 0.0f

    // 2. Small-Party Enchant 267 (0x10b) (0x44ebe1..0x44ec5b)
    e267: u32 = actor.status.GetEnchant(267 /* 0x10b, stacks=False */)
    partyCount: u32 = CGameWork[0x71fc24].GetPartyCount() // 0x46ad40: total roster size ([+0x44]-[+0x40])>>2
    other += f32(u32(5 - partyCount)) * 0.1f * f32(e267)

    // 3. Full-HP Bonus Enchant 271 (0x10f) (0x44ec5c..0x44eca5)
    if actor.status.GetHp() == actor.status.GetMaxHp():
        other += f32(actor.status.GetEnchant(271 /* 0x10f, stacks=False */)) * 0.1f

    // 4. Level-Difference Bonus Enchants 219 (0xdb) & 220 (0xdc) (0x44eca6..0x44ed4f)
    targetLv: u32 = target.status.GetLevel(); actorLv: u32 = actor.status.GetLevel()
    if targetLv > actorLv: // unsigned strict >
        other += f32(actor.status.GetEnchant(219 /* 0xdb, stacks=False */)) * 0.1f
    if targetLv < actorLv: // unsigned strict <
        other += f32(actor.status.GetEnchant(220 /* 0xdc, stacks=False */)) * 0.1f

// All Cases Reconverge: Limit Field 190 (0xbe) (0x44ed53..0x44ed87)
otherTotal: f32 = other + CmdValOr0(targetMergedCmds, 190 /* 0xbe Limit Field */) // [ebp+0x48]
dmg: i32 = trunc0(rawMagicDmg * (1.0f + otherTotal) * critMult) // 0x44ee09..0x44ee28
```
- **Key Invariants:**
  - **RaceGuard is additive into `other` (`[ebp+0x44]`)**, combining additively with Limit Field (`190`) inside `(1.0f + otherTotal)` rather than multiplying separately.
  - **RaceSlayer enchants are absent** from `CalcMagicalAttack`; magical anti-race damage uses Effect `88` (`0x58`, races `{5, 7, 8}`) instead.
  - Small-Party enchant `267` uses `CGameWork::vt+0x148` (`0x46ad40`), counting total party roster entries (including KO'd members, excluding Dolls/Summons).
  - Full-HP (`271`), Level (`219`/`220`), and Small-Party (`267`) bonuses run ONLY when `target.isPlayer == 0`.
- **Program Evidence:**
```asm
0044e857  xorps    xmm0, xmm0
0044e85a  movss    dword ptr [ebp + 0x44], xmm0
0044e90b  cmp      dword ptr [eax + 0x28], 8
0044e914  push     0xe3
0044e921  push     0xe4
0044ea77  call     0x557d40
0044ea99  call     0x557da0
0044eadb  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0044eae3  subss    xmm1, xmm0
0044eb0f  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
0044eb17  subss    xmm1, xmm0
0044eb1b  movss    dword ptr [ebp + 0x44], xmm1
0044eb73  cmp      dword ptr [eax + 0x28], 5
0044eb8d  cmp      dword ptr [eax + 0x28], 8
0044eba7  cmp      dword ptr [eax + 0x28], 7
0044ebad  mov      edx, 0x58
0044ebe4  push     0x10b
0044ec16  call     dword ptr [eax + 0x148]
0044ec1c  mov      ecx, 5
0044ec24  sub      ecx, eax
0044ec68  cmp      eax, esi
0044ec6f  push     0x10f
0044ecc4  push     0xdb
0044ed19  push     0xdc
0044ed53  mov      edx, 0xbe
0044ed7a  addss    xmm0, dword ptr [ebp + 0x44]
0044ee0e  addss    xmm0, dword ptr [0x6d938c]    ; float 1
0044ee28  cvttss2si esi, xmm0
0046ad40  mov      eax, dword ptr [ecx + 0x44]
0046ad43  sub      eax, dword ptr [ecx + 0x40]
0046ad46  sar      eax, 2
```

---

### M03.04 Living-Only (`87`), Magic Critical (`301`), Demon Wall (`356`), & Post-Floor Multipliers

- **Binary VA(s):** `0x44e85f..0x44e8e9`, `0x44eb25..0x44eb58`, `0x44ed7f..0x44ee30`, `0x44ee87..0x44f0b7`, `0x44f12a..0x44f149` (`CBattle::CalcMagicalAttack`), `0x557ef0..0x557f9f` (`IsEnemyLiving`), `0x43af10..0x43afb8` -> `0x43e6d0..0x43e7df` (`CBattle::GetRowUnits`), `0x4fb5a0..0x4fb5ae` (`IsSleep`), `0x4faf20..0x4fb001` (`HasAilment`)
- **Calls:** `0x47e340` (`FindCmd`), `0x507310` (`[0x738a08]` CharData, `[0x7389d8]` EnemyData), `0x557ef0` (`IsEnemyLiving`), `0x490790` (`GlobalRng::Rand`), `0x43af10` (`GetRowUnits`), `0x44f720` (`_CalcSpecialDamage`), `CGameStatus::vt+0x48` (`0x4fab80`), `CGameStatus::vt+0x7c` (`0x4faf20`), `CGameStatus::vt+0xbc` (`0x4fb5a0`), `CGamePlayerStatus::vt+0x138` (`0x4f2180`), `CGamePlayerStatus::vt+0x13c` (`0x4f6f40`)
- **CalledBy:** `CBattle::CalcMagicalAttack` (`0x44e85f..0x44f149`)
- **Typed Pseudocode:**
```text
// 1. Living-Only Effect 87 (0x57) (0x44e881..0x44e8e7 & 0x44eb25..0x44eb56)
if target.isPlayer_0x78 != 0 and actor.isPlayer_0x78 == 0:
    if FindCmd(actorMergedCmds, 87 /* 0x57 Only Damages Living */) != null:
        charRace: i32 = Table[0x738a08].Find(target.data_0x14.GetCharId()).race_0x44
        if charRace != 4 /* Human */ and charRace != 2 /* Beast */:
            voidedFlag = 1 // [ebp+0x4c] = 1
elif target.isPlayer_0x78 == 0:
    if FindCmd(actorMergedCmds, 87 /* 0x57 Only Damages Living */) != null:
        if not IsEnemyLiving(target.data_0x14.enemyId_0x9c): // 0x557ef0
            voidedFlag = 1
// Player attacking Player skips Effect 87.

function IsEnemyLiving(enemyId: i32) -> bool: // 0x557ef0..0x557f9f
    race: i32 = Table[0x7389d8].Find(enemyId).race_0x28
    return race in {0 /* Fruit */, 2 /* Beast */, 3 /* Therian */,
                    4 /* Human */, 7 /* Apparition */, 8 /* Demon */, 9 /* Dragon */}
    // Returns false for race 5 (Undead), race 6 (Magic Being), and race 1 (unused).

// 2. Hit Roll & Magic Critical 301 (0x12d) (0x44e85f..0x44e86c, 0x44ed7f..0x44ee30)
critMult: f32 = 1.0f; isCrit: u8 = 0
isMiss: bool = (GlobalRng.Rand(100) >= trunc0(hitRate)) // [ebp+0x47]
if not isMiss and FindCmd(actorMergedCmds, 301 /* 0x12d Critical Magic */) != null:
    if GlobalRng.Rand(100) < 20: // 0x14 -> exact 20%
        critMult = 1.25f; isCrit = 1 // 0x6d93a4
(*outResPtr).isCrit_0x31 = isCrit
dmg: i32 = trunc0(rawMagicDmg * (1.0f + otherTotal) * critMult)
// ... Grazing & 1..5 Floor Roll run here (M03.05: 0x44ee31..0x44ee86) ...

// 3. Demon Wall 356 (0x164) (0x44ee87..0x44efe7)
if target.isPlayer_0x78 != 0 and actor.isPlayer_0x78 == 0:
    attackerRace: i32 = Table[0x7389d8].Find(actor.data_0x14.enemyId_0x9c).race_0x28
    if attackerRace in {5 /* Undead */, 8 /* Demon */, 7 /* Apparition */}:
        rowFilter: i32 = (target.row_0x79 == 0) ? 2 : 1 // same row as target
        rowAllies = CBattle__GetRowUnits(this, sort=0, rowFilter, aliveOnly=1) // 0x43af10 -> team=Player
        for allyStatus in rowAllies:
            cmd356 = allyStatus.FindActiveStatus(0, 356 /* 0x164 Demon Wall */)
            if cmd356 != null:
                dmg = trunc0(f32(dmg) + f32(dmg) * cmd356.GetValue())
                if dmg < 0: dmg = 0 // cmovs clamp >= 0
                (*outResPtr).demonWallRefA_0x48 = target.status
                (*outResPtr).demonWallRefB_0x4c = target.status
                (*outResPtr).demonWallCmdId_0x50 = cmd356.GetId()
                (*outResPtr).demonWallRefC_0x54 = target.status
                break // FIRST matching same-row ally only

// 4. Post-Floor Multipliers & Special Damage (0x44efe8..0x44f0b7)
if target.status.IsSleep(): // vt+0xbc (0x4fb5a0: status 116 / 0x74)
    dmg = (dmg * 3) / 2 // signed trunc0 (1.5x)
if actor.status.GetEnchant(280 /* 0x118, stacks=False */) != 0 and
   target.status.HasAilment(): // vt+0x7c (0x4faf20 -> vt+0x68: {113..122, 139})
    dmg = dmg + trunc0(f32(dmg) * 0.15f)
if FindCmd(actorMergedCmds, 86 /* 0x56 Magic Users: Damage x2 */) != null and
   target.isPlayer_0x78 != 0 and target.data_0x14.GetClassId(0) in {12..19}:
    dmg = dmg * 2
if CBattle__CalcSpecialDamage(&dmg, target, actor, &targetMergedCmds, &actorMergedCmds): // 0x44f720
    (*outResPtr).isCrit_0x31 = 0
    (*outResPtr).isSpecialDmg_0x32 = 1

// 5. Critical Interrupt Roll (0x44f12a..0x44f149)
if (*outResPtr).isCrit_0x31 != 0 and GlobalRng.Rand(100) < 33: // 0x21 -> 33%
    (*outResPtr).isInterrupted_0x33 = 1
```
- **Key Invariants:**
  - Effect `87` sets `voidedFlag = 1` without early-returning; damage is zeroed and marked `resultType = 4` at `0x44f0b8..0x44f0c9` (`M03.05`). Because `isCrit` is still rolled on hits, crit-interrupt (`0x44f12a`) can still fire unless `_CalcSpecialDamage` cleared `isCrit`.
  - Magic Critical (`301`) is a flat `20%` proc (`1.25x`) gated only on `!isMiss` and command `301` — it does not invoke `_CalcCritical` (`0x44f190`).
  - Demon Wall (`356`) triggers only for enemy races `{5, 7, 8}` attacking a player, checks all alive same-row player allies via `0x43af10`, and stops at the first match after the `1..5` floor roll.
  - Sleep `1.5x` (`0x4fb5a0`) checks strictly status `116` (`0x74`); Enchant `280` (`0x118`) checks the 11-status `vt+0x68` ailment group `{113 Poison, 114 Freeze, 115 Paralysis, 116 Sleep, 117 Silence, 118 Stun, 119 Instakill, 120 Petrification, 121 Special Petrification, 122 Slow, 139 Special Instakill}`.
- **Program Evidence:**
```asm
0044e86c  movss    dword ptr [ebp + 0x5c], xmm0
0044e881  mov      edx, 0x57
0044e8b7  cmp      dword ptr [eax + 0x44], 4
0044e8db  cmp      dword ptr [eax + 0x44], 2
0044eb2b  mov      edx, 0x57
0044eb41  call     0x557ef0
0044eb56  mov      byte ptr [ebp + 0x4c], cl
00557f14  cmp      dword ptr [eax + 0x28], 0
00557f31  cmp      dword ptr [eax + 0x28], 2
00557f4e  cmp      dword ptr [eax + 0x28], 3
00557f6b  cmp      dword ptr [eax + 0x28], 4
00557f73  call     0x557e60
00557f7e  call     0x557e90
00557f89  call     0x557ec0
0044ed91  cvttss2si ecx, dword ptr [ebp + 0x54]
0044ed98  setge    byte ptr [ebp + 0x47]
0044edbe  cmp      eax, 0x12d
0044eded  cmp      eax, 0x14
0044edf2  movss    xmm0, dword ptr [0x6d93a4]    ; float 1.25
0044edfc  movss    dword ptr [ebp + 0x5c], xmm0
0044eebc  cmp      dword ptr [eax + 0x28], 5
0044eedd  cmp      dword ptr [eax + 0x28], 8
0044eefe  cmp      dword ptr [eax + 0x28], 7
0044ef26  cmp      byte ptr [edi + 0x79], al
0044ef36  call     0x43af10
0044ef59  push     0x164
0044efa1  cvttss2si eax, dword ptr [ebp + 0x50]
0044efa8  cmovs    eax, ecx
0044eff9  lea      eax, [esi + esi*2]
0044f009  push     0x118
0044f040  mov      edx, 0x56
0044f0a0  call     0x44f720
0044f13f  cmp      eax, 0x21
0044f146  mov      byte ptr [eax + 0x33], 1
```

---

### M03.05 Missed-Spell Grazing, Spell Floor Roll, Damage Cap, & Voided/Nullify Interaction

- **Binary VA(s):** `0x44ee31..0x44ee86`, `0x44f0b8..0x44f16c` (`CBattle::CalcMagicalAttack`), `0x421a67..0x421ca6` (`CActionPatternBase::_Task`), `0x4fc1ac..0x4fc1e5` (`CGameStatus` status `192` resistance bonus), `0x416ea0..0x417045` (`IsAttributeNone`)
- **Calls:** `CGameStatus::vt+0xf0` (`0x4f5470` / `0x4d4dd0`), `0x490790` (`GlobalRng::Rand`), `0x48cbf0` (`FindCmdIdx`), `0x47e340` (`FindCmd`), `0x415f50` / `0x416260` / `0x416570` / `0x416880` / `0x416b90`, `0x416ea0` (`IsAttributeNone`, attribute `9`), `CGameStatus::vt+0x50` (`0x4f9910`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x42195c..0x421ca6`)
- **Typed Pseudocode:**
```text
// 1. Missed-Spell Grazing inside CalcMagicalAttack (0x44ee31..0x44ee6f)
if isMiss: // [ebp+0x47] != 0
    if actor.status.GetEnchant(272 /* 0x110, stacks=False */) != 0:
        dmg = (dmg * 3) / 4 // signed trunc0 (lea+cdq+and 3+sar 2)
    else:
        dmg = dmg / 2       // signed trunc0 (cdq+sub+sar 1)
    (*outResPtr).resultType_0x2c = 3 // 3 = Miss / Graze

// 2. Spell Floor Roll (1..5) (0x44ee70..0x44ee86) — applies to BOTH hits and grazed misses
if dmg <= 0:
    dmg = GlobalRng.Rand(5) + 1 // uniform in {1, 2, 3, 4, 5}

// ... Demon Wall (356), Sleep (1.5x), Ailment (+15%), Magic User (x2), _CalcSpecialDamage run here ...

// 3. Living-Only Void Resolution, Damage Cap 296 (0x128), & Output Routing (0x44f0b8..0x44f16c)
if voidedFlag != 0: // Effect 87 (M03.04)
    dmg = 0
    (*outResPtr).resultType_0x2c = 4 // 4 = Voided

capIdx: i32 = FindCmdIdx(actorMergedCmds, 296 /* 0x128 Damage Cap */) // 0x48cbf0
if capIdx != -1:
    capVal: i32 = trunc0(actorMergedCmds[capIdx].GetValue())
    if dmg > capVal: dmg = capVal

if (*outResPtr).resultType_0x2c != 4:
    if FindCmd(actorMergedCmds, 2 /* 0x02 Anti-TP Attack */) != null:
        (*outResPtr).tpDmg_0x24 = dmg; (*outResPtr).tpDmgCopy_0x28 = dmg
    else:
        (*outResPtr).hpDmg_0x1c = dmg; (*outResPtr).hpDmgCopy_0x20 = dmg

if FindCmd(actorMergedCmds, 12 /* 0x0c Self-Destruct */) != null and actor.isPlayer_0x78 == 0:
    actor.data_0x14.selfDestructFlag_0x15d = 1

// 4. Post-Calc Voided / Nullify Interaction in CActionPatternBase::_Task (0x421a67..0x421c81)
// (Runs immediately after CBattle::CalcMagicalAttack returns; this.isPhysical_0x79 == 0)
res: TaskResult* = outRes
if FindCmd(targetCmds, 25 /* 0x19 Magic Hit Determination */) != null:
    res.hpDmg_0x1c = res.hpDmgCopy_0x20 = res.tpDmg_0x24 = res.tpDmgCopy_0x28 = 0x7fffffff
    isVoided = (res.resultType_0x2c != 2)
else:
    isVoided = (res.resultType_0x2c != 2 and res.resultType_0x2c != 3)
res.isVoided_0x38 = isVoided
if isVoided: goto SKIP_POST_CALC // 0x421f5a

// Physical nullify enchants (120..123) skipped when isPhysical_0x79 == 0 (0x421afb -> 0x421bbd)
// Elemental Nullify Enchants (124..128 / 0x7c..0x80, stacks=False):
nullified: bool = false
if   IsAttrFire(action)      and target.status.GetEnchant(124 /* 0x7c */) != 0: nullified = true
elif IsAttrWater(action)     and target.status.GetEnchant(125 /* 0x7d */) != 0: nullified = true
elif IsAttrWind(action)      and target.status.GetEnchant(126 /* 0x7e */) != 0: nullified = true
elif IsAttrEarth(action)     and target.status.GetEnchant(127 /* 0x7f */) != 0: nullified = true
elif IsAttrLightning(action) and target.status.GetEnchant(128 /* 0x80 */) != 0: nullified = true
// Status 192 (0xc0 All Resistances 100): voids ANY action EXCEPT attribute 9 (Non-Elemental)
elif (not IsAttrNone(action) /* 0x416ea0 */) and target.status.HasStatus(192 /* 0xc0 */):
    nullified = true

if nullified: // 0x421b35..0x421b60
    res.hpDmg_0x1c = res.hpDmgCopy_0x20 = res.tpDmg_0x24 = res.tpDmgCopy_0x28 = 0x7fffffff
    res.resultType_0x2c = 4
    res.isVoided_0x38   = 1
    goto SKIP_POST_CALC // 0x421f5a

// Status 192 stat layer (0x4fc1ac..0x4fc1e5): adds +10000 (0x6d9e10) to resistance slots 6..13.
```
- **Key Invariants:**
  - Missed spells graze with signed integer trunc0 (`dmg * 3 / 4` with enchant `272`, else `dmg / 2`), set `resultType = 3`, and then pass through the `dmg <= 0 -> Rand(5) + 1` floor roll and all post-floor modifiers.
  - Damage Cap (`296`) clamps `min(dmg, trunc0(capVal))` after Demon Wall, Sleep `1.5x`, Ailment `+15%`, Magic User `2x`, and `_CalcSpecialDamage`.
  - Nullify Enchants `124..128` (`0x7c..0x80`) and Status `192` (`0xc0`) run in `CActionPatternBase::_Task` after `CalcMagicalAttack` for both Hit (`2`) and Graze (`3`), writing sentinel `0x7fffffff` and `resultType = 4`, skipping Alter Fate (`349`), Barrier (`261`), and Magic Cover.
  - Non-elemental spells (`attribute == 9`, `0x416ea0 == true`) bypass Status `192` in both `_CalcElementRevision` and `_Task`.
- **Program Evidence:**
```asm
0044ee33  mov      ecx, dword ptr [ebx + 0x10]
0044ee36  push     0x110
0044ee47  lea      eax, [esi + esi*2]
0044ee4b  and      edx, 3
0044ee51  sar      esi, 2
0044ee59  sub      eax, edx
0044ee5d  sar      esi, 1
0044ee69  mov      dword ptr [eax + 0x2c], 3
0044ee70  test     ecx, ecx
0044ee7a  push     5
0044ee7c  call     0x490790
0044ee81  lea      esi, [eax + 1]
0044f0b8  cmp      byte ptr [ebp + 0x4c], 0
0044f0c2  mov      dword ptr [eax + 0x2c], 4
0044f0ce  mov      edx, 0x128
0044f0d9  call     0x48cbf0
0044f0fa  cmovg    esi, eax
0044f105  mov      edx, 2
00421b35  mov      dword ptr [ebx + 0x1c], 0x7fffffff
00421b51  mov      dword ptr [ebx + 0x2c], 4
00421b58  mov      byte ptr [ebx + 0x38], 1
00421bc0  call     0x415f50
00421bcb  push     0x7c
00421be0  call     0x416260
00421beb  push     0x7d
00421c00  call     0x416570
00421c0b  push     0x7e
00421c20  call     0x416880
00421c2b  push     0x7f
00421c40  call     0x416b90
00421c4b  push     0x80
00421c63  call     0x416ea0
00421c6e  push     0xc0
004fc1b0  push     0xc0
004fc1be  movaps   xmm1, xmmword ptr [0x6d9e10]
```

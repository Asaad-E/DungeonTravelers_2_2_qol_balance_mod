# M02 — Physical Damage, Criticals & Multi-Hit (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x417cd0..0x56e182`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`)**
> Every physical damage stage, stat substitution, swing roll, field/zone revision, range/row factor, damage cut, elemental/physical resistance, racial slayer/guard, additive `other` modifier, post-truncation override, special/fixed damage cascade, damage cap, critical roll, crit-triggered Murder, and multi-hit count table is specified directly from `backups/exe/DT22_en_unwrapped.vanilla.exe`.

---

## 1. End-to-End Physical Damage Pipeline Order

```
Action_s::SetHitCount (0x417cd0) [M02.07] -> hitCount (cmds 89..100, 178 + Rondo 210 + Triple 252 / Double 251)
  │
  ▼  (per hit, hitSeqIdx = [actionPattern+0x88], isCounter = [actionPattern+0x11])
CActionPatternBase::_Task (0x42105b..0x42172c): if [action+0x48] != 0 (Furious) injects cmd 69 & cmd 72
  │
  ▼  CBattle::CalcPhysicalAttack (0x44a850..0x44d366, vtable +0x4c = 0x6c9bac)
  ├── 0. Hit Roll (0x44a9e6..0x44b21c; see M04): on miss, jumps to 0x44d339 (cmd 12 exit flag)
  ├── 1. [M02.01] Base Stat (ATK / 47 RES / 49 INT) * cmd50 * (2 + swing) -> _CalcFieldElementRevision(mode=1) = atkValA
  │     └── atkValB = atkValA * (1 + skillAtkMod[26, 443@20%, 111, enemySkill, Doll 286/304/305, 161/195/335/219, JoinAtk]) * (1 + 0.01*atkEnch[29/30<=50])
  │     └── defValA = cmd69 ? 0 : (DEF * 1.35) * (1 + defSkillMod[28/162/187/196/205/336/219]) * (1 + 0.01*defEnch[33/34<=50])
  │     └── baseDmgA = atkValB * cmd73 - defValA
  ├── 2. [M02.02] baseDmgB = baseDmgA * rangeFactor (0x44a7a0/0x44a7d0, Doll override) * dmgCut (max(0.75, 1 - 66/67/70/71))
  ├── 3. [M02.03] _CalcElementRevision (0x44f5d0), Race Guard/Slayer + Effect 88 + Feline/Sea, Effect 87 flag, Both-Sides Elem Boost (251..255)
  ├── 4. [M02.06] _CalcCritical (0x44f190) -> critMult (1.25f / 1.0f), sets TaskResult[0].isCrit ([+0x31])
  ├── 5. [M02.02] defendMult (0.5f if Defense or Auto-Guard 255)
  │     └── baseDmgC = (((((baseDmgB * raceSlayer) * elemRes) * elemBoost) * defendMult) * raceGuard) * critMult
  ├── 6. [M02.04] other = sum(StatCount71[22 statuses], Hit136, MatGuard179, Lim190, Eff191[!counter], ImpGuard308[min],
  │                           DarkQuest263[11 ailments], JoinEnch261/290, SmallParty267, FullHP271, LvDiff219/220)
  │     └── dmg: i32 = trunc0(baseDmgC * (1.0f + other))   // cvttss2si at 0x44cacc
  ├── 7. [M02.05] WarningShot (3/10) -> MinRoll (<=0: INVERTED isCrit==1 ? Rand(2)+1 : 3) -> DemonWall 356 ->
  │               PosTrance 440 (X17 threshold 100.0f) -> Sleep 1.5x -> Ailed 280 (+15%) -> MagicUser 86 (2x) ->
  │               _CalcSpecialDamage (0x44f720, 9 cmds + Lim190) -> Effect 87 zero (resultType=4) -> Cap 296 (0x48c640)
  └── 8. [M02.06] Chant Interrupt + Crit 33% Interrupt -> Crit-Triggered Murder 258 (CCommand_0119) -> Cmd 12 Exit Flag
```

**Conventions:** `trunc0(x)` = x86 `cvttss2si` (round toward zero); `round_f32_to_i32(x)` = helper `0x61e650`; `Rand(n)` = `CRandom::Get([0x816ce8], n)` (`0x490790` / wrapper `0x505ac0`), returning `0..n-1`; `Ench(u, id)` = `u.status->vtable+0xf0(id)` (`u32` converted to `f32` via `0x6d9fd0`); `FindCmd(v, id)` = `0x47e340`; `CmdVal(v, id)` = `0x47e400` (`0.0f` if absent). `ActionType` (`[unit+0x1c]` / `[act+0x04]`, jump table `0x43f048`): `0=CActionJoinAttack`, `1=CActionAttack`, `2/3=CActionSkill`, `4=CActionItem`, `5=CActionDefense`, `6=CActionEscape`, `7=NoOp`, `8/9=CActionEnemyAttack`.

---

## 2. Binary Rules (`M02.01` – `M02.07`)

### M02.01 Base Physical ATK/DEF, Stat Substitution, Swing, Weapon/Skill Rank, Status/Enchant Modifiers & Ignore-DEF

- **Binary VA(s):** `0x44b221..0x44baae` (`CBattle::CalcPhysicalAttack` ATK/DEF/BaseDmgA stage), `0x42105b..0x4210b7` (`CActionPatternBase::_Task` Furious / Ignore-DEF `69` injection), `0x4f4f60..0x4f4fa0` (`GetEquipmentID`), `0x5593f0..0x559412` (weapon table `[0x7389e0]`), `0x5587c0..0x5587e2` (enemy table `[0x7389d8]`), `0x5576a0..0x5576c2` (enemy skill table `[0x7389d4]`), `0x56e160..0x56e182` (joint-attack skill table `[0x738a54]`)
- **Calls:** `0x47e340` (`FindCommand`), `0x490790` (`CRandom::Get`), `0x61e650` (`round_f32_to_i32`), `0x44fbb0` (`CBattle::_CalcFieldElementRevision`, see `M02.03`), `0x4f4f60`, `0x5593f0`, `0x5587c0`, `0x5576a0`, `0x56e160`, `0x61edf4` (`__RTDynamicCast`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x42172c` via `CBattle` vtable `+0x4c` = `0x6c9bac`)
- **Typed Pseudocode:**
```text
// Entered at 0x44b221 after physical hit roll succeeds (miss jumps to 0x44d339).
// actor = [ebp+0x18] (ebx), target = [ebp+0x10] (edi),
// actorCmds = [ebp-0x2c], targetCmds = [ebp-0x48].

// 1. Base Offensive Stat & Stat Substitution (0x44b22b..0x44b2b5)
// CGameStatusBase::vtable+0x34(idx): 0=ATK, 1=DEF, 2=INT, 3=RES
statVal: f32 = f32(actor.status->GetStat(0))               // default: ATK (idx 0)
if FindCmd(actorCmds, 47 /* 0x2f */) != null:
    statVal = f32(actor.status->GetStat(3))                // substitute RES (idx 3)
if FindCmd(actorCmds, 49 /* 0x31 */) != null:
    statVal = f32(actor.status->GetStat(2))                // substitute INT (idx 2; overrides 47 if both present)
if (cmd50 = FindCmd(actorCmds, 50 /* 0x32 */)) != null:
    statVal = statVal * cmd50->GetVal()                    // command 50 stat multiplier

// 2. Weapon / Monster Swing Roll & Attack Value A (0x44b2b6..0x44b3a9)
variance: f32
if actor.isPlayerSide_0x78 != 0:
    wepId: i32 = GetEquipmentID(actor.status2_0x14, 0)     // slot 0 = main hand
    variance = (wepId == -1) ? 0.0f : WeaponTable_0x5593f0(wepId).variance_0x48
else:
    variance = EnemyTable_0x5587c0(actor.status2_0x14.enemyId_0x9c).variance_0x40
v: i32 = round_f32_to_i32(variance * 100.0f)               // 0x61e650
swingRoll: i32 = GlobalRng_0x816ce8.Rand(2 * v + 1)        // [0 .. 2*v]
swing: f32 = (f32(swingRoll) - f32(u32(v))) / 100.0f       // [-v/100 .. +v/100]
atkSwung: f32 = statVal * (2.0f + swing)                   // float 2.0 at 0x6d93f8
// Field Element / Zone Revision (mode = 1 physical; xmm1=atkSwung -> xmm0=atkValA, see M02.03)
atkValA: f32 = this->_CalcFieldElementRevision(atkSwung, actor, isPhysical=1) // 0x44b3a0

// 3. Skill / Status / Lance / Enemy / Doll / Joint-Attack ATK Modifiers (0x44b3aa..0x44b692)
skillAtkMod: f32 = 0.0f
elbowGreaseTriggered: u8 = 0                               // [ebp+0x1f]
if (cmd26 = FindCmd(actorCmds, 26 /* 0x1a */)) != null:
    skillAtkMod = cmd26->GetVal() + 0.0f
    // Elbow Grease 443 (0x1bb) is STRICTLY gated inside `if (cmd26 != null)`!
    if (cmd443 = FindCmd(actorCmds, 443 /* 0x1bb */)) != null:
        if GlobalRng_0x816ce8.Rand(100) < 20:              // 0x44b411: cmp esi, 0x14; jge skip (20% proc)
            skillAtkMod += cmd443->GetVal()
            elbowGreaseTriggered = 1u8                     // emits passive banner at 0x44cee1

// 2H Lance Bonus 111 (0x6f) & Enemy/Summon Skill Power Table (0x44b434..0x44b4a5)
if (cmd111 = FindCmd(actorCmds, 111 /* 0x6f */)) != null:
    if actor.isPlayerSide_0x78 == 0:
        goto add_enemy_skill_power                         // 0x44b44b: non-player skips 111 -> 0x44b48f
    wepId = GetEquipmentID(actor.status2_0x14, 0)
    if u32(wepId - 183 /* 0xb7 */) <= 16u:                 // weapon IDs 183..199 (0xb7..0xc7, 2H Lances)
        skillAtkMod += cmd111->GetVal()
if actor.isPlayerSide_0x78 == 0 || u32(actor.unitId_0x04 - 3000 /* 0xbb8 */) <= 999u /* 0x3e7 */:
add_enemy_skill_power:
    skillAtkMod += EnemySkillTable_0x5576a0(actor.enemySkillId_0x28).atkMod_0x3c

// Doll Physical Power Bonus 286 (0x11e) + Enchants 304 (0x130) & 305 (0x131) (0x44b4a6..0x44b5b1)
isDoll: bool =
    dynamic_cast<CGamePlayerStatusETCDoll*>(actor.status)      != null || // RTTI 0x7086d0
    dynamic_cast<CGamePlayerStatusOtherETCDoll*>(actor.status) != null || // RTTI 0x708634
    dynamic_cast<CGameEnemyStatusETCDoll*>(actor.status)       != null    // RTTI 0x708608
if isDoll:
    dollCmd: f32 = CmdVal(actorCmds, 286 /* 0x11e */)
    dollEnch: f32 = min(0.05f,                             // capped at 0.05f (0x6d92ec)
        f32(u32(Ench(actor, 304 /* 0x130 */))) * 0.02f +
        f32(u32(Ench(actor, 305 /* 0x131 */))) * 0.01f)
    skillAtkMod += dollCmd + dollEnch

// Active ATK Buff/Debuff Commands (0x44b5b2..0x44b675)
skillAtkMod += CmdVal(actorCmds, 161 /* 0xa1 */)
skillAtkMod += CmdVal(actorCmds, 195 /* 0xc3 */)
skillAtkMod += CmdVal(actorCmds, 335 /* 0x14f */)
skillAtkMod += CmdVal(actorCmds, 219 /* 0xdb */)

// Joint-Attack (Co-op Skill) Power Table (0x44b66c..0x44b692)
if actor.actionType_0x1c == 0:                             // CActionJoinAttack (jump table 0x43f048 case 0)
    skillAtkMod += JoinAttackTable_0x56e160(actor.joinAtkId_0x20).atkMod_0x40

// 4. Actor ATK Enchants (29, 30) & Attack Value B (0x44b693..0x44b789)
atkEnch: f32 = min(50.0f,                                  // capped at 50.0f (0x6d94e0)
    f32(u32(Ench(actor, 29 /* 0x1d */))) * 4.0f +
    f32(u32(Ench(actor, 30 /* 0x1e */))) * 2.0f)
atkValB: f32 = atkValA * (1.0f + skillAtkMod) * (atkEnch * 0.01f + 1.0f)

// 5. Target DEF Statuses, Enchants (33, 34) & Defense Value A (0x44b78a..0x44b9fb)
defSkillMod: f32 =
    CmdVal(targetCmds, 28  /* 0x1c */) +
    CmdVal(targetCmds, 162 /* 0xa2 */) +
    CmdVal(targetCmds, 187 /* 0xbb */) +
    CmdVal(targetCmds, 196 /* 0xc4 */) +
    CmdVal(targetCmds, 205 /* 0xcd */) +
    CmdVal(targetCmds, 336 /* 0x150 */) +
    CmdVal(targetCmds, 219 /* 0xdb */)
defEnch: f32 = min(50.0f,                                  // capped at 50.0f (0x6d94e0)
    f32(u32(Ench(target, 33 /* 0x21 */))) * 4.0f +
    f32(u32(Ench(target, 34 /* 0x22 */))) * 2.0f)
defValA: f32 = (f32(target.status->GetStat(1)) * 1.35f) * (1.0f + defSkillMod) * (defEnch * 0.01f + 1.0f)

// 6. Skill Multiplier (73), Ignore-DEF (69 / Furious) & Base Damage A (0x44b9fc..0x44baae)
// In CActionPatternBase::_Task (0x42105b..0x4210b7), if action.isFurious ([action+0x48] != 0),
// commands 69 (0x45, Ignore-DEF, val=1.0f) and 72 (0x48, Guaranteed Hit, val=1.0f) are injected into actorCmds.
multN: f32 = (c73 = FindCmd(actorCmds, 73 /* 0x49 */)) ? c73->GetVal() : 1.0f
if FindCmd(actorCmds, 69 /* 0x45 */) != null:
    defValA = 0.0f
baseDmgA: f32 = atkValB * multN - defValA                  // NOT clamped to >= 0 here
```
- **Program Evidence:**
```asm
0044b23c  mov      edx, 0x2f
0044b250  call     0x47e340
0044b26f  mov      edx, 0x31
0044b296  mov      edx, 0x32
0044b2f9  call     0x61e650
0044b36e  addss    xmm0, dword ptr [0x6d93f8]    ; float 2
0044b3a0  call     0x44fbb0
0044b3b4  mov      edx, 0x1a
0044b3db  mov      edx, 0x1bb
0044b411  cmp      esi, 0x14
0044b434  mov      edx, 0x6f
0044b457  add      eax, 0xffffff49
0044b45c  cmp      eax, 0x10
0044b4fd  mov      edx, 0x11e
0044b527  push     0x130
0044b53c  push     0x131
0044b56e  movss    xmm1, dword ptr [0x6d92ec]    ; float 0.05
0044b66c  cmp      dword ptr [ebx + 0x1c], 0
0044b67f  call     0x56e160
0044b6bf  mulss    xmm0, dword ptr [0x6d9430]    ; float 4
0044b706  minss    xmm1, xmm0
0044b9c0  mulss    xmm1, dword ptr [0x6d93b0]    ; float 1.35
0044ba0f  mov      edx, 0x49
0044ba33  mov      edx, 0x45
0044ba8e  subss    xmm0, dword ptr [ebp - 0x4c]
0042105e  cmp      byte ptr [eax + 0x48], 0
0042106c  mov      edx, 0x45
```

---

### M02.02 Range & Row Factor, Damage Cuts, Defending Multiplier & Min/Crit-Min Damage Roll

- **Binary VA(s):** `0x44a7a0..0x44a7c5` (`CBattle::_GetRowDistance`, vtable `+0x3c`), `0x44a7d0..0x44a847` (`CBattle::_GetAttackRangeRevision`, vtable `+0x40`), `0x43ea20..0x43ea43` (`CBattleBase::_GetAttackRangeRevisionForUnits`, vtable `+0x44`), `0x44baaf..0x44bcc8` (Doll range override + Physical/All Damage Cut enchants `66, 67, 70, 71`), `0x44c550..0x44c607` (Defending multiplier + `baseDmgC` product), `0x417309..0x417368` (Auto-Guard passive `255` setting `[unit+0x104] = 1`), `0x44cb12..0x44cb5e` (Guaranteed Minimum & inverted crit-min damage roll)
- **Calls:** `0x61edf4` (`__RTDynamicCast`), `0x44a7a0`, `0x44a7d0`, `0x43ea20`, `0x43ea50` (`IsActionType`), `0x505ac0` (`Rand(n)`)
- **CalledBy:** `CBattle::CalcPhysicalAttack` (`0x44baaf..0x44cb5e`)
- **Typed Pseudocode:**
```text
// 1. Row Distance (CBattle::_GetRowDistance, 0x44a7a0..0x44a7c5)
// [unit+0x79]: 1 = Front Row, 0 = Back Row
function CBattle_GetRowDistance(actor: BattleUnit_s*, target: BattleUnit_s*) -> i32:
    // Front-to-Front => 0, Front-to-Back or Back-to-Front => 1, Back-to-Back => 2
    if actor.isFrontRow_0x79 != 0:
        return (target.isFrontRow_0x79 == 0) ? 1 : 0
    else:
        return (target.isFrontRow_0x79 == 0) ? 2 : 1

// 2. Range & Row Factor (CBattle::_GetAttackRangeRevision, 0x44a7d0..0x44a847)
// range: 0=Short (S), 1=Medium (M), 2=Long (L), 3=Unlimited (LL/Special)
function CBattle_GetAttackRangeRevision(dist: i32, range: i32) -> f32:
    if range == 0:                                         // Short (S)
        if dist == 1: return 0.75f                         // 0x3f400000
        if dist == 2: return 0.50f                         // 0x3f000000
        return 1.0f                                        // dist == 0
    else if range == 1:                                    // Medium (M)
        if dist == 2: return 0.75f                         // 0x3f400000
        return 1.0f                                        // dist in {0, 1}
    else if range == 2 || range == 3:                      // Long (L) or Unlimited
        return 1.0f                                        // 0x3f800000
    else:
        AssertFail("Battle::CBattle::_GetAttackRangeRevision", 0x5dd)

// Doll Range Override in CalcPhysicalAttack (0x44baaf..0x44bb6e):
// Checks dynamic_cast<CGamePlayerStatusETCDoll*>(actor.status) -> dollType = [p+0x180]
//     or dynamic_cast<CGamePlayerStatusOtherETCDoll*>           -> dollType = [p+0x190]
//     or dynamic_cast<CGameEnemyStatusETCDoll*>                 -> dollType = [p+0x19c]
// If matched and dollType in { 228 (0xe4)->range 0, 229 (0xe5)->range 1, 231 (0xe7)->range 2 }:
//     rangeFactor = _GetAttackRangeRevision(_GetRowDistance(actor, target), range)
// Else (all non-Dolls and other Doll IDs):
//     rangeFactor = CBattleBase::vtable_44(actor, target) // 0x43ea20 -> uses [actor+0x4c]

// 3. Physical & All-Damage Cut Enchants (0x44bb6f..0x44bcc8)
// Target enchants: 66 (0x42)=PhysCut L (-10%), 67 (0x43)=PhysCut S (-5%),
//                  70 (0x46)=AllCut L  (-8%),  71 (0x47)=AllCut S  (-4%)
dmgCut: f32 = 1.0f
    - f32(u32(Ench(target, 66 /* 0x42 */))) * 0.10f        // 0x6d930c
    - f32(u32(Ench(target, 67 /* 0x43 */))) * 0.05f        // 0x6d92ec
    - f32(u32(Ench(target, 70 /* 0x46 */))) * 0.08f        // 0x6d9300
    - f32(u32(Ench(target, 71 /* 0x47 */))) * 0.04f        // 0x6d92e8
dmgCut = max(0.75f, dmgCut)                                // floored at 0.75f (max 25% cut, 0x6d9368)
baseDmgB: f32 = baseDmgA * rangeFactor * dmgCut

// 4. Defending & Auto-Guard Multiplier (0x44c550..0x44c605)
// 0x43ea50(unit, type): returns (unit.actionType_0x1c != 7) && (unit.actionType_0x1c == type)
// [target+0x104] is set to 1 by Auto-Guard passive 255 (0xff) when Rand(100) < trunc0(cmd255.val * 100.0f) (0x417309..0x417368)
defendMult: f32 = (IsActionType(target, 5 /* Defense */) || target.autoGuardFlag_0x104 != 0) ? 0.5f : 1.0f

// Product into Base Damage C (0x44c5c8..0x44c5ee, left-to-right IEEE-754 f32 order):
baseDmgC: f32 = (((((baseDmgB * raceSlayerFactor) * elemResFactor) * elemBothUpFactor) * defendMult) * raceGuardFactor) * critMult

// 5. Guaranteed Minimum & Crit-Min Damage Roll (0x44cb12..0x44cb5e)
// Executed AFTER trunc0(baseDmgC * (1.0f + other)) (0x44cacc) and Warning Shot 3/10 (0x44cae1..0x44cb11).
// VANILLA INVERTED PARITY QUIRK at 0x44cb24..0x44cb49:
//   TaskResult[0].isCrit ([res0+0x31]) is 1 on crit (critMult != 1.0f) and 0 on non-crit (0x44c4ea..0x44c517).
//   At 0x44cb24..0x44cb3a, the binary converts byte isCrit to f32 and executes `ucomiss xmm0, 1.0f; lahf; test ah, 0x44; jp 0x44cb49`:
//     - isCrit == 1 (CRIT):     1.0f == 1.0f => ZF=1,PF=0 => ah&0x44 == 0x40 (odd parity, PF=0) => jp NOT taken => Rand(2) + 1 (1 or 2)
//     - isCrit == 0 (NON-CRIT): 0.0f != 1.0f => ZF=0,PF=0 => ah&0x44 == 0x00 (even parity, PF=1) => jp TAKEN    => fixed 3
if dmg <= 0:
    if f32(TaskResult[0].isCrit_0x31) == 1.0f:             // true when isCrit == 1 (CRIT)
        dmg = Rand(2) + 1                                  // 0x505ac0(2) + 1 -> 1 or 2
    else:                                                  // true when isCrit == 0 (NON-CRIT)
        dmg = 3                                            // 0x44cb49
```
- **Program Evidence:**
```asm
0044a7ab  cmp      byte ptr [eax + 0x79], 0
0044a7d5  mov      dword ptr [esp], 0x3f800000
0044a7ee  mov      dword ptr [esp], 0x3f000000
0044a808  mov      dword ptr [esp], 0x3f400000
0044bb72  push     0x42
0044bb8a  push     0x43
0044bbc5  push     0x46
0044bc00  push     0x47
0044bc5f  movss    xmm0, dword ptr [0x6d9368]    ; float 0.75
0044bc67  maxss    xmm0, xmm1
0044c562  push     5
0044c565  call     0x43ea50
0044c56e  cmp      byte ptr [edi + 0x104], al
0044c576  movss    xmm0, dword ptr [0x6d9348]    ; float 0.5
0044cb12  cmp      dword ptr [ebp - 0x1c], 0
0044cb19  jg       0x44cb5f
0044cb24  movzx    eax, byte ptr [eax + 0x31]
0044cb2f  ucomiss  xmm0, dword ptr [0x6d938c]    ; float 1
0044cb36  lahf     
0044cb37  test     ah, 0x44
0044cb3a  jp       0x44cb49
0044cb3c  mov      ecx, 2
0044cb41  call     0x505ac0
0044cb46  inc      eax
0044cb49  mov      eax, 3
```

---

### M02.03 Elemental/Physical Resistance, Race Slayer/Guard, Effects `87`/`88`, Element Boost & Zone Factor

- **Binary VA(s):** `0x44f5d0..0x44f715` (`CBattle::_CalcElementRevision`), `0x44fbb0..0x44fdd2` (`CBattle::_CalcFieldElementRevision`), `0x448be6..0x448c18` & `0x4498f8..0x4499b2` (zone multipliers `[battle+0x1e4..0x1f4]`), `0x4489f0..0x448a44` (Earth `10` / Thunder `11` zone predicates), `0x44bccc..0x44c4ca` & `0x44ce48..0x44ce75` (Race Guard/Slayer, Effects `87`/`88`, Feline/Sea, Both-Sides Element Boost in `CalcPhysicalAttack`), `0x557d40..0x557f9f` (enemy race & living predicates), `0x55d810..0x55d865` (player living predicate), `0x4f21c0..0x4f2261` (Feline `0x6d3820` & Sea Creature `0x6d38b0` ID tables), `0x415410..0x416e84` (`CParameterSkill::IsAttribute*`)
- **Calls:** `0x415f50` (`IsFire`), `0x416260` (`IsWater`), `0x416570` (`IsWind`), `0x416880` (`IsEarth`), `0x416b90` (`IsThunder`), `0x415410` (`IsCut`), `0x415710` (`IsStab`), `0x415a10` (`IsHit`), `0x4489f0`, `0x448a20`, `0x61edf4`, `0x47e340`, `0x5587c0`, `0x557d40..0x557ef0`, `0x55d810`, `0x4f21c0`, `0x4f21f0`
- **CalledBy:** `CBattle::CalcPhysicalAttack` (`0x44b3a0`, `0x44bcd0`), `CBattle::CalcMagicalAttack` (`0x44dcb3`, `0x44dcfc`, `0x44e846`)
- **Typed Pseudocode:**
```text
// Attribute predicates on (CParameterSkill*)(attacker + 0x18):
//   Skill/enemy attribute enum: 1=Cut, 2=Stab, 3=Hit, 4=Fire, 5=Water, 6=Wind, 7=Earth, 8=Thunder.
//   Player elemental fallback (0x416193..0x416e58): checks weapon-element statuses via vtable+0x50:
//     325(0x145)=Fire, 326(0x146)=Water, 327(0x147)=Thunder, 328(0x148)=Wind, 329(0x149)=Earth;
//     any other active element status forces false; else own status -> true;
//     else weapon/equip enchant != 0 for 78(0x4e)=Fire, 79(0x4f)=Water, 80(0x50)=Wind, 81(0x51)=Earth, 82(0x52)=Thunder.
//   Player physical fallback (0x41563f..0x415cba): weapon flags [+0x6c]: Cut=(f>>6)&1, Stab=(f>>7)&1, Hit=(f>>8)&1.

// 1. Elemental / Physical Resistance Revision (CBattle::_CalcElementRevision, 0x44f5d0..0x44f715)
function CBattle_CalcElementRevision(target: BattleUnit_s*, attacker: BattleUnit_s*) -> f32:
    sk = (CParameterSkill*)(attacker + 0x18)
    res: f32 = 0.0f                                        // strict priority: elemental overrides physical
    if      sk.IsFire():    res = f32(target.status->GetStat(9))  // 0x09
    else if sk.IsWater():   res = f32(target.status->GetStat(10)) // 0x0a
    else if sk.IsWind():    res = f32(target.status->GetStat(11)) // 0x0b
    else if sk.IsEarth():   res = f32(target.status->GetStat(12)) // 0x0c
    else if sk.IsThunder(): res = f32(target.status->GetStat(13)) // 0x0d
    else if sk.IsCut():     res = f32(target.status->GetStat(6))  // 0x06
    else if sk.IsStab():    res = f32(target.status->GetStat(7))  // 0x07
    else if sk.IsHit():     res = f32(target.status->GetStat(8))  // 0x08
    return (100.0f - (res * 0.5f)) * 0.01f                 // no internal clamp; 0x6d9348/0x6d9540/0x6d92d4

// 2. Living Predicates & Race IDs (0x557d40..0x557f9f, 0x55d810..0x55d865)
// Enemy raceId = EnemyTable[id].race_0x28 == EnemySub_0x5587c0(id).race_0x10:
//   0x557d40: 0(Fruit)   0x557d70: 2(Beast)      0x557da0: 3(Therian)   0x557dd0: 4(Human)
//   0x557e00: 5(Undead)  0x557e30: 6(MagicBeing) 0x557e60: 7(Apparition) 0x557e90: 8(Demon)  0x557ec0: 9(Dragon)
// IsEnemyLiving_0x557ef0(id): returns (race in {0, 2, 3, 4, 7, 8, 9}); FALSE for 5(Undead) & 6(MagicBeing)!
// IsPlayerLiving_0x55d810(charId): PlayerTable[0x738a08][charId].race_0x44 in {2, 4}.

// 3. Race Guard, Race Slayer, Effects 87 & 88, Feline/Sea & Both-Sides Element Boost (0x44bccc..0x44c4ca)
elemResFactor: f32    = this->_CalcElementRevision(target, attacker) // [ebp-0x10]
raceGuardFactor: f32  = 1.0f                                         // [ebp-0x18]
elemBothUpFactor: f32 = 1.0f                                         // [ebp-0x4c]
raceSlayerFactor: f32 = 1.0f                                         // [ebp-0x14]
nonLivingZero: bool   = false                                        // [ebp-0x3c]

if target.isPlayerSide_0x78 != 0:
    if attacker.isPlayerSide_0x78 == 0:                    // Enemy -> Player
        if FindCmd(actorCmds, 87 /* 0x57 */) != null && !IsPlayerLiving_0x55d810(target.status2->vtable_138()):
            nonLivingZero = true                           // 0x44bd05..0x44bd38
        r: i32 = EnemySub_0x5587c0(attacker.status2.enemyId_0x9c).race_0x10
        // Race Guard (0x44bd3b..0x44bf0e), (race -> [ench_5pct, ench_10pct]):
        //   8(Demon)->[227(0xe3),228(0xe4)], 7(Apparition)->[229(0xe5),230(0xe6)], 6(MagicBeing)->[231(0xe7),232(0xe8)],
        //   4(Human)->[233(0xe9),234(0xea)], 5(Undead)->[235(0xeb),236(0xec)],     9(Dragon)->[237(0xed),238(0xee)],
        //   2(Beast)->[239(0xef),240(0xf0)], 0(Fruit)->[241(0xf1),242(0xf2)],      3(Therian)->[243(0xf3),244(0xf4)]
        if r in {8, 7, 6, 4, 5, 9, 2, 0, 3}:               // no floor clamp
            raceGuardFactor = (1.0f - f32(u32(Ench(target, e5))) * 0.05f) - f32(u32(Ench(target, e10))) * 0.10f
else:                                                      // Target is Enemy
    id: u32 = target.status2.enemyId_0x9c
    if FindCmd(actorCmds, 87 /* 0x57 */) != null && !IsEnemyLiving_0x557ef0(id):
        nonLivingZero = true                               // 0x44bf13..0x44bf44; zeroes dmg at 0x44ce48 (resultType=4)
    r: i32 = EnemySub_0x5587c0(id).race_0x10
    if r == 5 /* Undead */ || r == 8 /* Demon */ || r == 7 /* Apparition */: // Effect 88 (0x58)
        raceSlayerFactor = CmdVal(actorCmds, 88 /* 0x58 */) + 1.0f
    // Race Slayer enchants on attacker (0x44bfa2..0x44c364; additive onto raceSlayerFactor; NO Therian(3) branch!):
    if      IsRace8_0x557e90(id): raceSlayerFactor += 0.30f*Ench(actor,170/*0xaa*/) + 0.15f*Ench(actor,171/*0xab*/) + 0.60f*Ench(actor,203/*0xcb*/)
    else if IsRace7_0x557e60(id): raceSlayerFactor += 0.30f*Ench(actor,172/*0xac*/) + 0.15f*Ench(actor,173/*0xad*/) + 0.60f*Ench(actor,204/*0xcc*/)
    else if IsRace6_0x557e30(id): raceSlayerFactor += 0.30f*Ench(actor,174/*0xae*/) + 0.15f*Ench(actor,175/*0xaf*/) + 0.60f*Ench(actor,205/*0xcd*/)
    else if IsRace4_0x557dd0(id): raceSlayerFactor += 0.60f*Ench(actor,176/*0xb0*/) + 0.30f*Ench(actor,177/*0xb1*/) + 0.15f*Ench(actor,178/*0xb2*/)
    else if IsRace5_0x557e00(id): raceSlayerFactor += 0.30f*Ench(actor,179/*0xb3*/) + 0.15f*Ench(actor,180/*0xb4*/) + 0.60f*Ench(actor,206/*0xce*/)
    else if IsRace9_0x557ec0(id): raceSlayerFactor += 0.30f*Ench(actor,181/*0xb5*/) + 0.15f*Ench(actor,182/*0xb6*/) + 0.60f*Ench(actor,207/*0xcf*/)
    else if IsRace2_0x557d70(id): raceSlayerFactor += 0.30f*Ench(actor,183/*0xb7*/) + 0.15f*Ench(actor,184/*0xb8*/) + 0.60f*Ench(actor,208/*0xd0*/)
    else if IsRace0_0x557d40(id): raceSlayerFactor += 1.00f*Ench(actor,185/*0xb9*/) + 0.50f*Ench(actor,186/*0xba*/) // Fruit: +1.0 / +0.5
    // Sub-race additive tables (0x44c364..0x44c3b5); IDs 215..217 are in both tables and match Feline only:
    //   Feline 0x6d3820 (23): {210..212,215..217,220..222,250..253,290..292,805..807,810..812,1000}
    //   Sea    0x6d38b0 (25): {59..61,101..104,193..195,204..207,215..217,257,783..785,799,839,840,842}
    if      IsFeline_0x4f21c0(target.status2):      raceSlayerFactor += 1.0f * f32(u32(Ench(actor, 196 /* 0xc4 */)))
    else if IsSeaCreature_0x4f21f0(target.status2): raceSlayerFactor += 1.0f * f32(u32(Ench(actor, 209 /* 0xd1 */)))

// Elemental Both-Sides-UP Enchants (0x44c3b8..0x44c4ca; uncapped; priority Fire..Thunder):
//   Fire->251(0xfb), Water->252(0xfc), Wind->253(0xfd), Earth->254(0xfe), Thunder->255(0xff)
if matchedElemEnchId != NONE:
    elemBothUpFactor = (1.0f + 0.2f * f32(u32(Ench(target, eid)))) + 0.2f * f32(u32(Ench(actor, eid)))

// 4. Zone / Field Element Factor (CBattle::_CalcFieldElementRevision, 0x44fbb0..0x44fdd2)
// Zone multipliers on CBattle (init 1.0f at 0x448be6..0x448c18; floor load at 0x44993a..0x4499b2):
//   [+0x1e4] physUp (zone 3), [+0x1ec] physDown (zone 5), [+0x1e8] magUp (zone 4),
//   [+0x1f0] magDown (zone 6), [+0x1f4] elemMatch (zones 7..11).
// ABI: ecx=CBattle*, xmm1=inputVal, [ebp+8]=attacker, [ebp+0xc]=isPhysicalMode, ret 8 -> xmm0.
function CBattle_CalcFieldElementRevision(inputVal: f32, attacker: BattleUnit_s*, isPhysical: u8) -> f32:
    dng = dynamic_cast<CGameModeDungeon*>(this.gameApp->mode_0x08) // RTTI 0x708c78 -> 0x708c3c
    if dng == null || dng.mapData_0x08 == null: return 1.0f * inputVal
    map = dng.mapData_0x08
    ent = map.zoneArray_0x130 + map.currentZoneIdx_0x134 * 0x230
    s0: i32 = ent.slot0_0x08; s1: i32 = ent.slot1_0x0c
    fac: f32 = 1.0f
    if isPhysical != 0:                                    // mode 1 (Physical); Up & Down stack multiplicatively
        fac = (s0 == 3 || s1 == 3) ? this.zonePhysUp_0x1e4 : 1.0f
        if s0 == 5 || s1 == 5: fac *= this.zonePhysDown_0x1ec
    else:                                                  // mode 0 (Magical)
        fac = (s0 == 4 || s1 == 4) ? this.zoneMagUp_0x1e8 : 1.0f
        if s0 == 6 || s1 == 6: fac *= this.zoneMagDown_0x1f0
    sk = (CParameterSkill*)(attacker + 0x18)
    match: bool = false
    if      sk.IsFire():    match = (s0 == 7 || s1 == 7)
    else if sk.IsWater():   match = (s0 == 8 || s1 == 8)
    else if sk.IsWind():    match = (s0 == 9 || s1 == 9)
    else if sk.IsEarth():   match = HasZoneEffect10_0x4489f0(map, map.currentZoneIdx_0x134) // s0==10 || s1==10
    else if sk.IsThunder(): match = HasZoneEffect11_0x448a20(map, map.currentZoneIdx_0x134) // s0==11 || s1==11
    if match: fac *= this.zoneElemMatch_0x1f4
    return fac * inputVal
```
- **Program Evidence:**
```asm
0044f5e0  call     0x415f50
0044f5ec  push     9
0044f6f5  mulss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0044f6fe  movss    xmm0, dword ptr [0x6d9540]    ; float 100
0044f70a  mulss    xmm0, dword ptr [0x6d92d4]    ; float 0.01
0044bd05  mov      edx, 0x57
0044bd23  call     0x55d810
0044bec9  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0044befd  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
0044bf2f  call     0x557ef0
0044bf6e  mov      edx, 0x58
0044bfa4  call     0x557e90
0044bfe3  mulss    xmm0, dword ptr [0x6d9330]    ; float 0.3
0044c01d  mulss    xmm0, dword ptr [0x6d931c]    ; float 0.15
0044c04d  mulss    xmm0, dword ptr [0x6d934c]    ; float 0.6
0044c367  call     0x4f21c0
0044c37a  call     0x4f21f0
0044c485  mulss    xmm0, dword ptr [0x6d9324]    ; float 0.2
0044c5d0  mulss    xmm0, dword ptr [ebp - 0x14]
0044c5d5  mulss    xmm0, dword ptr [ebp - 0x10]
0044c5da  mulss    xmm0, dword ptr [ebp - 0x4c]
0044c5e4  mulss    xmm0, dword ptr [ebp - 0x18]
00557f14  cmp      dword ptr [eax + 0x28], 0
0044fc2e  cmp      edx, 3
0044fc41  movss    xmm1, dword ptr [esi + 0x1e4]
0044fc6c  mulss    xmm1, dword ptr [esi + 0x1ec]
0044fd61  call     0x4489f0
0044fd70  mulss    xmm1, dword ptr [esi + 0x1f4]
0044fd9c  call     0x448a20
```

---

### M02.04 Additive `other` Modifiers & Float-to-Integer Truncation

- **Binary VA(s):** `0x44c608..0x44cade` (`CBattle::CalcPhysicalAttack` `other` accumulator & `cvttss2si`), `0x4151e0..0x4151e2` (`CCommand::vtable+0x88` returning `1` for exact 22 statuses), `0x43aef0..0x43af09` & `0x43e6d0..0x43e7e4` (front-row alive party query), `0x4fab50..0x4fab7a` (`GetStatusVal`), `0x4faf90..0x4fb003` (`CGameStatusBase::GetAilments`, `vtable+0x80`), `0x4fbd90..0x4fbdb5` (`IsAliveAndNotPetrified`, `vtable+0xe8`), `0x495b20` (`GetLevel`, `vtable+0x10`), `0x48be10` (`GetHP`, `vtable+0x24`), `0x469ef0` (`GetMaxHP`, `vtable+0x28`)
- **Calls:** `0x47e340` (`FindCommand`), `0x47e400` (`GetCommandValOrZero`), `0x418be0`/`0x418bf0`, `0x43aef0`, `0x4f4f60` (`GetEquipmentID`), `0x559190` (`IsShield`), `0x4fab50`, `0x43ea50` (`IsActionType`)
- **CalledBy:** `CBattle::CalcPhysicalAttack` (`0x44c608..0x44cade`)
- **Typed Pseudocode:**
```text
// ctx = [ebp+0xc] (PhysicalHitContext*):
//   ctx.hitSeqIdx_0x00 : u32 = [actionPattern+0x88] (0-based consecutive hit index)
//   ctx.isCounter_0x04 : u8  = [actionPattern+0x11] (1 on counter/follow-up patterns, else 0)
other: f32 = 0.0f

// 1. Stat-Count Command 71 (0x47) — Exact 22 Target Statuses (0x44c608..0x44c677)
// Iterates targetCmds ([ebp-0x48]) and calls cmd->vtable+0x88().
// Binary factory (0x47b220, jump table 0x47de14) binds vtable+0x88 to 0x4151e0 (`mov al, 1; ret`)
// on EXACTLY 22 command IDs (all other commands bind 0x4151f0 `xor al, al; ret`):
//   { 41 (0x29),  42 (0x2a),  43 (0x2b),  44 (0x2c),  45 (0x2d),  46 (0x2e),
//    161 (0xa1), 162 (0xa2), 163 (0xa3), 164 (0xa4), 165 (0xa5), 166 (0xa6),
//    167 (0xa7), 168 (0xa8), 169 (0xa9), 172 (0xac), 173 (0xad), 174 (0xae),
//    184 (0xb8), 185 (0xb9), 186 (0xba), 189 (0xbd) }
if (cmd71 = FindCmd(actorCmds, 71 /* 0x47 */)) != null:
    perStatusBonus: f32 = cmd71->GetVal()
    for cmd in targetCmds:
        if cmd->vtable_88_IsCountedStatus():
            other += perStatusBonus

// 2. Consecutive Hit Bonus 136 (0x88) (0x44c678..0x44c6ba)
other += CmdVal(actorCmds, 136 /* 0x88 */) * f32(u32(ctx.hitSeqIdx_0x00))

// 3. Material Guard 179 (0xb3) on Target (0x44c6bb..0x44c722)
if (cmd179 = FindCmd(targetCmds, 179 /* 0xb3 */)) != null:
    casterId: i32 = cmd179->vtable_40_GetCasterId()
    apply179: bool = true
    if casterId != -1:
        caster = GameManager_0x71fc24->vtable_14c_GetPartyMemberById(casterId)
        if caster == null || !caster->vtable_e8_IsAliveAndNotPetrified():
            apply179 = false
        else:
            offhandId: i32 = GetEquipmentID(caster, 1)
            if offhandId == -1 || !IsShield_0x559190(offhandId):
                apply179 = false
    if apply179:
        other += cmd179->GetVal()                          // negative value reduces damage

// 4. Limit Field 190 (0xbe) on Target & Effect 191 (0xbf) on Actor (0x44c723..0x44c763)
other += CmdVal(targetCmds, 190 /* 0xbe */)
if ctx.isCounter_0x04 == 0:                                // 191 suppressed when actionPattern+0x11 != 0
    other += CmdVal(actorCmds, 191 /* 0xbf */)

// 5. Imperial Guard 308 (0x134) — Front-Row Shield Bearer Protecting Back-Row Ally (0x44c764..0x44c819)
if target.isPlayerSide_0x78 != 0 && target.isFrontRow_0x79 == 0:
    // 0x43aef0(out, sort=0, rowFilter=1 [front], aliveOnly=1) -> 0x43e6d0(out, 0, 1, isPlayer=1, aliveOnly=1)
    // Excludes Dolls/Summons (unitId >= 2000 / 0x7d0) and dead/petrified units.
    frontAllies = this->GetAliveFrontRowPartyUnits()
    bestGuard: f32 = 0.0f                                  // initialized to 0.0f; takes min (most negative)
    for ally in frontAllies:
        offhandId: i32 = GetEquipmentID(ally.status2_0x14, 1)
        if offhandId != -1 && IsShield_0x559190(offhandId):
            v308: f32 = GetStatusVal_0x4fab50(ally.status2_0x14, 308 /* 0x134 */)
            bestGuard = min(bestGuard, v308)               // does NOT stack across multiple shield bearers
    other += bestGuard

// 6. Dark Quest 263 (0x107) — Scales with Actor's Active Ailment Count (0x44c81a..0x44c89a)
// actor.status->vtable+0x80 (0x4faf90) collects statuses where cmd->vtable+0x68() == true:
// Exact 11 ailment command IDs: { 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 139 } (0x71..0x7a, 0x8b).
if (cmd263 = FindCmd(actorCmds, 263 /* 0x107 */)) != null:
    ailments = actor.status->GetAilments()
    other += f32(u32(ailments.size())) * cmd263->GetVal()

// 7. Joint-Attack Enchants 261 (0x105) & 290 (0x122) (0x44c89b..0x44c91d)
if IsActionType(actor, 0 /* CActionJoinAttack */):
    other += f32(u32(Ench(actor, 261 /* 0x105 */))) * 0.10f
    other += f32(u32(Ench(actor, 290 /* 0x122 */))) * 0.20f

// 8. Small-Party Enchant 267 (0x10b) (0x44c91e..0x44c994)
if actor.isPlayerSide_0x78 != 0:
    e267: f32 = f32(u32(Ench(actor, 267 /* 0x10b */)))
    partyCount: i32 = GameManager_0x71fc24->vtable_148_GetPartyCount()
    other += f32(u32(5 - partyCount)) * 0.10f * e267

// 9. Full-HP Enchant 271 (0x10f) (0x44c995..0x44c9e5)
if actor.status->GetHP() == actor.status->GetMaxHP():
    other += f32(u32(Ench(actor, 271 /* 0x10f */))) * 0.10f

// 10. Level-Difference Enchants 219 (0xdb) & 220 (0xdc) (0x44c9e6..0x44ca91)
// Unsigned 32-bit comparisons (`jbe` / `jae`) on CGameStatusBase::GetLevel() ([status+0x04]):
if u32(target.status->GetLevel()) > u32(actor.status->GetLevel()):
    other += f32(u32(Ench(actor, 219 /* 0xdb */))) * 0.10f
if u32(target.status->GetLevel()) < u32(actor.status->GetLevel()):
    other += f32(u32(Ench(actor, 220 /* 0xdc */))) * 0.10f

// 11. Apply `other` & Truncate to Signed 32-Bit Integer (0x44caba..0x44cade)
dmg: i32 = trunc0(baseDmgC * (1.0f + other))               // cvttss2si eax, xmm0 at 0x44cacc
```
- **Program Evidence:**
```asm
0044c60e  mov      edx, 0x47
0044c64d  mov      eax, dword ptr [eax + 0x88]
0044c678  mov      edx, 0x88
0044c68e  mov      edx, 0xb3
0044c70a  call     0x559190
0044c723  mov      edx, 0xbe
0044c738  cmp      byte ptr [eax + 4], 0
0044c748  mov      edx, 0xbf
0044c76e  cmp      byte ptr [edi + 0x79], 0
0044c790  call     0x43aef0
0044c7d7  push     0x134
0044c7de  call     0x4fab50
0044c7e3  minss    xmm0, dword ptr [ebp + 0xc]
0044c81a  mov      edx, 0x107
0044c842  call     dword ptr [edx + 0x80]
0044c8ad  push     0x105
0044c8bd  push     0x122
0044c927  push     0x10b
0044c95f  mov      ecx, 5
0044c964  sub      ecx, eax
0044c9af  push     0x10f
0044c9fd  cmp      esi, eax
0044ca04  push     0xdb
0044ca59  push     0xdc
0044cacc  cvttss2si eax, xmm0
```

---

### M02.05 Post-Truncation Modifiers, Demon Wall `356`, Positive Trance `440`, SpecialDamage & Cap `296`

- **Binary VA(s):** `0x44cae1..0x44cfac` (`CBattle::CalcPhysicalAttack` post-truncation pipeline), `0x436d80..0x4370b9` (Warning Shot passive `259` setting `[actor+0x105] = 1`), `0x43af10..0x43afb8` (same-row alive party status list), `0x4f5440..0x4f5451` & `0x4f69e0..0x4f6a89` (`GetMotivation` `[esi+0xd8]` clamped to `[70, 130]`), `0x4fb5a0..0x4fb5ae` (`IsAsleep`, `vtable+0xbc`), `0x4faf20..0x4faf88` (`HasAnyAilment`, `vtable+0x7c`), `0x44f720..0x44fb7a` (`CBattle::_CalcSpecialDamage`), `0x48c640..0x48c678` (Damage Cap `296` / `0x128`), `0x44fb80..0x44fba8` (post-calc enemy command `12` flag)
- **Calls:** `0x505ac0` (`Rand`), `0x4f2180`, `0x557e00`/`0x557e90`/`0x557e60`, `0x43af10`, `0x47e340`, `0x4f5440`, `0x47e290`, `0x44f720`, `0x48c640`, `0x48cbf0`, `0x44fb80`
- **CalledBy:** `CBattle::CalcPhysicalAttack` (`0x44cae1..0x44d345`); `CBattle::_CalcSpecialDamage` also called by `CBattle::CalcMagicalAttack` (`0x44f0a0`)
- **Typed Pseudocode:**
```text
// Exact sequential execution order after `dmg = trunc0(baseDmgC * (1.0f + other))` (0x44cacc):

// 1. Warning Shot Penalty (0x44cae1..0x44cb11)
// [actor+0x105] is cleared at turn start (0x436713) and set to 1 by Warning Shot passive 259 (0x103) at 0x4370b3.
if actor.warningShotFlag_0x105 != 0:
    dmg = (dmg * 3) / 10                                   // signed trunc0 via magic 0x66666667, sar edx, 2

// 2. Guaranteed Minimum Roll (0x44cb12..0x44cb5e) — see M02.02 for inverted vanilla isCrit parity quirk
if dmg <= 0:
    dmg = (f32(TaskResult[0].isCrit_0x31) == 1.0f) ? (Rand(2) + 1) : 3

// 3. Demon Wall 356 (0x164) — Same-Row Party Protection vs Enemy Races 5, 7, 8 (0x44cb5f..0x44ccb1)
// Races: 0x557e00 -> 5 (Undead), 0x557e90 -> 8 (Demon), 0x557e60 -> 7 (Apparition).
if target.isPlayerSide_0x78 != 0 && actor.isPlayerSide_0x78 == 0:
    enemyId: i32 = actor.status2_0x14->GetEnemyId()        // 0x4f2180 ([status2+0x9c])
    if IsRace5(enemyId) || IsRace8(enemyId) || IsRace7(enemyId):
        rowFilter: i32 = (target.isFrontRow_0x79 != 0) ? 1 : 2 // 1=front, 2=back
        // 0x43af10(out, sort=0, rowFilter, aliveOnly=1) -> alive party CGameStatus* in target's row (no Dolls/Summons)
        for allyStatus in this->GetAliveSameRowPartyStatuses(rowFilter):
            if (cmd356 = allyStatus->vtable_48_FindStatus(0, 356 /* 0x164 */)) != null:
                // Stops at FIRST ally carrying 356! Does NOT stack or take min across multiple allies.
                raw: i32 = trunc0(f32(dmg) + f32(dmg) * cmd356->GetVal())
                dmg = (raw < 0) ? 0 : raw                  // cmovs -> can reduce dmg to 0!
                TaskResult[0].RecordPassiveTrigger(target.status, cmd356->GetId())
                break

// 4. Positive Trance 440 (0x1b8) — Motivation Over Vanilla Threshold 100.0f (0x44ccb2..0x44cd29)
// actor.status2->GetMotivation() (0x4f5440 -> 0x4f69e0):
//   clamps [status2+0xd8] to [70.0f, 130.0f]; ench 201 -> 70.0f; ench 200 -> max(100.0f, m);
//   ench 195 -> 130.0f; status 81 (0x51) -> overwrites with cmd81.val.
// Vanilla X17 threshold pointer at VA 0x44ccd2 (operand of 0x44ccce `movss xmm1, dword ptr [0x6d9540]`) = 100.0f.
if (cmd440 = FindCmd(actorCmds, 440 /* 0x1b8 */)) != null:
    motivation: f32 = actor.status2_0x14->GetMotivation()  // 0x4f5440
    if motivation >= 100.0f:                               // 0x44ccd6 comiss; jb skip
        excess: f32 = motivation - 100.0f
        // x87: 0x44ccf8 fdivr [ebp+0x10] (D8 /7 = excess / cmd440.val); 0x44cd02 fdiv 100.0f
        dmg = dmg + trunc0(f32(dmg) * ((excess / cmd440->GetVal()) / 100.0f))

// 5. Sleeping Target 1.5x Bonus (0x44cd2a..0x44cd56)
// target.status->vtable+0xbc (0x4fb5a0) checks ONLY status 116 (0x74, Sleep).
if target.status->IsAsleep():
    dmg = (dmg * 3) / 2                                    // signed trunc0

// 6. Ailed-Target Enchant 280 (0x118) +15% Bonus (0x44cd57..0x44cda1)
if Ench(actor, 280 /* 0x118 */) != 0 && target.status->HasAnyAilment(): // non-stacking count check
    dmg = dmg + trunc0(f32(dmg) * 0.15f)                   // 0x6d931c

// 7. Magic-User Class 2x Bonus — Command 86 (0x56) (0x44cda2..0x44ce03)
if HasCommand(actorCmds, 86 /* 0x56 */) && target.isPlayerSide_0x78 != 0:
    if target.status2_0x14->vtable_13c_GetClassId(0) in { 12, 13, 14, 15, 16, 17, 18, 19 }: // 0x0c..0x13
        dmg = dmg * 2

// 8. CBattle::_CalcSpecialDamage (0x44f720..0x44fb7a, zero Rand() draws; called at 0x44ce15)
function CBattle_CalcSpecialDamage(pDmg: i32*, target, actor, targetCmds, actorCmds) -> bool:
    origDmg: i32 = *pDmg; out: i32
    // Strict 9-command priority cascade on actorCmds:
    if      (c = FindCmd(actorCmds, 8   /* 0x08 Fixed */))       != null: out = trunc0(c->GetVal())
    else if (c = FindCmd(actorCmds, 12  /* 0x0c SelfDestruct */))!= null: out = trunc0(f32(actor.status->GetHP()) * c->GetVal())
    else if (    FindCmd(actorCmds, 134 /* 0x86 Gold/20 */))     != null: out = GameManager_0x71fc24->GetGold() / 20 // trunc0 (sar edx, 3)
    else if (c = FindCmd(actorCmds, 138 /* 0x8a %MaxHP */))      != null:
        base: f32 = f32(target.status->GetMaxHP()) * c->GetVal()
        idx: i32 = MatchFirstAttrStatIdx(actor + 0x18)     // Fire(9)..Thunder(13), Cut(6)..Hit(8), else -1
        out = (idx >= 0) ? trunc0(((100.0f - f32(target.status->GetStat(idx)) * 0.5f) * 0.01f) * base) : trunc0(base)
    else if (    FindCmd(actorCmds, 140 /* 0x8c HalveHP */))     != null && (target.isPlayerSide_0x78 != 0 || target.status2_0x14.pctHpSusceptible_0xa5 != 0):
        out = target.status->GetHP() / 2
    else if (    FindCmd(actorCmds, 141 /* 0x8d 3/4 HP */))      != null && (target.isPlayerSide_0x78 != 0 || target.status2_0x14.pctHpSusceptible_0xa5 != 0):
        out = (target.status->GetHP() * 3) / 4
    else if (    FindCmd(actorCmds, 142 /* 0x8e To1HP */))       != null: out = target.status->GetHP() - 1 // NO +0xa5 gate
    else if (    FindCmd(actorCmds, 434 /* 0x1b2 UserHP-1 */))   != null: out = actor.status->GetHP() - 1
    else if (c = FindCmd(actorCmds, 435 /* 0x1b3 UserLv*v */))   != null: out = trunc0(f32(u32(actor.status->GetLevel())) * c->GetVal())
    else: *pDmg = origDmg; return false
    // Limit Field 190 (0xbe) on targetCmds applies to all special damage EXCEPT cmd 142 (0x44fb13..0x44fb5d):
    if (lim = FindCmd(targetCmds, 190 /* 0xbe */)) != null && FindCmd(actorCmds, 142 /* 0x8e */) == null:
        out += trunc0(f32(out) * lim->GetVal())
    *pDmg = out; return true

if this->_CalcSpecialDamage(&dmg, target, actor, targetCmds, actorCmds):
    TaskResult[0].isCrit_0x31 = 0u8                        // clears crit flag on special damage override
    TaskResult[0].isFixed_0x32 = 1u8

// 9. Living-Only Effect 87 (0x57) Zero Override & Damage Cap 296 (0x128) (0x44ce48..0x44cfac)
if nonLivingZero:
    dmg = 0; TaskResult[0].resultType_0x2c = 4             // Invalid / Voided
// 0x48c640(dmg, &actorCmds): if cmd 296 (0x128) present via 0x48cbf0, dmg = min(dmg, trunc0(cmd296->GetVal())).
dmg = ApplyDamageCap296_0x48c640(dmg, actorCmds)
if TaskResult[0].resultType_0x2c != 4:
    if HasCommand(actorCmds, 2 /* TP damage */): TaskResult[0].tpDmg_0x24 = TaskResult[0].tpDmgRaw_0x28 = dmg
    else:                                        TaskResult[0].hpDmg_0x1c = TaskResult[0].hpDmgRaw_0x20 = dmg
    if elbowGreaseTriggered != 0 && FindCmd(actorCmds, 443 /* 0x1bb */) != null:
        TaskResult[0].RecordPassiveTriggerAndBanner(actor.status, 443 /* 0x1bb */)

// 10. Exit Flag for Command 12 (0x0c) on Enemy Actor (0x44d339..0x44d345 -> 0x44fb80; runs on hit AND miss)
if FindCmd(actorCmds, 12 /* 0x0c */) != null && actor.isPlayerSide_0x78 == 0:
    actor.status2_0x14.flag_0x15d = 1u8
```
- **Program Evidence:**
```asm
0044cae1  cmp      byte ptr [ebx + 0x105], 0
0044caf0  mov      eax, 0x66666667
0044cb83  call     0x557e00
0044cb8f  call     0x557e90
0044cb9b  call     0x557e60
0044cbb9  cmp      byte ptr [edi + 0x79], al
0044cbf0  push     0x164
0044cc45  cmovs    eax, ecx
0044ccb2  mov      edx, 0x1b8
0044ccc9  call     0x4f5440
0044ccce  movss    xmm1, dword ptr [0x6d9540]    ; float 100
0044ccd6  comiss   xmm0, xmm1
0044ccf8  fdivr    dword ptr [ebp + 0x10]
0044cd02  fdiv     dword ptr [0x6d9540]    ; float 100
0044cd2f  mov      eax, dword ptr [eax + 0xbc]
0044cd5a  push     0x118
0044cda2  mov      edx, 0x56
0044ce15  call     0x44f720
0044ce48  cmp      byte ptr [ebp - 0x3c], 0
0044ce7b  call     0x48c640
0044f758  cmp      eax, 8
0044f7a8  cmp      eax, 0xc
0044f806  mov      edx, 0x86
0044f858  cmp      eax, 0x8a
0044f989  cmp      eax, 0x8c
0044f9c0  mov      al, byte ptr [eax + 0xa5]
0044f9ec  cmp      eax, 0x8d
0044fa43  mov      edx, 0x8e
0044fa63  mov      edx, 0x1b2
0044fa9f  cmp      eax, 0x1b3
0044fb17  mov      edx, 0xbe
0044fb27  mov      edx, 0x8e
0048c647  mov      edx, 0x128
0048c670  cmovg    esi, ecx
```

---

### M02.06 Physical Critical Rate & Multiplier, Crit Interrupt & Crit-Triggered Murder `258`

- **Binary VA(s):** `0x44f190..0x44f5c4` (`CBattle::_CalcCritical`, vtable `0x6c9b60` slot `+0x60` at `0x6c9bc0`), `0x44c4ca..0x44c5f5` (call site, `isCrit` flag, damage multiply in `CBattle::CalcPhysicalAttack`), `0x44cfad..0x44d265` (chant interrupt + independent 33% crit interrupt bit), `0x44d266..0x44d336` (crit-triggered Murder `258`/`0x102`), `0x482e40..0x48300b` (`CCommand_0119::apply`), `0x558060..0x558087` (enemy instant-death immunity bit 6)
- **Calls:** `0x47e340` (`FindCommand`), `0x490790` (`CRandom::Get`), `0x505ac0` (`Rand(n)`), `0x507310` (table lookup `[0x738a08]`/`[0x7389d8]`), `0x47b220` (`CCommand` factory `119`/`0x77`), `0x482e40` (`CCommand_0119::apply`), `0x428560`/`0x428570`, `vtable+0x10` (`Level`), `vtable+0x34` (stat `4`=DEX, `5`=AGI, `12`=instant-death resist), `vtable+0xf0` (enchant)
- **CalledBy:** `CBattle::CalcPhysicalAttack` (`0x44c4e0` via `vtable+0x60`; `CalcMagicalAttack` never calls `_CalcCritical`)
- **Typed Pseudocode:**
```text
// CBattle::_CalcCritical(this, defender, tgtCmds, attacker, actCmds, hitSeqIdx: u32) -> f32
// hitSeqIdx = [CActionPatternBase+0x88] (0-based hit counter incremented per hit).
function CBattle_CalcCritical(this, defender, tgtCmds, attacker, actCmds, hitSeqIdx: u32) -> f32:
    // 1. Base stat term (0x44f19f..0x44f215): stat 4=DEX, 5=AGI
    atkDex: i32 = attacker.status->GetStat(4)
    defAgi: i32 = defender.status->GetStat(5)
    baseStat: f32 = ((f32(atkDex) * 0.2f) / f32(atkDex + defAgi)) * 100.0f // 0x6d9324, 0x6d9540

    // 2. Level diff bonus (0x44f21b..0x44f25c):
    lvDiff: f32 = max(0.0f, f32(attacker.status->GetLevel() - defender.status->GetLevel()) * 0.5f)

    // 3. Additive command terms (0x44f242..0x44f32d; percentage-scale, NOT *100.0f):
    preRate: f32 = baseStat + lvDiff
                 + CmdVal(actCmds, 31  /* 0x1f Critical Rate */)
                 + CmdVal(tgtCmds, 32  /* 0x20 Critical Vulnerability */)
                 + CmdVal(actCmds, 174 /* 0xae Crit Rate */)
                 + CmdVal(actCmds, 211 /* 0xd3 Prelude */)

    // 4. Multiplicative enchants (0x44f325..0x44f471):
    //    atkMult in [1.0f, 2.0f]; defMult in [0.0f, 1.0f] (50 defPts zeroes rate before floor).
    atkPts: f32 = min(50.0f, 4.0f*f32(u32(Ench(attacker, 45/*0x2d*/))) + 2.0f*f32(u32(Ench(attacker, 46/*0x2e*/))))
    defPts: f32 = max(-50.0f, -(4.0f*f32(u32(Ench(defender, 47/*0x2f*/))) + 2.0f*f32(u32(Ench(defender, 48/*0x30*/)))))
    critRate: f32 = preRate * (atkPts * 0.02f + 1.0f) * (defPts * 0.02f + 1.0f) // 0x6d92e0, 0x6d938c

    // 5. Effect 125 (0x7d, More Crits Later) (0x44f477..0x44f4af): presence-only, +5.0f/hit before clamp.
    if FindCmd(actCmds, 125 /* 0x7d */) != null:
        critRate += f32(u32(hitSeqIdx)) * 5.0f             // 0x6d9434

    // 6. Clamp (0x44f4af..0x44f4f4): Enchant 268 (0x10c, non-stacking) raises floor 5.0f -> 20.0f; cap 50.0f.
    minCrit: f32 = (Ench(attacker, 268 /* 0x10c */) != 0) ? 20.0f : 5.0f // 0x6d948c / 0x6d9434
    critRate = min(50.0f, max(minCrit, critRate))          // 0x6d94e0

    // 7. Effect 70 (0x46, Crit Rate Fixed Modifier) override — bypasses [minCrit, 50.0f] (0x44f4e3..0x44f51c):
    if (cmd70 = FindCmd(actCmds, 70 /* 0x46 */)) != null:
        critRate = cmd70->GetVal() * 100.0f                // 0x6d9540

    // 8. Effect 110 (0x6e, Crits on Beasts) override — overrides even Effect 70 (0x44f51c..0x44f593):
    if FindCmd(actCmds, 110 /* 0x6e */) != null:
        isBeast: bool = (defender.isPlayerSide_0x78 != 0)
            ? (TableLookup([0x738a08], defender.status2_0x14->vtable_138()).race_0x44 == 2)
            : (TableLookup([0x7389d8], defender.status2_0x14.enemyId_0x9c).race_0x28 == 2)
        if isBeast: critRate = 100.0f

    // 9. RNG roll, trunc0, strict '<', immediate 1.25f / 1.0f return (0x44f593..0x44f5c4):
    return (GlobalRng_0x816ce8.Rand(100) < trunc0(critRate)) ? 1.25f : 1.0f // 0x3fa00000 vs 0x3f800000

// Consumption inside CBattle::CalcPhysicalAttack (0x44c4ca..0x44d336):
critMult: f32 = this->vtable_60_CalcCritical(target, &targetCmds, actor, &actorCmds, ctx.hitSeqIdx_0x00)
TaskResult[0].isCrit_0x31 = (critMult != 1.0f) ? 1u8 : 0u8 // ucomiss vs 1.0f at 0x44c4ea
// Multiplied into baseDmgC at 0x44c5e9; note inverted min-damage check at 0x44cb24..0x44cb49 (see M02.02).

// Chant Interrupt & Independent 33% Crit Interrupt (0x44cfad..0x44d265):
// Note: binary adds (1.0f + cmd264) to (MaxHP * 1.5f) instead of multiplying!
baseInt: f32 = clamp(f32(dmg) / (f32(target.status->GetMaxHP()) * 1.5f + (1.0f + CmdVal(targetCmds, 264 /* 0x108 */))), 0.0f, 0.95f)
intEnch: f32 = 0.10f*Ench(target,57) + 0.06f*Ench(target,58) + 0.03f*Ench(target,59) - 0.06f*Ench(target,60) + 0.20f*Ench(target,61)
intRate: f32 = clamp(baseInt - intEnch, 0.0f, 0.95f)
TaskResult[0].isInterrupted_0x33 = (Rand(100) < trunc0(intRate * 100.0f)) ? 1u8 : 0u8
if TaskResult[0].isCrit_0x31 != 0:                         // independent 33% roll drawn even if already interrupted
    if Rand(100) < 33:                                     // 0x505ac0(0x64) < 0x21 (strict '<')
        TaskResult[0].isInterrupted_0x33 |= 1u8            // 0x44d246

// Crit-Triggered Murder Passive 258 (0x102, Instakill) (0x44d266..0x44d336):
if TaskResult[0].isCrit_0x31 != 0 && (cmd258 = FindCmd(actorCmds, 258 /* 0x102 */)) != null:
    cmd119 = CCommandFactory_0x47b220(id=119 /* 0x77 */, srcType=0, val=cmd258->GetVal(), -1, -1, 0)
    cmd119->apply_0x482e40(resultVec, this.battleInfo, target.status, &targetCmds, actor.status)
    // CCommand_0119::apply (0x482e40..0x48300b) appends a new TaskResult:
    //   Immune (resultType=4, or 2 if dead/type==3) if target.IsDead(vt+0xc8), ench 134(0x86)!=0, ench 137(0x89)!=0,
    //   or enemy boss bit 6 ((enemyParam[+0x54] >> 6) & 1 via 0x558060).
    //   Else: basePct = cmd119.val * 100.0f; effPct = trunc0(basePct - (f32(target.GetStat(12) / 10) * basePct) / 10.0f);
    //   Rand(100) < effPct -> resultType=1, hpDmg=target.GetHP(); else (effPct <= 0) ? 4 : 3.
    newRes = resultVec[resultVec.size() - 1]
    if newRes.resultType_0x2c == 1:
        newRes.RecordPassiveTrigger(actor.status, cmd258->GetId())
```
- **Program Evidence:**
```asm
0044f1d8  mulss    xmm0, dword ptr [0x6d9324]    ; float 0.2
0044f209  divss    xmm1, xmm0
0044f20d  mulss    xmm1, dword ptr [0x6d9540]    ; float 100
0044f250  mulss    xmm0, dword ptr [0x6d9348]    ; float 0.5
0044f258  maxss    xmm1, xmm0
0044f41a  minss    xmm4, xmm1
0044f42b  mulss    xmm4, dword ptr [0x6d92e0]    ; float 0.02
0044f451  movss    xmm0, dword ptr [0x6d97d0]    ; float -50
0044f49b  mulss    xmm0, dword ptr [0x6d9434]    ; float 5
0044f4b2  push     0x10c
0044f4c3  movss    xmm1, dword ptr [0x6d948c]    ; float 20
0044f4db  movss    xmm0, dword ptr [0x6d94e0]    ; float 50
0044f599  push     0x64
0044f59b  call     0x490790
0044f5a0  cvttss2si ecx, dword ptr [esp + 0xc]
0044f5a6  mov      dword ptr [esp + 0xc], 0x3fa00000
0044f5ae  cmp      eax, ecx
0044f5b0  jl       0x44f5ba
0044f5b2  mov      dword ptr [esp + 0xc], 0x3f800000
0044c4e0  call     eax
0044c517  mov      byte ptr [eax + 0x31], cl
0044c5e9  mulss    xmm0, dword ptr [ebp - 0x34]
0044d238  cmp      eax, 0x21
0044d246  or       byte ptr [eax + 0x33], 1
0044d279  mov      edx, 0x102
0044d2a8  mov      edx, 0x77
0044d2af  call     0x47b220
```

---

### M02.07 Multi-Hit Count (`SetHitCount`, Weight Tables & Rondo Shift)

- **Binary VA(s):** `0x417cd0..0x418152` (`CActionBase::Action_s::SetHitCount`), `0x505ad0..0x505b75` (`PickWeightedIndex`), `0x6c94c0..0x6c9583` (`.rdata` weight tables at bases `0x6c94c0..0x6c9574`; `0x6c9508..0x6c9528` is a `CActionBase` vtable between tables), `0x48c350..0x48c5b0` (Double Attack passive trigger/cut-in helper)
- **Calls:** `0x418480` (collect action commands), `0x4192c0` (append actor status commands via `vtable+0x4c`), `0x507310` (lookup `[0x7389d4]`), `0x47e340` (`FindCommand`), `0x505ad0` (`PickWeightedIndex` -> `0x490790`), `0x61e650` (`round_f32_to_i32`), `0x490790` (`CRandom::Get`), `0x48c350`, `0x418c80`
- **CalledBy:** `0x42d3d1`, `0x42d9f2`, `0x42e196`, `0x4314b2`, `0x4389b9`, `0x438af8`, `0x43d502`, `0x43ec8a`, `0x451165`, `0x451c08`, `0x453b9d`, `0x457b00`
- **Typed Pseudocode:**
```text
// PickWeightedIndex (0x505ad0..0x505b75): prefix sums -> r = Rand(total) -> first i with r < prefix[i] (unsigned 'jb').
function PickWeightedIndex(weights: u32*, count: u32) -> u32:
    total: u32 = 0
    for i in 0 .. count - 1: total += weights[i]; prefix[i] = total
    r: u32 = GlobalRng_0x816ce8.Rand(total)                // 0x490790
    for i in 0 .. count - 1:
        if r < prefix[i]: return i                         // 0x505b43 jb
    return count

// .rdata weight tables (0x6c94c0..0x6c9583; every table sums to 100):
//   0x6c94c0 (4): [25, 25, 25, 25]      0x6c9564 (4): [15, 20, 35, 30]
//   0x6c94d0 (5): [0, 15, 30, 25, 30]   0x6c9574 (4): [0, 20, 30, 50]
//   0x6c94e4 (4): [20, 20, 30, 30]      0x6c952c (3): [0, 50, 50]
//   0x6c94f4 (5): [0, 15, 25, 30, 30]   0x6c9538 (3): [15, 50, 35]
//   0x6c9544 (3): [20, 50, 30]          0x6c9550 (5): [10, 15, 30, 25, 20]

// Action_s::SetHitCount (0x417cd0..0x418152):
//   [act+0x00]=actor, [act+0x04]=actionType, [act+0x10]=enemyAtkId, [act+0x40]=hitCount.
// All hit commands (89..100, 178) are evaluated INDEPENDENTLY and ADD to hitCount. Zero upper/lower caps.
function Action_s_SetHitCount(act: Action_s*, arg0: void*, battle: CBattle*):
    act.hitCount = 1
    cmds = CollectActionAndStatusCommands(act, battle)     // 0x418480 + 0x4192c0
    isBasic: bool = (act.actionType == 1 /* CActionAttack */)
                 || (act.actionType == 8 && (TableLookup([0x7389d4], act.enemyAtkId).flags_0x40 & 1) != 0)
    act.hitCount = 0
    hasExplicit: bool = false                              // [ebp+0x0f]
    // Rondo = cmd 210 (0xd2) checked per random-hit effect:
    if HasCmd(cmds, 89  /* 0x59 2~5 */): act.hitCount += PickWeightedIndex(HasCmd(cmds,210)?0x6c9564:0x6c94c0, 4)+2; hasExplicit=true // {2..5}: [25,25,25,25] -> Rondo [15,20,35,30]
    if HasCmd(cmds, 90  /* 0x5a 3   */): act.hitCount += 3; hasExplicit=true
    if HasCmd(cmds, 91  /* 0x5b 8   */): act.hitCount += 8; hasExplicit=true
    if HasCmd(cmds, 92  /* 0x5c 2~4 */): act.hitCount += PickWeightedIndex(HasCmd(cmds,210)?0x6c952c:0x6c9538, 3)+2; hasExplicit=true // {2..4}: [15,50,35] -> Rondo [0,50,50]
    if (c = FindCmd(cmds, 93 /* 0x5d */)): act.hitCount += round_f32_to_i32(c->GetVal()); hasExplicit=true
    if HasCmd(cmds, 94  /* 0x5e 0~4 */): act.hitCount += PickWeightedIndex(HasCmd(cmds,210)?0x6c94f4:0x6c9550, 5);   hasExplicit=true // {0..4}: [10,15,30,25,20] -> Rondo [0,15,25,30,30]; can yield 0!
    if HasCmd(cmds, 95  /* 0x5f 1~5 */): act.hitCount += PickWeightedIndex(HasCmd(cmds,210)?0x6c94d0:0x6c9550, 5)+1; hasExplicit=true // {1..5}: [10,15,30,25,20] -> Rondo [0,15,30,25,30]
    if HasCmd(cmds, 96  /* 0x60 3~5 */): act.hitCount += PickWeightedIndex(HasCmd(cmds,210)?0x6c952c:0x6c9544, 3)+3; hasExplicit=true // {3..5}: [20,50,30] -> Rondo [0,50,50]
    if HasCmd(cmds, 97  /* 0x61 2   */): act.hitCount += 2; hasExplicit=true
    if HasCmd(cmds, 98  /* 0x62 7   */): act.hitCount += 7; hasExplicit=true
    if HasCmd(cmds, 99  /* 0x63 1~3 */): act.hitCount += PickWeightedIndex(HasCmd(cmds,210)?0x6c952c:0x6c9544, 3)+1; hasExplicit=true // {1..3}: [20,50,30] -> Rondo [0,50,50]
    if HasCmd(cmds, 100 /* 0x64 4~7 */): act.hitCount += PickWeightedIndex(HasCmd(cmds,210)?0x6c9574:0x6c94e4, 4)+4; hasExplicit=true // {4..7}: [20,20,30,30] -> Rondo [0,20,30,50]
    if (c = FindCmd(cmds, 178 /* 0xb2 */)): act.hitCount += round_f32_to_i32(c->GetVal()) + 1; hasExplicit=true

    // Basic-attack passives (0x418033..0x4180e3): Triple Attack (252) FALLS THROUGH to Double Attack (251) -> stacks to 5 hits!
    if isBasic && !hasExplicit:
        if (c252 = FindCmd(cmds, 252 /* 0xfc Triple Attack */)) != null:
            if GlobalRng_0x816ce8.Rand(100) < trunc0(c252->GetVal() * 100.0f): // strict '<', cvttss2si
                act.hitCount += 3
                hasExplicit = true                         // falls through to 251!
        if (c251 = FindCmd(cmds, 251 /* 0xfb Double Attack */)) != null:
            thr251: i32 = trunc0(c251->GetVal() * 100.0f)
            if GlobalRng_0x816ce8.Rand(100) < thr251:      // strict '<'
                act.hitCount += 2                          // stacks with 252 -> 3 + 2 = 5 hits!
                NotifyPassive_0x48c350(c251, act.actor, thr251)
                return
    if !hasExplicit:
        act.hitCount = 1                                   // 0x4180e3
```
- **Program Evidence:**
```asm
00417d75  cmp      eax, 1
00417d7f  cmp      eax, 8
00417da9  mov      dword ptr [ebx + 0x40], 0
00417db0  mov      edx, 0x59
00417dc4  mov      edx, 0xd2
00417dd6  mov      ecx, 0x6c9564
00417ddf  mov      ecx, 0x6c94c0
00417de4  call     0x505ad0
00417de9  add      eax, 2
00417e87  call     0x61e650
00417fe1  mov      ecx, 0x6c9574
00417fea  mov      ecx, 0x6c94e4
00417ff4  add      eax, 4
00418020  call     0x61e650
00418025  inc      eax
00418045  mov      edx, 0xfc
0041807c  cvttss2si ecx, xmm0
00418084  add      dword ptr [ebx + 0x40], 3
0041808c  mov      edx, 0xfb
004180cd  add      dword ptr [ebx + 0x40], 2
004180e3  mov      dword ptr [ebx + 0x40], 1
00505b35  call     0x490790
00505b40  cmp      eax, dword ptr [ebx + esi*4]
00505b43  jb       0x505b4a
```

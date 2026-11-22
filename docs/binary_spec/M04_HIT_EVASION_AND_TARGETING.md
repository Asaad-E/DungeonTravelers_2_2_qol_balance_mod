# M04 — Hit / Evasion, Targeting Scopes, Formation & Binary Legality (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x413000..0x570000`)**
> Target binary: `backups/exe/DT22_en_unwrapped.vanilla.exe` (x86-32, image base `0x400000`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`).
> Specifies physical and magical hit/evasion formulas, auto-hit/auto-miss overrides, Parry and Counter-Evade hooks, attack range and row distance revision, targeting scopes (`0..18`), target resolution and mid-action retarget fallback, Cover (`171`), formation tables (`0x6517a0`), enemy front-row wipe shift, pierce adjacency (`[unit+0x64]`), aggro weighting (`0x44a630`, `0x505ad0`), and the complete binary action/skill/item legality gate (`CheckSkillCondition` `0x4f4910`, `0x455bc0`, `0x4fd250`, `0x515f7c`, `0x4208a0`).

---

## 1. Physical & Magical Hit / Evasion Formulas (`M04.01` – `M04.05`)

### M04.01 Physical Attack Hit Rate, Modifiers & Stab Evasion (`CBattle::CalcPhysicalAttack`)

- **Binary VA(s):** `0x44a9e6..0x44aef0` (`CBattle::CalcPhysicalAttack` hit-rate computation), `0x415710..0x4159ba` (`Action_s::IsAttributeStab`), `0x5576a0` (`GetEnemyAttackParam`)
- **Calls:** `CGameStatusBase::GetStat` (`vtable+0x34`), `CGameStatusBase::GetEnchantCount` (`vtable+0xf0`), `0x47e340` (`FindCommand`), `0x415710` (`Action_s::IsAttributeStab`), `0x5576a0` (`GetEnemyAttackParam`)
- **CalledBy:** `M00.06` (`CActionPatternBase::_Task` at `0x42172c` via `CBattle` `vtable+0x4c`)
- **Typed Pseudocode:**
```text
// RNG calls: 0 (roll occurs in M04.02).
// Stat IDs passed to status->vtable+0x34: 4 = DEX, 5 = AGI.
// Neither LUK nor unit level enters physical hit rate.
function CalcPhysicalHitRate(actor: BattleUnit_s*, target: BattleUnit_s*,
                             actCmds: Vec<CCommand*>*, tgtCmds: Vec<CCommand*>*) -> (f32, f32):
    // 1. Base accuracy modifier (0x44a9f3..0x44aa4e):
    //    Player non-summons (isPlayerSide != 0 && unitId not in 3000..3999 [0xbb8..0xf9f])
    //    read Cmd 29 (0x1d, Physical Accuracy); enemies & summons read EnemyAttackData[+0x38].
    baseMod: f32 = 0.0f
    if actor.isPlayerSide != 0u8 and not (actor.unitId >= 3000 and actor.unitId <= 3999):
        if c29 = FindCommand(actCmds, 29 /* 0x1d */): baseMod = c29.val
    else:
        baseMod = GetEnemyAttackParam(actor.actionEnemyAtkId).physHitMod // [param+0x38]

    // 2. BaseA (0x44aaa3..0x44aaf4):
    dex: i32 = actor.status.GetStat(4)              // vtable+0x34(4)
    agi: i32 = target.status.GetStat(5)             // vtable+0x34(5)
    baseA: f32 = (f32(dex + 100) * 0.885f) / f32(agi + 100) + baseMod

    // 3. Additive buff / dance / geas / stab-evasion terms (0x44ab0b..0x44ac8b):
    evaBuff: f32 = 0.0f
    if c164 = FindCommand(tgtCmds, 164 /* 0xa4 Physical Evasion */):  evaBuff += c164.val
    if c198 = FindCommand(tgtCmds, 198 /* 0xc6 Polka */):             evaBuff += c198.val
    if c338 = FindCommand(tgtCmds, 338 /* 0x152 Gravitating Geas */): evaBuff += c338.val

    hitBuff: f32 = 0.0f
    if c166 = FindCommand(actCmds, 166 /* 0xa6 Physical Accuracy */): hitBuff += c166.val
    if c197 = FindCommand(actCmds, 197 /* 0xc5 Tango */):             hitBuff += c197.val
    if c337 = FindCommand(actCmds, 337 /* 0x151 Gloomy Geas */):      hitBuff += c337.val

    // Physical Stab Evasion (Cmd 253 / 0xfd): active iff Action_s::IsAttributeStab() (0x415710)
    // checks skill/enemy-attack attribute == 2 (Stab), or player weapon [equip+0x6c] bit 7.
    stabEva: f32 = 0.0f
    if Action_s_IsAttributeStab(&actor.action):
        if c253 = FindCommand(tgtCmds, 253 /* 0xfd Physical Stab Evasion */):
            stabEva = c253.val

    // Dual-track percentage conversion (0x44acbb..0x44acf5):
    // Track A (hitRate_eff) includes stabEva; Track B (hitRate_noStab) omits stabEva for proc log.
    baseB_eff: f32    = (hitBuff - (evaBuff + stabEva) + baseA) * 100.0f
    baseB_noStab: f32 = (hitBuff - evaBuff + baseA) * 100.0f

    // 4. Equipment enchant contributions, each individually capped at 50.0f (0x44ad0e..0x44ae06):
    //    u32 counts converted via cvtdq2pd + unsigned bias -> cvtpd2ps.
    hitEnch: f32 = min(50.0f, 4.0f * f32(actor.status.GetEnchantCount(31 /* 0x1f */))
                            + 2.0f * f32(actor.status.GetEnchantCount(32 /* 0x20 */)))
    evaEnch: f32 = min(50.0f, 4.0f * f32(target.status.GetEnchantCount(35 /* 0x23 */))
                            + 2.0f * f32(target.status.GetEnchantCount(36 /* 0x24 */)))

    // 5. Barcarole divisor (Cmd 221 / 0xdd on target) & [5.0f, 100.0f] clamp (0x44adfd..0x44aed9):
    barcDiv: f32 = 1.0f
    if c221 = FindCommand(tgtCmds, 221 /* 0xdd Barcarole */):
        barcDiv = 1.0f + c221.val

    hitRate_eff: f32    = clamp((baseB_eff    + hitEnch - evaEnch) / barcDiv, 5.0f, 100.0f)
    hitRate_noStab: f32 = clamp((baseB_noStab + hitEnch - evaEnch) / barcDiv, 5.0f, 100.0f)
    return (hitRate_eff, hitRate_noStab)
```
- **Program Evidence:**
```asm
0044aab3  add      eax, 0x64
0044aabe  cvtdq2ps xmm2, xmm2
0044aac1  mulss    xmm2, dword ptr [0x6d9378]    ; float 0.885
0044aad6  add      eax, 0x64
0044aae3  divss    xmm1, xmm0
0044aae7  addss    xmm1, dword ptr [ebp + 0x14]
0044ab11  mov      edx, 0xa4
0044ab42  mov      edx, 0xa6
0044ab76  mov      edx, 0xc5
0044aba7  mov      edx, 0xc6
0044abe0  call     0x415710
0044abe9  mov      edx, 0xfd
0044ac1d  mov      edx, 0x151
0044ac49  mov      edx, 0x152
0044ad16  push     0x1f
0044ad21  push     0x20
0044ad3d  mulss    xmm0, dword ptr [0x6d9430]    ; float 4
0044ad5b  movss    xmm1, dword ptr [0x6d94e0]    ; float 50
0044ad88  minss    xmm1, xmm0
0044adfd  mov      edx, 0xdd
0044ae84  movss    xmm0, dword ptr [0x6d9434]    ; float 5
0044ae8c  movss    xmm2, dword ptr [0x6d9540]    ; float 100
0044ae99  divss    xmm1, dword ptr [ebp - 0x10]
0044ae9e  maxss    xmm0, xmm1
0044aeab  minss    xmm2, xmm0
```

---

### M04.02 Physical Hit Overrides, Age Flags, `trunc0_u32` Roll & `Furious Strike` (`348`)

- **Binary VA(s):** `0x44aef0..0x44b21c` (`CBattle::CalcPhysicalAttack` overrides and roll), `0x4fb5a0..0x4fb5ae` (`CGameStatusBase::IsSleep`), `0x41754d..0x4175cf` (`Furious Strike` `348` trigger), `0x42105b..0x4210b7` (synthetic `Cmd 69`/`72` injection), `0x61e650..0x61e7a0` (`__ftoui3` `trunc0_u32`)
- **Calls:** `0x47e340` (`FindCommand`), `CGameStatusBase::IsSleep` (`vtable+0xbc` = `0x4fb5a0`), `0x55d8a0` (`GetCharParam`), `0x5587c0` (`GetEnemyParam`), `0x490790` (`CRandom::Get`), `0x61e650` (`__ftoui3` = `trunc0_u32`), `0x47b220` (`CCommand` factory)
- **CalledBy:** `M04.01` (`CBattle::CalcPhysicalAttack`), `M00.06` (`CActionPatternBase::_Task`)
- **Typed Pseudocode:**
```text
// 1. Pre-action Furious Strike (348 / 0x15c) proc in CActionBase (0x41754d..0x4175cf):
//    RNG calls: 1 (if physical attack and actor has passive 348).
function CheckFuriousStrike(action: Action_s*, tgtCmds: Vec<CCommand*>*):
    if FindCommand(tgtCmds, 0 /* Physical Attack */) != null:
        if c348 = action.actor.GetCommand(0, 348 /* 0x15c Furious Strike */):
            if GlobalRng.Rand(100) < trunc0(c348.val * 100.0f): // cvttss2si, strict <
                action.flag48 = 1u8                              // [action+0x48] = 1
//    Inside CActionPatternBase::_Task (0x42105b..0x4210b7):
//    If action.flag48 != 0: synthesizes and appends to actCmds:
//      - Cmd 69 (0x45, Ignore Defense, val = 1.0f)
//      - Cmd 72 (0x48, Physical Accuracy Fixed Modifier, val = 1.0f -> 100.0f hit override)

// 2. Physical hit overrides & roll inside CalcPhysicalAttack (0x44aef0..0x44b21c):
//    RNG calls: exactly 1 (GlobalRng.Rand(100) at 0x44b0f3 -> [0..99]).
//    Note: NO Darkness/Blind ailment exists in DT22; ONLY Sleep (116 / 0x74) grants auto-hit.
//    Freeze (114), Paralysis (115), Stun (118), and Petrification (120) do NOT auto-hit.
function RollPhysicalHit(res: TaskResult*, target: BattleUnit_s*,
                         actCmds: Vec<CCommand*>*, tgtCmds: Vec<CCommand*>*,
                         hitRate_eff: f32, hitRate_noStab: f32) -> bool:
    // Override 1: Fixed Accuracy (55 / 0x37) takes priority over Physical Accuracy Fixed Modifier (72 / 0x48)
    if c55 = FindCommand(actCmds, 55 /* 0x37 */):
        hitRate_eff = hitRate_noStab = c55.val * 100.0f
    else if c72 = FindCommand(actCmds, 72 /* 0x48 */):
        hitRate_eff = hitRate_noStab = c72.val * 100.0f

    // Override 2: Sleep auto-hit (target->vtable+0xbc -> 0x4fb5a0 -> GetCommand(0, 0x74))
    if target.status.IsSleep():
        hitRate_eff = hitRate_noStab = 100.0f

    // Re-clamp [5.0f, 100.0f] AFTER Fixed/Sleep overrides, BEFORE age-gate checks (0x44afbe..0x44aff8):
    hitRate_eff    = clamp(hitRate_eff,    5.0f, 100.0f)
    hitRate_noStab = clamp(hitRate_noStab, 5.0f, 100.0f)

    // Override 3: Age-gate auto-miss (sets BOTH tracks to 0.0f, bypassing the 5.0f floor!)
    //   isAdult: player -> ([CharParam(memberId)+0x0c] & 1) != 0;
    //            enemy  -> (([EnemyParam(enemyId)+0x3c] >> 13) & 1) != 0.
    if FindCommand(tgtCmds, 149 /* 0x95 Nobody Over 20 */) != null:
        if IsTargetAdult(target):
            hitRate_eff = hitRate_noStab = 0.0f
    if FindCommand(tgtCmds, 150 /* 0x96 Nobody Under 20 */) != null:
        if not IsTargetAdult(target):
            hitRate_eff = hitRate_noStab = 0.0f

    // 3. Hit Roll (0x44b0eb..0x44b124):
    //    0x61e650 (__ftoui3) truncates f32 toward zero into u32 (mantissa shift, NO +0.5 rounding).
    roll: u32 = u32(GlobalRng.Rand(100))                  // 0..99
    if roll < trunc0_u32(hitRate_eff):                    // unsigned jb (strict <) at 0x44b108
        return true                                       // Hit -> proceed to damage calculation

    res.resultType = 3                                    // [res+0x2c] = 3 (Miss)
    if roll < trunc0_u32(hitRate_noStab):                 // unsigned jae skip at 0x44b124
        LogPassiveTrigger(target, 253 /* 0xfd Physical Stab Evasion */)
    return false                                          // Skips damage, crit, and interrupt
```
- **Program Evidence:**
```asm
0044aef3  mov      edx, 0x37
0044af0a  fmul     dword ptr [0x6d9540]    ; float 100
0044af34  mov      edx, 0x48
0044af83  mov      eax, dword ptr [eax + 0xbc]
0044af89  call     eax
0044afbe  movss    xmm2, dword ptr [0x6d9434]    ; float 5
0044afd4  maxss    xmm0, dword ptr [ebp + 0x14]
0044afde  mov      edx, 0x95
0044b047  shr      eax, 0xd
0044b070  mov      edx, 0x96
0044b0f1  push     0x64
0044b0f3  call     0x490790
0044b100  call     0x61e650
0044b105  cmp      dword ptr [ebp - 0x34], eax
0044b108  jb       0x44b221
0044b115  mov      dword ptr [ecx + 0x2c], 3
0044b121  cmp      dword ptr [ebp - 0x34], eax
0044b124  jae      0x44b20f
004fb5a2  push     0x74
004fb5a6  call     dword ptr [eax + 0x48]
00417567  push     0x15c
004175b1  mov      byte ptr [eax + 0x48], 1
0042106c  mov      edx, 0x45
00421098  mov      edx, 0x48
```

---

### M04.03 Magical Attack Hit Rate, Modifiers, Overrides, Graze & `Cmd 25` (`Magic Hit Determination`)

- **Binary VA(s):** `0x44d56d..0x44db97` (`CBattle::CalcMagicalAttack` hit rate & overrides), `0x44ed7f..0x44ee87` (magic hit roll, crit `301`, missed-spell graze), `0x42173e..0x421763`, `0x42196e..0x421ad2`, `0x422d3b..0x422d94` (`Cmd 25` non-damaging magic hit gate)
- **Calls:** `0x507310` (table lookup), `0x47e340` (`FindCommand`), `CGameStatusBase::GetStat` (`vtable+0x34`), `CGameStatusBase::GetEnchantCount` (`vtable+0xf0`), `CGameStatusBase::IsSleep` (`vtable+0xbc`), `0x490790` (`CRandom::Get`), `0x47e290` (`HasCommand`)
- **CalledBy:** `M00.06` (`CActionPatternBase::_Task` at `0x42195c` via `CBattle` `vtable+0x50`)
- **Typed Pseudocode:**
```text
// RNG calls for hit: 1 (GlobalRng.Rand(100) at 0x44ed8c, executed AFTER raw damage variance roll).
// Additional RNG calls in this block:
//   - If !isMiss and actor has passive 301 (0x12d): +1 RNG call Rand(100) < 20 (Magic Crit 1.25x).
//   - If final dmg <= 0: +1 RNG call Rand(5) + 1 (min magic damage 1..5).
// Stat IDs: 2 = INT, 3 = RES.
function CalcMagicalHitAndGraze(res: TaskResult*, target: BattleUnit_s*, actor: BattleUnit_s*,
                                skillId: i32, skillLv: i32, enemyAtkId: i32,
                                actCmds: Vec<CCommand*>*, tgtCmds: Vec<CCommand*>*,
                                rawMagicDmg: f32, condDmgBonus: f32):
    // 1. Base magic accuracy (0x44d56d..0x44d600):
    baseHit: f32 = 1.0f
    if skillId != -1:
        baseHit = MagicParam[skillId].hitByLv[skillLv]    // [0x738a58] + skillLv*4 + 0x110
    else if enemyAtkId != -1:
        baseHit = EnemyAttackParam[enemyAtkId].magHitMod  // [0x7389d4] + 0x50
    cmd30Val: f32 = (c30 = FindCommand(actCmds, 30 /* 0x1e Magic Accuracy */)) ? c30.val : 0.0f

    // 2. INT - RES term & equipment enchants (0x44d600..0x44d758):
    //    Note: Magic MiniUP enchants (40, 44) add +1.0 per stack (NOT +2.0 like physical 32, 36).
    intStat: i32 = actor.status.GetStat(2)
    resStat: i32 = target.status.GetStat(3)
    statTerm: f32 = baseHit + cmd30Val + f32(intStat - resStat) * 0.002f
    magHitEnch: f32 = min(50.0f, 3.0f * f32(actor.status.GetEnchantCount(39 /* 0x27 */))
                               + 1.0f * f32(actor.status.GetEnchantCount(40 /* 0x28 */)))
    magEvaEnch: f32 = min(50.0f, 3.0f * f32(target.status.GetEnchantCount(43 /* 0x2b */))
                               + 1.0f * f32(target.status.GetEnchantCount(44 /* 0x2c */)))
    midHit: f32 = statTerm * 100.0f + magHitEnch - magEvaEnch

    // 3. Multiplicative buff / song / geas modifiers (0x44d759..0x44da43):
    hitMultSum: f32 = 0.0f
    if c167 = FindCommand(actCmds, 167 /* 0xa7 Magic Accuracy */):   hitMultSum += c167.val
    if c309 = FindCommand(actCmds, 309 /* 0x135 Nirvana */):         hitMultSum += c309.val
    if c197 = FindCommand(actCmds, 197 /* 0xc5 Tango */):            hitMultSum += c197.val
    if c222 = FindCommand(actCmds, 222 /* 0xde Ballad */):           hitMultSum += c222.val
    if c337 = FindCommand(actCmds, 337 /* 0x151 Gloomy Geas */):     hitMultSum += c337.val
    if skillId == 205 /* 0xcd */:                                    // 0x44d8ea..0x44d95f
        if c278 = FindCommand(actCmds, 278 /* 0x116 Maid Bonus */):    hitMultSum += c278.val
        if c353 = FindCommand(actCmds, 353 /* 0x161 Maximum Maid */):  hitMultSum += c353.val

    evaMultSum: f32 = 0.0f
    if c165 = FindCommand(tgtCmds, 165 /* 0xa5 Magic Evasion */):    evaMultSum += c165.val
    if c198 = FindCommand(tgtCmds, 198 /* 0xc6 Polka */):            evaMultSum += c198.val
    if c338 = FindCommand(tgtCmds, 338 /* 0x152 Gravitating Geas */): evaMultSum += c338.val

    // Target song divisor: Nocturne (220 / 0xdc) takes priority over Kotodama Blessing (223 / 0xdf);
    // uses cmd.val directly as divisor (NOT 1.0 + val) and does NOT stack both.
    songDiv: f32 = 1.0f
    if c220 = FindCommand(tgtCmds, 220 /* 0xdc Nocturne */):
        songDiv = c220.val
    else if c223 = FindCommand(tgtCmds, 223 /* 0xdf Kotodama Blessing */):
        songDiv = c223.val

    // Clamp to [25.0f, 95.0f] BEFORE overrides (0x44d9f7..0x44da43):
    hitRate: f32 = clamp((midHit * (1.0f + hitMultSum) / songDiv) * (1.0f - evaMultSum), 25.0f, 95.0f)

    // 4. Overrides (NOT re-clamped to [25, 95], so Fixed Accuracy can exceed 95 or go below 25;
    //    Cmd 72 is NOT checked in CalcMagicalAttack):
    if c55 = FindCommand(actCmds, 55 /* 0x37 Fixed Accuracy */):
        hitRate = c55.val * 100.0f
    if target.status.IsSleep():                           // vtable+0xbc (Sleep 116 ONLY)
        hitRate = 100.0f
    if FindCommand(tgtCmds, 149 /* 0x95 Nobody Over 20 */) != null and IsTargetAdult(target):
        hitRate = 0.0f
    if FindCommand(tgtCmds, 150 /* 0x96 Nobody Under 20 */) != null and not IsTargetAdult(target):
        hitRate = 0.0f

    // 5. Roll (signed cvttss2si = trunc0, >= is miss) & Graze (0x44ed7f..0x44ee87):
    isMiss: bool = (GlobalRng.Rand(100) >= trunc0(hitRate)) // cmp eax, ecx; setge
    critMult: f32 = 1.0f
    res.isCrit = 0u8
    if not isMiss and FindCommand(actCmds, 301 /* 0x12d Critical Magic */) != null:
        if GlobalRng.Rand(100) < 20 /* 0x14 */:
            critMult = 1.25f
            res.isCrit = 1u8
    dmg: i32 = trunc0(rawMagicDmg * (1.0f + condDmgBonus) * critMult)
    if isMiss:
        if actor.status.GetEnchantCount(272 /* 0x110 */) > 0:
            dmg = (dmg * 3) / 4                           // signed sar 2 with round-toward-zero bias
        else:
            dmg = dmg / 2                                 // signed sar 1 with round-toward-zero bias
        res.resultType = 3                                // Graze / Miss
    if dmg <= 0:
        dmg = GlobalRng.Rand(5) + 1                       // 1..5

// 6. Non-damaging Magic Hit Determination (Cmd 25 / 0x19) in CActionPatternBase::_Task:
//    - At 0x421750: skills lacking Cmd 0 and Cmd 1 still enter CalcMagicalAttack if Cmd 25 is present.
//    - At 0x421a83..0x421ab7: if Cmd 25 is present, sets res HP/TP damage to 0x7fffffff and sets
//      skipPostEffects = (res.resultType != 2); on miss (resultType == 3), secondary commands are skipped.
//    - At 0x422d3b..0x422d94: clears all res damage/heal fields (+0x0c..+0x28) to 0x7fffffff.
```
- **Program Evidence:**
```asm
0044d63f  mulss    xmm0, dword ptr [0x6d92cc]    ; float 0.002
0044d67b  mulss    xmm0, dword ptr [0x6d9408]    ; float 3
0044d6c2  minss    xmm1, xmm0
0044d764  mov      edx, 0xa7
0044d795  mov      edx, 0xa5
0044d7c9  mov      edx, 0x135
0044d85c  mov      edx, 0xde
0044d8ea  cmp      dword ptr [ebp + 0x44], 0xcd
0044d8fd  mov      edx, 0x116
0044d929  mov      edx, 0x161
0044d980  cmp      eax, 0xdc
0044d9be  cmp      eax, 0xdf
0044da22  divss    xmm1, dword ptr [ebp + 0x48]
0044da2b  movss    xmm0, dword ptr [0x6d9498]    ; float 25
0044da33  maxss    xmm0, xmm1
0044da37  movss    xmm1, dword ptr [0x6d9534]    ; float 95
0044da3f  minss    xmm1, xmm0
0044da58  cmp      eax, 0x37
0044da98  mov      eax, dword ptr [eax + 0xbc]
0044dab1  mov      edx, 0x95
0044db24  mov      edx, 0x96
0044ed8c  call     0x490790
0044ed91  cvttss2si ecx, dword ptr [ebp + 0x54]
0044ed96  cmp      eax, ecx
0044ed98  setge    byte ptr [ebp + 0x47]
0044ee36  push     0x110
00421a83  mov      edx, 0x19
00422d3b  mov      edx, 0x19
```

---

### M04.04 Post-Hit Physical Evasion & Negation Hooks: Parry (`180`) & Counter-Evade (`250`)

- **Binary VA(s):** `0x4223b2..0x42265f` (Parry `180` and Counter-Evade `250` inside `CActionPatternBase::_Task`), `0x416ea0..0x417042` (`Action_s::IsAttribute9`), `0x56c460..0x56c4f6` (`CParameterSkill::IsAttribute9`)
- **Calls:** `0x416ea0` (`Action_s::IsAttribute9`), `CGameStatusBase::GetCommand` (`vtable+0x48`), `CGameStatusBase::HasCommand` (`vtable+0x50`), `0x505ac0` (`Rand(100)`), `0x43b5f0` (`IsDoll`), `0x43b610` (`IsSummon`)
- **CalledBy:** `M00.06` (`CActionPatternBase::_Task` post-hit physical branch)
- **Typed Pseudocode:**
```text
// Evaluated inside CActionPatternBase::_Task ONLY after CalcPhysicalAttack landed (not missed).
// Both hooks precede TakeDamage and can completely negate a physical hit.
function CheckParryAndCounterEvade(this: CActionPatternBase*, res: TaskResult*, target: CGameStatusBase*):
    // 1. Parry (Cmd 180 / 0xb4) — 0x4223b2..0x42254e:
    //    Requires physical hit (this.isPhysical != 0) and !Action_s::IsAttribute9() (0x416ea0:
    //    returns true when skill/enemy-attack attribute == 9 [Breath / Non-Parryable]).
    if this.isPhysical != 0u8 and not Action_s_IsAttribute9(this.action):
        if cmd180 = target.GetCommand(0, 180 /* 0xb4 Parry */):
            // 100% damage negation (leaves sentinel 0x7fffffff untouched):
            if res.hpDmg != 0x7fffffff: res.hpDmg = 0; res.hpDmgDisp = 0
            if res.tpDmg != 0x7fffffff: res.tpDmg = 0; res.tpDmgDisp = 0
            res.flags36 = 0u16
            res.blockedFlag38 = 1u8
            skipPostEffects = true
            // Wear-off roll (1 RNG call): Rand(100) < trunc0(cmd180.val * 100.0f) removes Parry!
            if Rand100() < trunc0(cmd180.val * 100.0f):   // 0x505ac0(0x64), cvttss2si, strict <
                QueueRemoveStatus(target, 180 /* 0xb4 */)
            return                                        // Bypasses Counter-Evade 250

    // 2. Counter-Evade (Cmd 250 / 0xfa) — 0x422553..0x42265f:
    //    Requires: !inCounter ([this+0x11]==0), attackRange in {0 (Near), 1 (Mid)},
    //              actor != target, !actor.HasCommand(307 / 0x133 Counter Immunity),
    //              and target has active passive 250 (0xfa Counter).
    if this.inCounter == 0u8 and (this.action.attackRange == 0 or this.action.attackRange == 1):
        actor = this.action.actor
        if actor != target and not actor.HasCommand(307 /* 0x133 */):
            if cmd250 = target.GetCommand(0, 250 /* 0xfa Counter */):
                // 1 RNG call: Rand(100) < trunc0(cmd250.val * 100.0f)
                if Rand100() < trunc0(cmd250.val * 100.0f): // 0x505ac0(0x64), cvttss2si, strict <
                    res.hpDmg = res.hpDmgDisp = 0x7fffffff
                    res.tpDmg = res.tpDmgDisp = 0x7fffffff
                    res.resultType = 3                    // Converted to Miss / Evaded!
                    skipPostEffects = true
                    // Counter follow-up is suppressed if actor is Doll (0x43b5f0) or Summon (0x43b610)
                    if not this.battle.IsDoll(actor) and not this.battle.IsSummon(actor):
                        QueueCounterPending(target, cmd250)
```
- **Program Evidence:**
```asm
004223b5  cmp      byte ptr [esi + 0x79], 0
004223c2  call     0x416ea0
004223d4  push     0xb4
004223f6  mov      dword ptr [ebx + 0x1c], 0
004224b3  call     0x505ac0
004224bf  mulss    xmm0, dword ptr [0x6d9540]    ; float 100
004224c7  cvttss2si esi, xmm0
004224da  cmp      edi, esi
004224dc  jge      0x42253a
00422559  cmp      byte ptr [eax + 0x11], 0
00422566  mov      eax, dword ptr [ecx + 0x34]
0042256d  cmp      eax, 1
00422582  push     0x133
00422596  push     0xfa
004225be  call     0x505ac0
004225d2  cvttss2si esi, xmm0
004225e5  cmp      edi, esi
004225e7  jge      0x42265f
00422608  mov      dword ptr [ebx + 0x2c], 3
0042261b  call     0x43b5f0
00422630  call     0x43b610
```

---

### M04.05 Attack Range Determination & Row Distance Revision (`SetAttackRange`, `_GetAttackRangeRevision`)

- **Binary VA(s):** `0x418160..0x4181d2` (`Action_s::SetAttackRange(CGamePlayerStatusBase*)`), `0x4181e0..0x4183c8` (`Action_s::SetAttackRange(skillId)`, jump tables `0x418388`, `0x4183a0`, `0x4183b8`), `0x4183d0..0x418475` (`Action_s::SetAttackRange(enemyAtkId)`), `0x559290..0x5593ab` (`IsRangeNear/Mid/Far`), `0x44a7a0..0x44a842` (`_GetAttackDistance` & `_GetAttackRangeRevision`)
- **Calls:** `0x4f4f60` (`GetEquipmentID`), `0x559290` (`IsWeaponNear`), `0x5592f0` (`IsWeaponMid`), `0x559350` (`IsWeaponFar`), `0x56ba30` (`GetSkillType`), `0x507310` (table lookup)
- **CalledBy:** `M00.04` (`CBattleMenuAttack` `0x450f69`, `CBattleMenuSkill` `0x4579da`/`0x457c1e`, `CActionPattern*` / turn-start auto-attacks), `M00.06` (`CBattle::CalcPhysicalAttack`)
- **Typed Pseudocode:**
```text
// AttackRange enum stored at [Action_s + 0x34]: 0 = Near (S), 1 = Mid (M), 2 = Far (L), 3 = Ignore.
// RNG calls: 0.

// 1. Player basic attack weapon range (0x418160..0x4181d2):
function Action_s_SetAttackRange_Weapon(act: Action_s*, player: CGamePlayerStatusBase*):
    equipId: i32 = player.GetEquipmentID(0)          // slot 0 = main weapon
    if equipId == -1 or IsWeaponNear(equipId):       // 0x559290: [equip+0x38]==0 && ([equip+0x6c]>>1)&1
        act.attackRange = 0                          // Near (unarmed defaults to Near)
    else if IsWeaponMid(equipId):                    // 0x5592f0: [equip+0x38]==0 && ([equip+0x6c]>>2)&1
        act.attackRange = 1                          // Mid
    else if IsWeaponFar(equipId):                    // 0x559350: [equip+0x38]==0 && ([equip+0x6c]>>3)&1
        act.attackRange = 2                          // Far

// 2. Skill range (0x4181e0..0x4183c8):
//    SkillType 0 (Technique, [0x738a64]) reads flags at [+0x48];
//    SkillType 3 (Joint,     [0x738a54]) reads flags at [+0x50];
//    SkillType 1,2,4,5 (Magic/Passive/etc.) fall through to 3 (Ignore Range).
function Action_s_SetAttackRange_Skill(act: Action_s*, skillId: i32):
    st: i32 = GetSkillType(skillId)                  // 0x56ba30
    flags: u32 = (st == 0) ? TechParam[skillId].flags48
               : (st == 3) ? JoinParam[skillId].flags50 : 0u
    if (flags & 1u) != 0u:       act.attackRange = 0 // Near
    else if (flags & 2u) != 0u:  act.attackRange = 1 // Mid
    else if (flags & 4u) != 0u:  act.attackRange = 2 // Far
    else:                        act.attackRange = 3 // Ignore Range

// 3. Enemy attack range (0x4183d0..0x418475):
function Action_s_SetAttackRange_Enemy(act: Action_s*, enemyAtkId: i32):
    flags: u32 = EnemyAttackParam[enemyAtkId].flags40 // [0x7389d4] + 0x40
    if ((flags >> 7) & 1u) != 0u:      act.attackRange = 0 // Near
    else if ((flags >> 8) & 1u) != 0u: act.attackRange = 1 // Mid
    else if ((flags >> 9) & 1u) != 0u: act.attackRange = 2 // Far
    else:                              act.attackRange = 3 // Ignore Range

// 4. Row distance (CBattle vtable+0x3c = 0x44a7a0) & multiplier (vtable+0x40 = 0x44a7d0):
function CBattle_GetAttackDistance(actor: BattleUnit_s*, target: BattleUnit_s*) -> i32:
    // Front=1, Back=0 at [unit+0x79]: F->F=0, F->B=1, B->F=1, B->B=2
    return (actor.isFrontRow != 0u8 ? 0 : 1) + (target.isFrontRow != 0u8 ? 0 : 1)

function CBattle_GetAttackRangeRevision(dist: i32, attackRange: i32) -> f32:
    if attackRange == 0:                             // Near (S)
        return (dist == 0) ? 1.0f : (dist == 1) ? 0.75f : (dist == 2) ? 0.5f : 1.0f
    if attackRange == 1:                             // Mid (M)
        return (dist == 2) ? 0.75f : 1.0f
    if attackRange == 2 or attackRange == 3:         // Far (L) or Ignore
        return 1.0f
```
- **Program Evidence:**
```asm
0041816c  call     0x4f4f60
00418173  cmp      edi, -1
0041817a  call     0x559290
0041818e  call     0x5592f0
004181a7  call     0x559350
00418246  test     al, 1
004182a6  shr      eax, 1
00418307  shr      eax, 2
004183fc  shr      eax, 7
0041842d  shr      eax, 8
0041845f  shr      eax, 9
0044a7a4  mov      cl, byte ptr [eax + 0x79]
0044a7ab  cmp      byte ptr [eax + 0x79], 0
0044a7ee  mov      dword ptr [esp], 0x3f000000
0044a808  mov      dword ptr [esp], 0x3f400000
0044a820  mov      dword ptr [esp], 0x3f800000
```

---

## 2. Targeting Scopes, Target Resolution & Fallback (`M04.06` – `M04.10`)

### M04.06 Master Target Pool Collector, Liveness Predicate & Unit-Type Filtering (`0x43e6d0`, `0x43b580`)

- **Binary VA(s):** `0x43e6d0..0x43e7e5` (`CBattleBase::_CollectUnits`), `0x43b580..0x43b5e9` (`CBattleBase::_IsTargetValid`), `0x4fb570..0x4fb65e` (`CGameStatusBase` ailment predicates), `0x4fbd90..0x4fbdb5` (`CGameStatusBase::IsAliveAndNotPetrified`, `vtable+0xe8`), `0x43af10..0x43b067` (`GetPlayerUnits`), `0x43b1d0..0x43b325` (`GetEnemyUnits`), `0x43acc0..0x43ad49` (`GetAllCombatants`), `0x440d10..0x440f00` (`SortUnitsByTiebreak`)
- **Calls:** `CGameStatusBase::IsDead` (`vtable+0x38`), `CGameStatusBase::IsPetrified` (`vtable+0xc8` = `0x4fb600`), `CGameStatusBase::IsAliveAndNotPetrified` (`vtable+0xe8` = `0x4fbd90`), `0x440d10` (`SortUnitsByTiebreak`)
- **CalledBy:** `M04.07` (`0x43f450`), `M04.08` (`0x456ff0`), `M04.09` (`0x41a850`, `0x420500`, `0x420560`), `M04.10` (`0x420b40`), `M04.11` (`0x43b7a8`), `M04.13` (`0x44a630`)
- **Typed Pseudocode:**
```text
// Unit ID bands stored at [BattleUnit_s + 0x04]:
//   0..999       : Player party members (isPlayerSide = 1)
//   1000..1999   : Enemies (front = 0x3e8+slot, back = 0x400+slot; isPlayerSide = 0)
//   2000..2999   : Dolls (0x7d0..0xbb7) — EXCLUDED from targeting!
//   3000..3999   : Summons / Guests (0xbb8..0xf9f) — EXCLUDED from targeting!
//   >= 4000      : Sentinel / inactive (0xfa0+) — EXCLUDED from targeting!
// RNG calls: 0.

// 1. Liveness predicate CGameStatusBase::IsAliveAndNotPetrified (vtable+0xe8 = 0x4fbd90):
function IsAliveAndNotPetrified(s: CGameStatusBase*) -> bool:
    // Dead (HP == 0, vtable+0x38) OR Fully Petrified (Cmd 120 / 0x78 with stage >= 3, 0x4fb600) -> false
    return (not s.IsDead()) and (not s.IsPetrified())

// 2. CBattleBase::_CollectUnits (0x43e6d0..0x43e7e5):
//    rowFilter: 0 = any row, 1 = front only (isFrontRow != 0), 2 = back only (isFrontRow == 0).
function CBattleBase_CollectUnits(this: CBattleBase*, out: Vec<BattleUnit_s*>*,
                                  sortFlag: bool, rowFilter: i32, isPlayer: bool, aliveOnly: bool):
    out.clear()
    for u in this.units:
        if u.unitId >= 2000: continue                     // skips Dolls, Summons, Sentinels
        if (u.isPlayerSide != 0u8) != isPlayer: continue
        if rowFilter == 1 and u.isFrontRow == 0u8: continue
        if rowFilter == 2 and u.isFrontRow != 0u8: continue
        if aliveOnly and not u.status.IsAliveAndNotPetrified(): continue
        out.push_back(u)
    if sortFlag:
        // 0x440d10: introsort descending by [unit + 0x0c] (sortTiebreak = 999-slot for players, 994-idx for enemies)
        SortDescendingBySortTiebreak(out)

// 3. CBattleBase::_IsTargetValid (0x43b580..0x43b5e9):
//    Note: Dead enemies are removed from this.units by _RemoveUnit (0x43b6a0), so any enemy found
//    in this.units is automatically valid. Dead/petrified players remain in this.units, so
//    aliveOnly=true rejects dead/petrified players while aliveOnly=false (Revive) accepts them.
function CBattleBase_IsTargetValid(this: CBattleBase*, status: CGameStatusBase*, aliveOnly: bool) -> bool:
    for u in this.units:
        if u.status == status:
            if aliveOnly and u.isPlayerSide != 0u8:
                return status.IsAliveAndNotPetrified()    // vtable+0xe8
            return true
    return false
```
- **Program Evidence:**
```asm
0043e72a  mov      eax, dword ptr [esi + 4]
0043e72d  cmp      eax, 0x7d0
0043e73b  cmp      eax, 0xbb8
0043e749  cmp      eax, 0xfa0
0043e754  cmp      byte ptr [esi + 0x78], al
0043e759  cmp      edx, 1
0043e75e  cmp      byte ptr [esi + 0x79], 0
0043e766  cmp      edx, 2
0043e77d  mov      eax, dword ptr [eax + 0xe8]
0043e7d8  call     0x440d10
0043b5a5  cmp      ebp, ecx
0043b5ba  cmp      byte ptr [edx + 0x78], 0
0043b5c2  mov      eax, dword ptr [eax + 0xe8]
004fbd95  mov      eax, dword ptr [eax + 0x38]
004fbda2  mov      eax, dword ptr [eax + 0xc8]
004fb603  push     0x78
004fb633  cmp      eax, 3
```

---

### M04.07 Master Target Scope Resolution (`0x43f450`, TargetTypes `0..15`, Heal AI & Multi-Hit Deduplication `112`)

- **Binary VA(s):** `0x43f450..0x43fe2c` (`CBattleBase::_ResolveTargets`, side-flip table `0x43fde8`/`0x43fdf4`, 16-entry scope jump table `0x43fe04`), `0x43b070..0x43b1c4` (skill & enemy-attack wrapper callers)
- **Calls:** `0x43b580` (`_IsTargetValid`), `0x43e6d0` (`_CollectUnits`), `0x43acc0` (`GetAllCombatants`), `CBattle::_UpdateTargetRate` (`vtable+0x28` = `0x44a630`), `0x505ad0` (`WeightedRandom`), `0x490790` (`CRandom::Get`), `CBattleBase::GetUnitById` (`vtable+0x30`), `0x557620` / `0x56ce70` (`HasEffect`)
- **CalledBy:** `0x43b070` (skill target resolve), `0x43b0d0` (enemy attack target resolve — checks heal commands `9, 103, 104, 128, 131, 138` and deduplication command `112 / 0x70`)
- **Typed Pseudocode:**
```text
// TargetType (0..15) side_inv table at 0x43fdf4:
//   0..4  -> 0 (targetSide = argSide)         [Enemy Single, Random, Row, Pierce, All]
//   5..12 -> 1 (targetSide = argSide ^ 1)     [Ally Single, Random, Row, All, Self, Self2, LowestHP, LowestTP]
//   13    -> 2 (targetSide = argSide)         [Special Single]
//   14..15-> 0 (targetSide = argSide)         [All Combatants, Global Random]
function CBattleBase_ResolveTargets(this: CBattleBase*, out: Vec<CGameStatusBase*>*,
                                    hitCountIO: i32*, targetType: i32, isHeal: bool,
                                    noRepeat112: bool, argSide: bool, forcedTarget: CGameStatusBase*)
                                    -> CGameStatusBase*:
    out.clear()
    if forcedTarget != null and not this._IsTargetValid(forcedTarget, true):
        forcedTarget = null
    targetSide: bool = (targetType in 5..12) ? (not argSide) : argSide
    pool = this._CollectUnits(sort=true, row=0, isPlayer=targetSide, aliveOnly=targetSide)
    forcedUnit = find(pool, u => u.status == forcedTarget) // else null (clears forcedTarget)
    actorUnit = this.units[0]

    // A. Ally-Heal AI Branch (0x43f541..0x43f7a5): triggers iff targetSide == actorUnit.isPlayerSide && isHeal
    if targetSide == (actorUnit.isPlayerSide != 0u8) and isHeal:
        switch targetType:
            case 5, 7: // Lowest HP% ally (Single=5, Row=7). Ties pick LATER unit (comiss min, cur; jb).
                chosen = forcedTarget
                if chosen == null:
                    minRatio: f32 = 1.0f
                    for u in pool:
                        ratio: f32 = f32(u.status.CurHP()) / f32(u.status.MaxHP())
                        if minRatio >= ratio:             // jb skips only when minRatio < ratio
                            minRatio = ratio; chosen = u.status; chosenRow = u.isFrontRow
                    if chosen == null:                    // 1 RNG call if all > 1.0f or empty
                        u = pool[GlobalRng.Rand(pool.size())]; chosen = u.status; chosenRow = u.isFrontRow
                if targetType == 5: out.push_back(chosen)
                else: out.extend([u.status for u in pool if u.isFrontRow == chosenRow])
            case 6: // Random ally (0 RNG if forced, else 1 RNG)
                out.push_back(forcedTarget ?? pool[GlobalRng.Rand(pool.size())].status)
            case 8: out.extend([u.status for u in pool])  // All allies (0 RNG)
            case 9: out.push_back(actorUnit.status)       // Self (0 RNG)
        *hitCountIO = 1
        return null

    // B. Standard Target Selection (0x43f7aa..0x43fdc8):
    chosenUnit: BattleUnit_s*
    if forcedTarget != null:
        chosenUnit = forcedUnit                           // 0 RNG calls
    else if targetSide == true and actorUnit.isPlayerSide == 0u8:
        // Enemy targeting Player side: AGGRO-WEIGHTED selection (1 RNG call via 0x505ad0, see M04.13)
        this.UpdateTargetRate(actorUnit)                  // vtable+0x28 = 0x44a630
        weights = [u.targetRate for u in pool]            // [u+0x70]
        chosenUnit = pool[WeightedRandom(weights, pool.size())]
    else:
        // Player targeting Enemy OR same-side non-heal: UNIFORM random (1 RNG call)
        chosenUnit = pool[GlobalRng.Rand(pool.size())]

    // C. Scope Expansion via 16-entry jump table 0x43fe04:
    switch targetType:
        case 0, 5, 13: // Single target (0 extra RNG)
            out.push_back(chosenUnit.status)
        case 1, 6:     // Multi-hit Random (Cmd 112 / 0x70 toggles without-replacement)
            if chosenUnit == forcedUnit:
                out.push_back(forcedUnit.status)          // forced target collapses to 1 hit
            else if not noRepeat112:
                // *hitCountIO RNG calls WITH replacement (UNIFORM, NOT aggro-weighted per hit!)
                for k in 0 .. (*hitCountIO - 1):
                    out.push_back(pool[GlobalRng.Rand(pool.size())].status)
            else:
                // min(*hitCountIO, pool.size()) RNG calls WITHOUT replacement (erases picked entry)
                rem = copy(pool)
                for k in 0 .. (*hitCountIO - 1):
                    if rem.empty(): break
                    idx = GlobalRng.Rand(rem.size())
                    out.push_back(rem[idx].status)
                    rem.erase_at(idx)
            *hitCountIO = 1
        case 2, 7:     // Row containing chosenUnit (0 extra RNG)
            rowCode = (chosenUnit.isFrontRow != 0u8) ? 1 : 2
            rowUnits = this._CollectUnits(sort=true, row=rowCode, isPlayer=targetSide, aliveOnly=targetSide)
            out.extend([u.status for u in rowUnits])
        case 3:        // Pierce (chosenUnit + all alive unitIds in [chosenUnit+0x64..+0x68]) (0 extra RNG)
            out.push_back(chosenUnit.status)
            for pid in chosenUnit.pierceIds:
                if pu = this.GetUnitById(pid): out.push_back(pu.status)
        case 4, 8:     // All alive units on targetSide (0 extra RNG)
            out.extend([u.status for u in pool])
        case 9, 10:    // Self (0 extra RNG)
            out.push_back(actorUnit.status)
        case 11:       // Lowest HP% across ALL combatants (both sides). Strict < (ties keep EARLIER).
            both = this._CollectUnits(true,0,true,true) + this._CollectUnits(true,0,false,false)
            best = argmin_strict(both, u => f32(u.status.CurHP()) / f32(u.status.MaxHP()), init=10000.0f)
            out.push_back(best.status)
        case 12:       // Lowest TP% on targetSide. Strict < (ties keep EARLIER).
            best = argmin_strict(pool, u => f32(u.status.curTP) / f32(u.status.maxTP), init=10000.0f)
            out.push_back(best.status)
        case 14:       // Everyone (targetSide first, then opposite side) (0 extra RNG)
            out.extend([u.status for u in pool])
            opp = this._CollectUnits(true, 0, not targetSide, not targetSide)
            out.extend([u.status for u in opp])
        case 15:       // Global random across both sides (1 extra RNG unless forced)
            if chosenUnit == forcedUnit: out.push_back(forcedUnit.status)
            else:
                all = this.GetAllCombatants()             // 0x43acc0 (players + enemies)
                out.push_back(all[GlobalRng.Rand(all.size())].status)
    return out.empty() ? null : out[0]
```
- **Program Evidence:**
```asm
0043f4be  movzx    eax, byte ptr [eax + 0x43fdf4]
0043f4c5  jmp      dword ptr [eax*4 + 0x43fde8]
0043f6bf  divss    xmm1, xmm0
0043f6c8  comiss   xmm0, xmm1
0043f6cb  jb       0x43f6e3
0043f7e2  jmp      dword ptr [eax*4 + 0x43fe04]
0043f7f1  call     dword ptr [eax + 0x28]
0043f847  mov      eax, dword ptr [eax + 0x70]
0043f859  call     0x505ad0
0043f8d7  call     0x490790
0043f946  call     0x490790
0043f978  call     0x606150
0043fa0c  call     0x43e6d0
0043fa85  mov      eax, dword ptr [ecx + 0x64]
0043faaf  call     dword ptr [eax + 0x30]
0043fc29  comiss   xmm0, xmm1
0043fc2c  jbe      0x43fc36
0043fca0  comiss   xmm2, xmm1
0043fca3  jbe      0x43fca8
0043fd60  call     0x43acc0
```

---

### M04.08 Player Menu Target Selection & Item Scopes (`CBattleMenuSelectTarget` `0x456ff0`, TargetTypes `0..18`)

- **Binary VA(s):** `0x456ff0..0x457690` (`CBattleMenuSelectTarget::_Initialize`, 19-entry jump table `0x457648`), `0x45795f..0x457c7c` (`CBattleMenuSkill::Update`), `0x45340b..0x453530` (`CBattleMenuItem::Update`), `0x56d570..0x56d598` (`CParameterSkill::IsAliveTargetOnly`), `0x55b640..0x55b667` (`CParameterItem::CanTargetEnemy`)
- **Calls:** `0x43b1d0` (`GetEnemyUnits`), `0x43af10` (`GetPlayerUnits`), `0x43b8e0` (`GetPierceTargetGroups`), `0x43bab0` (`_FilterPierceOrder`), `0x490790` (`CRandom::Get`), `0x56c1f0` (`GetSkillTargetType`), `0x56d570`, `0x55b640`
- **CalledBy:** `M00.04` (`CBattleMenuAttack`, `CBattleMenuSkill`, `CBattleMenuItem`)
- **Typed Pseudocode:**
```text
// 1. Revive / aliveOnly flag for skills ([Action_s + 0x3a]) via 0x56d570:
function IsSkillAliveOnly(skillId: i32) -> bool:
    // Returns false ONLY if skill contains Cmd 105 (0x69 Resurrect) or Cmd 106 (0x6a Nurse).
    return (not SkillHasCommand(skillId, 105 /* 0x69 */))
       and (not SkillHasCommand(skillId, 106 /* 0x6a */))

// 2. Item targeting flags in CBattleMenuItem::Update (0x45344c..0x4534d6):
//    Item targetType = ItemParam[itemId].targetType ([+0x74]) MUST be in {16, 17, 18}.
//    canTargetEnemies = (ItemParam[itemId].flags30 >> 4) & 1 (0x55b640).
//    canTargetDead    = any(effId == 12 /* 0x0c Revive */ in ItemParam[itemId].effectIds[+0x60]).

// 3. Player target scope dispatch in CBattleMenuSelectTarget::_Initialize (0x456ff0, JT 0x457648):
//    Note: Player manual selection of ally scopes (5..8, 16..18) calls GetPlayerUnits(..., aliveOnly=0)
//    so dead allies appear in the selector; for skills, [Action_s+0x3a] enforces aliveOnly at execution.
function InitPlayerTargetSelector(targetType: i32, canTargetEnemies: bool, canTargetDead: bool):
    switch targetType:
        case 0:  SingleEnemySelector(GetEnemyUnits(sort=1, row=0))               // 0x45703f
        case 1:  // Random Enemy: rolls action.hitCount uniform draws from enemies, then clamps hitCount = (hitCount != 0 ? 1 : 0)
                 for k in 0 .. (action.hitCount - 1): targets.push(enemies[Rand(enemies.size())]) // 0x45707a
        case 2:  RowEnemySelector(GetEnemyUnits(sort=1, row=0))                  // 0x4570fa
        case 3:  PierceEnemySelector(GetEnemyUnits(1,0), GetPierceGroups(0))     // 0x457133
        case 4:  targets = GetEnemyUnits(sort=1, row=0)                          // All Enemies (0x4571ae)
        case 5:  SingleAllySelector(GetPlayerUnits(sort=1, row=0, aliveOnly=0))  // 0x4571c3
        case 6:  // Random Ally: rolls action.hitCount uniform draws from players (0x4571eb)
                 for k in 0 .. (action.hitCount - 1): targets.push(players[Rand(players.size())])
        case 7:  RowAllySelector(GetPlayerUnits(sort=1, row=0, aliveOnly=0))     // 0x45726a
        case 8:  targets = GetPlayerUnits(sort=1, row=0, aliveOnly=0)            // All Allies (0x4572a5)
        case 9:  targets = [actor.status]                                        // Self (0x4572bc)
        case 10: // Handled directly in CBattleMenuSkill (0x457b9d) as Self without opening SelectTarget!
                 // Passing 10..13 to SelectTarget triggers assert at 0x457614.
        case 14: targets = GetEnemyUnits(1,0) + GetPlayerUnits(1,0,0)            // Everyone (0x4572e1)
        case 15: // Random Everyone: rolls action.hitCount uniform draws from (enemies + players) (0x45733d)
        case 16: // Item Single (0x45740a): pool = canTargetEnemies ? (enemies + players) : players; passes canTargetDead
        case 17: // Item Row    (0x457499): pool = canTargetEnemies ? (enemies + players) : players
        case 18: // Item SideAll(0x457525): CGameSelectSideAll over (canTargetEnemies ? enemies+players : players)
```
- **Program Evidence:**
```asm
0045702f  cmp      eax, 0x12
00457032  ja       0x457614
00457038  jmp      dword ptr [eax*4 + 0x457648]
004570b7  call     0x490790
004570ef  setne    al
004570f2  mov      dword ptr [ecx + 0x40], eax
00457191  call     0x43b8e0
00457227  call     0x490790
0045740a  cmp      byte ptr [ebp + 8], 0
00453454  lea      eax, [ecx - 0x10]
00453457  cmp      eax, 2
004534a5  cmp      dword ptr [eax], 0xc
004534be  call     0x55b640
0056d571  mov      edx, 0x69
0056d581  mov      edx, 0x6a
0055b65c  mov      eax, dword ptr [eax + 0x30]
0055b65f  shr      eax, 4
```

---

### M04.09 Enemy Action Target Selection, Mid-Action Retarget Fallback & Splash (`137`)

- **Binary VA(s):** `0x41a850..0x41abcc` (`CActionEnemyAttack::_SelectTarget`, jump tables `0x41ab94`/`0x41aba4` and `0x41abb4`/`0x41abc0`), `0x420470..0x420555` (`CActionPatternBase::_CheckActor` & `_CheckTarget`), `0x420560..0x420893` (`CActionPatternBase::_SelectTarget`, jump tables `0x420868`, `0x420884`/`0x42088c`), `0x4200e0..0x4202ff` (`CActionPatternBase::_BeforeAttackInterrupt` `Cmd 137` splash)
- **Calls:** `0x43b580` (`_IsTargetValid`), `0x43af10` (`GetPlayerUnits`), `0x43b1d0` (`GetEnemyUnits`), `0x43ad50` (`GetOrderedSideUnits`), `0x43b8e0` (`GetPierceGroups`), `0x43ba10` (`GetUnitPierceGroup`), `0x43bab0` (`_FilterPierceOrder`), `0x490790` (`CRandom::Get`), `0x61e650` (`trunc0_u32`)
- **CalledBy:** `M00.05` (`CActionEnemyAttack::Update` at `0x419d06`, `CActionPattern*` subclasses at `0x41ee5b`, `0x41f16b`, `0x42a99c`, `0x42c01d`, `0x42c9e0`)
- **Typed Pseudocode:**
```text
// 1. Mid-Action Target Validation (_CheckTarget 0x420500..0x420555):
function CActionPatternBase_CheckTarget(this: CActionPatternBase*, extraTarget: CGameStatusBase*) -> bool:
    if this.battle == null: return true
    if this.action.slots.empty(): return false
    curSlot = this.action.slots[this.action.hitIdx]       // [action+0x20] + 0x4c * [action+0x3c]
    if not this.battle._IsTargetValid(curSlot.target, this.action.aliveOnly):
        return false
    if extraTarget != null:
        return this.battle._IsTargetValid(extraTarget, this.action.aliveOnly)
    return true

// 2. Mid-Action Retarget Fallback (CActionPatternBase::_SelectTarget 0x420560..0x420893):
//    Called when current target died pre-action or mid-multi-hit!
//    RNG calls: 1 (UNIFORM GlobalRng.Rand(pool.size()) — does NOT use aggro weighting 0x505ad0!).
function CActionPatternBase_SelectTarget(this: CActionPatternBase*):
    isPlayerActor: bool = (dynamic_cast<CGamePlayerStatusBase*>(this.action.actor) != null)
    // Derive targetType from actionType:
    //   actionType == 1 (Basic Attack): (flag39 != 0) ? 2 : 0
    //   actionType in {0, 2, 3} (Skill): GetSkillTargetType(skillId)
    //   actionType in {8, 9} (EnemyAtk): GetEnemyAttackTargetType(enemyAtkId)
    //   other: -1 (no retarget)
    // Jump table 0x420868 (targetType 0..6):
    //   - targetType 2 (Row), 4 (All), or > 6: NO retarget (returns immediately!).
    //   - targetType 3 (Pierce): ONLY retargets when hitIdx == 0 ([action+0x3c] == 0)!
    //     If primary pierce target died before hit 0, clears slots[1..], picks new random target,
    //     rebuilds pierce group via 0x43ba10 + 0x43bab0, and updates [action+0x2c].
    //   - targetType 0, 1 (Enemy Single/Random):
    //     if isPlayerActor: pool = GetEnemyUnits(sort=1, row=0)
    //     else:             pool = GetPlayerUnits(sort=1, row=0, aliveOnly=1)
    //   - targetType 5, 6 (Ally Single/Random):
    //     if isPlayerActor: pool = GetPlayerUnits(sort=0, row=0, aliveOnly=action.aliveOnly)
    //     else:             pool = GetEnemyUnits(sort=1, row=0)
    if pool.empty(): return
    newTarget = pool[GlobalRng.Rand(pool.size())]         // 0x4206b7 (UNIFORM!)
    if targetType == 3:
        RebuildPierceSlots(this.action, newTarget)        // 0x42076f..0x4207f5
    else:
        this.action.slots[this.action.hitIdx].ReplaceTarget(newTarget) // preserves remaining hits
    this.action.primaryTarget = newTarget                 // [action+0x2c]

// 3. CActionEnemyAttack::_SelectTarget (0x41a850..0x41abcc):
//    Called on enemy re-targeting (e.g. after chant completion if target died):
//    - targetType 0..3: opposing side; 5..7: same side; 4,8,9,10,14: no-op; 11..13: assert.
//    - targetType 0,1,3,5,6: uniform Rand(pool.size()); for 3 (Pierce), appends pierce group (0x43b8e0).
//    - targetType 2,7 (Row): uniform Rand(pool.size()) picks seed unit, then adds all pool units with same isFrontRow!

// 4. Target Count / Splash Expansion (Cmd 137 / 0x89 in _BeforeAttackInterrupt 0x42017a..0x4202ff):
//    RNG calls: 0. Runs once before hit execution.
function ExpandTargetCount137(this: CActionPatternBase*, actCmds: Vec<CCommand*>*):
    if c137 = FindCommand(actCmds, 137 /* 0x89 Target Count */):
        extraCount: u32 = trunc0_u32(c137.val) - 1u       // 0x61e650 then dec eax
        primary = this.action.slots[0].target
        isPlayerPrimary = (dynamic_cast<CGamePlayerStatusBase*>(primary) != null)
        // Collects all alive non-doll/non-summon units in battle.units order (0x43ad50)
        ordered = this.battle.GetOrderedUnits(sort=0, aliveOnly=1, includeDolls=0, includeSummons=0)
        idx = find_index(ordered, primary) + 1
        while idx < ordered.size() and extraCount > 0u:
            if SameSideClass(ordered[idx], isPlayerPrimary):
                this.action.slots.push_back(TargetSlot(ordered[idx], this.action.hitCount))
                extraCount -= 1u
            idx += 1
```
- **Program Evidence:**
```asm
0042051e  imul     edx, dword ptr [eax + 0x3c], 0x4c
0042052a  call     0x43b580
0042061b  jmp      dword ptr [edi*4 + 0x420868]
0042063d  cmp      dword ptr [eax + 0x3c], 0
00420641  jne      0x42084b
004206b7  call     0x490790
004207a5  call     0x43ba10
004207cb  call     0x43bab0
0042017a  mov      edx, 0x89
004201e0  call     0x43ad50
004201f6  call     0x61e650
004201fe  dec      eax
0041a8c0  jmp      dword ptr [eax*4 + 0x41ab94]
0041a954  jmp      dword ptr [eax*4 + 0x41abb4]
0041a973  call     0x490790
0041aaa5  call     0x490790
```

---

### M04.10 Target Redirection: Physical Cover (`171`) & Absence of `172` / `324` / Magic Cover

- **Binary VA(s):** `0x420b40..0x420f02` (`CActionPatternBase::_Cover`), `0x424940..0x424a30` (`_CheckAfterAttackInterrupt` Cover `171` wear-off), `0x4fc08d..0x4fc0bb` (`Cmd 172` = `Max HP`, NOT redirect)
- **Calls:** `0x557530` (`GetEnemyAttackTargetType`), `0x56c1f0` (`GetSkillTargetType`), `0x43af10` (`GetPlayerUnits`), `0x43b1d0` (`GetEnemyUnits`), `CGameStatusBase::HasCommand` (`vtable+0x50`), `CGameStatusBase::GetCommand` (`vtable+0x48`), `0x490790` (`CRandom::Get`)
- **CalledBy:** `M00.05` (`CActionPattern*` pre-calc physical dispatch), `M00.07` (`_CheckAfterAttackInterrupt`)
- **Typed Pseudocode:**
```text
// Binary ground truth on target redirection commands:
//   - Cmd 171 (0xab, Cover): the SOLE target-redirect command in the binary.
//   - Cmd 172 (0xac, Max HP): modifies Max HP at 0x4fc08d; performs ZERO target redirection.
//   - Cmd 324 (0x144): plain CCommand marker with ZERO inline askers in the binary.
//   - Magic / AoE Cover does NOT exist: _Cover (0x420b40) strictly requires isPhysical != 0
//     and TargetType in {0, 1}.

// 1. Pre-Calc Physical Cover (CActionPatternBase::_Cover 0x420b40..0x420f02):
//    RNG calls: 0 if no eligible coverer; 1 (GlobalRng.Rand(candidates.size())) if >= 1 coverer.
function CActionPatternBase_Cover(this: CActionPatternBase*):
    if this.battle == null or this.isPhysical == 0u8: return
    targetType = GetActionTargetType(this.action)
    if targetType != 0 and targetType != 1: return        // Single or Random ONLY (0x420bc8..0x420bcf)
    slot = &this.action.slots[this.action.hitIdx]         // [action+0x20] + 0x4c * [action+0x3c]
    if slot.wasCovered != 0u8: return                     // [slot+0x44] prevents double-cover

    // Collect alive allies on target's side (slot.memberId != -1 -> player side, else enemy side):
    allies = (slot.memberId != -1) ? this.battle.GetPlayerUnits(sort=0, row=0, aliveOnly=1)
                                   : this.battle.GetEnemyUnits(sort=0, row=0)
    // Filter: c != slot.target AND c.HasCommand(171 / 0xab Cover)
    candidates = [c for c in allies if c != slot.target and c.HasCommand(171 /* 0xab */)]
    if candidates.empty(): return

    coverer = candidates[GlobalRng.Rand(candidates.size())] // 0x420ca7 (uniform across coverers)
    slot.ReplaceTarget(coverer)                           // preserves hit count [slot+0x40]
    slot.wasCovered = 1u8                                 // [slot+0x44] = 1 (0x420eb3)

// 2. Post-Hit Cover Wear-Off Roll (_CheckAfterAttackInterrupt 0x42496b..0x424a30):
//    RNG calls: 1 if slot.wasCovered != 0 and coverer is still alive with Cmd 171.
function CheckCoverWearOff(slot: TargetSlot*):
    if slot.wasCovered != 0u8 and IsAlive(slot.target):
        if cmd171 = slot.target.GetCommand(0, 171 /* 0xab Cover */):
            if GlobalRng.Rand(100) < trunc0(cmd171.val * 100.0f): // cvttss2si, strict <
                QueueRemoveStatus(slot.target, 171 /* 0xab */)
```
- **Program Evidence:**
```asm
00420b70  cmp      byte ptr [ecx + 0x79], 0
00420bc8  test     eax, eax
00420bcc  cmp      eax, 1
00420bcf  jne      0x420ede
00420be2  cmp      byte ptr [ebx + 0x44], 0
00420c42  cmp      ecx, dword ptr [ebx]
00420c48  push     0xab
00420ca7  call     0x490790
00420eb3  mov      byte ptr [ebp - 0x14], 1
0042496e  cmp      byte ptr [eax + 0x44], 0
0042497a  push     0xab
004249a6  call     0x490790
004249b8  cvttss2si ecx, xmm0
004249bc  cmp      eax, ecx
004249be  jge      0x424b1d
004fc08d  push     0xac
```

---

## 3. Formation, Row Adjacency & Target-Rate / Aggro Weighting (`M04.11` – `M04.13`)

### M04.11 Formation Table (`FormationShareTable` `0x6517a0`), Row Assignment & Enemy Front-Row Wipe Shift

- **Binary VA(s):** `0x6517a0..0x65187b` (`FormationShareTable`, 11 rows x 5 `i32`), `0x46af00..0x46b080` (`CGameData::GetFormationCounts`, jump table `0x46b050`), `0x43da60..0x43db60` (`CBattleBase::_Initialize`), `0x43b7a8..0x43b865` (`CBattleBase::_RemoveUnit` enemy front-row wipe shift)
- **Calls:** `CGameData::GetFormation` (`vtable+0x17c` = `0x46b240`), `CGameData::GetFormationCounts` (`vtable+0x160` = `0x46af00`), `0x43e6d0` (`_CollectUnits`), `CBattleBase::_SortTime` (`vtable+0x24` = `0x43e510`)
- **CalledBy:** `M00.01` (`CBattleBase::_Initialize`), `CBattleBase::_RemoveUnit` (`0x43b6a0`)
- **Typed Pseudocode:**
```text
// 1. Formation Table (0x6517a0 & GetFormationCounts 0x46af00):
//    formationId | (front, back) | baseShare [slot 0..4] (sum = 100)
//    ------------|---------------|-----------------------------------
//       -1       |   (0, 0)      | (unused)
//        0       |   (1, 0)      | [100,   0,   0,   0,   0]
//        1       |   (2, 0)      | [ 50,  50,   0,   0,   0]
//        2       |   (1, 1)      | [ 60,  40,   0,   0,   0]
//        3       |   (3, 0)      | [ 33,  34,  33,   0,   0]
//        4       |   (2, 1)      | [ 38,  38,  24,   0,   0]
//        5       |   (1, 2)      | [ 40,  30,  30,   0,   0]
//        6       |   (3, 1)      | [ 28,  28,  28,  16,   0]
//        7       |   (2, 2)      | [ 30,  30,  20,  20,   0]
//        8       |   (1, 3)      | [ 31,  23,  23,  23,   0]
//        9       |   (3, 2)      | [ 24,  24,  24,  14,  14]
//       10       |   (2, 3)      | [ 26,  26,  16,  16,  16]
//
//    At battle start (0x43dac4..0x43db42):
//      unit.baseShare  = FormationShareTable[formationId][slotIdx]   // [unit+0x74]
//      unit.isFrontRow = (u32(slotIdx) < frontCount) ? 1u8 : 0u8     // [unit+0x79]
//
// 2. Mid-Battle Formation Swap:
//    NOT SUPPORTED in battle. FormationShareTable (0x6517a0) has exactly 1 reference in the
//    entire binary (0x43daca in CBattleBase::_Initialize). Player [unit+0x79] and [unit+0x74]
//    are written ONLY once at battle initialization and never change mid-battle.
//
// 3. Front-Row Wipe Shift (CBattleBase::_RemoveUnit 0x43b7a8..0x43b865):
//    APPLIES TO ENEMIES ONLY (isPlayer = 0). Player back row NEVER shifts forward when the
//    player front row dies! Does NOT re-run _SetPierceTarget (0x43def0).
//    RNG calls: 0.
function OnEnemyRemoved_CheckFrontRowShift(this: CBattleBase*):
    frontEnemies = this._CollectUnits(sort=false, row=1 /* Front */, isPlayer=false, aliveOnly=false)
    if frontEnemies.empty():
        backEnemies = this._CollectUnits(sort=false, row=2 /* Back */, isPlayer=false, aliveOnly=false)
        for u in backEnemies:
            u.enemyStatus.isFrontRow = 1u8                // [u.status + 0xa4] = 1
            u.isFrontRow = 1u8                            // [u + 0x79] = 1 (0x43b84c)
            // Also shifts visual screen position by ([0x738b7c]/2, [0x738b78]/2)
    this.vtable_SortTime(1, 0)                            // 0x43b85f
```
- **Program Evidence:**
```asm
0043dac4  lea      eax, [edi + edi*4]
0043dac7  lea      eax, [eax*4 + 0x6517a0]
0043db33  mov      eax, dword ptr [esi]
0043db35  mov      dword ptr [edi + 0x74], eax
0043db3c  cmp      ebx, dword ptr [ebp - 0x1c]
0043db3f  setb     al
0043db42  mov      byte ptr [edi + 0x79], al
0046af18  jmp      dword ptr [ecx*4 + 0x46b050]
0046b009  mov      dword ptr [eax], 3
0046b013  mov      dword ptr [eax], 2
0046b020  mov      dword ptr [eax], 2
0046b02a  mov      dword ptr [eax], 3
0043b7ac  push     1
0043b7ae  push     0
0043b7b6  call     0x43e6d0
0043b7be  cmp      eax, dword ptr [ebp - 0x20]
0043b7c1  jne      0x43b857
0043b7cb  push     2
0043b7d5  call     0x43e6d0
0043b80f  mov      byte ptr [ecx + 0xa4], 1
0043b84c  mov      byte ptr [edx + 0x79], 1
```

---

### M04.12 Pierce / Column Adjacency Graph (`CBattleBase::_SetPierceTarget` `0x43def0`)

- **Binary VA(s):** `0x43def0..0x43e500` (`CBattleBase::_SetPierceTarget`), `0x43b8e0..0x43bbd8` (`_GetPierceTargetList`, `_GetPierceTargets`, `_FilterPierceOrder`), `0x439e0e..0x439f5b` (enemy unitId assignment & call to `0x43def0`)
- **Calls:** `CGameData::GetFormationCounts` (`vtable+0x160`), `CGameData::GetPartyMember` (`vtable+0x150`), `CBattleBase::GetUnitByStatus` (`vtable+0x38` = `0x43e7f0`), `CBattleBase::GetUnitById` (`vtable+0x30` = `0x43e830`)
- **CalledBy:** `CBattleBase::_Initialize` (`0x43dba4`), `CBattleBase::_InitializeEnemy` (`0x439f5b`)
- **Typed Pseudocode:**
```text
// Builds the vector of pierced unitIds at [BattleUnit_s + 0x64..+0x68] for every unit.
// RNG calls: 0.
function CBattleBase_SetPierceTarget(this: CBattleBase*):
    for u in this.units: u.pierceIds.clear()              // [u+0x68] = [u+0x64]

    // 1. Player Party Pierce Graph (0x43df22..0x43e184):
    //    Let F = frontCount, B = backCount; front slots = 0..F-1, back slots = F..F+B-1.
    //    If B == 0: no player has pierce targets.
    (F, B) = GameData.GetFormationCounts(0xb)
    if B > 0:
        if F <= B:                                        // 0x43df4e..0x43e184
            diff = B - F                                  // 0, 1, or 2
            for f in 0 .. F-1:                            // Front -> Back edges
                if diff == 0:   add_edge(front[f], back[f])
                elif diff == 1: add_edge(front[f], back[f]); add_edge(front[f], back[f + 1])
                elif diff == 2: add_edge(front[f], back[f + 1]) // center back slot (e.g. 1F/3B: F0 -> B1)
            for b in 0 .. B-1:                            // Back -> Front edges
                if diff == 0:   add_edge(back[b], front[b])
                elif diff == 1:
                    add_edge(back[b], front[b >> 1])      // b=0->F0, b=1->F0, b=2->F1
                    if b == 1 and (b >> 1) + 1 < F:       // center back hits BOTH adjacent fronts!
                        add_edge(back[1], front[1])
                elif diff == 2:
                    if b == 1: add_edge(back[1], front[0])
        else:                                             // F > B (0x43e1f0..0x43e40f)
            diff = F - B                                  // 1 or 2
            for b in 0 .. B-1:                            // Back -> Front edges
                if diff == 1: add_edge(back[b], front[b]); add_edge(back[b], front[b + 1])
                elif diff == 2: add_edge(back[b], front[b + 1]) // center front (e.g. 3F/1B: B0 -> F1)
            for f in 0 .. F-1:                            // Front -> Back edges
                if diff == 1:
                    add_edge(front[f], back[f >> 1])
                    if f == 1 and (f >> 1) + 1 < B:
                        add_edge(front[1], back[1])       // center front hits BOTH adjacent backs!
                elif diff == 2:
                    if f == 1: add_edge(front[1], back[0])

    // 2. Enemy Pierce Graph (0x43e185..0x43e494):
    //    Enemy unitIds assigned in 0x439e0e..0x439e2c:
    //      Front row slot k -> unitId = 0x3e8 (1000) + k
    //      Back  row slot k -> unitId = 0x400 (1024) + k   (offset = +24 = +0x18)
    for u in this.units where u.isPlayerSide == 0u8:
        if u.isFrontRow != 0u8:
            // Front enemy at id pierces existing back-row enemies in [id + 23 .. id + 25] (+0x17..+0x19)
            for pid in [u.unitId + 0x17, u.unitId + 0x18, u.unitId + 0x19]:
                if this.GetUnitById(pid) != null: u.pierceIds.push_back(pid)
        else:
            // Back enemy at id pierces existing front-row enemies in [id - 25 .. id - 23] (-0x19..-0x17)
            for pid in [u.unitId - 0x19, u.unitId - 0x18, u.unitId - 0x17]:
                if this.GetUnitById(pid) != null: u.pierceIds.push_back(pid)
```
- **Program Evidence:**
```asm
0043df36  call     dword ptr [eax + 0x160]
0043df4e  cmp      ecx, eax
0043df50  ja       0x43e1f0
0043df8b  cmp      ecx, 1
0043e002  cmp      ecx, 2
0043e0ba  shr      edx, 1
0043e0ee  cmp      ebp, 1
0043e1a3  cmp      byte ptr [ebx + 0x78], 0
0043e1ad  cmp      byte ptr [ebx + 0x79], 0
0043e1b1  mov      ebp, 3
0043e1bf  add      edi, 0x17
0043e1cb  call     dword ptr [eax + 0x30]
0043e433  add      edi, -0x19
0043e445  call     dword ptr [eax + 0x30]
00439e11  mov      ecx, 0x400
00439e1e  mov      eax, 0x3e8
```

---

### M04.13 Target-Rate / Aggro Weighting & Weighted Selection (`CBattle::_UpdateTargetRate` `0x44a630`, `0x505ad0`)

- **Binary VA(s):** `0x44a630..0x44a793` (`CBattle::_UpdateTargetRate`, `CBattle` `vtable+0x28`), `0x43f7e9..0x43f892` (aggro-weighted invocation in `0x43f450`), `0x505ad0..0x505b75` (`WeightedRandom`)
- **Calls:** `0x43e6d0` (`_CollectUnits`), `CGameStatusBase::GetCommand` (`vtable+0x48`), `CGamePlayerStatusBase::GetMemberId` (`vtable+0x138`), `CGameStatusBase::GetEnchantCount` (`vtable+0xf0`), `0x490790` (`CRandom::Get`)
- **CalledBy:** `M04.07` (`0x43f7f1` when an enemy selects a player target with no forced target)
- **Typed Pseudocode:**
```text
// 1. CBattle::_UpdateTargetRate (0x44a630..0x44a793):
//    Recomputes effective aggro weight [u+0x70] for every alive, non-petrified player unit u.
//    RNG calls: 0.
function CBattle_UpdateTargetRate(this: CBattle*, attacker: BattleUnit_s*):
    players = this._CollectUnits(sort=true, row=0, isPlayer=true, aliveOnly=true)
    for u in players:
        rate: i32 = u.baseShare                           // [u+0x74] from FormationShareTable
        // Provoke / Taunt (Cmd 170 / 0xaa) resides on the ATTACKER (enemy), storing the
        // taunter's player memberId at cmd170->vtable+0x40()!
        if cmd170 = attacker.enemyStatus.GetCommand(0, 170 /* 0xaa Taunt */):
            if cmd170.GetActorId() == u.playerStatus.GetMemberId():
                rate += trunc0(cmd170.val)                // cvttss2si at 0x44a71c
        // Equipment enmity enchants (both stackable):
        rate += 10 * u.status.GetEnchantCount(49 /* 0x31 Enmity UP */)
        rate -=  5 * u.status.GetEnchantCount(50 /* 0x32 Enmity DOWN */)
        u.targetRate = max(10, rate)                      // floor clamp = 10 (0x0a) at 0x44a757

// 2. WeightedRandom (0x505ad0..0x505b75):
//    RNG calls: 1 (GlobalRng.Rand(total) -> [0 .. total - 1]).
function WeightedRandom(weights: i32*, count: u32) -> u32:
    prefix: i32[count]
    total: i32 = 0
    for i in 0 .. count-1:
        total += weights[i]
        prefix[i] = total
    r: u32 = u32(GlobalRng.Rand(total))                   // 0x490790(total)
    for i in 0 .. count-1:
        if r < u32(prefix[i]):                            // unsigned jb (strict <) at 0x505b43
            return i
    return count
```
- **Program Evidence:**
```asm
0044a673  call     0x43e6d0
0044a6ca  mov      eax, dword ptr [edi + 0x74]
0044a6d0  mov      dword ptr [edi + 0x70], eax
0044a6e1  push     0xaa
0044a6fa  call     dword ptr [edx + 0x40]
0044a706  call     dword ptr [edx + 0x138]
0044a70c  cmp      esi, eax
0044a71c  cvttss2si eax, dword ptr [ebp - 0x14]
0044a721  add      dword ptr [edi + 0x70], eax
0044a727  push     0x31
0044a734  push     0x32
0044a736  lea      eax, [eax + eax*4]
0044a739  add      eax, eax
0044a74d  lea      eax, [eax + eax*4]
0044a750  sub      ecx, eax
0044a757  cmp      ecx, 0xa
0044a75a  cmovl    ecx, eax
0044a75d  mov      dword ptr [edi + 0x70], ecx
00505b20  add      edx, dword ptr [esi + ecx]
00505b35  call     0x490790
00505b40  cmp      eax, dword ptr [ebx + esi*4]
00505b43  jb       0x505b4a
```

---

## 4. Binary Action & Skill Legality Gate (`M04.14` – `M04.16`)

### M04.14 Equipment & Weapon Condition Gate (`CGamePlayerStatusBase::CheckSkillCondition` `0x4f4910`)

- **Binary VA(s):** `0x4f4910..0x4f4c30` (`CGamePlayerStatusBase::CheckSkillCondition`, `vtable+0x12c`, 21-entry jump table `0x4f4bdc`), `0x4f4f60..0x4f4fb6` (`GetEquipmentID`), `0x559190..0x5592ea` (`IsShield`, `GetWeaponCategory`, `IsMeleeWeapon`)
- **Calls:** `0x4f4f60` (`GetEquipmentID(slot)`), `0x559290` (`IsMeleeWeapon`), `0x559260` (`GetWeaponCategory`), `0x559190` (`IsShield`)
- **CalledBy:** `M04.15` (`0x455d2b` inside `GetUsableSkills`), dungeon/status UI skill checks (`0x4ad4eb`, `0x4ad5f5`, `0x4c7902`, `0x4dacc5`)
- **Typed Pseudocode:**
```text
// Equipment slots passed to GetEquipmentID (0x4f4f60 -> [player + slot*4 + 0xa8]):
//   slot 0 = Main Weapon, slot 1 = Sub / Shield, slot 2 = Head / Armor, slot 3 = Accessory / Body.
// Returns -1 when empty. NO dual-wield condition exists in DT22.
// RNG calls: 0.
function CheckSkillCondition(player: CGamePlayerStatusBase*, condType: i32) -> bool:
    // Jump table 0x4f4bdc indexed by (condType + 1) in 0..20 (condType in -1..19):
    switch condType:
        case -1:    return true                                              // Unconditional (0x4f495f)
        case 0:     id = player.GetEquipmentID(0)                            // Melee Weapon (0x4f492a)
                    return id != -1 and IsMeleeWeapon(id)                    // 0x559290: [e+0x38]==0 && ([e+0x6c]>>1)&1
        case 1..14: id = player.GetEquipmentID(0)                            // Exact Weapon Category (0x4f4944..0x4f4b24)
                    return id != -1 and GetWeaponCategory(id) == (condType - 1) // 0x559260: [e+0x68] == 0..13
        case 15:    id = player.GetEquipmentID(0)                            // Ranged / Special Categories (0x4f4b27)
                    return id != -1 and GetWeaponCategory(id) in {14, 15, 16, 17, 18, 19, 20} // 0x0e..0x14
        case 16:    id = player.GetEquipmentID(1)                            // Shield in Slot 1 (0x4f4b70)
                    return id != -1 and IsShield(id)                         // 0x559190: [e+0x38] == 1
        case 17:    return player.GetEquipmentID(2) != -1                    // Slot 2 Equipped (0x4f4b8e)
        case 18:    return player.GetEquipmentID(3) != -1                    // Slot 3 Equipped (0x4f4b9f)
        case 19:    return player.GetEquipmentID(0) != -1                    // Any Weapon in Slot 0 (0x4f4bb0)
        default:    assert("ConditionType error")                            // 0x4f4bc1
```
- **Program Evidence:**
```asm
004f4917  lea      esi, [edx + 1]
004f491a  cmp      esi, 0x14
004f491d  ja       0x4f4bc1
004f4923  jmp      dword ptr [esi*4 + 0x4f4bdc]
004f492a  push     0
004f492c  call     0x4f4f60
004f493b  call     0x559290
004f4955  call     0x559260
004f4b41  cmp      eax, 0xe
004f4b5f  cmp      eax, 0x14
004f4b70  push     1
004f4b85  call     0x559190
004f4b8e  push     2
004f4b9f  push     3
004f4bb0  push     0
005591ac  cmp      dword ptr [eax + 0x38], 1
0055927c  mov      eax, dword ptr [eax + 0x68]
005592d9  mov      eax, dword ptr [eax + 0x6c]
005592dc  shr      eax, 1
```

---

### M04.15 Battle Skill, Item & Command Legality Gate (`0x455bc0`, `0x4fd250`, `0x515f7c`, `0x455e60`)

- **Binary VA(s):** `0x455bc0..0x455e54` (`GetUsableBattleSkills`, `IsUseBattle` jump table `0x455e3c`), `0x4f7190..0x4f725e` (`CGamePlayerStatus::GetTP`), `0x4fd250..0x4fd3bf` (`CGamePlayerStatusBase::CalcConsumeTP`, `vtable+0x11c`), `0x4fb650..0x4fb65e` (`IsShadowSewed`, `vtable+0xd0`), `0x455e60..0x456145` (`CBattleMenuMain::_Initialize`), `0x515f7c..0x516025` (`CMenuBase::EnumerateItem` case `0x15`)
- **Calls:** `CGameStatusBase::IsDead` (`+0x38`), `IsSleep` (`+0xbc`), `IsPetrified` (`+0xc8`), `IsFreeze` (`+0xb4`), `IsSilence` (`+0xc0`), `IsShadowSewed` (`+0xd0` = `0x4fb650`), `CheckSkillCondition` (`+0x12c` = `0x4f4910`), `GetTP` (`+0x150` = `0x4f7190`), `CalcConsumeTP` (`+0x11c` = `0x4fd250`), `0x61c040` (`ceil(f64)`), `0x515bb0` (`EnumerateItem`)
- **CalledBy:** `M00.04` (`CBattleMenuMain` Outer State 2 player command selection)
- **Typed Pseudocode:**
```text
// RNG calls: 0.
// Explicitly NOT gated at menu legality time: no row restriction, no stance gate, no HP-cost
// gate, and no Paralysis gate (Paralysis 115 is a 30% turn-start skip in M01/M06).

// 1. Battle Skill Legality (0x455bc0..0x455e54, called by CBattleMenuMain for cat=0 [Technique] and cat=1 [Magic]):
function IsBattleSkillLegal(actor: CGamePlayerStatus*, skillId: i32) -> bool:
    // Actor incapacitation gate (0x455bd4..0x455c05):
    if actor.IsDead() or actor.IsSleep() or actor.IsPetrified():
        return false
    // SkillType & IsUseBattle gate (JT 0x455e3c): Passive(2), Joint(3), Party(4), Other(5) EXCLUDED!
    st: i32 = GetSkillType(skillId)
    if st == 0:                                           // Technique ([0x738a64])
        if ((TechParam[skillId].flags48 >> 4) & 1u) == 0u: return false // bit 4 = 0x10
    else if st == 1:                                      // Magic ([0x738a58])
        if ((MagicParam[skillId].flags48 >> 3) & 1u) == 0u: return false // bit 3 = 0x08
    else:
        return false                                      // Non-active skill types excluded

    usable: bool = true
    if st == 0:                                           // Technique checks (0x455cb9..0x455d6b)
        if actor.IsFreeze():                              // vtable+0xb4 (Cmd 114 / 0x72 Freeze)
            usable = false
        else:
            // Multi-condition weapon check: OR semantics! Passes if N==0 OR ANY condType passes.
            N: u32 = TechParam[skillId].condCount         // [+0xec]
            if N > 0u:
                usable = any(actor.CheckSkillCondition(TechParam[skillId].conds[j]) for j in 0..N-1)
    else if st == 1:                                      // Magic checks (0x455d6d..0x455d8f)
        if actor.IsSilence():                             // vtable+0xc0 (Cmd 117 / 0x75 Silence)
            usable = false

    // Shadow Sew (Cmd 123 / 0x7b, vtable+0xd0 = 0x4fb650) blocks BOTH Techniques AND Magic!
    if actor.IsShadowSewed():                             // 0x455d90..0x455dab
        usable = false

    // Effective TP Cost Gate (0x455db2..0x455dcf):
    if usable:
        effTp: i32 = actor.GetTP(skillId, 0)              // vtable+0x150 = 0x4f7190 -> CalcConsumeTP 0x4fd250
        usable = (actor.curTP >= effTp)                   // [actor+0x14] >= effTp (jge)
    return usable

// 2. Effective TP Cost (CGamePlayerStatusBase::CalcConsumeTP 0x4fd250..0x4fd3bf):
function CalcConsumeTP(actor: CGamePlayerStatusBase*, baseTP: i32, skillId: i32) -> i32:
    if baseTP <= 0: return baseTP
    tp: i32 = baseTP
    if IsTechnique(skillId):                              // in [0x738a64]
        if actor.GetEnchantCount(246 /* 0xf6 */) > 0: tp = trunc0(f32(tp) * 0.8f)
        if actor.GetEnchantCount(247 /* 0xf7 */) > 0: tp = trunc0(f32(tp) * 0.6f) // stacks sequentially!
    else if IsMagic(skillId):                             // in [0x738a58]
        if actor.GetEnchantCount(248 /* 0xf8 */) > 0: tp = trunc0(f32(tp) * 0.8f)
        if actor.GetEnchantCount(249 /* 0xf9 */) > 0: tp = trunc0(f32(tp) * 0.6f) // stacks sequentially!
    tp = max(1, tp)
    // Passive 266 (0x10a, TP Cost Reduction) inside active dungeon battle:
    if c266 = actor.GetCommand(0, 266 /* 0x10a */):
        if InDungeonBattle():
            // 0x61c040 is IEEE-754 ceil(f64): rounds reduction UP before subtracting!
            reduction: i32 = trunc0(f32(ceil(f64(f32(tp) * c266.val))))
            tp = max(1, tp - reduction)
    return tp

// 3. Battle Item & Top-Level Command Legality (CBattleMenuMain 0x455e60..0x456145, EnumerateItem 0x515f7c):
//    - Attack & Defense: always enabled (byte = 1).
//    - Skill menu enabled iff >= 1 battle-usable Technique or Magic is learned (even if currently greyed out).
//    - Item menu enabled iff party bag contains >= 1 entry where:
//        entry.IsConsumableItem() (vtable+0x14) AND ((ItemParam[id].flags30 >> 2) & 1 != 0) [bit 2 = 0x04]
//        (and item stack count > 0 in bag list).
//    - Escape enabled iff battle.canEscape != 0 ([battle+0x31] at 0x45613c).
```
- **Program Evidence:**
```asm
00455bd6  mov      eax, dword ptr [eax + 0x38]
00455be7  mov      eax, dword ptr [eax + 0xbc]
00455bfb  mov      eax, dword ptr [eax + 0xc8]
00455c61  jmp      dword ptr [eax*4 + 0x455e3c]
00455c86  shr      eax, 4
00455ca9  shr      eax, 3
00455cc5  mov      eax, dword ptr [eax + 0xb4]
00455d2b  mov      eax, dword ptr [edx + 0x12c]
00455d76  mov      eax, dword ptr [eax + 0xc0]
00455d94  mov      eax, dword ptr [eax + 0xd0]
00455dbb  call     dword ptr [eax + 0x150]
00455dc6  cmp      esi, eax
00455dc8  jge      0x455dcf
004fb652  push     0x7b
004fd291  push     0xf6
004fd2a7  mulss    xmm0, dword ptr [0x6d936c]    ; float 0.8
004fd2b3  push     0xf7
004fd2e2  push     0xf8
004fd304  push     0xf9
004fd31e  mulss    xmm0, dword ptr [0x6d934c]    ; float 0.6
004fd331  push     0x10a
004fd38f  call     0x61c040
00515fc6  mov      eax, dword ptr [eax + 0x30]
00515fc9  shr      eax, 2
```

---

### M04.16 Mid-Action Legality Downgrade on Freeze (`114`) & Silence (`117`) (`0x4208a0`)

- **Binary VA(s):** `0x4208a0..0x420b38` (`CActionPatternBase::_UpdateBeforeAttackInterrupt`), `0x5574d0..0x557527` (`IsEnemyAttackTechnique` & `IsEnemyAttackMagic`)
- **Calls:** `0x43b580` (`_IsTargetValid`), `CGameStatusBase::IsFreeze` (`vtable+0xb4` = `0x4fb580`), `CGameStatusBase::IsSilence` (`vtable+0xc0` = `0x4fb5b0`), `0x5574d0` (`IsEnemyAttackTechnique`), `0x557500` (`IsEnemyAttackMagic`), `0x428370` (erase trailing target slots)
- **CalledBy:** `CActionPatternBase::Update` (after pre-attack counter `303` resolves and before hit execution)
- **Typed Pseudocode:**
```text
// Enforces Freeze (114) and Silence (117) legality AFTER pre-attack interrupts or chant completion,
// immediately before hit execution. Rather than canceling the turn, illegal skills/enemy attacks
// are silently downgraded to a single-hit basic attack on the primary target!
// RNG calls: 0.
function EnforceMidActionAilmentLegality(this: CActionPatternBase*) -> bool:
    act = this.action
    actor = act.actor
    if this.battle != null and not this.battle._IsTargetValid(actor, true):
        return false                                      // Actor died/petrified -> abort action

    downgrade: bool = false
    // 1. Freeze (vtable+0xb4, Cmd 114 / 0x72) blocks Techniques:
    if act.actionType == 2 and IsTechnique(act.skillId) and actor.IsFreeze():
        downgrade = true
    if act.actionType == 8 and IsEnemyAttackTechnique(act.enemyAtkId) and actor.IsFreeze():
        // 0x5574d0: ([EnemyAttackParam + 0x40] >> 1) & 1
        downgrade = true

    // 2. Silence (vtable+0xc0, Cmd 117 / 0x75) blocks Magic:
    if act.actionType == 2 and IsMagic(act.skillId) and actor.IsSilence():
        downgrade = true
    if act.actionType == 8 and IsEnemyAttackMagic(act.enemyAtkId) and actor.IsSilence():
        // 0x557500: ([EnemyAttackParam + 0x40] >> 2) & 1
        downgrade = true

    if downgrade:
        if act.actionType == 2:
            act.actionType = 1                            // Downgrade to player Basic Attack
            act.skillId = -1
        else if act.actionType == 8:
            act.enemyAtkId = EnemyParam[actor.enemyId].defaultAttackId // [+0xc8]
        // Truncate target list to first target slot and force single hit:
        act.slots.erase(act.slots.begin() + 1, act.slots.end())
        act.slots[0].hitCount = 1                         // [slots[0] + 0x40] = 1

    // Final validity check on current target slot before executing _Task:
    if this.battle == null: return true
    if act.slots.empty(): return false
    return this.battle._IsTargetValid(act.slots[act.hitIdx].target, act.aliveOnly)
```
- **Program Evidence:**
```asm
00420947  call     0x43b580
00420957  cmp      dword ptr [ebx + 4], 2
00420985  mov      eax, dword ptr [eax + 0xb4]
00420998  cmp      dword ptr [esi + 4], 8
004209a1  call     0x5574d0
004209ae  mov      eax, dword ptr [eax + 0xb4]
004209eb  mov      eax, dword ptr [eax + 0xc0]
00420a07  call     0x557500
00420a18  mov      eax, dword ptr [eax + 0xc0]
00420a33  mov      dword ptr [eax + 4], 1
00420a3d  mov      dword ptr [eax + 8], 0xffffffff
00420a8b  mov      eax, dword ptr [eax + 0xc8]
00420aa9  call     0x428370
00420ab4  mov      dword ptr [eax + 0x40], 1
005574ec  mov      eax, dword ptr [eax + 0x40]
005574ef  shr      eax, 1
0055751f  shr      eax, 2
```

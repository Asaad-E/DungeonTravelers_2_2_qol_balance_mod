# M08 — Procs, Counters, Cover/Parry Break, Patterns & AfterHit (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x41a4a0..0x556160`)**
> Target binary: `backups/exe/DT22_en_unwrapped.vanilla.exe` (x86-32, image base `0x400000`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`).
> Raw effect and enchantment names are taken verbatim from `backups/CommandData.pck` and `backups/EnchantData.pck` as indexed in `docs/binary_spec/00_INVENTORY.json`.
> All integer conversions distinguish `cvttss2si` (`trunc0`, truncation toward zero) from `0x61e650` (`round_f32_to_i32`, round-to-nearest), all RNG draws distinguish `CRandom::Get` (`0x490790` on `[0x816ce8]`, returns `[0, N-1]`) from `0x505ac0` (wrapper calling `0x490790` on `[0x816ce8]`), and all comparisons record exact `<` (`jl`/`jb`) vs `<=` (`jle`/`jbe`) bounds.

---

## 1. Reactive & Pattern Execution Overview

```
CAction*::CreatePattern (M08.08) -> CActionPatternBase::CActionPatternBase (0x41f4b0)
   └── _Initialize / _BeforeAttackInterrupt setup (0x4200e0, M08.01)
         ├── Flags [this+0x79]=isPhysical (cmd 0), [this+0x7a]=isMagical (cmd 1)
         ├── Target Count splash cmd 137 (0x89) appends extra target slots
         └── Counter Whip 303 (0x12f) -> _SetupCounter (0x425930), PhaseNo = 9
               └── Phase 9 resolution (0x4208a0, M08.01):
                     ├── Attacker killed -> abort action
                     └── Attacker Frozen/Silenced -> downgrade skill to 1-hit basic attack

CActionPattern*::Update (M08.09..M08.11) -> per-hit _Task (0x420f10 or subclass override)
   ├── Physical hit negation in _Task (M08.04):
   │     ├── Knock Down 305 (0x131, long range, weapon required for player) -> zero dmg
   │     ├── Parry 180 (0xb4, physical) -> zero dmg + break roll
   │     └── Counter 250 (0xfa, range 0..1, !inCounter) -> Miss + immediate/deferred counter
   ├── Steal branch: CBattle::_Steal (0x44fde0, M08.12)
   ├── Chant Interrupt roll + X14 vanilla site 0x44d044 + Crit 33% + Crit Instakill 258 (M08.07)
   ├── _AfterHit1 (0x423560, M08.02): Devil's Whisper 320 (0x140) -> cmd 119 (0x77) on ailed target
   ├── _AfterHit2 (0x423810, M08.03): Survival Rate 254 (0xfe) clamp -> Turn Delay 54 (0x36) ATB swap
   ├── _CheckEachInterrupt (0x423cd0, M08.05):
   │     ├── Dark Aura 262 (0x106) 6-threshold debuffs (!cmd 304)
   │     ├── Slow Target 293 (0x125) -> cmd 122 (Slow) + cmd 168 (Speed -0.75)
   │     ├── Reprisal 249 (0xf9) roll (!inCounter, front row) -> [slot+0x45]
   │     └── Arcane Shield 447 (0x1bf, X13 vanilla site 0x424768) hardcoded < 15 -> [slot+0x48]
   └── _CheckAfterAttackInterrupt (0x4247e0, M08.06) -> _UpdateInterrupt (0x425890):
         ├── Cover 171 (0xab) removal roll on covered slots
         ├── Deferred Counter 250 (0xfa) -> skips 249 & 447
         ├── Reprisal 249 (0xf9) -> queues 1-hit basic attack (inCounter=1)
         ├── Arcane Shield 447 (0x1bf) -> scales skill 240 (0xf0) by lastHpDmg * cmd447.val
         └── Support Shot 260 (0x104) -> attacker ally follow-up basic attack on primary target

CBattleBase::Update Passives:
   ├── Turn-Start (0x436713..0x438700, M08.13): 311, 345 (+Phase 13), 446 (->U0008), 319 (->E1580), 357, 350, 448, 355 (+field 306)
   └── Post-Action (0x438e50..0x439285, M08.14): 291 (jump table 0x439884), 288, 289, 354
```

---

## 2. Pre-Attack Interrupt & Post-Hit Hooks (`M08.01` – `M08.04`)

### M08.01 Pre-Attack Interrupt (`0x4200e0`, `0x4208a0`): Counter Whip `303` (`0x12f`), Splash `137` (`0x89`), and Physical Stab Evasion `253` (`0xfd`)

- **Binary VA(s):** `0x4200e0..0x420466` (`CActionPatternBase::_Initialize` / pre-attack setup), `0x4208a0..0x420b38` (`CActionPatternBase::_BeforeAttackInterrupt` Phase 9 runtime), `0x44abd0..0x44ac1d` & `0x44b100..0x44b1d5` (Passive `253` / `0xfd` in `CBattle::CalcPhysicalAttack`)
- **Calls:** `0x418480` (`Action_s::CollectCommands`), `0x47e340` (`FindCommand`), `0x43ad50` (collect alive battle statuses), `0x61e650` (`round_f32_to_i32`), `0x425930` (`_SetupCounter`), `0x43b580` (`IsUnitAlive`), `0x5574d0` (is enemy tech), `0x557500` (is enemy magic), `0x428370` (erase trailing slots)
- **CalledBy:** `CActionPatternBase::CActionPatternBase` (`0x41f6b7`), `CActionPattern*::Update` Phase 9 (`0x41f05b`, `0x41f373`, `0x42abce`, `0x42af4e`, `0x42b233`, `0x42c8ee`, `0x42cbc4`, `0x42d699`, `0x42f649`), `M00.05`
- **Typed Pseudocode:**
```text
// PART A: Pattern Constructor Setup (0x4200e0..0x420466)
// RNG calls: 0 (Counter Whip 303 is 100% deterministic; no roll is performed).
function CActionPatternBase_SetupBeforeAttackInterrupt(this: CActionPatternBase*, checkCounter: bool):
    if this.action.actionType == 4: return                           // Item actions skip setup
    (actCmds, tgtCmds) = this.action.CollectCommands(this.battle, 1, 0) // 0x418480
    this.isPhysical = (FindCommand(actCmds, 0x00) != null)           // [this+0x79], cmd 0 Physical Attack
    this.isMagical  = (FindCommand(actCmds, 0x01) != null)           // [this+0x7a], cmd 1 Magical Attack

    // 1. Target Count Splash (cmd 137 / 0x89, 0x42017a..0x4202ff):
    if cmd137 = FindCommand(tgtCmds, 0x89):
        extraTargets: i32 = round_f32_to_i32(cmd137.val) - 1         // 0x61e650 - 1
        primaryTarget = this.action.targetSlots[0].target
        isPlayerPrimary: bool = (dynamic_cast<CGamePlayerStatus*>(primaryTarget) != null)
        allAlive = this.battle.GetAliveUnits(0, 1, 0, 0)             // 0x43ad50
        idx = IndexOf(allAlive, primaryTarget) + 1
        while idx < allAlive.size() and extraTargets > 0:
            cand = allAlive[idx]
            if SameClassSide(cand, isPlayerPrimary):                 // CGamePlayerStatus vs CGameEnemyStatus
                slot = TargetSlot(cand); slot.hitCount = this.action.hitCount
                this.action.targetSlots.push_back(slot)
                extraTargets -= 1
            idx += 1

    // 2. Pre-Attack Counter Whip Gate (cmd 303 / 0x12f, 0x42034b..0x420446):
    //    NOTE: Checks 303 (0x12f, 'Counter Whip'), NOT 253 (0xfd, 'Physical Stab Evasion').
    if !checkCounter or this.battle == null: return
    actorUnit = this.battle.GetUnitByStatus(this.action.actor)       // vtable+0x34
    if actorUnit.unitId in 2000..2999: return                        // 0x7d0..0xbb7 Doll excluded
    if actorUnit.unitId in 3000..3999: return                        // 0xbb8..0xf9f Summon/Guest excluded
    if this.inCounter != 0: return                                   // [this+0x11] != 0
    if this.isPhysical == 0: return                                  // [this+0x79] == 0
    if this.action.actor.HasCommand(0x133): return                   // 307 Absolute Attack blocks counter
    for slot in this.action.targetSlots:
        if slot.subHitIdx == 0:                                      // [slot+0x3c] == 0
            if cmd303 = slot.target.GetCommand(0, 0x12f):            // 303 Counter Whip
                this._SetupCounter(slot.target, cmd303)              // 0x425930 (queues 1-hit counter, inCounter=1)
                this.PatternPhaseNo = 9                              // [this+0x18] = 9
                break                                                // First matching slot only

// PART B: Phase 9 Pre-Attack Counter Resolution (0x4208a0..0x420b1e)
function CActionPatternBase_UpdateBeforeAttackInterrupt(this: CActionPatternBase*) -> bool:
    // Executes queued counter action(s) in [this+0x7c..0x80] FIFO (0x4208a9..0x420937).
    if this.interruptQueue.size() > 0: return true
    if this.battle != null and !this.battle.IsUnitAlive(this.action.actor, 1):
        this.PatternPhaseNo = this.startPhaseNo
        return false                                                 // Attacker died during preemptive counter -> abort!

    // If counter inflicted Freeze (vtable+0xb4) during a Technique or Silence (vtable+0xc0) during Magic:
    downgradeToBasic: bool = false
    if this.action.actionType == 2 and IsTechnique(this.action.skillId) and this.action.actor.IsFrozen():
        downgradeToBasic = true
    else if this.action.actionType == 8 and IsEnemyTech(this.action.enemyAttackId) and this.action.actor.IsFrozen():
        downgradeToBasic = true
    else if this.action.actionType == 2 and IsMagic(this.action.skillId) and this.action.actor.IsSilenced():
        downgradeToBasic = true
    else if this.action.actionType == 8 and IsEnemyMagic(this.action.enemyAttackId) and this.action.actor.IsSilenced():
        downgradeToBasic = true

    if downgradeToBasic:
        if this.action.actionType == 2:
            this.action.actionType = 1; this.action.skillId = -1     // Player basic attack
        else if this.action.actionType == 8:
            this.action.enemyAttackId = enemyParam.normalAttackId    // [enemyParam+0xc8]
        this.action.targetSlots.erase(begin + 1, end)                // Keep only slot 0
        this.action.targetSlots[0].hitCount = 1                      // 1 hit only
    this.PatternPhaseNo = this.startPhaseNo                          // Restore [this+0x18] = [this+0x1c]
    return IsAlive(actor) and IsAlive(currentTarget)

// PART C: Passive 253 (0xfd, 'Physical Stab Evasion') — Located in CalcPhysicalAttack (0x44abe0..0x44ac1d, 0x44b100..0x44b1d5)
// NOT in _BeforeAttackInterrupt. Evaluated during physical hit-rate calculation:
//   if Action_s::IsStabAttack(0x415710) and (cmd253 = FindCommand(tgtCmds, 0xfd)):
//       stabEvaBonus: f32 = cmd253.val                              // Added to target evasion term [ebp+0x14]
//   On miss (rawRoll >= round_f32_to_i32(finalHitRate)):
//       if rawRoll < round_f32_to_i32(hitRateWithout253): log cmd253 activation string.
```
- **Program Evidence:**
```asm
0042015b  call     0x47e340
0042016d  mov      byte ptr [ebx + 0x79], al
0042017a  mov      edx, 0x89
0042036d  sub      eax, 0x7d0
00420372  cmp      eax, 0x3e7
00420377  jbe      0x420446
0042038d  sub      eax, 0xbb8
00420392  cmp      eax, 0x3e7
00420397  jbe      0x420446
0042039d  cmp      byte ptr [ebx + 0x11], 0
004203a1  jne      0x420446
004203a7  cmp      byte ptr [ebx + 0x79], 0
004203ab  je       0x420446
004203b4  push     0x133
004203fd  push     0x12f
0042043a  call     0x425930
0042043f  mov      dword ptr [ebx + 0x18], 9
00420985  mov      eax, dword ptr [eax + 0xb4]
004209eb  mov      eax, dword ptr [eax + 0xc0]
00420a33  mov      dword ptr [eax + 4], 1
00420ab4  mov      dword ptr [eax + 0x40], 1
0044abe0  call     0x415710
0044abe9  mov      edx, 0xfd
0044b12a  mov      edx, 0xfd
```

---

### M08.02 Post-Hit Hook `_AfterHit1` (`0x423560`): Devil's Whisper `320` (`0x140`) Bonus Instakill Command `119` (`0x77`)

- **Binary VA(s):** `0x423560..0x423803` (`CActionPatternBase::_AfterHit1`)
- **Calls:** `0x429b00` (copy command vector), `0x4192c0` (append actor status commands), `0x47e340` (`FindCommand`), `0x47b220` (`CCommand` factory for `0x77`), `cmd119->vtable+0x18` (execute instakill command), `0x423810` (`_AfterHit2`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x422d32`), `M00.06`, `M00.07`
- **Typed Pseudocode:**
```text
// RNG calls: 0 directly in _AfterHit1 (cmd 119's vtable+0x18 performs its own instakill roll).
function CActionPatternBase_AfterHit1(
    this: CActionPatternBase*,
    seq: Vec<TaskResult>*,
    res: TaskResult*,
    target: CGameStatusBase*,
    tgtCmds: Vec<CCommand*>*,
    actCmds: Vec<CCommand*>*
):
    // 1. Merge skill/action actor commands with actor's active status commands (vtable+0x4c):
    mergedActCmds: Vec<CCommand*> = copy(actCmds) + this.action.actor.GetStatusList()

    // 2. Devil's Whisper (cmd 320 / 0x140): ONLY fires if target has >= 1 active ailment (vtable+0x7c):
    if cmd320 = FindCommand(mergedActCmds, 0x140):
        if target.HasAnyAilment():                                   // target->vtable+0x7c() != 0
            val: f32 = cmd320.GetValue()                             // cmd320->vtable+0x2c()
            // Instantiate CCommand ID 119 (0x77, 'Instakill') with type=0, skillId=-1, subId=-1, dur=0:
            cmd119 = CreateCommand(type=0, id=0x77, val=val, skillId=-1, subId=-1, dur=0) // 0x47b220
            cmd119.ExecuteCalc(seq, this.battleInfo, target, tgtCmds, this.action.actor)  // vtable+0x18
            lastRes: TaskResult* = &seq[seq.size() - 1]
            if lastRes.resultType == 1:                              // Instakill / bonus hit landed ([+0x2c] == 1)
                bonusDmg: i32 = lastRes.hpDamage                     // [lastRes+0x1c]
                if res.hpDamage != 0x7fffffff:
                    res.hpDamage = res.hpDamage + bonusDmg
                else:
                    res.hpDamage = bonusDmg
                lastRes.logActor = this.action.actor                 // [lastRes+0x48]
                lastRes.logTarget = target                           // [lastRes+0x4c]
                lastRes.logSource = this.action.actor                // [lastRes+0x54]
                FormatAndAppendSkillLog(lastRes, cmd320)

    // 3. Unconditionally chains to _AfterHit2 (0x4237e6):
    this._AfterHit2(seq, res, target, tgtCmds)                       // 0x423810
```
- **Program Evidence:**
```asm
004235d5  mov      edx, 0x140
004235dd  call     0x47e340
004235e2  mov      edi, eax
004235e4  test     edi, edi
004235e6  je       0x4237d7
004235f3  mov      eax, dword ptr [eax + 0x7c]
004235f6  call     eax
004235f8  test     al, al
004235fa  je       0x4237d7
00423617  mov      edx, 0x77
0042361e  call     0x47b220
0042363a  call     dword ptr [edx + 0x18]
00423663  cmp      dword ptr [edx + esi + 0x2c], 1
00423668  jne      0x4237d7
0042367b  cmp      esi, 0x7fffffff
00423681  je       0x423685
00423683  add      eax, esi
00423688  mov      dword ptr [ecx + 0x1c], eax
004237e6  call     0x423810
```

---

### M08.03 Post-Hit Hook `_AfterHit2` (`0x423810`): Survival Rate / Endure `254` (`0xfe`) and Turn Delay / Push Back `54` (`0x36`)

- **Binary VA(s):** `0x423810..0x423cbf` (`CActionPatternBase::_AfterHit2`)
- **Calls:** `0x429b00`, `0x4192c0`, `0x47e340` (`FindCommand`), `0x490790` (`CRandom::Get`), `battle->vtable+0x24` (`CBattleBase::_SortTime`), `0x5081b0` (UI/achievement trigger)
- **CalledBy:** `CActionPatternBase::_AfterHit1` (`0x4237e6`), `CActionPatternBase::_Task` (`0x422eb3`), `M00.06`, `M00.07`
- **Typed Pseudocode:**
```text
// RNG calls: up to 1 for Endure (254), and up to 1 for Turn Delay (54) (mutually exclusive via pre-Endure dmg snapshot).
function CActionPatternBase_AfterHit2(
    this: CActionPatternBase*,
    seq: Vec<TaskResult>*,
    res: TaskResult*,
    target: CGameStatusBase*,
    tgtCmds: Vec<CCommand*>*
):
    // 1. Merge incoming target commands with target's active status list (vtable+0x4c):
    mergedTgtCmds: Vec<CCommand*> = copy(tgtCmds) + target.GetStatusList()

    // Snapshot raw HP damage BEFORE Endure clamp into local `origDmg` ([ebp+0x40]):
    origDmg: i32 = (res.hpDamage == 0x7fffffff) ? 0 : res.hpDamage

    // 2. Survival Rate / Endure (cmd 254 / 0xfe, 0x42389d..0x423a18):
    //    Fires on lethal hit (CurHP - origDmg <= 0). Does NOT update `origDmg`!
    if target.GetCurHP() - origDmg <= 0:
        if cmd254 = FindCommand(mergedTgtCmds, 0xfe):
            chance: i32 = trunc0(cmd254.GetValue() * 100.0f)         // cvttss2si at 0x4238ea
            if GlobalRng.Rand(100) < chance:                         // 0x490790(0x64), strict <
                res.hpDamage = target.GetCurHP() - 1                 // Survives at 1 HP (if CurHP==1 -> 0 dmg!)
                res.logActor = target; res.logTarget = target
                res.logCmdId = cmd254.GetCommandId(); res.logSource = target
                AppendPassiveMessage(res, cmd254)

    // 3. Turn Delay / Push Back (cmd 54 / 0x36, 0x423a18..0x423ca6):
    //    Re-checks `target.GetCurHP() - origDmg > 0` using UNMODIFIED `origDmg` ([ebp+0x40]),
    //    so a lethal hit saved by Endure 254 CANNOT also trigger Push Back 54!
    if target.GetCurHP() - origDmg > 0 and origDmg > 0 and this.battle != null:
        if cmd54 = FindCommand(mergedTgtCmds, 0x36):
            // Boss knockback immunity check: EnemyParam+0x54 bit 12 (0x423a5b..0x423aa0):
            if enemy = dynamic_cast<CGameEnemyStatus*>(target):
                enemyParam = EnemyTable.Lookup(enemy.enemyId)        // [0x7389d8]
                if ((enemyParam.flags54 >> 12) & 1) != 0:
                    seq.push_back(TaskResult(target, resultType=4))  // Blocked / Immune result
                    return
            chance54: i32 = trunc0(cmd54.GetValue() * 100.0f)        // cvttss2si at 0x423b2d
            if GlobalRng.Rand(100) < chance54:                       // 0x490790(0x64), strict <
                targetUnit = this.battle.GetUnitByStatus(target)     // vtable+0x38
                pos = FindInVector(this.battle.units, targetUnit)    // [battle+0x24..0x28]
                if pos + 1 < this.battle.units.size():
                    nextUnit = this.battle.units[pos + 1]
                    swap(targetUnit.gauge, nextUnit.gauge)           // Swap [u+0x08] f32 ATB gauges!
                    this.battle.vtable_SortTime(0, 1)                // vtable+0x24(0, 1)
                    AppendTurnDelayMessage(res, target)
    // No other command IDs are checked in _AfterHit1 or _AfterHit2.
```
- **Program Evidence:**
```asm
0042388d  mov      eax, dword ptr [edi + 0x1c]
00423890  cmp      eax, 0x7fffffff
00423895  cmove    eax, ecx
0042389a  mov      dword ptr [ebp + 0x40], eax
004238a2  sub      eax, dword ptr [ebp + 0x40]
004238a5  test     eax, eax
004238a7  jg       0x423a18
004238ad  mov      edx, 0xfe
004238d8  call     0x490790
004238e2  mulss    xmm0, dword ptr [0x6d9540]    ; float 100
004238ea  cvttss2si ecx, xmm0
004238ee  cmp      eax, ecx
004238f0  jge      0x423a18
004238fd  dec      eax
00423901  mov      dword ptr [edi + 0x1c], eax
00423a22  sub      eax, ecx
00423a26  jle      0x423ca6
00423a41  mov      edx, 0x36
00423a98  mov      eax, dword ptr [eax + 0x54]
00423a9b  shr      eax, 0xc
00423a9e  test     al, 1
00423b1b  call     0x490790
00423b2d  cvttss2si ecx, xmm0
00423b31  cmp      eax, ecx
00423b33  jge      0x423ca6
00423b86  movss    xmm0, dword ptr [edi + 8]
00423b91  mov      edx, dword ptr [eax + 8]
00423b94  mov      dword ptr [edi + 8], edx
00423b97  movss    dword ptr [eax + 8], xmm0
00423b9e  call     dword ptr [eax + 0x24]
```

---

### M08.04 In-Task Physical Hit Negations (`0x4221ee..0x42265f`): Knock Down `305` (`0x131`), Parry `180` (`0xb4`), and Counter `250` (`0xfa`)

- **Binary VA(s):** `0x4221ee..0x4223a0` (Knock Down `305` / `0x131`), `0x4223b5..0x42254e` (Parry `180` / `0xb4`), `0x422553..0x42265f` (Counter `250` / `0xfa`) inside `CActionPatternBase::_Task`
- **Calls:** `0x4f4f60` (`GetEquipmentID`), `0x505ac0` (`Rand`), `0x416ea0` (check unparryable action), `0x43b5f0` (`IsDoll`), `0x43b610` (`IsSummonOrGuest`), `0x425930` (`_SetupCounter`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x420f10`), `M00.06`
- **Typed Pseudocode:**
```text
// Executed inside CActionPatternBase::_Task after physical damage calculation, before _AfterHit1:
// 1. Knock Down (cmd 305 / 0x131, 0x4221ee..0x4223a0):
//    NOT a turn-start passive; fires on incoming Long-range (attackRange == 2) physical attacks.
if this.isPhysical != 0 and this.action.attackRange == 2:            // [action+0x34] == 2 (Long)
    if cmd305 = slot.target.GetCommand(0, 0x131):
        player = dynamic_cast<CGamePlayerStatus*>(slot.target)
        if player == null or player.GetEquipmentID(0) != -1:         // Players must hold a weapon in slot 0
            if Rand(100) < trunc0(cmd305.GetValue() * 100.0f):       // 0x505ac0(0x64), strict <
                if res.hpDamage != 0x7fffffff: res.hpDamage = 0; res.hpDamageRaw = 0
                if res.tpDamage != 0x7fffffff: res.tpDamage = 0; res.tpDamageRaw = 0
                res.flag37 = 0; res.flag38 = !HasVoice(cmd305)
                // Skips Parry 180 and Counter 250 on success (jumps to 0x421f5a)!

// 2. Parry Status Barrier (cmd 180 / 0xb4, 0x4223b5..0x42254e):
if this.isPhysical != 0 and !this.action.IsUnparryable():            // 0x416ea0 == 0
    if cmd180 = slot.target.GetCommand(0, 0xb4):
        if res.hpDamage != 0x7fffffff: res.hpDamage = 0; res.hpDamageRaw = 0
        if res.tpDamage != 0x7fffffff: res.tpDamage = 0; res.tpDamageRaw = 0
        res.flag36 = 0; res.flag37 = 0; res.flag38 = 1
        // Parry break roll: Rand(100) < trunc0(cmd180.val * 100.0f) removes status 180!
        if Rand(100) < trunc0(cmd180.GetValue() * 100.0f):           // 0x505ac0(0x64), strict <
            QueueStatusRemove(postSeq, slot.target, cmdId=0xb4, resultType=2)
        // Jumps to 0x421f5d (skips Counter 250)!

// 3. Counter / Counter-Evade (cmd 250 / 0xfa, 0x422553..0x42265f):
//    Can trigger on any hit reaching 0x422553 (physical or non-physical if range in {0, 1}).
if this.inCounter == 0 and this.action.attackRange in {0, 1}:        // Close (0) or Mid (1)
    if this.action.actor != slot.target and !this.action.actor.HasCommand(0x133): // !307 Absolute Attack
        if cmd250 = slot.target.GetCommand(0, 0xfa):
            if Rand(100) < trunc0(cmd250.GetValue() * 100.0f):       // 0x505ac0(0x64), strict <
                res.hpDamage = 0x7fffffff; res.hpDamageRaw = 0x7fffffff
                res.tpDamage = 0x7fffffff; res.tpDamageRaw = 0x7fffffff
                res.resultType = 3                                   // Evaded / Miss!
                if !this.battle.IsDoll(actor) and !this.battle.IsSummonOrGuest(actor): // 0x43b5f0, 0x43b610
                    if this.flag10 != 0:                             // Sequential patterns A/B/C/T0105/M0140
                        this._SetupCounter(slot.target, cmd250)      // Immediate queue -> aborts remaining hits!
                    else:                                            // Simultaneous/AoE patterns D/E/F/G/M0124
                        slot.parryCounterPending = 1u8               // [slot+0x46] = 1 (deferred to M08.06)
```
- **Program Evidence:**
```asm
004221f8  mov      eax, dword ptr [esi + 0xc]
004221fb  cmp      dword ptr [eax + 0x34], 2
00422207  push     0x131
0042223e  call     0x4f4f60
00422243  cmp      eax, -1
0042225e  call     0x505ac0
00422272  cvttss2si esi, xmm0
00422285  cmp      edi, esi
00422287  jge      0x4223b2
00422296  mov      dword ptr [ebx + 0x1c], 0
004223c2  call     0x416ea0
004223d4  push     0xb4
004224b3  call     0x505ac0
004224da  cmp      edi, esi
004224dc  jge      0x42253a
00422559  cmp      byte ptr [eax + 0x11], 0
00422566  mov      eax, dword ptr [ecx + 0x34]
00422582  push     0x133
00422596  push     0xfa
004225be  call     0x505ac0
004225e5  cmp      edi, esi
004225e7  jge      0x42265f
00422608  mov      dword ptr [ebx + 0x2c], 3
0042261b  call     0x43b5f0
00422630  call     0x43b610
00422640  cmp      byte ptr [esi + 0x10], al
0042264c  call     0x425930
00422656  mov      byte ptr [ebx + 0x46], 1
```

---

## 3. Per-Hit & Post-Attack Reactive Chains + Chant Interrupt (`M08.05` – `M08.07`)

### M08.05 Per-Hit Reactive Chain `_CheckEachInterrupt` (`0x423cd0`): Dark Aura `262`, Slow Target `293`, Reprisal `249`, and Arcane Shield `447` (`X13` Site `0x424768`)

- **Binary VA(s):** `0x423cd0..0x42478e` (`CActionPatternBase::_CheckEachInterrupt`); vanilla `X13` byte at `0x424768` (`cmp eax, 0xf`)
- **Calls:** `0x47b220` / `0x47e260` (create debuff commands), `actor->vtable+0x54` (`AddStatus`), `0x490790` (`CRandom::Get`), `0x47e500` (`CCommand::Execute`)
- **CalledBy:** `CActionPatternA..G/E1580/M0140/T0105::Update` (`0x41ef8e`, `0x41f29f`, `0x42aaa8`, `0x42ad48`, `0x42b11c`, `0x42c077`, `0x42c7ea`, `0x42caba`, `0x42d596`, `0x42f546`), `M00.07`
- **Typed Pseudocode:**
```text
// Returns true iff interruptQueue [this+0x7c..0x80] is non-empty (triggers immediate abort of remaining multi-hits
// in sequential patterns A/B/C when Counter 250 queued _SetupCounter inside _Task).
function CActionPatternBase_CheckEachInterrupt(this: CActionPatternBase*) -> bool:
    if this.battle == null: return (this.interruptQueue.size() > 0)
    actorUnit = this.battle.GetUnitByStatus(this.action.actor)
    if actorUnit.unitId in 2000..2999: return (this.interruptQueue.size() > 0) // Doll excluded
    if actorUnit.unitId in 3000..3999: return (this.interruptQueue.size() > 0) // Summon/Guest excluded

    slot = &this.action.targetSlots[this.action.curHitIdx]
    range: i32 = this.action.attackRange                             // [action+0x34]

    // Shared Contact Gate for Dark Aura 262 & Slow Target 293 (0x423d50..0x423d72):
    // Requires hitLanded ([this+0x70] != 0), Close range (range == 0), actionType != 0, and actor != target.
    // NOTE: Does NOT check !this.inCounter ([this+0x11])! Both 262 and 293 can proc on counterattacks!
    if this.hitLanded != 0 and range == 0 and this.action.actionType != 0 and this.action.actor != slot.target:
        // 1. Dark Aura (cmd 262 / 0x106, 0x423d78..0x424314):
        //    0 RNG calls. Blocked by actor passive 304 (0x130, 'Anti-Dark Aura') or action.flag49 != 0.
        if !this.action.actor.HasCommand(0x130) and this.action.flag49 == 0:
            if cmd262 = slot.target.GetCommand(0, 0x106):
                lvl: f32 = cmd262.GetValue()
                // Applies 4-turn -10% (-0.1f) stat debuffs cumulatively via actor->vtable+0x54 (AddStatus):
                if lvl >= 1.0f: actor.AddStatus(MakeCmd(0x2d, -0.1f, dur=4)) // 45 DEX
                if lvl >= 2.0f: actor.AddStatus(MakeCmd(0x2c, -0.1f, dur=4)) // 44 RES
                if lvl >= 3.0f: actor.AddStatus(MakeCmd(0x2b, -0.1f, dur=4)) // 43 INT
                if lvl >= 4.0f: actor.AddStatus(MakeCmd(0x2a, -0.1f, dur=4)) // 42 DEF
                if lvl >= 5.0f: actor.AddStatus(MakeCmd(0x29, -0.1f, dur=4)) // 41 ATK
                if lvl >= 6.0f: actor.AddStatus(MakeCmd(0x2e, -0.1f, dur=4)) // 46 AGI

        // 2. Slow Target (cmd 293 / 0x125, 0x424317..0x424679):
        //    Blocked only by action.flag49 != 0 (NOT blocked by 304).
        if cmd293 = slot.target.GetCommand(0, 0x125):
            if this.action.flag49 == 0:
                if GlobalRng.Rand(100) < trunc0(cmd293.GetValue() * 100.0f): // 0x490790(0x64), strict <
                    // Creates & executes cmd 122 (0x7a Slow, val=1.0f, dur=5) AND cmd 168 (0xa8 Speed, val=-0.75f, dur=5):
                    seq = []
                    MakeCmd(0x7a,  1.0f, dur=5).ExecuteCalc(seq, battleInfo, actor, actor.statuses, slot.target)
                    MakeCmd(0xa8, -0.75f, dur=5).ExecuteCalc(seq, battleInfo, actor, actor.statuses, slot.target)
                    CCommand_Execute(seq, -1, this.battleInfo)       // 0x47e500

    // 3. Reprisal / Physical Counter Roll (cmd 249 / 0xf9, 0x42467f..0x424714):
    if this.inCounter == 0 and this.isPhysical != 0 and this.hitLanded != 0 and range in {0, 1}:
        tgtUnit = this.battle.GetUnitByStatus(slot.target)
        if tgtUnit != null and tgtUnit.isFrontRow != 0:              // [tgtUnit+0x79] != 0 (Front Row ONLY!)
            if this.action.actor != slot.target and !this.action.actor.HasCommand(0x133): // !307
                if cmd249 = slot.target.GetCommand(0, 0xf9):
                    // Overwrites [slot+0x45] on each hit (last hit wins on multi-hit to same slot!):
                    slot.reprisalTriggered = (GlobalRng.Rand(100) < trunc0(cmd249.GetValue() * 100.0f))

    // 4. Arcane Shield Reflection Roll (cmd 447 / 0x1bf, 0x424714..0x424771) — VANILLA X13 SITE:
    //    [this+0x78] == 0 means non-physical (magical) hit; lastHpDmg ([this+0x74]) must be non-zero & != 0x7fffffff.
    if this.inCounter == 0 and this.lastHpDmg != 0x7fffffff and this.lastHpDmg != 0 and this.hitWasPhysical == 0:
        if this.action.actor != slot.target and !this.action.actor.HasCommand(0x133): // !307
            if slot.target.GetCommand(0, 0x1bf) != null:             // Does NOT read cmd447.val for proc rate!
                // VANILLA X13 BYTE AT 0x424768: immediate 0x0f (15 = 15% flat proc chance)
                if GlobalRng.Rand(100) < 15:                         // 0x490790(0x64), cmp eax, 0xf
                    slot.magicReflectDmg = this.lastHpDmg            // [slot+0x48] = [this+0x74]

    return (this.interruptQueue.size() > 0)
```
- **Program Evidence:**
```asm
00423d50  cmp      byte ptr [ebx + 0x70], 0
00423d7a  push     0x130
00423d8f  cmp      byte ptr [eax + 0x49], 0
00423d9b  push     0x106
00423df9  comiss   xmm0, dword ptr [0x6d938c]    ; float 1
00423e42  movss    xmm2, dword ptr [0x6d9780]    ; float -0.1
00423e4a  mov      edx, 0x2d
00423e97  comiss   xmm0, dword ptr [0x6d93f8]    ; float 2
00423f35  comiss   xmm0, dword ptr [0x6d9408]    ; float 3
00423fd3  comiss   xmm0, dword ptr [0x6d9430]    ; float 4
00424071  comiss   xmm0, dword ptr [0x6d9434]    ; float 5
0042410f  comiss   xmm0, dword ptr [0x6d9438]    ; float 6
00424319  push     0x125
00424353  call     0x490790
004244dc  mov      edx, 0x7a
00424566  movss    xmm2, dword ptr [0x6d9794]    ; float -0.75
0042456e  mov      edx, 0xa8
0042467f  cmp      byte ptr [ebx + 0x11], 0
004246b0  mov      al, byte ptr [eax + 0x79]
004246d2  push     0xf9
0042470e  setl     al
00424711  mov      byte ptr [esi + 0x45], al
00424728  cmp      byte ptr [ebx + 0x78], 0
00424749  push     0x1bf
00424761  call     0x490790
00424766  cmp      eax, 0xf
00424769  jge      0x424771
0042476e  mov      dword ptr [esi + 0x48], eax
```

---

### M08.06 Post-Attack Reactive Chain `_CheckAfterAttackInterrupt` (`0x4247e0`), `_SetupCounter` (`0x425930`), and `_UpdateInterrupt` (`0x425890`)

- **Binary VA(s):** `0x4247e0..0x42588f` (`CActionPatternBase::_CheckAfterAttackInterrupt`), `0x425890..0x425928` (`CActionPatternBase::_UpdateInterrupt`), `0x425930..0x425bd7` (`CActionPatternBase::_SetupCounter`)
- **Calls:** `0x490790` (`CRandom::Get`), `0x47e500` (`CCommand::Execute`), `0x425930` (`_SetupCounter`), `0x414e20` (`CActionAttack`), `0x419ad0` (`CActionEnemyAttack`), `0x41d480` (`CActionSkill`), `0x56d860` (set skill 240 reflected power), `0x43af10` (get alive player units), `0x43b410` (get alive summon/NPC allies), `0x43b1d0` (get alive enemy units)
- **CalledBy:** `CActionPatternA..G/M0140/T0105::Update` (`0x41eed3`, `0x41f1e3`, `0x42a93c`, `0x42ae4c`, `0x42af32`, `0x42b060`, `0x42c771`, `0x42caf1`, `0x42d4c0`, `0x42f470`), `M00.07`
- **Typed Pseudocode:**
```text
function IsUnitAliveInBattle(battle: CBattleBase*, status: CGameStatusBase*) -> bool:
    // Inline pattern used at 0x42481a..0x4248a0, 0x42492c..0x424a70, 0x424b87..0x424c32, 0x424d68..0x424e15, 0x425114..0x4251c2:
    // Finds status in battle.units; if player-side ([u+0x78] != 0), requires status->vtable+0xe8() (IsAlive) == true.
    // (Dead enemies are already removed from battle.units; dead players remain with IsAlive()==false.)

function CActionPatternBase_CheckAfterAttackInterrupt(this: CActionPatternBase*) -> bool:
    queuedAny: bool = false                                          // [ebp-0xd] = 0
    if this.battle == null: return false
    if !IsUnitAliveInBattle(this.battle, this.action.actor): return false
    actorUnit = this.battle.GetUnitByStatus(this.action.actor)
    if actorUnit.unitId in 2000..2999: return false                  // Doll attacker cannot be countered
    if this.inCounter != 0: return false                             // [this+0x11] != 0 blocks counter-of-counter!

    isSummonOrGuest: bool = (actorUnit.unitId in 3000..3999)         // 0xbb8..0xf9f
    if !isSummonOrGuest:
        // STAGE 1 — Cover Break / Removal Roll (cmd 171 / 0xab, 0x4248ed..0x424b4b):
        // Runs on EVERY alive covered slot (does NOT break after first, does NOT set queuedAny).
        for slot in this.action.targetSlots:
            if IsUnitAliveInBattle(this.battle, slot.target) and slot.wasCovered != 0: // [slot+0x44] != 0
                if cmd171 = slot.target.GetCommand(0, 0xab):
                    if GlobalRng.Rand(100) < trunc0(cmd171.GetValue() * 100.0f): // 0x490790(0x64)
                        // Executes resultType=2 (Status Remove) for cmdId=171 via CCommand::Execute (0x47e500):
                        CCommand_Execute([TaskResult(slot.target, cmdId=0xab, resultType=2)], -1, this.battleInfo)

        // STAGE 2 — Deferred Counter / Parry (cmd 250 / 0xfa, 0x424b4b..0x424c42):
        // Scans for FIRST alive slot with [slot+0x46] != 0 and cmd 250.
        // MUTUAL EXCLUSION: On match, queues _SetupCounter and JUMPS TO STAGE 5 (0x424c42),
        // SKIPPING Stage 3 (Reprisal 249) and Stage 4 (Arcane Shield 447)!
        parryFired: bool = false
        for slot in this.action.targetSlots:
            if IsUnitAliveInBattle(this.battle, slot.target) and slot.parryCounterPending != 0: // [slot+0x46]
                if cmd250 = slot.target.GetCommand(0, 0xfa):
                    this._SetupCounter(slot.target, cmd250)          // 0x425930 (sets inCounter=1)
                    queuedAny = true; parryFired = true
                    break

        if !parryFired:
            // STAGE 3 — Reprisal Physical Counter (cmd 249 / 0xf9, 0x424d2c..0x4250d4):
            // Scans for FIRST alive slot with [slot+0x45] != 0 and cmd 249.
            // Falls through to Stage 4 (Arcane Shield 447) even when a Reprisal is queued!
            for slot in this.action.targetSlots:
                if IsUnitAliveInBattle(this.battle, slot.target) and slot.reprisalTriggered != 0: // [slot+0x45]
                    if cmd249 = slot.target.GetCommand(0, 0xf9):
                        // Builds 1-hit basic attack by slot.target targeting this.action.actor (inCounter=1):
                        //   Player -> CActionAttack (vtable 0x6c94a0, actionType=1)
                        //   Enemy  -> CActionEnemyAttack (0x419ad0, actionType=8, enemyParam+0xc8)
                        this.interruptQueue.push_back(InterruptEntry(slot.target, cmd249, action, flag10=0))
                        queuedAny = true
                        break                                        // At most ONE Reprisal per attack

            // STAGE 4 — Arcane Shield Reflection (cmd 447 / 0x1bf, 0x4250d4..0x42537c):
            // Scans for FIRST alive slot with [slot+0x48] != 0x7fffffff and cmd 447.
            for slot in this.action.targetSlots:
                if IsUnitAliveInBattle(this.battle, slot.target) and slot.magicReflectDmg != 0x7fffffff:
                    if cmd447 = slot.target.GetCommand(0, 0x1bf):
                        reflectedPower: f32 = f32(slot.magicReflectDmg) * cmd447.GetValue() // fmul at 0x4251f8
                        SetSkill240Power(reflectedPower)             // 0x56d860 (mutates skill 240 / 0xf0 power!)
                        // Builds 1-hit CActionSkill (0x41d480) for player-side slot.target:
                        //   actionType = 2, skillId = 240 (0xf0), [act+0x44] = 1, [act+0x49] = 1, inCounter = 1
                        //   targets this.action.actor
                        this.interruptQueue.push_back(InterruptEntry(slot.target, cmd447, skill240Action, flag10=1))
                        queuedAny = true
                        break                                        // At most ONE Arcane Shield per attack

    // STAGE 5 — Support Shot (cmd 260 / 0x104, 0x424c42..0x424d27 & 0x425381..0x425821):
    // Runs even when attacker is a Summon/Guest! Requires basic attack (actionType == 1) and
    // primaryTarget ([this.action+0x2c]) still alive in battle.units.
    if this.action.actionType == 1 and IsUnitAliveInBattle(this.battle, this.action.primaryTarget):
        if dynamic_cast<CGamePlayerStatus*>(this.action.actor) != null:
            allies = this.battle.GetAlivePlayerUnits(1, 0, 1) + this.battle.GetAliveSummonNpcUnits() // 0x43af10 + 0x43b410
        else:
            allies = this.battle.GetAliveEnemyUnits(1, 0)            // 0x43b1d0
        for ally in allies:
            if ally == this.action.actor: continue                   // Attacker cannot Support Shot itself
            if cmd260 = ally.GetCommand(0, 0x104):                   // 260 Support Shot
                if GlobalRng.Rand(100) < trunc0(cmd260.GetValue() * 100.0f): // 0x490790(0x64), strict <
                    // Builds 1-hit basic attack by `ally` targeting `this.action.primaryTarget` (inCounter=1):
                    //   Player party member -> CActionAttack (actionType=1)
                    //   NPC (0x707d34)      -> CActionEnemyAttack (actionType=8, npcParam+0x54)
                    //   Summon (0x707d5c)   -> CActionEnemyAttack (actionType=8, summonParam+0x58)
                    //   Enemy (0x707dfc)    -> CActionEnemyAttack (actionType=8, enemyParam+0xc8)
                    this.interruptQueue.push_back(InterruptEntry(ally, cmd260, followUpAction, flag10=0))
                    queuedAny = true
                    break                                            // At most ONE Support Shot per basic attack

    return queuedAny

// _SetupCounter (0x425930..0x425bd7):
//   Constructs a 1-hit basic attack by `counterer` targeting `this.action.actor` with `inCounter = 1`
//   (CActionAttack 0x414e20 for player; CActionEnemyAttack 0x419ad0 using enemyParam+0xc8 for enemy)
//   and appends it to `this.interruptQueue` ([this+0x7c..0x80]).
// _UpdateInterrupt (0x425890..0x425928):
//   Drains `this.interruptQueue` FIFO: runs `entry.action->Update()` until false, deletes entry, shifts queue
//   left by 0x14 bytes, returns `(queue.begin != queue.end)`.
```
- **Program Evidence:**
```asm
004248aa  cmp      byte ptr [edi + 0x11], al
004248ad  jne      0x42547a
0042496e  cmp      byte ptr [eax + 0x44], 0
0042497a  push     0xab
004249a6  call     0x490790
00424a2b  mov      dword ptr [ebp - 0x88], 2
00424a87  call     0x47e500
00424bc6  cmp      byte ptr [esi + 0x46], 0
00424bce  push     0xfa
00424c39  call     0x425930
00424c42  cmp      dword ptr [ebp - 0x2c], 1
00424da6  cmp      byte ptr [esi + 0x45], 0
00424dae  push     0xf9
0042514c  cmp      dword ptr [esi + 0x48], 0x7fffffff
00425157  push     0x1bf
004251f8  fmul     dword ptr [ebp - 0x20]
00425203  call     0x56d860
00425262  mov      dword ptr [eax + 8], 0xf0
004252c8  mov      byte ptr [eax + 0x49], 1
0042531b  call     0x41d480
0042540a  push     0x104
00425431  call     0x490790
00425449  jl       0x42548d
004258de  call     eax
00425aa3  call     0x414e20
00425b54  call     0x419ad0
```

---

### M08.07 Chant Interruption Roll, Vanilla `X14` Site (`0x44d044`), Crit `+33%` Interrupt, and Crit Instakill `258` (`0x102`)

- **Binary VA(s):** `0x44cfad..0x44d336` (Physical Chant Interrupt, vanilla `X14` site at `0x44d042..0x44d04b` / patched bytes `0x44d044..0x44d04c`, Crit `+33%`, and Passive `258` / `0x102` in `CBattle::CalcPhysicalAttack`), `0x44f12a..0x44f14a` (Magical Crit `+33%` Interrupt in `CBattle::CalcMagicalAttack`)
- **Calls:** `0x47e400` (`SumCommandValues`), `target->vtable+0x28` (`GetMaxHP`), `target->vtable+0xf0` (`GetEnchantCount`), `0x505ac0` (`Rand`, physical path), `0x490790` (`CRandom::Get`, magical path), `0x47b220` (`CCommand` factory for `0x77`)
- **CalledBy:** `CBattle::CalcPhysicalAttack` (`0x44a850`), `CBattle::CalcMagicalAttack` (`0x44d370`), `M00.06`
- **Typed Pseudocode:**
```text
// PART A: Physical Chant Interruption & Crit Instakill (0x44cfad..0x44d336)
// RNG calls: 1 for base interrupt roll + 1 if res.isCrit (33% roll) [+ cmd119 roll if crit & passive 258].
function CalcPhysical_InterruptAndCritInstakill(
    target: CGameStatusBase*,
    dmg: i32,
    res: TaskResult*,
    actCmds: Vec<CCommand*>*,
    tgtCmds: Vec<CCommand*>*
):
    // 1. Base Damage-Ratio Interruption Rate (0x44cfad..0x44d065):
    mod264: f32 = SumCommandValues(tgtCmds, 0x108)                   // 264 Magic Interruption Modifier
    // VANILLA X14 SITE (0x44d042..0x44d04b; bytes 0x44d044..0x44d04c = 58 c1 f3 0f 10 4d 0c f3):
    // Vanilla executes `addss xmm0, xmm1`, ADDING (mod264 + 1.0f) to (MaxHP * 1.5f) instead of multiplying!
    denom: f32 = f32(target.GetMaxHP()) * 1.5f + (mod264 + 1.0f)     // addss at 0x44d042!
    baseRate: f32 = clamp(f32(dmg) / denom, 0.0f, 0.95f)             // maxss 0.0f, minss 0.95f

    // 2. Equipment Enchantment Interruption Modifiers (0x44d079..0x44d1d9):
    //    57 (0x39 GrandDOWN): +0.10f | 58 (0x3a DOWN): +0.06f | 59 (0x3b MiniDOWN): +0.03f
    //    60 (0x3c UP):        -0.06f (SUBTRACTED at 0x44d15d!) | 61 (0x3d MegaDOWN): +0.20f
    enchRes: f32 = 0.10f * f32(target.GetEnchantCount(0x39))
                 + 0.06f * f32(target.GetEnchantCount(0x3a))
                 + 0.03f * f32(target.GetEnchantCount(0x3b))
                 - 0.06f * f32(target.GetEnchantCount(0x3c))         // subss xmm1, xmm0 at 0x44d15d
                 + 0.20f * f32(target.GetEnchantCount(0x3d))
    finalRate: f32 = clamp(baseRate - enchRes, 0.0f, 0.95f)

    // 3. Primary Interrupt Roll (0x44d1f3..0x44d220):
    res.isInterrupted = (Rand(100) < trunc0(finalRate * 100.0f)) ? 1u8 : 0u8 // 0x505ac0(0x64), strict <

    // 4. Independent Critical Hit +33% Interrupt Roll (0x44d223..0x44d24a):
    if res.isCrit != 0:                                              // [res+0x31] != 0
        if Rand(100) < 33:                                           // 0x505ac0(0x64), cmp eax, 0x21
            res.isInterrupted |= 1u8                                 // [res+0x33] |= 1

    // 5. Passive 258 (0x102, 'Instakill' on Critical Hit, 0x44d266..0x44d336):
    if res.isCrit != 0:
        if cmd258 = FindCommand(actCmds, 0x102):
            cmd119 = CreateCommand(type=0, id=0x77, val=cmd258.GetValue(), skillId=-1, subId=-1, dur=0)
            cmd119.ExecuteCalc(seq, battleInfo, target, tgtCmds, actor) // vtable+0x18

// PART B: Magical Chant Interruption (0x44f12a..0x44f14a)
// Magical hits NEVER perform the physical damage-ratio interrupt roll.
// ONLY Magic Critical hits (from Passive 301 / 0x12d 20% roll) roll 33% interrupt:
function CalcMagical_CritInterrupt(res: TaskResult*):
    if res.isCrit != 0:                                              // [res+0x31] != 0
        if GlobalRng.Rand(100) < 33:                                 // 0x490790(0x64), cmp eax, 0x21
            res.isInterrupted = 1u8                                  // [res+0x33] = 1
```
- **Program Evidence:**
```asm
0044cfad  mov      edx, 0x108
0044cfb5  call     0x47e400
0044d02b  addss    xmm1, dword ptr [0x6d938c]    ; float 1
0044d03a  mulss    xmm0, dword ptr [0x6d93bc]    ; float 1.5
0044d042  addss    xmm0, xmm1
0044d046  movss    xmm1, dword ptr [ebp + 0xc]
0044d04b  divss    xmm1, xmm0
0044d056  movss    xmm1, dword ptr [0x6d9384]    ; float 0.95
0044d081  push     0x39
0044d0a8  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
0044d0e2  mulss    xmm0, dword ptr [0x6d92f0]    ; float 0.06
0044d119  mulss    xmm0, dword ptr [0x6d92e4]    ; float 0.03
0044d155  mulss    xmm0, dword ptr [0x6d92f0]    ; float 0.06
0044d15d  subss    xmm1, xmm0
0044d18c  mulss    xmm0, dword ptr [0x6d9324]    ; float 0.2
0044d1f8  call     0x505ac0
0044d20c  cvttss2si ecx, xmm0
0044d228  cmp      byte ptr [eax + 0x31], 0
0044d233  call     0x505ac0
0044d238  cmp      eax, 0x21
0044d246  or       byte ptr [eax + 0x33], 1
0044d279  mov      edx, 0x102
0044d2a8  mov      edx, 0x77
0044f12c  cmp      byte ptr [eax + 0x31], 0
0044f13a  call     0x490790
0044f13f  cmp      eax, 0x21
0044f146  mov      byte ptr [eax + 0x33], 1
```

---

## 4. Complete Action Pattern Dispatch & All 26 `CActionPattern*` Subclasses (`M08.08` – `M08.12`)

### M08.08 Action Pattern Factories: `CActionSkill::_CreatePattern` (`0x41e060`, Cases `0..15`) & `CActionEnemyAttack::_CreatePattern` (`0x41a4a0`, Cases `0..17`)

- **Binary VA(s):** `0x41e060..0x41e63c` (`CActionSkill::_CreatePattern`, jump table `0x41e5fc`), `0x41a4a0..0x41a84a` (`CActionEnemyAttack::_CreatePattern`, indirect byte table `0x41a838` + jump table `0x41a814`)
- **Calls:** `0x56d450` (`GetSkillPatternType`), `0x41f4b0` (`CActionPatternBase::ctor`), `0x42c940` (`CActionPatternG::ctor`), `0x42d1d0` (`CActionPatternM0124::ctor`), `0x42db00` (`CActionPatternRandomSkillBase::ctor`), `0x505ad0` (`WeightedRand`), `0x5b0480` (assert)
- **CalledBy:** `CActionSkill::Update` (`0x41d480`), `CActionEnemyAttack::Update` (`0x419ad0`), `M00.04`
- **Typed Pseudocode:**
```text
// Base constructor signature:
//   CActionPatternBase::ctor(battleInfo, ownerAction, action_s, flag10: bool, inCounter: bool, startPhase: i32, checkBeforeInterrupt: bool)
//   flag10 ([this+0x10]): 1 = sequential single-target (Parry 250 queues counter immediately & aborts multi-hit)
//                         0 = simultaneous/AoE (Parry 250 sets [slot+0x46]=1 and defers to _CheckAfterAttackInterrupt)

function CActionSkill_CreatePattern(this: CActionSkill*):
    patternType: u32 = GetSkillPatternType(this.action.skillId)      // 0x56d450
    if patternType > 15: Assert("PatternType error.")                // 0x41e5e0
    switch patternType:                                              // Jump table 0x41e5fc
        case 0:  return new CActionPatternA(flag10=1, inCounter=this.inCounter, startPhase=2, checkPre=1)
        case 1:  return new CActionPatternB(flag10=1, inCounter=this.inCounter, startPhase=2, checkPre=1)
        case 2:  return new CActionPatternC(flag10=1, inCounter=this.inCounter, startPhase=2, checkPre=1)
        case 3:  return new CActionPatternD(flag10=0, inCounter=this.inCounter, startPhase=4, checkPre=1)
        case 4:  return new CActionPatternE(flag10=0, inCounter=this.inCounter, startPhase=2, checkPre=1)
        case 5:  return new CActionPatternF(flag10=0, inCounter=this.inCounter, startPhase=4, checkPre=1)
        case 6:  return new CActionPatternG(flag10=0, inCounter=this.inCounter, startPhase=4, checkPre=1) // 0x42c940
        case 7:  return new CActionPatternT0067(flag10=1, inCounter=0, startPhase=6, checkPre=0)
        case 8:  return new CActionPatternT0080(flag10=1, inCounter=0, startPhase=6, checkPre=0)
        case 9:  return new CActionPatternT0105(flag10=1, inCounter=this.inCounter, startPhase=2, checkPre=1)
        case 10: return new CActionPatternT0111(table1=0x64f8c0, table2=0x64f930, count=9)  // 0x42db00
        case 11: return new CActionPatternT0118(table1=0x64fa28, table2=0x64f9a0, count=11) // + Genzimaru swap 0x79->0x7d!
        case 12: return new CActionPatternT0130(table1=0x64fb50, table2=0x64fab0, count=13) // 0x42db00
        case 13: return new CActionPatternM0124(flag10=0, inCounter=this.inCounter, startPhase=4, checkPre=1) // 0x42d1d0
        case 14: return new CActionPatternM0129(table1=0x64f458, table2=0x64f440, count=2)  // 0x42db00
        case 15: return new CActionPatternM0140(flag10=1, inCounter=this.inCounter, startPhase=2, checkPre=1)

function CActionEnemyAttack_CreatePattern(this: CActionEnemyAttack*):
    param = EnemyAttackTable.Lookup(this.action.enemyAttackId)       // [0x7389d4]
    patternType: u32 = param.patternType                             // [param+0xa8]
    if patternType > 17: Assert("PatternType error.")                // 0x41a7fa
    switch patternType:                                              // Indirect table 0x41a838 -> 0x41a814
        case 0..6: same constructors as CActionSkill cases 0..6 (A, B, C, D, E, F, G)
        case 7..16: Assert("PatternType error.")                     // Mapped to index 8 -> 0x41a7fa
        case 17: return new CActionPatternE2520(table=0x64f1c0, count=13) // WeightedRand 0x505ad0, vtable 0x6c97f0
```

| Case ID | `CActionSkill` (`0x41e060`) | `CActionEnemyAttack` (`0x41a4a0`) | `flag10` | `startPhase` | `checkPre` | Classification |
|---:|---|---|---:|---:|---:|---|
| 0 | `CActionPatternA` (`0x6c968c`) | `CActionPatternA` (`0x6c968c`) | 1 | 2 | 1 | Sequential single-target (`_SelectTarget` + `_Cover`, immediate Parry abort) |
| 1 | `CActionPatternB` (`0x6c96ac`) | `CActionPatternB` (`0x6c96ac`) | 1 | 2 | 1 | Visual-only over `A` (identical combat call set) |
| 2 | `CActionPatternC` (`0x6c9730`) | `CActionPatternC` (`0x6c9730`) | 1 | 2 | 1 | Visual-only over `A` (identical combat call set) |
| 3 | `CActionPatternD` (`0x6c9750`) | `CActionPatternD` (`0x6c9750`) | 0 | 4 | 1 | Simultaneous/AoE wave (NO `_SelectTarget`, NO pre-calc `_Cover`, deferred Parry) |
| 4 | `CActionPatternE` (`0x6c9770`) | `CActionPatternE` (`0x6c9770`) | 0 | 2 | 1 | Multi-target with pre-calc `_Cover`, NO `_SelectTarget`, deferred Parry |
| 5 | `CActionPatternF` (`0x6c981c`) | `CActionPatternF` (`0x6c981c`) | 0 | 4 | 1 | Simultaneous/AoE wave (visual-only over `D`: NO `_SelectTarget`, NO pre-calc `_Cover`) |
| 6 | `CActionPatternG` (`0x6c983c`) | `CActionPatternG` (`0x6c983c`) | 0 | 4 | 1 | Wave loop with `_SelectTarget` on primary death, NO pre-calc `_Cover`, deferred Parry |
| 7 | `CActionPatternT0067` (`0x6c9940`) | Assert `0x41a7fa` | 1 | 6 | 0 | Out-of-combat utility (Item Identify, cmd `20` / `0x14`) |
| 8 | `CActionPatternT0080` (`0x6c9960`) | Assert `0x41a7fa` | 1 | 6 | 0 | Out-of-combat utility (Dungeon Chest Counter) |
| 9 | `CActionPatternT0105` (`0x6c99a0`) | Assert `0x41a7fa` | 1 | 2 | 1 | Sequential with `_Cover`, NO `_SelectTarget`, immediate Parry abort |
| 10 | `CActionPatternT0111` (`0x6c99c0`) | Assert `0x41a7fa` | 1 | 0 | 0 | **Combat-Distinct:** Random Skill (9 moves, `315` alt table) |
| 11 | `CActionPatternT0118` (`0x6c99ec`) | Assert `0x41a7fa` | 1 | 0 | 0 | **Combat-Distinct:** Random Skill (11 moves, `315` alt table, Genzimaru `121->125` swap) |
| 12 | `CActionPatternT0130` (`0x6c9a18`) | Assert `0x41a7fa` | 1 | 0 | 0 | **Combat-Distinct:** Random Skill (13 moves, `315` alt table) |
| 13 | `CActionPatternM0124` (`0x6c987c`) | Assert `0x41a7fa` | 0 | 4 | 1 | **Combat-Distinct:** Rotates caster self-slot to end of `targetSlots`, then runs `D::Update` |
| 14 | `CActionPatternM0129` (`0x6c989c`) | Assert `0x41a7fa` | 1 | 0 | 0 | **Combat-Distinct:** Random Skill (2 moves `141/142`, `315` alt table, preserves target slots) |
| 15 | `CActionPatternM0140` (`0x6c98c8`) | Assert `0x41a7fa` | 1 | 2 | 1 | Sequential with `_Cover`, NO `_SelectTarget`, immediate Parry abort (same combat calls as `T0105`) |
| 16 | — (OOB) | Assert `0x41a7fa` | — | — | — | Invalid / Assert |
| 17 | — (OOB) | `CActionPatternE2520` (`0x6c97f0`) | 1 | 0 | 0 | **Combat-Distinct:** Random Enemy Attack (13 moves `2701..2713` at `0x64f1c0`) |

- **Program Evidence:**
```asm
0041e098  call     0x56d450
0041e09d  cmp      eax, 0xf
0041e0a0  ja       0x41e5e0
0041e0a6  jmp      dword ptr [eax*4 + 0x41e5fc]
0041e342  push     9
0041e344  push     0x64f930
0041e349  push     0x64f8c0
0041e364  call     0x42db00
0041e544  call     0x42d1d0
0041a4ed  mov      ecx, dword ptr [eax + 0xa8]
0041a4f3  cmp      ecx, 0x11
0041a4f6  ja       0x41a7fa
0041a4fc  movzx    eax, byte ptr [ecx + 0x41a838]
0041a503  jmp      dword ptr [eax*4 + 0x41a814]
0041a79f  call     0x505ad0
0041a7da  mov      dword ptr [ebx], 0x6c97f0
```

---

### M08.09 Exhaustive 26-Subclass `CActionPattern*` RTTI Matrix & `CActionPatternM0124` Self-Last Rotation (`0x42d1d0`)

- **Binary VA(s):** `0x6c968c..0x6c9a44` (all 26 `CActionPattern*` vtables), `0x41ee10..0x43034c` (all subclass methods), `0x42d1d0..0x42d33b` (`CActionPatternM0124::ctor`)
- **Calls:** `0x41f4b0` (`CActionPatternBase::ctor`), `0x41ec30` (`TargetSlot::operator=`), `0x420560` (`_SelectTarget`), `0x420b40` (`_Cover`), `0x420f10` (`CActionPatternBase::_Task`), `0x423cd0` (`_CheckEachInterrupt`), `0x4247e0` (`_CheckAfterAttackInterrupt`)
- **CalledBy:** `CActionSkill::_CreatePattern` (`0x41e060`), `CActionEnemyAttack::_CreatePattern` (`0x41a4a0`), `CActionJoinAttack::_CreatePattern` (`0x41c970`), `CBattleBase::Update` (`0x436b6a`, `0x43746c`, `0x438066`, `0x438211`, `0x438411`), `CActionItem`
- **Typed Pseudocode:**
```text
// Complete vtable slot layout of CActionPatternBase (0x6c96f0, 7 slots):
//   s0 (+0x00) = 0x41f6e0  ~CActionPatternBase (dtor)
//   s1 (+0x04) = 0x60460c  Update() (pure virtual)
//   s2 (+0x08) = 0x414560  no-op / Draw
//   s3 (+0x0c) = 0x41f910  helper
//   s4 (+0x10) = 0x420f10  _Task() (core combat hit resolution)
//   s5 (+0x14) = 0x425be0  animation-wait check
//   s6 (+0x18) = 0x425c60  effect trigger
//   Random-move subclasses extend vtable to 10 slots:
//     s7 (+0x1c) = 0x414560 (no-op), s8 (+0x20) = PrepareSubAction(), s9 (+0x24) = LogSubAction()

// CActionPatternM0124::ctor (0x42d1d0..0x42d33b) — Self-Slot Last Rotation:
function CActionPatternM0124_Ctor(this: CActionPatternM0124*, battleInfo, owner, action, inCounter):
    CActionPatternBase_Ctor(this, battleInfo, owner, action, flag10=0, inCounter=inCounter, startPhase=4, checkPre=1)
    this.vtable = 0x6c987c
    // Searches targetSlots for slot where slot.target == action.actor ([action+0x00]):
    selfIdx = FindIndex(action.targetSlots, s => s.target == action.actor)
    if selfIdx < action.targetSlots.size():
        tmp = action.targetSlots[selfIdx]
        for i in selfIdx .. action.targetSlots.size() - 2:
            action.targetSlots[i] = action.targetSlots[i + 1]        // Left-shift remaining targets
        action.targetSlots[last] = tmp                               // Caster resolves LAST!
    // Shares Update() verbatim with CActionPatternD (0x42ac40).
```

| # | RTTI Subclass (`Action::*`) | Vtable VA | Slots | Non-Dtor Overrides vs Base | `_SelectTarget` / `_Cover` / `_Task` | Combat-Distinct vs Visual-Only |
|---:|---|---|---:|---|---|---|
| 1 | `CActionPatternBase` | `0x6c96f0` | 7 | Base class (`_Task`=`0x420f10`) | Owns all base combat hooks | **Base** (abstract `Update`) |
| 2 | `CActionPatternA` | `0x6c968c` | 7 | `s1=0x41ee10` | `_SelectTarget`=Y, `_Cover`=Y, `_Task`=Base | **Base Sequential Template** (`flag10=1`, Parry aborts hits) |
| 3 | `CActionPatternB` | `0x6c96ac` | 7 | `s1=0x41f120` | `_SelectTarget`=Y, `_Cover`=Y, `_Task`=Base | **Visual-Only over `A`** (identical combat calls) |
| 4 | `CActionPatternC` | `0x6c9730` | 7 | `s1=0x42a8b0` | `_SelectTarget`=Y, `_Cover`=Y, `_Task`=Base | **Visual-Only over `A`** (identical combat calls) |
| 5 | `CActionPatternD` | `0x6c9750` | 7 | `s1=0x42ac40` | `_SelectTarget`=N, `_Cover`=N, `_Task`=Base | **Base AoE Wave Template** (`flag10=0`, deferred Parry, post-calc cover) |
| 6 | `CActionPatternE` | `0x6c9770` | 7 | `s1=0x42afd0` | `_SelectTarget`=N, `_Cover`=Y, `_Task`=Base | **Combat-Distinct Sequencing** (pre-calc `_Cover`, no `_SelectTarget`, `flag10=0`) |
| 7 | `CActionPatternF` | `0x6c981c` | 7 | `s1=0x42c6a0` | `_SelectTarget`=N, `_Cover`=N, `_Task`=Base | **Visual-Only over `D`** (identical combat calls) |
| 8 | `CActionPatternG` | `0x6c983c` | 7 | `s1=0x42c9b0` | `_SelectTarget`=Y, `_Cover`=N, `_Task`=Base | **Combat-Distinct Sequencing** (re-targets dead primary, no pre-calc `_Cover`, `flag10=0`) |
| 9 | `CActionPatternT0105` | `0x6c99a0` | 7 | `s1=0x42f3e0` | `_SelectTarget`=N, `_Cover`=Y, `_Task`=Base | **Combat-Distinct Sequencing** (`flag10=1` + `_Cover`, no `_SelectTarget`) |
| 10 | `CActionPatternM0140` | `0x6c98c8` | 7 | `s1=0x42d430` | `_SelectTarget`=N, `_Cover`=Y, `_Task`=Base | **Visual-Only over `T0105`** (identical combat calls) |
| 11 | `CActionPatternM0124` | `0x6c987c` | 7 | `s1=0x42ac40` (`D`), custom ctor `0x42d1d0` | `_SelectTarget`=N, `_Cover`=N, `_Task`=Base | **Combat-Distinct:** Rotates caster self-slot to end of `targetSlots` |
| 12 | `CActionPatternItem` | `0x6c985c` | 7 | `s1=0x42cc90`, `s2=0x42cfc0` | Dispatches `CItemResult` (`0x50c570`) | **Combat-Distinct:** Item execution pipeline (`M05`) |
| 13 | `CActionPatternE0822` | `0x6c9790` | 7 | `s1=0x42b2e0`, `s4=0x42b420` | Custom `_Task` | **Combat-Distinct:** Dance `200` MaxTP% TP damage (M08.11) |
| 14 | `CActionPatternE0835` | `0x6c97b0` | 7 | `s1=0x42b940`, `s4=0x42ba80` | Custom `_Task` | **Combat-Distinct:** Dance `204` Motivation boost (M08.11) |
| 15 | `CActionPatternE1580` | `0x6c97d0` | 7 | `s1=0x42bef0`, `s4=0x42c180` | Custom `_Task` | **Combat-Distinct:** Murder License `319` Instakill `119` (M08.11) |
| 16 | `CActionPatternT0094` | `0x6c9980` | 7 | `s1=0x42ed30`, `s4=0x42ee70` | Custom `_Task` | **Combat-Distinct:** Samba `199` / Geass `339` MaxHP% HP damage (M08.11) |
| 17 | `CActionPatternU0008` | `0x6c9a44` | 7 | `s1=0x42f940`, `s4=0x42fb60`, `s5=0x430340` | Custom `_Task` + `CItemResult` | **Combat-Distinct:** Overstock Clearance `446` weighted free item cast (M08.11) |
| 18 | `CActionPatternT0067` | `0x6c9940` | 7 | `s1=0x42e2f0`, `s4=0x42e380`, `s5=0x42e7a0` | Custom `_Task` (cmd `20`) | **Out-of-Combat Utility:** Item identification (`0x4e1150`) |
| 19 | `CActionPatternT0080` | `0x6c9960` | 7 | `s1=0x42e850`, `s4=0x42e8e0`, `s5=0x42e7a0` | Custom `_Task` | **Out-of-Combat Utility:** Floor treasure chest counter |
| 20 | `CActionPatternRandomEnemyAttackBase` | `0x6c98e8` | 10 | `s1=0x42d6f0`, `s2=0x42d960`, `s8=0x42d990`, `s9=0x42daa0` | Spawns sub-`CActionEnemyAttack` | **Combat-Distinct Base:** Random enemy move runner (M08.10) |
| 21 | `CActionPatternE2520` | `0x6c97f0` | 10 | Inherits #20 + `s9=0x42c5f0` | Table `0x64f1c0` (13 attacks) | **Combat-Distinct:** Enemy case 17 weighted random attack (M08.10) |
| 22 | `CActionPatternRandomSkillBase` | `0x6c9914` | 10 | `s1=0x42dd80`, `s2=0x42d960`, `s8=0x42e130`, `s9=0x42e240` | Spawns sub-`CActionSkill` (`315` table swap) | **Combat-Distinct Base:** Random skill runner (M08.10) |
| 23 | `CActionPatternM0129` | `0x6c989c` | 10 | Inherits #22 + `s8=0x42d370` | Table `0x64f458`/`0x64f440`, keeps targets | **Combat-Distinct:** Skill case 14 (2 moves, no re-target) (M08.10) |
| 24 | `CActionPatternT0111` | `0x6c99c0` | 10 | Inherits #22 verbatim | Table `0x64f8c0`/`0x64f930` (9 moves) | **Combat-Distinct:** Skill case 10 weighted random skill (M08.10) |
| 25 | `CActionPatternT0118` | `0x6c99ec` | 10 | Inherits #22 + `s9=0x42f700` + ctor swap | Table `0x64fa28`/`0x64f9a0` (11 moves) | **Combat-Distinct:** Skill case 11 (+ Genzimaru `121->125` swap) (M08.10) |
| 26 | `CActionPatternT0130` | `0x6c9a18` | 10 | Inherits #22 + `s9=0x42f7a0` | Table `0x64fb50`/`0x64fab0` (13 moves) | **Combat-Distinct:** Skill case 12 weighted random skill (M08.10) |

- **Program Evidence:**
```asm
0042d1ee  push     1
0042d1f0  push     4
0042d205  call     0x41f4b0
0042d21b  mov      dword ptr [ebx], 0x6c987c
0042d245  mov      ebx, dword ptr [ecx]
0042d247  cmp      ebx, dword ptr [edi]
0042d249  je       0x42d26f
0042d2a5  call     0x41ec30
0042d2df  call     0x41ec30
0042d314  call     0x41ec30
0041ef8e  call     0x423cd0
0041ef98  jne      0x41efcb
0041efe8  mov      dword ptr [edi + 0x18], 0xa
0042ad48  call     0x423cd0
0042ae30  mov      dword ptr [edi + 0x3c], 0
```

---

### M08.10 Random-Move Action Patterns (`CActionPatternRandomSkillBase` `0x42db00`, `T0111`/`T0118`/`T0130`/`M0129`, `E2520`) & Triple Joker `315` (`0x13b`)

- **Binary VA(s):** `0x505ad0..0x505b50` (`WeightedRand`), `0x42db00..0x42dc42` (`CActionPatternRandomSkillBase::ctor`), `0x42dd80..0x42e240` (`RandomSkillBase::Update` & `s8`), `0x42d370..0x42d3f6` (`M0129::s8`), `0x41e374..0x41e4d9` (`T0118` Genzimaru override), `0x41a6c6..0x41a7f9` (`E2520::ctor`), `0x42d990..0x42da98` (`RandomEnemyAttackBase::s8`)
- **Calls:** `0x490790` (`CRandom::Get`), `0x505ad0` (`WeightedRand`), `0x4181e0` / `0x4183d0` (`SetAttackRange`), `0x417cd0` (`SetHitCount`), `0x43f450` (skill target select), `0x43b0d0` (enemy target select), `0x41d480` (`CActionSkill`)
- **CalledBy:** `CActionSkill::_CreatePattern` (`0x41e364`, `0x41e3ad`, `0x41e50f`, `0x41e593`), `CActionEnemyAttack::_CreatePattern` (`0x41a6c6`)
- **Typed Pseudocode:**
```text
// WeightedRand (0x505ad0..0x505b50): 1 RNG call on GlobalRng ([0x816ce8]).
function WeightedRand(weights: i32*, count: u32) -> u32:
    cum: i32[count]; total: i32 = 0
    for i in 0 .. count - 1:
        total += weights[i]; cum[i] = total
    r: u32 = GlobalRng.Rand(total)                                   // 0x490790(total)
    for i in 0 .. count - 1:
        if r < u32(cum[i]): return i                                 // strict < (jb at 0x505b43)
    return count

// CActionPatternRandomSkillBase::ctor (0x42db00..0x42dc42):
function RandomSkillBase_Ctor(this, battleInfo, owner, action, inCounter, table1, table2, count):
    CActionPatternBase_Ctor(this, battleInfo, owner, action, flag10=1, inCounter=inCounter, startPhase=0, checkPre=0)
    // Passive 315 (0x13b, 'Triple Joker') switches table1 -> table2! (0x42db80..0x42db93)
    tbl = action.actor.HasCommand(0x13b) ? table2 : table1           // vtable+0x50(0x13b)
    idx = WeightedRand([tbl[i].weight for i in 0..count-1], count)   // 0x505ad0
    this.selectedEntry = &tbl[idx]                                   // [this+0x9c] (3 x i32: skill0, skill1, weight)

// T0118 Constructor Genzimaru Doll Override (0x41e3c2..0x41e4d9):
if selectedEntry.skill0 == 121 (0x79):
    if ExistsAlivePlayerSideDollWithRTTI(CGamePlayerStatusETCGenzimaru /* 0x70855c */):
        selectedEntry = FindEntryInTable(0x64fa28, skill0 == 125 /* 0x7d */)

// Sub-action preparation difference (vtable slot 8, +0x20):
// - RandomSkillBase::s8 (0x42e130, used by T0111/T0118/T0130): sets action.skillId = selectedEntry[subIdx],
//   recomputes SetAttackRange (0x4181e0) + SetHitCount (0x417cd0), AND re-selects targets via 0x43f450!
// - M0129::s8 (0x42d370): sets action.skillId = selectedEntry[subIdx], recomputes SetAttackRange + SetHitCount,
//   resets curHitIdx = 0, and PRESERVES existing targetSlots (does NOT call 0x43f450)!
// - RandomEnemyAttackBase::s8 (0x42d990, used by E2520): sets action.enemyAttackId = selectedEntry[subIdx],
//   recomputes SetAttackRange (0x4183d0) + SetHitCount (0x417cd0), AND re-selects targets via 0x43b0d0!
```

| Pattern | Default Table (`table1`) | `315` Triple Joker Table (`table2`) | Entries `(moveId: w1 / w2)` |
|---|---|---|---|
| `M0129` (Case 14) | `0x64f458` (2) | `0x64f440` (2) | `141`: 50/70, `142`: 50/30 (sum 100) |
| `T0111` (Case 10) | `0x64f8c0` (9) | `0x64f930` (9) | `108..112`: 10/12 ea, `113`: 20/20, `114`: 10/5, `115`: 10/10, `116`: 10/5 (sum 100) |
| `T0118` (Case 11) | `0x64fa28` (11) | `0x64f9a0` (11) | `117`: 10/10, `118`: 10/15, `119`: 10/5, `120`: 10/10, `121`: 10/15, `122`: 10/5, `123`: 10/10, `124`: 5/5, `125`: 5/5, `126`: 10/5, `127`: 10/15 (sum 100) |
| `T0130` (Case 12) | `0x64fb50` (13) | `0x64fab0` (13) | `128`: 5/10, `129`: 10/10, `130`: 5/10, `131`: 10/3, `132`: 10/10, `133`: 5/7, `134`: 5/3, `135`: 5/10, `136`: 10/5, `137`: 10/12, `138`: 5/3, `139`: 10/12, `140`: 5/5 (sum 100) |
| `E2520` (Enemy 17) | `0x64f1c0` (13) | *(none)* | `2701`: 5, `2702`: 10, `2703`: 5, `2704`: 10, `2705`: 10, `2706`: 5, `2707`: 5, `2708`: 5, `2709`: 10, `2710`: 10, `2711`: 5, `2712`: 10, `2713`: 5 (sum 100) |

- **Program Evidence:**
```asm
0042db82  push     0x13b
0042db89  mov      eax, dword ptr [eax + 0x50]
0042db8c  call     eax
0042db8e  mov      esi, dword ptr [ebp + 0x1c]
0042db91  test     al, al
0042db93  cmovne   esi, dword ptr [ebp + 0x20]
0042dbf1  call     0x505ad0
0041e3c2  cmp      dword ptr [eax], 0x79
0041e465  push     0x70855c
0041e490  cmp      dword ptr [eax + 0x64fa28], 0x7d
0042d3bc  mov      dword ptr [ecx + 8], eax
0042d3c5  call     0x4181e0
0042d3d1  call     0x417cd0
0042e1e2  call     0x43f450
00505b35  call     0x490790
00505b40  cmp      eax, dword ptr [ebx + esi*4]
00505b43  jb       0x505b4a
```

---

### M08.11 Direct-Update Custom `_Task` Patterns: `E0822` (`0x42b240`), `E0835` (`0x42b8a0`), `E1580` (`0x42be90`), `T0094` (`0x42ec90`), and `U0008` (`0x42f870`)

- **Binary VA(s):** `0x42b240..0x42b89d` (`CActionPatternE0822`), `0x42b8a0..0x42be86` (`CActionPatternE0835`), `0x42be90..0x42c56e` (`CActionPatternE1580`), `0x42ec90..0x42f3ad` (`CActionPatternT0094`), `0x42f870..0x43034c` (`CActionPatternU0008`), `0x4f69e0..0x4f6a50` (Motivation clamp)
- **Calls:** `0x48cbf0` (find command index `0x128`), `0x47e500` (`CCommand::Execute`), `0x4f69e0` (clamp Motivation `[70, 130]`), `0x47b220` (`CCommand` factory `0x77`), `0x490790` (`CRandom::Get`), `0x43af10` (alive player list), `0x43b1d0` (alive enemy list), `0x50c570` (`CItemResult` factory)
- **CalledBy:** `CBattleBase::Update` (`0x436b6a`, `0x43746c`, `0x438066`, `0x438211`, `0x438411`), `M00.03`
- **Typed Pseudocode:**
```text
// 1. CActionPatternE0822::_Task (0x42b420..0x42b89d) — Dance 200 (0xc8) MaxTP% TP Damage:
//    0 RNG calls.
function E0822_Task(this, slot):
    if cmd200 = FindInVec(actCmds, 0xc8):
        tpDmg: i32 = trunc0(f32(slot.target.maxTP /* [target+0x18] */) * cmd200.GetValue())
        if cmd296 = FindInVec(actCmds, 0x128):                       // 296 Damage Cap
            tpDmg = min(tpDmg, trunc0(cmd296.GetValue()))
        seq.push_back(TaskResult(slot.target, tpDamage=tpDmg, tpDamageRaw=tpDmg))
    CCommand_Execute(seq, -1, this.battleInfo)

// 2. CActionPatternE0835::_Task (0x42ba80..0x42be86) — Dance 204 (0xcc) Motivation Boost:
//    0 RNG calls. Player targets only (dynamic_cast<CGamePlayerStatus*> != null and !vtable+0x100()).
function E0835_Task(this, slot):
    if cmd204 = FindInVec(actCmds, 0xcc):
        if player = dynamic_cast<CGamePlayerStatus*>(slot.target):
            if !player.vtable_0x100():
                member = GameManager.GetMemberById(player.GetMemberId())
                member.motivation += cmd204.GetValue()               // [member+0xd8] f32
                // ClampMotivation (0x4f69e0): clamp([70.0f, 130.0f]);
                //   if ench 201 (0xc9) > 0 -> force 70.0f; if ench 200 (0xc8) > 0 -> max(100.0f, motivation).
                member.ClampMotivation(); member.vtable_0x108()
    CCommand_Execute(seq, -1, this.battleInfo)

// 3. CActionPatternE1580::_Task (0x42c180..0x42c56e) — Murder License 319 (0x13f) Instakill:
function E1580_Task(this, slot):
    // Instantiates cmd 119 (0x77, 'Instakill') with val = 1.0f (0x6d938c) and executes on slot.target:
    cmd119 = CreateCommand(type=1, id=0x77, val=1.0f, skillId_or_neg1, subId=-1, dur=0)
    cmd119.ExecuteCalc(seq, this.battleInfo, slot.target, actCmds, this.action.actor)
    CCommand_Execute(seq, -1, this.battleInfo)

// 4. CActionPatternT0094::_Task (0x42ee70..0x42f3ad) — Samba Dance 199 (0xc7) & Geass 339 (0x153) MaxHP% HP Damage:
//    0 RNG calls.
function T0094_Task(this, slot):
    cmd = FindInVec(actCmds, 0xc7) ?? FindInVec(actCmds, 0x153)      // 199 checked before 339
    if cmd != null:
        hpDmg: i32 = trunc0(f32(slot.target.GetMaxHP()) * cmd.GetValue())
        if cmd296 = FindInVec(actCmds, 0x128):                       // 296 Damage Cap
            hpDmg = min(hpDmg, trunc0(cmd296.GetValue()))
        seq.push_back(TaskResult(slot.target, hpDamage=hpDmg, hpDamageRaw=hpDmg, flag37=0))
    for r in seq:
        if r.cmd != null and r.cmd.GetCommandId() in {0xc7, 0x153}:
            r.resultType = 0                                         // Suppress raw dance/geass result log
    CCommand_Execute(seq, -1, this.battleInfo)

// 5. CActionPatternU0008::_Task (0x42fb60..0x4302cf) & ::Update (0x42f940) — Overstock Clearance 446 (0x1be):
//    RNG calls: 1 for item pick (Rand(105)) + 0 or 1 for target selection (items 49, 55, 56).
function U0008_Task(this):
    // Cumulative thresholds [20, 40, 60, 75, 90, 105] -> weights [20, 20, 20, 15, 15, 15] (total 105 = 0x69):
    r: u32 = GlobalRng.Rand(105)                                     // 0x490790(0x69)
    idx = FirstIndexWhere(r < [20, 40, 60, 75, 90, 105][i])          // strict < (jb at 0x42fbf9)
    itemId: i32 = [1, 6, 45, 49, 55, 56][idx]                        // [idx*8 + 0x64fd04]
    this.itemId = itemId; this.action.itemId = itemId; this.action.targetSlots.clear()
    switch itemId:
        case 1  (0x01): target = ArgMin(aliveAllies, u => f32(u.CurHP) / f32(u.MaxHP)) // Tie: first
        case 6  (0x06): targets = allAliveAllies                     // 0x43af10(1, 0, 1)
        case 45 (0x2d): target = ArgMin(aliveAllies, u => f32(u.CurTP) / f32(u.MaxTP)) // [u+0x14]/[u+0x18]
        case 49 (0x31): pool = Filter(aliveAllies, u => u.vtable_0x7c() || u.vtable_0x8c())
                        if pool.empty(): pool = aliveAllies
                        target = pool[GlobalRng.Rand(pool.size())]
        case 55 (0x37): target = aliveEnemies[GlobalRng.Rand(aliveEnemies.size())]
        case 56 (0x38): front = aliveEnemiesRow(1); back = aliveEnemiesRow(2)
                        row = front.empty() ? back : back.empty() ? front : (GlobalRng.Rand(2)==0 ? front : back)
                        targets = row
    // U0008::Update (0x42f940) then runs every CItemResult of `itemId` via 0x50c570 without consuming inventory!
```
- **Program Evidence:**
```asm
0042b58e  cmp      eax, 0xc8
0042b5b7  mov      esi, dword ptr [eax + 0x18]
0042b5cb  mov      edx, 0x128
0042b5db  cvttss2si esi, dword ptr [ebp + 0x48]
0042bbd0  cmp      eax, 0xcc
0042bc5b  movss    xmm0, dword ptr [esi + 0xd8]
0042bc68  addss    xmm0, dword ptr [ebp - 0x24]
0042bc75  call     0x4f69e0
0042c2d1  lea      edx, [ecx + 0x76]
0042c2db  call     0x47b220
0042efde  cmp      eax, 0xc7
0042f01e  cmp      eax, 0x153
0042f06b  mov      edx, 0x128
0042f073  cvttss2si edi, dword ptr [ebp + 0x4c]
0042fbc4  push     0x69
0042fbef  call     0x490790
0042fbf6  cmp      eax, dword ptr [edi + esi*4]
0042fbf9  jb       0x42fc01
0042fc2c  mov      eax, dword ptr [esi*8 + 0x64fd04]
0042fa1b  call     0x50c570
```

---

### M08.12 Steal Resolution `CBattle::_Steal` (`0x44fde0`)

- **Binary VA(s):** `0x44fde0..0x45069c` (`CBattle::_Steal`)
- **Calls:** `0x47e340` (`FindCommand`), `actor->vtable+0x34(4)` (`GetDEX`), `target->vtable+0x34(5)` (`GetAGI`), `0x490790` (`CRandom::Get`), `0x61e650` (`round_f32_to_i32`), `0x558180` (roll enemy drop/steal item)
- **CalledBy:** `CActionPatternBase::_Task` (`0x421591`), `M00.06`
- **Typed Pseudocode:**
```text
// RNG calls: 1 for steal success roll (0x490790(100)) [+ drop roll in 0x558180 on successful Item Steal].
function CBattle_Steal(this: CBattle*, res: TaskResult*, target: BattleUnit_s*, actCmds: Vec<CCommand*>*, actor: BattleUnit_s*):
    // 1. Base Steal Rate from cmd 60 (0x3c Gold Steal) else cmd 61 (0x3d Item Steal):
    baseRate: f32 = 0.0f
    if cmd60 = FindCommand(actCmds, 0x3c): baseRate = cmd60.GetValue()
    else if cmd61 = FindCommand(actCmds, 0x3d): baseRate = cmd61.GetValue()

    // 2. Stat-Scaled Clamped Steal Probability (0x44fe82..0x44ff35):
    dex: f32 = f32(actor.status.GetStat(4))                          // Stat 4 = DEX
    agi: f32 = f32(target.status.GetStat(5))                         // Stat 5 = AGI
    rate: f32 = clamp(((dex + 50.0f) / (agi + 50.0f)) * 0.5f * baseRate, 0.05f, 0.95f)
    isFail: bool = (GlobalRng.Rand(100) >= trunc0(rate * 100.0f))    // 0x490790(0x64), cvttss2si, setge!

    // 3. Branch A — Gold Steal (cmd 60 / 0x3c, 0x44ff39..0x450369):
    if FindCommand(actCmds, 0x3c) != null:
        mult: f32 = (cmd62 = FindCommand(actCmds, 0x3e)) ? cmd62.GetValue() : 1.0f // 62 Enemy Gold Steal
        if target.isPlayerSide != 0:                                 // Enemy stealing from Player Party
            if isFail: res.resultType = 3; return
            stolen: i32 = trunc0(f32(GameManager.GetGold()) * mult)  // cvttss2si at 0x44ffc7
            GameManager.AddGold(-stolen)                             // vtable+0x48
            enemyActor = dynamic_cast<CGameEnemyStatus*>(actor.status)
            enemyActor.stolenGold = clamp(enemyActor.stolenGold + stolen, 0, 999999999) // [enemy+0x158], 0x3b9ac9ff
            return
        else:                                                        // Player stealing from Enemy
            enemyTgt = dynamic_cast<CGameEnemyStatus*>(target.status)
            enemyParam = EnemyTable.Lookup(enemyTgt.enemyId)         // [0x7389d8]
            if enemyTgt.goldAlreadyStolen != 0 or enemyParam.gold == 0: // [enemy+0x155], [param+0x50]
                res.resultType = 3; return                           // Nothing to steal
            if isFail: res.resultType = 3; return
            stolen: i32 = max(1, round_f32_to_i32(f32(enemyParam.gold) * mult)) // 0x61e650 at 0x450214!
            this.bonusGold += stolen                                 // [battle+0x58]
            enemyTgt.goldAlreadyStolen = 1u8                         // [enemy+0x155] = 1 (once per enemy!)
            return

    // 4. Branch B — Item Steal (cmd 61 / 0x3d, 0x45036a..0x45064d):
    if FindCommand(actCmds, 0x3d) != null and target.isPlayerSide == 0:
        enemyTgt = dynamic_cast<CGameEnemyStatus*>(target.status)
        enemyParam = EnemyTable.Lookup(enemyTgt.enemyId)
        if ((enemyParam.flags54 >> 15) & 1) == 0:                    // Stealable flag bit 15 ([param+0x54] >> 0xf)
            res.resultType = 3; return
        if enemyTgt.itemAlreadyStolen != 0: return                   // [enemy+0x154] != 0 (once per enemy!)
        if isFail: res.resultType = 3; return
        if item = RollEnemyStealItem(enemyTgt, actor.status, floorFlag): // 0x558180
            this.stolenItems.push_back((enemyTgt.enemyId, item))     // [battle+0x4c..0x50]
            enemyTgt.itemAlreadyStolen = 1u8                         // [enemy+0x154] = 1
```
- **Program Evidence:**
```asm
0044fe2c  mov      edx, 0x3c
0044fe55  mov      edx, 0x3d
0044febc  addss    xmm0, dword ptr [0x6d94e0]    ; float 50
0044fee8  divss    xmm1, xmm0
0044feec  movss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0044fef4  mulss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0044ff05  movss    xmm1, dword ptr [0x6d9384]    ; float 0.95
0044ff16  call     0x490790
0044ff2d  cvttss2si ecx, xmm0
0044ff31  cmp      eax, ecx
0044ff35  setge    byte ptr [ebp + 0x13]
0044ff50  mov      edx, 0x3e
0044ffc7  cvttss2si ebx, xmm0
0045014d  cmp      byte ptr [edi + 0x155], 0
00450214  call     0x61e650
00450232  add      dword ptr [ebx + 0x58], esi
004503bf  mov      eax, dword ptr [eax + 0x54]
004503c2  shr      eax, 0xf
004503cd  cmp      byte ptr [esi + 0x154], 0
004504bf  call     0x558180
```

---

## 5. Turn-Start & Post-Action Class Passive Procs (`M08.13` – `M08.14`)

### M08.13 Turn-Start Class Passive Procs (`311`, `345`, `446`, `319`, `357`, `350`, `448`, `355`) and Field Passive `306`

- **Binary VA(s):** `0x436713..0x436be4` (`TurnPhaseNo` 0, 2, 3: `311`, `345`, `446`), `0x439613..0x4396b5` (Outer `PhaseNo` 13: Third Eye Wide `345` resolution), `0x437364..0x437b0b` (`TurnPhaseNo` 12..15: `319`, `357`, `350`, `448`), `0x438495..0x438700` (`TurnPhaseNo` 22: `355`), `0x555f20..0x556160` (Field passive `306` / `0x132`), `0x6c9a7c` (`311` ailment table), `0x6c9af8` (`345` ailment/dispel table)
- **Calls:** `0x61e650` (`round_f32_to_i32`), `0x505ac0` (`Rand`), `0x47e500` (`CCommand::Execute`), `0x47b220` / `0x47e260` (`CCommand` factory), `0x42f870` (`CActionPatternU0008`), `0x42be90` (`CActionPatternE1580`), `0x43b6a0` (remove unit), `0x4fe2e0` + `0x43a150` (spawn Doll), `0x4e4dd0` (party passive lookup for `306`)
- **CalledBy:** `CBattleBase::Update` (`0x436700`, jump table `0x439820` & outer `0x4397e0`), `M00.03`; Dungeon step update (`0x555f20`)
- **Typed Pseudocode:**
```text
// Note on TurnPhaseNo skip: All inner turn-start states (0..24) are SKIPPED on extra turns ([actor+0xb0] != 0)
// and for Dolls (2000..2999), Summons/Guests (3000..3999), or unitId >= 4000 (0x4365ff..0x43664d).
// `opponents` ([ebp-0x40]) = alive opposing-side units (0x436681..0x4366fb).

// 1. Esarhaddon (cmd 311 / 0x137, TurnPhaseNo 0, 0x436727..0x43692e) — 0 RNG calls:
if cmd311 = actor.status.GetCommand(0, 0x137):
    count: i32 = round_f32_to_i32(cmd311.GetValue())                 // 0x61e650
    // Fixed table at 0x6c9a7c: [113 Poison, 115 Paralysis, 117 Silence, 114 Freeze, 116 Sleep, 122 Slow]
    purgeSeq = []
    for i in 0 .. count - 1:
        if active = actor.status.GetCommand(0, Table_0x6c9a7c[i]):
            purgeSeq.push_back(TaskResult(actor.status, cmd=active, resultType=2))
    if !purgeSeq.empty():
        CCommand_Execute(purgeSeq, -1, this.battleInfo); this.PhaseNo = 14

// 2. Third Eye Wide (cmd 345 / 0x159, TurnPhaseNo 2, 0x436955..0x436a98 + Outer Phase 13, 0x439613..0x4396b5):
//    Checked on OPPOSING alive units (NOT on actor!) in `opponents` order. Stops at first proc.
//    RNG calls: 1 per opposing owner (0x505ac0(100)) + 1 on proc (0x505ac0(7)).
for opp in opponents:
    if opp.isPlayerSide != actor.isPlayerSide:
        if cmd345 = opp.status.GetCommand(0, 0x159):
            if Rand(100) < trunc0(cmd345.GetValue() * 100.0f):       // 0x505ac0(0x64), strict <
                this.thirdEyeOwner = opp                             // [battle+0x1a4] = opp
                this.PhaseNo = 13                                    // Outer Phase 13 (0x439613)
                break
// Outer Phase 13 (0x43963c..0x4396b5):
//   Table_0x6c9af8 (7 entries): [113 Poison, 115 Paralysis, 116 Sleep, 114 Freeze, 117 Silence, 118 Stun, 74 Strip Buffs]
//   cmdId = Table_0x6c9af8[Rand(7)]                                 // 0x505ac0(7)
//   cmd = CreateCommand(type=1, id=cmdId, val=0.75f, skillId=-1, subId=-1, dur=0)
//   actor.status.vtable_0xe4([cmd], this.battleInfo, this.thirdEyeOwner.status)
//   this.PhaseNo = 14

// 3. Overstock Clearance (cmd 446 / 0x1be, TurnPhaseNo 3, 0x436a9b..0x436be3) — 1 RNG call:
if cmd446 = actor.status.GetCommand(0, 0x1be):
    if Rand(100) < trunc0(cmd446.GetValue() * 100.0f):               // 0x505ac0(0x64), strict <
        // Player-side only (else assert 0x436b21); spawns CActionPatternU0008 (0x42f870, M08.11) -> PhaseNo = 11

// 4. Murder License (cmd 319 / 0x13f, TurnPhaseNo 12, 0x437364..0x437498) — 1 RNG call (target pick ONLY):
//    100% deterministic proc (NO chance roll!).
if cmd319 = actor.status.GetCommand(0, 0x13f):
    target = opponents[Rand(opponents.size())]                       // 0x505ac0(size)
    // Sets 1-hit action targeting `target` and spawns CActionPatternE1580 (0x42be90, M08.11) -> PhaseNo = 11

// 5. Tranquil Song (cmd 357 / 0x165, TurnPhaseNo 13, 0x437499..0x4376e2) — 1 RNG call:
if cmd357 = actor.status.GetCommand(0, 0x165):
    if Rand(100) < trunc0(cmd357.GetValue() * 100.0f):               // 0x505ac0(0x64), strict <
        for opp in opponents:
            opp.status.AddStatus(MakeCmd(0x29, -0.1f, dur=4))        // 41 ATK -10%, 4 turns
            opp.status.AddStatus(MakeCmd(0x2b, -0.1f, dur=4))        // 43 INT -10%, 4 turns
        this.PhaseNo = 14

// 6. Usurper of Souls (cmd 350 / 0x15e, TurnPhaseNo 14, 0x4376e3..0x4378d8) — 1 (+1 if candidates) RNG calls:
if cmd350 = actor.status.GetCommand(0, 0x15e):
    if Rand(100) < trunc0(cmd350.GetValue() * 100.0f):               // 0x505ac0(0x64), strict <
        // Player-side actor only (0x437799): collects opposing alive Dolls (unitId 2000..2999,
        // CGameEnemyStatusETCBase 0x707fc4 with [etc+0x194] == 3 via 0x4fd6a0):
        if !cands.empty():
            victim = cands[Rand(cands.size())]                       // 0x505ac0(size)
            this.RemoveUnit(victim)                                  // 0x43b6a0
            this.PhaseNo = 14

// 7. Shadow Heart (cmd 448 / 0x1c0, TurnPhaseNo 15, 0x4378d9..0x437b0b) — 1 RNG call:
if cmd448 = actor.status.GetCommand(0, 0x1c0):
    if Rand(100) < trunc0(cmd448.GetValue() * 100.0f):               // 0x505ac0(0x64), strict <
        // Checks if actor already owns a living Doll (0x707ec4 or 0x707f90 with owner 0x4fd950 == actor.playerStatus):
        if !actorAlreadyOwnsLivingDoll:
            doll = new DollStatus(actor.playerStatus, dollType=3, emptyVec, 0, skillId=0x17c /* 380 */) // 0x4fe2e0
            this.AddDollToBattle(doll)                               // 0x43a150
            this.PhaseNo = 14

// 8. Undaunted Spirit (cmd 355 / 0x163, TurnPhaseNo 22, 0x438495..0x438700) — 1 RNG call per dead ally with 355:
//    Checked on EVERY dead unit (`vtable+0x38`) on `actor`'s side (NOT on actor itself!).
for u in this.units where u.status.IsDead() and u.isPlayerSide == actor.isPlayerSide:
    if cmd355 = u.status.GetCommand(0, 0x163):
        if Rand(100) < trunc0(cmd355.GetValue() * 100.0f):           // 0x505ac0(0x64), strict <
            CCommand_Execute([TaskResult(u.status, hpHeal=1, hpHealRaw=1, resultType=0)], -1, this.battleInfo)
            this.vtable_SortTime(1, 1)                               // vtable+0x24(1, 1)
            this.PhaseNo = 14

// 9. Cross-References for 305 & 306 (NOT in CBattleBase::Update Turn-Start):
//    - Passive 305 (0x131, 'Knock Down'): In-task long-range physical hit negation at 0x422207 (see M08.04).
//    - Passive 306 (0x132, 'Present for Me'): Out-of-combat dungeon step trigger at 0x555f20..0x556160.
//      Requires stepCounter [dungeon+0x77c] >= 10, queries party passive 0x4e4dd0(0x132) for `slotCount = round(val)`,
//      rolls GlobalRng.Rand(100) < sum(floorPresentWeights[0..slotCount-1]), awards matching floor item, resets counter to 0.
```
- **Program Evidence:**
```asm
00436727  push     0x137
0043676a  call     0x61e650
00436793  push     dword ptr [edi*4 + 0x6c9a7c]
0043697b  push     0x159
00436a80  mov      dword ptr [edi + 0x18], 0xd
00439643  mov      ecx, 7
0043964a  call     0x505ac0
0043964f  movss    xmm2, dword ptr [0x6d9368]    ; float 0.75
00439660  mov      edx, dword ptr [eax*4 + 0x6c9af8]
00436aa2  push     0x1be
00436b6a  call     0x42f870
0043736a  push     0x13f
0043746c  call     0x42be90
0043749f  push     0x165
00437546  mov      edx, 0x29
00437585  mov      edx, 0x2b
004376e9  push     0x15e
00437845  call     0x43b6a0
004378e2  push     0x1c0
00437a1f  push     0x17c
00437a35  call     0x4fe2e0
0043852d  push     0x163
00438668  mov      dword ptr [ebp - 0xb4], 1
00438698  call     0x47e500
00555f31  cmp      dword ptr [ebp + 0x77c], 0xa
00555f49  push     0x132
00555f4e  call     0x4e4dd0
```

---

### M08.14 Post-Action Class Passive Procs (`291` Jump Table `0x439884`, `288`, `289`, `354`)

- **Binary VA(s):** `0x438e50..0x43903b` (Heretic Samsara `291` / `0x123`, jump table `0x439884..0x4398a3`), `0x43903b..0x439285` (Extra-turn passives `288` / `0x120`, `289` / `0x121`, `354` / `0x162`)
- **Calls:** `0x505ac0` (`Rand`), `0x47b220` / `0x47e260` (`CCommand` factory), `actor->vtable+0x54` (`AddStatus`), `0x43e5c0` (`CBattleBase::_SetTime`)
- **CalledBy:** `CBattleBase::Update` Outer State 3 (`0x438beb`), `M00.08`
- **Typed Pseudocode:**
```text
// Executed in CBattleBase::Update Outer State 3 after currentAction finishes, Doll/Summon expiry, and victory check:

// 1. Heretic Samsara (cmd 291 / 0x123, 0x438e50..0x43903b) — 8 RNG calls when active (1 per resistance):
if cmd291 = actor.status.GetCommand(0, 0x123):
    if cmd291.GetValue() >= 1.0f:                                    // comiss 1.0f; jb 0x43903b
        // Loops idx = 6..13 via jump table 0x439884 -> Fixed Elemental/Physical Resistance commands 416..423:
        //   6 -> 416 (0x1a0 Fixed Slash)    | 10 -> 420 (0x1a4 Fixed Water)
        //   7 -> 417 (0x1a1 Fixed Stab)     | 11 -> 421 (0x1a5 Fixed Wind)
        //   8 -> 418 (0x1a2 Fixed Bash)     | 12 -> 422 (0x1a6 Fixed Earth)
        //   9 -> 419 (0x1a3 Fixed Fire)     | 13 -> 423 (0x1a7 Fixed Lightning)
        for idx in 6 .. 13:
            cmdId = 0x1a0 + (idx - 6)
            resVal: f32 = f32((Rand(2) + 1) * 50)                    // 0x505ac0(2) -> 50.0f or 100.0f
            actor.status.AddStatus(MakeCmd(cmdId, resVal, dur=0))    // vtable+0x54

// 2. Extra-Turn Passive Rolls (0x43903b..0x439285) — Priority: 288 -> 289 -> 354:
//    Guards:
//      (a) actor.grantedExtraTurn == 0 ([actor+0x107] == 0: cannot chain extra-turn rolls on an extra turn!)
//      (b) actor == battle.units[0] (actor must still be head of ATB queue, e.g. not pushed back)
//      (c) !actor.status.IsIncapacitated() (vtable+0xbc == 0)
extraActions: i32 = 0
if actor.grantedExtraTurn == 0 and actor == this.units[0] and !actor.status.IsIncapacitated():
    if (cmd288 = actor.status.GetCommand(0, 0x120)) != null:         // 288 Double Action
        if Rand(100) < trunc0(cmd288.GetValue() * 100.0f):           // 0x505ac0(0x64), strict <
            extraActions = 2                                         // 2 total actions (1 bonus)
    if extraActions == 0 and (cmd289 = actor.status.GetCommand(0, 0x121)) != null: // 289 Triple Action
        if Rand(100) < trunc0(cmd289.GetValue() * 100.0f):           // 0x505ac0(0x64), strict <
            extraActions = 3                                         // 3 total actions (2 bonus)
    if extraActions == 0 and (cmd354 = actor.status.GetCommand(0, 0x162)) != null: // 354 Did You Call for Me?
        if Rand(100) < trunc0(cmd354.GetValue() * 100.0f):           // 0x505ac0(0x64), strict <
            extraActions = 2                                         // 2 total actions (1 bonus)

if extraActions > 0:
    actor.grantedExtraTurn = 1u8                                     // [actor+0x107] = 1
    actor.extraActionLimit = extraActions                            // [actor+0xb4] = 2 or 3
    // Skips CBattleBase::_SetTime (0x43e5c0); actor keeps front of ATB queue & skips TurnPhaseNo on re-entry!
else:
    this._SetTime(needAdvance ? actor : null)                        // 0x43e5c0
    this.TurnPhaseNo = 0                                             // [battle+0x20] = 0
```
- **Program Evidence:**
```asm
00438e53  push     0x123
00438e7d  comiss   xmm0, dword ptr [0x6d938c]    ; float 1
00438e84  jb       0x43903b
00438e8a  mov      ecx, 6
00438e9c  cmp      eax, 7
00438ea4  jmp      dword ptr [eax*4 + 0x439884]
00438eab  mov      dword ptr [ebp - 0x14], 0x1a0
00438eea  mov      dword ptr [ebp - 0x14], 0x1a7
00438f10  mov      ecx, 2
00438f15  call     0x505ac0
00438f1d  inc      eax
00438f1e  imul     esi, eax, 0x32
00438fec  cmp      ecx, 0xd
00438fef  jbe      0x438e92
0043903b  cmp      byte ptr [esi + 0x107], 0
00439042  jne      0x439272
0043905f  mov      eax, dword ptr [eax + 0xbc]
00439072  push     0x120
00439098  call     0x505ac0
004390b0  jl       0x43914b
004390b9  push     0x121
004390df  call     0x505ac0
004390f9  mov      eax, 3
00439103  push     0x162
0043912d  call     0x505ac0
0043914b  mov      eax, 2
00439153  mov      byte ptr [esi + 0x107], 1
0043915a  mov      dword ptr [esi + 0xb4], eax
0043927f  call     0x43e5c0
```

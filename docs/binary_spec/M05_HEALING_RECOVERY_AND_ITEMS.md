# M05 — Healing, Recovery, After-Battle & `ItemResult` (`0..106`) (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x413000..0x570000`)**
> Extracted directly from `backups/exe/DT22_en_unwrapped.vanilla.exe` (x86-32, image base `0x400000`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`) and `docs/binary_spec/00_INVENTORY.json`.
> Covers all HP/TP healing commands, healing caps, resurrection & auto-revive hooks, HP/TP drains and drain enchants, turn-start HoT/DoT/equipment-regen ticks, after-battle recovery & status cleanup, `CActionItem` / `CActionPatternItem`, and all 107 `ItemResult` effect types (`0..106`).

---

## 1. HP & TP Healing Commands, Modifiers & Application (`M05.01` – `M05.03`)

### M05.01 Stat-Scaled Magic Healing (`CCommand_0103`), Doll Scaling & Healing Cap

- **Binary VA(s):** `0x4817c0..0x48187e` (`Command::CCommand_0103` apply), `0x48d730..0x48d92f` (`CalcHeal` helper), `0x48c5c0..0x48c632` (`ApplyHealCap` helper)
- **Calls:** `0x48d730` (`CalcHeal`), `0x48c5c0` (`ApplyHealCap`), `0x47e340` (`FindCommand`), `0x48cbf0` (`FindCommandIndex`), `0x490790` (`CRandom::Get`), `0x61edf4` (`__RTDynamicCast`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x420f10`, `M00.06`) via `CCommand_0103::vtable+0x18`
- **Typed Pseudocode:**
```text
function CCommand_0103_Apply(this: CCommand_0103*, seq: Vec<TaskResult>*, target: CGameStatusBase*, actCmds: Vec<CCommand*>*, actor: CGameStatusBase*):
    res = TaskResult_Init(target)                     // 0x419640; res.cmd = this; res.resultType = 2
    if target.vtable_0xe8_IsHealable():               // !IsDead() && !IsFullPetrified() (0x4fbd90)
        heal: i32 = CalcHeal_0x48d730(actCmds, actor, this.GetVal())
        res.hpHeal = heal                             // [res+0x0c]
        res.hpHealDisp = heal                         // [res+0x10]
    seq.push_back(res)

function CalcHeal_0x48d730(actCmds: Vec<CCommand*>*, actor: CGameStatusBase*, healPower: f32) -> i32:
    // 1. Doll caster bonus (0x48d73b..0x48d865):
    //    Checks RTTI __RTDynamicCast against CGamePlayerStatusETCDoll (0x7086d0),
    //    CGamePlayerStatusOtherETCDoll (0x708634), and CGameEnemyStatusETCDoll (0x708608).
    magicHealMod: f32 = 0.0f
    if IsDoll(actor):
        dollBonus: f32 = (cmd286 = FindCommand(actCmds, 0x11e)) ? cmd286.GetVal() : 0.0f // 286 Doll Bonus
        e304: f32 = f32(u32_to_f64(actor.GetEnchantCount(0x130))) * 0.02f                // 304 Doll efficacy UP
        e305: f32 = f32(u32_to_f64(actor.GetEnchantCount(0x131))) * 0.01f                // 305 Doll efficacy MiniUP
        enchBonus: f32 = min(0.05f, e304 + e305) * 20.0f
        healPower = healPower + dollBonus * 20.0f + enchBonus

    // 2. Variance roll (1 RNG draw) & Magic Heal Modifier passive 245 (0xf5) (0x48d86b..0x48d8bb):
    variance: f32 = f32(GlobalRng_0x816ce8.Rand(5) + 48) / 100.0f // 0x30..0x34 -> 0.48f..0.52f
    if cmd245 = actor.GetCommand(0, 0xf5):                        // 245 Magic Heal Modifier
        magicHealMod = cmd245.GetVal()

    // 3. RES stat scaling & Fixed Healing 9 override (0x48d8bb..0x48d927):
    _ = actor.GetStat(3)                                          // vtable+0x34(3) RES (unused first call)
    resStat: i32 = actor.GetStat(3)                               // vtable+0x34(3) RES
    rawHeal: f32 = f32(resStat) * variance * healPower * (magicHealMod + 1.0f)
    if cmd9 = FindCommand(actCmds, 9):                            // 9 (0x09) Fixed Healing override
        rawHeal = cmd9.GetVal()
    return ApplyHealCap_0x48c5c0(trunc0(rawHeal), actCmds, actor) // cvttss2si

function ApplyHealCap_0x48c5c0(heal: i32, actCmds: Vec<CCommand*>*, actor: CGameStatusBase*) -> i32:
    idx: i32 = FindCommandIndex(actCmds, 0x127)                   // 295 Healing Cap
    if idx != -1:
        cap: i32 = trunc0(actCmds[idx].GetVal())                  // cvttss2si
        if cmd317 = actor.GetCommand(0, 0x13d):                   // 317 Healing Cap UP
            cap += trunc0(f32(cap) * cmd317.GetVal())
        if heal > cap:
            heal = cap
    return heal
```
- **Program Evidence:**
```asm
00481815  mov      eax, dword ptr [eax + 0xe8]
0048181b  call     eax
0048181d  test     al, al
0048181f  je       0x481843
00481838  call     0x48d730
0048d7a1  mov      edx, 0x11e
0048d7cd  push     0x130
0048d7ff  mulss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
0048d813  movss    xmm1, dword ptr [0x6d92ec]    ; float 0.05
0048d821  mulss    xmm2, dword ptr [0x6d948c]    ; float 20
0048d847  mulss    xmm0, dword ptr [0x6d92d4]    ; float 0.01
0048d855  minss    xmm1, xmm0
0048d871  push     5
0048d873  call     0x490790
0048d878  add      eax, 0x30
0048d87d  push     0xf5
0048d88d  divss    xmm0, dword ptr [0x6d9540]    ; float 100
0048d8bf  push     3
0048d8c1  call     dword ptr [eax + 0x34]
0048d8d3  mov      edx, 9
0048d8ff  call     0x47e340
0048d91d  cvttss2si ecx, xmm0
0048d922  call     0x48c5c0
0048c5c7  mov      edx, 0x127
0048c5ce  call     0x48cbf0
0048c5e8  push     0x13d
0048c5f1  cvttss2si edi, dword ptr [esp + 0xc]
0048c620  cvttss2si ecx, dword ptr [esp + 8]
0048c626  add      edi, ecx
0048c628  cmp      esi, edi
0048c62a  cmovg    esi, edi
```

---

### M05.02 Fixed, Percentage, TP Transfer & Nurse/Purge Healing Commands (`9`, `104`, `106`, `128`, `129`, `130`, `131`, `132`, `235`, `426`)

- **Binary VA(s):** `0x47fb70..0x47fc23` (`CCommand_0009`), `0x481890..0x481944` (`CCommand_0104`), `0x481a20..0x481d68` (`CCommand_0106`), `0x483a60..0x483b29` (`CCommand_0128`), `0x483b30..0x483c10` (`CCommand_0129`), `0x483c20..0x483d10` (`CCommand_0130`), `0x483d20..0x483dee` (`CCommand_0131`), `0x483e00..0x483ed7` (`CCommand_0132`), `0x48a430..0x48a638` (`CCommand_0235`), `0x48b120..0x48b1de` (`CCommand_0426`), `0x6cc79c..0x6cc7b7` (7-entry ailment purge table)
- **Calls:** `0x48c5c0` (`ApplyHealCap`), `0x61e650` (`round_f32_to_i32`), `0x61edf4` (`__RTDynamicCast`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x420f10`, `M00.06`) via `CCommand::vtable+0x18`
- **Typed Pseudocode:**
```text
// Every healing/recovery CCommand constructs TaskResult (resultType = 2) and writes either
// HP heal ([res+0x0c/+0x10]) or TP heal ([res+0x14/+0x18]). All conversions use trunc0 unless noted.

// 9 (0x009) Fixed Healing (0x47fb70): NO Healing Cap
if target.vtable_0xe8_IsHealable():
    res.hpHeal = res.hpHealDisp = trunc0(this.GetVal())

// 104 (0x068) Full Heal (0x481890): NO Healing Cap
if target.vtable_0xe8_IsHealable():
    res.hpHeal = res.hpHealDisp = target.GetMaxHP() - target.GetCurHP()

// 128 (0x080) HP Recovery (% MaxHP, 0x483a60): NO Healing Cap
if target.vtable_0xe8_IsHealable():
    res.hpHeal = res.hpHealDisp = trunc0(f32(target.GetMaxHP()) * this.GetVal())

// 132 (0x084) Heal Percent HP (0x483e00): APPLIES Healing Cap 295 + 317!
if target.vtable_0xe8_IsHealable():
    raw: i32 = trunc0(f32(target.GetMaxHP()) * this.GetVal())
    res.hpHeal = res.hpHealDisp = ApplyHealCap_0x48c5c0(raw, actCmds, actor)

// 131 (0x083) Heal Enemy (0x483d20): enemy-only fixed HP heal
if dynamic_cast<CGameEnemyStatus*>(target) != null and target.vtable_0xe8_IsHealable(): // RTTI 0x707dfc
    res.hpHeal = res.hpHealDisp = trunc0(this.GetVal())

// 129 (0x081) TP Recovery (% MaxTP, 0x483b30): player-only
if dynamic_cast<CGamePlayerStatusBase*>(target) != null and target.vtable_0xe8_IsHealable(): // RTTI 0x707da8
    res.tpHeal = res.tpHealDisp = trunc0(f32(target.MaxTP) * this.GetVal())            // [target+0x18]

// 130 (0x082) Pass All TP (0x483c20): player-only target, unconditionally drains actor TP to 0
if dynamic_cast<CGamePlayerStatusBase*>(target) != null and target.vtable_0xe8_IsHealable():
    res.tpHeal = res.tpHealDisp = trunc0(f32(actor.CurTP) * this.GetVal())             // [actor+0x14]
actor.CurTP = 0                                                                        // unconditional!
actor.vtable_0x108_Recalc()

// 426 (0x1aa) Fixed TP Recovery (0x48b120): player-only; NO vtable+0xe8 check here
// (dead targets are still blocked in CCommand::Execute at 0x47eda3; full-petrified alive targets are NOT blocked!)
if dynamic_cast<CGamePlayerStatusBase*>(target) != null:
    res.tpHeal = res.tpHealDisp = trunc0(this.GetVal())

// 106 (0x06a) Nurse (0x481a20) & 235 (0x0eb) Perdurabo (0x48a430):
// Table 0x6cc79c = [113 (Poison), 115 (Paralysis), 117 (Silence), 114 (Freeze), 116 (Sleep), 120 (Petrify), 122 (Slow)]
// CCommand_0106:
level: u32 = round_f32_to_i32(this.GetVal())          // 0x61e650
n: u32 = min(level, 7u)
for i in 0 .. n - 1:
    if cmd = target.GetCommand(0, Table_0x6cc79c[i]): removeList.push(cmd)
if level == 8u:
    removeList.append(target.vtable_0x90_GetDebuffs())
// Emits one removal TaskResult per entry in removeList (resultType = 2, removeCmdId = cmd.GetId(), flag38 = 0)
// CCommand_0235 (0x48a430): iterates 0 .. level-1 over Table_0x6cc79c via vtable+0x50 (HasCommand);
// if level >= 8u, additionally appends all entries from target.vtable_0x90_GetDebuffs().
```
- **Program Evidence:**
```asm
0047fbc5  mov      eax, dword ptr [eax + 0xe8]
0047fbcb  call     eax
0047fbdd  cvttss2si eax, dword ptr [ebp + 0x10]
004818fe  call     dword ptr [edx + 0x24]
00481901  sub      esi, eax
00481aa3  call     0x61e650
00481aaa  mov      edx, 7
00481ab4  cmova    eax, edx
00481ad3  push     dword ptr [esi*4 + 0x6cc79c]
00481b12  cmp      ecx, 8
00481b39  call     dword ptr [eax + 0x90]
00483ac5  call     dword ptr [eax + 0x28]
00483ae3  cvttss2si eax, dword ptr [ebp + 0x10]
00483bb0  mov      esi, dword ptr [esi + 0x18]
00483ca4  mov      esi, dword ptr [edi + 0x14]
00483ccd  mov      dword ptr [edi + 0x14], 0
00483d69  push     0x707dfc
00483e89  cvttss2si ecx, dword ptr [ebp + 0x10]
00483e8e  call     0x48c5c0
0048b169  push     0x707da8
0048b198  cvttss2si eax, dword ptr [ebp + 0x10]
```

---

### M05.03 HP/TP Clamping, Petrification Gating, TP Conversion (`257`, `E72`/`E73`) & Defend Regen (`E257`/`E292`)

- **Binary VA(s):** `0x4f9800..0x4f982d` (`CGameStatusBase::SetHP`), `0x4f9830..0x4f9871` (`CGameStatusBase::AddHP`), `0x4f1c80..0x4f1cca` (`CGameEnemyStatus::AddHP`), `0x4f9890..0x4f98b8` (`CGameStatusBase::AddTP`), `0x4f98e0..0x4f98ea` (`IsDead`), `0x4fb600..0x4fb63f` (`IsFullPetrified`), `0x4fbd90..0x4fbdb5` (`IsHealable`), `0x47e500..0x47edef` (`CCommand::Execute` TP conversion & HP/TP apply), `0x419730..0x4198c5` (`CActionDefense` regen enchants)
- **Calls:** `0x4f9830` / `0x4f1c80` (`AddHP`), `0x4f9890` (`AddTP`), `0x4f5fa0` / `0x4fc890` (`OnDeath` `vtable+0x114`), `0x4f6980` (`OnRevive` `vtable+0x118`), `0x4e3f80` (`CBattle::TakeDamage`), `0x47e430`
- **CalledBy:** `CCommand::Execute` (`0x47e500`, `M00.06`), `CBattleBase::Update` (`M00.03`), `CBattleBase::End` (`M00.09`), `CItemResult::*` (`M05.10`), `CActionDefense` (`M00.04`)
- **Typed Pseudocode:**
```text
function IsDead_0x4f98e0(u: CGameStatusBase*) -> bool:               // vtable+0x38
    return u.GetCurHP() <= 0

function IsFullPetrified_0x4fb600(u: CGameStatusBase*) -> bool:      // vtable+0xc8
    cmd120 = u.GetCommand(0, 0x78)                                   // 120 Petrification
    if cmd120 == null: return false
    return (dynamic_cast<CCommand_0120*>(cmd120).GetStage() >= 3u)   // vtable+0xb0 >= 3

function IsHealable_0x4fbd90(u: CGameStatusBase*) -> bool:           // vtable+0xe8
    return !u.IsDead() and !u.IsFullPetrified()

function AddHP_0x4f9830(u: CGameStatusBase*, delta: i32):            // vtable+0x20
    oldHp: i32 = u.CurHP                                             // [u+0x0c]
    u.CurHP = max(0, oldHp + delta)                                  // cmovns clamps < 0 to 0
    u.vtable_0x108_Recalc()
    u.CurHP = min(u.CurHP, u.MaxHP)                                  // [u+0x10]
    u.vtable_0x114_OnDeath()                                         // 0x4f5fa0 (Player) / 0x4fc890 (Enemy)
    u.vtable_0x118_OnRevive(oldHp)                                   // 0x4f6980 (Player) / no-op (Enemy)
    // CGameEnemyStatus::AddHP (0x4f1c80) additionally calls 0x4f2320(1) at end.

function SetHP_0x4f9800(u: CGameStatusBase*, newHp: i32):            // vtable+0x1c
    oldHp: i32 = u.CurHP
    u.CurHP = newHp
    u.vtable_0x108_Recalc()
    u.vtable_0x114_OnDeath()
    u.vtable_0x118_OnRevive(oldHp)

function AddTP_0x4f9890(u: CGameStatusBase*, delta: i32):
    u.CurTP = max(0, u.CurTP + delta)                                // [u+0x14]
    u.vtable_0x108_Recalc()
    u.CurTP = min(u.CurTP, u.MaxTP)                                  // [u+0x18]

function CCommand_Execute_RecoveryAndConversion(seq: Vec<TaskResult>*, slotIdx: i32, battleInfo: BattleInfo*):
    // 1. Damage-to-TP Conversion (0x47e634..0x47e750): ONLY inspects seq[0] when seq[0].hpDamage != 0x7fffffff:
    if !seq.empty() and seq[0].hpDamage != 0x7fffffff:
        t = seq[0].target; dmg = seq[0].hpDamage; tpGain: i32 = 0
        if cmd257 = t.GetCommand(0, 0x101):                          // 257 TP Conversion
            tpGain = trunc0(f32(dmg) * cmd257.GetVal())
            if tpGain == 0: tpGain = 1
        e72: f32 = f32(u32_to_f64(t.GetEnchantCount(0x48))) * 0.05f  // 72 Convert dmg to TP
        e73: f32 = f32(u32_to_f64(t.GetEnchantCount(0x49))) * 0.10f  // 73 Convert dmg to big TP
        rate: f32 = e72; minFloor: i32 = 1
        if e73 > 0.0f:
            rate += e73; minFloor = 5
        if rate > 0.0f:
            tpGain += trunc0(f32(dmg) * min(0.50f, rate))
            if tpGain < minFloor: tpGain = minFloor
        if tpGain > 0 and slotIdx != -1:
            seq[slotIdx].tpHeal = seq[slotIdx].tpHealDisp = tpGain
    // 2. When slotIdx == -1 (0x47e750..0x47e9b7): coalesces all hpHeal (+0x0c/+0x10) and tpHeal (+0x14/+0x18)
    //    entries sharing the same target pointer into the first entry for that target.
    // 3. Per-entry application (0x47ed43..0x47edea):
    //    - HP heal ([r+0x0c] != 0x7fffffff): calls r.target.AddHP(r.hpHeal) UNCONDITIONALLY (allows Resurrect 105).
    //    - TP heal ([r+0x14] != 0x7fffffff): ONLY if !r.target.IsDead() (vtable+0x38 == 0), calls AddTP(r.tpHeal).

function CActionDefense_RegenEnchants_0x419730(actor: CGameStatusBase*):
    if actor.GetEnchantCount(0x101) > 0:                             // Enchant 257: HP recovers while defending
        hp: i32 = max(10, trunc0(f32(actor.GetMaxHP()) * 0.20f))
        actor.AddHP(hp)
    if actor.GetEnchantCount(0x124) > 0:                             // Enchant 292: TP recovers while defending
        tp: i32 = max(5, trunc0(f32(actor.MaxTP) * 0.10f))
        actor.CurTP = clamp(actor.CurTP + tp, 0, actor.MaxTP)        // inline AddTP + vtable+0x108
```
- **Program Evidence:**
```asm
004f983d  add      edx, esi
004f983f  cmovns   eax, edx
004f9852  cmp      dword ptr [edi + 0xc], eax
004f9855  cmovle   eax, dword ptr [edi + 0xc]
004f985e  call     dword ptr [eax + 0x114]
004f9869  call     dword ptr [eax + 0x118]
004fb603  push     0x78
004fb633  cmp      eax, 3
004fb636  cmovb    esi, ecx
004fbd95  mov      eax, dword ptr [eax + 0x38]
004fbda2  mov      eax, dword ptr [eax + 0xc8]
0047e64d  push     0x101
0047e682  test     edi, edi
0047e684  cmove    edi, eax
0047e689  push     0x48
0047e695  push     0x49
0047e6f9  mov      ecx, 5
0047e70e  movss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0047e72c  cmp      edi, ecx
0047e72e  cmovl    edi, ecx
0047ed43  mov      edx, dword ptr [ebx + 0xc]
0047ed57  call     dword ptr [eax + 0x20]
0047eda7  mov      eax, dword ptr [eax + 0x38]
0047edc1  call     0x4f9890
004197ae  push     0x101
004197f3  mulss    xmm0, dword ptr [0x6d9324]    ; float 0.2
004197ff  cmp      esi, eax
00419801  cmovl    esi, eax
00419843  push     0x124
0041988c  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
00419898  cmp      edi, eax
0041989a  cmovl    edi, eax
```

---

## 2. Resurrection, Auto-Revive, Sacrifice & HP/TP Drain (`M05.04` – `M05.05`)

### M05.04 Resurrection (`105`), Resuscitate (`188`), Undaunted Spirit (`355`), Sacrifice (`77`) & Death/Revive Hooks

- **Binary VA(s):** `0x481950..0x481a16` (`CCommand_0105` Resurrect), `0x47f8f2..0x47fa4c` (`Resuscitate 188` in `CCommand::Execute`), `0x438495..0x4386ff` (`Undaunted Spirit 355` in `TurnPhaseNo 22`), `0x481060..0x481150` (`CCommand_0077` Sacrifice), `0x4f5fa0..0x4f60b6` (`OnDeath` Player `vtable+0x114`), `0x4fc890..0x4fc9a1` (`OnDeath` Base/Enemy), `0x4f6980..0x4f69db` (`OnRevive` Player `vtable+0x118`)
- **Calls:** `0x4f9830` (`AddHP`), `0x47e500` (`CCommand::Execute`), `0x505ac0` (`Rand(100)`), `0x43c110`/`0x43c600`/`0x43c9b0` (cancel Dance/Puppet/Geass), `0x4e4800` (party passive recalc), `0x43cfb0` (battle revive re-sync)
- **CalledBy:** `CActionPatternBase::_Task` (`M00.06`), `CCommand::Execute` (`0x47e500`), `CBattleBase::Update` (`TurnPhaseNo 22`, `M00.03`), `AddHP` / `SetHP` (`M05.03`)
- **Typed Pseudocode:**
```text
// 1. CCommand_0105 Resurrect (0x481950):
function CCommand_0105_Apply(this, seq, target, actCmds, actor):
    res = TaskResult_Init(target); res.cmd = this; res.resultType = 2
    if target.vtable_0x38_IsDead():                          // strictly gates on CurHP <= 0 (does NOT check 0xc8!)
        hp: i32 = trunc0(f32(target.GetMaxHP()) * this.GetVal()) // no min-1 clamp here; val > 0 required
        res.hpHeal = res.hpHealDisp = hp
    seq.push_back(res)

// 2. Resuscitate 188 (0xbc) Auto-Revive on Death inside CCommand::Execute (0x47e5b2..0x47e631 & 0x47f8f2..0x47f9d9):
//    At entry to CCommand::Execute, records unique targets `u` and `wasAlive[i] = !u.IsDead()`.
//    After all TaskResult entries execute:
for i in 0 .. uniqueTargets.size() - 1:
    u = uniqueTargets[i]
    if u.IsDead() and wasAlive[i] != 0:                      // unit died during this Execute batch
        if cmd188 = u.GetCommand(0, 0xbc):                   // 188 Resuscitate
            u.AddHP(trunc0(f32(u.GetMaxHP()) * cmd188.GetVal())) // revives immediately & fires OnRevive!
            u.vtable_0x64_RemoveStatus(cmd188.GetCommandId())    // consumes status 188

// 3. Undaunted Spirit 355 (0x163) Turn-Start Auto-Revive in CBattleBase::Update TurnPhaseNo 22 (0x438495..0x4386ff):
deadUnits = [u for u in battle.units if u.status.IsDead()]
for u in deadUnits:
    if u.isPlayerSide == actor.isPlayerSide:                 // same side as current turn actor
        if cmd355 = u.status.GetCommand(0, 0x163):           // 355 Undaunted Spirit on the DEAD unit
            if Rand_0x505ac0(100) < trunc0(cmd355.GetVal() * 100.0f): // 1 RNG draw per eligible dead ally
                ExecuteHeal(u.status, hpHeal = 1)            // 0x47e500 -> revives at exactly 1 HP!
                battle.vtable_0x24_SortTime(1, 1)
                battle.PhaseNo = 14

// 4. CCommand_0077 Sacrifice (0x481060):
function CCommand_0077_Apply(this, seq, target, actCmds, actor):
    res = TaskResult_Init(target); res.cmd = this; res.resultType = 2
    if target == actor:
        for entry in seq:                                    // wipes all prior HP heals in sequence!
            entry.hpHeal = 0x7fffffff
            entry.hpHealDisp = 0x7fffffff
        res.hpDamage = target.GetMaxHP()                     // [res+0x1c] = MaxHP (kills caster)
    seq.push_back(res)

// 5. Death & Revive Status Cleanup Hooks (fired at end of AddHP / SetHP):
//    OnDeath (vtable+0x114, 0x4f5fa0 Player / 0x4fc890 Enemy):
//      if u.IsDead():
//          u.vtable_0x6c_ClearAllStatuses(1, 1)             // purges active battle/ailment statuses
//          if inBattle: cancel Dance (0x43c110), Puppet (0x43c600), Geass (0x43c9b0), Song, Chant
//    OnRevive (vtable+0x118, 0x4f6980 Player only; Enemy is no-op 0x414570):
//      if !u.IsDead() and oldHp == 0:
//          u.vtable_0x58_ReapplyPassives()
//          u.vtable_0x130_RecalcEquipmentAndPassives()
//          RecalcPartyPassives_0x4e4800()
//          if inBattle: battle.OnUnitRevived_0x43cfb0(u)
```
- **Program Evidence:**
```asm
004819a5  mov      eax, dword ptr [eax + 0x38]
004819a8  call     eax
004819aa  test     al, al
004819ac  je       0x4819db
004819d0  cvttss2si eax, dword ptr [ebp + 0x10]
0047f936  push     0xbc
0047f976  cvttss2si eax, dword ptr [ebp - 0x2c]
0047f97c  call     dword ptr [edx + 0x20]
0047f9d6  call     dword ptr [esi + 0x64]
0043852d  push     0x163
00438557  call     0x505ac0
0043856b  cvttss2si esi, xmm0
0043857e  cmp      edi, esi
00438580  jge      0x4386cb
00438668  mov      dword ptr [ebp - 0xb4], 1
00438698  call     0x47e500
004810b4  cmp      ebx, dword ptr [ebp + 0x18]
004810de  mov      dword ptr [eax + edi - 0x4c], 0x7fffffff
00481112  call     dword ptr [eax + 0x28]
00481115  mov      dword ptr [ebp - 0x4c], eax
004f5fbd  push     1
004f5fbf  push     1
004f5fc1  call     dword ptr [eax + 0x6c]
004f698e  cmp      dword ptr [esp + 8], 0
004f6993  jne      0x4f69da
004f6999  call     dword ptr [eax + 0x58]
004f69a0  call     dword ptr [eax + 0x130]
004f69a6  call     0x4e4800
004f69d5  call     0x43cfb0
```

---

### M05.05 HP & TP Drain Commands (`75`, `76`) & Normal-Attack Drain Enchants (`161..164`)

- **Binary VA(s):** `0x42152e..0x421698` (Normal-attack drain enchant synthesis in `CActionPatternBase::_Task`), `0x422eb8..0x423100` (HP/TP drain evaluation in `CActionPatternBase::_Task`), `0x557e00..0x557e26` (`IsUndeadEnemy`), `0x4151e0` / `0x4151f0` (`vtable+0xfc` `IsETC/Doll`)
- **Calls:** `0x5587c0` (enemy param lookup), `0x557e00` (`IsUndeadEnemy`), `0x47e340` (`FindCommand`), `0x47b220` (`CCommand` factory), `0x47e500` (`CCommand::Execute`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x420f10`, `M00.06`) after `_AfterHit2` (`0x423810`)
- **Typed Pseudocode:**
```text
// 1. Normal-Attack Drain Enchant Synthesis (0x42152e..0x421698):
//    Note: In the binary, commands 10 (0x0a) and 11 (0x0b) are Defend and Escape, and 135 (0x87) is unused.
//    All HP/TP drains in CActionPatternBase::_Task use commands 75 (0x4b, Absorb HP) and 76 (0x4c, Absorb TP).
canDrain: bool = (targetEnemyId == -1) or (GetEnemyParam_0x5587c0(targetEnemyId).race10 != 5) // race 5 = Undead
if canDrain:
    if actor.GetEnchantCount(0xa1) > 0 and FindCommand(actCmds, 0x4b) == null: // Enchant 161: lots of HP
        actCmds.push(CreateCommand(0x4b, val = 0.50f))                         // takes priority over 162
    if actor.GetEnchantCount(0xa2) > 0 and FindCommand(actCmds, 0x4b) == null: // Enchant 162: HP
        actCmds.push(CreateCommand(0x4b, val = 0.15f))
    if actor.GetEnchantCount(0xa3) > 0 and FindCommand(actCmds, 0x4c) == null: // Enchant 163: lots of TP
        actCmds.push(CreateCommand(0x4c, val = 0.20f))                         // takes priority over 164
    if actor.GetEnchantCount(0xa4) > 0 and FindCommand(actCmds, 0x4c) == null: // Enchant 164: TP
        actCmds.push(CreateCommand(0x4c, val = 0.05f))

// 2. Drain Execution after _AfterHit2 (0x422eb8..0x423100):
//    Requires hit applied HP damage (res.hpDamage != 0x7fffffff) and target survived guard flag == 0.
//    Blocked if IsUndeadEnemy(targetEnemyId) ([enemyParam+0x28] == 5 at 0x557e1c) OR actor.vtable_0xfc_IsETC() != 0 (Dolls!).
if res != null and res.hpDamage != 0x7fffffff:
    if cmd75 = FindCommand(actCmds, 0x4b):                                     // 75 Absorb HP
        if !IsUndeadEnemy_0x557e00(targetEnemyId) and !actor.vtable_0xfc_IsETC():
            drain: i32 = trunc0(f32(res.hpDamage) * cmd75.GetVal())
            curHp: i32 = target.GetCurHP()                                     // pre-damage CurHP
            if drain > curHp: drain = curHp                                    // capped at target CurHP
            if drain <= 0:    drain = 1                                        // min 1 HP
            seq[1].target = target; seq[1].flag34 = 1u8
            seq[2].target = actor;  seq[2].hpHeal = seq[2].hpHealDisp = drain

    if cmd76 = FindCommand(actCmds, 0x4c):                                     // 76 Absorb TP
        if !IsUndeadEnemy_0x557e00(targetEnemyId) and !actor.vtable_0xfc_IsETC():
            tpDrain: i32 = trunc0(f32(res.hpDamage) * cmd76.GetVal())
            if tpDrain <= 0: tpDrain = 1                                       // min 1 TP; NO clamp to target CurTP
            seq[3].target = target; seq[3].flag35 = 1u8
            if dynamic_cast<CGamePlayerStatusBase*>(target) != null:           // drains TP only from players
                seq[4].target = target; seq[4].tpDamage = seq[4].tpDamageDisp = tpDrain
            if dynamic_cast<CGamePlayerStatusBase*>(actor) != null:            // restores TP only to players
                seq[5].target = actor;  seq[5].tpHeal = seq[5].tpHealDisp = tpDrain
```
- **Program Evidence:**
```asm
00421547  push     0xa1
0042155a  mov      edx, 0x4b
0042156f  movss    xmm2, dword ptr [0x6d9348]    ; float 0.5
0042159c  push     0xa2
004215c4  movss    xmm2, dword ptr [0x6d931c]    ; float 0.15
004215f1  push     0xa3
00421619  movss    xmm2, dword ptr [0x6d9324]    ; float 0.2
00421646  push     0xa4
0042166e  movss    xmm2, dword ptr [0x6d92ec]    ; float 0.05
00422eda  mov      edx, 0x4b
00422efe  call     0x557e00
00422f1a  mov      eax, dword ptr [eax + 0xfc]
00422f54  cvttss2si esi, dword ptr [ebp + 0x70]
00422f5c  cmp      esi, eax
00422f5e  jle      0x422f69
00422f69  test     esi, esi
00422f73  cmovle   esi, eax
00422fc7  mov      edx, 0x4c
00423047  cvttss2si eax, dword ptr [ebp + 0x70]
0042304e  cmovle   eax, ecx
00557e1c  cmp      dword ptr [eax + 0x28], 5
00557e20  sete     al
```

---

## 3. Turn-Start HoT, DoT & Equipment Regen Ticks (`M05.06`)

### M05.06 Turn-Start HoT Commands (`215`, `216`, `246`, `247`), Regen Enchants (`144..149`, `296`) & Poison DoT (`113`)

- **Binary VA(s):** `0x437b0c..0x437ed6` (`CBattleBase::Update` Inner `TurnPhaseNo 16` via `0x439820[16]`), `0x4894a0..0x48956e` (`CCommand_0215` Carol `vtable+0x0c`), `0x4895e0..0x4896c8` (`CCommand_0216` Chorale `vtable+0x0c`), `0x48a640..0x48a705` (`CCommand_0246` HP Regen `vtable+0x0c`), `0x48a710..0x48a7d9` (`CCommand_0247` TP Regen `vtable+0x0c`), `0x43841e..0x438495` (`TurnPhaseNo 21` Poison dispatch), `0x482150..0x48228f` (`CCommand_0113` Poison tick)
- **Calls:** `0x48bf90` (`GetSubBonus` for Song Bonus `279` / `0x117`), `0x505ac0` (`Rand(100)`), `0x47e500` (`CCommand::Execute`)
- **CalledBy:** `CBattleBase::Update` Inner Turn-Start State Machine (`0x436700`, `M00.03`: `TurnPhaseNo 16` at `0x439860`, `TurnPhaseNo 21` at `0x439874`)
- **Typed Pseudocode:**
```text
// === TurnPhaseNo 16 (0x437b0c..0x437ed6) — HoT Commands & Equipment Regen ===
// (Note: TurnPhaseNo 11 at 0x436eb0 is Temptation 203; HoT/Regen executes at TurnPhaseNo 16.)
function TurnPhase16_HoTAndRegen(battle: CBattleBase*, actor: BattleUnit_s*):
    seq = [TaskResult_Init(actor.status)]                           // dummy slot 0

    // 1. Active commands with vtable+0x80() == true (EXACTLY 4 CCommand subclasses in the entire binary):
    for cmd in actor.status.activeStatuses:
        if cmd.vtable_0x80_IsTurnStartTick():                       // 0x4151e0 on 215, 216, 246, 247 only
            cmd.vtable_0x0c_OnTurnStart(&seq, battle.battleInfo, actor.status)
    // Exact vtable+0x0c formulas (all require battleInfo.battle != null):
    //   - 215 (0xd7) Carol (0x4894a0):
    //       sb: f32 = cmd.GetSubBonus_0x48bf90(0x117)              // 279 Song Bonus
    //       hpHeal = trunc0(cmd.GetVal() * (sb * 10.0f + 1.0f))
    //   - 216 (0xd8) Chorale (0x4895e0, CGamePlayerStatusBase only):
    //       sb: f32 = cmd.GetSubBonus_0x48bf90(0x117)
    //       tpHeal = trunc0(cmd.GetVal() + sb * 100.0f)            // ADDITIVE + sb * 100.0f!
    //   - 246 (0xf6) HP Regen (0x48a640):
    //       hpHeal = trunc0(f32(actor.status.GetMaxHP()) * cmd.GetVal())
    //   - 247 (0xf7) TP Regen (0x48a710, CGamePlayerStatusBase only):
    //       tpHeal = trunc0(cmd.GetVal())                          // FLAT TP, not % MaxTP!

    // 2. Equipment HP Regen Enchants (0x437bb5..0x437d7a):
    hpRegen: i32 = 0
    r144: f32 = f32(u32_to_f64(actor.status.GetEnchantCount(0x90))) * 0.04f // 144 HP recovery/turn
    if r144 > 0.0f: hpRegen = max(4, trunc0(f32(actor.status.GetMaxHP()) * r144))
    r145: f32 = f32(u32_to_f64(actor.status.GetEnchantCount(0x91))) * 0.02f // 145 Slight HP recovery
    if r145 > 0.0f: hpRegen += max(2, trunc0(f32(actor.status.GetMaxHP()) * r145))
    r148: f32 = f32(u32_to_f64(actor.status.GetEnchantCount(0x94))) * 0.08f // 148 Large HP recovery
    if r148 > 0.0f: hpRegen += max(10, trunc0(f32(actor.status.GetMaxHP()) * r148))
    if actor.status.GetEnchantCount(0x128) > 0:                             // 296 Rare full HP regen
        if Rand_0x505ac0(100) < 4:                                          // 4% chance (1 RNG draw)
            hpRegen += actor.status.GetMaxHP()
    if hpRegen > 0: seq.push(TaskResult_HpHeal(actor.status, hpRegen))

    // 3. Equipment TP Regen Enchants (0x437d7a..0x437e00):
    tpRegen: i32 = 4 * actor.status.GetEnchantCount(0x92)                   // 146 TP recovery/turn
                 + 2 * actor.status.GetEnchantCount(0x93)                   // 147 Slight TP recovery
                 + 6 * actor.status.GetEnchantCount(0x95)                   // 149 Large TP recovery
    if tpRegen > 0: seq.push(TaskResult_TpHeal(actor.status, tpRegen))

    // 4. Coalesces & executes via CCommand::Execute(seq, -1, battleInfo) (0x437eb4).

// === TurnPhaseNo 21 (0x43841e..0x438495) — Poison 113 (0x71) DoT Tick ===
function CCommand_0113_PoisonTick_0x482150(this: CCommand_0113*, seq: Vec<TaskResult>*, battleInfo: BattleInfo*, target: CGameStatusBase*):
    if this.skipFieldOnce != 0 and battleInfo.battle == null: return
    dmg: i32 = trunc0(f32(target.GetMaxHP()) * 0.05f)
    if dmg == 0 or dmg >= target.GetCurHP():                        // NON-LETHAL clamp; also triggers when MaxHP < 20!
        dmg = target.GetCurHP() - 1
    if !target.vtable_0xbc_IsHardIncapacitated() and dmg > 0:       // skips if Frozen/Asleep/Stunned or CurHP <= 1
        if dmg > 250: dmg = 250                                     // capped at 250 (0xfa)
        seq.push(TaskResult_HpDamage(target, dmg))
    this.skipFieldOnce = 0
```
- **Program Evidence:**
```asm
00437b83  mov      edx, dword ptr [edx + 0x80]
00437b89  call     edx
00437b9e  call     dword ptr [edx + 0xc]
00437bb8  push     0x90
00437be9  mulss    xmm0, dword ptr [0x6d92e8]    ; float 0.04
00437c09  mov      ecx, 4
00437c29  push     0x91
00437c53  mulss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
00437c73  mov      ecx, 2
00437c93  push     0x94
00437cbd  mulss    xmm0, dword ptr [0x6d9300]    ; float 0.08
00437cdd  mov      ecx, 0xa
00437cfd  push     0x128
00437d15  call     0x505ac0
00437d1a  cmp      eax, 4
00437d7d  push     0x92
00437d91  push     0x93
00437da6  push     0x95
004894e0  push     0x117
004894f1  mulss    xmm0, dword ptr [0x6d9468]    ; float 10
00489658  mulss    xmm0, dword ptr [0x6d9540]    ; float 100
0048966a  fadd     dword ptr [ebp + 0xc]
0048a6b1  cvttss2si esi, dword ptr [ebp + 0xc]
0048a783  cvttss2si esi, dword ptr [ebp + 0xc]
00482197  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0048219f  cvttss2si esi, xmm0
004821a3  test     esi, esi
004821a5  je       0x4821b2
004821ae  cmp      esi, eax
004821b0  jl       0x4821bc
004821b9  lea      esi, [eax - 1]
004821ed  mov      eax, 0xfa
004821ff  cmovg    esi, eax
```

---

## 4. After-Battle Recovery & Battle-End Cleanup (`M05.07`)

### M05.07 `CBattleBase::End` Party Recovery (`272`, `273`, `353`, `E193`, `E194`) & `ClearBattleStatuses` (`vtable+0x70`)

- **Binary VA(s):** `0x4b27ba..0x4b27d5` (battle-end gate), `0x43d650..0x43da55` (`CBattleBase::End`), `0x435df5..0x435e44` (`CBattleBase::~CBattleBase` unit cleanup loop), `0x43ffd0..0x440019` (`BattleUnit_s::Clear`), `0x4fa960..0x4fab45` (`CGameStatusBase::ClearBattleStatuses` `vtable+0x70`), `0x56c5e0..0x56c625` (`SkillPersistsOutOfBattle`)
- **Calls:** `0x48bf90` (`GetSubBonus` for `353` / `0x161`), `0x47e500` (`CCommand::Execute`), `0x43ffd0`, `0x4fa960`, `0x56c5e0`
- **CalledBy:** Battle scene teardown (`0x4b27d0`, `M00.09`), `CBattle::~CBattle` (`0x448c30` -> `0x435cf0`)
- **Typed Pseudocode:**
```text
function BattleEnd_Gate_0x4b27ba(battle: CBattleBase*):
    if GameManager.GetEventFlag(0xab) == 0u16:                      // vtable+0x200(0xab)
        CBattleBase_End_0x43d650(battle)

function CBattleBase_End_0x43d650(this: CBattleBase*):
    // 1. Aggregate party-wide after-battle recovery passives across IsHealable (alive & not full-petrified) members:
    hpSum272: f32 = 0.0f; hpBonus353: f32 = 0.0f
    tpSum273: f32 = 0.0f; tpBonus353: f32 = 0.0f
    for i in 0 .. GameManager.GetPartyCount() - 1:
        m = GameManager.GetPartyMember(i)
        if m.vtable_0xe8_IsHealable():                              // !IsDead() && !IsFullPetrified()
            if cmd272 = m.GetCommand(0, 0x110):                     // 272 Heal Everyone's HP
                hpSum272   += cmd272.GetVal()
                hpBonus353 += cmd272.GetSubBonus_0x48bf90(0x161)    // 353 Maximum Maid synergy
            if cmd273 = m.GetCommand(0, 0x111):                     // 273 Heal Everyone's TP
                tpSum273   += cmd273.GetVal()
                tpBonus353 += cmd273.GetSubBonus_0x48bf90(0x161)
    // 30% cap applies to 272/273 sums BEFORE adding 353 bonus!
    partyHpRate: f32 = min(0.30f, hpSum272) + hpBonus353
    partyTpRate: f32 = min(0.30f, tpSum273) + tpBonus353

    // 2. Apply recovery per IsHealable party member (dead & full-petrified members are skipped):
    for i in 0 .. GameManager.GetPartyCount() - 1:
        m = GameManager.GetPartyMember(i)
        if !m.vtable_0xe8_IsHealable(): continue
        seq = []
        hpRate: f32 = (m.GetEnchantCount(0xc1) > 0) ? 1.0f : partyHpRate // Enchant 193 -> 100% HP
        if hpRate > 0.0f:
            seq.push(TaskResult_HpHeal(m, max(1, trunc0(f32(m.GetMaxHP()) * hpRate))))
        tpRate: f32 = (m.GetEnchantCount(0xc2) > 0) ? 1.0f : partyTpRate // Enchant 194 -> 100% TP
        if tpRate > 0.0f:
            seq.push(TaskResult_TpHeal(m, max(1, trunc0(f32(m.MaxTP) * tpRate))))
        if !seq.empty():
            CCommand_Execute_0x47e500(&seq, -1, this)

function ClearBattleStatuses_0x4fa960(u: CGameStatusBase*):         // vtable+0x70, called by BattleUnit_s::Clear (0x43ffd8)
    for cmd in u.activeStatuses (in-place erase):
        if cmd.vtable_0x68_IsTrueAilment(): continue                // Ailments 113..122, 139 PERSIST after battle!
        skillId: i32 = cmd.vtable_0x34_GetSkillId()
        if skillId != -1:
            if skillId in (TechniqueTable_0x738a64 or MagicTable_0x738a58 or UniqueTable_0x738a54):
                if !SkillPersistsOutOfBattle_0x56c5e0(skillId):     // checks ([skillParam+0x48] >> 5) & 1
                    erase_and_delete(cmd)                           // battle-only skill buff/debuff REMOVED
            // Passives (not in those 3 tables) PERSIST.
        else:
            eAtkId: i32 = cmd.vtable_0x3c_GetEnemyAttackId()
            itemId: i32 = cmd.vtable_0x48_GetItemId()
            if itemId == -1 and eAtkId == -1: continue              // innate status PERSISTS
            if u32(itemId - 1000) <= 999u:                          // battle item IDs 1000..1999 REMOVED
                erase_and_delete(cmd)
            else if (EnemyAttackTable_0x7389d4[eAtkId].flags40 & 0x7) != 0: // bits 0..2 set -> REMOVED
                erase_and_delete(cmd)
    u.vtable_0x108_Recalc()
```
- **Program Evidence:**
```asm
004b27ba  push     0xab
004b27c9  test     ax, ax
004b27cc  jne      0x4b27d5
004b27d0  call     0x43d650
0043d6bc  mov      edx, dword ptr [edx + 0xe8]
0043d6cc  push     0x110
0043d6e8  push     0x161
0043d6f2  call     0x48bf90
0043d705  push     0x111
0043d751  movss    xmm0, dword ptr [0x6d9330]    ; float 0.3
0043d764  minss    xmm1, dword ptr [ebp - 0x10]
0043d769  minss    xmm0, dword ptr [ebp - 0x18]
0043d85e  push     0xc1
0043d8ae  cvttss2si esi, xmm0
0043d8b4  cmovle   esi, edi
0043d904  push     0xc2
0043d949  cvttss2si esi, xmm0
0043d99d  call     0x47e500
0043ffd8  call     dword ptr [eax + 0x70]
004fa989  mov      eax, dword ptr [eax + 0x68]
004faa30  call     0x56c5e0
004faa7e  add      eax, 0xfffffc18
004faa83  cmp      eax, 0x3e7
004faa88  jbe      0x4fab0c
004faaad  test     byte ptr [eax + 0x40], 1
0056c615  shr      eax, 5
0056c618  and      al, 1
```

---

## 5. `CActionItem`, `ItemResult` Dispatch (`0x50c570` / `0x50e538`) & All 107 Item Effect Types (`0..106`)

### M05.08 `CActionItem`, `CActionPatternItem`, Item Consumption (`274`) & `ItemResult` Factory (`0x50c570`)

- **Binary VA(s):** `0x41b5f0..0x41b710` (`CActionItem::Update` & special script item `0x375`), `0x42cc90..0x42cf84` (`CActionPatternItem::Update`, jump table `0x42cf8c`), `0x42cfe0..0x42d1a3` (`CActionPatternItem::_ConsumeItem`), `0x50c570..0x50e537` (`ItemResult` factory), `0x50e538..0x50e6e3` (107-entry jump table for item effect types `0..106`)
- **Calls:** `0x55b550` (item effect count), `0x55b5b0` (fetch effect type & float value), `0x50c570` (`CreateItemResult`), `0x490790` (`CRandom::Get`), `0x50a5b0` (`CItemResultBase` ctor)
- **CalledBy:** `CBattleBase::_CreateAction` (`0x43ea70` case 4 -> `CActionItem` `0x41b440`, `M00.04`), `CActionPatternU0008` (`0x42fa1b`), dungeon menu (`0x5915f6`)
- **Typed Pseudocode:**
```text
function CActionItem_Dispatch(action: CActionItem*):
    // Item ID 885 (0x375) runs a dedicated event script (/Script/Item0885.pck) instead of CActionPatternItem (0x41b694).
    // All other items run CActionPatternItem::Update (0x42cc90):
    effectCount: u32 = GetItemEffectCount_0x55b550(itemId)
    for effectIdx in 0 .. effectCount - 1:
        (effectType: u32, itemVal: f32) = GetItemEffect_0x55b5b0(itemId, isPlayerTarget, effectIdx)
        // Instantiates CItemResult* via factory 0x50c570 (jump table 0x50e538, bounds check effectType <= 0x6a):
        resultObj = CreateItemResult_0x50c570(effectType, itemVal, ...)
        while resultObj.vtable_0x04_Update(): yield                  // calls vtable+0x0c apply handler
        pattern.anyEffectSucceeded |= resultObj.flag1c
        pattern.escaped            |= resultObj.flag1d
    // After all effects complete, calls _ConsumeItem (0x42cfe0):
    ConsumeItem_0x42cfe0(pattern)

function ConsumeItem_0x42cfe0(pattern: CActionPatternItem*) -> bool:
    flags: u32 = ItemTable_0x7389f4[itemId].flags30
    shouldConsume: bool = ((flags >> 6) & 1) == 0                    // bit 6 = infinite/non-consumable
    if actor != null and shouldConsume:
        if cmd274 = actor.GetCommand(0, 0x112):                      // 274 Loss Rate (item conservation passive!)
            if GlobalRng_0x816ce8.Rand(100) < trunc0(cmd274.GetVal() * 100.0f): // 1 RNG draw
                shouldConsume = false                                // item NOT consumed!
                LogMessage(0x41)
    if shouldConsume:
        invItem = GameManager.FindInventoryItem(itemId)              // vtable+0x8c
        if invItem.GetCount() == 1:
            GameManager.RemoveInventoryItem(invItem, 1)              // vtable+0xb0
        else:
            invItem.DecrementCount(1)
    return didShowConservationLog
```
- **Program Evidence:**
```asm
0041b694  cmp      dword ptr [eax + 0xc], 0x375
0042ccdf  call     0x55b550
0042cd08  call     0x55b5b0
0042cda2  call     0x50c570
0042d00e  mov      eax, dword ptr [eax + 0x30]
0042d011  shr      eax, 6
0042d014  not      al
0042d016  and      al, 1
0042d032  push     0x112
0042d055  push     0x64
0042d05b  call     0x490790
0042d066  mulss    xmm0, dword ptr [0x6d9540]    ; float 100
0042d06e  cvttss2si ecx, xmm0
0042d072  cmp      eax, ecx
0042d074  jge      0x42d15c
0042d182  cmp      eax, 1
0042d191  call     dword ptr [edx + 0xb0]
0050c596  cmp      ecx, 0x6a
0050c599  ja       0x50e509
0050c59f  jmp      dword ptr [ecx*4 + 0x50e538]
```

---

### M05.09 Grouped Tabular Batch Rule: All 58 Skill-Casting `CItemResult*` Types (41 Direct Thunks + 17 Wrappers via `0x50b030`)

- **Binary VA(s):** `0x50b030..0x50b181` (`CItemResultBase::_SkillTask`, jump table `0x50b1a0`), `0x56c690..0x56c6ee` (`GetMaxSkillLevel`), `0x511560..0x51182e` (types `25..51` thunks & wrappers `35/36/39`), `0x513c30..0x51424f` (types `73..86` hardcoded-level wrappers), `0x5143d0..0x5144de` (types `90..106` thunks)
- **Calls:** `0x490790` (`CRandom::Get`), `0x56c690` (`GetMaxSkillLevel`), `0x61e650` (`round_f32_to_i32`), `0x41d2b0` (`CActionSkill` item-cast ctor)
- **CalledBy:** `CActionPatternItem::Update` (`0x42ce73`, `M05.08`)
- **Typed Pseudocode:**
```text
function CItemResultBase_SkillTask_0x50b030(this: CItemResultBase*, skillId: i32, useValAsLevel: bool, fixedLevel: i32) -> bool:
    // 5-state machine [this+0x38] in 0..4 (jump table 0x50b1a0):
    switch this.skillPhase:
        case 0: // 0x50b062 — Optional Probability Gate when useValAsLevel == false
            if !useValAsLevel:
                // Treats itemVal ([this+8]) as success probability [0..1]: 1 RNG draw!
                if GlobalRng_0x816ce8.Rand(100) >= trunc0(this.itemVal * 100.0f):
                    this.PrintFail_0x50a9b0()
                    this.skillPhase = 4
                    return true
            this.flag1c = 1u8                                        // succeeded
            this.skillPhase = 1
        case 1: // 0x50b0ad — Play item use animations (0x50a820) -> skillPhase = 2
        case 2: // 0x50b0cd — Resolve Skill Level & Construct CActionSkill (0x41d2b0)
            if useValAsLevel:
                lv: i32 = round_f32_to_i32(this.itemVal)             // 0x61e650
            else if fixedLevel != -1:
                lv = fixedLevel
            else:
                lv = GetMaxSkillLevel_0x56c690(skillId)              // counts non-zero level slots [param+0x4c..0x70]
            this.subSkill = new CActionSkill_0x41d2b0(skillId, lv, this.battleInfo, this.action.actor, &this.action.targetSlots)
            this.skillPhase = 3
        case 3: // 0x50b147 — Tick this.subSkill.Update() until false -> skillPhase = 4
        case 4: // 0x50b15e — Wait for message/effect completion -> return false

// Wrapper variants:
//   - Direct Thunks (41 types: 25..34, 37..38, 40..51, 90..106): 5-instruction call to 0x50b030(skillId, useValAsLevel, fixedLevel).
//   - Party-Buff Wrappers (3 types: 35, 36, 39): call 0x50b030(skillId, 0, -1), then emit party buff message when out of battle.
//   - Hardcoded-Level Wrappers (14 types: 73..86): overwrite this.itemVal = 5.0f (0x40a00000) or 10.0f (0x41200000),
//     call 0x50b030(skillId, 1, -1), and copy message 0xb7 on completion.
```

#### Complete Parameter Table of All 58 Skill-Casting `ItemResult` Types

| Type | Hex | Class | `apply_va` | `skillId` | `skillId` (hex) | `useValAsLevel` | `fixedLevel` | Mode / Override |
|---:|---|---|---|---:|---|---:|---:|---|
| 25 | `0x19` | `CItemResult_0033` | `0x511560` | 193 | `0xc1` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 26 | `0x1a` | `CItemResult_0034` | `0x511570` | 194 | `0xc2` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 27 | `0x1b` | `CItemResult_0035` | `0x511580` | 36 | `0x24` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 28 | `0x1c` | `CItemResult_0036` | `0x511590` | 175 | `0xaf` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 29 | `0x1d` | `CItemResult_0037` | `0x5115a0` | 197 | `0xc5` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 30 | `0x1e` | `CItemResult_0038` | `0x5115b0` | 5 | `0x05` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 31 | `0x1f` | `CItemResult_0039` | `0x5115c0` | 6 | `0x06` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 32 | `0x20` | `CItemResult_0040` | `0x5115d0` | 2 | `0x02` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 33 | `0x21` | `CItemResult_0041` | `0x5115e0` | 188 | `0xbc` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 34 | `0x22` | `CItemResult_0042` | `0x5115f0` | 191 | `0xbf` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 35 | `0x23` | `CItemResult_0043` | `0x511600` | 226 | `0xe2` | 0 | -1 | Wrapper (`val` = prob, Lv = Max) |
| 36 | `0x24` | `CItemResult_0044` | `0x511670` | 227 | `0xe3` | 0 | -1 | Wrapper (`val` = prob, Lv = Max) |
| 37 | `0x25` | `CItemResult_0045` | `0x5116e0` | 35 | `0x23` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 38 | `0x26` | `CItemResult_0046` | `0x5116f0` | 33 | `0x21` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 39 | `0x27` | `CItemResult_0047` | `0x511700` | 195 | `0xc3` | 0 | -1 | Wrapper (`val` = prob, Lv = Max) |
| 40 | `0x28` | `CItemResult_0048` | `0x511770` | 177 | `0xb1` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 41 | `0x29` | `CItemResult_0049` | `0x511780` | 198 | `0xc6` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 42 | `0x2a` | `CItemResult_0051` | `0x511790` | 200 | `0xc8` | 0 | 1 | Thunk (`val` = prob, Lv = 1) |
| 43 | `0x2b` | `CItemResult_0052` | `0x5117a0` | 201 | `0xc9` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 44 | `0x2c` | `CItemResult_0053` | `0x5117b0` | 202 | `0xca` | 0 | -1 | Thunk (`val` = prob, Lv = Max) |
| 45 | `0x2d` | `CItemResult_0054` | `0x5117c0` | 216 | `0xd8` | 0 | 1 | Thunk (`val` = prob, Lv = 1) |
| 46 | `0x2e` | `CItemResult_0055` | `0x5117d0` | 144 | `0x90` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 47 | `0x2f` | `CItemResult_0056` | `0x5117e0` | 148 | `0x94` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 48 | `0x30` | `CItemResult_0057` | `0x5117f0` | 152 | `0x98` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 49 | `0x31` | `CItemResult_0058` | `0x511800` | 156 | `0x9c` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 50 | `0x32` | `CItemResult_0059` | `0x511810` | 160 | `0xa0` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 51 | `0x33` | `CItemResult_0060` | `0x511820` | 164 | `0xa4` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 73 | `0x49` | `CItemResult_0093` | `0x513c30` | 179 | `0xb3` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 74 | `0x4a` | `CItemResult_0094` | `0x513ca0` | 180 | `0xb4` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 75 | `0x4b` | `CItemResult_0095` | `0x513d10` | 181 | `0xb5` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 76 | `0x4c` | `CItemResult_0096` | `0x513d80` | 182 | `0xb6` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 77 | `0x4d` | `CItemResult_0097` | `0x513df0` | 183 | `0xb7` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 78 | `0x4e` | `CItemResult_0098` | `0x513e60` | 184 | `0xb8` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 79 | `0x4f` | `CItemResult_0099` | `0x513ed0` | 185 | `0xb9` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 80 | `0x50` | `CItemResult_0100` | `0x513f40` | 186 | `0xba` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 81 | `0x51` | `CItemResult_0104` | `0x513fb0` | 201 | `0xc9` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 82 | `0x52` | `CItemResult_0105` | `0x514020` | 197 | `0xc5` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 83 | `0x53` | `CItemResult_0106` | `0x514090` | 35 | `0x23` | 1 | -1 | Wrapper (forces `val = 10.0f`) |
| 84 | `0x54` | `CItemResult_0107` | `0x514100` | 36 | `0x24` | 1 | -1 | Wrapper (forces `val = 10.0f`) |
| 85 | `0x55` | `CItemResult_0108` | `0x514170` | 198 | `0xc6` | 1 | -1 | Wrapper (forces `val = 10.0f`) |
| 86 | `0x56` | `CItemResult_0109` | `0x5141e0` | 202 | `0xca` | 1 | -1 | Wrapper (forces `val = 5.0f`) |
| 90 | `0x5a` | `CItemResult_0120` | `0x5143d0` | 143 | `0x8f` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 91 | `0x5b` | `CItemResult_0121` | `0x5143e0` | 145 | `0x91` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 92 | `0x5c` | `CItemResult_0122` | `0x5143f0` | 146 | `0x92` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 93 | `0x5d` | `CItemResult_0123` | `0x514400` | 147 | `0x93` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 94 | `0x5e` | `CItemResult_0124` | `0x514410` | 149 | `0x95` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 95 | `0x5f` | `CItemResult_0125` | `0x514420` | 150 | `0x96` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 96 | `0x60` | `CItemResult_0126` | `0x514430` | 151 | `0x97` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 97 | `0x61` | `CItemResult_0127` | `0x514440` | 153 | `0x99` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 98 | `0x62` | `CItemResult_0128` | `0x514450` | 154 | `0x9a` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 99 | `0x63` | `CItemResult_0129` | `0x514460` | 155 | `0x9b` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 100 | `0x64` | `CItemResult_0130` | `0x514470` | 157 | `0x9d` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 101 | `0x65` | `CItemResult_0131` | `0x514480` | 158 | `0x9e` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 102 | `0x66` | `CItemResult_0132` | `0x514490` | 159 | `0x9f` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 103 | `0x67` | `CItemResult_0133` | `0x5144a0` | 161 | `0xa1` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 104 | `0x68` | `CItemResult_0134` | `0x5144b0` | 162 | `0xa2` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 105 | `0x69` | `CItemResult_0136` | `0x5144c0` | 178 | `0xb2` | 1 | -1 | Thunk (Lv = `round(val)`) |
| 106 | `0x6a` | `CItemResult_0137` | `0x5144d0` | 224 | `0xe0` | 1 | -1 | Thunk (Lv = `round(val)`) |

- **Program Evidence:**
```asm
0050b062  cmp      byte ptr [ebp + 0xc], 0
0050b066  jne      0x50b09d
0050b068  movss    xmm0, dword ptr [edi + 8]
0050b06d  mulss    xmm0, dword ptr [0x6d9540]    ; float 100
0050b07d  cvttss2si esi, xmm0
0050b081  call     0x490790
0050b086  cmp      eax, esi
0050b088  jl       0x50b09d
0050b0ed  call     0x56c690
0050b0f9  call     0x61e650
0050b136  call     0x41d2b0
00511564  push     0xc1
00511569  call     0x50b030
0051160c  push     0xe2
00511613  call     0x50b030
00513c3b  push     0xb3
00513c40  mov      dword ptr [esi + 8], 0x40a00000
00513c47  call     0x50b030
0051409b  push     0x23
005140a4  call     0x50b030
005143d4  push     0x8f
005143d9  call     0x50b030
```

---

### M05.10 Consumable HP/TP Recovery & Revive `CItemResult*` Handlers (`0..5`, `8`, `59`, `61`, `62..64`)

- **Binary VA(s):** `0x50e6f0` (`0`), `0x50ea40` (`1`), `0x50ed60` (`2`), `0x50f1a0` (`3`), `0x50f490` (`4`), `0x50f750` (`5`), `0x510120` (`8`), `0x512570` (`59`), `0x512b30` (`61`), `0x512eb0` (`62`), `0x513130` (`63`), `0x5133c0` (`64`), `0x6d3820..0x6d387b` (23-entry enemy ID table)
- **Calls:** `0x4f9830` (`AddHP` `vtable+0x20`), `0x4f9800` (`SetHP` `vtable+0x1c`), `0x47e430` (single-result execute)
- **CalledBy:** `CActionPatternItem::Update` (`0x42ce73`, `M05.08`)
- **Typed Pseudocode:**
```text
// Shared Healing Item Modifier helper (Passive 275 / 0x113):
function ApplyItemHealMod_275(actor: CGameStatusBase*, base: i32) -> i32:
    if actor != null and (cmd275 = actor.GetCommand(0, 0x113)) != null:
        return base + trunc0(f32(base) * cmd275.GetVal())
    return base

// 1. Types 0..5 — Fixed HP / Fixed TP / Fixed HP+TP (Single 0..2, Party 3..5):
//    - Type 0 (0x50e6f0, Single HP) & Type 3 (0x50f1a0, Party HP):
//        base = trunc0(itemVal)
//        for t in targets: if t.IsHealable(): t.AddHP(ApplyItemHealMod_275(actor, base))
//        (Type 0 displays full-HP text if itemVal >= 9999.0f at 0x50e821.)
//    - Type 1 (0x50ea40, Single TP) & Type 4 (0x50f490, Party TP):
//        base = trunc0(itemVal)
//        for t in targets: if t.IsHealable(): t.CurTP = clamp(t.CurTP + ApplyItemHealMod_275(actor, base), 0, t.MaxTP)
//    - Type 2 (0x50ed60, Single HP+TP) & Type 5 (0x50f750, Party HP+TP):
//        base = trunc0(itemVal)
//        for t in targets: if t.IsHealable():
//            amt = ApplyItemHealMod_275(actor, base)
//            t.AddHP(amt); t.CurTP = clamp(t.CurTP + amt, 0, t.MaxTP)

// 2. Types 62..64 — 10%-Step MaxHP / MaxTP / Both (0x512eb0, 0x513130, 0x5133c0):
//    Uses signed integer division by 10 (0x66666667, sar edx, 2):
//    - Type 62 (0x512eb0): base = (t.GetMaxHP() * trunc0(itemVal)) / 10 -> t.AddHP(ApplyItemHealMod_275(actor, base))
//    - Type 63 (0x513130): base = (t.MaxTP      * trunc0(itemVal)) / 10 -> t.CurTP = clamp(t.CurTP + ApplyItemHealMod_275(actor, base), 0, t.MaxTP)
//    - Type 64 (0x5133c0): applies BOTH Type 62 HP formula and Type 63 TP formula (each querying Passive 275).

// 3. Types 59 & 61 — Conditional 10%-Step HP Recovery (0x512570, 0x512b30):
//    - Type 59 (0x512570): requires target is CGameEnemyStatus with enemyId in 23-entry table 0x6d3820
//      [210,211,212,215,216,217,220,221,222,250,251,252,253,290,291,292,805,806,807,810,811,812,1000].
//    - Type 61 (0x512b30): requires (Enemy with [enemyParam+0x28] == 2) OR (Player with [charParam+0x44] == 2).
//    - Both require t.IsHealable() and t.GetCurHP() < t.GetMaxHP(); compute
//      amt = ApplyItemHealMod_275(actor, (t.GetMaxHP() * trunc0(itemVal)) / 10) and execute via 0x47e430.

// 4. Type 8 — Revive Item (0x510120): NO Passive 275 scaling!
for t in targets:
    if t.vtable_0x38_IsDead() and !t.vtable_0xc8_IsFullPetrified():  // dead & NOT full-petrified
        hp: i32 = max(1, trunc0(f32(t.GetMaxHP()) * itemVal / 100.0f))
        t.vtable_0x1c_SetHP(hp)                                     // 0x4f9800 -> fires OnRevive (0x4f6980)
```
- **Program Evidence:**
```asm
0050e71f  cvttss2si eax, dword ptr [ebx + 8]
0050e789  push     0x113
0050e7b4  cvttss2si esi, dword ptr [ebp + 0x18]
0050e7b9  add      esi, eax
0050e7c3  call     dword ptr [eax + 0x20]
0050ead5  push     0x113
0050f7ea  push     0x113
00510183  mov      eax, dword ptr [eax + 0x38]
00510194  mov      eax, dword ptr [eax + 0xc8]
005101bc  divss    xmm0, dword ptr [0x6d9540]    ; float 100
005101c4  cvttss2si ecx, xmm0
005101ca  cmovle   ecx, eax
005101d5  call     dword ptr [eax + 0x1c]
00512605  cmp      eax, dword ptr [ecx*4 + 0x6d3820]
00512635  mov      eax, 0x66666667
0051266c  push     0x113
00512bd1  cmp      dword ptr [eax + 0x28], 2
00512c19  cmp      dword ptr [eax + 0x44], 2
00512f37  mov      eax, 0x66666667
00512f5a  push     0x113
005131ad  mov      eax, 0x66666667
005131d0  push     0x113
0051344d  mov      eax, 0x66666667
00513470  push     0x113
005134d1  push     0x113
```

---

### M05.11 Ailment Cure & Debuff Purge `CItemResult*` Handlers (`6`, `7`, `20..23`, `65..72`)

- **Binary VA(s):** `0x50fb30` (`6`), `0x50fe20` (`7`), `0x510a60` (`20`), `0x510c70` (`21`), `0x510e80` (`22`), `0x511090` (`23`), `0x50ae90..0x50b02f` (shared single-ailment cure helper), `0x5136f0..0x51398f` (`65..71`), `0x513990..0x513c2f` (`72`)
- **Calls:** `0x490790` (`CRandom::Get`), `0x50ae90`, `vtable+0x80` (`GetAilments`), `vtable+0x90` (`GetDebuffs`), `vtable+0x64` (`RemoveStatusById`), `vtable+0x68` (`RemoveStatusPtr`)
- **CalledBy:** `CActionPatternItem::Update` (`0x42ce73`, `M05.08`)
- **Typed Pseudocode:**
```text
// - Type 6  (0x50fb30, Cure 1 Random Ailment):
//     for t in targets: if !t.IsDead():
//         ails = t.vtable_0x80_GetAilments()
//         if !ails.empty(): t.RemoveStatusById(ails[GlobalRng.Rand(ails.size())].GetId()) // 1 RNG draw
// - Type 7  (0x50fe20, Cure All Ailments):
//     for t in targets: if !t.IsDead():
//         for cmd in t.vtable_0x80_GetAilments(): t.RemoveStatusById(cmd.GetId())
// - Types 20, 21, 22 (0x510a60, 0x510c70, 0x510e80):
//     Check target status flag and remove one specific status via vtable+0x64:
//       20 -> 114 (0x72 Freeze), 21 -> 116 (0x74 Sleep), 22 -> 123 (0x7b Shadow Sew).
// - Type 23 (0x511090, Dispel All Debuffs):
//     for t in targets:
//         for cmd in t.vtable_0x90_GetDebuffs(): t.vtable_0x68_RemoveStatusPtr(cmd)
// - Types 65..71 (0x5136f0..0x513930 -> shared helper 0x50ae90(cmdId)):
//     for t in targets: if t.GetCommand(0, cmdId) != null: t.RemoveStatusById(cmdId)
//       65 -> 113 (0x71 Poison)      66 -> 117 (0x75 Silence)   67 -> 116 (0x74 Sleep)
//       68 -> 115 (0x73 Paralysis)   69 -> 114 (0x72 Freeze)    70 -> 122 (0x7a Slow)
//       71 -> 120 (0x78 Petrification)
// - Type 72 (0x513990, Panacea — Cure All Ailments AND All Debuffs):
//     for t in targets:
//         list = t.vtable_0x80_GetAilments() + t.vtable_0x90_GetDebuffs()
//         for cmd in list: t.RemoveStatusById(cmd.GetId())
```
- **Program Evidence:**
```asm
0050fbcd  call     dword ptr [eax + 0x80]
0050fbed  call     0x490790
0050fc25  call     dword ptr [eax + 0x64]
0050fed8  call     dword ptr [eax + 0x80]
00510acd  push     0x72
00510acf  call     dword ptr [eax + 0x64]
0051111e  call     dword ptr [eax + 0x90]
00511155  call     dword ptr [edx + 0x68]
0050aef6  push     edi
0050aef9  call     dword ptr [eax + 0x64]
005136f5  push     0x71
005136f9  call     0x50ae90
00513935  push     0x78
00513939  call     0x50ae90
00513a36  call     dword ptr [eax + 0x80]
00513a44  call     dword ptr [eax + 0x90]
00513a88  call     dword ptr [edx + 0x64]
```

---

### M05.12 Offensive Damage & Ailment-Inflicting `CItemResult*` Handlers (`11..19`, `52..58`, `60`)

- **Binary VA(s):** `0x50aa50..0x50adbf` (shared ailment-inflict helper), `0x510500` (`11`), `0x5105f0..0x51064f` (`12..17`), `0x510650..0x510a4f` (`18`), `0x510a50` (`19`), `0x511830` (`52`), `0x511ad0` (`53`, `54`), `0x511da0` (`55`), `0x512060` (`56`, `57`), `0x5122f0` (`58`), `0x5128a0` (`60`), `0x4f21f0` (25-ID Sea Creature table `0x6d38b0`)
- **Calls:** `0x50aa50`, `0x47b220` (`CCommand` factory), `0x47e500` (`CCommand::Execute`), `0x47e430`, `0x4f21f0`, `0x41f920`
- **CalledBy:** `CActionPatternItem::Update` (`0x42ce73`, `M05.08`)
- **Typed Pseudocode:**
```text
// 1. Shared Ailment-Inflict Helper 0x50aa50(cmdId, duration) — Types 11..17, 19:
//    Creates CCommand(cmdId, val = itemVal / 100.0f, duration) via 0x47b220, applies via target.vtable+0xe0
//    and executes via CCommand::Execute (0x47e500):
//      11 (0x510500): cmd 118 (0x76 Stun, dur=5); if landed in battle, sets targetUnit.gauge = 0 ([u+0x08]=0) & _SortTime(0, 0)!
//      12 (0x5105f0): cmd 113 (0x71 Poison)      13 (0x510600): cmd 115 (0x73 Paralysis)
//      14 (0x510610): cmd 117 (0x75 Silence)     15 (0x510620): cmd 114 (0x72 Freeze)
//      16 (0x510630): cmd 116 (0x74 Sleep)       17 (0x510640): cmd 120 (0x78 Petrification)
//      19 (0x510a50): cmd 119 (0x77 Instakill)

// 2. Type 18 (0x510650, Instant Full Petrification):
//    Tests cmd 120 (0x78 Petrification) at chance itemVal / 100.0f via vtable+0xe0;
//    if result == 1 (hit), replaces command with cmd 121 (0x79 Special Petrification -> stage 3) and executes!

// 3. Types 52..55 — Non-Lethal Direct / % MaxHP Damage Items (all clamp dmg <= CurHP - 1):
//    - Type 52 (0x511830): dmg = trunc0(itemVal); if CurHP - dmg <= 0: dmg = CurHP - 1
//    - Types 53 & 54 (0x511ad0, shared): dmg = min(100, trunc0(f32(MaxHP) * itemVal)); if CurHP - dmg <= 0: dmg = CurHP - 1
//    - Type 55 (0x511da0): dmg = trunc0(f32(MaxHP) * itemVal); if CurHP - dmg <= 0: dmg = CurHP - 1 (no 100 cap)

// 4. Types 56..58 & 60 — Enemy-Specific Ailment Items (duration = 5, raw itemVal NOT divided by 100):
//    - Types 56 & 57 (0x512060, shared): Enemy with enemyId in 23-entry table 0x6d3820 -> cmd 115 (0x73 Paralysis, dur=5)
//    - Type 58 (0x5122f0): Enemy matching Sea Creature 25-entry table 0x4f21f0 (0x6d38b0) -> cmd 114 (0x72 Freeze, dur=5)
//    - Type 60 (0x5128a0): Enemy with race [enemyParam+0x28] == 7 -> cmd 117 (0x75 Silence, dur=5)
```
- **Program Evidence:**
```asm
0050ab17  movss    xmm2, dword ptr [edi + 8]
0050ab21  divss    xmm2, dword ptr [0x6d9540]    ; float 100
0050ab32  call     0x47b220
0050abd0  call     0x47e500
00510508  push     0x76
0051050e  call     0x50aa50
00510593  mov      dword ptr [eax + 8], 0
0051059c  call     dword ptr [eax + 0x24]
0051071b  mov      edx, 0x78
005107c9  mov      edx, 0x79
005118bf  sub      ecx, edx
005118c1  lea      ebx, [eax - 1]
00511b74  cvttss2si ebx, xmm0
00511b78  cmp      ebx, 0x64
00511b7b  cmovg    ebx, eax
00511e3d  cvttss2si ecx, xmm0
005120e0  cmp      ecx, dword ptr [eax*4 + 0x6d3820]
0051210b  mov      edx, 0x73
00512369  call     0x4f21f0
00512384  mov      edx, 0x72
00512935  cmp      dword ptr [eax + 0x28], 7
0051294d  mov      edx, 0x75
```

---

### M05.13 Utility, Dungeon & Out-of-Battle `CItemResult*` Handlers (`9`, `10`, `24`, `87`, `88`, `89`)

- **Binary VA(s):** `0x5103b0..0x510472` (`9`), `0x510480..0x5104fb` (`10`), `0x511310..0x511555` (`24`), `0x4151f0..0x4151f2` (`87`), `0x514250..0x514362` (`88`), `0x514370..0x5143cb` (`89`)
- **Calls:** `0x61e650` (`round_f32_to_i32`), `0x47b220` (`CCommand` factory), `0x43b280` (collect battle enemies), `0x61edf4` (`__RTDynamicCast`)
- **CalledBy:** `CActionPatternItem::Update` (`0x42ce73`, `M05.08`)
- **Typed Pseudocode:**
```text
// - Type 9  (0x5103b0, Dungeon Light):
//     dur: i32 = round_f32_to_i32(itemVal)                         // 0x61e650
//     cmd = CreateCommand_0x47b220(0x6b, val = 0.0f, dur = dur)    // 107 Light
//     GameManager.vtable_0x18c_AddDungeonStatus(cmd)
// - Type 10 (0x510480, Escape Battle / Smoke Bomb):
//     If battle event object does NOT block escape (vtable+0x44 == false):
//         battleInfo.flag20 = 0; battleInfo.flag34 = 0; this.escaped = 1u8 ([this+0x1d] = 1)
// - Type 24 (0x511310, Skill Point Gain):
//     for t in targets (CGamePlayerStatusBase):
//         t.skillPoints = min(999u, u32(t.skillPoints + round_f32_to_i32(itemVal))) // [t+0x124], cap 0x3e7
// - Type 87 (0x4151f0, No-Op):
//     returns false immediately (xor al, al; ret).
// - Type 88 (0x514250, Force Enemies Flee / Special Battle Trigger):
//     if battle != null and battle.flag32 != 0 and battle.flag33 == 0:
//         for e in battle.GetEnemies_0x43b280(): e.flag15c = 1u8
//         this.flag1c = 1u8; LogMessage(0x275)
// - Type 89 (0x514370, Lose 5% Party Gold in Battle):
//     if battle != null:
//         loss: i32 = GameManager.GetGold() / 20                   // 0x66666667, sar edx, 3
//         if loss == 0: loss = 1                                   // cmove -> min 1 Gold
//         GameManager.AddGold(-loss)                               // vtable+0x48
```
- **Program Evidence:**
```asm
005103be  call     0x61e650
005103c4  mov      edx, 0x6b
005103d3  call     0x47b220
005103e4  call     dword ptr [edx + 0x18c]
005104d1  mov      eax, dword ptr [eax + 0x44]
005104ef  mov      byte ptr [esi + 0x1d], 1
00511383  call     0x61e650
00511393  cmp      ecx, 0x3e7
0051139e  cmova    ecx, eax
004151f0  xor      al, al
004151f2  ret      
0051427c  mov      al, byte ptr [ecx + 0x32]
00514287  mov      al, byte ptr [ecx + 0x33]
005142b6  call     0x43b280
005142d4  mov      byte ptr [eax + 0x15c], 1
00514385  call     dword ptr [eax + 0x4c]
0051438a  mov      eax, 0x66666667
00514397  sar      edx, 3
005143a8  cmove    esi, edx
005143ab  neg      esi
005143ae  call     dword ptr [eax + 0x48]
```

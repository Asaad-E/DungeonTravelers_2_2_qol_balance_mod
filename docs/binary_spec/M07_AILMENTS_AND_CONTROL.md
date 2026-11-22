# M07 — Ailments, Immunities, Crowd Control, Barriers & Recovery (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x413000..0x570000`)**
> Target binary: `backups/exe/DT22_en_unwrapped.vanilla.exe` (x86-32, image base `0x400000`, SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`).
> Every formula, elemental resistance index, bitmask offset, comparison operator (`<` vs `<=`), rounding mode (`trunc0` = `cvttss2si`, `round_f32_to_i32` = `0x61e650`), PRNG call count (`0x490790` / `0x505ac0`), and execution order is extracted directly from x86-32 disassembly of the vanilla executable.

---

## 1. Status & Ailment ID Reference Table (Binary Ground Truth)

| Dec ID | Hex ID | Command Class | `apply_va` | `tick_va` (`+0x0c`) | Self-Cure / Dur (`+0x10`/`+0x14`) | `+0x68` (Ailment) | `+0x64` (Buff) | `+0x84` (Excl. Barrier) | Elemental Resist Index (`vtable+0x34`) |
|---:|---:|---|---:|---:|---:|:---:|:---:|:---:|---|
| 54 | `0x036` | `CCommandBase` (Turn Delay) | `0x48bd60` | `0x48bc50` | — | 0 | dyn | 0 | None (Enemy Bit 12) |
| 101 | `0x065` | `CCommand_0101` (Clone) | `0x480090` | `0x48d160` | `0x48d590` | 0 | 1 | **1** | — |
| 102 | `0x066` | `CCommand_0102` (Clone) | `0x480090` | `0x48d160` | `0x48d590` | 0 | 1 | **1** | — |
| 105 | `0x069` | `CCommand_0105` (Resurrect) | `0x481950` | `0x48bc50` | — | 0 | dyn | 0 | — |
| 106 | `0x06a` | `CCommand_0106` (Nurse) | `0x481a20` | `0x48bc50` | — | 0 | dyn | 0 | — |
| 113 | `0x071` | `CCommand_0113` (Poison) | `0x481ea0` | `0x481e40` | `0x48d180` (`+0x10`) | **1** | dyn | 0 | `10` (`0x0a`, Water) |
| 114 | `0x072` | `CCommand_0114` (Freeze) | `0x4822c0` | `0x4822a0` | `0x48d180` (`+0x10`) | **1** | dyn | 0 | `10` (`0x0a`, Water) |
| 115 | `0x073` | `CCommand_0115` (Paralysis) | `0x482530` | `0x4822a0` | `0x48d180` (`+0x10`) | **1** | dyn | 0 | `13` (`0x0d`, Lightning) |
| 116 | `0x074` | `CCommand_0116` (Sleep) | `0x4827a0` | `0x4822a0` | `0x48d180` (`+0x10`) | **1** | dyn | 0 | `11` (`0x0b`, Wind) |
| 117 | `0x075` | `CCommand_0117` (Silence) | `0x482a10` | `0x4822a0` | `0x48d180` (`+0x10`) | **1** | dyn | 0 | `11` (`0x0b`, Wind) |
| 118 | `0x076` | `CCommand_0118` (Stun) | `0x482c80` | `0x48d160` | `0x48d180` (`+0x14`) | **1** | dyn | 0 | `9` (`0x09`, Fire) |
| 119 | `0x077` | `CCommand_0119` (Instakill) | `0x482e40` | `0x48bc50` | — | **1** | dyn | 0 | `12` (`0x0c`, Earth) |
| 120 | `0x078` | `CCommand_0120` (Petrification) | `0x4831f0` | `0x483010` | Stage 0..3 (`+0x0c`) | **1** | dyn | 0 | `12` (`0x0c`, Earth) |
| 121 | `0x079` | `CCommand_0121` (Special Petrification) | `0x4834b0` | `0x48d160` | Converts to `120` Stg 3 | **1** | dyn | 0 | `12` (`0x0c`, Earth >= 100) |
| 122 | `0x07a` | `CCommand_0122` (Slow) | `0x4835d0` | `0x4822a0` | `0x48d180` (`+0x10`) | **1** | dyn | 0 | `12` (`0x0c`, Earth) |
| 123 | `0x07b` | `CCommand_0123` (Shadow Sew) | `0x483840` | `0x48d160` | `0x48d590` (`+0x14`) | 0 | dyn | 0 | Level gate (`tgt.Lv >= act.Lv`) |
| 139 | `0x08b` | `CCommand_0139` (Special Instakill) | `0x484020` | `0x48bc50` | — | **1** | dyn | 0 | None (Requires Sleep `116`) |
| 143 | `0x08f` | `CCommand_0143` (Special Sleep) | `0x484150` | `0x48bc50` | Delegates to `116` (`10.0f`) | 0 | dyn | 0 | `11` (`0x0b`, Wind via `116`) |
| 179 | `0x0b3` | `CCommand_0179` (Physical Barrier) | `0x480090` | `0x48d160` | `0x48d590` | 0 | dyn | 0 | — |
| 180 | `0x0b4` | `CCommand_0180` (Parry) | `0x480090` | `0x48d160` | `0x48d590` | 0 | dyn | 0 | — |
| 181 | `0x0b5` | `CCommand_0181` (Barrier System) | `0x486c70` | `0x48d160` | `0x48d590` | 0 | 1 | **1** | — |
| 182 | `0x0b6` | `CCommand_0182` (Nullify Short-Mid) | `0x486e70` | `0x48d160` | `0x48d590` | 0 | dyn | 0 | — |
| 183 | `0x0b7` | `CCommand_0183` (Magic Barrier) | `0x480090` | `0x48d160` | `0x48d590` | 0 | dyn | 0 | — |
| 188 | `0x0bc` | `CCommand_0188` (Resuscitate) | `0x480090` | `0x48d160` | `0x48d590` | 0 | dyn | 0 | — |
| 189 | `0x0bd` | `CCommand_0189` (Magical Change) | `0x480090` | `0x48d160` | `0x48d590` | 0 | 1 | 0 | — |
| 191 | `0x0bf` | `CCommand_0191` (Power Charge) | `0x480090` | `0x48d160` | `0x48d590` | 0 | 1 | 0 | — |
| 192 | `0x0c0` | `CCommand_0192` (All Resistances 100) | `0x487540` | `0x48d160` | `0x48d590` | 0 | dyn | 0 | — |
| 193 | `0x0c1` | `CCommand_0193` (Limiter Removal) | `0x487780` | `0x48d160` | `0x48d590` | 0 | 1 | 0 | — |
| 194 | `0x0c2` | `CCommand_0194` (Beginning of the End) | `0x4879d0` | `0x48d160` | `0x48d590` | 0 | 1 | 0 | — |
| 203 | `0x0cb` | `CCommand_0203` (Erotic Dance) | `0x480090` | `0x48d160` | `0x48d590` | 0 | dyn | 0 | — |
| 261 | `0x105` | `CCommand_0261` (Stamina) | `0x480090` | `0x48cf50` | Permanent | 0 | dyn | 0 | — |

---

## 2. Clean-Room Specification Rules (`M07.01` – `M07.12`)

### M07.01 Core Ailment Application Formula (`113`–`118`, `120`, `122`)

- **Binary VA(s):** `0x481ea0..0x482081` (`CCommand_0113` Poison), `0x4822c0..0x4824a1` (`CCommand_0114` Freeze), `0x482530..0x482711` (`CCommand_0115` Paralysis), `0x4827a0..0x482981` (`CCommand_0116` Sleep), `0x482a10..0x482bf1` (`CCommand_0117` Silence), `0x482c80..0x482e31` (`CCommand_0118` Stun), `0x4831f0..0x4833d1` (`CCommand_0120` Petrification), `0x4835d0..0x4837b1` (`CCommand_0122` Slow), `0x4f98d0..0x4f98da` (`CGameStatusBase::vtable+0x34` stat/resist getter)
- **Calls:** `0x4fb600` (`IsFullyPetrified` `vtable+0xc8`), `0x4f5470` / `0x4d4dd0` (`GetEnchantCount` `vtable+0xf0`), `0x557fd0..0x558120` (enemy immunity bit getters), `0x4f98d0` (`GetStatOrResist` `vtable+0x34`), `0x490790` (`CRandom::Get` on global PRNG `[0x816ce8]`), `0x419640` (`TaskResult` ctor)
- **CalledBy:** `CGameStatusBase::vtable+0xe0` (`0x4fbc40` at `0x4fbd08`), `CActionPatternBase::_Task` (`0x422bd0`), `CCommand_0143` (`0x48424d`), `CItemResult` (`0x50aa50`, `0x51078b`, `0x512163`, `0x5123dc`)
- **Typed Pseudocode:**
```text
// Shared application pipeline for standard ailments:
//   113 (0x71) Poison        -> resistIdx = 10 (Water),     nullEnch = 131 (0x83), enemyBit = 8  (0x5580c0)
//   114 (0x72) Freeze        -> resistIdx = 10 (Water),     nullEnch = 130 (0x82), enemyBit = 7  (0x558090)
//   115 (0x73) Paralysis     -> resistIdx = 13 (Lightning), nullEnch = 136 (0x88), enemyBit = 9  (0x5580f0)
//   116 (0x74) Sleep         -> resistIdx = 11 (Wind),      nullEnch = 132 (0x84), enemyBit = 3  (0x557fd0)
//   117 (0x75) Silence       -> resistIdx = 11 (Wind),      nullEnch = 133 (0x85), enemyBit = 4  (0x558000)
//   118 (0x76) Stun          -> resistIdx =  9 (Fire),      nullEnch = 129 (0x81), enemyBit = 2  (inline shr 2)
//   120 (0x78) Petrification -> resistIdx = 12 (Earth),     nullEnch = 135 (0x87), enemyBit = 5  (0x558030)
//   122 (0x7a) Slow          -> resistIdx = 12 (Earth),     nullEnch = 139 (0x8b), enemyBit = 11 (0x558120)
//
// NOTE: Elemental resistance scaling (NOT LUK, NOT level) governs all 8 standard ailments.
// Signed integer division by 10 (`imul 0x66666667; sar edx, 2; add eax, edx`) truncates toward 0!
// At resist >= 100 (e.g. All Resistances 100 cmd 192 / 0xc0): (res / 10) >= 10 -> chance <= 0.0f -> IMMUNE.
// Negative elemental resistance (weakness, e.g. -50): (res / 10) = -5 -> chance = base * 1.5f!

function ApplyStandardAilment(
    cmd: CCommand*,
    outSeq: Vec<TaskResult>*,
    battleInfo: BattleInfo*,
    target: CGameStatusBase*
) -> void:
    resultType: i32 = 1                                  // 1=Landed, 2=NoOp/Silent, 3=Miss, 4=Nullified/Immune

    // 0. Stun (118 / 0x76) only executes inside battle ([battleInfo+0x40] != 0 at 0x482cd3):
    if cmd.id == 118 and battleInfo.battlePtr == null:
        PushTaskResult(outSeq, target, cmd, resultType=1) // No roll outside battle
        return

    // 1. Stage-3 Petrification guard (vtable+0xc8 = IsFullyPetrified):
    if target.vtable_0xc8_IsFullyPetrified():
        resultType = 2                                   // No-op (0 RNG calls)
        goto FINALIZE

    // 2. Trap-origin gas-trap immunity (for 113..117, 120, 122; NOT checked on 118 Stun):
    if cmd.id != 118 and cmd.originType == 4:            // [cmd+0x08] == 4 (dungeon trap)
        if target.vtable_0xf0_GetEnchantCount(0x8a) != 0:// Enchant 138 (Nullify gas traps)
            resultType = 4                               // NOTE: falls through to check 0x83/0x89, then skips roll at cmp ebx, 1

    // 3. Specific ailment immunity enchant & all-ailment immunity enchant (0 RNG calls):
    if target.vtable_0xf0_GetEnchantCount(nullEnch) != 0:
        resultType = 4
        goto FINALIZE
    if target.vtable_0xf0_GetEnchantCount(0x89) != 0:    // Enchant 137 (Nullify all status ailments)
        resultType = 4
        goto FINALIZE

    // 4. EnemyParam+0x54 immunity bit check (0 RNG calls):
    if target is CGameEnemyStatus:
        if ((EnemyParam[target.enemyId].flags54 >> enemyBit) & 1) != 0:
            resultType = 4
            goto FINALIZE

    // 5. Probability calculation & PRNG roll (1 RNG call on GlobalRng [0x816ce8]):
    if resultType == 1:
        basePct: f32 = cmd.vtable_0x2c_GetValue() * 100.0f
        resVal: i32  = target.vtable_0x34_GetStat(resistIdx) // [target + resistIdx*4 + 0x54]
        resStep: i32 = trunc0(resVal / 10)               // Signed trunc-toward-0 division by 10
        chance: f32  = basePct - (f32(resStep) * basePct) / 10.0f
        if cmd.id != 118 and cmd.originType == 4:        // Dungeon trap evasion enchant 269 (0x10d)
            if target.vtable_0xf0_GetEnchantCount(0x10d) != 0:
                chance = chance - 15.0f                  // Flat -15.0 percentage points
        threshold: i32 = trunc0(chance)                  // cvttss2si
        roll: i32      = GlobalRng_0x816ce8.Rand(100)    // 0..99 inclusive (1 RNG call)
        if roll < threshold:                             // Strict `<` (jl): 0% never lands, 100% always lands
            resultType = 1                               // Landed!
        else:
            resultType = (threshold <= 0) ? 4 : 3        // <=0 displays Immune(4); >0 displays Miss(3)

FINALIZE:
    // 6. Origin 3 suppression (e.g. item/ambient secondary procs): converts failure into silent NoOp(2)
    if resultType != 1 and cmd.originType == 3:          // [cmd+0x08] == 3
        resultType = 2
    PushTaskResult(outSeq, target, cmd, resultType)
```
- **Program Evidence:**
```asm
00481ef4  mov      eax, dword ptr [eax + 0xc8]
00481efa  call     eax
00481efc  test     al, al
00481f2d  push     0x83
00481f32  call     dword ptr [eax + 0xf0]
00481f4a  push     0x89
00481f4f  call     dword ptr [eax + 0xf0]
00481f84  call     0x5580c0
00481fa9  fmul     dword ptr [0x6d9540]    ; float 100
00481fb3  push     0xa
00481fb8  call     dword ptr [eax + 0x34]
00481fc2  mov      eax, 0x66666667
00481fc7  imul     ecx
00481fc9  sar      edx, 2
00481fde  mulss    xmm0, xmm1
00481fe2  divss    xmm0, dword ptr [0x6d9468]    ; float 10
00481fea  subss    xmm1, xmm0
0048200d  subss    xmm1, dword ptr [0x6d947c]    ; float 15
0048201d  cvttss2si esi, xmm1
00482021  call     0x490790
00482026  cmp      eax, esi
00482028  jl       0x482040
0048202e  setle    bl
00482031  add      ebx, 3
00482034  cmp      dword ptr [edi + 8], 3
```

---

### M07.02 Instant Death (`119`, `139`), Special Sleep (`143`), Shadow Sew (`123`), Weapon Procs & Reactive Ailments

- **Binary VA(s):** `0x482e40..0x48300d` (`CCommand_0119` Instakill), `0x484020..0x484149` (`CCommand_0139` Special Instakill), `0x484150..0x484329` (`CCommand_0143` Special Sleep), `0x483840..0x48399c` (`CCommand_0123` Shadow Sew), `0x421258..0x4216e9` (weapon ailment enchants `153..160`, `165`, `197` in `_Task`), `0x44d266..0x44d336` (Passive `258` Instakill on crit), `0x423560..0x423690` (Passive `320` Devil's Whisper), `0x424317..0x424520` (Passive `293` Slow Target), `0x422810..0x422a8b` (Passive `346` Sugar Coma)
- **Calls:** `0x558060` (enemy bit 6 Instakill), `0x490790` (`CRandom::Get`), `0x505ac0` (`Rand(100)`), `0x47b220` (`CreateCommand`), `0x47e260` (enemy `CreateCommand`), `0x4827a0` (`CCommand_0116::Apply`), `0x47e340` (`FindCommand`)
- **CalledBy:** `CGameStatusBase::vtable+0xe0` (`0x4fbc40`), `CActionPatternBase::_Task` (`0x421258`, `0x422810`), `CBattle::CalcPhysicalAttack` (`0x44d266`), `CActionPatternBase::_AfterHit1` (`0x423560`), `CActionPatternBase::_CheckEachInterrupt` (`0x424317`)
- **Typed Pseudocode:**
```text
// 1. Standard Instakill — CCommand_0119 (0x77, VA 0x482e40):
function ApplyInstakill_119(cmd: CCommand_0119*, outSeq: Vec<TaskResult>*, target: CGameStatusBase*):
    if target.vtable_0xc8_IsFullyPetrified(): return PushResult(2)
    if target.GetEnchantCount(0x86) != 0 or target.GetEnchantCount(0x89) != 0: // Ench 134 or 137
        return PushResult(cmd.originType == 3 ? 2 : 4)
    if target is CGameEnemyStatus and EnemyBit6_InstakillImmune(target.enemyId): // 0x558060
        return PushResult(cmd.originType == 3 ? 2 : 4)
    basePct: f32 = cmd.GetValue() * 100.0f
    earthRes: i32 = target.GetStat(12)                   // vtable+0x34(0xc) Earth Resistance
    chance: f32 = basePct - (f32(trunc0(earthRes / 10)) * basePct) / 10.0f
    threshold: i32 = trunc0(chance)                      // cvttss2si
    if GlobalRng_0x816ce8.Rand(100) < threshold:         // 1 RNG call
        res.hpDamage = target.GetCurHP()                 // vtable+0x24 -> exact lethal HP damage!
        PushResult(resultType=1, res)
    else:
        r = (threshold <= 0) ? 4 : 3
        PushResult(cmd.originType == 3 ? 2 : r)

// 2. Special Instakill (Nightmare) — CCommand_0139 (0x8b, VA 0x484020):
//    0 RNG calls! Ignores Earth Resistance and player enchants 134/137!
function ApplySpecialInstakill_139(cmd: CCommand_0139*, outSeq: Vec<TaskResult>*, target: CGameStatusBase*):
    resultType: i32 = 2
    if target.vtable_0xe8_IsAlive() and target.vtable_0xbc_HasSleep():
        if target is CGameEnemyStatus and ((EnemyParam[target.enemyId].flags54 >> 6) & 1) != 0:
            resultType = 4                               // Enemy bit 6 blocks Nightmare
        else:
            res.hpDamage = target.GetCurHP()             // Guaranteed lethal damage (no RNG!)
            resultType = 1
            return PushResult(1, res)
    if cmd.originType == 3: resultType = 2
    PushResult(resultType)

// 3. Special Sleep — CCommand_0143 (0x8f, VA 0x484150):
//    Instantiates temporary CCommand_0116 (0x74, vtable 0x6cc024) with val = 10.0f (0x41200000 = 1000%),
//    originType = 0, selfCureInit = 5, and calls CCommand_0116::Apply (0x4827a0).
//    Still blocked by Ench 132/137, Enemy Bit 3, and Wind Resistance >= 100!

// 4. Shadow Sew — CCommand_0123 (0x7b, VA 0x483840):
//    Level-gated (no elemental resistance scaling!).
function ApplyShadowSew_123(cmd: CCommand_0123*, outSeq: Vec<TaskResult>*, target: CGameStatusBase*, actor: CGameStatusBase*):
    if target.vtable_0xc8_IsFullyPetrified(): return PushResult(2)
    if target.GetEnchantCount(0x89) != 0: return PushResult(4) // Ench 137 only (no specific enchant)
    if target is CGameEnemyStatus and ((EnemyParam[target.enemyId].flags54 >> 10) & 1) != 0:
        return PushResult(4)                             // Enemy bit 10 immunity
    if u32(target.GetLevel()) >= u32(actor.GetLevel()):  // vtable+0x10 unsigned jb at 0x483924!
        return PushResult(4)                             // Immune if target Lv >= actor Lv!
    threshold: i32 = trunc0(cmd.GetValue() * 100.0f)
    if GlobalRng_0x816ce8.Rand(100) < threshold:         // 1 RNG call
        PushResult(1)
    else:
        PushResult(3)

// 5. Weapon Normal-Attack Ailment Proc Enchants (0x421258..0x4216e9 in CActionPatternBase::_Task):
//    Active ONLY on physical basic attacks (isPhysical != 0 and actionType == 1).
//    For each enchant present on actor, if action command list does NOT already contain that cmdId,
//    appends CreateCommand(origin=5, cmdId, val=rate, -1, -1, selfCureInit=0):
//      Ench 153 (0x99) -> 113 Poison        @ 0.18f (18%), selfCureInit = 0
//      Ench 154 (0x9a) -> 116 Sleep         @ 0.15f (15%), selfCureInit = 0
//      Ench 155 (0x9b) -> 117 Silence       @ 0.18f (18%), selfCureInit = 0
//      Ench 156 (0x9c) -> 114 Freeze        @ 0.18f (18%), selfCureInit = 0
//      Ench 157 (0x9d) -> 115 Paralysis     @ 0.15f (15%), selfCureInit = 0
//      Ench 158 (0x9e) -> 118 Stun          @ 0.12f (12%), selfCureInit = 0
//      Ench 159 (0x9f) -> 120 Petrification @ 0.10f (10%), stage = 0
//      Ench 160 (0xa0) -> 119 Instakill     @ 0.07f ( 7%)
//      Ench 197 (0xc5) -> 119 Instakill     @ 0.75f (75%)  (skipped if 160 already appended 119!)
//      Ench 165 (0xa5) -> 122 Slow          @ 0.12f (12%), selfCureInit = 0

// 6. Reactive Passive Ailment Triggers:
//    - Passive 258 (0x102, Instakill on Physical Crit, 0x44d266..0x44d336):
//      If res.isCrit != 0 and actor has cmd 258: creates cmd 119 with val = cmd258.val, executes 0x482e40.
//    - Passive 320 (0x140, Devil's Whisper, _AfterHit1 0x4235d5):
//      If actor has cmd 320 and target.vtable_0x7c_HasAnyAilment(): executes cmd 119 with val = cmd320.val;
//      if resultType == 1, adds [tmp+0x1c] directly to res.hpDamage!
//    - Passive 293 (0x125, Slow Target, _CheckEachInterrupt 0x424317..0x424520):
//      If target has cmd 293 and Rand(100) < trunc0(cmd293.val * 100.0f):
//      applies cmd 122 (Slow, val=1.0f, selfCureInit=5) + cmd 168 (Speed -0.75f) to attacker!
//    - Passive 346 (0x15a, Sugar Coma, _Task 0x422810..0x422a8b):
//      On non-lethal close-range (range==0) hit, if target has cmd 346 and Rand(100) < trunc0(cmd346.val * 100.0f):
//      applies cmd 122 (Slow, val=1.0f, selfCureInit=5) + cmd 168 (Speed -0.20f, 3 turns) to attacker!
```
- **Program Evidence:**
```asm
00482eb7  push     0x86
00482ebc  call     dword ptr [eax + 0xf0]
00482f26  call     0x558060
00482f58  push     0xc
00482f97  cvttss2si eax, xmm1
00482f9e  call     0x490790
00482fc6  call     dword ptr [eax + 0x24]
0048407d  call     eax
00484087  mov      eax, dword ptr [eax + 0xbc]
004840d0  mov      eax, dword ptr [eax + 0x54]
004840d3  shr      eax, 6
004841da  mov      dword ptr [edi + 0x10], 0x41200000
00484201  mov      dword ptr [edi + 0x28], 5
00483900  mov      eax, dword ptr [eax + 0x54]
00483903  shr      eax, 0xa
00483922  cmp      esi, eax
00483924  jb       0x48392d
0042127c  movss    xmm2, dword ptr [0x6d9320]    ; float 0.18
004214b3  movss    xmm2, dword ptr [0x6d92fc]    ; float 0.07
00421504  movss    xmm2, dword ptr [0x6d9368]    ; float 0.75
```

---

### M07.03 Chant Interruption (`CalcPhysicalAttack` / `CalcMagicalAttack`) & Turn Delay (`54`)

- **Binary VA(s):** `0x44d012..0x44d265` (physical damage + crit interrupt in `CBattle::CalcPhysicalAttack`), `0x44f130..0x44f155` (magical crit interrupt in `CBattle::CalcMagicalAttack`), `0x47ea83..0x47eac0` (interrupt execution in `CCommand::Execute`), `0x423a18..0x423ca6` (Turn Delay `54` / `0x36` in `CActionPatternBase::_AfterHit2`)
- **Calls:** `0x4f5470` (`GetEnchantCount` `vtable+0xf0`), `0x505ac0` (`Rand(100)`), `0x490790` (`CRandom::Get`), `0x43bc50` (cancel Song), `0x43c110` (cancel Dance), `0x43c600` (cancel Puppet), `0x43c9b0` (cancel Geass), `0x43ce30` (cancel Chant), `0x43e510` (`_SortTime`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x4216f0..0x423244`), `CActionPatternBase::_AfterHit1` (`0x4237e6`)
- **Typed Pseudocode:**
```text
// 1. Physical Damage Interruption & Critical Interruption (0x44d012..0x44d265):
function CalcPhysicalInterrupt(res: TaskResult*, dmg: i32, target: BattleUnit_s*, cmd264Val: f32):
    // cmd264 (0x108 = Magic Interruption Modifier) adds to denominator!
    denom: f32   = f32(target.MaxHP) * 1.5f + (cmd264Val + 1.0f)
    baseInt: f32 = clamp(f32(dmg) / denom, 0.0f, 0.95f)

    // Target interruption resistance enchants (0x44d081..0x44d199):
    enchRed: f32 = 0.0f
                 + f32(target.GetEnchantCount(0x39)) * 0.10f // Enchant 57 (GrandDOWN)
                 + f32(target.GetEnchantCount(0x3a)) * 0.06f // Enchant 58 (DOWN)
                 + f32(target.GetEnchantCount(0x3b)) * 0.03f // Enchant 59 (MiniDOWN)
                 - f32(target.GetEnchantCount(0x3c)) * 0.06f // Enchant 60 (UP -> increases interrupt rate!)
                 + f32(target.GetEnchantCount(0x3d)) * 0.20f // Enchant 61 (MegaDOWN)
    finalInt: f32 = clamp(baseInt - enchRed, 0.0f, 0.95f)

    // Roll 1: damage-based interrupt (1 RNG call via 0x505ac0)
    res.isInterrupted = (Rand(100) < trunc0(finalInt * 100.0f)) ? 1u8 : 0u8 // [res+0x33]

    // Roll 2: independent 33% critical interrupt roll (1 extra RNG call if isCrit != 0!)
    if res.isCrit != 0 and Rand(100) < 33:               // cmp eax, 0x21 at 0x44d238
        res.isInterrupted |= 1u8

// 2. Magical Critical Interruption (0x44f13a..0x44f146):
//    Spells do NOT run the physical damage-ratio interrupt roll; ONLY a Magic Critical (Passive 301)
//    performs the independent `Rand(100) < 33` roll to set `res.isInterrupted = 1u8`.

// 3. Interrupt Execution inside CCommand::Execute (0x47ea83..0x47eac0):
//    Runs ONLY when [res+0x1c] != 0x7fffffff AND target.vtable_0xe8_IsAlive() == true AND [res+0x33] != 0:
//      battle.CancelSong(target)   // 0x43bc50
//      battle.CancelDance(target)  // 0x43c110
//      battle.CancelPuppet(target) // 0x43c600
//      battle.CancelGeass(target)  // 0x43c9b0
//      battle.CancelChant(target)  // 0x43ce30

// 4. Turn Delay / Push Back — Command 54 (0x36) in _AfterHit2 (0x423a18..0x423ca6):
function ApplyTurnDelay_54(battle: CBattleBase*, res: TaskResult*, target: CGameStatusBase*, cmds: Vec<CCommand*>*):
    dmg: i32 = (res.hpDamage == 0x7fffffff) ? 0 : res.hpDamage
    if target.GetCurHP() - dmg <= 0 or dmg <= 0 or battle == null: return
    if (cmd54 = FindCommand(cmds, 0x36)) == null: return
    if target is CGameEnemyStatus and ((EnemyParam[target.enemyId].flags54 >> 12) & 1) != 0:
        LogImmunity(target)                              // Enemy bit 12 immunity (0 RNG calls)
        return
    if GlobalRng_0x816ce8.Rand(100) < trunc0(cmd54.GetValue() * 100.0f): // 1 RNG call
        idx = FindUnitIndex(battle.units, target)
        if idx + 1 < battle.units.size():
            swap(battle.units[idx].gauge, battle.units[idx + 1].gauge) // [u+0x08]
            battle.vtable_0x24_SortTime(1, 0)
```
- **Program Evidence:**
```asm
0044d03a  mulss    xmm0, dword ptr [0x6d93bc]    ; float 1.5
0044d04b  divss    xmm1, xmm0
0044d056  movss    xmm1, dword ptr [0x6d9384]    ; float 0.95
0044d081  push     0x39
0044d0a8  mulss    xmm0, dword ptr [0x6d930c]    ; float 0.1
0044d0e2  mulss    xmm0, dword ptr [0x6d92f0]    ; float 0.06
0044d119  mulss    xmm0, dword ptr [0x6d92e4]    ; float 0.03
0044d15d  subss    xmm1, xmm0
0044d18c  mulss    xmm0, dword ptr [0x6d9324]    ; float 0.2
0044d1f8  call     0x505ac0
0044d20c  cvttss2si ecx, xmm0
0044d210  cmp      eax, ecx
0044d238  cmp      eax, 0x21
0047ea83  cmp      byte ptr [ebx + 0x33], 0
0047ea97  call     0x43bc50
0047eaa0  call     0x43c110
0047eaa9  call     0x43c600
0047eab2  call     0x43c9b0
0047eabb  call     0x43ce30
```

---

### M07.04 Enemy & Boss Immunity Bitmask (`[enemyParam+0x54]` / `EnemyData.pck +0x3c`)

- **Binary VA(s):** `0x557fa0..0x558147` (EnemyParam bitmask getters), `0x482d6a` (bit 2), `0x483900` (bit 10), `0x423a82` (bit 12), `0x44db12` / `0x44db85` (bit 13), `0x48146a` (bit 14), `0x4503b3` (bit 15), `0x426aa8` (bit 0), `0x426b86` / `0x439f1d` (bit 1)
- **Calls:** `0x507310` (EnemyParam map lookup on `[0x7389d8]`)
- **CalledBy:** `CCommand_0113..0123`, `CCommand_0139`, `CCommand_0084`, `CActionPatternBase::_AfterHit2`, `CBattle::CalcMagicalAttack`, `CBattle::_Steal`, `CBattleBase` death/sealbook handlers
- **Typed Pseudocode:**
```text
// Runtime EnemyParam struct (from global map [0x7389d8], populated from EnemyData.pck +0x3c)
// stores a 16-bit flag word at [enemyParam + 0x54]. Every bit 0..15 is accounted for below:
//
//   Bit  Mask     Getter / Site VA              Exact Meaning in Vanilla Binary
//   ---  ------   ----------------------------  -----------------------------------------------------------
//    0   0x0001   0x557fa0, 0x426aa8, 0x52ba5f  Boss / Sealbook drop cap (99) & unsealable/non-normal flag
//    1   0x0002   0x426b86, 0x439f1d            Boss death sequence / special defeat animation flag (0x21)
//    2   0x0004   0x482d6a (inline shr 2)       Stun (118 / 0x76) Immunity
//    3   0x0008   0x557fd0 (shr 3)              Sleep (116 / 0x74 & Special Sleep 143 / 0x8f) Immunity
//    4   0x0010   0x558000 (shr 4)              Silence (117 / 0x75) Immunity
//    5   0x0020   0x558030 (shr 5)              Petrification (120 / 0x78 & Special Petrify 121 / 0x79) Immunity
//    6   0x0040   0x558060, 0x4840d0 (shr 6)    Instakill (119 / 0x77 & Special Instakill 139 / 0x8b) Immunity
//    7   0x0080   0x558090 (shr 7)              Freeze (114 / 0x72) Immunity
//    8   0x0100   0x5580c0 (shr 8)              Poison (113 / 0x71) Immunity
//    9   0x0200   0x5580f0 (shr 9)              Paralysis (115 / 0x73) Immunity
//   10   0x0400   0x483900 (inline shr 0xa)     Shadow Sew (123 / 0x7b) Immunity
//   11   0x0800   0x558120 (shr 0xb)            Slow (122 / 0x7a) Immunity
//   12   0x1000   0x423a82 (inline shr 0xc)     Turn Delay / Push Back (54 / 0x36) Immunity
//   13   0x2000   0x44db12, 0x44db85 (shr 0xd)  Age-category flag for cmd 149 (Nobody Over 20) & 150 (Under 20)
//   14   0x4000   0x48146a, 0x52dc94 (shr 0xe)  Snackification (84 / 0x54) Immunity
//   15   0x8000   0x4503b3 (inline shr 0xf)     Steal (_Steal 0x44fde0) Immunity / rare steal block
//
// NOTE: [enemyParam + 0x50] holds the enemy base drop/encounter rate field read at 0x43a9c3
//       (NOT an ailment bitmask). All combat/ailment immunity bits reside in [enemyParam + 0x54].

function IsEnemyImmuneToAilment(enemyId: i32, cmdId: i32) -> bool:
    flags54: u32 = EnemyParamMap_0x7389d8.Find(enemyId).flags54 // [param + 0x54]
    switch cmdId:
        case 118: return ((flags54 >>  2) & 1) != 0      // Stun
        case 116, 143: return ((flags54 >> 3) & 1) != 0  // Sleep / Special Sleep
        case 117: return ((flags54 >>  4) & 1) != 0      // Silence
        case 120, 121: return ((flags54 >> 5) & 1) != 0  // Petrification / Special Petrification
        case 119, 139: return ((flags54 >> 6) & 1) != 0  // Instakill / Special Instakill
        case 114: return ((flags54 >>  7) & 1) != 0      // Freeze
        case 113: return ((flags54 >>  8) & 1) != 0      // Poison
        case 115: return ((flags54 >>  9) & 1) != 0      // Paralysis
        case 123: return ((flags54 >> 10) & 1) != 0      // Shadow Sew
        case 122: return ((flags54 >> 11) & 1) != 0      // Slow
        case  54: return ((flags54 >> 12) & 1) != 0      // Turn Delay
        default:  return false
```
- **Program Evidence:**
```asm
00557fbc  mov      al, byte ptr [eax + 0x54]
00557fbf  and      al, 1
00557fec  mov      eax, dword ptr [eax + 0x54]
00557fef  shr      eax, 3
0055801f  shr      eax, 4
0055804f  shr      eax, 5
0055807f  shr      eax, 6
005580af  shr      eax, 7
005580df  shr      eax, 8
0055810f  shr      eax, 9
0055813f  shr      eax, 0xb
00482d6a  mov      eax, dword ptr [eax + 0x54]
00482d6d  shr      eax, 2
00483900  mov      eax, dword ptr [eax + 0x54]
00483903  shr      eax, 0xa
0044db12  mov      eax, dword ptr [eax + 0x54]
0044db15  shr      eax, 0xd
```

---

### M07.05 Player Equipment, Elemental Resistance, and Status Immunity Gates

- **Binary VA(s):** `0x481f0a..0x481f63` (Poison enchants), `0x48232a..0x482383` (Freeze enchants), `0x4825c2..0x4825f3` (Paralysis enchants), `0x48280a..0x482863` (Sleep enchants), `0x482a7a..0x482ad3` (Silence enchants), `0x482cf7..0x482d31` (Stun enchants), `0x482eb3..0x482f05` (Instakill enchants), `0x48325a..0x4832b3` (Petrification enchants), `0x483517..0x48354b` (Special Petrification `121` immunity & EarthRes >= 100 check), `0x483662..0x483693` (Slow enchants), `0x4838aa..0x4838c7` (Shadow Sew enchant), `0x4fc1ac..0x4fc1e6` (`All Resistances 100` cmd `192` / `0xc0`)
- **Calls:** `0x4f5470` (`CGamePlayerStatusBase::GetEnchantCount` `vtable+0xf0`), `0x4d4dd0` (`CGameEnemyStatus::GetEnchantCount` `vtable+0xf0` — returns 0), `0x4f98d0` (`GetStat` `vtable+0x34`), `0x4fb600` (`IsFullyPetrified` `vtable+0xc8`)
- **CalledBy:** `CCommand_0113..0123`, `CGameStatusBase::vtable+0x108` stat recalc (`0x4fbdd0`)
- **Typed Pseudocode:**
```text
// 1. Equipment Immunity Enchants (any piece -> GetEnchantCount(id) != 0 grants 100% immunity):
//    Ench 129 (0x81): Nullify Stun (118)
//    Ench 130 (0x82): Nullify Freeze (114)
//    Ench 131 (0x83): Nullify Poison (113)
//    Ench 132 (0x84): Nullify Sleep (116, 143)
//    Ench 133 (0x85): Nullify Silence (117)
//    Ench 134 (0x86): Nullify Instakill (119; NOT checked by 139 Special Instakill!)
//    Ench 135 (0x87): Nullify Petrification (120, 121)
//    Ench 136 (0x88): Nullify Paralysis (115)
//    Ench 137 (0x89): Nullify All Status Ailments (checked by 113..123; NOT checked by 139!)
//    Ench 138 (0x8a): Nullify Gas Traps (checked when [cmd+0x08] == 4 on 113..117, 120, 122)
//    Ench 139 (0x8b): Nullify Slow (122)
//    Ench 269 (0x10d): Trap evasion (-15.0f to chance when [cmd+0x08] == 4 on 113..117, 120, 122)

// 2. Special Petrification (121 / 0x79, VA 0x4834b0) — Guaranteed unless immune:
//    NO RNG roll! Succeeds (resultType = 1) if and only if ALL four guards pass:
//      a) !target.vtable_0xc8_IsFullyPetrified()        // else resultType = 2
//      b) target.GetEnchantCount(0x87) == 0             // Ench 135
//      c) target.GetEnchantCount(0x89) == 0             // Ench 137
//      d) target.vtable_0x34_GetStat(12) < 100          // Earth Resistance < 100 (cmp eax, 0x64; jge!)
//      e) !(target is Enemy and EnemyBit5_PetrifyImmune(target.enemyId)) // 0x558030

// 3. Status 192 (0xc0, All Resistances 100) Stat Bonus (0x4fc1ac..0x4fc1e6):
//    Adds +100 (xmmword [0x6d9e10] = [100, 100, 100, 100]) to resist indices 6..13
//    (Slash, Stab, Bash, Fire, Water, Wind, Earth, Lightning).
//    For any target with base resist >= 0, this pushes resist >= 100 -> trunc0(res / 10) >= 10
//    -> effective chance <= 0.0f for all elemental-resist-scaled ailments (113..122)!

// 4. Target-State Guards:
//    - Stage-3 Petrification (vtable+0xc8): blocks all new ailments in Apply (returns 2) AND
//      aborts CGameStatusBase::AddStatus (0x4f9950..0x4f995a) immediately for EVERY status!
//    - Dead targets (CurHP <= 0) are excluded at targeting / _Task entry, except Resurrect (105)
//      and Revive items (ItemResult_0011).
```
- **Program Evidence:**
```asm
00483504  mov      eax, dword ptr [eax + 0xc8]
0048350a  call     eax
0048351b  push     0x87
00483520  call     dword ptr [eax + 0xf0]
0048352e  push     0x89
00483533  call     dword ptr [eax + 0xf0]
00483541  push     0xc
00483543  call     dword ptr [eax + 0x34]
00483546  cmp      eax, 0x64
00483549  jge      0x483575
0048356c  call     0x558030
004fc1b0  push     0xc0
004fc1be  movaps   xmm1, xmmword ptr [0x6d9e10]
004fc1d5  paddd    xmm0, xmm1
```

---

### M07.06 Gradual & Instant Petrification Lifecycle (`120`, `121`)

- **Binary VA(s):** `0x483010..0x4831e4` (`CCommand_0120::vtable+0x0c` stage advance), `0x4f99b7..0x4f9bd3` (`121 -> 120` conversion & deduplication in `AddStatus`), `0x4fc019..0x4fc050` (DEF/AGI stat modifier), `0x4fb5c0..0x4fb63f` (`vtable+0xc4` `IsGraduallyPetrifying` & `vtable+0xc8` `IsFullyPetrified`), `0x4fbd90..0x4fbdb5` (`vtable+0xe8` `IsAlive`), `0x436be4..0x436c9e` (`CBattleBase::Update` Inner States 4 & 5), `0x43b580..0x43b5e9` (target validity)
- **Calls:** `0x41f920` (exclusive barrier interception `101`/`102`/`181`), `0x43c110` (cancel Dance), `0x43c600` (cancel Puppet), `0x43c9b0` (cancel Geass), `0x43ce30` (cancel Chant), `0x43bc50` (cancel Song), `vtable+0x6c` (`0x4fa870` purge battle statuses), `0x43a4a0` (enemy defeat/removal), `0x47b220` (`CreateCommand`)
- **CalledBy:** `CBattleBase::Update` Inner States 4 & 5 (`0x436be4`, `0x436c3f`), `CCommand::Execute` (`0x47e500`), `CGameStatusBase::AddStatus` (`0x4f9930`), `CGameStatusBase::vtable+0x108` (`0x4fbdd0`)
- **Typed Pseudocode:**
```text
// 1. Creation & Initial Stage:
//    - Gradual Petrification (120 / 0x78) is created with stage [cmd+0x28] = 0 (0x41859a / 0x418a7e / 0x42146d).
//    - Special/Instant Petrification (121 / 0x79) converts inside AddStatus (0x4f99b7..0x4f9b71):
//        a) Cancels Dance (0x43c110), Puppet (0x43c600), Geass (0x43c9b0), Chant (0x43ce30), Song (0x43bc50).
//        b) Purges all other battle statuses: target.vtable_0x6c(0, 1).
//        c) Allocates CCommand_0120 (0x78), sets stage = 3 (vtable+0xac(3)), deletes old 0x79 command.
//    - Deduplication in AddStatus (0x4f9b9f..0x4f9bd3):
//        If target ALREADY has cmd 120:
//          - If incoming cmd 120 has stage < 3: DISCARD incoming (keepNew = 0, existing stage is NOT reset!).
//          - If incoming cmd 120 has stage >= 3 (from 121): DELETE existing 120 and replace with stage 3!

// 2. Stat Modifier for ANY Active Stage of 120 (0x4fc019..0x4fc050):
//    While target.HasStatus(0x78) (stages 0, 1, 2, or 3):
//      DEF += trunc0(target.GetBaseStat(1) / 2)         // +50% base DEF
//      AGI -= trunc0(target.GetBaseStat(5) / 2)         // -50% base AGI

// 3. Stage Progression (CCommand_0120::vtable+0x0c at 0x483010, called in Inner State 4 at 0x436be4):
function TickPetrification_120(cmd: CCommand_0120*, outSeq: Vec<TaskResult>*, battleInfo: BattleInfo*, target: CGameStatusBase*) -> bool:
    if battleInfo.battlePtr == null:                     // Out of battle (dungeon walking)
        cmd.stepCounter += 1                             // [cmd+0x2c]++
        if cmd.stepCounter < 5: return true              // Advances 1 stage every 5 steps
        cmd.stepCounter = 0
    if cmd.stage < 0xffffffffu32:                        // [cmd+0x28]
        cmd.stage += 1                                   // 0 -> 1 -> 2 -> 3 (takes 3 turns in battle!)
        if cmd.stage == 3:
            // Exclusive Barrier Intercept (0x48309e -> 0x41f920):
            // Clone 101 / Clone 102 / Barrier System 181 CAN BLOCK Stage 3 completion!
            if CheckExclusiveBarrier_0x41f920(&res, target):
                // Consumes 1 barrier charge and queues removal of cmd 120 (resultType=2, removeFlag=0)!
                PushRemovalResult(outSeq, target, cmdId=0x78)
                return true
            // Final Petrification Lock-in (0x4830de..0x4831d1):
            if battleInfo.battlePtr != null:
                CancelDance(target); CancelPuppet(target); CancelGeass(target)
                CancelChant(target); CancelSong(target)
            target.vtable_0x6c(0, 1)                     // Purge all other battle statuses (keeps 120!)
            NotifyPartyPetrified(target)
    return true

// 4. Stage 3 Alive Flag, Targetability & Turn-Start State 5 (0x4fb5c0..0x4fb63f, 0x4fbd90, 0x436c3f):
//    - vtable+0xc4 (0x4fb5c0): IsGraduallyPetrifying() = (Has(120) && stage < 3)
//    - vtable+0xc8 (0x4fb600): IsFullyPetrified()      = (Has(120) && stage >= 3)
//    - vtable+0xe8 (0x4fbd90): IsAlive()               = (!IsDead() [CurHP > 0]) && (!IsFullyPetrified())
//    - Because IsAlive() is FALSE at Stage 3:
//        * Player units are excluded from normal alive-target pools (0x43b5c0) and count as incapacitated
//          for party-wipe checks, while CurHP remains > 0 (so Resurrect 105 / Revive items do NOT apply;
//          Nurse tier >= 6 or Panacea ItemResult_0010 is required to cure!).
//        * Inner State 5 (0x436c3f..0x436c9e):
//            - Player unit ([unit+0x78] != 0): logs msg 0x42 -> PhaseNo = 4 (turn skipped).
//            - Enemy unit ([unit+0x78] == 0): calls CBattleBase::_SetDead (0x43a4a0) -> PhaseNo = 15
//              (immediately defeated and removed from battle!).
```
- **Program Evidence:**
```asm
00483032  cmp      dword ptr [ebx + 0x40], 0
0048305a  inc      eax
0048305b  mov      dword ptr [ecx + 0x28], eax
0048305e  cmp      eax, 3
00483061  jne      0x4831d9
0048309e  call     0x41f920
004830e8  call     0x43c110
00483115  call     dword ptr [eax + 0x6c]
004f9b52  push     3
004f9b54  call     dword ptr [edx + 0xac]
004f9bc8  cmp      eax, 3
004f9bcb  jae      0x4f9bd3
004fc01d  push     0x78
004fc036  sar      eax, 1
004fb633  cmp      eax, 3
004fb636  cmovb    esi, ecx
004fbd95  mov      eax, dword ptr [eax + 0x38]
004fbda2  mov      eax, dword ptr [eax + 0xc8]
00436c82  call     0x43a4a0
00436c92  mov      dword ptr [edi + 0x18], 0xf
```

---

### M07.07 Ailment Self-Cure (`CCommandProbabilityBase`) & Duration Tick (`CCommandTurnBase`)

- **Binary VA(s):** `0x4fb8e0..0x4fba16` (`CGameStatusBase::vtable+0xd8` turn-start self-cure pass), `0x481e80` / `0x48d180..0x48d36e` (`CCommandProbabilityBase::CheckSelfCure`), `0x4fba20..0x4fbb50` (`CGameStatusBase::vtable+0xdc` turn-duration tick), `0x48d590..0x48d6bb` (`CCommandTurnBase::TickDuration`), `0x48bec0..0x48bee9` (`CCommandBase::vtable+0x8c` expires-on-sleep flag), `0x418573..0x4185b9` & `0x418a57..0x418a9f` (`selfCureInit = 5` setup)
- **Calls:** `0x490790` (`CRandom::Get` on `[0x816ce8]`), `0x4fb5a0` (`HasSleep` `vtable+0xbc`), `0x48bec0` (`vtable+0x8c`), `0x4f5470` (`GetEnchantCount` `vtable+0xf0`), `0x47e500` (`CCommand::Execute`)
- **CalledBy:** `CBattleBase::Update` Inner State 1 (`0x43692f` -> `vtable+0xd8`) and Inner State 8 (`0x436d4c` -> `vtable+0xdc`), dungeon step tick (`0x4fb660`)
- **Typed Pseudocode:**
```text
// 1. Self-Cure Eligible Commands (implement vtable+0x10 -> 0x481e80 -> 0x48d180):
//    EXACTLY: 113 (Poison), 114 (Freeze), 115 (Paralysis), 116 (Sleep), 117 (Silence), 122 (Slow).
//    - Initial self-cure probability [cmd+0x28]:
//        * Skills, Enemy Attacks, Items, Passives (293/346), Special Sleep (143): 5 (5%)
//        * Weapon Normal-Attack Proc Enchants (153..157, 165 at 0x421287..0x4216d2): 0 (0%)
//    - NOTE: Stun (118) self-removes immediately in AddStatus; Petrification (120) uses stage progression
//            and NEVER self-cures; Shadow Sew (123) and Erotic Dance (203) use turn-count CCommandTurnBase.

function CheckProbabilitySelfCure_0x48d180(
    cmd: CCommandProbabilityBase*,
    outSeq: Vec<TaskResult>*,
    battleInfo: BattleInfo*,
    target: CGameStatusBase*
) -> bool:
    // Step counter wrap [cmd+0x2c] = ([cmd+0x2c] + 1) % 5 (0x48d1a7..0x48d1b5)
    cmd.subCounter = (cmd.subCounter + 1 < 5) ? (cmd.subCounter + 1) : 0

    // Sleep-triggered expiry for compatible statuses (vtable+0x8c = (CommandData[id]+0x50 >> 1) & 1):
    if target != null and target.vtable_0xbc_HasSleep() and cmd.vtable_0x8c_ExpiresOnSleep():
        goto EXPIRE_NOW                                  // 0 RNG calls

    // Out-of-battle step throttle ([battleInfo+0x40] == 0):
    if battleInfo.battlePtr == null:
        stepInterval: u32 = (target.GetEnchantCount(0x109) != 0) ? 2 : 5 // Ench 265 (0x109): 5 - 3 = 2 steps!
        cmd.stepCounter += 1                             // [cmd+0x30]++
        if cmd.stepCounter < stepInterval:
            return false                                 // Not yet due for roll (0 RNG calls)
        cmd.stepCounter = 0

    // Self-cure PRNG roll (1 RNG call on GlobalRng [0x816ce8]):
    // Note: Enchant 265 (0x109) is NOT queried when battleInfo.battlePtr != null!
    roll: u32 = u32(GlobalRng_0x816ce8.Rand(100))        // 0..99
    if roll < cmd.cureChance:                            // Unsigned `jb` (<) at 0x48d223!
        goto EXPIRE_NOW
    cmd.cureChance += 10                                 // +10% per failed turn (5->15->25->...->105%)
    return false

EXPIRE_NOW:
    QueueStatusRemoval(outSeq, target, cmd.id)           // Executed via CCommand::Execute (0x47e500)
    return true                                          // Causes Inner State 1 to set PhaseNo = 14

// 2. Turn-Count Duration Tick (CCommandTurnBase::vtable+0x14 at 0x48d590, called in Inner State 8):
function TickTurnDuration_0x48d590(cmd: CCommandTurnBase*, outSeq: Vec<TaskResult>*, battleInfo: BattleInfo*, target: CGameStatusBase*) -> bool:
    if target != null and target.vtable_0xbc_HasSleep() and cmd.vtable_0x8c_ExpiresOnSleep():
        goto EXPIRE_TURN                                 // Immediate expiry while asleep
    if cmd.remainingTurns == 0: return false             // 0 == permanent / infinite duration
    if battleInfo.battlePtr == null:
        cmd.stepCounter += 1
        if cmd.stepCounter < 5: return false             // Out-of-battle: 1 turn per 5 steps
        cmd.stepCounter = 0
    cmd.remainingTurns -= 1                              // [cmd+0x28]--
    if cmd.remainingTurns != 0: return false
EXPIRE_TURN:
    QueueStatusRemoval(outSeq, target, cmd.id)
    return true
```
- **Program Evidence:**
```asm
0048d1c0  mov      eax, dword ptr [eax + 0xbc]
0048d1d0  mov      eax, dword ptr [eax + 0x8c]
0048d1e3  cmp      dword ptr [edi + 0x40], 0
0048d1ed  push     0x109
0048d1ff  and      eax, 0xfffffffd
0048d202  add      eax, 5
0048d217  push     0x64
0048d219  call     0x490790
0048d21e  mov      ecx, dword ptr [ebx + 0x28]
0048d221  cmp      eax, ecx
0048d223  jb       0x48d241
0048d225  lea      eax, [ecx + 0xa]
0048d228  mov      dword ptr [ebx + 0x28], eax
0048d605  lea      eax, [ecx - 1]
0048d608  mov      dword ptr [esi + 0x28], eax
0048bec0  sub      esp, 8
0048bedf  mov      eax, dword ptr [eax + 0x50]
0048bee2  shr      eax, 1
00418a9b  push     5
```

---

### M07.08 Crowd-Control Turn-Start Gates & Action Restrictions (`113`–`118`, `120`, `122`, `123`, `203`, `259`, `283`)

- **Binary VA(s):** `0x436653..0x437364` (`CBattleBase::Update` Inner States 0..11), `0x43841e..0x438494` (Inner State 21 Poison tick), `0x482150..0x482291` (`CCommand_0113` Poison damage), `0x4fa185..0x4fa2fe` (Stun `118` ATB reset & self-remove in `AddStatus`), `0x4559d0..0x455db0` (skill/co-op legality gates), `0x420970..0x420ab5` (Freeze/Silence mid-turn downgrade to basic attack), `0x449e61..0x449ea9` (Slow `122` in `CBattle::_SetTime`)
- **Calls:** `0x505ac0` (`Rand(100)`), `0x4fb580` (`HasFreeze`), `0x4fb590` (`HasParalysis`), `0x4fb5a0` (`HasSleep`), `0x4fb5b0` (`HasSilence`), `0x4fb600` (`IsFullyPetrified`), `0x4fb640` (`HasSlow`), `0x4fb650` (`HasShadowSew`), `0x47e500` (`CCommand::Execute`), `0x43e510` (`_SortTime`)
- **CalledBy:** `CBattleBase::Update` (`0x4360f0`), `CGameStatusBase::AddStatus` (`0x4f9930`), `CActionPatternBase::_SelectTarget` (`0x420560`), `CBattle::_SetTime` (`0x4499d0`)
- **Typed Pseudocode:**
```text
// 1. Exact Turn-Start Control Sequence (CBattleBase::Update Inner States 0..11, 21):
//    Note: Skipped entirely on extra-turn re-entry ([actor+0xb0] != 0) and for Dolls/Summons (unitId >= 2000).
//    Before entering the switch, builds opposing-side pool [ebp-0x50] (alive enemies if player turn;
//    alive players + dolls if enemy turn, 0x436684..0x4366fb).
//
//    State  0 (0x436713): Reset [actor+0x105]=0, [actor+0x107]=0; run Esarhaddon 311 (0x137) purge.
//    State  1 (0x43692f): Run actor.vtable_0xd8() -> probability self-cure for 113,114,115,116,117,122.
//                         If any cured -> PhaseNo = 14 (returns to State 2 after popup).
//    State  4 (0x436be4): If actor has 120 (Petrification) -> cmd120.vtable_0x0c() (advance stage 0->1->2->3).
//    State  5 (0x436c3f): If actor.vtable_0xc8_IsFullyPetrified() (stage >= 3):
//                         Player -> log 0x42, PhaseNo = 4 (skip turn).
//                         Enemy  -> 0x43a4a0, PhaseNo = 15 (remove defeated enemy).
//    State  6 (0x436ca1): If actor.vtable_0xbc_HasSleep() (116):
//                         Log 0x43, PhaseNo = 4 (unconditional turn skip).
//    State  7 (0x436d08): If actor.vtable_0xb8_HasParalysis() (115):
//                         If Rand(100) < 30 (0x1e, 1 RNG call via 0x505ac0): log 0x44, PhaseNo = 4 (skip turn).
//    State  8 (0x436d4c): Run actor.vtable_0xdc() -> turn-duration tick for CCommandTurnBase statuses.
//    State  9 (0x436d60): Warning Shot — Passive 259 (0x103) on OPPOSING units in [ebp-0x50]:
//                         For each opp in [ebp-0x50]:
//                           if cmd259 = opp.GetCommand(0, 0x103):
//                             if Rand(100) < trunc0(cmd259.val * 100.0f): // 1 RNG call per opp with 259
//                               opp.isConfusedAttack = 1u8 ([opp+0x105]=1 -> 0.3x dmg in CalcPhysicalAttack!)
//                               Queue basic attack from opp targeting actor -> PhaseNo = 12, break.
//    State 10 (0x436e0c): Mesmerized — Passive 283 (0x11b) on OPPOSING units in [ebp-0x50]:
//                         For each opp in [ebp-0x50]:
//                           if cmd283 = opp.GetCommand(0, 0x11b):
//                             if Rand(100) < trunc0(cmd283.val * 100.0f): // 1 RNG call per opp with 283
//                               PhaseNo = 4 (skip actor's turn!), break.
//    State 11 (0x436eb0): Erotic Dance / Temptation — Status 203 (0xcb) on ACTOR:
//                         If cmd203 = actor.GetCommand(0, 0xcb):
//                           if Rand(100) < trunc0(cmd203.val * 100.0f):   // 1 RNG call
//                             Log 0x45, PhaseNo = 4 (skip actor's turn!).
//    State 21 (0x43841e): Poison 113 (0x71) damage tick (0x482150):
//                         raw: i32 = trunc0(f32(target.MaxHP) * 0.05f)
//                         dmg: i32 = (raw == 0 || raw >= target.CurHP) ? (target.CurHP - 1) : raw
//                         if !target.HasSleep() and dmg > 0:
//                           dmg = min(dmg, 250)          // Hard cap 250 (0xfa) at 0x4821ed..0x4821ff!
//                           ApplyHP(target, -dmg)        // Never kills (leaves >= 1 HP); skipped while Asleep!

// 2. Stun (118 / 0x76) Instantaneous Effect inside AddStatus (0x4fa185..0x4fa2fe):
//    Stun does NOT persist across turns! On application in AddStatus:
//      a) Cancels Dance (0x43c110), Puppet (0x43c600), Geass (0x43c9b0), Chant (0x43ce30), Song (0x43bc50).
//      b) Sets targetUnit.gauge = 0.0f ([unit+0x08] = 0) and calls battle.vtable_0x24_SortTime(0, 0).
//      c) Immediately removes status 0x76 (target.vtable_0x64(0x76)) and returns null!

// 3. Action-Selection & Execution Restrictions:
//    - Freeze (114 / 0x72):
//        * AddStatus (0x4f9e6f): cancels Puppet, Geass, Chant (preserves Dance & Song).
//        * Skill menu (0x455cc5): blocks Physical / Technique skills (category == 0) and Co-op (0x4559f9).
//        * Action execution (0x420985..0x420ab4): downgrades queued physical skill to 1-hit basic attack.
//    - Silence (117 / 0x75):
//        * AddStatus (0x4fa0e2): cancels Dance & Song.
//        * Skill menu (0x455d76): blocks Magic / Spell skills (category == 1) and Co-op (0x455a09).
//        * Action execution (0x4209eb..0x420ab4): downgrades queued magic spell to 1-hit basic attack.
//    - Shadow Sew (123 / 0x7b):
//        * AddStatus (0x4fa430): cancels Dance, Puppet, Geass, Chant, Song, AND destroys Doll (0x43d2c0)!
//        * Skill menu (0x455d94): blocks ALL skills (every category) and Co-op (0x455a39).
//    - Slow (122 / 0x7a):
//        * CBattle::_SetTime (0x449e65..0x449ea3): multiplies ATB speed factor by 0.5f (halves speed).
```
- **Program Evidence:**
```asm
00436caa  mov      eax, dword ptr [eax + 0xbc]
00436d11  mov      eax, dword ptr [eax + 0xb8]
00436d22  call     0x505ac0
00436d27  cmp      eax, 0x1e
00436d89  push     0x103
00436e2d  push     0x11b
00436eb6  push     0xcb
00482197  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0048219f  cvttss2si esi, xmm0
004821b9  lea      esi, [eax - 1]
004821c0  mov      edx, dword ptr [edx + 0xbc]
004821ed  mov      eax, 0xfa
004821ff  cmovg    esi, eax
004fa256  mov      dword ptr [eax + 8], 0
004fa2f0  push     0x76
004fa2f2  call     dword ptr [eax + 0x64]
00455cc5  mov      eax, dword ptr [eax + 0xb4]
00455d76  mov      eax, dword ptr [eax + 0xc0]
00455d94  mov      eax, dword ptr [eax + 0xd0]
00449e65  push     0x7a
00449e72  movss    xmm1, dword ptr [0x6d9348]    ; float 0.5
```

---

### M07.09 Sleep Combat Modifiers & Wake-on-Hit (`116` / `0x74`)

- **Binary VA(s):** `0x4f9f8e..0x4fa08a` (Sleep application side effects in `AddStatus`), `0x44af83..0x44afa4` (physical hit override), `0x44cd2a..0x44cd57` (physical 1.5x damage), `0x44da93..0x44dab1` (magical hit override), `0x44efe8..0x44f006` (magical 1.5x damage), `0x47ea41..0x47ea83` (Sleep wake-on-hit in `CCommand::Execute`), `0x43905f` (extra-turn block)
- **Calls:** `0x43c110` (cancel Dance), `0x43c600` (cancel Puppet), `0x43c9b0` (cancel Geass), `0x43ce30` (cancel Chant), `0x43bc50` (cancel Song), `0x48bec0` (`vtable+0x8c`), `vtable+0x64` (`RemoveStatusById`), `vtable+0x68` (`RemoveStatusPtr`), `0x4fbd90` (`IsAlive`)
- **CalledBy:** `CGameStatusBase::AddStatus`, `CBattle::CalcPhysicalAttack`, `CBattle::CalcMagicalAttack`, `CCommand::Execute`, `CBattleBase::Update`
- **Typed Pseudocode:**
```text
// 1. On Sleep (116 / 0x74) Application in AddStatus (0x4f9f8e..0x4fa08a):
//    - Cancels Dance, Puppet, Geass, Chant, and Song.
//    - Iterates all active statuses on target; immediately removes every status where
//      `cmd->vtable+0x8c()` (`(CommandData[id]+0x50 >> 1) & 1`, 0x48bec0) returns true!

// 2. While Asleep (target.vtable_0xbc_HasSleep() == true):
//    - Physical Hit Rate (0x44af83..0x44af9f): forced to 100.0f.
//    - Magical Hit Rate  (0x44da93..0x44daac): forced to 100.0f (before Nobody Over/Under 20 check).
//    - Physical Damage   (0x44cd2a..0x44cd4f): dmg = trunc0((dmg * 3) / 2) (+50% post-truncation!).
//    - Magical Damage    (0x44efe8..0x44f003): dmg = trunc0((dmg * 3) / 2) (+50% post-truncation!).
//    - Poison DoT (113)  (0x4821c0..0x4821ca): skipped while asleep!
//    - Special Instakill (139) (0x484087): enabled (guaranteed lethal unless enemy bit 6).
//    - Extra-Turn Passives (288/289/354) (0x43905f): blocked while asleep.

// 3. Sleep Wake-on-Hit in CCommand::Execute (0x47ea41..0x47ea83):
//    Executes identically for BOTH physical AND magical attacks (no isPhysical branch!).
function ExecuteHPDelta_And_WakeSleep(res: TaskResult*):
    hpDmg: i32 = res.hpDamage                            // [res+0x1c]
    if hpDmg != 0x7fffffff:                              // 0x7fffffff = sentinel "no HP delta"
        res.target.vtable_0x20_AddHP(-hpDmg)             // Applies HP delta (including 0-dmg!)
        if res.target.vtable_0xe8_IsAlive():             // Must survive the hit
            if res.target.vtable_0x50_HasStatus(0x74):   // Sleep (116)
                res.target.vtable_0x64_RemoveStatus(0x74)// Wakes target immediately!
//    Consequences of the `hpDmg != 0x7fffffff` check:
//    - Physical hits & magical hits (including grazed misses in CalcMagicalAttack): WAKE target.
//    - Zero-damage hits whose handler sets [res+0x1c] = 0 (Clone 101/102, Barrier System 181,
//      Parry 180, Pretend 310, Alter Fate 349, Elegant Dancing 285, Knock Down 305): WAKE target!
//    - Complete misses (physical miss), Counter-Parry 250, Nullify enchants 120..128,
//      All Resistances 100 (192), Nullify Short-Mid (182): leave [res+0x1c] = 0x7fffffff -> DO NOT WAKE!
```
- **Program Evidence:**
```asm
004fa056  mov      eax, dword ptr [eax + 0x8c]
004fa05c  call     eax
004fa06f  call     dword ptr [edx + 0x68]
0044cd2f  mov      eax, dword ptr [eax + 0xbc]
0044cd3e  lea      eax, [eax + eax*2]
0044cd44  sar      eax, 1
0044da98  mov      eax, dword ptr [eax + 0xbc]
0044daa4  movss    xmm0, dword ptr [0x6d9540]    ; float 100
0044efed  mov      eax, dword ptr [eax + 0xbc]
0044eff9  lea      eax, [esi + esi*2]
0044f001  sar      esi, 1
0047ea41  cmp      edx, 0x7fffffff
0047ea47  je       0x47eacb
0047ea5f  mov      eax, dword ptr [eax + 0xe8]
0047ea6d  push     0x74
0047ea71  mov      eax, dword ptr [eax + 0x50]
0047ea7c  push     0x74
0047ea80  call     dword ptr [eax + 0x64]
```

---

### M07.10 Exclusive Hit-Consuming Barriers (`101` Clone, `102` Clone, `181` Barrier System) & `vtable+0x84` Exclusivity

- **Binary VA(s):** `0x41f920..0x41fd52` (exclusive barrier interceptor `CheckExclusiveBarrier`), `0x4f9c7c..0x4f9cfc` (`vtable+0x84` mutual-exclusivity purge in `AddStatus`), `0x4fb4f0..0x4fb564` (`CGameStatusBase::vtable+0xac` collector), `0x42265f..0x4226c4` (damage-hit barrier call & `140`/`141`/`142` bypass in `_Task`), `0x422c10..0x422c74` (ailment-hit barrier call in `_Task`), `0x48309e` (Stage-3 Petrification barrier call), `0x510816` (Special Petrification item barrier call)
- **Calls:** `vtable+0x48` (`GetCommand`), `vtable+0x2c` (`GetValue` = remaining hit charges), `vtable+0x28` (`SetValue`), `vtable+0x64` (`RemoveStatusById`), `0x47e290` (`HasCommand`)
- **CalledBy:** `CActionPatternBase::_Task` (`0x4226ab`, `0x422c4b`), `CCommand_0120::vtable+0x0c` (`0x48309e`), `CItemResult` (`0x50aba1`, `0x510816`, `0x511918`, `0x511bdf`, `0x511ea6`)
- **Typed Pseudocode:**
```text
// 1. Mutual Exclusivity Group (CCommand::vtable+0x84 == 1):
//    EXACTLY THREE commands return 1 from vtable+0x84: 101 (0x65 Clone), 102 (0x66 Clone), 181 (0xb5 Barrier System).
//    In AddStatus (0x4f9c7c..0x4f9cfc): whenever an incoming command has cmd->vtable+0x84() == 1,
//    target.vtable_0xac() (0x4fb4f0) collects all existing active statuses with vtable+0x84() == 1
//    and removes them via target.vtable_0x64() BEFORE inserting the new barrier.
//    All three also have vtable+0x64() == 1, so Strip Buffs (74 / 0x4a) dispels them!

// 2. Exclusive Barrier Interception (0x41f920..0x41fd52):
function CheckExclusiveBarrier_0x41f920(res: TaskResult*, target: CGameStatusBase*) -> bool:
    for barrierId in [0x65 (101), 0x66 (102), 0xb5 (181)]:
        if (cmd = target.GetCommand(0, barrierId)) != null:
            if res.hpDamage != 0x7fffffff: res.hpDamage = 0 // Zeroes HP damage (NOT 0x7fffffff!)
            if res.tpDamage != 0x7fffffff: res.tpDamage = 0 // Zeroes TP damage
            res.flags37 = 0x0100u16                         // [res+0x37]=0, [res+0x38]=1 (blocked flag)
            newCharges: f32 = cmd.vtable_0x2c_GetValue() - 1.0f
            cmd.vtable_0x28_SetValue(newCharges)
            if newCharges <= 0.0f:                          // ucomiss + jp at 0x41f9b7..0x41f9c2
                target.vtable_0x64_RemoveStatus(barrierId)  // Consumed last charge -> remove!
            LogBarrierMessage(res, target, barrierId, depleted=(newCharges <= 0.0f))
            return true                                     // 0 RNG calls; consumes 1 charge
    return false

// 3. Exact Invocation & Bypass Rules in CActionPatternBase::_Task:
//    A) Damage-Hit Gate (0x42265f..0x4226c4):
//       - Runs ONLY if (res.hpDamage != 0x7fffffff || res.tpDamage != 0x7fffffff).
//       - BYPASSED if attack carries fixed/percent HP reduction commands:
//           140 (0x8c, Halve HP), 141 (0x8d, Quarter HP), or 142 (0x8e, Reduce HP to 1)!
//       - When 0x41f920 returns true: jumps to 0x421f5d, erasing ALL secondary queued entries
//         in [ebp+0x48][1..N] (so attached ailments/debuffs on that hit are ALSO blocked in the same 1 charge!).
//       - Multi-hit skills invoke _Task once per hit -> each hit consumes 1 charge independently.
//       - Poison DoT (0x482150) bypasses _Task entirely -> does NOT trigger or consume 101/102/181.
//    B) Pure Ailment Gate (0x422c10..0x422c74):
//       - After evaluating target status commands (vtable+0xe0), scans queued TaskResult entries:
//         if any entry has `cmd->vtable+0x68() == 1` (Ailment: 113..122, 139) AND `resultType == 1`:
//         calls CheckExclusiveBarrier_0x41f920(seq[0], target)!
//       - If true: consumes 1 charge and jumps to 0x421f5d, erasing all landed ailments on that hit!
//    C) Stage-3 Petrification Completion (0x48309e):
//       - Calls 0x41f920; if true, consumes 1 charge and removes Petrification (120)!
```
- **Program Evidence:**
```asm
0041f947  push     0x65
0041f954  call     dword ptr [eax + 0x48]
0041f96d  mov      dword ptr [ebx + 0x1c], 0
0041f997  fsub     dword ptr [0x6d938c]    ; float 1
0041f9b7  ucomiss  xmm0, dword ptr [0x6d928c]    ; float 0
0041f9d1  call     dword ptr [esi + 0x64]
0041faaf  push     0x66
0041fbd0  push     0xb5
004f9c80  mov      eax, dword ptr [eax + 0x84]
004f9cb0  call     dword ptr [eax + 0xac]
00422671  mov      edx, 0x8c
00422682  mov      edx, 0x8d
00422693  mov      edx, 0x8e
004226ab  call     0x41f920
00422c25  mov      edx, dword ptr [edx + 0x68]
00422c31  cmp      dword ptr [eax + 0x2c], 1
00422c4b  call     0x41f920
```

---

### M07.11 Non-Exclusive Nullify Shields, Mitigation Barriers & Block Priority Chain (`179`, `180`, `182`, `183`, `188`, `189`, `191`, `192`, `193`, `194`, `261`, `285`, `305`, `310`, `349`)

- **Binary VA(s):** `0x421b01..0x4227d5` (complete nullify/block/dispel chain in `CActionPatternBase::_Task`), `0x422b58..0x422b71` (`179`/`183` consumption in `_Task`), `0x44c68e..0x44c764` (`179` Physical Barrier & `191` Power Charge in `CalcPhysicalAttack`), `0x44e6e0..0x44e72b` (`183` Magic Barrier in `CalcMagicalAttack`), `0x47f86c..0x47f8c6` (`261` Stamina trigger in `CCommand::Execute`), `0x47f932..0x47f9d9` (`188` Resuscitate trigger in `CCommand::Execute`), `0x4fc140..0x4fc1e6` (`189`, `192`, `193`, `194` stat recalc)
- **Calls:** `0x4f5470` (`GetEnchantCount`), `0x416ea0` (`IsNonElemental`), `0x505ac0` (`Rand(100)`), `0x4f4f60` (`GetEquipmentID`), `0x559190` (`IsShield`), `0x41f920` (`CheckExclusiveBarrier`), `0x4fb1f0` (`vtable+0x94` buff collector)
- **CalledBy:** `CActionPatternBase::_Task`, `CBattle::CalcPhysicalAttack`, `CBattle::CalcMagicalAttack`, `CCommand::Execute`, `CGameStatusBase::vtable+0x108`
- **Typed Pseudocode:**
```text
// 1. Exact Priority Order of Nullify / Negation Gates inside CActionPatternBase::_Task (0x421b01..0x4227d5):
//    None of these are in the vtable+0x84 exclusive group (they coexist with Clone 101/102 & Barrier System 181).
//    Once ANY gate triggers (sets blocked = 1), all later gates and all attached ailments/debuffs are skipped!
//
//    [1] Equipment Nullify Enchants (0x421b01..0x421c5a):
//        - Physical (isPhysical != 0): Ench 123 (0x7b All Phys), 120 (0x78 Slash), 121 (0x79 Stab), 122 (0x7a Bash).
//        - Elemental (phys or mag): Ench 124..128 (0x7c..0x80 Fire/Water/Wind/Earth/Lightning).
//        -> Sets hpDmg = tpDmg = 0x7fffffff, resultType = 4 (Nullified).
//    [2] All Resistances 100 — Status 192 (0xc0, 0x421c60..0x421c80):
//        - If !IsNonElemental(action) (0x416ea0 == false): sets hpDmg = tpDmg = 0x7fffffff, resultType = 4.
//    [3] Nullify Short-Mid — Status 182 (0xb6, 0x421c82..0x421ca5):
//        - If action.range in {0 (Short), 1 (Mid)}: sets hpDmg = tpDmg = 0x7fffffff, resultType = 4.
//    [4] Alter Fate — Passive 349 (0x15d, 0x421ca7..0x421db3):
//        - If Rand(100) < trunc0(cmd349.val * 100.0f): sets hpDmg = 0, tpDmg = 0 (negates hit & ailments).
//    [5] Pretend — Passive 310 (0x136, 0x421db8..0x421f57):
//        - Physical only; if Rand(100) < trunc0(cmd310.val * 100.0f): sets hpDmg = 0, tpDmg = 0.
//    [6] Elegant Dancing — Passive 285 (0x11d, 0x42206c..0x4221eb):
//        - Requires damage hit (hpDmg or tpDmg != 0x7fffffff) and target.danceState == 0: sets hpDmg = 0, tpDmg = 0.
//    [7] Knock Down — Passive 305 (0x131, 0x4221ee..0x4223b2):
//        - Physical, range == 2 (Long), weapon equipped in slot 0 (if player);
//          if Rand(100) < trunc0(cmd305.val * 100.0f): sets hpDmg = 0, tpDmg = 0.
//    [8] Parry — Status 180 (0xb4, 0x4223b2..0x422553):
//        - Physical, !IsNonElemental(action) (0x416ea0 == false): sets hpDmg = 0, tpDmg = 0;
//          rolls Rand(100) < trunc0(cmd180.val * 100.0f) -> if true, queues removal of status 180 (consumed!).
//    [9] Counter-Parry — Passive 250 (0xfa, 0x422553..0x42265f):
//        - !inCounter, range in {0, 1}, actor != target, !actor.Has(307);
//          if Rand(100) < trunc0(cmd250.val * 100.0f): sets hpDmg = tpDmg = 0x7fffffff, resultType = 3 (Miss) + queues counter.
//   [10] Exclusive Barriers 101 / 102 / 181 via 0x41f920 (0x42265f..0x4226c4) [see M07.10].
//   [11] Strip Buffs — Command 74 (0x4a, 0x4226c4..0x4227d5):
//        - If Rand(100) < trunc0(cmd74.val * 100.0f): collects all buffs with cmd->vtable+0x64() == 1
//          via target.vtable_0x94() (0x4fb1f0) and removes each via vtable+0x68!

// 2. Damage-Mitigation Barriers (179 Physical Barrier & 183 Magic Barrier) — NOT Full Blocks:
//    - 179 (0xb3, Physical Barrier): in CalcPhysicalAttack (0x44c68e..0x44c723), adds cmd179.val to the
//      post-multiplier ONLY IF caster (cmd179.GetActorId()) is alive AND has a Shield in slot 1 (0x559190).
//      Consumed (removed via vtable+0x64(0xb3)) after 1 physical hit at 0x422b58..0x422b71.
//    - 183 (0xb7, Magic Barrier): in CalcMagicalAttack (0x44e6e0..0x44e72b), adds cmd183.val to the
//      magic damage reduction term. Consumed (vtable+0x64(0xb7)) after 1 magical hit at 0x422b69..0x422b71.

// 3. Non-Barrier Buffs / Special Passives Often Grouped by vtable+0x64 or ID:
//    - 189 (0xbd Magical Change), 193 (0xc1 Limiter Removal), 194 (0xc2 Beginning of the End):
//      vtable+0x64() == 1 (dispellable), NOT hit shields; scale core stats 0..5 by cmd.val (0x4fc140..0x4fc1aa).
//    - 191 (0xbf Power Charge): vtable+0x64() == 1 (dispellable), adds physical attack multiplier (0x44c748).
//    - 188 (0xbc Resuscitate): auto-revive on lethal hit in CCommand::Execute (0x47f932..0x47f9d9);
//      when CurHP drops to <= 0, heals trunc0(f32(MaxHP) * cmd188.val) HP and removes status 188.
//    - 261 (0x105 Stamina): NOT a damage barrier; in CCommand::Execute (0x47f86c..0x47f8c6), triggers
//      activation notification when HP crosses from > (MaxHP * 40) / 100 to <= (MaxHP * 40) / 100,
//      and grants ATB speed bonus in CBattle::_SetTime (0x44a0a8).
```
- **Program Evidence:**
```asm
00421c6e  push     0xc0
00421c78  call     eax
00421c93  push     0xb6
00421ca9  push     0x15d
00421dc4  push     0x136
0042208e  push     0x11d
00422207  push     0x131
004223d4  push     0xb4
00422596  push     0xfa
004226c4  mov      edx, 0x4a
00422730  call     dword ptr [eax + 0x94]
00422b62  push     0xb3
00422b69  push     0xb7
00422b6e  call     dword ptr [eax + 0x64]
0044c70a  call     0x559190
0047f8aa  push     0x105
0047f936  push     0xbc
0047f976  cvttss2si eax, dword ptr [ebp - 0x2c]
```

---

### M07.12 Ailment Cure, Recovery Skills, Cure Items & Turn-Start Purge (`106` Nurse, `105` Resurrect, `311` Esarhaddon, `ItemResult_0009`/`0010`/`0011`)

- **Binary VA(s):** `0x481a20..0x481d68` (`CCommand_0106` Nurse), `0x6cc79c..0x6cc7b7` (Nurse 7-entry ailment table), `0x481950..0x481a16` (`CCommand_0105` Resurrect), `0x436724..0x43692a` (Passive `311` / `0x137` Esarhaddon in Inner State 0), `0x6c9a7c..0x6c9a93` (Esarhaddon 6-entry ailment table), `0x50fb30..0x50fdd7` (`ItemResult_0009` single random ailment cure), `0x50fe20..0x510119` (`ItemResult_0010` Panacea all-ailment cure), `0x510120..0x5103ab` (`ItemResult_0011` revive item), `0x4faf90..0x4fb001` (`CGameStatusBase::vtable+0x80` ailment collector), `0x4fb170..0x4fb1e1` (`CGameStatusBase::vtable+0x90` debuff collector)
- **Calls:** `0x61e650` (`round_f32_to_i32`), `0x490790` (`CRandom::Get`), `vtable+0x48` (`GetCommand`), `vtable+0x64` (`RemoveStatusById`), `vtable+0x80` (`GetAilments`), `vtable+0x90` (`GetDebuffs`), `vtable+0x38` (`IsDead`), `vtable+0xc8` (`IsFullyPetrified`), `0x47e500` (`CCommand::Execute`)
- **CalledBy:** `CGameStatusBase::vtable+0xe0` (`0x4fbc40`), `CBattleBase::Update` Inner State 0 (`0x436724`), `CActionItem` (`0x50e538`)
- **Typed Pseudocode:**
```text
// 1. Nurse / Cure Skill — CCommand_0106 (0x6a, VA 0x481a20..0x481d68):
//    Static priority table at 0x6cc79c (7 entries):
//      NURSE_TABLE[0..6] = [113 Poison, 115 Paralysis, 117 Silence, 114 Freeze, 116 Sleep, 120 Petrification, 122 Slow]
function ApplyNurse_106(cmd: CCommand_0106*, outSeq: Vec<TaskResult>*, target: CGameStatusBase*):
    tier: u32  = u32(round_f32_to_i32(cmd.vtable_0x2c_GetValue())) // 0x61e650 at 0x481aa3
    limit: u32 = min(tier, 7u32)                                   // cmova eax, 7 at 0x481ab4
    toRemove: Vec<CCommand*> = []
    for i in 0 .. limit - 1:
        if (s = target.GetCommand(0, NURSE_TABLE[i])) != null:
            toRemove.push(s)
    // Tier 8 ALSO purges all active stat debuffs (cmd->vtable+0x5c() == 1 via target.vtable_0x90 at 0x481b39)!
    if tier == 8:
        debuffs = target.vtable_0x90_GetDebuffs()                  // 0x4fb170
        toRemove.extend(debuffs)
    for s in toRemove:
        QueueStatusRemoval(outSeq, target, s.id)                   // Executed via CCommand::Execute
    // NOTE:
    // - Does NOT check !IsFullyPetrified: Nurse tier >= 6 cures Stage 1, Stage 2, AND Stage 3 Petrification!
    // - Does NOT cure Shadow Sew (123 / 0x7b) or Erotic Dance (203 / 0xcb) (neither is in 0x6cc79c or vtable+0x5c).
    // - 0 RNG calls (100% deterministic).

// 2. Resurrect Skill — CCommand_0105 (0x69, VA 0x481950..0x481a16):
//    Requires target.vtable_0x38_IsDead() (CurHP <= 0). Restores trunc0(f32(target.MaxHP) * cmd105.val) HP.
//    Has NO effect on Stage-3 Petrified units (whose CurHP > 0).

// 3. Turn-Start Ailment Purge Passive — Esarhaddon 311 (0x137, Inner State 0 at 0x436724..0x43692a):
//    Static table at 0x6c9a7c (6 entries — EXCLUDES 120 Petrification!):
//      ESARHADDON_TABLE[0..5] = [113 Poison, 115 Paralysis, 117 Silence, 114 Freeze, 116 Sleep, 122 Slow]
//    Loops i in 0 .. round_f32_to_i32(cmd311.val) - 1; queues removal of every matching active status
//    and executes via CCommand::Execute (0x47e500) -> PhaseNo = 14 if any removed. 0 RNG calls.

// 4. Consumable Recovery Items (CItemResult):
//    - ItemResult_0009 (0x50fb30, cure 1 random ailment):
//        Requires !target.IsDead() (vtable+0x38). Collects ailments via target.vtable_0x80 (0x4faf90:
//        all active commands with cmd->vtable+0x68() == 1 -> {113..122}).
//        If non-empty: picks `ailments[GlobalRng_0x816ce8.Rand(ailments.size())]` (1 RNG call) and removes it!
//    - ItemResult_0010 (0x50fe20, Panacea / cure all ailments):
//        Requires !target.IsDead() (vtable+0x38). Collects all active ailments via target.vtable_0x80
//        (cmd->vtable+0x68() == 1 -> {113..122}, INCLUDING Stage-3 Petrification if CurHP > 0!) and removes ALL.
//        0 RNG calls. Does NOT remove debuffs, Shadow Sew (123), or Erotic Dance (203).
//    - ItemResult_0011 (0x510120, Revive item):
//        Requires target.IsDead() (vtable+0x38 == true) AND !target.IsFullyPetrified() (vtable+0xc8 == false).
//        Restores `max(1, trunc0(f32(target.MaxHP) * itemVal / 100.0f))` HP via vtable+0x1c.
```
- **Program Evidence:**
```asm
00481aa3  call     0x61e650
00481aaa  mov      edx, 7
00481ab4  cmova    eax, edx
00481ad3  push     dword ptr [esi*4 + 0x6cc79c]
00481b12  cmp      ecx, 8
00481b39  call     dword ptr [eax + 0x90]
004819a5  mov      eax, dword ptr [eax + 0x38]
004819d0  cvttss2si eax, dword ptr [ebp + 0x10]
00436727  push     0x137
0043676a  call     0x61e650
00436793  push     dword ptr [edi*4 + 0x6c9a7c]
0050fbcd  call     dword ptr [eax + 0x80]
0050fbed  call     0x490790
0050fed8  call     dword ptr [eax + 0x80]
0050ff0c  call     dword ptr [edx + 0x64]
00510183  mov      eax, dword ptr [eax + 0x38]
00510194  mov      eax, dword ptr [eax + 0xc8]
005101c4  cvttss2si ecx, xmm0
004fafc1  mov      eax, dword ptr [eax + 0x68]
004fb1a1  mov      eax, dword ptr [eax + 0x5c]
```

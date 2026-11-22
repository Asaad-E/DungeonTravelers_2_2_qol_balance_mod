# M00 — Combat Pipeline Spine (`DT22_en_unwrapped.vanilla.exe`)

> **Clean-Room Binary Specification (`0x413000..0x570000`)**
> This document defines the end-to-end ordered combat pipeline spine extracted directly from `backups/exe/DT22_en_unwrapped.vanilla.exe`. Every stage, state-machine index, virtual table dispatch, PRNG draw order, float-to-integer conversion (`cvttss2si` = `trunc0` vs `0x61e650` = `round_f32_to_i32`), comparison operator (`<` vs `<=`), and module hand-off (`M01..M11`) is specified in exact execution order.

---

## 1. End-to-End Execution Spine & Module Hand-off Map

```
[M00.01] CBattle::CBattle (0x448c60) -> CBattleBase::_Initialize (0x43da60) -> CBattle::_Initialize (0x449130)
   ├── Party/Enemy BattleUnit_s allocation, formation aggro share init (0x6517a0), battle jitter PRNG [this+0x1bc]
   ├── Floor elemental zone init [this+0x1e4..0x1f4] = 1.0f, initial gauge CBattle::_SetTime(u, 0) (0x4499d0)
   └── Preemptive / Ambush roll CBattle::_SetFirstAttack (0x44a3d0) + gauge sort CBattleBase::_SortTime (0x43e510)
          │
          ▼
[M00.02] CBattle::Update (0x448ee0) -> CBattleBase::Update (0x4360f0, 16-state jump table 0x4397e0)
   ├── State 0: Victory check (0x43b510) -> Head unit [this+0x24][0] selection -> Incapacitated skip loop (0x43e5c0(0))
   │     ├── If [actor+0xb0] != 0 (extra turn re-entry): skip TurnPhaseNo loop -> jump to 0x43875a
   │     ├── If actor in 3000..3999 (Summon/Guest): run Samba Dance (199 / 0xc7) tick (0x436343..0x4365fb)
   │     └── If actor in 2000..2999 (Doll) or 3000..3999 (Summon/Guest) or >= 4000: skip [M00.03] -> jump to 0x43875a
   │
   ├── [M00.03] Inner Turn-Start State Machine (0x436700, 25-state jump table 0x439820, TurnPhaseNo 0..24)
   │     ├── States 0..2: Pre-turn passive 311 (0x137), Ailment self-cure (113..118, 256), Hard CC gate (116/118/120), Paralysis 114 (30% skip)
   │     ├── States 3..5: Auto-cast passives 446 (0x1be -> U0008), 319 (0x13f -> E1580), 345 (0x159)
   │     ├── States 6..7: Panic 259 (0x103, 50% basic attack on random unit), Charm 283 (0x11b)
   │     ├── States 8..10: Auto-buff/Doll passives 357 (0x165), 350 (0x15e), 448 (0x1c0)
   │     ├── State 11: Turn-start DoT/HoT commands + Enchants (144/145/148/296 HP, 146/147/149 TP)
   │     ├── States 12..14: Dances 200 (0xc8 -> E0822), 204 (0xcc -> E0835), 199 (0xc7)
   │     ├── States 15..20: Geass 339 (0x153 -> T0094), Status tick vtable+0xdc, Temptation 203 (0xcb), Chants, Songs, Puppets
   │     └── States 21..24: Passives 355 (0x163), 305 (0x131), 306 (0x132), 203 cleanup -> exit to 0x43875a
   │
   ├── [M00.04] Action Selection, Legality Gate & _CreatePattern Dispatch (Outer States 1 -> 2 -> 3)
   │     ├── CheckSkillCondition (0x4f4910, jump table 0x4f4bdc) + chant completion / AI / command menu (States 1..2)
   │     ├── CBattleBase::_CreateAction (0x43ea70, jump table 0x43f020, ActionType 0..9 + CActionJoinAttack 0x41c640)
   │     ├── CActionBase::Action_s::SetHitCount (0x417cd0) & SetAttackRange (0x418160 / 0x4183d0)
   │     └── _CreatePattern: CActionSkill (0x41e060), CActionEnemyAttack (0x41a4a0), CActionJoinAttack (0x41c970)
   │
   ├── [M00.05] Target Resolution & Cover/Provoke/Redirect Hand-off
   │     ├── CBattle::_UpdateTargetRate (0x44a630: base share + Provoke 170 + 10*ench49 - 5*ench50, min 10)
   │     ├── CActionPatternBase::_BeforeAttackInterrupt (0x4200e0: passive 253 / 0xfd preemptive counter roll)
   │     ├── CActionPatternBase::_SelectTarget (0x420560: target validity, redirect 172 / 0xac & 324 / 0x144)
   │     └── Physical Cover _Cover (0x420b40, single-target pre-calc) vs Magic/AoE Cover (0x422b40, post-calc)
   │
   ├── [M00.06] Per-Hit Resolution: CActionPatternBase::_Task (0x420f10..0x423546)
   │     ├── Branch: _Steal (0x44fde0) | CalcPhysicalAttack (0x44a850) | CalcMagicalAttack (0x44d370) | Pure Commands
   │     ├── Physical: Hit roll -> ATK*var*fieldElem*skill - DEF*1.35 -> Range*Elem -> _CalcCritical (0x44f190) -> Min clamp -> Post-mults -> _CalcSpecialDamage (0x44f720) -> Cap/Barrier -> Interrupt roll (+33% on crit, passive 258)
   │     ├── Magical: Raw dmg (INT*var*fieldElem*skill - RES*1.5)*Elem -> Hit roll -> Magic Crit 301 (20% -> 1.25x) -> Missed-spell graze (1/2 or 3/4 via ench 272) -> Min clamp (1..5) -> Post-mults -> _CalcSpecialDamage -> Cap 296 -> Crit interrupt (33%)
   │     └── Post-calc: Elemental Zone shift -> Dispel 441 -> Barrier 261 -> _AfterHit1/2 -> Drains (10/11/135) -> CCommand::Execute (0x47e500) -> Sleep wake (116) & Chant Interrupt -> CBattle::TakeDamage (0x4e3f80)
   │
   ├── [M00.07] AfterHit & Interrupt Reactive Chain (0x423560..0x425bd7)
   │     ├── _AfterHit1 (0x423560): Devil's Whisper 320 (0x140) bonus command 119 damage on ailed target
   │     ├── _AfterHit2 (0x423810): Endure 254 (0xfe, clamp lethal dmg to CurHP-1), Push Back 54 (0x36, swap ATB gauge)
   │     ├── _CheckEachInterrupt (0x423cd0): Sugar Coma 262 (0x106), Dark Aura 293 (0x125), Counter 249 & Arcane Shield 447 rolls (!inCounter)
   │     └── _CheckAfterAttackInterrupt (0x4247e0): Cover aggro 171, Parry 250, Counter 249, Arcane Shield 447 (skill 240), Avenger 260 (!inCounter)
   │
   ├── [M00.08] Post-Action Resolution, AddStatus (0x4f9930), Extra-Turn Rolls & _SetTime (0x438c81..0x4392ea)
   │     ├── Action count [actor+0xb8]++, extra-turn count [actor+0xb0]++, Summon/Doll lifetime expiry (0x43b6a0 / 0x43d2c0)
   │     ├── Passive 291 (0x123) random stat +25% buff (jump table 0x439884)
   │     ├── Extra-turn rolls: 288 (0x120), 289 (0x121), 354 (0x162) -> set [actor+0x107]=1 & skip _SetTime
   │     └── CBattleBase::_SetTime (0x43e5c0) -> CBattle::_SetTime (0x4499d0) -> _SortTime (0x43e510) -> loop to State 0
   │
   └── [M00.09] Battle End, After-Battle Recovery & Rewards Hand-off
         ├── Per-hit/kill EXP scaling: CBattle::_AddExp (0x450710, level-diff table + enchant 270 / 0x10e)
         ├── Outer State 5 -> 6: Passive 218 (0xda) bonus EXP -> CBattleResult::_Initialize (0x445830: alive split, status 157 x2, ench 275 x2, Gold, Drops)
         └── CBattleBase::End (0x43d650): Party-wide passives 272/273 (capped 30%) + 353, enchants 193/194 (100% full heal), CCommand::Execute (0x47e500)
```

| Downstream Module | Scope Owned | Upstream Entry Points from `M00` |
|---|---|---|
| `M01` Turn Order & Loop | `CBattleBase::Update`, `_SetTime`, `_SortTime`, `_SetFirstAttack`, battle PRNG | `M00.01`, `M00.02`, `M00.03`, `M00.08` |
| `M02` Action & Pattern Dispatch | `_CreateAction`, `SetHitCount`, `SetAttackRange`, `CAction*`, `CActionPattern*` | `M00.03`, `M00.04`, `M00.05`, `M00.06` |
| `M03` Stats, Equipment & Legality | `CheckSkillCondition`, stat getters `vtable+0x34`, equipment & enchant queries `vtable+0xf0` | `M00.01`, `M00.04`, `M00.06`, `M00.08` |
| `M04` Targeting, Aggro & Cover | `_UpdateTargetRate`, `_SelectTarget`, `_Cover`, magic cover, `_BeforeAttackInterrupt` | `M00.01`, `M00.04`, `M00.05`, `M00.06` |
| `M05` Hit, Crit & Damage Formulas | `CalcPhysicalAttack`, `CalcMagicalAttack`, `_CalcCritical`, `_CalcElementRevision`, `_CalcSpecialDamage`, `_CalcFieldElementRevision`, Barrier `261`, Interrupt | `M00.06` |
| `M06` Ailments & Crowd Control | Turn-start self-cure, hard CC skip, Paralysis `114`, Panic `259`, Charm `283`, Temptation `203`, Sleep wake `116`, DoT/HoT | `M00.03`, `M00.06`, `M00.08` |
| `M07` Buffs, Debuffs & `AddStatus` | `CGamePlayerStatusBase::AddStatus` (`0x4f9930`), `CCommand::Execute` (`0x47e500`), status tick `vtable+0xdc` | `M00.03`, `M00.06`, `M00.07`, `M00.08` |
| `M08` Class Passives & Reactives | Turn-start auto-skills (`311/446/319/345/357/350/448/355/305/306`), `_AfterHit1/2` (`320/254/54`), `_CheckEachInterrupt` (`262/293/249/447`), `_CheckAfterAttackInterrupt` (`250/249/447/260`), post-action (`291/288/289/354`) | `M00.03`, `M00.05`, `M00.06`, `M00.07`, `M00.08` |
| `M09` Songs, Dances, Dolls, Co-op | Song/Dance/Puppet/Geass managers, `CActionJoinAttack`, Doll/Summon lifetime & turns | `M00.01`, `M00.02`, `M00.03`, `M00.04`, `M00.08` |
| `M10` Enemy AI & Boss Immunities | `CActionEnemyAttack`, enemy target selection, boss immunity bitmasks (`[enemyParam+0x50/+0x54]`) | `M00.04`, `M00.05`, `M00.06`, `M00.07` |
| `M11` Zones, Steal, Rewards & End | Floor elemental zones (`[battle+0x1e4..0x1f4]`), `_Steal`, `_AddExp`, `CBattleResult::_Initialize`, `CBattleBase::End` recovery | `M00.01`, `M00.02`, `M00.06`, `M00.09` |

---

## 2. Ordered Pipeline Rules (`M00.01` – `M00.09`)

### M00.01 Battle Initialization & Start

- **Binary VA(s):** `0x448c60..0x448ed5` (`CBattle::CBattle`), `0x43da60..0x43dee2` (`CBattleBase::_Initialize`), `0x43def0..0x43e500` (`CBattleBase::_SetPosition`), `0x449130..0x449532` (`CBattle::_Initialize`), `0x44a3d0..0x44a629` (`CBattle::_SetFirstAttack`), `0x43e510..0x43e5b7` (`CBattleBase::_SortTime`)
- **Owning Module(s):** `M01` (Turn Order & Initialization), `M04` (Initial Formation Shares), `M09` (Summon/Guest/Doll Init), `M11` (Floor Elemental Zones)
- **Calls:** `0x43da60` (`CBattleBase::_Initialize`), `0x43def0` (`CBattleBase::_SetPosition`), `0x490790` (`CRandom::Get`), `0x4499d0` (`CBattle::_SetTime`), `0x44a3d0` (`CBattle::_SetFirstAttack`), `0x43e510` (`CBattleBase::_SortTime`), `M00.02`
- **CalledBy:** Battle scene creation (`0x448c60`)
- **Typed Pseudocode:**
```text
function CBattle_ConstructAndInit(this: CBattle*, battleInfo: BattleInfo*, expMult: i32):
    // 1. Base state & container initialization (0x448c60..0x448de5)
    this.vtable = 0x6c9a98
    this.battleInfo = battleInfo               // [this+0x10]
    this.flags14 = 0x0101u16                   // [this+0x14]=1, [this+0x15]=1
    this.PhaseNo = 6                           // [this+0x18] (overwritten to 0 in _Initialize)
    this.PrevPhaseNo = 6                       // [this+0x1c]
    this.TurnPhaseNo = 0                       // [this+0x20]
    CBattleBase_Initialize(this)               // 0x43da60

    // 2. Inside CBattleBase::_Initialize (0x43da60..0x43dee2):
    formationId = GameManager.GetFormation()   // [0x71fc24]->vtable+0x17c()
    (frontCount, backCount) = GameManager.GetFormationCounts(0xb) // vtable+0x160()
    shareTable: i32* = &FormationShareTable_0x6517a0[formationId * 5]
    for i in 0 .. GameManager.GetPartyCount() - 1:
        member = GameManager.GetPartyMember(i) // vtable+0x150(i)
        unit = new BattleUnit_s()              // 0x114 bytes, 0x43a010 / 0x435890
        unit.slotIdx = i                       // [unit+0x00]
        unit.unitId = member.GetMemberId()     // [unit+0x04] (0..999 for party)
        unit.sortTiebreak = 999 - i            // [unit+0x0c] (0x3e7 - i)
        unit.status = member                   // [unit+0x10] & [unit+0x14]
        unit.baseShare = shareTable[i]         // [unit+0x74]
        unit.isPlayerSide = 1u8                // [unit+0x78] = 1
        unit.isFrontRow = (u32(i) < frontCount) ? 1u8 : 0u8 // [unit+0x79]
        this.units.push_back(unit)             // [this+0x24..0x28]
    if this.isNotRetry == 0:
        CBattleBase_SetPosition(this)          // 0x43def0: builds row adjacency lists [unit+0x64]
    this.jitterRng = new CRandom()             // [this+0x1bc], 0x24 bytes
    this.jitterRng.seed0 = GlobalRng_0x816ce8.Rand(0x7fffffff) // [rng+0x1c]
    this.jitterRng.seed1 = GlobalRng_0x816ce8.Rand(0x7fffffff) // [rng+0x20]

    // 3. Floor Elemental Zone initialization (0x448e24..0x448e5c)
    this.vtable = 0x6c9b60
    this.fieldElemState = 0                    // [this+0x1e0]
    this.fieldElemMult[0..4] = [1.0f, 1.0f, 1.0f, 1.0f, 1.0f] // [this+0x1e4..0x1f4] = 0x3f800000

    // 4. Inside CBattle::_Initialize (0x449130..0x449532):
    for unit in this.units:
        if unit.unitId in 3000..3999:          // 0xbb8..0xf9f (Summon/Guest)
            unit.gauge = (this.flag33 != 0) ? 1.0f : 0.0f // [unit+0x08]
        else:
            this.vtable_SetTime(unit, 0)       // 0x4499d0: initial ATB gauge [unit+0x08]
    // First-strike arbitration (0x4492b4..0x44931d):
    // Checks CBattle::_SetFirstAttack(side, baseRate, isPlayer) (0x44a3d0):
    //   - Forced preemptive command 321 (0x141) -> rate = 1000
    //   - Adds passive 268 (0x10c) * 100 (round_f32_to_i32 via 0x61e650)
    //   - Rolls GlobalRng.Rand(100) < rate
    //   - Unless rate >= 1000, checks opposing side's anti-ambush passive 267 (0x10b):
    //     if GlobalRng.Rand(100) < round_f32_to_i32(cmd267.val * 100.0f), blocks first strike!
    //   - On success: sets [u+0x08] = 1.0f (0x3f800000) for all units on winning side!
    this.vtable_SortTime(0, 1)                 // 0x43e510: sorts [this+0x24] by [u+0x08] desc, normalizes head to 1.0f
    this.PhaseNo = 0                           // [this+0x18] = 0
```
- **Program Evidence:**
```asm
0043dac4  lea      eax, [edi + edi*4]
0043dac7  lea      eax, [eax*4 + 0x6517a0]
0043db23  mov      eax, 0x3e7
0043db28  sub      eax, ebx
0043db2a  mov      dword ptr [edi + 0xc], eax
0043db33  mov      eax, dword ptr [esi]
0043db35  mov      dword ptr [edi + 0x74], eax
0043db38  mov      byte ptr [edi + 0x78], 1
0043db3c  cmp      ebx, dword ptr [ebp - 0x1c]
0043db3f  setb     al
0043db42  mov      byte ptr [edi + 0x79], al
00448e34  mov      dword ptr [esi + 0x1e4], 0x3f800000
00448e3e  mov      dword ptr [esi + 0x1e8], 0x3f800000
00448e48  mov      dword ptr [esi + 0x1ec], 0x3f800000
00448e52  mov      dword ptr [esi + 0x1f0], 0x3f800000
00448e5c  mov      dword ptr [esi + 0x1f4], 0x3f800000
0044a3eb  push     0x141
0044a407  mov      ecx, 0x3e8
0044a40c  cmovne   ebx, ecx
0044a429  push     0x10c
0044a464  cmp      eax, ebx
0044a466  jge      0x44a61e
0044a487  push     0x10b
0044a4c5  cmp      eax, ebx
0044a4c7  jl       0x44a61e
0044a4f8  mov      dword ptr [eax + 8], 0x3f800000
```

---

### M00.02 Outer `CBattleBase::Update` State Machine

- **Binary VA(s):** `0x448ee0..0x448fc2` (`CBattle::Update`), `0x4360f0..0x4397dc` (`CBattleBase::Update`), `0x4397e0..0x43981f` (16-entry outer jump table for `[this+0x18]`)
- **Owning Module(s):** `M01` (Combat Loop & State Machine), `M02` (Action Execution Hand-off), `M09` (Summon Samba Tick & Turn Skip), `M10` (Enemy AI Hand-off), `M11` (Victory/Defeat/Escape Transitions)
- **Calls:** `0x43b510` (count alive enemies), `0x43e5c0` (`CBattleBase::_SetTime`), `M00.03`, `M00.04`, `M00.08`, `M00.09`
- **CalledBy:** `CBattle::Update` (`0x448f9e`), `M00.01`
- **Typed Pseudocode:**
```text
function CBattleBase_Update(this: CBattleBase*) -> bool:
    // Dispatches on this.PhaseNo ([this+0x18] in 0..15) via jump table at 0x4397e0:
    switch this.PhaseNo:
        case 0: // 0x43625b — Turn Start & Actor Selection
            if !BattleUI_IsReady(): return true
            if this.GetAliveEnemyCount() == 0:             // 0x43b510
                this.PhaseNo = 5                           // Victory
                return true
            actor = this.units[0]                          // [this+0x24][0]
            while actor.status.vtable_0x38_IsDeadOrGone(): // 0x4362a2..0x4362cd
                this._SetTime(0)                           // 0x43e5c0(0)
                actor = this.units[0]
            while actor.unitId >= 4000:                    // 0xfa0 sentinel (0x4362cf..0x4362fe)
                actor.gauge = 0.0f
                this.vtable_SortTime(1, 0)
                actor = this.units[0]
            this.activeStatus = actor.status               // [this+0x40] = [actor+0x10]
            if actor.extraTurnCount != 0:                  // [actor+0xb0] != 0 at 0x436314
                goto LABEL_ACTION_PHASE_0x43875a           // Extra-turn re-entry skips TurnPhaseNo!
            if actor.unitId in 3000..3999:                 // 0xbb8..0xf9f (Summon/Guest, 0x436322..0x4365fb)
                // Runs 2-step TurnPhaseNo (0 -> 1 -> 2) ticking Samba Dance 199 (0xc7):
                // Deal trunc0(f32(target.MaxHP) * cmd199.val) HP damage via CCommand::Execute (0x47e500)
                if this.TurnPhaseNo < 2 or this.PhaseNo != 0: return true
            if actor.extraTurnCount != 0:                  // [actor+0xb0] != 0 at 0x4365ff
                goto LABEL_ACTION_PHASE_0x43875a
            if actor.unitId in 2000..2999 or actor.unitId in 3000..3999 or actor.unitId >= 4000:
                goto LABEL_ACTION_PHASE_0x43875a           // Dolls/Summons/Guests skip 25-state machine!
            return M00_03_InnerTurnStartMachine(this, actor)

        case 1: // 0x4387b0 — Action Readiness / Chant Completion / Menu or AI Trigger
            // Checks chant completion ([actor+0x1c] in {3, 9}), enemy/doll AI selection (0x43d420),
            // or opens player command menu (PhaseNo = 2) / creates action directly (PhaseNo = 3)
        case 2: // 0x438987 — Player Command Menu Input Poll
            // Polls player command menu ([this+0x38]); on confirm -> _CreateAction (0x43ea70) -> PhaseNo = 3;
            // on party formation change -> PhaseNo = 9
        case 3: // 0x438c5a — Active CAction Execution & Post-Action Resolution
            // Calls this.currentAction.Update() ([this+0x44]->vtable+0x04()); when done -> M00.08
        case 4: // 0x4392ef — Incapacitated / Skipped Turn Advance
            // Sets [actor+0x1c] = 7, calls _SetTime(0) (0x43e5c0), resets TurnPhaseNo = 0, PhaseNo = 0
        case 5: // 0x439331 — Victory Initialization (allocates CBattleResult 0x443c30 -> PhaseNo = 6)
        case 6: // 0x439426 — Victory Result Screen Loop (0x444340; when done -> PhaseNo = 10, returns false)
        case 7: // 0x43945a — Defeat / Party Wipe Initialization (allocates defeat handler 0x48f930 -> PhaseNo = 8)
        case 8: // 0x4394af — Defeat Screen Loop (0x48fa50; sets [this+0x61]=1, returns false)
        case 9: // 0x4394dc — Formation Change / Escape Sub-Menu ([this+0x64] poll)
        case 10: // 0x439527 — Post-Victory Transition Wait (0x43f070 -> returns false to end battle)
        case 11: // 0x439541 — Turn-Start Direct CActionPattern Update ([this+0x48]->vtable+0x04(), e.g. U0008/E1580/E0822/E0835/T0094)
        case 12: // 0x439584 — Turn-Start Direct CAction Update ([this+0x44]->vtable+0x04(), e.g. Panic 259 / Charm 283 / Temptation 203)
        case 13: // 0x439613 — Ambush Random Debuff Application (picks Rand(7) from 0x6c9af8 at -0.75f -> PhaseNo = 14)
        case 14: // 0x4396ba — Wait for Popup/Effect Completion (0x43f070(1) -> PhaseNo = 0)
        case 15: // 0x4396d0 — Remove Fled/Banished Unit (0x4f22f0 -> 0x43b6a0 -> TurnPhaseNo = 0, PhaseNo = 0)
```
- **Program Evidence:**
```asm
00436248  mov      eax, dword ptr [edi + 0x18]
0043624b  cmp      eax, 0xf
0043624e  ja       0x439702
00436254  jmp      dword ptr [eax*4 + 0x4397e0]
0043627f  call     0x43b510
00436284  test     eax, eax
00436286  je       0x438793
00436314  mov      eax, dword ptr [esi + 0xb0]
0043631a  test     eax, eax
0043631c  jne      0x43875a
004363d0  cmp      dword ptr [edx], 0xc7
004365ff  mov      eax, dword ptr [esi + 0xb0]
00436605  test     eax, eax
00436607  jne      0x43875a
0043660d  mov      eax, dword ptr [esi + 4]
00436610  cmp      eax, 0x7d0
00436617  cmp      eax, 0xbb8
00436626  jne      0x43875a
0043662c  cmp      eax, 0xbb8
00436633  cmp      eax, 0xfa0
00436642  jne      0x43875a
```

---

### M00.03 Inner Turn-Start State Machine

- **Binary VA(s):** `0x436700..0x438759` (inner turn-start dispatcher in `CBattleBase::Update`), `0x439820..0x439883` (25-entry jump table for `TurnPhaseNo` `[this+0x20]` in `0..24`)
- **Owning Module(s):** `M01` (Turn-Start Sequencing), `M06` (Ailment Self-Cure, Hard Incapacitation, Paralysis `114`, Panic `259`, Charm `283`, Temptation `203`, DoT/HoT & Enchant Regen), `M07` (Status Tick `vtable+0xdc`), `M08` (Turn-Start Auto-Passives `311`, `446`, `319`, `345`, `357`, `350`, `448`, `355`, `305`, `306`), `M09` (Dances `200`, `204`, `199` & Geass `339`)
- **Calls:** `0x61e650` (`round_f32_to_i32`), `0x505ac0` (`Rand(100)`), `0x47e500` (`CCommand::Execute`), `0x42f870` (`CActionPatternU0008`), `0x42be90` (`CActionPatternE1580`), `0x42b240` (`CActionPatternE0822`), `0x42b8a0` (`CActionPatternE0835`), `0x42ec90` (`CActionPatternT0094`), `0x414e20` (`CActionAttack`), `0x419ad0` (`CActionEnemyAttack`), `0x41d480` (`CActionSkill`)
- **CalledBy:** `M00.02` (`CBattleBase::Update` Outer State 0 at `0x436700`)
- **Typed Pseudocode:**
```text
function M00_03_InnerTurnStartMachine(this: CBattleBase*, actor: BattleUnit_s*):
    // Dispatches on this.TurnPhaseNo ([this+0x20] in 0..24) via jump table at 0x439820.
    // Every state increments this.TurnPhaseNo++ on entry.
    switch this.TurnPhaseNo:
        case 0: // 0x436713 — Reset flags & Passive 311 (0x137) Ailment Purge
            actor.isConfusedAttack = 0u8; actor.grantedExtraTurn = 0u8 // [actor+0x105]=0, [actor+0x107]=0
            if cmd311 = actor.status.GetCommand(0, 0x137):
                count = round_f32_to_i32(cmd311.val) // 0x61e650
                // Removes up to `count` ailments from table 0x6c9a7c via CCommand::Execute (0x47e500) -> PhaseNo = 14
        case 1: // 0x43692f — Turn-Start Status Hook: actor.status.vtable_0xd8(this.battleInfo)
        case 2: // 0x436955 — Passive 345 (0x159, Turn-Start Self Status)
            // If present & Rand(100) < trunc0(cmd345.val * 100.0f): applies via vtable+0x54 -> PhaseNo = 14
        case 3: // 0x436a9b — Passive 446 (0x1be, Maid/Auto-Skill U0008)
            if cmd446 = actor.status.GetCommand(0, 0x1be):
                if Rand(100) < trunc0(cmd446.val * 100.0f):
                    this.currentPattern = new CActionPatternU0008(this.battleInfo, &actor.action) // 0x42f870
                    this.PhaseNo = 11
        case 4: // 0x436be4 — Stun 120 (0x78) Command Update (cmd120.vtable_0x0c() -> 0x47e500)
        case 5: // 0x436c3f — Dead/Gone Check (actor.status.vtable_0xc8() -> 0x43a4a0 -> PhaseNo = 15 or 4)
        case 6: // 0x436ca1 — Hard Incapacitation Gate (actor.status.vtable_0xbc() Sleep/Freeze/Stun -> PhaseNo = 4)
        case 7: // 0x436d08 — Paralysis (114) Gate
            if actor.status.vtable_0xb8_IsParalyzed():
                if Rand(100) < 30:           // 0x505ac0(0x64) < 0x1e at 0x436d1d..0x436d27
                    // Log paralysis skip -> PhaseNo = 4
        case 8: // 0x436d4c — Status Duration Tick: actor.status.vtable_0xdc_TickStatuses(this.battleInfo)
        case 9: // 0x436d60 — Status 259 (0x103, Panic / Confusion)
            if cmd259 = actor.status.GetCommand(0, 0x103):
                if Rand(100) < trunc0(cmd259.val * 100.0f): // 0x436daf..0x436dd8
                    actor.isConfusedAttack = 1u8 // [actor+0x105] = 1 at 0x4370b3 (0.3x damage in CalcPhysicalAttack)
                    // Picks random target from shuffled pool, creates CActionAttack (0x414e20) or CActionEnemyAttack (0x419ad0) -> PhaseNo = 12
        case 10: // 0x436e0c — Status 283 (0x11b, Charm): rolls Rand(100) < trunc0(cmd283.val * 100.0f) -> PhaseNo = 4
        case 11: // 0x436eb0 — Status 203 (0xcb, Temptation): rolls Rand(100) < trunc0(cmd203.val * 100.0f) -> PhaseNo = 4 or 12
        case 12: // 0x437364 — Passive 319 (0x13f, Auto-Skill E1580)
            if cmd319 = actor.status.GetCommand(0, 0x13f):
                if Rand(100) < trunc0(cmd319.val * 100.0f):
                    this.currentPattern = new CActionPatternE1580(this.battleInfo, &actor.action) // 0x42be90
                    this.PhaseNo = 11
        case 13: // 0x437499 — Passive 357 (0x165, Turn-Start Enemy ATK/RES -10% Debuff) -> PhaseNo = 14
        case 14: // 0x4376e3 — Passive 350 (0x15e, Turn-Start Banish Enemy Doll via 0x43b6a0) -> PhaseNo = 14
        case 15: // 0x4378d9 — Passive 448 (0x1c0, Turn-Start Auto-Deploy Doll)
            // If present & Rand(100) < trunc0(cmd448.val * 100.0f) and no Doll owned by actor: spawns Doll (0x4fe2e0 / 0x43a150) -> PhaseNo = 14
        case 16: // 0x437b0c — Turn-Start DoT/HoT & Equipment Enchant HP/TP Regen
            // 1. Executes all active commands on actor where cmd->vtable+0x80() (isTurnStartTick) is true
            // 2. Equipment HP regen enchants:
            //    - 144 (0x90): max(4, trunc0(MaxHP * 0.04f * count))
            //    - 145 (0x91): max(2, trunc0(MaxHP * 0.02f * count))
            //    - 148 (0x94): max(10, trunc0(MaxHP * 0.08f * count))
            //    - 296 (0x128): if count > 0 and Rand(100) < 4: +MaxHP (full HP heal!)
            // 3. Equipment TP regen enchants:
            //    - 146 (0x92): +4 * count
            //    - 147 (0x93): +2 * count
            //    - 149 (0x95): +6 * count
            // 4. Applies combined HP/TP delta via CCommand::Execute (0x47e500)
        case 17: // 0x437ed6 — Post-Regen Fall-through into Dance Checks
        case 18: // 0x437eda — Dance 200 (0xc8) -> CActionPatternE0822 (0x42b240) -> PhaseNo = 11
        case 19: // 0x438085 — Dance 204 (0xcc) -> CActionPatternE0835 (0x42b8a0) -> PhaseNo = 11
        case 20: // 0x43824e — Dance 199 (0xc7) / Geass 339 (0x153) -> CActionPatternT0094 (0x42ec90) -> PhaseNo = 11
        case 21: // 0x43841e — Poison 113 (0x71) Turn-Start Damage Tick (0x482150 -> CCommand::Execute 0x47e500)
        case 22: // 0x438495 — Passive 355 (0x163, Turn-Start Auto-Revive Dead Ally with 1 HP via 0x47e500 & vtable+0x24(1,1)) -> PhaseNo = 14
        case 23: // 0x4386ff — Increment TurnPhaseNo to 24 (0x18)
        case 24: // 0x438722 — Terminal Check (TurnPhaseNo >= 24 && PhaseNo == 0 -> proceeds to 0x43875a -> PhaseNo = 1)
```
- **Program Evidence:**
```asm
00436700  mov      eax, dword ptr [edi + 0x20]
00436703  cmp      eax, 0x18
00436706  ja       0x438705
0043670c  jmp      dword ptr [eax*4 + 0x439820]
00436d1d  mov      ecx, 0x64
00436d22  call     0x505ac0
00436d27  cmp      eax, 0x1e
00436d89  push     0x103
00436daf  mov      ecx, 0x64
00436db7  call     0x505ac0
004370b3  mov      byte ptr [esi + 0x105], 1
00437ce9  mulss    xmm0, dword ptr [ebp - 0x10]
00437cee  cvttss2si eax, xmm0
00437cf2  cmp      eax, ecx
00437cf4  cmovl    eax, ecx
00437cfd  push     0x128
00437d10  mov      ecx, 0x64
00437d15  call     0x505ac0
00437d1a  cmp      eax, 4
00438066  call     0x42b240
0043806e  mov      dword ptr [edi + 0x48], eax
00438071  mov      dword ptr [edi + 0x18], 0xb
```

---

### M00.04 Action Selection, Legality Gate & `_CreatePattern` Dispatch

- **Binary VA(s):** `0x4f4910..0x4f4c30` (`CGamePlayerStatusBase::CheckSkillCondition`, jump table `0x4f4bdc`), `0x43ea70..0x43f044` (`CBattleBase::_CreateAction`, jump table `0x43f020`), `0x417cd0..0x418152` (`CActionBase::Action_s::SetHitCount`), `0x418160..0x418475` (`SetAttackRange`), `0x41a4a0..0x41a84a` (`CActionEnemyAttack::_CreatePattern`), `0x41c970..0x41cbd0` (`CActionJoinAttack::_CreatePattern`), `0x41e060..0x41e63c` (`CActionSkill::_CreatePattern`)
- **Owning Module(s):** `M02` (Action & Pattern Dispatch, Hit Count & Range Setup), `M03` (Weapon Condition Legality `CheckSkillCondition`), `M09` (Co-op / Joint Attack `CActionJoinAttack`), `M10` (Enemy Attack Pattern Dispatch)
- **Calls:** `0x4f4f60` (`GetEquipmentID`), `0x559260` (`GetWeaponCategory`), `0x559290` (`IsMeleeWeapon`), `0x559190` (`IsShield`), `0x417cd0` (`SetHitCount`), `0x418160` (`SetAttackRange`), `0x41a4a0`, `0x41c970`, `0x41e060`, `M00.05`
- **CalledBy:** `M00.02` (Outer States 1, 2, 3), `M00.03` (Inner States 3, 4, 6, 7, 12, 13, 15, 17), `M00.07` (`_SetupCounter` `0x425930`)
- **Typed Pseudocode:**
```text
function CheckSkillCondition(status: CGamePlayerStatusBase*, condType: i32) -> bool:
    // Jump table at 0x4f4bdc indexed by (condType + 1) in 0..20:
    switch condType:
        case -1: return true
        case 0:  id = status.GetEquipmentID(0); return id != -1 and IsMeleeWeapon(id)      // 0x559290
        case 1..14: id = status.GetEquipmentID(0); return id != -1 and GetWeaponCategory(id) == (condType - 1) // 0x559260
        case 15: id = status.GetEquipmentID(0); return id != -1 and GetWeaponCategory(id) in 14..20 // 0x0e..0x14 ranged
        case 16: id = status.GetEquipmentID(1); return id != -1 and IsShield(id)           // 0x559190
        case 17: return status.GetEquipmentID(2) != -1
        case 18: return status.GetEquipmentID(3) != -1
        case 19: return status.GetEquipmentID(0) != -1

function CBattleBase_CreateAction(this: CBattleBase*, act: Action_s*) -> CActionBase*:
    // If joint attack skill is active (0x43ea93..0x43ed24), constructs CActionJoinAttack (0x41c640).
    // Otherwise dispatches on act.actionType ([act+0x04] in 0..9) via jump table at 0x43f020:
    //   0 -> CActionAttack (0x414e20)
    //   1 -> CActionSkill(isChantStart=0) (0x41d480)
    //   2 -> CActionSkill(isChantStart=0) (0x41d480)
    //   3 -> CActionSkill(isChantStart=1) (0x41d480)
    //   4 -> CActionItem (0x41b440)
    //   5 -> CActionDefense (0x4199b0)
    //   6 -> CActionEscape (0x41ae00)
    //   7 -> return null (incapacitated / no-op)
    //   8 -> CActionEnemyAttack(isChantStart=0) (0x419ad0)
    //   9 -> CActionEnemyAttack(isChantStart=1) (0x419ad0)

function Action_s_SetHitCount(act: Action_s*, status: CGameStatusBase*):
    // Evaluates command hit-count modifiers 89..100 (0x59..0x64) and 178 (0xb2).
    // For basic physical attacks (actionType == 1 or enemy basic attack flag bit 0):
    //   - If status has passive 252 (0xfc) and Rand(100) < trunc0(cmd252.val * 100.0f): hitCount = 3
    //   - Else if status has passive 251 (0xfb) and Rand(100) < trunc0(cmd251.val * 100.0f): hitCount = 2
    //   - Else: hitCount = 1 ([act+0x40] = 1)

function CAction_CreatePattern_Dispatch(action: CActionBase*):
    // 1. CActionSkill::_CreatePattern (0x41e060): switches on skill.GetPatternType() (0x56d450) via 0x41e5fc
    //    to instantiate CActionPatternA..M, E0260..E1590, S0150..S1080, T0080..T0150, U0005.
    // 2. CActionEnemyAttack::_CreatePattern (0x41a4a0): switches on [enemySkill+0xa8] (0..17) via 0x41a814
    //    (case 6 -> CActionPatternE1630 0x42c940; case 16 -> weighted random table 0x64f1c0 via CActionPatternL).
    // 3. CActionJoinAttack::_CreatePattern (0x41c970): switches on skill.GetPatternType() (0..6) via 0x41cbd0
    //    (cases 0..5 -> CActionPatternA/B/F/G/H/M via 0x41f4b0; case 6 -> CActionPatternE1630 0x42c940).
```
- **Program Evidence:**
```asm
004f4917  lea      esi, [edx + 1]
004f491a  cmp      esi, 0x14
004f491d  ja       0x4f4bc1
004f4923  jmp      dword ptr [esi*4 + 0x4f4bdc]
0041a4ed  mov      ecx, dword ptr [eax + 0xa8]
0041a4f3  cmp      ecx, 0x11
0041a4f6  ja       0x41a7fa
0041a4fc  movzx    eax, byte ptr [ecx + 0x41a838]
0041a503  jmp      dword ptr [eax*4 + 0x41a814]
0041c9a0  call     0x56d450
0041c9a5  cmp      eax, 6
0041c9a8  ja       0x41cbb4
0041c9ae  jmp      dword ptr [eax*4 + 0x41cbd0]
0041e098  call     0x56d450
0041e09d  cmp      eax, 0xf
0041e0a0  ja       0x41e5e0
0041e0a6  jmp      dword ptr [eax*4 + 0x41e5fc]
```

---

### M00.05 Target Resolution & Cover/Provoke/Redirect Hand-off

- **Binary VA(s):** `0x44a630..0x44a793` (`CBattle::_UpdateTargetRate`), `0x41a850..0x41ab93` (`CActionEnemyAttack::_SelectTarget`), `0x4200e0..0x420466` (`CActionPatternBase::_BeforeAttackInterrupt`), `0x420470..0x420555` (`CActionPatternBase::_CheckTarget`), `0x420560..0x420b34` (`CActionPatternBase::_SelectTarget`), `0x420b40..0x420f02` (`CActionPatternBase::_Cover`), `0x422b40..0x422cf8` (magic/AoE cover inside `CActionPatternBase::_Task`)
- **Owning Module(s):** `M04` (Target Selection, Aggro Shares, Redirect & Cover), `M08` (Pre-Attack Interrupt `303` / `0x12f`, Cover `171` / `0xab`, Counter Immunity `307` / `0x133`)
- **Calls:** `0x43e6d0` (collect targetable units), `0x490790` (`CRandom::Get`), `0x425930` (`_SetupCounter`), `0x43b580` (check unit alive/valid), `M00.06`
- **CalledBy:** `M00.04` (`CAction*::Update` / `CActionPatternBase::Update`), `M00.06` (`CActionPatternBase::_Task`)
- **Typed Pseudocode:**
```text
function CBattle_UpdateTargetRate(this: CBattle*, attacker: BattleUnit_s*):
    // 0x44a630..0x44a793: Recomputes effective aggro weight [u+0x70] for each alive player unit u:
    for u in this.GetAlivePlayerUnits():
        rate: i32 = u.baseShare                        // [u+0x70] = [u+0x74]
        if cmd170 = attacker.enemyStatus.GetCommand(0, 0xaa): // Provoke / Taunt (170)
            if cmd170.GetActorId() == u.playerStatus.GetMemberId():
                rate += trunc0(cmd170.val)             // cvttss2si at 0x44a71c
        rate += 10 * u.status.GetEnchantCount(0x31)    // Enchant 49 (+10 aggro per stack)
        rate -=  5 * u.status.GetEnchantCount(0x32)    // Enchant 50 (-5 aggro per stack)
        u.targetRate = max(10, rate)                   // cmp ecx, 0xa; cmovl ecx, eax at 0x44a757

function CActionPatternBase_BeforeAttackInterrupt(this: CActionPatternBase*, checkCounter: bool):
    // 0x4200e0..0x420466:
    // 1. Sets this.isPhysical = HasCommand(0) or HasCommand(1) ([this+0x79], [this+0x7a]).
    // 2. If command 137 (0x89, AoE/Row Splash) is present, appends splash targets to [Action_s+0x20].
    // 3. Pre-attack interrupt gate (0x42034b..0x420446):
    if checkCounter and this.battle != null:
        actorUnit = this.battle.GetUnit(this.action.actor)
        if actorUnit.unitId not in 2000..3999 and !this.inCounter and this.isPhysical:
            if !this.action.actor.HasCommand(0x133):   // 307 Counter Immunity
                for slot in this.action.targetSlots:
                    if slot.subHitIdx == 0 and (cmd303 = slot.target.GetCommand(0, 0x12f)): // 303 Pre-Attack Counter
                        this._SetupCounter(slot.target, cmd303) // 0x425930
                        this.PatternPhaseNo = 9        // [this+0x18] = 9 (interrupts before hit!)
                        break

function CActionPatternBase_SelectTarget_And_Cover(this: CActionPatternBase*):
    // 1. _SelectTarget (0x420560): validates current target slot ([Action_s+0x20] + 0x4c * hitIdx)
    //    via 0x43b580; if dead, re-selects alive target according to TargetType (0..6, jump table 0x420868).
    // 2. Physical Single-Target Cover _Cover (0x420b40..0x420f02):
    //    Requires this.isPhysical ([this+0x79] != 0), TargetType in {0, 1}, and !slot.wasCovered ([slot+0x44] == 0).
    //    Collects all alive allies `c != slot.target` on target's side that have active command 171 (0xab, Cover)
    //    (`c->vtable+0x50(0xab)` is true at 0x420c48).
    //    If candidate pool is non-empty: picks `coverer = candidates[GlobalRng.Rand(candidates.size())]` (0x420ca7),
    //    replaces target slot with `coverer`, and sets `slot.wasCovered = 1` ([slot+0x44] = 1 at 0x420eb3).
    // 3. Magic / AoE Cover (0x422b40..0x422cf8 inside _Task):
    //    Evaluated AFTER damage calculation when `!this.isPhysical` (or multi-target) and HP damage > 0:
    //    collects allies with command 171 (0xab), picks random coverer, and redirects TaskResult target to coverer.
```
- **Program Evidence:**
```asm
0044a6ca  mov      eax, dword ptr [edi + 0x74]
0044a6d0  mov      dword ptr [edi + 0x70], eax
0044a6e1  push     0xaa
0044a71c  cvttss2si eax, dword ptr [ebp - 0x14]
0044a721  add      dword ptr [edi + 0x70], eax
0044a727  push     0x31
0044a734  push     0x32
0044a757  cmp      ecx, 0xa
0044a75a  cmovl    ecx, eax
0044a75d  mov      dword ptr [edi + 0x70], ecx
004203b4  push     0x133
004203fd  push     0x12f
0042043a  call     0x425930
0042043f  mov      dword ptr [ebx + 0x18], 9
00420c48  push     0xab
00420ca6  push     edi
00420ca7  call     0x490790
```

---

### M00.06 Hit -> Crit -> Damage -> Barrier -> TakeDamage -> Interrupt Hand-off

- **Binary VA(s):** `0x420f10..0x423546` (`CActionPatternBase::_Task`), `0x44a850..0x44d366` (`CBattle::CalcPhysicalAttack`), `0x44d370..0x44f18c` (`CBattle::CalcMagicalAttack`), `0x44f190..0x44f5c4` (`CBattle::_CalcCritical`), `0x44f5d0..0x44f715` (`CBattle::_CalcElementRevision`), `0x44f720..0x44fb7a` (`CBattle::_CalcSpecialDamage`), `0x44fbb0..0x44fdd2` (`CBattle::_CalcFieldElementRevision`), `0x44fde0..0x45069c` (`CBattle::_Steal`), `0x47e500..0x47f8f0` (`CCommand::Execute`)
- **Owning Module(s):** `M05` (Hit, Crit, Physical/Magical/Special Damage, Elemental & Field Revisions, Barrier `261`, Chant Interrupt), `M06` (Sleep Wake `116` & Chant/Song/Dance Cancel on Interrupt), `M07` (`CCommand::Execute`), `M11` (Elemental Zone Shift & `_Steal`)
- **Calls:** `0x44a850` (`CalcPhysicalAttack`), `0x44d370` (`CalcMagicalAttack`), `0x44f190` (`_CalcCritical`), `0x44f5d0` (`_CalcElementRevision`), `0x44f720` (`_CalcSpecialDamage`), `0x44fbb0` (`_CalcFieldElementRevision`), `0x44fde0` (`_Steal`), `0x423560` (`_AfterHit1`), `0x423810` (`_AfterHit2`), `0x47e500` (`CCommand::Execute`), `0x4e3f80` (`CBattle::TakeDamage`), `M00.07`
- **CalledBy:** `CActionPatternBase::Update` (`0x41f750..0x41fe00`), `M00.05`
- **Typed Pseudocode:**
```text
function CBattle_CalcPhysicalAttack(this: CBattle*, res: TaskResult*, target: BattleUnit_s*, actor: BattleUnit_s*, actCmds: Vec*, tgtCmds: Vec*):
    // 1. Hit Roll (0x44a9e6..0x44b21c)
    baseHit: f32 = ((f32(actor.DEX + 100) * 0.885f) / f32(target.AGI + 100) + weaponHit + hitBuffs - evaBuffs) * 100.0f
    hitEnchant: f32 = min(50.0f, 4.0f * actor.ench(31) + 2.0f * actor.ench(32))
    evaEnchant: f32 = min(50.0f, 4.0f * target.ench(35) + 2.0f * target.ench(36))
    hitRate: f32 = clamp((baseHit + hitEnchant - evaEnchant) / (1.0f + cmd221.val), 5.0f, 100.0f)
    // Overrides: cmd 55 (0x37) or cmd 72 (0x48) -> cmd.val * 100.0f; target.IsIncapacitated (vtable+0xbc) -> 100.0f;
    // flying/ranged immunity (149/150) -> 0.0f.
    if GlobalRng.Rand(100) >= round_f32_to_i32(hitRate): // 0x44b0f3..0x44b115
        res.resultType = 3                               // Miss (skips crit, damage, and interrupt!)
        return

    // 2. Base Damage, Variance, Field Element, DEF, Range & Element Revision (0x44b221..0x44bcd5)
    v: i32 = round_f32_to_i32(weaponVar * 100.0f)
    varMult: f32 = 2.0f + f32(GlobalRng.Rand(2 * v + 1) - v) * 0.01f
    atkTerm: f32 = this._CalcFieldElementRevision(actor, 1) * (f32(statVal) * statScale * varMult + flatBonus) * skillMult * passiveMult
    defTerm: f32 = cmd69_ignoreDef ? 0.0f : (f32(target.DEF) * 1.35f * (1.0f + defBuffs) * (1.0f + min(50.0f, 4.0f*target.ench(33) + 2.0f*target.ench(34))*0.01f))
    rawDmg: f32 = (atkTerm * defMult_cmd73 - defTerm) * this._GetAttackRangeRevision(range, dist) * physRedEnch * this._CalcElementRevision(target, actor)

    // 3. Critical Roll (0x44c4ca..0x44c54b -> _CalcCritical 0x44f190)
    // critRate = clamp(((DEX*0.2f/(DEX+AGI))*100.0f + max(0.0f, (actorLv-targetLv)*0.5f) + critEnch) * critMults, minCrit, 50.0f)
    // Rolls GlobalRng.Rand(100) < trunc0(critRate) -> critMult = 1.25f (0x3fa00000) or 1.0f; sets res.isCrit = (critMult != 1.0f)
    if target.IsDefending(): rawDmg *= 0.5f
    dmg: i32 = trunc0(rawDmg * racialAndCondMults * critMult) // cvttss2si at 0x44cacc
    if actor.isConfusedAttack != 0: dmg = (dmg * 3) / 10      // [actor+0x105] != 0 at 0x44caea
    if dmg <= 0: dmg = res.isCrit ? 3 : (GlobalRng.Rand(2) + 1) // 0x44cb12..0x44cb5f

    // 4. Post-Truncation Multipliers, Special Damage, Cap & Interrupt Roll (0x44cb5f..0x44d336)
    // Applies ally row guard 356 (0x164), over-100% TP scaling 440 (0x1b8), incapacitated target 1.5x ((dmg*3)/2),
    // ailed target +15% (passive 280), class bonus 2x (cmd 86), _CalcSpecialDamage (0x44f720), and damage cap (0x48c640).
    // Chant Interrupt roll (0x44cfad..0x44d246):
    intRate: f32 = clamp(f32(dmg) / (f32(target.MaxHP) * 1.5f + 1.0f + cmd264) - intResEnch, 0.0f, 0.95f)
    res.isInterrupted = (GlobalRng.Rand(100) < trunc0(intRate * 100.0f))
    if res.isCrit and GlobalRng.Rand(100) < 33: res.isInterrupted = 1 // +33% independent crit interrupt roll!
    if res.isCrit and actor.HasPassive(0x102): ExecuteCritStun119()   // Passive 258

function CBattle_CalcMagicalAttack(this: CBattle*, res: TaskResult*, target: BattleUnit_s*, actor: BattleUnit_s*, actCmds: Vec*, tgtCmds: Vec*):
    // 1. Hit Rate & Pre-Hit Raw Magic Damage (0x44d56d..0x44ed7a)
    // hitRate = clamp(baseHit + (actor.INT - target.RES)*0.2f + magHitEnch - magEvaEnch + buffs, 25.0f, 95.0f)
    // Computes rawMagicDmg = ((INT * varMult * _CalcFieldElementRevision(actor, 0) + spellPower) * skillMult * elemAffinity - RES * 1.5f * mdefMult) * magRedEnch * _CalcElementRevision(target, actor)
    // 2. Hit Roll, Magic Crit 301 (0x12d) & Missed-Spell Grazing (0x44ed7f..0x44ee87)
    isMiss: bool = (GlobalRng.Rand(100) >= trunc0(hitRate))   // cvttss2si at 0x44ed91
    critMult: f32 = 1.0f
    if !isMiss and actor.HasPassive(0x12d) and GlobalRng.Rand(100) < 20: // 301 Magic Critical (20% proc -> 1.25x)
        critMult = 1.25f; res.isCrit = 1u8
    dmg: i32 = trunc0(rawMagicDmg * (1.0f + condBonuses) * critMult) // cvttss2si at 0x44ee28
    if isMiss:                                                // Missed spells graze instead of dealing 0!
        dmg = (actor.ench(0x110) > 0) ? ((dmg * 3) / 4) : (dmg / 2) // Enchant 272 -> 3/4, else 1/2
        res.resultType = 3                                    // Graze/Miss flag
    if dmg <= 0: dmg = GlobalRng.Rand(5) + 1                  // Min magic damage 1..5
    // 3. Applies row guard 356, incapacitated 1.5x, ailed target +15% (280), class 2x (86), _CalcSpecialDamage, cap 296.
    // 4. If res.isCrit and GlobalRng.Rand(100) < 33: res.isInterrupted = 1u8 (0x44f13a..0x44f146)

function CActionPatternBase_Task_PostCalc(this: CActionPatternBase*):
    // 1. Shifts floor elemental zones [battle+0x1e4..0x1f4] (clamped to [0.1f, 3.0f]) (0x421620..0x4218a0)
    // 2. Dispel on hit 441 (0x1b9, 0x421a45), Barrier 261 (0x105) absorption (0x421d0c), Magic/AoE Cover 171 (0x422b40)
    // 3. Calls _AfterHit1 (0x423560 at 0x422d32) and _AfterHit2 (0x423810 at 0x422eb3)
    // 4. Evaluates HP Drain (75 / 0x4b at 0x422eda) and TP Drain (76 / 0x4c at 0x422fc7)
    // 5. Calls CCommand::Execute (0x47e500) on target sequence (0x423233) and actor drain/recoil sequence (0x423244):
    //    - Applies HP damage/absorption (257 / ench 72,73), wakes Sleep 116 (0x74), cancels Chant/Song/Dance/Puppet/Geass on res.isInterrupted
    //    - Calls CBattle::TakeDamage (0x4e3f80) and applies queued statuses via AddStatus (0x4f9930)
```
- **Program Evidence:**
```asm
0044ed8c  call     0x490790
0044ed91  cvttss2si ecx, dword ptr [ebp + 0x54]
0044ed96  cmp      eax, ecx
0044ed98  setge    byte ptr [ebp + 0x47]
0044edbe  cmp      eax, 0x12d
0044eded  cmp      eax, 0x14
0044edf2  movss    xmm0, dword ptr [0x6d93a4]    ; float 1.25
0044ee28  cvttss2si esi, xmm0
0044ee36  push     0x110
0044ee47  lea      eax, [esi + esi*2]
0044ee51  sar      esi, 2
0044ee5d  sar      esi, 1
0044ee69  mov      dword ptr [eax + 0x2c], 3
00422d32  call     0x423560
00422eb3  call     0x423810
00423233  call     0x47e500
00423244  call     0x47e500
```

---

### M00.07 `AfterHit` Reactive Chain

- **Binary VA(s):** `0x423560..0x423803` (`CActionPatternBase::_AfterHit1`), `0x423810..0x423cbf` (`CActionPatternBase::_AfterHit2`), `0x423cd0..0x42478e` (`CActionPatternBase::_CheckEachInterrupt`), `0x4247e0..0x42588f` (`CActionPatternBase::_CheckAfterAttackInterrupt`), `0x425890..0x425928` (`CActionPatternBase::_UpdateInterrupt`), `0x425930..0x425bd7` (`CActionPatternBase::_SetupCounter`)
- **Owning Module(s):** `M08` (Reactive Passives: Devil's Whisper `320`, Endure `254`, Push Back `54`, Sugar Coma `262`, Dark Aura `293`, Physical Counter `249`, Parry/KnockDown `250`, Avenger `260`, Arcane Shield `447`, Counter Immunity `307`), `M10` (Boss Knockback Immunity Bit 12)
- **Calls:** `0x490790` (`CRandom::Get`), `0x47e500` (`CCommand::Execute`), `0x43e510` (`CBattleBase::_SortTime`), `0x425930` (`_SetupCounter`), `0x4f9930` (`AddStatus`), `M00.08`
- **CalledBy:** `M00.06` (`CActionPatternBase::_Task`), `CActionPatternBase::Update` (`0x41f750..0x41fe00`)
- **Typed Pseudocode:**
```text
function CActionPatternBase_AfterHit1(this: CActionPatternBase*, seq: Vec*, res: TaskResult*, target: CGameStatusBase*, actCmds: Vec*, tgtCmds: Vec*):
    // 0x423560..0x423803:
    // 1. Devil's Whisper (320 / 0x140): if attacker has cmd 320 and target.HasAnyAilment() (vtable+0x7c() != 0):
    //    creates command 119 (0x77) with cmd320.val, executes it via cmd->vtable+0x18, and if hit lands ([tmp+0x2c]==1),
    //    adds bonus damage [tmp+0x1c] directly to res.hpDamage ([res+0x1c])!
    // 2. Chains directly to this._AfterHit2(seq, res, target, tgtCmds) (0x4237e6 -> 0x423810).

function CActionPatternBase_AfterHit2(this: CActionPatternBase*, seq: Vec*, res: TaskResult*, target: CGameStatusBase*, cmds: Vec*):
    // 0x423810..0x423cbf:
    dmg: i32 = (res.hpDamage == 0x7fffffff) ? 0 : res.hpDamage
    // 1. Endure / Survive Lethal Hit (254 / 0xfe, 0x423888..0x423a18):
    if target.GetCurHP() - dmg <= 0:
        if cmd254 = FindCommand(cmds, 0xfe):
            if GlobalRng.Rand(100) < trunc0(cmd254.val * 100.0f):
                res.hpDamage = target.GetCurHP() - 1      // Clamps damage so target survives at 1 HP!
    // 2. Push Back / Slow Target ATB Swap (54 / 0x36, 0x423a18..0x423ca6):
    if target.GetCurHP() - dmg > 0 and dmg > 0 and this.battle != null:
        if cmd54 = FindCommand(cmds, 0x36):
            if target.IsEnemy() and ((target.enemyParam.flags54 >> 12) & 1) != 0:
                LogBlockResult(seq, target)               // Boss knockback immunity bit 12
            else if GlobalRng.Rand(100) < trunc0(cmd54.val * 100.0f):
                // Finds targetUnit in battle.units ([battle+0x24]); if not last unit, swaps
                // targetUnit.gauge ([u+0x08]) with nextUnit.gauge ([next+0x08]) and calls battle.vtable_SortTime(1, 0)!

function CActionPatternBase_CheckEachInterrupt(this: CActionPatternBase*) -> bool:
    // 0x423cd0..0x42478e: Called after EACH hit in the pattern.
    // Guard: returns false if actor is Doll (2000..2999) or Summon/Guest (3000..3999).
    slot = &this.action.targetSlots[this.action.curHitIdx]
    // 1. Sugar Coma (262 / 0x106, 0x423d50..0x424314):
    //    If this.hitLanded ([this+0x70]!=0), range==0 (close), actionType!=0, actor!=target,
    //    !actor.HasCommand(0x130) (304), !action.flag49, and target has cmd 262 (0x106):
    //    Applies 4-turn -10% stat debuffs to attacker based on cmd262.val thresholds:
    //    >=1.0f: cmd 45 (DEX), >=2.0f: cmd 44 (AGI), >=3.0f: cmd 43 (RES),
    //    >=4.0f: cmd 42 (DEF), >=5.0f: cmd 41 (ATK), >=6.0f: cmd 46 (SPD).
    // 2. Dark Aura (293 / 0x125, 0x424317..0x424679):
    //    If target has cmd 293 (0x125), !action.flag49, and GlobalRng.Rand(100) < trunc0(cmd293.val * 100.0f):
    //    Executes cmd 122 (0x7a, val=1.0f) and cmd 168 (0xa8, val=-0.75f) on attacker via CCommand::Execute (0x47e500).
    // 3. Per-Hit Counter & Arcane Shield Rolls (!this.inCounter [this+0x11]==0, 0x42467f..0x424771):
    //    - Physical Counter 249 (0xf9): if isPhysical ([this+0x79]!=0), hitLanded, range in {0,1},
    //      target.isFrontRow, actor!=target, !actor.HasCommand(0x133) (307), and target has cmd 249:
    //      slot.counterTriggered = (GlobalRng.Rand(100) < trunc0(cmd249.val * 100.0f)) // [slot+0x45]
    //    - Arcane Shield 447 (0x1bf): if !isPhysical ([this+0x78]==0), lastHpDmg not in {0, 0x7fffffff},
    //      actor!=target, !actor.HasCommand(0x133), and target has cmd 447:
    //      if GlobalRng.Rand(100) < 15: slot.magicReflectDmg = this.lastHpDmg // [slot+0x48] = [this+0x74]

function CActionPatternBase_CheckAfterAttackInterrupt(this: CActionPatternBase*) -> bool:
    // 0x4247e0..0x42588f: Called once all hits of the pattern finish.
    // Guard: requires attacker alive, attacker not Doll (2000..2999), and !this.inCounter ([this+0x11]==0).
    // 1. If attacker not Summon/Guest (3000..3999):
    //    - Cover Aggro Boost 171 (0xab, 0x4248ed..0x424b4b): for each alive covered slot ([slot+0x44]!=0) with cmd 171:
    //      if GlobalRng.Rand(100) < trunc0(cmd171.val * 100.0f): executes aggro boost on coverer via 0x47e500.
    //    - Parry / KnockDown Counter 250 (0xfa, 0x424b4b..0x424c42): for each alive slot with [slot+0x46]!=0 and cmd 250:
    //      calls _SetupCounter(slot.target, cmd250) (0x425930, sets inCounter = 1).
    //    - Physical Counter 249 (0xf9, 0x424d2c..0x4250d4): for each alive slot with [slot+0x45]!=0 and cmd 249:
    //      queues CActionAttack (0x414e20) or CActionEnemyAttack (0x419ad0) with inCounter = 1 into [this+0x7c].
    //    - Arcane Shield Reflection 447 (0x1bf, 0x4250d4..0x42537c): for each alive slot with [slot+0x48]!=0x7fffffff and cmd 447:
    //      scales skill 240 (0xf0) power by cmd447.val * f32([slot+0x48]) (0x56d860) and queues CActionSkill (0x41d480) with inCounter = 1.
    // 2. Avenger / Ally-Hit Counter 260 (0x104, 0x424c42..0x424d27 & 0x4253ae..0x425821):
    //    If actionType == 1 and primary target [Action_s+0x2c] survived: shuffles alive allies on target's side;
    //    first ally `a != target` with cmd 260 where GlobalRng.Rand(100) < trunc0(cmd260.val * 100.0f) queues basic attack counter (inCounter = 1).
```
- **Program Evidence:**
```asm
004235d5  mov      edx, 0x140
00423683  add      eax, esi
00423688  mov      dword ptr [ecx + 0x1c], eax
004237e6  call     0x423810
004238ad  mov      edx, 0xfe
004238fd  dec      eax
00423901  mov      dword ptr [edi + 0x1c], eax
00423a41  mov      edx, 0x36
00423b86  movss    xmm0, dword ptr [edi + 8]
00423b94  mov      dword ptr [edi + 8], edx
00423b97  movss    dword ptr [eax + 8], xmm0
00423b9e  call     dword ptr [eax + 0x24]
00423d9b  push     0x106
00424319  push     0x125
0042467f  cmp      byte ptr [ebx + 0x11], 0
00424683  jne      0x424771
004246d2  push     0xf9
00424749  push     0x1bf
00424766  cmp      eax, 0xf
004248aa  cmp      byte ptr [edi + 0x11], al
004248ad  jne      0x42547a
```

---

### M00.08 Post-Action Resolution, Status Add (`0x4f9930`), Death/Revive/Fall, Extra-Turn Rolls (`0x438cd2..0x4392ea`), Doll Life Tick & `_SetTime` (`0x43e5c0`, `0x439884`)

- **Binary VA(s):** `0x4f9930..0x4fa600` (`CGamePlayerStatusBase::AddStatus`), `0x438c81..0x4392ea` (Outer State 3 post-action resolution in `CBattleBase::Update`), `0x439884..0x4398a3` (passive `291` stat-buff jump table), `0x43e5c0..0x43e6c3` (`CBattleBase::_SetTime`), `0x4499d0..0x44a3cf` (`CBattle::_SetTime`)
- **Owning Module(s):** `M01` (Extra-Turn Loop & `_SetTime` ATB Recalculation), `M06` (Crowd-Control Application Side Effects in `AddStatus`), `M07` (`AddStatus` Deduplication, Opposition Purge & Song/Dance/Puppet/Geass Registration), `M08` (Post-Action Passives `291`, `288`, `289`, `354`), `M09` (Doll/Summon Action-Count Lifetime Tick)
- **Calls:** `0x43b6a0` (remove Summon/Guest), `0x43d2c0` (destroy Doll), `0x43b510` (count alive enemies), `0x505ac0` (`Rand`), `0x47b220` / `0x47e260` (create status command), `0x4f9930` (`AddStatus`), `0x43e5c0` (`CBattleBase::_SetTime`), `0x4499d0` (`CBattle::_SetTime`), `M00.02`, `M00.09`
- **CalledBy:** `M00.02` (Outer State 3 when `currentAction->Update()` returns `false`), `M00.06`, `M00.07`
- **Typed Pseudocode:**
```text
function CGamePlayerStatusBase_AddStatus(this: CGamePlayerStatusBase*, cmd: CCommand*):
    // 0x4f9930..0x4fa600 (vtable+0x54):
    if this.vtable_0xc8_IsDead(): return
    if cmd.GetCommandId() == 0x79:                         // 121 Stun / Chant Break
        // Cancels active Dance (0x43c110), Puppet (0x43c600), Geass (0x43c9b0), Chant (0x43ce30), Song (0x43bc50),
        // purges battle statuses (vtable+0x6c(0,1)), and converts cmd into status 120 (0x78) with priority/duration 3.
    // Deduplicates existing status with same CommandId in [this+0x8c..0x90] (for 0x78, only replaces if new priority >= 3).
    if cmd.IsAilment() (vtable+0x7c): this.PurgeIncompatibleOnAilment()   // vtable+0xa8 (0x4f9c30)
    if cmd.IsStatMod() (vtable+0x84): this.PurgeIncompatibleOnStatMod()   // vtable+0xac (0x4f9cb0)
    // Registers Song (0x43bdd0), Dance (0x43c2a0), Puppet (0x43c790), or Geass (0x43cb80) if applicable.
    // Appends cmd to [this+0x8c..0x90], sorts active statuses (0x4fc9b0), and applies CC side-effects (114/116/117/118).

function CBattleBase_PostActionResolution(this: CBattleBase*):
    // 0x438c81..0x4392ea (inside Outer State 3 after currentAction completes):
    actor = this.units[0]                                  // [this+0x24][0]
    actor.totalActionCount++                               // [actor+0xb8]++ at 0x438cd2
    if actor.unitId in 3000..3999 and actor.totalActionCount >= actor.maxActions:
        this.RemoveUnit(actor.status)                      // 0x43b6a0 (Summon/Guest lifetime expired)
    else if actor.unitId in 2000..2999 and actor.totalActionCount >= actor.dollMaxActions:
        this.DestroyDoll(actor)                            // 0x43d2c0 (Doll lifetime expired)
    if this.GetAliveEnemyCount() == 0:                     // 0x43b510 at 0x438df0
        this.PhaseNo = 5; return                           // Transition to Victory (M00.09)

    // 1. Passive 291 (0x123, Post-Action Random Stat Buff, 0x438e53..0x43903b):
    if cmd291 = actor.status.GetCommand(0, 0x123):
        if cmd291.val >= 1.0f:
            for statIdx in 6..13:                          // Jump table 0x439884 -> commands 0x1a0..0x1a7 (416..423)
                val: f32 = f32((Rand(2) + 1) * 50)         // 50.0f or 100.0f
                actor.status.vtable_0x54_AddStatus(CreateStatCommand(cmdId, val))

    // 2. Extra-Turn Passive Rolls (0x43903b..0x439272):
    //    Requires !actor.grantedExtraTurn ([actor+0x107]==0), actor is still head of [this+0x24],
    //    and !actor.status.vtable_0xbc_IsIncapacitated():
    extraTurns: i32 = 0
    if (cmd288 = actor.status.GetCommand(0, 0x120)) and Rand(100) < trunc0(cmd288.val * 100.0f):
        extraTurns = 2                                     // Passive 288 -> 1 extra action (2 actions total)
    else if (cmd289 = actor.status.GetCommand(0, 0x121)) and Rand(100) < trunc0(cmd289.val * 100.0f):
        extraTurns = 3                                     // Passive 289 -> 2 extra actions (3 actions total)
    else if (cmd354 = actor.status.GetCommand(0, 0x162)) and Rand(100) < trunc0(cmd354.val * 100.0f):
        extraTurns = 2                                     // Passive 354 -> 1 extra action
    if extraTurns > 0:
        actor.grantedExtraTurn = 1u8                       // [actor+0x107] = 1
        actor.extraTurnCount = extraTurns                  // [actor+0xb0/+0xb4] (skips _SetTime!)
    else:
        this._SetTime(actor_or_null)                       // 0x43e5c0 -> decrements [actor+0xb0] or calls CBattle::_SetTime (0x4499d0) & _SortTime (0x43e510)
        this.TurnPhaseNo = 0                               // [this+0x20] = 0

    // 3. Cleanup & Loop Back to Outer State 0 (0x43928b..0x4392ea):
    for u in this.units:
        if u.status.vtable_0x38_IsDeadOrGone(): u.actionType = 7 // [u+0x1c] = 7
        u.isDefending = 0u8                                // [u+0x104] = 0
    this.PhaseNo = 0
```
- **Program Evidence:**
```asm
004f9950  mov      eax, dword ptr [eax + 0xc8]
004f9956  call     eax
004f9958  test     al, al
004f995a  jne      0x4fa5f9
004f99b7  cmp      dword ptr [ebp - 0x20], 0x79
00438ea4  jmp      dword ptr [eax*4 + 0x439884]
0043903b  cmp      byte ptr [esi + 0x107], 0
00439042  jne      0x439272
00439072  push     0x120
004390b9  push     0x121
004390f9  mov      eax, 3
00439103  push     0x162
0043914b  mov      eax, 2
00439153  mov      byte ptr [esi + 0x107], 1
0043915a  mov      dword ptr [esi + 0xb4], eax
0043927f  call     0x43e5c0
00439284  mov      dword ptr [edi + 0x20], 0
004392e3  mov      dword ptr [edi + 0x18], 0
```

---

### M00.09 Battle End, After-Battle Recovery (`0x43d6a7`) & Rewards (EXP/Gold/Drops) Hand-off

- **Binary VA(s):** `0x450710..0x450828` (`CBattle::_AddExp`), `0x439331..0x439455` (Outer States 5 & 6 in `CBattleBase::Update`), `0x443c30..0x443de2` (`CBattleResult::CBattleResult`), `0x445830..0x446800` (`CBattleResult::_Initialize`), `0x43d650..0x43da55` (`CBattleBase::End`)
- **Owning Module(s):** `M01` (Battle End Lifecycle), `M11` (EXP Level-Difference Scaling, Alive-Party Split, EXP Multipliers, Gold/Drops, Post-Battle HP/TP Recovery)
- **Calls:** `0x61e650` (`round_f32_to_i32`), `0x443c30` (`CBattleResult::CBattleResult`), `0x445830` (`CBattleResult::_Initialize`), `0x43fe50` (clear Dolls on victory), `0x47e500` (`CCommand::Execute`)
- **CalledBy:** `M00.02` (Outer States 0, 3, 5, 6), `M00.08`, Battle scene teardown (`0x43d650`)
- **Typed Pseudocode:**
```text
function CBattle_AddExp(this: CBattle*, playerUnit: BattleUnit_s*, enemyUnit: BattleUnit_s*, baseExp: f32):
    // 0x450710..0x450828: Called when a player unit damages/kills an enemy unit.
    diff: i32 = playerUnit.playerStatus.GetLevel() - enemyUnit.enemyStatus.GetLevel()
    hasEnch270: bool = (playerUnit.playerStatus.GetEnchantCount(0x10e) > 0) // Enchant 270 (Underdog EXP Up)
    if diff in 5..9:         mult = 0.90f
    else if diff >= 10:      mult = 0.85f
    else if diff in -4..-1:  mult = hasEnch270 ? 1.15f : 1.00f
    else if diff in -9..-5:  mult = hasEnch270 ? 1.30f : 1.10f
    else if diff in -19..-10:mult = hasEnch270 ? 1.50f : 1.25f
    else if diff <= -20:     mult = hasEnch270 ? 1.75f : 1.25f
    else:                    mult = 1.00f                  // diff in 0..4
    playerUnit.accumExp += round_f32_to_i32(baseExp * mult) // [playerUnit+0xec] += 0x61e650(baseExp * mult)

function CBattleResult_Initialize(this: CBattleResult*, bonusExpRate_cmd218: f32):
    // 0x445830..0x446800 (invoked from Outer State 5 at 0x4393e0 after checking party cmd 218 / 0xda):
    aliveCount: f32 = f32(this.battle.GetAlivePlayerCount()) // 0x43afc0
    for member in this.battle.GetAllPlayerMembers():
        unit = this.battle.GetUnit(member)
        exp: f32 = (f32(unit.accumExp) / aliveCount) * (1.0f + bonusExpRate_cmd218) // 0x4459bf..0x4459cc
        if member.HasStatus(0x9d): exp += exp              // Status 157 (EXP Up buff) doubles EXP (0x4459ed)
        if member.GetEnchantCount(0x113) > 0: exp += exp   // Enchant 275 (EXP x2) doubles EXP (0x445a1e)
        // Queues final EXP for member level-up tick in CBattleResult::Update (0x444340)
    // Awards battle Gold to party ([0x71fc24]->vtable+0x48(gold) at 0x446488),
    // transfers dropped & stolen items ([battle+0x4c]) into inventory, and increments Guest battle counter.

function CBattleBase_End(this: CBattleBase*):
    // 0x43d650..0x43da55: Post-battle party HP/TP recovery:
    hpRate272: f32 = 0.0f; hpRate353: f32 = 0.0f
    tpRate273: f32 = 0.0f; tpRate353: f32 = 0.0f
    for i in 0 .. GameManager.GetPartyCount() - 1:         // 0x43d6a7..0x43d74b
        m = GameManager.GetPartyMember(i)
        if m.vtable_0xe8_IsAlive():
            if cmd272 = m.GetCommand(0, 0x110):            // Passive 272 (Party After-Battle HP%)
                hpRate272 += cmd272.val
                hpRate353 += cmd272.GetSubBonus(0x161)     // Passive 353 synergy bonus (0x48bf90)
            if cmd273 = m.GetCommand(0, 0x111):            // Passive 273 (Party After-Battle TP%)
                tpRate273 += cmd273.val
                tpRate353 += cmd273.GetSubBonus(0x161)
    totalHpRate: f32 = min(0.30f, hpRate272) + hpRate353   // Capped at 30% (0.3f at 0x43d751) + 353 bonus
    totalTpRate: f32 = min(0.30f, tpRate273) + tpRate353   // Capped at 30% (0.3f at 0x43d769) + 353 bonus

    for i in 0 .. GameManager.GetPartyCount() - 1:         // 0x43d7a0..0x43da3f
        m = GameManager.GetPartyMember(i)
        if m.vtable_0xe8_IsAlive():
            myHpRate: f32 = (m.GetEnchantCount(0xc1) > 0) ? 1.0f : totalHpRate // Enchant 193 -> 100% HP
            if myHpRate > 0.0f:
                hpHeal: i32 = max(1, trunc0(f32(m.GetMaxHP()) * myHpRate))
                QueueHealResult(seq, m, hpHeal, isTp=false)
            myTpRate: f32 = (m.GetEnchantCount(0xc2) > 0) ? 1.0f : totalTpRate // Enchant 194 -> 100% TP
            if myTpRate > 0.0f:
                tpHeal: i32 = max(1, trunc0(f32(m.GetMaxTP()) * myTpRate))
                QueueHealResult(seq, m, tpHeal, isTp=true)
            if !seq.empty():
                CCommand_Execute(seq, -1, this)            // 0x47e500 at 0x43d99d
```
- **Program Evidence:**
```asm
00450736  lea      eax, [esi - 5]
00450739  cmp      eax, 4
0045073e  movss    xmm0, dword ptr [0x6d937c]    ; float 0.9
00450750  movss    xmm0, dword ptr [0x6d9374]    ; float 0.85
00450768  push     0x10e
00450815  mulss    xmm0, dword ptr [esp + 0x14]
0045081b  call     0x61e650
00450820  add      dword ptr [edi + 0xec], eax
00445997  push     0x9d
004459bf  divss    xmm0, dword ptr [ebp - 0x18]
004459c7  mulss    xmm1, dword ptr [ebp - 0x2c]
004459cc  addss    xmm1, xmm0
004459ed  addss    xmm0, xmm1
00445a06  push     0x113
00445a1e  addss    xmm1, xmm1
0043d6cc  push     0x110
0043d705  push     0x111
0043d751  movss    xmm0, dword ptr [0x6d9330]    ; float 0.3
0043d764  minss    xmm1, dword ptr [ebp - 0x10]
0043d769  minss    xmm0, dword ptr [ebp - 0x18]
0043d85e  push     0xc1
0043d904  push     0xc2
0043d99d  call     0x47e500
```

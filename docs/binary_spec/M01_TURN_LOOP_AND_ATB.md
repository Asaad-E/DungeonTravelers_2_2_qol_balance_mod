# Module M01 â€” Turn Loop, ATB Gauge, Action/Chant Speed, and Interruption

**Clean-Room Binary Specification (`backups/exe/DT22_en_unwrapped.vanilla.exe`)**

---

## Core Battle Unit & State Layout

### `CBattle` (`sizeof = 0x1fc`, inherits `CBattleBase`)

| Offset | Type | Field | Description |
|---|---|---|---|
| `+0x00` | `vtable*` | `vptr` | `CBattleBase` (`0x651204`) / `CBattle` (`0x652ad4`); `+0x20` = `_SetTime`, `+0x24` = `_SortTime`, `+0x48` = `FindCommandOnSide` |
| `+0x10` | `CBattleInfo*` | `battleInfo` | Shared battle context; `[battleInfo+0x40]` points back to `CBattleBase*` |
| `+0x18` | `u32` | `PhaseNo` | Outer state machine index (`0..15`, jump table `0x4397e0`) |
| `+0x1c` | `u32` | `PrevPhaseNo` | Saved `PhaseNo` while in Formation/Escape sub-menu (`PhaseNo = 9`) |
| `+0x20` | `u32` | `TurnPhaseNo` | Inner turn-start state machine index (`0..24`, jump table `0x439820`) |
| `+0x24..0x2c` | `vector<Unit*>` | `units` | Turn-order vector (`[units+0]` is the current head actor) |
| `+0x30` | `u8` | `isPlayerPreempt` | Set to `1` when player preemptive strike succeeds (`0x4491fd`) |
| `+0x32` | `u8` | `allowNormalPreempt` | Encounter flag; if `0`, preemptive/ambush requires `rate >= 100` (`321`) |
| `+0x33` | `u8` | `noTurnJitterFlag` | Fixed-order encounter flag; disables Summon init randomizer and 20% order scramble |
| `+0x34` | `i32` | `dollSortCounter` | Initialized to `962` (`0x3c2`), decrements per Doll spawn (wraps `0 -> 962`) |
| `+0x40` | `CGameStatus*` | `activeStatus` | `units[0]->status` set at turn start (`0x436311`) |
| `+0x44` | `CAction*` | `currentAction` | Active `CAction` instance during `PhaseNo = 3` and `PhaseNo = 12` |
| `+0x48` | `CActionPattern*` | `currentPattern` | Direct turn-start `CActionPattern` instance during `PhaseNo = 11` |
| `+0x60` | `u8` | `escapedFlag` | Set to `1` when party escape succeeds (`0x438c2d -> PhaseNo = 10`) |
| `+0x61` | `u8` | `defeatedOrGaveUp` | Set to `1` on Defeat or Give Up |
| `+0x1a0` | `Unit*` | `warningShotUnit` | Opposing unit triggering Warning Shot (`259`) in `TurnPhaseNo = 9` |
| `+0x1a4` | `Unit*` | `thirdEyeUnit` | Opposing unit triggering Third Eye Wide (`345`) in `TurnPhaseNo = 2` |
| `+0x1bc` | `CJitterRng*` | `jitterRng` | Dedicated battle LCG seeded from `GlobalRng` (`0x816ce8`) in `CBattleBase::_Initialize` |

### `CBattleBase::Unit_s` (`sizeof = 0x114`)

| Offset | Type | Field | Description |
|---|---|---|---|
| `+0x00` | `u32` | `slotIdx` | Party or enemy formation slot index |
| `+0x04` | `u32` | `unitId` | `0..999` Party, `1000..1999` (`0x3e8..0x7cf`) Enemy, `2000..2999` (`0x7d0..0xbb7`) Doll, `3000` (`0xbb8`) Summon, `3001` (`0xbb9`) Guest, `>=4000` (`0xfa0`) Sentinel |
| `+0x08` | `f32` | `gauge` | Current ATB gauge (`0.0f..1.0f+`; capped at `0.92f` on `_SetTime`) |
| `+0x0c` | `i32` | `sortTiebreak` | Tie-breaker in `_SortTime`: Party `999 - slotIdx`, Doll `962..1`, Summon `930`, Guest `929`, Enemy `999 - enemyOrder` |
| `+0x10` | `CGameStatus*` | `status` | Base status pointer |
| `+0x14` | `CGameEnemyStatus*` | `enemyStatus` | Enemy status pointer (`null` for players) |
| `+0x18` | `CGamePlayerStatus*` | `playerStatus` | Player status pointer (`null` for enemies) |
| `+0x1c` | `u32` | `actionType` | `Action_s.actionType`: `0` Attack, `1` Skill/Pattern, `2` Player Cast Ready, `3` Player Chanting, `4` Item, `5` Defend, `6` Escape, `7` None/Done, `8` Enemy Attack/Cast Ready, `9` Enemy/Summon Chanting |
| `+0x20` | `u32` | `skillId` | Player skill ID (`Action_s + 0x04`) |
| `+0x28` | `u32` | `enemyAttackId` | Enemy/Summon attack ID (`Action_s + 0x0c`) |
| `+0x78` | `u8` | `isPlayerSide` | `1` for Player/Summon/Guest/Player-Doll, `0` for Enemy/Enemy-Doll |
| `+0x79` | `u8` | `isFrontRow` | `1` front row, `0` back row |
| `+0xb0` | `u32` | `extraTurnCount` | Actions completed in the current turn (`0` on turn entry) |
| `+0xb4` | `u32` | `maxTurnActions` | Target actions for current turn (`1` normal, `2` Double/`354`, `3` Triple) |
| `+0xb8` | `u32` | `totalActionCount` | Cumulative actions taken by this unit in battle (used for Doll lifetime) |
| `+0xbc..0xc4` | `vector<u32>` | `songs` | Active Song command IDs maintained by this unit |
| `+0xc8..0xd0` | `vector<u32>` | `dances` | Active Dance command IDs maintained by this unit |
| `+0xd4..0xdc` | `vector<u32>` | `puppets` | Active Puppet command IDs maintained by this unit |
| `+0xe0..0xe8` | `vector<u32>` | `geass` | Active Geass command IDs maintained by this unit |
| `+0x104` | `u8` | `isDefending` | Cleared to `0` at end of every `PhaseNo = 3` action |
| `+0x105` | `u8` | `isWarningShot` | Set to `1` during Warning Shot (`259`); scales physical damage by `3 / 10` (`0x44caea`) |
| `+0x107` | `u8` | `grantedExtraTurn` | Set to `1` when `288`/`289`/`354` procs so extra turns cannot chain within the same turn |

---

### M01.01 Battle Start Gauges, Random Order Jitter, Preemptive/Ambush (`321`/`268`/`267`), First Grid (`300`), and `_SortTime`

**Binary VA(s):** `0x448c60..0x448ed5`, `0x43da60..0x43dee2`, `0x449130..0x4494d5`, `0x449750..0x4499c2`, `0x43a150..0x43a315`, `0x44a3d0..0x44a629`, `0x43e510..0x43e5b2`, `0x440a80..0x440c80`
**Calls:** `0x490790` (`CRandom::Get(max)` on `GlobalRng` `0x816ce8`), `0x61e650` (`round_f32_to_i32`), `0x4499d0` (`CBattle::_SetTime`), `0x44a3d0` (`CBattle::_SetFirstAttack`), `0x43e510` (`CBattleBase::_SortTime`), `0x440a80` (`std::_Sort_time`), `0x43e6d0` (`CBattleBase::CollectUnits`), `0x4f98e0` (`CGameStatus::IsDead`, `vtable+0x38`)
**CalledBy:** `0x449035` (`CBattle::Setup`), `0x43e641`, `0x43e691` (`CBattleBase::_SetTime`), `0x4362ef`, `0x4386af`, `0x438e39` (`CBattleBase::Update`)

**Typed Pseudocode:**
```python
def CBattle_Initialize(this: CBattle) -> bool:
    # 1. Base init (0x43da60): party tiebreak = 999 - slotIdx; Summon(3000)=930, Guest(3001)=929.
    #    Doll counter [this+0x34] starts at 962 (0x3c2). Seeds jitterRng ([this+0x1bc]) with two
    #    GlobalRng.Rand(0x7fffffff) draws into [rng+0x1c] and [rng+0x20] (0x43dd71..0x43ddb6).
    CBattleBase_Initialize(this)

    # 2. Initial ATB gauge assignment (0x449154..0x4491cd)
    for u in this.units:
        if 3000 <= u.unitId <= 3999 and this.noTurnJitterFlag == 0:
            # Summon/Guest special initial gauge: (Rand(500) + 1) / 1000.0f in [0.001f, 0.500f]
            u.gauge = f32(GlobalRng.Rand(500) + 1) / 1000.0
        else:
            this._SetTime(u, isChanting=0)

    # 3. Preemptive Strike (base 6%, playerSide=1) then Enemy Ambush (base 4%, playerSide=0)
    firstAttackMode: i32 = CBattle_SetFirstAttack(this, baseRate=6, isPlayerSide=1)
    if firstAttackMode == 0:
        firstAttackMode = CBattle_SetFirstAttack(this, baseRate=4, isPlayerSide=0)

    if firstAttackMode == 1:
        this.isPlayerPreempt = 1  # [this+0x30] = 1
    elif firstAttackMode == 0:
        # 4. 20% Battle-Start Random Order Scramble (0x449316..0x449373)
        if this.noTurnJitterFlag == 0 and GlobalRng.Rand(100) < 20:
            for u in this.units:
                u.gauge = f32(GlobalRng.Rand(93)) / 100.0  # 0.00f .. 0.92f

        # 5. Passive 300 (0x12c, First Grid) check (0x449375..0x44949e)
        #    Evaluates alive player units first, then alive enemy units; stops at first proc.
        candidates: list[Unit] = (
            this.CollectUnits(aliveOnly=1, includeDolls=0, playerSide=1, excludePetrified=1)
            + this.CollectUnits(aliveOnly=1, includeDolls=0, playerSide=0, excludePetrified=0)
        )
        for u in candidates:
            cmd300: CCommand | None = u.status.FindCommand(0, 0x12C)  # 300 First Grid
            if cmd300 is not None:
                if GlobalRng.Rand(100) < trunc0(cmd300.GetValue() * 100.0):
                    u.gauge = 1.0  # 0x3f800000
                    break

    # 6. Initial sort & normalization to head gauge = 1.0f (0x4494ba..0x4494c2)
    this._SortTime(normalize=1, updateUi=1)
    return True


def CBattle_SetFirstAttack(this: CBattle, baseRate: i32, isPlayerSide: u8) -> i32:
    # 0x44a3d0..0x44a629
    # Passive 321 (0x141, Absolute Preemptive Attack) forces rate = 1000
    cmd321: CCommand | None = this.FindCommandOnSide(outUnit=None, cmdId=0x141, side=isPlayerSide)
    rate: i32 = 1000 if (cmd321 is not None) else baseRate

    if this.allowNormalPreempt == 0 and rate < 100:
        return 0

    # Passive 268 (0x10c, Preemptive Attack Chance) adds round(val * 100.0f)
    cmd268: CCommand | None = this.FindCommandOnSide(outUnit=None, cmdId=0x10C, side=isPlayerSide)
    if cmd268 is not None:
        rate += round_f32_to_i32(cmd268.GetValue() * 100.0)

    if GlobalRng.Rand(100) >= rate:
        return 0

    oppSide: u8 = isPlayerSide ^ 1
    # If rate < 1000 (not guaranteed by 321), opposing passive 267 (0x10b, Preemptive Attack Evasion Chance) can block
    if rate < 1000:
        cmd267: CCommand | None = this.FindCommandOnSide(outUnit=None, cmdId=0x10B, side=oppSide)
        antiRate: i32 = round_f32_to_i32(cmd267.GetValue() * 100.0) if (cmd267 is not None) else 0
        # Always draws Rand(100) even when antiRate == 0 (0x44a4be)
        if GlobalRng.Rand(100) < antiRate:
            return 0

    for u in this.units:
        if u.isPlayerSide == isPlayerSide:
            u.gauge = 1.0  # 0x3f800000
    return i32(oppSide) + 1  # 1 = Player Preemptive, 2 = Enemy Ambush


def CBattleBase_SortTime(this: CBattleBase, normalize: u8, updateUi: u8) -> None:
    # 0x43e510..0x43e5b2 & comparator at 0x440b50..0x440ba4
    # Introsort descending by composite integer key:
    #   key(u) = round_f32_to_i32(u.gauge * 1000.0f) * 1000 + u.sortTiebreak
    this.units.sort_descending(
        key=lambda u: round_f32_to_i32(u.gauge * 1000.0) * 1000 + u.sortTiebreak
    )
    if updateUi != 0:
        this.ui.RefreshOrder()
    if normalize != 0 and len(this.units) > 0:
        # Note: normalization truncates head gauge*1000 toward zero (cvttss2si at 0x43e566)
        headGauge: f32 = f32(trunc0(this.units[0].gauge * 1000.0)) / 1000.0
        delta: f32 = 1.0 - headGauge
        for u in this.units:
            if not u.status.IsDead():  # CurHP > 0 (0x4f98e0)
                u.gauge += delta
```

> [!NOTE]
> When a Doll is spawned mid-battle via `CBattleBase::AddDoll` (`0x43a150`, capped at `< 12` active Dolls at `0x43a1a0`), its `sortTiebreak` is `[this+0x34]` (`962` down to `1`), its `unitId` is `sortTiebreak + 2000` (`0x7d0`), its initial gauge is `f32(GlobalRng.Rand(92)) / 100.0f` (`0x43a2a3..0x43a2bf`), and `_SortTime(0, 0)` is called immediately.

**Program Evidence:**
```text
00449194  mov      ecx, dword ptr [0x816ce8]
0044919a  push     0x1f4
0044919f  call     0x490790
004491a4  inc      eax
004491a5  movd     xmm0, eax
004491a9  mov      eax, dword ptr [ebx + 0x24]
004491ac  cvtdq2ps xmm0, xmm0
004491af  mov      eax, dword ptr [eax + esi*4]
004491b2  divss    xmm0, dword ptr [0x6d96b0]    ; float 1000
004491ba  movss    dword ptr [eax + 8], xmm0
0044a405  test     edi, edi
0044a407  mov      ecx, 0x3e8
0044a40c  cmovne   ebx, ecx
0044a40f  cmp      byte ptr [esi + 0x32], 0
0044a413  jne      0x44a41e
0044a415  cmp      ebx, 0x64
0044a418  jl       0x44a61e
00449316  cmp      byte ptr [ebx + 0x33], 0
0044931a  jne      0x449375
0044931c  mov      ecx, dword ptr [0x816ce8]
00449322  push     0x64
00449324  call     0x490790
00449329  cmp      eax, 0x14
0044932c  jge      0x449375
0043e551  movss    xmm1, dword ptr [0x6d938c]    ; float 1
0043e559  movss    xmm0, dword ptr [eax + 8]
0043e55e  mulss    xmm0, dword ptr [0x6d96b0]    ; float 1000
0043e566  cvttss2si eax, xmm0
00440b5c  movss    xmm0, dword ptr [eax + 8]
00440b61  mulss    xmm0, dword ptr [0x6d96b0]    ; float 1000
00440b69  call     0x61e650
00440b6e  movss    xmm0, dword ptr [esi + 8]
00440b73  mulss    xmm0, dword ptr [0x6d96b0]    ; float 1000
00440b7b  imul     ecx, eax, 0x3e8
00440b81  mov      eax, dword ptr [esp + 0x14]
00440b85  mov      eax, dword ptr [eax + 0xc]
00440b88  add      eax, ecx
```

---

### M01.02 Outer `CBattleBase::Update` (`0x4397e0`, States `0..15`), Win/Loss/Escape Checks, Doll/Summon/Guest Skip, and Summon/Guest Samba `199` Tick

**Binary VA(s):** `0x448ee0..0x448fc2`, `0x4360f0..0x436710`, `0x43875a..0x4397dc`, jump table `0x4397e0`
**Calls:** `0x43b510` (`GetAliveEnemyCount`), `0x43e5c0` (`CBattleBase::_SetTime`), `0x4359e0` (`IsDoll`), `0x435a00` (`IsSummonOrGuest`), `0x435a20` (`IsSentinel`), `0x47e500` (`CCommand::Execute`), `0x4fba20` (`CGameStatus::TickTimedStatuses`, `vtable+0xdc`), `0x43ea70` (`CBattleBase::_CreateAction`), `0x43d420` (`CBattleBase::SelectEnemyAction`), `0x43ff60` (`CheckPartyWipe`), `0x505ac0` (`Rand(max)`)
**CalledBy:** `0x448fb5` (`CBattle::Update`)

**Outer `PhaseNo` (`[this+0x18]`, Jump Table `0x4397e0`) Summary:**

| `PhaseNo` | Handler VA | Purpose & Transition |
|---|---|---|
| `0` | `0x43625b` | Turn-start gate: checks `GetAliveEnemyCount() == 0 -> PhaseNo = 5`; cycles dead/sentinel head units; runs Summon/Guest Samba `199` tick; skips inner 25-state machine if `extraTurnCount != 0` or Doll/Summon/Guest/Sentinel; otherwise dispatches inner `TurnPhaseNo` (`0..24`, `M01.03`). When ready to act, transitions to `PhaseNo = 1` (`0x438787`). |
| `1` | `0x43879f` | Action selection / Chant completion: Player with `actionType == 3` sets `actionType = 2`, calls `_CreateAction`, `PhaseNo = 3`; else opens player command menu (`0x4542c0`) and sets `PhaseNo = 2`. Doll (`0x4359e0`) selects skill via `vtable+0x190`, picks target (`0x43b070`/`0x43b0d0`), calls `_CreateAction`, `PhaseNo = 3`. Summon/Guest (`0x435a00`) or Enemy (`isPlayerSide == 0`) with `actionType == 9` sets `actionType = 8`; else runs AI (`0x430f00` / `0x43d420`), calls `_CreateAction`, `PhaseNo = 3`. |
| `2` | `0x438bb0` | Player command menu poll (`0x454930`); on confirm calls `_CreateAction(&units[0].action)` and sets `PhaseNo = 3`. |
| `3` | `0x438beb` | Active `CAction::Update` loop (`[this+0x44]->vtable+0x04()`). On completion: queries `consumeTurn = action->vtable+0x14()`, deletes `currentAction`, calls `CheckPartyWipe()` (`0x43ff60`, sets `PhaseNo = 7` if all party members dead/petrified). If `escapedFlag != 0` (`[this+0x60] != 0`), sets `PhaseNo = 10`; else runs post-action resolution (`M01.04`). |
| `4` | `0x4392ef` | Incapacitated / Skipped Turn Advance: sets `units[0].actionType = 7`, calls `_SetTime(0)` (`0x43e5c0`), resets `TurnPhaseNo = 0` and `PhaseNo = 0`. |
| `5` | `0x439331` | Victory init (`0x443c30`): applies party post-battle passive `218` (`0xda`, Paean), despawns Dolls (`0x43fe50`), sets `PhaseNo = 6`. |
| `6` | `0x439426` | Victory screen loop (`0x444340`); when finished sets `PhaseNo = 10` and returns `false`. |
| `7` | `0x43945a` | Defeat init (`0x48f930`): sets `PhaseNo = 8`. (Intercepted in `CBattle::Update` `0x448f31` when story retry flag `0xab` is active: strips Petrify `120`, heals party to `1 HP`, returns `false`). |
| `8` | `0x4394af` | Defeat screen loop (`0x48fa50`); when finished sets `defeatedOrGaveUp = 1` (`[this+0x61] = 1`) and returns `false`. |
| `9` | `0x4394dc` | Formation / Escape sub-menu (`[this+0x64]`): on give-up returns `false`; else restores `PhaseNo = PrevPhaseNo` (`[this+0x1c]`). |
| `10` | `0x439527` | Post-Victory / Escape transition wait (`0x43f070(1)`); returns `false` to exit battle. |
| `11` | `0x439541` | Turn-start direct `CActionPattern::Update` (`[this+0x48]`, used by `446`, `319`, `200`, `204`, `199/339`). On finish: deletes `currentPattern`, pops saved `Action_s` on `units[0]` (`0x435b50`), and sets `PhaseNo = 0` (resuming `TurnPhaseNo`). |
| `12` | `0x439584` | Turn-start direct `CAction::Update` (`[this+0x44]`, used by `259` Warning Shot). On finish: if `units[0]` was killed/disabled by the shot (`[slot+0xc]==0 && [slot+0xd]==0 && [slot+0x10] < 0`), sets `units[0].actionType = 7`, calls `_SetTime(0)`, and resets `TurnPhaseNo = 0`. Deletes `currentAction` and sets `PhaseNo = 0`. |
| `13` | `0x439613` | Third Eye Wide (`345`) random ailment/dispel execution (`0x439613..0x4396b5`): picks `idx = Rand(7)` (`0x505ac0(7)`) into table `0x6c9af8` = `[113, 115, 116, 114, 117, 118, 74]`, creates command with value `0.75f` (`0x6d9368`), applies it from `this.thirdEyeUnit->status` to `units[0]` via `vtable+0xe4`, and sets `PhaseNo = 14`. |
| `14` | `0x4396ba` | Turn-start popup/effect wait (`0x43f070(1)`); when ready sets `PhaseNo = 0` (resuming `TurnPhaseNo`). |
| `15` | `0x4396d0` | Petrified/Banished Enemy Removal (`0x4f22f0` -> `0x43b6a0(units[0].status)`): removes enemy unit, resets `TurnPhaseNo = 0` and `PhaseNo = 0`. |

**Typed Pseudocode:** *(Outer `PhaseNo == 0` gate, Summon/Guest Samba `199`, Doll/Summon/Guest skip)*
```python
def CBattleBase_Update_Phase0(this: CBattleBase) -> bool:
    if not this.IsUiReady():
        return True
    if this.GetAliveEnemyCount() == 0:
        this.PhaseNo = 5  # Victory (0x438793)
        return True

    # Advance past any dead head units (0x4362a2..0x4362cd)
    actor: Unit = this.units[0]
    while actor.status.IsDead():
        this._SetTime(None)
        actor = this.units[0]

    # Advance past any sentinel units (unitId >= 4000 / 0xfa0, 0x4362cf..0x4362fe)
    while actor.unitId >= 4000:
        actor.gauge = 0.0
        this._SortTime(normalize=1, updateUi=0)
        actor = this.units[0]

    this.ui.RefreshOrder()
    this.activeStatus = actor.status

    # Extra-turn re-entry skip #1 (0x436314)
    if actor.extraTurnCount != 0:
        return CBattleBase_EnterActionPhase(this, actor)

    # Summon / Guest (unitId in 3000..3999) dedicated Samba 199 tick (0x436322..0x4365fb)
    if 3000 <= actor.unitId < 4000:
        enemies: list[Unit] = this.CollectUnits(aliveOnly=1, includeDolls=0, playerSide=0, excludePetrified=0)
        if this.TurnPhaseNo == 0:
            this.TurnPhaseNo = 1
            if 199 in actor.dances and len(enemies) > 0:
                cmd199: CCommand | None = enemies[0].status.FindCommand(0, 199)
                if cmd199 is not None:
                    seq = CCommandResultList()
                    for e in enemies:
                        dmg: i32 = trunc0(f32(e.status.GetMaxHP()) * cmd199.GetValue())
                        seq.AddHpDamage(target=e.status, hpDamage=dmg)
                    CCommand_Execute(seq, mode=6, battleInfo=this.battleInfo)
        elif this.TurnPhaseNo == 1:
            this.TurnPhaseNo = 2
        if this.TurnPhaseNo < 2 or this.PhaseNo != 0:
            return True

    # Extra-turn re-entry skip #2 (0x4365ff)
    if actor.extraTurnCount != 0:
        return CBattleBase_EnterActionPhase(this, actor)

    # Doll (2000..2999), Summon/Guest (3000..3999), and Sentinel (>=4000) skip inner states 0..24 (0x43660d..0x43664d)
    if (2000 <= actor.unitId < 3000) or (3000 <= actor.unitId < 4000) or (actor.unitId >= 4000):
        return CBattleBase_EnterActionPhase(this, actor)

    # Otherwise execute one step of the 25-state TurnPhaseNo machine (M01.03)
    return CBattleBase_RunInnerTurnPhase(this, actor)


def CBattleBase_EnterActionPhase(this: CBattleBase, actor: Unit) -> bool:
    # 0x43875a..0x43878e: Summon/Guest still ticks timed status durations via vtable+0xdc!
    if 3000 <= actor.unitId < 4000:
        actor.status.TickTimedStatuses(this.battleInfo)  # vtable+0xdc (0x4fba20)
    if this.GetAliveEnemyCount() != 0:
        this.PhaseNo = 1
    else:
        this.PhaseNo = 5
    return True
```

**Program Evidence:**
```text
004362a2  mov      ecx, dword ptr [esi + 0x10]
004362a5  mov      eax, dword ptr [ecx]
004362a7  mov      eax, dword ptr [eax + 0x38]
004362aa  call     eax
004362ac  test     al, al
004362ae  je       0x4362cf
004362b0  push     0
004362b2  mov      ecx, edi
004362b4  call     0x43e5c0
00436314  mov      eax, dword ptr [esi + 0xb0]
0043631a  test     eax, eax
0043631c  jne      0x43875a
004365ff  mov      eax, dword ptr [esi + 0xb0]
00436605  test     eax, eax
00436607  jne      0x43875a
0043660d  mov      eax, dword ptr [esi + 4]
00436610  cmp      eax, 0x7d0
00436615  jb       0x436622
00436617  cmp      eax, 0xbb8
0043661c  jae      0x436622
0043661e  mov      cl, 1
00436620  jmp      0x436624
00436622  xor      cl, cl
00436624  test     cl, cl
00436626  jne      0x43875a
0043662c  cmp      eax, 0xbb8
00436631  jb       0x43663e
00436633  cmp      eax, 0xfa0
00436638  jae      0x43663e
0043663a  mov      cl, 1
0043663c  jmp      0x436640
0043663e  xor      cl, cl
00436640  test     cl, cl
00436642  jne      0x43875a
00436648  cmp      eax, 0xfa0
0043664d  jae      0x43875a
```

---

### M01.03 Inner Turn-Start 25-State Machine (`0x439820`, States `0..24`)

**Binary VA(s):** `0x436653..0x438759`, jump table `0x439820`, `0x4fb8e0` (`vtable+0xd8`), `0x4fba20` (`vtable+0xdc`), `0x48d180` (`CCommand::CheckNaturalRecovery`), `0x48d590` (`CCommand::TickDuration`), `0x483010` (`CCommand_0120::TickStage`), `0x482150` (`CCommand_0113::TickDamage`), `0x4894a0` (`215` Carol), `0x4895e0` (`216` Chorale), `0x48a640` (`246` HP Regen), `0x48a710` (`247` TP Regen)
**Calls:** `0x47e500` (`CCommand::Execute`), `0x505ac0` (`Rand(max)`), `0x490790` (`CRandom::Get`), `0x61e650` (`round_f32_to_i32`), `0x435a30` (`Unit::PushAction`), `0x43a150` (`CBattleBase::AddDoll`), `0x43b6a0` (`CBattleBase::RemoveUnit`), `0x43e510` (`CBattleBase::_SortTime`)
**CalledBy:** `0x43670c` (`CBattleBase::Update` when `PhaseNo == 0`)

**Target Pools Constructed Before State Dispatch (`0x436653..0x436700`):**
- If `actor.isPlayerSide == 0` (Enemy turn):
  - `oppUnits` (`[ebp-0x40]`): alive, non-Doll, non-petrified Player party units (`0x43e6d0(1, 0, 1, 1)`).
  - `oppPlusSummons` (`[ebp-0x50]`): alive Summon/Guest units (`0x43b3a0`) concatenated with `oppUnits`.
- If `actor.isPlayerSide != 0` (Player turn):
  - `oppUnits` (`[ebp-0x40]`): alive, non-Doll Enemy units (`0x43e6d0(1, 0, 0, 0)`).
  - `oppPlusSummons` (`[ebp-0x50]`): copy of `oppUnits`.

**Complete 25-State Table (`TurnPhaseNo` `[this+0x20]` in `0..24`, Jump Table `0x439820`):**

| State | VA | Mechanic & Exact Branch / Skip Rules |
|---|---|---|
| `0` | `0x436713` | **Reset Turn Flags & Esarhaddon (`311` / `0x137`):** Sets `actor.isWarningShot = 0` (`[actor+0x105] = 0`), `actor.grantedExtraTurn = 0` (`[actor+0x107] = 0`), `TurnPhaseNo++`. If `actor` has passive `311`, computes `n = round_f32_to_i32(cmd311.val)` and checks the first `n` entries of `0x6c9a7c` = `[113 (Poison), 115 (Paralysis), 117 (Silence), 114 (Freeze), 116 (Sleep), 122 (Slow)]`. Removes any matching active status via `CCommand::Execute` (`resultType = 2`) and sets `PhaseNo = 14`. |
| `1` | `0x43692f` | **Natural Ailment Recovery (`vtable+0xd8` = `0x4fb8e0`):** `TurnPhaseNo++`. Calls `cmd->vtable+0x10` (`0x481e80 -> 0x48d180`) on active ailments (`113, 114, 115, 116, 117, 122`). In `0x48d180`: if `actor.IsAsleep()` (`vtable+0xbc`) and `cmd->IsSleepDecaying()` (`vtable+0x8c`, `[CommandData+0x50] & 2`), removes immediately; else rolls `GlobalRng.Rand(100) < cmd.recoveryChance` (`[cmd+0x28]`, starts at `0`). On failure, `cmd.recoveryChance += 10` (`0x48d225`). If any status recovered, executes removal and sets `PhaseNo = 14`. |
| `2` | `0x436955` | **Opposing Third Eye Wide (`345` / `0x159`):** `TurnPhaseNo++`. Iterates `u` in `oppUnits`. If `u` has passive `345`, `u.isPlayerSide != actor.isPlayerSide`, and `Rand(100) < trunc0(cmd345.val * 100.0f)`: sets `this.thirdEyeUnit = u` (`[this+0x1a4]`), `PhaseNo = 13` (which picks `Rand(7)` from `0x6c9af8` = `[113, 115, 116, 114, 117, 118, 74]` at value `0.75f`), and breaks. |
| `3` | `0x436a9b` | **Overstock Clearance (`446` / `0x1be`):** `TurnPhaseNo++`. If `actor` has passive `446` and `Rand(100) < trunc0(cmd446.val * 100.0f)`: pushes `actor.action` (`0x435a30`), sets `actor.actionType = 1`, `actor.skillId = cmd446.skillId`, allocates `CActionPatternU0008` (`0x42f870`) into `this.currentPattern`, and sets `PhaseNo = 11`. |
| `4` | `0x436be4` | **Gradual Petrification (`120` / `0x78`) Stage Advance:** `TurnPhaseNo++`. If `actor` has status `120`, calls `CCommand_0120::TickStage` (`0x483010`) and `CCommand::Execute`. Increments `stage = ++[cmd120+0x28]`. When `stage == 3`: if blocked by status barrier (`0x41f920`: `101/102/181`), queues removal of `120`; otherwise cancels Chant/Song/Dance/Puppet/Geass and clears all other statuses (`vtable+0x6c(0, 1)`). |
| `5` | `0x436c3f` | **Stage-3 Petrification Gate (`vtable+0xc8` = `0x4fb600`):** `TurnPhaseNo++`. If `actor.IsPetrifiedStage3()` (`120` with `stage >= 3`): if `actor.isPlayerSide != 0`, logs msg `0x42` and sets `PhaseNo = 4` (hard turn loss); if `actor.isPlayerSide == 0` (Enemy), defeats enemy (`0x43a4a0(enemyStatus, 0, -1)`) and sets `PhaseNo = 15` (removes enemy). |
| `6` | `0x436ca1` | **Sleep (`116` / `0x74`) Hard Turn Loss Gate (`vtable+0xbc` = `0x4fb5a0`):** `TurnPhaseNo++`. If `actor.IsAsleep()` (has status `116`), logs msg `0x43` and sets `PhaseNo = 4` (`100%` turn loss). |
| `7` | `0x436d08` | **Paralysis (`115` / `0x73`) Soft Turn Loss Gate (`vtable+0xb8` = `0x4fb590`):** `TurnPhaseNo++`. If `actor.IsParalyzed()` (has status `115`) and `Rand(100) < 30` (`0x1e`), logs msg `0x44` and sets `PhaseNo = 4` (`30%` turn loss). |
| `8` | `0x436d4c` | **Timed Status Countdown (`vtable+0xdc` = `0x4fba20`):** `TurnPhaseNo++`. Calls `cmd->vtable+0x14` (`0x48d590`) on every active status on `actor`: if `actor.IsAsleep()` and `cmd->IsSleepDecaying()`, expires immediately; else if `turns = [cmd+0x28] > 0` (`0` = permanent), decrements `turns--` and removes when `turns == 0`. Note: reached only if States `5..7` did not branch to `PhaseNo = 4/15`. |
| `9` | `0x436d60` | **Opposing Warning Shot (`259` / `0x103`):** `TurnPhaseNo++`. Iterates `u` in `oppPlusSummons`. If `u` has passive `259` and `Rand(100) < trunc0(cmd259.val * 100.0f)`: sets `this.warningShotUnit = u`, pushes `u.action`, sets `u.isWarningShot = 1` (`[u+0x105] = 1`), creates `CActionAttack` (`0x414e20`) or `CActionEnemyAttack` (`0x419ad0`) targeting `actor`, sets `PhaseNo = 12`, and breaks. |
| `10` | `0x436e0c` | **Opposing Mesmerized (`283` / `0x11b`) Turn Loss:** `TurnPhaseNo++`. Iterates `u` in `oppPlusSummons`. If `u` has passive `283` and `Rand(100) < trunc0(cmd283.val * 100.0f)`: logs message, sets `PhaseNo = 4` (`actor` loses turn), and breaks. |
| `11` | `0x436eb0` | **Erotic Dance (`203` / `0xcb`) Turn Loss:** `TurnPhaseNo++`. If `actor` has active status `203` and `Rand(100) < trunc0(cmd203.val * 100.0f)`: logs msg `0x45` and sets `PhaseNo = 4` (`actor` loses turn). |
| `12` | `0x437364` | **Murder License (`319` / `0x13f`):** `TurnPhaseNo++`. If `actor` has active status `319` (no `Rand(100)` roll in State `12` â€” triggers deterministically when `319` is on `actor`): pushes `actor.action`, picks random target `oppUnits[Rand(len(oppUnits))]`, allocates `CActionPatternE1580` (`0x42be90`, which applies command `119` Instakill with `val = 1.0f`), and sets `PhaseNo = 11`. |
| `13` | `0x437499` | **Tranquil Song (`357` / `0x165`):** `TurnPhaseNo++`. If `actor` has passive `357` and `Rand(100) < trunc0(cmd357.val * 100.0f)`: applies 4-turn `-10%` (`-0.1f`) debuffs for command `41` (`0x29`, ATK) and command `43` (`0x2b`, INT) to all `u` in `oppUnits`, and sets `PhaseNo = 14`. |
| `14` | `0x4376e3` | **Usurper of Souls (`350` / `0x15e`):** `TurnPhaseNo++`. If `actor` has passive `350` and `Rand(100) < trunc0(cmd350.val * 100.0f)`: collects opposing enemy Dolls (`u.isPlayerSide != actor.isPlayerSide`, `u.IsDoll()`, `actor.isPlayerSide != 0`, passing `0x4fd6a0`), removes one random Doll via `0x43b6a0`, and sets `PhaseNo = 14`. |
| `15` | `0x4378d9` | **Shadow Heart (`448` / `0x1c0`):** `TurnPhaseNo++`. If `actor` has passive `448` and `Rand(100) < trunc0(cmd448.val * 100.0f)`: if no active Doll on `actor`'s side is owned by `actor.playerStatus` (`0x4fd950`), spawns Doll ID `380` (`0x17c`, 3 turns) via `0x4fe2e0` + `0x43a150`, and sets `PhaseNo = 14`. |
| `16` | `0x437b0c` | **Regen Statuses (`215, 216, 246, 247`) & Equipment Enchants (`144..149, 296`):** `TurnPhaseNo++`. Ticks all active commands on `actor` where `vtable+0x80()` is true (`215` Carol, `216` Chorale, `246` HP Regen, `247` TP Regen) plus equipment HP/TP regen enchants (see pseudocode below), and executes via `CCommand::Execute`. |
| `17` | `0x437ed6` | **Post-Regen Fall-Through:** `TurnPhaseNo++` (`17 -> 18`), falls directly into State `18`. |
| `18` | `0x437eda` | **Subtle Dance (`200` / `0xc8`) Performer Tick:** `TurnPhaseNo++`. If `200` is in `actor.dances`: pushes `actor.action`, targets `oppUnits`, allocates `CActionPatternE0822` (`0x42b240`) into `this.currentPattern`, and sets `PhaseNo = 11`. |
| `19` | `0x438085` | **Weird Dance (`204` / `0xcc`) Performer Tick:** `TurnPhaseNo++`. If `204` is in `actor.dances`: pushes `actor.action`, targets `oppUnits`, allocates `CActionPatternE0835` (`0x42b8a0`) into `this.currentPattern`, and sets `PhaseNo = 11`. |
| `20` | `0x43824e` | **Salsa (`199` / `0xc7`) & Debilitating Geas (`339` / `0x153`) Performer Tick:** `TurnPhaseNo++`. If `199` is in `actor.dances` or `339` is in `actor.geass` (and present on `oppUnits[0]`): pushes `actor.action`, targets `oppUnits`, allocates `CActionPatternT0094` (`0x42ec90`) into `this.currentPattern`, and sets `PhaseNo = 11`. |
| `21` | `0x43841e` | **Poison (`113` / `0x71`) Damage Tick:** `TurnPhaseNo++`. If `actor` has status `113`, calls `CCommand_0113::TickDamage` (`0x482150`) and `CCommand::Execute`: deals `0` damage if `actor.IsAsleep()` (`vtable+0xbc`); else `raw = trunc0(f32(MaxHP) * 0.05f)`, clamped to `CurHP - 1` (if `raw == 0` or `raw >= CurHP`, `raw = CurHP - 1`), then capped at `min(250, raw)` (`0xfa`). |
| `22` | `0x438495` | **Undaunted Spirit (`355` / `0x163`) Auto-Revive:** `TurnPhaseNo++`. Scans all dead units (`u.status->IsDead()`) in `this.units`; for each dead unit `u` on `actor`'s side with passive `355`, rolls `Rand(100) < trunc0(cmd355.val * 100.0f)`. On proc: revives `u` at `1 HP` via `CCommand::Execute`, calls `_SortTime(1, 1)`, and sets `PhaseNo = 14`. |
| `23` | `0x4386ff` | **Pre-Terminal Advance:** `TurnPhaseNo++` (`23 -> 24`), jumps to State `24`. |
| `24` | `0x438722` | **Terminal Gate:** When `TurnPhaseNo >= 24` and `PhaseNo == 0`, jumps to `0x438773` -> sets `PhaseNo = 1` (or `5` if no alive enemies). |

**Typed Pseudocode:** *(State `16` Regen and State `21` Poison)*
```python
def TurnPhase16_Regen(this: CBattleBase, actor: Unit) -> None:
    # 0x437b0c..0x437ed5
    seq = CCommandResultList()
    st: CGameStatus = actor.status
    maxHp: i32 = st.GetMaxHP()

    # 1. Command-based turn-start regen (vtable+0x80() == True: 215, 216, 246, 247)
    for cmd in st.activeCommands:
        if cmd.IsTurnStartRegen():  # vtable+0x80
            if cmd.id == 215:  # Carol (0x4894a0): song bonus 279 (0x117) scales by *10.0f
                hp = trunc0(cmd.GetValue() * (1.0 + cmd.GetSubBonus(279) * 10.0))
                seq.AddHpHeal(st, hp)
            elif cmd.id == 216 and actor.playerStatus is not None:  # Chorale (0x4895e0)
                tp = trunc0(cmd.GetValue() + cmd.GetSubBonus(279) * 100.0)
                seq.AddTpHeal(st, tp)
            elif cmd.id == 246:  # HP Regen (0x48a640)
                hp = trunc0(f32(maxHp) * cmd.GetValue())
                seq.AddHpHeal(st, hp)
            elif cmd.id == 247 and actor.playerStatus is not None:  # TP Regen (0x48a710)
                tp = trunc0(cmd.GetValue())
                seq.AddTpHeal(st, tp)

    # 2. Equipment HP regen enchants (144/0x90, 145/0x91, 148/0x94, 296/0x128)
    hpEnch: i32 = 0
    if (c144 := st.GetEnchantCount(0x90)) > 0:
        hpEnch += max(4, trunc0(f32(maxHp) * (0.04 * f32(c144))))
    if (c145 := st.GetEnchantCount(0x91)) > 0:
        hpEnch += max(2, trunc0(f32(maxHp) * (0.02 * f32(c145))))
    if (c148 := st.GetEnchantCount(0x94)) > 0:
        hpEnch += max(10, trunc0(f32(maxHp) * (0.08 * f32(c148))))
    if st.GetEnchantCount(0x128) > 0 and Rand(100) < 4:  # 296: 4% full HP restore
        hpEnch += maxHp
    if hpEnch > 0:
        seq.AddHpHeal(st, hpEnch)

    # 3. Equipment TP regen enchants (146/0x92 = +4, 147/0x93 = +2, 149/0x95 = +6)
    tpEnch: i32 = 4 * st.GetEnchantCount(0x92) + 2 * st.GetEnchantCount(0x93) + 6 * st.GetEnchantCount(0x95)
    if tpEnch > 0:
        seq.AddTpHeal(st, tpEnch)

    CCommand_Execute(seq, mode=-1, battleInfo=this.battleInfo)


def TurnPhase21_Poison(this: CBattleBase, actor: Unit) -> None:
    # 0x43841e..0x438494 & CCommand_0113::TickDamage at 0x482150..0x482286
    st: CGameStatus = actor.status
    if st.FindCommand(0, 113) is None or st.IsAsleep():
        return  # Sleeping units take 0 poison damage (0x4821bc..0x4821ca)
    dmg: i32 = trunc0(f32(st.GetMaxHP()) * 0.05)
    curHp: i32 = st.GetCurHP()
    if dmg == 0 or dmg >= curHp:
        dmg = curHp - 1
    if dmg > 0:
        dmg = min(250, dmg)  # Cap at 250 (0xfa at 0x4821ed..0x4821ff)
        seq = CCommandResultList()
        seq.AddHpDamage(st, dmg)
        CCommand_Execute(seq, mode=0, battleInfo=this.battleInfo)
```

**Program Evidence:**
```text
00436713  mov      byte ptr [esi + 0x105], 0
0043671a  mov      byte ptr [esi + 0x107], 0
00436721  inc      dword ptr [edi + 0x20]
00436724  mov      ecx, dword ptr [esi + 0x10]
00436727  push     0x137
0048d211  mov      ecx, dword ptr [0x816ce8]
0048d217  push     0x64
0048d219  call     0x490790
0048d21e  mov      ecx, dword ptr [ebx + 0x28]
0048d221  cmp      eax, ecx
0048d223  jb       0x48d241
0048d225  lea      eax, [ecx + 0xa]
0048d228  mov      dword ptr [ebx + 0x28], eax
00436d08  inc      eax
00436d09  mov      dword ptr [edi + 0x20], eax
00436d0c  mov      ecx, dword ptr [esi + 0x10]
00436d0f  mov      eax, dword ptr [ecx]
00436d11  mov      eax, dword ptr [eax + 0xb8]
00436d17  call     eax
00436d19  test     al, al
00436d1b  je       0x436d4c
00436d1d  mov      ecx, 0x64
00436d22  call     0x505ac0
00436d27  cmp      eax, 0x1e
00436d2a  jge      0x436d4c
0048218d  call     dword ptr [eax + 0x28]
00482190  movd     xmm0, eax
00482194  cvtdq2ps xmm0, xmm0
00482197  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
0048219f  cvttss2si esi, xmm0
004821bc  mov      edx, dword ptr [edi]
004821be  mov      ecx, edi
004821c0  mov      edx, dword ptr [edx + 0xbc]
004821c6  call     edx
004821c8  test     al, al
004821ca  jne      0x482278
004821ed  mov      eax, 0xfa
004821f2  mov      dword ptr [ebp - 4], 0
004821f9  cmp      esi, eax
004821fb  lea      ecx, [ebp - 0x68]
004821fe  push     edi
004821ff  cmovg    esi, eax
```

---

### M01.04 Post-Action Resolution, Extra Turns (`288`/`289`/`354`), Doll/Summon Life Expiry, and Heretic Samsara (`291`)

**Binary VA(s):** `0x438c81..0x4392ea`, jump table `0x439884`, `0x436314`, `0x4365ff`, `0x43b6a0..0x43b800`, `0x43d2c0..0x43d3ba`
**Calls:** `0x4f98e0` (`CGameStatus::IsDead`, `vtable+0x38`), `0x4359e0` (`IsDoll`), `0x4fd960` / `0x4d4230` (`GetDollMaxActions`), `0x43b510` (`GetAliveEnemyCount`), `0x505ac0` (`Rand(max)`), `0x47b220` / `0x47e260` (`CreateCommand`), `0x43e5c0` (`CBattleBase::_SetTime`), `0x43e510` (`CBattleBase::_SortTime`), `0x43b6a0` (`CBattleBase::RemoveUnit`), `0x43d2c0` (`CBattleBase::DestroyDollsByOwner`)
**CalledBy:** `0x438c7b` (`CBattleBase::Update` at completion of `PhaseNo == 3`)

**Typed Pseudocode:**
```python
def CBattleBase_PostAction(this: CBattleBase, actor: Unit, consumeTurn: bool) -> None:
    # 0x438cba..0x4392ea
    actor.totalActionCount += 1  # [actor+0xb8]++
    if actor.status.IsDead():
        this._SetTime(None)
        this.TurnPhaseNo = 0
        CBattleBase_EndActionCleanup(this)
        return

    actor.extraTurnCount += 1  # [actor+0xb0]++ (0x438cd2)
    # If already inside a multi-action turn (e.g. action 1 of 2 or 3), loop back without _SetTime!
    if actor.extraTurnCount < actor.maxTurnActions:
        CBattleBase_EndActionCleanup(this)
        return

    # Doll lifetime expiry check (0x438cea..0x438e3c)
    if actor.IsDoll():  # unitId in 2000..2999
        maxActions: u32 = actor.GetDollMaxActions()  # 0x4fd960 / 0x4d4230 (0 -> 0xffffffff)
        if maxActions == 0:
            maxActions = 0xFFFFFFFF
        if actor.totalActionCount < maxActions:
            this._SetTime(actor)
            this.TurnPhaseNo = 0
        else:
            # Doll expires: remove from this.units, re-sort & normalize turn list
            this.RemoveDollUnit(actor)
            this._SortTime(normalize=1, updateUi=1)
            this.TurnPhaseNo = 0
        CBattleBase_EndActionCleanup(this)
        return

    # Note: Owner death/incapacitation also destroys owned Dolls via 0x43d2c0, and banished/expired
    # Summon/Guest/Enemy units are removed from this.units via 0x43b6a0 (which calls _SortTime(0, 1)).

    if this.GetAliveEnemyCount() == 0:
        if consumeTurn:
            this._SetTime(actor)
            this.TurnPhaseNo = 0
        CBattleBase_EndActionCleanup(this)
        return

    # Heretic Samsara (291 / 0x123, 0x438e50..0x439038, jump table 0x439884)
    cmd291: CCommand | None = actor.status.FindCommand(0, 0x123)
    if cmd291 is not None and cmd291.GetValue() >= 1.0:
        # Maps statIdx 6..13 -> fixed resistance commands 416..423 (0x1a0..0x1a7):
        # 416 Slash, 417 Stab, 418 Bash, 419 Fire, 420 Water, 421 Wind, 422 Earth, 423 Lightning
        for statIdx in range(6, 14):
            effId: u32 = 0x1A0 + (statIdx - 6)
            resVal: f32 = f32((Rand(2) + 1) * 50)  # 50.0f or 100.0f (0x438f10..0x438f1e)
            actor.status.AddFixedResistanceStatus(effId, resVal, sourceCmd=cmd291)

    # Extra-Turn Rolls: 288 (Double Action), 289 (Triple Action), 354 (Did You Call for Me?)
    # Guard (0x43903b..0x439069): cannot chain if grantedExtraTurn != 0, if no longer units[0], or if asleep
    if actor.grantedExtraTurn == 0 and actor == this.units[0] and not actor.status.IsAsleep():
        targetActions: u32 = 0
        cmd288 = actor.status.FindCommand(0, 0x120)  # 288 Double Action
        cmd289 = actor.status.FindCommand(0, 0x121)  # 289 Triple Action
        cmd354 = actor.status.FindCommand(0, 0x162)  # 354 Did You Call for Me?

        if cmd288 is not None and Rand(100) < trunc0(cmd288.GetValue() * 100.0):
            targetActions = 2
        elif cmd289 is not None and Rand(100) < trunc0(cmd289.GetValue() * 100.0):
            targetActions = 3
        elif cmd354 is not None and Rand(100) < trunc0(cmd354.GetValue() * 100.0):
            targetActions = 2

        if targetActions > 0:
            actor.grantedExtraTurn = 1  # [actor+0x107] = 1
            actor.maxTurnActions = targetActions  # [actor+0xb4] = targetActions
            # Skips _SetTime and keeps TurnPhaseNo; on next PhaseNo=0, [actor+0xb0] != 0 jumps to 0x43875a!
            CBattleBase_EndActionCleanup(this)
            return

    if consumeTurn:
        this._SetTime(actor)
        this.TurnPhaseNo = 0
    CBattleBase_EndActionCleanup(this)


def CBattleBase_EndActionCleanup(this: CBattleBase) -> None:
    # 0x439292..0x4392ea
    for u in this.units:
        if u.status.IsDead():
            u.actionType = 7
    this.units[0].isDefending = 0  # [units[0]+0x104] = 0
    this.PhaseNo = 0
```

**Program Evidence:**
```text
00438cba  mov      ecx, dword ptr [esi + 0x10]
00438cbd  inc      dword ptr [esi + 0xb8]
00438cc3  mov      edx, dword ptr [ecx]
00438cc5  mov      edx, dword ptr [edx + 0x38]
00438cc8  call     edx
00438cca  test     al, al
00438ccc  jne      0x43927b
00438cd2  inc      dword ptr [esi + 0xb0]
00438cd8  mov      eax, dword ptr [esi + 0xb0]
00438cde  cmp      eax, dword ptr [esi + 0xb4]
00438ce4  jb       0x43928b
00438ea1  lea      eax, [ecx - 6]
00438ea4  jmp      dword ptr [eax*4 + 0x439884]
00438f10  mov      ecx, 2
00438f15  call     0x505ac0
00438f1a  mov      edi, dword ptr [ebp - 0x1c]
00438f1d  inc      eax
00438f1e  imul     esi, eax, 0x32
0043903b  cmp      byte ptr [esi + 0x107], 0
00439042  jne      0x439272
00439150  mov      ecx, dword ptr [ebp - 0x18]
00439153  mov      byte ptr [esi + 0x107], 1
0043915a  mov      dword ptr [esi + 0xb4], eax
```

---

### M01.05 ATB `_SetTime` (`0x43e5c0` -> `0x4499d0..0x44a3c5`)

**Binary VA(s):** `0x43e5c0..0x43e6cb` (`CBattleBase::_SetTime`), `0x4499d0..0x44a3cf` (`CBattle::_SetTime`)
**Calls:** `0x43e510` (`CBattleBase::_SortTime`), `0x4f7280` (`GetActionSpeed`, `vtable+0x154`), `0x4f52d0` (`GetSingSpeed`, `vtable+0x158`), `0x4f54d0` (`GetWeaponActionSpeed`, `vtable+0xf4`), `0x56c9a0` (`CParameterSkill::GetSpeed`), `0x557590` (`GetEnemySpellSpeed`), `0x490790` (`CRandom::Get`)
**CalledBy:** `0x44917d`, `0x44918f` (`CBattle::_Initialize`), `0x4362b4`, `0x438e15`, `0x43927d`, `0x439317`, `0x4395f8` (`CBattleBase::Update`), `0x43ec38`, `0x43ee87` (`CBattleBase::_CreateAction`)

**Typed Pseudocode:**
```python
def CBattleBase_SetTime(this: CBattleBase, unitArg: Unit | None) -> None:
    # 0x43e5c0..0x43e6cb
    head: Unit = this.units[0]
    if unitArg is not None and unitArg != head:
        # Non-head unit: only resets extra-turn counters without recalculating gauge!
        unitArg.extraTurnCount = 0
        unitArg.maxTurnActions = 1
        return

    target: Unit = unitArg if (unitArg is not None) else head
    head.gauge = 0.0
    this._SortTime(normalize=0, updateUi=0)

    isChanting: u8 = 1 if (target.actionType in (3, 9)) else 0
    this.vtable_SetTime(target, isChanting)  # CBattle::_SetTime (0x4499d0)

    hasAliveEnemies: u8 = 1 if (this.GetAliveEnemyCount() >= 1) else 0
    this._SortTime(normalize=1, updateUi=hasAliveEnemies)
    target.extraTurnCount = 0
    target.maxTurnActions = 1


def CBattle_SetTime(this: CBattle, unit: Unit, isChanting: u8) -> None:
    # 0x4499d0..0x44a3cf
    st: CGameStatus = unit.status
    actType: u32 = unit.actionType
    isPlayerUnit: bool = (unit.isPlayerSide != 0) and not (3000 <= unit.unitId <= 3999)

    # 1. Governing Stat Selection (0x449a0d..0x449b4c)
    #    Default statIdx = 5 (AGI). On Chant start (actType in {3, 9}), spell flags select INT(2)/RES(3)/AGI(5).
    statIdx: u32 = 5
    if actType != 7 and actType in (3, 9):
        if isPlayerUnit:
            skillParam = SkillData_Magic.Find(unit.skillId)  # [0x738a58]
            flags48: u32 = skillParam.u32_at(0x48)
            if (flags48 & 1) != 0:
                statIdx = 2  # INT
            elif ((flags48 >> 1) & 1) != 0:
                statIdx = 3  # RES
            elif ((flags48 >> 2) & 1) != 0:
                statIdx = 5  # AGI
        else:
            atkParam = EnemyAttackData.Find(unit.enemyAttackId)  # [0x7389d4]
            flags40: u32 = atkParam.u32_at(0x40)
            if ((flags40 >> 11) & 1) != 0:
                statIdx = 2  # INT
            elif ((flags40 >> 12) & 1) != 0:
                statIdx = 3  # RES
            else:
                statIdx = 5  # AGI

    statFactor: f32 = (f32(st.GetStat(statIdx)) + 100.0) / 200.0

    # 2. Battle Jitter PRNG (0..5%) & Equipment Weight/Level Penalty (0x449b60..0x449c39)
    this.jitterRng.StepVtable04()
    s0: i32 = this.jitterRng.seed0  # [rng+0x1c]
    s1: i32 = this.jitterRng.seed1  # [rng+0x20]
    prod64: i64 = i64(s0) * i64(s1)
    ebx_u32: u32 = u32(prod64 & 0xFFFFFFFF)
    this.jitterRng.seed0 = i32((u32(s0) + 0x126 + u32((prod64 >> 3) & 0xFFFFFFFF)) & 0xFFFFFFFF)
    this.jitterRng.seed1 = s1 + 1
    r: u32 = (ebx_u32 % 12) >> 1  # integer in 0..5

    jitteredStat: f32 = statFactor + statFactor * (f32(r) / 100.0)
    weightTerm: f32 = st.GetWeaponActionSpeed() / 12.0  # vtable+0xf4 / 12.0f
    lv: u32 = st.GetLevel()  # vtable+0x10
    baseTerm: f32 = jitteredStat - weightTerm * (1.0 + f32(lv) / 100.0)

    # 3. Action Speed Factor (actSpeed, default 1.0f, 0x449c3f..0x449d5e)
    actSpeed: f32 = 1.0
    if actType != 7 and actType in (0, 2, 8):
        if isPlayerUnit:
            if SkillData_Tech.Contains(unit.skillId):  # [0x738a64]
                actSpeed = unit.playerStatus.GetActionSpeed(unit.skillId, 0)  # 0x4f7280
            elif SkillData_Passive.Contains(unit.skillId):  # [0x738a54]
                actSpeed = CParameterSkill_GetSpeed(unit.skillId, 1)  # 0x56c9a0
        else:
            atkParam = EnemyAttackData.Find(unit.enemyAttackId)
            if ((atkParam.u32_at(0x40) >> 2) & 1) == 0:  # non-magic enemy attack
                actSpeed = atkParam.f32_at(0x5C)

    # 4. Chant / Spell Speed Factor (chantSpeed, default 1.0f, 0x449d5e..0x449e61)
    chantSpeed: f32 = 1.0
    if actType != 7:
        if isPlayerUnit:
            if actType == 3:  # Player Chant start
                chantSpeed = unit.playerStatus.GetSingSpeed(unit.skillId, 0)  # 0x4f52d0
            elif actType == 2 and SkillData_Magic.Contains(unit.skillId):  # Player Magic completion
                chantSpeed = unit.playerStatus.GetActionSpeed(unit.skillId, 0)  # 0x4f7280
        else:
            atkParam = EnemyAttackData.Find(unit.enemyAttackId)
            if actType == 9:  # Enemy/Summon Chant start
                chantSpeed = atkParam.f32_at(0x4C)
            elif actType == 8 and ((atkParam.u32_at(0x40) >> 2) & 1) != 0:  # Enemy Magic completion
                chantSpeed = GetEnemySpellSpeed(unit.enemyAttackId)  # 0x557590 ([atkParam+0x5c])

    # 5. Slow (122 / 0x7a) & Core Product (0x449e61..0x449ea3)
    slowMult: f32 = 0.5 if st.HasCommand(0x7A) else 1.0
    core: f32 = actSpeed * baseTerm * chantSpeed * slowMult * 0.5

    # 6. Additive Speed Buffs, Passives, and Equipment Enchants (0x449ea9..0x44a309)
    if actType != 7 and actType in (3, 9):
        # Chanting modifiers: 214 Requiem (0xd6), 265 Chant Speed Inc (0x109), 281 Chant Speed Mod (0x119)
        buffSum: f32 = 1.0 + st.CmdVal(0xD6) + st.CmdVal(0x109) + st.CmdVal(0x119)
        # Chant speed enchants: 54 (0x36) +0.20, 55 (0x37) +0.10, 56 (0x38) -0.20
        enchDelta: f32 = (
            0.20 * f32(st.GetEnchantCount(0x36))
            + 0.10 * f32(st.GetEnchantCount(0x37))
            - 0.20 * f32(st.GetEnchantCount(0x38))
        )
    else:
        # Action modifiers: 168 Speed (0xa8), 217 March (0xd9), 221 Barcarole (0xdd)
        buffSum = 1.0 + st.CmdVal(0xA8) + st.CmdVal(0xD9) + st.CmdVal(0xDD)
        # Passive 261 (0x105, Stamina): active when CurHP <= (MaxHP * 40) // 100
        if st.HasCommand(0x105) and st.GetCurHP() <= (st.GetMaxHP() * 40) // 100:
            buffSum += st.CmdVal(0x105)
        # Action speed enchants: 51 (0x33) +0.10, 52 (0x34) +0.05, 53 (0x35) -0.10
        enchDelta = (
            0.10 * f32(st.GetEnchantCount(0x33))
            + 0.05 * f32(st.GetEnchantCount(0x34))
            - 0.10 * f32(st.GetEnchantCount(0x35))
        )

    enchDelta = clamp(enchDelta, -0.50, +0.50)  # Clamped to [-0.5f, +0.5f] at 0x44a1ab..0x44a1d8

    # Shared additive modifiers: 201 Mazurka (0xc9), 340 Dumbing Geas (0x154),
    # 276 Singing Speed Mod (0x114), 277 Dancing Speed Mod (0x115), 316 Doll Speed UP (0x13c, if puppets active)
    modSum: f32 = (
        buffSum
        + enchDelta
        + st.CmdVal(0xC9)
        + st.CmdVal(0x154)
        + st.CmdVal(0x114)
        + st.CmdVal(0x115)
        + (st.CmdVal(0x13C) if len(unit.puppets) > 0 else 0.0)
    )

    # 7. Defend (1.15x), Escape (1.20x), 0.92f Cap, and Enchant 298 (0x12a) (0x44a309..0x44a3b3)
    gauge: f32 = core * modSum
    if actType == 5:  # Defend
        gauge *= 1.15
    elif actType == 6:  # Escape
        gauge *= 1.20

    gauge = min(0.92, gauge)

    # Enchant 298 (0x12a): checks Rand(10) < 10 (always true!) when isChanting != 0, adding +0.25f (capped at 0.92f)
    if isChanting != 0 and st.GetEnchantCount(0x12A) > 0:
        if GlobalRng.Rand(10) < 10:
            gauge = min(0.92, gauge + 0.25)

    unit.gauge = gauge
```

**Program Evidence:**
```text
00449b4c  addss    xmm0, dword ptr [0x6d9540]    ; float 100
00449b54  mov      edi, dword ptr [esp + 0x1c]
00449b58  divss    xmm0, dword ptr [0x6d95b8]    ; float 200
00449ba3  mov      eax, dword ptr [eax + 0xf4]
00449ba9  call     eax
00449bab  fdiv     dword ptr [0x6d9470]    ; float 12
00449e72  movss    xmm1, dword ptr [0x6d9348]    ; float 0.5
00449e7a  test     al, al
00449e7c  je       0x449e84
00449e7e  movss    dword ptr [esp + 0xc], xmm1
00449e84  movss    xmm0, dword ptr [esp + 0x18]
00449e8a  mulss    xmm0, dword ptr [esp + 0x14]
00449e90  mov      eax, dword ptr [ebx + 0x1c]
00449e93  mulss    xmm0, dword ptr [esp + 0x10]
00449e99  mulss    xmm0, dword ptr [esp + 0xc]
00449e9f  mulss    xmm0, xmm1
0044a321  cmp      eax, 5
0044a324  jne      0x44a330
0044a326  mulss    xmm0, dword ptr [0x6d939c]    ; float 1.15
0044a32e  jmp      0x44a33d
0044a330  cmp      eax, 6
0044a333  jne      0x44a33d
0044a335  mulss    xmm0, dword ptr [0x6d93a0]    ; float 1.2
0044a33d  cmp      byte ptr [ebp + 0xc], 0
0044a341  movss    xmm1, dword ptr [0x6d9380]    ; float 0.92
0044a349  minss    xmm1, xmm0
0044a359  push     0x12a
0044a35e  call     dword ptr [eax + 0xf0]
0044a364  test     eax, eax
0044a366  je       0x44a3a2
0044a368  mov      ecx, dword ptr [0x816ce8]
0044a36e  push     0xa
0044a370  call     0x490790
0044a375  cmp      eax, 0xa
0044a378  jge      0x44a3a2
0044a37a  movss    xmm0, dword ptr [esp + 0x14]
0044a380  addss    xmm0, dword ptr [0x6d932c]    ; float 0.25
```

---

### M01.06 Player Weapon / Unarmed / Action / Chant Speed Slots & Enemy Spell Speed

**Binary VA(s):** `0x4f7280..0x4f72e5` (`CGamePlayerStatusBase::GetActionSpeed`, `vtable+0x154`), `0x4f52d0..0x4f536f` (`CGamePlayerStatusBase::GetSingSpeed`, `vtable+0x158`), `0x4f54d0..0x4f55e7` (`CGamePlayerStatusBase::GetWeaponActionSpeed`, `vtable+0xf4`), `0x56c9a0..0x56ca85` (`CParameterSkill::GetSpeed`), `0x557590..0x5575b4` (`GetEnemySpellSpeed`)
**Calls:** `0x4f68a0` (`_SearchSkill`), `0x56ba30` (`GetSkillType`), `0x56c9a0` (`CParameterSkill::GetSpeed`), `0x507310` (`RBTree::Find`)
**CalledBy:** `0x449ba9`, `0x449cc5`, `0x449d9d`, `0x449ded`, `0x449e56` (`CBattle::_SetTime`)

**Typed Pseudocode:**
```python
def CGamePlayerStatusBase_GetActionSpeed(this: CGamePlayerStatusBase, skillId: u32, lv: u32) -> f32:
    # 0x4f7280..0x4f72e5 (vtable+0x154)
    if lv == 0:
        lv = this._SearchSkill(skillId).level  # [entry+4] via 0x4f68a0
    base: f32 = CParameterSkill_GetSpeed(skillId, lv)  # 0x56c9a0:
    #   lv in 1..10:
    #     SkillType 0, 2 (Tech 0x738a64) or 1 (Magic 0x738a58): f32([param + lv*4 + 0xc0])
    #     SkillType 3 (Passive/Unique 0x738a54): f32([param + 0x60])
    #     SkillType 4, 5 or lv not in 1..10: 1.0f
    cmd352: CCommand | None = this.FindCommand(0, 0x160)  # 352 Wreathed in Glory
    return (base + cmd352.GetValue()) if (cmd352 is not None) else base


def CGamePlayerStatusBase_GetSingSpeed(this: CGamePlayerStatusBase, skillId: u32, lv: u32) -> f32:
    # 0x4f52d0..0x4f536f (vtable+0x158)
    if lv == 0:
        lv = this._SearchSkill(skillId).level
    if 1 <= lv <= 10 and GetSkillType(skillId) == 1:  # Magic skill table [0x738a58]
        param = SkillData_Magic.Find(skillId)
        return param.f32_at(lv * 4 + 0xE8)
    return 1.0


def CGamePlayerStatusBase_GetWeaponActionSpeed(this: CGamePlayerStatusBase) -> f32:
    # 0x4f54d0..0x4f55e7 (vtable+0xf4; base CGameStatus::vtable+0xf4 at 0x4f9a60 returns 0.0f for enemies)
    mainHand = this.equipSlots[0]  # [this+0xa8]
    if mainHand is not None:
        equipParam = EquipmentData.Find(mainHand.itemId)  # [0x7389e0], itemId at [mainHand+0x70]
        if equipParam.u32_at(0x38) != 0:  # Not a weapon
            return 1.0
        rankId: u32 = equipParam.u32_at(0x64)
        return WeaponRankData.Find(rankId).f32_at(0x28)  # [0x738a94]

    # Unarmed: Enchant 263 (0x107, "A-rank speed when no weapon is equipped") forces rankId = 1
    if this.GetEnchantCount(0x107) > 0:
        return WeaponRankData.Find(1).f32_at(0x28)

    classId: u32 = this.GetClassId()  # vtable+0x13c
    unarmedRankId: u32 = ClassData.Find(classId).u32_at(0x3C)  # [0x7389bc]
    return WeaponRankData.Find(unarmedRankId).f32_at(0x28)


def GetEnemySpellSpeed(enemyAttackId: u32) -> f32:
    # 0x557590..0x5575b4
    return EnemyAttackData.Find(enemyAttackId).f32_at(0x5C)  # [0x7389d4]
```

**Program Evidence:**
```text
004f729e  call     0x56c9a0
004f72a3  mov      eax, dword ptr [edi]
004f72a5  mov      ecx, edi
004f72a7  push     0x160
004f72ac  push     0
004f72ae  movss    dword ptr [esp + 0x18], xmm0
004f72b4  call     dword ptr [eax + 0x48]
004f5335  mov      eax, dword ptr [eax]
004f5337  movss    xmm0, dword ptr [eax + esi*4 + 0xe8]
004f54d8  mov      eax, dword ptr [esi + 0xa8]
004f54de  test     eax, eax
004f54e0  je       0x4f5556
004f5595  push     0x107
004f559a  mov      ecx, esi
004f559c  mov      eax, dword ptr [eax]
004f559e  movss    xmm0, dword ptr [eax + 0x28]
004f55a3  mov      eax, dword ptr [esi]
004f55a5  movss    dword ptr [esp + 8], xmm0
004f55ab  call     dword ptr [eax + 0xf0]
004f55b1  test     eax, eax
004f55b3  je       0x4f55df
004f55b5  mov      dword ptr [esp + 4], 1
005575aa  mov      eax, dword ptr [eax]
005575ac  movss    xmm0, dword ptr [eax + 0x5c]
```

---

### M01.07 Chant & Performance Interruption (`0x44cf90..0x44d266` Physical, `0x44f12a..0x44f14a` Magic Crit-Only, `0x47ea83..0x47eac0` Cancellation)

**Binary VA(s):** `0x44cf90..0x44d266` (physical interruption in `CBattle::CalcPhysicalAttack`), `0x44f12a..0x44f14a` (magical crit-only interruption in `CBattle::CalcMagicalAttack`), `0x47ea83..0x47eac0` (`CCommand::Execute` cancellation dispatch), `0x43bc50` (`CancelChant`), `0x43c110` (`CancelSong`), `0x43c600` (`CancelDance`), `0x43c9b0` (`CancelPuppet`), `0x43ce30` (`CancelGeass`)
**Calls:** `0x47e400` (`SumCommandValues`), `0x505ac0` (`Rand(max)`), `0x490790` (`CRandom::Get`), `0x428560` (`CCommandResultList::GetEntry`), `0x43bc50`, `0x43c110`, `0x43c600`, `0x43c9b0`, `0x43ce30`
**CalledBy:** `0x44c770` (`CBattle::CalcPhysicalAttack`), `0x44e690` (`CBattle::CalcMagicalAttack`), `0x47e500` (`CCommand::Execute`)

**Typed Pseudocode:**
```python
def CalcPhysicalInterruption(
    target: Unit, targetCmds: CCommandList, hpDamage: i32, res: CommandResult_s
) -> None:
    # 0x44cfad..0x44d24a
    # 1. Concentrate / Magic Interruption Modifier (command 264 / 0x108)
    conc: f32 = targetCmds.SumValues(0x108)  # 0x47e400; note: in vanilla, added to denominator as (1.0f + conc)

    # 2. Base damage-to-HP ratio clamped to [0.0f, 0.95f] (0x44d011..0x44d065)
    #    Note: 0x44d044 is the X14 balance-patch site; in vanilla it executes:
    #    denom = f32(target.status.GetMaxHP()) * 1.5f + (1.0f + conc)
    denom: f32 = f32(target.status.GetMaxHP()) * 1.5 + (1.0 + conc)
    baseRate: f32 = clamp(f32(hpDamage) / denom, 0.0, 0.95)

    # 3. Equipment Interruption-Resistance Enchants on target.status (0x44d07f..0x44d199)
    #    57 (0x39 GrandDOWN) = +0.10, 58 (0x3a DOWN) = +0.06, 59 (0x3b MiniDOWN) = +0.03,
    #    60 (0x3c UP) = -0.06, 61 (0x3d MegaDOWN) = +0.20
    st: CGameStatus = target.status
    enchRes: f32 = (
        0.10 * f32(st.GetEnchantCount(0x39))
        + 0.06 * f32(st.GetEnchantCount(0x3A))
        + 0.03 * f32(st.GetEnchantCount(0x3B))
        - 0.06 * f32(st.GetEnchantCount(0x3C))
        + 0.20 * f32(st.GetEnchantCount(0x3D))
    )

    # 4. Final rate clamped to [0.0f, 0.95f] & primary roll (0x44d1b9..0x44d220)
    finalRate: f32 = clamp(baseRate - enchRes, 0.0, 0.95)
    res.isInterrupted = 1 if (Rand(100) < trunc0(finalRate * 100.0)) else 0  # [res+0x33]

    # 5. Independent Critical-Hit 33% Interrupt Roll (0x44d228..0x44d24a)
    #    Bypasses Concentrate (264) and equipment enchants (57..61)!
    if res.isCrit != 0 and Rand(100) < 33:  # 0x21
        res.isInterrupted |= 1


def CalcMagicalInterruption(res: CommandResult_s) -> None:
    # 0x44f12a..0x44f14a
    # Magical hits never run the HP-ratio formula; they only interrupt on a Magical Critical (301) at 33%.
    if res.isCrit != 0 and GlobalRng.Rand(100) < 33:  # 0x21
        res.isInterrupted = 1


def ExecuteInterruptionCancellation(battle: CBattleBase, targetStatus: CGameStatus, res: CommandResult_s) -> None:
    # 0x47ea83..0x47eac0 (called when target took HP damage, survived, and res.isInterrupted != 0)
    if res.isInterrupted != 0 and battle is not None:
        battle.CancelChant(targetStatus)   # 0x43bc50: if unit.actionType in (3, 9), sets unit.actionType = 7
        battle.CancelSong(targetStatus)    # 0x43c110: strips unit.songs IDs from ally side, clears unit.songs
        battle.CancelDance(targetStatus)   # 0x43c600: strips unit.dances IDs from opposing side, clears unit.dances
        battle.CancelPuppet(targetStatus)  # 0x43c9b0: calls 0x43f210, strips unit.puppets IDs from self, clears unit.puppets
        battle.CancelGeass(targetStatus)   # 0x43ce30: strips unit.geass IDs from opposing side, clears unit.geass
```

**Program Evidence:**
```text
0044d023  movss    xmm1, dword ptr [ebp + 0x10]
0044d028  sub      esp, 8
0044d02b  addss    xmm1, dword ptr [0x6d938c]    ; float 1
0044d033  movd     xmm0, eax
0044d037  cvtdq2ps xmm0, xmm0
0044d03a  mulss    xmm0, dword ptr [0x6d93bc]    ; float 1.5
0044d042  addss    xmm0, xmm1
0044d046  movss    xmm1, dword ptr [ebp + 0xc]
0044d04b  divss    xmm1, xmm0
0044d04f  xorps    xmm0, xmm0
0044d052  maxss    xmm0, xmm1
0044d056  movss    xmm1, dword ptr [0x6d9384]    ; float 0.95
0044d05e  minss    xmm1, xmm0
0044d228  cmp      byte ptr [eax + 0x31], 0
0044d22c  je       0x44d24a
0044d22e  mov      ecx, 0x64
0044d233  call     0x505ac0
0044d238  cmp      eax, 0x21
0044d23b  jge      0x44d24a
0044d23d  push     0
0044d23f  mov      ecx, esi
0044d241  call     0x428560
0044d246  or       byte ptr [eax + 0x33], 1
0044f12a  mov      eax, dword ptr [edi]
0044f12c  cmp      byte ptr [eax + 0x31], 0
0044f130  je       0x44f14a
0044f132  mov      ecx, dword ptr [0x816ce8]
0044f138  push     0x64
0044f13a  call     0x490790
0044f13f  cmp      eax, 0x21
0044f142  jge      0x44f14a
0044f144  mov      eax, dword ptr [edi]
0044f146  mov      byte ptr [eax + 0x33], 1
0047ea83  cmp      byte ptr [ebx + 0x33], 0
0047ea87  je       0x47eac3
0047ea97  call     0x43bc50
0047eaa0  call     0x43c110
0047eaa9  call     0x43c600
0047eab2  call     0x43c9b0
0047eabb  call     0x43ce30
```

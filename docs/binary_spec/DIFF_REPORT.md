# Phase 2 — Two-Way Global Diff & Architectural Triage (`DT22_en_unwrapped.vanilla.exe`)

> **Machine-Verified Binary Diff (`140` Clean-Room Rules `M00.01..M11.15` + `6` Mechanical Reverse-Sweep `ENGINE-ONLY` Items)**
> Verified by `python tools/audit_check.py --diff docs/binary_spec/DIFF_REPORT.md`. Structured ledger: `docs/binary_spec/DIFF_TABLE.json`.

## Executive Summary

| Verdict | Rule Count | Description |
|---|---:|---|
| `S0` | 29 | Fundamental / architectural discrepancy (pipeline, state machine, vtable lifecycle, data export, AI VM) |
| `S1` | 75 | Active combat or loader bug firing on vanilla `pck_usage` skills/attacks/enemies/items/equipment |
| `S2` | 15 | Rare / narrow multi-condition or low-reach edge case |
| `ENGINE-ONLY` | 6 | Unbacked engine/simulator proxy or invented mechanic from mechanical reverse sweep |
| `MATCH` | 19 | 100% faithful to vanilla binary |
| `MODEL-LIMIT` | 2 | Documented Section 2 out-of-scope system |
| **Total Items** | **146** | **Enumerated sub-bugs: 282** (`S0=36`, `S1=174`, `S2=72`, `ENGINE-ONLY=0`) |

## Module Breakdown

| Module | MATCH | S0 | S1 | S2 | MODEL-LIMIT | ENGINE-ONLY |
|---|---:|---:|---:|---:|---:|---:|
| `M00` | 0 | 5 | 4 | 0 | 0 | 0 |
| `M01` | 1 | 2 | 3 | 1 | 0 | 0 |
| `M02` | 0 | 0 | 7 | 0 | 0 | 0 |
| `M03` | 0 | 0 | 4 | 1 | 0 | 0 |
| `M04` | 2 | 4 | 9 | 1 | 0 | 0 |
| `M05` | 2 | 1 | 10 | 0 | 0 | 0 |
| `M06` | 1 | 3 | 2 | 2 | 0 | 0 |
| `M07` | 1 | 3 | 8 | 0 | 0 | 0 |
| `M08` | 0 | 5 | 8 | 1 | 0 | 0 |
| `M09` | 5 | 3 | 5 | 1 | 1 | 0 |
| `M10` | 4 | 3 | 7 | 5 | 0 | 0 |
| `M11` | 3 | 0 | 8 | 3 | 1 | 0 |
| `REVERSE` | 0 | 0 | 0 | 0 | 0 | 6 |

## Global S0 Architectural Triage (Fix First in Phase 3)

| Rule ID | Title | Key S0 Sub-Bugs |
|---|---|---|
| `M00.02` | Outer CBattleBase::Update State Machine | M00.02a: Dolls (2000..2999), Summons, and Guests (3000..3999) execute the full inner Turn-Start States 0..24 instead of; M00.02b: Outer State 12 Warning Shot (259) 0.3x physical attack execution is absent; turn is unconditionally cancelled  |
| `M00.03` | Inner Turn-Start State Machine | M00.03a: Systematic Turn-Start state ordering violations: State 3 (446) and States 12..15 (319/357/350/448) are moved i |
| `M00.04` | Action Selection, Legality Gate & _CreatePattern Dispatch | M00.04a: Skill pattern IDs (Trailer[4], 14 distinct values) and EnemyAttack+0x90 (8 distinct values, including 55 uses ; M00.04b: No centralized Battle.IsLegalAction() gate in Battle.Turn() (NextAction checks only Silence 117 and Freeze 114 |
| `M00.06` | Hit -> Crit -> Damage -> Barrier -> TakeDamage -> Interrupt Hand-off | M00.06a: Material Guard (179 / 0xb3) and Magic Barrier (183 / 0xb7) are NEVER consumed on hit in Battle.cs, whereas CAc |
| `M00.08` | Post-Action Resolution, Status Add (0x4f9930), Death/Revive/Fall, Extra-Turn Rolls, Doll Life Tick & _SetTime | M00.08a: Heretic Samsara (291) executes at Turn-Start instead of Post-Action (0x438e50) and re-checks live < 50% HP ins |
| `M01.02` | Outer CBattleBase::Update (0x4397e0, States 0..15), Win/Loss/Escape Checks, Doll/Summon/Guest Skip, and Summon/Guest Samba 199 Tick | M01.02a: Dolls, Summons, and Guests execute the full inner Turn-Start States 0..24 instead of skipping (Dolls) or runni; M01.02b: Outer State 12 (0x439584) Warning Shot (259) 0.3x physical attack execution is absent; turn is unconditionally |
| `M01.03` | Inner Turn-Start 25-State Machine (0x439820, States 0..24) | M01.03a: Turn-Start state ordering diverges from States 0..24: State 3 (446) and States 12..15 (319/357/350/448) run in |
| `M04.06` | Master Target Pool Collector, Liveness Predicate & Unit-Type Filtering (0x43e6d0, 0x43b580) | M04.06a: Battle.Build and Battle.TargetableArray check only u.Alive (Hp > 0) instead of vtable+0xe8 (!IsDead && !IsFull |
| `M04.08` | Player Menu Target Selection & Item Scopes (CBattleMenuSelectTarget 0x456ff0, TargetTypes 0..18) | M04.08a: Systemic data-pipeline omission: ItemData w_0x5c (targetType 16 Single / 17 Row / 18 SideAll) and Flags_0x18 ( |
| `M04.09` | Enemy Action Target Selection, Mid-Action Retarget Fallback & Splash (137) | M04.09a: Battle.Perform completely lacks mid-action retarget fallback (CActionPatternBase::_SelectTarget 0x420560..0x42 |
| `M04.15` | Battle Skill, Item & Command Legality Gate (0x455bc0, 0x4fd250, 0x515f7c, 0x455e60) | M04.15a: No centralized Battle.IsLegalAction(Action) gate is asserted in Battle.Turn, and Shadow Sew (123, 0x455d94) is |
| `M05.07` | CBattleBase::End Party Recovery (272, 273, 353, E193, E194) & ClearBattleStatuses (vtable+0x70) | M05.07a: Scenario.PlayRun calls unit.ClearStatuses() unconditionally before every battle in a chain, wiping all true ai |
| `M06.01` | CGameStatusBase::AddStatus, Removal, and Status Wipe | M06.01a: Units.cs:212 SetStatus has no Stage-3 Petrification guard (0x4f9950 vt+0xc8), allowing buffs, debuffs, songs, ; M06.01b: Sleep (116) application in Battle.cs:3024 never strips active statuses with vtable+0x8c (IsSleepCleared, 36 co |
| `M06.02` | CCommand Vtable Boolean Flag Matrix (All 328 Instantiated IDs) | M06.02a: CommandData.pck flags38 bit 1 (+0x8c IsSleepCleared, 36 IDs) and bit 2 (+0x90 ClearOnDeath, 8 exempt IDs) are  |
| `M06.08` | Performance Groups: Songs, Dances, Puppets, Geass, Bonuses, Ticks & Cancellation | M06.08a: PerformSong and PerformGeass track performance slots by skill Name string instead of cmdId and never erase cmd |
| `M07.06` | Gradual & Instant Petrification Lifecycle (120, 121) | M07.06a: Battle.LostTurnHard skips Stage-3 Petrified enemies instead of defeating/removing them via CBattleBase::_SetDe |
| `M07.08` | Crowd-Control Turn-Start Gates & Action Restrictions (113-118, 120, 122, 123, 203, 259, 283) | M07.08a: Battle.LostTurnSoft omits Warning Shot (259) opponent 0.3x confused basic attack (0x436d60, PhaseNo = 12) and ; M07.08b: Shadow Sew (123, 0x455d94) does not block player skills in Policy.ComputeOptions or Battle.NextAction.; M07.08c: Stage-3 Petrified enemies are not defeated at Inner State 5 (Battle.cs:1020). |
| `M07.09` | Sleep Combat Modifiers & Wake-on-Hit (116 / 0x74) | M07.09a: Sleep (116) application in Battle.cs:3024 fails to strip the 36 vtable+0x8c statuses (0x4fa056). |
| `M08.04` | Defensive Procs Inside _Task (Parry 180, Counter 250, Knock Down 305, Pretend 310) | M08.04a: Counter 250 (Mind's Eye) branches on pattern flag10 (0x422640..0x422656): sequential patterns (A/B/C/T0105/M01 |
| `M08.06` | _CheckAfterAttackInterrupt 4-Stage Post-Action Chain (250, 249, 447, 260) | M08.06a: Stage 2 Deferred Counter 250 (which suppresses Stages 3 & 4) is missing, AND Stage 4 Arcane Shield 447 (Battle |
| `M08.08` | CActionPattern* Factory & Dispatch Table (Skill Trailer[4] & EnemyAttack+0x90) | M08.08a: pattern (Skill Trailer[4] and EnemyAttack+0x90) is not parsed for EnemyAttack in gamedata/data.py:213-234, is  |
| `M08.09` | Standard Multi-Hit & AoE Patterns (A..G, T0105, M0124, M0140) | M08.09a: Patterns A/B/C/G re-select a new living target via _SelectTarget when the current target dies mid-multi-hit; B; M08.09b: CActionPatternM0124 (case 13, Magic 230 Primevil, 0x42d1d0) rotates self-slot last in target order (unimplemen |
| `M08.13` | Turn-Start Auto-Trigger State Machine (TurnPhaseNo 0..24) | M08.13a: Overstock Clearance 446 (TurnPhaseNo 3), Murder License 319 (12), Tranquil 357 (13), Usurper of Souls 350 (14) |
| `M09.03` | Doll Stat Snapshot, Enchant Inheritance, TP=9999 & Post-Hit Exclusions | M09.03a: UnitFactory.BuildDoll (Units.cs:903-939) leaves unit.Enchants = NoEnchants instead of copying owner.Enchants ( |
| `M09.04` | Doll Turn Execution, TurnPhaseNo Skip, Life Decrement & Shadow Sew Destruction | M09.04a: Battle.cs:838-900 executes full TurnPhaseNo 0..24 for Kind.Doll instead of skipping directly to action executi |
| `M09.15` | Master Reference Table of All 280 Enchants (0..305) | M09.15a: Systemic Doll enchant drop (M09.03a): UnitFactory.BuildDoll (Units.cs:903-939) omits owner.Enchants, silently  |
| `M10.04` | AI Condition Opcodes (0..15) & Stop Flag Semantics | M10.04a: Passes() for comparison opcodes 3, 4, 10, 11, 12, 13, 14 (Ai.cs:171-184) NEVER checks v != -1 because SourceVa |
| `M10.14` | EnemyAttackData.pck Binary Layout (incl. +0x90 Pattern ID) | M10.14a: tools/extract_vanilla.py:477 dumps 0x88..0xA0 (including pattern at +0x90) only as an opaque Trailer CSV strin |
| `M10.15` | Skill .pck Binary Layouts (Technique, Magic, Passive, Unique & Trailer[4]) | M10.15a: tools/engine_export.py:43-53 omits Trailer[4] (pattern) from skill_json(), dropping CActionPattern* dispatch f |

## Part: M00–M03 (Pipeline, Turn Loop, Physical & Magical Damage)


> **Scope:** 28 binary spec rules (`M00.01..M00.09`, `M01.01..M01.07`, `M02.01..M02.07`, `M03.01..M03.05`) compared against `engine_cs/src/DtEngine/` (`Battle.cs`, `Formulas.cs`, `Action.cs`, `Units.cs`, `Data.cs`, `Loader.cs`, `Policy.cs`, `Scenario.cs`), `tools/engine_export.py`, `tools/character_data.py`, `gamedata/data.py`, `gamedata/progression.py`, and `gamedata/variant.py`.
> **Summary Counts:** `28` rules total — `1 MATCH`, `7 S0`, `18 S1`, `2 S2`, `0 MODEL-LIMIT` (out-of-scope Joint/Party/Escape sub-clauses noted inline). Intentional mod patches `X13`, `X14`, `X16`, `X17` verified in both vanilla and patched modes.

---

## M00 — Combat Pipeline Spine (`M00.01` – `M00.09`)

### M00.01 Battle Initialization & Start

**Verdict:** S1

```asm
00449316  cmp      byte ptr [ebx + 0x33], 0
0044931a  jne      0x449375
00449329  cmp      eax, 0x14
0043a21c  mov      dword ptr [ebx + 0xc], ecx
0043e55e  mulss    xmm0, dword ptr [0x6d96b0]    ; float 1000
0043e566  cvttss2si eax, xmm0
00440b69  call     0x61e650
```

- **Sub-bugs:**
  - **`M00.01a` (`S1`) — `noTurnJitterFlag` (`[this+0x33]`, enemy `0x3C` bit 1) does not suppress 20% random order scramble:** At `0x449316`, `noTurnJitterFlag != 0` skips the 20% battle-start order scramble (present on `105` enemies in vanilla `pck_usage`, including bosses). `Battle.Start()` gates Summon/Guest initial gauge on `!flagged` but omits `&& !flagged` on the 20% scramble. Fix: add `&& !flagged` to the `RANDOM_ORDER` guard.
  - **`M00.01b` (`S1`) — First Grid (`300`) scans dead/petrified units and non-candidates (`>= 2000`):** At `0x449375..0x44949e`, `300` iterates only living, non-petrified, non-Doll/Summon/Guest units (`CollectUnits(aliveOnly=1, includeDolls=0)`). `Battle.Start()` iterates all `Units`, so a dead member in a multi-battle chain can proc `300` and `break`. Fix: filter `CanFight(u) && !NotACandidate(u)`.
  - **`M00.01c` (`S1`) — Missing `_SortTime` `1/1000` gauge quantization and inverted Doll `TieKey`:** Binary sorts by `trunc0(gauge * 1000.0f) * 1000 + sortTiebreak` (`0x440b5c..0x440b88`, where `0x61e650` is `__ftoui3` `trunc0`), normalizes `headGauge = trunc0(gauge * 1000.0f) / 1000.0f` (`0x43e551..0x43e566`), and assigns Dolls `sortTiebreak = 962..1` (`0x43a21c`, above Summon `930` and Guest `929`). `Battle.cs` uses unquantized `double NextTime` and negative Doll `TieKey = -unit.Position`. Fix: quantize sort/normalization to `1/1000` ticks and initialize a per-battle Doll tiebreak counter at `962` decrementing per spawn.

`engine_cs/src/DtEngine/Battle.cs:600`
```csharp
                u.TieKey = u.Kind == Kind.Member ? 999 - members++ : u.Kind == Kind.Enemy ? 994 - enemies++
                         : u.Kind == Kind.Summon ? (u.IsGuest ? 929 : 930) : -u.Position;
...
            if (!ambush && Rng.RandRange(100) < RANDOM_ORDER)
                foreach (var u in Units) u.NextTime = 1.0 - Rng.RandRange(93) / 100.0;
            // 0x4491f2..0x44949e: Preemptive Strike (300) is skipped after an ambush and stops after the first unit that procs.
            if (!ambush)
            {
                foreach (var u in Units)
                    if (u.Has(300) && Roll(u.Value(300))) { u.NextTime = 0.0; break; }
            }
```

---

### M00.02 Outer `CBattleBase::Update` State Machine

**Verdict:** S0

```asm
00436254  jmp      dword ptr [eax*4 + 0x4397e0]
004365ff  mov      eax, dword ptr [esi + 0xb0]
00436607  jne      0x43875a
0043660d  mov      eax, dword ptr [esi + 4]
00436610  cmp      eax, 0x7d0
00436626  jne      0x43875a
00436642  jne      0x43875a
004395b6  call     0x43b580
004395cb  cmp      dword ptr [esi + 0x10], 0
004395cf  jge      0x4395f3
```

- **Sub-bugs:**
  - **`M00.02a` (`S0`) — Dolls (`2000..2999`), Summons, and Guests (`3000..3999`) do NOT skip inner Turn-Start States `0..24`:** Binary `0x436322..0x43664d` skips the entire 25-state inner machine for Dolls (no `vtable+0xdc` tick) and runs only dedicated Samba `199` + `vtable+0xdc` (`0x43875a`) for Summons/Guests. `Battle.Turn()` executes the entire `if (!extraTurn)` turn-start pipeline (including opponent `345`/`259`/`283`, regen, poison, and same-side `355` Undaunted revives) on every Doll, Summon, and Guest turn! Active in virtually all battles with Summons, Guests, or Dolls. Fix: branch in `Battle.Turn()` on `unit.Kind == Kind.Doll` (skip turn-start completely) and `unit.Kind == Kind.Summon || unit.Kind == Kind.Npc` (run only Samba `199` + `DecrementTimedStatuses`).
  - **`M00.02b` (`S0`) — Outer State 12 (`0x439584`) Warning Shot (`259`) attack execution is completely absent:** Binary executes an actual `0.3x` physical attack (`[u+0x105] = 1`) against `actor` and cancels `actor`'s turn ONLY if the shot lands and deals HP damage (`0x4395bf..0x4395cf`), resetting `TurnPhaseNo = 0` (skipping States `10..24`). `Battle.LostTurnSoft()` never performs the attack, unconditionally denies the turn (`Lost.Empty`), and still runs `TickRegenAndDances` and `Undaunted`. Reach: `259` has `4` uses (`Passive: 1, EnemyAttack: 3`). Fix: perform the `0.3x` physical attack via `Perform`/`Resolve` and cancel the turn (skipping States `10..24`) only on landed HP damage.
  - **`M00.02c` (`S1`) — Stage-3 Petrified enemies are never defeated/removed (`PhaseNo = 15`, `0x4396d0`) and Enemy Dolls are counted in `Over()`:** Binary defeats and removes Stage-3 petrified enemies (`0x436c3f -> 0x4396d0`), and `GetAliveEnemyCount` (`0x43b510 -> 0x43e6d0`) excludes Enemy Dolls (`unitId >= 2000`). `Battle.CompletePetrify()` leaves Stage-3 petrified enemies `Alive = true` so `TargetableArray(ENEMIES)` keeps targeting them, and `Battle.Over()` counts Enemy Dolls (`u.Side == Unit.ENEMIES`). Fix: defeat/remove Stage-3 petrified enemies (`Alive = false`, clear statuses/dolls) and exclude `Kind.Doll` in `Over()`.

`engine_cs/src/DtEngine/Battle.cs:535`
```csharp
                if (u.Side == Unit.ENEMIES) enemies = true;
...
            if (!extraTurn)
            {
...
                if (other.Has(259) && Roll(other.Value(259))) return Deny(unit, Lost.Empty);
```

---

### M00.03 Inner Turn-Start State Machine

**Verdict:** S0

```asm
00436700  mov      eax, dword ptr [edi + 0x20]
00436703  cmp      eax, 0x18
0043670c  jmp      dword ptr [eax*4 + 0x439820]
00436d27  cmp      eax, 0x1e
0048d1bc  mov      eax, dword ptr [esi]
0048d1c0  mov      eax, dword ptr [eax + 0xbc]
0048d1d0  mov      eax, dword ptr [eax + 0x8c]
0048d1da  jne      0x48d2f4
```

- **Sub-bugs:**
  - **`M00.03a` (`S0`) — Systematic state-ordering divergence across States `0..24`:**
    1. State `3` (`446` Overstock Clearance, `0x436a9b`) runs BEFORE Petrification/Sleep/Paralysis (`States 4..7`) in binary, but is placed in `BeforeAction()` (`Battle.cs:909, 934`) AFTER Hard/Soft CC, Regen, and Undaunted.
    2. States `12..15` (`319` Murder License, `357` Tranquil Song, `350` Usurper of Souls, `448` Shadow Heart) run BEFORE States `16..22` (Regen/Dances/Poison/Undaunted) in binary, but run AFTER them in `BeforeAction()` (`Battle.cs:909`).
    3. Heretic Samsara (`291`, `0x438e50`) is Post-Action in binary, but runs at Turn-Start (`Battle.cs:850`).
    4. State `22` (`355` Undaunted Spirit, `Battle.cs:899`) still executes after `softLost` (`259`/`283`/`203`), whereas binary branches to `PhaseNo = 4` / `TurnPhaseNo = 0` and skips States `12..24`.
  - **`M00.03b` (`S1`) — States `9` (`259`) and `10` (`283`) are interleaved and include Dolls:** Binary finishes all `oppPlusSummons` checks for `259` in State `9` before checking `283` in State `10`, and excludes Dolls; `Battle.LostTurnSoft()` checks both inside one `OpponentsArray(unit)` loop and omits `259`'s attack.
  - **`M00.03c` (`S1`) — State `1` (`RollAilmentRecovery`) omits Sleep-decay check (`0x48d1bc..0x48d1da`):** Binary removes ailments with `vtable+0x8c() == true` immediately when `actor.IsAsleep()`; `Battle.RollAilmentRecovery()` omits this check.
  - **`M00.03d` (`S2`) — Minor state fidelity gaps:** State `2` (`345` Third Eye Wide, `Battle.cs:857`) does not `break` on first proc and scans Dolls/Summons/Guests/petrified units (X16 `ThirdEyeDispel` matches both vanilla and Balance modes); State `13` (`357`, `Battle.cs:943`) debuffs Dolls/Summons/Guests; States `18..20` tick `199->339->200->204` instead of `200->204->199/339`; State `22` (`355`, `Battle.cs:1005`) calls `Wait(u)` instead of keeping frozen gauge + `_SortTime(1, 1)`.

`engine_cs/src/DtEngine/Battle.cs:785`
```csharp
                if (!IsAilment[effect] || effect == 118 || effect == 119 || effect == 120 || effect == 123) continue;
...
                if (unit.Alive && softLost != Lost.Skip) TickRegenAndDances(unit);
                if (!unit.Alive) return;
                // Inner State 22 (0x43851e): Undaunted (355) runs on a living unit's turn for dead members on the same side.
                Undaunted(unit.Side);
            }
...
            if (softLost == Lost.No && unit.Alive)
            {
                BeforeAction(unit);
```

---

### M00.04 Action Selection, Legality Gate & `_CreatePattern` Dispatch

**Verdict:** S0

```asm
004f4917  lea      esi, [edx + 1]
004f491a  cmp      esi, 0x14
004f4923  jmp      dword ptr [esi*4 + 0x4f4bdc]
0041a4ed  mov      ecx, dword ptr [eax + 0xa8]
0041a503  jmp      dword ptr [eax*4 + 0x41a814]
0041e098  call     0x56d450
0041e0a6  jmp      dword ptr [eax*4 + 0x41e5fc]
004180e3  mov      dword ptr [ebx + 0x40], 1
```

- **Sub-bugs:**
  - **`M00.04a` (`S0`) — Pattern IDs (`Trailer[4]` / `EnemyAttack+0x90`) are not exported to C# and no `CActionPattern*` dispatch exists:** `tools/engine_export.py:43-62` omits `Skill.pattern` (`14` distinct patterns in vanilla `pck_usage`: `0, 1, 3, 4, 6..15`) and `EnemyAttack+0x90` (`8` distinct values `-1, 0..6`, including `55` uses of pattern `6` `E1630`). `Battle.Perform()` reconstructs behavior heuristically from effect IDs instead of dispatching patterns. (`CActionJoinAttack` `0x41c970` is `MODEL-LIMIT` per Section 2.) Fix: export `pattern` for both `Skill` and `EnemyAttack` and dispatch pattern-specific behaviors in `Battle.Perform()`.
  - **`M00.04b` (`S0`) — No centralized `Battle.IsLegalAction()` gate in `Battle.Turn()` and `Policy.WeaponAllows()` omits codes `17`/`18`:** `Battle.NextAction()` (`Battle.cs:1049-1054`) checks only Silence (`117`) and Freeze (`114`), relying on `Policy.Options` for TP, `UsableInBattle`, `WeaponAllows`, and `NoMagic`. Additionally, `CheckSkillCondition` (`0x4f4910`, `0x4f4bdc`) supports codes `17` (Head slot equipped) and `18` (Body slot equipped), which are missing from `Policy.WeaponAllows()` (`0` vanilla skills use `17`/`18`, S2 sub-part). Fix: add `Battle.IsLegalAction(action)` asserted on `Policy.Choose` inside `Battle.Turn()`, and add cases `17`/`18` to `WeaponAllows`.
  - **`M00.04c` (`S1`) — `SetHitCount` (`0x417cd0`) lower clamp breaks Effect `94` (`0~4 Hits`):** `Battle.NumberOfHits()` clamps `Math.Max(1, hits)`, eliminating the 10% `0`-hit outcome of Effect `94` (`18` uses in vanilla `pck_usage`). Fix: return `hits` unclamped when `any` is true.

`tools/engine_export.py:43`
```python
def skill_json(s):
    return {
        'category': s.category, 'id': s.id, 'name': s.name, 'levels': whole(s.levels, 'levels'), 'target': s.target,
        'attr': s.attr, 'group': s.group, 'weapons': list(s.weapons or []),
...
        'turns': list(s.turns), 'classes': list(s.classes or []), 'range': s.range, 'chant_stat': s.chant_stat,
        'swing': s.swing or 0.0,
    }
```

`engine_cs/src/DtEngine/Policy.cs:216`
```csharp
        public static bool WeaponAllows(Piece weapon, bool shield, Skill skill)
        {
            if (skill.Weapons.Length == 0) return true;
            foreach (int code in skill.Weapons)
            {
                if (code == -1) return true;
                if (code == 0 && weapon != null && weapon.Range == 0) return true;
                if (code == 15 && weapon != null && weapon.Type >= 14 && weapon.Type <= 20) return true;
                if (code == 16 && shield) return true;
                if (code == 19 && weapon != null) return true;
                if (code >= 1 && code <= 14 && weapon != null && weapon.Type + 1 == code) return true;
            }
            return false;
        }
```

---

### M00.05 Target Resolution & Cover/Provoke/Redirect Hand-off

**Verdict:** S1

```asm
0044a6ca  mov      eax, dword ptr [edi + 0x74]
0044a6e1  push     0xaa
0044a757  cmp      ecx, 0xa
004203b4  push     0x133
004203fd  push     0x12f
00420c48  push     0xab
00420ca7  call     0x490790
```

- **Sub-bugs:**
  - **`M00.05a` (`S1`) — Auto-Guard (`255`) is rolled before Cover (`171`) redirect:** `Battle.Perform()` rolls `255` for original `targets` at lines `1330-1340`, before `Resolve()` calls `Redirect()` (Cover `171`) at line `1756`. A covering ally bearing `255` therefore never receives its Auto-Guard roll when covering a single-target/random physical hit. Fix: evaluate Auto-Guard (`255`) on the post-Cover target (once per unique final target per action).
  - **`M00.05b` (`S1`) — Multi-hit loop aborts on target death instead of re-selecting via `_SelectTarget` (`0x420560`):** Binary `_SelectTarget` checks target liveness before each hit (`0x43b580`) and re-selects a living enemy on `TargetType` `0..6` if the previous target died. `Battle.Perform()` breaks out of `for (int h = 0; h < hits; h++)` when `!target.Alive`, wasting remaining hits of single-target multi-hit attacks. Fix: re-pick a living target via `PickOpponent` on remaining hits when `target` dies.
  - **`M00.05c` (`S1`) — `Redirect()` does not exclude Stage-3 Petrified coverers, and Counter Whip (`303`) does not gate remaining hits on Sleep (`116`):** `TargetableArray(target.Side)` checks `u.Alive` only (not `CanFight(u)`), allowing Stage-3 petrified allies to cover; if Counter Whip (`303`) inflicts Sleep (`116`) via weapon enchant, `Battle.Perform()` only checks `!unit.Alive` and proceeds with the attack. (Note: `CBattle::_UpdateTargetRate` `0x44a630` matches `Battle.WeightedPick` + `F.TargetWeight`, and direct disassembly of `0x422b58` confirms `0x422b58` is `179`/`183` hit-consumption rather than magic cover.)

`engine_cs/src/DtEngine/Battle.cs:1330`
```csharp
            if (action.Physical)
            {
                for (int j = 0; j < targets.Length; j++)
                {
...
                    if (t.Side != unit.Side && t.Has(255) && Roll(t.Value(255))) guarding.Add(t);
                }
            }
...
                for (int h = 0; h < hits; h++)
                {
                    if (!unit.Alive || (!target.Alive && !action.Has(105))) break;
                    Resolve(action, target, index);
```

---

### M00.06 Hit -> Crit -> Damage -> Barrier -> TakeDamage -> Interrupt Hand-off

**Verdict:** S0

```asm
0044a9e1  call     0x43e970
0043e9d8  fadd     dword ptr [esp + 0x10]
00422b58  cmp      byte ptr [esi + 0x79], 0
00422b62  push     0xb3
00422b69  push     0xb7
00422b6e  call     dword ptr [eax + 0x64]
00421b58  mov      byte ptr [ebx + 0x38], 1
00423233  call     0x47e500
```

- **Sub-bugs:**
  - **`M00.06a` (`S0`) — Material Guard (`179` / `0xb3`) and Magic Barrier (`183` / `0xb7`) are NEVER consumed on hit:** Disassembly of `CActionPatternBase::_Task` at `0x422b58..0x422b6e` proves every non-voided physical hit removes status `179` and every non-voided magical hit removes status `183` via `target->vt+0x64` (`0x4fa630`). `Battle.cs` reads `target.St[179]` and `target.StatusValue(183)` without ever popping them, making both buffs last their entire 3–7 turn duration across unlimited hits (`179`: `10` uses; `183`: `2` player skills `Spell Guard` & `Magic Barrier`). Fix: pop `179` after a non-voided physical hit and pop `183` after a non-voided magical hit.
  - **`M00.06b` (`S1`) — Missing `0x43e970` command-merge summation drops active status buffs `26` and `31`:** Both `CalcPhysicalAttack` (`0x44a9e1`) and `CalcMagicalAttack` (`0x44d56c`) sum duplicate command IDs across action + actor statuses/passives via `0x43e970`. `Battle.cs:2098` (`First(action, unit, 26)`) and `Battle.cs:1970` (`AddFirst(..., 31)`) discard `unit.St[26]` (Berserk/Defender/High Risk, High Return) on all `58` Techniques with Effect `26`, and discard `unit.St[31]` (Last Stand) on `Moonlight Purgatory` and `Divine Cannon`. Fix: sum `action.Val(e)` + `unit.Value(e)` for merged command IDs (`26`, `31`, `27`, `173`, etc.).
  - **`M00.06c` (`S1`) — Effect `87` (`Only Damages Living`) fails to void `AfterHit`/Murder `258` and misses party member `Ist` (`race=6`):** Returns `0` inside `DamageInner` instead of setting `isVoided`, and `Units.cs:724` sets `Race = T.NONE` for all party members.
  - **`M00.06d` (`S1`) — `Voided()` applies physical blocks `182`/`250` to `19` short/mid-range enemy Magic attacks (`Pink Typhoon`, `Solvent`, `Feel'n Woozy`), Endure `254` clamps damage before `Interrupt`, and duplicate zone slots square `f.Element`.**

`engine_cs/src/DtEngine/Battle.cs:2098`
```csharp
            double modifiers = First(action, unit, 26) + (action.Atk != null ? action.Atk.Power : 0.0) + SumStatus(unit, ATTACK_STATUS_MODIFIERS);
...
            var guard = target.St[MATERIAL_GUARD];
            if (guard != null && (guard.Source == null || (guard.Source.Alive && guard.Source.Shield))) other += guard.Value;
...
            double cut = (target.HasEnchants ? Math.Max(-0.25, -(0.10 * target.Pieces(68) + 0.05 * target.Pieces(69) + 0.08 * target.Pieces(70) + 0.04 * target.Pieces(71))) : 0.0) + target.StatusValue(183);
```

---

### M00.07 `AfterHit` Reactive Chain

**Verdict:** S1

```asm
00423683  add      eax, esi
00423688  mov      dword ptr [ecx + 0x1c], eax
004237e6  call     0x423810
00424319  push     0x125
0042467f  cmp      byte ptr [ebx + 0x11], 0
004246b0  mov      al, byte ptr [eax + 0x79]
004246b5  je       0x424714
00424728  cmp      byte ptr [ebx + 0x78], 0
0042472c  jne      0x424771
00424766  cmp      eax, 0xf
```

- **Sub-bugs:**
  - **`M00.07a` (`S1`) — Reprisal (`249`) omits `target.Front` and `!inCounter` guards:** Binary `0x42467f..0x4246b5` requires `!this.inCounter` and `target.isFrontRow != 0` (`[eax+0x79]`). `Battle.cs:2897` omits both checks, allowing back-row units with `249` to counter-attack (`249` has `4` uses: `Passive: 1, EnemyAttack: 3`). Fix: add `&& !inCounter && target.Front`.
  - **`M00.07b` (`S1`) — Arcane Shield (`447`) omits `!action.IsSpecial` guard (vanilla 15% & X13 25%):** Disassembly at `0x422c87..0x422c97` and `0x424728` shows `[ebx+0x78]` is `lastHitWasSpecialDmg`, suppressing Arcane Shield on special/fixed damage (`8, 12, 134, 138, 140..142, 434, 435`). `Battle.cs:2579` omits `!action.IsSpecial`, reflecting special damage in both vanilla and X13 modes. Fix: add `&& (action == null || !action.IsSpecial)`.
  - **`M00.07c` (`S1`) — Devil's Whisper (`320`) runs after `TakeDamage` instead of before Endure (`254`):** Binary `_AfterHit1` (`0x423560..0x423688`) adds bonus lethal damage into `res.hpDamage` BEFORE `_AfterHit2` (`0x423810`, Endure `254`). `Battle.cs:2868` calls `ApplyAilment(..., 119, ...)` after `TakeDamage`, bypassing Endure `254` (`320`: `2` enemy attacks).
  - **`M00.07d` (`S1`) — Slow Target / Dark Aura (`293`) wrongly gated on `action.Reach == T.SHORT`:** Binary `0x424317..0x42436b` has no range check on `293` (`2` enemy attacks), whereas `Battle.cs:2889` requires `action.Reach == T.SHORT`. Fix: remove `action.Reach == T.SHORT` from the `293` check.
  - **`M00.07e` (`S1`) — Support Shot / Avenger (`260`) does not shuffle allies and fires even if primary target died:** Binary `0x4253ae..0x425821` requires the primary target to survive and shuffles allies before picking the first proc; `Battle.cs:1418-1428` scans in fixed `AlliesArray` order and falls back to `opp[0]`. (Note: `Options.SurvivalGuard` `L46` at `Battle.cs:2540` is an inactive trial hook, disabled in vanilla.)

`engine_cs/src/DtEngine/Battle.cs:2579`
```csharp
            if (!inCounter && target.Alive && target.HasUnique && target.UniqueEffect == 447 && unit != null && !NotACandidate(unit) && !unit.Has(307) && amount > 0)
...
                if (target.Has(293) && action.Reach == T.SHORT && Roll(target.Value(293)))
...
                if (target.Has(249) && action.Physical && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
```

---

### M00.08 Post-Action Resolution, Status Add (`0x4f9930`), Death/Revive/Fall, Extra-Turn Rolls, Doll Life Tick & `_SetTime`

**Verdict:** S0

```asm
004f9950  mov      eax, dword ptr [eax + 0xc8]
004f995a  jne      0x4fa5f9
00438e53  push     0x123
00438e7d  comiss   xmm0, dword ptr [0x6d938c]    ; float 1
0043903b  cmp      byte ptr [esi + 0x107], 0
00439052  cmp      esi, dword ptr [eax]
0043905f  mov      eax, dword ptr [eax + 0xbc]
0043915a  mov      dword ptr [esi + 0xb4], eax
```

- **Sub-bugs:**
  - **`M00.08a` (`S0`) — Heretic Samsara (`291`) executes at Turn-Start instead of Post-Action and re-checks live `< 50% HP`:** Binary latches `cmd291.val = 1.0f` when damaged (`0x47f775`) and re-rolls all 8 resistances (`416..423`) POST-ACTION (`0x438e50..0x438f20`). `Battle.cs:850-855` runs Samsara at Turn-Start and re-checks `unit.Hp < unit.MaxHp / 2.0`, missing post-action timing and failing if healed back above 50% before its turn. Fix: latch `SamsaraState` on `< 50% HP` damage and re-roll in `EndOfTurn()`.
  - **`M00.08b` (`S1`) — Extra-turn rolls (`288`/`289`/`354`) omit Sleep/head guards, cancel on Chant Start, and waste a `Wait()` RNG draw:** Binary `0x43903b..0x43915a` guards on `!grantedExtraTurn && actor == units[0] && !IsAsleep()` (no `Chant == null` check) and skips `_SetTime` when granting an extra turn. `Battle.cs:1110-1139` calls `Wait()` first (wasting an RNG draw), omits `!IsAsleep()` and head-unit check, and blocks extra turns on `unit.Chant != null` (destroying remaining Triple-Action extra turns). Fix: move `Wait()` after extra-turn check, add `unit.St[116] == null` and head-unit check, and allow extra turns to complete chants.
  - **`M00.08c` (`S1`) — `Unit.SetStatus()` omits `IsDead`/Stage-3 Petrified guard (`0x4f9950`):** Binary `AddStatus` immediately returns if `vtable+0xc8` (dead or Stage-3 petrified) is true; `Units.cs:212` has no guard. Fix: guard `SetStatus` (or callers) against dead/Stage-3 petrified targets (except initial `120` Stage-3 placement).
  - **`M00.08d` (`S1`) — Enemy Self-Destruct (`12`) and Escape (`11`) bypass `Fall()`, leaking Dolls and active songs/dances/geass:** `Battle.cs:1401-1407` and `2797-2801` set `unit.Alive = false` without destroying owned Dolls (`0x43d2c0`) or removing statuses cast by `unit` on other units. Fix: call shared cleanup (`EndParts(unit, PerfParts.All)` + remove owned Dolls + remove `SongKind` statuses sourced from `unit`).

`engine_cs/src/DtEngine/Battle.cs:850`
```csharp
                if (unit.SamsaraState != 0 && (unit.SamsaraState == 2 || unit.Hp < unit.MaxHp / 2.0))
...
            if (unit.Chant != null) wait = Wait(unit, unit.Chant, true);
            else wait = Wait(unit, last);
            unit.NextTime = Time + wait;
            if (unit.Extra > 0 && unit.Chant == null && !Over())
...
            else if (acted && unit.Chant == null && !Over())
```

`engine_cs/src/DtEngine/Units.cs:212`
```csharp
        public void SetStatus(Status s)
        {
            if (St == NoStatuses) St = RentStatusArray();
```

---

### M00.09 Battle End, After-Battle Recovery (`0x43d6a7`) & Rewards (EXP/Gold/Drops) Hand-off

**Verdict:** S1

```asm
0045073e  movss    xmm0, dword ptr [0x6d937c]    ; float 0.9
0045081b  call     0x61e650
004459bf  divss    xmm0, dword ptr [ebp - 0x18]
0043d6c2  call     edx
0043d6cc  push     0x110
0043d705  push     0x111
0043d751  movss    xmm0, dword ptr [0x6d9330]    ; float 0.3
0043d85e  push     0xc1
0043d904  push     0xc2
```

- **Sub-bugs:**
  - **`M00.09a` (`S1`) — `Scenario.RecoverAfterBattle()` includes Stage-3 Petrified members:** Binary `CBattleBase::End` (`0x43d6a7..0x43d99d`) filters both contributors (`272`/`273`/`353`) and recipients (`193`/`194`/fraction heal) by `m->vtable+0xe8()` (`IsAliveAndNotPetrified`). `Scenario.RecoverAfterBattle()` filters by `u.Alive && u.Kind == Kind.Member`, and `Scenario.PlayRun()` clears statuses only at the start of the NEXT battle (`Scenario.cs:1036`, after `RecoverAfterBattle` at line `1076`). A Stage-3 petrified member therefore wrongly contributes `272`/`273`/`353` and receives post-battle HP/TP recovery in multi-battle chains. Fix: check `u.Alive && !(u.St[120] != null && u.St[120].Stage >= 3) && u.Kind == Kind.Member`.
  - *(Verified matching: `gamedata/progression.py:14-39` EXP level-gap table `LEVEL_GAP`, `int(exp * mult)` matching `0x61e650` `__ftoui3`, alive split, status `157` x2, enchant `275` x2, and `Formulas.cs:373-390` `0.30` cap + `353` synergy + `193`/`194` full recovery + `max(1, trunc0(max*frac))`.)*

`engine_cs/src/DtEngine/Scenario.cs:1083`
```csharp
        public static void RecoverAfterBattle(List<Unit> party)
        {
            var living = party.Where(u => u.Alive && u.Kind == Kind.Member).ToList();
```

`gamedata/progression.py:14`
```python
LEVEL_GAP = ((10, None, 0.85, 0.85), (5, 9, 0.90, 0.90), (0, 4, 1.00, 1.00), (-4, -1, 1.00, 1.15),
             (-9, -5, 1.10, 1.30), (-19, -10, 1.25, 1.50), (None, -20, 1.25, 1.75))
```

---

## M01 — Turn Loop, ATB Gauge, Action/Chant Speed, and Interruption (`M01.01` – `M01.07`)

### M01.01 Battle Start Gauges, Random Order Jitter, Preemptive/Ambush (`321`/`268`/`267`), First Grid (`300`), and `_SortTime`

**Verdict:** S1

```asm
0044919a  push     0x1f4
004491b2  divss    xmm0, dword ptr [0x6d96b0]    ; float 1000
00449316  cmp      byte ptr [ebx + 0x33], 0
0044931a  jne      0x449375
00449329  cmp      eax, 0x14
0043e55e  mulss    xmm0, dword ptr [0x6d96b0]    ; float 1000
0043e566  cvttss2si eax, xmm0
00440b69  call     0x61e650
00440b85  mov      eax, dword ptr [eax + 0xc]
```

- **Sub-bugs:**
  - **`M01.01a` (`S1`) — `noTurnJitterFlag` (`0x3C` bit 1, `105` enemies) does not suppress the 20% random order scramble:** `Battle.Start()` (`Battle.cs:647`) checks `if (!ambush && Rng.RandRange(100) < RANDOM_ORDER)`, omitting `&& !flagged`. Fix: add `&& !flagged`.
  - **`M01.01b` (`S1`) — `_SortTime` quantization and Doll `TieKey` mismatch:** Binary quantizes sort keys to `trunc0(gauge * 1000.0f) * 1000 + sortTiebreak` (`0x440b5c..0x440b88`, `0x61e650` is `__ftoui3` `trunc0`), normalizes by `1.0f - trunc0(headGauge * 1000.0f) / 1000.0f` (`0x43e551..0x43e566`), and gives Dolls `sortTiebreak = 962..1` (`0x43a21c`, above Summon `930` / Guest `929`). `Battle.cs:494, 601, 692` uses unquantized `double NextTime` and Doll `TieKey = -unit.Position`. Fix: quantize gauge comparisons/normalization to `1/1000` steps and track a `dollSortCounter = 962` per battle.
  - **`M01.01c` (`S1`) — First Grid (`300`) does not exclude dead/petrified units or non-candidates:** `Battle.cs:652-653` scans all `Units` instead of living, non-petrified members followed by living non-Doll enemies (`0x449375..0x44949e`). Fix: filter `CanFight(u) && !NotACandidate(u)`.
  - **`M01.01d` (`S2`) — `Ambush` (`321`/`268`/`267`) RNG draw count and non-candidate filter:** Binary `0x43e870` (`FindCommandOnSide`) excludes Dolls/Summons/Guests and petrified players, and `0x44a45e` still draws `Rand(100)` when `certain` (`321`) is true (always passes `< 1000`). `Battle.cs:660-672` scans all `Units` and skips `Rand(100)` when `certain` is true.

`engine_cs/src/DtEngine/Battle.cs:646`
```csharp
            bool ambush = Ambush(Unit.PARTY) || Ambush(Unit.ENEMIES);
            if (!ambush && Rng.RandRange(100) < RANDOM_ORDER)
                foreach (var u in Units) u.NextTime = 1.0 - Rng.RandRange(93) / 100.0;
            // 0x4491f2..0x44949e: Preemptive Strike (300) is skipped after an ambush and stops after the first unit that procs.
            if (!ambush)
            {
                foreach (var u in Units)
                    if (u.Has(300) && Roll(u.Value(300))) { u.NextTime = 0.0; break; }
            }
```

---

### M01.02 Outer `CBattleBase::Update` (`0x4397e0`, States `0..15`), Win/Loss/Escape Checks, Doll/Summon/Guest Skip, and Summon/Guest Samba `199` Tick

**Verdict:** S0

```asm
00436314  mov      eax, dword ptr [esi + 0xb0]
0043631c  jne      0x43875a
0043660d  mov      eax, dword ptr [esi + 4]
00436610  cmp      eax, 0x7d0
00436617  cmp      eax, 0xbb8
00436626  jne      0x43875a
0043662c  cmp      eax, 0xbb8
00436633  cmp      eax, 0xfa0
00436642  jne      0x43875a
0043b554  call     0x43e6d0
```

- **Sub-bugs:**
  - **`M01.02a` (`S0`) — Dolls, Summons, and Guests run the full inner Turn-Start States `0..24` instead of skipping:** Binary `0x436322..0x43664d` skips States `0..24` for Dolls (`2000..2999`, also skipping `vtable+0xdc`) and for Summons/Guests (`3000..3999`, running ONLY Samba `199` + `vtable+0xdc` at `0x43875a`). `Battle.Turn()` (`Battle.cs:838-900`) runs the entire turn-start sequence (including opposing `345`/`259`/`283`, regen, poison, and `355` Undaunted revives) for Dolls, Summons, and Guests! Fix: separate Doll and Summon/Guest turn-start branches in `Battle.Turn()`.
  - **`M01.02b` (`S0`) — Outer State 12 (`0x439584`) Warning Shot (`259`) attack execution missing:** `Battle.LostTurnSoft()` (`Battle.cs:1030`) never executes the `0.3x` physical attack (`CActionAttack` / `CActionEnemyAttack`), always cancels the turn even when the shot would miss/void, and wrongly proceeds to `TickRegenAndDances` and `Undaunted`. Fix: execute the `0.3x` attack and cancel the turn (skipping States `10..24`) only if it deals HP damage.
  - **`M01.02c` (`S1`) — Stage-3 Petrified enemies remain `Alive` and targetable (`PhaseNo = 15`, `0x4396d0`) and `Over()` counts Enemy Dolls:** `Battle.CompletePetrify()` (`Battle.cs:813-827`) keeps `Alive = true` for enemies too, so `TargetableArray(ENEMIES)` (`Battle.cs:460`) still targets them; `Battle.Over()` (`Battle.cs:535`) counts Enemy Dolls (`u.Side == Unit.ENEMIES`) unlike `0x43b510`. Fix: remove/kill Stage-3 petrified enemies (`Alive = false`) and guard `u.Kind != Kind.Doll` in `Over()`.

`engine_cs/src/DtEngine/Battle.cs:836`
```csharp
            bool extraTurn = unit.ExtraTurn;
            Lost softLost = Lost.No;
            if (!extraTurn)
            {
...
                Undaunted(unit.Side);
            }
```

---

### M01.03 Inner Turn-Start 25-State Machine (`0x439820`, States `0..24`)

**Verdict:** S0

```asm
00436713  mov      byte ptr [esi + 0x105], 0
0043671a  mov      byte ptr [esi + 0x107], 0
0048d1c0  mov      eax, dword ptr [eax + 0xbc]
0048d1d0  mov      eax, dword ptr [eax + 0x8c]
0048d221  cmp      eax, ecx
00436d27  cmp      eax, 0x1e
00436d89  push     0x103
00482197  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
004821ff  cmovg    esi, eax
```

- **Sub-bugs:**
  - **`M01.03a` (`S0`) — Turn-start state execution order diverges from States `0..24`:**
    - State `3` (`446` Overstock Clearance) is executed in `BeforeAction()` (`Battle.cs:909, 934`) AFTER Hard/Soft CC (`States 4..11`), Regen (`State 16`), and Undaunted (`State 22`), so Sleeping/Paralyzed/Mesmerized units wrongly fail to proc `446`.
    - States `12..15` (`319` Murder License, `357` Tranquil Song, `350` Usurper of Souls, `448` Shadow Heart) are executed in `BeforeAction()` (`Battle.cs:909`) AFTER States `16..22` (Regen/Dances/Poison/Undaunted).
    - Heretic Samsara (`291`, Post-Action `0x438e50`) is placed at Turn-Start (`Battle.cs:850`).
    - State `22` (`355` Undaunted Spirit, `Battle.cs:899`) runs even after `softLost` (`259`/`283`/`203`), when binary branches to `PhaseNo = 4` / `TurnPhaseNo = 0` skipping States `12..24`.
  - **`M01.03b` (`S1`) — State `9` (`259`) and State `10` (`283`) are interleaved in one loop and include Dolls:** Binary completes all `oppPlusSummons` (Summons/Guests first, then Players; no Dolls) for `259` in State `9` before checking `283` in State `10`. `Battle.LostTurnSoft()` (`Battle.cs:1028-1032`) checks both inside one `OpponentsArray` loop and omits `259`'s `0.3x` attack.
  - **`M01.03c` (`S1`) — State `1` (`RollAilmentRecovery`, `Battle.cs:775-792`) omits `IsAsleep() && IsSleepDecaying()` (`vtable+0x8c`):** Binary (`0x48d1bc..0x48d1da`) immediately removes sleep-decaying ailments when `actor.IsAsleep()`; `Battle.cs` never checks `vtable+0x8c`.
  - **`M01.03d` (`S2`) — Minor state divergences:** State `2` (`345` Third Eye Wide, `Battle.cs:857`) does not `break` on first proc and iterates Dolls/Summons/Guests/petrified units (intentional patch `X16` `ThirdEyeDispel` at `Battle.cs:864` is verified faithful in both vanilla and patched modes); State `13` (`357`, `Battle.cs:943`) debuffs Dolls/Summons/Guests; States `18..20` run `199->339->200->204` instead of `200->204->199/339`; State `22` (`355`, `Battle.cs:1005`) calls `Wait(u)` instead of preserving frozen gauge + `_SortTime(1, 1)`. *(State `0` Esarhaddon `311`, State `16` Regen `215/216/246/247` + enchants `144..149/296`, and State `21` Poison `113` match binary.)*

`engine_cs/src/DtEngine/Battle.cs:893`
```csharp
                softLost = LostTurnSoft(unit);
                if (softLost != Lost.No) Rec?.TurnsLost.Add(new RecKey(unit), 1);
                // Inner States 16-21: regen, dancer-turn dances (199/200/204/339), and Poison (113).
                if (unit.Alive && softLost != Lost.Skip) TickRegenAndDances(unit);
                if (!unit.Alive) return;
                // Inner State 22 (0x43851e): Undaunted (355) runs on a living unit's turn for dead members on the same side.
                Undaunted(unit.Side);
...
        Lost LostTurnSoft(Unit unit)
        {
            foreach (var other in OpponentsArray(unit))
            {
                if (other.Has(259) && Roll(other.Value(259))) return Deny(unit, Lost.Empty);
                if (other.Has(283) && Roll(other.Value(283))) return Deny(unit, Lost.Skip);
            }
            if (unit.Has(203) && Roll(unit.Value(203))) return Deny(unit, Lost.Skip);
            return Lost.No;
        }
```

---

### M01.04 Post-Action Resolution, Extra Turns (`288`/`289`/`354`), Doll/Summon Life Expiry, and Heretic Samsara (`291`)

**Verdict:** S1

```asm
00438cd2  inc      dword ptr [esi + 0xb0]
00438cde  cmp      eax, dword ptr [esi + 0xb4]
00438ce4  jb       0x43928b
00438e53  push     0x123
00438e7d  comiss   xmm0, dword ptr [0x6d938c]    ; float 1
00438f1e  imul     esi, eax, 0x32
0043903b  cmp      byte ptr [esi + 0x107], 0
00439052  cmp      esi, dword ptr [eax]
0043905f  mov      eax, dword ptr [eax + 0xbc]
00439153  mov      byte ptr [esi + 0x107], 1
```

- **Sub-bugs:**
  - **`M01.04a` (`S1`) — Heretic Samsara (`291`) runs at Turn-Start instead of Post-Action and re-checks live `< 50% HP`:** Binary latches `cmd291.val = 1.0f` when damaged (`0x47f775`) and re-rolls all 8 resistances (`416..423`) POST-ACTION (`0x438e50..0x438f20`). `Battle.cs:850-855` runs it at Turn-Start and re-checks `unit.Hp < unit.MaxHp / 2.0`, missing post-action activation and failing if healed back `>= 50%` before acting. Fix: latch Samsara activation on `< 50% HP` damage and re-roll resistances in `EndOfTurn()`.
  - **`M01.04b` (`S1`) — Extra-turn rolls (`288`/`289`/`354`) omit Sleep/head guards and block on Chant Start:** Binary `0x43903b..0x43915a` guards on `grantedExtraTurn == 0 && actor == units[0] && !IsAsleep()`, without checking `actionType != 3/9` (Chant Start). `Battle.cs:1112, 1124` omits `unit.St[116] == null` (Sleep) and head-unit check (after counter Push Back `54`/Stun `118`), and requires `unit.Chant == null` (cancelling remaining Triple-Action extra turns when starting a chant). Fix: add `!IsAsleep()` and head-unit guards and remove `unit.Chant == null` gate.
  - **`M01.04c` (`S1`) — `EndOfTurn()` wastes a `Wait()` RNG draw on every extra turn:** `Battle.cs:1109-1111` calls `Wait(unit, last)` (drawing speed jitter) BEFORE checking `unit.Extra > 0` or rolling `288`/`289`/`354`, then overwrites `unit.NextTime = Time`. Binary skips `_SetTime` completely on extra turns (`0x438ce4`, `0x43915a`). Fix: compute `Wait()` only when no extra turn is granted.

`engine_cs/src/DtEngine/Battle.cs:1109`
```csharp
            if (unit.Chant != null) wait = Wait(unit, unit.Chant, true);
            else wait = Wait(unit, last);
            unit.NextTime = Time + wait;
            if (unit.Extra > 0 && unit.Chant == null && !Over())
            {
                unit.Extra--;
                unit.NextTime = Time;
                unit.ExtraTurn = true;
            }
...
            else if (acted && unit.Chant == null && !Over())
            {
                if (unit.Has(288) && Roll(unit.Value(288))) unit.Extra = 1;
```

---

### M01.05 ATB `_SetTime` (`0x43e5c0` -> `0x4499d0..0x44a3c5`)

**Verdict:** S2

```asm
00449b4c  addss    xmm0, dword ptr [0x6d9540]    ; float 100
00449b58  divss    xmm0, dword ptr [0x6d95b8]    ; float 200
00449bab  fdiv     dword ptr [0x6d9470]    ; float 12
00449e72  movss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0044a335  mulss    xmm0, dword ptr [0x6d93a0]    ; float 1.2
0044a341  movss    xmm1, dword ptr [0x6d9380]    ; float 0.92
0044a359  push     0x12a
0044a370  call     0x490790
0044a375  cmp      eax, 0xa
```

- **Sub-bugs:**
  - **`M01.05a` (`S2`) — `SPEED_BUFFS` (`168, 217, 221`) uses `SumStatus` instead of `SumValue` (status + passive):** Binary `0x449f20..0x44a050` queries `vtable+0x48` (statuses and passives). `Battle.cs:569` calls `SumStatus(unit, SPEED_BUFFS)`, ignoring passives (`0` vanilla passives grant `168`/`217`/`221`, so `S2`). Fix: change `SumStatus` to `SumValue`.
  - **`M01.05b` (`S2`) — Enchant `298` (`0x12a`) omits the always-true `Rand(10) < 10` draw & Escape (`1.20x`) hardcoded `false`:** Binary `0x44a36e..0x44a378` consumes 1 `Rand(10)` draw (always `< 10`, identical 100% probability) before adding `+0.25f` capped at `0.92f`; `Battle.cs:586` adds `+0.25` without an RNG draw, and `Battle.cs:585` passes `escaping: false` (Escape is not simulated in battle loops). All core `_SetTime` math, stat selection, Stamina (`261`, `<= (MaxHP*40)//100`), enchant clamps `[-0.5, +0.5]`, shared tail (`201, 340, 276, 277, 316`), Defend `1.15x`, and `0.92f` cap match binary.

`engine_cs/src/DtEngine/Battle.cs:569`
```csharp
                bonus = SumStatus(unit, SPEED_BUFFS);
                if (unit.Hp <= 0.4 * unit.MaxHp && unit.Has(261)) bonus += unit.Value(261);
...
            double value = F.TurnValue(stat, unit.Weight, unit.Level, f1 * f2, bonus + enchant, unit.St[122] != null,
                                       action != null && action.Kind == AKind.Defend, false, random);
            if (chanting && unit.HasEnchants && unit.Pieces(298) != 0) value = Math.Min(F.VALUE_CAP, value + 0.25);
```

---

### M01.06 Player Weapon / Unarmed / Action / Chant Speed Slots & Enemy Spell Speed

**Verdict:** MATCH

```asm
004f729e  call     0x56c9a0
004f72a7  push     0x160
004f5337  movss    xmm0, dword ptr [eax + esi*4 + 0xe8]
004f54d8  mov      eax, dword ptr [esi + 0xa8]
004f5595  push     0x107
004f55b5  mov      dword ptr [esp + 4], 1
005575ac  movss    xmm0, dword ptr [eax + 0x5c]
```

- **Verification:** All 4 speed accessors match the vanilla binary 1-to-1:
  - `GetActionSpeed` (`0x4f7280`): `Action.Speed` (`Action.cs:377-385`) + Wreathed in Glory `352` (`Battle.cs:575`).
  - `GetSingSpeed` (`0x4f52d0`): `Action.ChantSpeed` (`Action.cs:388-396`, `gamedata/data.py:192`).
  - `GetWeaponActionSpeed` (`0x4f54d0`): main-hand weapon rank, else Enchant `263` (`0x107`) -> Rank A (`WeaponRanks[1]`), else `ClassData+0x24` unarmed rank (`Units.cs:714-722`), while Dolls return `0.0` (`0x4fd630`, `Units.cs:930`) and Enemies/Summons/Guests use their respective weight slots (`0x4f2150`/`0x5001d0`/`0x4feeb0`).
  - `GetEnemySpellSpeed` (`0x557590`): `Atk.Speed` (`Action.cs:382`, `Battle.cs:575-577`; `0` non-passive vanilla enemy attacks have `Speed == 0`).

`engine_cs/src/DtEngine/Units.cs:714`
```csharp
            double rankDelay;
            if (weapon != null && weapon.Rank != T.NONE && weapon.Rank >= 0)
                rankDelay = data.WeaponRanks[weapon.Rank];
            else if (counted.ContainsKey(263) && data.WeaponRanks.TryGetValue(1, out double rankA))
                rankDelay = rankA;
            else if (data.ClassUnarmedRanks.TryGetValue(classId, out int unarmedRank) && data.WeaponRanks.TryGetValue(unarmedRank, out double classUnarmed))
                rankDelay = classUnarmed;
            else
                rankDelay = UnarmedDelay(data);
```

`engine_cs/src/DtEngine/Battle.cs:575`
```csharp
                    double spd = action.Speed + (unit.HasUnique && unit.UniqueEffect == 352 ? unit.Value(352) : 0.0);
                    if (action.Skill != null && action.Skill.IsMagic) { f1 = 1.0; f2 = spd; }
                    else { f1 = spd; f2 = 1.0; }
```

---

### M01.07 Chant & Performance Interruption (`0x44cf90..0x44d266` Physical, `0x44f12a..0x44f14a` Magic Crit-Only, `0x47ea83..0x47eac0` Cancellation)

**Verdict:** S1

```asm
0044d03a  mulss    xmm0, dword ptr [0x6d93bc]    ; float 1.5
0044d042  addss    xmm0, xmm1
0044d056  movss    xmm1, dword ptr [0x6d9384]    ; float 0.95
0044d238  cmp      eax, 0x21
0044d246  or       byte ptr [eax + 0x33], 1
0044f13f  cmp      eax, 0x21
0047ea83  cmp      byte ptr [ebx + 0x33], 0
0047ea97  call     0x43bc50
0047eaa0  call     0x43c110
0047eaa9  call     0x43c600
0047eab2  call     0x43c9b0
0047eabb  call     0x43ce30
```

- **Sub-bugs:**
  - **`M01.07a` (`S1`) — Endure (`254`) clamps damage BEFORE `Interrupt()` computes the interruption ratio:** Binary computes `isInterrupted` inside `CalcPhysicalAttack` (`0x44cfad..0x44d24a`) using the **pre-Endure** unclamped `dmg` BEFORE `_AfterHit2` (`0x423888`) clamps lethal damage to `CurHP - 1`. `Battle.TakeDamage()` clamps `amount = target.Hp - 1` at line `2542` and then passes the clamped `amount` to `Interrupt()` at line `2575` (massively understating interrupt chance on Endure procs, and skipping both Sleep wake and `Interrupt()` completely when `target.Hp == 1` so `amount` becomes `0`!). Fix: pass pre-Endure `rawAmount` to `Interrupt()` and gate Sleep wake / `Interrupt()` on `rawAmount > 0 && target.Alive` (after `Endure`).
  - **`M01.07b` (`S2`) — `target.Value(264)` does not sum status + passive `264`, and non-crit Magic draws 1 wasted `Rng.Random()`:** Binary `0x47e400` sums all `264` commands (`3` uses in `pck_usage`: `Passive: 1, EnemyAttack: 2`); `Battle.cs:2596` uses `target.Value(264)` (first only), and `Battle.cs:2575 -> 2597` draws `Rng.Random()` even when `chance == 0.0` (non-crit Magic). *(Intentional patch `X14` `InterruptProduct` at `Formulas.cs:292` is verified faithful in both vanilla `maxHp*1.5 + (1+mod)` and patched `maxHp*1.5*(1+mod)` modes; all 5 enchant coefficients `57..61` and all 5 cancellation targets `Chant/Song/Dance/Puppet/Geass` match.)*

`engine_cs/src/DtEngine/Battle.cs:2542`
```csharp
            if (fatal && target.Has(254) && Roll(target.Value(254))) amount = target.Hp - 1;
...
            if (target.Alive && amount > 0)
            {
                target.PopStatus(116);
                if (target.Chant != null || Performing(target))
                    Interrupt(target, amount, critical, action == null || !action.Magic);
            }
```

`engine_cs/src/DtEngine/Formulas.cs:292`
```csharp
                double divisor = product ? maxHp * INTERRUPT_HP_FACTOR * (1 + modifier) : maxHp * INTERRUPT_HP_FACTOR + (1 + modifier);
```

---

## M02 — Physical Damage, Criticals & Multi-Hit (`M02.01` – `M02.07`)

### M02.01 Base Physical ATK/DEF, Stat Substitution, Swing, Weapon/Skill Rank, Status/Enchant Modifiers & Ignore-DEF

**Verdict:** S1

```asm
0044a9e1  call     0x43e970
0044b23c  mov      edx, 0x2f
0044b26f  mov      edx, 0x31
0044b2f9  call     0x61e650
0044b36e  addss    xmm0, dword ptr [0x6d93f8]    ; float 2
0044b3b4  mov      edx, 0x1a
0044b3db  mov      edx, 0x1bb
0044b411  cmp      esi, 0x14
0044b457  add      eax, 0xffffff49
0044b45c  cmp      eax, 0x10
0044b9c0  mulss    xmm1, dword ptr [0x6d93b0]    ; float 1.35
0044ba33  mov      edx, 0x45
```

- **Sub-bugs:**
  - **`M02.01a` (`S1`) — `First(action, unit, 26)` discards active status `26` (`Berserk`, `Defender`, `High Risk, High Return`) on all 58 Techniques with Effect `26`:** Binary `CalcPhysicalAttack` (`0x44a9e1 -> 0x43e970`) merges action and status/passive commands by **summing** duplicate IDs (`fadd` at `0x43e9d8`). `Battle.cs:2098` uses `First(action, unit, 26)`, which returns only `action.Val(26)` and drops `unit.St[26]` whenever the skill carries Effect `26`! Reach: `61` player Techniques + `7` EnemyAttacks (`Berserk`/`Defender`) in vanilla `pck_usage`. Fix: sum `action.Val(26, 0.0) + unit.Value(26, 0.0)`.
  - **`M02.01b` (`S1`) — Player Dolls (`CGamePlayerStatusETCDoll`) have `Swing = 0.0` instead of inheriting main-hand weapon swing:** Binary `0x44b2b6..0x44b2f0` reads `GetEquipmentID(actor.status2, 0)` for all `isPlayerSide != 0` units (including Player Dolls, which copy owner equipment). `UnitFactory.BuildDoll()` (`Units.cs:930`) hardcodes `swing = 0.0` (only `AddShadow` copies `owner.Swing`). Fix: copy `owner.Swing` in `BuildDoll` for player puppets.
  - **`M02.01c` (`S2`) — Stat-substitution priority (`47` RES vs `49` INT) inverted, and `SwingOf` uses `Round` instead of `__ftoui3` `trunc0`:** Binary checks `47` first then `49` (`49` overrides `47` at `0x44b26f`); `Battle.cs:2110-2111` checks `49` first then `47` (`0` vanilla skills carry both -> `S2`). Binary `0x44b2f9` calls `0x61e650` (`__ftoui3` `trunc0`), whereas `Battle.SwingOf()` (`Battle.cs:2474`) uses `PyMath.Round(100 * swing)` (`0` vanilla weapons/enemies differ between `f32 trunc0` and `Round` -> `S2`). *(Verified matching: 2H Lance `111` `{183..199}` == `TwoHanded && Type==3`, Elbow Grease `443` gated on `26` at `20%`, Doll `286` + `304/305` capped `0.05`, ATK/DEF enchants `29/30` & `33/34` capped `50`, DEF `1.35x`, Ignore-DEF `69`/Furious; Joint Attack `actionType==0` is `MODEL-LIMIT`.)*

`engine_cs/src/DtEngine/Battle.cs:2098`
```csharp
            double modifiers = First(action, unit, 26) + (action.Atk != null ? action.Atk.Power : 0.0) + SumStatus(unit, ATTACK_STATUS_MODIFIERS);
...
            double atk = unit.Stat(Unit.ATK);
            if (action.Has(49)) atk = unit.Stat(Unit.INT);
            if (action.Has(47)) atk = unit.Stat(Unit.RES);
...
        double SwingOf(double swing)
        {
            int n = PyMath.Round(100 * swing);
```

`engine_cs/src/DtEngine/Units.cs:930`
```csharp
            var unit = new Unit(doll.Name, owner.Side, owner.Level, DOLL_HP, 0, baseStats, null, 0.0, 0.0, T.NONE, Kind.Doll);
```

---

### M02.02 Range & Row Factor, Damage Cuts, Defending Multiplier & Min/Crit-Min Damage Roll

**Verdict:** S1

```asm
0044a7d5  mov      dword ptr [esp], 0x3f800000
0044a7ee  mov      dword ptr [esp], 0x3f000000
0044a808  mov      dword ptr [esp], 0x3f400000
0044bc5f  movss    xmm0, dword ptr [0x6d9368]    ; float 0.75
0044bc67  maxss    xmm0, xmm1
0044c565  call     0x43ea50
0044c56e  cmp      byte ptr [edi + 0x104], al
0044cb2f  ucomiss  xmm0, dword ptr [0x6d938c]    ; float 1
0044cb3a  jp       0x44cb49
0044cb49  mov      eax, 3
```

- **Sub-bugs:**
  - **`M02.02a` (`S1`) — Auto-Guard (`255`) rolled before Cover (`171`) redirect:** `Battle.Perform()` (`Battle.cs:1330-1340`) populates `guarding` for original `targets` BEFORE `Resolve()` calls `Redirect()` (`Battle.cs:1756`). A Covering ally with Auto-Guard (`255`) never gets its `255` roll when taking a covered physical hit. Fix: roll `255` on the post-Cover defender.
  - **`M02.02b` (`S2`) — Doll range override (`228->0, 229->1, 231->2` at `0x44baaf..0x44bb6e`) not enforced in `Action.Reach`:** `Action.cs:352-364` reads `Skill.Range` / `Atk.Range` without overriding for `PuppetEffect in {228, 229, 231}` (`S2` because all vanilla `228/229/231` player & enemy doll actions already store matching ranges `0/1/2`). *(Verified matching: row distance `0/1/2`, range factors `1.0/0.75/0.5`, physical/all cut enchants `66/67/70/71` floored at `0.75`, defending `0.5x`, and the vanilla inverted crit-min quirk `critical ? 1 + Rand(2) : 3` at `Battle.cs:2170`.)*

`engine_cs/src/DtEngine/Battle.cs:1330`
```csharp
            if (action.Physical)
            {
                for (int j = 0; j < targets.Length; j++)
                {
...
                    if (t.Side != unit.Side && t.Has(255) && Roll(t.Value(255))) guarding.Add(t);
                }
            }
...
            if (damage <= 0) damage = critical ? 1 + Rng.ChoiceIndex(2) : F.MIN_DAMAGE;
```

---

### M02.03 Elemental/Physical Resistance, Race Slayer/Guard, Effects `87`/`88`, Element Boost & Zone Factor

**Verdict:** S1

```asm
0044f6f5  mulss    xmm1, dword ptr [0x6d9348]    ; float 0.5
0044bd05  mov      edx, 0x57
0044bd23  call     0x55d810
0044bf2f  call     0x557ef0
0044c367  call     0x4f21c0
0044c37a  call     0x4f21f0
0044fc2e  cmp      edx, 3
0044fc41  movss    xmm1, dword ptr [esi + 0x1e4]
0044fd70  mulss    xmm1, dword ptr [esi + 0x1f4]
```

- **Sub-bugs:**
  - **`M02.03a` (`S1`) — `ZoneFactor()` squares duplicate zone slots (`St02_0070` fixed battle `41` has `slots = (9, 9)`):** Binary `_CalcFieldElementRevision` (`0x44fc2e..0x44fd9c`) tests `s0 == k || s1 == k` (logical OR — multiplies ONCE even when both slots match). `Battle.ZoneFactor()` (`Battle.cs:2526-2531`) loops `foreach (int slot in ZoneInfo.Slots)`, multiplying `f.Element` TWICE on duplicate slots (confirmed in real vanilla `map_data`: `St02_0070` battle `41` `(9, 9)` Wind). Fix: check `Array.IndexOf(ZoneInfo.Slots, code) >= 0` once per zone type.
  - **`M02.03b` (`S1`) — Effect `87` (`Only Damages Living`) misses `Character.Race` (`Ist` id=11 `race=6`), fails to void `AfterHit`, and is skipped on special damage:**
    1. `tools/character_data.py:66`, `tools/engine_export.py:136`, `Loader.cs:402`, and `Units.cs:724` never load `Character.Race` (`PlayerStatusData+0x30`, memory `+0x44`), leaving every party member with `Race = -1`. Party member **Ist** (`id=11`) has `race = 6` (Magic Being, non-living) and MUST be immune to all `13` vanilla EnemyAttacks carrying Effect `87`!
    2. `Battle.cs:2123` returns `0` inside `DamageInner` instead of marking the hit voided (`resultType = 4`), so `Resolve()` (`Battle.cs:1783`) still runs `AfterHit` (ailments, drains, etc.) and `DamageInner` still runs Murder `258`!
    3. `Battle.cs:2002` (`if (special)`) bypasses `PhysicalDamageValue`, skipping Effect `87` on special-damage attacks (`0x44ce48` runs AFTER `_CalcSpecialDamage`).
    Fix: export/load `Character.Race`, set `unit.Race` in `BuildMember`, check `87` against `!(Race in {0,2,3,4,7,8,9})` (enemy) / `!(Race in {2,4})` (player) after special damage, and return a voided status to skip `AfterHit` and Murder `258`.
  - **`M02.03c` (`S1`) — Feline (`196`) and Sea Creature (`209`) stack instead of `else if` on Enemy IDs `215..217`:** Binary (`0x44c364..0x44c3b5`) uses mutually exclusive `if IsFeline else if IsSeaCreature`. `Battle.RaceFactor()` (`Battle.cs:2489`) loops over both without `break`, double-stacking on overlapping enemies `215, 216, 217` and applying `209` where binary applies `0`. Fix: `break` on first matching `RACE_SPECIAL` table.
  - **`M02.03d` (`S1`) — Player Dolls do not inherit owner enchants for RaceSlayer / Both-Sides Element (`251..255`):** `BuildDoll` (`Units.cs:930`) does not copy `owner.Enchants`, unlike `CGamePlayerStatusETCDoll`.

`engine_cs/src/DtEngine/Battle.cs:2123`
```csharp
            if (action.Has(87) && (target.Race == 5 || target.Race == 6)) { immediateZero = 1; return 0; }
...
                foreach (var (e, ids) in F.RACE_SPECIAL) if (target.EnemyId != T.NONE && ids.Contains(target.EnemyId)) t.AddInt(unit.Pieces(e));
...
            foreach (int slot in ZoneInfo.Slots)
            {
                if (slot == (physical ? 3 : 4)) factor *= f != null ? (physical ? f.UpA : f.UpB) : 1.0;
                if (slot == (physical ? 5 : 6)) factor *= f != null ? (physical ? f.DownA : f.DownB) : 1.0;
                if (slot >= 7 && slot <= 11 && action.Attr == slot - 3) factor *= f != null ? f.Element : 1.0;
            }
```

`engine_cs/src/DtEngine/Units.cs:723`
```csharp
            var unit = new Unit(name ?? (character != null ? character.Name : "class " + classId), Unit.PARTY, level, hp, tp, totals, resist,
                                rankDelay, weapon != null ? weapon.Swing : 0.0, T.NONE, Kind.Member);
```

---

### M02.04 Additive `other` Modifiers & Float-to-Integer Truncation

**Verdict:** S1

```asm
0044c60e  mov      edx, 0x47
0044c678  mov      edx, 0x88
0044c68e  mov      edx, 0xb3
0044c723  mov      edx, 0xbe
0044c738  cmp      byte ptr [eax + 4], 0
0044c748  mov      edx, 0xbf
0044c7d7  push     0x134
0044c81a  mov      edx, 0x107
0044cacc  cvttss2si eax, xmm0
00422b62  push     0xb3
00422b6e  call     dword ptr [eax + 0x64]
```

- **Sub-bugs:**
  - **`M02.04a` (`S1`) — Effect `191` (`Power Charge`) is NOT suppressed during counter-attacks:** Binary `0x44c738` checks `ctx.isCounter_0x04 == 0` before adding `CmdVal(actorCmds, 191)`. `Battle.cs:2125` adds `unit.StatusValue(191)` unconditionally, even during `inCounter` counter-attacks (`191`: `1` player Technique `Power Charge`). Fix: gate on `!inCounter ? unit.StatusValue(191) : 0.0`.
  - **`M02.04b` (`S1`) — Material Guard (`179`) is never removed on physical hit (`0x422b58..0x422b6e`) and `179`/`308` do not exclude Stage-3 Petrified casters/allies:** As proven at `0x422b58..0x422b6e`, `CActionPatternBase::_Task` removes status `179` (`0xb3`) after a non-voided physical hit; `Battle.cs:2126` never pops it (`179`: `10` uses). Also `Battle.cs:2127` (`179`) and `2135` (`308` Imperial Guard) check `Alive` instead of `CanFight` (Stage-3 Petrified, `vtable+0xe8`, `S2` sub-part). Fix: pop `179` after non-voided physical hits and use `CanFight`. *(Verified matching: exact 22 `StatEffect71` IDs, `136 * index`, `190`, `263 * CountTrueAilments`, `267`, `271`, `219`/`220`, and `cvttss2si` `trunc0`. Joint enchants `261`/`290` are `MODEL-LIMIT`.)*

`engine_cs/src/DtEngine/Battle.cs:2125`
```csharp
            double other = target.Value(190) + unit.StatusValue(191) + FullHpBonus(unit) + LevelBonus(unit, target);
            var guard = target.St[MATERIAL_GUARD];
            if (guard != null && (guard.Source == null || (guard.Source.Alive && guard.Source.Shield))) other += guard.Value;
```

---

### M02.05 Post-Truncation Modifiers, Demon Wall `356`, Positive Trance `440`, SpecialDamage & Cap `296`

**Verdict:** S1

```asm
0044cae1  cmp      byte ptr [ebx + 0x105], 0
0044cbf0  push     0x164
0044ccb2  mov      edx, 0x1b8
0044ccce  movss    xmm1, dword ptr [0x6d9540]    ; float 100
0044ccf8  fdivr    dword ptr [ebp + 0x10]
0044cda2  mov      edx, 0x56
0044ce15  call     0x44f720
0044ce48  cmp      byte ptr [ebp - 0x3c], 0
0044f806  mov      edx, 0x86
0044f9c0  mov      al, byte ptr [eax + 0xa5]
0048c647  mov      edx, 0x128
```

- **Sub-bugs:**
  - **`M02.05a` (`S1`) — Warning Shot `3/10` penalty (`0x44cae1..0x44cb11`) completely absent:** Because Warning Shot (`259`) never executes an attack in `Battle.cs`, the `(dmg * 3) / 10` pre-min-roll scaling is unimplemented. Fix: add `bool warningShot` flag to `Action` and apply `dmg = (dmg * 3) / 10` before the `dmg <= 0` floor roll.
  - **`M02.05b` (`S1`) — Effect `140` (`Halve HP`) ignores boss/fixed `+0xa5` flag, and `141` (`3/4 HP`) / `134` (`Gold/20`) issues:** Binary gates both `140` (`1` player Technique) and `141` (`0` uses) on `target.isPlayerSide != 0 || target.pctHpSusceptible_0xa5 != 0` (`0x44f9c0`). `Scenario.OptionsFrom()` defaults `HalveEnemies = true` even on fixed/boss battles, `Battle.cs:2463` has no gate on `141` (`S2`), and Effect `134` (`Gold/20`, `0` uses, `S2`) is missing from `Action.IsSpecial` and `RawSpecialDamage`. Fix: gate `140`/`141` on `target.Side == Unit.PARTY || (!Fixed && !Options.Boss)` (matching `+0xa5`) and add `134`.
  - **`M02.05c` (`S1`) — Effect `86` (`Magic Users: Damage x2`) runs AFTER `_CalcSpecialDamage` instead of BEFORE, and Effect `87` is skipped on special damage:** Binary runs `86` (`0x44cda2`) -> `_CalcSpecialDamage` (`0x44ce15`) -> `87` (`0x44ce48`). `Battle.DamageInner()` (`Battle.cs:2002, 2023`) runs `SpecialDamage` first, skips `87`, and then doubles special damage with `86`! Fix: gate `86` inside `if (!special)` and evaluate `87` after `SpecialDamage`.
  - **`M02.05d` (`S2`) — Demon Wall `356` doesn't exclude Stage-3 Petrified allies (`Battle.cs:2045`), Positive Trance `440` clamps divisor `Math.Max(1.0, UniqueValue)` (`Battle.cs:2019`; all vanilla `440` values are `1..10`, and `X17` threshold matches both vanilla `100` and Balance patched modes), and Cap `296` only checks `action.TryVal(296)` (`Battle.cs:2025`).**

`engine_cs/src/DtEngine/Battle.cs:2018`
```csharp
                if (!action.Magic && actor.HasUnique && actor.UniqueEffect == 440 && actor.Pep > ptThresh)
                    amount += PyMath.Int(amount * (actor.Pep - ptThresh) / Math.Max(1.0, actor.UniqueValue) / 100.0);
            }
            if (target.St[116] != null && !special) amount = amount * F.SLEEP_NUM / F.SLEEP_DEN;
            if (!special && action.Actor.Pieces(F.AILING_ENCHANT) != 0 && HasTrueAilment(target)) amount += PyMath.Int(amount * F.AILING_SHARE);
            if (action.Has(86) && target.Kind == Kind.Member && target.ClassId >= F.MAGIC_USER_LOW && target.ClassId < F.MAGIC_USER_HIGH) amount += amount;
...
            if (action.Has(140)) return target.Side == Unit.PARTY || Options.HalveEnemies ? target.Hp / 2 : 0;
            if (action.Has(141)) return target.Hp * 3 / 4;
```

---

### M02.06 Physical Critical Rate & Multiplier, Crit Interrupt & Crit-Triggered Murder `258`

**Verdict:** S1

```asm
0044a9e1  call     0x43e970
0044f1d8  mulss    xmm0, dword ptr [0x6d9324]    ; float 0.2
0044f4b2  push     0x10c
0044f4db  movss    xmm0, dword ptr [0x6d94e0]    ; float 50
0044f5a0  cvttss2si ecx, dword ptr [esp + 0xc]
0044f5b0  jl       0x44f5ba
0044d238  cmp      eax, 0x21
0044d279  mov      edx, 0x102
0044d2af  call     0x47b220
```

- **Sub-bugs:**
  - **`M02.06a` (`S1`) — `AddFirst(..., 31)` discards `Last Stand` (`unit.St[31]`) when using `Moonlight Purgatory` or `Divine Cannon`:** Binary `0x44a9e1 -> 0x43e970` merges action and actor status commands by summing duplicate IDs. `Battle.CriticalRateOf()` (`Battle.cs:1970`) calls `AddFirst` for `CRIT_TERMS = {31, 174, 211}`, dropping `Last Stand` (`St[31]`, Technique 9) whenever the skill itself has Effect `31` (`Moonlight Purgatory` Technique 13, `Divine Cannon` Technique 50). Fix: sum action + unit values for `31`/`174`/`211`.
  - **`M02.06b` (`S1`) — Crit-triggered Murder (`258`) fires on voided Effect `87` hits and is skipped on Effect `2` TP damage:** `Battle.DamageInner()` rolls `critical` at line `2009` before Effect `87` returns `0`, then still executes `ApplyAilment(..., 119, ...)` at line `2032` (whereas binary voids `resultType = 4` in `_Task`!). Conversely, `Battle.cs:2026-2030` returns early on Effect `2` (TP damage), skipping Murder `258` even on physical crits (`0x44d266` runs unconditionally on physical crits).
  - **`M02.06c` (`S1`) — Crit/Chant Interrupt (`0x44cfad..0x44d265`) uses post-Endure damage** (`Battle.cs:2542 -> 2575`, see `M01.07a`).
  - **`M02.06d` (`S2`) — Effect `110` (`Crits on Beasts`) skips player Beast `Luco` (`id=19, race=2`):** `Battle.cs:1982` requires `target.Side == Unit.ENEMIES` and `Units.cs:724` sets `Race = -1` (`0` enemy attacks use `110` in vanilla -> `S2`).

`engine_cs/src/DtEngine/Battle.cs:1970`
```csharp
            foreach (int e in CRIT_TERMS) AddFirst(ref s, action, unit, e);
...
            if (target.Side == Unit.ENEMIES && action.Has(110) && target.Race == 2) return true;
...
            if (action.Has(2))
            {
                target.Tp = Math.Max(0, target.Tp - amount);
                return amount;
            }
            TakeDamage(target, amount, action, critical);
            if (critical && action.Physical && target.Alive && (action.Has(MURDER) || action.Actor.Has(MURDER)))
                ApplyAilment(action.Actor, target, 119, First(action, action.Actor, MURDER), action);
```

---

### M02.07 Multi-Hit Count (`SetHitCount`, Weight Tables & Rondo Shift)

**Verdict:** S1

```asm
00417da9  mov      dword ptr [ebx + 0x40], 0
00417db0  mov      edx, 0x59
00417dc4  mov      edx, 0xd2
00417de4  call     0x505ad0
00417e87  call     0x61e650
00418045  mov      edx, 0xfc
00418084  add      dword ptr [ebx + 0x40], 3
0041808c  mov      edx, 0xfb
004180cd  add      dword ptr [ebx + 0x40], 2
004180e3  mov      dword ptr [ebx + 0x40], 1
```

- **Sub-bugs:**
  - **`M02.07a` (`S1`) — `Math.Max(1, hits)` breaks Effect `94` (`0~4 Hits`, 18 vanilla skills/attacks):** Binary `0x417eb0` has ZERO lower cap on `act.hitCount`, so Effect `94` (`[10, 15, 30, 25, 20]` without Rondo) genuinely yields `0` hits `10%` of the time. `Battle.NumberOfHits()` (`Battle.cs:1716`) and `T.RANDOM` targeting (`Battle.cs:1306, 1313`) clamp `Math.Max(1, hits)`, turning every `0`-hit roll into `1` hit on `Danger Shoot` (Technique 79) and `17` EnemyAttacks (`Daedalus Attack`, `Heart Corruption`, `Share Misery`, etc.)! Fix: return `hits` unclamped when `any` is true and allow `0` hits in `T.RANDOM` (`if (hits <= 0) return;`).
  - **`M02.07b` (`S2`) — `Action.MultiHitIndex` evaluates at most one effect from `{89..92, 94..100}` instead of independent additive checks:** Binary (`0x417db0..0x418032`) runs independent `if` blocks summing all present hit commands; `Action.cs:93-95` picks only the first matching effect (`0` vanilla skills/attacks combine two distinct IDs from `{89..92, 94..100}` -> `S2`). *(Verified matching: all 11 normal & Rondo `.rdata` weight tables, `93` & `178` `__ftoui3` `trunc0`, and Triple `252` + Double `251` fall-through stacking to `5` hits on plain attacks.)*

`engine_cs/src/DtEngine/Action.cs:93`
```csharp
                MultiHitIndex = HasBit(89) ? 0 : HasBit(90) ? 1 : HasBit(91) ? 2 : HasBit(92) ? 3
                              : HasBit(94) ? 4 : HasBit(95) ? 5 : HasBit(96) ? 6 : HasBit(97) ? 7
                              : HasBit(98) ? 8 : HasBit(99) ? 9 : HasBit(100) ? 10 : -1;
```

`engine_cs/src/DtEngine/Battle.cs:1313`
```csharp
                    int count = Math.Max(1, hits);
...
            if (!any) hits = 1;
            return Math.Max(1, hits);
```

---

## M03 — Magical Damage (`M03.01` – `M03.05`)

### M03.01 Base Magic Damage Formula

**Verdict:** S1

```asm
0044dbc3  movss    xmm0, dword ptr [eax + 0x13c]
0044dbd3  call     0x61e650
0044dc58  cmp      eax, 0x2f
0044dcb3  call     0x44fbb0
0044de26  mulss    xmm2, dword ptr [0x6d9640]    ; float 500
0044de6d  mov      edx, 0xf4
0044e626  mulss    xmm0, dword ptr [0x6d93bc]    ; float 1.5
0044e65d  subss    xmm1, xmm0
0044fc89  movss    xmm1, dword ptr [esi + 0x1e8]
0044fd70  mulss    xmm1, dword ptr [esi + 0x1f4]
```

- **Sub-bugs:**
  - **`M03.01a` (`S1`) — `ZoneFactor()` squares duplicate zone slots on spells (`St02_0070` battle `41` `(9, 9)`):** Binary `_CalcFieldElementRevision` (`0x44fc89..0x44fd70`) uses logical OR across `z1, z2` (multiplies once). `Battle.ZoneFactor()` (`Battle.cs:2526-2531`) multiplies `f.Element` once per slot, squaring Wind spell boost on `St02_0070` battle `41` (`(9, 9)`). Fix: test zone presence once per zone effect type.
  - **`M03.01b` (`S2`) — `SwingOf` uses `PyMath.Round` instead of `__ftoui3` `trunc0`, and `First(27)/First(173)` does not merge action + status:** Binary `0x44dbd3` calls `0x61e650` (`__ftoui3` `trunc0`), whereas `Battle.SwingOf()` uses `PyMath.Round` (`0` vanilla spells differ -> `S2`); `Battle.cs:2218` uses `First` instead of sum for `27`/`173` (`0` vanilla damaging spells carry `27`/`173` -> `S2`). *(Verified matching: RES substitution `47`, zone scaling only `magicStat`, Doll `+500*(286 + min(0.05, 0.02*e304 + 0.01*e305))`, Magic Mastery `244`, `195+335`, INT enchants `37/38` cap `50`, Fantasia `212`, target RES `1.5x` + 7 `MAGIC_DEFENCE_MODIFIERS` + RES enchants `41/42` cap `50`, and post-subtraction `27/173`; Joint Attack `actionType==0` `+0x58` is `MODEL-LIMIT`.)*

`engine_cs/src/DtEngine/Battle.cs:2218`
```csharp
            double powerBoost = First(action, unit, 27) + First(action, unit, 173);
...
            double swing = expect || action.Skill == null ? 0.0 : SwingOf(action.Skill.Swing);
            // 0x44dc50..0x44dc8e: effect 47 (Damage based on RES) switches magic stat from INT to RES (Prism Dawn).
            double magicStat = action.Has(47) ? unit.Stat(Unit.RES) : unit.Stat(Unit.INT);
            return F.MagicDamage(magicStat * ZoneFactor(unit, action), power, target.Stat(Unit.RES), mastery, modifiers,
...
            foreach (int slot in ZoneInfo.Slots)
            {
                if (slot == (physical ? 3 : 4)) factor *= f != null ? (physical ? f.UpA : f.UpB) : 1.0;
                if (slot == (physical ? 5 : 6)) factor *= f != null ? (physical ? f.DownA : f.DownB) : 1.0;
                if (slot >= 7 && slot <= 11 && action.Attr == slot - 3) factor *= f != null ? f.Element : 1.0;
            }
```

---

### M03.02 Element Boost, Elemental Resistance Multiplier, and Magic Damage Cuts

**Verdict:** S1

```asm
0044e026  mov      edx, 0x145
0044e409  movss    xmm0, dword ptr [0x6d9334]    ; float 0.4
0044e6ee  cmp      eax, 0xb7
0044e812  movss    xmm0, dword ptr [0x6d978c]    ; float -0.25
0044e846  call     0x44f5d0
0044f6f5  mulss    xmm1, dword ptr [0x6d9348]    ; float 0.5
00422b58  cmp      byte ptr [esi + 0x79], 0
00422b69  push     0xb7
00422b6e  call     dword ptr [eax + 0x64]
```

- **Sub-bugs:**
  - **`M03.02a` (`S1`) — Magic Barrier / Spell Guard (`183` / `0xb7`) is NEVER consumed on a magical hit:** Disassembly of `CActionPatternBase::_Task` at `0x422b58..0x422b6e` proves that after every non-voided magical hit (`[esi+0x79] == 0`), `target->vt+0x64(0xb7)` immediately removes status `183`. `Battle.MagicValue()` (`Battle.cs:2219`) reads `target.StatusValue(183)` without ever popping it, so `Spell Guard` (Skill 23) and `Magic Barrier` (Skill 58) remain active for their entire 4–7 turn duration across unlimited spell hits! Fix: pop `target.St[183]` after a non-voided magical hit. *(Verified matching: Element boost `325..329` + both-sides `78..82` & `251..255` capped at `0.4`, magic enchant cuts `68..71` floored at `-0.25` additive with `183`, and `_CalcElementRevision` `(100 - resist*0.5)*0.01`.)*

`engine_cs/src/DtEngine/Battle.cs:2214`
```csharp
                elementBoost = Math.Min(F.ELEMENT_BOOST_CAP, F.ELEMENT_ENCHANT_SHARE * ((unit.St[status] != null ? 1 : 0) + unit.Pieces(enchant) + target.Pieces(enchant) + unit.Pieces(both) + target.Pieces(both)));
...
            double cut = (target.HasEnchants ? Math.Max(-0.25, -(0.10 * target.Pieces(68) + 0.05 * target.Pieces(69) + 0.08 * target.Pieces(70) + 0.04 * target.Pieces(71))) : 0.0) + target.StatusValue(183);
```

---

### M03.03 Additive `other` Modifiers (`[ebp+0x44]`)

**Verdict:** S2

```asm
0044e857  xorps    xmm0, xmm0
0044eb1b  movss    dword ptr [ebp + 0x44], xmm1
0044ebad  mov      edx, 0x58
0044ebe4  push     0x10b
0044ec6f  push     0x10f
0044ecc4  push     0xdb
0044ed19  push     0xdc
0044ed53  mov      edx, 0xbe
0044ee28  cvttss2si esi, xmm0
```

- **Sub-bugs:**
  - **`M03.03a` (`S2`) — Full-HP (`271`), Level-Diff (`219`/`220`), and Small-Party (`267`) bonuses are not gated on `target.Side == Unit.ENEMIES`:** Binary `0x44eb59..0x44ed50` evaluates `88`, `267`, `271`, `219`, and `220` ONLY when `target.isPlayer_0x78 == 0` (enemy target); Player-vs-Player spells jump directly to Limit Field `190` (`0x44ed53`). `Battle.MagicValue()` (`Battle.cs:2222-2227`) adds `FullHpBonus`, `LevelBonus`, and Enchant `267` unconditionally even when `target.Side == Unit.PARTY` (`S2` because `0` vanilla damaging player spells target allies; only non-damaging `Limit Field` 228 has `TargetCode == 14`). Fix: gate `FullHpBonus`, `LevelBonus`, and `267` in `MagicValue` on `target.Side == Unit.ENEMIES`. *(Verified matching: RaceGuard additive into `other`, Effect `88` on races `{5, 7, 8}`, Limit Field `190`, and `cvttss2si` truncation.)*

`engine_cs/src/DtEngine/Battle.cs:2222`
```csharp
            double other = target.Value(190) + (RaceGuard(unit, target) - 1.0) + FullHpBonus(unit) + LevelBonus(unit, target);
            if (action.Has(88) && (target.Race == 5 || target.Race == 7 || target.Race == 8))
                other += action.Val(88, 0.0);
            // 0x44ebe1: enchant 267 adds +0.10 * (5 - partyCount) per piece for small parties.
            if (unit.Kind == Kind.Member && unit.HasEnchants && unit.Pieces(267) != 0)
                other += 0.10 * Math.Max(0, 5 - initialPartyCount) * unit.Pieces(267);
```

---

### M03.04 Living-Only (`87`), Magic Critical (`301`), Demon Wall (`356`), & Post-Floor Multipliers

**Verdict:** S1

```asm
0044e881  mov      edx, 0x57
0044e8b7  cmp      dword ptr [eax + 0x44], 4
0044e8db  cmp      dword ptr [eax + 0x44], 2
0044eb41  call     0x557ef0
0044edbe  cmp      eax, 0x12d
0044eded  cmp      eax, 0x14
0044ef36  call     0x43af10
0044ef59  push     0x164
0044f040  mov      edx, 0x56
0044f0a0  call     0x44f720
0044f13f  cmp      eax, 0x21
```

- **Sub-bugs:**
  - **`M03.04a` (`S1`) — Living-Only Effect `87` (`0x57`) misses party member `Ist` (`race=6`), fails to void `AfterHit`, and is skipped on special magic:**
    1. `Units.cs:724` sets every party member's `Race = T.NONE`, ignoring `PlayerStatusData+0x30`, so **Ist** (`id=11`, Magic Being `race=6`) takes full damage from enemy Effect `87` attacks (`13` vanilla EnemyAttacks).
    2. `Battle.cs:2186` returns `0.0` (`immediateZero = 1`) without marking `isVoided`, so `Resolve()` (`Battle.cs:1771, 1783`) still executes `AfterHit` (applying ailments/statuses) instead of skipping post-calc (`0x421a67 -> 0x421f5a`).
    3. `Battle.cs:2002` (`if (special)`) bypasses `MagicValue`, skipping `87` on special-damage spells (`0x44f0b8` runs AFTER `_CalcSpecialDamage`).
    Fix: load `Character.Race`, evaluate `87` after `SpecialDamage`, and signal voided to skip `AfterHit`.
  - **`M03.04b` (`S1`) — Effect `86` (`Magic Users: Damage x2`) runs AFTER `_CalcSpecialDamage` instead of BEFORE:** Binary runs `86` (`0x44f040`) BEFORE `_CalcSpecialDamage` (`0x44f0a0`), which overwrites `dmg`. `Battle.DamageInner()` (`Battle.cs:2002, 2023`) runs `86` AFTER `SpecialDamage`. Fix: move `86` inside `if (!special)`.
  - **`M03.04c` (`S2`) — Demon Wall (`356`) does not exclude Stage-3 Petrified allies (`Battle.cs:2045`):** Binary `0x43af10(aliveOnly=1)` excludes Stage-3 Petrified members; `Battle.DemonWallOf()` checks `u.Alive` only. *(Verified matching: Magic Critical `301` at flat 20% -> `1.25x` on `!spellMissed`, Sleep `1.5x`, Ailed `+15%` enchant `280` on `HasTrueAilment`, and Magic Crit 33% interrupt.)*

`engine_cs/src/DtEngine/Battle.cs:2186`
```csharp
            if (action.Has(87) && (target.Race == 5 || target.Race == 6)) { immediateZero = 1; return 0.0; }
...
            if (action.Has(86) && target.Kind == Kind.Member && target.ClassId >= F.MAGIC_USER_LOW && target.ClassId < F.MAGIC_USER_HIGH) amount += amount;
...
                if (u.Side == target.Side && u.Alive && u.Front == target.Front && u.Has(DEMON_WALL)) return u;
```

---

### M03.05 Missed-Spell Grazing, Spell Floor Roll, Damage Cap, & Voided/Nullify Interaction

**Verdict:** S1

```asm
0044ee36  push     0x110
0044ee51  sar      esi, 2
0044ee5d  sar      esi, 1
0044ee7a  push     5
0044ee81  lea      esi, [eax + 1]
0044f0ce  mov      edx, 0x128
00421b51  mov      dword ptr [ebx + 0x2c], 4
00421bcb  push     0x7c
00421c63  call     0x416ea0
00421c6e  push     0xc0
```

- **Sub-bugs:**
  - **`M03.05a` (`S1`) — `Voided()` applies Range Immunity (`182`) and Parry (`250`) to `19` short/mid-range enemy Magic attacks:** Binary `CActionPatternBase::_Task` (`0x421afb -> 0x421bbd`) skips physical-only nullify/evade/parry checks when `this.isPhysical_0x79 == 0`. `Battle.Voided()` (`Battle.cs:1839, 1866`) checks `target.Has(182) && (action.Reach == T.SHORT || action.Reach == T.MID)` and `target.Has(250) && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307)` WITHOUT checking `action.Physical`! In vanilla `EnemyAttackData`, **19** real enemy Magic attacks (`Pink Typhoon` `1808..1812/1854`, `Feel'n Woozy` `2151`, `Solvent` `2152..2155/2194/2196/2210/2211`, etc.) have `Range = SHORT (0)` or `MID (1)`, so `Battle.cs` wrongly allows `182` and Parry `250` to void and counter-attack them! Fix: require `action.Physical` on both `182` and `250` checks in `Voided()`.
  - **`M03.05b` (`S2`) — Damage Cap `296` only checks `action.TryVal(296)` rather than `actorMergedCmds` (`Battle.cs:2025`):** All `34` vanilla uses of `296` are on Skills/EnemyAttacks (`S2`). *(Verified matching: missed-spell grazing `dmg * 3 / 4` with enchant `272` else `dmg / 2` trunc0, `<= 0` -> `Rand(5) + 1` floor roll, `Magic Hit Determination (25)` skipping damage/graze on miss, Elemental Nullify enchants `124..128`, and Status `192` bypassed by `T.NEUTRAL` attribute `9` before Alter Fate `349` and Barriers `101/102/181`.)*

`engine_cs/src/DtEngine/Battle.cs:1838`
```csharp
            if (target.Has(192) && attr != T.NEUTRAL) return true;
            if (target.Has(182) && (action.Reach == T.SHORT || action.Reach == T.MID)) return true;
...
            if (target.Has(250) && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
            {
                if (Roll(target.Value(250)))
                {
                    Counter(target, unit);
                    return true;
                }
            }
```

## Part: M04–M07 (Hit/Evasion/Targeting, Healing/Items, Status Lifecycle & Ailments)


> **Scope:** 49 Clean-Room Binary Spec rules (`M04.01..M04.16`, `M05.01..M05.13`, `M06.01..M06.08`, `M07.01..M07.12`) diffed against `engine_cs/src/DtEngine/`, `tools/item_effect_data.py`, `tools/enemy_data.py`, `tools/engine_export.py`, and `gamedata/data.py`.
> **Verdict Summary (49 rules):** `MATCH=6`, `S0=11`, `S1=29`, `S2=3`, `MODEL-LIMIT=0`.

---

## M04 — Hit / Evasion, Targeting Scopes, Formation & Binary Legality (`M04.01` – `M04.16`)

### M04.01 Physical Attack Hit Rate, Modifiers & Stab Evasion (`CBattle::CalcPhysicalAttack`)

**Verdict:** S1

```asm
0044aab3  add      eax, 0x64
0044aac1  mulss    xmm2, dword ptr [0x6d9378]    ; float 0.885
0044abe0  call     0x415710
0044abe9  mov      edx, 0xfd
0044adfd  mov      edx, 0xdd
0044ae84  movss    xmm0, dword ptr [0x6d9434]    ; float 5
0044ae8c  movss    xmm2, dword ptr [0x6d9540]    ; float 100
```

- **M04.01a (S1):** For `Attr == 0` (`WEAPON_ATTR`) enemy attacks, `Action.PhysicalAttr` falls back to `Actor.AttackAttr` (`Attacks[0].Attr`), whereas binary `Action_s::IsAttributeStab` (`0x415710`) checks `EnemyAttackParam.attr == 2` directly without falling back to `Attacks[0]`. This falsely triggers Stab Evasion (`253`) on 16 vanilla enemies (e.g., Odin, Paladin, Royal Guard, Seraph, Titania) whose `Attacks[0]` is Stab and who carry an `Attr == 0` attack.
  - **Fix:** In `Action.PhysicalAttr`, return `a` directly for `Atk != null` without falling back to `Actor.AttackAttr` when `a == T.WEAPON_ATTR`.
- **M04.01b (S2):** `F.PhysicalHit` computes in `f64` (`double`) instead of x86 `f32` (`0.885f`, `mulss`/`divss`), causing rare 1-point truncation boundary differences before `trunc0`.
  - **Fix:** Compute `F.PhysicalHit` terms in `float` (`f32`) matching `0x44aabe..0x44aeab`.

engine_cs/src/DtEngine/Action.cs:314
```csharp
        public int PhysicalAttr
        {
            get
            {
                if (Skill == null && Atk == null) return Actor.AttackAttr;
                int a = Skill != null ? Skill.Attr : Atk.Attr;
                if (a == T.NONE || a == -1 || a == T.WEAPON_ATTR) return Actor.AttackAttr;
                return a;
            }
        }
```

engine_cs/src/DtEngine/Formulas.cs:233
```csharp
        public static double PhysicalHit(double dex, double targetAgi, double skillAccuracy, double buffs, double targetBuffs,
                                         double enchant, double targetEnchant, double divisor)
        {
            double a = HIT_SCALE * (100 + dex) / (100 + targetAgi) + skillAccuracy;
            double b = (buffs - targetBuffs + a) * 100;
            return Clamp((b + enchant - targetEnchant) / divisor, HIT_MIN, HIT_MAX);
        }
```

---

### M04.02 Physical Hit Overrides, Age Flags, `trunc0_u32` Roll & `Furious Strike` (`348`)

**Verdict:** S1

```asm
0044aef3  mov      edx, 0x37
0044af34  mov      edx, 0x48
0044af83  mov      eax, dword ptr [eax + 0xbc]
0044afde  mov      edx, 0x95
0044b070  mov      edx, 0x96
0044b0f3  call     0x490790
0044b100  call     0x61e650
0044b108  jb       0x44b221
0044b12a  mov      edx, 0xfd
```

- **M04.02a (S1):** `Battle.Hits` invents a free `Counter(target, action.Actor)` whenever `Physical Stab Evasion (253)` causes a miss (`roll < chance * 100`). In the vanilla binary (`0x44b124..0x44b20f`), `253` has only two askers (`0x44abe9`, `0x44b12a`) and ONLY logs the passive activation message — it NEVER queues a counterattack. Reach: Maiden passive `253` (`1` vanilla passive) vs any Stab attack.
  - **Fix:** Remove the `Counter(target, action.Actor)` call from `Battle.Hits`.
- **M04.02b (S2):** `if (action.Furious) return true;` short-circuits `Battle.Hits` before `HitChance`, skipping age-gate overrides (`149`/`150`) and skipping the `Rand(100)` RNG draw (`0x44b0f3`). In the binary (`0x42105b..0x4210b7`), `Furious Strike (348)` synthesizes `Cmd 69` + `Cmd 72 (1.0f)`, which still passes through `149`/`150` and draws `Rand(100)`.
  - **Fix:** Apply `action.Furious` as a `Cmd 72 (1.0)` override inside `HitChance` rather than short-circuiting `Hits`.
- **M04.02c (S2):** `else if (action.Has(72))` runs for both physical (`roll == 1`) and magical (`roll == 2`) hits, whereas `CalcMagicalAttack` never queries `Cmd 72`.
  - **Fix:** Gate `action.Has(72)` on `roll == 1`.

engine_cs/src/DtEngine/Battle.cs:1888
```csharp
        bool Hits(Action action, Unit target)
        {
            if (action.Furious) return true;
            double chance = HitChance(action, target);
            double dodge = StabDodge(action, target);
            int roll = Rng.RandRange(100);
            if (roll < PyMath.Round((chance - dodge) * 100)) return true;
            if (dodge != 0 && roll < PyMath.Round(chance * 100) && target.Alive) Counter(target, action.Actor);
            return false;
        }
```

engine_cs/src/DtEngine/Battle.cs:2298
```csharp
            if (action.Has(55)) chance = action.Val(55, 0) * 100;
            else if (action.Has(72)) chance = action.Val(72, 0) * 100;
            if (roll == 1) chance = F.Clamp(chance, F.HIT_MIN, F.HIT_MAX);
            if (target.St[116] != null) chance = 100.0;
```

---

### M04.03 Magical Attack Hit Rate, Modifiers, Overrides, Graze & `Cmd 25` (`Magic Hit Determination`)

**Verdict:** S1

```asm
0044d63f  mulss    xmm0, dword ptr [0x6d92cc]    ; float 0.002
0044da2b  movss    xmm0, dword ptr [0x6d9498]    ; float 25
0044da37  movss    xmm1, dword ptr [0x6d9534]    ; float 95
0044da58  cmp      eax, 0x37
0044ed8c  call     0x490790
0044ed91  cvttss2si ecx, dword ptr [ebp + 0x54]
0044ed98  setge    byte ptr [ebp + 0x47]
00421a83  mov      edx, 0x19
```

- **M04.03a (S1):** `Battle.Resolve` runs `Hits()` and `Voided()` BEFORE `MagicDamageActual()`, reversing the binary RNG order (`Swing -> Hit -> Crit -> MinDmg` at `0x44dbc3..0x44ee87` becomes `Hit -> Crit -> Swing -> MinDmg`) and skipping Swing/Crit/MinDmg RNG draws entirely whenever a spell is Voided (`192`, `182`, `349`, `285`, `101/102/181`, or nullify enchants `124..128`). Reach: 39 Magic skills + 603 Magic EnemyAttacks.
  - **Fix:** Compute raw magic damage (including spell swing) before the magic hit roll, and evaluate `Voided` after `CalcMagicalAttack` produces the damage result.
- **M04.03b (S2):** `Battle.HitChance` applies `Cmd 72` (`Physical Accuracy Fixed Modifier`) when `roll == 2` (Magic), whereas `CalcMagicalAttack` (`0x44da58`) checks only `Cmd 55`. Reach: 0 Magic skills carry `Cmd 72` in vanilla.
  - **Fix:** Restrict `action.Has(72)` to `roll == 1`.

engine_cs/src/DtEngine/Battle.cs:1758
```csharp
                bool landed = Hits(action, target);
                Trace?.Hit(this, action, target, landed);
                if (!landed)
                {
                    // 0x421ab9..0x421ade, 0x44f0a0: a missed damaging spell (incl. special-damage magic) still checks Voided,
                    // deals grazed (or full special) damage, and runs AfterHit (ailments, drains, reactive triggers).
                    if (!action.Magic || !Aimed(action, target) || action.Has(25) || Voided(action, target)) return;
```

engine_cs/src/DtEngine/Battle.cs:2241
```csharp
        int MagicDamageActual(Action action, Unit target, out bool critical)
        {
            var unit = action.Actor;
            critical = !spellMissed && unit.Has(301) && Rng.RandRange(100) < F.MAGIC_CRIT_CHANCE;
            double value = MagicValue(action, target, false, critical ? F.MAGIC_CRIT_FACTOR : 1.0, critical, out int zero);
```

---

### M04.04 Post-Hit Physical Evasion & Negation Hooks: Parry (`180`) & Counter-Evade (`250`)

**Verdict:** S1

```asm
004223b5  cmp      byte ptr [esi + 0x79], 0
004223c2  call     0x416ea0
004223d4  push     0xb4
00422559  cmp      byte ptr [eax + 0x11], 0
0042256d  cmp      eax, 1
00422582  push     0x133
00422596  push     0xfa
```

- **M04.04a (S1):** `Battle.Voided` checks Counter-Evade (`250`) WITHOUT guarding on `!inCounter` (`0x422559 cmp byte ptr [eax + 0x11], 0`). When a counterattack hits a unit carrying `250`, `Battle.Voided` still rolls `250`, calls `Counter()` (which returns early because `inCounter == true`), and then returns `true` — completely voiding the counterattack instead of bypassing `250`. Reach: `Eff 250` (`Passive: 1`, `EnemyAttack: 3`) vs any counterattacking opponent.
  - **Fix:** Add `!inCounter` to the `target.Has(250)` guard in `Battle.Voided`.

engine_cs/src/DtEngine/Battle.cs:1861
```csharp
            if (target.St[180] != null && action.Physical && attr != T.NEUTRAL)
            {
                if (Roll(target.St[180].Value)) target.PopStatus(180);
                return true;
            }
            if (target.Has(250) && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
            {
                if (Roll(target.Value(250)))
                {
                    Counter(target, unit);
                    return true;
                }
            }
```

---

### M04.05 Attack Range Determination & Row Distance Revision (`SetAttackRange`, `_GetAttackRangeRevision`)

**Verdict:** MATCH

```asm
0041817a  call     0x559290
00418246  test     al, 1
004183fc  shr      eax, 7
0044a7a4  mov      cl, byte ptr [eax + 0x79]
0044a7ee  mov      dword ptr [esp], 0x3f000000
0044a808  mov      dword ptr [esp], 0x3f400000
0044a820  mov      dword ptr [esp], 0x3f800000
```

Weapon Near/Mid/Far flags (`0x2`/`0x4`/`0x8`, default Near when unarmed), Technique bits `0..2` / Magic Ignore, EnemyAttack bits `7..9`, row distance `0/1/2`, and Near (`1.0/0.75/0.5`) / Mid (`1.0/1.0/0.75`) / Far-Ignore (`1.0`) multipliers match the binary faithfully.

engine_cs/src/DtEngine/Formulas.cs:315
```csharp
        public static int Distance(bool attackerBack, bool targetBack) => (attackerBack ? 1 : 0) + (targetBack ? 1 : 0);

        public static double RangeFactor(int attackRange, int dist)
        {
            if (attackRange == SHORT) return dist == 0 ? 1.0 : dist == 1 ? 0.75 : 0.5;
            if (attackRange == MID) return dist == 2 ? 0.75 : 1.0;
            return 1.0;
        }
```

gamedata/data.py:165
```python
def _skill_range(category, group):
    if category != 'Technique' or group is None:
        return NO_RANGE if category == 'Magic' else None
    for bit, value in ((1, SHORT), (2, MID), (4, LONG), (8, NO_RANGE)):
        if group & bit:
            return value
    return NO_RANGE
```

---

### M04.06 Master Target Pool Collector, Liveness Predicate & Unit-Type Filtering (`0x43e6d0`, `0x43b580`)

**Verdict:** S0

```asm
0043e72d  cmp      eax, 0x7d0
0043e77d  mov      eax, dword ptr [eax + 0xe8]
0043b5c2  mov      eax, dword ptr [eax + 0xe8]
004fbd95  mov      eax, dword ptr [eax + 0x38]
004fbda2  mov      eax, dword ptr [eax + 0xc8]
004fb633  cmp      eax, 3
```

- **M04.06a (S0):** Fundamental liveness-predicate bug: binary `CBattleBase::_CollectUnits` (`0x43e77d`) and `_IsTargetValid` (`0x43b5c2`) both call `vtable+0xe8` (`IsAliveAndNotPetrified = !IsDead() && !IsFullPetrified()`). In the simulator, `Battle.Build` and `Battle.TargetableArray` check ONLY `u.Alive` (`Hp > 0`), leaving Stage-3 Petrified units (`St[120].Stage >= 3`) inside all alive target pools, aggro weights, AoE/Row/Pierce scopes, Cover candidates, and healing pools. Reach: `Eff 120` (68 uses) + `Eff 121` (7 uses).
  - **Fix:** Replace `u.Alive` with `CanFight(u)` (`u.Alive && !(u.St[120] != null && u.St[120].Stage >= 3)`) in `TargetableArray`, `Build(aliveOnly=true)` / `SideArray`, and invalidate `roster.Version` whenever Stage-3 petrification is entered or cured.

engine_cs/src/DtEngine/Battle.cs:438
```csharp
        Unit[] Build(int side, bool aliveOnly)
        {
            int n = 0;
            foreach (var u in Units) if (u.Side == side && (u.Alive || !aliveOnly)) n++;
            var r = new Unit[n];
            int k = 0;
            foreach (var u in Units) if (u.Side == side && (u.Alive || !aliveOnly)) r[k++] = u;
            return r;
        }
```

engine_cs/src/DtEngine/Battle.cs:460
```csharp
        public Unit[] TargetableArray(int side)
        {
            Refresh();
            ref Unit[] slot = ref (side == Unit.PARTY ? ref targetable0 : ref targetable1);
            if (slot != null) return slot;
            var alive = SideArray(side, true);
            int n = 0;
            foreach (var u in alive) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) n++;
            var r = new Unit[n];
            int k = 0;
            foreach (var u in alive) if (u.Kind != Kind.Doll && u.Kind != Kind.Summon && u.Kind != Kind.Npc) r[k++] = u;
            slot = r;
            return r;
        }
```

---

### M04.07 Master Target Scope Resolution (`0x43f450`, TargetTypes `0..15`, Heal AI & Multi-Hit Deduplication `112`)

**Verdict:** S1

```asm
0043f4c5  jmp      dword ptr [eax*4 + 0x43fde8]
0043f6bf  divss    xmm1, xmm0
0043f6c8  comiss   xmm0, xmm1
0043f6cb  jb       0x43f6e3
0043f7e2  jmp      dword ptr [eax*4 + 0x43fe04]
0043f859  call     0x505ad0
0043f946  call     0x490790
0043fc29  comiss   xmm0, xmm1
```

- **M04.07a (S1):** `Battle.OwnSidePick` omits the Ally-Heal AI branch (`0x43f541..0x43f7a5`) when `chosen == null`: for enemy heals (`9, 103, 104, 128, 131, 138`) with `TargetType 5` (52 EnemyAttacks) or `7` (11 EnemyAttacks), `OwnSidePick` picks a uniform random ally instead of the lowest HP% ally (ties keeping later unit).
  - **Fix:** Pass `isHeal` (`action.Has` any of `9, 103, 104, 128, 131, 138`) into `OwnSidePick` and select lowest `HpRatio` (ties keeping later unit, `<=`) when `chosen == null`.
- **M04.07b (S1):** `Battle.Targets` uses `OwnSideAll(unit.Side)` for `105 || 106` on BOTH sides. Because dead enemies remain in `Units` with `Alive = false` in C# (whereas binary `_RemoveUnit` deletes dead enemies), enemy Nurse (`106`, 18 EnemyAttacks) can target dead enemies.
  - **Fix:** Use `OwnSideAll` only for `unit.Side == Unit.PARTY` (or only for `105` on enemies if enemy revive is allowed; dead enemies are absent from `battle.units` in binary).
- **M04.07c (S1):** `Battle.Perform` multi-hit random expansion (`if (action.TargetCode == T.RANDOM)`) omits `T.RANDOM_ALLY` (`6`, `Roulette Circus Effect 113`), ignores forced `action.Target` on `T.RANDOM` (158 skills/attacks), and skips the initial `chosenUnit` RNG draw (`0x43f7aa..0x43f892`).
  - **Fix:** Handle both `T.RANDOM` and `T.RANDOM_ALLY` with forced-target collapse (`hitCount = 1`) and `112` without-replacement logic.
- **M04.07d (S2):** `TargetType 11` (Lowest HP% across all combatants) and `13` (Special Single, `Identify 53`) are unhandled and fall through to Self (`return new[] { unit };`); `T.ALLY_MOST_TP_LOST (12)` returns `new[] { null }` if `friends` is empty; `T.ANYONE (15)` ignores forced target; `T.EVERYONE (14)` ignores `targetSide`-first ordering.
  - **Fix:** Add explicit cases for `11` and `13`, guard empty `friends` in `12`, honor forced target in `15`, and order `targetSide` first in `14`.

engine_cs/src/DtEngine/Battle.cs:1454
```csharp
        Unit OwnSidePick(Unit chosen, Unit[] candidates)
        {
            if (candidates.Length == 0) return null;
            if (chosen != null)
            {
                if (Array.IndexOf(candidates, chosen) >= 0) return chosen;
                Unit lowest = null; double ratio = 1.0;
                foreach (var u in candidates) if (u.HpRatio <= ratio) { ratio = u.HpRatio; lowest = u; }
                return lowest ?? candidates[candidates.Length - 1];
            }
            return candidates[Rng.ChoiceIndex(candidates.Length)];
        }
```

engine_cs/src/DtEngine/Battle.cs:1482
```csharp
            var friends = action.Has(105) || action.Has(106) ? OwnSideAll(unit.Side) : TargetableArray(unit.Side);
```

engine_cs/src/DtEngine/Battle.cs:1301
```csharp
            if (action.TargetCode == T.RANDOM)
            {
                var pool = targets;
```

---

### M04.08 Player Menu Target Selection & Item Scopes (`CBattleMenuSelectTarget` `0x456ff0`, TargetTypes `0..18`)

**Verdict:** S0

```asm
0045702f  cmp      eax, 0x12
00457038  jmp      dword ptr [eax*4 + 0x457648]
00453454  lea      eax, [ecx - 0x10]
00453457  cmp      eax, 2
004534be  call     0x55b640
0055b65c  mov      eax, dword ptr [eax + 0x30]
0055b65f  shr      eax, 4
```

- **M04.08a (S0):** Systemic data-pipeline omission: `ItemData` `w_0x5c` (`targetType` in `{16 Single, 17 Row, 18 SideAll}`) and `Flags_0x18` (`canTargetEnemies` bit 4) are dropped across `gamedata/data.py`, `tools/engine_export.py`, `Loader.cs`, and `Data.cs`. Consequently, `Battle.UseItem` NEVER expands Row (`17`, 9 battle-usable items) or SideAll (`18`, 59 battle-usable items) targets across the row or side, applying cure/revive/skill/offensive items to only a single target.
  - **Fix:** Export `target_type` (`w_0x5c`) and `flags` (`Flags_0x18`) in `gamedata/data.py` -> `engine_export.py` -> `Loader.cs` -> `Data.Item`, and expand `16`/`17`/`18` target lists in `Battle.UseItem`.
- **M04.08b (S1):** Player menu target selection (`0x4571eb`, `0x45733d`) rolls `action.hitCount` uniform targets for `TargetType 6` (`RANDOM_ALLY`) and `TargetType 15` (`ANYONE`), whereas `Battle.Perform` only expands multi-hit random targets for `T.RANDOM (1)`.
  - **Fix:** Expand `hitCount` random targets for `T.RANDOM_ALLY (6)` and `T.ANYONE (15)` alongside `T.RANDOM (1)`.

gamedata/data.py:281
```python
    for r in _rows(wb, 'Items'):
        # Preserve the fixed 4-slot layout (slots 0-1 ally, slots 2-3 enemy; 0x55b550) alongside filtered 'effects'
        slots = [(-1 if r[f'Eff{k}_Type'] is None else r[f'Eff{k}_Type'], r[f'Eff{k}_Value'] or 0) for k in range(1, 5)]
        data.items[r['Item_ID']] = {'name': r['Name'], 'price': r['Buy_Price'],
                                    'effects': [(t, v) for t, v in slots if t != -1],
                                    'slots': slots}
```

engine_cs/src/DtEngine/Data.cs:213
```csharp
    public sealed class Item
    {
        public int Id;
        public string Name;
        public int[] Kinds;
        public double[] Values;
    }
```

---

### M04.09 Enemy Action Target Selection, Mid-Action Retarget Fallback & Splash (`137`)

**Verdict:** S0

```asm
0042052a  call     0x43b580
0042061b  jmp      dword ptr [edi*4 + 0x420868]
004206b7  call     0x490790
0042017a  mov      edx, 0x89
004201e0  call     0x43ad50
0041a973  call     0x490790
```

- **M04.09a (S0):** Fundamental action-pipeline omission: `Battle.Perform` has ZERO mid-action retarget fallback (`CActionPatternBase::_SelectTarget` `0x420560..0x420893`). When a target dies mid-multi-hit (or is killed by pre-attack Counter Whip `303`) on `TargetType 0, 1, 5, 6` or before hit 0 of `TargetType 3` (Pierce), `Battle.cs:1349` executes `break;` and discards all remaining hits instead of uniformly retargeting another living unit on that side. Fires in virtually every battle with Double/Triple Attack or multi-hit skills.
  - **Fix:** Implement `_SelectTarget` uniform retarget fallback inside the hit loop for `TargetType 0, 1, 5, 6` (and pre-hit-0 `3` Pierce rebuild) when the current target is invalid.
- **M04.09b (S1):** `Cmd 137` (`EXTRA_TARGETS`, 15 uses: 1 Tech + 14 EnemyAttacks) breaks immediately upon encountering an opposite-side unit (`if (nxt.Side != chosen.Side) break;`), whereas binary `0x42017a..0x4202ff` skips opposite-side units and keeps scanning `battle.units` until `extraCount` same-side targets are appended.
  - **Fix:** Replace `break;` with `continue;` and track `added < extra` instead of `step <= extra`.
- **M04.09c (S1):** When a chanted enemy attack's target dies before resolution, `Battle.Targets` calls aggro-weighted `PickOpponent`, whereas binary `CActionEnemyAttack::_SelectTarget` (`0x41a850`, `0x41a973`) draws uniformly (`GlobalRng.Rand(pool.size())`).
  - **Fix:** Use uniform random retargeting when re-selecting a dead target for a chanted enemy attack.

engine_cs/src/DtEngine/Battle.cs:1345
```csharp
            foreach (var target in targets)
            {
                for (int h = 0; h < hits; h++)
                {
                    if (!unit.Alive || (!target.Alive && !action.Has(105))) break;
                    Resolve(action, target, index);
                    index++;
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:1501
```csharp
                            for (int step = 1; step <= extra && idx + step < all.Count; step++)
                            {
                                var nxt = all[idx + step];
                                if (nxt.Side != chosen.Side) break;
                                res.Add(nxt);
                            }
```

---

### M04.10 Target Redirection: Physical Cover (`171`) & Absence of `172` / `324` / Magic Cover

**Verdict:** S1

```asm
00420b70  cmp      byte ptr [ecx + 0x79], 0
00420bcc  cmp      eax, 1
00420be2  cmp      byte ptr [ebx + 0x44], 0
00420ca7  call     0x490790
00420eb3  mov      byte ptr [ebp - 0x14], 1
0042496e  cmp      byte ptr [eax + 0x44], 0
004249a6  call     0x490790
```

- **M04.10a (S1):** `Battle.Resolve` invokes `Redirect()` on EVERY hit `h = 0..hits-1` of a multi-hit single-target attack, incrementing `covered` count per hit. In the binary (`0x420be2..0x420eb3`), `_Cover` checks `slot.wasCovered` (`[slot+0x44]`), replaces `slot.target` ONCE for all hits in that slot, and rolls wear-off ONCE per slot (`0x42496e`). Reach: Paladin `Cover (171)` vs any multi-hit single-target enemy attack.
  - **Fix:** Run `Redirect` once per target slot before the `for (int h = 0; h < hits; h++)` loop and set a per-slot `wasCovered` flag.
- **M04.10b (S1):** `Battle.Perform` defers Cover (`171`) wear-off rolls until AFTER the entire action (`Battle.cs:1354-1362`). In the binary (`0x42496e`), `_CheckAfterAttackInterrupt` rolls wear-off after EACH target slot, so on a multi-slot `T.RANDOM` attack Cover can wear off on slot 0 and no longer cover slot 1.
  - **Fix:** Roll Cover wear-off immediately after each covered target slot completes.

engine_cs/src/DtEngine/Battle.cs:1354
```csharp
            for (int ci = 0; ci < covered.Count; ci++)
            {
                var (cover, count) = covered[ci];
                for (int j = 0; j < count; j++)
                {
                    var s = cover.St[171];
                    if (s != null && Roll(s.Value)) cover.PopStatus(171);
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:1756
```csharp
                target = Redirect(action, target);
                if (target == null) return;
```

---

### M04.11 Formation Table (`FormationShareTable` `0x6517a0`), Row Assignment & Enemy Front-Row Wipe Shift

**Verdict:** S1

```asm
0043dac7  lea      eax, [eax*4 + 0x6517a0]
0043db35  mov      dword ptr [edi + 0x74], eax
0043db42  mov      byte ptr [edi + 0x79], al
0043b7b6  call     0x43e6d0
0043b80f  mov      byte ptr [ecx + 0xa4], 1
0043b84c  mov      byte ptr [edx + 0x79], 1
```

- **M04.11a (S1):** `FormationShareTable` (`F.TARGET_SHARE`) and battle-start `BaseTargetShare` assignment match `0x6517a0`, and player formation stays fixed mid-battle. HOWEVER, **Enemy Front-Row Wipe Shift (`CBattleBase::_RemoveUnit` `0x43b7a8..0x43b865`) is COMPLETELY MISSING** from `Battle.Fall` (and from self-destruct/escape removal paths `12`/`11`/`432`). Whenever all front-row enemies die in a 2-row encounter (60 fixed battles + 1,442 random formations), back-row enemies remain stuck at `Front = false`, imposing permanent `0.75x`/`0.50x` melee range penalties and corrupting AI front/back queries (`Source 8/9`, `Target 7/10`).
  - **Fix:** Whenever an enemy unit dies/leaves battle, check if any living enemy has `Front == true`; if none remain, set `u.Front = true` on all living back-row enemies.

engine_cs/src/DtEngine/Formulas.cs:197
```csharp
        public static readonly int[][] TARGET_SHARE =
        {
            new[] { 100 }, new[] { 50, 50 }, new[] { 60, 40 }, new[] { 33, 34, 33 }, new[] { 38, 38, 24 }, new[] { 40, 30, 30 },
            new[] { 28, 28, 28, 16 }, new[] { 30, 30, 20, 20 }, new[] { 31, 23, 23, 23 }, new[] { 24, 24, 24, 14, 14 },
            new[] { 26, 26, 16, 16, 16 },
        };
```

engine_cs/src/DtEngine/Battle.cs:2633
```csharp
            unit.Alive = false;
            unit.Chant = null;
            unit.ClearStatuses();
```

---

### M04.12 Pierce / Column Adjacency Graph (`CBattleBase::_SetPierceTarget` `0x43def0`)

**Verdict:** MATCH

```asm
0043df4e  cmp      ecx, eax
0043e0ba  shr      edx, 1
0043e1bf  add      edi, 0x17
0043e433  add      edi, -0x19
00439e11  mov      ecx, 0x400
00439e1e  mov      eax, 0x3e8
```

Player pierce adjacency in `Battle.Behind` (`|j - (other.Count - 1)/2 - (at - (mine.Count - 1)/2)| <= 0.5`) is algebraically identical to `0x43df22..0x43e40f` across all 11 formations (`diff in {0, 1, 2}`), and enemy pierce adjacency (`u.Front != unit.Front && Math.Abs(u.Slot - unit.Slot) <= 1`) matches `[id + 0x17..+0x19]` / `[id - 0x19..-0x17]` (`0x3e8+k` vs `0x400+k`) across all fixed and random formations.

engine_cs/src/DtEngine/Battle.cs:1592
```csharp
        public List<Unit> Behind(Unit unit)
        {
            if (unit.Side == Unit.ENEMIES && unit.Slot != T.NONE)
            {
                var r = new List<Unit>();
                foreach (var u in Units)
                    if (u.Side == Unit.ENEMIES && u.Kind == Kind.Enemy && u.Alive && u.Front != unit.Front && u.Slot != T.NONE && Math.Abs(u.Slot - unit.Slot) <= 1) r.Add(u);
                return r;
            }
...
            double centre = at - (mine.Count - 1) / 2.0;
            var res = new List<Unit>();
            for (int j = 0; j < other.Count; j++)
                if (Math.Abs(j - (other.Count - 1) / 2.0 - centre) <= 0.5 && other[j].Alive) res.Add(other[j]);
            return res;
        }
```

---

### M04.13 Target-Rate / Aggro Weighting & Weighted Selection (`CBattle::_UpdateTargetRate` `0x44a630`, `0x505ad0`)

**Verdict:** S1

```asm
0044a673  call     0x43e6d0
0044a6e1  push     0xaa
0044a727  push     0x31
0044a734  push     0x32
0044a757  cmp      ecx, 0xa
00505b35  call     0x490790
00505b43  jb       0x505b4a
```

- **M04.13a (S1):** `Battle.PickOpponent` / `WeightedPick` receives `TargetableArray(1 - unit.Side)`, which fails to exclude Stage-3 Petrified players (`St[120].Stage >= 3`), whereas `CBattle::_UpdateTargetRate` (`0x44a673`) calls `_CollectUnits(..., aliveOnly=true)` (`vtable+0xe8`). Petrified players thus inflate `total` weight and get selected as enemy targets. Reach: all battles with Petrification (`120`/`121`).
  - **Fix:** Exclude Stage-3 Petrified units in `TargetableArray` / `WeightedPick`.
- **M04.13b (S2):** `WeightedPick` draws continuous `Rng.Random() * total` instead of discrete integer `Rng.RandRange((int)total)` (`0x505b35`).
  - **Fix:** Use `int roll = Rng.RandRange((int)total);` with strict `<` prefix check.

engine_cs/src/DtEngine/Formulas.cs:338
```csharp
        public static int TargetWeight(int share, double provoked, int up, int down)
        {
            return Math.Max(ENMITY_MIN, share + PyMath.Int(provoked) + ENMITY_UP * up - ENMITY_DOWN * down);
        }
```

engine_cs/src/DtEngine/Battle.cs:1660
```csharp
            var p170 = enemy.St[170];
            for (int k = 0; k < count; k++)
            {
                var u = ordered[k];
                int share = u.BaseTargetShare > 0 ? u.BaseTargetShare : (k < fallbackRow.Length ? fallbackRow[k] : fallbackRow[fallbackRow.Length - 1]);
                double provoked = (p170 != null && p170.Source == u) ? p170.Value : 0.0;
                weights[k] = F.TargetWeight(share, provoked, u.Pieces(49), u.Pieces(50));
                total += weights[k];
            }
            double roll = Rng.Random() * total;
```

---

### M04.14 Equipment & Weapon Condition Gate (`CGamePlayerStatusBase::CheckSkillCondition` `0x4f4910`)

**Verdict:** S2

```asm
004f491a  cmp      esi, 0x14
004f4923  jmp      dword ptr [esi*4 + 0x4f4bdc]
004f4b70  push     1
004f4b8e  push     2
004f4b9f  push     3
004f4bb0  push     0
```

- **M04.14a (S2):** `Policy.WeaponAllows` faithfully implements `condType` `-1`, `0`, `1..14`, `15`, `16`, and `19`, but omits `condType 17` (`GetEquipmentID(2) != -1`, slot 2 Head/Armor equipped) and `condType 18` (`GetEquipmentID(3) != -1`, slot 3 Accessory/Body equipped). Reach: `0` vanilla skills use `condType 17` or `18` in `Skills`.
  - **Fix:** Store `HasHead` / `HasBody` (slots 2 and 3) on `Unit` and add `code == 17` and `code == 18` cases to `Policy.WeaponAllows`.

engine_cs/src/DtEngine/Policy.cs:216
```csharp
        public static bool WeaponAllows(Piece weapon, bool shield, Skill skill)
        {
            if (skill.Weapons.Length == 0) return true;
            foreach (int code in skill.Weapons)
            {
                if (code == -1) return true;
                if (code == 0 && weapon != null && weapon.Range == 0) return true;
                if (code == 15 && weapon != null && weapon.Type >= 14 && weapon.Type <= 20) return true;
                if (code == 16 && shield) return true;
                if (code == 19 && weapon != null) return true;
                if (code >= 1 && code <= 14 && weapon != null && weapon.Type + 1 == code) return true;
            }
            return false;
        }
```

---

### M04.15 Battle Skill, Item & Command Legality Gate (`0x455bc0`, `0x4fd250`, `0x515f7c`, `0x455e60`)

**Verdict:** S0

```asm
00455c86  shr      eax, 4
00455ca9  shr      eax, 3
00455cc5  mov      eax, dword ptr [eax + 0xb4]
00455d76  mov      eax, dword ptr [eax + 0xc0]
00455d94  mov      eax, dword ptr [eax + 0xd0]
004fb652  push     0x7b
004fd38f  call     0x61c040
00515fc9  shr      eax, 2
```

- **M04.15a (S0):** Fundamental/Architectural legality gap: `Battle.cs` has NO centralized `Battle.IsLegalAction(Action)` gate asserted on `Policy.Choose` inside `Battle.Turn`, AND **`Shadow Sew (123)` (`0x455d94 -> vtable+0xd0 -> 0x4fb650`) is COMPLETELY MISSING from both `Policy.Options` (including `OptionCache` key) and `Battle.NextAction`!** A Shadow-Sewed player freely casts EVERY Technique and Magic skill. Reach: `Eff 123` is used by 28 EnemyAttacks in vanilla.
  - **Fix:** Implement `Battle.IsLegalAction(Action)` covering alive/not-petrified/not-asleep, `UsableInBattle`, `WeaponAllows`, Freeze (`114`), Silence (`117`), Shadow Sew (`123`), `EffectiveTpCost <= Tp`, target legality, and battle-usable item bit 2; assert it on `ChooseMember.Choose` in `Battle.Turn`; add `ShadowSewed` (`St[123] != null`) to `Policy.OptionCache` and `Policy.ComputeOptions`.
- **M04.15b (S1):** Battle-usable item flag `Flags_0x18` bit 2 (`0x04`, `0x515fc9`) is not exported by `gamedata/data.py` or checked by `Policy.ActItem` / `Battle.UseItem`, allowing out-of-battle-only items if placed in a bag.
  - **Fix:** Export `Flags_0x18` on `Data.Item` and gate battle item usage on `(item.Flags & 0x04) != 0`.

engine_cs/src/DtEngine/Policy.cs:241
```csharp
            bool silenced = unit.St[117] != null, frozen = unit.St[114] != null;
            if (entry.List != null && entry.Owner == unit && entry.Tp == unit.Tp && entry.Silenced == silenced && entry.Frozen == frozen) return entry.List;
```

engine_cs/src/DtEngine/Policy.cs:267
```csharp
        static void ComputeOptions(Battle battle, Unit unit, bool silenced, bool frozen, List<(Skill skill, int level)> found)
        {
            found.Clear();
            bool noMagic = silenced || (battle.ZoneInfo != null && battle.ZoneInfo.NoMagic);
            int tp = unit.Tp;
            var usable = GetUsableSkills(battle.Data, unit);
            for (int i = 0; i < usable.Length; i++)
            {
                var (skill, level) = usable[i];
                if (skill.IsMagic && noMagic) continue;
                if (skill.IsTechnique && frozen) continue;
                if (Battle.EffectiveTpCost(unit, skill, level) > tp) continue;
                found.Add((skill, level));
            }
        }
```

---

### M04.16 Mid-Action Legality Downgrade on Freeze (`114`) & Silence (`117`) (`0x4208a0`)

**Verdict:** S1

```asm
00420985  mov      eax, dword ptr [eax + 0xb4]
004209a1  call     0x5574d0
004209eb  mov      eax, dword ptr [eax + 0xc0]
00420a07  call     0x557500
00420a33  mov      dword ptr [eax + 4], 1
00420a8b  mov      eax, dword ptr [eax + 0xc8]
00420ab4  mov      dword ptr [eax + 0x40], 1
```

- **M04.16a (S1):** `Battle.NextAction` returns completed chants immediately at line 1045 (before the Freeze/Silence downgrade check at lines 1052–1054), only checks `action.Skill != null` (ignoring `action.Atk`), never re-checks Freeze/Silence AFTER pre-attack Counter Whip (`303`) in `Battle.Perform`, and when downgrading replaces `action` with a fresh `new Action(unit, AKind.Attack)` (discarding the original `Target` slot and allowing Double/Triple Attack multi-hits instead of forcing `hitCount = 1` at `0x420ab4`). Reach: `Eff 114` (92 uses) + `Eff 117` (98 uses) + `Eff 303` Counter Whip / chanted techniques.
  - **Fix:** Move Freeze (`114`) / Silence (`117`) mid-action legality downgrade into `Battle.Perform` right after Counter Whip (`303`) and before hit execution, covering both `action.Skill` and `action.Atk` (downgrading enemy attacks to `Attacks[0]`), preserving `targets[0]`, and clamping `hits = 1`.

engine_cs/src/DtEngine/Battle.cs:1039
```csharp
            if (unit.Chant != null)
            {
                var chanted = unit.Chant;
                unit.Chant = null;
                chanted.Chanting = false;
                Rec?.ChantsDone.Add(new RecKey(unit), 1);
                return chanted;
            }
...
            if ((unit.St[117] != null && action.Skill != null && action.Skill.IsMagic) ||
                (unit.St[114] != null && action.Skill != null && action.Skill.IsTechnique))
                action = new Action(unit, AKind.Attack);
```

---

## M05 — Healing, Recovery, After-Battle & `ItemResult` (`0..106`) (`M05.01` – `M05.13`)

### M05.01 Stat-Scaled Magic Healing (`CCommand_0103`), Doll Scaling & Healing Cap

**Verdict:** S1

```asm
00481815  mov      eax, dword ptr [eax + 0xe8]
0048d873  call     0x490790
0048d878  add      eax, 0x30
0048d87d  push     0xf5
0048d8d3  mov      edx, 9
0048d922  call     0x48c5c0
0048c5c7  mov      edx, 0x127
0048c5e8  push     0x13d
```

- **M05.01a (S1):** `Battle.Restore` / `Battle.Heal` (`103`) check only `unit.Alive`, omitting the Stage-3 Petrification guard (`vtable+0xe8` `IsHealable` at `0x481815`), so Heal / Circle Heal (`Eff 103`, 56 uses) restores HP on Stage-3 Petrified units.
  - **Fix:** Gate `Battle.Restore` (or `Heal` `103`) on `CanFight(target)` (`!IsDead && !IsFullPetrified`).
- **M05.01b (S2):** When `Cmd 9` (`Fixed Healing`) overrides `Cmd 103`, `Battle.Heal` skips BOTH `ApplyHealCap` (`295` + `317`) and the `Rand(5)` variance RNG draw, whereas `0x48d873..0x48d922` always rolls variance and always calls `ApplyHealCap` after the `Cmd 9` override. Reach: 0 vanilla skills/attacks combine `9` and `103`.
  - **Fix:** Always roll variance first and apply `295`+`317` heal cap after checking `Cmd 9`.
- **M05.01c (S2):** `Battle.Heal` checks `IsPuppet(unit)` rather than `unit.Kind == Kind.Doll` (`0x48d73b` checks all 3 Doll RTTI types).
  - **Fix:** Check `unit.Kind == Kind.Doll && unit.Owner != null`.

engine_cs/src/DtEngine/Battle.cs:2659
```csharp
        public int Restore(Unit unit, int amount)
        {
            if (!unit.Alive || amount <= 0) return 0;
            int gained = Math.Min(unit.MaxHp - unit.Hp, amount);
            unit.Hp += gained;
            if (gained > 0) Trace?.Restore(this, unit, gained);
            return gained;
        }
```

engine_cs/src/DtEngine/Battle.cs:3138
```csharp
            if (effect == 103)
            {
                double coefficient = value;
                if (IsPuppet(unit) && unit.Owner != null)
                    coefficient += F.DollHealBonus(unit.Owner.Passive(286, 0.0), unit.Owner.Pieces(304), unit.Owner.Pieces(305));
                bool hasFixed = action.TryVal(9, out double fixedValue) && fixedValue != 0;
                int amount;
                if (hasFixed) amount = PyMath.Int(fixedValue);
                else
                {
                    double random = F.HEAL_RANDOM[Rng.ChoiceIndex(F.HEAL_RANDOM.Length)];
                    amount = F.Heal(unit.Stat(Unit.RES), coefficient, unit.Passive(245, 0.0), hasCap, cap, unit.Passive(317, 0.0), random);
                }
                Healed(unit, Restore(target, amount));
            }
```

---

### M05.02 Fixed, Percentage, TP Transfer & Nurse/Purge Healing Commands (`9`, `104`, `106`, `128`, `129`, `130`, `131`, `132`, `235`, `426`)

**Verdict:** S1

```asm
0047fbc5  mov      eax, dword ptr [eax + 0xe8]
00481aa3  call     0x61e650
00481ad3  push     dword ptr [esi*4 + 0x6cc79c]
00481b12  cmp      ecx, 8
00483ccd  mov      dword ptr [edi + 0x14], 0
00483d69  push     0x707dfc
00483e8e  call     0x48c5c0
0048b169  push     0x707da8
```

- **M05.02a (S1):** `Cmd 131` (`Heal Enemy`, `0x483d20`) strictly checks `dynamic_cast<CGameEnemyStatus*>(target) != null` (`0x483d69 push 0x707dfc`), healing ENEMIES ONLY. `Battle.Heal` omits this check and heals player targets on 6 vanilla EnemyAttacks (`971..973 Here's Some Sweets`, `2081..2083 Hospitality`).
  - **Fix:** Gate `effect == 131` on `target.Kind == Kind.Enemy && CanFight(target)`.
- **M05.02b (S1):** `Cmd 129`, `130`, and `426` omit `target.Kind == Kind.Member` (`CGamePlayerStatusBase`), `!target.Alive` (`!IsDead`), and (for `129`/`130`) `!IsFullPetrified` (`vtable+0xe8`) checks, allowing dead or Stage-3 Petrified units to receive TP. Reach: `129` (10 uses), `130` (1 Tech), `426` (1 Tech).
  - **Fix:** Gate `129`/`130` TP gain on `target.Kind == Kind.Member && CanFight(target)` (keeping `unit.Tp = 0` unconditional for `130`), and gate `426` on `target.Kind == Kind.Member && target.Alive`.
- **M05.02c (S1):** `Cmd 9, 104, 128, 132` omit the Stage-3 Petrification gate (`vtable+0xe8` `IsHealable`) via `Battle.Restore`.
  - **Fix:** Enforce `CanFight(target)` in `Battle.Restore`.
- **M05.02d (S2):** `Cmd 235` (`Perdurabo`) checks `== 8` instead of `>= 8` (`0x48a430`) and uses `PyMath.Int` instead of `0x61e650` (`round_f32_to_i32`); `Policy.ExpectedHeal` omits `unit.Passive(317, 0.0)` on `Cmd 132`.
  - **Fix:** Use `>= 8` for `235` and pass `action.Actor.Passive(317, 0.0)` to `F.FractionRecovery` in `Policy.ExpectedHeal`.

engine_cs/src/DtEngine/Battle.cs:3174
```csharp
            else if (effect == 131)
            {
                // Heal Enemy: a fixed amount, the value itself, with no cap (0x483da0 - 0x483dad)
                Healed(unit, Restore(target, PyMath.Int(value)));
            }
...
            else if (effect == 129)
            {
                target.Tp = Math.Min(target.MaxTp, target.Tp + PyMath.Int(target.MaxTp * value));
            }
            else if (effect == 426)
            {
                target.Tp = Math.Min(target.MaxTp, target.Tp + PyMath.Int(value));
            }
            else if (effect == 130)
            {
                int given = PyMath.Int(unit.Tp * value);
                unit.Tp = 0;
                target.Tp = Math.Min(target.MaxTp, target.Tp + given);
            }
```

---

### M05.03 HP/TP Clamping, Petrification Gating, TP Conversion (`257`, `E72`/`E73`) & Defend Regen (`E257`/`E292`)

**Verdict:** S1

```asm
004fbd95  mov      eax, dword ptr [eax + 0x38]
004fbda2  mov      eax, dword ptr [eax + 0xc8]
0047e64d  push     0x101
0047e689  push     0x48
0047e695  push     0x49
0047eda7  mov      eax, dword ptr [eax + 0x38]
004197ae  push     0x101
00419843  push     0x124
```

- **M05.03a (S1):** Defend regen (`E257`, `E292`) and TP Conversion rates/caps/floors (`257`, `E72`, `E73`) match the binary. However, `Battle.Restore` omits `!IsFullPetrified` (`vtable+0xe8`), and TP recovery sites in `Battle.Heal` omit `!IsDead` (`0x47eda7`). Reach: all healing/TP skills when an ally is dead or Stage-3 Petrified.
  - **Fix:** Enforce `CanFight` on HP heals and `target.Alive` on TP heals (with `CanFight` on `129`/`130`).
- **M05.03b (S2):** `Battle.TakeDamage` gates TP Conversion (`257`, `E72`, `E73`) on `amount > 0`, whereas `CCommand::Execute` (`0x47e634..0x47e750`) triggers whenever `seq[0].hpDamage != 0x7fffffff` (so 0-damage hits from Parry/Clone/Barrier System grant the 1 or 5 TP floor).
  - **Fix:** Trigger TP conversion on non-sentinel 0-damage hits as well.

engine_cs/src/DtEngine/Battle.cs:2551
```csharp
            if (target.Alive && amount > 0)
            {
                int gained = target.Has(257) ? Math.Max(1, PyMath.Int(amount * target.Value(257))) : 0;
                double share = F.TP_CONVERSION_UP * target.Pieces(72);
                int floor = F.TP_CONVERSION_FLOOR;
                if (target.Pieces(73) != 0)
                {
                    share += F.TP_CONVERSION_MINI * target.Pieces(73);
                    floor = F.TP_CONVERSION_FLOOR_73;
                }
                if (share != 0) gained = Math.Max(floor, gained + PyMath.Int(amount * Math.Min(F.TP_CONVERSION_MAX, share)));
                if (gained != 0) target.Tp = Math.Min(target.MaxTp, target.Tp + gained);
            }
```

---

### M05.04 Resurrection (`105`), Resuscitate (`188`), Undaunted Spirit (`355`), Sacrifice (`77`) & Death/Revive Hooks

**Verdict:** S1

```asm
004819a5  mov      eax, dword ptr [eax + 0x38]
0047f936  push     0xbc
0047f97c  call     dword ptr [edx + 0x20]
0043852d  push     0x163
00438668  mov      dword ptr [ebp - 0xb4], 1
004810de  mov      dword ptr [eax + edi - 0x4c], 0x7fffffff
004f5fc1  call     dword ptr [eax + 0x6c]
004f69d5  call     0x43cfb0
```

- **M05.04a (S1):** `Battle.Fall` intercepts `Resuscitate (188)` and returns EARLY before running death cleanup (`unit.Chant = null`, `unit.ClearStatuses()`, `unit.ClearSongsAndDances()`, owned doll destruction, song/dance removal). In the binary (`0x4f5fa0` -> `0x47f936`), `AddHP(-dmg)` runs `OnDeath` FIRST (wiping statuses, chants, songs, dances, geasses, and dolls) before `CCommand::Execute` revives `u` with `188`. Reach: `Magic 188` (`Resuscitate`, 1 skill).
  - **Fix:** Run death status/performance/chant/doll cleanup before reviving via `188` (saving `cmd188.Value` prior to clearing).
- **M05.04b (S1):** All revive paths (`105` Resurrect, `188` Resuscitate, `355` Undaunted Spirit, Item Type `8`) omit `OnRevive` (`0x4f6980 -> 0x43cfb0`), failing to re-apply active ally Songs (and opposing Dances/Geasses) onto the revived unit, and overwrite `NextTime = Time + Wait(target)` instead of preserving gauge and sorting (`SortTime(1, 1)`). Reach: `105` (5 uses), `188` (1), `355` (1 Unique), Revive items (4).
  - **Fix:** Add `OnUnitRevived(unit)` to re-sync active Songs/Dances/Geasses on revive.
- **M05.04c (S2):** `Sacrifice (77)` (`Battle.cs:1399`) executes `LoseHp(unit, unit.MaxHp, unit)` after `103` already healed the caster in `Primevil (Magic 230)` instead of wiping prior self HP heals in `seq` (`0x4810de`), inflating `Rec.Healing` and firing even if `actor` wasn't targeted.
  - **Fix:** Suppress self-heals on `actor` when `action.Has(SACRIFICE)` and gate Sacrifice on `target == actor`.

engine_cs/src/DtEngine/Battle.cs:2624
```csharp
        void Fall(Unit unit, Unit source)
        {
            if (unit.Has(188) && unit.St[188] != null)
            {
                double value = unit.PopStatus(188).Value;
                unit.Hp = Math.Max(1, PyMath.Int(unit.MaxHp * value));
                return;
            }
```

engine_cs/src/DtEngine/Battle.cs:3161
```csharp
            else if (effect == 105)
            {
                if (!target.Alive)
                {
                    target.Alive = true;
                    target.Hp = Math.Max(1, PyMath.Int(target.MaxHp * value));
                    target.NextTime = Time + Wait(target);
                }
            }
```

---

### M05.05 HP & TP Drain Commands (`75`, `76`) & Normal-Attack Drain Enchants (`161..164`)

**Verdict:** MATCH

```asm
00421547  push     0xa1
0042156f  movss    xmm2, dword ptr [0x6d9348]    ; float 0.5
004215c4  movss    xmm2, dword ptr [0x6d931c]    ; float 0.15
00421619  movss    xmm2, dword ptr [0x6d9324]    ; float 0.2
0042166e  movss    xmm2, dword ptr [0x6d92ec]    ; float 0.05
00422efe  call     0x557e00
00422f1a  mov      eax, dword ptr [eax + 0xfc]
00557e1c  cmp      dword ptr [eax + 0x28], 5
```

Normal-attack drain enchant synthesis (`161>162` for `75` at `0.50/0.15`, `163>164` for `76` at `0.20/0.05`), Undead (`Race == 5`) and Doll (`Kind.Doll`) exclusions, HP drain cap at pre-hit HP with floor 1, and player-only TP drain/restore with floor 1 match the binary faithfully.

engine_cs/src/DtEngine/Formulas.cs:57
```csharp
        public static readonly (int enchant, int effect, double value)[] PLAIN_ATTACK_ENCHANTS =
        {
            (161, 75, 0.5), (162, 75, 0.15), (163, 76, 0.2), (164, 76, 0.05),
```

engine_cs/src/DtEngine/Battle.cs:2703
```csharp
                if (effect == 75 && dealt != 0)
                {
                    // 0x422ef2..0x4230b3: HP Drain skips Undead (race 5), dolls, and dead actors; floor 1, capped at target's pre-hit HP.
                    if (target.Race != 5 && unit.Kind != Kind.Doll && unit.Alive)
                    {
                        int drained = Math.Min(preHp, Math.Max(1, PyMath.Int(dealt * value)));
                        Restore(unit, drained);
                    }
                    continue;
                }
                if (effect == 76 && dealt != 0)
                {
                    // 0x422ef2..0x4230b3: TP Drain skips Undead (race 5), dolls, and dead actors; floor 1; subtracts from player target TP.
                    if (target.Race != 5 && unit.Kind != Kind.Doll && unit.Alive)
                    {
                        int drained = Math.Max(1, PyMath.Int(dealt * value));
                        if (target.Kind == Kind.Member) target.Tp = Math.Max(0, target.Tp - drained);
                        if (unit.Kind == Kind.Member) unit.Tp = Math.Min(unit.MaxTp, unit.Tp + drained);
                    }
                    continue;
                }
```

---

### M05.06 Turn-Start HoT Commands (`215`, `216`, `246`, `247`), Regen Enchants (`144..149`, `296`) & Poison DoT (`113`)

**Verdict:** MATCH

```asm
00437be9  mulss    xmm0, dword ptr [0x6d92e8]    ; float 0.04
00437c53  mulss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
00437cbd  mulss    xmm0, dword ptr [0x6d9300]    ; float 0.08
00437d1a  cmp      eax, 4
004894f1  mulss    xmm0, dword ptr [0x6d9468]    ; float 10
00489658  mulss    xmm0, dword ptr [0x6d9540]    ; float 100
00482197  mulss    xmm0, dword ptr [0x6d92ec]    ; float 0.05
004821ed  mov      eax, 0xfa
```

Carol (`215`: `val * (1 + 10 * sb)`), Chorale (`216`: `val + 100 * sb`), HP Regen (`246`: `% MaxHp`), TP Regen (`247`: flat TP), equipment HP/TP regen enchants (`144/145/148/296` in `f32`, `146/147/149`), and Poison DoT (`113`: 5% MaxHp capped at 250, non-lethal `Hp - 1`, skipped while asleep `St[116] != null`, 0 `f32`/`f64` diffs across `1..6000` HP) match the binary faithfully.

engine_cs/src/DtEngine/Battle.cs:1164
```csharp
                else if (effect == 215)
                {
                    double bonus = s.HasData ? s.Data : 0.0;
                    Restore(unit, PyMath.Int(s.Value * (1 + 10 * bonus)));
                }
                else if (effect == 216 && unit.Side == Unit.PARTY)
                {
                    double bonus = s.HasData ? s.Data : 0.0;
                    unit.Tp = Math.Min(unit.MaxTp, unit.Tp + PyMath.Int(s.Value + 100 * bonus));
                }
```

engine_cs/src/DtEngine/Battle.cs:1212
```csharp
            if (unit.Alive && unit.St[113] != null && unit.St[116] == null)
            {
                int amount = Math.Min(POISON_CAP, PyMath.Int(unit.MaxHp * POISON_SHARE));
                if (amount <= 0 || amount >= unit.Hp) amount = unit.Hp - 1;
                LoseHp(unit, amount, null);
            }
```

---

### M05.07 `CBattleBase::End` Party Recovery (`272`, `273`, `353`, `E193`, `E194`) & `ClearBattleStatuses` (`vtable+0x70`)

**Verdict:** S0

```asm
0043d6bc  mov      edx, dword ptr [edx + 0xe8]
0043d6cc  push     0x110
0043d6e8  push     0x161
0043d751  movss    xmm0, dword ptr [0x6d9330]    ; float 0.3
0043d85e  push     0xc1
0043d904  push     0xc2
004fa989  mov      eax, dword ptr [eax + 0x68]
004faa30  call     0x56c5e0
```

- **M05.07a (S0):** Fundamental battle-row status lifecycle bug: `Scenario.PlayRun` calls `unit.ClearStatuses()` unconditionally before every battle in a multi-battle chain, wiping all true ailments (`113..122`, `139`) and out-of-battle persistent buffs (`0x56c5e0`). Binary `ClearBattleStatuses` (`0x4fa960`) explicitly preserves all true ailments (`cmd.vtable+0x68() == 1`) and persistent skill buffs between battles. Reach: every random-battle walk and multi-phase boss chain.
  - **Fix:** Replace `unit.ClearStatuses()` between consecutive battles with `ClearBattleStatuses()` that preserves true ailments (`113..122`) and out-of-battle persistent buffs.
- **M05.07b (S1):** `Scenario.RecoverAfterBattle` filters `living` using `u.Alive && u.Kind == Kind.Member`, omitting `!IsFullPetrified` (`vtable+0xe8` at `0x43d6bc`). Stage-3 Petrified members thus wrongly contribute `272`/`273`/`353` (and note `278` via `CCommand_0272::GetVal` at `0x48a8f2` is verified faithful) and receive after-battle HP/TP recovery.
  - **Fix:** Exclude Stage-3 Petrified members (`!(u.St[120] != null && u.St[120].Stage >= 3)`) from `living` in `RecoverAfterBattle`.

engine_cs/src/DtEngine/Scenario.cs:1034
```csharp
                    if (unit.Kind == Kind.Member || unit.Kind == Kind.Summon)
                    {
                        unit.ClearStatuses();
                        unit.Chant = null;
                        unit.ClearSongsAndDances();
                    }
```

engine_cs/src/DtEngine/Scenario.cs:1083
```csharp
        public static void RecoverAfterBattle(List<Unit> party)
        {
            var living = party.Where(u => u.Alive && u.Kind == Kind.Member).ToList();
```

---

### M05.08 `CActionItem`, `CActionPatternItem`, Item Consumption (`274`) & `ItemResult` Factory (`0x50c570`)

**Verdict:** S1

```asm
0042d00e  mov      eax, dword ptr [eax + 0x30]
0042d011  shr      eax, 6
0042d032  push     0x112
0042d05b  call     0x490790
0050c596  cmp      ecx, 0x6a
0050c59f  jmp      dword ptr [ecx*4 + 0x50e538]
```

- **M05.08a (S1):** Non-consumable / infinite item flag (`Flags_0x18` bit 6 = `0x40` at `0x42d011`) is not loaded or checked. `Battle.UseItem` always decrements `unit.Items[action.Item]` and rolls `Loss Rate (274)` even on the 8 infinite battle-usable vanilla items (`859 Sea Palace Orb`, `860 Leaf`, `861 New World Egg`, `863 Forbidden Fruit`, `864 Forbidden Grain`, `865 Prima Materia`, `866 Dry Mandra Sapling`, `867 Raurau Manuscript`).
  - **Fix:** Export `Flags_0x18` on `Data.Item`; skip decrement and `274` roll when `(item.Flags & 0x40) != 0`.
- **M05.08b (S1):** `Battle.UseItem` decrements the item and rolls `274` BEFORE executing the item's effect slots, reversing RNG order relative to `CActionPatternItem::Update` -> `_ConsumeItem` (`0x42cfe0`) which runs AFTER all effects.
  - **Fix:** Move item consumption and `274` conservation roll to the end of `Battle.UseItem`.
- **M05.08c (S1):** `Battle.UseItem` implements only types `0..8` plus the 41 direct skill thunks, silently dropping ~40 battle-usable `ItemResult` types (`11..23, 35, 36, 39, 52..61, 69, 88, 89`).
  - **Fix:** Implement the missing combat `ItemResult` types per `M05.09..M05.13`.

engine_cs/src/DtEngine/Battle.cs:3496
```csharp
            if (item == null || !unit.Items.TryGetValue(action.Item, out int have) || have <= 0) return;
            unit.Items[action.Item] = have - 1;
            if (unit.Has(274) && Roll(unit.Value(274))) unit.Items[action.Item] += 1;
```

---

### M05.09 Grouped Tabular Batch Rule: All 58 Skill-Casting `CItemResult*` Types (41 Direct Thunks + 17 Wrappers via `0x50b030`)

**Verdict:** S1

```asm
0050b062  cmp      byte ptr [ebp + 0xc], 0
0050b081  call     0x490790
0050b0f9  call     0x61e650
0051160c  push     0xe2
00511613  call     0x50b030
00513c3b  push     0xb3
00513c40  mov      dword ptr [esi + 8], 0x40a00000
```

- **M05.09a (S1):** `tools/item_effect_data.py:skill_item_specs` only scans the 41 5-instruction direct thunks, omitting the 3 battle-usable Party-Buff Wrappers (`35 -> skill 226`, 8 uses; `36 -> skill 227`, 8 uses; `39 -> skill 195`, 10 uses — 26 total battle item uses) and the 14 meal wrappers (`73..86`). `gamedata/data.py` never adds `35, 36, 39` into `item_skill_specs`, so `Battle.UseItem` silently ignores them.
  - **Fix:** Include types `35 -> (226, 0, -1)`, `36 -> (227, 0, -1)`, and `39 -> (195, 0, -1)` (and `73..86`) in `skill_item_specs()`.
- **M05.09b (S1):** `tools/item_effect_data.py` `MEAL_BUFFS_FALLBACK` is corrupted: omits `78` (`184, 5`) and `79` (`185, 5`), mismaps `80` to `184` instead of `186`, and mismaps `35` to `193` (instead of `226`) and `36` to `194` (instead of `227`).
  - **Fix:** Correct `MEAL_BUFFS_FALLBACK` to match the verified binary table (`35->226, 36->227, 39->195, 73..86->179..186,201,197,35,36,198,202`).
- **M05.09c (S2):** When `useValAsLevel == 1`, `Battle.UseItem` uses `PyMath.Int(value)` instead of `0x61e650` (`round_f32_to_i32`), and passes only a single `action.Target` instead of expanding `item.TargetType` (`17`/`18`).
  - **Fix:** Use `PyMath.Round(value)` for `useValAsLevel == 1` and pass expanded target list for Row/SideAll items.

tools/item_effect_data.py:53
```python
MEAL_BUFFS_FALLBACK = {
    73: (179, 5), 74: (180, 5), 75: (181, 5), 76: (182, 5), 77: (183, 5),
    80: (184, 5), 81: (201, 5), 82: (197, 5), 83: (35, 10), 84: (36, 10),
    85: (198, 10), 86: (202, 5), 35: (193, 5), 36: (194, 5), 39: (195, 5)
}
```

engine_cs/src/DtEngine/Battle.cs:3565
```csharp
                    if (spec.UseValAsLevel || Rng.RandRange(100) < PyMath.Int(value * 100))
                    {
                        var skill = Data.ById(spec.SkillId);
                        if (skill != null)
                        {
                            int lv = spec.UseValAsLevel ? Math.Max(1, Math.Min(skill.Levels, PyMath.Int(value)))
                                   : (spec.FixedLevel > 0 ? Math.Min(skill.Levels, spec.FixedLevel) : skill.Levels);
                            Perform(new Action(unit, AKind.Skill, skill, lv, action.Target) { Paid = true });
                        }
                    }
```

---

### M05.10 Consumable HP/TP Recovery & Revive `CItemResult*` Handlers (`0..5`, `8`, `59`, `61`, `62..64`)

**Verdict:** S1

```asm
0050e789  push     0x113
00510183  mov      eax, dword ptr [eax + 0x38]
00510194  mov      eax, dword ptr [eax + 0xc8]
005101bc  divss    xmm0, dword ptr [0x6d9540]    ; float 100
00512605  cmp      eax, dword ptr [ecx*4 + 0x6d3820]
00512bd1  cmp      dword ptr [eax + 0x28], 2
00512f5a  push     0x113
```

- **M05.10a (S1):** Conditional 10%-step HP recovery item Types `59` (feline enemies `0x6d3820`, 1 battle item use) and `61` (Beast race `2` / charParam `+0x44 == 2`, 2 battle item uses) are completely unimplemented in `Battle.UseItem`.
  - **Fix:** Implement Types `59` and `61` with `(MaxHp * PyMath.Int(value)) / 10` and `ApplyItemMastery` (`275`).
- **M05.10b (S1):** Types `0..5` omit `!IsFullPetrified` (`vtable+0xe8`), healing HP/TP of Stage-3 Petrified units; Type `8` (Revive item) omits `!IsFullPetrified` (`0x510194`), omits `OnRevive` (`0x43cfb0`) performance resync, and resets `target.NextTime`.
  - **Fix:** Gate `0..5` on `CanFight`, gate `8` on `!target.Alive && !IsFullPetrified(target)`, and trigger `OnUnitRevived`.
- **M05.10c (S2):** 10%-step MaxHP/MaxTP Types `62..64` (`0x512eb0..0x5133c0`) are unimplemented in `Battle.UseItem` (0 vanilla item uses).
  - **Fix:** Add handlers for Types `62`, `63`, `64`.

engine_cs/src/DtEngine/Battle.cs:3509
```csharp
                if (kind == 0) Restore(target, ApplyItemMastery(value, mastery));
                else if (kind == 1)
                {
                    if (target.Alive) target.Tp = Math.Min(target.MaxTp, target.Tp + ApplyItemMastery(value, mastery));
                }
...
                else if (kind == 8 && !target.Alive)
                {
                    target.Alive = true;
                    target.Hp = Math.Max(1, PyMath.Int(target.MaxHp * value / 100.0));
                    target.NextTime = Time + Wait(target);
                }
```

---

### M05.11 Ailment Cure & Debuff Purge `CItemResult*` Handlers (`6`, `7`, `20..23`, `65..72`)

**Verdict:** S1

```asm
0050fbcd  call     dword ptr [eax + 0x80]
0050fbed  call     0x490790
00510acd  push     0x72
0051111e  call     dword ptr [eax + 0x90]
005136f5  push     0x71
00513a36  call     dword ptr [eax + 0x80]
00513a44  call     dword ptr [eax + 0x90]
```

- **M05.11a (S1):** Battle-usable cure/purge item Types `20` (Cure Freeze, 17 uses), `21` (Cure Sleep, 4 uses), `22` (Cure Shadow Sew, 17 uses), `23` (Dispel All Debuffs, 26 uses), and `69` (Cure Freeze, 2 uses) — 66 total battle item uses — are completely unimplemented in `Battle.UseItem`.
  - **Fix:** Implement Types `20` (`114`), `21` (`116`), `22` (`123`), `23` (remove all `IsDebuffStatus`), and `65..72` in `Battle.UseItem`.
- **M05.11b (S1):** Types `6` (`ITEM_CURE_ONE`, 35 uses) and `7` (`ITEM_CURE_ALL`, 36 uses) omit the `!target.IsDead()` guard, omit Row/SideAll expansion (`targetType 17/18`), and omit `0x43cfb0` performance resync when curing Petrification (`120`).
  - **Fix:** Loop over expanded `targetType` targets, gate on `t.Alive`, and invoke `OnPetrifyCured` when `120` is popped.
- **M05.11c (S2):** Types `65..68`, `70..72` (single-ailment cures & Panacea `72`) are unimplemented (0 vanilla item uses).
  - **Fix:** Add handlers for `65..72` alongside `20..23`.

engine_cs/src/DtEngine/Battle.cs:3548
```csharp
                else if (kind == ITEM_CURE_ONE)
                {
                    // 0x50fbcd: cure items clear true ailments 113..122 only (never Shadow Sew 123).
                    var present = new List<int>();
                    foreach (int e in AILMENT_IDS) if (e != 123 && target.St[e] != null) present.Add(e);
                    if (present.Count > 0) target.PopStatus(present[Rng.ChoiceIndex(present.Count)]);
                }
                else if (kind == ITEM_CURE_ALL)
                {
                    var present = new List<int>();
                    foreach (int e in AILMENT_IDS) if (e != 123 && target.St[e] != null) present.Add(e);
                    foreach (int e in present) target.PopStatus(e);
                }
```

---

### M05.12 Offensive Damage & Ailment-Inflicting `CItemResult*` Handlers (`11..19`, `52..58`, `60`)

**Verdict:** S1

```asm
0050ab21  divss    xmm2, dword ptr [0x6d9540]    ; float 100
00510508  push     0x76
0051071b  mov      edx, 0x78
005107c9  mov      edx, 0x79
005118c1  lea      ebx, [eax - 1]
00511b78  cmp      ebx, 0x64
005120e0  cmp      ecx, dword ptr [eax*4 + 0x6d3820]
00512369  call     0x4f21f0
00512935  cmp      dword ptr [eax + 0x28], 7
```

- **M05.12a (S1):** ALL 17 offensive item handlers (`11..19`, `52..58`, `60`) are completely unimplemented in `Battle.UseItem` (silently no-op), covering **246 battle-usable item effect slots** in vanilla `ItemData.pck`: `11..17, 19` (ailments/instakill at `val / 100`, 211 uses), `18` (instant Stage-3 petrify, 2 uses), `52..55` (non-lethal direct/% MaxHp damage clamped to `CurHp - 1`, 28 uses), and `56..58, 60` (enemy-specific ailment items, 5 uses).
  - **Fix:** Implement Types `11..19`, `52..58`, and `60` inside `Battle.UseItem` over expanded `targetType` targets (including Exclusive Barrier checks `0x41f920` and Stun gauge reset `0x510593`).

engine_cs/src/DtEngine/Battle.cs:3503
```csharp
            int from = target.Side == unit.Side ? 0 : 2, to = Math.Min(item.Kinds.Length, from + 2);
            for (int i = from; i < to; i++)
            {
                int kind = item.Kinds[i];
                if (kind < 0) continue;
```

---

### M05.13 Utility, Dungeon & Out-of-Battle `CItemResult*` Handlers (`9`, `10`, `24`, `87`, `88`, `89`)

**Verdict:** S1

```asm
005103c4  mov      edx, 0x6b
005104ef  mov      byte ptr [esi + 0x1d], 1
00511393  cmp      ecx, 0x3e7
004151f0  xor      al, al
005142d4  mov      byte ptr [eax + 0x15c], 1
0051438a  mov      eax, 0x66666667
```

- **M05.13a (S1):** Combat-active battle item Types `88` (Force Enemies Flee, 2 battle-usable vanilla items: `187 Bag of Darkness`, `359 Cloaking Device`), `10` (Escape Battle / Smoke Bomb, 6 items), and `89` (Lose 5% Party Gold in battle, 3 battle-usable items: `273, 275, 451`) are unimplemented in `Battle.UseItem`. (Types `9` Dungeon Light and `24` Menu SP Gain are out-of-scope dungeon/menu utility; Type `87` is a binary no-op.)
  - **Fix:** Implement Type `88` (mark enemies fleeing when `Options.RandomBattle`) and Type `10` (escapable battle exit) in `Battle.UseItem`.

engine_cs/src/DtEngine/Battle.cs:3576
```csharp
                else if (Data.ItemSkills.TryGetValue(kind, out int skillId))
                {
                    var skill = Data.ById(skillId);
                    // 0x50b136: item-invoked skills do not spend TP.
                    if (skill != null) Perform(new Action(unit, AKind.Skill, skill, skill.Levels, action.Target) { Paid = true });
                }
```

---

## M06 — Status Lifecycle, Vtable Flag Matrix, Stat/Resistance Recalculation, Dispel, Countdown, and Performance Groups (`M06.01..M06.08`)

### M06.01 `CGameStatusBase::AddStatus`, Removal, and Status Wipe

**Verdict:** S0

```asm
004f9950  mov eax, dword ptr [eax + 0xc8]
004f9956  call eax
004f9958  test al, al
004f995a  jne 0x4fa5f9
004fa056  mov eax, dword ptr [eax + 0x8c]
004fa05c  call eax
004fa06f  call dword ptr [edx + 0x68]
004fa8b1  mov eax, dword ptr [eax + 0x90]
```

engine_cs/src/DtEngine/Units.cs:212
```csharp
        public void SetStatus(Status s)
        {
            if (St == NoStatuses) St = RentStatusArray();
...
            St[s.Effect] = s;
        }

        public Status PopStatus(int e)
        {
            var s = St[e];
            if (s == null) return null;
            St[e] = null;
...
            if (e == MAX_HP_BUFF && Hp > MaxHp) Hp = MaxHp;
            return s;
        }
```

engine_cs/src/DtEngine/Battle.cs:3024
```csharp
            target.SetStatus(new Status(effect, value, 0, unit).WithData(start));
            EndParts(target, PartsFor(effect));
            return true;
```

engine_cs/src/DtEngine/Battle.cs:3082
```csharp
                    if (u.Owner == unit && u.Kind == Kind.Doll && u.Alive && !u.Arrow && !u.Genjimaru && u.ShadowOf == null) RemoveDoll(u);
```

- **Sub-bugs:**
  - **`M06.01a` (S0):** `CGameStatusBase::AddStatus` (`0x4f9950..0x4f995a`) immediately returns `null` when `vt+0xc8` (`HasFullPetrify_120`, Stage >= 3) is true, blocking every new status/buff/debuff/ailment. `Units.cs:212` `SetStatus` has no Stage-3 Petrify guard at all, allowing buffs, dances, songs, and ailments to attach to fully petrified units. *Reach:* Any battle where a unit reaches Stage-3 Petrification (40+ vanilla enemy attacks & skills inflict `120`/`121`). *Fix:* Return early from `Unit.SetStatus` when `St[120] != null && St[120].Stage >= 3` (except explicit `120` Stage-3 upgrade).
  - **`M06.01b` (S0):** When Sleep (`116`) is added (`0x4fa03a..0x4fa072`), `AddStatus` iterates `StatusList` and strips every active status whose `vt+0x8c` (`IsSleepCleared`) is `true` — 36 command IDs including Cover (`171`), Parry (`180`), Limit Field (`190`), Puppets (`228..233`), Counter-Parry (`250`), Warning Shot (`259`), Elegant Dancing (`285`), etc. `Battle.cs:3024` only calls `EndParts(target, PerfParts.All)` and never strips `vtable+0x8c` statuses on Sleep. *Reach:* Active in every battle involving Sleep (`116`/`143`) against Cover (`171`), Parry (`180`), Limit Field (`190`), or Puppet/counter stances. *Fix:* Export `flags38` bit 1 (`IsSleepCleared`) from `CommandData.pck` and remove all active matching statuses when `116` is applied.
  - **`M06.01c` (S1):** `RemoveStatusByIndex` (`0x4fa690`) calls `CBattleBase::ResyncAllyPerformances_0x43cfb0(this)` whenever `cmdId == 120` is cured on a living unit, re-applying active ally Songs/Dances/Geasses to the cured unit. `Units.cs:236` `PopStatus(120)` and `Battle.cs` never resync active performances after Petrification cure. *Reach:* Active whenever Nurse (`106` tier >= 6) or Panacea (`Item 7`) cures a petrified unit while Songs/Dances/Geasses are active. *Fix:* Call a `ResyncAllyPerformances(unit)` helper in `Battle` when status `120` is removed from an alive unit.
  - **`M06.01d` (S1):** Applying `123` (Shadow Sew / Instant Death hook at `0x4fa430 -> 0x43d2c0`) calls `DestroyOwnedDolls`, destroying all dolls owned by the unit. `Battle.cs:3082` `EndParts(unit, PerfParts.Doll)` explicitly excludes `!u.Arrow && !u.Genjimaru && u.ShadowOf == null`, preserving Arrow, Genjimaru, and Shadow dolls. (Verified faithful: `Freeze 114` cancels Dance/Puppet/Geass only and `Silence 117` cancels Song/Chant only at `Battle.cs:2909-2911`, matching `0x4f9e6f` and `0x4fa0e2`.) *Reach:* Active when a Shadow/Genjimaru/Arrow owner is hit by `123`. *Fix:* Match `0x43d2c0` doll destruction predicate on `123`.

---

### M06.02 `CCommand` Vtable Boolean Flag Matrix (All 328 Instantiated IDs)

**Verdict:** S0

```asm
00479df0  push ecx
00479df3  mov eax, dword ptr [eax + 0x2c]
00479df6  call eax
00479e00  comiss xmm0, dword ptr [0x6d928c]
00479e07  setae al
0048bec3  mov eax, dword ptr [ecx + 0xc]
0048bedf  mov eax, dword ptr [eax + 0x50]
0048bee2  shr eax, 1
0048bee4  and al, 1
```

engine_cs/src/DtEngine/Battle.cs:71
```csharp
        public static readonly int[] AILMENT_IDS = { 113, 114, 115, 116, 117, 118, 119, 120, 122, 123 };
```

engine_cs/src/DtEngine/Battle.cs:109
```csharp
        static readonly bool[] DispelAlways = Flags(new[] { 27, 171, 325, 326, 327, 328, 329, 101, 102, 181, 189, 191, 193, 194 });
        static readonly bool[] DispelIfRaised = Flags(new[] { 21, 26, 28, 31, 41, 42, 43, 44, 45, 46, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173, 174, 184, 185, 186 });
        // Exact CCommand vtable+0x54 (IsBuff) and vtable+0x5c (IsDebuff) classification (0x433b80, 0x481b12).
        static readonly bool[] SignedBuffDebuff = Flags(new[] { 21, 26, 28, 31, 41, 42, 43, 44, 45, 46, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173, 174, 184, 185, 186 });
        static readonly bool[] AlwaysBuffStatus = Flags(new[] { 27, 171, 325, 326, 327, 328, 329 });
```

engine_cs/src/DtEngine/Battle.cs:215
```csharp
        public static bool IsTrueAilmentId(int e) => e >= 0 && e < IsAilment.Length && IsAilment[e] && e != 123;
```

- **Sub-bugs:**
  - **`M06.02a` (S0):** The data pipeline (`gamedata/data.py`, `tools/engine_export.py`, `Data.cs`, `Loader.cs`) does not extract `CommandData.pck` `flags38` bit 1 (`+0x8c` `IsSleepCleared`, 36 command IDs) or bit 2 (`+0x90` `ClearOnDeath`, 8 exempt IDs `[67, 68, 81, 133, 134, 355, 428, 433]`), nor does `Battle.cs`/`Units.cs` encode them. Consequently, Sleep-clear (`0x4fa056`), Sleep-decay (`0x48d5cd`), and Death-clear exemptions (`0x4fa8b1`) are missing architecture-wide. (Verified faithful: `+0x54` Buff, `+0x5c` Debuff, `+0x64` Dispellable, ID `32` inverted sign, `+0x6c/+0x70/+0x78` Song/Dance/Geass, and `+0x7c/+0x84` WeaponEnchant/Barrier exclusivity at `Battle.cs:104-113, 216-235` and `Units.cs:216-226` match the binary matrix.) *Reach:* Systemic across all battles involving Sleep or death-persistent effects. *Fix:* Export `flags38` bits 1 and 2 from `CommandData.pck` into `engine_data.json` and enforce them in `Units.cs` and `Battle.cs`.
  - **`M06.02b` (S2):** Binary `+0x68` (`IsAilment`) covers the 11 IDs `113..122, 139`. `Battle.cs:71, 215` `IsTrueAilmentId` omits `121` (transiently converted to `120`) and `139` (instant lethal, never persists as a status). *Reach:* Near-0 runtime impact because `121` converts to `120` and `139` kills immediately, though `139` is checked by barrier gating (`M07.10`). *Fix:* Include `121, 139` in the `IsTrueAilmentId` predicate for exact vtable `+0x68` parity.

---

### M06.03 Stat Recalculation (`0x4fbdd0..0x4fc6cc`)

**Verdict:** S1

```asm
004fbfb4  push 0x30
004fbfca  call dword ptr [eax + 0x48]
004fbfef  mov ebx, 0xffffd8f0
004fc00d  cvttss2si eax, dword ptr [esp + 0x1c]
004fc013  add ebp, eax
004fc26f  push 0x100
004fc2db  cmp dword ptr [eax + 0x38], 0
```

engine_cs/src/DtEngine/Units.cs:697
```csharp
            int[] gearedForLine = totals;
            if (offhandBonus != null)
            {
                gearedForLine = new int[6];
                for (int s = 0; s < 6; s++) gearedForLine[s] = totals[s] + offhandBonus[s];
            }
            EnchantBonus(counted, characterStats, hp, tp, front, bonusTotal, out int bonusHp, out int bonusTp, resistBonus, gearedForLine);
```

engine_cs/src/DtEngine/Units.cs:368
```csharp
            if (St[TRUMP_CARD] != null)
            {
                if (name == ATK) total += PyMath.Int(Base[DEF] * St[TRUMP_CARD].Value);
                else if (name == DEF) total -= 10000;
            }
```

- **Sub-bugs:**
  - **`M06.03a` (S1):** In `CGamePlayerStatus::RecalculateAll` (`0x4f7c00..0x4f7c69`), Stage 4 `ApplyEnchants` (`0x4f8270`, including front/back line-multiplier enchants `222..225, 281`) runs BEFORE Stage 5 `ApplyStatusModifiers` (`0x4fbdd0`), where Dual-Wield Offhand Passive `256` (`0x4fc26f..0x4fc5c5`) adds offhand weapon stats. `Units.cs:697-703` adds `offhandBonus` into `gearedForLine` BEFORE calling `EnchantBonus`, inflating front/back line-bonus enchant stats on every dual-wielding character. *Reach:* Active for every Dual-Wield (`256`, Samurai/Kunoichi/Valkyrie/etc.) build wearing front/back stat-boost enchants (`222..225, 281`). *Fix:* Pass `totals` (without `offhandBonus`) as `gearedForLine` into `EnchantBonus`, keeping `offhandBonus` strictly in Stage 5 (`Unit.Stat`).
  - **`M06.03b` (S2):** For Trump Card (`48`, `0x4fbfef`), the binary sets `delta[1] = -10000` (overwriting any prior DEF buff `42`), whereas `Units.cs:371` does `total -= 10000` (keeping `42`). Because DEF is clamped to `[0, 9999]`, `total -= 10000` still yields `0` unless `Base[DEF] + buffs > 10000` (possible only with extreme late-postgame DEF + large `42`/`189`/`120` buffs). *Reach:* Rare edge case when `Base[DEF] + DEF buffs > 10000` under Trump Card (`48`). *Fix:* Reset the prior `42` DEF delta to `-10000` when `St[TRUMP_CARD] != null` instead of subtracting `10000`.

---

### M06.04 Max HP Buff `172` & Life Bringer `133` MaxHP Drain Modifier

**Verdict:** S2

```asm
004f7c29  mov edi, dword ptr [ebx + 0x10]
004f7c4d  push edi
004f7c4e  call dword ptr [eax + 0x10c]
004fc629  mov edx, dword ptr [esi + 0x98]
004fc62f  add edx, dword ptr [esi + 0x10]
004fc635  test edx, edx
004fc637  cmovle edx, edi
004fc63a  cmp dword ptr [esi + 0xc], edx
004fc63d  mov dword ptr [esi + 0x10], edx
004fc640  cmovle edx, dword ptr [esi + 0xc]
004fc646  mov dword ptr [esi + 0xc], edx
```

engine_cs/src/DtEngine/Units.cs:385
```csharp
        public int MaxHp
        {
            get
            {
                int hp = MaxHpBase;
                if (StCount == 0) return hp;
                var s = St[MAX_HP_BUFF];
                // 0x4f7c29, 0x4fc089: effect 172 multiplies pre-enchant BaseHp (growth + crown), not post-enchant MaxHpBase.
                if (s != null) hp += PyMath.Int(BaseHp * s.Value);
                return hp;
            }
        }
```

engine_cs/src/DtEngine/Battle.cs:2783
```csharp
                if (effect == MAX_HP_DRAIN && hostile && dealt != 0)
                {
                    target.MaxHpBase = Math.Max(1, target.MaxHpBase - PyMath.Int(dealt * value));
                    target.Hp = Math.Min(target.Hp, target.MaxHp);
                    continue;
                }
```

- **Sub-bugs:**
  - **`M06.04a` (S2):** `Units.cs:385-396` `MaxHp` omits the `Math.Max(1, hp)` floor (`0x4fc635..0x4fc637`), and `Units.cs:212` `SetStatus` does not clamp `Hp <= MaxHp` if a negative `172` debuff is applied (only `PopStatus(172)` clamps at `Units.cs:250`). *Reach:* 0 vanilla enemy attacks apply negative `172` (vanilla `172` values are positive buffs); only reachable on custom/mod negative `172`. *Fix:* Return `Math.Max(1, hp)` in `MaxHp` and clamp `Hp = Math.Min(Hp, MaxHp)` whenever `172` is set or popped.
  - **`M06.04b` (S2):** In the binary (`0x4fc629..0x4fc63d`), Life Bringer (`133`) accumulates into a separate unclamped `MaxHPDelta_0x98` field added AFTER `max(1, MaxHP + hpBuffDelta)`, then floored at `1`. `Battle.cs:2785` mutates and floors `target.MaxHpBase` at `1` immediately, so if `172` (Max HP Buff) and `133` (Life Bringer) overlap on the same target and `133` drains below `1`, the excess drain is lost instead of offsetting `172`. *Reach:* Rare multi-condition overlap (`133` Life Bringer is a player skill targeting enemies; vanilla enemies rarely hold `172`). *Fix:* Track `unit.MaxHpDelta` separately from `MaxHpBase` and apply `Math.Max(1, Math.Max(1, MaxHpBase + hpBuffDelta) + MaxHpDelta)` in `Unit.MaxHp`.

---

### M06.05 Resistance Recalculation & Samsara Override (`0x4fc050..0x4fc889`)

**Verdict:** MATCH

```asm
004fc054  push 0xa9
004fc0c9  push 0xb8
004fc0f2  push 0xb9
004fc11b  push 0xba
004fc1b0  push 0xc0
004fc1ea  push 0xca
004fc1fc  push 0x155
004fc236  push 0xf8
004fc6c7  mov edx, 0xffffff9c
004fc6cf  mov ecx, 0x64
004fc709  push 0x1a0
004fc771  call dword ptr [eax + 0x48]
004fc781  call 0x61d550
```

engine_cs/src/DtEngine/Units.cs:398
```csharp
        public int Resistance(int index)
        {
            if (SamsaraState == 2) return Samsara[index];
            // 0x4fc1b0..0x4fc1e4: Effect 192 (All Resistances 100) adds +10000 to all 8 resistances, clamping to +100.
            if (StCount != 0 && St[192] != null) return 100;
            int value = ResistBase[index];
            if (index >= 3)
            {
                if (StCount != 0 || hasElemResistPassive)
                {
                    // 0x4fc1e6: 202 and 341 are mutually exclusive (202 wins); 169 and 248 remain additive.
                    if (Has(169)) value += PyMath.Int(Value(169));
                    if (Has(202)) value += PyMath.Int(Value(202));
                    else if (Has(341)) value += PyMath.Int(Value(341));
                    if (Has(248)) value += PyMath.Int(Value(248));
                }
            }
            else if (StCount != 0)
            {
                // PHYSICAL_RESIST_BUFFS {185: 0, 184: 1, 186: 2}
                int e = index == 0 ? 185 : index == 1 ? 184 : 186;
                var s = St[e];
                if (s != null) value += PyMath.Int(s.Value);
            }
            // 0x4fc6c7..0x4fc751: clamp all 8 resistances to [-100, +100] before Samsara (416..423) overrides.
            return value < -100 ? -100 : value > 100 ? 100 : value;
        }
```

- Exact match: `Units.cs:398-424` implements all 8 resistance indices (`0..2` Slash/Stab/Bash via `185/184/186`, `3..7` elemental via `169`, mutually exclusive `202 ?? 341`, and `248`), Effect `192` clamping to `+100`, `trunc0` (`PyMath.Int`), standard `[-100, +100]` clamp, and post-clamp Samsara override (`416..423`, returning `Samsara[index]` unclamped).

---

### M06.06 Timed Status Countdown, Sleep-Decay, and Map Step Counter (`X15`)

**Verdict:** S1

```asm
0048d5b5  test edi, edi
0048d5b7  je 0x48d5d9
0048d5bd  mov eax, dword ptr [eax + 0xbc]
0048d5c3  call eax
0048d5cd  mov eax, dword ptr [eax + 0x8c]
0048d5d3  call eax
0048d5d7  jne 0x48d613
0048d5d9  mov ecx, dword ptr [esi + 0x28]
0048d5dc  test ecx, ecx
0048d5de  je 0x48d6a7
0048d5f0  cmp dword ptr [esi + 0x2c], 5
0048d605  lea eax, [ecx - 1]
```

engine_cs/src/DtEngine/Battle.cs:794
```csharp
        void DecrementTimedStatuses(Unit unit)
        {
            // Inner State 8 (0x436d4c): timed status durations decrement BEFORE 259/283/203 turn-loss checks.
            int n = unit.StCount;
            if (n == 0) return;
            var order = n <= tickScratch.Length ? tickScratch : new int[n];
            for (int i = 0; i < n; i++) order[i] = unit.StatusAt(i);
            for (int k = 0; k < n; k++)
            {
                int effect = order[k];
                var s = unit.St[effect];
                if (s != null && s.Turns > 0)
                {
                    s.Turns -= 1;
                    if (s.Turns <= 0) unit.PopStatus(effect);
                }
            }
        }
```

- **Sub-bugs:**
  - **`M06.06a` (S1):** `CCommandTurnBase::TickCountdown` (`0x48d5b5..0x48d5d7`) checks `target->HasSleep_116() && cmd->IsSleepCleared()` (`vtable+0x8c`) BEFORE checking `turnsRemaining == 0`, expiring any `vtable+0x8c` status immediately on Sleep even if permanent (`Turns == 0`). `Battle.cs:794-811` `DecrementTimedStatuses` never checks Sleep or `vtable+0x8c`. *Reach:* Active whenever a unit holds a `vtable+0x8c` timed/permanent status and is asleep (see `M06.01b`). *Fix:* Check `unit.St[116] != null && Data.IsSleepCleared(effect)` at the top of the `DecrementTimedStatuses` loop and pop immediately.
  - **`M06.06b` (S2):** Field-only wrapper `0x47fdc0` prevents IDs `[17, 18, 21, 107]` from ticking down during battle (`inBattleFlag_0x40 != 0`). `DecrementTimedStatuses` decrements any status with `s.Turns > 0` without exempting `[17, 18, 21, 107]`. (Note: intentional mod patch **`X15`** at `0x48d5f3` changes out-of-battle map steps per turn from `5` to `steps_a_turn`, exported via `tools/engine_export.py:277` `design_rows.steps_a_turn`, and is out-of-battle dungeon walking.) *Reach:* Near-0 in combat; ID `21` (map/buff utility) rarely has combat duration. *Fix:* Skip countdown in `DecrementTimedStatuses` for field-only IDs `{17, 18, 21, 107}`.

---

### M06.07 Dispel (`74`), Cure (`106`), Light (`107`), and Esarhaddon (`311`)

**Verdict:** S2

```asm
004226c4  mov edx, 0x4a
004226ea  call 0x505ac0
00422711  cmp edi, esi
00422713  jge 0x4227d2
00422730  call dword ptr [eax + 0x94]
0047ee6f  cmp dword ptr [ebx + 8], -1
0047ee73  je 0x47efc4
00481aa3  call 0x61e650
00481ab4  cmova eax, edx
00481b12  cmp ecx, 8
00436727  push 0x137
0043676a  call 0x61e650
```

engine_cs/src/DtEngine/Battle.cs:2698
```csharp
                if (effect == 74 && hostile)
                {
                    if (Roll(value)) Dispel(target);
                    continue;
                }
```

engine_cs/src/DtEngine/Battle.cs:2737
```csharp
                if (effect == 106 || effect == 235)
                {
                    int n = Math.Min(PyMath.Int(value), CURE_ORDER.Length);
                    for (int k = 0; k < n; k++) target.PopStatus(CURE_ORDER[k]);
                    if (PyMath.Int(value) == CURE_ALL)
```

engine_cs/src/DtEngine/Battle.cs:863
```csharp
                        // X16 (0x47ee73): vanilla skips buff dispel; Balance NOPs the jump (75% dispel chance).
                        if (effect == 74) { if ((Options.ThirdEyeDispel ?? Data.ThirdEyeDispel) && Roll(0.75)) Dispel(unit); }
```

- **Sub-bugs:**
  - **`M06.07a` (S2):** `CCommand_0106::Execute` (`0x481aa3`) and Esarhaddon `311` (`0x43676a`) convert `GetValue()` using `round_f32_to_i32` (`0x61e650`), whereas `Battle.cs:843, 2739-2741` use `PyMath.Int` (`trunc0`). Additionally, for `Cmd 235`, `Battle.cs:2741` checks `== 8` (exact for `106` at `0x481b12`, whereas `235` uses `>= 8`). *Reach:* 0 divergence on vanilla integer tier values (`1..8`), only diverges if fractional float values or `235` values `> 8` are used. (Note: intentional mod patch **`X16`** at `0x47ee73` is faithfully gated via `Options.ThirdEyeDispel ?? Data.ThirdEyeDispel` at `Battle.cs:864`.) *Fix:* Use `Math.Round(..., MidpointRounding.ToEven)` for `106`/`311` tiers and `>= 8` for `235`.
  - **`M06.07b` (S2):** In `CActionPatternBase::_Task`, attack-embedded Dispel `74` runs at `0x4226c4` BEFORE target `vtable+0xe0` status/ailment application (`0x422bd0`). `Battle.cs:2677-2702` runs `effect == 74` in slot order inside the effect loop, so an attack listing an ailment slot before slot `74` would roll the ailment before dispelling `169`/`192`/etc. *Reach:* Near-0 in vanilla `pck_usage` (the only vanilla enemy attack combining `74` and an ailment is `942 Abyss Roar`, which lists `74` before `118`). *Fix:* Execute attack-embedded `74` before the `IsAilment` loop in `AfterHit`.

---

### M06.08 Performance Groups: Songs, Dances, Puppets, Geass, Bonuses, Ticks & Cancellation

**Verdict:** S0

```asm
0043bfbd  push 0x11f
0043bfca  call eax
0043bfd7  mov ecx, 2
0043bfdc  cmovne esi, ecx
0043c47e  push 0x11c
0043c48b  call eax
0048c027  push 0x12c
0048c032  push 0x12d
0043809c  mov dword ptr [ebp - 0x10], 0xcc
00438265  mov dword ptr [ebp - 0x10], 0xc7
004382bc  mov dword ptr [ebp - 0x10], 0x153
```

engine_cs/src/DtEngine/Battle.cs:2928
```csharp
            string name = action.Skill != null ? action.Skill.Name : action.Atk.Name;
            if (!own.Contains(name))
            {
                own.Add(name);
```

engine_cs/src/DtEngine/Battle.cs:2960
```csharp
            string name = action.Skill != null ? action.Skill.Name : action.Atk.Name;
            if (!own.Contains(name))
            {
                own.Add(name);
```

engine_cs/src/DtEngine/Battle.cs:2987
```csharp
                double sign = 1, scale = 1;
                switch (effect)
                {
                    case 195: case 196: case 197: case 198: case 201: case 205: sign = -1; scale = 1; break;
                    case 202: sign = -1; scale = 100; break;
                    case 211: sign = 1; scale = 100; break;
                }
                var st = new Status(effect, value + sign * scale * bonus, 0, singer, name, Status.SongKind, atkId);
```

engine_cs/src/DtEngine/Battle.cs:1178
```csharp
            for (int i = 0; i < Units.Count; i++)
            {
                var t = Units[i];
                if (!t.Alive || t.StCount == 0) continue;
                var s199 = t.St[199];
...
                var s339 = t.St[339];
...
                var s200 = t.St[200];
...
                var s204 = t.St[204];
```

- **Sub-bugs:**
  - **`M06.08a` (S0):** In `AddSongCommand` (`0x43bdd0`), `AddDanceCommand` (`0x43c2a0`), and `AddGeassCommand` (`0x43cb80`), performance slots track `cmdId` (not skill `Name`), and BEFORE checking the caster's slot cap, the binary erases `cmdId` from ANY OTHER unit on the caster's side already performing `cmdId`. `Battle.cs:2928, 2960` track performances by `Name` string and NEVER remove `cmdId` from another ally performer, so if Ally A sings a song and Ally B casts the same song, Ally A's slot remains occupied and when Ally A later dies/gets silenced, Ally A can corrupt/retain stale slot bookkeeping (and multi-effect performances with two distinct `cmdId`s consume only 1 slot in the sim vs 2 in binary). *Reach:* Active whenever two party members (or two enemies) use overlapping Songs/Dances/Geasses, or on multi-effect performance skills. *Fix:* Track performance vectors by `int cmdId` per unit and erase `cmdId` from all allies on the same side before FIFO eviction.
  - **`M06.08b` (S1):** `Battle.cs:2987-2995` defaults `sign = 1, scale = 1` and adds `+bonus` (`279`/`280` + enchants `300..303`) to EVERY Song/Dance effect except `215/216`, including `200` (Subtle Dance TP drain), `203` (Erotic Dance skip chance), `204` (Weird Dance pep drain), `219` (Soul Song), `220`, `221`, and `223` — NONE of which override `GetValue` with `GetSongDanceBonus` (`0x48bf90`) in the binary (binary only applies `280` to `195..199, 201, 202, 205` and `279` to `210..218, 222`)! In particular, `204` has negative pep drain, so adding `+bonus` actually WEAKENS `204` instead of leaving it unchanged, while `200`, `203`, `219..221`, `223` are falsely amplified. *Reach:* Active for every Diva/Mistress/Dancer using `200, 203, 204, 219, 220, 221, 223` with `279`/`280` passives or enchants `300..303`. *Fix:* Apply `bonus` ONLY to `{195, 196, 197, 198, 199, 201, 202, 205}` (Dance) and `{210, 211, 212, 213, 214, 215, 216, 217, 218, 222}` (Song); leave all other IDs at raw `value`.
  - **`M06.08c` (S1):** Inner Turn-Start States execute in order **State 18 (`200` TP drain) -> State 19 (`204` Motivation) -> State 20 (`199`/`339` HP DoT)** (`0x437eda -> 0x438085 -> 0x43824e`). `Battle.cs:1178-1211` executes `199 -> 339 -> 200 -> 204` per unit, so if `199`/`339` kills the target (or triggers Resuscitate/Samsara/Ecstasy), `200` and `204` are skipped on that turn instead of firing beforehand. *Reach:* Active when a Dancer/Mistress maintains `199`/`339` alongside `200` or `204` via On Stage (`284`). *Fix:* Run three separate passes over `Units` in binary order: `200` first, `204` second, `199`/`339` third.

---

## M07 — Ailments, Immunities, Crowd Control, Barriers & Recovery (`M07.01..M07.12`)

### M07.01 Core Ailment Application Formula (`113`–`118`, `120`, `122`)

**Verdict:** S1

```asm
00481ef4  mov      eax, dword ptr [eax + 0xc8]
00481efa  call     eax
00481efc  test     al, al
00481f2d  push     0x83
00481f32  call     dword ptr [eax + 0xf0]
00481f4a  push     0x89
00481f4f  call     dword ptr [eax + 0xf0]
00481f84  call     0x5580c0
00481fb3  push     0xa
00481fb8  call     dword ptr [eax + 0x34]
00481fc2  mov      eax, 0x66666667
00481fc7  imul     ecx
00481fc9  sar      edx, 2
00481fde  mulss    xmm0, xmm1
00481fea  subss    xmm1, xmm0
0048201d  cvttss2si esi, xmm1
00482021  call     0x490790
00482026  cmp      eax, esi
00482028  jl       0x482040
```

engine_cs/src/DtEngine/Battle.cs:3000
```csharp
        public bool ApplyAilment(Unit unit, Unit target, int effect, double value, Action action, int start = T.NONE)
        {
            string name = AilmentName[effect];
            // 0x481ef4..0x483624: recovering ailments (113..117, 122) can be re-applied (stripping barriers / resetting recovery to start);
            // Petrify (120) and Shadow Sew (123) do not overwrite an existing instance; 192 is handled in Voided, not ApplyAilment.
            if (target.Immune(name) || Nullified(target, effect)) return false;
            if ((effect == 120 || effect == 123) && target.St[effect] != null) return false;
            int index = AilmentResist[effect];
            int resistance = index != T.NONE ? target.Resistance(index) : 0;
            int chance = F.AilmentThreshold(value, resistance);
            if (chance <= 0 || Rng.RandRange(100) >= chance) return false;
            if (ConsumeBarrier(target)) return false;
```

- **Sub-bugs:**
  - **`M07.01a` (S1):** `ApplyStandardAilment` (`0x481ef4`) checks `target->vtable+0xc8` (`IsFullyPetrified`, Stage >= 3) FIRST and immediately returns `NoOp` (0 RNG calls, no barrier consumption). `Battle.cs:3005` completely omits the Stage-3 Petrification check, allowing ailments (and `ConsumeBarrier`) to land on fully petrified units. *Reach:* Active whenever AoE/random ailment skills hit a Stage-3 Petrified unit. *Fix:* Add `if (target.St[120] != null && target.St[120].Stage >= 3) return false;` at the top of `ApplyAilment`.
  - **`M07.01b` (S1):** At `0x482021`, the binary ALWAYS draws `GlobalRng.Rand(100)` even when `threshold <= 0` (e.g. `resist >= 100` via All Resistances 100 or high elemental resist), then tests `roll < threshold`. `Battle.cs:3010` short-circuits `if (chance <= 0 || Rng.RandRange(100) >= chance)`, skipping the RNG draw whenever `chance <= 0`, desynchronizing PRNG stream alignment on high-resist targets. *Reach:* Active whenever any ailment targets a unit with `>= 100` corresponding elemental resistance. *Fix:* Always draw `int roll = Rng.RandRange(100);` before comparing `roll >= chance`.
  - **`M07.01c` (S2):** For duplicate Petrification (`120`), the binary deduplicates inside `AddStatus` (`0x4f9b9f..0x4f9bcd`) AFTER the `Rand(100)` roll and exclusive barrier check (`0x422c4b`). `Battle.cs:3006` returns `false` early before the roll and before `ConsumeBarrier(target)`, so a barrier on a Stage 1–2 petrified target is not stripped by a second petrify hit. *Reach:* Narrow edge case (target already has Stage 1–2 Petrify AND an active Clone/Barrier `101/102/181` when hit by `120` again). *Fix:* Move the duplicate `120` discard to after `ConsumeBarrier` (inside `SetStatus`).

---

### M07.02 Instant Death (`119`, `139`), Special Sleep (`143`), Shadow Sew (`123`), Weapon Procs & Reactive Ailments

**Verdict:** S1

```asm
00482eb7  push     0x86
00482ebc  call     dword ptr [eax + 0xf0]
00482f26  call     0x558060
00482f58  push     0xc
00482f97  cvttss2si eax, xmm1
00482f9e  call     0x490790
00482fc6  call     dword ptr [eax + 0x24]
00483900  mov      eax, dword ptr [eax + 0x54]
00483903  shr      eax, 0xa
00483922  cmp      esi, eax
00483924  jb       0x48392d
```

engine_cs/src/DtEngine/Action.cs:216
```csharp
                foreach (var (enchant, effect, value) in F.PLAIN_ATTACK_ENCHANTS)
                {
                    if (actor.Pieces(enchant) != 0)
                    {
                        bool present = false;
                        for (int i = 0; i < set.Count; i++) if (set.Id[i] == effect) { present = true; break; }
                        if (!present) AddTo(set, effect, 4, value, false);
                    }
                }
```

engine_cs/src/DtEngine/Battle.cs:3023
```csharp
            if (start == T.NONE) start = 5;
            target.SetStatus(new Status(effect, value, 0, unit).WithData(start));
```

engine_cs/src/DtEngine/Battle.cs:2874
```csharp
                if (target.Alive && target.HasUnique && target.UniqueEffect == 346 && action.Reach == T.SHORT && Roll(target.UniqueValue))
                {
                    if (!unit.Immune("slow") && !Nullified(unit, 122))
                        unit.SetStatus(new Status(122, 1.0, 0, target).WithData(SUGAR_COMA_RECOVERY));
                    unit.SetStatus(new Status(168, -0.2, SUGAR_COMA_TURNS, target));
                }
...
                if (target.Has(293) && action.Reach == T.SHORT && Roll(target.Value(293)))
                {
                    if (!unit.Immune("slow") && !Nullified(unit, 122))
                        unit.SetStatus(new Status(122, 1.0, 0, target).WithData(SLOW_TARGET_RECOVERY));
                    unit.SetStatus(new Status(168, -0.75, SLOW_TARGET_TURNS, target));
                }
```

- **Sub-bugs:**
  - **`M07.02a` (S1):** Weapon normal-attack ailment proc enchants `153..157, 165` (`0x421287..0x4216d2`) initialize `selfCureInit = 0` (`0%` first-turn recovery), NOT `5%`. `Action.cs:222` adds them as ordinary effects and `Battle.cs:2694 -> 3023` initializes `start = 5`, giving weapon-proc ailments an extra `+5%` self-cure on every turn (`5/15/25...` instead of `0/10/20...`). *Reach:* Active on every weapon bearing enchants `153..157, 165` during basic attacks. *Fix:* Tag weapon-proc effects in `MakePlainSet` (or pass `start: 0` when `action.Kind == AKind.Attack` and the effect came from `PLAIN_ATTACK_ENCHANTS`).
  - **`M07.02b` (S1):** Passive `346` (Sugar Coma, `0x422810..0x422a8b`) and Passive `293` (Slow Target, `0x424317..0x424520`) both apply Slow (`122`) with `val = 1.0f` through standard `CCommand_0122::Apply` (which checks Earth resistance scaling, `IsFullyPetrified`, and Exclusive Barriers `101/102/181`). `Battle.cs:2876, 2891` bypass `ApplyAilment`, ignoring Earth Resistance (so `EarthRes >= 100` or `EarthRes = 50` fails to reduce/block Slow!) and ignoring Clone/Barrier `101/102/181`. Furthermore, `Battle.cs:2889` restricts `293` (Slow Target) to `action.Reach == T.SHORT`, whereas binary `0x424317..0x424520` has NO range restriction (unlike Sugar Coma `346` which requires `range == 0`). *Reach:* Active whenever any unit attacks a target with `293` (Slow Target, e.g. Mistress/enemies) at Mid/Long range or with high Earth resistance / Clone barriers, or triggers `346` (Sugar Coma) with Earth resistance / Clone barriers. *Fix:* Route `122` inside `346` and `293` through `ApplyAilment(..., 122, 1.0, action, 5)` and remove `action.Reach == T.SHORT` from `293`.
  - **`M07.02c` (S1):** Both `CCommand_0119` (`0x482e40`) and `CCommand_0123` (`0x483840`) check `target->IsFullyPetrified()` (`vtable+0xc8`) first. `Battle.cs:2688, 3005` omit this guard, allowing `119` and `123` to land on Stage-3 Petrified units. *Reach:* Active on AoE Instakill (`119`) / Shadow Sew (`123`) when a Stage-3 Petrified unit is present. *Fix:* Add the `!IsFullyPetrified` guard to `123` at `Battle.cs:2688` and to `ApplyAilment`.
  - **`M07.02d` (S2):** Passive `258` (Instakill on Physical Crit, `0x44d266`) and Passive `320` (Devil's Whisper, `0x4235d5`) in the binary set/add `res.hpDamage` BEFORE HP is deducted so lethal hits resolve inside the same damage application (single `TakeDamage`/Resuscitate/TP-conversion pass). `Battle.cs:2575, 2869` run `258`/`320` AFTER `TakeDamage`, causing a second `LoseHp` call (triggering TP Conversion twice or breaking Resuscitate if the first hit already killed). *Reach:* Narrow edge case where `258` or `320` procs on a hit against a target with Resuscitate `188` or TP Conversion. *Fix:* Evaluate `258` inside `PhysicalDamageActual` and `320` before `TakeDamage` when `dealt > 0`.

---

### M07.03 Chant Interruption (`CalcPhysicalAttack` / `CalcMagicalAttack`) & Turn Delay (`54`)

**Verdict:** S1

```asm
0044d03a  mulss    xmm0, dword ptr [0x6d93bc]
0044d04b  divss    xmm1, xmm0
0044d056  movss    xmm1, dword ptr [0x6d9384]
0044d081  push     0x39
0044d1f8  call     0x505ac0
0044d20c  cvttss2si ecx, xmm0
0044d210  cmp      eax, ecx
0044d238  cmp      eax, 0x21
0047ea83  cmp      byte ptr [ebx + 0x33], 0
```

engine_cs/src/DtEngine/Battle.cs:2574
```csharp
                if (target.Chant != null || Performing(target))
                    Interrupt(target, amount, critical, action == null || !action.Magic);
```

engine_cs/src/DtEngine/Battle.cs:2592
```csharp
        void Interrupt(Unit target, int amount, bool critical, bool physical)
        {
            // the interruption enchantments of the target: 57, 58, 59 lower the rate, 60 and 61 raise it (P6.10 of the audit)
            double enchant = 0.10 * target.Pieces(57) + 0.06 * target.Pieces(58) + 0.03 * target.Pieces(59) - 0.06 * target.Pieces(60) + 0.20 * target.Pieces(61);
            double chance = F.InterruptionChance(amount, target.MaxHp, target.Value(264), enchant, critical, physical, Options.InterruptProduct ?? Data.InterruptProduct);
            if (Rng.Random() < chance)
```

engine_cs/src/DtEngine/Formulas.cs:286
```csharp
        public static double InterruptionChance(double damage, double maxHp, double modifier, double enchant, bool critical, bool physical,
                                                bool product)
        {
            double rate = 0.0;
            if (physical)
            {
                double divisor = product ? maxHp * INTERRUPT_HP_FACTOR * (1 + modifier) : maxHp * INTERRUPT_HP_FACTOR + (1 + modifier);
                double a = Clamp(damage / divisor, 0.0, INTERRUPT_MAX);
                rate = PyMath.Int(Clamp(a - enchant, 0.0, INTERRUPT_MAX) * 100) / 100.0;
            }
            if (critical) rate = 1 - (1 - rate) * (1 - INTERRUPT_CRITICAL / 100.0);
            return rate;
        }
```

- **Sub-bugs:**
  - **`M07.03a` (S1):** `Battle.cs:2575` passes `physical = (action == null || !action.Magic)` into `Interrupt()`. Non-physical, non-magic Special Damage attacks (breath/fixed/HP% skills and enemy attacks like `140/141/142`, `63/64`, `135`, Dance `199`/Geass `339` DoT where `action == null`, Poison DoT where `action == null`) have `!action.Magic == true`, so the simulator runs the physical damage-ratio interrupt formula (`CalcPhysicalAttack` `0x44d012`) on them — even on Poison/Dance DoT ticks (`action == null`)! In the binary, ONLY `CalcPhysicalAttack` runs the damage-ratio interrupt; Poison/Dance/Special Damage NEVER trigger physical interruption. *Reach:* Active in every battle where a chanting/performing unit takes Poison (`113`), Salsa (`199`), Geass (`339`), or Special-Damage enemy attacks. *Fix:* Pass `action != null && action.Physical` for physical damage-ratio interruption, and skip `Interrupt()` completely when `action == null` (DoTs) or for non-physical/non-magic special attacks.
  - **`M07.03b` (S1):** `CalcPhysicalAttack` (`0x44d1f8`, `0x44d238`) runs 1 discrete `Rand(100) < trunc0(finalInt * 100)` roll unconditionally on every physical hit (even if target is not chanting/performing) plus a 2nd independent `Rand(100) < 33` roll on crits; `CalcMagicalAttack` (`0x44f13a`) runs `Rand(100) < 33` on magic crits. `Battle.cs:2574, 2597` and `Formulas.cs:296` skip RNG when not chanting/performing and combine both probabilities into a single continuous `Rng.Random() < 1 - (1-rate)*(1-0.33)` draw. (Note: intentional mod patch **`X14`** changing `+ (1 + modifier)` to `* (1 + modifier)` is faithfully gated via `Options.InterruptProduct ?? Data.InterruptProduct` at `Formulas.cs:292`.) *Reach:* Active on every physical hit and every crit in combat (RNG stream alignment + exact crit-interrupt quantization). *Fix:* Use discrete `Rng.RandRange(100) < threshold` and independent `Rng.RandRange(100) < 33` draws matching `0x44d1f8`/`0x44d238`/`0x44f13a`.

---

### M07.04 Enemy & Boss Immunity Bitmask (`[enemyParam+0x54]` / `EnemyData.pck +0x3c`)

**Verdict:** MATCH

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

tools/enemy_data.py:51
```python
IMMUNITY_BITS = {2: 'stun', 3: 'sleep', 4: 'silence', 5: 'petrification', 6: 'instant death', 7: 'freeze', 8: 'poison',
                 9: 'paralysis', 10: 'shadow sew', 11: 'slow', 12: 'turn delay'}
STEAL_BIT = 15          # set when Item Steal works on the enemy (0x4503c5)
SNACK_BIT = 14          # set when the enemy can be turned into a snack (0x481488: the other way round)
```

engine_cs/src/DtEngine/Units.cs:781
```csharp
            unit.Snack = e.Snack;
            unit.Adult = ((e.Flags >> ADULT_BIT) & 1) != 0;
```

engine_cs/src/DtEngine/Battle.cs:2759
```csharp
                    bool allowed = !item || (target.EnemyId != T.NONE && Data.Enemies.TryGetValue(target.EnemyId, out var er) && ((er.Flags >> 15) & 1) != 0);
```

- Exact match: All 16 bits of `EnemyData.pck +0x3c` (`[enemyParam+0x54]`) match the vanilla binary (`bits 2..12` ailments/turn delay, `bit 13` adult/age flag for `149`/`150`, `bit 14 == 1` allows Snackification `84` verified at `0x48148c jne`, `bit 15 == 1` allows Item Steal `61` verified at `0x4503c7 je`, and `bits 0..1` boss/death flags).

---

### M07.05 Player Equipment, Elemental Resistance, and Status Immunity Gates

**Verdict:** S1

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
```

engine_cs/src/DtEngine/Battle.cs:2826
```csharp
                if (effect == 121 && hostile && !target.Immune("petrification") && target.Resistance(6) < 100 && !Nullified(target, 120))
                {
                    // 0x4f99c1..0x4f9b6b: Instant Petrify checks barrier (101/102/181), attaches Status(120) at Stage = 3,
                    // ends performances, and clears all other statuses while keeping Alive = true and HP intact.
                    if (!ConsumeBarrier(target))
                    {
                        target.SetStatus(new Status(120, 1, 0, unit) { Stage = 3 });
                        CompletePetrify(target);
                    }
                    continue;
                }
```

- **Sub-bugs:**
  - **`M07.05a` (S1):** All equipment immunity enchants (`129..137, 139`), `All Resistances 100` (`192`), and Special Petrification (`121`) Earth resistance `< 100` match the binary (`Battle.cs:2826, 3029-3039`, `Units.cs:402`). However, the Stage-3 Petrification (`vtable+0xc8`) target-state immunity gate at `0x483504`, `0x481ef4`, and `0x4f9950` is completely missing from `Battle.cs:2826` (`121`), `Battle.cs:3005` (`ApplyAilment`), and `Units.cs:212` (`SetStatus`), allowing `121` and other statuses/ailments to re-trigger on a Stage-3 Petrified target (and consume barriers or re-run `CompletePetrify`). *Reach:* Active in any battle where a unit is Stage-3 Petrified and targeted by AoE `121` or ailments/statuses. *Fix:* Add `!(target.St[120] != null && target.St[120].Stage >= 3)` to `Battle.cs:2826`, `Battle.cs:3005`, and `Units.cs:212`.

---

### M07.06 Gradual & Instant Petrification Lifecycle (`120`, `121`)

**Verdict:** S0

```asm
0048305a  inc      eax
0048305b  mov      dword ptr [ecx + 0x28], eax
0048305e  cmp      eax, 3
00483061  jne      0x4831d9
0048309e  call     0x41f920
00483115  call     dword ptr [eax + 0x6c]
004fbd95  mov      eax, dword ptr [eax + 0x38]
004fbda2  mov      eax, dword ptr [eax + 0xc8]
00436c82  call     0x43a4a0
00436c92  mov      dword ptr [edi + 0x18], 0xf
```

engine_cs/src/DtEngine/Battle.cs:1016
```csharp
        Lost LostTurnHard(Unit unit)
        {
            if (!unit.Alive) return Lost.Skip;
            // 0x436c3f..0x436d4c & 0x4fb590..0x4fb63f: Phase 5 (+0xc8) skips only stage>=3 petrification; Phase 6 (+0xbc) skips Sleep (116); Phase 7 Paralysis (115) 30%.
            var pet = unit.St[120];
            if ((pet != null && pet.Stage >= 3) || unit.St[116] != null) return Deny(unit, Lost.Skip);
            if (unit.St[115] != null && Rng.RandRange(100) < 30) return Deny(unit, Lost.Skip);
            return Lost.No;
        }
```

engine_cs/src/DtEngine/Battle.cs:813
```csharp
        void CompletePetrify(Unit unit)
        {
            // 0x48305a..0x4831eb, 0x4f99c1..0x4f9b6b, 0x4fa870:
            // Stage-3 petrification leaves HP intact and Alive = true, ends performances/chant,
            // and clears all other statuses while preserving Status(120) at Stage = 3.
            EndParts(unit, PerfParts.All);
            var pet = unit.St[120];
```

- **Sub-bugs:**
  - **`M07.06a` (S0):** At Inner Turn-Start State 5 (`0x436c3f..0x436c9e`), Stage-3 Petrified **enemies** (`[unit+0x78] == 0`) are immediately defeated and removed via `CBattleBase::_SetDead` (`0x43a4a0`, `PhaseNo = 15`), and `vtable+0xe8` (`IsAlive`) returns `false` for ANY Stage-3 Petrified unit (excluding them from targeting pools, party-wipe checks, and enemy-defeat checks). `Battle.cs:1020-1021` treats Stage-3 Petrified enemies identically to players (merely skipping their turn forever while leaving `Alive = true` and targetable!), so a fully petrified enemy NEVER dies from petrification and stalls battles until manually killed by HP damage, while Stage-3 Petrified players still soak enemy hits and prevent party wipe (`M04.06a`). *Reach:* Active in every battle where Petrification (`120`/`121`) reaches Stage 3 on either side (e.g. Gorgon/Medusa/Basilisk fights and player Stone/Petrify builds). *Fix:* Call `Fall(unit, null)` (defeat enemy) in Inner State 5 when `unit.Side == Unit.ENEMIES && pet.Stage >= 3`, and define `IsFightable = Alive && !IsFullPetrified` for targeting (`M04.06a`) and `Over()` win/loss checks.
  - **`M07.06b` (S1):** As noted in `M06.01a` and `M06.01c`, `Units.cs:212` `SetStatus` does not reject new statuses on a Stage-3 Petrified unit (`0x4f9950`) and `Units.cs:236` `PopStatus(120)` does not call `ResyncAllyPerformances` (`0x43cfb0`) when Petrification is cured. *Reach:* Active whenever a petrified unit is hit by buffs/ailments or cured by Nurse/Panacea. *Fix:* Enforce the Stage-3 guard in `SetStatus` and resync ally performances on `120` cure.

---

### M07.07 Ailment Self-Cure (`CCommandProbabilityBase`) & Duration Tick (`CCommandTurnBase`)

**Verdict:** S1

```asm
0048d1c0  mov      eax, dword ptr [eax + 0xbc]
0048d1d0  mov      eax, dword ptr [eax + 0x8c]
0048d217  push     0x64
0048d219  call     0x490790
0048d21e  mov      ecx, dword ptr [ebx + 0x28]
0048d221  cmp      eax, ecx
0048d223  jb       0x48d241
0048d225  lea      eax, [ecx + 0xa]
0048d228  mov      dword ptr [ebx + 0x28], eax
```

engine_cs/src/DtEngine/Battle.cs:775
```csharp
        void RollAilmentRecovery(Unit unit)
        {
            // Inner State 1 (0x43692f..0x436b60): natural recovery for recovering ailments (113..117, 122) runs BEFORE LostTurn.
            int n = unit.StCount;
            if (n == 0) return;
            var order = n <= tickScratch.Length ? tickScratch : new int[n];
            for (int i = 0; i < n; i++) order[i] = unit.StatusAt(i);
            for (int k = 0; k < n; k++)
            {
                int effect = order[k];
                if (!IsAilment[effect] || effect == 118 || effect == 119 || effect == 120 || effect == 123) continue;
                var s = unit.St[effect];
                if (s == null) continue;
                int chance = s.HasData ? PyMath.Int(s.Data) : 0;
                if (Rng.RandRange(100) < chance) unit.PopStatus(effect);
                else s.WithData(chance + 10);
            }
        }
```

- **Sub-bugs:**
  - **`M07.07a` (S1):** Weapon normal-attack ailment proc enchants (`153..157, 165`, `0x421287..0x4216d2`) initialize `cureChance = 0` (`0%`), whereas `Battle.cs:3023` sets `start = 5` (`5%`) for all non-Third-Eye-Wide ailment applications (duplicate root cause with `M07.02a`). *Reach:* Active on every weapon ailment proc (`153..157, 165`). *Fix:* Pass `start: 0` for weapon-enchant ailment procs.
  - **`M07.07b` (S1):** Both `CheckProbabilitySelfCure_0x48d180` (`0x48d1c0..0x48d1d8`) and `TickTurnDuration_0x48d590` (`0x48d5bd..0x48d5d7`) check `target.HasSleep() && cmd.vtable+0x8c` (`IsSleepCleared`) to expire compatible statuses immediately without consuming RNG. `Battle.cs:775-811` omit this Sleep-expiry check in both `RollAilmentRecovery` and `DecrementTimedStatuses`. *Reach:* Active whenever Sleep (`116`) coexists with a `vtable+0x8c` status (`M06.01b`, `M06.06a`). *Fix:* Add the `unit.St[116] != null && Data.IsSleepCleared(effect)` immediate-expiry branch to `RollAilmentRecovery` and `DecrementTimedStatuses`.

---

### M07.08 Crowd-Control Turn-Start Gates & Action Restrictions (`113`–`118`, `120`, `122`, `123`, `203`, `259`, `283`)

**Verdict:** S0

```asm
00436caa  mov      eax, dword ptr [eax + 0xbc]
00436d11  mov      eax, dword ptr [eax + 0xb8]
00436d22  call     0x505ac0
00436d27  cmp      eax, 0x1e
00436d89  push     0x103
00436e2d  push     0x11b
00436eb6  push     0xcb
00455cc5  mov      eax, dword ptr [eax + 0xb4]
00455d76  mov      eax, dword ptr [eax + 0xc0]
00455d94  mov      eax, dword ptr [eax + 0xd0]
```

engine_cs/src/DtEngine/Battle.cs:1026
```csharp
        Lost LostTurnSoft(Unit unit)
        {
            foreach (var other in OpponentsArray(unit))
            {
                if (other.Has(259) && Roll(other.Value(259))) return Deny(unit, Lost.Empty);
                if (other.Has(283) && Roll(other.Value(283))) return Deny(unit, Lost.Skip);
            }
            if (unit.Has(203) && Roll(unit.Value(203))) return Deny(unit, Lost.Skip);
            return Lost.No;
        }
```

engine_cs/src/DtEngine/Battle.cs:838
```csharp
            if (!extraTurn)
            {
                // Esarhaddon (311)
                if (unit.Has(311))
...
                // Inner State 2: Third Eye Wide (345) of each opponent — initializes recovery chance at 0% (0x47ee00).
                foreach (var other in OpponentsArray(unit))
                {
                    if (other.HasUnique && other.UniqueEffect == 345 && Roll(other.UniqueValue))
```

engine_cs/src/DtEngine/Policy.cs:267
```csharp
        static void ComputeOptions(Battle battle, Unit unit, bool silenced, bool frozen, List<(Skill skill, int level)> found)
        {
            found.Clear();
            bool noMagic = silenced || (battle.ZoneInfo != null && battle.ZoneInfo.NoMagic);
            int tp = unit.Tp;
            var usable = GetUsableSkills(battle.Data, unit);
            for (int i = 0; i < usable.Length; i++)
            {
                var (skill, level) = usable[i];
                if (skill.IsMagic && noMagic) continue;
                if (skill.IsTechnique && frozen) continue;
                if (Battle.EffectiveTpCost(unit, skill, level) > tp) continue;
                found.Add((skill, level));
            }
        }
```

- **Sub-bugs:**
  - **`M07.08a` (S0):** In Inner State 9 (`0x436d60..0x436e0b`), when Warning Shot (`259`) procs on an opposing unit `opp`, the binary sets `opp.isConfusedAttack = 1` (`[opp+0x105] = 1` -> `0.3x` physical damage) and **queues a basic attack from `opp` targeting `actor`** (`PhaseNo = 12`) — it does NOT simply cancel the actor's turn with no attack! Furthermore, State 9 checks ALL opponents for `259` BEFORE State 10 (`0x436e0c`) checks ALL opponents for Mesmerized (`283`). `Battle.cs:1026-1035` completely omits `opp`'s `0.3x` Warning Shot attack, returns `Lost.Empty` (cancelling `actor`'s turn with zero damage dealt), AND interleaves `259` and `283` per opponent in a single loop! *Reach:* Active in every battle with Archer/Sniper/Etoile/enemy Warning Shot (`259`) or Diva/enemy Mesmerized (`283`). *Fix:* Split State 9 (`259` loop) and State 10 (`283` loop); on `259` proc, execute a `0.3x` basic attack from `other` against `unit` (and respect binary phase handoff).
  - **`M07.08b` (S0):** Shadow Sew (`123`, `0x455d94`, `0x455a39`) blocks ALL skills (every category) and Co-op skills. `Policy.cs:267-281` and `Battle.cs:1052` check only Silence (`117`) and Freeze (`114`), never blocking skills when `unit.St[123] != null` (`M04.15a`). *Reach:* Active whenever any enemy inflicts Shadow Sew (`123`) on a party member. *Fix:* Reject all skills in `Policy.ComputeOptions` and in `Battle.NextAction`/`IsLegalAction` whenever `unit.St[123] != null`.
  - **`M07.08c` (S0):** Stage-3 Petrified enemies are not defeated at Inner State 5 (`Battle.cs:1020`, see `M07.06a`). *Reach:* Active on every Stage-3 Petrified enemy. *Fix:* Defeat enemy at Inner State 5 via `Fall`.
  - **`M07.08d` (S1):** At `0x4365ff`, Inner Turn-Start States `0..23` are skipped entirely for Dolls and Summons/Guests (`unitId >= 2000`; summons only run the dedicated `199` hook at `0x436343`). `Battle.cs:838` only gates Inner States `0..22` on `!extraTurn`, so Dolls (`Kind.Doll`) and Summons/Guests (`Kind.Summon`) falsely trigger opponent Third Eye Wide (`345`), Warning Shot (`259`), Mesmerized (`283`), Undaunted (`355`), and Poison/Regen ticks on their turns! *Reach:* Active in every battle featuring Maid Dolls, Shadows, Genjimaru, Arrow, Summons, or Guest allies. *Fix:* Gate Inner States `0..22` on `!extraTurn && unit.Kind != Kind.Doll && unit.Kind != Kind.Summon` (running only the `199` tick for `Kind.Summon` per `0x436343`).

---

### M07.09 Sleep Combat Modifiers & Wake-on-Hit (`116` / `0x74`)

**Verdict:** S0

```asm
004fa056  mov      eax, dword ptr [eax + 0x8c]
004fa05c  call     eax
004fa06f  call     dword ptr [edx + 0x68]
0044cd2f  mov      eax, dword ptr [eax + 0xbc]
0044cd3e  lea      eax, [eax + eax*2]
0044cd44  sar      eax, 1
0047ea41  cmp      edx, 0x7fffffff
0047ea47  je       0x47eacb
0047ea6d  push     0x74
0047ea80  call     dword ptr [eax + 0x64]
```

engine_cs/src/DtEngine/Battle.cs:1124
```csharp
            else if (acted && unit.Chant == null && !Over())
            {
                if (unit.Has(288) && Roll(unit.Value(288))) unit.Extra = 1;
                else if (unit.Has(289) && Roll(unit.Value(289))) unit.Extra = 2;
                else if (unit.HasUnique && unit.UniqueEffect == 354 && Roll(unit.UniqueValue))
```

engine_cs/src/DtEngine/Battle.cs:2571
```csharp
            if (target.Alive && amount > 0)
            {
                target.PopStatus(116);
                if (target.Chant != null || Performing(target))
                    Interrupt(target, amount, critical, action == null || !action.Magic);
            }
```

- **Sub-bugs:**
  - **`M07.09a` (S0):** Sleep (`116`) application in `Battle.cs:3024` does not strip active statuses with `vtable+0x8c == true` (`0x4fa056`, 36 command IDs including Cover `171`, Parry `180`, Limit Field `190`, Puppets `228..233`, etc.; same root cause as `M06.01b`). *Reach:* Active whenever Sleep lands on a unit holding any `vtable+0x8c` status. *Fix:* Strip all active `vtable+0x8c` statuses when `116` is applied.
  - **`M07.09b` (S1):** At `0x43905f`, Extra-Turn Passives (`288` Double Action, `289` Triple Action, `354` Unique) are blocked when the actor is Asleep (`HasSleep_116`, e.g. put to sleep mid-action by a reactive/self effect). `Battle.cs:1124` checks only `acted && unit.Chant == null && !Over()`, omitting `unit.St[116] == null`. *Reach:* Active if an extra-turn bearer becomes Asleep before turn end. *Fix:* Require `unit.St[116] == null` (and `!unit.IsFullPetrified`) at `Battle.cs:1124`.
  - **`M07.09c` (S1):** `CCommand::Execute` (`0x47ea41..0x47ea83`) wakes Sleep (`116`) whenever `res.hpDamage != 0x7fffffff` (the "no HP delta" sentinel) and target survives — which INCLUDES `hpDamage == 0` hits negated by Clone `101/102`, Barrier System `181`, Parry `180`, Pretend `310`, Alter Fate `349`, Elegant Dancing `285`, Knock Down `305`, as well as 0-damage hits! `Battle.cs:2571` gates wake-up on `amount > 0` inside `TakeDamage`, and `Voided()` (`Battle.cs:1841-1884`) returns before `TakeDamage`, so none of those 0-damage negated hits wake a sleeping target. *Reach:* Active whenever a sleeping unit blocks a hit with Clone/Barrier/Parry/Alter Fate/Pretend/Elegant Dancing/Knock Down or takes 0 HP damage. *Fix:* Wake Sleep (`target.PopStatus(116)`) on every non-sentinel HP-delta hit (including `amount == 0` and voids `349, 310, 285, 305, 180, 101, 102, 181`, while NOT waking on physical miss, `250`, nullify enchants `120..128`, `192`, or `182`).

---

### M07.10 Exclusive Hit-Consuming Barriers (`101` Clone, `102` Clone, `181` Barrier System) & `vtable+0x84` Exclusivity

**Verdict:** S1

```asm
0041f947  push     0x65
0041f954  call     dword ptr [eax + 0x48]
0041f96d  mov      dword ptr [ebx + 0x1c], 0
0041faaf  push     0x66
0041fbd0  push     0xb5
00422671  mov      edx, 0x8c
00422682  mov      edx, 0x8d
00422693  mov      edx, 0x8e
004226ab  call     0x41f920
00422c25  mov      edx, dword ptr [edx + 0x68]
00422c31  cmp      dword ptr [eax + 0x2c], 1
00422c4b  call     0x41f920
```

engine_cs/src/DtEngine/Battle.cs:1874
```csharp
            for (int k = 0; k < 3; k++)
            {
                int effect = k == 0 ? 101 : k == 1 ? 102 : 181;
                var s = target.St[effect];
                if (s != null && !(action.Has(140) || action.Has(141) || action.Has(142)) && (action.Physical || action.Magic))
                {
                    s.Value -= 1;
                    if (s.Value <= 0) target.PopStatus(effect);
                    return true;
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:2682
```csharp
                if (IsAilment[effect])
                {
                    if (Aimed(action, target) || effect == 123)
                    {
...
                        else ApplyAilment(unit, target, effect, value, action);
                    }
                    continue;
                }
```

- **Sub-bugs:**
  - **`M07.10a` (S1):** In `CActionPatternBase::_Task` (`0x422c10..0x422c74`), the pure-ailment barrier gate scans ALL landed ailments on a hit, and if ANY ailment (`vtable+0x68 == 1`) landed, calls `CheckExclusiveBarrier_0x41f920` ONCE — consuming **1 charge** and erasing ALL landed ailments on that hit! `Battle.cs:2682-2696 -> 3011` calls `ConsumeBarrier(target)` independently inside `ApplyAilment` for EACH ailment effect slot, so a multi-ailment enemy attack (e.g., Bad Breath / multi-status skills) burns 2–5 Clone/Barrier charges on a single hit (or breaks through a 1-charge barrier and still lands the 2nd ailment)! *Reach:* Active on every multi-ailment vanilla enemy attack / player skill against Clone (`101`/`102`) or Barrier System (`181`). *Fix:* Evaluate all ailment rolls on a hit first; if any `IsTrueAilmentId` landed, call `ConsumeBarrier(target)` once and discard all landed ailments if blocked.
  - **`M07.10b` (S1):** `Battle.cs:1878` gates damage-hit exclusive barriers on `(action.Physical || action.Magic)`, whereas binary `0x42265f` triggers whenever `(res.hpDamage != 0x7fffffff || res.tpDamage != 0x7fffffff)` (unless `140/141/142` is present). Thus non-0/1 Special Damage attacks (fixed damage `63/64`, Breath/special HP damage `135`, etc.) and Anti-TP (`2`) bypass Clone `101/102` and Barrier System `181` in the simulator! *Reach:* Active whenever Special Damage or TP-damage skills/enemy attacks hit a unit protected by `101/102/181`. *Fix:* Replace `(action.Physical || action.Magic)` at `Battle.cs:1878` with a check for any HP/TP damage payload (not `140/141/142`).
  - **`M07.10c` (S1):** `Battle.cs:1882` returns `true` without waking Sleep (`116`), whereas `0x41f96d` sets `res.hpDamage = 0` (`!= 0x7fffffff`), waking Sleep at `0x47ea41` (`M07.09c`). *Reach:* Active when a sleeping unit absorbs a hit with `101/102/181`. *Fix:* Pop Sleep (`116`) when `101/102/181` blocks an HP-damage hit.

---

### M07.11 Non-Exclusive Nullify Shields, Mitigation Barriers & Block Priority Chain (`179`, `180`, `182`, `183`, `188`, `189`, `191`, `192`, `193`, `194`, `261`, `285`, `305`, `310`, `349`)

**Verdict:** S1

```asm
00421ca9  push     0x15d
00421dc4  push     0x136
0042208e  push     0x11d
00422207  push     0x131
004223d4  push     0xb4
00422596  push     0xfa
00422b62  push     0xb3
00422b69  push     0xb7
00422b6e  call     dword ptr [eax + 0x64]
0047f8aa  push     0x105
0047f936  push     0xbc
```

engine_cs/src/DtEngine/Battle.cs:2126
```csharp
            var guard = target.St[MATERIAL_GUARD];
            if (guard != null && (guard.Source == null || (guard.Source.Alive && guard.Source.Shield))) other += guard.Value;
```

engine_cs/src/DtEngine/Battle.cs:2219
```csharp
            double cut = (target.HasEnchants ? Math.Max(-0.25, -(0.10 * target.Pieces(68) + 0.05 * target.Pieces(69) + 0.08 * target.Pieces(70) + 0.04 * target.Pieces(71))) : 0.0) + target.StatusValue(183);
```

engine_cs/src/DtEngine/Battle.cs:1842
```csharp
            if (target.Has(PRETEND) && action.Physical && Roll(target.Value(PRETEND)))
            {
                Counter(target, unit);
                return true;
            }
...
            if (target.Has(KNOCK_DOWN) && action.Physical && action.Reach == T.LONG &&
                (target.Kind != Kind.Member || target.Weapon != null) && Roll(target.Value(KNOCK_DOWN)))
            {
                Counter(target, unit);
                return true;
            }
```

engine_cs/src/DtEngine/Battle.cs:570
```csharp
                if (unit.Hp <= 0.4 * unit.MaxHp && unit.Has(261)) bonus += unit.Value(261);
```

- **Sub-bugs:**
  - **`M07.11a` (S1):** At `0x422b58..0x422b71`, `Physical Barrier / Material Guard (179 / 0xb3)` is consumed (`RemoveStatusById(0xb3)`) after 1 physical hit, and `Magic Barrier (183 / 0xb7)` is consumed (`RemoveStatusById(0xb7)`) after 1 magical hit! `Battle.cs:2126, 2219` read `target.St[179]` and `target.StatusValue(183)` and **NEVER consume/pop either status** on hit — making Material Guard (`179`) and Magic Barrier (`183`) last for their entire multi-turn duration across unlimited hits! *Reach:* Active on every Paladin/Valkyrie/Bishop/enemy using Material Guard (`179`) or Magic Barrier (`183`, e.g. Magic Barrier skill). *Fix:* Pop `target.PopStatus(179)` after resolving a physical hit and `target.PopStatus(183)` after resolving a magical hit.
  - **`M07.11b` (S1):** `Battle.cs:1844, 1857` invoke `Counter(target, unit)` when `Pretend (310)` or `Knock Down (305)` triggers. In the vanilla binary (`0x421db8..0x421f57` for `310`, `0x4221ee..0x4223b2` for `305`), NEITHER passive triggers a counterattack — both ONLY set `hpDmg = 0, tpDmg = 0` and negate the hit (only `Counter-Parry 250` at `0x422553` and `Reprisal 249` queue counterattacks)! *Reach:* Active on every Kunoichi/Etoile/Sniper/enemy with `310` (Pretend) or `305` (Knock Down). *Fix:* Remove `Counter(target, unit)` from both the `PRETEND` (`310`) and `KNOCK_DOWN` (`305`) blocks in `Voided`.
  - **`M07.11c` (S1):** Additional chain divergences inside `Voided` / `Fall`: (1) `Counter-Parry 250` (`Battle.cs:1866`) omits `!inCounter` (`0x422559`, `M04.04a`); (2) `Resuscitate 188` (`Battle.cs:2626`) skips `OnDeathCleanup` (`0x4fc890`) and `OnRevive` (`0x43cfb0`) (`M05.04a`/`b`); (3) `349, 310, 285, 305, 180` fail to wake Sleep (`116`) (`M07.09c`). *Reach:* Active in standard combat with `250`, `188`, `349`, `310`, `285`, `305`, or `180`. *Fix:* Add `!inCounter` to `250`, run death/revive lifecycle hooks for `188`, and wake Sleep on zeroed-damage voids.
  - **`M07.11d` (S2):** `Stamina (261)` in `Battle.cs:570` compares `unit.Hp <= 0.4 * unit.MaxHp` in floating point instead of integer `(MaxHP * 40) / 100` (`0x47f86c`), and `Elegant Dancing (285)` tracks `spent.Add((target, 285))` in a battle-wide set (`Battle.cs:1850`) that is never cleared on death/revive (unlike binary `target.danceState` reset). *Reach:* Rare edge cases (`MaxHp % 5 != 0` boundary for `261`; revived unit with `285`). *Fix:* Use `(unit.MaxHp * 40) / 100` for `261` and reset `285` state on death/revive.

---

### M07.12 Ailment Cure, Recovery Skills, Cure Items & Turn-Start Purge (`106` Nurse, `105` Resurrect, `311` Esarhaddon, `ItemResult_0009`/`0010`/`0011`)

**Verdict:** S1

```asm
00481aa3  call     0x61e650
00481aaa  mov      edx, 7
00481ab4  cmova    eax, edx
00481ad3  push     dword ptr [esi*4 + 0x6cc79c]
00481b12  cmp      ecx, 8
00481b39  call     dword ptr [eax + 0x90]
004819a5  mov      eax, dword ptr [eax + 0x38]
00436727  push     0x137
0043676a  call     0x61e650
0050fbcd  call     dword ptr [eax + 0x80]
0050fbed  call     0x490790
0050fed8  call     dword ptr [eax + 0x80]
00510183  mov      eax, dword ptr [eax + 0x38]
00510194  mov      eax, dword ptr [eax + 0xc8]
```

engine_cs/src/DtEngine/Battle.cs:3161
```csharp
            else if (effect == 105)
            {
                if (!target.Alive)
                {
                    target.Alive = true;
                    target.Hp = Math.Max(1, PyMath.Int(target.MaxHp * value));
                    target.NextTime = Time + Wait(target);
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:3542
```csharp
                else if (kind == 8 && !target.Alive)
                {
                    target.Alive = true;
                    target.Hp = Math.Max(1, PyMath.Int(target.MaxHp * value / 100.0));
                    target.NextTime = Time + Wait(target);
                }
                else if (kind == ITEM_CURE_ONE)
                {
                    // 0x50fbcd: cure items clear true ailments 113..122 only (never Shadow Sew 123).
                    var present = new List<int>();
                    foreach (int e in AILMENT_IDS) if (e != 123 && target.St[e] != null) present.Add(e);
                    if (present.Count > 0) target.PopStatus(present[Rng.ChoiceIndex(present.Count)]);
                }
                else if (kind == ITEM_CURE_ALL)
                {
                    var present = new List<int>();
                    foreach (int e in AILMENT_IDS) if (e != 123 && target.St[e] != null) present.Add(e);
                    foreach (int e in present) target.PopStatus(e);
                }
```

- **Sub-bugs:**
  - **`M07.12a` (S1):** `Nurse (106)` (`Battle.cs:2740`) and `Resurrect (105)` (`Battle.cs:3165`) omit `ResyncAllyPerformances` (`0x43cfb0`) on Petrify cure / revival (`M05.04b`, `M06.01c`); `Battle.cs:1482` lets enemy Nurse target dead enemies (`M04.07b`); and `Battle.cs:3167` overwrites `target.NextTime = Time + Wait(target)` on revive instead of preserving/resetting gauge per binary (`M05.04b`). Also `Battle.cs:843, 2739` use `PyMath.Int` instead of `0x61e650` `round_f32_to_i32` for `311` and `106` (`M06.07a`). *Reach:* Active whenever Nurse (`106`) cures Petrification or Resurrect (`105`) revives a party member while Songs/Dances/Geasses are active. *Fix:* Invoke `ResyncAllyPerformances(target)` on `120` removal and revival, exclude dead units from enemy Nurse, and match binary ATB gauge behavior on revive.
  - **`M07.12b` (S1):** Cure items `6` (`ItemResult_0009`) and `7` (`ItemResult_0010`) at `Battle.cs:3548-3560` omit the `!target.IsDead` (`vtable+0x38`) guard, omit Row/SideAll item target expansion (`w_0x5c` dropped per `M04.08a`), and omit `ResyncAllyPerformances` (`0x43cfb0`) when curing `120`; Revive item `8` (`ItemResult_0011`, `Battle.cs:3542`) omits `!IsFullPetrified` (`0x510194`), `ResyncAllyPerformances`, and overwrites `NextTime` (`M05.11b`). *Reach:* Active on all 60+ vanilla cure/revive battle items (`Types 6, 7, 8`). *Fix:* Add `!target.Alive` guards (`6, 7` require `Alive`, `8` requires `!Alive && !IsFullPetrified`), expand item targets via `w_0x5c`, and resync ally performances.

## Part: M08–M10 (Procs/Counters/Patterns, Dolls/Summons/Enchants & AI VM/Loaders)


- **Scope:** 48 rules (`M08.01..M08.14`, `M09.01..M09.15`, `M10.01..M10.19`)
- **Verdict Counts:** `MATCH=9` | `S0=11` | `S1=20` | `S2=7` | `MODEL-LIMIT=1`
- **Verified Mod Patches:** `X13` (`Data.ArcaneChance`), `X14` (`Data.InterruptProduct`), `X16` (`Data.ThirdEyeDispel`) all faithfully parameterized.
- **Verified Spec-Text Corrections (Checked Directly in Exe):** `M08.01` cmd `137` opposite-side break (`0x42027f`), `M09.12` `246+247`/`248+249` multiplicative stacking (`0x4fd291..0x4fd326`) & `0x61c040` = `ceil()`, `M09.13` Enchant `280` in both Phys & Mag (`0x44cd5a`/`0x44f009`), `M09.15` Enchant `51..56` / `39..44` / `61` signs, `M10.04` stop flag (`0x4325cf`), `M10.13` `+0x2c=DEX`/`+0x30=AGI` (`0x4f26db..0x4f2707`).

## M08 — Procs, Counters, After-Hit & Action Patterns (M08.01..M08.14)

### M08.01 Hit-Time Effects & Pre-Action Interception (253, 303, 137)
**Verdict:** S1

```asm
0044b100  call 0x61e650
0044b120  add byte ptr [ecx], bh
00420985  mov eax, dword ptr [eax + 0xb4]
004209bc  or al, 0x83
0042027f  je 0x4202e3
00420296  inc ecx
```

engine_cs/src/DtEngine/Battle.cs:1888
```csharp
        bool Hits(Action action, Unit target)
        {
            if (action.Furious) return true;
            double chance = HitChance(action, target);
            double dodge = StabDodge(action, target);
            int roll = Rng.RandRange(100);
            if (roll < PyMath.Round((chance - dodge) * 100)) return true;
            if (dodge != 0 && roll < PyMath.Round(chance * 100) && target.Alive) Counter(target, action.Actor);
            return false;
        }
```

engine_cs/src/DtEngine/Battle.cs:1319
```csharp
            foreach (var t in targets)
            {
                // Counter Whip answers a physical action, never one of a doll, the summon or a guest (P7.3 of the audit)
                if (t.Side != unit.Side && t.Has(303) && !unit.Has(307) && action.Physical && !NotACandidate(unit))
                {
                    Counter(t, unit);
                    break;
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:1495
```csharp
                        InsertionSortByTime(all);
                        var res = new List<Unit> { chosen };
                        int idx = all.IndexOf(chosen);
                        int extra = Math.Max(0, PyMath.Int(action.Val(EXTRA_TARGETS, 0)) - 1);
                        if (idx >= 0)
                        {
                            for (int step = 1; step <= extra && idx + step < all.Count; step++)
                            {
                                var nxt = all[idx + step];
                                if (nxt.Side != chosen.Side) break;
                                res.Add(nxt);
```

**Audit Notes:** Verified directly against exe `0x42027f je 0x4202e3` that cmd `137` splash breaks on opposite side, matching `Battle.cs:1504`. However, Passive `253` and Counter Whip `303` have active S1 bugs.

**Discrepancies:**
- **M08.01a (S1)** [`0x44b100..0x44b20f` vs `engine_cs/src/DtEngine/Battle.cs:1895`]: Passive 253 (Flowing Water Stance / Stab Dodge) only logs a dodge message in binary (0x44b100..0x44b20f) with NO counterattack; Battle.cs:1895 erroneously calls Counter(target, action.Actor). **Reach:** 1 vanilla player passive (Flowing Water Stance, active on every dodged Stab hit). **Fix:** Remove the Counter(target, action.Actor) call from Hits() at Battle.cs:1895 when dodge != 0.
- **M08.01b (S1)** [`0x420985..0x420ab4` vs `engine_cs/src/DtEngine/Battle.cs:1319`]: Counter Whip (303) Phase 9 (0x420985..0x420ab4) downgrades the attacker's queued skill to a 1-hit basic attack if the pre-action counter inflicts Freeze on a Technique or Silence on Magic; Battle.cs:1319-1327 never checks for Freeze/Silence downgrade after Counter(t, unit). **Reach:** 1 player passive + enemy Counter Whip users; fires whenever a Counter Whip weapon/enchant inflicts Freeze or Silence. **Fix:** After Counter(t, unit) in Perform(), if unit is alive and Frozen (on Technique) or Silenced (on Magic), replace action with a 1-hit plain Attack.
- **M08.01c (S2)** [`0x420296` vs `engine_cs/src/DtEngine/Battle.cs:1498`]: cmd 137 (EXTRA_TARGETS splash) rounds its target count via round_f32_to_i32 (0x61e650 at 0x420296), whereas Battle.cs:1498 truncates via PyMath.Int (identical on vanilla integer values 2..5). **Reach:** 15 vanilla skills/attacks with cmd 137 (all carry exact integers 2..5 in vanilla). **Fix:** Use PyMath.Round instead of PyMath.Int for cmd 137 extra target count.

### M08.02 _AfterHit1 (Drain 75/76, Devil's Whisper 320, Status Application)
**Verdict:** S1

```asm
00422cf0  dec edx
00422d09  cmp dword ptr [eax + 0x1c], 0x7fffffff
00423560  push ebp
00423764  add byte ptr [eax], al
```

engine_cs/src/DtEngine/Battle.cs:2541
```csharp
            else fatal = amount >= target.Hp;
            if (fatal && target.Has(254) && Roll(target.Value(254))) amount = target.Hp - 1;
            int before = target.Hp;
            LoseHp(target, amount, unit);
            if (unit != null && unit.Side != target.Side)
            {
                Grow(unit.Position);
                RecDamage[unit.Position] += Math.Min(before, amount);
                Rec?.Damage.Add(new RecKey(unit), Math.Min(before, amount));
```

engine_cs/src/DtEngine/Battle.cs:2673
```csharp
            // Capture pre-hit ailment state BEFORE the current hit's ailments are applied (0x422b82 runs before 0x422bd0).
            bool preAiling = hostile && dealt != 0 && target.Alive && HasTrueAilment(target);
            int count = action.Count;
            // the list is walked as worked out before the hit; copy it as the loop can change nothing of it
            for (int i = 0; i < count; i++)
...
            // Devil's Whisper (320; 0x422b82, 0x422cf1..0x422d32, 0x423560): fires only on damaging hits (dealt != 0) when
            // the target ALREADY had a true ailment (113..122, excluding 123) before the hit's own ailments were applied.
            if (preAiling && target.Alive && (action.Has(320) || unit.Has(320)))
                ApplyAilment(unit, target, 119, First(action, unit, 320), action);
            // the answers of the unit hit (0x423cd0): skipped whole when the attacker is a doll, the summon or a guest (0x423d0e - 0x423d38)
```

**Audit Notes:** In the binary, `_AfterHit1` (including Devil's Whisper `320`) executes BEFORE `_AfterHit2` (Endure `254`), merging cmd `119` lethal damage into `res.hpDamage` so Endure `254` can save the target.

**Discrepancies:**
- **M08.02a (S1)** [`0x422d09, 0x423560..0x4237e6` vs `engine_cs/src/DtEngine/Battle.cs:2868`]: Devil's Whisper (320) runs in AfterHit AFTER TakeDamage/Endure 254 and calls ApplyAilment(119)->LoseHp, bypassing Endure 254; also Battle.cs:2674 gates preAiling on dealt != 0 instead of hpDamage != 0x7fffffff (0x422d09), skipping 0-damage hits. **Reach:** 2 enemy passives across 11 vanilla enemies (Devil's Whisper) + any Endure 254 bearer. **Fix:** Check hitLanded (not dealt != 0) for preAiling and route Devil's Whisper 119 lethal damage through Endure 254 before committing HP loss.

### M08.03 _AfterHit2 (Endure 254, Turn Delay 54, Lethal Snapshot)
**Verdict:** S1

```asm
0042388d  mov eax, dword ptr [edi + 0x1c]
004238eb  cvttps2pi mm1, xmm0
004239b6  add byte ptr [edx - 0x3f7bbeff], cl
004239e8  cli
```

engine_cs/src/DtEngine/Battle.cs:2541
```csharp
            else fatal = amount >= target.Hp;
            if (fatal && target.Has(254) && Roll(target.Value(254))) amount = target.Hp - 1;
            int before = target.Hp;
            LoseHp(target, amount, unit);
            if (unit != null && unit.Side != target.Side)
            {
                Grow(unit.Position);
                RecDamage[unit.Position] += Math.Min(before, amount);
                Rec?.Damage.Add(new RecKey(unit), Math.Min(before, amount));
```

engine_cs/src/DtEngine/Battle.cs:2725
```csharp
                if (effect == 54 && hostile)
                {
                    // 0x423a18..0x423a41: Turn Delay requires dealt > 0 and target still alive.
                    if (dealt > 0 && target.Alive && !target.Immune("turn delay") && Rng.RandRange(100) < PyMath.Int(value * 100)) Delay(target);
                    continue;
                }
                if (effect == 103 || effect == 9 || effect == 104 || effect == 105 || effect == 128 || effect == 129 || effect == 130 ||
```

**Audit Notes:** Note: `Options.SurvivalGuard` (`L46`) is inactive (`false`) in vanilla and Balance, so vanilla `amount >= target.Hp` matches `CurHP - origDmg <= 0`. However, Turn Delay `54` fails to respect the pre-Endure lethal snapshot.

**Discrepancies:**
- **M08.03a (S1)** [`0x42388d..0x423a26` vs `engine_cs/src/DtEngine/Battle.cs:2728`]: _AfterHit2 snapshots origDmg before Endure 254 clamps damage and gates Turn Delay (54) on CurHP - origDmg > 0, making Endure save and Turn Delay mutually exclusive; Battle.cs:2728 checks post-Endure dealt > 0 and target.Alive, erroneously applying Turn Delay 54 on Endure-saved hits. **Reach:** 45 vanilla skills/attacks carrying Turn Delay (54) against any Endure 254 bearer. **Fix:** Track whether Endure 254 triggered on the current hit (or pass origDamage >= hpBefore) and skip Turn Delay 54 when the raw hit was lethal.

### M08.04 Defensive Procs Inside _Task (Parry 180, Counter 250, Knock Down 305, Pretend 310)
**Verdict:** S0

```asm
00421e00  cvttss2si esi, xmm0
00422285  cmp edi, esi
00422296  mov dword ptr [ebx + 0x1c], 0
004223d4  push 0xb4
00422559  cmp byte ptr [eax + 0x11], 0
00422640  cmp byte ptr [esi + 0x10], al
0056c460  sub esp, 8
```

engine_cs/src/DtEngine/Battle.cs:1842
```csharp
            if (target.Has(PRETEND) && action.Physical && Roll(target.Value(PRETEND)))
            {
                Counter(target, unit);
                return true;
            }
            if (target.Has(285) && !spent.Contains((target, 285)) && (action.Physical || action.Magic))
            {
                target.PopStatus(285);
                spent.Add((target, 285));
                return true;
            }
            // Knock Down (305; 0x42222c..0x422246): requires the defender (if a player) to have a weapon equipped in slot 0.
            if (target.Has(KNOCK_DOWN) && action.Physical && action.Reach == T.LONG &&
                (target.Kind != Kind.Member || target.Weapon != null) && Roll(target.Value(KNOCK_DOWN)))
            {
                Counter(target, unit);
                return true;
            }
            // Parry (180; 0x4223b5..0x4223d9): requires physical action with non-neutral attribute.
            if (target.St[180] != null && action.Physical && attr != T.NEUTRAL)
            {
                if (Roll(target.St[180].Value)) target.PopStatus(180);
                return true;
            }
            if (target.Has(250) && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
            {
                if (Roll(target.Value(250)))
                {
                    Counter(target, unit);
                    return true;
                }
            }
```

**Audit Notes:** Verified `0x56c460` (`IsUnparryable`) checks `attr == 9` (Neutral), matching `Battle.cs:1861`. However, the Counter `250` sequential vs AoE pattern architecture and Knock Down/Pretend/Parry behaviors diverge severely.

**Discrepancies:**
- **M08.04a (S0)** [`0x422640..0x422656` vs `engine_cs/src/DtEngine/Battle.cs:1866`]: Counter 250 (Mind's Eye) branches on pattern flag10 (0x422640..0x422656): sequential patterns (A/B/C/T0105/M0140) counter immediately and abort remaining multi-hits, whereas AoE patterns (D/E/F/G/M0124) defer to Stage 2 of _CheckAfterAttackInterrupt (max 1 counter for entire AoE, suppressing Reprisal 249 & Arcane Shield 447). Battle.cs:1866-1873 counters immediately per hit, never aborts multi-hits, permits multiple AoE counters, and fails to suppress 249/447. **Reach:** 1 player passive (Mind's Eye) + 3 enemy passives across 47 vanilla enemies. **Fix:** Wire pattern flag10: on sequential patterns trigger immediate counter and break the remaining hit loop; on AoE patterns record deferredCounterSlot and execute once in Stage 2 before Reprisal/Arcane Shield.
- **M08.04b (S1)** [`0x421e00..0x421f57, 0x422285..0x4223ad` vs `engine_cs/src/DtEngine/Battle.cs:1857`]: Knock Down 305 (0x422285..0x4223ad) and Pretend 310 (0x421e00..0x421f57) ONLY void/zero damage in binary with NO counterattack; Battle.cs:1844 and Battle.cs:1857 erroneously call Counter(target, unit). **Reach:** 1 player passive + 4 enemy passives across 75 vanilla enemies (Knock Down 305) + Pretend 310 users. **Fix:** Remove Counter(target, unit) from Pretend 310 (Battle.cs:1844) and Knock Down 305 (Battle.cs:1857).
- **M08.04c (S1)** [`0x422559` vs `engine_cs/src/DtEngine/Battle.cs:1866`]: Counter 250 checks this.inCounter == 0 at 0x422559 before rolling; Battle.cs:1866 omits !inCounter, allowing Voided() to roll 250 during a counterattack and evade/void the counter hit. **Reach:** All Mind's Eye / enemy Counter 250 bearers struck by a counterattack. **Fix:** Add !inCounter to the Counter 250 condition at Battle.cs:1866.
- **M08.04d (S1)** [`0x422296, 0x4223d4` vs `engine_cs/src/DtEngine/Battle.cs:1854`]: Voided() returns early on Knock Down 305 (Battle.cs:1858) and Parry 180 (Battle.cs:1864) before AfterHit, skipping secondary status/ailment commands, whereas binary (0x422296, 0x4223d4) zeroes HP/TP damage inside _Task without aborting non-damage commands. **Reach:** 75 enemies + 1 passive (305) and all Parry 180 stances when hit by skills with secondary ailments/debuffs. **Fix:** Zero HP/TP damage for Knock Down 305 and Parry 180 instead of returning true from Voided() before AfterHit.

### M08.05 Post-Hit Passive Recording (Dark Aura 262, Slow Target 293, Reprisal 249, Arcane Shield 447)
**Verdict:** S1

```asm
00423d50  cmp byte ptr [ebx + 0x70], 0
004244dc  mov edx, 0x7a
0042467f  cmp byte ptr [ebx + 0x11], 0
004246b0  mov al, byte ptr [eax + 0x79]
00424728  cmp byte ptr [ebx + 0x78], 0
00424766  cmp eax, 0xf
```

engine_cs/src/DtEngine/Battle.cs:2579
```csharp
            if (!inCounter && target.Alive && target.HasUnique && target.UniqueEffect == 447 && unit != null && !NotACandidate(unit) && !unit.Has(307) && amount > 0)
            {
                int arcaneSet = Options.HasArcaneChance ? Options.ArcaneChance : Data.ArcaneChance;
                int arcane = arcaneSet != T.NONE && arcaneSet != 0 ? arcaneSet : ARCANE_CHANCE;
                if (Rng.RandRange(100) < arcane)
                {
                    Grow(target.Position);
                    arcaneDamage[target.Position] = amount;
                    arcaneDirty = true;
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:2871
```csharp
            if (hostile && dealt != 0 && !NotACandidate(unit))
            {
                // Sugar Coma (346; 0x4227d5..0x422822): fires post-damage/post-barrier when target survives a short-range hit.
                if (target.Alive && target.HasUnique && target.UniqueEffect == 346 && action.Reach == T.SHORT && Roll(target.UniqueValue))
                {
                    if (!unit.Immune("slow") && !Nullified(unit, 122))
                        unit.SetStatus(new Status(122, 1.0, 0, target).WithData(SUGAR_COMA_RECOVERY));
                    unit.SetStatus(new Status(168, -0.2, SUGAR_COMA_TURNS, target));
                }
                // Dark Aura: each stat debuff is set to -0.1, not deepened (0x423d9b onward)
                if (target.Has(262) && action.Physical && action.Reach == T.SHORT && !unit.Has(304))
                {
                    int points = PyMath.Int(target.Value(262));
                    int[] order = { 45, 44, 43, 42, 41, 46 };
                    int n = Math.Max(0, Math.Min(points < 0 ? order.Length + points : points, order.Length));
                    for (int k = 0; k < n; k++) unit.SetStatus(new Status(order[k], -0.1, DARK_AURA_TURNS, target));
                }
                // Slow Target (293; 0x424535..0x4245da): Slow (122) checks immune+Nullified; Speed -0.75 (168) applies independently.
                if (target.Has(293) && action.Reach == T.SHORT && Roll(target.Value(293)))
                {
                    if (!unit.Immune("slow") && !Nullified(unit, 122))
                        unit.SetStatus(new Status(122, 1.0, 0, target).WithData(SLOW_TARGET_RECOVERY));
                    unit.SetStatus(new Status(168, -0.75, SLOW_TARGET_TURNS, target));
                }
                // Reprisal rolls on every hit and writes the result on the target's record, the last hit's roll standing
                // (0x424711); one counter at most is set up after the whole action (0x4247e0)
                if (target.Has(249) && action.Physical && (action.Reach == T.SHORT || action.Reach == T.MID) && !unit.Has(307))
                {
                    reprisal[target.Position] = Roll(target.Value(249));
                    reprisalDirty = true;
                }
            }
```

**Audit Notes:** Mod patch `X13` (`0x424768`, 15% vanilla vs 25% Balance) is faithfully parameterized via `Data.ArcaneChance` at `Battle.cs:2581-2583`. Five vanilla condition mismatches remain.

**Discrepancies:**
- **M08.05a (S1)** [`0x4246b0` vs `engine_cs/src/DtEngine/Battle.cs:2897`]: Reprisal 249 requires Front Row (tgtUnit.isFrontRow != 0 at 0x4246b0); Battle.cs:2897 omits target.Front, allowing back-row units and enemies to trigger Reprisal. **Reach:** 1 player passive + 4 enemy passives across 126 vanilla enemies (Avenger / Reprisal). **Fix:** Add target.Front to the Reprisal 249 guard at Battle.cs:2897.
- **M08.05b (S1)** [`0x42467f` vs `engine_cs/src/DtEngine/Battle.cs:2897`]: Reprisal 249 requires this.inCounter == 0 at 0x42467f; Battle.cs:2897 omits !inCounter, allowing counter hits to overwrite reprisal[] flags. **Reach:** 126 vanilla enemies + Reprisal passive bearers during counter exchanges. **Fix:** Add !inCounter to the Reprisal 249 guard at Battle.cs:2897.
- **M08.05c (S1)** [`0x424728` vs `engine_cs/src/DtEngine/Battle.cs:2579`]: Arcane Shield 447 requires this.hitWasPhysical == 0 (non-physical/magical hits ONLY at 0x424728); Battle.cs:2579 omits this check and reflects physical attacks as well. **Reach:** 1 Unique Skill (Arcane Shield 447) in both vanilla and X13-patched modes. **Fix:** Gate Arcane Shield recording at Battle.cs:2579 on action != null && !action.Physical.
- **M08.05d (S1)** [`0x423d50..0x423d9b` vs `engine_cs/src/DtEngine/Battle.cs:2881`]: Dark Aura 262 (0x423d50..0x423d9b) only requires close range and hitLanded (no isPhysical check); Battle.cs:2881 wrongly requires action.Physical, suppressing Dark Aura on short-range spells. **Reach:** 1 player passive + 3 enemy passives across 65 vanilla enemies. **Fix:** Remove action.Physical from the Dark Aura 262 check at Battle.cs:2881.
- **M08.05e (S1)** [`0x4244dc` vs `engine_cs/src/DtEngine/Battle.cs:2891`]: Battle.cs:2871 gates 262/293/249 on dealt != 0 instead of hitLanded, and Slow Target 293 (Battle.cs:2891-2892) directly sets Slow (122) bypassing Earth resistance (AilmentThreshold) and barrier consumption (0x4244dc executes cmd 122 val=1.0f via ExecuteCalc). **Reach:** 10 vanilla enemies with Slow Target 293 + all 0-damage hit interactions for 262/293/249. **Fix:** Gate post-hit passives on hitLanded (not dealt != 0) and route Slow Target 293 Slow (122) through ApplyAilment(target, unit, 122, 1.0, null, SLOW_TARGET_RECOVERY).

### M08.06 _CheckAfterAttackInterrupt 4-Stage Post-Action Chain (250, 249, 447, 260)
**Verdict:** S0

```asm
00424c42  cmp dword ptr [ebp - 0x2c], 1
00424d50  mov dword ptr [ebp - 0x1c], ecx
00424e70  inc ebp
004251f8  fmul dword ptr [ebp - 0x20]
00425381  cmp byte ptr [edx + 0x78], 0
00425821  jmp 0x425472
```

engine_cs/src/DtEngine/Battle.cs:1366
```csharp
            if (arcaneDirty)
            {
                bool fired = false;
                for (int ui = 0; ui < Units.Count; ui++)
                {
                    int stored = arcaneDamage[ui];
                    if (stored <= 0) continue;
                    arcaneDamage[ui] = 0;
                    if (fired) continue;
                    var bearer = Units[ui];
                    if (bearer.Alive && unit.Alive && bearer.HasUnique && bearer.UniqueEffect == 447)
                    {
                        LoseHp(unit, PyMath.Int(stored * bearer.UniqueValue), bearer);
                        fired = true;
                    }
                }
                arcaneDirty = false;
            }
            // Reprisal after the action: the first target, in order, whose record is set and who still bears it and stands (0x424d50 -
            // 0x424de7); one counter for the whole action
            if (reprisalDirty)
            {
                foreach (var target in targets)
                {
                    if (reprisal[target.Position] && target.Has(249) && target.Alive)
                    {
                        Counter(target, unit);
                        break;
                    }
                }
                Array.Clear(reprisal, 0, Units.Count);
                reprisalDirty = false;
            }
```

engine_cs/src/DtEngine/Battle.cs:1416
```csharp
            if (!inCounter && unit.Kind != Kind.Doll && (action.Kind == AKind.Attack || (action.Atk != null && action.Atk.Plain)))
            {
                foreach (var ally in AlliesArray(unit))
                {
                    if (ally != unit && ally.Kind != Kind.Doll && ally.Has(260) && Roll(ally.Value(260)))
                    {
                        Unit first = null;
                        foreach (var t in targets) if (t.Alive) { first = t; break; }
                        if (first == null)
                        {
                            var opp = OpponentsArray(unit);
                            if (opp.Length > 0) first = opp[0];
                        }
                        if (first != null)
                        {
                            Action shot = new Action(ally, AKind.Attack);
                            if (ally.Kind != Kind.Member && ally.Attacks != null && ally.Attacks.Length > 0)
                            {
                                var atk0 = Data.GetAttack(ally.Attacks[0]);
                                if (atk0 != null) shot = new Action(ally, AKind.Enemy, atk0, 1);
                            }
                            Resolve(shot, first, 0);
                        }
                        break;
                    }
                }
            }
```

**Audit Notes:** Binary executes 4 strictly ordered stages: (1) Support Shot `260` -> (2) Deferred Counter `250` (skips 3 & 4) -> (3) Reprisal `249` -> (4) Arcane Shield `447` via Skill `240`. C# inverts stages and omits Stage 2.

**Discrepancies:**
- **M08.06a (S0)** [`0x424c42..0x425381` vs `engine_cs/src/DtEngine/Battle.cs:1366`]: Stage 2 Deferred Counter 250 (which suppresses Stages 3 & 4) is missing, AND Stage 4 Arcane Shield 447 (Battle.cs:1366-1383) executes BEFORE Stage 3 Reprisal 249 (Battle.cs:1386-1398) and Support Shot 260 runs last (Battle.cs:1416-1442). **Reach:** All AoE/multi-target actions involving Mind's Eye 250, Reprisal 249 (126 enemies), Arcane Shield 447, or Support Shot 260. **Fix:** Implement the exact 4-stage post-action order: Support Shot 260 -> Deferred Counter 250 (if fired, skip 249 & 447) -> Reprisal 249 -> Arcane Shield 447.
- **M08.06b (S1)** [`0x4251f8..0x42531b` vs `engine_cs/src/DtEngine/Battle.cs:1378`]: Arcane Shield 447 (0x4251f8..0x42531b) executes Skill 240 (0xf0: effects [(8,0),(1,1),(55,1),(296,500),(70,0)]), which enforces a 500 damage cap (cmd 296), barriers, and Endure 254; Battle.cs:1378 calls raw LoseHp(unit, PyMath.Int(stored * bearer.UniqueValue), bearer), bypassing all three. **Reach:** 1 Unique Skill (Arcane Shield 447) whenever stored * mult > 500 or attacker has barrier/Endure 254. **Fix:** Cap Arcane Shield damage at 500 (Skill 240 cmd 296) and route through barrier/TakeDamage/Endure 254.
- **M08.06c (S1)** [`0x424c42, 0x425821` vs `engine_cs/src/DtEngine/Battle.cs:1424`]: Support Shot 260 (0x424c42..0x425821) requires primaryTarget alive (no fallback to another foe) and executes with inCounter = 1; Battle.cs:1424-1428 falls back to opp[0] on target death and Battle.cs:1437 calls Resolve(shot, first, 0) without setting inCounter = true. **Reach:** 1 player passive + 7 enemy attacks across 9 vanilla enemies with Support Shot 260. **Fix:** Skip Support Shot if the primary target is dead (remove opp[0] fallback) and wrap Resolve(shot, first, 0) in inCounter = true.
- **M08.06d (S2)** [`0x424e70` vs `engine_cs/src/DtEngine/Battle.cs:1369`]: Arcane Shield 447 iterates global Units order (Battle.cs:1369) instead of targetSlots order (0x424e70). **Reach:** Only matters if multiple Arcane Shield bearers are hit by the same AoE in non-Units order. **Fix:** Iterate targets in targetSlots order for Arcane Shield just like Reprisal 249.

### M08.07 Chant/Song/Dance Interruption & Crit Instakill (258)
**Verdict:** S1

```asm
0044cff7  pop ebx
0044d044  pop eax
0044d079  mov ecx, dword ptr [edi + 0x10]
0044d194  addss xmm0, dword ptr [ebp + 0x10]
0044d266  push 0
```

engine_cs/src/DtEngine/Battle.cs:2571
```csharp
            if (target.Alive && amount > 0)
            {
                target.PopStatus(116);
                if (target.Chant != null || Performing(target))
                    Interrupt(target, amount, critical, action == null || !action.Magic);
            }
...
        void Interrupt(Unit target, int amount, bool critical, bool physical)
        {
            // the interruption enchantments of the target: 57, 58, 59 lower the rate, 60 and 61 raise it (P6.10 of the audit)
            double enchant = 0.10 * target.Pieces(57) + 0.06 * target.Pieces(58) + 0.03 * target.Pieces(59) - 0.06 * target.Pieces(60) + 0.20 * target.Pieces(61);
            double chance = F.InterruptionChance(amount, target.MaxHp, target.Value(264), enchant, critical, physical, Options.InterruptProduct ?? Data.InterruptProduct);
            if (Rng.Random() < chance)
            {
```

engine_cs/src/DtEngine/Formulas.cs:286
```csharp
        public static double InterruptionChance(double damage, double maxHp, double modifier, double enchant, bool critical, bool physical,
                                                bool product)
        {
            double rate = 0.0;
            if (physical)
            {
                double divisor = product ? maxHp * INTERRUPT_HP_FACTOR * (1 + modifier) : maxHp * INTERRUPT_HP_FACTOR + (1 + modifier);
                double a = Clamp(damage / divisor, 0.0, INTERRUPT_MAX);
                rate = PyMath.Int(Clamp(a - enchant, 0.0, INTERRUPT_MAX) * 100) / 100.0;
            }
            if (critical) rate = 1 - (1 - rate) * (1 - INTERRUPT_CRITICAL / 100.0);
            return rate;
        }
```

engine_cs/src/DtEngine/Battle.cs:2030
```csharp
            }
            TakeDamage(target, amount, action, critical);
            if (critical && action.Physical && target.Alive && (action.Has(MURDER) || action.Actor.Has(MURDER)))
                ApplyAilment(action.Actor, target, 119, First(action, action.Actor, MURDER), action);
            return amount;
        }
```

**Audit Notes:** Mod patch `X14` (`0x44d044`) is faithfully parameterized via `Data.InterruptProduct` (`Formulas.cs:292`), and enchant `61` sign (`+0.20`) was verified directly against `0x44d194 addss`. Three divergences remain.

**Discrepancies:**
- **M08.07a (S1)** [`0x44cff7` vs `engine_cs/src/DtEngine/Battle.cs:2575`]: Battle.cs:2575 passes physical = (action == null || !action.Magic) into Interrupt(), wrongly applying the physical damage-ratio interrupt roll to non-physical special-damage attacks (0x44cff7 runs only in CalcPhysicalAttack). **Reach:** All non-physical special-damage skills/attacks hitting chanting/singing/dancing targets. **Fix:** Pass action != null && action.Physical (not !action.Magic) to Interrupt() at Battle.cs:2575.
- **M08.07b (S1)** [`0x44d266` vs `engine_cs/src/DtEngine/Battle.cs:2032`]: Crit Instakill 258 (Murder) runs at Battle.cs:2032-2033 AFTER TakeDamage/Endure 254 instead of inside CalcPhysicalAttack (0x44d266) before _AfterHit2, causing Murder to bypass Endure 254. **Reach:** 1 player passive (Murder 258) on critical hits against Endure 254 bearers. **Fix:** Evaluate Crit Instakill 258 inside the physical damage calculation before TakeDamage so Endure 254 can intercept the lethal hit.
- **M08.07c (S2)** [`0x44d044..0x44d1ff` vs `engine_cs/src/DtEngine/Formulas.cs:296`]: Formulas.cs:296 + Battle.cs:2597 merges the binary's two separate integer Rand(100) rolls on critical hits into a single combined float Roll(chance) (mathematically equivalent probability, 1 fewer RNG draw on crits). **Reach:** All critical hits on chanting/performing units (RNG stream alignment only). **Fix:** Roll physical ratio interrupt and critical 15% interrupt as two separate Rng.RandRange(100) checks.

### M08.08 CActionPattern* Factory & Dispatch Table (Skill Trailer[4] & EnemyAttack+0x90)
**Verdict:** S0

```asm
0041e060  push ebp
0041e09a  adc al, 0
0041b530  push ebp
0041b567  push 0xd74c985
```

tools/engine_export.py:43
```python
def skill_json(s):
    return {
        'category': s.category, 'id': s.id, 'name': s.name, 'levels': whole(s.levels, 'levels'), 'target': s.target,
        'attr': s.attr, 'group': s.group, 'weapons': list(s.weapons or []),
        'effects': [[e, k, list(v)] for e, k, v in s.effects],
        'tp': whole_list(s.tp, f'tp of {s.name}'), 'sp': whole_list(s.sp, f'sp of {s.name}'), 'speed': list(s.speed),
        'cast': None if s.cast is None else list(s.cast),
        'accuracy': None if s.accuracy is None else list(s.accuracy),
        'turns': list(s.turns), 'classes': list(s.classes or []), 'range': s.range, 'chant_stat': s.chant_stat,
        'swing': s.swing or 0.0,
    }


def attack_json(a):
    return {
        'id': a.id, 'name': a.name, 'target': a.target, 'attr': a.attr, 'chant_speed': a.chant_speed,
        'accuracy': a.accuracy, 'power': a.power, 'turns': a.turns, 'speed': a.speed,
        'effects': [[e, k, v] for e, k, v in a.effects], 'range': a.range, 'passive': bool(a.passive),
        'chant_stat': a.chant_stat, 'plain': bool(a.plain), 'spell': bool(a.spell), 'technique': bool(a.technique),
    }
```

gamedata/data.py:223
```python
        data.attacks[r['Skill_ID']] = EnemyAttack(
            id=r['Skill_ID'], name=r['Name'], target=r['Target_Code'], attr=r['Attr_Code'],
            chant_speed=r['Chant_Speed'] or 0, accuracy=r['Accuracy'] or 0, power=r['Power'] or 0,
            turns=int(r['Turns'] or 0), speed=r['Speed'] if r['Speed'] else 1.0, effects=effects, range=reach,
            passive='Passive Skill' in str(r['Vanilla_Desc'] or ''),
            chant_stat=_enemy_chant_stat(r['Anim_0x28'] or 0),
            # bit 2 of the word at file 0x28 (+0x40 in memory): a spell, which an anti-magic zone stops (0x41a483)
            plain=bool((r['Anim_0x28'] or 0) & 1), spell=bool((r['Anim_0x28'] or 0) >> 2 & 1),
            # bit 1 of the same word: a technique, which freeze stops (the choice of an AI unit, 0x431344 for spells under
            # silence, 0x4312e4 for techniques under freeze)
            technique=bool((r['Anim_0x28'] or 0) >> 1 & 1))

```

**Audit Notes:** Root architectural gap: the entire `CActionPattern*` subclass system (18 patterns across skills and enemy attacks) is dropped before reaching C#.

**Discrepancies:**
- **M08.08a (S0)** [`0x41e060, 0x41b530` vs `tools/engine_export.py:43`]: pattern (Skill Trailer[4] and EnemyAttack+0x90) is not parsed for EnemyAttack in gamedata/data.py:213-234, is dropped for both Skills and EnemyAttacks in tools/engine_export.py:43-62, and does not exist in Data.cs/Loader.cs/Battle.cs. All 2,616 vanilla skills and enemy attacks collapse into a single Battle.Perform() path. **Reach:** All 241 vanilla skills and 2,375 vanilla enemy attacks (100% of active combat actions). **Fix:** Parse pattern from EnemyAttack Trailer[2] (+0x90) and Skill Trailer[4], export it in engine_export.py, load it in Data.cs/Loader.cs, and dispatch pattern-specific sequencing/flag10/Cover/retarget rules in Battle.cs.

### M08.09 Standard Multi-Hit & AoE Patterns (A..G, T0105, M0124, M0140)
**Verdict:** S0

```asm
0042d1d0  push ebp
00422640  cmp byte ptr [esi + 0x10], al
```

engine_cs/src/DtEngine/Battle.cs:1345
```csharp
            foreach (var target in targets)
            {
                for (int h = 0; h < hits; h++)
                {
                    if (!unit.Alive || (!target.Alive && !action.Has(105))) break;
                    Resolve(action, target, index);
                    index++;
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:1796
```csharp
        {
            int c = action.TargetCode;
            // 0x420b70: Cover (171) only redirects physical actions (effect ID 0), never magic or pure status attacks.
            if (action.Physical && (c == T.SINGLE || c == T.RANDOM))
            {
                redirectScratch.Clear();
                var covers = redirectScratch;
                // only units below 2000 can cover (P5.5 of the audit): never a doll, the summon or a guest
                foreach (var u in TargetableArray(target.Side)) if (u != target && u.St[171] != null && u.Alive) covers.Add(u);
                if (covers.Count > 0)
                {
                    var cover = covers[Rng.ChoiceIndex(covers.Count)];
                    if (covered != null)
```

**Audit Notes:** Because `CActionPattern*` subclasses are unmodeled (`M08.08`), multi-hit dead-target re-selection, `M0124` self-last rotation, and pattern-keyed `_Cover` gating all diverge.

**Discrepancies:**
- **M08.09a (S0)** [`0x41e060, 0x41b530` vs `engine_cs/src/DtEngine/Battle.cs:1349`]: Patterns A/B/C/G re-select a new living target via _SelectTarget when the current target dies mid-multi-hit; Battle.cs:1349 breaks the hit loop (if (!target.Alive) break;) and wastes all remaining hits. **Reach:** 1,325+ vanilla A/B/C/G multi-hit skills and enemy attacks (e.g., Divine Cannon, Mad Zapper, Prism Dawn). **Fix:** On A/B/C/G patterns, when target dies mid-multi-hit, re-select another valid living target via _SelectTarget instead of breaking.
- **M08.09b (S0)** [`0x42d1d0` vs `engine_cs/src/DtEngine/Battle.cs:1799`]: CActionPatternM0124 (case 13, Magic 230 Primevil, 0x42d1d0) rotates self-slot last in target order (unimplemented), and pre-calc _Cover (Battle.cs:1799) dispatches by TargetCode instead of pattern (D/F/G/M0124 skip pre-calc _Cover while E/T0105/M0140 run it). **Reach:** Magic 230 (Primevil) + all AoE/row/random attacks interacting with Cover (171). **Fix:** Rotate self slot to the end for pattern 13 (M0124) and gate Cover(171) by pattern class (A/B/C/E/T0105/M0140) rather than TargetCode alone.

### M08.10 Random Skill Patterns (10/11/12/14/17 & Weighted Draw)
**Verdict:** S1

```asm
0041e342  push 9
0042d370  push ebp
00505b35  call 0x490790
```

engine_cs/src/DtEngine/Battle.cs:3472
```csharp
                bool present = false;
                foreach (var u in Units) if (u.Alive && u.Genjimaru) present = true;
                if (present)
                {
                    RandomResult empty = null;
                    foreach (var r in table.Results) if (r.Effects.Length == 0) { empty = r; break; }
                    skill = empty != null ? Data.ById(empty.Skill) : null;
                    if (skill == null) return null;
                }
            }
            return new Action(action.Actor, AKind.Skill, skill, action.Level);
        }

```

engine_cs/src/DtEngine/Battle.cs:1730
```csharp
        int Weighted(int[] picks, double[] weights)
        {
            var s = new PySum();
            foreach (var w in weights) s.AddFloat(w);
            double roll = Rng.Random() * s.Result;
            for (int i = 0; i < picks.Length && i < weights.Length; i++)
            {
                roll -= weights[i];
                if (roll < 0) return picks[i];
            }
            return picks[picks.Length - 1];
```

tools/random_move_data.py:27
```python
# effect of the skill: (usual table, table with Triple Joker, entries), as pushed at 0x41e342, 0x41e387, 0x41e4ed, 0x41e571
TABLES = {152: (0x64f8c0, 0x64f930, 9),
          153: (0x64fa28, 0x64f9a0, 11),
          154: (0x64fb50, 0x64fab0, 13),
          155: (0x64f458, 0x64f440, 2)}

```

**Audit Notes:** All 4 player random move tables (`152..155`, incl. `0x64fb50` sum=95) are extracted accurately, but `M0129` drops its target and `E2520` is omitted.

**Discrepancies:**
- **M08.10a (S1)** [`0x42d370` vs `engine_cs/src/DtEngine/Battle.cs:3482`]: CActionPatternM0129 (case 14, Magic 234 Heaven or Hell, 0x42d370) preserves the caster's chosen target slots when executing the drawn skill; Battle.cs:3482 constructs new Action(action.Actor, AKind.Skill, skill, action.Level) without copying action.Target, redirecting to a random target. **Reach:** Magic 234 (Heaven or Hell) whenever cast by player. **Fix:** Copy Target = action.Target onto the returned Action in RandomMove() when effect == 155 (Heaven or Hell).
- **M08.10b (S2)** [`0x41b530` vs `tools/random_move_data.py:28`]: EnemyAttack pattern 17 (E2520, table at 0x64f1c0, 13 moves 2701..2713, sum=95) is neither extracted by tools/random_move_data.py:28-31 nor handled in Battle.cs. **Reach:** 0 vanilla EnemyAttackData records carry pattern 17. **Fix:** Add table 0x64f1c0 (13 entries) to tools/random_move_data.py and handle pattern 17 in Battle.cs.
- **M08.10c (S2)** [`0x505b35` vs `engine_cs/src/DtEngine/Battle.cs:1734`]: Battle.cs:1734 draws continuous Rng.Random() * total instead of integer GlobalRng.Rand(total) (0x505b35). **Reach:** All random-move weighted draws (RNG precision/stream divergence). **Fix:** Use integer Rng.RandRange((int)total) for integer weight tables in Weighted().

### M08.11 Special Patterns (E1580 Murder License 319 & U0008 Overstock Clearance 446)
**Verdict:** S1

```asm
0042c180  push ebp
0042fb60  push ebp
00430260  push eax
```

engine_cs/src/DtEngine/Battle.cs:92
```csharp
        const int SAMSARA_STEP = 50;
        const int MURDER = 258, DARK_QUEST = 263, KNOCK_DOWN = 305, PRETEND = 310, MURDER_LICENSE = 319, MURDER_LICENSE_ATTACK = 413, DEMON_WALL = 356, ENEMIES_FLEE = 432, ESCAPE_SELF = 11;
        const int DARK_AURA_TURNS = 4, ECSTASY_TURNS = 3;
        const int SLOW_TARGET_RECOVERY = 5, SLOW_TARGET_TURNS = 5, SUGAR_COMA_RECOVERY = 5, SUGAR_COMA_TURNS = 3;
```

engine_cs/src/DtEngine/Battle.cs:924
```csharp
            if (unit.Alive && unit.Has(MURDER_LICENSE))
            {
                var mlAtk = Data.GetAttack(MURDER_LICENSE_ATTACK);
                var foes = TargetableArray(1 - unit.Side);
                if (mlAtk != null && foes.Length > 0)
                    Perform(new Action(unit, AKind.Enemy, mlAtk, 1) { Target = foes[Rng.ChoiceIndex(foes.Length)] });
            }
            if (!unit.Alive || !unit.HasUnique) return;
            int effect = unit.UniqueEffect;
            double value = unit.UniqueValue;
            if (effect == 446 && unit.Items.Count > 0 && Roll(value) && ChooseMember != null)
            {
                bool hurt = false;
                foreach (var m in AlliesArray(unit)) if (m.Kind == Kind.Member && m.HpRatio < 0.6) { hurt = true; break; }
                var item = Policy.ActItem(this, unit, hurt ? "heal" : "tp", null);
                if (item != null) UseItem(item);
            }
```

**Audit Notes:** Both `E1580` (`319`) and `U0008` (`446`) are replaced in C# by non-binary proxy mechanics (also flagged by reverse sweep as `ENGINE-ONLY-01/02`).

**Discrepancies:**
- **M08.11a (S1)** [`0x42c180` vs `engine_cs/src/DtEngine/Battle.cs:924`]: CActionPatternE1580 (Murder License 319, 0x42c180) directly executes raw cmd 119 (Instakill, val=1.0f) on a random target with no physical attack/hit roll; Battle.cs:93,924-929 instead fires EnemyAttack 413 (Head Shot: Stab physical attack, acc=-0.15, pow=0.35, range=2, eff 119 @ 0.5). **Reach:** 3 vanilla boss/enemies (Carmilla, Koumoku Mary, Aradia). **Fix:** Replace the EnemyAttack 413 proxy with direct ApplyAilment(unit, foe, 119, 1.0, null) on a random living targetable opponent.
- **M08.11b (S1)** [`0x42fb60..0x4302cf` vs `engine_cs/src/DtEngine/Battle.cs:934`]: CActionPatternU0008 (Overstock Clearance 446, 0x42fb60..0x4302cf) casts a FREE weighted random item from [1, 6, 45, 49, 55, 56] (weights [20,20,20,15,15,15], sum=105) with hardcoded target rules and NO inventory consumption; Battle.cs:934-940 requires unit.Items.Count > 0, picks a heal/TP item via Policy.ActItem, and consumes the bag. **Reach:** 1 Unique Skill (Overstock Clearance 446). **Fix:** Implement the hardcoded 6-item free weighted table [1,6,45,49,55,56] with weights [20,20,20,15,15,15] and zero inventory decrement.

### M08.12 Steal & Turn-Into-Snack (59, 60, 62, 84/292)
**Verdict:** S2

```asm
0044fed3  call 0x6a458044
0044ff16  call 0x490790
00481488  test al, 1
0048151f  fmul dword ptr [ecx + 0x458d0073]
```

engine_cs/src/DtEngine/Battle.cs:2754
```csharp
                if ((effect == 60 || effect == 61) && hostile)
                {
                    // gold (60) and items (61) are stolen once each (bytes 0x155, 0x154 of the unit); an item can be stolen only from an
                    // enemy whose flags word has bit 15 (0x4503bf - 0x4503d4)
                    bool item = effect == 61;
                    bool allowed = !item || (target.EnemyId != T.NONE && Data.Enemies.TryGetValue(target.EnemyId, out var er) && ((er.Flags >> 15) & 1) != 0);
                    bool already = item ? target.StolenItem : target.StolenGold;
                    double chance = 0.5 * (unit.Stat(Unit.DEX) + 50) / (target.Stat(Unit.AGI) + 50) * action.Val(effect, 0.0);
                    if (allowed && !already && Rng.RandRange(100) < PyMath.Int(F.Clamp(chance, 0.05, 0.95) * 100))
                    {
                        if (item) target.StolenItem = true; else target.StolenGold = true;
                        Rec?.ItemsUsed.Add(new RecKey(unit, true), 1);
                    }
                    continue;
                }
                if (effect == 84 && hostile)
                {
                    if (target.Snack && target.Hp < PyMath.Int(target.MaxHp * 0.5) && Roll(value))
                    {
                        target.Alive = false;
                        if (Rec != null) Rec.Kills++;
                    }
```

**Audit Notes:** Party gold wallet and post-battle item drops are out of single-battle scope per Roadmap Section 2 (`MODEL-LIMIT`); minor guard/RNG ordering divergences exist in `Battle.cs:2754-2768`.

**Discrepancies:**
- **M08.12a (S2)** [`0x44fed3, 0x44ff16` vs `engine_cs/src/DtEngine/Battle.cs:2762`]: Gold Steal 60 (Battle.cs:2754-2768) omits the enemyParam.gold == 0 guard (0x44fed3), rolls RandRange(100) only after checking allowed && !already (binary 0x44ff16 rolls before), and does not model Enemy Gold Steal 62 (9 enemy attacks; wallet economy out of single-battle scope). **Reach:** Item/Gold Steal skills (59/60) against 0-gold enemies and 9 enemy attacks with cmd 62. **Fix:** Export enemy gold (or gold > 0) for the cmd 60 guard and roll RandRange(100) unconditionally before checking allowed/already if RNG-exact parity is desired.

### M08.13 Turn-Start Auto-Trigger State Machine (TurnPhaseNo 0..24)
**Verdict:** S0

```asm
004365ff  mov eax, dword ptr [esi + 0xb0]
0043660d  mov eax, dword ptr [esi + 4]
00436955  inc eax
004376e3  mov esi, dword ptr [ebp - 0x18]
00437960  push dword ptr [ebp - 0x1c]
0043851e  mov al, byte ptr [ecx + 0x78]
```

engine_cs/src/DtEngine/Battle.cs:838
```csharp
            if (!extraTurn)
            {
                // Esarhaddon (311)
                if (unit.Has(311))
                {
                    int n = PyMath.Int(unit.Value(311));
                    for (int i = 0; i < Math.Min(Math.Max(n, 0), ESARHADDON_ORDER.Length); i++)
                        unit.PopStatus(ESARHADDON_ORDER[i]);
                }
                // Inner State 1: natural recovery of recovering ailments (113..117, 122) before Sleep/Paralysis turn-loss.
                RollAilmentRecovery(unit);
                // Samsara (291)
                if (unit.SamsaraState != 0 && (unit.SamsaraState == 2 || unit.Hp < unit.MaxHp / 2.0))
                {
                    unit.Samsara = new int[8];
                    for (int i = 0; i < 8; i++) unit.Samsara[i] = (Rng.RandRange(2) + 1) * SAMSARA_STEP;
                    unit.SamsaraState = 2;
                }
                // Inner State 2: Third Eye Wide (345) of each opponent — initializes recovery chance at 0% (0x47ee00).
                foreach (var other in OpponentsArray(unit))
                {
                    if (other.HasUnique && other.UniqueEffect == 345 && Roll(other.UniqueValue))
                    {
                        int[] choices = { 113, 115, 116, 114, 117, 118, 74 };
                        int effect = choices[Rng.ChoiceIndex(choices.Length)];
                        // X16 (0x47ee73): vanilla skips buff dispel; Balance NOPs the jump (75% dispel chance).
                        if (effect == 74) { if ((Options.ThirdEyeDispel ?? Data.ThirdEyeDispel) && Roll(0.75)) Dispel(unit); }
                        else ApplyAilment(other, unit, effect, 0.75, null, 0);
                    }
                }
...
                // Inner State 22 (0x43851e): Undaunted (355) runs on a living unit's turn for dead members on the same side.
                Undaunted(unit.Side);
            }
            else if (!CanFight(unit))
            {
                EndOfTurn(unit, false, false);
                return;
            }
            bool acted = false;
            if (softLost == Lost.No && unit.Alive)
            {
                BeforeAction(unit);
                Action action = unit.Alive ? NextAction(unit) : null;
                if (action != null)
                {
                    acted = true;
                    Perform(action);
                }
            }
...
            if (unit.Alive && unit.Has(MURDER_LICENSE))
            {
                var mlAtk = Data.GetAttack(MURDER_LICENSE_ATTACK);
                var foes = TargetableArray(1 - unit.Side);
                if (mlAtk != null && foes.Length > 0)
                    Perform(new Action(unit, AKind.Enemy, mlAtk, 1) { Target = foes[Rng.ChoiceIndex(foes.Length)] });
            }
            if (!unit.Alive || !unit.HasUnique) return;
            int effect = unit.UniqueEffect;
            double value = unit.UniqueValue;
            if (effect == 446 && unit.Items.Count > 0 && Roll(value) && ChooseMember != null)
            {
                bool hurt = false;
                foreach (var m in AlliesArray(unit)) if (m.Kind == Kind.Member && m.HpRatio < 0.6) { hurt = true; break; }
                var item = Policy.ActItem(this, unit, hurt ? "heal" : "tp", null);
                if (item != null) UseItem(item);
            }
            if (effect == 357 && Roll(value))
            {
                foreach (var other in OpponentsArray(unit))
                {
                    other.SetStatus(new Status(41, -0.1, TRANQUIL_TURNS, unit));
                    other.SetStatus(new Status(43, -0.1, TRANQUIL_TURNS, unit));
                }
            }
            if (effect == 350 && Roll(value))
            {
                // one doll of the other side, drawn evenly (0x437787 - 0x437845): never the summon or a guest, never more than one
                var list = new List<Unit>();
                foreach (var u in Units) if (u.Side != unit.Side && u.Alive && u.Kind == Kind.Doll) list.Add(u);
                if (list.Count > 0) RemoveDoll(list[Rng.ChoiceIndex(list.Count)]);
            }
            if (effect == 448 && Roll(value))
            {
                // 0x437960: blocked if the unit already owns ANY active doll (not only a shadow), and subject to MAX_ACTIVE_DOLLS.
                bool any = false;
                foreach (var u in Units) if (u.Alive && u.Kind == Kind.Doll && u.Owner == unit) { any = true; break; }
                if (!any && ActiveDollCount() < MAX_ACTIVE_DOLLS) AddShadow(unit);
            }
        }
```

**Audit Notes:** Mod patch `X16` (`0x47ee73`, Third Eye Wide dispel) is faithfully parameterized via `Data.ThirdEyeDispel` at `Battle.cs:864`. Field passive `306` (Present for Me) is out-of-combat (`MODEL-LIMIT`). Major TurnPhaseNo ordering and extra-turn bugs exist.

**Discrepancies:**
- **M08.13a (S0)** [`0x4365ff, 0x437364..0x437960` vs `engine_cs/src/DtEngine/Battle.cs:909`]: Overstock Clearance 446 (TurnPhaseNo 3), Murder License 319 (12), Tranquil 357 (13), Usurper of Souls 350 (14), and ShadowHeart 448 (15) are all placed in BeforeAction(unit) (Battle.cs:909-963) OUTSIDE if (!extraTurn) and AFTER hard/soft turn loss, Regen, Dances, Poison, and Undaunted. All five fire illegally on extra turns (violating 0x4365ff) and in the wrong turn-start order. **Reach:** 4 Unique Skills (446, 357, 350, 448) + 3 boss enemies (319) on every turn and extra turn. **Fix:** Move 446 into TurnPhaseNo 3 (before Petrify/hard turn-loss) and 319/357/350/448 into TurnPhaseNo 12..15 (after soft turn-loss, before Regen/Dances/Poison/Undaunted), all inside if (!extraTurn).
- **M08.13b (S1)** [`0x436955..0x436a98` vs `engine_cs/src/DtEngine/Battle.cs:859`]: Third Eye Wide 345 (0x436955..0x436a98) breaks after the first opposing bearer procs; Battle.cs:857-867 lacks a break statement. **Reach:** Unique Skill 345 (Third Eye Wide) when multiple opponents hold it. **Fix:** Add break; inside the successful Roll(other.UniqueValue) branch at Battle.cs:866.
- **M08.13c (S1)** [`0x4376e3..0x4378d8` vs `engine_cs/src/DtEngine/Battle.cs:953`]: Usurper of Souls 350 (0x4376e3..0x4378d8) is player-only and destroys only enemy puppets ([etc+0x194] == 3); Battle.cs:953 targets any opposing Kind.Doll including Star Dust Arrows. **Reach:** Unique Skill 350 (Usurper of Souls) against enemies summoning dolls/arrows. **Fix:** Filter Usurper of Souls 350 to unit.Kind == Kind.Member and opposing IsPuppet(u) only.
- **M08.13d (S1)** [`0x43660d..0x43664d` vs `engine_cs/src/DtEngine/Battle.cs:838`]: Battle.cs:838 never skips TurnPhaseNo 0..24 for Kind.Doll, Kind.Summon, or Kind.Npc (0x43660d..0x43664d), causing them to trigger Third Eye Wide 345, Warning Shot/Magnificent Steps, and Undaunted 355. **Reach:** Every Doll, Arrow, Genjimaru, Shadow, Summon, and Guest NPC turn. **Fix:** Skip TurnPhaseNo 0..24 for Kind.Doll and route Kind.Summon/Npc to the dedicated Samba-199-only tick.

### M08.14 Post-Action Triggers (Heretic Samsara 291 & Extra-Turn 288/289/354)
**Verdict:** S1

```asm
00438e50  mov ecx, dword ptr [esi + 0x10]
0047f775  mov dword ptr [esp], 0x3f800000
0043903b  cmp byte ptr [esi + 0x107], 0
00439054  jne 0x439272
00439064  add bh, bh
```

engine_cs/src/DtEngine/Battle.cs:849
```csharp
                // Samsara (291)
                if (unit.SamsaraState != 0 && (unit.SamsaraState == 2 || unit.Hp < unit.MaxHp / 2.0))
                {
                    unit.Samsara = new int[8];
                    for (int i = 0; i < 8; i++) unit.Samsara[i] = (Rng.RandRange(2) + 1) * SAMSARA_STEP;
                    unit.SamsaraState = 2;
                }
```

engine_cs/src/DtEngine/Battle.cs:1106
```csharp
            if (!unit.Alive) return;
            Action last = acted ? lastAction[unit.Position] : null;
            double wait;
            if (unit.Chant != null) wait = Wait(unit, unit.Chant, true);
            else wait = Wait(unit, last);
            unit.NextTime = Time + wait;
            if (unit.Extra > 0 && unit.Chant == null && !Over())
            {
                unit.Extra--;
                unit.NextTime = Time;
                unit.ExtraTurn = true;
            }
            else if (unit.ExtraTurn)
            {
                unit.Extra = 0;
                unit.ExtraTurn = false;
                unit.ExtraUnique = false;
            }
            else if (acted && unit.Chant == null && !Over())
            {
                if (unit.Has(288) && Roll(unit.Value(288))) unit.Extra = 1;
```

**Audit Notes:** Both post-action triggers in Outer State 3 (`0x438e50` Samsara and `0x43903b` extra turn) diverge in timing and guards.

**Discrepancies:**
- **M08.14a (S1)** [`0x438e50, 0x47f775` vs `engine_cs/src/DtEngine/Battle.cs:850`]: Heretic Samsara 291 triggers POST-ACTION (0x438e50, Outer State 3) once cmd291.val >= 1.0f (flagged at 0x47f775); Battle.cs:850-855 instead triggers at TURN-START and checks unit.Hp < unit.MaxHp / 2.0. **Reach:** 3 vanilla boss enemies (Ma, Riko, Demiurge). **Fix:** Move Samsara resistance shuffle to post-action EndOfTurn() triggered by SamsaraState >= 1 (set on crossing the damage threshold), not turn-start.
- **M08.14b (S1)** [`0x43903b..0x439069` vs `engine_cs/src/DtEngine/Battle.cs:1110`]: Extra-turn passives 288 (5 enemies), 289 (1 enemy), and 354 (1 Unique Skill) at 0x43903b..0x439069 require actor == battle.units[0] AND !actor.IsAsleep (vt+0xbc); Battle.cs:1124 omits both guards and Battle.cs:1110 wastes a SPEED_RANDOM RNG draw in Wait() even when granting an extra turn. **Reach:** 5 enemies (288), 1 enemy (289), and 1 Unique Skill (354). **Fix:** Check !unit.HasStatus(116) (Sleep) and evaluate extra-turn eligibility before calling Wait() so no SPEED_RANDOM draw is wasted.

## M09 — Dolls, Summons, Guest NPCs & Enchants (M09.01..M09.15)

### M09.01 Doll & Arrow Spawning, Caster Status Whitelist (0x6cc7b8) & Enemy Doll Table
**Verdict:** S1

```asm
004fd840  push ebp
00484449  mov dword ptr [ebp + 0x3c], edi
004844d6  call 0x4fd840
```

engine_cs/src/DtEngine/Units.cs:903
```csharp
        public static Unit BuildDoll(Unit owner, DollRec doll, int level, GameData data)
        {
            int[] baseStats;
            if (owner.DollBase != null)
            {
                // CGamePlayerStatusETCDoll (0x4f3290 + 0x4f7c00): characterStats (with crown) + copied equipment + class mods + all enchants
                baseStats = (int[])owner.DollBase.Clone();
            }
            else if (owner.Kind == Kind.Member && data != null && owner.ClassId != T.NONE)
            {
                int row = data.GrowthRowOf(owner.ClassId, owner.PreviousClass);
                int[] grown = data.Stats(row, owner.Level);
                baseStats = new int[6];
                Array.Copy(grown, baseStats, 6);
            }
            else
            {
                baseStats = (int[])owner.Base.Clone();
            }
            // 0x4fdfd0: Soul Seal (314) applies only to the 6 puppets (effects 228..233), not Arrow or Genjimaru.
            bool isPuppet = doll.Effect >= 228 && doll.Effect <= 233;
            if (isPuppet && data != null && owner.Has(SOUL_SEAL) && owner.Sealbook != T.NONE && data.Enemies.ContainsKey(owner.Sealbook))
            {
                var sealed_ = data.Enemies[owner.Sealbook];
                for (int s = 0; s < 6; s++) baseStats[s] += PyMath.Int(sealed_.Stats[s] * owner.Value(SOUL_SEAL));
            }
            // All three doll vtables (0x6d4768, 0x6d4dd8, 0x6d434c) map weight slot +0xf4 to 0x4fd630 (fldz; ret => 0.0).
            var unit = new Unit(doll.Name, owner.Side, owner.Level, DOLL_HP, 0, baseStats, null, 0.0, 0.0, T.NONE, Kind.Doll);
            unit.Owner = owner;
            unit.Life = doll.Turns[level - 1];
            unit.Doll = doll;
            unit.DollLevel = level;
            unit.PuppetEffect = doll.Effect;
            unit.AttackRange = doll.Range == "short" ? T.SHORT : doll.Range == "mid" ? T.MID : doll.Range == "long" ? T.LONG : T.SHORT;
            unit.Front = owner.Front;
            return unit;
        }
```

engine_cs/src/DtEngine/Battle.cs:3236
```csharp
        static readonly Dictionary<int, int[]> EnemyDollActions = new Dictionary<int, int[]>
        {
            { 690, new[] { 307 } }, { 691, new[] { 308 } },
            { 693, new[] { 310 } }, { 694, new[] { 311 } },
            { 696, new[] { 313 } }, { 697, new[] { 314 } },
            { 699, new[] { 316 } }, { 700, new[] { 317 } },
            { 702, new[] { 319 } }, { 703, new[] { 320 } },
            { 705, new[] { 322 } }, { 706, new[] { 323 } },
            { 708, new[] { 737 } }, { 709, new[] { 738 } },
            { 711, new[] { 740 } }, { 712, new[] { 741 } },
            { 717, new[] { 1480 } }, { 718, new[] { 1481 } }, { 719, new[] { 1482 } },
            { 721, new[] { 1484 } }, { 722, new[] { 1485 } }, { 723, new[] { 1486 } },
            { 725, new[] { 1488 } }, { 726, new[] { 1489 } }, { 727, new[] { 1490 } },
            { 729, new[] { 1492 } }, { 730, new[] { 1493 } }, { 731, new[] { 1494 } },
            { 733, new[] { 1590, 1594, 1598, 1602, 1606 } },
            { 734, new[] { 1591, 1595, 1599, 1603, 1607 } },
            { 735, new[] { 1592, 1596, 1600, 1604, 1608 } },
            { 1789, new[] { 1801 } }, { 1790, new[] { 1802 } }, { 1791, new[] { 1803 } },
        };
```

tools/doll_data.py:15
```python
and its hidden action (power, ailment chance, heal power, spell power). The value of the doll effect itself
(228 to 233) is not what the action uses.

    python tools/doll_data.py        prints every doll with its action
"""
import os
import sys

import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx')
SHORT, MID, LONG = 'short', 'mid', 'long'
# doll skill id: (doll effect id, category of its actions, action skill ids, range of its physical hits)
# skill ids and effect ids as 0x484150 pairs them (0x484534 - 0x484883); ranges from 0x44bb1c
DOLLS = {95: (228, 'Technique', (101,), SHORT),
         96: (229, 'Technique', (102,), MID),
         97: (230, 'Technique', (104,), None),
```

**Audit Notes:** `Battle.cs:3236-3254` (`EnemyDollActions`) faithfully includes all 34 enemy/NPC doll action mappings. However, caster status whitelist inheritance is missing.

**Discrepancies:**
- **M09.01a (S1)** [`0x4fd840, 0x6cc7b8` vs `engine_cs/src/DtEngine/Units.cs:903`]: The 12-command caster status whitelist at 0x6cc7b8 ([41..46, 48, 189, 193, 194, 256, 286], copied in CGamePlayerStatusETCDoll::ctor 0x4fd840) is NOT copied from owner to newly spawned Dolls or Star Dust Arrows in UnitFactory.BuildDoll (Units.cs:903-939) or MakeDoll/MakeGuestDoll (Battle.cs:3287-3378). Only AddShadow copies statuses. **Reach:** All 6 player puppets, Star Dust Arrow, Genjimaru, and all 34 enemy/NPC doll skills whenever caster has buffs/256/286. **Fix:** Copy any active caster statuses in the 12-command whitelist [41..46, 48, 189, 193, 194, 256, 286] onto the new doll in UnitFactory.BuildDoll().
- **M09.01b (S2)** [`0x484481` vs `tools/doll_data.py:15`]: Player skill 315 (0x13b -> EnemyAttack 341 Bunmawashi) is absent from tools/doll_data.py (0 vanilla records in TechniqueSkillData.pck). **Reach:** 0 vanilla TechniqueSkillData.pck records use skill ID 315. **Fix:** Optionally register skill 315 -> action 341 in tools/doll_data.py for completeness.

### M09.02 Doll Eviction Rules, Global 12-ETC Cap, ATB Gauge & Tiebreak Counter
**Verdict:** S1

```asm
00484491  cmp ecx, 0x31
004844df  mov dword ptr [edi], 0x6d45cc
0043a20d  mov ecx, dword ptr [edi + 0x34]
0043a2a3  push 0x5c
0043a2f1  mov eax, 0x3c2
```

engine_cs/src/DtEngine/Battle.cs:3298
```csharp
            bool arrow = doll.Effect == T.NONE;
            if (arrow)
            {
                var list = new List<Unit>();
                foreach (var u in Units) if (u.Owner == owner && u.Arrow && u.Alive) list.Add(u);
                foreach (var u in list) RemoveDoll(u);
            }
            else
            {
                RemoveSameTypeDolls(owner, doll.Effect);
                int keep = owner.Has(313) ? 2 : 1;
                var own = new List<Unit>();
                foreach (var u in Units) if (IsPuppet(u) && u.Owner == owner) own.Add(u);
                while (own.Count >= keep)
                {
                    RemoveDoll(own[0]);
                    own.RemoveAt(0);
                }
            }
            double n = action.Val(146, 1);
            int count = Math.Max(1, PyMath.Int(n != 0 ? n : 1));
            for (int i = 0; i < count; i++)
            {
                if (ActiveDollCount() >= MAX_ACTIVE_DOLLS) break;
                var unit = UnitFactory.BuildDoll(owner, doll, action.Level, Data);
                unit.Arrow = arrow;
                // 0x4fdfd0: Doll's Life (297) extends only the 6 puppets, not Star Dust Arrow.
                if (!arrow) unit.Life += PyMath.Int(owner.Passive(297, 0.0));
                unit.Position = Units.Count;
                // 0x43a2a3..0x43a2bf: newly summoned dolls start at gauge = RandRange(92) / 100.0 -> NextTime = Time + 1.0 - gauge.
                unit.NextTime = Time + 1.0 - Rng.RandRange(92) / 100.0;
                AddUnit(unit);
            }
```

engine_cs/src/DtEngine/Battle.cs:598
```csharp
            foreach (var u in Units)
            {
                u.TieKey = u.Kind == Kind.Member ? 999 - members++ : u.Kind == Kind.Enemy ? 994 - enemies++
                         : u.Kind == Kind.Summon ? (u.IsGuest ? 929 : 930) : -u.Position;
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member)
```

**Audit Notes:** Global 12-ETC cap (`MAX_ACTIVE_DOLLS = 12`), Double Puppet (`313`) cap 2 vs 1, `Doll's Life` (`297`, puppets only), and initial ATB gauge `RandRange(92) / 100.0` match. Star Dust Arrow eviction diverges.

**Discrepancies:**
- **M09.02a (S1)** [`0x484491..0x4844fa` vs `engine_cs/src/DtEngine/Battle.cs:3299`]: Battle.cs:3299-3304 evicts all of owner's existing Star Dust Arrows whenever Star Dust Arrow is recast; in binary (0x484491..0x4844fa, 0x43c790), Arrows carry no puppet status command and NEVER self-evict, stacking freely up to the global 12-ETC cap. **Reach:** Star Dust Arrow (Technique 49) whenever cast on consecutive turns by an Archer/Sniper. **Fix:** Remove the if (arrow) eviction block at Battle.cs:3299-3304 so Arrows only respect MAX_ACTIVE_DOLLS.
- **M09.02b (S2)** [`0x43a20d..0x43a2f1` vs `engine_cs/src/DtEngine/Battle.cs:601`]: Battle.cs:601 sets doll TieKey = -unit.Position instead of the decrementing etcCounter starting at 962 wrapping 0->962 (0x43a20d..0x43a2f1); identical relative order until >962 spawns in one battle. **Reach:** Battles spawning >962 dolls (effectively unreachable in normal fights). **Fix:** Track a decrementing etcCounter starting at 962 (wrapping to 962 on 0) for doll TieKey.

### M09.03 Doll Stat Snapshot, Enchant Inheritance, TP=9999 & Post-Hit Exclusions
**Verdict:** S0

```asm
004fd867  call 0x4f3290
004fd922  mov dword ptr [ebx + 0x18], 0x270f
004f3290  push ebx
00422f1a  mov eax, dword ptr [eax + 0xfc]
00423006  mov eax, dword ptr [eax + 0xfc]
```

engine_cs/src/DtEngine/Units.cs:903
```csharp
        public static Unit BuildDoll(Unit owner, DollRec doll, int level, GameData data)
        {
            int[] baseStats;
            if (owner.DollBase != null)
            {
                // CGamePlayerStatusETCDoll (0x4f3290 + 0x4f7c00): characterStats (with crown) + copied equipment + class mods + all enchants
                baseStats = (int[])owner.DollBase.Clone();
            }
            else if (owner.Kind == Kind.Member && data != null && owner.ClassId != T.NONE)
            {
                int row = data.GrowthRowOf(owner.ClassId, owner.PreviousClass);
                int[] grown = data.Stats(row, owner.Level);
                baseStats = new int[6];
                Array.Copy(grown, baseStats, 6);
            }
            else
            {
                baseStats = (int[])owner.Base.Clone();
            }
            // 0x4fdfd0: Soul Seal (314) applies only to the 6 puppets (effects 228..233), not Arrow or Genjimaru.
            bool isPuppet = doll.Effect >= 228 && doll.Effect <= 233;
            if (isPuppet && data != null && owner.Has(SOUL_SEAL) && owner.Sealbook != T.NONE && data.Enemies.ContainsKey(owner.Sealbook))
            {
                var sealed_ = data.Enemies[owner.Sealbook];
                for (int s = 0; s < 6; s++) baseStats[s] += PyMath.Int(sealed_.Stats[s] * owner.Value(SOUL_SEAL));
            }
            // All three doll vtables (0x6d4768, 0x6d4dd8, 0x6d434c) map weight slot +0xf4 to 0x4fd630 (fldz; ret => 0.0).
            var unit = new Unit(doll.Name, owner.Side, owner.Level, DOLL_HP, 0, baseStats, null, 0.0, 0.0, T.NONE, Kind.Doll);
            unit.Owner = owner;
            unit.Life = doll.Turns[level - 1];
            unit.Doll = doll;
            unit.DollLevel = level;
            unit.PuppetEffect = doll.Effect;
            unit.AttackRange = doll.Range == "short" ? T.SHORT : doll.Range == "mid" ? T.MID : doll.Range == "long" ? T.LONG : T.SHORT;
            unit.Front = owner.Front;
            return unit;
```

engine_cs/src/DtEngine/Units.cs:636
```csharp
                    // 0x4f6530: Equipment Mastery (243 + 298) scales ATK and RES of every equipped piece except off-hand weapon.
                    stats[Unit.ATK] = stats[Unit.ATK] + PyMath.Int(stats[Unit.ATK] * mastery);
                    stats[Unit.RES] = stats[Unit.RES] + PyMath.Int(stats[Unit.RES] * mastery);
                    for (int s = 0; s < 6; s++) totals[s] += stats[s];
                    // CGamePlayerStatusETCDoll: copies all active pieces without passives (mastery=0, dualWield=0 -> slot 1 weapon skipped).
                    for (int s = 0; s < 6; s++) dollTotals[s] += rawStats[s];
                }
                foreach (int e in piece.Enchants)
                {
                    // 0x4f6334..0x4f638d: off-hand weapon enchantments only register if EnchantData 0x20 bit 7 (0x80) is set.
                    if (isOffhandWeapon && offhandFilter && !data.EnchantOffhand.Contains(e)) continue;
                    enchants.TryGetValue(e, out int c);
                    enchants[e] = c + 1;
                    dollEnchants.TryGetValue(e, out int dc);
                    dollEnchants[e] = dc + 1;
                }
```

**Audit Notes:** HP/TP drain exclusions (`Battle.cs:2706,2716`) and Sugar Coma (`Battle.cs:2871`) match. However, dropping `owner.Enchants` on `BuildDoll` is an architectural S0 bug.

**Discrepancies:**
- **M09.03a (S0)** [`0x4fd867, 0x4f3290` vs `engine_cs/src/DtEngine/Units.cs:930`]: UnitFactory.BuildDoll (Units.cs:903-939) leaves unit.Enchants = NoEnchants instead of copying owner.Enchants (0x4fd867 -> 0x4f3290 copies full enchantList), stripping ALL offensive, crit, speed, slayer, element, and ailment enchants from every player Doll, Star Dust Arrow, and Genjimaru (AddShadow at Battle.cs:980 copies Enchants, BuildDoll does not). **Reach:** Every player Puppet (6), Star Dust Arrow, and Genjimaru in every geared party. **Fix:** In UnitFactory.BuildDoll(), call unit.SetEnchants((int[])owner.Enchants.Clone()) when owner.HasEnchants.
- **M09.03b (S1)** [`0x4fd922, 0x4fd929` vs `engine_cs/src/DtEngine/Units.cs:930`]: Units.cs:930 sets Doll MaxTp = 0, Tp = 0 instead of 9999 (0x4fd922..0x4fd929), and Units.cs:640 excludes offhand weapon stats (256 Lefty Bonus) from DollBase even though 256 is in the 12-cmd whitelist 0x6cc7b8. **Reach:** All player Dolls/Arrows/Genjimaru (especially Dual-Wielding Doll Masters / Snipers). **Fix:** Initialize Doll MaxTp/Tp to 9999 and include offhand stats in DollBase when owner has 256 (Dual Wield).

### M09.04 Doll Turn Execution, TurnPhaseNo Skip, Life Decrement & Shadow Sew Destruction
**Verdict:** S0

```asm
0043660d  mov eax, dword ptr [esi + 4]
0043662c  cmp eax, 0xbb8
004fa4d7  call 0x43d2c0
0043d2c0  push ecx
00438cea  mov ecx, esi
```

engine_cs/src/DtEngine/Battle.cs:838
```csharp
            if (!extraTurn)
            {
                // Esarhaddon (311)
                if (unit.Has(311))
                {
                    int n = PyMath.Int(unit.Value(311));
                    for (int i = 0; i < Math.Min(Math.Max(n, 0), ESARHADDON_ORDER.Length); i++)
                        unit.PopStatus(ESARHADDON_ORDER[i]);
                }
                // Inner State 1: natural recovery of recovering ailments (113..117, 122) before Sleep/Paralysis turn-loss.
                RollAilmentRecovery(unit);
                // Samsara (291)
                if (unit.SamsaraState != 0 && (unit.SamsaraState == 2 || unit.Hp < unit.MaxHp / 2.0))
                {
                    unit.Samsara = new int[8];
                    for (int i = 0; i < 8; i++) unit.Samsara[i] = (Rng.RandRange(2) + 1) * SAMSARA_STEP;
                    unit.SamsaraState = 2;
                }
                // Inner State 2: Third Eye Wide (345) of each opponent — initializes recovery chance at 0% (0x47ee00).
                foreach (var other in OpponentsArray(unit))
                {
                    if (other.HasUnique && other.UniqueEffect == 345 && Roll(other.UniqueValue))
                    {
...
                DecrementTimedStatuses(unit);
                // Inner States 9-11: soft turn loss (Warning Shot 259 -> Empty, Magnificent Steps 283 -> Skip, Mesmerized 203 -> Skip).
                softLost = LostTurnSoft(unit);
                if (softLost != Lost.No) Rec?.TurnsLost.Add(new RecKey(unit), 1);
                // Inner States 16-21: regen, dancer-turn dances (199/200/204/339), and Poison (113).
                if (unit.Alive && softLost != Lost.Skip) TickRegenAndDances(unit);
                if (!unit.Alive) return;
                // Inner State 22 (0x43851e): Undaunted (355) runs on a living unit's turn for dead members on the same side.
                Undaunted(unit.Side);
            }
```

engine_cs/src/DtEngine/Battle.cs:3080
```csharp
                {
                    var u = Units[i];
                    if (u.Owner == unit && u.Kind == Kind.Doll && u.Alive && !u.Arrow && !u.Genjimaru && u.ShadowOf == null) RemoveDoll(u);
                }
            }
        }

        void Delay(Unit target)
        {
            if (!target.Alive) return;
            delayOrderScratch.Clear();
```

engine_cs/src/DtEngine/Battle.cs:3437
```csharp
            else if (members.Count > 0 && action.TargetCode == T.NO_TARGET && action.Has(235))
            {
                // sorted by -(number of ailments), stable
                var ailing = new List<Unit>(members);
                for (int i = 1; i < ailing.Count; i++)
                {
                    var x = ailing[i];
                    int cx = CountAilments(x);
                    int j = i - 1;
                    while (j >= 0 && CountAilments(ailing[j]) < cx) { ailing[j + 1] = ailing[j]; j--; }
                    ailing[j + 1] = x;
                }
                int take = Math.Min(Options.DollCureTargets, ailing.Count);
                if (take < 0) take = Math.Max(0, ailing.Count + Options.DollCureTargets);
                action.FixedTargets = ailing.GetRange(0, take).ToArray();
            }
            return action;
```

**Audit Notes:** Doll turn execution lacks the binary's TurnPhaseNo skip, Shadow Sew fails to destroy non-puppet ETCs, and Perdurabo uses an invented target cap.

**Discrepancies:**
- **M09.04a (S0)** [`0x43660d..0x43662c` vs `engine_cs/src/DtEngine/Battle.cs:838`]: Battle.cs:838-900 executes full TurnPhaseNo 0..24 for Kind.Doll instead of skipping directly to action execution (0x43660d..0x43662c), exposing Dolls to Third Eye Wide 345, Warning Shot/Magnificent Steps, Undaunted 355, DecrementTimedStatuses, and TickRegenAndDances. **Reach:** Every Doll, Arrow, Genjimaru, and ShadowHeart turn in combat. **Fix:** Bypass TurnPhaseNo 0..24 when unit.Kind == Kind.Doll (jump straight to DollAction/Perform + EndOfTurn life decrement).
- **M09.04b (S1)** [`0x4fa4d7, 0x43d2c0` vs `engine_cs/src/DtEngine/Battle.cs:3082`]: Shadow Sew (123) calls EndParts() (Battle.cs:3082), which removes only puppets (!u.Arrow && !u.Genjimaru && u.ShadowOf == null), whereas binary 0x4fa4d7 -> 0x43d2c0 (DestroyAllETCOfOwner) destroys ALL ETC units owned by the victim (Arrows, Genjimaru, and ShadowHearts too). **Reach:** Any unit afflicted by Shadow Sew 123 while owning Arrows, Genjimaru, or ShadowHeart. **Fix:** When Shadow Sew (123) lands, destroy every Kind.Doll with u.Owner == target (including Arrows, Genjimaru, and ShadowHearts).
- **M09.04c (S1)** [`0x438cea` vs `engine_cs/src/DtEngine/Battle.cs:3449`]: DollAction() (Battle.cs:3437-3452) invents an Options.DollCureTargets = 2 cap on Perdurabo's Action (Skill 105, Target=10 NO_TARGET, effect 235), whereas binary cmd 235 cures up to skill-level ailments across the party without a 2-ally target cap. **Reach:** Perdurabo puppet (Technique 99 / Action 105) whenever >=3 party members have ailments. **Fix:** Remove the artificial DollCureTargets = 2 truncation and apply Perdurabo's cmd 235 across all eligible party members per binary Target=10 rules.

### M09.05 Summon & Guest NPC Battle Lifecycle, Slot Priority (930/929) & Untargetability
**Verdict:** S1

```asm
004497ce  mov dword ptr [esi + 4], 0xbb8
00449892  mov dword ptr [esi + 4], 0xbb9
00449182  cmp byte ptr [ebx + 0x33], 0
0044919a  push 0x1f4
0043e72a  mov eax, dword ptr [esi + 4]
00438a9d  call 0x430f00
```

engine_cs/src/DtEngine/Battle.cs:595
```csharp
            int members = 0, enemies = 0;
            bool party297 = false, party295 = false;
            var initParty = new List<Unit>(6);
            foreach (var u in Units)
            {
                u.TieKey = u.Kind == Kind.Member ? 999 - members++ : u.Kind == Kind.Enemy ? 994 - enemies++
                         : u.Kind == Kind.Summon ? (u.IsGuest ? 929 : 930) : -u.Position;
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member)
                {
```

engine_cs/src/DtEngine/Battle.cs:838
```csharp
            if (!extraTurn)
            {
                // Esarhaddon (311)
                if (unit.Has(311))
                {
                    int n = PyMath.Int(unit.Value(311));
                    for (int i = 0; i < Math.Min(Math.Max(n, 0), ESARHADDON_ORDER.Length); i++)
                        unit.PopStatus(ESARHADDON_ORDER[i]);
```

engine_cs/src/DtEngine/Ai.cs:319
```csharp
        static Action AttackAction(Battle battle, Unit unit, int slot, int attackId, bool byId = false)
        {
            if (!byId) attackId = unit.Attacks[Math.Min(slot, unit.Attacks.Length - 1)];
            var attack = battle.Data.GetAttack(attackId);
            if (attack == null) return new Action(unit, AKind.Defend);
            var action = new Action(unit, AKind.Enemy, attack, 1);
            int kind = T.NONE;
```

**Audit Notes:** Initial ATB gauge (`RandRange(500)+1 / 1000.0` vs `flag33`), TieKey (`930`/`929`), untargetability (`TargetableArray`), and party-wipe exclusion (`Over()`) all match.

**Discrepancies:**
- **M09.05a (S1)** [`0x43662d..0x43664d` vs `engine_cs/src/DtEngine/Battle.cs:838`]: Battle.cs:838-900 runs full TurnPhaseNo 0..24 for Kind.Summon and Guest NPCs instead of skipping to the Samba-199-only hook (0x43662d..0x43664d), exposing them to Third Eye Wide 345, Undaunted 355, and normal turn-start ticks. **Reach:** Every Summon (105 forms) and Guest NPC (107 entries) turn in combat. **Fix:** Route Kind.Summon/Npc away from TurnPhaseNo 0..24 to the dedicated Samba-199-only tick.
- **M09.05b (S2)** [`0x438a9d` vs `engine_cs/src/DtEngine/Ai.cs:323`]: Ai.cs:323 returns AKind.Defend if attack lookup fails, whereas binary Outer State 1 (0x438a66..0x438b68) falls back to EnemyAttack ID 0 when AI returns false. **Reach:** Only if a Summon/NPC AI script returns no valid attack (0 vanilla occurrences). **Fix:** Fall back to EnemyAttack ID 0 instead of Defend when AI yields null.

### M09.06 Summon/NPC Stat Scaling, Leader Sealbook Inheritance, Buddy Enchants (295/297) & Samba (199) Tick
**Verdict:** S1

```asm
004ffc90  push ebp
004fec90  sub esp, 0xc
004ff530  mov eax, dword ptr [0x71fc24]
004ff630  push edi
00436322  mov ecx, dword ptr [esi + 4]
```

engine_cs/src/DtEngine/Units.cs:794
```csharp
        public static Unit BuildGuest(GameData data, NpcRec record)
        {
            double weight = data.WeaponRanks.TryGetValue(record.Rank, out var w) ? w : 2.0;
            // a guest ally has no HP and is never a target (0x43e6d0); the figure only keeps the unit standing
            var unit = new Unit(record.Name, Unit.PARTY, record.Level, 9999, 0, record.Stats, null, weight, 0.0, T.NONE, Kind.Summon);
            unit.IsGuest = true;
            unit.Attacks = record.Attacks;
            unit.AttackAttr = FirstAttackAttr(data, record.Attacks);
            unit.Script = record.Script;
            foreach (int id in record.Passives)
                if (data.Attacks.TryGetValue(id, out var extra) && extra.Passive)
                    for (int k = 0; k < extra.EffId.Length; k++) unit.SetPassive(extra.EffId[k], extra.EffValue[k], extra.EffIsInt[k]);
            return unit;
        }
```

engine_cs/src/DtEngine/Units.cs:847
```csharp
        public static Unit BuildSummon(GameData data, SummonForm form, List<Unit> party, int hp, int[] partyEnchants = null)
        {
            data.Enemies.TryGetValue(form.Enemy, out var enemy);
            Dictionary<int, int> partyCounted = null;
            if (partyEnchants != null && partyEnchants.Length > 0)
            {
                partyCounted = new Dictionary<int, int>();
                foreach (int e in partyEnchants)
                {
                    partyCounted.TryGetValue(e, out int c);
                    partyCounted[e] = data.EnchantStacks.Contains(e) ? c + 1 : 1;
                }
            }
            var memberStats = new List<int[]>(party.Count);
...
            double weight = data.WeaponRanks.TryGetValue(form.Rank, out var w) ? w : 2.0;
            var unit = new Unit(form.Name, Unit.PARTY, form.Level, hp, 0, stats, null, weight, 0.0, T.NONE, Kind.Summon);
            unit.Attacks = form.Attacks;
            unit.AttackAttr = FirstAttackAttr(data, form.Attacks);
            unit.Script = form.Script;
            // 0x50030b..0x500497: apply all passive_count (up to 5) passives on SummonData.
            var passives = form.Passives != null && form.Passives.Length > 0
                ? form.Passives
                : (form.Passive != T.NONE ? new[] { form.Passive } : Array.Empty<int>());
            foreach (int pid in passives)
                if (pid != T.NONE && data.Attacks.TryGetValue(pid, out var pa))
                    for (int k = 0; k < pa.EffId.Length; k++) unit.SetPassive(pa.EffId[k], pa.EffValue[k], pa.EffIsInt[k]);
            return unit;
        }
```

engine_cs/src/DtEngine/Battle.cs:1178
```csharp
            for (int i = 0; i < Units.Count; i++)
            {
                var t = Units[i];
                if (!t.Alive || t.StCount == 0) continue;
                var s199 = t.St[199];
                if (s199 != null && (s199.Source == unit || (s199.Source == null && t == unit)))
                {
                    int amount = PyMath.Int(t.MaxHp * s199.Value);
                    if (s199.HasData) amount = Math.Min(amount, PyMath.Int(s199.Data));
                    LoseHp(t, amount, s199.Source);
                }
                if (!t.Alive) continue;
```

**Audit Notes:** Summon party-max scaling (incl. Grand Sealbook temp copies), Guest `295` (+10%) / `297` (+30) buddy enchants, and multi-passive loading match. Guest contract battle-count expiry (`0x446554`) is multi-battle state (`MODEL-LIMIT`). Two active S1 bugs remain.

**Discrepancies:**
- **M09.06a (S1)** [`0x4ff530..0x4ff62e` vs `engine_cs/src/DtEngine/Units.cs:889`]: Party Slot 0 Sealbook enchant inheritance (0x4ff530, vtable+0x178 on BOTH CGamePlayerStatusSummon and CGamePlayerStatusNPC) is completely unimplemented in BuildGuest (Units.cs:794-807) and BuildSummon (Units.cs:847-901) — neither sets unit.Enchants from the leader's equipped Sealbook. **Reach:** All 105 Summon forms and 107 Guest NPCs whenever Party Slot 0 equips any Sealbook. **Fix:** Copy Party Slot 0's Sealbook enchants onto Summon and Guest NPC units via SetEnchants() in BuildSummon() and BuildGuest().
- **M09.06b (S1)** [`0x436322..0x4365fb` vs `engine_cs/src/DtEngine/Battle.cs:1182`]: Samba 199 (Debilitating Salsa, carried by Summons 111/112 & NPC 170) runs inside full TurnPhaseNo/TickRegenAndDances (Battle.cs:896,1182) instead of the dedicated 2-step Samba-only tick (0x436322..0x4365fb), exposing Summons/NPCs to all other turn-start states. **Reach:** Summons 111/112 & Guest NPC 170 (Debilitating Salsa) + all Summons/NPCs taking turns. **Fix:** Run only the Samba 199 tick (and no other TurnPhaseNo states) at turn start for Kind.Summon/Npc.

### M09.07 Enchant Aggregation, Stacking Bit 0, Offhand Bit 7 & Party-Wide Presence (295/297)
**Verdict:** MATCH

```asm
004f7d80  cld
004e4f50  push esi
```

engine_cs/src/DtEngine/Units.cs:641
```csharp
                    for (int s = 0; s < 6; s++) dollTotals[s] += rawStats[s];
                }
                foreach (int e in piece.Enchants)
                {
                    // 0x4f6334..0x4f638d: off-hand weapon enchantments only register if EnchantData 0x20 bit 7 (0x80) is set.
                    if (isOffhandWeapon && offhandFilter && !data.EnchantOffhand.Contains(e)) continue;
                    enchants.TryGetValue(e, out int c);
                    enchants[e] = c + 1;
                    dollEnchants.TryGetValue(e, out int dc);
                    dollEnchants[e] = dc + 1;
                }
...
            var counted = new Dictionary<int, int>();
            foreach (var kv in enchants) counted[kv.Key] = data.EnchantStacks.Contains(kv.Key) ? kv.Value : Math.Min(kv.Value, 1);
            var dollCounted = new Dictionary<int, int>();
            foreach (var kv in dollEnchants) dollCounted[kv.Key] = data.EnchantStacks.Contains(kv.Key) ? kv.Value : Math.Min(kv.Value, 1);
            var bonusTotal = new int[6];
```

engine_cs/src/DtEngine/Battle.cs:602
```csharp
                if (u.Side == Unit.PARTY && u.Kind == Kind.Member)
                {
                    initParty.Add(u);
                    if (u.HasEnchants)
                    {
                        if (u.Pieces(297) != 0) party297 = true;
                        if (u.Pieces(295) != 0) party295 = true;
                    }
                }
            }
```

**Audit Notes:** All 280 enchants' `stacks` (bit 0) and `offhand` (bit 7) match `00_INVENTORY.json` 280/280. `Units.cs:641-695` filters offhand weapons (`u.Slot == 1 && p.Category == 0 && !data.EnchantOffhand.Contains(e)`), deduplicates non-stacking enchants, keeps enemies at `NoEnchants`, and `Battle.cs:605-610` checks `295/297` across all party members regardless of alive state (`0x4e4f50`).

### M09.08 Stat, Accuracy/Evasion, Speed/Chant, Interruption & Element Resistance Enchants
**Verdict:** MATCH

```asm
00449fc7  mulss xmm0, dword ptr [0x6d930c]
0044a1a3  mulss xmm0, dword ptr [0x6d930c]
0044d079  mov ecx, dword ptr [edi + 0x10]
0044d194  addss xmm0, dword ptr [ebp + 0x10]
0044d67b  mulss xmm0, dword ptr [0x6d9408]
0044d742  addss xmm1, dword ptr [ebp + 0x48]
```

engine_cs/src/DtEngine/Units.cs:475
```csharp
            foreach (var kv in enchants)
            {
                int e = kv.Key, n = kv.Value;
                for (int rep = 0; rep < n; rep++)
                {
                    if (F.ENCHANT_SHARE.TryGetValue(e, out var sh))
                    {
                        int source = sh.figure == F.FIG_HP ? baseHp : sh.figure == F.FIG_TP ? baseTp : baseStats[sh.figure];
                        int share = Math.Max(sh.floor, PyMath.Int(source / (double)Math.Abs(sh.divisor)));
                        share = sh.divisor > 0 ? share : -share;
                        if (sh.figure == F.FIG_HP) hp += share;
                        else if (sh.figure == F.FIG_TP) tp += share;
                        else total[sh.figure] += share;
                    }
                    if (F.ENCHANT_ALL_STATS.TryGetValue(e, out int all))
                        for (int s = 0; s < 6; s++) total[s] += all;
                    if (F.ENCHANT_RESIST.TryGetValue(e, out var rs))
                        foreach (var (index, value) in rs) resist[index] += value;
                    if (F.ENCHANT_LINE.TryGetValue(e, out var line) && line.front == front)
                        foreach (var (stat, share) in line.shares)
                            total[stat] += share < 1 ? PyMath.Int(lineSource[stat] * share) : PyMath.Int(lineSource[stat] / share);
                }
            }
            int halfHp = PyMath.Int(baseHp / 2.0), halfTp = PyMath.Int(baseTp / 2.0);
            int cap = F.ENCHANT_RESIST_CAP;
            hpOut = Math.Max(-halfHp, Math.Min(halfHp, hp));
            tpOut = Math.Max(-halfTp, Math.Min(halfTp, tp));
            for (int i = 0; i < 8; i++) resistOut[i] = Math.Max(-cap, Math.Min(cap, resist[i]));
        }
```

engine_cs/src/DtEngine/Battle.cs:564
```csharp
                bonus = unit.StatusValue(214) + unit.Value(265) + unit.Value(281);
                enchant = unit.HasEnchants ? F.SpeedEnchantBonus(unit.Pieces(54), unit.Pieces(55), unit.Pieces(56), 0.20, 0.10, 0.20) : 0.0;
            }
            else
            {
                bonus = SumStatus(unit, SPEED_BUFFS);
                if (unit.Hp <= 0.4 * unit.MaxHp && unit.Has(261)) bonus += unit.Value(261);
                enchant = unit.HasEnchants ? F.SpeedEnchantBonus(unit.Pieces(51), unit.Pieces(52), unit.Pieces(53)) : 0.0;
                if (action != null && (action.Kind == AKind.Skill || action.Kind == AKind.Enemy))
```

engine_cs/src/DtEngine/Battle.cs:2594
```csharp
            // the interruption enchantments of the target: 57, 58, 59 lower the rate, 60 and 61 raise it (P6.10 of the audit)
            double enchant = 0.10 * target.Pieces(57) + 0.06 * target.Pieces(58) + 0.03 * target.Pieces(59) - 0.06 * target.Pieces(60) + 0.20 * target.Pieces(61);
            double chance = F.InterruptionChance(amount, target.MaxHp, target.Value(264), enchant, critical, physical, Options.InterruptProduct ?? Data.InterruptProduct);
            if (Rng.Random() < chance)
```

**Audit Notes:** Verified directly against exe: Speed/Chant `51..56` (`0x449fc7..0x44a1a3`: `0.10/0.05/-0.10` & `0.20/0.10/-0.20`), Magic acc/eva `39..44` (`0x44d67b..0x44d742`: `3.0/1.0`), Interruption `57..61` (`0x44d079..0x44d194`: `+0.10/+0.06/+0.03/-0.06/+0.20`), and Stat/Row/Resist enchants (`Units.cs:475-503`) all match 100%.

### M09.09 Normal-Attack Ailment/Drain Enchants (152..165, 197) & Weapon Element Overrides (78..82)
**Verdict:** S1

```asm
00416209  push 0x4e
0041620d  call dword ptr [eax + 0xf0]
00416215  setne bl
```

engine_cs/src/DtEngine/Action.cs:291
```csharp
        int WeaponAttrWithOverrides()
        {
            // 0x416193..0x416e49: non-players return Actor.AttackAttr directly; players check 325..329 (1 active -> element; >=2 -> weapon physical,
            // NOT falling through to enchants 78..82); if 0 statuses, first active weapon-element enchant in Fire..Lightning order (78..82) wins.
            if (Actor.Kind != DtEngine.Kind.Member) return Actor.AttackAttr;
            if (Actor.StCount > 0)
            {
                int count = 0, element = 0;
                for (int e = 325; e <= 329; e++)
                    if (Actor.St[e] != null) { count++; element = WeaponElement(e); }
                if (count == 1) return element;
                if (count >= 2) return Actor.AttackAttr;
            }
            if (Actor.HasEnchants)
            {
                for (int e = 78; e <= 82; e++)
                    if (Actor.Pieces(e) != 0) return EnchantElement(e);
            }
            return Actor.AttackAttr;
        }
```

engine_cs/src/DtEngine/Formulas.cs:57
```csharp
        public static readonly (int enchant, int effect, double value)[] PLAIN_ATTACK_ENCHANTS =
        {
            (161, 75, 0.5), (162, 75, 0.15), (163, 76, 0.2), (164, 76, 0.05),
            (153, 113, 0.18), (154, 116, 0.15), (155, 117, 0.18), (156, 114, 0.18), (157, 115, 0.15),
            (158, 118, 0.12), (159, 120, 0.1), (165, 122, 0.12), (160, 119, 0.07), (197, 119, 0.75),
        };

```

**Audit Notes:** Normal-attack ailment/drain ordering (`160` before `197`, `161/162`, `163/164`) and Undead drain block (`target.Race == 5` at `Battle.cs:2706,2716`) match. Weapon element overrides (`78..82`) have two S1 divergences.

**Discrepancies:**
- **M09.09a (S1)** [`0x415f50..0x416e49` vs `engine_cs/src/DtEngine/Action.cs:306`]: Action.cs:306-307 returns only the FIRST active weapon-element enchant in 78..82 (Fire..Lightning), whereas binary IsAttributeFire/Water/Wind/Earth/Lightning (0x415f50..0x416e49) tests each enchant independently, allowing multi-element normal attacks to trigger multiple element boosts/resists/nullifiers. **Reach:** 41 vanilla gear/sealbook occurrences of enchants 78..82 whenever a character equips >=2 different element-buff enchants. **Fix:** Represent attack elements as a bitmask/set for normal attacks so multiple active 78..82 enchants all apply independently.
- **M09.09b (S1)** [`0x41620d` vs `engine_cs/src/DtEngine/Action.cs:295`]: Action.cs:295 gates weapon element overrides (325..329 and 78..82) on Actor.Kind == Kind.Member, excluding Dolls even though binary checks CGamePlayerStatusBase (0x41620d) which Dolls inherit. **Reach:** Player Dolls/Arrows whose owner carries weapon-element enchants 78..82 or statuses 325..329. **Fix:** Allow player-owned Kind.Doll units (with inherited enchants) to evaluate weapon-element overrides in WeaponAttrWithOverrides().

### M09.10 Damage Nullification (120..128), Ailment Nullification (129..139), Trap (269) & Dissipation (265)
**Verdict:** MATCH

```asm
00421aee  cmp byte ptr [esi + 0x79], 0
00421b03  push 0x7b
00421b35  mov dword ptr [ebx + 0x1c], 0x7fffffff
00481f2d  push 0x83
00481f4a  push 0x89
0048d1e3  cmp dword ptr [edi + 0x40], 0
```

engine_cs/src/DtEngine/Battle.cs:1825
```csharp
            if (target.HasNullifyEnchant)
            {
                // NULLIFY_ENCHANTS: 120..123 check PhysicalAttr (Slash/Stab/Bash without element overrides); 124..128 check Attr (Fire..Lightning).
                for (int enchant = 120; enchant <= 128; enchant++)
                {
                    if (target.Pieces(enchant) != 0)
                    {
                        bool blowsOnly = enchant <= 123;
                        bool attrMatch = enchant == 123 ? T.Physical(physAttr) : enchant <= 122 ? physAttr == enchant - 119 : attr == enchant - 120;
                        if (attrMatch && (action.Physical || !blowsOnly)) return true;
                    }
                }
            }
```

engine_cs/src/DtEngine/Battle.cs:3029
```csharp
        public static bool Nullified(Unit target, int ailment)
        {
            if (!target.HasEnchants) return false;
            if (target.Pieces(F.ENCHANT_NULLIFY_ALL) != 0) return true;
            if ((uint)ailment < (uint)NullifyEnchantOfAilment.Length)
            {
                int e = NullifyEnchantOfAilment[ailment];
                if (e >= 0 && target.Pieces(e) != 0) return true;
            }
            return false;
        }
```

engine_cs/src/DtEngine/Formulas.cs:122
```csharp
        public static readonly (int enchant, int ailment)[] ENCHANT_NULLIFY_AILMENT =
            { (129, 118), (130, 114), (131, 113), (132, 116), (133, 117), (134, 119), (135, 120), (136, 115), (139, 122) };
        public const int ENCHANT_NULLIFY_ALL = 137;
```

**Audit Notes:** All in-battle damage nullification (`120..123` physical-gated per `0x421aee`, `124..128` elemental) and ailment nullification (`129..137, 139`, incl. Special Petrification `121` -> `135/137` at `Battle.cs:2826`) match 100%. Out-of-battle dungeon gas trap (`138`, `269`, `sourceType == 4`) and map step dissipation (`265`, `battleInfo.battle == null`) are explicitly out-of-scope per Roadmap Section 2 (`MODEL-LIMIT`).

### M09.11 Turn-Start Regen (144..149, 296), Defend Regen (257, 292), Damage-to-TP (72, 73) & Post-Battle (193, 194)
**Verdict:** MATCH

```asm
00437bc4  mov eax, dword ptr [ecx]
004197ab  mov eax, dword ptr [ebx + 8]
0047e687  mov ecx, dword ptr [ebx]
0043d85e  push 0xc1
```

engine_cs/src/DtEngine/Battle.cs:1223
```csharp
        void EnchantRecovery(Unit unit)
        {
            int heal = 0;
            foreach (var (enchant, share, floor) in F.HP_REGEN_ENCHANTS)
            {
                int n = unit.Pieces(enchant);
                if (n == 0) continue;
                float f = (float)n * (float)share;
                heal += Math.Max(floor, (int)((float)unit.MaxHp * f));
            }
            if (unit.Pieces(F.FULL_RECOVERY_ENCHANT) != 0 && Rng.RandRange(100) < F.FULL_RECOVERY_CHANCE) heal += unit.MaxHp;
            if (heal > 0) Restore(unit, heal);
            int tp = 0;
            foreach (var (enchant, amount) in F.TP_REGEN_ENCHANTS) tp += amount * unit.Pieces(enchant);
            if (tp > 0) unit.Tp = Math.Min(unit.MaxTp, unit.Tp + tp);
        }
```

engine_cs/src/DtEngine/Battle.cs:1259
```csharp
                if (unit.Pieces(F.DEFEND_HP_ENCHANT) != 0)
                    Healed(unit, Restore(unit, Math.Max(F.DEFEND_HP_FLOOR, PyMath.Int(F.Single(F.Single(unit.MaxHp) * F.Single(F.DEFEND_HP_SHARE))))));
                if (unit.Pieces(F.DEFEND_TP_ENCHANT) != 0)
                    unit.Tp = Math.Min(unit.MaxTp, Math.Max(0, unit.Tp + Math.Max(F.DEFEND_TP_FLOOR, PyMath.Int(F.Single(F.Single(unit.MaxTp) * F.Single(F.DEFEND_TP_SHARE))))));
                return;
```

engine_cs/src/DtEngine/Battle.cs:2553
```csharp
                int gained = target.Has(257) ? Math.Max(1, PyMath.Int(amount * target.Value(257))) : 0;
                double share = F.TP_CONVERSION_UP * target.Pieces(72);
                int floor = F.TP_CONVERSION_FLOOR;
                if (target.Pieces(73) != 0)
                {
                    share += F.TP_CONVERSION_MINI * target.Pieces(73);
                    floor = F.TP_CONVERSION_FLOOR_73;
                }
                if (share != 0) gained = Math.Max(floor, gained + PyMath.Int(amount * Math.Min(F.TP_CONVERSION_MAX, share)));
                if (gained != 0) target.Tp = Math.Min(target.MaxTp, target.Tp + gained);
```

**Audit Notes:** Turn-start HP/TP regen (`144..149`, `296` 4% full heal), Defend recovery (`257` max(10, 20% HP), `292` max(5, 10% TP)), Damage-to-TP (`72` 5%, `73` 10% + floor 5), and post-battle `193/194` all match the binary formulas.

### M09.12 TP Cost (246..249 + cmd 266), Performance (300..305), Unarmed (263), Class Mod (264) & Unique+1 (293)
**Verdict:** MATCH

```asm
004fd291  push 0xf6
004fd2b3  push 0xf7
004fd2e2  push 0xf8
004fd304  push 0xf9
004fd38f  call 0x61c040
0061c110  cmpnlepd xmm0, xmm1
```

engine_cs/src/DtEngine/Battle.cs:1075
```csharp
        public static int EffectiveTpCost(Unit unit, Skill skill, int level)
        {
            if (skill == null) return 0;
            int cost = skill.Tp[Math.Min(level, skill.Tp.Length) - 1];
            if (cost <= 0) return 0;
            bool technique = skill.IsTechnique;
            if (unit.Pieces(technique ? 246 : 248) != 0) cost = PyMath.Int(cost * 0.8);
            if (unit.Pieces(technique ? 247 : 249) != 0) cost = PyMath.Int(cost * 0.6);
            cost = Math.Max(1, cost);
            if (unit.Has(266)) cost = Math.Max(1, cost - PyMath.Int(Math.Ceiling(cost * unit.Value(266))));
            return cost;
        }
```

engine_cs/src/DtEngine/Battle.cs:2956
```csharp
            int bonusEffect = dance ? 280 : 279, up = dance ? 302 : 300, mini = dance ? 303 : 301;
            double bonus = singer.Value(bonusEffect, 0.0) + Math.Min(0.05, 0.02 * singer.Pieces(up) + 0.01 * singer.Pieces(mini));
            int keep = PerformanceSlots(singer, dance);
```

engine_cs/src/DtEngine/Units.cs:715
```csharp
            if (weapon != null && weapon.Rank != T.NONE && weapon.Rank >= 0)
                rankDelay = data.WeaponRanks[weapon.Rank];
            else if (counted.ContainsKey(263) && data.WeaponRanks.TryGetValue(1, out double rankA))
                rankDelay = rankA;
            else if (data.ClassUnarmedRanks.TryGetValue(classId, out int unarmedRank) && data.WeaponRanks.TryGetValue(unarmedRank, out double classUnarmed))
                rankDelay = classUnarmed;
            else
                rankDelay = UnarmedDelay(data);
```

**Audit Notes:** Verified directly against exe: `0x4fd291..0x4fd326` stacks `246+247` (`*0.8` then `*0.6`) and `248+249` multiplicatively, and `0x61c040` (`0x61c102..0x61c12f`) is `ceil()` (NOT `floor()`), so `Battle.cs:1081-1084` matches 100%! Enchants `300..305`, `263`, `264`, and `293` also match.

### M09.13 Conditional/Species Combat Enchants (262, 267, 268, 271, 272, 219, 220, 280, 298, Slayers/Guards)
**Verdict:** S2

```asm
0044c927  push 0x10b
0044cd5a  push 0x118
0044f009  push 0x118
0044a370  call 0x490790
0043b55a  jne 0x43b548
```

engine_cs/src/DtEngine/Battle.cs:584
```csharp
            double value = F.TurnValue(stat, unit.Weight, unit.Level, f1 * f2, bonus + enchant, unit.St[122] != null,
                                       action != null && action.Kind == AKind.Defend, false, random);
            if (chanting && unit.HasEnchants && unit.Pieces(298) != 0) value = Math.Min(F.VALUE_CAP, value + 0.25);
            return Math.Max(1.0 - F.VALUE_CAP, 1.0 - value);
        }
```

engine_cs/src/DtEngine/Battle.cs:2154
```csharp
            if (unit.Kind == Kind.Member && unit.HasEnchants && unit.Pieces(267) != 0)
                other += 0.10 * Math.Max(0, 5 - initialPartyCount) * unit.Pieces(267);
```

engine_cs/src/DtEngine/Battle.cs:2398
```csharp
            if (wall != null) perHit = Math.Max(0.0, perHit + perHit * wall.Value(DEMON_WALL));
            if (action.Actor.Pieces(F.AILING_ENCHANT) != 0 && HasTrueAilment(target)) perHit += perHit * F.AILING_SHARE;
            if (action.Has(86) && target.Kind == Kind.Member && target.ClassId >= F.MAGIC_USER_LOW && target.ClassId < F.MAGIC_USER_HIGH) perHit += perHit;
```

**Audit Notes:** Verified directly against exe: Enchant `280` (`0x118`, +15% vs ailing) runs in BOTH `CalcPhysicalAttack` (`0x44cd5a`) and `CalcMagicalAttack` (`0x44f009`), matching `Battle.cs:2022,2399`; `267` uses party roster size (`5 - initialPartyCount`); `268`, `271`, `272`, `219`, `220`, slayers, and guards match. Joint-skill enchants `261/290` are out-of-scope (`MODEL-LIMIT`).

**Discrepancies:**
- **M09.13a (S2)** [`0x44a370` vs `engine_cs/src/DtEngine/Battle.cs:586`]: Fast-Chant 298 (Battle.cs:586) faithfully replicates the vanilla Rand(10) < 10 unconditional +0.25 bonus, but omits the 1 GlobalRng.Rand(10) draw at 0x44a370. **Reach:** 1 vanilla gear/sealbook item with enchant 298 (RNG stream parity only; gameplay effect identical). **Fix:** Consume Rng.RandRange(10) < 10 when chanting with enchant 298 if RNG-exact parity is required.
- **M09.13b (S2)** [`0x43b55a` vs `engine_cs/src/DtEngine/Battle.cs:586`]: Escape Probability UP 262 (floor 0.50 at 0x43b55a) is not implemented because battle escape is not modeled in Battle.cs (1 vanilla gear/sealbook occurrence). **Reach:** 1 vanilla gear/sealbook item with enchant 262 (escape command out of sim scope). **Fix:** Implement when/if battle escape is added to Battle.cs.

### M09.14 EXP (270, 275), Drop (276), Pep (195, 200, 201) & Field/Exploration Enchants
**Verdict:** MODEL-LIMIT

```asm
004f69e0  movss xmm1, dword ptr [0x6d950c]
00450734  sub esi, eax
00445a1e  addss xmm1, xmm1
00558517  mov esi, dword ptr [eax + 0x98]
```

engine_cs/src/DtEngine/Units.cs:191
```csharp
        {
            Pep = F.Clamp(Pep, 70.0, 130.0);
            if (!HasEnchants) return;
            if (Pieces(201) != 0) Pep = 70.0;
            if (Pieces(200) != 0 && Pep < 100.0) Pep = 100.0;
            if (Pieces(195) != 0) Pep = 130.0;
        }

```

gamedata/progression.py:14
```python
LEVEL_GAP = ((10, None, 0.85, 0.85), (5, 9, 0.90, 0.90), (0, 4, 1.00, 1.00), (-4, -1, 1.00, 1.15),
             (-9, -5, 1.10, 1.30), (-19, -10, 1.25, 1.50), (None, -20, 1.25, 1.75))
DOUBLE = 2.0                   # 0x4459ed (effect 157) and 0x445a1e (enchantment 275)

...
def battle_exp(member_level, enemies, living, bonus=0.0, doubled=False, double_exp_piece=False, more_from_higher=False,
               gap_table=LEVEL_GAP):
    """EXP one member receives from a battle. enemies: [(level, EXP)] of the enemies defeated.
    living: members alive at the end. bonus: the party-wide fraction the result code is handed."""
    banked = sum(int(exp * level_gap_factor(member_level, level, more_from_higher, gap_table)) for level, exp in enemies)
    gained = banked / float(living)
    gained += gained * bonus
    if doubled:
        gained *= DOUBLE
    if double_exp_piece:
        gained *= DOUBLE
    return gained
```

**Audit Notes:** In-scope Pep clamps (`195/200/201` at `Units.cs:194-196`) and EXP multipliers (`270/275` at `gamedata/progression.py:14-39`, with minor f64 vs f32 truncation tracked in `M11.11`) are implemented. Field/exploration/drop/shop/food enchants (`192, 211..214, 216, 217, 258..260, 266, 269, 276, 291, 294`) are explicitly out-of-scope per Roadmap Section 2.

### M09.15 Master Reference Table of All 280 Enchants (0..305)
**Verdict:** S0

```asm
004fd867  call 0x4f3290
004ff530  mov eax, dword ptr [0x71fc24]
0041620d  call dword ptr [eax + 0xf0]
0044a370  call 0x490790
```

engine_cs/src/DtEngine/Units.cs:930
```csharp
            var unit = new Unit(doll.Name, owner.Side, owner.Level, DOLL_HP, 0, baseStats, null, 0.0, 0.0, T.NONE, Kind.Doll);
            unit.Owner = owner;
            unit.Life = doll.Turns[level - 1];
            unit.Doll = doll;
            unit.DollLevel = level;
            unit.PuppetEffect = doll.Effect;
            unit.AttackRange = doll.Range == "short" ? T.SHORT : doll.Range == "mid" ? T.MID : doll.Range == "long" ? T.LONG : T.SHORT;
            unit.Front = owner.Front;
            return unit;
```

engine_cs/src/DtEngine/Action.cs:304
```csharp
            if (Actor.HasEnchants)
            {
                for (int e = 78; e <= 82; e++)
                    if (Actor.Pieces(e) != 0) return EnchantElement(e);
            }
            return Actor.AttackAttr;
```

**Audit Notes:** Cross-checking all 280 vanilla enchants against the entire simulator pipeline confirms all individual combat formulas (`0..305`) match except the inherited structural/dispatch defects below (all out-of-battle map/drop/joint enchants are Roadmap Section 2 `MODEL-LIMIT`).

**Discrepancies:**
- **M09.15a (S0)** [`0x4fd867` vs `engine_cs/src/DtEngine/Units.cs:930`]: Systemic Doll enchant drop (M09.03a): UnitFactory.BuildDoll (Units.cs:903-939) omits owner.Enchants, silently disabling all 280 enchants on player Dolls, Arrows, and Genjimaru. **Reach:** All 280 enchants on every player Doll/Arrow/Genjimaru. **Fix:** Copy owner.Enchants in UnitFactory.BuildDoll().
- **M09.15b (S1)** [`0x4ff530, 0x41620d` vs `engine_cs/src/DtEngine/Action.cs:306`]: Systemic Companion Sealbook drop (M09.06a): BuildSummon/BuildGuest omit Party Slot 0 Sealbook enchants (0x4ff530), disabling all Sealbook enchants on Summons and Guest NPCs; plus weapon-element 78..82 single-element & Member-only limitation (M09.09a/b). **Reach:** All 105 Summons, 107 Guest NPCs, and 41 vanilla weapon-element enchant occurrences. **Fix:** Propagate Slot 0 Sealbook enchants to Summons/NPCs and support multi-element 78..82 on Members and Dolls.

## M10 — Enemy AI VM, Random Moves, Floors/Maps & Binary Loaders (M10.01..M10.19)

### M10.01 Enemy/Summon/NPC AI Script Container & Bytecode Framing
**Verdict:** MATCH

```asm
00430f00  add ecx, 0x14
00431018  cmp dword ptr [edi], -1
```

tools/enemy_ai.py:42
```python
def _command(b, pos, cid=None):
    top = cid is None
    if top:
        cid = b[pos]
        pos += 1
    if cid == SET:
        return {'cmd': SET, 'set': b[pos], 'weights': list(b[pos + 1:pos + 1 + WEIGHTS])}, pos + 1 + WEIGHTS
    if cid not in ARGUMENTS:
        raise ValueError(f'not an AI command: {cid} at byte {pos - 1}')
    args = []
    for kind in ARGUMENTS[cid]:
        size = 2 if kind == 'w' else 1
        args.append(int.from_bytes(b[pos:pos + size], 'big'))
        pos += size
    out = {'cmd': cid, 'args': args}
    if cid == TARGET:
        return out, pos
    out['result'] = int.from_bytes(b[pos:pos + 2], 'big')
    pos += 2
    if out['result'] & CHAIN:
        out['and'], pos = _command(b, pos, out['result'] & 0x0FFF)
```

**Audit Notes:** `tools/enemy_ai.py`, `enemy_data.py`, `summon_data.py`, `npc_data.py`, and `Loader.cs` faithfully decode the 2-byte big-endian entity ID, set headers (16 weight bytes), and `0xFF`-terminated command lists across all 516 Enemies, 105 Summons, and 107 NPCs.

### M10.02 AI Instruction Format, Action-Word Bitfields & Chaining (0x1000/0x2000/0x4000/0x8000)
**Verdict:** S2

```asm
00432fd0  mov eax, dword ptr [esp + 4]
00433024  and ecx, 0xffff3fff
00433037  and eax, 0xffff3fff
```

engine_cs/src/DtEngine/Ai.cs:138
```csharp
        static Decided FinalResult(Battle battle, Unit unit, Command command, int rolled)
        {
            int result = command.Result;
            while ((result & CHAIN) != 0)
            {
                command = command.And;
                if (!Passes(battle, unit, command, rolled)) return new Decided(0, 0);
                result = command.Result;
            }
            if ((result & TO_SET) != 0) return new Decided(3, result & 0x0FFF);
            // a slot the unit does not have, or an attack id it does not carry, decides nothing (P4.8 of the audit)
            if ((result & SLOT) != 0) return (result & 0x0FFF) < unit.Attacks.Length ? new Decided(1, result & 0x0FFF) : new Decided(0, 0);
            if ((result & ATTACK_ID) != 0) return Array.IndexOf(unit.Attacks, result & 0x0FFF) >= 0 ? new Decided(2, result & 0x0FFF) : new Decided(0, 0);
            return new Decided(0, 0);
        }
```

tools/enemy_ai.py:63
```python
    if top:
        out['once'], out['stop'] = bool(b[pos]), bool(b[pos + 1])
        pos += 2
    return out, pos


def decode(blob):
    """The script of an enemy: {'id', 'opening': commands before the first set, 'sets': {number: {'weights',
    'commands'}}}. The commands after a set belong to it (the parser files them under the set it read last)."""
    b = bytes(blob)
    script = {'id': int.from_bytes(b[:2], 'big'), 'opening': [], 'sets': {}}
    pos, current = 2, None
    while b[pos] != END:
        command, pos = _command(b, pos)
        if command['cmd'] == SET:
            current = script['sets'].setdefault(command['set'], {'weights': command['weights'], 'commands': []})
        elif current is None:
            script['opening'].append(command)
        else:
            current['commands'].append(command)
    if pos != len(b) - 1:
        raise ValueError(f'the script ends at byte {pos} of {len(b)}')
    return script
```

**Audit Notes:** `tools/enemy_ai.py` decodes all opcodes `0..15`, recursive `0x1000` chains, and top-level `once`/`stop` tail bytes faithfully. `Ai.cs` has a narrow bitmask mismatch.

**Discrepancies:**
- **M10.02a (S2)** [`0x433024, 0x433037` vs `engine_cs/src/DtEngine/Ai.cs:149`]: FinalResult() at Ai.cs:149-150 masks SLOT (0x4000) and ATTACK_ID (0x8000) action words with 0x0FFF instead of 0x3FFF (0x433024, 0x433037); SkillOf() at Ai.cs:159,162 uses 0x3FFF correctly. **Reach:** 0 vanilla impact (max vanilla EnemyAttackId is 2693 < 4096); breaks modded IDs >= 4096. **Fix:** Change 0x0FFF to 0x3FFF on Ai.cs:149-150 (matching SkillOf at Ai.cs:159,162).

### M10.03 AI Set Switching, Visited-Set Guard, Weight Roll & Missing-Script Fallback
**Verdict:** S2

```asm
00430f37  je 0x4313ba
00431018  cmp dword ptr [edi], -1
004311c0  mov eax, dword ptr [ebp - 0x1c]
004311d2  mov dword ptr [edi], 0xffffffff
004311dd  cmp dword ptr [esi + 0xfc], -1
```

engine_cs/src/DtEngine/Ai.cs:46
```csharp
        static Action ChooseAttack(Battle battle, Unit unit)
        {
            var attacks = unit.Attacks;
            var script = unit.Script;
            if (script == null) return AttackAction(battle, unit, RollUniform(battle, attacks), T.NONE);
            unit.AiSet = 0;
            Decided decided = Run(battle, unit, script.Opening, -1);
            // a set switch marks the set left as done; a switch to a set already done this choice, or to no set, ends the choice
            // (0x4311c8, 0x431054, 0x43105c): no limit on the number of switches
...
                var entry = script.Get(unit.AiSet) ?? (first ? script.Get(script.MinSet()) : null);
                first = false;
                if (entry == null)
                {
                    decided = new Decided(1, RollUniform(battle, attacks));
                    break;
                }
                int slot = RollWeights(battle, entry.Weights, attacks.Length);
                var found = Run(battle, unit, entry.Commands, slot);
                decided = !found.None ? found : new Decided(1, slot);
            }
            if (decided.None || decided.Kind == 3) decided = new Decided(1, 0);
...
        static int RollWeights(Battle battle, int[] weights, int count)
        {
            long total = 0;
            int usableCount = 0, last = 0;
            for (int slot = 0; slot < weights.Length; slot++)
                if (weights[slot] != 0 && slot < count) { total += weights[slot]; usableCount++; last = slot; }
            if (usableCount == 0) return 0;
            int roll = battle.Rng.RandRange((int)total);
            for (int slot = 0; slot < weights.Length; slot++)
            {
                if (weights[slot] != 0 && slot < count)
                {
                    roll -= weights[slot];
                    if (roll < 0) return slot;
                }
            }
            return last;
        }
```

**Audit Notes:** Verified directly at `0x4311c0..0x4311dd` that when `activeSetId != curSetId`, binary resets `selectedAttackId = -1` and loops to the new set, matching `Ai.cs:135`. Fallback/weight details have narrow S2 mismatches.

**Discrepancies:**
- **M10.03a (S2)** [`0x430f37, 0x431018` vs `engine_cs/src/DtEngine/Ai.cs:50`]: When script == null or initial AiSet is absent, Ai.cs:50,70-75 falls back to MinSet() / RollUniform(battle, attacks), whereas binary (0x430f37 -> 0x4313ba, 0x431018) falls back to slot 0 (_SelectNormalAttack). **Reach:** 0 vanilla enemies lack scripts; Summons/NPCs without scripts default to RollUniform vs slot 0. **Fix:** Fall back to slot 0 (AttackAction(battle, unit, 0, T.NONE)) when script or set is missing.
- **M10.03b (S2)** [`0x431018` vs `engine_cs/src/DtEngine/Ai.cs:93`]: RollWeights() (Ai.cs:88-105) filters slot < attacks.Length when summing weights, whereas binary sums all 16 weight slots 0..15 unconditionally. **Reach:** Only affects scripts with non-zero weight on an out-of-range slot index. **Fix:** Sum all 16 weight entries and fall back to slot 0 if rolled slot >= attacks.Length.

### M10.04 AI Condition Opcodes (0..15) & Stop Flag Semantics
**Verdict:** S0

```asm
004325cf  cmp dword ptr [edi + 0x10], 0
00431aa0  push ebp
0043232e  cmp byte ptr [ebx + 0x1c], 0
00438cbd  inc dword ptr [esi + 0xb8]
```

engine_cs/src/DtEngine/Ai.cs:130
```csharp
                if (result.None) continue;
                if (once) unit.OnceDone.Add(key);
                if (result.Kind == 3 && !command.Stop) { pending = result; continue; }
                return result;
            }
```

engine_cs/src/DtEngine/Ai.cs:166
```csharp
        static bool Passes(Battle battle, Unit unit, Command command, int rolled)
        {
            int cid = command.Cmd;
            var args = command.Args;
            if (cid == 2) return unit.TurnsTaken <= args[0];
            if (cid == 3 || cid == 10 || cid == 12 || cid == 13 || cid == 14)
            {
                int value = SourceValue(battle, unit, args[0]);
                int n = args[1];
                switch (cid)
                {
                    case 3: return value <= n;
                    case 10: return value > n;
                    case 12: return value >= n;
                    case 13: return value < n;
                    default: return value == n;
                }
            }
            if (cid == 4 || cid == 11) return SourceValue(battle, unit, args[0]) > 0;
            if (cid == 5)
...
            if (cid == 9)
            {
                foreach (var u in battle.AlliesArray(unit, false)) if (!u.Alive && u.Kind != Kind.Doll) return true;
                return false;
            }
            return false;
        }
```

**Audit Notes:** Verified directly against exe `0x4325cf cmp [edi+0x10], 0; setne bl` that `stop != 0` stops rule evaluation and `stop == 0` continues (`Ai.cs:132` MATCHES exe!). However, `-1` sentinel handling and opcode `2` turn counting are severe bugs.

**Discrepancies:**
- **M10.04a (S0)** [`0x431aa0, 0x432690` vs `engine_cs/src/DtEngine/Ai.cs:171`]: Passes() for comparison opcodes 3, 4, 10, 11, 12, 13, 14 (Ai.cs:171-184) NEVER checks v != -1 because SourceValue() returns 0 (for false boolean sources 5..11) or 100 (for empty HP/TP sources 1..4) instead of -1, and returns counts 0..N instead of 1/-1 for sources 5..11. Thus opcode 3 (<= N) on source 5..11 when NO unit qualifies evaluates 0 <= N -> TRUE instead of FALSE! **Reach:** All 516 Enemies, 105 Summons, and 107 NPCs executing AI comparison opcodes 3/10/12/13/14 on sources 1..11. **Fix:** Return -1 from SourceValue() when empty/false and 1 when true for sources 5..11, and return false in Passes() whenever value == -1.
- **M10.04b (S1)** [`0x438cbd` vs `engine_cs/src/DtEngine/Ai.cs:170`]: Opcode 2 (Turn count <= N, Ai.cs:170) tests unit.TurnsTaken, which increments at TURN START (Battle.cs:832) including lost turns (Sleep/Paralysis/Petrify) and chant-start turns; binary battleUnit[+0xb8] increments at Outer State 3 (0x438cbd) AFTER completing an action. **Reach:** 124 vanilla Enemy AI scripts + 6 NPC AI scripts using opcode 2. **Fix:** Increment AI action/turn counter in Outer State 3 post-action (excluding hard-lost turns) rather than at turn start.
- **M10.04c (S2)** [`0x43232e` vs `engine_cs/src/DtEngine/Ai.cs:230`]: Opcode 9 (Dead ally, Ai.cs:230-234) runs for Enemies too, whereas binary 0x43232e forces false for Enemies (task.isPlayerSide == 0). **Reach:** 0 vanilla Enemy scripts use opcode 9 (2 NPC scripts use it). **Fix:** Gate cid == 9 on unit.Side == Unit.PARTY.
- **M10.04d (S2)** [`0x431aa0` vs `engine_cs/src/DtEngine/Ai.cs:235`]: Opcode 15 (Summon/NPC per-skill use limit) is completely unimplemented in Ai.cs:235 (always returns false) and useLimit is unread by summon_data.py/npc_data.py. **Reach:** 0 vanilla AI scripts use opcode 15. **Fix:** Extract useLimit in summon_data.py/npc_data.py and implement cid == 15 in Ai.cs.

### M10.05 AI Condition Sources (0..11) & CalcUnitPercent Rounding
**Verdict:** S1

```asm
00430700  mov ecx, dword ptr [esp + 8]
00430706  je 0x430753
0043074b  call 0x61e650
00432690  push ebp
```

engine_cs/src/DtEngine/Ai.cs:238
```csharp
        static int SourceValue(Battle battle, Unit unit, int source)
        {
            // allies are the candidates of the unit's side (0x43e6d0): units below 2000, never a doll, the summon or a guest
            var allies = battle.TargetableArray(unit.Side);
            var foes = battle.TargetableArray(1 - unit.Side);
            switch (source)
            {
                case 0: return PyMath.Int(unit.HpRatio * 100);
                case 1: { int m = 100; bool any = false; foreach (var u in allies) { int v = PyMath.Int(u.HpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : 100; }
                case 2: { int m = 100; bool any = false; foreach (var u in foes) { int v = PyMath.Int(u.HpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : 100; }
                case 3: { int m = 100; bool any = false; foreach (var u in allies) { int v = PyMath.Int(u.TpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : 100; }
                case 4: { int m = 100; bool any = false; foreach (var u in foes) { int v = PyMath.Int(u.TpRatio * 100); if (!any || v < m) { m = v; any = true; } } return any ? m : 100; }
                case 5: { int n = 0; foreach (var u in allies) if (HasAilmentOrDebuff(u)) n++; return n; }
                case 6: { int n = 0; foreach (var u in foes) if (HasAilmentOrDebuff(u)) n++; return n; }
                case 7: { int n = 0; foreach (var u in foes) if (u.Chant != null) n++; return n; }
                case 8: { int n = 0; foreach (var u in foes) if (!u.Front) n++; return n; }
                case 9: { int n = 0; foreach (var u in foes) if (u.Front) n++; return n; }
                case 10: { int n = 0; foreach (var u in foes) if (HasBuff(u)) n++; return n; }
                case 11: { int n = 0; foreach (var u in allies) if (HasDebuff(u)) n++; return n; }
                default: return 0;
            }
        }
```

engine_cs/src/DtEngine/Units.cs:428
```csharp
        public double HpRatio { get { int m = MaxHp; return m != 0 ? (double)Hp / m : 0.0; } }
        public double TpRatio => MaxTp != 0 ? (double)Tp / MaxTp : 1.0;
```

**Audit Notes:** Disassembled `0x430700..0x430760` (`CalcUnitPercent`) directly: confirmed `round_f32_to_i32` (`0x61e650` at `0x43074b`) and `Max==0 -> 100` (`0x430706`).

**Discrepancies:**
- **M10.05a (S1)** [`0x43074b` vs `engine_cs/src/DtEngine/Ai.cs:245`]: SourceValue() sources 0..4 (Ai.cs:245-249) truncate HP/TP percent with PyMath.Int instead of round_f32_to_i32 (0x61e650 at 0x43074b), causing systematic 1% threshold drift on AI HP/TP checks. **Reach:** 117+23 Enemy, 10+2 Summon, and 20+8 NPC AI source usages (180+ vanilla checks). **Fix:** Replace PyMath.Int(... * 100) with PyMath.Round(... * 100) in SourceValue() cases 0..4.
- **M10.05b (S1)** [`0x432690` vs `engine_cs/src/DtEngine/Ai.cs:250`]: SourceValue() returns 100 (when empty) for sources 1..4 and counts 0..N for sources 5..11 (Ai.cs:246-256), whereas binary 0x432690 returns -1 (empty/false) and 1 (true) for boolean presence sources 5..11. **Reach:** All vanilla AI scripts using sources 5..11 with comparison opcodes. **Fix:** Return -1 when empty/false and 1 when any matching unit exists for sources 5..11.
- **M10.05c (S2)** [`0x430706` vs `engine_cs/src/DtEngine/Units.cs:428`]: Unit.HpRatio returns 0 when MaxHp == 0 (Units.cs:428), whereas binary CalcUnitPercent (0x430706) returns 100. **Reach:** Only units with MaxHp == 0 (never occurs on normal combat units). **Fix:** Return 100 in CalcUnitPercent helper when Max == 0.

### M10.06 AI Target Selection Modes (0..15) & Eager vs Lazy Opcode-1 Evaluation
**Verdict:** S1

```asm
00433350  push ebp
004338ec  mov eax, dword ptr [eax + 0xc8]
00433c90  mov ecx, dword ptr [0x7389d4]
00433d5a  jne 0x433c90
0043453a  mov eax, dword ptr [eax + 0x7c]
```

engine_cs/src/DtEngine/Ai.cs:325
```csharp
            int kind = T.NONE;
            if (unit.AiTargets != null)
                foreach (var (word, k) in unit.AiTargets)
                    if (SkillOf(unit, word) == attackId) kind = k;
            if (kind != T.NONE) action.Target = PickByKind(battle, unit, kind, attack);
            return action;
...
            switch (kind)
            {
                case 0: Lowest(allies, false, found); break;
                case 1: Lowest(foes, false, found); break;
                case 2: Lowest(allies, true, found); break;
                case 3: Lowest(foes, true, found); break;
                case 4: MostAilments(allies, found); break;
                case 5: MostAilments(foes, found, skipPetrified: true); break;
                case 9: PickCurePriority(allies, found); break;
                case 13: foreach (var u in allies) if (HasAilmentOrDebuff(u)) found.Add(u); break;
                case 14: foreach (var u in foes) if (HasAilmentOrDebuff(u)) found.Add(u); break;
                case 6: foreach (var u in foes) if (u.Chant != null) found.Add(u); break;
                case 7: foreach (var u in foes) if (!u.Front) found.Add(u); break;
                case 8:
                    foreach (var u in allies)
                    {
                        bool shares = false;
                        for (int i = 0; i < attack.EffId.Length; i++) if (u.St[attack.EffId[i]] != null) shares = true;
                        if (!shares) found.Add(u);
                    }
                    break;
                case 10: foreach (var u in foes) if (u.Front) found.Add(u); break;
...
        static void Lowest(Unit[] list, bool tp, List<Unit> found)
        {
            // 0x43083e: compares truncated integer percents (0..100).
            int best = int.MaxValue;
            foreach (var u in list) { int v = PyMath.Int((tp ? u.TpRatio : u.HpRatio) * 100); if (v < best) best = v; }
            foreach (var u in list) if (PyMath.Int((tp ? u.TpRatio : u.HpRatio) * 100) == best) found.Add(u);
        }
```

**Audit Notes:** Disassembled `0x43387d..0x433930` (Target 5), `0x433be0..0x433d60` (Target 8), and `0x4344fc..0x4345a0` (Targets 13/14) directly against `Ai.cs:341-380`.

**Discrepancies:**
- **M10.06a (S1)** [`0x43074b` vs `engine_cs/src/DtEngine/Ai.cs:378`]: Lowest() for Target Modes 0..3 (Ai.cs:378-379) truncates HP/TP percent with PyMath.Int instead of round_f32_to_i32 (0x61e650). **Reach:** 66 vanilla AI target-override rules using Target Modes 0..3. **Fix:** Use PyMath.Round instead of PyMath.Int in Lowest() at Ai.cs:378-379.
- **M10.06b (S1)** [`0x4338ec` vs `engine_cs/src/DtEngine/Ai.cs:348`]: Target Mode 5 (opponent with most ailments+debuffs, Ai.cs:348) passes skipPetrified: true, whereas binary 0x4338ec keeps petrified units (same filter as Target Mode 4). **Reach:** All vanilla AI scripts using Target Mode 5 when a player is petrified. **Fix:** Remove skipPetrified: true from case 5 at Ai.cs:348.
- **M10.06c (S1)** [`0x43453a` vs `engine_cs/src/DtEngine/Ai.cs:350`]: Target Modes 13 & 14 (Ai.cs:350-351) check HasAilmentOrDebuff(u), whereas binary 0x43453a calls vt+0x7c (HasTrueAilment ONLY, excluding stat debuffs). **Reach:** All vanilla AI scripts using Target Modes 13 or 14 (e.g., healers/ailment-punishers). **Fix:** Replace HasAilmentOrDebuff(u) with Battle.HasTrueAilment(u) in cases 13 and 14 at Ai.cs:350-351.
- **M10.06d (S1)** [`0x433c90..0x433d5a` vs `engine_cs/src/DtEngine/Ai.cs:354`]: Target Mode 8 (ally without skill's turn-status effects, Ai.cs:354-361) requires ally to lack ALL of attack.EffId, whereas binary 0x433c90..0x433d5a counts only (flags & 4) CCommandTurnBase commands and selects allies with activeMatchingCount < totalTurnCmds (missing ANY turn-status, ignoring non-turn commands). **Reach:** All vanilla AI buff/support scripts using Target Mode 8 on multi-effect skills. **Fix:** Filter attack effects to turn-status commands (flags & 4) and include allies missing at least one of them.
- **M10.06e (S2)** [`0x433350` vs `engine_cs/src/DtEngine/Ai.cs:329`]: Ai.cs:326-329 evaluates Target Override (opcode 1) lazily only for the chosen attack, whereas binary 0x433350 runs SelectTargetMode eagerly during _Check (consuming 1 RNG draw per opcode-1 rule encountered). **Reach:** RNG stream alignment on AI scripts containing multiple opcode-1 rules. **Fix:** Evaluate PickByKind() eagerly when executing opcode 1 in Run() if RNG-exact parity is needed.

### M10.07 Enemy-Only Freeze/Silence/Shadow Sew Override & Breath (3) Bypass
**Verdict:** S1

```asm
00431206  cmp dword ptr [esi + 0x18], 0
00431257  cmp dword ptr [ebx + eax + 0x64], 3
0043125c  je 0x431289
```

engine_cs/src/DtEngine/Ai.cs:35
```csharp
            // 0x431257..0x4313b5: Shadow Sew (123) replaces any attack with plain attack; Breath (effect ID 3) bypasses
            // Silence (117, spells) and Freeze (114, techniques).
            if (chosen.Atk != null)
            {
                bool blocked = unit.St[123] != null
                    || (!IsBreath(chosen.Atk) && ((unit.St[117] != null && chosen.Atk.Spell) || (unit.St[114] != null && chosen.Atk.Technique)));
                if (blocked) return AttackAction(battle, unit, 0, T.NONE);
            }
            return chosen;
```

**Audit Notes:** Breath (`effect 3`) bypass of Freeze (`114`) and Silence (`117`) matches `0x431257`. However, the Enemy-only guard (`task.asEnemy != NULL` at `0x431206`) is missing.

**Discrepancies:**
- **M10.07a (S1)** [`0x431206` vs `engine_cs/src/DtEngine/Ai.cs:37`]: Ai.cs:37-42 applies the Freeze/Silence/Shadow Sew -> slot-0 override to ALL AI units (Enemies, Summons, AND Guest NPCs), whereas binary 0x431206 checks task.asEnemy != NULL and skips this entire block for Summons and Guest NPCs. **Reach:** All 105 Summons and 107 Guest NPCs if ever bearing 114/117/123. **Fix:** Guard Ai.cs:37-42 with if (unit.Kind == Kind.Enemy && chosen.Atk != null).

### M10.08 Static Random Move Tables (0x64f8c0, 0x64fa28, 0x64fb50, 0x64f458, 0x64f1c0)
**Verdict:** S2

```asm
0041e342  push 9
0041e387  push 0xb
0041e4ed  push 0xd
0041e571  push 2
```

tools/random_move_data.py:27
```python
# effect of the skill: (usual table, table with Triple Joker, entries), as pushed at 0x41e342, 0x41e387, 0x41e4ed, 0x41e571
TABLES = {152: (0x64f8c0, 0x64f930, 9),
          153: (0x64fa28, 0x64f9a0, 11),
          154: (0x64fb50, 0x64fab0, 13),
          155: (0x64f458, 0x64f440, 2)}

```

**Audit Notes:** All 4 player random move tables (including `0x64fb50` sum=95 handled via normalized `weight / total`) are read directly from the exact exe addresses.

**Discrepancies:**
- **M10.08a (S2)** [`0x41b530` vs `tools/random_move_data.py:28`]: tools/random_move_data.py:28-31 omits the 5th static random move table at 0x64f1c0 (CActionPatternE2520, EnemyAttack pattern 17, 13 entries 2701..2713, sum=95). **Reach:** 0 vanilla EnemyAttackData records carry pattern 17. **Fix:** Add 0x64f1c0 (13 entries) to tools/random_move_data.py.

### M10.09 FloorParameter Loader (Normal, Fixed & Boss Groups, Zone Factors)
**Verdict:** S1

```asm
004d3180  push 0x459
0044fbb0  push ebp
```

tools/floor_data.py:52
```python
_F = __import__('game_profile').layout('FloorParameter')          # data_tables/record_layouts.json
ZONE_COUNT, ZONE_POINTER, ZONE_SIZE = _F['zone_count'], _F['zone_pointer'], _F['zone_size']
COUNT, FORMATIONS, RECORD = _F['count'], _F['formations'], _F['record']
FIXED_COUNT, FIXED_POINTER = _F['fixed_count'], _F['fixed_pointer']
ENEMY_SLOTS = _F['enemy_slots']
ZONE_FACTORS, FACTOR_NAMES = _F['zone_factors'], ('up_a', 'up_b', 'down_a', 'down_b', 'element')
ENCOUNTER = _F['encounter']               # the chance of a random battle per step, then the five special chances
EQUIPMENT_COUNT, EQUIPMENT_POINTER = _F['equipment_count'], _F['equipment_pointer']
EQUIPMENT_RECORD, DROP_KINDS = _F['equipment_record'], _F['drop_kinds']
...
def read_formation(blob, base):
    number = struct.unpack_from('<i', blob, base)[0]
    ids = struct.unpack_from(f'<{ENEMY_SLOTS}i', blob, base + 0x04)
    front = blob[base + 0x34:base + 0x34 + ENEMY_SLOTS]
    return {'number': number, 'chance': struct.unpack_from('<i', blob, base + 0x40)[0],
            'enemies': [(enemy, bool(front[slot])) for slot, enemy in enumerate(ids) if enemy != -1],
            # the slot of each enemy: the program numbers it 1000 + slot in front, 1024 + slot behind (0x439e0e)
            'slots': [slot for slot, enemy in enumerate(ids) if enemy != -1]}


def read_fixed(blob):
    """Fixed battles of a floor, in the shape of formations."""
    blob = bytes(blob)
    start = struct.unpack_from('<Q', blob, FIXED_POINTER)[0]
    return [read_formation(blob, start + RECORD * k) for k in range(struct.unpack_from('<i', blob, FIXED_COUNT)[0])]

...
def read_zones(blob):
    """[(formations, {factor name: value}, {'encounter': percent per step, 'special': five percents})] for every zone."""
    blob = bytes(blob)
    zones = []
    first = struct.unpack_from('<Q', blob, ZONE_POINTER)[0]
    for zone in range(struct.unpack_from('<i', blob, ZONE_COUNT)[0]):
        block = first + ZONE_SIZE * zone
        count = struct.unpack_from('<i', blob, block + COUNT)[0]
        start = struct.unpack_from('<Q', blob, block + FORMATIONS)[0]
        found = [read_formation(blob, start + RECORD * k) for k in range(count)]
        factors = dict(zip(FACTOR_NAMES, struct.unpack_from('<5f', blob, block + ZONE_FACTORS)))
        chances = struct.unpack_from('<6i', blob, block + ENCOUNTER)
        zones.append((found, factors, {'encounter': chances[0], 'special': list(chances[1:]),
                                       'equipment': read_equipment(blob, block)}))
    return zones
```

**Audit Notes:** `normalGroups` (`+0x5c/+0x60`), `fixedGroups` (`+0x28/+0x30`, 196 records), and `zone_factors` (`+0xb8..+0xc8`) match. `bossGroups` (`+0x38/+0x40`) and `isBossOrNoEscape` (`EncGroup+0x50`) are missing.

**Discrepancies:**
- **M10.09a (S1)** [`0x4d3180` vs `tools/floor_data.py:86`]: tools/floor_data.py and data_tables/record_layouts.json NEVER read bossGroups (+0x38 count / +0x40 pointer, 182 boss/FOE formations across 101 vanilla floors) or EncGroup+0x50 (isBossOrNoEscape flag). **Reach:** 182 vanilla boss/FOE encounter formations across 101 dungeon floors. **Fix:** Add boss_count=0x38, boss_pointer=0x40, and EncGroup+0x50 (is_boss) to record_layouts.json and tools/floor_data.py (read_bosses()).

### M10.10 FloorMap Cell Grid (Mass_s, Kind 1 vs Kind 5 & 3-Tier Group Namespace)
**Verdict:** S1

```asm
004cc260  mov ecx, dword ptr [edi + 0x14]
004cc32a  lea ecx, [ebx - 1]
```

tools/map_data.py:125
```python
            dungeon, name = entry.split('/')
            floor = name[:-4]
            try:
                names = script_names(params.read(f'{dungeon}/{floor}.bin'))
            except KeyError:
                continue
            for cell in read_map(archive.read(entry))['cells']:
                if cell['kind'] != EVENT_CELL or cell['index'] >= len(names):
                    continue
                script = names[cell['index']]
                script_entry = f'{dungeon}/{floor}/{script}.adv.bin'
                if script_entry not in entries:
                    continue
                for number in battles_of_script(archive.read(script_entry)):
                    found.setdefault((floor, number), []).append(
                        {'x': cell['x'], 'y': cell['y'], 'slots': cell['slots'], 'zone': cell['zone'],
```

**Audit Notes:** `Mass_s` 42-byte stride and offsets `+0x00, +0x01, +0x02, +0x03, +0x06` match. However, `battle_cells()` completely misses `kind == 5` fixed-tile encounter cells.

**Discrepancies:**
- **M10.10a (S1)** [`0x4cc260, 0x4cc32a` vs `tools/map_data.py:132`]: tools/map_data.py:132 (battle_cells) only scans cell["kind"] == 1 (EVENT_CELL), completely ignoring cell["kind"] == 5 (927 fixed-tile encounter cells in vanilla floor_maps.zip) and never resolving the 3-tier group namespace (0..39 normal, 40..59 fixed, >=60 boss, >=0x80000000 direct). **Reach:** 927 vanilla fixed-tile encounter cells across dungeon maps. **Fix:** Include cell["kind"] == 5 in battle_cells() and dispatch group indices across normal/fixed/boss/direct tiers.

### M10.11 .adv.bin Event Script Opcode 0x1F (Battle Trigger) Scanner
**Verdict:** S1

```asm
004d2570  sub esp, 0x10
004d2a10  mov edx, ecx
```

tools/map_data.py:70
```python


def battles_of_script(blob):
    """The fixed battle numbers a script starts (command 0x1F)."""
    b, found, pos = bytes(blob), [], 0
    while True:
        pos = b.find(BATTLE_COMMAND, pos)
        if pos < 0 or pos + 7 > len(b):
            return found
        found.append(struct.unpack_from('<i', b, pos + 3)[0])
        pos += 1


```

**Audit Notes:** Verified across all vanilla `.adv.bin` scripts in `backups/Dungeon/floor_maps.zip`: 198 real `0x1F` triggers (`41..52`) vs 235 naive matches = 37 false positives.

**Discrepancies:**
- **M10.11a (S1)** [`0x4d2570, 0x4d2a10` vs `tools/map_data.py:74`]: tools/map_data.py:72-80 (battles_of_script) scans raw bytes with b.find(b"\x1f\x01\x00") instead of walking .adv.bin instruction framing (0x4d2570/0x4d2a10), injecting 37 bogus battle number -256 false positives across vanilla floor_maps.zip. **Reach:** 37 vanilla dungeon event scripts in backups/Dungeon/floor_maps.zip. **Fix:** Walk .adv.bin instruction headers/lengths properly (or validate opcode framing) instead of raw substring search.

### M10.12 Aquaplus .pck Archive Container Format (Filename & Pack Chunks)
**Verdict:** S2

```asm
005ab5ab  mov eax, dword ptr [ecx + 0x14]
005ab5ae  add eax, 7
005ab5b1  and eax, 0xfffffff8
005ab5e4  mov al, byte ptr [ecx + 0x6b6394]
```

tools/pck_handler.py:26
```python
    def parse(self, data, filepath='<bytes>'):
        pack_idx = data.find(b'Pack                ')
        if pack_idx == -1:
            raise ValueError(f"Not a valid PCK archive (missing 'Pack' header): {filepath}")

        hdr_size, file_count = struct.unpack('<II', data[pack_idx+20:pack_idx+28])
        
        # Read filenames from table (offsets relative to 0x18)
        filenames = []
        for i in range(file_count):
            fn_rel = struct.unpack('<I', data[0x18 + i*4:0x18 + (i+1)*4])[0]
            fn_abs = 0x18 + fn_rel
            fn_end = data.find(b'\x00', fn_abs)
            filenames.append(data[fn_abs:fn_end].decode('latin-1'))

        # Read file entries
        self.files = []
        entry_pos = pack_idx + 28
        for i in range(file_count):
            off, sz = struct.unpack('<II', data[entry_pos:entry_pos+8])
            self.files.append((filenames[i], bytearray(data[off:off+sz])))
            entry_pos += 8

```

**Audit Notes:** Works on all vanilla `.pck` archives (where `Filename` precedes `Pack` and offsets are file-absolute), but uses substring search instead of chunk walking.

**Discrepancies:**
- **M10.12a (S2)** [`0x5ab5ab..0x5ab5b4` vs `tools/pck_handler.py:27`]: tools/pck_handler.py:27 locates the Pack chunk via raw byte search data.find(b"Pack                ") instead of walking chunks via (chunkSize + 7) & ~7 (0x5ab5ab..0x5ab5b4). **Reach:** 0 failures on vanilla .pck files; fragile if payload bytes ever contain the 20-byte Pack marker. **Fix:** Walk 24-byte chunk headers advancing by (chunkSize + 7) & ~7 to locate Filename and Pack chunks.

### M10.13 EnemyStatusData.pck Binary Layout
**Verdict:** MATCH

```asm
004f26db  mov eax, dword ptr [eax + 0x44]
004f2707  mov dword ptr [ebx + 0x30], eax
004503c5  test al, 1
00481488  test al, 1
```

tools/enemy_data.py:61
```python
def read_status(b):
    b = bytes(b)
    enemy = {'id': struct.unpack_from('<i', b, 0)[0], 'race': struct.unpack_from('<i', b, 0x10)[0],
             'name': cstring(b, struct.unpack_from('<Q', b, 0x08)[0]),
             'habitat': cstring(b, struct.unpack_from('<Q', b, 0x108)[0]),
             'flags': struct.unpack_from('<I', b, 0x3C)[0],
             'swing': struct.unpack_from('<f', b, 0x40)[0], 'weight': struct.unpack_from('<f', b, 0x44)[0]}
    enemy['race_name'] = RACES.get(enemy['race'], f"race {enemy['race']}")
    enemy['immune'] = [name for bit, name in IMMUNITY_BITS.items() if enemy['flags'] >> bit & 1]
    enemy['snack'] = bool(enemy['flags'] >> SNACK_BIT & 1)
    for key, off in STATS:
        enemy[key] = struct.unpack_from('<i', b, off)[0]
    for k, key in enumerate(RESISTANCES):
        enemy['res_' + key] = struct.unpack_from('<i', b, RESIST_OFFSET + 4 * k)[0]
    count = struct.unpack_from('<i', b, ATTACK_COUNT)[0]
    enemy['attacks'] = [a for a in struct.unpack_from(f'<{ATTACK_SLOTS}i', b, ATTACK_IDS) if a != -1][:max(count, 0)]
    enemy['raw_68'] = list(struct.unpack_from('<17i', b, 0x68))
    raw = enemy['raw_68']
    enemy['drops'] = [(raw[1 + 2 * k], raw[2 + 2 * k]) for k in range(max(0, min(raw[0], 2))) if raw[1 + 2 * k] != -1]
    enemy['equipment_drop'] = (raw[5], raw[6])        # chance in percent, how many slots it is drawn among
    # the slots (0x558517 - 0x5586fa): (0 a fixed piece | 1 the table of the zone, piece id | kind of the table, weight)
    enemy['equipment_slots'] = [tuple(raw[7 + 3 * k:10 + 3 * k]) for k in range(max(0, min(raw[6], 3)))]
    enemy['can_steal'] = bool(enemy['flags'] >> STEAL_BIT & 1)
    enemy['snack_item'] = raw[16] if raw[16] != -1 else None
    enemy['raw_f0'] = list(struct.unpack_from('<6i', b, 0xF0))
    enemy['passives'] = [a for a in enemy['raw_f0'][1:1 + max(0, min(enemy['raw_f0'][0], 5))] if a != -1]
    enemy['raw_110'] = list(struct.unpack_from('<6i', b, 0x110))
    return enemy
```

**Audit Notes:** Verified directly against exe `0x4f26db..0x4f2707` that `+0x2c` loads into stat[4] (DEX) and `+0x30` loads into stat[5] (AGI). Every field in `tools/enemy_data.py:61-88` and `record_layouts.json` matches.

### M10.14 EnemyAttackData.pck Binary Layout (incl. +0x90 Pattern ID)
**Verdict:** S0

```asm
0041b530  push ebp
004183d0  sub esp, 8
0041a483  mov eax, dword ptr [eax + 0x40]
```

tools/extract_vanilla.py:462
```python
    for fn, b in load('EnemyAttackData.pck'):
        e = EnemyAttackHelper.read_enemy_attack(b)
        count = i32(b, 0x48)
        slots = [(i32(b, 0x4C + 12 * k), word(b, 0x50 + 12 * k), i32(b, 0x54 + 12 * k)) for k in range(5)]
        if count != sum(1 for s in slots if s[0] != -1):
            problems.append(f"{fn} ({e['name']}): effect count {count} does not match slots")
        row = [fn, i32(b, 0), e['name'], e['desc'].split('\n')[0], i32(b, 0x28),
               i32(b, 0x2C), TARGET_NAMES.get(i32(b, 0x2C), ''), i32(b, 0x30), ATTR_NAMES.get(i32(b, 0x30), ''),
               f32(b, 0x34), f32(b, 0x38), f32(b, 0x3C), int(f32(b, 0x40)), f32(b, 0x44), count]
        for k, (eff_id, value, tail) in enumerate(slots):
            if k < count:
                uses[eff_id] += 1
                row += [eff_id, effect_name(eff_id), value, tail]
            else:
                row += [None, '', None, None]
        row += [', '.join(str(i32(b, o)) for o in range(0x88, 0xA0, 4)), e['desc']]
        rows.append(row)
```

gamedata/data.py:221
```python
        anim = r['Anim_0x28'] or 0
        reach = SHORT if (anim >> 7 & 1) else MID if (anim >> 8 & 1) else LONG if (anim >> 9 & 1) else NO_RANGE
        data.attacks[r['Skill_ID']] = EnemyAttack(
            id=r['Skill_ID'], name=r['Name'], target=r['Target_Code'], attr=r['Attr_Code'],
            chant_speed=r['Chant_Speed'] or 0, accuracy=r['Accuracy'] or 0, power=r['Power'] or 0,
            turns=int(r['Turns'] or 0), speed=r['Speed'] if r['Speed'] else 1.0, effects=effects, range=reach,
            passive='Passive Skill' in str(r['Vanilla_Desc'] or ''),
            chant_stat=_enemy_chant_stat(r['Anim_0x28'] or 0),
            # bit 2 of the word at file 0x28 (+0x40 in memory): a spell, which an anti-magic zone stops (0x41a483)
            plain=bool((r['Anim_0x28'] or 0) & 1), spell=bool((r['Anim_0x28'] or 0) >> 2 & 1),
            # bit 1 of the same word: a technique, which freeze stops (the choice of an AI unit, 0x431344 for spells under
            # silence, 0x4312e4 for techniques under freeze)
            technique=bool((r['Anim_0x28'] or 0) >> 1 & 1))

```

**Audit Notes:** Header `0xA0`, string pointers, power/speed/turns/acc, 5 effect slots (`+0x4C`, stride 12), and `Anim_0x28` flags match, but `+0x90` (`pattern`) is dropped downstream.

**Discrepancies:**
- **M10.14a (S0)** [`0x41b530` vs `gamedata/data.py:223`]: tools/extract_vanilla.py:477 dumps 0x88..0xA0 (including pattern at +0x90) only as an opaque Trailer CSV string, and gamedata/data.py:213-234 + tools/engine_export.py:56-62 never read or export pattern (+0x90), severing CActionPattern* dispatch for all 2,375 EnemyAttacks. **Reach:** All 2,375 vanilla EnemyAttackData.pck records. **Fix:** Extract pattern = i32(b, 0x90) (Trailer[2]) into EnemyAttack and export it in tools/engine_export.py.

### M10.15 Skill .pck Binary Layouts (Technique, Magic, Passive, Unique & Trailer[4])
**Verdict:** S0

```asm
0041e060  push ebp
0056dc10  sub esp, 0x14
00418227  mov al, byte ptr [eax + 0x48]
```

tools/skill_tree_data.py:51
```python
    for r in _rows('Skills'):
        trailer = [int(x) for x in str(r['Trailer']).split(',')]
        mask = trailer[CLASS_MASK] & 0xFFFFFFFF
        group = r['Group_0x30']
        found.append({'category': r['Category'], 'id': r['Skill_ID'], 'name': r['Name'], 'levels': r['Levels'],
                      'classes': [bit for bit in range(32) if mask >> bit & 1], 'pattern': trailer[PATTERN],
                      'range': RANGE_BITS.get(group & 0xF) if r['Category'] == 'Technique' and group is not None else None,
                      'sp': costs.get((r['Category'], r['Skill_ID']), [])[:r['Levels'] or 0]})
    return found
```

tools/engine_export.py:43
```python
def skill_json(s):
    return {
        'category': s.category, 'id': s.id, 'name': s.name, 'levels': whole(s.levels, 'levels'), 'target': s.target,
        'attr': s.attr, 'group': s.group, 'weapons': list(s.weapons or []),
        'effects': [[e, k, list(v)] for e, k, v in s.effects],
        'tp': whole_list(s.tp, f'tp of {s.name}'), 'sp': whole_list(s.sp, f'sp of {s.name}'), 'speed': list(s.speed),
        'cast': None if s.cast is None else list(s.cast),
        'accuracy': None if s.accuracy is None else list(s.accuracy),
        'turns': list(s.turns), 'classes': list(s.classes or []), 'range': s.range, 'chant_stat': s.chant_stat,
        'swing': s.swing or 0.0,
    }
```

**Audit Notes:** Verified `Technique` `n_slots = 5` at `0xE4..0x1D4` (`0x1D4 - 0xE4 = 5 * 0x30`) in `record_layouts.json` matches real `.pck` records. `tools/skill_tree_data.py:56` reads `Trailer[4]` (`pattern`), but `engine_export.py` drops it.

**Discrepancies:**
- **M10.15a (S0)** [`0x41e060` vs `tools/engine_export.py:43`]: tools/engine_export.py:43-53 omits Trailer[4] (pattern) from skill_json(), dropping CActionPattern* dispatch for all 241 vanilla player skills. **Reach:** All 241 vanilla player skills (Technique, Magic, Passive, Unique). **Fix:** Store pattern (Trailer[4]) on Skill in gamedata/data.py and export it in skill_json() at tools/engine_export.py:43-53.

### M10.16 EquipmentData.pck & SealScrollData.pck Binary Layouts
**Verdict:** MATCH

```asm
004f6530  sub esp, 8
004f7d80  cld
```

tools/pck_handler.py:286
```python
    HEADER = 0x48
    POINTERS = (8, 16, 0x38)

    @staticmethod
    def _strings(bin_data):
        return [bytes(bin_data[p:bin_data.find(b'\x00', p)]).decode('utf-8')
                for p in (struct.unpack_from('<Q', bin_data, off)[0] for off in SealScrollHelper.POINTERS)]

    @staticmethod
    def read_seal(bin_data):
        name, desc, name2 = SealScrollHelper._strings(bin_data)
        count = struct.unpack_from('<i', bin_data, 0x1C)[0]
        return {'name': name, 'desc': desc, 'name2': name2,
                'grand': struct.unpack_from('<i', bin_data, 0x18)[0] == 1,
                'enchants': list(struct.unpack_from('<4i', bin_data, 0x20))[:count],
                'price': struct.unpack_from('<i', bin_data, 0x30)[0],
                'level': struct.unpack_from('<i', bin_data, 0x34)[0]}

```

tools/pck_handler.py:609
```python
    @staticmethod
    def read_equipment(bin_data):
        p0 = struct.unpack('<I', bin_data[8:12])[0]
        p1 = struct.unpack('<I', bin_data[16:20])[0]
        p2 = struct.unpack('<I', bin_data[24:28])[0]
        p70 = struct.unpack('<I', bin_data[0x70:0x74])[0] if len(bin_data) > 0x74 else 0
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1', 'replace')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1', 'replace')
        s2 = bin_data[p2:bin_data.find(b'\x00', p2)].decode('latin-1', 'replace') if p2 < len(bin_data) else ""
        s70 = bin_data[p70:bin_data.find(b'\x00', p70)].decode('latin-1', 'replace') if p70 < len(bin_data) else name
        return {'name': name, 'desc': desc, 's2': s2, 's70': s70}

```

tools/extract_vanilla.py:421
```python
    for fn, b in load('EquipmentData.pck'):
        e = EquipmentHelper.read_equipment(b)
        rank_idx = i32(b, 0x4C)
        rank_label, rank_delay = ranks.get(rank_idx, ('', None))
        ids = [i32(b, o) for o in range(0x60, 0x70, 4)]
        if i32(b, 0x5C) != sum(1 for v in ids if v != -1):
            problems.append(f"{fn} ({e['name']}): enchant count {i32(b, 0x5C)} does not match ids {ids}")
        row = [fn, i32(b, 0), e['name'], e['s2'], i32(b, 0x20), EQUIP_CATEGORIES.get(i32(b, 0x20), '')]
        row += [i32(b, o) for o in range(0x24, 0x3C, 4)]
        row += [f32(b, 0x3C), f"{i32(b, 0x40) & 0xFFFFFFFF:#010x}", i32(b, 0x44), f32(b, 0x48)]
        row += [rank_idx, rank_label, rank_delay, i32(b, 0x50), i32(b, 0x54), i32(b, 0x58), i32(b, 0x5C)]
        for v in ids:
            row += [v if v != -1 else None, enchant_names.get(v, '') if v != -1 else '']
        row.append(e['desc'])
```

**Audit Notes:** All offsets for `EquipmentData.pck` (header `0x80`, stats `+0x24..+0x38`, upgrade rate `+0x3C`, class mask `+0x40`, swing `+0x48`, rank `+0x4C`, enchants `+0x5C..+0x6C`, string ptrs `8/16/24/0x70`) and `SealScrollData.pck` (header `0x48`, grand `+0x18`, count `+0x1C`, enchants `+0x20`, price `+0x30`, level `+0x34`) match.

### M10.17 ItemData.pck Binary Layout & Item Effect Switch Table (0x46c040)
**Verdict:** MATCH

```asm
0046c040  push esi
```

tools/pck_handler.py:232
```python
    @staticmethod
    def read_item(bin_data):
        p0, p1 = struct.unpack('<2Q', bin_data[8:24])
        p60 = struct.unpack('<Q', bin_data[0x60:0x68])[0]
        name = bin_data[p0:bin_data.find(b'\x00', p0)].decode('latin-1')
        desc = bin_data[p1:bin_data.find(b'\x00', p1)].decode('latin-1')
        name2 = bin_data[p60:bin_data.find(b'\x00', p60)].decode('latin-1') if p60 < len(bin_data) else ""
        return {'name': name, 'desc': desc, 'name2': name2}

```

tools/item_effect_data.py:60
```python
def skill_items(exe=None):
    """{item effect type: (skill id, flag)} for the types whose class only performs a skill."""
    try:
        exe = exe or Exe()
    except (SystemExit, Exception):
        return dict(SKILL_ITEMS_FALLBACK)
    if not exe or not exe.data:
        return dict(SKILL_ITEMS_FALLBACK)
    cases = struct.unpack(f'<{TYPES}I', exe.read(SWITCH_TABLE, 4 * TYPES))
    found = {}
    for kind, case in enumerate(cases):
```

**Audit Notes:** `ItemData.pck` header `0x70`, buy/sell prices (`+0x1C/+0x20`), 4 `(type, value)` pairs (`+0x24`, stride 8), string pointers (`8/16/0x60`), and `tools/item_effect_data.py` reading the `0x46c040` item-effect switch table directly from the exe all match.

### M10.18 SummonData.bin & NPCData.bin Binary Layouts (Attack Slots & useLimit)
**Verdict:** S2

```asm
004ff2bb  mov ebp, dword ptr [eax + 0xac]
0050030b  mov ebp, dword ptr [eax + 0xb0]
```

tools/summon_data.py:45
```python
    count = i(r['attack_count'])
    strings = [t.decode('utf-8', 'replace') for t in b[r['attack_ids'] + 8 * r['attack_slots']:].split(b'\x00') if t]
    printable = [t for t in strings if len(t) > 2 and all(32 <= ord(c) < 0x3000 for c in t)]
    pcount = max(0, min(i(r['passive_count']), r.get('passive_slots', 5)))
    passives = [i(r['passive'] + 4 * k) for k in range(pcount) if i(r['passive'] + 4 * k) != -1]
    return {'id': i(r['id']), 'character': i(r['character']),
            'family': i(r['enemy']), 'enemy': i(r['enemy']),
            'level': i(r['level']),
            'rank': i(r['rank']),
            'factors': dict(zip(STATS, struct.unpack_from('<6f', b, r['factors']))),
            'attacks': [i(r['attack_ids'] + 8 * k) for k in range(max(count, 0))],
            'passive': passives[0] if passives else None,
            'passives': passives,
            'name': printable[-1] if printable else ''}
```

tools/npc_data.py:48
```python
           'name': b[name_at:b.index(b'\x00', name_at)].decode('utf-8', 'replace'),
           'attacks': [i(ATTACK_IDS + 8 * k) for k in range(count)],
           'cost': i(RECORD['cost']), 'contract': i(RECORD['contract']), 'unlock_flag': i(RECORD['unlock_flag'])}
    passive_count = max(0, min(i(RECORD['passive_count']), RECORD['passive_slots']))
    npc['passives'] = [i(PASSIVE_IDS + 4 * k) for k in range(passive_count) if i(PASSIVE_IDS + 4 * k) != -1]
    npc.update(zip(STATS, struct.unpack_from('<6i', b, RECORD['stats'])))
    return npc
```

**Audit Notes:** Stat multipliers, levels, ranks, attack IDs, passive counts/IDs, cost, contract, and unlock flags match; two S2 layout defects remain.

**Discrepancies:**
- **M10.18a (S2)** [`0x4ff2bb, 0x50030b` vs `tools/summon_data.py:55`]: Neither tools/summon_data.py:55 nor tools/npc_data.py:49 reads the per-attack useLimit int (+0x44 + 8*k in SummonData, +0x40 + 8*k in NPCData) needed by AI opcode 15 (0 non-zero vanilla useLimits). **Reach:** 0 vanilla Summons/NPCs have non-zero useLimit (105 Summons, 107 NPCs checked). **Fix:** Read useLimit at +0x44+8*k (SummonData) and +0x40+8*k (NPCData) and export alongside attack IDs.
- **M10.18b (S2)** [`0x50030b` vs `tools/summon_data.py:46`]: data_tables/record_layouts.json sets SummonData.attack_slots = 12, which overlaps passive_count at 0x98 (0x40 + 11*8 = 0x98, not 12*8 = 0xA0), shifting summon_data.py:46's trailing string-scan start to 0xA0 inside passive[1..4]. **Reach:** 0 vanilla string corruption (vanilla count <= 11 and strings read from tail), but schema overlaps 0x98..0x9F. **Fix:** Set SummonData.attack_slots = 11 in data_tables/record_layouts.json and start string scanning after passive[4] (0xB0).

### M10.19 CharacterData.pck / PlayerStatusData.bin, CommandData.pck & EnchantData.pck Layouts
**Verdict:** S1

```asm
00459ff0  push ebp
0044b01e  test byte ptr [eax + 0xc], 1
004e4b70  sub esp, 8
```

tools/character_data.py:60
```python
        return None
    name = re.search(rb'Name="([^"]*)"', files.get('PlayerData.txt', b''))
    ints = struct.unpack_from('<15i', status, 0)
    foods = lambda at: [f for f in ints[at + 1:at + 1 + max(0, min(ints[at], 3))] if f != -1]
    character = {'id': ints[0], 'name': name.group(1).decode('utf-8') if name else '', 'base_class': ints[1],
                 'unique_skill': ints[2] if ints[2] != -1 else None, 'flag': ints[3],
                 'foods_first': foods(4), 'foods_second': foods(8), 'raw_30': list(ints[12:15]),
                 'pep': list(struct.unpack_from(f'<{PEP_COUNT}f', status, PEP_OFFSET)),
                 'start_class': None, 'start_exp': None}
    if initial:
        first = struct.unpack_from('<4i', initial, 0)
        character['start_class'], character['start_exp'] = first[1], first[3]
    return character
```

tools/engine_export.py:136
```python
        'characters': [{'name': c['name'], 'base_class': c['base_class'], 'flag': c['flag'],
                        'start_exp': c['start_exp'], 'unique_skill': c['unique_skill']} for c in data.characters],
        'equipment': [equipment_json(p) for p in data.equipment.values()],
```

**Audit Notes:** `CommandData.pck` and `EnchantData.pck` match. However, `PlayerStatusData.bin` drops two active combat fields (`+0x30` Race and `+0x3C` 21-float Pep table) before C#.

**Discrepancies:**
- **M10.19a (S1)** [`0x459ff0, 0x4e4b70` vs `tools/character_data.py:62`]: tools/character_data.py:62-67 discards PlayerStatusData.bin +0x30 (Character.Race, where Ist id=11 has race=6) and tools/engine_export.py:136-137 omits both race (+0x30) and the 21-float pep table (+0x3C) from the C# export, causing Ist to take full damage from all 13 Effect 87 EnemyAttacks and freezing party Pep in combat. **Reach:** All 20 playable characters (esp. Ist race=6 vs 13 Effect-87 attacks, and Alisia Positive Trance 440). **Fix:** Expose race = ints[12] (+0x30) in tools/character_data.py and export both race and pep (21 floats) in tools/engine_export.py:136.

## Part: M11 & Reverse Sweep (Unit Build/Stats & ENGINE-ONLY Detector)


> **Auditor:** `diff-m11-reverse` (Read-Only Phase 2 Two-Way Diff)
> **Binary Spec:** `docs/binary_spec/M11_UNIT_BUILD_AND_STATS.md` (`M11.01..M11.15`) + `docs/binary_spec/00_INVENTORY.json` + `docs/binary_spec/M00..M10.md`
> **Target Executable:** `backups/exe/DT22_en_unwrapped.vanilla.exe` (SHA-256 `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`)
> **Summary Counts (21 items):** `MATCH = 3` (`M11.03, M11.06, M11.10`) | `S0 = 0` | `S1 = 8` (`M11.01, M11.02, M11.04, M11.05, M11.08, M11.09, M11.11, M11.14`) | `S2 = 3` (`M11.07, M11.12, M11.15`) | `MODEL-LIMIT = 1` (`M11.13`) | `ENGINE-ONLY = 6` (`ENGINE-ONLY-01..06`, including confirmed intentional inactive trial hook `L46` at `ENGINE-ONLY-06`).

---

## Part A — Forward Diff of M11 (`M11.01..M11.15`)

### M11.01 `ClassLevelData.pck`, `ClassData.pck`, `Character.pck` Binary Layouts & `GetClassLevelID` (`0x5545b0`)

- **Verdict:** S1
- **Summary:** Python binary readers for `ClassLevelData.pck` (all 38 rows, 99 levels, 8 stats, `GROWTH_ROW` mapping & default fallback), `ClassData.pck` (all 49 records, `+0x10` name, `+0x24` unarmed rank), and `Character.pck` (`PlayerStatusData.bin` + `InitialData.bin`, 18 playable characters) match the vanilla binary. However, `M11.01a` (`S1`): `engine_export.py` drops the `PlayerStatusData.bin +0x3c` 21-float motivation delta table (`pep`) when exporting `characters`, and C# `Character` (`Data.cs`/`Loader.cs`) has no `Pep` field, starving `Battle.cs` of all per-character battle motivation deltas (`M11.14`). *(Note: `InitialData.bin +0x08` `initPrevClassId` and starting gear are not read because `Scenario.cs` uses checkpoint role templates.)*
- **Sub-bugs:**
  - `M11.01a` (`S1`): `engine_export.py` omits `c['pep']` from exported `characters`, and `Data.cs`/`Loader.cs` do not model `PlayerStatusData.bin +0x3c..+0x8c`.

**Binary Evidence (`0x5545b0`, `0x5540e0`, `0x553ac8`):**
```asm
005545b0  cmp      ecx, 0x1f
005545b9  jmp      dword ptr [ecx*4 + 0x5546fc]
005545e2  cmp      edx, 2
005545e5  sete     al
005545e8  add      eax, 4
005540e0  mov      ecx, 0x319
00553ac8  movq     xmm0, qword ptr [edi + 0x20]
```

**Code Evidence — `tools/class_data.py:26`:**
```python
GROWTH_ROW = {0: 0, 1: 1, 2: 2, 3: 3, 4: {1: 4, 2: 5}, 5: 6,
...
def growth_row(class_id, previous=None):
    row = GROWTH_ROW[class_id]
    if isinstance(row, dict):
        return row.get(previous, min(row.values()))
    return row
```

**Code Evidence — `tools/character_data.py:64`:**
```python
    character = {'id': ints[0], 'name': name.group(1).decode('utf-8') if name else '', 'base_class': ints[1],
                 'unique_skill': ints[2] if ints[2] != -1 else None, 'flag': ints[3],
                 'foods_first': foods(4), 'foods_second': foods(8), 'raw_30': list(ints[12:15]),
                 'pep': list(struct.unpack_from(f'<{PEP_COUNT}f', status, PEP_OFFSET)),
                 'start_class': None, 'start_exp': None}
```

**Code Evidence — `tools/engine_export.py:136`:**
```python
        'characters': [{'name': c['name'], 'base_class': c['base_class'], 'flag': c['flag'],
                        'start_exp': c['start_exp'], 'unique_skill': c['unique_skill']} for c in data.characters],
```

**Code Evidence — `engine_cs/src/DtEngine/Data.cs:198`:**
```csharp
    public sealed class Character
    {
        public string Name;
        public int BaseClass, Flag;
        public int StartExp;
        public int UniqueSkill = T.NONE;
    }
```

---

### M11.02 Player Stat Recalculation Spine (`0x4f7c00`) & Base + Growth + Crown Formula (`0x4f5d60`)

- **Verdict:** S1
- **Summary:** Base + Growth + Crown addition to HP, TP, all 6 stats, and all 8 resistances matches `0x4f5d60`, and Stage-2 Specialty / Stage-3 Equipment ordering matches. However, two active `S1` pipeline divergences break the 7-stage spine:
  - `M11.02a` (`S1`): Stage 4/5 inversion — `Units.cs` adds Stage-5 `offhandBonus` (Dual-Wield Passive `256`) into `gearedForLine` **before** running Stage-4 `EnchantBonus`, inflating row-conditional enchants (`222..225, 281`, e.g., Grand Sealbook `222` Front ATK +8%) for every dual-wielding member. In the binary (`0x4f7c42` -> `0x4f7c4e`), Stage 4 runs strictly before Stage 5 (`0x4fc26f`).
  - `M11.02b` (`S1`): `Scenario.cs` mutates `unit.Front` (enforcing `front_size`) **after** `BuildMember` already baked `ENCHANT_LINE` (`222..225, 281`) into `unit.Base`, leaving moved members with stale opposite-row enchant bonuses.
  - `M11.02c` (`S2`): Stage-1 Command `81` (`0x51`, Pep Freeze from food `Miracle Shake`) overwrite of `motivation_0xd8` is absent from `Units.cs`.
  - *(Per Roadmap Section 2, `charBonus[0..15]` sub-event bonuses and Stage 6 `_CalculatePartySkillSynergy` `0x4f8fe0` are `MODEL-LIMIT` out of scope.)*

**Binary Evidence (`0x4f7c1f..0x4f7c62`, `0x4f5dab..0x4f5f06`):**
```asm
004f7c1f  call     dword ptr [eax + 0x104]
004f7c2f  call     dword ptr [eax + 0x18c]
004f7c37  call     0x4f6530
004f7c42  call     dword ptr [eax + 0x180]
004f7c4e  call     dword ptr [eax + 0x10c]
004f7c62  jmp      dword ptr [eax + 0x110]
004f5dab  mov      ebp, dword ptr [ebp + 0x120]
004f5f04  add      eax, ebp
004f5f06  mov      dword ptr [ebx + 0x6c], eax
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:697`:**
```csharp
            int[] gearedForLine = totals;
            if (offhandBonus != null)
            {
                gearedForLine = new int[6];
                for (int s = 0; s < 6; s++) gearedForLine[s] = totals[s] + offhandBonus[s];
            }
            EnchantBonus(counted, characterStats, hp, tp, front, bonusTotal, out int bonusHp, out int bonusTp, resistBonus, gearedForLine);
```

**Code Evidence — `engine_cs/src/DtEngine/Scenario.cs:720`:**
```csharp
            if (frontCount > front)
            {
                var order = party.Where(u => u.Front).OrderBy(u => u.MaxHp).ToList();
                for (int i = 0; i < frontCount - front; i++) order[i].Front = false;
            }
            if (!party.Any(u => u.Front) && party.Count > 0)
            {
                Unit best = null;
                foreach (var u in party) if (best == null || u.MaxHp > best.MaxHp) best = u;
                best.Front = true;
            }
```

---

### M11.03 Class Change (`0x4f4e80`), Level Reset (`0x4f5650` / `0x523727` / `0x5245d0`) & Crown Reset Steps (`0x4f94f0`, Vanilla `X09..X12`)

- **Verdict:** MATCH
- **Summary:** Vanilla crown reset thresholds `((98, 5), (89, 4), (79, 3), (69, 2), (59, 1))` and cap `50` in `progression.py` match `0x4f94f0..0x4f954a` exactly. Intentional Balance mod patches `X09..X12` (`0x4f9502..0x4f952c`: `+5->+6, +4->+5, +3->+4, +2->+3`) are evaluated cleanly via `catch_up_options.py` (`CrownOptions`) without mutating vanilla defaults. `Units.cs` applies `crownBonus` to HP, TP, all 6 stats, and all 8 resistances (`0x4f5dab..0x4f5f06`), and `Scenario.cs` matches Tier-1/2/3 `ClassPath` and unclamped cumulative SP sum `1..level` (`0x4f5b27..0x4f5b87`). *(Guild menu UI `0x523727`, save bitmasks, and trophy 42 are out-of-scope UI/save systems per Section 2.)*

**Binary Evidence (`0x4f94f0..0x4f954a`):**
```asm
004f94f0  mov      eax, dword ptr [esp + 4]
004f94f4  sub      eax, dword ptr [ecx + 4]
004f94f7  cmp      eax, 0x62
004f94fc  add      dword ptr [ecx + 0x120], 5
004f9505  cmp      eax, 0x59
004f9513  cmp      eax, 0x4f
004f9521  cmp      eax, 0x45
004f952f  cmp      eax, 0x3b
004f9540  mov      edx, 0x32
004f9547  cmovg    eax, edx
```

**Code Evidence — `gamedata/progression.py:58`:**
```python
RESET_STEPS = ((98, 5), (89, 4), (79, 3), (69, 2), (59, 1))      # 0x4f94f7 - 0x4f9534
RESET_MAX = 50                                                   # 0x4f9540
...
def reset_bonus(level_before, level_after=1, bonus=0, steps=RESET_STEPS, cap=RESET_MAX):
    dropped = level_before - level_after
    gained = next((points for levels, points in steps if dropped >= levels), 0)
    return min(cap, bonus + gained)
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:528`:**
```csharp
            for (int s = 0; s < 6; s++) characterStats[s] = grown[s] + crownBonus;
            int hp = grown[6] + crownBonus, tp = grown[7] + crownBonus;
...
            for (int i = 0; i < 8; i++) resist[i] = crownBonus + resistBonus[i];
```

---

### M11.04 Class Specialty Modifiers (`_CalculateParameterSpecialty` `0x4f7c70`, Jump Table `0x4f81e8` & `.rdata` `0x6d3b64..0x6d40a0`)

- **Verdict:** S1
- **Summary:** All 38 `.rdata` specialty tables in `class_modifier_data.py` (both live exe disassembly `_cases` and `STATIC_CLASS_MODIFIERS`) match `0x4f81e8` / `0x6d3b64..0x6d40ab` with 0 diffs, and `Units.cs` correctly uses pre-mastery raw upgraded piece stats, `yearningFloor`, and Enchant `264` (`+0.02`). However, three divergences exist:
  - `M11.04a` (`S1`): `Units.cs` computes `rate = entry.Modifier + 0.01 * yearning + modifierUp` and `(characterStats[s] + rawStats[s]) * rate` in IEEE-754 `f64` rather than `f32` (`mulss`/`addss`/`cvttss2si` at `0x4f7fa4..0x4f803b`), yielding off-by-1 divergences on real combinations (369 tested cases diverge, e.g., `base=0.01, yearning=2, ench264=1, combined=100` -> binary `4` vs C# `5`; `base=0.01, yearning=5, combined=50` -> binary `2` vs C# `3`).
  - `M11.04b` (`S1`): Python helper `class_modifier_data.py:specialty_gain` floors at `0` instead of `int(yearning)` (`0x4f800e..0x4f8041`) and omits Enchant `264` (`+0.02f` at `0x4f7fb0..0x4f7fd1`).
  - `M11.04c` (`S2`): `Units.cs:ClassModifierEntries` falls back to `first` (`exact ?? none ?? first`) when `previous` matches neither valid parent of a dual-parent Tier-3 class (`4, 10, 17, 18, 24, 30`), whereas the binary (`0x4f7d31..0x4f7d49`) jumps to `0x4f7eb1` with `edi = 0` (`count = 0`, no specialty bonus).

**Binary Evidence (`0x4f7d31..0x4f7d49`, `0x4f7fa4..0x4f8041`):**
```asm
004f7d31  mov      eax, dword ptr [ebx + 0xa4]
004f7d37  cmp      eax, 7
004f7d46  cmp      eax, 8
004f7d49  jne      0x4f7eb1
004f7fa4  mulss    xmm0, dword ptr [0x6d92d4]    ; float 0.01
004f7fb0  push     0x108
004f7fd1  addss    xmm0, dword ptr [0x6d92e0]    ; float 0.02
004f800e  cvttss2si ebp, xmm0
004f8035  mulss    xmm0, dword ptr [esp + 0x10]
004f803b  cvttss2si ecx, xmm0
004f8041  cmovge   eax, ecx
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:456`:**
```csharp
            var chosen = exact ?? none ?? first;
            return chosen == null ? Array.Empty<ClassMod>() : new[] { chosen };
...
                                gains[s] += Math.Max(yearningFloor, PyMath.Int((characterStats[s] + rawStats[s]) * (entry.Modifier + 0.01 * yearning + modifierUp)));
```

**Code Evidence — `tools/class_modifier_data.py:249`:**
```python
def specialty_gain(character_stat, piece_stat, modifier, yearning=0):
    if piece_stat <= 0:
        return 0
    return max(0, int((character_stat + piece_stat) * (modifier + 0.01 * yearning)))
```

---

### M11.05 Equipment Stat Aggregation, Forge Growth (`0x4e12a0..0x4e15ef`) & Passives `243`/`298` (`0x4f6530`)

- **Verdict:** S1
- **Summary:** Equipment layout extraction, zero-base-stat non-scaling (`base == 0 -> 0`), offhand weapon skip (`slot == 1 && Category == 0`), Sealbook skip, and Passives `243 + 298` applying exclusively to `ATK` and `RES` across slots `0..4` match `0x4e12a0..0x4e15ef` and `0x4f6530`. However:
  - `M11.05a` (`S1`): `extract_vanilla.py` rounds `Upgrade_Rate` (`f32`) to 4 decimal places in Excel (`1.2999999523 -> 1.3`, `1.3999999762 -> 1.4`) and `Units.cs:PieceStats` multiplies `upgrade * piece.Rate` in `f64` rather than `f32` (`mulss` at `0x4e1304`), causing 4 exact off-by-1 divergences on vanilla gear (`Tantou` id 356 at +90: binary `116` vs C# `117`; `Kite Shield` id 538 at +45/+85/+90: binary `63/119/126` vs C# `62/118/125`).
  - `M11.05b` (`S2`): `Units.cs` multiplies `stats[Unit.ATK] * mastery` and `stats[Unit.RES] * mastery` in `f64` instead of `f32` (`0x4f6604`, `0x4f6638`).

**Binary Evidence (`0x4e12c6..0x4e130d`, `0x4f659c..0x4f6644`):**
```asm
004e12c6  mov      esi, dword ptr [eax + 0x3c]
004e12c9  test     esi, esi
004e1304  mulss    xmm0, dword ptr [ecx + 0x54]
004e1309  cvttss2si eax, xmm0
004e130d  add      eax, esi
004f659c  cmp      dword ptr [eax + 0x38], 0
004f65ab  push     0xf3
004f65d6  push     0x12a
004f6604  mulss    xmm0, dword ptr [esp + 0xc]
004f6638  mulss    xmm0, dword ptr [esp + 0xc]
```

**Code Evidence — `tools/extract_vanilla.py:239`:**
```python
def f32(b, off):
    v = struct.unpack_from('<f', b, off)[0]
    return round(v, 4) if math.isfinite(v) else None
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:513`:**
```csharp
        public static int[] PieceStats(Piece piece, int upgrade)
        {
            var r = new int[6];
            for (int s = 0; s < 6; s++) r[s] = piece.Stats[s] != 0 ? piece.Stats[s] + PyMath.Int(upgrade * piece.Rate) : 0;
            return r;
        }
...
                    stats[Unit.ATK] = stats[Unit.ATK] + PyMath.Int(stats[Unit.ATK] * mastery);
                    stats[Unit.RES] = stats[Unit.RES] + PyMath.Int(stats[Unit.RES] * mastery);
```

---

### M11.06 Weapon Rank, Unarmed Rank (`ClassData+0x24` / `0x4f5585`) & Enchant `263` (`0x4f54d0`)

- **Verdict:** MATCH
- **Summary:** All 12 `WeaponRankData.pck` multipliers (`0..11`: `1.00..2.90`) match `extract_vanilla.py` and `gamedata/data.py` with 0 diffs. All 49 `ClassData.pck +0x24` unarmed rank IDs (`0..31` playable + `32..48` all Rank 1) match `class_data.py`, `engine_export.py`, and `Loader.cs` with 0 diffs. `Units.cs` matches the exact priority: mainhand weapon rank -> Enchant `263` forced to Rank 1 (`A` = `1.20f`) -> `ClassUnarmedRanks[classId]`. *(Synthetic non-weapon in slot 0 returning `1.0f` at `0x4f5515..0x4f553f` is unreachable in real gear/UI.)*

**Binary Evidence (`0x4f54d8..0x4f55d4`):**
```asm
004f54d8  mov      eax, dword ptr [esi + 0xa8]
004f5536  mov      eax, dword ptr [eax + 0x64]
004f557f  mov      eax, dword ptr [eax + 0x3c]
004f5595  push     0x107
004f55ab  call     dword ptr [eax + 0xf0]
004f55b5  mov      dword ptr [esp + 4], 1
004f55d4  movss    xmm0, dword ptr [eax + 0x28]
```

**Code Evidence — `tools/class_data.py:76`:**
```python
def class_unarmed_ranks(path=CLASS_PCK):
    ranks = {}
    for _, blob in PckArchive(path).files:
        blob = bytes(blob)
        ranks[struct.unpack_from('<i', blob, 0)[0]] = struct.unpack_from('<i', blob, 0x24)[0]
    return ranks
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:714`:**
```csharp
            double rankDelay;
            if (weapon != null && weapon.Rank != T.NONE && weapon.Rank >= 0)
                rankDelay = data.WeaponRanks[weapon.Rank];
            else if (counted.ContainsKey(263) && data.WeaponRanks.TryGetValue(1, out double rankA))
                rankDelay = rankA;
            else if (data.ClassUnarmedRanks.TryGetValue(classId, out int unarmedRank) && data.WeaponRanks.TryGetValue(unarmedRank, out double classUnarmed))
                rankDelay = classUnarmed;
            else
                rankDelay = UnarmedDelay(data);
```

---

### M11.07 Enchantment Collection, Dual-Wield Offhand Filter, Stacking & Party-Leader Sealbook (`0x4f62c0`, `0x4f64b0`, `0x4f7ac0`, `0x4f5470`)

- **Verdict:** S2
- **Summary:** `EnchantData.pck +0x20` bit 0 (`enchant_stacks`) and bit 7 (`enchant_offhand`) match `backups/EnchantData.pck` with 0 diffs (`gamedata/data.py`, `Loader.cs`), `Units.cs` enforces the offhand weapon bit-7 gate on innate equipment enchants, collects personal Sealbook (`slot 5`) and Party-Leader Grand Sealbook (`partyEnchants`), and applies bit-0 stacking deduplication (including Balance variant toggles in `variant.py`).
- **Sub-bug:**
  - `M11.07a` (`S2`): `Scenario.cs:ForgeEnchants` aggregates forged enchants from all pieces — including a slot-1 dual-wield offhand weapon — into a single flat `Dictionary<int, int> forged`, and `Units.cs` adds all `forged` entries unconditionally without checking `data.EnchantOffhand` (bit 7). In the binary (`0x4f6362..0x4f6385`), all enchants in `eq.enchants_0x84` (both innate and forged) on an offhand weapon require bit 7. *(Severity `S2`: 0 rows in default `sim_setup.xlsx` `EnchantPlan` lack bit 7, so dormant unless a non-bit-7 enchant is forged onto an offhand weapon.)*

**Binary Evidence (`0x4f6334..0x4f638d`, `0x4f64fc..0x4f6501`):**
```asm
004f6334  cmp      dword ptr [esp + 0x10], 1
004f635c  cmp      dword ptr [eax + 0x38], 0
004f637d  mov      eax, dword ptr [eax + 0x38]
004f6380  shr      eax, 7
004f6383  test     al, 1
004f6385  je       0x4f6393
004f64fc  mov      al, byte ptr [eax + 0x38]
004f64ff  and      al, 1
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:646`:**
```csharp
                    if (isOffhandWeapon && offhandFilter && !data.EnchantOffhand.Contains(e)) continue;
...
            if (forged != null)
                foreach (var kv in forged)
                {
                    enchants.TryGetValue(kv.Key, out int c); enchants[kv.Key] = c + kv.Value;
                    dollEnchants.TryGetValue(kv.Key, out int dc); dollEnchants[kv.Key] = dc + kv.Value;
                }
```

**Code Evidence — `engine_cs/src/DtEngine/Scenario.cs:291`:**
```csharp
            foreach (var use in equipment)
                pieces.Add(new ForgePiece { Weapon = Data.Equipment[use.EquipId].Category == 0, Upgrade = use.Upgrade, Free = EnchantSlotsFor(use.Upgrade) });
```

---

### M11.08 Equipment & Sealbook Enchant Stat/Resistance Modifiers (`_CalculateParameterEnchant` `0x4f8270`)

- **Verdict:** S1
- **Summary:** All 78 stat/resistance enchant IDs (`0..28`, `88..119`, `222..225`, `281`, `310..356`), percentage/flat formulas, and intermediate clamps (`±baseHp/2`, `±baseTp/2`, `±100` resist) in `Formulas.cs` and `Units.cs:EnchantBonus` match `0x4f8270..0x4f8fd3` (and `f32(x) * 0.08f` matches `f64` with 0 diffs across `1..1999`). However, two active `S1` bugs affect row-conditional enchants `222..225, 281`:
  - `M11.08a` (`S1`): `Units.cs:697-703` feeds `totals + offhandBonus` into `gearedForLine` for `222..225, 281`, whereas Stage 4 (`0x4f8270`) runs **before** Stage 5 Dual-Wield `256` (`0x4fc26f`).
  - `M11.08b` (`S1`): `Scenario.cs:723, 729` flips `unit.Front` after `BuildMember` statically baked `ENCHANT_LINE` (`222..225, 281`) into `unit.Base`, leaving row-adjusted members with wrong-row bonuses.

**Binary Evidence (`0x4f8311..0x4f84a0`, `0x4f8bde..0x4f8d7e`):**
```asm
004f8311  test     byte ptr [eax + 0x38], 1
004f8372  cmp      eax, 4
004f8437  sar      eax, 1
004f8497  cmp      eax, 0x64
004f849d  cmp      eax, -0x64
004f8bde  mulss    xmm0, dword ptr [0x6d9300]    ; float 0.08
004f8c3a  sar      edx, 3
004f8d7e  sar      edx, 4
```

**Code Evidence — `engine_cs/src/DtEngine/Formulas.cs:112`:**
```csharp
        public static readonly Dictionary<int, (bool front, (int stat, double share)[] shares)> ENCHANT_LINE =
            new Dictionary<int, (bool, (int, double)[])>
            {
                { 222, (true, new[] { (0, 0.08) }) },
                { 223, (true, new[] { (0, 25.0), (1, 25.0) }) },
                { 224, (false, new[] { (2, 0.08) }) },
                { 225, (false, new[] { (2, 25.0), (3, 25.0) }) },
                { 281, (false, new[] { (4, 50.0), (5, 50.0) }) },
            };
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:697`:**
```csharp
            int[] gearedForLine = totals;
            if (offhandBonus != null)
            {
                gearedForLine = new int[6];
                for (int s = 0; s < 6; s++) gearedForLine[s] = totals[s] + offhandBonus[s];
            }
            EnchantBonus(counted, characterStats, hp, tp, front, bonusTotal, out int bonusHp, out int bonusTp, resistBonus, gearedForLine);
```

---

### M11.09 Status/Passive `%` Modifiers (`0x4fbdd0`), Dual-Wield Offhand (`256`), Party-Skill Synergy (`0x4f8fe0`) & Hard Caps (`0x4fc620`)

- **Verdict:** S1
- **Summary:** `Units.cs` matches `41..46` on `CurStat`, exclusive `189 -> 193 -> 194`, Petrification `120` (`±Raw/2`), `169`/`172` (on `BaseHp`)/`184..186`/`192`/`202 -> 341`/`248`, Dual-Wield `256` offhand added after stat buffs, `[0, 9999]` primary stat caps, and `[-100, +100]` resistance caps. Stage-6 `_CalculatePartySkillSynergy` (`0x4f8fe0`, passives `360..377/405/415`) is explicitly `MODEL-LIMIT` (out-of-scope Party Skills per Section 2). Divergences:
  - `M11.09a` (`S1`): `Units.cs:MaxHp` (`385..396`) and `BuildMember` (`710`) omit the binary `max(1, ...)` lower clamp on `MaxHp` and `MaxTp` (`0x4fc62f..0x4fc64e`), allowing `MaxHp <= 0` under negative `St[172]` or HP-down enchants.
  - `M11.09b` (`S2`): `Trump Card` (`48`) subtracts `10000` (`total -= 10000`) instead of overwriting `dStat[1] = -10000` (`0x4fbfef`), retaining any prior `St[42]` DEF% buff delta.
  - `M11.09c` (`S2`): Post-clamp Fixed Resistances `416..423` (`0x4fc709..0x4fc887`) are hardcoded solely to `SamsaraState == 2` (`Units.cs:400`) rather than reading status commands `416..423`; `184/185/186` only check `St[]` (not `Has()`); and status/dual-wield multipliers use `f64` instead of `f32`.

**Binary Evidence (`0x4fbfef`, `0x4fc26f`, `0x4fc629..0x4fc786`):**
```asm
004fbfef  mov      ebx, 0xffffd8f0
004fc26f  push     0x100
004fc629  mov      edx, dword ptr [esi + 0x98]
004fc62f  add      edx, dword ptr [esi + 0x10]
004fc637  cmovle   edx, edi
004fc649  mov      edx, 0x270f
004fc6c7  mov      edx, 0xffffff9c
004fc6cf  mov      ecx, 0x64
004fc709  push     0x1a0
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:368`:**
```csharp
            if (St[TRUMP_CARD] != null)
            {
                if (name == ATK) total += PyMath.Int(Base[DEF] * St[TRUMP_CARD].Value);
                else if (name == DEF) total -= 10000;
            }
...
        public int MaxHp
        {
            get
            {
                int hp = MaxHpBase;
                if (StCount == 0) return hp;
                var s = St[MAX_HP_BUFF];
                if (s != null) hp += PyMath.Int(BaseHp * s.Value);
                return hp;
            }
        }
...
            if (SamsaraState == 2) return Samsara[index];
```

---

### M11.10 `LvExpSkptData.pck` Layout, Cumulative EXP/SP Curves (`0x55c100`, `0x4f5610`) & Level-Up SP Cap (`0x448560`)

- **Verdict:** MATCH
- **Summary:** All 99 levels of `backups/LvExpSkptData.pck` match `extract_vanilla.py`, `gamedata/data.py`, `engine_export.py`, and `Loader.cs` with 0 diffs (cumulative Lv99 EXP = `3,042,158`, cumulative SP = `685`). `Scenario.cs:LevelOfExp` matches `0x4f5610` (`RecalcLevelFromExp`), `Scenario.cs:SpTotal` matches cumulative SP sum `1..level`, and `variant.py` cleanly supports `sp_curve` mod rows. *(Battle-result SP cap `999` at `0x4485c4` and `SetExp` cap `9,999,999` at `0x4f97e0` never trigger on vanilla static builds since `685 < 999` and `3,042,158 < 9,999,999`.)*

**Binary Evidence (`0x4f97e0..0x4f97ee`, `0x4f5625..0x4f563f`, `0x4485c4..0x44861b`):**
```asm
004f97e0  mov      edx, 0x98967f
004f5625  call     0x55c100
004f5630  cmp      esi, 0x63
004f563b  cmova    esi, ebp
004485c4  mov      edi, 0x3e7
00448612  cmp      eax, 0x3e7
```

**Code Evidence — `tools/extract_vanilla.py:456`:**
```python
def build_exp_rows():
    return [[fn] + list(struct.unpack_from('<3I', b, 0)) for fn, b in load('LvExpSkptData.pck')]
```

**Code Evidence — `engine_cs/src/DtEngine/Scenario.cs:96`:**
```csharp
        public int LevelOfExp(double exp)
        {
            int level = 1;
            double total = 0;
            foreach (var kv in Data.ExpCurve)
            {
                total += kv.Value;
                if (total <= exp) level = kv.Key;
            }
            return level;
        }
...
        long SpTotal(int level)
        {
            long total = 0;
            for (int lv = 1; lv <= level; lv++) total += Data.SpCurve.TryGetValue(lv, out var v) ? (long)v : 0;
            return total;
        }
```

---

### M11.11 Per-Kill EXP Level-Gap Scaling (`CBattle::_AddExp` `0x450710`, Vanilla `X01..X08` & Enchant `270`)

- **Verdict:** S1
- **Summary:** All 7 vanilla and Enchant `270` level-gap multiplier bands in `progression.py` (`LEVEL_GAP`) match `0x450734..0x45080d` 100%, and `int(...)` truncation matches `0x61e650` (verified in disassembly `0x61e650..0x61e7d1` as MSVC `__ftoui3` float-to-uint32 truncation toward zero — note M11.11 spec mislabeled `0x61e650` as `round_f32_to_i32`). However:
  - `M11.11a` (`S1`): `progression.py` (line 32) computes `int(exp * level_gap_factor(...))` in IEEE-754 `f64` rather than `f32` (`mulss` at `0x450815`), causing **151 exact off-by-1 divergences** across vanilla enemies (e.g., enemy 0 `exp=90 * 1.3f`: binary `116` vs Python `117`; enemy 5 `exp=440 * 1.15f`: binary `506` vs Python `505`).
  - `M11.11b` (`S2`): `catch_up_options.py` (line 82) constructs `gap` option tables with `with_enchant = max(values[k], vanilla_with_enchant)`, which cannot represent the `X06..X08` Balance Enchant-270 values (`1.5, 4.0, 6.0`) if `more_from_higher=True` is evaluated.

**Binary Evidence (`0x450734..0x450820`):**
```asm
00450734  sub      esi, eax
0045073e  movss    xmm0, dword ptr [0x6d937c]    ; float 0.9
00450750  movss    xmm0, dword ptr [0x6d9374]    ; float 0.85
00450768  push     0x10e
0045077d  movss    xmm0, dword ptr [0x6d939c]    ; float 1.15
004507ef  movss    xmm0, dword ptr [0x6d93c8]    ; float 1.75
00450815  mulss    xmm0, dword ptr [esp + 0x14]
0045081b  call     0x61e650
00450820  add      dword ptr [edi + 0xec], eax
```

**Code Evidence — `gamedata/progression.py:14`:**
```python
LEVEL_GAP = ((10, None, 0.85, 0.85), (5, 9, 0.90, 0.90), (0, 4, 1.00, 1.00), (-4, -1, 1.00, 1.15),
             (-9, -5, 1.10, 1.30), (-19, -10, 1.25, 1.50), (None, -20, 1.25, 1.75))
...
    banked = sum(int(exp * level_gap_factor(member_level, level, more_from_higher, gap_table)) for level, exp in enemies)
```

**Code Evidence — `tools/catch_up_options.py:81`:**
```python
        elif self.kind == 'gap':
            self.gap_table = tuple((low, high, values[k], max(values[k], with_enchant))
                                   for k, (low, high, _, with_enchant) in enumerate(progression.LEVEL_GAP))
```

---

### M11.12 Victory EXP Split & Multipliers (`CBattleResult::_Initialize` `0x445830`, Passive `218`, Status `157`, Enchant `275`)

- **Verdict:** S2
- **Summary:** `gamedata/progression.py:battle_exp` matches the exact division by `living`, additive Paean `218` bonus (`gained += gained * bonus`), Status `157` doubling (`*= 2.0`), and Enchant `275` doubling (`*= 2.0`).
- **Sub-bug:**
  - `M11.12a` (`S2`): `progression.py:33-39` performs all operations in `f64` and returns an un-truncated float without binary `f32` (`divss`/`mulss`/`addss`) rounding, `0x61e650` (`__ftoui3`) truncation of `startExp + exp`, or dead-member zeroing (`0x4443c5..0x4443cf`). *(Severity `S2`: analytical expected-EXP helper used in `catch_up_options.py`, not inside C# battle loops.)*

**Binary Evidence (`0x4459bf..0x445a29`, `0x4443cd..0x44442f`):**
```asm
004459bf  divss    xmm0, dword ptr [ebp - 0x18]
004459c7  mulss    xmm1, dword ptr [ebp - 0x2c]
004459cc  addss    xmm1, xmm0
004459ed  addss    xmm0, xmm1
00445a1e  addss    xmm1, xmm1
004443cd  test     al, al
004443cf  je       0x4444db
00444427  call     0x61e650
```

**Code Evidence — `gamedata/progression.py:33`:**
```python
    gained = banked / float(living)
    gained += gained * bonus
    if doubled:
        gained *= DOUBLE
    if double_exp_piece:
        gained *= DOUBLE
    return gained
```

---

### M11.13 Battle Gold & Enemy Drop Calculations (`0x43a9be..0x43ab08`, `0x558180`, `0x505ad0`)

- **Verdict:** MODEL-LIMIT
- **Summary:** `enemy_data.py` accurately parses `gold` (`+0x38`), `drops` (`+0x68`), `equipment_drop` (`+0x7c/+0x80`), and `equipment_slots` (`+0x84`, stride `0x0c`), and `engine_export.py`/`Loader.cs`/`Units.cs` carry `Gold`. Post-battle gold and item/equipment drop resolution (`428`, `271`, `67`, `270`, `68`, `276`, `0x558180`, `0x505ad0`) is out-of-combat economy/loot simulation outside the combat simulator's scope (confirmed in `variant.py` lines 135–142: "no battle of the simulator reads it").

**Binary Evidence (`0x43a9e3..0x43aa79`, `0x5581ff..0x55842c`):**
```asm
0043a9e3  push     0x43
0043aa0e  push     0x1ac
0043aa33  push     0x10f
0043aa38  call     0x4e4dd0
005581ff  push     0x10e
00558250  push     0x114
0055842c  call     0x505ad0
```

**Code Evidence — `tools/enemy_data.py:79`:**
```python
    enemy['drops'] = [(raw[1 + 2 * k], raw[2 + 2 * k]) for k in range(max(0, min(raw[0], 2))) if raw[1 + 2 * k] != -1]
    enemy['equipment_drop'] = (raw[5], raw[6])        # chance in percent, how many slots it is drawn among
    enemy['equipment_slots'] = [tuple(raw[7 + 3 * k:10 + 3 * k]) for k in range(max(0, min(raw[6], 3)))]
```

**Code Evidence — `gamedata/variant.py:138`:**
```python
                _check(row, enemy['raw_68'][9 + 3 * k])
                enemy['raw_68'][9 + 3 * k] = int(new)
                enemy['equipment_slots'][k] = enemy['equipment_slots'][k][:2] + (int(new),)
            elif field in ('equipment drop rate', 'steal rate'):
                continue
```

---

### M11.14 Motivation / Pep System (`0x4f5410`, `0x4f5440`, `0x4f69e0`, `[70..130]`)

- **Verdict:** S1
- **Summary:** `Units.cs:ClampPep` matches `[70.0, 130.0]` clamp and Enchant `201 -> 70`, `200 -> max(100, Pep)`, `195 -> 130` precedence (`0x4f69e0..0x4f6a60`). `Battle.cs:2017-2019` matches Positive Trance (`440`) vanilla threshold `100` and intentional `X17` Balance patch (`85`, via `variant.py:271-276`, `engine_export.py:341`, `Loader.cs:307`), where `0x44ccce` reuses `xmm1` in both `comiss` and `subss`. However:
  - `M11.14a` (`S1`): Per-character battle motivation deltas (`PlayerStatusData.bin +0x3c`, read in `character_data.py:67`) are dropped by `engine_export.py:136-137` and never applied in `Battle.cs` on enemy kill (`idx 0`, `0x43abd1`), player KO (`idx 1`, `0x43a6b9`), critical hits (`idx 2/3`), or per-hit combat actions (`idx 5`, `0x4234ef`). Alisia's Pep therefore stays frozen at `100.0` (e.g., never earning `+0.5` per kill, `+1.5` per crit, or `-1.0` per hit), directly distorting Positive Trance (`440`) damage in vanilla and `X17` Balance runs!
  - `M11.14b` (`S2`): `Units.cs:ClampPep` omits highest-priority Command `81` (`0x51`, Pep Freeze from `Miracle Shake`, `0x4f6a6e`), `Recipe.cs:166` sets `tested.Pep` without clamping, and `Battle.cs:2018` reads `actor.Pep` without calling `ClampPep` (`0x4f5440`).

**Binary Evidence (`0x4f5440..0x4f5448`, `0x4f69e0..0x4f6a6e`, `0x44ccc9..0x44cd13`):**
```asm
004f5443  call     0x4f69e0
004f5448  movss    xmm0, dword ptr [esi + 0xd8]
004f69e0  movss    xmm1, dword ptr [0x6d950c]    ; float 70
004f69e8  movss    xmm0, dword ptr [0x6d956c]    ; float 130
004f69f3  push     0xc9
004f6a26  push     0xc8
004f6a51  push     0xc3
004f6a6e  push     0x51
0044ccc9  call     0x4f5440
0044ccce  movss    xmm1, dword ptr [0x6d9540]    ; float 100
0044ccde  subss    xmm0, xmm1
0044cd13  cvttss2si eax, xmm0
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:190`:**
```csharp
        public void ClampPep()
        {
            Pep = F.Clamp(Pep, 70.0, 130.0);
            if (!HasEnchants) return;
            if (Pieces(201) != 0) Pep = 70.0;
            if (Pieces(200) != 0 && Pep < 100.0) Pep = 100.0;
            if (Pieces(195) != 0) Pep = 130.0;
        }
```

**Code Evidence — `engine_cs/src/DtEngine/Battle.cs:2017`:**
```csharp
                int ptThresh = Options.PositiveTranceThreshold ?? Data.PositiveTranceThreshold;
                if (!action.Magic && actor.HasUnique && actor.UniqueEffect == 440 && actor.Pep > ptThresh)
                    amount += PyMath.Int(amount * (actor.Pep - ptThresh) / Math.Max(1.0, actor.UniqueValue) / 100.0);
```

**Code Evidence — `gamedata/variant.py:271`:**
```python
def positive_trance_threshold():
    import exe_patch
    row = next((p for p in exe_patch.patches('balance') if p['id'] == 'X17'), None)
    return int(round(row['float_after'])) if row and row['float_after'] is not None else 100
```

---

### M11.15 Battle-Entry Enemy Construction from `Enemy.pck` (`0x4f05d0`, `0x4f25f0`, `0x4f2820`, `0x4f1fc0`, `0x4f2150`)

- **Verdict:** S2
- **Summary:** `enemy_data.py`, `engine_export.py`, `Loader.cs`, and `Units.cs:BuildEnemy` read all 516 `Enemy.pck` entries verbatim with zero dynamic scaling (level, HP, 6 stats, 8 resistances, direct-float `weight` at `+0x44`, `exp`, `gold`, `flags`, and up to 5 innate passive IDs at `+0xf0/+0xf4`), and all 31 effect IDs present on vanilla enemy innate passives are read via `Has()`/`Value()`/`HasPassive()` in `Battle.cs`.
- **Sub-bug:**
  - `M11.15a` (`S2`): Binary `CGameEnemyStatus::ctor` (`0x4f079c..0x4f07b0`) installs innate passives via `AddStatus` (`0x4f1fc0`) and calls `Recalculate` -> `ClampParameter` (`MaxHp >= 1`, `MaxTp = 1` while `CurTp = 0`, `CurHp = MaxHp` post-status). `Units.cs:BuildEnemy` sets `MaxTp = 0`, stores innate passives in `Pv` (not `St`), and skips post-init `Recalculate`/`Clamp`. Notably, `Units.cs:429` (`TpRatio => MaxTp != 0 ? (double)Tp / MaxTp : 1.0`) returns `1.0` (`100%`) instead of `0.0` (`0%`) for enemies with `MaxTp = 0, Tp = 0`! *(Severity `S2`: 0 vanilla enemies have stat/MaxHP-modifying innate passives or `Hp <= 0`, and enemy `TpRatio` is only read by rare AI source `4`.)*

**Binary Evidence (`0x4f0794..0x4f07b0`, `0x4f2621..0x4f2840`, `0x4f2172`):**
```asm
004f079c  call     dword ptr [eax + 0x58]
004f07a3  call     dword ptr [eax + 0x108]
004f07a9  mov      eax, dword ptr [edi + 0x10]
004f07b0  mov      dword ptr [edi + 0xc], eax
004f2825  call     dword ptr [eax + 0x104]
004f2835  call     dword ptr [eax + 0x10c]
004f2840  jmp      dword ptr [eax + 0x110]
004f2172  fld      dword ptr [eax + 0x5c]
```

**Code Evidence — `engine_cs/src/DtEngine/Units.cs:429`:**
```csharp
        public double TpRatio => MaxTp != 0 ? (double)Tp / MaxTp : 1.0;
...
        public static Unit BuildEnemy(GameData data, int enemyId, bool front, string name = null)
        {
            var e = data.Enemies[enemyId];
            var unit = new Unit(name ?? e.Name, Unit.ENEMIES, e.Level, e.Hp, 0, e.Stats, e.Resist, e.Weight, e.Swing, e.Race, Kind.Enemy);
...
            foreach (int attackId in e.Passives)
            {
                var attack = data.GetAttack(attackId);
                if (attack != null)
                    for (int k = 0; k < attack.EffId.Length; k++) unit.SetPassive(attack.EffId[k], attack.EffValue[k], attack.EffIsInt[k]);
            }
```

---

## Part B — Mechanical Reverse Sweep (`Code -> Spec`, `ENGINE-ONLY` Findings)

### Reverse Sweep Coverage Summary

Mechanically scanned **9 C# engine files** (`Battle.cs`, `Units.cs`, `Formulas.cs`, `Action.cs`, `Ai.cs`, `Loader.cs`, `Policy.cs`, `Scenario.cs`, `Recipe.cs`) and **19 Python files** (`gamedata/*.py`, `tools/*_data.py`, `tools/engine_export.py`, plus `tools/enemy_ai.py`) against `docs/binary_spec/00_INVENTORY.json` (Routes a–e, vtable flag groups, `pck_usage`) and `docs/binary_spec/M00..M11.md`:

| Category Scanned | Distinct Literals / Tables | Binary-Backed | `ENGINE-ONLY` / Unbacked | Notes |
|---|---:|---:|---:|---|
| Effect / Status / Passive IDs (`Battle/Units/Action/Policy`) | 251 | 251 | 0 *(IDs)* | Every effect ID literal exists in Route (a)/(b)/(c); `DispelAlways`/`DispelIfRaised`/`AlwaysBuffStatus`/`SignedBuffDebuff` match `route_a_vtable_flag_groups` with 0 diff. |
| Enchant IDs (`Formulas/Battle/Units/Scenario/progression`) | 239 | 239 | 0 *(IDs)* | All 234 C# + 5 Python encounter/recovery enchant IDs backed by Route (c), `M09`, and `M11.08`. *(See `ENGINE-ONLY-05` for `ONE_PER_PIECE` forging rule on IDs `6..21`.)* |
| Item Effect Type IDs (`Battle.UseItem`, `Policy`, `item_effect_data.py`) | 57 | 57 | 0 | `0..8` (`UseItem`), 39 `SKILL_ITEMS_FALLBACK`, 15 `MEAL_BUFFS_FALLBACK`, 3 `MAX_LEVEL_TYPES` all match Route (e) (`0..106`). |
| AI Opcodes / Sources / Targets (`Ai.cs`, `tools/enemy_ai.py`) | 43 | 43 | 0 | Opcodes `0..14`, sources `0..11`, target overrides `0..15` all backed by `M10` (`0x432fa0`, `0x434754`). |
| Enemy Sub-Race / Race / Doll / Random-Move Tables (`Formulas/Battle/tools`) | 109 | 108 | 1 | `FELINES` (23/23), `SEA_CREATURES` (25/25), `RACE_GUARD`/`RACE_ATTACK` (9/9), `EnemyDollActions` (34/34), `DOLLS` (7/7), `TABLES` (4/4), `DEMON_WALL_RACES` (3/3) backed; **`MURDER_LICENSE_ATTACK = 413`** unbacked (`ENGINE-ONLY-01`). |
| Combat Branches, `BattleOptions` & Magic Constants (`Battle/Scenario/Formulas`) | 68 | 63 | 5 | `ENGINE-ONLY-02` (`446` proxy), `ENGINE-ONLY-03` (`DollCureTargets`), `ENGINE-ONLY-04` (`HalveEnemies`), `ENGINE-ONLY-05` (`ONE_PER_PIECE`), and `ENGINE-ONLY-06` (`SurvivalGuard` `L46` intentional inactive trial hook). *(Note: `MaxTime = 400.0` is an expected simulation infinite-loop timeout guard, and `X01..X17` are documented Balance mod patches.)* |

---

### ENGINE-ONLY-01 `Battle.cs` Substitutes `EnemyAttackData` `413` ("Head Shot") for Murder License (`319`) `CActionPatternE1580`

- **Verdict:** ENGINE-ONLY
- **Why Unbacked:** In the vanilla binary (`M08.11`, `CActionPatternE1580::_Task`, `0x42c180..0x42c56e`), Murder License (`319` / `0x13f`) directly constructs and executes `CCommand(id=119, val=1.0f)` (100% Instakill with NO physical damage and NO hit roll). `Battle.cs:93, 924-930` instead hardcodes `MURDER_LICENSE_ATTACK = 413` (`EnemyAttackData 413` "Head Shot": physical `power=0.35`, `acc=-0.15`, `effects=[(0,4,1), (119,4,0.5)]`), an attack ID with zero binary link to Murder License (`319`).
- **Recommended Disposition:** **Fix / Replace** — delete `MURDER_LICENSE_ATTACK = 413` and execute direct `CCommand_0119(val=1.0f)` per `M08.11` (`0x42c180`).

**Binary Evidence (`0x43736a`):**
```asm
0043736a  push     0x13f
```

**Code Evidence — `engine_cs/src/DtEngine/Battle.cs:93`:**
```csharp
        const int MURDER = 258, DARK_QUEST = 263, KNOCK_DOWN = 305, PRETEND = 310, MURDER_LICENSE = 319, MURDER_LICENSE_ATTACK = 413, DEMON_WALL = 356, ENEMIES_FLEE = 432, ESCAPE_SELF = 11;
...
            if (unit.Alive && unit.Has(MURDER_LICENSE))
            {
                var mlAtk = Data.GetAttack(MURDER_LICENSE_ATTACK);
                var foes = TargetableArray(1 - unit.Side);
                if (mlAtk != null && foes.Length > 0)
                    Perform(new Action(unit, AKind.Enemy, mlAtk, 1) { Target = foes[Rng.ChoiceIndex(foes.Length)] });
            }
```

---

### ENGINE-ONLY-02 `Battle.cs` Invented Overstock Clearance (`446`) Bag-Consuming `HpRatio < 0.6` Heal/TP Proxy

- **Verdict:** ENGINE-ONLY
- **Why Unbacked:** In the vanilla binary (`M08.11`, `CActionPatternU0008::_Task`, `0x42fb60..0x4302cf`), Overstock Clearance (`446` / `0x1be`) rolls `GlobalRng.Rand(105)` over a 6-item weighted table (`[20, 20, 20, 15, 15, 15]`) and runs `CItemResult` on a **free** spawned item without checking or consuming party inventory. `Battle.cs:934-940` invents an `HpRatio < 0.6` threshold and calls `Policy.ActItem(this, unit, hurt ? "heal" : "tp", null)` -> `UseItem(item)`, which requires `unit.Items.Count > 0` and consumes real bag items.
- **Recommended Disposition:** **Remove & Replace** — delete the `HpRatio < 0.6` / `Policy.ActItem` / inventory-consuming proxy and implement `CActionPatternU0008` (`M08.11`, `0x42fb60`).

**Code Evidence — `engine_cs/src/DtEngine/Battle.cs:934`:**
```csharp
            if (effect == 446 && unit.Items.Count > 0 && Roll(value) && ChooseMember != null)
            {
                bool hurt = false;
                foreach (var m in AlliesArray(unit)) if (m.Kind == Kind.Member && m.HpRatio < 0.6) { hurt = true; break; }
                var item = Policy.ActItem(this, unit, hurt ? "heal" : "tp", null);
                if (item != null) UseItem(item);
            }
```

---

### ENGINE-ONLY-03 `Options.DollCureTargets` Invented Perdurabo (`235`) Ailment-Sort Target Cap

- **Verdict:** ENGINE-ONLY
- **Why Unbacked:** Nowhere in the vanilla binary (`0x4388ea..0x438a65`, `0x4fd980`, `0x43f450`, `0x48a430`) does Perdurabo (`Skill 105`, `TargetCode 10`, `CCommand_0235`) sort party members by descending ailment count and cap cured targets at `Options.DollCureTargets` (default `2`, or `ailing.Count + DollCureTargets` when negative). Both the sorting/slicing loop (`Battle.cs:3437-3452`) and the `Options.DollCureTargets` / `sim_setup.xlsx` `doll_cure_targets` knob are entirely invented.
- **Recommended Disposition:** **Remove** `Options.DollCureTargets` and replace with exact binary target resolution for Skill `105` / `CCommand_0235` (`0x43f450`, `0x48a430`).

**Code Evidence — `engine_cs/src/DtEngine/Battle.cs:13`:**
```csharp
        public int DollCureTargets = 2;
...
            else if (members.Count > 0 && action.TargetCode == T.NO_TARGET && action.Has(235))
            {
                var ailing = new List<Unit>(members);
                for (int i = 1; i < ailing.Count; i++)
                {
                    var x = ailing[i];
                    int cx = CountAilments(x);
                    int j = i - 1;
                    while (j >= 0 && CountAilments(ailing[j]) < cx) { ailing[j + 1] = ailing[j]; j--; }
                    ailing[j + 1] = x;
                }
                int take = Math.Min(Options.DollCureTargets, ailing.Count);
                if (take < 0) take = Math.Max(0, ailing.Count + Options.DollCureTargets);
                action.FixedTargets = ailing.GetRange(0, take).ToArray();
            }
```

**Code Evidence — `engine_cs/src/DtEngine/Scenario.cs:84`:**
```csharp
            o.DollCureTargets = Has("doll_cure_targets") ? Setup.ToInt(Get("doll_cure_targets")) : 2;
```

---

### ENGINE-ONLY-04 `Options.HalveEnemies` Global Toggle Replacing Per-Enemy `flagA5` (`pctHpSusceptible_0xa5`)

- **Verdict:** ENGINE-ONLY
- **Why Unbacked:** In the vanilla binary (`M02.05`, `_CalcSpecialDamage` `0x44f989`), BOTH Effect `140` (`Halve HP`) and Effect `141` (`3/4 HP`) are gated on a per-enemy encounter flag `status2_0x14.pctHpSusceptible_0xa5` (passed as `flagA5` to `CGameEnemyStatus::ctor` `0x4f05d0`). `Battle.cs:12, 2462` and `Scenario.cs:83` replace this per-enemy binary flag with a global boolean toggle `Options.HalveEnemies = true` (affecting only `140` while leaving `141` completely ungated).
- **Recommended Disposition:** **Remove** `Options.HalveEnemies` and gate both `140` and `141` on the decoded per-enemy `flagA5` (`pctHpSusceptible_0xa5`) bit.

**Code Evidence — `engine_cs/src/DtEngine/Battle.cs:12`:**
```csharp
        public bool HalveEnemies = true;
...
            if (action.Has(140)) return target.Side == Unit.PARTY || Options.HalveEnemies ? target.Hp / 2 : 0;
            if (action.Has(141)) return target.Hp * 3 / 4;
```

**Code Evidence — `engine_cs/src/DtEngine/Scenario.cs:83`:**
```csharp
            o.HalveEnemies = Has("halve_enemies") ? Setup.Truthy(Get("halve_enemies")) : true;
```

---

### ENGINE-ONLY-05 `Scenario.cs` `ONE_PER_PIECE` (`{ 6, 9, 12, 15, 18, 21 }`) Simulator-Only Forge Restriction

- **Verdict:** ENGINE-ONLY
- **Why Unbacked:** In `EnchantData.pck`, Enchants `6, 9, 12, 15, 18, 21` (`ATK/DEF/INT/RES/DEX/AGI UP`) all have bit 0 (`stacks`) set, and `CGamePlayerStatusBase::_SetupEnchant` (`0x4f62c0`) enforces no per-piece uniqueness limit on them. `Scenario.cs:41, 306` hardcodes `ONE_PER_PIECE` inside `ForgeEnchants` as a simulator build-model heuristic.
- **Recommended Disposition:** **Document** explicitly as a `Scenario.cs` build-model assumption (or move the constraint into `sim_setup.xlsx` `EnchantPlan`), not a binary engine rule.

**Code Evidence — `engine_cs/src/DtEngine/Scenario.cs:41`:**
```csharp
        static readonly int[] ONE_PER_PIECE = { 6, 9, 12, 15, 18, 21 };
...
                           && !(piece.Has.Contains(eid) && Array.IndexOf(ONE_PER_PIECE, eid) >= 0))
```

---

### ENGINE-ONLY-06 `Options.SurvivalGuard` (`L46`) — Confirmed Intentional Inactive Trial Hook

- **Verdict:** ENGINE-ONLY
- **Why Unbacked (Confirmed Intentional Inactive Trial Hook):** Modifies Endure (`254`) fatality detection from `amount >= target.Hp` to `target.Hp > 1 && amount >= target.Hp - 1` (`Battle.cs:2540`). Has zero backing in the vanilla binary and zero rows in `balance_criteria.xlsx` `ExePatches` (`Data.SurvivalGuard` is `false` in both vanilla and Balance exports). Explicitly classified in Roadmap Section 2 as a **confirmed intentional inactive trial hook (`L46`)**.
- **Recommended Disposition:** **Document / Retain Inactive** — keep `SurvivalGuard = false` by default for vanilla and Balance parity, or remove once trial `L46` is retired.

**Code Evidence — `engine_cs/src/DtEngine/Battle.cs:2540`:**
```csharp
            if (Options.SurvivalGuard ?? Data.SurvivalGuard) fatal = target.Hp > 1 && amount >= target.Hp - 1;
            else fatal = amount >= target.Hp;
```

**Code Evidence — `gamedata/variant.py:238`:**
```python
    out.survival_guard = lever_patched('L46')
```

**Code Evidence — `tools/engine_export.py:339`:**
```python
            'survival_guard': bool(getattr(data, 'survival_guard', False)),
```

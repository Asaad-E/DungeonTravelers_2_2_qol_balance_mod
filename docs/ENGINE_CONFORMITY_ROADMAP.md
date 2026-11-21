# Clean-Room Binary Conformity Roadmap (`engine_cs` + `extract_vanilla` + `gamedata`)

> **PURPOSE:** Achieve full, mechanically verified binary fidelity between the combat simulator pipeline (`backups/*.pck -> tools/extract_vanilla.py -> data_tables/vanilla_source_of_truth.xlsx -> gamedata/ -> tools/engine_export.py -> engine_cs/src/DtEngine/`) and the clean vanilla executable (`backups/exe/DT22_en_unwrapped.vanilla.exe`, pinned by SHA-256) using a **Binary-First Clean-Room Specification**, **Global Two-Way Diff & Architectural Triage**, **Machine-Checked Evidence**, **Automated Binary-Table Invariants**, and a **5-Stratum Independent Random Audit with Canary & Circuit Breaker**.
>
> **WHY THIS EXISTS:** Auditing from `C# -> Exe` is structurally blind to mechanics present in the executable that the simulator never implemented (e.g., extra-turn turn-start skipping at `0x4365ff`, Geass performance group `0x43cb80`, `AddStatus` exclusive vtable groups `0x7c`/`0x84`, Magic effect `47`). This campaign reverses the direction strictly to `Exe -> Clean-Room Spec -> Two-Way Global Diff -> Fix -> Hardened Random Acceptance Sampling`.

---

## 0. Mandatory Resumption Protocol (Context-Loss Shield)

**READ THIS ENTIRE SECTION FIRST after any context compaction, restart, or new session.**

1. **Check machine truth first:** Once Phase 0 creates `docs/binary_spec/STATE.json` and `docs/binary_spec/DIFF_TABLE.json`, run `python tools/conformity_status.py` to regenerate Section 1 counts rather than editing counters by hand. Until then, read Section 1 and Section 4 below. Never rely on conversation memory.
2. **Verify repository state:** run `git status --short` and `git log -3 --oneline`.
3. **Single-writer discipline:** Only the **coordinator** edits this roadmap, `STATE.json`, and `DIFF_TABLE.json`. Workers write only their assigned module/claim output files.
4. **Pin the clean vanilla executable by SHA-256 (NEVER rely on `exe_reader.reading_path()` defaults):**
   - `exe_reader.reading_path()` gives `config.json` (`formula_exe`) priority over the vanilla backup, and an installed game `.exe` may carry Balance mod patches (`X01..X17`).
   - **Every Phase 0–4 script MUST open `backups/exe/DT22_en_unwrapped.vanilla.exe` explicitly and assert:**
     - **SHA-256:** `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60` (matches `backups/exe/DT22_en_unwrapped.vanilla.exe.sha256`, 3,247,104 bytes).
   - **Vanilla `.pck` backups:** `backups/`
   - **Existing disassembly tools:** `tools/exe_dis.py`, `tools/exe_who_calls.py`, `tools/exe_find_const.py`, `tools/exe_around.py`, `tools/exe_effects.py`, `tools/exe_enchants.py`, `tools/exe_digest.py`. *(When extending/calling them in Phases 0–4, pin the vanilla exe by SHA-256 and redirect ALL outputs to `docs/binary_spec/` — NEVER write into frozen `docs/generated/`!)*
5. **Obey Phase Quarantine & Freeze Rules strictly:**
   - **Phase 0 & Phase 1 Quarantine (enforced by explicit sandboxed file list in worker briefs):** Clean-room writers are **FORBIDDEN** from reading:
     - `engine_cs/`
     - `docs/FORMULAS.md`
     - `docs/ENGINE_AUDIT.md` (quotes C#)
     - `data_tables/engine_conformity.json`
     - `docs/generated/EFFECT_*`
     - `data_tables/balance_criteria.xlsx` (`EffectRules` sheet)
     - `RESULTADOS_REGLAS_COMBATE.md` (if present)
     - Any labels/notes derived from `FORMULAS.md` MUST be stripped from raw disassembly/digest outputs before Phase 1 writers see them.
   - **Phase 2 Read-Only Rule:** Diff auditors compare `docs/binary_spec/M00..M11.md` + `00_INVENTORY.json` against the real code pipeline (`tools/extract_vanilla.py`, `gamedata/`, `tools/engine_export.py`, `engine_cs/src/DtEngine/`). Existing `docs/ENGINE_AUDIT.md` P-items and `BinaryConformityTests.cs` are treated as **unverified claims to re-check**, NOT as ground truth. **NO code edits during Phase 2.**
   - **Phases 0–4 Balance Freeze:** **FREEZE** `data_tables/balance_changes.xlsx`, `docs/generated/*`, `measures/*`, and `tools/full_suite.py` until Phase 4 certifies the engine. *(A small, fast smoke battery writing only to stdout/scratch is permitted during Phase 3 to catch crashes or extreme swings without touching tracked reports.)*
6. **Commit & local pointer hygiene:** Commit this roadmap before starting Phase 0, and add a 1-line pointer to `docs/ENGINE_CONFORMITY_ROADMAP.md` in local `CLAUDE.md` so fresh sessions always discover it immediately. Record the commit hash in every Section 4 handoff row.

---

## 1. Live Campaign Dashboard

*(Once `tools/conformity_status.py` exists, this section is regenerated mechanically from `docs/binary_spec/STATE.json` and `docs/binary_spec/DIFF_TABLE.json`.)*

- **Campaign Status:** `NOT STARTED — READY FOR PHASE 0`
- **Active Phase:** `Phase 0 — Mechanical Binary Inventory`
- **Last Updated:** `2026-11-21`
- **Baseline Commit:** `ae68713` (`219/219` Python tests PASS, `61/61` C# tests PASS)
- **Active Blocker:** `None`

### In-Progress Claims

| Module / Task | Owner | Started Commit | Output Path | Status |
|---|---|---|---|---|
| *(none)* | — | — | — | — |

### Phase Gate Tracker

| Phase | Name | Status | Primary Artifacts | Exit Gate | Sign-off Commit |
|---|---|---|---|---|---|
| **0** | Mechanical Binary Inventory | `[ ] pending` | `tools/exe_inventory.py`, `docs/binary_spec/00_INVENTORY.json`, `docs/binary_spec/00_INVENTORY.md`, `docs/binary_spec/STATE.json`, `tools/conformity_status.py` | SHA-256 pinned; all 3 effect routes, `Battle::*` denominator, RTTI vtables, all battle jump tables, `.rdata` tables, `.pck` usage, `X01..X17` byte diff, and stratified `audit_catalog` generated cleanly | — |
| **1** | Clean-Room Binary Spec (`Exe` only) | `[ ] pending` | `docs/binary_spec/M00_PIPELINE.md`, `docs/binary_spec/M01..M11.md`, generalized `tools/audit_check.py` | `M00` + `M01..M11` complete with typed pseudocode, `Calls`/`CalledBy`, ~40 KB/module budget, 100% inventory coverage, **0 unverified quotes** via `audit_check.py` | — |
| **2** | Two-Way Global Diff & Triage | `[ ] pending` | `docs/binary_spec/DIFF_REPORT.md`, `docs/binary_spec/DIFF_TABLE.json` | Forward diff (`Spec -> Code`) + Reverse sweep (`Code literals -> Spec / ENGINE-ONLY`); `audit_check.py` passes on all verdicts; global `S0` review signed off | — |
| **3** | Fixes, Tests & Binary Invariants | `[ ] pending` | `engine_cs/`, `gamedata/`, `tools/extract_vanilla.py`, `BinaryConformityTests.cs`, `tests/test_binary_invariants.py` | 0 open `S0/S1/S2`; `Legal()` predicate + `Battle` assert mode passing; `.pck`-direct invariant & exe-table invariants PASS; `CalibrationTests` intact; `X01..X17` vanilla/variant pairs PASS | — |
| **4** | 5-Stratum Independent Random Audit | `[ ] pending` | `tools/sample_audit_batch.py`, `docs/binary_spec/RANDOM_AUDIT_LOG.md` | 1 full round of **15** items (4 catalog strata + 3 `Trace.cs` out-of-catalog events) + detected **canary** with **0 verified fails** AND cumulative `<= 1` S2 | — |
| **5** | Final Balance Recalibration & Release | `[ ] pending` | `docs/generated/*`, `measures/*`, `dist/*.zip`, `docs/FORMULAS.md`, `data_tables/engine_conformity.json` | `full_suite.py` + batteries + `package_all.py` + all tests green; working artifacts cleanly archived | — |

### Phase 1–3 Module Progress Matrix (`M00`–`M11`)

| ID | Module | Spec File (`docs/binary_spec/`) | Phase 1 (Spec + `audit_check`) | Phase 2 (2-Way Diff) | Open `S0 / S1 / S2` | Phase 3 (Fixed + Tested) |
|---|---|---|---|---|---|---|
| `M00` | Global Action & Turn Call-Graph Pipeline *(FIRST)* | `M00_PIPELINE.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M01` | Turn Loop, State Table (`0x439820`), ATB & Extra Turns | `M01_TURN_LOOP_AND_ATB.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M02` | Physical Damage, Range, Crit, Multi-Hit & Zones | `M02_PHYSICAL_DAMAGE.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M03` | Magical Damage, Elements & Missed Spells | `M03_MAGICAL_DAMAGE.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M04` | Hit / Evasion, Targeting Scopes & Formation | `M04_HIT_EVASION_AND_TARGETING.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M05` | Healing, Recovery, After-Battle & Items | `M05_HEALING_RECOVERY_AND_ITEMS.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M06` | Status Lifecycle, Vtable Groups, Recalc & Dispel | `M06_STATUS_LIFECYCLE_AND_RECALC.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M07` | Ailments, Immunities, Barriers & Recovery | `M07_AILMENTS_AND_CONTROL.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M08` | Procs, Counters, Cover, Parry & AfterHit | `M08_PROCS_COUNTERS_AND_AFTERHIT.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M09` | Dolls, Summons, Guests & Enchantments | `M09_DOLLS_SUMMONS_NPCS_AND_ENCHANTS.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M10` | Enemy/NPC AI VM, `Script/Battle.pck` & Loaders | `M10_ENEMY_AI_AND_DATA_LOADERS.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |
| `M11` | Unit Build, Growth, Unarmed Rank, Party/Join & EXP/SP | `M11_UNIT_BUILD_AND_STATS.md` | `[ ]` | `[ ]` | `- / - / -` | `[ ]` |

### Phase 4 Random Audit Circuit-Breaker Tracker

- **Consecutive Failed Rounds:** `0 / 3`
- **Immediate Trip Triggers:** ANY verified `S0`, OR `>= 2` verified fails sharing a root-cause class, OR `3` consecutive failed rounds → **HARD STOP & Drawing Board `POST_MORTEM.md`**.
- **Items Audited Without Replacement:** `0` | **Cumulative S2 Across All Rounds:** `0` *(must stay `<= 1` to certify)*

| Round | Date | Seed | Canary Planted / Caught? | Items (12 catalog + 3 Trace = 15) | Verified Fails (`S0/S1/undoc S2`) | Verdict |
|---|---|---|---|---|---|---|
| 1 | — | — | — | — | — | `[ ] pending` |
| 2 *(if needed)* | — | — | — | — | — | `[ ] standby` |
| 3 *(if needed)* | — | — | — | — | — | `[ ] standby` |

---

## 2. Frozen Scope Boundary & Real Code Pipeline

### Real Code Pipeline Under Audit (Exact Files)
1. **Binary Extraction:** `backups/*.pck` → `tools/extract_vanilla.py` → `data_tables/vanilla_source_of_truth.xlsx`
2. **Data Assembly & Export:** `gamedata/data.py` (including `balance_criteria.xlsx` `EffectRules` and `data_tables/sim_setup.xlsx`), `gamedata/levels.py`, `gamedata/progression.py` → `tools/engine_export.py` → `build/engine_snapshot.json`
3. **C# Simulator:** `engine_cs/src/DtEngine/` (`Loader.cs`, `Data.cs`, `Scenario.cs`, `Recipe.cs`, `Units.cs`, `Action.cs`, `Formulas.cs`, `Battle.cs`, `Ai.cs`, `Trace.cs`, and legality rules called by `Policy.cs`)

### IN SCOPE (Must Match Vanilla Binary Faithfully)
- Every combat calculation, branching rule, clamp, rounding (`f32` vs `f64`, `trunc0` vs `floor`), cap, floor, `<` vs `<=` roll bound, RNG call count, and execution order inside battles and battle-rows.
- Unit construction: class/level growth (`ClassLevelData`), `LvExpSkptData`, unarmed weapon ranks (`ClassData+0x24` / `0x4f5585`), equipment & `%` modifiers, caps, Join/PartySkill data, EXP/SP curves (`gamedata/levels.py`, `progression.py`).
- All three effect dispatch routes: `CCommand` factory, inline `FINDERS` lookups, and pushed passive/enchant lookups.
- Enemy/NPC AI script VM (`EnemyAIData`/`NPCAIData`: sources `0x432fa0`, targets `0x434754`, opcodes, once/switch flags, target overrides, breath `3` bypass) and `Script/Battle.pck` scripted-battle triggers.
- Intentional mod patches `X01..X17` (must match vanilla when vanilla options are active and match the patched exe bytes when variant options are active).
- **Action legality rules used by `Policy.cs`:** centralized behind a single engine predicate `Legal(unit, action, targets)` with an assert mode in `Battle` that rejects any illegal action submitted by `Policy`.

### OUT OF SCOPE (Documented Non-Simulated Systems)
- Graphics, animations, audio/voices, camera, UI layout, menu navigation, save/load serialization, dungeon tile/event scripts outside combat, and dialogue.
- CRT/hardware RNG algorithm identity (we verify roll thresholds, bounds, distributions, and call counts — not MSVC `rand()` bit parity).
- Player-party heuristic preferences inside `Policy.cs` (which legal action an optimal player *prefers*), once legality itself is enforced by `Battle.Legal(...)`.

---

## 3. Detailed Phase Playbook

### Phase 0 — Mechanical Binary Inventory *(No C# Reading)*

**Goal:** Build a complete, mechanically derived denominator of the game's combat binary by **extending existing tools** (`tools/exe_effects.py`, `tools/exe_enchants.py`, `tools/exe_digest.py`), pinning the vanilla `.exe` by SHA-256, and writing ONLY to `docs/binary_spec/` (never into `docs/generated/`).

**Deliverables:**
1. `tools/exe_inventory.py` — asserts SHA-256 `785b0257...8f60` on `backups/exe/DT22_en_unwrapped.vanilla.exe` and writes `docs/binary_spec/00_INVENTORY.json` + `docs/binary_spec/00_INVENTORY.md`, capturing:
   - **Mechanical Denominator:**
     - All `Battle::*` qualified names (~730 assert/RTTI strings) + RTTI vtables, each explicitly classified `in_scope` or `out_of_scope` (no uncounted functions).
     - All battle-code jump tables (`jmp [reg*4 + table]` paired with their `cmp reg, N` bound): `CBattleBase::Update` state table (`0x439820` — bound read directly from the `cmp`, never assumed `0..23`), AI sources (`0x432fa0`), AI targets (`0x434754`), target scopes (`0x43fde8`, `0x43fdf4`, `0x43fe04`), `0x4b36cc`, and any others discovered in combat code.
   - **All 3 Effect & Passive Dispatch Routes:**
     - **Route (a) `CCommand` factory (`0x47b220`):** jump table IDs `9..0x1C1` (`0x47de14`/`0x47e0a4`) PLUS all out-of-range IDs explicitly handled before/after the table, with each class vtable VA, every boolean/constant vtable slot (`+0x54`, `+0x5c`, `+0x64`, `+0x68`, `+0x6c`, `+0x70`, `+0x74`, `+0x78`, `+0x7c`, `+0x84`, `+0x8c`, etc.), and `Execute`/`Tick`/`OnAdd`/`OnRemove` VAs.
     - **Route (b) Inline effect lookups:** every call site of `FINDERS` (`0x47e340`, `0x47e290`, `0x47e390`, `0x47e400`, `0x48cbf0`, `0x48c680`, `0x557620`, `0x56ce70`) and `push N; call [vt+0x48]`.
     - **Route (c) Pushed passive & enchant lookups:** every call site of party passive finder `0x4e4dd0`, unit passive finder `0x4fab50`, and enchant slot `0xf0` (via `exe_enchants.py`).
   - **Static Data Tables & Systems:**
     - `.rdata` float/int tables cross-referenced by battle functions (row, element, weapon-rank, multi-hit, random-move, and `EffectSequence` tables).
     - Zone factor (`0x44fbb0`), Unit Build & Stat Calc (`ClassLevelData`, `LvExpSkpt`, `ClassData+0x24`/`0x4f5585`), Join/PartySkill tables, `Script/Battle.pck` triggers, EXP/SP curves.
   - **`.pck` Usage Cross-Reference (`pck_usage`):** every Effect ID, Enchant ID, Enemy `0x3C` bit, AI opcode, and Passive ID actually referenced in `backups/*.pck`, with occurrence counts (used to define `S1` vs `S2` reach mechanically).
   - **`X01..X17` Patch Inventory:** byte diff between vanilla `.exe` and an in-memory/temp `tools/exe_patch.py`-patched image → exact patched VAs mapped to modules/Rule IDs.
   - **Stratified `audit_catalog`:** atomic testable items falling out naturally from the mechanical denominator (no artificial target count), partitioned across the 4 catalog strata (`core_combat`, `status_procs`, `effects_passives`, `units_ai_loaders`).
2. `docs/binary_spec/STATE.json` + `tools/conformity_status.py` — machine source of truth for dashboard progress.

**Exit Gate:** SHA-256 verified; 0 unparsed `.pck` effect/enchant/AI IDs; 100% of `Battle::*` functions and jump tables classified; raw outputs contain **zero** labels copied from `FORMULAS.md` or `EffectRules`.

---

### Phase 1 — Clean-Room Binary Specification (`Exe` → Spec Only)

**Goal:** Specify every in-scope mechanic directly from the vanilla binary with machine-verified disassembly quotes.

**Ordering & Execution Rules:**
1. **`M00_PIPELINE.md` FIRST (before `M01..M11`):** One fresh quarantined writer maps the complete end-to-end ordered call graph:
   `battle_start -> select_actor -> turn_start_states -> action_select -> legality -> target_resolve -> hit -> crit -> damage -> barrier -> AfterHit -> counter/cover/arcane -> status_add -> death/revive -> extra_turn -> turn_end/_SetTime`
   recording exact VAs and the **owning module (`M01..M11`)** of every hand-off so no bug falls between module boundaries.
2. **`M01..M11` in parallel batches** by fresh, no-fork, read-only writers under strict Section 0 Quarantine (enforced by giving each worker an explicit allowed-file list: vanilla exe + `00_INVENTORY.json` + `M00_PIPELINE.md` + `backups/*.pck` only).
3. **Mandatory Spec Format (concise, typed, machine-checkable — target budget ~40 KB max per module):**
   - **Rule ID:** append-only (`M02.01`, `M02.02`, ...), **NEVER renumbered**.
   - **Calls / CalledBy:** explicit cross-module links matching `M00_PIPELINE.md`.
   - **Binary VA(s):** exact address range(s).
   - **Typed Pseudocode:** compact formal logic instead of prose — explicit `f32`/`i32`/`trunc0`/`floor`/`clamp`, `<` vs `<=`, exact RNG call count, exact step order, and edge guards.
   - **Program Evidence:** verbatim lines copied from `tools/exe_dis.py` (with VAs).
4. **Automated Evidence Gate (`tools/audit_check.py --spec`):**
   - Generalize existing `tools/audit_check.py` to re-disassemble every quoted VA line in `docs/binary_spec/M*.md` directly from the SHA-256-verified vanilla `.exe`.
   - **Hard Gate:** `0` mismatched/paraphrased instructions and minimum verified lines per rule before any module is marked complete in `STATE.json`.

---

### Phase 2 — Two-Way Global Diff & Architectural Triage

**Goal:** Compare the complete Clean-Room Spec (`M00`–`M11`) against the **entire simulator pipeline** (`tools/extract_vanilla.py`, `gamedata/`, `tools/engine_export.py`, `engine_cs/src/DtEngine/`) in **BOTH directions** before touching any code.

**Execution Rules:**
- Performed by fresh read-only auditors (distinct from Phase 1 authors). **NO code edits during Phase 2.**
- **Forward Diff (`Spec -> Code`):** every Rule ID in `M00..M11` mapped to `MATCH`, `S0`, `S1`, `S2`, or `MODEL-LIMIT` in `docs/binary_spec/DIFF_TABLE.json` and `docs/binary_spec/DIFF_REPORT.md`.
  - Every `MATCH` MUST cite both a verified exe quote and a verified C#/Python `file:line` quote (checked by generalized `tools/audit_check.py`).
- **Reverse Sweep (`Code -> Spec`):** mechanically grep every literal Effect ID, Enchant ID, status ID, and magic constant in `Battle.cs`, `Units.cs`, `Formulas.cs`, `Action.cs`, `Ai.cs`, and `gamedata/` against `pck_usage` and `M00..M11`. Any code branch not backed by a Rule ID is flagged **`ENGINE-ONLY`** (catches invented/ghost mechanics).
- **Mechanical Severity Classification (`S1` vs `S2` by reach, not guesswork):**
  - **`S0` (Fundamental / Architectural):** state-machine order, action pipeline hand-off, unit/status/performance lifecycle, vtable exclusivity, or systemic data-pipeline bug.
  - **`S1` (Active Combat / Loader Bug):** fires on skills, attacks, enemies, equipment, or passives present in vanilla `pck_usage` / real battles.
  - **`S2` (Rare / Unreachable Edge Case):** zero or near-zero reach in vanilla `pck_usage`, or narrow multi-condition edge case.
  - **`MODEL-LIMIT`:** justified under Section 2 Out-of-Scope.
- **Global Pre-Fix Validation Gate:** Review all `S0` findings together before editing code to resolve architectural root causes cleanly.

---

### Phase 3 — Fixes, "1 Bug = 1 Test", Legality Gate & Binary Invariants

**Goal:** Resolve all `S0` → `S1` → `S2` (and remove/justify all `ENGINE-ONLY` branches) with permanent automated regression guards.

**Mandatory Deliverables:**
1. **Strict Fix Order:** `S0` architectural batch first → `S1` batch → `S2` batch.
2. **1 Bug = 1 Deterministic Test:** Every fix adds a failing-before / passing-after unit test in `BinaryConformityTests.cs` (or Python `tests/` for extractor/loader bugs).
3. **Centralized Legality Gate (`Policy.cs` leak closure):** Add single engine predicate `Battle.Legal(unit, action, targets)` called by `Policy.cs`, plus an assert mode in `Battle` rejecting any illegal action. Verify with a battery smoke run in assert mode.
4. **`X01..X17` Patch Hook Test Pairs:** Every exe patch in Phase 0's byte-diff inventory gets an explicit test pair (`vanilla` option matches unpatched exe; `variant` option matches patched exe).
5. **Automated Binary-Table & `.pck` Invariants (`tests/test_binary_invariants.py`):**
   - Assert 1-to-1 equality between `00_INVENTORY.json` (vanilla `.exe` vtables/flags) and C# constant tables (`SONG_EFFECTS`, `DANCE_EFFECTS`, `GEASS_EFFECTS`, `DispelAlways`, `DispelIfRaised`, `AlwaysBuffStatus`, `SignedBuffDebuff`, `HasTrueAilment` `vtable+0x68`, exclusive barriers `101/102/181`, exclusive weapon enchants `325..329`, sleep-decay `vtable+0x8c`, `0x3C` immunity bits, enchant stacking flags).
   - Direct `.pck` round-trip invariant: re-parse `backups/*.pck` directly and compare field-by-field against `vanilla_source_of_truth.xlsx` and `build/engine_snapshot.json` (catches `extract_vanilla.py` / `gamedata` / `engine_export.py` drift!).
6. **Handling Existing Test Suites Cleanly:**
   - **`CalibrationTests`** (empirical oracles: JP-wiki speed tests, measured Daedalus damage ranges): independent ground truth — a fix must **NEVER** break them without an explicit binary-verified explanation.
   - **`ParityTests`** (golden baselines recorded from the removed legacy Python sim): may be re-recorded ONLY when a binary-verified Rule ID explains the delta, citing that Rule ID in the commit message.

**Exit Gate:** 0 open `S0/S1/S2`/`ENGINE-ONLY` items; `dotnet test engine_cs -c Release` PASS; `python -m unittest discover -s tests -p "test_*.py"` (including `test_binary_invariants.py`) PASS; `Policy` assert-mode smoke run PASS.

---

### Phase 4 — 5-Stratum Independent Random Audit with Canary & Circuit Breaker

**Goal:** Independently falsify the certified engine using unbiased sampling, out-of-catalog trace verification, false-negative canary detection, and strict false-positive adjudication.

**Sampling Protocol (`tools/sample_audit_batch.py`):**
- Uses a fresh logged random seed, sampling **without replacement** across rounds, drawing **15 items per round** across **5 strata**:
  - **3** from `core_combat` (`M00`–`M05`: pipeline, turns, damage, hit, heal)
  - **3** from `status_procs` (`M06`–`M08`: status lifecycle, ailments, procs/counters)
  - **3** from `effects_passives` (concrete active IDs drawn across all 3 dispatch routes: `CCommand`, `FINDERS`, `0x4e4dd0`/`0x4fab50`)
  - **3** from `units_ai_loaders` (`M09`–`M11`: dolls/summons/enchants, AI VM, unit build, `.pck` loaders)
  - **3 out-of-catalog `Trace.cs` events (unknown-unknown catcher):** run seeded random vanilla battles with `Trace.cs` enabled, pick 3 random concrete trace events (e.g., a damage number, a status application/tick, a turn-order advance), and require the auditor to **re-derive each exact number/outcome by hand from the vanilla `.exe`**.

**Auditor Isolation & Dual Control (Anti-FN & Anti-FP):**
- Launch fresh, no-fork, read-only auditor(s) with high reasoning capability. They receive ONLY the 15 items (12 catalog + 3 trace events), the SHA-256-pinned vanilla `.exe`, and the engine/loader code — **ZERO exposure** to `M00..M11.md`, `DIFF_REPORT.md`, or `engine_conformity.json`.
- **False-Negative Control (Canary Mutation):** Before each round, the coordinator plants **1 secret seeded mutation** in an isolated branch copy of `engine_cs/` (e.g., flipping `<` to `<=`, changing a rounding op, or dropping a row guard) on one of the sampled items. **If the auditor misses the canary, the entire round is VOID** and must be re-run with a stronger audit prompt/tooling check.
- **False-Positive Control (Adjudication):** A reported finding counts as a **VERIFIED FAIL** ONLY if it:
  1. Passes `tools/audit_check.py` (quoted exe and C#/Python lines verified verbatim), **AND**
  2. Reproduces via a concrete failing deterministic unit test against the unmutated engine.

**Certification & Upgraded Circuit-Breaker Rules:**
- **CERTIFIED PASS:** Final round achieves **0 verified fails** (with canary caught) **AND** cumulative `S2` across all Phase 4 rounds is `<= 1` → proceed to Phase 5.
- **Immediate Circuit-Breaker Trip (HARD STOP → Drawing Board `docs/binary_spec/POST_MORTEM.md`):**
  1. **ANY** verified `S0` finding in any round, **OR**
  2. **2 or more** verified fails sharing the same root-cause class, **OR**
  3. **3 consecutive failed rounds** (`Consecutive Failed Rounds == 3/3`).
- **Normal Retry (Round 1 or Round 2 fails with S1/S2 only, no shared root-cause pattern):**
  - Fix every verified fail + add regression tests + update binary invariants → draw **15 brand-new un-audited items** (without replacement) + fresh canary for the next round.
- **Drawing Board Post-Mortem (`docs/binary_spec/POST_MORTEM.md`) when Breaker Trips:**
  - For every leaked bug, explicitly classify **which phase failed to catch it**:
    - `P0` (missing from binary inventory),
    - `P1` (spec wrong/incomplete),
    - `P2` (diff misclassified or missed), or
    - `P3` (fix or invariant test inadequate).
  - Fix the **tooling/process defect** at that owning phase, re-run affected modules through Phases 1–3, reset breaker to `0/3`, and re-enter Phase 4 only after user approval.

---

### Phase 5 — Final Balance Recalibration, Packaging & Hygiene *(Post-Certification Only)*

**Entry Requirement:** Phase 4 status = `CERTIFIED PASS`.

1. Run `python tools/full_suite.py` + `dtcli sealbook-battery` + `dtcli support-battery` + `python tools/suite_charts.py`.
2. Review all balance reports (`DIFFICULTY_CURVE.md`, `POSTGAME_COMPARE.md`, `CLASS_BALANCE.md`, `CLASS_STAGES.md`, `PARTY_BATTERY.md`, `WIN_RATES.md`, `SKILL_BATTERY.md`, `UNIQUE_BATTERY.md`, `MERCENARY_BATTERY.md`, `SEALBOOK_BATTERY.md`).
3. Recalibrate `data_tables/balance_changes.xlsx` only where the certified engine shifted targets (preserving `0 easier` in story and postgame and `16/16` classes in band).
4. Run `python tools/package_all.py` to build and verify final `dist/DT22_qol_*.zip` and `dist/DT22_balance_*.zip`.
5. Sync `docs/FORMULAS.md` and `data_tables/engine_conformity.json` (`python tools/engine_conformity.py`), run all Python + C# + Binary-Invariant tests, cleanly archive/remove temporary working files, and commit & push upon user approval.

---

## 4. Session Handoff Log (Append-Only)

| Date | Commit | Phase | Completed | Next Exact Action |
|---|---|---|---|---|
| 2026-11-21 | `ae68713` | Setup | Created `docs/ENGINE_CONFORMITY_ROADMAP.md` (baseline `219/219` Python, `61/61` C# PASS). | Review roadmap before starting Phase 0. |
| 2026-11-21 | `ae68713` *(uncommitted)* | Setup | Incorporated independent architecture review (`#25`): real `.pck -> extract_vanilla -> gamedata -> Loader/Data/Scenario/Recipe` pipeline; all 3 effect dispatch routes + mechanical `Battle::*`/RTTI/jump-table denominator + `M11`; SHA-256 pinning (`785b0257...8f60`) & expanded quarantine; `M00_PIPELINE.md` first + typed pseudocode; generalized `tools/audit_check.py` gate; Phase-2 reverse sweep (`ENGINE-ONLY`) & reach-based severity; `Legal()` assert gate; `X01..X17` byte-diff pairs; Phase-4 15-item 5-stratum audit (`Trace.cs` out-of-catalog + canary + FP adjudication + immediate S0/shared-root-cause breaker). | Commit roadmap + add pointer in local `CLAUDE.md`, then start **Phase 0** (`tools/exe_inventory.py` + `STATE.json` + `tools/conformity_status.py`) when user gives go-ahead. |

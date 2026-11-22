# Clean-Room Binary Conformity Roadmap (`engine_cs` + `tools/*_data` + `gamedata`)

> **PURPOSE:** Achieve full, mechanically verified binary fidelity between the entire combat simulator pipeline (`backups/** -> tools/extract_vanilla.py & tools/*_data.py -> gamedata/ -> tools/engine_export.py -> engine_cs/src/DtEngine/`) and the clean vanilla executable (`backups/exe/DT22_en_unwrapped.vanilla.exe`, pinned by SHA-256) using a **Binary-First Clean-Room Specification**, **Two-Way Global Diff & Architectural Triage**, **Machine-Checked Evidence**, **Automated Binary-Table & `.pck` Invariants**, and a **5-Stratum Independent Random Audit with Canary & Circuit Breaker**.
>
> **WHY THIS EXISTS:** Auditing from `C# -> Exe` is structurally blind to mechanics present in the executable that the simulator never implemented (e.g., extra-turn turn-start skipping at `0x4365ff`, Geass performance group `0x43cb80`, `AddStatus` exclusive vtable groups `0x7c`/`0x84`, Magic effect `47`). This campaign reverses the direction strictly to `Exe -> Clean-Room Spec -> Two-Way Global Diff -> Fix -> Hardened Random Acceptance Sampling`.

---

## 0. Mandatory Resumption Protocol (Context-Loss Shield)

**READ THIS ENTIRE SECTION FIRST after any context compaction, restart, or new session.**

1. **Check machine truth first:** Once Phase 0 creates `docs/binary_spec/STATE.json` and `docs/binary_spec/DIFF_TABLE.json`, run `python tools/conformity_status.py` to regenerate Section 1 counts rather than editing counters by hand. Until then, read Section 1 and Section 4 below. Never rely on conversation memory.
2. **Verify repository state:** run `git status --short` and `git log -3 --oneline`.
3. **Single-writer discipline:** Only the **coordinator** edits this roadmap, `STATE.json`, and `DIFF_TABLE.json`. Workers write only their assigned module/claim output files.
4. **Pin the clean vanilla executable by SHA-256 (first priority in `tools/exe_reader.py`):**
   - `tools/exe_reader.py:reading_path()` MUST prioritize `VANILLA_PATH` (`backups/exe/DT22_en_unwrapped.vanilla.exe`) ahead of `mod_config.formula_exe()` and assert:
     - **SHA-256:** `785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60` (matches `backups/exe/DT22_en_unwrapped.vanilla.exe.sha256`, 3,247,104 bytes).
   - **Vanilla data backups:** `backups/**/*.pck` (including nested `backups/Enemy/`, `backups/Character/`, `backups/Summon/`, `backups/NPC/`, `backups/Dungeon/floor_parameters.zip`, `backups/Dungeon/floor_maps.zip`).
   - **Existing disassembly tools:** `tools/exe_dis.py`, `tools/exe_who_calls.py`, `tools/exe_find_const.py`, `tools/exe_around.py`, `tools/exe_effects.py`, `tools/exe_enchants.py`, `tools/exe_digest.py`. *(In Phases 0–4, NEVER call `exe_effects.py` or `exe_enchants.py` main entrypoints directly — `exe_effects.py` mutates `balance_criteria.xlsx` in-place and writes `docs/generated/EFFECT_COVERAGE.md`. Call only pure binary-scanning helpers and redirect ALL outputs to `docs/binary_spec/`.)*
5. **Obey Phase Quarantine & Freeze Rules strictly:**
   - **Phase 0 & Phase 1 Quarantine (enforced by explicit sandboxed allowed-file list in worker briefs):** Clean-room writers are **FORBIDDEN** from reading:
     - `engine_cs/`, `engine_cs/tests/`, `tests/`
     - `gamedata/`, `tools/*_data.py`, `tools/extract_vanilla.py`, `tools/engine_export.py`
     - `docs/FORMULAS.md`, `docs/ENGINE_AUDIT.md` (quotes C#)
     - `data_tables/engine_conformity.json`, `docs/generated/EFFECT_*`
     - `data_tables/balance_criteria.xlsx` (`EffectRules` sheet), `data_tables/qol_rules.xlsx`, `data_tables/vanilla_source_of_truth.xlsx` (`Effects` notes)
     - `RESULTADOS_REGLAS_COMBATE.md` (if present)
     - Raw names in `00_INVENTORY.json` come ONLY from `backups/CommandData.pck`, `backups/EnchantData.pck`, and binary strings — zero `FORMULAS.md`-derived labels.
   - **Phase 2 Read-Only Rule:** Diff auditors compare `docs/binary_spec/M00..M11.md` + `00_INVENTORY.json` against the real code pipeline (`tools/extract_vanilla.py`, the 13 `tools/*_data.py` readers, `tools/pck_handler.py`, `data_tables/record_layouts.json`, `gamedata/`, `tools/engine_export.py`, `engine_cs/src/DtEngine/`). Existing `docs/ENGINE_AUDIT.md` P-items and `BinaryConformityTests.cs` are treated as **unverified claims to re-check**, NOT ground truth. **NO code edits during Phase 2.**
   - **Phases 0–4 Balance Freeze:** **FREEZE** `data_tables/balance_changes.xlsx`, `docs/generated/*`, `measures/*`, and `tools/full_suite.py` until Phase 4 certifies the engine. *(Fast stdout/scratch smoke runs are allowed during Phase 3 to catch crashes or large swings without modifying tracked reports.)*
6. **Commit & local pointer hygiene:** Keep `docs/ENGINE_CONFORMITY_ROADMAP.md` committed and keep the pointer + Phase 0/1 quarantine warning banner at the top of local `CLAUDE.md`. Record the commit hash in every Section 4 handoff row.
7. **Worker model priority ladder (user preference):** Spawn workers using `gemini-4-argon-high` first; if exhausted, fall back to `claude-sonnet-5-5-high`; if exhausted, fall back to `gemini-4-neon-high`. Check live quotas via `swarm(action="models", all=true)` before switching.

---

## 1. Live Campaign Dashboard

*(Once `tools/conformity_status.py` exists, this section is regenerated mechanically from `docs/binary_spec/STATE.json` and `docs/binary_spec/DIFF_TABLE.json`.)*

- **Campaign Status:** `IN PROGRESS — PHASE 0 STARTING`
- **Active Phase:** `Phase 0 — Mechanical Binary Inventory`
- **Last Updated:** `2026-11-21`
- **Baseline Commit:** `d6ddd7b` (`219/219` Python tests PASS, `61/61` C# tests PASS)
- **Active Blocker:** `None`

### In-Progress Claims

| Module / Task | Owner | Started Commit | Output Path | Status |
|---|---|---|---|---|
| Phase 5 Balance Recalibration *(deferred until user request)* | coordinator | `311db06` | `data_tables/balance_changes.xlsx` | `deferred` |

### Phase Gate Tracker

| Phase | Name | Status | Primary Artifacts | Exit Gate | Sign-off Commit |
|---|---|---|---|---|---|
| **0** | Mechanical Binary Inventory | `[x] done` | `tools/exe_reader.py` (pinned), `tools/exe_inventory.py`, `docs/binary_spec/00_INVENTORY.json`, `00_INVENTORY.md`, `STATE.json`, `tools/conformity_status.py`, generalized `tools/audit_check.py` | SHA-256 pinned; all 6 combat C++ namespaces (`0x413000..0x570000`) + 633 RTTI vtables + all 5 dispatch routes + all battle jump tables + `.rdata` tables + `.pck` usage + `X01..X17` byte diff + stratified `audit_catalog` dumped cleanly | `2133dab` |
| **1** | Clean-Room Binary Spec (`Exe` only) | `[x] done` | `docs/binary_spec/M00_PIPELINE.md`, `docs/binary_spec/M01..M11.md` | `M00` + `M01..M11` complete (140 rules, 3,224 verified exe lines, **0 failing**) via `audit_check.py --spec` | `ef410a6` |
| **2** | Two-Way Global Diff & Triage | `[x] done` | `docs/binary_spec/DIFF_REPORT.md`, `docs/binary_spec/DIFF_TABLE.json` | 146 items (140 spec + 6 `ENGINE-ONLY`), `audit_check.py --diff` passes (**0 failing**), 282 sub-bugs triaged | `6950513` |
| **3** | Fixes, Tests & Binary Invariants | `[x] done` | `engine_cs/`, `gamedata/`, `tools/*_data.py`, `tools/extract_vanilla.py`, `BinaryConformityTests.cs`, `tests/test_binary_invariants.py`, `tests/test_phase3_py_fixes.py` | All S0/S1/Py-loader waves fixed; `Battle.IsLegalAction()` enforced; `68/68` C# + `282/282` Py + paired `X01..X17` PASS | `f1700d5` |
| **4** | 5-Stratum Independent Random Audit | `[x] done` | `tools/sample_audit_batch.py`, `docs/binary_spec/RANDOM_AUDIT_LOG.md` | 2 rounds (24 catalog items without replacement + 6 real `TextTrace` packets + 2/2 caught canaries); Round 2 **CERTIFIED PASS** (`0 S0 / 0 S1`, 1 synthetic `S2` fixed) | `7ce0de7` |
| **5** | Final Balance Recalibration & Release | `[~] sync done` | `docs/generated/*`, `measures/*`, `dist/*.zip`, `docs/FORMULAS.md`, `data_tables/engine_conformity.json` | `full_suite.py` + `sealbook-battery` + `support-battery` + `suite_charts.py` + `package_all.py` + doc sync complete (`311db06`); optional `balance_changes.xlsx` recalibration deferred per user | `311db06` |

### Phase 1–3 Module Progress Matrix (`M00`–`M11`)

| ID | Module | Spec File (`docs/binary_spec/`) | Phase 1 (Spec + `audit_check`) | Phase 2 (2-Way Diff) | Open `S0 / S1 / S2` | Phase 3 (Fixed + Tested) |
|---|---|---|---|---|---|---|
| `M00` | Global Action & Turn Call-Graph Pipeline *(FIRST)* | `M00_PIPELINE.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M01` | Turn Loop, 3 `Update` Jump Tables, ATB & Extra Turns | `M01_TURN_LOOP_AND_ATB.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M02` | Physical Damage, Range, Crit, Multi-Hit & Zones | `M02_PHYSICAL_DAMAGE.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M03` | Magical Damage, Elements & Missed Spells | `M03_MAGICAL_DAMAGE.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M04` | Hit / Evasion, Targeting Scopes & Formation | `M04_HIT_EVASION_AND_TARGETING.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M05` | Healing, Recovery, After-Battle & `ItemResult` (`0..106`) | `M05_HEALING_RECOVERY_AND_ITEMS.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M06` | Status Lifecycle, Vtable Groups, Recalc & Dispel | `M06_STATUS_LIFECYCLE_AND_RECALC.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M07` | Ailments, Immunities, Barriers & Recovery | `M07_AILMENTS_AND_CONTROL.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M08` | Procs, Counters, Cover, Parry, Patterns & AfterHit | `M08_PROCS_COUNTERS_AND_AFTERHIT.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M09` | Dolls, Summons, Guests & Enchantments | `M09_DOLLS_SUMMONS_NPCS_AND_ENCHANTS.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M10` | Enemy/Summon/NPC AI VM, Map Triggers & Binary Readers | `M10_ENEMY_AI_AND_DATA_LOADERS.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |
| `M11` | Unit Build, Growth, Unarmed Rank, Caps & EXP/SP Curves | `M11_UNIT_BUILD_AND_STATS.md` | `[x]` | `[x]` | `0 / 0 / 0` | `[x]` |

### Phase 4 Random Audit Circuit-Breaker Tracker

- **Consecutive Failed Rounds:** `0 / 3`
- **Immediate Trip Triggers:** ANY verified `S0`, OR `>= 2` verified fails sharing a root-cause class, OR `3` consecutive failed rounds → **HARD STOP & Drawing Board `POST_MORTEM.md`**.
- **Items Audited Without Replacement:** `24` catalog + `6` Trace JSON = `30` | **Canaries Caught:** `2 / 2`

| Round | Date | Seed | Canary Planted / Caught? (Max 2 void retries) | Items (12 catalog + 3 Trace JSON = 15) | Verified Fails (`S0/S1/undoc S2`) | Verdict |
|---|---|---|---|---|---|---|
| 1 | 2026-11-22 | `20261122` | `SP11` / **YES** | 12 catalog + 3 Trace (`3/3 PASS`) | `0 / 3 / 4` *(all 7 fixed in `483e6df`)* | `[x] FAIL (fixed)` |
| 2 | 2026-11-22 | `20261123` | `EF275` / **YES** | 12 new catalog + 3 Trace (`3/3 PASS`) | `0 / 0 / 1` *(synthetic `SP02` fixed in `7ce0de7`)* | `[x] CERTIFIED PASS` |
| 3 *(if needed)* | — | — | — | — | — | `[ ] not needed` |

---

## 2. Frozen Scope Boundary & Real Code Pipeline

### Real Code Pipeline Under Audit (Exact Files)
1. **Excel-Backed Extraction:** `backups/*.pck` → `tools/extract_vanilla.py` → `data_tables/vanilla_source_of_truth.xlsx` → `gamedata/data.py` (+ `balance_criteria.xlsx` `EffectRules`, `data_tables/sim_setup.xlsx`)
2. **Direct Binary & Exe Readers (13 standalone modules bypassing `extract_vanilla.py`):**
   - `tools/enemy_data.py` (`backups/Enemy/Enemy.pck`)
   - `tools/enemy_ai.py` (`EnemyAIData.bin`, `SummonAIData.bin`, `NPCAIData.bin`)
   - `tools/class_data.py` (`backups/ClassLevelData.pck`, `ClassData.pck`, `GROWTH_ROW`)
   - `tools/class_modifier_data.py` (`.exe` `0x4f81e8` / `.rdata` `0x6d3b64..0x6d40a0`)
   - `tools/character_data.py` (`backups/Character/Character.pck`)
   - `tools/floor_data.py` (`backups/Dungeon/floor_parameters.zip`)
   - `tools/map_data.py` (`backups/Dungeon/floor_maps.zip` opcode `0x1F` battle cells)
   - `tools/summon_data.py` (`backups/Summon/Summon.pck`)
   - `tools/doll_data.py` (`DOLLS` table from `0x484150`)
   - `tools/npc_data.py` (`backups/NPC/NPC.pck`)
   - `tools/random_move_data.py` (`.exe` `0x64f8c0..0x64fb50`)
   - `tools/skill_tree_data.py` (`Trailer`)
   - `tools/item_effect_data.py` (`.exe` `0x50e538`)
   - Plus `tools/pck_handler.py`, `tools/game_profile.py`, `data_tables/record_layouts.json`, `gamedata/variant.py`, `gamedata/setup.py`, `gamedata/levels.py`, `gamedata/progression.py`, `tools/engine_export.py` → `build/engine_snapshot.json`
3. **C# Simulator:** `engine_cs/src/DtEngine/` (`Loader.cs`, `Data.cs`, `Scenario.cs`, `Recipe.cs`, `Units.cs`, `Action.cs`, `Formulas.cs`, `Battle.cs`, `Ai.cs`, `Trace.cs`, and binary legality rules called by `Policy.cs`).

### IN SCOPE (Must Match Vanilla Binary Faithfully)
- Every combat calculation, branching rule, clamp, rounding (`f32` vs `f64`, `trunc0` vs `floor`), cap, floor, `<` vs `<=` roll bound, RNG call count, and execution order inside battles and dungeon battle-rows.
- Unit construction: class/level growth (`ClassLevelData`), `LvExpSkptData`, unarmed weapon ranks (`ClassData+0x24` / `0x4f5585`), equipment & `%` modifiers, caps, EXP/SP curves (`gamedata/levels.py`, `progression.py`).
- **All 5 binary dispatch routes:** `CCommand` factory (`0x47b220`), inline `FINDERS` + `[effect+0x24]` + `vtable+0x48/+0x50`, pushed passive/enchant lookups (`0x4e4dd0`, `0x4fab50`, slot `0xf0`), `Action::CAction*::_CreatePattern` & `CActionPattern*` subclasses (`0x41a4a0`, `0x41e060`, `0x41c970`, `0x41f4b0..0x430340`), and `ItemResult` (`0x50c570` / `0x50e538`, 107 types `0..106`).
- Enemy, Summon, and NPC AI script VMs (`EnemyAIData.bin`, `SummonAIData.bin`, `NPCAIData.bin`: sources `0x432fa0`, targets `0x434754`, opcodes, once/switch flags, target overrides, breath `3` bypass) and fixed-battle map cell triggers (`backups/Dungeon/floor_maps.zip` opcode `0x1F`).
- Intentional mod patches `X01..X17` by actual ownership:
  - **C# Combat (`Battle.cs`/`Formulas.cs`):** `X13` Arcane Shield (`0x424768`), `X14` Interrupt Product (`0x44d044`), `X16` Third Eye Wide Dispel (`0x47ee73`), `X17` Positive Trance (`0x44ccd2`). *(Note: `Battle.cs` `Options.SurvivalGuard` / `L46` is an inactive trial hook with no `ExePatches` row — classify as intentional trial hook in reverse sweep.)*
  - **Python Progression (`gamedata/progression.py` / `tools/catch_up_options.py`):** `X01..X08` EXP level-gap factors (`0x450781..0x450811`), `X09..X12` crown reset steps (`0x4f9502..0x4f952c`).
  - **Out-of-Combat (`design_rows.steps_a_turn`):** `X15` (`0x48d5f3`, dungeon map steps per status turn).
- **Binary action legality rules used by `Policy.cs`:** centralized in `Battle.IsLegalAction(Action action)` and asserted on `Policy.Choose` inside `Battle.Turn`.

### OUT OF SCOPE (Documented Non-Simulated Systems)
- Graphics, animations, audio/voices, camera, UI layout, menu navigation, save/load serialization, dungeon tile/event/cutscene scripts (including `backups/Script/Battle.pck`, which is a VN cutscene `Main06_10.adv.bin` in `Dungeon::CDungeon::_Initialize`).
- **Joint Skills (`JoinSkillData` / `Action::CActionJoinAttack`) and Party Skills (`PartySkillData` / `CParameterSkillParty`)** — explicitly parked / out-of-model per `CLAUDE.md` (only their raw `.pck` extraction stays in `extract_vanilla.py`).
- Sub-event stat bonuses and DLC.
- CRT/hardware RNG algorithm identity (we verify roll thresholds, bounds, distributions, and call counts — not MSVC `rand()` bit parity).
- Player-party preference heuristics inside `Policy.cs` (song/dance/doll slot preservation, TP reserves, buff recasting thresholds), once binary legality itself is enforced by `Battle.IsLegalAction(action)`.

---

## 3. Detailed Phase Playbook

### Phase 0 — Mechanical Binary Inventory *(No C# Reading)*

**Goal:** Build a complete, mechanically derived denominator of the game's combat binary from `backups/exe/DT22_en_unwrapped.vanilla.exe` (SHA-256 pinned) and `backups/**`, writing ONLY to `docs/binary_spec/` (never into `docs/generated/` or `balance_criteria.xlsx`).

**Deliverables:**
1. **`tools/exe_reader.py` SHA-256 Pin:** prioritize `VANILLA_PATH` ahead of `mod_config.formula_exe()` and assert SHA-256 `785b0257...8f60` whenever `VANILLA_PATH` is selected.
2. **`tools/exe_inventory.py`** → writes `docs/binary_spec/00_INVENTORY.json` + `docs/binary_spec/00_INVENTORY.md`, extracting purely from the vanilla binary and `backups/**` (zero reads of `balance_criteria.xlsx`, `qol_rules.xlsx`, `FORMULAS.md`, or `vanilla_source_of_truth.xlsx`):
   - **Mechanical Denominator (6 C++ Namespaces in `0x413000..0x570000`):**
     - `Action::*` (`0x413460..0x42f8d0`, 46 RTTI classes), `Battle::*` (`0x430f10..0x4580a0`, 21 RTTI classes), `Command::*` (`0x468530..0x490000`, 153 RTTI classes), `Game::*` (`0x4e0670..0x505000`, 41 RTTI classes), `ItemResult::*` (`0x50a310..0x515000`, 106 RTTI classes), `Parameter::*` (`0x52c350..0x578510`, 1 RTTI class).
     - Enumerate **all RTTI vtables + vtable methods + assert strings + function prologues / call-graph targets** across `0x413000..0x570000`, each classified `in_scope` or `out_of_scope`.
     - Automated scan of **all `jmp [reg*4 + table]` (`FF 24 ...`) jump tables** in `0x413000..0x570000` with their `cmp reg, N` bounds — including `CBattleBase::Update`'s **3** jump tables (`0x4397e0`, `0x439820` `0..24` = 25 states, `0x439884`), `0x41a814`, `0x41e5fc`, `0x431964`, `0x432fa0`, `0x434754`, `0x43fde8`/`f4`/`04`, `0x47de14`/`47e0a4`, `0x47fa7c`/`c8`, `0x485d5c`/`e54`/`f04`, `0x4f4bdc`, `0x4f81e8`, `0x4fdf2c`/`e11c`, `0x50e538`, `0x5546fc`. *(Excluding `0x4b36cc` in `Dungeon::CDungeonBase`.)*
   - **All 5 Binary Dispatch Routes:**
     - **Route (a) `CCommand` factory (`0x47b220`):** jump table `9..0x1C1` (`0x47de14`/`0x47e0a4`) PLUS out-of-range IDs, with each class vtable VA, boolean/constant vtable slots (`+0x54`, `+0x5c`, `+0x64`, `+0x68`, `+0x6c`, `+0x70`, `+0x74`, `+0x78`, `+0x7c`, `+0x84`, `+0x8c`, etc.), and `Execute`/`Tick`/`OnAdd`/`OnRemove` VAs.
     - **Route (b) Inline effect lookups:** every call site of `FINDERS` (`0x47e340`, `0x47e290`, `0x47e390`, `0x47e400`, `0x48cbf0`, `0x48c680`, `0x557620`, `0x56ce70`), `push N; call [vt+0x48/+0x50]`, and `call dword ptr [reg+0x24]; cmp eax, IMM`.
     - **Route (c) Pushed passive & enchant lookups:** party passive `0x4e4dd0`, unit passive `0x4fab50`, and enchant slot `0xf0`.
     - **Route (d) Action Pattern factories & subclasses:** `CActionSkill::_CreatePattern` (`0x41e060`, cases `0..15`), `CActionEnemyAttack::_CreatePattern` (`0x41a4a0`, cases `0..17`), `0x41c970`, all `CActionPattern*` subclasses (`0x41f4b0..0x430340`), direct `CBattleBase::Update` patterns (`E0822` `0x42b240`, `E0835` `0x42b8a0`, `T0094` `0x42ec90`, `U0008` `0x42f870`), and random enemy attack table `0x64f1c0`.
     - **Route (e) `ItemResult` switch (`0x50c570` / `0x50e538`):** all 107 item effect types (`0..106`) → 106 `CItemResult*` RTTI classes (41 skill-casters via `0x50b030` + custom `vtable+0x0c` handlers).
   - **Static Data Tables & `.pck` Usage (`pck_usage`):**
     - `.rdata` float/int tables cross-referenced by battle code (row, element, weapon-rank, multi-hit, random-move `0x64f8c0..0x64fb50`, class modifiers `0x6d3b64..0x6d40a0`, `EffectSequence`).
     - Complete `.pck` usage scan across `backups/**/*.pck` and `backups/Dungeon/floor_*.zip`: every used Effect ID, Pattern ID (`Trailer[4]` / `EnemyAttack+0x90`), Item Effect Type, Enchant ID, Enemy `0x3C` bit, AI opcode, and Passive ID with occurrence counts (raw names read only from `CommandData.pck`/`EnchantData.pck`).
   - **`X01..X17` Patch Inventory:** byte diff between vanilla `.exe` and `exe_patch.py`-patched image → exact patched VAs mapped to owning subsystem (`C# combat` vs `Python progression` vs `design_rows`).
   - **Stratified `audit_catalog`:** atomic testable items falling out naturally from the mechanical denominator across the 4 catalog strata (`core_combat`, `status_procs`, `effects_passives`, `units_ai_loaders`).
3. **`docs/binary_spec/STATE.json` + `tools/conformity_status.py`** — machine source of truth for dashboard counts.
4. **Generalized `tools/audit_check.py`** — keep legacy `P*` checks untouched; add `--spec <M*.md>` (verifies `### M\d+\.\d+` headers, required fields, and re-disassembles every quoted `004xxxxx` line against SHA-256-pinned `VANILLA_PATH`) and `--diff <DIFF_REPORT.md>` (verifies both `004xxxxx` exe lines and `(?:engine_cs|tools|gamedata)/[\w/.\-]+\.(?:cs|py):(\d+)` code lines).

**Exit Gate:** SHA-256 verified; 100% of `.pck` effect/pattern/item/enchant/AI IDs mapped; all 6 combat namespaces & jump tables inventoried; zero reads of quarantined docs; `audit_check.py --spec` and `conformity_status.py` tested.

---

### Phase 1 — Clean-Room Binary Specification (`Exe` → Spec Only)

**Goal:** Specify every in-scope mechanic directly from the vanilla binary with machine-verified disassembly quotes.

**Ordering & Execution Rules:**
1. **`M00_PIPELINE.md` FIRST (before `M01..M11`):** One fresh quarantined writer maps the complete ordered call graph:
   `battle_start -> select_actor -> turn_start_states (0x4397e0 / 0x439820 / 0x439884) -> action_select -> legality -> _CreatePattern -> target_resolve -> hit -> crit -> damage -> barrier -> AfterHit -> counter/cover/arcane -> status_add -> death/revive -> extra_turn -> turn_end/_SetTime`
   recording exact VAs and the **owning module (`M01..M11`)** of every hand-off.
2. **`M01..M11` in parallel batches** by fresh, no-fork, read-only writers under Section 0.5 Quarantine (explicit allowed-file list: vanilla exe + `00_INVENTORY.json` + `M00_PIPELINE.md` + `backups/**/*.pck` + `backups/Dungeon/floor_*.zip` only).
3. **Mandatory Spec Format (typed, machine-checkable, scalable):**
   - **Rule ID:** append-only (`M02.01`, `M02.02`, ...), **NEVER renumbered**.
   - **Calls / CalledBy:** explicit cross-module links matching `M00_PIPELINE.md`.
   - **Binary VA(s):** exact address range(s).
   - **Typed Pseudocode:** compact formal logic — explicit `f32`/`i32`/`trunc0`/`floor`/`clamp`, `<` vs `<=`, exact RNG call count, exact step order, and edge guards.
   - **Program Evidence:** verbatim lines copied from `tools/exe_dis.py` (with VAs).
   - **Grouped Tabular Batch Rules:** for high-cardinality homogeneous families (`CCommand` plain markers, ~260 enchants, 41 skill-casting `CItemResult`s), quote the shared disassembly template once and include a complete machine-checked parameter table covering every member ID/VA. Target `~40 KB` per file as a soft readability budget (`M09` may split into `M09a_DOLLS_SUMMONS_NPCS.md` + `M09b_ENCHANTMENTS.md` if needed).
4. **Automated Evidence Gate:** Every module MUST pass `python tools/audit_check.py --spec docs/binary_spec/MXX_*.md` (`0` unverified instructions) before being marked complete in `STATE.json`.

---

### Phase 2 — Two-Way Global Diff & Architectural Triage

**Goal:** Compare the complete Clean-Room Spec (`M00`–`M11`) against the **entire simulator pipeline** (`tools/extract_vanilla.py`, all 13 `tools/*_data.py` readers, `tools/pck_handler.py`, `data_tables/record_layouts.json`, `gamedata/`, `tools/engine_export.py`, `engine_cs/src/DtEngine/`) in **BOTH directions** before touching any code.

**Execution Rules:**
- Performed by fresh read-only auditors (distinct from Phase 1 authors). **NO code edits during Phase 2.**
- **Forward Diff (`Spec -> Code`):** every Rule ID in `M00..M11` mapped to `MATCH`, `S0`, `S1`, `S2`, or `MODEL-LIMIT` in `docs/binary_spec/DIFF_TABLE.json` and `docs/binary_spec/DIFF_REPORT.md`. Every `MATCH` MUST cite both a verified exe quote and a verified `.cs`/`.py` `file:line` quote (checked by `tools/audit_check.py --diff`).
- **Reverse Sweep (`Code -> Spec`):** mechanically grep every literal Effect ID, Enchant ID, status ID, pattern ID, and magic constant in `Battle.cs`, `Units.cs`, `Formulas.cs`, `Action.cs`, `Ai.cs`, `Loader.cs`, `gamedata/`, and `tools/*_data.py` against `pck_usage` and `M00..M11`. Unbacked branches are flagged **`ENGINE-ONLY`** (catches invented/ghost mechanics; note `Options.SurvivalGuard` `L46` is an intentional inactive trial hook).
- **Mechanical Severity Classification (`S1` vs `S2` by reach):**
  - **`S0` (Fundamental / Architectural):** state-machine order, action pipeline/pattern hand-off, unit/status/performance lifecycle, vtable exclusivity, or systemic data-pipeline bug.
  - **`S1` (Active Combat / Loader Bug):** fires on skills, attacks, enemies, equipment, items, or passives present in vanilla `pck_usage` / real battles.
  - **`S2` (Rare / Unreachable Edge Case):** zero or near-zero reach in vanilla `pck_usage`, or narrow multi-condition edge case.
  - **`MODEL-LIMIT`:** justified under Section 2 Out-of-Scope.
- **Global Pre-Fix Validation Gate:** Review all `S0` findings together before editing code to resolve architectural root causes cleanly.

---

### Phase 3 — Fixes, "1 Bug = 1 Test", Legality Gate & Binary Invariants

**Goal:** Resolve all `S0` → `S1` → `S2` (and resolve all `ENGINE-ONLY` branches) with permanent automated regression guards.

**Mandatory Deliverables:**
1. **Strict Fix Order:** `S0` architectural batch first → `S1` batch → `S2` batch.
2. **1 Bug = 1 Deterministic Test:** Every fix adds a deterministic unit test in `BinaryConformityTests.cs` (or Python `tests/` for extractor/reader/exporter bugs).
3. **Centralized Binary Legality Gate (`Policy.cs` leak closure):**
   - Add `Battle.IsLegalAction(Action action)` checking strictly **binary action legality** (actor alive/capable; skill battle-usable `Group & 0x10`/`0x08`, `WeaponAllows`, not Silenced/NoMagic for Magic, not Frozen for Technique, `EffectiveTpCost <= Actor.Tp`, valid target liveness/side for `TargetCode`; item count `> 0`). Keep `Policy` preference heuristics in `Policy.cs`.
   - Assert `Battle.IsLegalAction(action)` on `ChooseMember.Choose(this, unit)` inside `Battle.Turn` (and in `Policy.Options`), **NOT** inside raw `Battle.Perform(action)` calls used by synthetic unit tests. Verify with a battery smoke run in assert mode.
4. **`X01..X17` Scope-Split Patch Tests:**
   - C# combat hooks (`X13, X14, X16, X17`): paired vanilla/variant tests in `BinaryConformityTests.cs`.
   - Python progression hooks (`X01..X12`) & `X15`: paired vanilla/variant tests in `tests/`.
5. **Automated Binary-Table & Direct `.pck` Invariants (`tests/test_binary_invariants.py`):**
   - Assert 1-to-1 equality between `00_INVENTORY.json` (vanilla `.exe` vtables/flags) and C# constant tables (`SONG_EFFECTS`, `DANCE_EFFECTS`, `GEASS_EFFECTS`, `DispelAlways`, `DispelIfRaised`, `AlwaysBuffStatus`, `SignedBuffDebuff`, `HasTrueAilment` `vtable+0x68`, exclusive barriers `101/102/181`, exclusive weapon enchants `325..329`, sleep-decay `vtable+0x8c`, `0x3C` immunity bits, enchant stacking flags).
   - Direct `.pck` / `.zip` round-trip invariant: re-parse `backups/**/*.pck` and `backups/Dungeon/floor_*.zip` directly and compare field-by-field against `vanilla_source_of_truth.xlsx` and `build/engine_snapshot.json` (covering both `extract_vanilla.py` and the 13 `tools/*_data.py` readers).
6. **Handling Existing Test Suites Cleanly:**
   - **`CalibrationTests`** (empirical oracles: JP-wiki speed tests, measured Daedalus damage ranges): independent ground truth — NEVER break without a binary-verified explanation.
   - **`ParityTests` (`engine_formulas_golden.json`):** note the legacy Python generator was deleted; if a binary-verified Rule ID changes `Formulas.cs`, update `engine_formulas_golden.json` / `FormulaCheck.cs` directly and cite the Rule ID in the commit. Keep `data_tables/engine_conformity.json` method pointers valid so `tests/test_engine_conformity.py` stays green throughout Phase 3.

**Exit Gate:** 0 open `S0/S1/S2`/`ENGINE-ONLY` items; `dotnet test engine_cs -c Release` PASS; `python -m unittest discover -s tests -p "test_*.py"` (including `test_binary_invariants.py`) PASS; `Policy` assert-mode smoke run PASS.

---

### Phase 4 — 5-Stratum Independent Random Audit with Canary & Circuit Breaker

**Goal:** Independently falsify the certified engine using unbiased sampling, self-contained trace re-derivation, verified canary detection, and strict adjudication.

**Sampling Protocol (`tools/sample_audit_batch.py`):**
- Uses a fresh logged random seed, sampling **without replacement** across rounds, drawing **15 items per round** across **5 strata**:
  - **3** from `core_combat` (`M00`–`M05`: pipeline, turns, damage, hit, heal)
  - **3** from `status_procs` (`M06`–`M08`: status lifecycle, ailments, procs/counters/patterns)
  - **3** from `effects_passives` (concrete active IDs drawn across all 5 dispatch routes)
  - **3** from `units_ai_loaders` (`M09`–`M11`: dolls/summons/enchants, AI VM, unit build, `.pck` readers)
  - **3 out-of-catalog `Trace.cs` events (unknown-unknown catcher):** run seeded random vanilla battles using `TextTrace.DamageHook`/`HitHook`/`TurnEndHook` to emit a **self-contained JSON event packet** per sampled event (`{event_kind, actor_state, target_state, action, zone_state, rng_draws_for_event, engine_output}`). The auditor plugs those exact inputs and RNG draws into the vanilla `.exe` instructions to verify `engine_output` by hand.

**Auditor Isolation & Dual Control (Anti-FN & Anti-FP):**
- Launch fresh, no-fork, read-only auditor(s) with high reasoning capability. They receive ONLY the 15 items (12 catalog + 3 JSON trace packets), the SHA-256-pinned vanilla `.exe`, and the engine/loader code — **ZERO exposure** to `M00..M11.md`, `DIFF_REPORT.md`, or `engine_conformity.json`.
- **False-Negative Control (Canary Mutation):** Before each round, the coordinator plants **1 secret seeded mutation** on **1 of the 12 catalog items** inside an isolated git worktree / temp copy (never the main working tree), verified to fail at least 1 deterministic test before launching the auditor. **If the auditor misses the canary, the round is VOID** (capped at max **2 void retries per round** before halting to diagnose auditor tooling).
- **False-Positive Control (Adjudication):** A reported finding counts as a **VERIFIED FAIL** ONLY if it:
  1. Passes `tools/audit_check.py` (quoted exe and `.cs`/`.py` lines verified verbatim), **AND**
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
  - Classify every leaked bug by **which phase failed to catch it** (`P0` inventory, `P1` spec, `P2` diff, or `P3` fix/invariant), repair that phase's tooling/process, re-audit affected modules through Phases 1–3, reset breaker to `0/3`, and re-enter Phase 4 only after user approval.

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
| 2026-11-21 | `d6ddd7b` | Setup | Created `docs/ENGINE_CONFORMITY_ROADMAP.md` incorporating Opus 5.5 High review (`#25`). | Incorporate Argon 4 High review (`#27`), update `CLAUDE.md` banner, commit, and begin Phase 0. |
| 2026-11-21 | *(committing)* | Phase 0 Start | Incorporated all 7 Argon 4 High binary-verified refinements (`#27`): 6 C++ combat namespaces (`0x413000..0x570000`, 633 RTTI vtables); Routes (d) `_CreatePattern`/`CActionPattern*` & (e) `ItemResult` 107-case + `[effect+0x24]`/`vt+0x50`; 3 `CBattleBase::Update` jump tables (`0x4397e0`/`0x439820` `0..24`/`0x439884`); all 13 `tools/*_data.py` readers; removed `Script/Battle.pck` & moved `Join/PartySkill` out of scope; split `X01..X17` by actual owner; pinned `VANILLA_PATH` + expanded quarantine; grouped tabular rules + `--spec`/`--diff` `audit_check.py`; `IsLegalAction` on `Policy.Choose`; self-contained `Trace.cs` JSON packets + canary bounds; added `CLAUDE.md` quarantine banner. | Commit updated roadmap, pin `tools/exe_reader.py`, build `tools/exe_inventory.py`, `STATE.json`, `tools/conformity_status.py`, and generalize `tools/audit_check.py`. |

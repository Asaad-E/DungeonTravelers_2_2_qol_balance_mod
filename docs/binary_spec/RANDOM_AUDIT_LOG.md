# Phase 4 — 5-Stratum Independent Random Audit Log

**Pinned Vanilla Executable:** `backups/exe/DT22_en_unwrapped.vanilla.exe` (`SHA-256: 785b0257329dd6533a5378bdbdc646b7166e425a091f27fa3b01d291359a8f60`)  
**Sampler:** `tools/sample_audit_batch.py` (without replacement across rounds; 3 `core_combat` + 3 `status_procs` + 3 `effects_passives` + 3 `units_ai_loaders` + 3 real `TextTrace` event packets = 15 items/round)

---

## Round 1 — 2026-11-22 (Seed `20261122`)

- **Isolated Clean-Room Copy:** `p4_r1_isolated` (all `docs/binary_spec/`, `FORMULAS.md`, `engine_conformity.json`, and test suites physically removed prior to auditor launch).
- **Auditor:** `p4-r1-auditor` (`gemini-4-neon-high`, fresh no-fork session, read-only).
- **Secret Canary:** Planted on `SP11` (`Battle.cs:Redirect` mutated to `(action.Physical || action.Magic)`, pre-verified to fail `R2_Targeting_ExtraTargets137_Cover171PhysicalOnly_Breath_AndMultiPassiveSummon`).
  - **Canary Caught?** **YES** — auditor reported `SP11` with verbatim disassembly `00420b70..00420b77` (`byte [ecx+0x79] == 0` skips Cover on Magic). Round 1 is **VALID**.
- **Sampled Items (15 total = 12 catalog + 3 real `TextTrace` packets):**
  - `core_combat`: `CC19`, `CC17`, `CC08`
  - `status_procs`: `SP13`, `SP11` *(canary)*, `SP10`
  - `effects_passives`: `EF031`, `EF070`, `EF278`
  - `units_ai_loaders`: `UL01`, `UL03`, `UL07`
  - `trace_event`: `TR-20261122-b0-t10-damage-D2>7=48` (**PASS**), `TR-20261122-b0-t18-hit-H2>6=1` (**PASS**), `TR-20261122-b0-t18-turn_end` (**PASS**)
- **Adjudicated Non-Canary Findings:** **0 `S0`**, **3 `S1`**, **4 `S2`** (all distinct root causes; Circuit Breaker NOT tripped, `1/3` consecutive failed rounds):
  1. **`UL07` (`S1` — FIXED):** `Battle.IsSequentialPattern` shifted 0-based `Pattern` by +1 (`1,2,3` vs `0,1,2`), misclassifying 54 Skills & 672 EnemyAttacks with `pattern==3` (`flag10=0` at `0041e194`/`0041a5f1`) as sequential. Fixed to exact 0-based binary cases (`Skill`: `0,1,2,7,8,9,15`; `Atk`: `0,1,2`).
  2. **`SP13` (`S1` — FIXED):** Arcane Shield `447` called raw `LoseHp` instead of Skill `240` (`0xf0`, `0042525b..0042531b`), bypassing its `500` damage cap (`Effect 296`), exclusive barriers (`101/102/181`), Alter Fate (`349`), and Endure (`254`). Fixed to cap at `500` and execute through `Voided` + `TakeDamage` with `inCounter=true`.
  3. **`CC17` (`S1` — FIXED):** Missed damaging spell with Effect `87` (`Soul Eater`) bypassed the Race 5/6 early-return (`0044f0c2` sets `hitStatus=4`), popping Magic Barrier `183` and rolling `AfterHit` Instant Death `119`. Moved Effect `87` Race 5/6 early return immediately before `if (!landed)`.
  4. **`CC19` (`S2` — FIXED):** Effect `103` + Effect `9` (Fixed Heal) skipped `Rand(5)` RNG draw (`0048d873`) and `295`/`317` heal cap (`0048d922`). Fixed to always draw `Rand(5)` and cap fixed heal via `295`/`317`.
  5. **`SP10` (`S2` — FIXED):** Multi-bearer Warning Shot `259` kept rolling after a miss (`004371c3` exits State 9 on first proc), and inline Shadow Sew `123` omitted `target.St[123] == null`. Fixed both.
  6. **`UL03` (`S2` — FIXED):** `Scenario.GuestUnit` (`Scenario.cs:569`, called by `Jobs.cs:258`) omitted `leaderSealbook` (`0x4ff530`). Added `leaderSealbook` to `GuestUnit` and `guestTemplates` cache key.
  7. **`EF278` (`S2` — FIXED):** `Action.SkillEffects` baked `278`/`353` statically into `168` speed buff instead of dynamically checking caster `CanFight()` (`0x483a20`/`0x48bf90`). Moved `168` Maid bonus evaluation dynamically to `Battle.Wait()`.
- **Regression Test:** `BinaryConformityTests.Phase4_Round1_VerifiedFixes_UL07_SP13_CC17_CC19_SP10_UL03_EF278`.
- **Round 1 Verdict:** **FAIL (0 S0, 3 S1, 4 S2 — all fixed; canary caught; 3/3 trace events exact PASS)** -> **Round 2 required** with 15 brand-new unsampled items + fresh canary.

---

## Round 2 — 2026-11-22 (Seed `20261123`)

- **Isolated Clean-Room Copy:** `p4_r2_isolated` (rebuilt from `483e6df` with all `docs/binary_spec/`, `FORMULAS.md`, `engine_conformity.json`, and test suites physically removed).
- **Auditor:** `p4-r2-auditor` (`gemini-4-neon-high`, fresh no-fork session, read-only).
- **Secret Canary:** Planted on `EF275` (`Battle.cs:ApplyItemMastery` mutated to return `PyMath.Int(value)` ignoring `mastery`, pre-verified to fail `Phase3_Wave2C_AutoGuardCover_Barriers_Arrows_Items_And_LeaderSealbook`).
  - **Canary Caught?** **YES** — auditor flagged `EF275` (`S0` mutation in isolated copy) with verbatim binary VAs `0x50e789`, `0x50ead5`, `0x50edfc`, `0x50f234`. Round 2 is **VALID**.
- **Sampled Items (15 brand-new items, 0 overlap with Round 1 = 12 catalog + 3 real `TextTrace` packets):**
  - `core_combat`: `CC18` (**PASS**), `CC06` (**PASS**), `CC20` (**PASS**)
  - `status_procs`: `SP09` (**PASS**), `SP02` (**1 synthetic `S2` edge — FIXED**), `SP16` (**PASS**)
  - `effects_passives`: `EF275` *(canary — caught)*, `EF283` (**PASS**), `EF152` (**PASS**)
  - `units_ai_loaders`: `UL02` (**PASS**), `UL04` (**PASS**), `UL12` (**PASS**)
  - `trace_event`: `TR-20261123-b0-t7-damage-D6>4=6` (**PASS**), `TR-20261123-b0-t4-hit-H1>7=1` (**PASS**), `TR-20261123-b0-t6-turn_end` (**PASS**)
- **Adjudicated Non-Canary Findings:** **0 `S0`**, **0 `S1`**, **1 synthetic `S2`**:
  1. **`SP02` (`S2` — FIXED):** Trump Card (`48`) overwrites `delta[DEF] = -10000` (`0x4fbffb`) rather than subtracting `10000` (reachable only if synthetic `Base[DEF] + DEF_buff > 10000`). Updated `Units.cs:414` to `total = b - 10000`.
- **Round 2 Verdict:** **CERTIFIED PASS (0 S0, 0 S1, 1 synthetic S2 fixed; canary caught; 6/6 real battle trace events exact PASS across Rounds 1–2; 24/24 catalog items audited without replacement)** -> **Engine Certified; proceed to Phase 5.**

---

## Round 3 — 2026-11-23 (Seed `20261124`) — Post-Wave 3 Strict Certification

- **Isolated Clean-Room Copy:** `p4_r3_isolated` (rebuilt from `0ee8aaa` after closing all remaining Phase 3 Wave 3 gaps: `0x40` infinite item bit 6, per-slot Cover `171`, enemy Ally-Heal AI, Sleep-decay, `f32` forge/specialty stats, `SetFront`, and battle Pep; all `docs/binary_spec/`, `FORMULAS.md`, `engine_conformity.json`, and test suites physically removed).
- **Auditor:** `p4-r3-auditor` (`gemini-4-neon-high`, fresh no-fork session, read-only).
- **Secret Canary:** Planted on `CC13` (`Battle.cs:MagicValue` mutated to drop `action.Has(47)` RES substitution, pre-verified to fail `R3_Recheck_DamageRowFilters_Magic47_88_87_RaceGuard_ElbowGrease_AndArcaneCounter`).
  - **Canary Caught?** **YES** — auditor flagged `CC13` (`S0` mutation in isolated copy) with verbatim disassembly `0044dc50..0044dc8e` and exact `Prism Dawn` repro. Round 3 is **VALID**.
- **Sampled Items (15 brand-new items, 0 overlap with Rounds 1–2 = 12 catalog + 3 real `C18` `TextTrace` packets):**
  - `core_combat`: `CC16` (**PASS**), `CC03` (**PASS**), `CC13` *(canary — caught)*
  - `status_procs`: `SP01` (**PASS**), `SP15` (**PASS**), `SP04` (**PASS**)
  - `effects_passives`: `EF340` (**PASS**), `EF357` (**PASS**), `EF133` (**PASS**)
  - `units_ai_loaders`: `UL09` (**PASS**), `UL11` (**PASS**), `UL06` (**PASS**)
  - `trace_event`: `TR-20261124-b0-t3-damage-D4>8=142` (**PASS**), `TR-20261124-b0-t3-hit-H4>8=1` (**PASS**), `TR-20261124-b0-t1-turn_end` (**PASS**)
- **Adjudicated Non-Canary Findings:** **0 `S0`**, **0 `S1`**, **0 `S2`** (11/11 catalog items PASS + 3/3 real battle trace events exact PASS).
- **Round 3 Verdict:** **STRICT CERTIFIED PASS (0 S0 / 0 S1 / 0 S2; 3/3 canaries caught; 36/36 catalog items audited without replacement + 9/9 real battle trace events exact PASS across Rounds 1–3).**

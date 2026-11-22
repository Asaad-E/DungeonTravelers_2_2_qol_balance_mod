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

# Skills with many "hurts": causes and tested fixes

Method: `dtcli skill-trace` (new: counts casts, recasts on an active status, real turn intervals, hit rate, actions of the role
with the status on and off) and `dtcli skill-rule-trial` (new: `one-skill-trial` with the rule condition set by hand). Every figure
below is N=1000 per boss on the 16 bosses of the brief (`C10;C13;C15;C18;C22;C26;C28;C29a;C30;C34;C36;C37;C39;C40;P08;P18`), same
seeds with and without the skill, against the current state (`build/engine_snapshot.json`). Columns: mean change in wins (points),
bosses worse / better by 3 points or more, mean change in length of won fights (+ is longer), cells hurt / cells that serve
(the battery's own test, applied per boss). Scripts: `scratch/hs/run_rules.py`, `scratch/hs/run_fixes.py`; raw results `scratch/hs/*.json`.

## Common finding

The battery plays every non-damage skill with the rule `always / status:X`, placed before the role's first damage row. For a
single-target buff of 5 to 10 turns that makes the caster recast it as soon as any ally lacks it, so the caster stops attacking.
The engine does not recast on an active status (0 to 5% of casts land on a status already carried, never on a single target in
the traces, except Berserk at C26, 10%), and the effects are modelled as the program reads them. Changing only the rule condition
(first turns, party hurt) removes most of the hurt:

| Skill | always: wins / length / hurt cells | turn_at_most:3 | other rule |
|---|---|---|---|
| Accelerator | -4.9 / +40.6% / 13 | -0.3 / +4.9% / 9 | enemies_at_least:3 0.0 / +1.4% |
| Amplify | +0.2 / +7.4% / 4 | 0.0 / 0.0% / 0 | |
| Aim | -0.8 / +1.9% / 8 | -0.4 / +1.2% / 2 | enemies_at_least:3 0.0 / +0.3% |
| Barrage Rondo | -0.1 / -2.7% / 0 | +0.2 / -1.0% / 0 | |
| Catalina | +0.7 / +16.3% / 6 | +1.2 / +3.9% / | party_hp_below:0.6 +1.2 / +0.9% / 0 |

Hypothesis 3 (SP taken from a better skill) is ruled out: the trial adds the skill (`extra_skills`), nothing is displaced.

## Per skill

### Accelerator (197), magical princess: policy artefact + real weakness

* Evidence (C36, 100 traced battles): 14.6 casts and 14.2 chants per battle; 68% of the princess's turns go to Accelerator, so
  her damage is gone (fights +67% at C10, wins 71% -> 29% at C36). Buffed units wait 0.413 before their next turn against 0.512
  unbuffed (-19%; C26: 0.488 vs 0.642): the effect is modelled right.
* Even without the bot behaviour it is worth nothing: one ally, +25%, 5 turns is +1.25 actions for about one spent. The siblings
  Circle Brave / Circle Protect (161, 162) hit all allies for 22 TP; Accelerator hits one for 27.
* Fix (data, sheet Changes: target 5 -> 8 "all allies", values x1.6 or x2, turns 5 -> 8):

| Variant | rule | wins | length | cells hurt / serve |
|---|---|---|---|---|
| current | always | -4.9 | +40.6% | 13 / 0 |
| all allies, same values | always | -0.2 | +4.8% | 8 / 1 |
| all allies, x1.6, 8 turns | always | +0.6 | -2.9% | 2 / 8 |
| all allies, x1.6, 8 turns | turn_at_most:3 | +0.7 | -2.2% | 2 / 5 |
| all allies, x2, 8 turns | always | +1.3 | -5.2% | 1 / 10 |
| all allies, x2, 8 turns | turn_at_most:3 | +0.7 | -4.0% | 2 / 9 |

  The brief's earlier change (chant 1.5x, turns 8, single target) stayed in the bot trap. Even x3 for 10 turns on all allies only
  reaches -9.9% length (+1.6 wins): the skill cannot turn into an excess of power. Recommended: all allies, x1.6, 8 turns
  (target and values are in the benign / structural classes L12, L13: a vanilla Magic with the all-allies target and a status
  effect already exists, Circle Brave).

### Berserk (5), attacker: real weakness, faithful to the program

* The program reads effect 26 as the first found among the action's effects, then the user's statuses (`docs/FORMULAS.md` 2.2 and
  the lists paragraph, `EFFECT_COVERAGE.md` row 26): a skill with its own power hides Berserk's +50%. Raging Smash, Frost Slash,
  Moonlight Purgatory, Onikagura and Armor Penetration all carry their own 26. Trace (attacker with Berserk on): C36 Moonlight
  Purgatory 846, Attack 111, Raging Smash 46; C26 Raging Smash 302, Moonlight Purgatory 251, Attack 139. The +50% reaches only the
  plain attack (13% of the actions) and skills with no 26 (Aura Eliminate); the DEF -25% (effect 28, read on the target) counts on
  every blow received, and a cast costs a turn and 16 TP.
* The role already has a rule `status:26` in its policy, so the rule variants do not matter (all identical, +6.5%).
* Fix tested: only the program can make it count for skills. What-if in the engine (modifier of the skill + Berserk's added; the switch
  was removed afterwards, the figures stay as measured):

| Variant | wins | length | cells hurt / serve |
|---|---|---|---|
| current | -0.5 | +6.5% | 13 / 0 |
| DEF cost x0.2 only | -0.1 | +5.5% | 11 / 1 |
| ATK adds to skills (program patch) | +1.0 | -10.2% | 0 / 16 |
| ATK adds to skills, DEF cost x0.6 | +1.2 | -10.2% | 0 / 16 |
| data only: effect 26 -> 161 (slot shared with War Cry and Circle Brave) | -0.2 | +0.1% | 3 / 3 |

  Lowering the DEF penalty does not help; the 161 swap is neutral and makes Berserk and the party buff overwrite each other.
  The only good fix is an executable patch (two program files), which needs approval. Recommended if approved: the patch with the
  DEF cost kept.

### Amplify (198), sage: real weakness (max HP only) + bot

* The program adds max HP, it does not heal (`EFFECT_COVERAGE.md` row 172). In the traces the current HP only rises because the
  Carol song fills the new room at the end of the turn (restore +264 on the same turn). Without that, it is a buffer for 10
  turns, for 45 TP and about 2 turns of the sage (she casts 10.4 per battle at C36, 8% of the party's actions).
* The sage's own rules put two buffs before it, so `turn_at_most:3` never reaches it (results identical to no skill).
* Fix: target all allies (as Sun Veil, Circle Protect): wins +1.1, length +1.2%, cells hurt 0 / serve 4 (current: +0.2, +7.4%,
  4 / 2). TP x0.6 on top changes nothing (+1.1, +0.9%, 1 / 4).

### Aim (35), shooter: real weakness, nothing to gain

* Hit chance is `0.885 * (100 + DEX) / (100 + AGI)` plus skill accuracy, capped at 100 (`FORMULAS.md` 2.1). With the reference party
  the shooter already hits 97.6 to 100% (with Aim up) on 12 of the 14 bosses measured (e.g. C40: 99.3% without Aim, 97.6% with it;
  C36 100/100); P08 is 95.5% and only C28 is evasive (79.7% even with Aim). Aim buys a turn and 28 TP for nothing at these checkpoints.
* The cast is cheap (2 to 2.5 per battle), so the hurt is small: -0.8 wins, +1.9% length, 8 cells.
* Fix tested: add a second effect, critical rate (31, status on the user):

| Variant | rule | wins | length | cells hurt / serve |
|---|---|---|---|---|
| current | always | -0.8 | +1.9% | 8 / 1 |
| + crit 30 points at L10 | always | -0.3 | -0.3% | 3 / 5 |
| + crit 30 points at L10 | turn_at_most:3 | -0.2 | -0.8% | 2 / 3 |

  Removes most of the hurt but does not make it positive; a bigger change (what Aim gives) is a design decision.
* Critical rate is weak in the engine: crit factor 1.25 and the rate is capped at 50, so +30 points are worth at most +7.5% damage.
  The hit chance of the shooter over 72 bosses is 97.3% on average (14 below 95%): accuracy gains 2.7 points at most.
* Second fix, a damage multiplier in the slot of Power Charge (191, added to the "other" bonus of the final blow, so it does not
  overwrite War Cry or Circle Brave), accuracy kept:

| Variant | rule | wins | length | cells hurt / serve |
|---|---|---|---|---|
| accuracy + crit 3 - 30 | always | -0.3 | -0.3% | 3 / 5 |
| accuracy + damage +10% - +30% | always | +0.5 | -7.3% | 0 / 14 |
| accuracy + crit + damage +10% - +30% | always | +0.8 | -10.2% | 0 / 16 |
| accuracy + damage +5% - +20% | always | +0.1 | -4.7% | 0 / 8 |

### Barrage Rondo (206), maid: song slot, small real effect

* Rondo only switches the multi-hit skills (effects 89 to 100) to their second table of hit counts, +9 to +15% hits on those skills,
  nothing on plain blows and Double/Triple Attack (`EFFECT_COVERAGE.md` row 210, `FORMULAS.md` 12.2).
* It is a song and the maid has one song slot: with it up she cannot sing Carol or Lightning March. C26, 100 battles, maid actions while
  Rondo is up: Cook 556, Attack 277, Carol 50; while it is not: Carol 130, Rondo 101, Cook 165, Attack 57. With the slot taken she
  falls back to Cook and plain blows, and the party loses the Carol heal.
* On these 16 bosses the hurt is already 0 cells (-0.1 wins, -2.7% length): the 23% of the battery comes from other cells.
* Optional fix tested (second effect, party ATK 161 while the song lasts): +10% -> -4.8% length, 7 cells serve; +20% -> -9.9%, 14
  cells serve, wins +0.1. A design decision.

### Catalina (97), dolls: policy artefact

* The cell casts it with `skill:Catalina` always: 9.5 casts at 48 TP per battle at C36, 7.0% of the party's actions, filling the
  doll slots and the TP of the role, so fights are +16.3% longer (6 cells hurt).
* The standard role never uses it (SIM_AUDIT: "no rule of the role uses it", the doll rule fills Spartan first).
* With a trigger a player would use (`party_hp_below:0.6`): wins +1.2, length +0.9%, 0 cells hurt, 4 serve, 3 bosses better by
  3 points or more. Fix: a policy row for the dolls role (sheet Policies of `sim_setup.xlsx`), no change to the game. TP 48 -> 36
  (the brief's test) is not needed.

### Armor Penetration (11), attacker: dead, not hurting

* Battery: 0% hurt, 60% same, 4% serve ("dead"): the policy never picks it. Its damage per time is 38 to 44% of Moonlight Purgatory
  (SIM_AUDIT) and the policy does not value its DEF -38% for 4 turns on the target, which helps the whole party.
* Forced (`skill:Armor Penetration`): `always` -0.9 wins, +3.6% length (it displaces the better skills); `turn_at_most:3`
  (once at the start) +0.3 wins, -1.5% length, 4 cells serve / 1 hurt; with ATK +30% at every level: +0.4, -2.2%, 6 / 1.
* Fix: a policy row on bosses (`turn_at_most:3`, `skill:Armor Penetration`) is enough for it to serve; +30% damage is optional.

## Decisions (2026-10-29) and result

| Skill | Decision | Applied in |
|---|---|---|
| Accelerator | all allies, x1.6 (27% - 40%), 8 turns | rows V006 - V015, Y020 |
| Amplify | all allies | row Y021 |
| Aim | damage +10% to +30% added (accuracy kept; the critical rate version is replaced) | row Y022, sheet Policies (shooter) |
| Catalina | rule `party_hp_below:0.6` for the dolls role | sheet Policies, sim_setup.xlsx |
| Armor Penetration | rule `turn_at_most:3` for the attacker role | sheet Policies, sim_setup.xlsx |
| Berserk | no change: the executable is not patched (stacking modifiers could break other fights) | |
| Barrage Rondo | not applied, see below | |

Skill battery after the build (hurt share of the cells, before > after): Accelerator 50% > 11% (serve 5% > 10%), Amplify 33% > 7%
(serve 2% > 13%), Aim 26% > 6% (serve 2% > 13%, the battery plays it with `status:166`), Armor Penetration dead (60% same) > niche (serve 8%, hurt 6%). Berserk 33% > 26% and Barrage Rondo 23% >
25% are not changed by any row (noise of the scan). Catalina stays at 29% because the battery forces it with its own rule `always`;
the new rule serves the role in play only. Class stages: 67 of 76 rows within the band, as before; class balance: 14 of 16 classes in the
band, as before; 197 tests pass.

### Barrage Rondo, Diva against the band

Only the Diva learns it (class 23). `rondo_diva_chart.png` (images are not kept in git; made by `scratch/hs/rondo_plot.py`): class-balance of the final classes (400 parties a boss, 10 runs a cell),
the Diva with the song in place of Lightning March (she holds two songs):

| Diva | wins | speed of one member |
|---|---|---|
| current, no Rondo | 88.1% (+2.4 sd) | x1.28 |
| Rondo as it is | 87.0% | x1.06 |
| Rondo, party ATK +10% | 86.9% | x1.15 |
| Rondo, party ATK +20% | 87.2% | x1.20 |
| Rondo +20% in place of Carol | 68.9% | x0.67 |

The song does not raise the Diva: she gives up March, and she is already above the band (too strong) before it. Not applied.

## Tooling

`engine_cs/src/DtEngine/Suite/SkillTrace.cs` (`skill-trace`, `skill-rule-trial`, registered in `Registry.cs`) and observer hooks in
`Trace.cs`. Scripts: `scratch/hs/run_rules.py`, `run_fixes.py`, `rondo_chart.py`, `rondo_plot.py`.

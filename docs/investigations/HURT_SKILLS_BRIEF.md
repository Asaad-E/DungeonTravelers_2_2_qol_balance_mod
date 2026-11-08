# Investigation brief: skills with many "hurts"

Skills: **Accelerator, Berserk, Amplify, Aim, Catalina, Barrage Rondo, Armor Penetration**.

## Context (2026-10-25)

`docs/generated/SKILL_BATTERY.md` gives these skills a high hurt rate (with the skill the party wins less or fights longer):

| Skill | Id | Role tested | Hurt (battery) | Notes |
|---|---|---|---|---|
| Accelerator | 197 | magical princess | 50% | +25% ally speed, 5 turns, speed 1.41x, chant 2.5x (res) |
| Berserk | 5 | attacker | 33% | ATK +50% / DEF -25%, 8 turns, speed 1.77x |
| Amplify | 198 | sage | 33% | ally max HP +47%, speed 1.82x, TP 45 |
| Aim | 35 | shooter | 26% | own accuracy +30%, speed 1.46x |
| Barrage Rondo | 206 | maid | 23% | song, multi-strike chance, chant 1.4x (int) |
| Catalina | 97 | dolls | 30% | heal doll, TP 48 |
| Armor Penetration | ? | ? | ? | not yet looked at |

## What was already tried (and failed)

Hypothesis: "the turn spent casting is too slow". Tested with `scratch/hurt_skills_trial.py` (one-skill-trial, 16 bosses
`C10;C13;C15;C18;C22;C26;C28;C29a;C30;C34;C36;C37;C39;C40;P08;P18`, N=1000, modified snapshot). Results in
`scratch/hurt_skills_results.json`, report `scratch/hurt_skills_report.py`:

| Skill | Change | Hurt before > after | Wins delta | Won fights shorter |
|---|---|---|---|---|
| Accelerator | chant 2.5x->1.5x, turns 5->8 | 94% > 94% | -4.9 > -4.2 | -40.6% > -36.6% |
| Berserk | speed 1.77x->1.2x | 94% > 100% | -0.5 > -0.9 | -6.5% > -8.2% |
| Amplify | speed 1.82x->1.2x, TP 45->30 | 44% > 75% | +0.2 > -0.1 | -7.4% > -9.0% |
| Aim | speed 1.46x->1.0x | 62% > 75% | -0.8 > -0.9 | -1.9% > -2.9% |
| Barrage Rondo | chant 1.4x->1.0x | 0% > 0% | -0.1 > -0.1 | +2.7% > +2.6% |
| Catalina | TP 48->36 | 75% > 69% | +0.7 > +0.5 | -16.3% > -18.5% |

Conclusion: action speed / chant is NOT the cause. Accelerator makes fights 40% longer, which is suspicious (possible model bug).

## Open hypotheses to check

1. **Policy over-use**: the AI (`engine_cs/src/DtEngine/Policy.cs`) recasts the buff while it is still active, or casts it instead of attacking every turn.
2. **Effect mis-modelled**: effect ids 168 (Accelerator, in `SPEED_BUFFS` of `Battle.cs`), 26/28 (Berserk), 172 (Amplify: does max HP raise current HP?), 166 (Aim), 210 (Barrage Rondo), 230 (Catalina) may be applied wrong, with the wrong sign, or not at all. Compare with the exe/notes (`docs/generated/EFFECT_COVERAGE.md`, `SIM_AUDIT.md`).
3. **Measurement artefact**: the one-skill-trial compares "learns the skill" vs "not"; SP spent on the skill may come out of a better skill.
4. **Armor Penetration**: find its id, roles and battery row; same checks.

## Useful commands

- Trace one fight: `dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll trace ...` (see `Program.cs`, `case "trace"`).
- Trial: `dtcli.dll one-skill-trial "<role>" "<Skill>" "<bosses ; separated>" <N> --snapshot <file> --root .`
- Skill data: `build/engine_snapshot.json` -> `sides.variant.skills[id]` (fields `speed`, `cast`, `tp`, `turns`, `effects`).
- Changes go to `data_tables/balance_changes.xlsx` (sheet Changes), never to generated files.

## Deliverable

For each skill: cause (policy / model bug / real weakness / measurement), evidence (trace excerpt or numbers), and a fix
(engine fix or data change) tested with N>=1000 on the 16 bosses. Do not commit balance changes without approval.

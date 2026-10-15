# engine_cs: the battle engine in C#

A 1-to-1 port of the battle side of `sim/` (battle loop, party policy, enemy AI, formulas, units, the building of a party and
its enemies, the guest allies, the runs of a checkpoint and the measures around a battle). It reads one snapshot of the data
written by Python (`tools/engine_export.py`) and holds no value of the mod. `sim/` stays the reference: the parity tests play the
same cases in both and compare the traces.

| Folder | What it holds |
|---|---|
| `src/DtEngine` | the library: `PyRandom` (CPython's generator), `Formulas`, `Units`, `Battle`, `Policy`, `Ai`, `Scenario`, `Measures`, `Jobs`, `Trace` |
| `src/DtEngine.Cli` | the command-line program `dtcli` (server garbage collector: `runtimeconfig.template.json`) |
| `tests/DtEngine.Tests` | xunit tests: generator, formulas, rounding, snapshot, templates, guests, measures, traces of a few fixed cases |
| `parity/` | the Python side of the parity tests (traced runs of `sim/`, the case generators, the comparison, the speed test) |
| `parity/cases/failing` | cases that did not match, saved with all their inputs; replay with `run_parity.py replay` |
| `parity/cases/regression` | cases that once failed (or are kept for good); played by every `corpus` run |

`tools/engine_client.py` is the bridge for the Python tools (see below).

## Commands

```bash
python tools/engine_export.py                                   # the snapshot: build/engine_snapshot.json
dotnet build engine_cs/src/DtEngine.Cli -c Release              # the program: engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll run --snapshot build/engine_snapshot.json --jobs jobs.json --out results.json [--threads N] [--trace-out trace.txt | --trace-digest digest.txt]
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll measure --snapshot build/engine_snapshot.json --jobs measures.json --out results.json [--threads N]
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll trace --snapshot build/engine_snapshot.json --job job.json --out trace.txt [--level 1|2]
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll profile --snapshot build/engine_snapshot.json --jobs jobs.json [--repeat N]   # time, bytes allocated and by which types, on one thread
dotnet test engine_cs                                           # the xunit tests

python engine_cs/parity/rng_golden.py                                         # golden files of the generator, of the formulas and of round(x, n) (the tests write them when missing)
python engine_cs/parity/formulas_golden.py
python engine_cs/parity/round_golden.py
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll check-rng build/engine_rng_golden.json
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll check-formulas build/engine_formulas_golden.json
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll check-round build/engine_round_golden.json

python engine_cs/parity/run_parity.py corpus --seeds 20261005,7,123456 --runs 2 --fixed   # the fixed corpus (add --only smoke for a few cases)
python engine_cs/parity/run_parity.py random --count 3000                     # new random cases; prints the seed of the generator
python engine_cs/parity/run_parity.py directed                                # one case for each skill, enemy, formation, item, enchantment, piece of gear, guest ally, summon, enemy attack, heal and status, and made-up AI scripts
python engine_cs/parity/run_parity.py replay engine_cs/parity/cases/failing/x.json
python engine_cs/parity/run_parity.py determinism                             # sim/ against itself, in two sets of processes
python engine_cs/parity/run_measures.py --count 150                           # expedition, play_checkpoint, check_change, walked_zones against sim/
python engine_cs/parity/coverage_run.py --count 1500 --corpus --directed --measures 12   # which lines of sim/ the cases reach
python engine_cs/parity/bench.py [--threads 1,4,12] [--cli earlier/dtcli.dll]  # battles per second of both engines
python -m unittest discover -s engine_cs/parity -p "test_engine_client.py"   # the bridge against sim/
```

The corpus is every checkpoint of the setup on both sides with the reference party, the parties of `measures/win_rates.py` at
its 17 bosses, every fixed battle of the game (with `--fixed`, which also plays every guest ally at three checkpoints and the
arguments `unique_level` and `passives`), and the cases of `parity/cases/regression`. A random case is a random party (roles of
the sheet Roles, a level near a random checkpoint or near the enemies, sometimes skills, enchantments, items, other gear, guest
allies, passives, rules of the policy or flags of the data added on top of the plan) against a random fixed battle or random
formations of a random floor zone.

`dump_jobs.py` writes all of these jobs to one file. After a change that must not change a result (an optimisation), run that
file through `dtcli run --trace-digest` before and after and compare the digests with `dump_jobs.py --check`: the C# engine is
then checked against itself on some 12,000 jobs in seconds, and `run_parity.py` against `sim/` once at the end.

## Jobs

A job (JSON) is a side (`vanilla` or `variant`), a party (the checkpoint whose chapter, gear and crown bonus it takes, a list
of roles or `null` for the composition of the setup, a level or `null` for the reference level), the enemies, a number of runs
and a seed. Run `k` of a job plays with the generator seeded `seed + k`, as `sim.scenario.play` does. The results hold, for each
run, the figures of `sim.scenario.play` (`won`, `lost`, `time`, `actions`, `lowest_hp`, `enemy_damage`, `enemy_actions`,
`party_max_hp`, `hp_left`, `tp_left`, `alive`, and `parts`, one per fight) and the figures of `sim.measures.summary` for the job.

The enemies (`enemies.kind`): `checkpoint` the fixed battles of the checkpoint; `fixed` a list of `[floor, number]`; `zone`
random formations of a floor zone, a number of battles; `formation` a list of `[zone name, index]`; `enemies` a list of
battles, each a list of `[enemy id, front]` or `[enemy id, front, {script, attacks, passives}]` (a script of the format of the
snapshot, a list of attack ids, passive attacks added).

More fields of a job: `kit`, `bag`, `extra_skills`, `extra_enchants` (given to every member), `options` (settings of the battle),
`policies` (rows of the sheet Policies added for this job), `settings` (settings of the model set for this job), `flags` (`survival_guard`, `interrupt_product`, `arcane_chance` of the
data), and in `party`: `guest` (`none` for the members alone, or the name of a guest ally, who takes the place of the summon at the
stage of her growth for the level of the party, as `measures/mercenaries.py` does), `unique_level`, `passives` and `pieces`
(arguments of `build_member` and the gear of the roles, given to every member).

## Measures

`dtcli measure` plays the measures of `sim/measures.py` and `sim/scenario.py` that go around a battle, from a file of jobs
`{id, measure, side, ...}`: `expedition` (`floor`, `level`, `cid`, `roles`, `battles`, `runs`, `kit`), `play_checkpoint` (`cid`,
`runs`), `check_change` (`checkpoints`, `runs`; `side` is the data before the change, `changed_side` the data after), and
`walked_zones` (`floor`, `level`; the result is the names of the zones). The figures are the same as Python's value by value.

## Bridge for the Python tools

`tools/engine_client.py` exports the snapshot when it is stale, builds `dtcli` when a source is newer, runs it and gives back the
dictionaries of `sim.scenario.play`, `sim.measures.summary` and `sim.measures.play_checkpoint` (a result has no `record`: the
recorder of the battle is not ported). No tool uses it yet.

## Trace

One line per turn: the time, the actor, the events of the turn (the action, each hit, damage, healing and loss of HP), the HP, TP,
state and next turn of every unit, and the count of 32-bit words the generator has given (a draw of `random()` takes two).
Level 2 adds every draw. A header describes every unit before the battle starts.

## Not ported

The recorder of a battle (`result['record']`: damage, healing, skill uses by unit), which `tools/class_stages.py`,
`tools/sim_audit.py` and a few scripts of `measures/` read; `measures.slot_share`, `measures.weapon_band` and `measures.touched` (and
`GameData.with_changes`), which nothing calls; the analysis calls on a `Battle` made by hand (`expected_damage`, `time_of`) that
`tools/sim_audit.py` and `tools/skill_worth.py` use to score options; the tools that change the data or the sheet Policies in their
own process (`measures/mercenary_trial.py`, the trials that patch `Battle` methods). The parties that those tools build by
replacing a member with a "tested" one are built in the tools, not in `sim/`: a job gives the reference party, the guest ally, the
extra skills and the other fields above.

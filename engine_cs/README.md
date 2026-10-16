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

## The measures in C# (`dtcli suite`)

Every measure of the project that plays battles runs in `src/DtEngine/Suite`: the choice of cells, the parties and their recipes, the jobs, the
aggregation and the report writers, with the same outputs, at the same paths, as the Python script each one stands for (which stays as the reference).
A measure reads what it needs of the workbooks from the section `measures` of the snapshot (`tools/engine_export.py`: sheets as rows, the constants of
the scripts, the rows of balance_changes.xlsx that name a boss, the maps, the meals); it holds no value of the mod.

```bash
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll suite [--only a,b] [--threads N] [--snapshot S] [--root R]     # every measure, in parallel
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll difficulty-curve                                              # one measure alone
python engine_cs/parity/gate_suite.py          # the suite against the files of the last commit (git diff --ignore-cr-at-eol: none left)
python engine_cs/parity/gate_trials.py         # the trial commands against their Python scripts
```

The measures: `difficulty-curve`, `party-battery`, `class-stages`, `skill-value`, `skill-ailments`, `boss-fit`, `skill-worth`, `guide-curve`,
`sim-anchors`, `sim-audit` (passives, usage, actives), `win-rates`, `mercenaries`, `party-skills`, `postgame-compare`, `unique-skills`,
`skill-value-contested`, `random-battles`, `regression-r04`, `boss-rows-check`, `design-rows`, `support-chains`, `support-stages`. They start
together; one that reads the files of another waits for it (`boss-fit` for `difficulty-curve`, `regression-r04` for `party-battery`,
`skill-value-contested` for `skill-value`). `python tools/full_suite.py` exports the snapshot, runs `dtcli suite`, then the checklists that play no
battle and the tests, which stay in Python.

The trial scripts of measures/ are commands too, with the arguments of their script and the lines it prints: `curve-recheck`, `etoile-dances`,
`magic-wall`, `measure-open-rows`, `samba-trial`, `etoile-trial`, `dance-trial`, `def-debuff-trial`, `sage-buffs-trial`, `provoke-trial`,
`boss-trim-trial`, `grand-sealbook-trial`, `lize-ideas`, `mercenary-trial`, `one-skill-trial`, `tp-items-trial`, `worth-with-weapon`. The data a trial
changes (a value of a skill, an item, a guest, a sealbook, a column of a role, rows of policies) is changed in C# on a copy (`Suite/Kit.cs`).
`rows-trial` and `curve-ablation` need the game built from other rows of balance_changes.xlsx than the variant of the snapshot: `python
tools/engine_sides.py rows P031,P032` or `ablation` writes those sides to build/engine_extra_*.json and `--extra <file>` brings them in.

`Suite/Py.cs` holds what Python does that the reports depend on and C# does not: `%.nf`, `:.n%` and `repr` of a float, `statistics.mean` and
`median`, `json.dump` with and without `indent`. `dtcli check-pyformat build/engine_pyformat_golden.json` compares them with Python on some 25,000
cases (`parity/py_format_golden.py` writes the file; `dotnet test` does both).

## Bridge for the Python tools

Historical: the Python measures played their battles here before every measure moved into `src/DtEngine/Suite`. It is
kept with the Python scripts as the reference they were proven against; measures are run with `dtcli`.

`tools/engine_client.py` exports the snapshot when it is stale, builds `dtcli` when a source is newer, runs it and gives back the
dictionaries of `sim.scenario.play` (with `record` when the job says `record: true`), `sim.measures.summary` and
`sim.measures.play_checkpoint`. A side (a `GameData`) or a setup (a `Setup`) that the snapshot does not hold, because a tool changed it
in its own process, goes with the call: `side_of(data)` and `setup_of(setup)` give the name to put in a job (`vanilla` and `variant` when the
snapshot holds the same content; the content is compared by hash), and the engine reads the others from a second file (`--extra`).
The tools that play on the engine are listed in `engine_cs/parity/gate_tools.py`, each with a gate that compares it with its Python path.

## Recorder

A job with `record: true` gets, for each battle (`parts[k].record`), the tables of `sim.battle.Recorder` (damage, healing, actions,
skill uses, TP spent, items used, chants, performances broken, turns lost, denied, delayed, largest hit, deaths, kills) with the units
that name them (position, name, kind, side, role, owner, level); `result['record']` is that of the first battle, as in `sim.scenario.play`.
The trace carries one line `C ...` after the `E` line of each battle, so the parity tests compare the recorder with every case.

## Party recipe, enemies and more fields of a job

`party.recipe` says what a tool does to the reference party of the checkpoint: `bonuses` (hp, tp, resist, stats on the first members),
`bag_set`, `name_not` / `role_not` / `drop_last` / `first` (which members stay), `drop_others` (no summon), `tested` (members built by role:
`role`, `character` or the first of the preference not in the party, `level`, `crown`, `forge`, `extra_skills`, `unique_pieces`,
`no_unique`, `passives_add`, `pep`), `place` (`append` or `replace_role`) and `items` (`first_kept`, `all_first`). The characters the tested
members were given come back as `tested`. `enemies.kind: chain` (`zones`, `seed`, `battles`) draws rows of random battles from one generator
shared by all the runs, in the order they are played. Also: `setup` (a name from `setup_of`), `policy_rows` (the whole sheet Policies for the job),
`enemy_changes` (stats of enemy records) and `flags`.

`dtcli measure` also plays `skill_scores` (the options of a member scored by damage per time and TP, the analysis of `tools/skill_worth.py` and
`tools/sim_audit.py` usage) and `probe` (a skill performed into a battle prepared by hand, `tools/sim_audit.py` actives).

## Trace

One line per turn: the time, the actor, the events of the turn (the action, each hit, damage, healing and loss of HP), the HP, TP,
state and next turn of every unit, and the count of 32-bit words the generator has given (a draw of `random()` takes two).
Level 2 adds every draw. A header describes every unit before the battle starts.

## Not ported

`measures.slot_share`, `measures.weapon_band` and `measures.touched` (nothing calls them). `GameData.with_changes` is not ported: a tool
that changes the data in Python sends the changed data as a side of its own (`engine_client.side_of`), or, for the stats of enemy
records, gives `enemy_changes` in the job. The text log of a battle (`Battle.log`, read by `measures/mercenary_log.py`) is not ported.

Of the scripts of measures/ and tools/ that play battles, these have no command: `mercenary_log` (reads the text log of a battle), `win_causes`, `record_causes`,
`graceful_rose_trial`, `unique_trial`, `unique_trial_random` and `random_parties` (trials that no document or row of a workbook cites; the first two also take
rows of balance_changes.xlsx out by family and so need sides built by `tools/engine_sides.py`). `status_value_getters` and `installer_trial` play no battle.

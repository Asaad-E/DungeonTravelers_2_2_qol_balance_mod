# engine_cs: the battle engine in C#

The battle engine of the project and every measure that plays battles: battle loop, party policy, enemy AI, formulas, units,
the building of a party and its enemies, the guest allies, the runs of a checkpoint, the measures around a battle, and the 22
measures of the suite (`src/DtEngine/Suite`). It reads one snapshot of the data written by `tools/engine_export.py` and holds no
value of the mod (configuration: `data_tables/measure_config.json`, `data_tables/engine_coverage.json` and the workbooks).

It began as a 1-to-1 port of a Python simulator and was proven equal to it, trace line by trace line, on 2026-10-16 (a corpus of
every checkpoint and fixed battle, 3,000 random cases, a directed case for every skill, enemy, item, enchantment, piece of gear,
guest and summon, and the measures: 0 differences). That simulator was then removed; the engine is the reference. A change of its
code is checked against its own recorded traces: `python tools/engine_golden.py check` (12,731 jobs in about 11 s, part of
`tools/full_suite.py`); after a change meant to move results, `record` again and say so in the commit.

| Folder | What it holds |
|---|---|
| `src/DtEngine` | the library: `PyRandom` (CPython's generator), `Formulas`, `Units`, `Battle`, `Policy`, `Ai`, `Scenario`, `Measures`, `Jobs`, `Trace`, `Suite/` |
| `src/DtEngine.Cli` | the command-line program `dtcli` (server garbage collector: `runtimeconfig.template.json`) |
| `tests/DtEngine.Tests` | xunit tests: generator, formulas, rounding and number text against recorded golden files (`golden/`), snapshot, templates, recorder, and the calibration against what players measured (`CalibrationTests.cs`) |

## Commands

```bash
python tools/engine_export.py                                   # the snapshot: build/engine_snapshot.json
dotnet build engine_cs/src/DtEngine.Cli -c Release              # the program: engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll
dtcli suite [--only a,b] | dtcli <measure> | dtcli <trial> ARGS  # with --snapshot build/engine_snapshot.json --root .
dtcli run --snapshot build/engine_snapshot.json --jobs jobs.json --out results.json [--threads N] [--trace-out trace.txt | --trace-digest digest.txt]
dtcli measure --snapshot build/engine_snapshot.json --jobs measures.json --out results.json [--threads N]
dtcli trace --snapshot build/engine_snapshot.json --job job.json --out trace.txt [--level 1|2]
dtcli profile --snapshot build/engine_snapshot.json --jobs jobs.json [--repeat N]   # time, bytes allocated and by which types, on one thread
dotnet test engine_cs                                           # the xunit tests
python tools/engine_golden.py check | record                    # the engine against its own recorded traces
```

`dtcli` stands for `dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll`.

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

`dtcli measure` plays the measures that go around a battle, from a file of jobs
`{id, measure, side, ...}`: `expedition` (`floor`, `level`, `cid`, `roles`, `battles`, `runs`, `kit`), `play_checkpoint` (`cid`,
`runs`), `check_change` (`checkpoints`, `runs`; `side` is the data before the change, `changed_side` the data after), and
`walked_zones` (`floor`, `level`; the result is the names of the zones). They were proven equal to the removed Python simulator, value by value.

## The measures in C# (`dtcli suite`)

Every measure of the project that plays battles runs in `src/DtEngine/Suite`: the choice of cells, the parties and their recipes, the jobs, the
aggregation and the report writers, with the same outputs, at the same paths, as the Python script each one stands for (those scripts were removed on 2026-10-16).
A measure reads what it needs of the workbooks from the section `measures` of the snapshot (`tools/engine_export.py`: sheets as rows, the constants of
the scripts, the rows of balance_changes.xlsx that name a boss, the maps, the meals); it holds no value of the mod.

```bash
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll suite [--only a,b] [--threads N] [--snapshot S] [--root R]     # every measure, in parallel
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll difficulty-curve                                              # one measure alone
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
Three mass tests run on demand and are not part of the suite (their configuration: sections `skill_battery`, `support_battery` and
`class_search` of `data_tables/measure_config.json`):

```bash
dtcli skill-battery [names|*] [scan runs] [confirm runs]     # every skill with and without, in the battery parties; docs/generated/SKILL_BATTERY.md
dtcli unique-battery [scan runs] [confirm runs]                # each girl's unique skill with and without, in every role that names her, in the battery parties; docs/generated/UNIQUE_BATTERY.md
dtcli support-battery [runs] [stage]                         # each support and tank against an attacker in its place, boss / walk / walk then boss; docs/generated/SUPPORT_BATTERY.md
dtcli class-search [STAGE] [preset=NAME] [scan=N] [confirm=N] [cids=C34,C38] [context=boss|random|all] [with=Soul Summoner*2+Witch]
                  [without=Diva+Mistress] [sample=N]
                  [compare=vanilla|variant] [enemy=1036.hp=8800,...] [trial="Power Charge:e191*1.1;..."] [kit=N] [out=NAME]
                                                             # every party of the classes of a stage on two sides, A and B: vanilla and the
                                                             # variant, or (compare=variant) the variant and the variant with the trial values;
                                                             # with= keeps the parties that hold those classes; a table by class, A > B;
                                                             # without= leaves out parties that hold any of those classes; sample=N plays
                                                             # N parties of each target drawn with the seed; preset= the named arguments of
                                                             # class_search.presets (dolls, dark_lord, no_maid_line, quick), the others win;
                                                             # measures/CLASS_SEARCH_<STAGE>[_<OUT>].md (scan=0: the plan only)
```

`rows-trial` and `curve-ablation` need the game built from other rows of balance_changes.xlsx than the variant of the snapshot: `python
tools/engine_sides.py rows P031,P032` or `ablation` writes those sides to build/engine_extra_*.json and `--extra <file>` brings them in.

`Suite/Py.cs` holds what Python does that the reports depend on and C# does not: `%.nf`, `:.n%` and `repr` of a float, `statistics.mean` and
`median`, `json.dump` with and without `indent`. `dtcli check-pyformat build/engine_pyformat_golden.json` compares them with Python on some 25,000
cases (the file is kept in `tests/DtEngine.Tests/golden/`; `dotnet test` reads it).

## Recorder

A job with `record: true` gets, for each battle (`parts[k].record`), the tables of `sim.battle.Recorder` (damage, healing, actions,
skill uses, TP spent, items used, chants, performances broken, turns lost, denied, delayed, largest hit, deaths, kills) with the units
that name them (position, name, kind, side, role, owner, level); `result['record']` is that of the first battle, as in `sim.scenario.play`.
The trace carries one line `C ...` after the `E` line of each battle, so the recorded traces of `tools/engine_golden.py` cover the recorder.

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

The text log of a battle (the `log` of the removed simulator) has no counterpart: the trace is the record of a battle.

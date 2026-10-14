# engine_cs: the battle engine in C#

A 1-to-1 port of the battle side of `sim/` (battle loop, party policy, enemy AI, formulas, units, the building of a party and
its enemies, the runs of a checkpoint). It reads one snapshot of the data written by Python (`tools/engine_export.py`) and
holds no value of the mod. `sim/` stays the reference: the parity tests play the same cases in both and compare the traces.

| Folder | What it holds |
|---|---|
| `src/DtEngine` | the library: `PyRandom` (CPython's generator), `Formulas`, `Units`, `Battle`, `Policy`, `Ai`, `Scenario`, `Jobs`, `Trace` |
| `src/DtEngine.Cli` | the command-line program `dtcli` |
| `tests/DtEngine.Tests` | xunit tests: generator, formulas, snapshot, traces of a few fixed cases |
| `parity/` | the Python side of the parity tests (traced runs of `sim/`, the case generators, the comparison, the speed test) |
| `parity/cases/failing` | cases that did not match, saved with all their inputs; replay with `run_parity.py replay` |
| `parity/cases/regression` | cases that once failed (or are kept for good); played by every `corpus` run |

## Commands

```bash
python tools/engine_export.py                                   # the snapshot: build/engine_snapshot.json
dotnet build engine_cs/src/DtEngine.Cli -c Release              # the program: engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll run --snapshot build/engine_snapshot.json --jobs jobs.json --out results.json [--threads N] [--trace-out trace.txt]
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll trace --snapshot build/engine_snapshot.json --job job.json --out trace.txt [--level 1|2]
dotnet test engine_cs                                           # the xunit tests

python engine_cs/parity/rng_golden.py                                         # golden files of the generator and of the formulas (the tests write them when missing)
python engine_cs/parity/formulas_golden.py
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll check-rng build/engine_rng_golden.json
dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll check-formulas build/engine_formulas_golden.json

python engine_cs/parity/run_parity.py corpus --seeds 20261005,7,123456 --runs 2 --fixed   # the fixed corpus (add --only smoke for a few cases)
python engine_cs/parity/run_parity.py random --count 3000                     # new random cases; prints the seed of the generator
python engine_cs/parity/run_parity.py replay engine_cs/parity/cases/failing/x.json
python engine_cs/parity/run_parity.py determinism                             # sim/ against itself, in two sets of processes
python engine_cs/parity/coverage_run.py --count 1200 --corpus                 # which lines of sim/ the cases reach
python engine_cs/parity/bench.py                                              # battles per second of both engines
```

The corpus is every checkpoint of the setup on both sides with the reference party, the parties of `measures/win_rates.py` at
its 17 bosses, every fixed battle of the game (with `--fixed`), and the cases of `parity/cases/regression`. A random case is a
random party (roles of the sheet Roles, a level near a random checkpoint or near the enemies, sometimes skills, enchantments or
items added on top of the plan) against a random fixed battle or random formations of a random floor zone.

## Jobs

A job (JSON) is a side (`vanilla` or `variant`), a party (the checkpoint whose chapter, gear and crown bonus it takes, a list
of roles or `null` for the composition of the setup, a level or `null` for the reference level), the enemies (`checkpoint`: the
fixed battles of the checkpoint; `fixed`: a list of `[floor, number]`; `zone`: random formations of a floor zone, a number of
battles), a number of runs and a seed. Run `k` of a job plays with the generator seeded `seed + k`, as `sim.scenario.play`
does. The results hold, for each run, the figures of `sim.scenario.play` (`won`, `lost`, `time`, `actions`, `lowest_hp`,
`enemy_damage`, `enemy_actions`, `party_max_hp`, `hp_left`, `tp_left`, `alive`, and `parts`, one per fight) and the figures
of `sim.measures.summary` for the job.

## Trace

One line per turn: the time, the actor, the events of the turn (the action, each hit, damage, healing and loss of HP), the HP, TP,
state and next turn of every unit, and the count of 32-bit words the generator has given (a draw of `random()` takes two).
Level 2 adds every draw. A header describes every unit before the battle starts.

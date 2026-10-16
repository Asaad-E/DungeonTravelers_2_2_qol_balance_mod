# sim/ — frozen

The Python battle simulator the C# engine (`engine_cs/`) was ported from. The engine was proven equal to it, trace line by
trace line, on the parity sets of `engine_cs/parity/` (corpus, fixed battles, 3,000 random cases, directed cases, measures:
0 differences on 2026-10-16). Since that day this folder is **frozen**: no measure runs on it, and it is not edited.

- Measures run in C#: `python tools/full_suite.py`, or `dtcli <measure>` (`engine_cs/README.md`).
- A change of the engine is checked against the engine's own recorded traces: `python tools/engine_golden.py check`
  (and `record` after a change that is meant to move results).
- The data readers this folder also holds (`data.py`, `setup.py`, `variant.py`) still feed the snapshot of the engine
  (`tools/engine_export.py`); a change there is a change of the data, not of the simulator.

It is kept as the historical reference: the code the engine's behaviour was proven against, and the easiest place to read
how a rule was written.

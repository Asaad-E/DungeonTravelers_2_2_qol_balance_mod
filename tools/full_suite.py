"""
Every measure of the project played on the C# engine (engine_cs/), then the generated checklists and the tests: the whole of
docs/generated/ and of the figures of measures/ written again from the current data and model.

    python tools/full_suite.py            the whole suite, with the time of each step and the total
    python tools/full_suite.py --list     the steps, without running them

The steps: the snapshot of the data (tools/engine_export.py); `dtcli suite`, which runs every measure that plays battles (the choice of
cells, the parties, the battles, the aggregation and the reports, all in C#) at once, the measures side by side and the battles of each
in parallel; then the checklists that play no battle and the tests, which stay in Python. One measure alone is `dtcli <name>`
(`dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll difficulty-curve`); `dtcli suite --only a,b` runs some. The scripts
of tools/ and measures/ that play battles keep their own `engine` and `--engine` commands (the reference: the Python path of each).
"""
import os
import subprocess
import sys
import time

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SUITE = ['@dtcli', 'suite']             # one process: every measure that plays battles

STEPS = [
    ['tools/engine_export.py'],
    ['tools/engine_golden.py', 'check'],   # the engine against its own recorded traces (a change of its code shows here)
    SUITE,
    ['tools/balance_baseline.py'], ['tools/checkpoint_levels.py'], ['tools/sim_coverage.py'], ['tools/verdicts.py'],
    ['tools/class_charts.py'],             # the charts of class-balance and class-stages (docs/generated/charts)
    ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'],
]


def command_of(step):
    """The command line of a step: a Python script, or the engine's program."""
    if step[0] == '@dtcli':
        sys.path.insert(0, os.path.join(PROJECT, 'tools'))
        import engine_golden
        return ['dotnet', engine_golden.dtcli(), *step[1:], '--snapshot', os.path.join(PROJECT, 'build', 'engine_snapshot.json'),
                '--root', PROJECT]
    return [sys.executable, *step]


def main(args):
    if '--list' in args:
        for step in STEPS:
            print('dtcli' if step[0] == '@dtcli' else 'python', ' '.join(step[1:] if step[0] == '@dtcli' else step))
        return 0
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    started, failed = time.time(), []
    for step in STEPS:
        began = time.time()
        run = subprocess.run(command_of(step), cwd=PROJECT, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        lines = [line for line in (run.stdout + run.stderr).strip().splitlines() if line.strip()]
        mark = '' if run.returncode == 0 else '  FAILED'
        name = ('dtcli ' + ' '.join(step[1:])) if step[0] == '@dtcli' else 'python ' + ' '.join(step)
        print(f'{time.time() - began:6.0f} s  {name}{mark}', flush=True)
        for line in (lines if step[0] == '@dtcli' else lines[-1:]):
            print('          ' + line[:150], flush=True)
        if run.returncode:
            failed.append(name)
    print(f'total {time.time() - started:.0f} s; {len(STEPS) - len(failed)} of {len(STEPS)} steps passed'
          + (f'; failed: {"; ".join(failed)}' if failed else ''))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main(sys.argv[1:]))

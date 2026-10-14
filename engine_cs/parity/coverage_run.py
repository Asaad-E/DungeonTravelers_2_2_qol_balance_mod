"""
Which lines of the simulator the parity cases run. Plays jobs of the random generator (and, with --corpus, the checkpoints)
in this process under sys.monitoring and lists the lines of sim/battle.py, policy.py, ai.py, scenario.py, units.py and
formulas.py that no case reached: what the parity tests do not verify.

    python engine_cs/parity/coverage_run.py [--count N] [--seed S] [--corpus]
"""
import argparse
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
for path in (PROJECT, os.path.join(PROJECT, 'tools'), HERE):
    if path not in sys.path:
        sys.path.insert(0, path)

MODULES = ('battle', 'policy', 'ai', 'scenario', 'units', 'formulas', 'measures')


def executable_lines(path):
    """The lines of the bodies of functions (module-level lines run at import, before the watch starts)."""
    with open(path, encoding='utf-8') as f:
        code = compile(f.read(), path, 'exec')
    lines, stack = set(), [k for k in code.co_consts if hasattr(k, 'co_lines')]
    while stack:
        c = stack.pop()
        first = c.co_firstlineno
        for _, _, line in c.co_lines():
            if line and line != first:
                lines.add(line)
        stack.extend(k for k in c.co_consts if hasattr(k, 'co_lines'))
    return lines


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--count', type=int, default=150)
    p.add_argument('--seed', type=int, default=99)
    p.add_argument('--corpus', action='store_true')
    args = p.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    import pyref
    import run_parity
    state = pyref.load_state()
    pyref.install()
    jobs = run_parity.random_jobs(random.Random(args.seed), args.count, state, 0)
    if args.corpus:
        ns = argparse.Namespace(seeds='20261005', runs=1, trace=0, only=None)
        jobs += run_parity.corpus_jobs(ns)
    for k, j in enumerate(jobs):
        j['id'] = f'cov{k}'
        j['trace'] = 0

    mon = sys.monitoring
    tool = mon.COVERAGE_ID
    mon.use_tool_id(tool, 'parity-coverage')
    wanted = {os.path.normcase(os.path.join(PROJECT, 'sim', m + '.py')): m for m in MODULES}
    executed = {m: set() for m in MODULES}

    def on_line(code, line):
        module = wanted.get(os.path.normcase(code.co_filename))
        if module is not None:
            executed[module].add(line)
        return mon.DISABLE

    mon.register_callback(tool, mon.events.LINE, on_line)
    mon.set_events(tool, mon.events.LINE)
    started = time.time()
    for k, job in enumerate(jobs):
        pyref.run_job(job, state)
        if k % 25 == 0:
            print(k, 'jobs', f'{time.time() - started:.0f} s', flush=True)
    mon.set_events(tool, 0)
    print()
    for m in MODULES:
        path = os.path.join(PROJECT, 'sim', m + '.py')
        lines = executable_lines(path)
        missed = sorted(lines - executed[m])
        print(f'{m}.py: {len(lines) - len(missed)} of {len(lines)} lines run ({100 * (len(lines) - len(missed)) / len(lines):.1f}%)')
        ranges, start = [], None
        for line in missed:
            if start is None or line != prev + 1:
                if start is not None:
                    ranges.append((start, prev))
                start = line
            prev = line
        if start is not None:
            ranges.append((start, prev))
        print('  not run:', ', '.join(f'{a}' if a == b else f'{a}-{b}' for a, b in ranges))
        with open(path, encoding='utf-8') as src:
            text = src.read().split(chr(10))
        with open(os.path.join(PROJECT, 'build', 'parity', f'uncovered_{m}.txt'), 'w', encoding='utf-8') as out:
            for line in missed:
                out.write(f'{line}: {text[line - 1]}' + chr(10))


if __name__ == '__main__':
    main()

"""
Which lines of the simulator the parity cases run. Plays jobs of the random generator (and, with --corpus, the checkpoints)
in this process under sys.monitoring and lists the lines of sim/battle.py, policy.py, ai.py, scenario.py, units.py and
formulas.py that no case reached: what the parity tests do not verify.

    python engine_cs/parity/coverage_run.py [--count N] [--seed S] [--corpus]
"""
import argparse
import inspect
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
        if c.co_flags & inspect.CO_OPTIMIZED:                  # a function: the body of a class runs at import, with its def lines
            for _, _, line in c.co_lines():
                if line and line != first:
                    lines.add(line)
        stack.extend(k for k in c.co_consts if hasattr(k, 'co_lines'))
    return lines


_W = {}


def _watch():
    """Starts the line monitor in this process; returns the sets of lines run so far, by module."""
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
    return executed


def _init_worker():
    import pyref
    _W['state'] = pyref.load_state()
    pyref.install()
    _W['executed'] = _watch()


def _run_chunk(chunk):
    """Plays a chunk of jobs ({job} or ('measure', job)) and returns every line run by this process so far."""
    import pyref
    import run_measures
    run_measures._STATE.update(_W['state'])
    for item in chunk:
        if isinstance(item, tuple):
            run_measures.python_result(item[1])
        else:
            try:
                pyref.run_job(item, _W['state'])
            except Exception:                    # a case that is meant to raise
                pass
    return {m: sorted(lines) for m, lines in _W['executed'].items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--count', type=int, default=150)
    p.add_argument('--seed', type=int, default=99)
    p.add_argument('--corpus', action='store_true')
    p.add_argument('--directed', action='store_true', help='also the directed cases (run_parity.py directed)')
    p.add_argument('--parts', default=None, help='with --directed: only these parts of the directed cases (a comma list)')
    p.add_argument('--measures', type=int, default=0, help='also play this many expedition jobs and the other measures (run_measures.py)')
    p.add_argument('--workers', type=int, default=6, help='processes (each watches its own lines; the sets are joined)')
    args = p.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    import pyref
    import run_parity
    state = pyref.load_state()
    jobs = run_parity.random_jobs(random.Random(args.seed), args.count, state, 0, args.seed)
    if args.corpus:
        ns = argparse.Namespace(seeds='20261005', runs=1, trace=0, only=None)
        jobs += run_parity.corpus_jobs(ns)
        jobs += run_parity.fixed_battle_jobs(ns, state)
        jobs += run_parity.extension_jobs(ns, state)
    if args.directed:
        ns = argparse.Namespace(directed_seed=17, trace=0, ai_jobs=900)
        jobs += run_parity.directed_jobs(ns, state, tuple(args.parts.split(',')) if args.parts else run_parity.DIRECTED_PARTS)
    for k, j in enumerate(jobs):
        j['id'] = f'cov{k}'
        j['trace'] = 0
    items = list(jobs)
    if args.measures:
        import run_measures
        run_measures._STATE.update(state)
        items += [('measure', job) for job in run_measures.make_jobs(args.measures, args.seed)]
    chunks = [items[k:k + 40] for k in range(0, len(items), 40)]
    print(f'{len(items)} jobs in {len(chunks)} chunks on {args.workers} processes', flush=True)

    from concurrent.futures import ProcessPoolExecutor
    executed = {m: set() for m in MODULES}
    started = time.time()
    with ProcessPoolExecutor(args.workers, initializer=_init_worker) as pool:
        for done, seen in enumerate(pool.map(_run_chunk, chunks)):
            for m, lines in seen.items():
                executed[m].update(lines)
            if done % 20 == 0:
                print(done, 'chunks', f'{time.time() - started:.0f} s', flush=True)
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
        os.makedirs(os.path.join(PROJECT, 'build', 'parity'), exist_ok=True)
        with open(os.path.join(PROJECT, 'build', 'parity', f'uncovered_{m}.txt'), 'w', encoding='utf-8') as out:
            for line in missed:
                out.write(f'{line}: {text[line - 1]}' + chr(10))


if __name__ == '__main__':
    main()

"""
Speed of the two engines on the same jobs: battles per second of sim/ (one process) and of the C# engine on one thread, on four and
on all of them.

    python engine_cs/parity/bench.py [--runs N] [--cs-factor F] [--threads 1,4,12] [--repeat R] [--cli PATH] [--no-python]

The jobs are the reference party against the boss of a few checkpoints, on both sides. The C# engine plays F times more
runs than Python (it is too fast to time on the same count); battles per second are comparable across both. --cli: another
build of the program to time (an earlier version of the engine), played on the same jobs. Each figure is the best of R runs.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
for path in (PROJECT, os.path.join(PROJECT, 'tools'), HERE):
    if path not in sys.path:
        sys.path.insert(0, path)

CHECKPOINTS = ('C06', 'C17', 'C24', 'C40')
DEFAULT_CLI = os.path.join(PROJECT, 'engine_cs', 'src', 'DtEngine.Cli', 'bin', 'Release', 'net10.0', 'dtcli.dll')


def jobs_for(runs, cps, sides=('vanilla', 'variant')):
    return [{'id': f'bench-{side}-{cid}', 'side': side, 'runs': runs, 'seed': 20261005, 'trace': 0, 'kit': None, 'options': {},
             'party': {'cid': cid, 'roles': None, 'level': None, 'crown': None}, 'enemies': {'kind': 'checkpoint'}}
            for cid in cps for side in sides]


def run_cs(jobs, threads, cli=DEFAULT_CLI):
    """Battles a second the program reports for the jobs on this many threads."""
    os.makedirs(os.path.join(PROJECT, 'build', 'parity'), exist_ok=True)
    jobs_path = os.path.join(PROJECT, 'build', 'parity', 'bench_jobs.json')
    out_path = os.path.join(PROJECT, 'build', 'parity', 'bench_results.json')
    with open(jobs_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f)
    snapshot = os.path.join(PROJECT, 'build', 'engine_snapshot.json')
    run = subprocess.run(['dotnet', cli, 'run', '--snapshot', snapshot, '--jobs', jobs_path, '--out', out_path, '--threads', str(threads)],
                         capture_output=True, text=True)
    line = run.stdout.strip().splitlines()[-1]
    # "snapshot 0.34 s; 8 jobs, 3200 battles in 1.234 s (2593.1 battles/s on 4 threads); 0 errors"
    rate = float(line.split('(')[1].split(' battles/s')[0])
    return rate, line


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--runs', type=int, default=6)
    p.add_argument('--cs-factor', type=int, default=20)
    p.add_argument('--threads', default='1,4,' + str(os.cpu_count()))
    p.add_argument('--repeat', type=int, default=3)
    p.add_argument('--cli', default=DEFAULT_CLI)
    p.add_argument('--no-python', action='store_true')
    args = p.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if not args.no_python:
        import pyref
        state = pyref.load_state()
        pyref.install()
        jobs = jobs_for(args.runs, CHECKPOINTS)
        started = time.perf_counter()
        battles = 0
        for job in jobs:
            result, _ = pyref.run_job(job, state)
            battles += sum(len(r['parts']) for r in result['runs'])
        py_time = time.perf_counter() - started
        print(f'Python, one process : {battles} battles in {py_time:.1f} s = {battles / py_time:.2f} battles/s')
    big = jobs_for(args.runs * args.cs_factor, CHECKPOINTS)
    for threads in (int(t) for t in args.threads.split(',')):
        rates = [run_cs(big, threads, args.cli)[0] for _ in range(args.repeat)]
        print(f'C#, {threads:2d} threads : best {max(rates):8.1f} battles/s  (runs: {", ".join(f"{r:.0f}" for r in rates)})')


if __name__ == '__main__':
    main()

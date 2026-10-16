"""
The check of the C# engine against itself. The engine was proven equal to the Python simulator of sim/ trace line by trace
line (engine_cs/parity/) up to 2026-10-16; sim/ is frozen since and is not run any more. From then on a change of the engine
is checked here: a bank of some 12,000 jobs (the parity corpus, the fixed battles, the directed cases and 3,000 random cases)
played on a frozen copy of the snapshot, its traces compared job by job with the traces recorded when the engine was last
known good. A balance change does not move them (the snapshot is frozen); only a change of the engine's code does.

    python tools/engine_golden.py check      plays the bank and compares; exit 1 and the jobs that differ when one does
    python tools/engine_golden.py record     records the bank and its traces: once, and again after a change of the engine
                                             that is meant to change results (say which in the commit)

The bank, the frozen snapshot and the traces live in build/golden/ (local: they hold figures of the game).
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
GOLDEN = os.path.join(PROJECT, 'build', 'golden')
SNAPSHOT = os.path.join(GOLDEN, 'snapshot.json')
JOBS = os.path.join(GOLDEN, 'bank_jobs.json')
REFERENCE = os.path.join(GOLDEN, 'bank_digest.txt')
sys.path.insert(0, HERE)


def play(digest_path):
    import engine_client
    started = time.time()
    run = subprocess.run(['dotnet', engine_client.ensure_built(), 'run', '--snapshot', SNAPSHOT, '--jobs', JOBS,
                          '--out', os.path.join(GOLDEN, 'bank_results.json'), '--trace-digest', digest_path],
                         capture_output=True, text=True)
    # three directed jobs give the policy rules it does not know, and must fail: dtcli then exits 1 with the digest written
    if not os.path.exists(digest_path) or (run.returncode != 0 and 'errors' not in run.stdout):
        raise SystemExit('dtcli failed:\n' + run.stdout[-2000:] + run.stderr[-2000:])
    return time.time() - started


def lines(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f if line.strip()]


def record():
    import engine_client
    os.makedirs(GOLDEN, exist_ok=True)
    shutil.copyfile(engine_client.ensure_snapshot(), SNAPSHOT)
    done = subprocess.run([sys.executable, os.path.join(PROJECT, 'engine_cs', 'parity', 'dump_jobs.py'), '--out', JOBS],
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit('dump_jobs.py failed:\n' + done.stdout + done.stderr)
    seconds = play(REFERENCE)
    print(f'recorded {len(lines(REFERENCE))} jobs in {seconds:.0f} s: {GOLDEN}')


def check():
    if not os.path.exists(REFERENCE):
        raise SystemExit('no reference: run "python tools/engine_golden.py record" once')
    new = os.path.join(GOLDEN, 'bank_digest_new.txt')
    seconds = play(new)
    ref, now = lines(REFERENCE), lines(new)
    differ = [a.split()[0] for a, b in zip(ref, now) if a != b]
    if len(ref) != len(now):
        differ.append(f'{len(ref)} jobs recorded, {len(now)} now')
    if differ:
        print(f'engine: {len(differ)} of {len(ref)} jobs give other traces ({seconds:.0f} s), first: ' + ', '.join(differ[:5]))
        sys.exit(1)
    print(f'engine: {len(ref)} jobs, every trace as recorded ({seconds:.0f} s)')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'record': record, 'check': check}[sys.argv[1] if len(sys.argv) > 1 else 'check']()

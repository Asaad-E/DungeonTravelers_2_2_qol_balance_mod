"""
The check of the C# engine against itself. The engine was proven equal to the Python simulator trace line by trace line on
2026-10-16; that simulator was removed the same day. A change of the engine is checked here: a bank of 12,731 jobs (the
parity corpus, the fixed battles, the directed cases and 3,000 random cases) played on a frozen copy of the snapshot, its
traces compared job by job with the traces recorded when the engine was last known good. A balance change does not move
them (the snapshot is frozen); only a change of the engine's code does.

    python tools/engine_golden.py check      plays the bank and compares; exit 1 and the jobs that differ when one does
    python tools/engine_golden.py record     records the traces again, after a change of the engine that is meant to change
                                             results (say which in the commit)

The bank, the frozen snapshot and the traces live in build/golden/ (local: they hold figures of the game). The bank was made
once by the parity tools of the removed simulator and cannot be made again; keep that folder.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
GOLDEN = os.path.join(PROJECT, 'build', 'golden')
SNAPSHOT = os.path.join(GOLDEN, 'snapshot.json')
JOBS = os.path.join(GOLDEN, 'bank_jobs.json')
REFERENCE = os.path.join(GOLDEN, 'bank_digest.txt')
SRC = os.path.join(PROJECT, 'engine_cs', 'src')
PROGRAM = os.path.join(SRC, 'DtEngine.Cli', 'bin', 'Release', 'net10.0', 'dtcli.dll')


def dtcli():
    """The engine's program, built first when a source of engine_cs/src is newer."""
    newest = 0.0
    for folder, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in ('bin', 'obj')]
        for name in files:
            if name.endswith(('.cs', '.csproj', '.json')):
                newest = max(newest, os.path.getmtime(os.path.join(folder, name)))
    if not os.path.exists(PROGRAM) or os.path.getmtime(PROGRAM) < newest:
        built = subprocess.run(['dotnet', 'build', os.path.join(SRC, 'DtEngine.Cli'), '-c', 'Release', '-nologo', '-v', 'q'],
                               capture_output=True, text=True)
        if built.returncode != 0:
            raise SystemExit('dtcli did not build:\n' + built.stdout + built.stderr)
    return PROGRAM


def play(digest_path):
    if not (os.path.exists(JOBS) and os.path.exists(SNAPSHOT)):
        raise SystemExit(f'no bank in {GOLDEN}: it was made once and cannot be made again')
    started = time.time()
    run = subprocess.run(['dotnet', dtcli(), 'run', '--snapshot', SNAPSHOT, '--jobs', JOBS,
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

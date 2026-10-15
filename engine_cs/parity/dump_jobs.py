"""
Writes the jobs of the parity sets (the corpus, the directed cases and random cases) to one file, so that the C# engine can be
run on all of them without Python and its traces compared with those of an earlier build of itself. After a change that must not
change a result (an optimisation), this is the quick check: the traces must be the same, byte for byte. The comparison with
sim/ is run_parity.py.

    python engine_cs/parity/dump_jobs.py [--out build/parity/bank_jobs.json] [--random N] [--seed S]
    dotnet engine_cs/src/DtEngine.Cli/bin/Release/net10.0/dtcli.dll run --snapshot build/engine_snapshot.json --jobs build/parity/bank_jobs.json --out build/parity/bank_results.json --trace-digest build/parity/bank_digest.txt
    python engine_cs/parity/dump_jobs.py --check build/parity/bank_digest_ref.txt build/parity/bank_digest.txt
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
for path in (PROJECT, os.path.join(PROJECT, 'tools'), HERE):
    if path not in sys.path:
        sys.path.insert(0, path)


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default=os.path.join(PROJECT, 'build', 'parity', 'bank_jobs.json'))
    p.add_argument('--random', type=int, default=3000)
    p.add_argument('--seed', type=int, default=424242)
    p.add_argument('--check', nargs=2, metavar=('REFERENCE', 'NEW'))
    args = p.parse_args()
    if args.check:
        a, b = (digest(x) for x in args.check)
        print('same traces' if a == b else 'DIFFERENT traces', a[:16], b[:16])
        sys.exit(0 if a == b else 1)
    import pyref
    import run_parity
    state = pyref.load_state()
    ns = argparse.Namespace(seeds='20261005,7', runs=2, trace=1, only=None, directed_seed=17, ai_jobs=900)
    jobs = run_parity.corpus_jobs(ns)
    jobs += run_parity.fixed_battle_jobs(ns, state)
    jobs += run_parity.extension_jobs(ns, state)
    jobs += run_parity.directed_jobs(ns, state)
    random_jobs = run_parity.random_jobs(random.Random(args.seed), args.random, state, 1, args.seed)
    for job in random_jobs:
        job['id'] = f's{args.seed}-{job["id"]}'
    jobs += random_jobs
    seen = set()
    for job in jobs:
        while job['id'] in seen:
            job['id'] += '+'
        seen.add(job['id'])
        job['trace'] = 1
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(jobs, f)
    print(len(jobs), 'jobs written to', args.out)


if __name__ == '__main__':
    main()

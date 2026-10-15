"""
Parity of the measures around a battle: the C# engine (dtcli measure) against sim/, figure by figure.

    python engine_cs/parity/run_measures.py [--count N] [--seed S] [--workers W] [--threads T]

The measures: sim.measures.expedition, sim.scenario.walked_zones, sim.measures.play_checkpoint and sim.measures.check_change
(with the whole variant as the changed data, as the tools call it). Every figure is compared for exact equality, floats included
(the results go through JSON, which keeps a float exactly). Jobs that differ are printed with both results.
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
for path in (PROJECT, os.path.join(PROJECT, 'tools'), HERE):
    if path not in sys.path:
        sys.path.insert(0, path)

BUILD = os.path.join(PROJECT, 'build')
WORK = os.path.join(BUILD, 'parity')
SNAPSHOT = os.path.join(BUILD, 'engine_snapshot.json')
CLI_DLL = os.path.join(PROJECT, 'engine_cs', 'src', 'DtEngine.Cli', 'bin', 'Release', 'net10.0', 'dtcli.dll')

_STATE = {}


def _state():
    if not _STATE:
        import pyref
        _STATE.update(pyref.load_state())
    return _STATE


def python_result(job):
    """The figures of one measure job, from sim/, in the shape dtcli measure writes them."""
    from sim import measures, scenario
    state = _state()
    side = job.get('side', 'variant')
    data, setup = state['sides'][side], state['setup']
    try:
        kind = job['measure']
        if kind == 'expedition':
            r = measures.expedition(data, setup, job['floor'], job['level'], job['cid'], roles=job.get('roles'),
                                    battles=job.get('battles'), runs=job.get('runs'), kit=job.get('kit'))
            return {'id': job['id'], 'measure': kind, 'won': r['won'], 'reached_limit': r['reached_limit'], 'tp_after': r['tp_after']}
        if kind == 'walked_zones':
            zones = scenario.walked_zones(data, setup, job['floor'], job['level'])
            return {'id': job['id'], 'measure': kind, 'zones': [z['name'] for z in zones]}
        if kind == 'play_checkpoint':
            level, summary = measures.play_checkpoint(data, setup, job['cid'], job.get('runs') if job.get('runs') is not None else int(setup.settings['runs']))
            return {'id': job['id'], 'measure': kind, 'level': level, 'summary': summary}
        if kind == 'check_change':
            changed = state['sides'][job.get('changed_side', 'variant')]
            rows = measures.check_change(data, setup, [], job['checkpoints'], runs=job.get('runs'), changed=changed)
            return {'id': job['id'], 'measure': kind, 'rows': [
                {'cid': cid, 'level_before': before['level'], 'level_after': after['level'],
                 'before': {k: before[k] for k in ('won', 'time', 'lowest_hp', 'pressure')},
                 'after': {k: after[k] for k in ('won', 'time', 'lowest_hp', 'pressure')}, 'out': out}
                for cid, before, after, out in rows]}
        raise ValueError(kind)
    except Exception as ex:
        return {'id': job['id'], 'error': f'{type(ex).__name__}: {ex}'}


def make_jobs(count, seed):
    from sim import scenario
    state = _state()
    data, setup = state['sides']['vanilla'], state['setup']
    rnd = random.Random(seed)
    checkpoints = [cp['ID'] for cp in setup.checkpoints]
    floors = sorted({z['floor'] for z in data.floors})
    roles = list(setup.roles)
    zones = [z['name'] for z in data.floors if z['formations']]
    levels = scenario.reference_levels(data, setup)
    jobs = []
    # walked_zones: every floor of the game at a few levels (cheap, no battle)
    for floor in floors:
        for level in (5, 20, 45, 70):
            jobs.append({'id': f'wz-{floor}-{level}', 'measure': 'walked_zones', 'side': rnd.choice(['vanilla', 'variant']), 'floor': floor, 'level': level})
    for z in zones[:40]:
        jobs.append({'id': f'wz-name-{z}', 'measure': 'walked_zones', 'side': 'variant', 'floor': z, 'level': rnd.randint(1, 80)})
    # play_checkpoint on a spread of checkpoints and both sides
    for cid in checkpoints[::4]:
        for side in ('vanilla', 'variant'):
            jobs.append({'id': f'pc-{side}-{cid}', 'measure': 'play_checkpoint', 'side': side, 'cid': cid, 'runs': rnd.choice([1, 3, 5])})
    # check_change: the variant against vanilla on a few checkpoints
    for n in range(max(3, count // 8)):
        cids = rnd.sample(checkpoints, rnd.randint(1, 3))
        jobs.append({'id': f'cc-{n}', 'measure': 'check_change', 'side': 'vanilla', 'changed_side': 'variant', 'checkpoints': cids,
                     'runs': rnd.choice([2, 4, 6])})
    # expedition: random zones, levels near the zone's enemies, with and without roles, kit, battles and runs
    for n in range(count):
        zone = rnd.choice(zones)
        cid = rnd.choice(checkpoints)
        top = max(data.enemies[e]['level'] for z in data.floors if z['name'] == zone for f in z['formations'] for e, _ in f['enemies'] if e in data.enemies)
        job = {'id': f'ex-{n}', 'measure': 'expedition', 'side': rnd.choice(['vanilla', 'variant']), 'floor': zone,
               'level': max(1, min(99, top + rnd.randint(-8, 4))), 'cid': cid, 'battles': rnd.choice([None, 3, 5, 9, 12]),
               'runs': rnd.choice([None, 2, 3, 5])}
        if job['runs'] is None:
            job['runs'] = 3
        if rnd.random() < 0.4:
            job['roles'] = [rnd.choice(roles) for _ in range(rnd.randint(1, 5))]
        if rnd.random() < 0.3:
            job['kit'] = rnd.choice([0, 4, 12])
        jobs.append(job)
    return jobs


def same(a, b, path=''):
    """First difference of two results (None when they are equal)."""
    if isinstance(a, dict) and isinstance(b, dict):
        for key in a:
            if key not in b:
                return f'{path}/{key}: missing in C#'
            found = same(a[key], b[key], f'{path}/{key}')
            if found:
                return found
        for key in b:
            if key not in a:
                return f'{path}/{key}: missing in Python'
        return None
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return f'{path}: {len(a)} items against {len(b)}'
        for k, (x, y) in enumerate(zip(a, b)):
            found = same(x, y, f'{path}[{k}]')
            if found:
                return found
        return None
    if a is None or b is None or isinstance(a, bool) or isinstance(b, bool) or isinstance(a, str) or isinstance(b, str):
        return None if a == b and type(a) == type(b) else f'{path}: {a!r} against {b!r}'
    return None if float(a) == float(b) else f'{path}: {a!r} against {b!r}'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--count', type=int, default=24, help='expedition jobs')
    p.add_argument('--seed', type=int, default=11)
    p.add_argument('--workers', type=int, default=6)
    p.add_argument('--threads', type=int, default=4)
    args = p.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    os.makedirs(WORK, exist_ok=True)
    subprocess.run(['dotnet', 'build', os.path.join(PROJECT, 'engine_cs', 'src', 'DtEngine.Cli', 'DtEngine.Cli.csproj'), '-c', 'Release', '-nologo', '-v', 'q'],
                   check=True, capture_output=True)
    jobs = make_jobs(args.count, args.seed)
    jobs_path, out_path = os.path.join(WORK, 'measure_jobs.json'), os.path.join(WORK, 'measure_results.json')
    with open(jobs_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f)
    started = time.time()
    with ProcessPoolExecutor(args.workers) as pool:
        py = list(pool.map(python_result, jobs, chunksize=1))
    print(f'Python: {len(jobs)} measure jobs ({time.time() - started:.1f} s)')
    started = time.time()
    run = subprocess.run(['dotnet', CLI_DLL, 'measure', '--snapshot', SNAPSHOT, '--jobs', jobs_path, '--out', out_path, '--threads', str(args.threads)],
                         capture_output=True, text=True)
    print('C#:', run.stdout.strip(), run.stderr.strip()[:300], f'({time.time() - started:.1f} s)')
    with open(out_path, encoding='utf-8') as f:
        cs = {r['id']: r for r in json.load(f)}
    bad = []
    by_kind = {}
    for job, a in zip(jobs, py):
        b = cs.get(job['id'])
        by_kind.setdefault(job['measure'], [0, 0])[0] += 1
        if 'error' in a or b is None or 'error' in b:
            if 'error' in a and b is not None and 'error' in b:
                continue                                    # both raised
            bad.append((job, 'error', a.get('error'), b and b.get('error')))
            by_kind[job['measure']][1] += 1
            continue
        found = same(a, b)
        if found:
            bad.append((job, found, a, b))
            by_kind[job['measure']][1] += 1
    for kind, (n, d) in sorted(by_kind.items()):
        print(f'  {kind}: {n} jobs, {d} differences')
    for job, why, a, b in bad[:10]:
        print('  -', job['id'], why, json.dumps(a)[:300], json.dumps(b)[:300])
    print(f'measures: {len(jobs)} jobs, {len(bad)} differences')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

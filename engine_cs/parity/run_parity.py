"""
Parity of the C# engine (engine_cs/) with the simulator of sim/, by traces.

    python engine_cs/parity/run_parity.py export                     writes the snapshot (build/engine_snapshot.json)
    python engine_cs/parity/run_parity.py corpus [options]           the fixed corpus: every checkpoint, both sides, a few seeds,
                                                                     the parties of measures/win_rates.py at its 17 bosses,
                                                                     and the cases kept in engine_cs/parity/cases/regression
    python engine_cs/parity/run_parity.py random [options]           random cases (a new set each time; the generator is seeded
                                                                     from the clock and prints its seed)
    python engine_cs/parity/run_parity.py replay <case.json> ...     plays the saved case(s) again
    python engine_cs/parity/run_parity.py selfcheck                  the instrumented Python against the plain one

options:  --count N (random cases)   --seed S (generator of the cases)   --workers W (Python processes)   --threads T (C#)
          --trace L (0: results only, 1: a line a turn, 2: with the draws of the generator)   --runs R   --batch B

A case that does not match is written to engine_cs/parity/cases/failing/ (all its inputs and the seed), with the first
lines that differ; once fixed, it is moved to cases/regression/, where `corpus` plays it for good.
"""
import argparse
import json
import os
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
CLI_DIR = os.path.join(PROJECT, 'engine_cs', 'src', 'DtEngine.Cli')
CLI_DLL = os.path.join(CLI_DIR, 'bin', 'Release', 'net10.0', 'dtcli.dll')
CASES = os.path.join(HERE, 'cases')
FAILING, REGRESSION = os.path.join(CASES, 'failing'), os.path.join(CASES, 'regression')

_STATE = {}


def _init_worker():
    import pyref
    _STATE.update(pyref.load_state())
    pyref.install()


def _play(job):
    import pyref
    try:
        result, lines = pyref.run_job(job, _STATE)
        return {'result': result, 'lines': lines, 'error': None}
    except Exception as ex:  # the reference raised: the case is compared with the engine raising too
        import traceback
        return {'result': None, 'lines': [], 'error': f'{type(ex).__name__}: {ex}', 'trace': traceback.format_exc()}


_POOL = {}
TALLY = {'jobs': 0, 'lines': 0, 'units': 0, 'turns': 0}


def python_side(jobs, workers):
    """Plays the jobs with sim/ in a pool of processes that is kept between batches (each loads the data once)."""
    if 'pool' not in _POOL:
        _POOL['pool'] = ProcessPoolExecutor(workers, initializer=_init_worker)
    return list(_POOL['pool'].map(_play, jobs, chunksize=1))


def build_cli():
    result = subprocess.run(['dotnet', 'build', os.path.join(CLI_DIR, 'DtEngine.Cli.csproj'), '-c', 'Release', '-nologo', '-v', 'q'],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(result.stdout + result.stderr)


def csharp_side(jobs, threads, tag):
    os.makedirs(WORK, exist_ok=True)
    jobs_path, out_path, trace_path = (os.path.join(WORK, f'{tag}_{n}.{e}') for n, e in (('jobs', 'json'), ('results', 'json'), ('trace', 'txt')))
    with open(jobs_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f)
    cmd = ['dotnet', CLI_DLL, 'run', '--snapshot', SNAPSHOT, '--jobs', jobs_path, '--out', out_path, '--trace-out', trace_path,
           '--threads', str(threads)]
    started = time.time()
    run = subprocess.run(cmd, capture_output=True, text=True)
    print('  C#:', run.stdout.strip().splitlines()[-1] if run.stdout.strip() else run.stderr.strip()[:300], f'({time.time() - started:.1f} s)')
    with open(out_path, encoding='utf-8') as f:
        results = {r['id']: r for r in json.load(f)}
    traces, current = {}, None
    if os.path.exists(trace_path):
        with open(trace_path, encoding='utf-8') as f:
            for line in f.read().split('\n'):
                if line.startswith('## job '):
                    current = line[7:]
                    traces[current] = []
                elif current is not None and line != '':
                    traces[current].append(line)
    return results, traces


def same_number(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    return a == b


def compare_results(py, cs):
    """First difference between the result dicts (None when equal)."""
    if len(py['runs']) != len(cs['runs']):
        return f'runs: {len(py["runs"])} against {len(cs["runs"])}'
    for k, (a, b) in enumerate(zip(py['runs'], cs['runs'])):
        for key in a:
            if key == 'parts':
                if len(a['parts']) != len(b['parts']):
                    return f'run {k}: {len(a["parts"])} parts against {len(b["parts"])}'
                for p, (x, y) in enumerate(zip(a['parts'], b['parts'])):
                    for kk in x:
                        if not same_number(x[kk], y[kk]):
                            return f'run {k} part {p} {kk}: {x[kk]!r} against {y[kk]!r}'
            elif not same_number(a[key], b[key]):
                return f'run {k} {key}: {a[key]!r} against {b[key]!r}'
    for key, value in py['summary'].items():
        other = cs['summary'][key]
        if value is None or other is None:
            if value is not other:
                return f'summary {key}: {value!r} against {other!r}'
        elif not same_number(value, other):
            return f'summary {key}: {value!r} against {other!r}'
    return None


def first_trace_difference(py_lines, cs_lines):
    for k in range(max(len(py_lines), len(cs_lines))):
        a = py_lines[k] if k < len(py_lines) else '<end>'
        b = cs_lines[k] if k < len(cs_lines) else '<end>'
        if a != b:
            return k, a, b
    return None


def compare(jobs, py_out, cs_results, cs_traces, trace):
    """Returns the failures: [{job, why, detail}]."""
    failures = []
    for job, py in zip(jobs, py_out):
        cs = cs_results.get(job['id'])
        if py['error'] is not None or (cs is not None and 'error' in cs):
            if py['error'] is not None and cs is not None and 'error' in cs:
                continue                                    # both raised: the same case, counted apart
            failures.append({'job': job, 'why': 'one engine raised', 'detail': {'python': py['error'], 'csharp': cs.get('error') if cs else None}})
            continue
        why = compare_results(py['result'], cs)
        if why:
            failures.append({'job': job, 'why': 'results', 'detail': why})
            continue
        if trace:
            diff = first_trace_difference(py['lines'], cs_traces.get(job['id'], []))
            if diff:
                k, a, b = diff
                failures.append({'job': job, 'why': 'trace', 'detail': {'line': k, 'python': a, 'csharp': b,
                                                                        'before': (py['lines'][k - 1] if k else None)}})
    return failures


def save_failures(failures, label):
    os.makedirs(FAILING, exist_ok=True)
    for f in failures:
        name = f"{label}_{f['job']['id']}".replace('/', '_').replace(' ', '_')
        with open(os.path.join(FAILING, name + '.json'), 'w', encoding='utf-8') as out:
            json.dump(f, out, indent=1, ensure_ascii=False)


def count_battles(py_out):
    return sum(len(r['parts']) for p in py_out if p['result'] for r in p['result']['runs'])


def run_set(jobs, args, label):
    """Plays the jobs in both engines and compares; returns (cases compared, battles, failures)."""
    started = time.time()
    py_out = python_side(jobs, args.workers)
    print(f'  Python: {len(jobs)} jobs, {count_battles(py_out)} battles ({time.time() - started:.1f} s)')
    cs_results, cs_traces = csharp_side(jobs, args.threads, label)
    failures = compare(jobs, py_out, cs_results, cs_traces, args.trace > 0)
    both = sum(1 for p, j in zip(py_out, jobs) if p['error'] is not None and 'error' in cs_results.get(j['id'], {}))
    lines = sum(len(p['lines']) for p in py_out)
    units = sum(1 for p in py_out for l in p['lines'] if l.startswith('U '))
    turns = sum(1 for p in py_out for l in p['lines'] if l.startswith('T '))
    TALLY['jobs'] += len(jobs); TALLY['lines'] += lines; TALLY['units'] += units; TALLY['turns'] += turns
    print(f'  compared {len(jobs)} jobs ({lines} trace lines, {units} unit lines, {turns} turn lines): {len(failures)} differences; {both} raised in both engines')
    for f in failures[:10]:
        print('   -', f['job']['id'], f['why'], json.dumps(f['detail'], ensure_ascii=False)[:600])
    if failures:
        save_failures(failures, label)
    return len(jobs), count_battles(py_out), failures


# effects whose code the ordinary cases rarely reach (random moves, dolls, Genjimaru, special damage, sacrifice, TP gifts ...)
RARE_EFFECTS = {2, 12, 74, 77, 84, 86, 105, 106, 111, 129, 130, 131, 132, 134, 138, 139, 140, 141, 142, 146, 152, 153, 154, 155, 179, 188,
                228, 229, 230, 231, 232, 233, 235, 258, 263, 320, 354, 358, 425, 426, 427, 434, 435, 440}


# --- the cases --------------------------------------------------------------------------------------------------------
def checkpoint_job(cid, side, seed, runs, trace, roles=None, label='cp'):
    return {'id': f'{label}-{side}-{cid}-{seed}', 'side': side, 'runs': runs, 'seed': seed, 'trace': trace, 'kit': None, 'options': {},
            'party': {'cid': cid, 'roles': roles, 'level': None, 'crown': None}, 'enemies': {'kind': 'checkpoint'}}


SMOKE_CHECKPOINTS = ('C01', 'C10', 'C24', 'C40')


def corpus_jobs(args):
    from sim import setup as setup_mod
    setup = setup_mod.load()
    jobs = []
    seeds = [int(s) for s in args.seeds.split(',')]
    for cp in setup.checkpoints:
        if args.only == 'smoke' and cp['ID'] not in SMOKE_CHECKPOINTS:
            continue
        for side in ('vanilla', 'variant'):
            for seed in seeds:
                jobs.append(checkpoint_job(cp['ID'], side, seed, args.runs, args.trace))
    if args.only == 'smoke':
        return jobs + regression_jobs(args)
    # the parties of measures/win_rates.py at its 17 bosses
    sys.path.insert(0, os.path.join(PROJECT, 'measures'))
    import win_rates
    bosses = [c.strip() for c in str(setup.settings['battery_checkpoints']).split(';') if c.strip()]
    for name, (roles, _, _) in win_rates.PARTIES.items():
        for cid in bosses:
            for side in ('vanilla', 'variant'):
                jobs.append(checkpoint_job(cid, side, int(seeds[0]), args.runs, args.trace, [r.strip() for r in roles.split(';')],
                                           label='wr-' + name.replace(' ', '_')))
    return jobs + regression_jobs(args)


def fixed_battle_jobs(args, state):
    """Every fixed battle of the game against the full party of the last chapter, below and above the level of its strongest enemy."""
    data, setup = state['sides']['vanilla'], state['setup']
    last = [cp['ID'] for cp in setup.checkpoints if cp['ID'].startswith('C')][-1]
    jobs = []
    for b in data.fixed:
        top = max(data.enemies[e]['level'] for e, _ in b['enemies'])
        for delta in (-5, 8):
            for side in ('vanilla', 'variant'):
                jobs.append({'id': f'fx-{side}-{b["floor"]}-{b["number"]}-{delta}', 'side': side, 'runs': 1, 'seed': 20261005,
                             'trace': args.trace, 'kit': None, 'options': {},
                             'party': {'cid': last, 'roles': None, 'level': max(1, min(99, top + delta)), 'crown': None},
                             'enemies': {'kind': 'fixed', 'battles': [[b['floor'], b['number']]]}})
    return jobs


def regression_jobs(args):
    jobs = []
    if os.path.isdir(REGRESSION):
        for n in sorted(os.listdir(REGRESSION)):
            with open(os.path.join(REGRESSION, n), encoding='utf-8') as f:
                case = json.load(f)
            job = case['job'] if 'job' in case else case
            jobs.append(dict(job, id='reg-' + job['id'], trace=args.trace))
    return jobs


def random_jobs(rnd, count, state, trace):
    from sim import scenario
    data, setup = state['sides']['vanilla'], state['setup']
    role_names = list(setup.roles)
    checkpoints = list(setup.checkpoints)
    fixed = data.fixed
    zones = [z for z in data.floors if z['formations']]
    ref = scenario.reference_levels(data, setup)
    rare_skills = [sk for sk in data.skills.values() if any(e in RARE_EFFECTS for e, _, _ in sk.effects)]
    item_ids = list(data.items)
    enchant_ids = list(data.enchants)
    jobs = []
    for n in range(count):
        side = rnd.choice(['vanilla', 'variant'])
        cp = rnd.choice(checkpoints)
        roles = [rnd.choice(role_names) for _ in range(rnd.randint(1, 5))]
        if rnd.random() < 0.5:
            roles = rnd.sample(role_names, min(5, len(role_names)))
        if rnd.random() < 0.55:
            floor = rnd.choice(fixed)
            battles = [floor]
            while rnd.random() < 0.3 and len(battles) < 3:
                battles.append(rnd.choice([b for b in fixed if b['floor'] == floor['floor']] or fixed))
            enemies = {'kind': 'fixed', 'battles': [[b['floor'], b['number']] for b in battles]}
            top = max(data.enemies[e]['level'] for b in battles for e, _ in b['enemies'])
            options = {'random_battle': True} if rnd.random() < 0.15 else {}
        else:
            zone = rnd.choice(zones)
            enemies = {'kind': 'zone', 'floor': zone['name'], 'battles': rnd.randint(1, 4)}
            top = max(data.enemies[e]['level'] for f in zone['formations'] for e, _ in f['enemies'] if e in data.enemies)
            options = {}
        level = rnd.choice([max(1, min(99, top + rnd.randint(-8, 6))), max(1, min(99, ref[cp['ID']][0] + rnd.randint(-6, 6)))])
        extra = {}
        if rnd.random() < 0.4:
            for skill in rnd.sample(list(data.skills.values()), rnd.randint(1, 8)):
                extra[str(skill.id)] = rnd.randint(1, skill.levels)
        if rnd.random() < 0.3 and rare_skills:
            for skill in rnd.sample(rare_skills, rnd.randint(1, 4)):
                extra[str(skill.id)] = rnd.randint(1, skill.levels)
        enchants = {}
        if rnd.random() < 0.3:
            for e in rnd.sample(enchant_ids, rnd.randint(1, 6)):
                enchants[str(e)] = rnd.randint(1, 4)
        bag = None
        if rnd.random() < 0.3:
            bag = rnd.sample(item_ids, rnd.randint(1, 5))
        job = {'id': f'rnd{n}', 'side': side, 'extra_skills': extra, 'extra_enchants': enchants, 'bag': bag, 'runs': rnd.randint(1, 3), 'seed': rnd.randrange(2 ** 31), 'trace': trace,
               'kit': rnd.choice([None, None, 0, 4, 12]), 'options': options,
               'party': {'cid': cp['ID'], 'roles': roles, 'level': level, 'crown': rnd.choice([None, None, 0])},
               'enemies': enemies}
        jobs.append(job)
    return jobs


# --- commands ------------------------------------------------------------------------------------------------------------
def cmd_export(args):
    import engine_export
    print(engine_export.write(SNAPSHOT))


def cmd_corpus(args):
    build_cli()
    jobs = corpus_jobs(args)
    if args.fixed:
        import pyref
        jobs += fixed_battle_jobs(args, pyref.load_state())
    print(f'corpus: {len(jobs)} jobs')
    total_jobs = total_battles = 0
    failures = []
    for start in range(0, len(jobs), args.batch):
        part = jobs[start:start + args.batch]
        n, b, f = run_set(part, args, 'corpus')
        total_jobs += n
        total_battles += b
        failures += f
    print(f'corpus: {total_jobs} jobs, {total_battles} battles, {TALLY["lines"]} trace lines ({TALLY["units"]} unit lines, {TALLY["turns"]} turn lines), {len(failures)} differences')
    return 1 if failures else 0


def cmd_random(args):
    import random
    seed = args.seed if args.seed is not None else int(time.time() * 1000) % (2 ** 31)
    print(f'random cases: generator seed {seed}, {args.count} cases')
    build_cli()
    import pyref
    state = pyref.load_state()
    rnd = random.Random(seed)
    jobs = random_jobs(rnd, args.count, state, args.trace)
    for job in jobs:
        job['id'] = f's{seed}-{job["id"]}'
    total_jobs = total_battles = 0
    failures = []
    for start in range(0, len(jobs), args.batch):
        part = jobs[start:start + args.batch]
        n, b, f = run_set(part, args, f'random{seed}')
        total_jobs += n
        total_battles += b
        failures += f
        print(f'  so far {total_jobs} cases, {total_battles} battles, {len(failures)} differences')
    print(f'random: generator seed {seed}: {total_jobs} cases, {total_battles} battles, {TALLY["lines"]} trace lines ({TALLY["units"]} unit lines, {TALLY["turns"]} turn lines), {len(failures)} differences')
    return 1 if failures else 0


def cmd_replay(args):
    build_cli()
    jobs = []
    for path in args.paths:
        with open(path, encoding='utf-8') as f:
            case = json.load(f)
        job = case['job'] if 'job' in case else case
        jobs.append(dict(job, trace=max(1, args.trace)))
    n, b, f = run_set(jobs, args, 'replay')
    return 1 if f else 0


def cmd_selfcheck(args):
    """The instrumented run of a job and the plain one give the same results."""
    import pyref
    state = pyref.load_state()
    pyref.install()
    job = checkpoint_job('C10', 'variant', 20261005, 2, 1)
    traced, _ = pyref.run_job(job, state)
    pyref.TRACER.plain = True
    plain, _ = pyref.run_job(dict(job, trace=0), state)
    pyref.TRACER.plain = False
    print('instrumented == plain:', traced == plain)
    return 0 if traced == plain else 1


def cmd_determinism(args):
    """The simulator against itself: the same jobs in two fresh sets of processes (other hash seeds, other order of work)."""
    import random
    import pyref
    state = pyref.load_state()
    jobs = random_jobs(random.Random(args.seed or 5), args.count, state, 1)
    first = python_side(jobs, args.workers)
    _POOL.pop('pool').shutdown()
    jobs.reverse()
    second = list(reversed(python_side(jobs, args.workers)))
    jobs.reverse()
    bad = [j['id'] for j, a, b in zip(jobs, first, second) if a['lines'] != b['lines'] or a['result'] != b['result'] or a['error'] != b['error']]
    print(f'determinism of sim/: {len(jobs)} jobs played twice, {len(bad)} differ', bad[:10])
    return 1 if bad else 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices=['export', 'corpus', 'random', 'replay', 'selfcheck', 'determinism'])
    p.add_argument('paths', nargs='*')
    p.add_argument('--count', type=int, default=200)
    p.add_argument('--seed', type=int, default=None)
    p.add_argument('--workers', type=int, default=6)
    p.add_argument('--threads', type=int, default=4)
    p.add_argument('--trace', type=int, default=1)
    p.add_argument('--runs', type=int, default=1)
    p.add_argument('--seeds', default='20261005,7')
    p.add_argument('--batch', type=int, default=200)
    p.add_argument('--only', default=None)
    p.add_argument('--fixed', action='store_true', help='corpus: also every fixed battle of the game')
    args = p.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    code = {'export': cmd_export, 'corpus': cmd_corpus, 'random': cmd_random, 'replay': cmd_replay, 'selfcheck': cmd_selfcheck, 'determinism': cmd_determinism}[args.command](args)
    sys.exit(code or 0)


if __name__ == '__main__':
    main()

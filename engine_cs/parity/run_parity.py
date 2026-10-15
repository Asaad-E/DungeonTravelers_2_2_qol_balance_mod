"""
Parity of the C# engine (engine_cs/) with the simulator of sim/, by traces.

    python engine_cs/parity/run_parity.py export                     writes the snapshot (build/engine_snapshot.json)
    python engine_cs/parity/run_parity.py corpus [options]           the fixed corpus: every checkpoint, both sides, a few seeds,
                                                                     the parties of measures/win_rates.py at its 17 bosses,
                                                                     and the cases kept in engine_cs/parity/cases/regression
    python engine_cs/parity/run_parity.py directed [options]         one case for each skill, enemy, formation, item and enchantment
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
import random
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


def extension_jobs(args, state):
    """Guest allies (every one, three checkpoints, both sides) and the arguments of build_member: unique_level and passives."""
    data = state['sides']['vanilla']
    jobs = []
    for name in sorted({n['name'] for n in data.npcs}) + ['none']:
        for cid in ('C10', 'C24', 'C40'):
            for side in ('vanilla', 'variant'):
                job = checkpoint_job(cid, side, 20261005, 1, args.trace, label='gu')
                job['id'] = f'gu-{side}-{cid}-{name}'.replace(' ', '_')
                job['party']['guest'] = name
                jobs.append(job)
    passive_skills = [sk for (category, _), sk in data.skills.items() if category == 'Passive']
    for level in (0, 1, 5, 10):
        for cid in ('C24', 'C40'):
            for side in ('vanilla', 'variant'):
                job = checkpoint_job(cid, side, 20261005, 1, args.trace, label='ul')
                job['id'] = f'ul-{side}-{cid}-{level}'
                job['party']['unique_level'] = level
                jobs.append(job)
    for k, skill in enumerate(passive_skills):
        job = checkpoint_job('C24' if k % 2 else 'C40', 'variant' if k % 3 else 'vanilla', 20261005, 1, args.trace, label='pv')
        job['id'] = f'pv-{skill.id}'
        job['party']['passives'] = {str(e): list(v)[-1] for e, _, v in skill.effects}
        jobs.append(job)
    return jobs


# the words of an AI script (tools/enemy_ai.py): flags of a result and of a skill word
AI_CHAIN, AI_TO_SET, AI_SLOT, AI_ATTACK_ID = 0x1000, 0x2000, 0x4000, 0x8000
AI_COMMANDS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)


def fuzz_command(rnd, attack_ids, n_attacks, depth=0, top=True, cid=None):
    """A command of a made-up AI script. Every command and every source of the decoder is drawn, the ones the game's
    scripts never use too."""
    cid = cid or rnd.choice(AI_COMMANDS)

    def word():
        r = rnd.random()
        if r < 0.55:
            return AI_SLOT | rnd.randrange(n_attacks + 1)
        if r < 0.9:
            return AI_ATTACK_ID | rnd.choice(attack_ids)
        return rnd.choice([AI_ATTACK_ID | 3999, 0x0005, AI_SLOT | 0x3FF0])           # an attack that does not exist, a word with no flag

    def source():
        return rnd.randrange(14)                                                      # 12 and 13 name no source
    if cid == 1:
        return {'cmd': 1, 'args': [word(), rnd.randrange(18)]}
    args = {2: lambda: [rnd.randint(0, 6)], 3: lambda: [source(), rnd.randint(0, 100)], 4: lambda: [source()],
            5: lambda: [word()], 6: lambda: [word()], 7: lambda: [word(), rnd.randint(1, 4)], 8: lambda: [], 9: lambda: [],
            10: lambda: [source(), rnd.randint(0, 100)], 11: lambda: [source()],
            12: lambda: [source(), rnd.randint(0, 100)], 13: lambda: [source(), rnd.randint(0, 100)],
            14: lambda: [source(), rnd.randint(0, 100)], 15: lambda: [word()]}[cid]()
    command = {'cmd': cid, 'args': args}
    r = rnd.random()
    if r < 0.2 and depth < 2:
        sub = rnd.choice([c for c in AI_COMMANDS if c != 1])
        command['result'] = AI_CHAIN | sub
        command['and'] = fuzz_command(rnd, attack_ids, n_attacks, depth + 1, False, sub)
    elif r < 0.45:
        command['result'] = AI_TO_SET | rnd.randrange(5)
    elif r < 0.75:
        command['result'] = AI_SLOT | rnd.randrange(n_attacks + 1)
    elif r < 0.91:
        command['result'] = AI_ATTACK_ID | rnd.choice(attack_ids)
    elif r < 0.95:
        command['result'] = AI_ATTACK_ID | 3999                                       # an attack that does not exist
    else:
        command['result'] = rnd.choice([0, 3, 0x0FFF])                                # a result with no flag decides nothing
    if top:
        command['once'] = rnd.random() < 0.3
    return command


def fuzz_script(rnd, attack_ids, n_attacks):
    if rnd.random() < 0.08:
        # sets that send each turn on to the next, round and round: the runner stops after its limit of switches
        sets = [{'set': number, 'weights': [rnd.choice([0, 1, 3]) for _ in range(16)],
                 'commands': [{'cmd': 2, 'args': [99], 'result': AI_TO_SET | ((number + 1) % 3)}]} for number in range(3)]
        return {'id': rnd.randrange(1000), 'opening': [], 'sets': sets}
    sets = []
    for number in rnd.sample(range(5), rnd.choice([0, 1, 1, 2, 3])):           # no set at all: only the opening decides
        sets.append({'set': number, 'weights': [rnd.choice([0, 0, 0, 1, 2, 5, 10]) for _ in range(16)],
                     'commands': [fuzz_command(rnd, attack_ids, n_attacks) for _ in range(rnd.randint(0, 4))]})
    return {'id': rnd.randrange(1000), 'opening': [fuzz_command(rnd, attack_ids, n_attacks) for _ in range(rnd.choice([0, 0, 1, 2, 3]))], 'sets': sets}


DIRECTED_CHECKPOINTS = ('C10', 'C20', 'C28', 'C36', 'C40', 'P10')


DIRECTED_PARTS = ('skills', 'enemies', 'formations', 'items', 'enchants', 'guests', 'summons', 'ai', 'gear', 'attacks', 'heals', 'statuses', 'performers', 'errors')


def directed_jobs(args, state, parts=DIRECTED_PARTS):
    """One case for each skill (forced on every member, at its top level and at level 1), each enemy (alone and in groups),
    each formation of each floor zone, each item (used by every member) and each enchantment: the rarely used paths of the
    code run in both engines. The rules of the policy are those of the sheet with one rule in front of them (job field `policies`)."""
    from sim.policy import usable_in_battle
    rnd = random.Random(args.directed_seed)
    data, setup = state['sides']['vanilla'], state['setup']
    role_names = list(setup.roles)
    ref = None
    jobs = []

    def party(cid, level=None, roles=None):
        return {'cid': cid, 'roles': roles, 'level': level, 'crown': None}

    def base(jid, side, cid, enemies, seed, **more):
        job = {'id': jid, 'side': side, 'runs': 1, 'seed': seed, 'trace': args.trace, 'kit': None, 'options': {}, 'party': party(cid), 'enemies': enemies}
        job.update(more)
        return job

    if 'skills' in parts:
        from sim import scenario
        from sim.policy import weapon_allows
        # who can use a skill: the member of a role, at a checkpoint, whose weapon allows it and whose TP pays for a level of it
        holders = {}
        for cid in DIRECTED_CHECKPOINTS:
            for role in role_names:
                try:
                    members = [u for u in scenario.party_of_roles(data, setup, cid, [role]) if u.kind == 'member' and getattr(u, 'role', None) == role]
                except Exception:
                    continue
                if members:
                    holders[(cid, role)] = members[0]
        for k, skill in enumerate(sorted((s for s in data.skills.values() if s.category in ('Technique', 'Magic') and usable_in_battle(s)),
                                         key=lambda s: s.id)):
            made = []
            for variant in range(2):
                side = ('vanilla', 'variant')[(k + variant) % 2]
                order = [DIRECTED_CHECKPOINTS[(k + variant + j) % len(DIRECTED_CHECKPOINTS)] for j in range(len(DIRECTED_CHECKPOINTS))]
                chosen = None
                for cid in order:
                    for role in rnd.sample(role_names, len(role_names)):
                        member = holders.get((cid, role))
                        if member is None or not weapon_allows(member, skill):
                            continue
                        affordable = [lv for lv in range(1, skill.levels + 1) if skill.tp[lv - 1] <= member.max_tp]
                        if affordable:
                            chosen = (cid, role, affordable[-1] if variant == 0 else affordable[0])
                            break
                    if chosen:
                        break
                cid, role, level = chosen or (order[0], None, skill.levels if variant == 0 else 1)
                job = base(f'ds-{skill.id}-{variant}', side, cid, {'kind': 'checkpoint'}, 1000 + k, extra_skills={str(skill.id): level},
                           policies=[{'Role': '*', 'Order': 0, 'Condition': 'always', 'Action': 'skill:' + skill.name}])
                roles = [role] if role else []
                roles += [r for r in rnd.sample(role_names, 5) if r != role]
                job['party']['roles'] = roles[:5]
                job['kit'] = 4 if variant else None
                jobs.append(job)
                made.append(job)
            # skills that work on a race or on a snack: against a group of that kind
            effects = {e for e, _, _ in skill.effects}
            pool = []
            if 110 in effects:
                pool = [e for e in data.enemies.values() if e['race'] == 2]
            elif 84 in effects:
                pool = [e for e in data.enemies.values() if e['snack']]
            elif effects & {87, 88}:
                pool = [e for e in data.enemies.values() if e['race'] in (5, 7, 8)]
            if pool:
                for variant in range(2):
                    group = [[rnd.choice(pool)['id'], True] for _ in range(3)]
                    top = max(data.enemies[g[0]]['level'] for g in group)
                    job = base(f'dr-{skill.id}-{variant}', ('vanilla', 'variant')[variant], DIRECTED_CHECKPOINTS[(k + variant) % len(DIRECTED_CHECKPOINTS)],
                               {'kind': 'enemies', 'groups': [group]}, 1500 + k, extra_skills={str(skill.id): skill.levels},
                               policies=[{'Role': '*', 'Order': 0, 'Condition': 'always', 'Action': 'skill:' + skill.name}])
                    job['party']['level'] = max(1, min(99, top + 3))
                    job['party']['roles'] = made[variant]['party']['roles']
                    job['runs'] = 4
                    jobs.append(job)
    if 'enemies' in parts:
        ids = sorted(data.enemies)
        for k, eid in enumerate(ids):
            e = data.enemies[eid]
            side = ('vanilla', 'variant')[k % 2]
            level = max(1, min(99, e['level'] + rnd.randint(-3, 6)))
            mates = [eid] + [rnd.choice(ids) for _ in range(rnd.choice([0, 0, 1, 2, 3]))]
            group = [[m, rnd.random() < 0.6] for m in mates]
            group[0][1] = True
            job = base(f'de-{eid}', side, DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'enemies', 'groups': [group]}, 2000 + k)
            job['party']['level'] = level
            job['runs'] = 2
            jobs.append(job)
    if 'formations' in parts:
        n = 0
        for z in data.floors:
            usable = [f for f in z['formations'] if all(e in data.enemies for e, _ in f['enemies'])]
            for index, f in enumerate(usable):
                top = max(data.enemies[e]['level'] for e, _ in f['enemies'])
                side = ('vanilla', 'variant')[n % 2]
                job = base(f'df-{n}', side, DIRECTED_CHECKPOINTS[n % len(DIRECTED_CHECKPOINTS)], {'kind': 'formation', 'picks': [[z['name'], index]]}, 3000 + n)
                job['party']['level'] = max(1, min(99, top + rnd.randint(-6, 5)))
                jobs.append(job)
                n += 1
    if 'items' in parts:
        for k, item_id in enumerate(sorted(data.items)):
            side = ('vanilla', 'variant')[k % 2]
            rows = [{'Role': '*', 'Order': 0, 'Condition': 'always', 'Action': 'item:' + kind} for kind in ('revive', 'cure', 'tp', 'heal')]
            job = base(f'di-{item_id}', side, DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'checkpoint'}, 4000 + k, bag=[item_id],
                       policies=rows)
            job['kit'] = 3
            jobs.append(job)
    if 'enchants' in parts:
        for k, enchant in enumerate(sorted(data.enchants)):
            side = ('vanilla', 'variant')[k % 2]
            pieces = (1, 2, 4)[k % 3]
            jobs.append(base(f'dc-{enchant}', side, DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'checkpoint'}, 5000 + k,
                             extra_enchants={str(enchant): pieces}))
    if 'attacks' in parts:
        # every attack of the enemies, used on each turn by an enemy of the game: its effects on a party that fights back
        ids = sorted(data.enemies)
        passive_attacks = sorted(a.id for a in data.attacks.values() if a.passive)
        for k, attack in enumerate(sorted((a for a in data.attacks.values() if not a.passive), key=lambda a: a.id)):
            side = ('vanilla', 'variant')[k % 2]
            eid = ids[(k * 7) % len(ids)]
            over = {'script': None, 'attacks': [attack.id]}
            if rnd.random() < 0.3:
                over['passives'] = [rnd.choice(passive_attacks)]
            group = [[eid, True, over]]
            if rnd.random() < 0.5:
                group.append([rnd.choice(ids), rnd.random() < 0.5])
            job = base(f'dt-{attack.id}', side, DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'enemies', 'groups': [group]}, 11000 + k)
            job['party']['level'] = max(1, min(99, data.enemies[eid]['level'] + rnd.randint(-2, 8)))
            if k % 3 == 0:
                job['party']['passives'] = {'253': 0.5}                      # Flowing Water Stance on the party: stab blows are dodged
            if k % 7 == 0:
                job['kit'] = 0
                job['policies'] = [{'Role': '*', 'Order': 0, 'Condition': 'ally_ailing', 'Action': 'cure'}]
            jobs.append(job)
        # Devil's Whisper after an ailment: an enemy that throws an ailment and then the whisper
        ailing = sorted(a.id for a in data.attacks.values() if not a.passive and any(e in AILMENT_EFFECTS and kind == 4 for e, kind, _ in a.effects))
        whisperers = [e for e in ids if any(a in (1575, 1576) for a in data.enemies[e]['passives'])]
        for k, eid in enumerate(whisperers):
            for j in range(3):
                over = {'script': None, 'attacks': [rnd.choice(ailing), 1575 if j % 2 else 1576]}
                job = base(f'dt-w{eid}-{j}', ('vanilla', 'variant')[j % 2], DIRECTED_CHECKPOINTS[(k + j) % len(DIRECTED_CHECKPOINTS)],
                           {'kind': 'enemies', 'groups': [[[eid, True, over], [eid, False, over]]]}, 12000 + 10 * k + j)
                job['party']['level'] = max(1, min(99, data.enemies[eid]['level'] + rnd.randint(0, 6)))
                job['runs'] = 12
                jobs.append(job)
    if 'heals' in parts:
        # each skill that heals, held by a healer and a diva against a hard fight, under the rules of the sheet
        for k, skill in enumerate(sorted((x for x in data.skills.values() if x.category in ('Technique', 'Magic') and any(e in (103, 104, 128, 131, 132) for e, _, _ in x.effects)),
                                         key=lambda x: x.id)):
            job = base(f'dh-{skill.id}', ('vanilla', 'variant')[k % 2], ('C36', 'C40', 'P10')[k % 3], {'kind': 'checkpoint'}, 13000 + k,
                       extra_skills={str(skill.id): skill.levels})
            job['party']['roles'] = ['healer', 'diva', 'tank', 'attacker', 'mage']
            job['runs'] = 3
            jobs.append(job)
    if 'statuses' in parts:
        # each status a skill puts, asked for by a rule in front of the others, with the skill held by every member
        effects = {}
        for x in data.skills.values():
            if x.category in ('Technique', 'Magic') and usable_in_battle(x):
                for e, kind, _ in x.effects:
                    if kind == 5:
                        effects.setdefault(e, []).append(x)
        for k, (effect, skills) in enumerate(sorted(effects.items())):
            job = base(f'dss-{effect}', ('vanilla', 'variant')[k % 2], DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'checkpoint'}, 14000 + k,
                       extra_skills={str(x.id): x.levels for x in skills[:3]},
                       policies=[{'Role': '*', 'Order': 0, 'Condition': 'always', 'Action': f'status:{effect}'}])
            job['party']['roles'] = rnd.sample(role_names, 5)
            job['runs'] = 2
            jobs.append(job)
    if 'performers' in parts:
        # every song and every dance held at once, each asked for in turn: the slots of a performer fill up
        from sim.battle import SONG_EFFECTS, DANCE_EFFECTS
        performances = sorted((x for x in data.skills.values() if x.category == 'Magic' or x.category == 'Technique'
                               if any(e in tuple(SONG_EFFECTS) + tuple(DANCE_EFFECTS) for e, kind, _ in x.effects if kind in (4, 5))), key=lambda x: x.id)
        wanted = sorted({e for x in performances for e, kind, _ in x.effects if e in tuple(SONG_EFFECTS) + tuple(DANCE_EFFECTS)})
        for k in range(24):
            chosen = rnd.sample(performances, min(len(performances), rnd.randint(2, 8)))
            rows = [{'Role': '*', 'Order': j, 'Condition': 'always', 'Action': f'status:{e}'} for j, e in enumerate(rnd.sample(wanted, min(len(wanted), 6)))]
            job = base(f'dpf-{k}', ('vanilla', 'variant')[k % 2], DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'checkpoint'}, 15000 + k,
                       extra_skills={str(x.id): x.levels for x in chosen}, policies=rows)
            job['party']['roles'] = ['diva', 'etoile', 'papillon', 'tank', 'healer']
            job['runs'] = 2
            jobs.append(job)
    if 'errors' in parts:
        # a rule the policy does not know: both engines raise
        for k, (cond, act) in enumerate((('sometimes', 'damage'), ('always', 'dance'), ('ally_down', 'summon'))):
            jobs.append(base(f'der-{k}', ('vanilla', 'variant')[k % 2], 'C10', {'kind': 'checkpoint'}, 16000 + k,
                             policies=[{'Role': '*', 'Order': 0, 'Condition': cond, 'Action': act}]))
    if 'gear' in parts:
        # every weapon, shield and piece of armour on the whole party (each class that can wear it), two-handed spears first
        weapons = sorted(data.equipment.values(), key=lambda p: (not (p['two_handed'] and p['type'] == 3), p['id']))
        for k, piece in enumerate(weapons):
            column = ('Weapon', 'Off hand', 'Head', 'Body', 'Accessory')[piece['category']]
            side = ('vanilla', 'variant')[k % 2]
            job = base(f'dw-{piece["id"]}', side, DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'checkpoint'}, 9000 + k)
            job['party']['pieces'] = {column: piece['name']}
            if piece['two_handed'] and piece['type'] == 3:
                # the skills that use a two-handed spear: forced at the top level
                job['extra_skills'] = {'26': 5}
                job['policies'] = [{'Role': '*', 'Order': 0, 'Condition': 'always', 'Action': 'skill:Daedalus Attack'}]
            jobs.append(job)
    if 'ai' in parts:
        # made-up scripts on enemies of the game: every command, source and target of the AI, and the paths of a missing script or attack
        ids = sorted(data.enemies)
        attack_ids = sorted(a.id for a in data.attacks.values() if not a.passive)
        passive_attacks = sorted(a.id for a in data.attacks.values() if a.passive)
        for k in range(args.ai_jobs):
            side = ('vanilla', 'variant')[k % 2]
            group = []
            for _ in range(rnd.randint(1, 4)):
                eid = rnd.choice(ids)
                e = data.enemies[eid]
                attacks = list(e['attacks']) if rnd.random() < 0.7 else [rnd.choice(attack_ids) for _ in range(rnd.randint(0, 6))]
                over = {}
                if rnd.random() < 0.8:
                    over['script'] = None if rnd.random() < 0.1 else fuzz_script(rnd, attack_ids, len(attacks))
                if attacks != list(e['attacks']):
                    over['attacks'] = attacks
                if rnd.random() < 0.4:
                    over['passives'] = [rnd.choice(passive_attacks) for _ in range(rnd.randint(1, 3))]
                group.append([eid, rnd.random() < 0.6, over])
            group[0][1] = True
            level = max(1, min(99, max(data.enemies[g[0]]['level'] for g in group) + rnd.randint(-4, 6)))
            job = base(f'da-{k}', side, DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)], {'kind': 'enemies', 'groups': [group]}, 8000 + k)
            job['party']['level'] = level
            job['runs'] = 2
            jobs.append(job)
    if 'guests' in parts:
        # every record of every guest ally: the stage is chosen by the level of the party, so the level of the record picks it
        for k, record in enumerate(data.npcs):
            side = ('vanilla', 'variant')[k % 2]
            cid = DIRECTED_CHECKPOINTS[k % len(DIRECTED_CHECKPOINTS)]
            job = base(f'dg-{record["id"]}', side, cid, {'kind': 'checkpoint'}, 6000 + k)
            job['party']['guest'] = record['name']
            job['party']['level'] = max(1, min(99, record['level']))
            job['runs'] = 2
            jobs.append(job)
    if 'summons' in parts:
        # every form of every summon of the grand sealbooks: at the first checkpoint that carries its sealbook, at the level of the form
        from sim import scenario
        for k, form in enumerate(data.summons):
            found = None
            for cp in setup.checkpoints:
                if scenario.grand_sealbook(setup, cp['Chapter'], cp['Floor']) == form['family']:
                    found = cp['ID']
                    break
            if found is None:
                continue
            side = ('vanilla', 'variant')[k % 2]
            job = base(f'dm-{form["id"]}', side, found, {'kind': 'checkpoint'}, 7000 + k)
            job['party']['level'] = max(1, min(99, form['level']))
            jobs.append(job)
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


AILMENT_EFFECTS = (113, 114, 115, 116, 117, 118, 119, 120, 122, 123)


def random_policy_rows(more, skill_names, status_effects):
    """One to three rules for every role (Role '*') in front of the sheet's: any condition and action of the vocabulary of the
    policy, with arguments of every kind."""
    def fraction():
        return round(more.uniform(0.05, 0.95), 2)

    def ailments():
        return ';'.join(str(e) for e in more.sample(AILMENT_EFFECTS, more.randint(1, 4)))
    conditions = [lambda: 'always', lambda: 'ally_hp_below:' + str(fraction()), lambda: 'party_hp_below:' + str(fraction()), lambda: 'ally_down',
                  lambda: 'ally_tp_below:' + str(fraction()), lambda: 'self_tp_below:' + str(fraction()), lambda: 'self_hp_below:' + str(fraction()),
                  lambda: 'enemy_buffed', lambda: 'ally_ailing' + more.choice(['', ':' + ailments()]), lambda: 'turn_at_most:' + str(more.randint(1, 4)),
                  lambda: 'enemies_at_least:' + str(more.randint(1, 4)), lambda: 'boss', lambda: 'no_doll', lambda: 'doll_slot_free']
    actions = [lambda: 'damage', lambda: 'heal:' + str(fraction()), lambda: 'revive', lambda: 'status:' + str(more.choice(status_effects)),
               lambda: 'dispel', lambda: 'doll', lambda: 'doll:' + more.choice(['Spartan|Oracles', 'Catalina', 'Musiy|Mercidarian', 'Nothing']),
               lambda: 'tp:' + str(fraction()), lambda: 'cure' + more.choice(['', ':' + ailments()]), lambda: 'ailment:' + ailments(),
               lambda: 'item:' + more.choice(['heal', 'tp', 'revive', 'cure', 'other']), lambda: 'skill:' + more.choice(skill_names),
               lambda: 'defend']
    return [{'Role': '*', 'Order': more.choice([0, 0, 1, 2, 3]), 'Condition': more.choice(conditions)(), 'Action': more.choice(actions)()}
            for _ in range(more.randint(1, 3))]


def random_jobs(rnd, count, state, trace, seed=0):
    from sim import scenario
    import random as random_mod
    more = random_mod.Random(seed * 7919 + 13)       # its own stream: the cases drawn from `rnd` stay what they were
    guest_names = sorted({n['name'] for n in state['sides']['vanilla'].npcs})
    passive_skills = [sk for (category, _), sk in state['sides']['vanilla'].skills.items() if category == 'Passive']
    skill_names = sorted({sk.name for (category, _), sk in state['sides']['vanilla'].skills.items() if category != 'Passive'})
    piece_names = {}
    for piece in state['sides']['vanilla'].equipment.values():
        column = ('Weapon', 'Off hand', 'Head', 'Body', 'Accessory')[piece['category']]
        piece_names.setdefault(column, set()).add(piece['name'])
    piece_names = {c: sorted(v) for c, v in piece_names.items()}
    status_effects = sorted({e for sk in state['sides']['vanilla'].skills.values() for e, kind, _ in sk.effects if kind == 5})
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
        # guest allies, the arguments unique_level and passives of build_member (drawn apart from the rest)
        if more.random() < 0.2:
            job['party']['guest'] = more.choice(guest_names + ['none'])
        if more.random() < 0.12:
            job['party']['unique_level'] = more.randint(0, 10)
        if more.random() < 0.3:
            job['settings'] = {'tp_weight': more.choice([0, 0.5, 2.0]), 'tp_reserve': more.choice([0, 0.3, 0.9]),
                               'heal_reserve_casts': more.choice([0, 2, 5]), 'party_buff_recast_share': more.choice([0, 0.5, 1.0]),
                               'punished_blow_floor': more.choice([0, 0.01, 0.2]), 'ailment_min_chance': more.choice([0, 0.5, 1.0])}
        if more.random() < 0.25:
            job['flags'] = {'survival_guard': more.random() < 0.5, 'interrupt_product': more.random() < 0.5,
                            'arcane_chance': more.choice([None, 0, 25, 60])}
        if more.random() < 0.3:
            job['policies'] = random_policy_rows(more, skill_names, status_effects)
        if more.random() < 0.3:
            # other gear than the role's own (a class that cannot wear a piece goes without it)
            job['party']['pieces'] = {column: more.choice(names) for column, names in piece_names.items() if more.random() < 0.6}
        if more.random() < 0.15:
            given = {}
            for skill in more.sample(passive_skills, more.randint(1, 4)):
                for effect, _, values in skill.effects:
                    given[str(effect)] = more.choice(list(values))
            job['party']['passives'] = given
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
        state = pyref.load_state()
        jobs += fixed_battle_jobs(args, state)
        jobs += extension_jobs(args, state)
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
    jobs = random_jobs(rnd, args.count, state, args.trace, seed)
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


def cmd_directed(args):
    import pyref
    build_cli()
    state = pyref.load_state()
    parts = tuple(args.only.split(',')) if args.only else DIRECTED_PARTS
    jobs = directed_jobs(args, state, parts)
    print(f'directed: {len(jobs)} jobs ({",".join(parts)})')
    total_jobs = total_battles = 0
    failures = []
    for start in range(0, len(jobs), args.batch):
        n, b, f = run_set(jobs[start:start + args.batch], args, 'directed')
        total_jobs += n
        total_battles += b
        failures += f
    print(f'directed: {total_jobs} jobs, {total_battles} battles, {TALLY["lines"]} trace lines ({TALLY["units"]} unit lines, {TALLY["turns"]} turn lines), {len(failures)} differences')
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
    jobs = random_jobs(random.Random(args.seed or 5), args.count, state, 1, args.seed or 5)
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
    p.add_argument('command', choices=['export', 'corpus', 'random', 'directed', 'replay', 'selfcheck', 'determinism'])
    p.add_argument('paths', nargs='*')
    p.add_argument('--count', type=int, default=200)
    p.add_argument('--seed', type=int, default=None)
    p.add_argument('--workers', type=int, default=6)
    p.add_argument('--threads', type=int, default=4)
    p.add_argument('--trace', type=int, default=1)
    p.add_argument('--runs', type=int, default=1)
    p.add_argument('--seeds', default='20261005,7')
    p.add_argument('--batch', type=int, default=200)
    p.add_argument('--only', default=None, help='corpus: smoke; directed: a comma list of parts (skills, enemies, formations, items, enchants, guests, summons, ai, gear, attacks, heals, statuses, performers, errors)')
    p.add_argument('--directed-seed', type=int, default=17)
    p.add_argument('--ai-jobs', type=int, default=900, help='directed: cases with made-up AI scripts')
    p.add_argument('--fixed', action='store_true', help='corpus: also every fixed battle of the game')
    args = p.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    code = {'export': cmd_export, 'corpus': cmd_corpus, 'random': cmd_random, 'directed': cmd_directed, 'replay': cmd_replay, 'selfcheck': cmd_selfcheck, 'determinism': cmd_determinism}[args.command](args)
    sys.exit(code or 0)


if __name__ == '__main__':
    main()

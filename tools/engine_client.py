"""
A bridge from the Python tools to the C# battle engine (engine_cs/): the same figures sim/ gives, played by `dtcli`.

    import engine_client as engine
    results = engine.play_party('variant', 'C24', roles, runs=200)          # as sim.scenario.play_party
    level, summary = engine.play_checkpoint('variant', 'C24', 200)          # as sim.measures.play_checkpoint
    summary = engine.summary('variant', job)                                 # as sim.measures.summary of the runs of a job
    engine.expedition('variant', 'St15_1150', 60, 'C40', roles=roles)       # as sim.measures.expedition
    engine.check_change('C10', 'C24')                                        # as sim.measures.check_change, whole variant against vanilla

The engine reads a snapshot of the data (tools/engine_export.py). The bridge writes it when it is missing or older than the files
it is made from, and builds `dtcli` when a source of engine_cs/ is newer than the program. The tools and the scripts of measures/ that
play battles use it through their `engine` command or their `--engine` flag; engine_cs/parity/gate_tools.py compares each with its
Python path, value by value.

A job is the dictionary of the engine (engine_cs/README.md, "Jobs"). `sides` are 'vanilla' and 'variant' (the Balance variant).
Differences from sim/: a result has a 'record' only when the job asks (record=True); walked_zones returns the names of the zones.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
BUILD = os.path.join(PROJECT, 'build')
SNAPSHOT = os.path.join(BUILD, 'engine_snapshot.json')
WORK = os.path.join(BUILD, 'engine_client')
CLI_PROJECT = os.path.join(PROJECT, 'engine_cs', 'src', 'DtEngine.Cli', 'DtEngine.Cli.csproj')
CLI_DLL = os.path.join(PROJECT, 'engine_cs', 'src', 'DtEngine.Cli', 'bin', 'Release', 'net10.0', 'dtcli.dll')

INT_FIELDS = ('actions', 'enemy_damage', 'enemy_actions', 'party_max_hp', 'alive')
FLOAT_FIELDS = ('time', 'lowest_hp', 'hp_left', 'tp_left')
BOOL_FIELDS = ('won', 'lost')

_SETTINGS = {}


def newest(paths, suffixes=None):
    """The latest modification time of the files under the paths (a file or a folder)."""
    found = 0.0
    for path in paths:
        if os.path.isfile(path):
            found = max(found, os.path.getmtime(path))
            continue
        for folder, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in ('bin', 'obj', '__pycache__')]
            for name in files:
                if suffixes is None or name.endswith(suffixes):
                    found = max(found, os.path.getmtime(os.path.join(folder, name)))
    return found


def snapshot_is_stale():
    if not os.path.exists(SNAPSHOT) or not os.path.exists(SNAPSHOT + '.hashes'):
        return True
    inputs = [os.path.join(PROJECT, 'data_tables'), os.path.join(PROJECT, 'backups'), os.path.join(PROJECT, 'sim'),
              os.path.join(PROJECT, 'tools'), os.path.join(PROJECT, 'config.json')]
    return newest([p for p in inputs if os.path.exists(p)], ('.xlsx', '.json', '.pck', '.bin', '.py', '.txt')) > os.path.getmtime(SNAPSHOT)


def ensure_snapshot():
    """Writes the snapshot when it is missing or older than the data and the readers it is made from."""
    if snapshot_is_stale():
        sys.path.insert(0, PROJECT)
        sys.path.insert(0, HERE)
        import engine_export
        engine_export.write(SNAPSHOT)
        _SETTINGS.clear()
    return SNAPSHOT


def ensure_built():
    """Builds dtcli when it is missing or older than a source of engine_cs/src."""
    sources = newest([os.path.join(PROJECT, 'engine_cs', 'src')], ('.cs', '.csproj'))
    if not os.path.exists(CLI_DLL) or os.path.getmtime(CLI_DLL) < sources:
        run = subprocess.run(['dotnet', 'build', CLI_PROJECT, '-c', 'Release', '-nologo', '-v', 'q'], capture_output=True, text=True)
        if run.returncode != 0:
            raise RuntimeError('dtcli did not build:\n' + run.stdout + run.stderr)
    return CLI_DLL


# --- sides and setups of the tools' own ------------------------------------------------------------------------------------
_EXTRA = {'sides': {}, 'setups': {}}        # name -> the text of the side or the setup
_NAMES = {}                                  # content hash -> name in the snapshot


def _known():
    """The sides and the setup the snapshot holds, by content."""
    if not _NAMES:
        ensure_snapshot()
        with open(SNAPSHOT + '.hashes', encoding='utf-8') as f:
            hashes = json.load(f)
        for name, digest in hashes['sides'].items():
            _NAMES[digest] = name
        _NAMES[hashes['setup']] = None
    return _NAMES


def side_of(data):
    """The name of a GameData for the jobs: 'vanilla' or 'variant' when the snapshot holds the same data, else it is sent with the next call."""
    import engine_export
    text = engine_export.text_of(engine_export.side_json(data, engine_export.flags_of(data)))
    digest = engine_export.digest(text)
    known = _known()
    if digest in known and known[digest] is not None:
        return known[digest]
    name = 'side-' + digest[:16]
    _EXTRA['sides'][name] = text
    return name


def setup_of(setup):
    """The name of a Setup for the jobs: None when the snapshot holds the same choices, else it is sent with the next call."""
    import engine_export
    text = engine_export.text_of(engine_export.setup_json(setup))
    digest = engine_export.digest(text)
    if digest in _known() and _known()[digest] is None:
        return None
    name = 'setup-' + digest[:16]
    _EXTRA['setups'][name] = text
    return name


def _extra_file(jobs, folder):
    """The file of the sides and setups the jobs name that the snapshot does not hold; None when they name none."""
    sides, setups = set(), set()
    for job in jobs:
        sides.update(x for x in (job.get('side'), job.get('changed_side')) if x in _EXTRA['sides'])
        if job.get('setup') in _EXTRA['setups']:
            setups.add(job['setup'])
    if not sides and not setups:
        return None
    path = os.path.join(folder, 'extra.json')
    with open(path, 'w', encoding='utf-8', newline=None) as f:
        f.write('{"sides":{' + ','.join(json.dumps(n) + ':' + _EXTRA['sides'][n] for n in sorted(sides)) + '},"setups":{'
                + ','.join(json.dumps(n) + ':' + _EXTRA['setups'][n] for n in sorted(setups)) + '}}')
    return path


def settings():
    """The settings of the model, from the snapshot (sheet Settings of sim_setup.xlsx)."""
    if not _SETTINGS:
        with open(ensure_snapshot(), encoding='utf-8') as f:
            _SETTINGS.update(json.load(f)['setup']['settings'])
    return _SETTINGS


def _call(command, jobs, threads, errors=False):
    ensure_snapshot()
    ensure_built()
    os.makedirs(WORK, exist_ok=True)
    folder = tempfile.mkdtemp(dir=WORK)
    jobs_path, out_path = os.path.join(folder, 'jobs.json'), os.path.join(folder, 'results.json')
    with open(jobs_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f)
    cmd = ['dotnet', CLI_DLL, command, '--snapshot', SNAPSHOT, '--jobs', jobs_path, '--out', out_path]
    extra = _extra_file(jobs, folder)
    if extra:
        cmd += ['--extra', extra]
    if threads:
        cmd += ['--threads', str(threads)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode != 0 and not os.path.exists(out_path):
        raise RuntimeError('dtcli failed:\n' + run.stdout + run.stderr)
    with open(out_path, encoding='utf-8') as f:
        results = json.load(f)
    for name in (jobs_path, out_path, extra):
        try:
            os.remove(name)
        except (OSError, TypeError):
            pass
    try:
        os.rmdir(folder)
    except OSError:
        pass
    by_id = {r['id']: r for r in results}
    out = []
    for job in jobs:
        r = by_id[job['id']]
        if 'error' in r and not errors:
            raise RuntimeError(f"job {job['id']}: {r['error']}")
        out.append(r)
    return out


# --- the shapes of sim/ -------------------------------------------------------------------------------------------------
class RecUnit:
    """A unit as the recorder of a result names it: what the tools read of the keys of sim.battle.Recorder."""

    def __init__(self, raw):
        self.position, self.name, self.kind, self.side, self.level = raw['p'], raw['name'], raw['kind'], raw['side'], raw['level']
        self.role, self.owner = raw['role'], None

    def __repr__(self):
        return f'<{self.kind} {self.name} L{self.level}>'


class Recorder:
    """sim.battle.Recorder, with RecUnit keys."""
    TABLES = ('damage', 'healing', 'actions', 'tp_spent', 'chants_started', 'chants_done', 'chants_broken', 'performances_broken',
              'turns_lost', 'denied', 'delayed', 'largest_hit', 'deaths')

    def __init__(self, raw):
        units = {u['p']: RecUnit(u) for u in raw['units']}
        for u in raw['units']:
            if u['owner'] is not None:
                units[u['p']].owner = units[u['owner']]
        self.units = list(units.values())
        for name in self.TABLES:
            setattr(self, name, {units[p]: v for p, v in raw[name]})
        self.skill_uses = {(units[p], n): v for p, n, v in raw['skill_uses']}
        self.items_used = {(('stolen', units[b]) if a == 'stolen' else (units[a], b)): v for a, b, v in raw['items_used']}
        self.kills = raw['kills']


def _part(raw):
    out = {}
    if 'record' in raw:
        out['record'] = Recorder(raw['record'])
    for key in BOOL_FIELDS:
        out[key] = bool(raw[key])
    for key in INT_FIELDS:
        out[key] = int(raw[key])
    for key in FLOAT_FIELDS:
        out[key] = float(raw[key])
    return out


def _run(raw):
    out = _part(raw)
    out['parts'] = [_part(p) for p in raw['parts']]
    if out['parts'] and 'record' in out['parts'][0]:
        out['record'] = out['parts'][0]['record']           # as sim.scenario.play: the record of the first fight stays at the top
    return out


def _summary(raw):
    return {'won': float(raw['won']), 'time': None if raw['time'] is None else float(raw['time']),
            'lowest_hp': float(raw['lowest_hp']), 'pressure': float(raw['pressure'])}


def make_job(side, cid, roles=None, runs=1, seed=None, level=None, crown=None, enemies=None, options=None, kit=None, guest=None, name=None,
             record=False, setup=None, recipe=None, extra_skills=None, settings_=None, policies=None, policy_rows=None,
             enemy_changes=None, flags=None):
    """A job of the engine: the party of a checkpoint (its chapter, gear and crown bonus; roles: the sheet Composition when None) against
    the fixed battles of the checkpoint, or against `enemies` ({'kind': 'fixed', 'battles': [[floor, number], ...]},
    {'kind': 'zone', 'floor': zone name, 'battles': n} or {'kind': 'chain', 'zones': [names], 'seed': s, 'battles': n}, the
    last with one generator for all the runs). seed: the setting seed when None. side: a name from side_of; setup: a name from
    setup_of (None: the choices of the snapshot). recipe: what is done to the reference party (engine_cs/README.md, "Party
    recipe"). settings_: settings of the model for this job alone; policies: rows added to the sheet Policies; policy_rows: the whole
    sheet Policies for this job (the rows as setup.policies holds them). enemy_changes: {enemy id: {hp, atk, def, int, res, dex, agi,
    res_slash ... res_lightning: value}}, the stats of those enemy records for this job (GameData.with_changes on 'enemies')."""
    party = {'cid': cid, 'roles': roles, 'level': level, 'crown': crown}
    if guest is not None:
        party['guest'] = guest
    if recipe is not None:
        party['recipe'] = recipe
    job = {'id': name or f'{side}-{cid}', 'side': side, 'runs': int(runs), 'seed': int(settings()['seed'] if seed is None else seed),
           'trace': 0, 'record': bool(record), 'kit': kit, 'options': dict(options or {}), 'party': party,
           'enemies': enemies or {'kind': 'checkpoint'}}
    if setup is not None:
        job['setup'] = setup
    if extra_skills:
        job['extra_skills'] = {str(k): v for k, v in extra_skills.items()}
    if settings_:
        job['settings'] = dict(settings_)
    if policies:
        job['policies'] = list(policies)
    if policy_rows is not None:
        job['policy_rows'] = [dict(r) for r in policy_rows]
    if flags:
        job['flags'] = dict(flags)
    if enemy_changes:
        job['enemy_changes'] = {str(k): dict(v) for k, v in enemy_changes.items()}
    return job


def run_jobs(jobs, threads=None, errors=False):
    """Plays the jobs: for each, {'runs': the dictionaries sim.scenario.play returns (one per run), 'summary': sim.measures.summary of them,
    'tested': the characters the tested members of its recipe were given}. errors: a job that fails gives {'error': text} in its place
    (else the call raises)."""
    return [{'error': raw['error']} if 'error' in raw else
            {'runs': [_run(r) for r in raw['runs']], 'summary': _summary(raw['summary']), 'tested': raw.get('tested', [])}
            for raw in _call('run', jobs, threads, errors)]


def play_jobs(jobs, threads=None):
    """Plays the jobs: for each, the list of the dictionaries sim.scenario.play returns (one per run, with 'record' when the job asks) and the
    summary sim.measures.summary gives. Returns [(results, summary)]."""
    return [(r['runs'], r['summary']) for r in run_jobs(jobs, threads)]


def play(job, threads=None):
    """sim.scenario.play of a job: the list of results of its runs."""
    return play_jobs([job], threads)[0][0]


def summary(job, threads=None):
    """sim.measures.summary of the runs of a job."""
    return play_jobs([job], threads)[0][1]


def play_party(side, cid, roles, runs, seed=None, threads=None, **more):
    """sim.scenario.play_party: the fights of a checkpoint played by the party of these roles. more: the other arguments of make_job."""
    return play(make_job(side, cid, roles=list(roles), runs=runs, seed=seed, **more), threads)


def _measure(jobs, threads=None):
    return _call('measure', jobs, threads)


def play_checkpoint(side, cid, runs, threads=None, enemy_changes=None, setup=None):
    """sim.measures.play_checkpoint: (level of the party, summary of its runs at the fixed battles of the checkpoint)."""
    return play_checkpoints([(side, cid, runs, enemy_changes, setup)], threads)[0]


def play_checkpoints(items, threads=None):
    """Several play_checkpoint at once: items [(side, cid, runs, enemy_changes or None, setup or None)] -> [(level, summary)]."""
    jobs = []
    for k, (side, cid, runs, changes, setup) in enumerate(items):
        job = {'id': f'pc{k}', 'measure': 'play_checkpoint', 'side': side, 'cid': cid, 'runs': int(runs)}
        if changes:
            job['enemy_changes'] = {str(e): dict(v) for e, v in changes.items()}
        if setup is not None:
            job['setup'] = setup
        jobs.append(job)
    return [(int(raw['level']), _summary(raw['summary'])) for raw in _measure(jobs, threads)]


class SerialPool:
    """In place of a ProcessPoolExecutor for the scripts that play on the engine: the cells run one after the other, each call of the
    engine using every core."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def map(self, fn, items, chunksize=None):
        return map(fn, items)


# --- drop-in versions of the calls the tools make on a GameData and a Setup -------------------------------------------------
def play_party_sim(data, setup, cid, roles, runs, seed=None, **more):
    """sim.scenario.play_party(data, setup, cid, roles, runs): the data and the setup are sent when the snapshot does not hold them."""
    return play_party(side_of(data), cid, roles, runs, seed=seed, setup=setup_of(setup), **more)


def summary_sim(data, setup, cid, roles, runs, seed=None, **more):
    """sim.measures.summary(sim.scenario.play_party(...))."""
    job = make_job(side_of(data), cid, roles=list(roles), runs=runs, seed=seed, setup=setup_of(setup), **more)
    return summary(job)


def play_checkpoint_sim(data, setup, cid, runs):
    """sim.measures.play_checkpoint(data, setup, cid, runs)."""
    return play_checkpoint(side_of(data), cid, runs, setup=setup_of(setup))


def check_change_sim(data, changed, setup, cids, runs=None):
    """sim.measures.check_change(data, setup, [], cids, runs=runs, changed=changed)."""
    return check_change(*cids, side=side_of(data), changed_side=side_of(changed), runs=runs, setup=setup_of(setup))


def skill_scores(items, threads=None):
    """The analysis of tools/skill_worth.py scores() and tools/sim_audit.py usage, played by the engine. items: [{side, setup, job (a job of
    make_job whose recipe names the tested member), contexts ([{'kind': 'fixed', 'floor', 'number'} or {'kind': 'draws', 'zones', 'seed',
    'count'}]), zone (the battles carry the zone of their cell), attack_first}]. Returns [{'tested': the character, 'contexts': [[(name,
    value), ...] one list for each group of enemies]}]; a list holds the options in the order of a Python dict."""
    jobs = []
    for k, item in enumerate(items):
        job = {'id': f'scores{k}', 'measure': 'skill_scores', 'side': item['side'], 'job': item['job'], 'contexts': item['contexts'],
               'zone': bool(item.get('zone')), 'attack_first': bool(item.get('attack_first'))}
        if item.get('setup') is not None:
            job['setup'] = item['setup']
        jobs.append(job)
    return [{'tested': raw['tested'], 'contexts': [[(n, v) for n, v in ctx] for ctx in raw['contexts']]} for raw in _measure(jobs, threads)]


def probe(items, threads=None):
    """The probe of tools/sim_audit.py actives, played by the engine. items: [{side, setup, job (the reference party: make_job), user (a tested
    member), skill (id), level, expect ([{'key', 'test': 'hp_lost' | 'ailment' | 'status' | 'changed', 'effect', 'gauge_above', 'fell'}]),
    tries, prelude}]. Returns [{'missed': the keys never met, 'crash': a message or None, 'user': the character}]."""
    jobs = []
    for k, item in enumerate(items):
        job = dict(item, id=f'probe{k}', measure='probe')
        jobs.append(job)
    return [{'missed': raw['missed'], 'crash': raw['crash'], 'user': raw['user']} for raw in _measure(jobs, threads)]


def expedition(side, floor, level, cid, roles=None, battles=None, runs=None, kit=None, threads=None):
    """sim.measures.expedition: the mean battles won, the share of runs that reached the limit, the TP left after the first battles."""
    job = {'id': 'ex', 'measure': 'expedition', 'side': side, 'floor': floor, 'level': int(level), 'cid': cid, 'roles': roles,
           'battles': battles, 'runs': runs, 'kit': kit}
    raw = _measure([job], threads)[0]
    return {'won': float(raw['won']), 'reached_limit': float(raw['reached_limit']), 'tp_after': [float(x) for x in raw['tp_after']]}


def walked_zones(side, floor, level):
    """sim.scenario.walked_zones, as the names of the zones (the records are in the data of sim/)."""
    return _measure([{'id': 'wz', 'measure': 'walked_zones', 'side': side, 'floor': floor, 'level': int(level)}])[0]['zones']


def check_change(*checkpoints, side='vanilla', changed_side='variant', runs=None, threads=None, setup=None):
    """sim.measures.check_change with the data already changed: [(checkpoint, figures before, figures after, windows left)];
    the figures hold the level of the party as sim/ puts it there."""
    jobs = [{'id': f'cc-{cid}', 'measure': 'check_change', 'side': side, 'changed_side': changed_side, 'checkpoints': [cid],
             'runs': runs, **({'setup': setup} if setup is not None else {})} for cid in checkpoints]   # one job a checkpoint, so that they run in parallel
    out = []
    for row in (row for raw in _measure(jobs, threads) for row in raw['rows']):
        before = dict(_summary(row['before']), level=int(row['level_before']))
        after = dict(_summary(row['after']), level=int(row['level_after']))
        out.append((row['cid'], before, after, list(row['out'])))
    return out

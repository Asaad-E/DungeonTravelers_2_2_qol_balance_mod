"""
A bridge from the Python tools to the C# battle engine (engine_cs/): the same figures sim/ gives, played by `dtcli`.

    import engine_client as engine
    results = engine.play_party('variant', 'C24', roles, runs=200)          # as sim.scenario.play_party, without 'record'
    level, summary = engine.play_checkpoint('variant', 'C24', 200)          # as sim.measures.play_checkpoint
    summary = engine.summary('variant', job)                                 # as sim.measures.summary of the runs of a job
    engine.expedition('variant', 'St15_1150', 60, 'C40', roles=roles)       # as sim.measures.expedition
    engine.check_change('C10', 'C24')                                        # as sim.measures.check_change, whole variant against vanilla

The engine reads a snapshot of the data (tools/engine_export.py). The bridge writes it when it is missing or older than the files
it is made from, and builds `dtcli` when a source of engine_cs/ is newer than the program. Nothing else of the tools uses this
module yet; engine_cs/parity/test_engine_client.py shows that its figures equal those of sim/.

A job is the dictionary of the engine (engine_cs/README.md, "Jobs"). `sides` are 'vanilla' and 'variant' (the Balance variant).
Differences from sim/: a result has no 'record' (the recorder of the battle is not ported); walked_zones returns the names of the zones.
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
    if not os.path.exists(SNAPSHOT):
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


def settings():
    """The settings of the model, from the snapshot (sheet Settings of sim_setup.xlsx)."""
    if not _SETTINGS:
        with open(ensure_snapshot(), encoding='utf-8') as f:
            _SETTINGS.update(json.load(f)['setup']['settings'])
    return _SETTINGS


def _call(command, jobs, threads):
    ensure_snapshot()
    ensure_built()
    os.makedirs(WORK, exist_ok=True)
    folder = tempfile.mkdtemp(dir=WORK)
    jobs_path, out_path = os.path.join(folder, 'jobs.json'), os.path.join(folder, 'results.json')
    with open(jobs_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f)
    cmd = ['dotnet', CLI_DLL, command, '--snapshot', SNAPSHOT, '--jobs', jobs_path, '--out', out_path]
    if threads:
        cmd += ['--threads', str(threads)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode != 0 and not os.path.exists(out_path):
        raise RuntimeError('dtcli failed:\n' + run.stdout + run.stderr)
    with open(out_path, encoding='utf-8') as f:
        results = json.load(f)
    for name in (jobs_path, out_path):
        try:
            os.remove(name)
        except OSError:
            pass
    try:
        os.rmdir(folder)
    except OSError:
        pass
    by_id = {r['id']: r for r in results}
    out = []
    for job in jobs:
        r = by_id[job['id']]
        if 'error' in r:
            raise RuntimeError(f"job {job['id']}: {r['error']}")
        out.append(r)
    return out


# --- the shapes of sim/ -------------------------------------------------------------------------------------------------
def _part(raw):
    out = {}
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
    return out


def _summary(raw):
    return {'won': float(raw['won']), 'time': None if raw['time'] is None else float(raw['time']),
            'lowest_hp': float(raw['lowest_hp']), 'pressure': float(raw['pressure'])}


def make_job(side, cid, roles=None, runs=1, seed=None, level=None, crown=None, enemies=None, options=None, kit=None, guest=None, name=None):
    """A job of the engine: the party of a checkpoint (its chapter, gear and crown bonus; roles: the sheet Composition when None) against
    the fixed battles of the checkpoint, or against `enemies` ({'kind': 'fixed', 'battles': [[floor, number], ...]} or
    {'kind': 'zone', 'floor': zone name, 'battles': n}). seed: the setting seed when None."""
    party = {'cid': cid, 'roles': roles, 'level': level, 'crown': crown}
    if guest is not None:
        party['guest'] = guest
    return {'id': name or f'{side}-{cid}', 'side': side, 'runs': int(runs), 'seed': int(settings()['seed'] if seed is None else seed),
            'trace': 0, 'kit': kit, 'options': dict(options or {}), 'party': party, 'enemies': enemies or {'kind': 'checkpoint'}}


def play_jobs(jobs, threads=None):
    """Plays the jobs: for each, the list of the dictionaries sim.scenario.play returns (one per run, without 'record') and the
    summary sim.measures.summary gives. Returns [(results, summary)]."""
    return [([_run(r) for r in raw['runs']], _summary(raw['summary'])) for raw in _call('run', jobs, threads)]


def play(job, threads=None):
    """sim.scenario.play of a job: the list of results of its runs."""
    return play_jobs([job], threads)[0][0]


def summary(job, threads=None):
    """sim.measures.summary of the runs of a job."""
    return play_jobs([job], threads)[0][1]


def play_party(side, cid, roles, runs, seed=None, threads=None):
    """sim.scenario.play_party: the fights of a checkpoint played by the party of these roles."""
    return play(make_job(side, cid, roles=list(roles), runs=runs, seed=seed), threads)


def _measure(jobs, threads=None):
    return _call('measure', jobs, threads)


def play_checkpoint(side, cid, runs, threads=None):
    """sim.measures.play_checkpoint: (level of the party, summary of its runs at the fixed battles of the checkpoint)."""
    raw = _measure([{'id': 'pc', 'measure': 'play_checkpoint', 'side': side, 'cid': cid, 'runs': int(runs)}], threads)[0]
    return int(raw['level']), _summary(raw['summary'])


def expedition(side, floor, level, cid, roles=None, battles=None, runs=None, kit=None, threads=None):
    """sim.measures.expedition: the mean battles won, the share of runs that reached the limit, the TP left after the first battles."""
    job = {'id': 'ex', 'measure': 'expedition', 'side': side, 'floor': floor, 'level': int(level), 'cid': cid, 'roles': roles,
           'battles': battles, 'runs': runs, 'kit': kit}
    raw = _measure([job], threads)[0]
    return {'won': float(raw['won']), 'reached_limit': float(raw['reached_limit']), 'tp_after': [float(x) for x in raw['tp_after']]}


def walked_zones(side, floor, level):
    """sim.scenario.walked_zones, as the names of the zones (the records are in the data of sim/)."""
    return _measure([{'id': 'wz', 'measure': 'walked_zones', 'side': side, 'floor': floor, 'level': int(level)}])[0]['zones']


def check_change(*checkpoints, side='vanilla', changed_side='variant', runs=None, threads=None):
    """sim.measures.check_change with the data already changed: [(checkpoint, figures before, figures after, windows left)];
    the figures hold the level of the party as sim/ puts it there."""
    jobs = [{'id': f'cc-{cid}', 'measure': 'check_change', 'side': side, 'changed_side': changed_side, 'checkpoints': [cid],
             'runs': runs} for cid in checkpoints]             # one job a checkpoint, so that they run in parallel
    out = []
    for row in (row for raw in _measure(jobs, threads) for row in raw['rows']):
        before = dict(_summary(row['before']), level=int(row['level_before']))
        after = dict(_summary(row['after']), level=int(row['level_after']))
        out.append((row['cid'], before, after, list(row['out'])))
    return out

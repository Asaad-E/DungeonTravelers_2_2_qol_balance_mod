"""
Bring each boss fight of the Balance variant back into the difficulty window of vanilla (Regression R08, R10).
Generated: docs/generated/BOSS_FIT.md.

    python tools/boss_fit.py all        every checkpoint docs/generated/DIFFICULTY_CURVE data marks easier
    python tools/boss_fit.py report
    python tools/boss_fit.py engine                 the same as `all`, played by the C# engine (engine_cs/) in one call
    python tools/boss_fit.py gentle-engine [C26;C30]    the same as `gentle`, played by the C# engine

For a checkpoint whose fights the variant made easier (tools/difficulty_curve.py), the enemies of its boss fights that
appear in no random formation (so that common fights are not touched) get a factor on HP and a factor on ATK and INT.
The search walks the grid of Settings boss_fit_hp and boss_fit_attack (smallest change first, HP before attack) and
keeps the first pair whose fights, played by the reference party at the reference level, land inside the windows of
vanilla (Settings check_*_window) for wins, length and lowest HP. Lever L01 (enemy stats): benign.

    python tools/boss_fit.py gentle [processes]     the same with a condition on the other parties
    python tools/boss_fit.py gentle 6 C26;C30       again, the checkpoints a change touched
    python tools/boss_fit.py gentle-report

gentle (decided 2026-10-11: "a little harder to make up for it, as long as the five parties stay inside their share"):
every checkpoint the curve marks easier, but those of Settings boss_fit_skip. The pairs are those of Settings
boss_fit_gentle only. A pair is allowed when no figure of the reference party leaves the window of vanilla on the
harder side and every archetype of the sheet BatteryParties (the best of its parties) still wins at least the floor of
the class the guide gives the boss (sheet GuideDifficulty, Settings guide_<class>_min_won). A boss where an archetype
is below that floor before any change is left alone. Among the allowed pairs and no change, the one nearest to
vanilla is kept: the sum, over wins, length, lowest HP and pressure, of the gap to vanilla in window widths.
"""
import json
import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'boss_fit')
REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'BOSS_FIT.md')
CURVE_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'difficulty_curve')

from sim import measures, scenario                       # noqa: E402
from sim import setup as setup_mod                       # noqa: E402
from sim.data import game_data                           # noqa: E402
from sim.variant import balance_data                     # noqa: E402


def easier(setup):
    rows = []
    for name in sorted(os.listdir(CURVE_DIR)):
        with open(os.path.join(CURVE_DIR, name), encoding='utf-8') as f:
            rows += json.load(f)
    out = []
    for r in rows:
        if any(k in r['out'] for k in ('won', 'time', 'lowest_hp')):
            out.append(r)
    return out


def boss_enemies(data, setup, cid):
    cp = setup.checkpoint(cid)
    common = {e for z in data.floors for f in z['formations'] for e, _ in f['enemies']}
    ids = set()
    for n in scenario.battle_numbers(cp):
        battle = next(b for b in data.fixed if b['floor'] == cp['Floor'] and b['number'] == n)
        ids |= {e for e, _ in battle['enemies']}
    return sorted(ids - common)


def scaled(data, ids, hp, attack):
    changes = []
    for e in ids:
        rec = data.enemies[e]
        changes += [('enemies', e, 'hp', int(round(rec['hp'] * hp))),
                    ('enemies', e, 'atk', int(round(rec['atk'] * attack))),
                    ('enemies', e, 'int', int(round(rec['int'] * attack)))]
    return data.with_changes(changes)


def inside(vanilla, fig, windows):
    for key in ('won', 'lowest_hp'):
        if abs(fig[key] - vanilla[key]) > windows[key]:
            return False
    if vanilla['time'] and fig['time'] and abs(fig['time'] - vanilla['time']) > windows['time'] * vanilla['time']:
        return False
    return True


def run(part='1/1'):
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    windows = {key: float(setup.settings[f'check_{key}_window']) for key in ('won', 'time', 'lowest_hp')}
    hps = [float(x) for x in str(setup.settings['boss_fit_hp']).split(';')]
    attacks = [float(x) for x in str(setup.settings['boss_fit_attack']).split(';')]
    runs = int(setup.settings['check_runs'])
    todo = easier(setup)
    out = []
    for row in todo[(k - 1) * len(todo) // n: k * len(todo) // n]:
        cid, vanilla = row['id'], row['vanilla']
        ids = boss_enemies(data, setup, cid)
        found = None
        for attack in attacks:
            for hp in hps:
                _, fig = measures.play_checkpoint(scaled(variant, ids, hp, attack), setup, cid, runs)
                if inside(vanilla, fig, windows):
                    found = {'hp': hp, 'attack': attack, 'figures': fig}
                    break
            if found:
                break
        out.append({'id': cid, 'enemies': ids, 'names': [data.enemies[e]['name'] for e in ids],
                    'vanilla': vanilla, 'variant': row['variant'], 'fit': found})
        print(cid, found and (found['hp'], found['attack']), flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f'part_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f)


def scaled_changes(data, ids, hp, attack):
    """scaled(), as the stats of the enemy records a job of the C# engine changes."""
    return {e: {'hp': int(round(data.enemies[e]['hp'] * hp)), 'atk': int(round(data.enemies[e]['atk'] * attack)),
                'int': int(round(data.enemies[e]['int'] * attack))} for e in ids}


def run_engine():
    """run(), played by the C# engine in one call: every pair of the grid for every checkpoint, and the first one inside the windows."""
    import engine_client as engine
    started = time.time()
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    side = engine.side_of(variant)
    windows = {key: float(setup.settings[f'check_{key}_window']) for key in ('won', 'time', 'lowest_hp')}
    hps = [float(x) for x in str(setup.settings['boss_fit_hp']).split(';')]
    attacks = [float(x) for x in str(setup.settings['boss_fit_attack']).split(';')]
    runs = int(setup.settings['check_runs'])
    todo = easier(setup)
    ids = {row['id']: boss_enemies(data, setup, row['id']) for row in todo}
    grid = [(row, attack, hp) for row in todo for attack in attacks for hp in hps]
    played = engine.play_checkpoints([(side, row['id'], runs, scaled_changes(variant, ids[row['id']], hp, attack), None)
                                      for row, attack, hp in grid])
    figures = {(row['id'], attack, hp): fig for (row, attack, hp), (_, fig) in zip(grid, played)}
    out = []
    for row in todo:
        cid, vanilla = row['id'], row['vanilla']
        found = None
        for attack in attacks:
            for hp in hps:
                fig = figures[(cid, attack, hp)]
                if inside(vanilla, fig, windows):
                    found = {'hp': hp, 'attack': attack, 'figures': fig}
                    break
            if found:
                break
        out.append({'id': cid, 'enemies': ids[cid], 'names': [data.enemies[e]['name'] for e in ids[cid]],
                    'vanilla': vanilla, 'variant': row['variant'], 'fit': found})
        print(cid, found and (found['hp'], found['attack']), flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in os.listdir(OUT_DIR):
        if name.startswith('part_'):
            os.remove(os.path.join(OUT_DIR, name))
    with open(os.path.join(OUT_DIR, 'part_1.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f)
    print(f'{len(out)} checkpoints in {time.time() - started:.0f} s')


def run_all():
    setup = setup_mod.load()
    n = int(setup.settings.get('parallel_workers', 1))
    started = time.time()
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'run', f'{k}/{n}'], stdout=subprocess.DEVNULL)
             for k in range(1, n + 1)]
    for p in procs:
        p.wait()
    print(f'{n} parts in {time.time() - started:.0f} s')


# --- gentle: a little harder, with the other parties inside their share --------------------------------------------
FIGURES = ('won', 'time', 'lowest_hp', 'pressure')
EASIER = {'won': 1, 'time': -1, 'lowest_hp': 1, 'pressure': -1}     # the sign of a change that makes a fight easier
RELATIVE = ('time', 'pressure')                                      # windows that are shares of the vanilla figure


def gentle_pairs(setup):
    return [(1.0, 1.0)] + [tuple(float(x) for x in pair.split('/'))
                           for pair in str(setup.settings['boss_fit_gentle']).split(';')]


def gentle_todo(setup):
    skip = {c.strip() for c in str(setup.settings.get('boss_fit_skip', '')).split(';') if c.strip()}
    rows = []
    for name in sorted(os.listdir(CURVE_DIR)):
        with open(os.path.join(CURVE_DIR, name), encoding='utf-8') as f:
            rows += json.load(f)
    return [r for r in rows if r['out'] and r['id'] not in skip]


def gaps(setup, vanilla, fig):
    """{figure: gap to vanilla in window widths, signed: above 0 is the easier side} for the figures both have."""
    out = {}
    for key in FIGURES:
        a, b = vanilla.get(key), fig.get(key)
        if a is None or b is None:
            continue
        width = float(setup.settings[f'check_{key}_window']) * (a if key in RELATIVE else 1.0)
        out[key] = EASIER[key] * (b - a) / width if width else 0.0
    return out


def gentle_run(part='1/1', only=None):
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    runs, party_runs = int(setup.settings['check_runs']), int(setup.settings['boss_fit_party_runs'])
    wanted = {c.strip() for c in only.split(';')} if only else None
    tasks = [(row, pair) for row in gentle_todo(setup) for pair in gentle_pairs(setup)
             if wanted is None or row['id'] in wanted]
    out = []
    for row, (hp, attack) in tasks[k - 1::n]:
        cid = row['id']
        ids = boss_enemies(data, setup, cid)
        source = variant if (hp, attack) == (1.0, 1.0) else scaled(variant, ids, hp, attack)
        _, fig = measures.play_checkpoint(source, setup, cid, runs)
        parties = {}
        for name, (_, roles) in setup.battery.items():
            results = scenario.play_party(source, setup, cid, roles, party_runs)
            parties[name] = sum(1 for r in results if r['won']) / len(results)
        out.append({'id': cid, 'hp': hp, 'attack': attack, 'enemies': ids, 'figures': fig, 'parties': parties})
        print(cid, hp, attack, flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    # a part of one checkpoint played again is read after the parts of a whole run and takes their place
    with open(os.path.join(OUT_DIR, f"gentle_{'update_' if only else ''}{k}.json"), 'w', encoding='utf-8') as f:
        json.dump(out, f)


def gentle_figures(data, setup, variant, tasks):
    """For each task (row of the curve, pair of factors): the figures of the reference party and the share of wins of each party of the
    battery, played by the C# engine. Returns [(figures, {party: share})]."""
    import engine_client as engine
    side = engine.side_of(variant)
    runs, party_runs = int(setup.settings['check_runs']), int(setup.settings['boss_fit_party_runs'])
    changes = [None if (hp, attack) == (1.0, 1.0) else scaled_changes(variant, boss_enemies(data, setup, row['id']), hp, attack)
               for row, (hp, attack) in tasks]
    checkpoints = engine.play_checkpoints([(side, row['id'], runs, change, None) for (row, _), change in zip(tasks, changes)])
    jobs = [engine.make_job(side, row['id'], roles=list(roles), runs=party_runs, enemy_changes=change,
                            name=f'{row["id"]}|{hp}|{attack}|{name}')
            for (row, (hp, attack)), change in zip(tasks, changes) for name, (_, roles) in setup.battery.items()]
    done = iter(engine.run_jobs(jobs))
    out = []
    for _, fig in checkpoints:
        parties = {}
        for name in setup.battery:
            results = next(done)['runs']
            parties[name] = sum(1 for r in results if r['won']) / len(results)
        out.append((fig, parties))
    return out


def gentle_engine(only=None):
    """gentle_all(), played by the C# engine in one call; the parts are one file."""
    started = time.time()
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    wanted = {c.strip() for c in only.split(';')} if only else None
    tasks = [(row, pair) for row in gentle_todo(setup) for pair in gentle_pairs(setup) if wanted is None or row['id'] in wanted]
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in os.listdir(OUT_DIR):
        if name.startswith('gentle_update_') or (name.startswith('gentle_') and not only):
            os.remove(os.path.join(OUT_DIR, name))
    out = []
    for (row, (hp, attack)), (fig, parties) in zip(tasks, gentle_figures(data, setup, variant, tasks)):
        out.append({'id': row['id'], 'hp': hp, 'attack': attack, 'enemies': boss_enemies(data, setup, row['id']), 'figures': fig,
                    'parties': parties})
        print(row['id'], hp, attack, flush=True)
    with open(os.path.join(OUT_DIR, f"gentle_{'update_' if only else ''}1.json"), 'w', encoding='utf-8') as f:
        json.dump(out, f)
    print(f'{len(out)} cells in {time.time() - started:.0f} s')


def gentle_all(processes=None, only=None):
    setup = setup_mod.load()
    n = int(processes or setup.settings.get('parallel_workers', 1))
    for name in os.listdir(OUT_DIR) if os.path.isdir(OUT_DIR) else []:
        if name.startswith('gentle_update_') or (name.startswith('gentle_') and not only):
            os.remove(os.path.join(OUT_DIR, name))
    started = time.time()
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'gentle-run', f'{k}/{n}'] + ([only] if only else []),
                              stdout=subprocess.DEVNULL) for k in range(1, n + 1)]
    for p in procs:
        p.wait()
    print(f'{n} parts in {time.time() - started:.0f} s')


def gentle_choice(setup=None, data=None):
    """[{id, names, enemies, floor, vanilla, tried, kept: the pair kept or None, why}] from the parts."""
    setup = setup or setup_mod.load()
    data = data or game_data()
    rows = []
    for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
        if name.startswith('gentle_'):
            with open(os.path.join(OUT_DIR, name), encoding='utf-8') as f:
                rows += json.load(f)
    order = {pair: i for i, pair in enumerate(gentle_pairs(setup))}
    archetypes = {}
    for name, (archetype, _) in setup.battery.items():
        archetypes.setdefault(archetype, []).append(name)
    # every checkpoint the parts hold, not those the curve marks today: once the rows of a kept pair are in the
    # workbook the curve no longer marks that boss, and its line here is still the fit that decided them. The vanilla
    # figures of the curve do not depend on the variant
    curve = {}
    for name in sorted(os.listdir(CURVE_DIR)):
        with open(os.path.join(CURVE_DIR, name), encoding='utf-8') as f:
            curve.update({r['id']: r for r in json.load(f)})
    found = []
    for cid, row in curve.items():
        latest = {(r['hp'], r['attack']): r for r in rows if r['id'] == cid}       # a part read later wins
        tried = sorted(latest.values(), key=lambda r: order[(r['hp'], r['attack'])])
        if not tried:
            continue
        floor = float(setup.settings[f"guide_{setup.guide_difficulty.get(cid, 'normal')}_min_won"])
        for r in tried:
            r['gaps'] = gaps(setup, row['vanilla'], r['figures'])
            r['archetypes'] = {a: max(r['parties'][n] for n in names) for a, names in archetypes.items()}
            r['below'] = sorted(a for a, share in r['archetypes'].items() if share < floor)
            r['harder'] = sorted(key for key, gap in r['gaps'].items() if gap < -1.0)
            r['distance'] = sum(abs(gap) for gap in r['gaps'].values())
        base = tried[0]
        if base['below']:
            kept, why = None, 'left alone, below the floor before any change: ' + ', '.join(base['below'])
        else:
            allowed = [r for r in tried[1:] if not r['below'] and not r['harder']]
            best = min([base] + allowed, key=lambda r: (round(r['distance'], 3), order[(r['hp'], r['attack'])]))
            if best is base:
                kept = None
                why = 'left alone: no allowed pair is nearer to vanilla' if allowed else \
                    'left alone: every pair takes an archetype below the floor or passes vanilla'
            else:
                kept, why = best, 'kept'
        found.append({'id': cid, 'enemies': tried[0]['enemies'],
                      'names': [data.enemies[e]['name'] for e in tried[0]['enemies']],
                      'floor': floor, 'vanilla': row['vanilla'], 'tried': tried, 'kept': kept, 'why': why})
    return found


def _share(x):
    return f'{x:.0%}'


def _figures(f):
    if not f.get('time'):
        return _share(f['won'])
    return f"{_share(f['won'])} / {f['time']:.1f} / {_share(f['lowest_hp'])} / {f['pressure']:.2f}"


def gentle_report():
    setup = setup_mod.load()
    found = gentle_choice(setup)
    lines = ['# Bosses made a little harder, with the other parties inside their share (generated)', '',
             'Generated by `tools/boss_fit.py gentle`. Do not edit. The rule is in the header of the tool; the pairs it '
             f"may try are Settings `boss_fit_gentle` ({setup.settings['boss_fit_gentle']}: factor on HP / factor on ATK "
             'and INT). Reference party: wins / length / lowest HP / pressure. Archetypes: the win share of the best '
             'party of each (sheet BatteryParties). Floor: the least win share the class of the boss allows.', '',
             f"**{sum(1 for r in found if r['kept'])} of {len(found)} bosses changed.**", '',
             '| Checkpoint | Boss | Floor | Vanilla | Variant, no change | Kept | Variant with it | Archetypes with it |',
             '|---|---|---|---|---|---|---|---|']
    for r in found:
        base, kept = r['tried'][0], r['kept']
        last = kept or base
        arch = ', '.join(f'{a} {_share(v)}' for a, v in last['archetypes'].items())
        what = f"HP x{kept['hp']:.2f}, ATK and INT x{kept['attack']:.2f}" if kept else r['why']
        lines.append(f"| {r['id']} | {', '.join(r['names'])} | {_share(r['floor'])} | {_figures(r['vanilla'])} | "
                     f"{_figures(base['figures'])} | {what} | {_figures(kept['figures']) if kept else ''} | {arch} |")
    lines += ['', '## Every pair tried', '',
              '| Checkpoint | HP | ATK, INT | Reference party | Gap to vanilla (window widths) | Below the floor | '
              'Past vanilla on |', '|---|---|---|---|---|---|---|']
    for r in found:
        for t in r['tried']:
            lines.append(f"| {r['id']} | x{t['hp']:.2f} | x{t['attack']:.2f} | {_figures(t['figures'])} | "
                         f"{t['distance']:.1f} | {', '.join(t['below']) or '-'} | {', '.join(t['harder']) or '-'} |")
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(lines[4])


def report():
    rows = []
    for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
        if not name.startswith('part_'):
            continue
        with open(os.path.join(OUT_DIR, name), encoding='utf-8') as f:
            rows += json.load(f)
    rows.sort(key=lambda r: (r['id'][0], float(''.join(ch for ch in r['id'][1:] if ch.isdigit()) or 0)))
    lines, fitted = [], 0
    for r in rows:
        v, b, f = r['vanilla'], r['variant'], r['fit']
        fitted += f is not None
        tail = (f"x{f['hp']:.2f} HP, x{f['attack']:.2f} ATK and INT | {f['figures']['won']:.0%} / {f['figures']['time']:.1f} / "
                f"{f['figures']['lowest_hp']:.0%}") if f else 'no pair of the grid | -'
        lines.append(f"| {r['id']} | {', '.join(r['names']) or '(shared with common fights)'} | {v['won']:.0%} / {v['time']:.1f} / "
                     f"{v['lowest_hp']:.0%} | {b['won']:.0%} / {b['time']:.1f} / {b['lowest_hp']:.0%} | {tail} |")
    text = ['# Bosses brought back to the difficulty of vanilla (generated)', '',
            'Generated by `tools/boss_fit.py`. Do not edit. Cells: wins / length of the won fights / lowest party HP.', '',
            f'**{fitted} of {len(rows)} easier checkpoints fitted back into the windows of vanilla.**', '',
            '| Checkpoint | Enemies scaled | Vanilla | Variant | Factor | After |', '|---|---|---|---|---|---|'] + lines
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print(text[4])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'run': run, 'all': run_all, 'report': report, 'gentle': gentle_all, 'gentle-run': gentle_run,
     'gentle-report': gentle_report, 'engine': run_engine, 'gentle-engine': gentle_engine}[sys.argv[1]](*sys.argv[2:])

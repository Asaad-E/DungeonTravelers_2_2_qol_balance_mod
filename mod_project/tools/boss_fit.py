"""
Bring each boss fight of the Balance variant back into the difficulty window of vanilla (Regression R08, R10).
Generated: docs/generated/BOSS_FIT.md.

    python mod_project/tools/boss_fit.py all        every checkpoint docs/generated/DIFFICULTY_CURVE data marks easier
    python mod_project/tools/boss_fit.py report

For a checkpoint whose fights the variant made easier (tools/difficulty_curve.py), the enemies of its boss fights that
appear in no random formation (so that common fights are not touched) get a factor on HP and a factor on ATK and INT.
The search walks the grid of Settings boss_fit_hp and boss_fit_attack (smallest change first, HP before attack) and
keeps the first pair whose fights, played by the reference party at the reference level, land inside the windows of
vanilla (Settings check_*_window) for wins, length and lowest HP. Lever L01 (enemy stats): benign.

    python mod_project/tools/boss_fit.py gentle [processes]     the same with a condition on the other parties
    python mod_project/tools/boss_fit.py gentle-report

gentle (the user, 2026-10-11: "a little harder to make up for it, as long as the five parties stay inside their share"):
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


def gentle_run(part='1/1'):
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    runs, party_runs = int(setup.settings['check_runs']), int(setup.settings['boss_fit_party_runs'])
    tasks = [(row, pair) for row in gentle_todo(setup) for pair in gentle_pairs(setup)]
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
    with open(os.path.join(OUT_DIR, f'gentle_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f)


def gentle_all(processes=None):
    setup = setup_mod.load()
    n = int(processes or setup.settings.get('parallel_workers', 1))
    for name in os.listdir(OUT_DIR) if os.path.isdir(OUT_DIR) else []:
        if name.startswith('gentle_'):
            os.remove(os.path.join(OUT_DIR, name))
    started = time.time()
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'gentle-run', f'{k}/{n}'],
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
    found = []
    for row in gentle_todo(setup):
        cid = row['id']
        tried = sorted((r for r in rows if r['id'] == cid), key=lambda r: order[(r['hp'], r['attack'])])
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
     'gentle-report': gentle_report}[sys.argv[1]](*sys.argv[2:])

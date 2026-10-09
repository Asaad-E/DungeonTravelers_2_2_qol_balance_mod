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


def report():
    rows = []
    for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
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
    {'run': run, 'all': run_all, 'report': report}[sys.argv[1]](*sys.argv[2:])

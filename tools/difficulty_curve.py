"""
The difficulty of the Balance variant against vanilla, boss by boss (Regression R08 and R10). Generated:
docs/generated/DIFFICULTY_CURVE.md.

    python tools/difficulty_curve.py all       every checkpoint, parallel_workers processes at once
    python tools/difficulty_curve.py report

The checkpoints: every story checkpoint of the sheet Checkpoints and the postgame ones of the late stage of the sheet
ClassStages (the rest of the postgame is a known limit). For each, sim/measures.py check_change on the whole variant:
the reference party at the reference level plays the boss fights on vanilla and on the variant (check_runs runs). The
four figures are wins, the length of the won fights, the lowest share of party HP and the pressure (enemy damage per
action over party max HP); a figure that leaves its window (Settings check_<figure>_window) is reported with its
direction. Easier on the variant (more wins, shorter, higher lowest HP, less pressure) is what R10 forbids.
"""
import json
import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'difficulty_curve')
REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'DIFFICULTY_CURVE.md')

from sim import measures                                 # noqa: E402
from sim import setup as setup_mod                       # noqa: E402
from sim.data import game_data                           # noqa: E402
from sim.variant import balance_data                     # noqa: E402
import class_stages                                      # noqa: E402

EASIER = {'won': 1, 'time': -1, 'lowest_hp': 1, 'pressure': -1}     # the sign of a change that makes a fight easier


def checkpoints(setup):
    story = [c['ID'] for c in setup.checkpoints if str(c['ID']).startswith('C')]
    late = next((s for s in class_stages.stages(setup) if s['Stage'] == 'late'), None)
    return story + ([c.strip() for c in str(late['Checkpoints']).split(';')] if late else [])


def run(part='1/1'):
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    every = checkpoints(setup)
    mine = every[(k - 1) * len(every) // n: k * len(every) // n]
    rows = []
    for cid in mine:
        _, before, after, out = measures.check_change(data, setup, [], [cid], changed=variant)[0]
        rows.append({'id': cid, 'vanilla': before, 'variant': after, 'out': out})
        print(cid, out, flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f'part_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f)


def run_all():
    setup = setup_mod.load()
    n = int(setup.settings.get('parallel_workers', 1))
    started = time.time()
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'run', f'{k}/{n}'], stdout=subprocess.DEVNULL)
             for k in range(1, n + 1)]
    for p in procs:
        p.wait()
    print(f'{n} parts in {time.time() - started:.0f} s')


def run_engine(threads=None):
    """The same pass as run_all, played by the C# engine (engine_cs/) in one call; writes the one part file."""
    import engine_client
    setup = setup_mod.load()
    started = time.time()
    rows = [{'id': cid, 'vanilla': before, 'variant': after, 'out': out}
            for cid, before, after, out in engine_client.check_change(*checkpoints(setup), threads=threads)]
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in os.listdir(OUT_DIR):
        os.remove(os.path.join(OUT_DIR, name))
    with open(os.path.join(OUT_DIR, 'part_1.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f)
    print(f'{len(rows)} checkpoints in {time.time() - started:.0f} s')


def fmt(v, key):
    if v is None:
        return '-'
    return f'{v:.0%}' if key in ('won', 'lowest_hp') else f'{v:.2f}' if key == 'pressure' else f'{v:.1f}'


def report():
    setup = setup_mod.load()
    rows = []
    for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
        with open(os.path.join(OUT_DIR, name), encoding='utf-8') as f:
            rows += json.load(f)
    order = checkpoints(setup)
    rows.sort(key=lambda r: order.index(r['id']))
    easier = harder = 0
    lines = []
    for r in rows:
        signs = []
        for key in r['out']:
            a, b = r['vanilla'].get(key), r['variant'].get(key)
            if a is None or b is None:
                signs.append(f'{key} lost' if b is None else f'{key} new')
                continue
            signs.append(f"{key} {'easier' if (b - a) * EASIER[key] > 0 else 'harder'}")
        easy = any(s.endswith('easier') for s in signs)
        hard = any(s.endswith('harder') for s in signs)
        easier += easy
        harder += hard and not easy
        cells = ' | '.join(f"{fmt(r['vanilla'].get(k), k)} > {fmt(r['variant'].get(k), k)}" for k in EASIER)
        lines.append(f"| {r['id']} | {r['vanilla'].get('level')} | {cells} | {', '.join(signs) or 'within'} |")
    text = ['# Difficulty of the variant against vanilla (generated)', '',
            'Generated by `tools/difficulty_curve.py`. Do not edit. The reference party at the reference level of each '
            'checkpoint, vanilla > Balance variant. Windows: Settings check_*_window.', '',
            f'**{len(rows) - easier - harder} of {len(rows)} checkpoints within the windows of vanilla; {easier} easier, '
            f'{harder} harder.**', '',
            '| Checkpoint | Level | Wins | Length | Lowest HP | Pressure | Out of the window |',
            '|---|---|---|---|---|---|---|'] + lines
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print(text[4])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'run': run, 'all': run_all, 'engine': run_engine, 'report': report}[sys.argv[1]](*sys.argv[2:])

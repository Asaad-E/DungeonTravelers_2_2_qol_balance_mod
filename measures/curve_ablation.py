"""What moved the checkpoints that left the windows between the pass of commit dc1a09b (35 of 44 within) and the pass of
2026-10-12 evening (30 of 44): each change made since is taken back alone, the rows of its records as the workbook of
that commit held them (balance_changes_at_dc1a09b.xlsx beside this file), and the checkpoints are measured again with
the measure of tools/difficulty_curve.py. 'now' takes nothing back, 'then' takes everything back. The reading of the
interruption rate (the program adds Concentrate where the simulator multiplied) is one of the changes: it moved vanilla
too. Nothing is written but the result.

    python curve_ablation.py run CASE       writes curve_ablation_CASE.json beside this file
    python curve_ablation.py all            every case, one process each
    python curve_ablation.py report         CURVE_ABLATION.md beside this file
    python curve_ablation.py engine CASE    the same as `run`, played by the C# engine (engine_cs/); `engine all` plays every case
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, setup as setup_mod, variant as variant_mod      # noqa: E402
from sim.data import game_data                                             # noqa: E402

THEN = os.path.join(HERE, 'balance_changes_at_dc1a09b.xlsx')
PLACES = ('C12', 'C14', 'C15', 'C17', 'C20', 'C28', 'C39', 'P24')
# case -> the records taken back to what they were (a start of the column Record), and the two figures of the program
GROUPS = {'samba': ('Technique 70 Alluring Samba',), 'third eye': ('Unique 365',), 'lize': ('Unique 370',),
          'arcane shield': ('Unique 379',), 'alter fate': ('Unique 369',), 'tranquil song': ('Unique 377',)}
CASES = ('now', 'then') + tuple(GROUPS) + ('interruption',)
EASIER = {'won': 1, 'time': -1, 'lowest_hp': 1, 'pressure': -1}


def build(case):
    """(vanilla data, variant data) of a case."""
    data = game_data()
    now, then = variant_mod.rows(), variant_mod.rows(THEN)
    back = sum(GROUPS.values(), ()) if case == 'then' else GROUPS.get(case, ())
    mine = lambda r: str(r['Record']).startswith(back) if back else False      # noqa: E731
    rows = [r for r in now if not mine(r)] + [r for r in then if mine(r)]
    if case.startswith('evasion '):      # 'evasion 0.04,0.06,...': the ten values of the unique skill of Lizerietta tried
        tried = [float(x) for x in case.split()[1].split(',')]
        rows = [dict(r, New=tried[int(r['Level']) - 1]) if str(r['Record']).startswith('Unique 370') and r['Field'] == 'value'
                else r for r in rows]
    out = variant_mod.apply(data, rows)
    old_roll = case in ('then', 'arcane shield')
    old_rate = case in ('then', 'interruption')
    out.arcane_chance = None if old_roll else variant_mod.arcane_chance()
    # the rate as the simulator played it at that commit: the product, on both sides
    out.interrupt_product = True if old_rate else variant_mod.interrupt_product()
    data.interrupt_product = old_rate
    return data, out


def run(case, runs=None):
    """runs: battles a checkpoint (the 40 of the setting check_runs when left out); the result is then kept apart."""
    data, changed = build(case)
    setup = setup_mod.load()
    rows = []
    for cid in PLACES:
        _, before, after, out = measures.check_change(data, setup, [], [cid], runs=int(runs) if runs else None, changed=changed)[0]
        rows.append({'id': cid, 'vanilla': before, 'variant': after, 'out': out})
        print(case, cid, out, flush=True)
    with open(os.path.join(HERE, f"curve_ablation_{case.replace(' ', '_').replace(',', '_')}{'_' + str(runs) if runs else ''}.json"), 'w', encoding='utf-8') as f:
        json.dump(rows, f)


def run_engine(case, runs=None):
    """run(), played by the C# engine: the data of the case are sent to it, the checkpoints play in one call."""
    if case == 'all':
        for each in CASES:
            run_engine(each, runs)
        return
    import engine_client as engine
    data, changed = build(case)
    setup = setup_mod.load()
    rows = []
    for cid, before, after, out in engine.check_change_sim(data, changed, setup, list(PLACES), runs=int(runs) if runs else None):
        rows.append({'id': cid, 'vanilla': before, 'variant': after, 'out': out})
        print(case, cid, out, flush=True)
    with open(os.path.join(HERE, f"curve_ablation_{case.replace(' ', '_').replace(',', '_')}{'_' + str(runs) if runs else ''}.json"), 'w', encoding='utf-8') as f:
        json.dump(rows, f)


def run_all():
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'run', case], stdout=subprocess.DEVNULL)
             for case in CASES]
    for p in procs:
        p.wait()


def cell(r):
    signs = [f"{k} {'easier' if (r['variant'][k] - r['vanilla'][k]) * EASIER[k] > 0 else 'harder'}" for k in r['out']
             if r['vanilla'].get(k) is not None and r['variant'].get(k) is not None]
    v = r['variant']
    return f"{v['won']:.0%} / {v['time']:.1f} / {v['lowest_hp']:.0%} / {v['pressure']:.2f}" + (f" ({', '.join(signs)})" if signs else '')


def report():
    found = {}
    for case in CASES:
        path = os.path.join(HERE, f"curve_ablation_{case.replace(' ', '_')}.json")
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                found[case] = {r['id']: r for r in json.load(f)}
    lines = ['# What moved the checkpoints of the curve (generated by measures/curve_ablation.py)', '',
             'Cells: wins / length / lowest HP / pressure of the variant, and what is out of the window of vanilla. '
             '"now": the variant as it is; "then": every change since commit dc1a09b taken back; the others: that change '
             'alone taken back.', '',
             '| Case | ' + ' | '.join(PLACES) + ' |', '|---|' + '---|' * len(PLACES)]
    for case, rows in found.items():
        lines.append(f'| {case} | ' + ' | '.join(cell(rows[c]) for c in PLACES) + ' |')
    with open(os.path.join(HERE, 'CURVE_ABLATION.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines[4:]))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'run': run, 'all': run_all, 'engine': run_engine, 'report': report}[sys.argv[1]](*sys.argv[2:])

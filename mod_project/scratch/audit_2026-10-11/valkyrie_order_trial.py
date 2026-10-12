"""A trial of the order of the Valkyrie's rules (sheet Policies): Parry and Cover before Spell Guard and War Cry in a
boss fight, as "prebuffs Parry and Cover in hard fights" reads. Vanilla data, the reference party; nothing written.

    python valkyrie_order_trial.py P41 P45 ...
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402

data, setup = game_data(), setup_mod.load()
usual = setup.policies
moved = [dict(r, Order=3.5 if r['Action'] == 'status:171' else 3.6) if r['Role'] == 'valkyrie' and
         r['Action'] in ('status:171', 'status:180') else r for r in usual]
for cid in sys.argv[1:]:
    cells = []
    for rules in (usual, moved):
        setup.policies = rules
        _, res = measures.play_checkpoint(data, setup, cid, 20)
        cells.append(f"{res['won']:.0%} / {res.get('time') or 0:.1f}")
    print(cid, 'usual', cells[0], '| Cover and Parry first', cells[1], flush=True)

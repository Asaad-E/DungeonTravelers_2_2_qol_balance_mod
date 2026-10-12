"""The Meta party at a boss with each support in the place of the Diva (variant): how the fights end, what the boss
kills with and what each member does. The reading of boss_diagnosis.py beside this file.

    python support_compare.py C40 diva etoile mistress maid [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import boss_diagnosis as B                                 # noqa: E402

cid = sys.argv[1]
runs = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 20
data, setup = B.game_data(), B.setup_mod.load()
variant = B.balance_data(data)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
for support in [a for a in sys.argv[2:] if not a.isdigit()]:
    roles = [support if r == 'diva' else r for r in setup.battery['Meta'][1]]
    print('===', cid, support)
    print('  ' + ', '.join(f"{u.name} {getattr(u, 'role', u.kind)} {u.max_hp}HP {u.max_tp}TP"
                           for u in B.scenario.party_of_roles(variant, setup, cid, roles)))
    B.play(variant, setup, cid, roles, runs)

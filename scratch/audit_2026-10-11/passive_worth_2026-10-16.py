"""What Avenger (effect 249, the tank) and Barrage (effect 251, the Kunoichi) are worth late in the game, on the
variant: the same party with the passive and with it at value 0 (passives_add), at the late bosses. For the rows F38 and
F63 of the register. Nothing is written.

    python scratch/audit_2026-10-11/passive_worth_2026-10-16.py [runs]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'tools')]
import engine_client as engine                               # noqa: E402

CIDS = ['C30', 'C34', 'C36', 'C38', 'C40']
CASES = {  # name: (party roles, the tested role, the passive)
    'Avenger': (None, 'tank', 249),
    'Barrage': (['tank', 'attacker', 'dark lord', 'kunoichi', 'diva'], 'kunoichi', 251),
}
runs = int(sys.argv[1]) if len(sys.argv) > 1 else 300
jobs, keys = [], []
for name, (roles, role, effect) in CASES.items():
    for cid in CIDS:
        for off in (False, True):
            tested = {'role': role}
            if off:
                tested['passives_add'] = {str(effect): 0}
            recipe = {'tested': [tested], 'place': 'replace_role'}
            jobs.append(engine.make_job('variant', cid, roles=roles, runs=runs, recipe=recipe, name=f'{name}|{cid}|{off}'))
            keys.append((name, cid, off))
out = {k: s for k, (_, s) in zip(keys, engine.play_jobs(jobs))}
for name in CASES:
    print(f'\n{name}: without > with (wins, length of the won fights, lowest HP)')
    for cid in CIDS:
        a, b = out[(name, cid, False)], out[(name, cid, True)]
        print(f"  {cid}: wins {b['won']:.0%} > {a['won']:.0%}, length {b['time'] or 0:.1f} > {a['time'] or 0:.1f}, "
              f"lowest HP {b['lowest_hp']:.0%} > {a['lowest_hp']:.0%}")

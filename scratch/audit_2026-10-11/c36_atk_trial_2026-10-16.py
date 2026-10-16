"""C36 (Demon God Fried, enemy 1015) with more ATK instead of more HP: the reference party and the seven parties of
measures/win_rates.py on the variant, the boss's ATK (and optionally HP) scaled, against vanilla as it is. Nothing is written.

    python scratch/audit_2026-10-11/c36_atk_trial_2026-10-16.py [runs]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'measures')]
import engine_client as engine                               # noqa: E402
import win_rates                                              # noqa: E402

CID, BOSS, ATK, HP = 'C36', 1015, 265, 18000
CASES = [('vanilla', 1.0, 1.0), ('variant', 1.0, 1.0), ('variant', 1.1, 1.0), ('variant', 1.2, 1.0), ('variant', 1.3, 1.0),
         ('variant', 1.4, 1.0), ('variant', 1.2, 1.1)]
runs = int(sys.argv[1]) if len(sys.argv) > 1 else 200
parties = {'reference': None, **{name: [r.strip() for r in roles.split(';')] for name, (roles, _, _) in win_rates.PARTIES.items()}}
jobs, keys = [], []
for side, atk, hp in CASES:
    change = None if (atk, hp) == (1.0, 1.0) else {BOSS: {'atk': int(ATK * atk), 'hp': int(HP * hp)}}
    for name, roles in parties.items():
        jobs.append(engine.make_job(side, CID, roles=roles, runs=runs, enemy_changes=change, name=f'{side}|{atk}|{hp}|{name}'))
        keys.append((side, atk, hp, name))
played = engine.play_jobs(jobs)
rows = {}
for key, (results, summary) in zip(keys, played):
    rows[key] = summary
names = list(parties)
print('| Case | ' + ' | '.join(names) + ' |')
print('|---|' + '---|' * len(names))
for side, atk, hp in CASES:
    cells = []
    for name in names:
        s = rows[(side, atk, hp, name)]
        t = s.get('time')
        cells.append(f"{s['won']:.0%} / {t:.1f}" if t else f"{s['won']:.0%}")
    print(f'| {side} ATK x{atk} HP x{hp} | ' + ' | '.join(cells) + ' |')

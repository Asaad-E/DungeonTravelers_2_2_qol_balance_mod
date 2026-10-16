"""Why the Juggernaut party (tank, attacker, dark lord, kunoichi, etoile) wins so little at the late bosses: what each
member does and suffers, against the same party with a Diva in place of the Etoile. Nothing is written.

    python scratch/audit_2026-10-11/juggernaut_causes_2026-10-16.py C36;C40 [runs] [side]
"""
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'tools')]
import engine_client as engine                               # noqa: E402

PARTIES = {'Juggernaut': ['tank', 'attacker', 'dark lord', 'kunoichi', 'etoile'],
           'Juggernaut-Plus': ['tank', 'attacker', 'dark lord', 'kunoichi', 'diva']}

cids = sys.argv[1].split(';')
runs = int(sys.argv[2]) if len(sys.argv) > 2 else 100
side = sys.argv[3] if len(sys.argv) > 3 else 'variant'
jobs, keys = [], []
for cid in cids:
    for name, roles in PARTIES.items():
        jobs.append(engine.make_job(side, cid, roles=roles, runs=runs, record=True, name=f'{cid}|{name}'))
        keys.append((cid, name))
for (cid, name), (results, summary) in zip(keys, engine.play_jobs(jobs)):
    won = sum(r['won'] for r in results) / len(results)
    print(f'\n== {cid} {name}: won {won:.0%}, time {summary.get("time")}, lowest HP {summary.get("lowest_hp")}')
    dmg, heal, deaths, tp, uses, items, turns_lost = Counter(), Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    enemy_dmg = Counter()
    for r in results:
        for part in r.get('parts') or [r]:
            rec = part.get('record')
            if rec is None:
                continue
            for u, v in rec.damage.items():
                (dmg if u.side == 0 else enemy_dmg)[u.role or u.name] += v
            for u, v in rec.healing.items():
                heal[u.role or u.name] += v
            for u, v in rec.deaths.items():
                deaths[u.role or u.name] += v
            for u, v in rec.tp_spent.items():
                tp[u.role or u.name] += v
            for u, v in rec.turns_lost.items():
                turns_lost[u.role or u.name] += v
            for (u, skill), v in rec.skill_uses.items():
                if u.side == 0:
                    uses[(u.role or u.name, skill)] += v
            for (u, item), v in rec.items_used.items():
                items[str(item)] += v
    n = len(results)
    for label, table in (('damage dealt', dmg), ('healing', heal), ('deaths', deaths), ('turns lost', turns_lost),
                         ('damage by enemies', enemy_dmg)):
        print(f'  {label}: ' + ', '.join(f'{k} {v / n:.0f}' for k, v in table.most_common(8)))
    print('  skills: ' + ', '.join(f'{k[0]}:{k[1]} {v / n:.1f}' for k, v in uses.most_common(14)))
    print('  items: ' + ', '.join(f'{k} {v / n:.1f}' for k, v in items.most_common(6)))

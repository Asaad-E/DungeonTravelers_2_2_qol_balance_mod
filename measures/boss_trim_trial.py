"""What a change to the enemies of one boss fight does to the share of wins of the parties of measures/win_rates.py:
the variant as it is, then each case of the command line. A case is a list of fields: `hp*1.15` multiplies the value
of the variant, `atk=game` puts back the value of the game. Nothing is written.

    python measures/boss_trim_trial.py C30 200 "hp*1.15" "atk=game,int=game" "hp*1.15,atk=game,int=game"
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import win_rates                                          # noqa: E402

_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod
        from sim.data import game_data
        from sim.variant import balance_data
        vanilla = game_data()
        _STATE.update(setup=setup_mod.load(), vanilla=vanilla, variant=balance_data(vanilla))
    return _STATE


def enemies_of(data, setup, cid):
    from sim import scenario
    cp = setup.checkpoint(cid)
    found = set()
    for n in scenario.battle_numbers(cp):
        for u in scenario.fixed_battle(data, cp['Floor'], n):
            found.add(getattr(u, 'enemy_id', None) or getattr(u, 'id', None))
    return [i for i in found if i in data.enemies]


def cell(task):
    party, cid, case, runs = task
    from sim import scenario
    state = _load()
    data, setup = state['variant'], state['setup']
    ids = enemies_of(data, setup, cid)
    kept = {i: dict(data.enemies[i]) for i in ids}
    for part in [p for p in case.split(',') if p.strip()]:
        for i in ids:
            if '*' in part:
                field, factor = part.split('*')
                data.enemies[i][field.strip()] = int(round(kept[i][field.strip()] * float(factor)))
            else:
                field = part.split('=')[0].strip()
                data.enemies[i][field] = state['vanilla'].enemies[i][field]
    try:
        roles = [r.strip() for r in win_rates.PARTIES[party][0].split(';')]
        res = scenario.play_party(data, setup, cid, roles, runs)
    finally:
        for i in ids:
            data.enemies[i].update(kept[i])
    won = [r for r in res if r['won']]
    return party, case, len(won) / len(res), sum(r['time'] for r in won) / len(won) if won else 0


def main():
    cid, runs, cases = sys.argv[1], int(sys.argv[2]), [''] + sys.argv[3:]
    tasks = [(p, cid, k, runs) for p in win_rates.PARTIES for k in cases]
    with ProcessPoolExecutor(12) as pool:
        at = {(p, k): (w, t) for p, k, w, t in pool.map(cell, tasks)}
    print(cid, '| ' + ' | '.join(k or 'variant' for k in cases))
    for p in win_rates.PARTIES:
        print(f'  {p:16s} ' + ' | '.join(f'{at[(p, k)][0]:.0%} ({at[(p, k)][1]:.0f}t)' for k in cases))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

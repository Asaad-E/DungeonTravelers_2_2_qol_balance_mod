"""What the size of the dances that lower the ATK and the INT of the enemies is worth, with the dance bonus taken away
as the program does (docs/FORMULAS.md 12.8): parties with an Etoile who keeps Fascinating Waltz and Dumbing Mazurka up,
on the variant, and on the variant with those two dances at the values of the game or halfway. Nothing is written.

    python measures/dance_trial.py C26;C30;C36;C38;C40 150
    python measures/dance_trial.py C26;C30;C36;C38;C40 150 --engine     the same, played by the C# engine (engine_cs/)
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))

PARTIES = {'Juggernaut': ['tank', 'attacker', 'dark lord', 'kunoichi', 'etoile'],
           'Physical, Diva': ['tank', 'attacker', 'dark lord', 'etoile', 'diva']}
CASES = {'game': None, 'variant': 1.0, 'variant, dances halfway': 0.5, 'variant, dances of the game': 0.0}
DANCES = {'Fascinating Waltz': 195, 'Dumbing Mazurka': 201}
ENGINE = False                               # --engine: the battles are played by the C# engine
_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod
        from sim.data import game_data
        from sim.variant import balance_data
        vanilla = game_data()
        _STATE.update(vanilla=vanilla, variant=balance_data(vanilla), setup=setup_mod.load())
    return _STATE


def skill(data, name):
    return next(s for s in data.skills.values() if s.name == name)


def cell(task):
    party, cid, case, runs = task
    from sim import scenario
    state = _load()
    share = CASES[case]
    data = state['vanilla'] if share is None else state['variant']
    kept = {}
    if share is not None and share < 1:
        for name, effect in DANCES.items():
            mine, base = skill(data, name), skill(state['vanilla'], name)
            kept[name] = mine.effects
            old = next(v for e, _, v in base.effects if e == effect)
            mine.effects = [(e, k, [o + (x - o) * share for x, o in zip(v, old)] if e == effect else v) for e, k, v in mine.effects]
    try:
        res = (__import__('engine_client').play_party_sim if ENGINE else scenario.play_party)(data, state['setup'], cid, PARTIES[party], runs)
    finally:
        for name, effects in kept.items():
            skill(data, name).effects = effects
    won = [r for r in res if r['won']]
    return party, cid, case, len(won) / len(res), sum(r['time'] for r in won) / len(won) if won else 0


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    bosses, runs = sys.argv[1].split(';'), int(sys.argv[2])
    tasks = [(p, c, k, runs) for p in PARTIES for c in bosses for k in CASES]
    with (__import__('engine_client').SerialPool() if ENGINE else ProcessPoolExecutor(12)) as pool:
        at = {(p, c, k): (w, t) for p, c, k, w, t in pool.map(cell, tasks)}
    for p in PARTIES:
        print(p, PARTIES[p])
        for k in CASES:
            print(f'  {k:30s} ' + ' | '.join(f'{c} {at[(p, c, k)][0]:.0%} ({at[(p, c, k)][1]:.0f}t)' for c in bosses))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

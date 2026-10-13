"""What the Sage needs to lift a party as a support: her in the last place of the reference party with her buffs
chanted faster (the chant speed factor of Circle Brave, Circle Protect, Sun Veil, Amplify and Accelerator) and a
little larger (the values of the first three), keeping two buffs up as the model plays her or the five. Balance
variant for everything else; nothing is written.

    python measures/sage_buffs_trial.py C30;C36;C38;C40;P24 200
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))

CHANTED = ('Circle Brave', 'Circle Protect', 'Sun Veil', 'Amplify', 'Accelerator')
SIZED = {'Circle Brave': 161, 'Circle Protect': 162, 'Sun Veil': 163}
EXTRA_RULES = ('status:163', 'status:172', 'status:168')        # Sun Veil, Amplify, Accelerator kept up as well
CASES = [(chant, size, rules) for rules in (2, 5) for size in (1.0, 1.2) for chant in (None, 2.0, 3.0)]
_STATE = {}


def cell(task):
    (chant, size, rules), cid, runs = task
    import class_stages
    from sim import setup as setup_mod
    from sim.data import game_data
    from sim.variant import balance_data
    if not _STATE:
        _STATE.update(data=balance_data(game_data()), setup=setup_mod.load())
    data, setup = _STATE['data'], _STATE['setup']
    kept, policies = {}, setup.policies
    for name in CHANTED:
        skill = next(s for s in data.skills.values() if s.name == name)
        kept[name] = (skill, skill.cast, skill.effects)
        if chant:
            skill.cast = [max(chant, c) for c in skill.cast]
        if name in SIZED and size != 1.0:
            skill.effects = [(e, k, [round(v * size, 2) for v in vals] if e == SIZED[name] else vals) for e, k, vals in skill.effects]
    if rules == 5:
        cut = next(r['Order'] for r in policies if r['Role'] == 'sage' and str(r['Action']).startswith('damage'))
        setup.policies = policies + [{'Role': 'sage', 'Order': cut - 0.5 + k / 10, 'Condition': 'always', 'Action': a, 'Source': ''}
                                     for k, a in enumerate(EXTRA_RULES)]
    try:
        res = class_stages.play(data, setup, cid, 'sage', runs)
    finally:
        setup.policies = policies
        for skill, cast, effects in kept.values():
            skill.cast, skill.effects = cast, effects
    return (chant, size, rules), cid, res


def main():
    bosses, runs = sys.argv[1].split(';'), int(sys.argv[2])
    with ProcessPoolExecutor(12) as pool:
        at = {(k, c): r for k, c, r in pool.map(cell, [(k, c, runs) for k in CASES for c in bosses])}
    print(f'the Sage in the last place of the reference party, {runs} battles: wins (length of the won fights)')
    for chant, size, rules in CASES:
        label = f"{rules} buffs kept up, chant {'as it is' if chant is None else chant}, size x{size}"
        cells = [at[((chant, size, rules), c)] for c in bosses]
        print(f'  {label:44s} ' + ' | '.join(f"{c} {r['won']:.0%} ({r['time_won'] or 0:.0f}t)" for c, r in zip(bosses, cells))
              + f" | mean {sum(r['won'] for r in cells) / len(cells):.0%}")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

"""A trial of other values for one unique skill (the user, 2026-10-12: with calm, one step at a time): the girl in
the reference party without her skill, with it as built, and with its ten values times each factor, at the five
places of unique_skills.py beside this file. For Arcane Shield a trial may also set the chance of its roll, which is
a figure of the program (lever L38). Nothing is written.

    python unique_trial.py Lilian 1.5 2 [runs]
    python unique_trial.py Siena 1.5 2 chance=25 [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import unique_skills                                      # noqa: E402
from sim import battle, setup as setup_mod                # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402


def mean(cells, key):
    return sum(c[key] for c in cells) / len(cells)


def main():
    girl = sys.argv[1]
    args = sys.argv[2:]
    chance = next((int(a.split('=')[1]) for a in args if a.startswith('chance=')), None)
    numbers = [a for a in args if not a.startswith('chance=')]
    runs = int(numbers[-1]) if numbers and float(numbers[-1]) > 10 else 100
    factors = [float(a) for a in numbers if float(a) <= 10]
    base, setup = balance_data(game_data()), setup_mod.load()
    uid = next(c for c in base.characters if c['name'] == girl)['unique_skill']
    values = base.unique[uid]['values']
    trials = [('without', None, None), ('as built', 1.0, None)] + [(f'x{f:g}', f, None) for f in factors]
    if chance is not None:
        trials += [(f'chance {chance}%', 1.0, chance)] + [(f'x{f:g}, chance {chance}%', f, chance) for f in factors]
    usual = battle.ARCANE_CHANCE
    for label, factor, roll in trials:
        data = base if factor in (None, 1.0) else base.with_changes(
            [('unique', uid, 'values', [round(v * factor, 4) for v in values])])
        battle.ARCANE_CHANCE = roll if roll is not None else usual
        cells = [unique_skills.play(data, setup, cid, crown, girl, factor is not None, runs)
                 for cid, crown in unique_skills.PLACES]
        battle.ARCANE_CHANCE = usual
        times = [c['time'] for c in cells if c['time']]
        print(f"{girl} | {label} | wins " + ' '.join(f"{c['won']:.0%}" for c in cells) +
              f" | mean {mean(cells, 'won'):.1%} | length {sum(times) / len(times):.2f} | HP left {mean(cells, 'hp_left'):.1%}",
              flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

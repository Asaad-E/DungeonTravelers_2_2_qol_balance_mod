"""Which second raise of the two protecting dances of the Etoile (the user, 2026-10-12): 1.0 (none), 1.3, 1.4 or 1.5
times the values of rows A084 - A093 and A124 - A133 before that raise. For each: the Meta party with her in the place
of the Diva, and the reference party with her in its last place, as tools/class_stages.py plays a role. The build
holds 1.5, so each factor is applied over it. Nothing is written.

    python etoile_factor.py C40 [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import class_stages                                       # noqa: E402
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

DANCES = {'Fascinating Waltz': 195, 'Dumbing Mazurka': 201}
BUILT = 1.5
FACTORS = (1.0, 1.3, 1.4, 1.5)


def with_factor(data, factor):
    changes = []
    for key, s in data.skills.items():
        if s.name in DANCES and s.classes:
            effect = DANCES[s.name]
            changes.append(('skills', key, 'effects', [(e, k, [round(v * factor / BUILT, 2) for v in vals] if e == effect
                                                        else vals) for e, k, vals in s.effects]))
    return data.with_changes(changes)


def main():
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    setup = setup_mod.load()
    variant = balance_data(game_data())
    cp = setup.checkpoint(cid)
    roles = ['etoile' if r == 'diva' else r for r in setup.battery['Meta'][1]]
    alone, beside = [], []
    for factor in FACTORS:
        source = with_factor(variant, factor)

        def party():
            return scenario.party_of_roles(source, setup, cid, roles)

        def enemies():
            return [scenario.fixed_battle(source, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

        alone.append(f"x{factor} {measures.summary(scenario.play(source, setup, party, enemies, runs=runs))['won']:.0%}")
        beside.append(f"x{factor} {class_stages.play(source, setup, cid, 'etoile', runs)['won']:.0%}")
    print(f'{cid} | the one support of Meta | ' + ' | '.join(alone), flush=True)
    print(f'{cid} | last place of the reference party | ' + ' | '.join(beside), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

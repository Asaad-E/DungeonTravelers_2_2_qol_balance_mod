"""A trial for the Etoile as the one support of a party (decided 2026-10-12): the values of her two protecting
dances, Fascinating Waltz (the ATK of the enemies) and Dumbing Mazurka (their INT), times each factor, and what the
Meta party with her in the place of the Diva then wins on the variant. Nothing is written.

    python etoile_trial.py C40 [runs]
    python etoile_trial.py C40 [runs] --engine    the battles are played by the C# engine (engine_cs/)
    python etoile_trial.py C40 [runs] primevil    the same with Primevil (her dance that heals, cures and revives the
                                                  party, 50 TP) first in her skills and used when the party is low
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

DANCES = {'Fascinating Waltz': 195, 'Dumbing Mazurka': 201}
FACTORS = (1.0, 1.5)
ENGINE = False                               # --engine: the battles are played by the C# engine


def stronger(data, factor):
    changes = []
    for key, s in data.skills.items():
        if s.name in DANCES and s.classes:
            effect = DANCES[s.name]
            changes.append(('skills', key, 'effects', [(e, k, [round(v * factor, 3) for v in vals] if e == effect else vals)
                                                       for e, k, vals in s.effects]))
    return data.with_changes(changes)


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 60
    setup = setup_mod.load()
    if 'primevil' in sys.argv:
        setup.roles['etoile']['Skill priority'] = 'Primevil; ' + setup.roles['etoile']['Skill priority']
        setup.policies = setup.policies + [{'Role': 'etoile', 'Order': 1.5, 'Condition': 'party_hp_below:0.5',
                                            'Action': 'heal:0.5'}]
    variant = balance_data(game_data())
    cp = setup.checkpoint(cid)
    parties = {'Meta, Etoile for Diva': ['etoile' if r == 'diva' else r for r in setup.battery['Meta'][1]],
               'Meta, Etoile for Papillon': ['etoile' if r == 'papillon' else r for r in setup.battery['Meta'][1]]}
    for label, roles in parties.items():
        cells = []
        for factor in FACTORS:
            source = stronger(variant, factor)

            def party():
                return scenario.party_of_roles(source, setup, cid, roles)

            def enemies():
                return [scenario.fixed_battle(source, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

            res = (__import__('engine_client').summary_sim(source, setup, cid, roles, runs) if ENGINE
                   else measures.summary(scenario.play(source, setup, party, enemies, runs=runs)))
            cells.append(f"x{factor} {res['won']:.0%} / {res.get('time') or 0:.1f}")
        print(f'{cid} | {label} | ' + ' | '.join(cells), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

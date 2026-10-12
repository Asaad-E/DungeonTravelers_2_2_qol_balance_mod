"""A trial of two rules of play for the supports that stand in for the Diva (sheet Policies): the Etoile heals with
First Aid when a member is low, as the Diva's own rule does, and the Mistress cooks when a member is short of TP, as
the Etoile's own rule does. Both skills are of the Maid, their base class. The Meta party with each support, at the
bosses given, on the variant: with the rules of the sheet and with the two added. Nothing is written.

    python support_rules_trial.py C40 [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

ADDED = ({'Role': 'etoile', 'Order': 1.5, 'Condition': 'ally_hp_below:0.35', 'Action': 'heal:0.35'},
         {'Role': 'mistress', 'Order': 1.7, 'Condition': 'ally_tp_below:0.35', 'Action': 'tp:0.35'})


def main():
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    setup = setup_mod.load()
    variant = balance_data(game_data())
    cp = setup.checkpoint(cid)
    usual = setup.policies
    for support in ('diva', 'etoile', 'mistress'):
        roles = [support if r == 'diva' else r for r in setup.battery['Meta'][1]]
        cells = []
        for rules in (usual, usual + list(ADDED)):
            setup.policies = rules

            def party():
                return scenario.party_of_roles(variant, setup, cid, roles)

            def enemies():
                return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

            res = measures.summary(scenario.play(variant, setup, party, enemies, runs=runs))
            cells.append(f"{res['won']:.0%} / {res.get('time') or 0:.1f}")
        setup.policies = usual
        print(f'{cid} | {support} | {cells[0]} | {cells[1]}', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

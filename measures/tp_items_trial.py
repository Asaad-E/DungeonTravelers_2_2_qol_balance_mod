"""Is TP what stops a party without the Maid line from C30 on (row F01)? The Meta party with a Bishop in the place of
its Diva, on the variant, with more TP fruit in the bag and with the fruit eaten sooner. Nothing is written.

    python tp_items_trial.py C30 [runs]
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

FRUIT = 20                       # Fairy Apple, TP 50 to one member
# label -> (fruit in the bag, share of TP under which a member is fed, TP a fruit gives)
TRIALS = {'8 fruit of 60 TP (the build, the bag of the sheets)': (8, 0.15, 60), '16 fruit of 60 TP': (16, 0.15, 60),
          '24 fruit of 60 TP': (24, 0.15, 60), '24 fruit of 50 TP (before the raise)': (24, 0.15, 50)}


def main():
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    setup = setup_mod.load()
    base = balance_data(game_data())
    cp = setup.checkpoint(cid)
    roles = ['healer' if r == 'diva' else r for r in setup.battery['Meta'][1]]
    usual = setup.policies
    for label, (count, share, amount) in TRIALS.items():
        data = base.with_changes([('items', FRUIT, 'effects', [(1, amount)])])
        setup.policies = [dict(r, Condition=f'ally_tp_below:{share}', Action=f'tp:{share}')
                          if str(r['Action']).startswith('tp:') and str(r['Condition']) == 'ally_tp_below:0.15' else r
                          for r in usual]

        def party():
            units = scenario.party_of_roles(data, setup, cid, roles)
            bag = dict(units[0].items)
            bag[FRUIT] = count
            for u in units:
                if u.kind == 'member':
                    u.items = bag
            return units

        def enemies():
            return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

        res = measures.summary(scenario.play(data, setup, party, enemies, runs=runs))
        print(f"{cid} | {label} | {res['won']:.0%} | {res.get('time') or 0:.1f}", flush=True)
    setup.policies = usual


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

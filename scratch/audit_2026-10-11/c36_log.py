"""The log of one lost battle of a party at a checkpoint, on the variant: c36_log.py PARTY [checkpoint] [seed offset]"""
import os
import random
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import scenario, setup as setup_mod                      # noqa: E402
from sim.battle import Battle                                     # noqa: E402
from sim.data import game_data                                    # noqa: E402
from sim.policy import Policy, load_rules                         # noqa: E402
from sim.variant import balance_data                              # noqa: E402


def main():
    name = sys.argv[1]
    cid = sys.argv[2] if len(sys.argv) > 2 else 'C36'
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    setup = setup_mod.load()
    data = balance_data(game_data())
    cp = setup.checkpoint(cid)
    policy = Policy(load_rules(setup.policies), setup.settings)
    for k in range(first, first + 60):
        rng = random.Random(int(setup.settings['seed']) + k)
        party = scenario.party_of_roles(data, setup, cid, setup.battery[name][1])
        enemies = scenario.fixed_battle(data, cp['Floor'], scenario.battle_numbers(cp)[0])
        scenario.prepare(setup, party, enemies)
        battle = Battle(data, party, enemies, rng, choose_member=policy, setup=dict(setup.settings),
                        zone=getattr(enemies, 'zone', None), max_time=float(setup.settings.get('max_time', 400)))
        battle.fixed = True
        battle.log = []
        result = battle.run()
        if not result['won']:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            print('run', k, 'time', result['time'])
            print('\n'.join(battle.log))
            return


if __name__ == '__main__':
    main()

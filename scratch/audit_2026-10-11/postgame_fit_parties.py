"""The parties of the sheet BatteryParties at the postgame bosses the variant leaves easier: wins in vanilla, on the
variant, and on the variant with the HP of the enemies of the fight times 1.3. Each boss at the crown bonus of
postgame_compare.py (the preparation at which the vanilla reference party reaches its floor). Nothing is written.

    python postgame_fit_parties.py P06 [runs]
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

CROWN = {'P06': 0, 'P23': 20, 'P27': 40, 'P52': 0, 'P54': 0}
FACTOR = 1.3


def main():
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    cp = setup.checkpoint(cid)
    cp['Crown bonus'] = CROWN[cid]
    ids = {eid for number in scenario.battle_numbers(cp)
           for b in data.fixed if b['floor'] == cp['Floor'] and b['number'] == number for eid, _ in b['enemies']}
    harder = variant.with_changes([('enemies', e, 'hp', int(variant.enemies[e]['hp'] * FACTOR)) for e in ids])
    for name, (_, roles) in setup.battery.items():
        cells = []
        for source in (data, variant, harder):
            def party():
                return scenario.party_of_roles(source, setup, cid, roles)

            def enemies():
                return [scenario.fixed_battle(source, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

            cells.append(measures.summary(scenario.play(source, setup, party, enemies, runs=runs))['won'])
        print(f'{cid} | {name} | {cells[0]:.0%} | {cells[1]:.0%} | {cells[2]:.0%}', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

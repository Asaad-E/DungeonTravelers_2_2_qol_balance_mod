"""Row J02 of the register on the variant: at every boss from C30 on, the best option of the mage beside the best of
the Dark Lord (value per time, the measure of tools/skill_worth.py), and the elemental resistances of the enemies.

    python magic_wall.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import skill_worth                                        # noqa: E402
from sim import scenario, setup as setup_mod              # noqa: E402
from sim import policy as P                               # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

ELEMENTS = ('fire', 'water', 'wind', 'earth', 'lightning')


def best(data, setup, role, cid, policy):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    boss = scenario.fixed_battle(data, cp['Floor'], scenario.battle_numbers(cp)[-1])
    member = skill_worth.full_member(data, setup, role, level, gear, cp)
    base = [u for u in scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
            if u.kind == 'member' and u.name != member.name][:4]
    sc = skill_worth.scores(data, setup, member, base + [member], boss, policy)
    name = max(sc, key=sc.get)
    return name, sc[name], boss


def main():
    setup = setup_mod.load()
    policy = P.Policy(P.load_rules(setup.policies), setup.settings)
    variants = (('vanilla', game_data()), ('mod', balance_data(game_data())))
    ids = [cp['ID'] for cp in setup.checkpoints]
    ids = ids[ids.index('C30'):]
    for cid in ids:
        cells, wall = [], ''
        for tag, data in variants:
            try:
                spell, mage, boss = best(data, setup, 'mage', cid, policy)
                _, lord, _ = best(data, setup, 'dark lord', cid, policy)
            except Exception as error:                      # a checkpoint the model cannot build
                cells.append(f'{tag}: {type(error).__name__}')
                continue
            cells.append(f'{tag} {mage / lord:.0%} ({spell})' if lord else f'{tag} -')
            cp = setup.checkpoint(cid)
            fight = next(b for b in data.fixed if b['floor'] == cp['Floor'] and b['number'] == scenario.battle_numbers(cp)[-1])
            wall = '; '.join(data.enemies[eid]['name'] + ' ' + '/'.join(str(data.enemies[eid]['res_' + e]) for e in ELEMENTS)
                             for eid, _ in fight['enemies'][:3])
        print(cid, '|', ' | '.join(cells), '|', wall, flush=True)


if __name__ == '__main__':
    main()

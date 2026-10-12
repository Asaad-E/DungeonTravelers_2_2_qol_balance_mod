"""Row F01 of the register (every party must hold a Maid): the Meta party with a Bishop or a Sage in the place of
its Diva, so that nobody of the Maid line stands in it, at the bosses of the battery, in vanilla and on the variant.
Nothing is written.

    python no_maid_line.py k/n [runs]
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

MAID_LINE = {'Maid', 'Bard', 'Dancer', 'Diva', 'Mistress', 'Etoile'}


def main():
    k, n = (int(x) for x in sys.argv[1].split('/'))
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    vanilla, setup = game_data(), setup_mod.load()
    variant = balance_data(vanilla)
    ids = [c.strip() for c in str(setup.settings['battery_checkpoints']).split(';')]
    for cid in ids[(k - 1) * len(ids) // n: k * len(ids) // n]:
        cp = setup.checkpoint(cid)
        cells = []
        for support in ('diva', 'healer', 'sage'):
            roles = [support if r == 'diva' else r for r in setup.battery['Meta'][1]]
            for source in (vanilla, variant):
                def party():
                    return scenario.party_of_roles(source, setup, cid, roles)

                def enemies():
                    return [scenario.fixed_battle(source, cp['Floor'], b) for b in scenario.battle_numbers(cp)]

                line = any(str(getattr(u, 'role', '')) in ('diva', 'maid', 'mistress', 'etoile') for u in party())
                won = measures.summary(scenario.play(source, setup, party, enemies, runs=runs))['won']
                cells.append(f"{won:.0%}{'*' if line and support != 'diva' else ''}")
        print(f'{cid} | diva {cells[0]} > {cells[1]} | healer {cells[2]} > {cells[3]} | sage {cells[4]} > {cells[5]}', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

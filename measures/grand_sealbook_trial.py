"""What the second enchantment of a grand sealbook adds (rows P001 - P005): the reference party carries the book at
a postgame checkpoint, with the one enchantment the game gives it and with the two the variant gives it. The
enchantment of a grand sealbook acts for every member (docs/FORMULAS.md 16.1). Variant for everything else; nothing is
written.

    python measures/grand_sealbook_trial.py 955 P24 150
    python measures/grand_sealbook_trial.py 955 P24 150 --engine     the same, played by the C# engine (engine_cs/)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402


def main():
    engine = '--engine' in sys.argv
    if engine:
        sys.argv.remove('--engine')
    book, cid, runs = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
    vanilla, setup = game_data(), setup_mod.load()
    data = balance_data(vanilla)
    setup.grand_sealbooks = [{'From checkpoint': setup.checkpoints[0]['ID'], 'Sealbook': book, 'Name': '', 'Source': ''}]
    both = list(data.sealbooks[book]['enchants'])
    name = data.sealbooks[book]['name']
    for label, enchants in (('one enchantment', list(vanilla.sealbooks[book]['enchants'])), ('two', both)):
        data.sealbooks[book]['enchants'] = enchants
        _, res = (__import__('engine_client').play_checkpoint_sim if engine else measures.play_checkpoint)(data, setup, cid, runs)
        print(f"{name} {cid} | {label} {enchants} | won {res['won']:.0%} | length {res['time']:.1f} | lowest HP "
              f"{res['lowest_hp']:.0%}", flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

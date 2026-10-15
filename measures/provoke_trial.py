"""What the size of Provoke changes (rows S032 - S036): the tank in the last place of the reference party, with the
enmity of Provoke (effect 170, by level) as the game has it, as the variant has it, and as each list given on the
command line. The weight of a member when an enemy picks one target is the share of her position (the party adds up
to 100) plus that value on the enemy she provoked (docs/FORMULAS.md 9.1), so the share of single-target attacks she
draws is (her share + value) / (100 + value). Variant for everything else; nothing is written.

    python measures/provoke_trial.py C30 100 250,325,400,500,600
    python measures/provoke_trial.py C30 100 250,325,400,500,600 --engine     the same, played by the C# engine (engine_cs/)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import class_stages                                       # noqa: E402
from sim import setup as setup_mod                        # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

ENGINE = False                               # --engine: the battles are played by the C# engine
PROVOKE, ENMITY = ('Technique', 0), 170
VANILLA = [250, 250, 250, 250, 250]


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    cid, runs = sys.argv[1], int(sys.argv[2])
    tried = [[float(x) for x in arg.split(',')] for arg in sys.argv[3:]]
    data, setup = balance_data(game_data()), setup_mod.load()
    skill = data.skills[PROVOKE]
    built = next(list(values) for effect, _, values in skill.effects if effect == ENMITY)
    for label, values in [('as the game has it', VANILLA), ('as the variant has it', built)] + [(str(t), t) for t in tried]:
        skill.effects = [(e, k, list(values) if e == ENMITY else v) for e, k, v in skill.effects]
        res = (class_stages.play_engine if ENGINE else class_stages.play)(data, setup, cid, 'tank', runs)
        share = ' / '.join(f'{(20 + v) / (100 + v):.0%}' for v in values)
        print(f"{cid} | {label} | she draws {share} | won {res['won']:.0%} | length {res['time']:.1f}", flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

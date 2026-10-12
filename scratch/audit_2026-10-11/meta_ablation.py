"""Which member holds the lead of the Meta party: the party at a boss on the variant, and again with one role changed
for a neighbour each time. Postgame bosses at the crown bonus of postgame_compare.py; nothing is written.

    python meta_ablation.py P06 [runs]
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
SWAPS = (('valkyrie', 'tank'), ('dark lord', 'attacker'), ('treasure hunter', 'shooter'), ('papillon', 'kunoichi'),
         ('diva', 'maid'))


def main():
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    setup = setup_mod.load()
    variant = balance_data(game_data())
    cp = setup.checkpoint(cid)
    if cid in CROWN:
        cp['Crown bonus'] = CROWN[cid]
    meta = list(setup.battery['Meta'][1])
    trials = [('Meta', meta)] + [(f'{old} > {new}', [new if r == old else r for r in meta]) for old, new in SWAPS]
    for label, roles in trials:
        def party():
            return scenario.party_of_roles(variant, setup, cid, roles)

        def enemies():
            return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

        res = measures.summary(scenario.play(variant, setup, party, enemies, runs=runs))
        print(f"{cid} | {label} | {res['won']:.0%} | {res.get('time') or 0:.1f}", flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

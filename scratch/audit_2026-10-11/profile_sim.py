"""Where the time of the simulator goes: the reference party against the boss fights of a checkpoint, under cProfile.

    python profile_sim.py C40 20
"""
import cProfile
import os
import pstats
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402


def main():
    cid, runs = sys.argv[1], int(sys.argv[2])
    start = time.perf_counter()
    data, setup = balance_data(game_data()), setup_mod.load()
    loaded = time.perf_counter()
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)

    def party():
        return scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    def work():
        return scenario.play(data, setup, party, enemies, runs=runs)

    if len(sys.argv) > 3:
        profile = cProfile.Profile()
        result = profile.runcall(work)
        pstats.Stats(profile).sort_stats('tottime').print_stats(28)
    else:
        result = work()
    done = time.perf_counter()
    won = sum(r['won'] for r in result)
    print(f'{sys.implementation.name} load {loaded - start:.1f}s, {runs} fights {done - loaded:.1f}s, '
          f'won {won}, time {sum(r["time"] for r in result):.4f}')


if __name__ == '__main__':
    main()

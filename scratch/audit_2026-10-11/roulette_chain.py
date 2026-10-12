"""Roulette Circus on rows of eight random battles (row F22): with and without it, as tools/skill_value.py plays a chain.

    python roulette_chain.py C05
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import skill_value                                        # noqa: E402
from sim import setup as setup_mod                        # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

data, setup = balance_data(game_data()), setup_mod.load()
skill = next(s for s in data.skills.values() if s.name == 'Roulette Circus' and s.classes)
for cid in sys.argv[1:]:
    for use in (False, True):
        print(cid, 'with' if use else 'without', skill_value.play(data, setup, 'dolls', cid, skill, use, chain=8), flush=True)

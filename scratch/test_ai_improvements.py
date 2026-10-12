"""
Test script to benchmark improved AI vs original AI across Vanilla and Mod on key checkpoints.
"""
import sys
import copy
import random
sys.path.insert(0, 'mod_project')

from sim.data import game_data
from sim.setup import load
from sim.variant import balance_data
from sim import measures, scenario
from sim.battle import Battle, Action
import sim.policy as policy_module

def run_benchmark():
    data = game_data()
    setup = load()
    mod = balance_data(data)
    
    checkpoints = ['C06', 'C17', 'C30', 'C34', 'C40']
    print("=== BENCHMARKING CHECKPOINTS (Vanilla vs Mod) ===")
    res = measures.check_change(data, setup, [], checkpoints, runs=10, changed=mod)
    for cid, b, a, out in res:
        print(f"[{cid}] Vanilla: won={b['won']*100:.0f}%, time={b['time']:.1f}s, low_hp={b['lowest_hp']*100:.0f}% | "
              f"Mod: won={a['won']*100:.0f}%, time={a['time']:.1f}s, low_hp={a['lowest_hp']*100:.0f}% | Out: {out}")

if __name__ == '__main__':
    run_benchmark()

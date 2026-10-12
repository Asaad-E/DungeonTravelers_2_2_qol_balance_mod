import io
import sys
import os
import random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')

from sim.data import game_data
from sim import setup as setup_mod, scenario
from sim.variant import balance_data
from tools.parallel_party_battery import PARTIES, build_party_complete

data = game_data()
setup = setup_mod.load()
mod = balance_data(data)

print("="*80)
print("TEST DE PARIDAD C29 (CALLIOPE) SIN SILENCINGBATTLE (N=20 RUNS)")
print("="*80)

cp = setup.checkpoint('C29')
runs = 20
seed = 42

def calc_rnds(res_list):
    if not res_list:
        return 0.0
    return sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in res_list) / len(res_list)

for pname, pinfo in PARTIES.items():
    # 1. Vanilla
    def pf_v(): return build_party_complete(data, setup, pinfo['roles'], 'C29')
    def ef_v(): return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    res_v = scenario.play(data, setup, pf_v, ef_v, runs=runs, seed=seed)
    wins_v = [r for r in res_v if r['won']]
    pct_v = len(wins_v) / runs * 100.0
    rnds_v = calc_rnds(wins_v) if wins_v else calc_rnds(res_v)

    # 2. Mod (SYMMETRIC STANDARD BATTLE)
    def pf_m(): return build_party_complete(mod, setup, pinfo['roles'], 'C29')
    def ef_m(): return [scenario.fixed_battle(mod, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    res_m = scenario.play(mod, setup, pf_m, ef_m, runs=runs, seed=seed)
    wins_m = [r for r in res_m if r['won']]
    pct_m = len(wins_m) / runs * 100.0
    rnds_m = calc_rnds(wins_m) if wins_m else calc_rnds(res_m)

    print(f"  Party: {pname:<16} | Vanilla: {pct_v:5.1f}% ({rnds_v:4.1f}r) | Mod (Simétrico): {pct_m:5.1f}% ({rnds_m:4.1f}r) | Delta: {pct_m - pct_v:+5.1f}%", flush=True)

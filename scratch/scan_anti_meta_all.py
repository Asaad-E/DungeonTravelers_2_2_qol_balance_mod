import sys
sys.path.insert(0, 'mod_project')
from sim import setup as setup_mod, scenario
from sim.data import game_data
from sim.variant import balance_data
from tools.parallel_party_battery import CHECKPOINTS, PARTIES, build_party_complete

data = game_data()
setup = setup_mod.load()
variant = balance_data(data)

p_info = PARTIES['Anti-Meta']
with open('mod_project/scratch/anti_meta_scan_results.txt', 'w', encoding='utf-8') as out_f:
    out_f.write("=== Anti-Meta Win Rates across 17 Story Bosses (10 runs each) ===\n")
    for cid in CHECKPOINTS:
        cp = setup.checkpoint(cid)
        def pf(): return build_party_complete(variant, setup, p_info['roles'], cid)
        def ef(): return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res = scenario.play(variant, setup, pf, ef, runs=10, seed=42)
        wins = sum(1 for r in res if r['won'])
        times = [r['time'] for r in res if r['won']]
        avg_t = sum(times)/len(times) if times else 0
        boss_name = cp.get('Boss (as the story page names it)', 'Unknown')
        out_f.write(f"{cid}: {wins*10}% win | {avg_t:.1f}t | {boss_name}\n")
        print(f"Finished {cid}: {wins*10}% win")

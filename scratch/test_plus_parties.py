import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from tools.parallel_party_battery import PARTIES, init_worker, run_single_task

init_worker()

bosses = ['C30', 'C36', 'C38', 'C40']
test_parties = ['Juggernaut', 'Juggernaut-Plus', 'Anti-Meta', 'Anti-Meta-Plus']

print('Testing Win Rates (N=20 iterations):')
for b in bosses:
    print(f'=== Boss {b} ===')
    for p in test_parties:
        roles = PARTIES[p]['roles']
        cid, p_name, win_pct_v, rounds_v, wins_v, win_pct_m, rounds_m, wins_m = run_single_task((b, p, roles, 20, 123))
        print(f"  {p:16}: Vanilla {win_pct_v:3.0f}% | Mod {win_pct_m:3.0f}% (turns: {rounds_m:.1f})")

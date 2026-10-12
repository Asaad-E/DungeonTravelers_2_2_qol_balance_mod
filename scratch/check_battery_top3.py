import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
from sim.data import game_data
from sim.setup import load
from sim.variant import balance_data
from sim import scenario
from tools.parallel_party_battery import build_party_complete, PARTIES

d = game_data()
s = load()
var = balance_data(d)
runs = 20

print("=== VERIFYING BATTERY PERFORMANCE UNDER MOD BALANCE_DATA() ===")
for cid in ['C10', 'C13', 'C24']:
    cp = s.checkpoint(cid)
    boss_name = cp.get('Boss (as the story page names it)', '')
    print(f"\n[{cid}] {boss_name}:")
    
    res_summary = {}
    for p_name, p_info in PARTIES.items():
        roles = p_info['roles']
        def party_f():
            return build_party_complete(var, s, roles, cid)
        def enemies_f():
            return [scenario.fixed_battle(var, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res = scenario.play(var, s, party_f, enemies_f, runs=runs, seed=42)
        wins = [r for r in res if r['won']]
        pct = len(wins) / len(res) * 100.0
        rnds = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins or res) / len(wins or res)
        res_summary[p_name] = (pct, rnds)
        
    avg_w = sum(w for w, _ in res_summary.values()) / len(res_summary)
    avg_r = sum(r for _, r in res_summary.values()) / len(res_summary)
    print(f"  Overall: Win={avg_w:.1f}%, Rnds={avg_r:.1f}r")
    for p, (w, r) in res_summary.items():
        print(f"    - {p:<13}: {w:>3.0f}% ({r:>4.1f}r)")

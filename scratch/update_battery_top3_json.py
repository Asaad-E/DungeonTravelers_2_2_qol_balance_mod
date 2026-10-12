import json
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

json_path = 'mod_project/scratch/battery_old_vs_new_ai_results.json'
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for cid in ['C10', 'C13', 'C24']:
    cp = s.checkpoint(cid)
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
        # Update m_new
        data[cid][p_name]['m_new'] = [pct, round(rnds, 2), pct >= 50.0]
        print(f"Updated {cid} {p_name} m_new: {pct}% ({rnds:.2f}r)")

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Saved updated battery JSON!")

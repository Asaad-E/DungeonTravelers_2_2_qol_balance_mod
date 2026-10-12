import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
import copy
from sim.data import game_data
from sim.setup import load
from sim.variant import balance_data
from sim import scenario
from tools.parallel_party_battery import build_party_complete, PARTIES

d = game_data()
s = load()
var = balance_data(d)

runs = 20

def run_test(var_custom, cid):
    cp = s.checkpoint(cid)
    res_summary = {}
    for p_name, p_info in PARTIES.items():
        roles = p_info['roles']
        def party_f():
            return build_party_complete(var_custom, s, roles, cid)
        def enemies_f():
            return [scenario.fixed_battle(var_custom, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res = scenario.play(var_custom, s, party_f, enemies_f, runs=runs, seed=42)
        wins = [r for r in res if r['won']]
        pct = len(wins) / len(res) * 100.0
        rnds = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins or res) / len(wins or res)
        res_summary[p_name] = (pct, rnds)
    return res_summary

print("Simulating baseline and buff variations for C10, C13, C24...")

experiments = [
    ('C10', 1002, [1.0, 1.20, 1.30]),
    ('C13', 760, [1.0, 1.20, 1.30]),
    ('C24', 825, [1.0, 1.25, 1.35]),
]

for cid, boss_id, hp_ratios in experiments:
    print(f"\n=================== CHECKPOINT {cid} ===================", flush=True)
    for ratio in hp_ratios:
        v_mod = copy.deepcopy(var)
        orig_hp = v_mod.enemies[boss_id]['hp']
        orig_atk = v_mod.enemies[boss_id]['atk']
        orig_def = v_mod.enemies[boss_id]['def']
        
        new_hp = int(round(orig_hp * ratio))
        v_mod.enemies[boss_id]['hp'] = new_hp
        if ratio > 1.0:
            # Also mild ATK/DEF buff (+5% to +10%)
            v_mod.enemies[boss_id]['atk'] = int(round(orig_atk * (1.0 + (ratio - 1.0) * 0.3)))
            v_mod.enemies[boss_id]['def'] = int(round(orig_def * (1.0 + (ratio - 1.0) * 0.3)))
            
        summary = run_test(v_mod, cid)
        label = f"Ratio {ratio:.2f} (HP: {orig_hp} -> {new_hp}, ATK: {orig_atk} -> {v_mod.enemies[boss_id]['atk']}, DEF: {orig_def} -> {v_mod.enemies[boss_id]['def']})"
        print(f"\n--- {label} ---", flush=True)
        avg_w = sum(w for w, _ in summary.values()) / len(summary)
        avg_r = sum(r for _, r in summary.values()) / len(summary)
        print(f"Overall Avg: Win={avg_w:.1f}%, Rnd={avg_r:.1f}r", flush=True)
        for p, (w, r) in summary.items():
            print(f"  {p:<13}: {w:>3.0f}% ({r:>4.1f}r)", flush=True)

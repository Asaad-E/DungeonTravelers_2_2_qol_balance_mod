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

# Proposed values
buffs = {
    'C10': (1002, 2289, 73, 56), # +15% HP, +4% ATK/DEF
    'C13': (760,  2732, 60, 58), # +20% HP, +5% ATK/DEF
    'C24': (825,  5728, 163, 129), # +25% HP, +7% ATK/DEF
}

v_mod = copy.deepcopy(var)
for cid, (eid, hp, atk, df) in buffs.items():
    v_mod.enemies[eid]['hp'] = hp
    v_mod.enemies[eid]['atk'] = atk
    v_mod.enemies[eid]['def'] = df

print("=== VERIFYING PROPOSED TOP 3 BUFFS ACROSS ALL 5 PARTIES ===")
for cid in ['C10', 'C13', 'C24']:
    cp = s.checkpoint(cid)
    boss_name = cp.get('Boss (as the story page names it)', '')
    eid, hp, atk, df = buffs[cid]
    orig = var.enemies[eid]
    print(f"\n[{cid}] {boss_name}:")
    print(f"  HP: {orig['hp']} -> {hp} (+{(hp/orig['hp']-1)*100:.1f}%) | ATK: {orig['atk']} -> {atk} | DEF: {orig['def']} -> {df}")
    
    res_summary = {}
    for p_name, p_info in PARTIES.items():
        roles = p_info['roles']
        def party_f():
            return build_party_complete(v_mod, s, roles, cid)
        def enemies_f():
            return [scenario.fixed_battle(v_mod, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res = scenario.play(v_mod, s, party_f, enemies_f, runs=runs, seed=42)
        wins = [r for r in res if r['won']]
        pct = len(wins) / len(res) * 100.0
        rnds = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins or res) / len(wins or res)
        res_summary[p_name] = (pct, rnds)
        
    avg_w = sum(w for w, _ in res_summary.values()) / len(res_summary)
    avg_r = sum(r for _, r in res_summary.values()) / len(res_summary)
    print(f"  Overall: Win={avg_w:.1f}%, Rnds={avg_r:.1f}r")
    for p, (w, r) in res_summary.items():
        print(f"    - {p:<13}: {w:>3.0f}% ({r:>4.1f}r)")

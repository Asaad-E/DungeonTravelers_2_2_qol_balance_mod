"""
Test script: Anti-Meta with Diva and Juggernaut with Diva across challenging boss checkpoints (C36, C38, C40).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')

from sim.data import game_data
from sim.setup import load
from sim.variant import balance_data
from sim import scenario
from tools.parallel_party_battery import build_party_complete

d = game_data()
s = load()
var = balance_data(d)

checkpoints = ['C34', 'C36', 'C38', 'C40']
runs = 20

# Configurations to test
configs = {
    'Anti-Meta (Base)': ['magical princess', 'mistress', 'soul summoner', 'joker', 'dolls'],
    'Anti-Meta (+Diva / no Dolls)': ['magical princess', 'mistress', 'soul summoner', 'joker', 'diva'],
    'Anti-Meta (+Diva / no Joker)': ['magical princess', 'mistress', 'soul summoner', 'dolls', 'diva'],
    'Anti-Meta (+Diva / no Mistress)': ['magical princess', 'diva', 'soul summoner', 'joker', 'dolls'],
    'Juggernaut (Base)': ['tank', 'attacker', 'dark lord', 'kunoichi', 'etoile'],
    'Juggernaut (+Diva / no Etoile)': ['tank', 'attacker', 'dark lord', 'kunoichi', 'diva'],
    'Juggernaut (+Diva / Dual Performer)': ['tank', 'attacker', 'dark lord', 'etoile', 'diva'],
}

def test_checkpoint(cid):
    cp = s.checkpoint(cid)
    print(f"\n==================== CHECKPOINT {cid} ({cp['Boss (as the story page names it)']}) ====================")
    print(f"{'Config':<35} | {'Mod Win%':<10} | {'Mod Rnd':<8} | {'Van Win%':<10} | {'Van Rnd':<8}")
    print("-" * 80)
    
    for cname, roles in configs.items():
        # Mod
        def party_m():
            return build_party_complete(var, s, roles, cid)
        def enemies_m():
            return [scenario.fixed_battle(var, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res_m = scenario.play(var, s, party_m, enemies_m, runs=runs, seed=42)
        
        # Vanilla
        def party_v():
            return build_party_complete(d, s, roles, cid)
        def enemies_v():
            return [scenario.fixed_battle(d, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res_v = scenario.play(d, s, party_v, enemies_v, runs=runs, seed=42)
        
        def calc(res):
            wins = [r for r in res if r['won']]
            losses = [r for r in res if not r['won']]
            pct = len(wins) / len(res) * 100.0
            if wins:
                rnds = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins) / len(wins)
            else:
                rnds = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in losses) / max(1, len(losses))
            return pct, rnds
            
        m_pct, m_rnd = calc(res_m)
        v_pct, v_rnd = calc(res_v)
        
        print(f"{cname:<35} | {m_pct:>6.0f}%    | {m_rnd:>6.1f}r  | {v_pct:>6.0f}%    | {v_rnd:>6.1f}r")

if __name__ == '__main__':
    for cid in checkpoints:
        test_checkpoint(cid)

"""
Comprehensive audit of difficulty curve with the smart AI across all story checkpoints C01-C40.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')

from sim.data import game_data
from sim.setup import load
from sim.variant import balance_data
from sim import measures, scenario
from sim.battle import Battle
import sim.policy as P

from scratch.test_ai_live import (
    improved_expected_damage, improved_best_single_target,
    improved_act_damage, improved_act_status, improved_act_dispel
)

def run_full_curve_audit():
    data = game_data()
    setup = load()
    mod = balance_data(data)
    
    # Apply smart AI
    Battle.expected_damage = improved_expected_damage
    P.best_single_target = improved_best_single_target
    P.act_damage = improved_act_damage
    P.act_status = improved_act_status
    P.act_dispel = improved_act_dispel
    P.ACTIONS['damage'] = improved_act_damage
    P.ACTIONS['status'] = improved_act_status
    P.ACTIONS['dispel'] = improved_act_dispel
    
    checkpoints = [c['ID'] for c in setup.checkpoints if str(c['ID']).startswith('C')]
    print(f"Auditing {len(checkpoints)} story checkpoints under Smart AI...")
    
    # Run in batches of 10
    results = measures.check_change(data, setup, [], checkpoints, runs=10, changed=mod)
    
    out_count = 0
    print("\n--- RESULTS TABLE ---")
    print(f"{'CID':<6} | {'Van Win':<8} | {'Van Time':<9} | {'Mod Win':<8} | {'Mod Time':<9} | {'Windows Left':<20}")
    print("-" * 75)
    for cid, b, a, out in results:
        v_win = f"{b['won']*100:.0f}%"
        v_time = f"{b['time']:.1f}s" if b['time'] else "N/A"
        m_win = f"{a['won']*100:.0f}%"
        m_time = f"{a['time']:.1f}s" if a['time'] else "N/A"
        out_str = ", ".join(out) if out else "OK (parity)"
        if out:
            out_count += 1
        print(f"{cid:<6} | {v_win:<8} | {v_time:<9} | {m_win:<8} | {m_time:<9} | {out_str:<20}")
        
    print("-" * 75)
    print(f"Total checkpoints: {len(checkpoints)}, Checkpoints with window deviations: {out_count}")

if __name__ == '__main__':
    run_full_curve_audit()

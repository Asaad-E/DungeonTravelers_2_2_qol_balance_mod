import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import scenario
from sim import setup as setup_mod
from sim.data import game_data
from sim.variant import balance_data
from tools.parallel_party_battery import PARTIES, build_party_complete

RUNS = 25
CID = 'C40'

def eval_single(variant_name, party_name, seed):
    data = game_data()
    setup = setup_mod.load()
    
    if variant_name == 'Vanilla':
        ds = data
    elif variant_name == 'Old Mod':
        ds = balance_data(data, path='mod_project/scratch/old_balance_changes.xlsx')
    elif variant_name == 'New Mod':
        ds = balance_data(data)
    else:
        raise ValueError(f"Unknown variant: {variant_name}")
        
    p_info = PARTIES[party_name]
    cp = setup.checkpoint(CID)
    
    def party_factory():
        return build_party_complete(ds, setup, p_info['roles'], CID)
        
    def enemy_factory():
        return [scenario.fixed_battle(ds, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        
    res = scenario.play(ds, setup, party_factory, enemy_factory, runs=1, seed=seed)[0]
    
    p0_time = res['parts'][0]['time'] if res['parts'][0]['won'] else None
    p1_time = res['parts'][1]['time'] if len(res['parts']) > 1 and res['parts'][1]['won'] else None
    
    return {
        'won': res['won'],
        'time': res['time'] if res['won'] else None,
        'lowest_hp': res['lowest_hp'],
        'p0_time': p0_time,
        'p1_time': p1_time
    }

def main():
    variants = ['Vanilla', 'Old Mod', 'New Mod']
    tasks = []
    
    # Prepare task tuples
    for v in variants:
        for p in PARTIES:
            for s in range(RUNS):
                tasks.append((v, p, 10000 + s * 17))
                
    print(f"Executing {len(tasks)} runs across {len(variants)} variants and {len(PARTIES)} parties...")
    t0 = time.time()
    
    # We can run with ProcessPoolExecutor
    raw_results = {v: {p: [] for p in PARTIES} for v in variants}
    
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(eval_single, v, p, s) for v, p, s in tasks]
        for (v, p, s), fut in zip(tasks, futures):
            res = fut.result()
            raw_results[v][p].append(res)
            
    print(f"Simulations completed in {time.time() - t0:.1f}s.")
    
    # Process summary
    summary = {}
    for v in variants:
        summary[v] = {}
        for p in PARTIES:
            runs = raw_results[v][p]
            wins = [r for r in runs if r['won']]
            win_pct = len(wins) / len(runs) * 100
            avg_time = sum(r['time'] for r in wins) / len(wins) if wins else 0
            avg_hp = sum(r['lowest_hp'] for r in runs) / len(runs) * 100
            
            p0_times = [r['p0_time'] for r in runs if r['p0_time'] is not None]
            p1_times = [r['p1_time'] for r in runs if r['p1_time'] is not None]
            avg_p0 = sum(p0_times) / len(p0_times) if p0_times else 0
            avg_p1 = sum(p1_times) / len(p1_times) if p1_times else 0
            
            summary[v][p] = {
                'win_pct': win_pct,
                'time': avg_time,
                'hp': avg_hp,
                'p0': avg_p0,
                'p1': avg_p1
            }
            
    # Output markdown report to file and stdout
    with open('mod_project/scratch/c40_5parties_report.txt', 'w', encoding='utf-8') as out_f:
        out_f.write("# Resultados de la Batalla Final (C40: Demiurgo + Atialco) en los 5 Arquetipos de Equipo\n\n")
        out_f.write(f"Muestra: {RUNS} combates por equipo y variante ({RUNS * len(PARTIES) * len(variants)} totales).\n\n")
        
        out_f.write("### Tabla Comparativa por Arquetipo (Win% / Duración Total / HP Mínimo / Fase 1 / Fase 2)\n\n")
        out_f.write("| Arquetipo de Party | Configuración | Vanilla | Old Mod (e2cf414) | New Mod (Actual) | Variación Vanilla → New |\n")
        out_f.write("|---|---|---|---|---|---|\n")
        
        for p, p_info in PARTIES.items():
            s_v = summary['Vanilla'][p]
            s_o = summary['Old Mod'][p]
            s_n = summary['New Mod'][p]
            
            v_str = f"{s_v['win_pct']:.0f}% / {s_v['time']:.1f}t (HP: {s_v['hp']:.0f}%) [F1:{s_v['p0']:.1f}t, F2:{s_v['p1']:.1f}t]"
            o_str = f"{s_o['win_pct']:.0f}% / {s_o['time']:.1f}t (HP: {s_o['hp']:.0f}%) [F1:{s_o['p0']:.1f}t, F2:{s_o['p1']:.1f}t]"
            n_str = f"**{s_n['win_pct']:.0f}%** / **{s_n['time']:.1f}t** (HP: {s_n['hp']:.0f}%) [F1:{s_n['p0']:.1f}t, F2:{s_n['p1']:.1f}t]"
            
            diff_turns = s_n['time'] - s_v['time']
            diff_win = s_n['win_pct'] - s_v['win_pct']
            diff_str = f"{diff_win:+.0f}% Win, {diff_turns:+.1f} turnos"
            
            desc_short = p_info['desc'].split('(')[1].rstrip(')') if '(' in p_info['desc'] else p_info['desc']
            out_f.write(f"| **{p}** ({p_info['opt']}) | {desc_short} | {v_str} | {o_str} | {n_str} | {diff_str} |\n")
            
        out_f.write("\n")

if __name__ == '__main__':
    main()

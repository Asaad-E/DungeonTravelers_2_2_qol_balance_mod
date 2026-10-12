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
from tools.parallel_party_battery import CHECKPOINTS, build_party_complete

RUNS = 15

CONFIGS = {
    'Anti-Meta (Original)': {
        'desc': 'Magical Princess, Mistress, Soul Summoner, Joker, Dolls (Papillon)',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'joker', 'dolls']
    },
    'Anti-Meta-Plus (Bishop)': {
        'desc': 'Magical Princess, Mistress, Soul Summoner, Joker, Bishop',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'joker', 'healer']
    },
    'Anti-Meta-Plus (Sage)': {
        'desc': 'Magical Princess, Mistress, Soul Summoner, Joker, Sage',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'joker', 'sage']
    }
}

def eval_single(cfg_name, cid, seed):
    data = game_data()
    setup = setup_mod.load()
    ds = balance_data(data)
    
    cfg = CONFIGS[cfg_name]
    cp = setup.checkpoint(cid)
    
    def party_factory():
        return build_party_complete(ds, setup, cfg['roles'], cid)
        
    def enemy_factory():
        return [scenario.fixed_battle(ds, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        
    res = scenario.play(ds, setup, party_factory, enemy_factory, runs=1, seed=seed)[0]
    return {
        'won': res['won'],
        'time': res['time'] if res['won'] else None,
        'lowest_hp': res['lowest_hp']
    }

def main():
    tasks = []
    for cid in CHECKPOINTS:
        for cfg_name in CONFIGS:
            for s in range(RUNS):
                tasks.append((cfg_name, cid, 30000 + s * 17))
                
    print(f"Executing {len(tasks)} runs across {len(CONFIGS)} compositions and {len(CHECKPOINTS)} bosses...")
    t0 = time.time()
    
    raw = {c: {cid: [] for cid in CHECKPOINTS} for c in CONFIGS}
    
    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(eval_single, c, cid, s) for c, cid, s in tasks]
        for (c, cid, s), fut in zip(tasks, futures):
            res = fut.result()
            raw[c][cid].append(res)
            
    print(f"Simulations completed in {time.time() - t0:.1f}s.")
    
    summary = {}
    for c in CONFIGS:
        summary[c] = {}
        for cid in CHECKPOINTS:
            runs = raw[c][cid]
            wins = [r for r in runs if r['won']]
            win_pct = len(wins) / len(runs) * 100
            avg_time = sum(r['time'] for r in wins) / len(wins) if wins else 0
            avg_hp = sum(r['lowest_hp'] for r in runs) / len(runs) * 100
            summary[c][cid] = {
                'win_pct': win_pct,
                'time': avg_time,
                'hp': avg_hp
            }
            
    setup = setup_mod.load()
    with open('mod_project/scratch/anti_meta_plus_comparison.txt', 'w', encoding='utf-8') as out_f:
        out_f.write("# Comparativa Completa: Anti-Meta Original vs Anti-Meta-Plus (Bishop) vs Anti-Meta-Plus (Sage)\n\n")
        out_f.write(f"Muestra: {RUNS} combates por jefe y composición ({len(tasks)} combates en total).\n\n")
        out_f.write("| Checkpoint | Jefe | Nivel | Anti-Meta Original | Anti-Meta-Plus (Bishop) | Anti-Meta-Plus (Sage) | Veredicto / Impacto |\n")
        out_f.write("|---|---|:---:|---|---|---|---|\n")
        
        for cid in CHECKPOINTS:
            cp = setup.checkpoint(cid)
            boss = cp.get('Boss (as the story page names it)', 'Jefe')
            lvl = cp.get('Level', '')
            
            s_orig = summary['Anti-Meta (Original)'][cid]
            s_bish = summary['Anti-Meta-Plus (Bishop)'][cid]
            s_sage = summary['Anti-Meta-Plus (Sage)'][cid]
            
            orig_str = f"{s_orig['win_pct']:.0f}% / {s_orig['time']:.1f}t (HP: {s_orig['hp']:.0f}%)" if s_orig['win_pct'] > 0 else f"**0%** (Cae tras {s_orig['hp']:.0f}% HP)"
            bish_str = f"{s_bish['win_pct']:.0f}% / {s_bish['time']:.1f}t (HP: {s_bish['hp']:.0f}%)" if s_bish['win_pct'] > 0 else f"**0%**"
            sage_str = f"{s_sage['win_pct']:.0f}% / {s_sage['time']:.1f}t (HP: {s_sage['hp']:.0f}%)" if s_sage['win_pct'] > 0 else f"**0%**"
            
            # Note on impact
            notes = []
            if s_orig['win_pct'] == 0 and (s_bish['win_pct'] > 0 or s_sage['win_pct'] > 0):
                notes.append(f"Resuelve wipe (B:{s_bish['win_pct']:.0f}%, S:{s_sage['win_pct']:.0f}%)")
            elif s_bish['win_pct'] > s_orig['win_pct'] or s_sage['win_pct'] > s_orig['win_pct']:
                notes.append("Mayor estabilidad")
            elif s_orig['win_pct'] == s_bish['win_pct'] == s_sage['win_pct']:
                notes.append("Victoria limpia")
            else:
                notes.append("Similar")
                
            note_str = ", ".join(notes)
            out_f.write(f"| **{cid}** | {boss} | Lvl {lvl} | {orig_str} | **{bish_str}** | **{sage_str}** | {note_str} |\n")
            
        out_f.write("\n")
        
    print("Report written to mod_project/scratch/anti_meta_plus_comparison.txt")

if __name__ == '__main__':
    main()

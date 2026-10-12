import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
import json
from sim.setup import load

s = load()
with open('mod_project/scratch/battery_old_vs_new_ai_results.json', encoding='utf-8') as f:
    data = json.load(f)

boss_stats = []
for cid in sorted(data.keys()):
    cp_info = s.checkpoint(cid)
    boss_name = cp_info.get('Boss (as the story page names it)', '')
    parties = data[cid]
    
    # Mod new AI
    m_wins = [parties[p]['m_new'][0] for p in parties]
    m_rnds = [parties[p]['m_new'][1] for p in parties]
    m_avg_win = sum(m_wins) / len(m_wins)
    m_min_win = min(m_wins)
    m_avg_rnd = sum(m_rnds) / len(m_rnds)
    
    # Van new AI
    v_wins = [parties[p]['v_new'][0] for p in parties]
    v_rnds = [parties[p]['v_new'][1] for p in parties]
    v_avg_win = sum(v_wins) / len(v_wins)
    v_min_win = min(v_wins)
    v_avg_rnd = sum(v_rnds) / len(v_rnds)
    
    boss_stats.append({
        'cid': cid,
        'boss': boss_name,
        'm_avg_win': m_avg_win,
        'm_min_win': m_min_win,
        'm_avg_rnd': m_avg_rnd,
        'm_wins': {p: parties[p]['m_new'][0] for p in parties},
        'm_rnds': {p: parties[p]['m_new'][1] for p in parties},
        'v_avg_win': v_avg_win,
        'v_min_win': v_min_win,
        'v_avg_rnd': v_avg_rnd,
    })

# Sort by mod avg win descending, then min win descending, then rnd ascending
boss_stats.sort(key=lambda x: (x['m_avg_win'], x['m_min_win'], -x['m_avg_rnd']), reverse=True)

print(f"{'CP':<5} | {'Boss':<24} | {'Mod Avg Win%':<12} | {'Mod Min Win%':<12} | {'Mod Avg Rnd':<12} | {'Van Avg Win%':<12} | {'Van Min Win%':<12}")
print("-" * 105)
for b in boss_stats:
    print(f"{b['cid']:<5} | {b['boss'][:22]:<24} | {b['m_avg_win']:>10.1f}%  | {b['m_min_win']:>10.0f}%  | {b['m_avg_rnd']:>10.1f}r  | {b['v_avg_win']:>10.1f}%  | {b['v_min_win']:>10.0f}%")

print("\n" + "=" * 80)
print("TOP 5 JEFES MÁS FÁCILES (Detalle por Party en Mod):")
print("=" * 80)
for b in boss_stats[:5]:
    print(f"\n[{b['cid']}] {b['boss']}:")
    print(f"  Promedio Win Rate: {b['m_avg_win']:.1f}% | Rondas Promedio: {b['m_avg_rnd']:.1f}r")
    for p, w in b['m_wins'].items():
        r = b['m_rnds'][p]
        print(f"    - {p:<13}: {w:>3.0f}% ({r:>4.1f}r)")

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
import json
from sim.setup import load

s = load()

with open("mod_project/scratch/battery_old_vs_new_ai_results.json", encoding="utf-8") as f:
    data = json.load(f)

print(f"{'CP':<5} | {'Boss':<24} | {'Van Meta/DS':<12} | {'Mod Meta/DS':<12} | {'Diff Meta/DS':<12} | {'Van All (w>=50%)':<16} | {'Mod All (w>=50%)':<16}")
print("-" * 110)

for cid in sorted(data.keys()):
    cp_info = s.checkpoint(cid)
    boss_name = cp_info.get("Boss (as the story page names it)", "")[:23]
    
    # Meta and Dual-Support
    v_top = [data[cid][p]["v_new"][1] for p in ["Meta", "Dual-Support"]]
    m_top = [data[cid][p]["m_new"][1] for p in ["Meta", "Dual-Support"]]
    v_top_avg = sum(v_top) / len(v_top)
    m_top_avg = sum(m_top) / len(m_top)
    diff_top = m_top_avg - v_top_avg

    # All winning parties
    v_win = [data[cid][p]["v_new"][1] for p in data[cid] if data[cid][p]["v_new"][0] >= 50]
    m_win = [data[cid][p]["m_new"][1] for p in data[cid] if data[cid][p]["m_new"][0] >= 50]
    v_win_avg = sum(v_win) / len(v_win) if v_win else 0
    m_win_avg = sum(m_win) / len(m_win) if m_win else 0
    
    print(f"{cid:<5} | {boss_name:<24} | {v_top_avg:>8.1f}r    | {m_top_avg:>8.1f}r    | {diff_top:>+8.1f}r    | {v_win_avg:>10.1f}r ({len(v_win)})  | {m_win_avg:>10.1f}r ({len(m_win)})")

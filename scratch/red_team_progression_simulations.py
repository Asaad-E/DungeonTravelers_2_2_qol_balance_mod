import os, struct, openpyxl

base_dir = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project'
tables_dir = os.path.join(base_dir, 'data_tables')

# Load exp_curve.xlsx
wb_exp = openpyxl.load_workbook(os.path.join(tables_dir, 'exp_curve.xlsx'))
ws_exp = wb_exp['ExpCurve']

curve_data = {}
for row in ws_exp.iter_rows(min_row=2, values_only=True):
    if row and row[0] is not None:
        lv = int(row[0])
        v_exp = int(row[1])
        m_exp = int(row[2])
        v_sp = int(row[3])
        m_sp = int(row[4])
        v_cum = int(row[5])
        m_cum = int(row[6])
        curve_data[lv] = {
            'v_exp': v_exp, 'm_exp': m_exp,
            'v_sp': v_sp, 'm_sp': m_sp,
            'v_cum': v_cum, 'm_cum': m_cum
        }

print("Loaded", len(curve_data), "levels.")

# ==============================================================================
# SIMULATION 1: TOTAL EXP TO LEVEL 99 & CROWN GRIND
# ==============================================================================
v_single_99 = curve_data[99]['v_cum']
m_single_99 = curve_data[99]['m_cum']

# Encounter models:
# 1 battle = 50 seconds (0.8333 minutes)
SEC_PER_BATTLE = 50.0

zones = {
    'Ancient Ruins (Mid-PG)': {'party_exp': 14000, 'per_char': 2800},
    'Radiant Plains 11 (Mid-High)': {'party_exp': 24000, 'per_char': 4800},
    'Matrix F20-30 (High PG)': {'party_exp': 32000, 'per_char': 6400},
    'Matrix F40-50 (Depths PG)': {'party_exp': 45000, 'per_char': 9000},
}

print("=== SIMULATION 1: SINGLE CLIMB (LV 1 -> 99) ===")
print(f"Vanilla: {v_single_99:,} EXP | Modded: {m_single_99:,} EXP (-{(1-m_single_99/v_single_99)*100:.2f}%)")

for zname, zinfo in zones.items():
    per_char = zinfo['per_char']
    # Vanilla 1.0x
    v_battles = v_single_99 / per_char
    v_hours = (v_battles * SEC_PER_BATTLE) / 3600.0
    # Modded 1.0x (base curve)
    m_battles = m_single_99 / per_char
    m_hours = (m_battles * SEC_PER_BATTLE) / 3600.0
    # Modded + Slave's Torc (2.0x)
    m_torc_battles = m_single_99 / (per_char * 2.0)
    m_torc_hours = (m_torc_battles * SEC_PER_BATTLE) / 3600.0
    # Modded + Slave's Torc + Dragon Papi (+50% = 3.0x multiplicative or 2.5x additive)
    m_combo3_battles = m_single_99 / (per_char * 3.0)
    m_combo3_hours = (m_combo3_battles * SEC_PER_BATTLE) / 3600.0
    m_combo25_battles = m_single_99 / (per_char * 2.5)
    m_combo25_hours = (m_combo25_battles * SEC_PER_BATTLE) / 3600.0

    print(f"Zone: {zname}")
    print(f"  Vanilla 1.0x:           {v_battles:6.1f} battles | {v_hours:5.2f} hrs")
    print(f"  Mod Base 1.0x:          {m_battles:6.1f} battles | {m_hours:5.2f} hrs (-{(1-m_hours/v_hours)*100:.1f}%)")
    print(f"  Mod + Torc (2.0x):      {m_torc_battles:6.1f} battles | {m_torc_hours:5.2f} hrs (-{(1-m_torc_hours/v_hours)*100:.1f}%)")
    print(f"  Mod + Torc + Papi (2.5x): {m_combo25_battles:6.1f} battles | {m_combo25_hours:5.2f} hrs (-{(1-m_combo25_hours/v_hours)*100:.1f}%)")
    print(f"  Mod + Torc + Papi (3.0x): {m_combo3_battles:6.1f} battles | {m_combo3_hours:5.2f} hrs (-{(1-m_combo3_hours/v_hours)*100:.1f}%)")

# CROWN GRIND (10 resets Lv 99 -> Lv 1, total 11 climbs)
print("\n=== SIMULATION 1: FULL CROWN GRIND (10 RESETS, 11 CLIMBS) ===")
v_crown_exp = v_single_99 * 11
m_crown_exp = m_single_99 * 11
print(f"Vanilla Crown Total: {v_crown_exp:,} EXP (~{v_crown_exp/1e6:.2f}M EXP)")
print(f"Modded Crown Total:  {m_crown_exp:,} EXP (~{m_crown_exp/1e6:.2f}M EXP)")
print(f"Net EXP Reduction:   {v_crown_exp - m_crown_exp:,} EXP (-{(1-m_crown_exp/v_crown_exp)*100:.2f}%)")

# Also 12.36 lifecycle (initial crawl + resets):
print(f"Lifecycle Model (37.6M vs 27.2M): Vanilla ~37,600,000 EXP, Mod ~27,200,000 EXP (-27.66%)")

for zname, zinfo in zones.items():
    per_char = zinfo['per_char']
    v_b = v_crown_exp / per_char
    v_h = (v_b * SEC_PER_BATTLE) / 3600.0
    m_b = m_crown_exp / per_char
    m_h = (m_b * SEC_PER_BATTLE) / 3600.0
    m_tb = m_crown_exp / (per_char * 2.0)
    m_th = (m_tb * SEC_PER_BATTLE) / 3600.0
    m_cb = m_crown_exp / (per_char * 3.0)
    m_ch = (m_cb * SEC_PER_BATTLE) / 3600.0

    print(f"Crown in {zname}:")
    print(f"  Vanilla (1.0x):         {v_b:7.1f} battles | {v_h:6.2f} hrs")
    print(f"  Mod Base (1.0x):        {m_b:7.1f} battles | {m_h:6.2f} hrs")
    print(f"  Mod + Torc (2.0x):      {m_tb:7.1f} battles | {m_th:6.2f} hrs")
    print(f"  Mod + Torc + Papi(3.0x):{m_cb:7.1f} battles | {m_ch:6.2f} hrs (Grind saved: {v_h - m_ch:5.2f} hrs, -{(1-m_ch/v_h)*100:.1f}%)")

# ==============================================================================
# SIMULATION 2: CATCH-UP BATTLE-BY-BATTLE PROGRESSION
# ==============================================================================
print("\n=== SIMULATION 2: CATCH-UP SIMULATION BATTLE-BY-BATTLE ===")

def simulate_catchup(start_lv, zone_exp, mult_torc=True, grand_seal=True):
    mult = 1.0
    if mult_torc:
        mult *= 2.0
    if grand_seal:
        mult *= 1.5 # Dragon papi +50% vs higher level
    
    current_cum_exp = curve_data[start_lv]['m_cum']
    current_lv = start_lv
    battles = 0
    history = [(0, current_lv, current_cum_exp)]
    
    # Target milestones: Lv 15, Lv 30, Lv 50, Lv 70
    milestones = [15, 30, 50, 70]
    m_results = {}
    
    while current_lv < 70 and battles < 500:
        battles += 1
        # Check if enemy is higher level than recruit
        # Assume postgame mob is level 70
        is_higher = (70 > current_lv)
        effective_mult = (2.0 if mult_torc else 1.0) * (1.5 if (grand_seal and is_higher) else 1.0)
        exp_gain = int(zone_exp * effective_mult)
        current_cum_exp += exp_gain
        
        # Determine new level
        while current_lv < 99 and current_cum_exp >= curve_data[current_lv + 1]['m_cum']:
            current_lv += 1
            if current_lv in milestones and current_lv not in m_results:
                m_results[current_lv] = battles
        
        if battles <= 10 or current_lv in [15, 30, 50, 70]:
            history.append((battles, current_lv, current_cum_exp))
            
    return m_results, history

# Test Lv 1 recruit in Matrix F20-30 (6,400 base EXP/char)
print("--- Recruit starting at Lv 1 in Matrix F20-30 (6,400 EXP base) ---")
res_van, _ = simulate_catchup(1, 6400, mult_torc=False, grand_seal=False)
res_torc, _ = simulate_catchup(1, 6400, mult_torc=True, grand_seal=False)
res_full, hist_full = simulate_catchup(1, 6400, mult_torc=True, grand_seal=True)

print("Milestone battle counts (Lv 1 recruit):")
print(f"  Milestone | Vanilla 1.0x | Mod + Torc (2x) | Mod + Torc + Papi (3x)")
for m in [15, 30, 50, 70]:
    print(f"  Lv {m:2d}    | {res_van.get(m, '>500'):12} | {res_torc.get(m, '>500'):15} | {res_full.get(m, '>500'):22}")

print("\nFirst 10 battles with Torc + Papi:")
for b, lv, exp in hist_full[:11]:
    print(f"  Battle {b:2d}: Level {lv:2d} | Cumulative EXP: {exp:10,d}")

# Test Lv 15 recruit in Matrix F20-30
print("\n--- Recruit starting at Lv 15 in Matrix F20-30 (6,400 EXP base) ---")
res_van15, _ = simulate_catchup(15, 6400, mult_torc=False, grand_seal=False)
res_torc15, _ = simulate_catchup(15, 6400, mult_torc=True, grand_seal=False)
res_full15, _ = simulate_catchup(15, 6400, mult_torc=True, grand_seal=True)
for m in [30, 50, 70]:
    print(f"  Lv {m:2d}    | Vanilla: {res_van15.get(m, '>500')} | Torc: {res_torc15.get(m, '>500')} | Torc+Papi: {res_full15.get(m, '>500')}")

# ==============================================================================
# SIMULATION 3: SKILL POINT ECONOMY (LV 2-30)
# ==============================================================================
print("\n=== SIMULATION 3: EARLY SP ECONOMY ===")
print("Level | Vanilla SP | Mod SP | Vanilla Cum | Mod Cum | Difference")
for lv in [1, 5, 10, 14, 15, 20, 25, 26, 27, 30]:
    v_sp = curve_data[lv]['v_sp']
    m_sp = curve_data[lv]['m_sp']
    v_c = sum(curve_data[i]['v_sp'] for i in range(1, lv+1))
    m_c = sum(curve_data[i]['m_sp'] for i in range(1, lv+1))
    print(f"Lv {lv:2d} | {v_sp:10d} | {m_sp:6d} | {v_c:11d} | {m_c:7d} | +{m_c - v_c:2d} SP")

# ==============================================================================
# SIMULATION 4: LEVEL RESET MILESTONES
# ==============================================================================
print("\n=== SIMULATION 4: LEVEL RESET MILESTONES ===")
# DT2-2 reset bonus rules:
# Drop levels:
# 59-68: +1 bonus stat
# 69-78: +2 bonus stat
# 79-88: +3 bonus stat
# 89-97: +4 bonus stat
# 98+:   +5 bonus stat

reset_milestones = [
    (15, 0, "No stat bonus (Skill Respec)"),
    (30, 0, "No stat bonus (Advanced Class Respec)"),
    (50, 0, "No stat bonus (Master Class Respec)"),
    (60, 1, "+1 Bonus Stat per reset (50 resets needed for Crown)"),
    (70, 2, "+2 Bonus Stats per reset (25 resets needed for Crown)"),
    (80, 3, "+3 Bonus Stats per reset (17 resets needed for Crown)"),
    (90, 4, "+4 Bonus Stats per reset (13 resets needed for Crown)"),
    (99, 5, "+5 Bonus Stats per reset (10 resets needed for Crown)"),
]

print(f"{'Reset Lv':<8} | {'Bonus':<5} | {'Resets Req':<10} | {'Vanilla Climb EXP':<17} | {'Mod Climb EXP':<14} | {'Vanilla Total Crown':<19} | {'Mod Total Crown':<15} | {'EXP/Stat Point'}")
print("-" * 120)
for r_lv, bonus, desc in reset_milestones:
    v_exp = curve_data[r_lv]['v_cum']
    m_exp = curve_data[r_lv]['m_cum']
    if bonus > 0:
        req_resets = (50 + bonus - 1) // bonus
        v_tot = v_exp * req_resets
        m_tot = m_exp * req_resets
        eff = m_exp / bonus
        print(f"Lv {r_lv:<5} | +{bonus:<4} | {req_resets:<10} | {v_exp:17,d} | {m_exp:14,d} | {v_tot:19,d} | {m_tot:15,d} | {eff:10,.0f} EXP")
    else:
        print(f"Lv {r_lv:<5} | +{bonus:<4} | {'N/A':<10} | {v_exp:17,d} | {m_exp:14,d} | {'N/A':<19} | {'N/A':<15} | Respec Only")

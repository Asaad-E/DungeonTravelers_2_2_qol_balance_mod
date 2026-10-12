import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
import enemy_data, enemy_ai, openpyxl

all_e = {e['id']: e for e in enemy_data.enemies()}
samael = all_e[951]
print("Samael ID:", samael['id'])
print("Samael attacks:", samael['attacks'])

wb = openpyxl.load_workbook('mod_project/data_tables/vanilla_source_of_truth.xlsx', data_only=True)
ws_atk = wb['EnemyAttacks']
all_attacks = {r[1]: r[2] for r in ws_atk.iter_rows(min_row=2, values_only=True) if r[1] is not None}
for idx, atkid in enumerate(samael['attacks']):
    print(f"  Slot {idx}: ID {atkid} ('{all_attacks.get(atkid, 'Unknown')}')")

print("\nSamael AI bytes length:", len(samael['ai']))
decoded = enemy_ai.decode(samael['ai'])
print("Samael AI decoded:")
print("  Opening:", [enemy_ai.describe(c) for c in decoded['opening']])
for snum, sdata in decoded['sets'].items():
    print(f"  Set {snum}: weights={sdata['weights']}")

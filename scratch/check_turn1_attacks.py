import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
import enemy_data, openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/vanilla_source_of_truth.xlsx', data_only=True)
ws_atk = wb['EnemyAttacks']
all_attacks = {r[1]: r[2] for r in ws_atk.iter_rows(min_row=2, values_only=True) if r[1] is not None}

all_e = {e['name']: e for e in enemy_data.enemies()}
for name, slot in [("Melek Taus", 1), ("Samael", 6), ("Last Judgment", 2), ("Azathoth", 7)]:
    e = all_e.get(name)
    if e and len(e['attacks']) > slot:
        atk_id = e['attacks'][slot]
        atk_name = all_attacks.get(atk_id, f"Attack {atk_id}")
        print(f"{name} (Enemy {e['id']}): Turn 1 uses slot {slot} -> Attack ID {atk_id} ('{atk_name}')")

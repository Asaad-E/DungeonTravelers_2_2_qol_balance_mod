import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))

from pck_handler import PckArchive
arc = PckArchive('mod_project/backups/SealScrollData.pck')

from enemy_data import enemies
all_enemies = {e['id']: e['name'] for e in enemies()}

# Load enchantment names from balance_criteria.xlsx or qol_rules.xlsx
import openpyxl
wb = openpyxl.load_workbook('mod_project/data_tables/vanilla_source_of_truth.xlsx', data_only=True)
ench_names = {}
if 'Enchantments' in wb.sheetnames:
    ws = wb['Enchantments']
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is not None:
            ench_names[r[0]] = r[1]

grand_seals = []
for name, data in arc.files:
    if len(data) >= 0x38:
        enemy_id, unk1 = struct.unpack('<II', data[0x00:0x08])
        kind = struct.unpack('<I', data[0x18:0x1C])[0]
        if kind == 1:
            ench_cnt = struct.unpack('<I', data[0x1C:0x20])[0]
            ench_ids = struct.unpack('<4i', data[0x20:0x30])
            lvl = struct.unpack('<I', data[0x34:0x38])[0]
            ename = all_enemies.get(enemy_id, f"Enemy {enemy_id}")
            eid = ench_ids[0]
            ename_str = ench_names.get(eid, f"Enchant {eid}")
            grand_seals.append((name, enemy_id, ename, ench_cnt, eid, ename_str, lvl))

print(f"Total Grand Sealbooks: {len(grand_seals)}")
for gs in sorted(grand_seals, key=lambda x: x[6]):
    print(f"Lvl {gs[6]:2d} | Enemy {gs[1]:3d} ({gs[2]:20s}) | Ench ID: {gs[4]:3d} ({gs[5]})")

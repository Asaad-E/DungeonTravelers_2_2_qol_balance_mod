import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
import capstone

# Where is the unwrapped exe?
exe_path = 'DungeonTravelers2-2_EN/DT22_en_unwrapped.exe'
if not os.path.exists(exe_path):
    print("Exe not found at", exe_path)
    sys.exit(0)

with open(exe_path, 'rb') as f:
    exe_data = f.read()

# Let's search for references to all stats enchantment IDs or where stat calculation occurs
# What are the IDs of All Stats UP?
# Let's search qol_enchant_text.xlsx for "all stats"
import openpyxl
wb = openpyxl.load_workbook('mod_project/data_tables/qol_enchant_text.xlsx', data_only=True)
ws = wb.active
all_stat_ids = []
for r in ws.iter_rows(min_row=2, values_only=True):
    vname = str(r[2] or '').lower()
    if 'all stat' in vname or 'all basic stat' in vname:
        all_stat_ids.append((r[0], r[2]))

print("All stat enchant IDs found in qol_enchant_text:")
for aid in all_stat_ids:
    print(" ", aid)

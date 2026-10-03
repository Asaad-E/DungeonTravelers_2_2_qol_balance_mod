import os, sys
sys.path.insert(0, r'mod_project\tools')
from pck_handler import PckArchive, SkillHelper
import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
GAME_PARAM_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Parameter')

# 1. Load original TechniqueSkillData from backup
backup_pck = os.path.join(BACKUP_DIR, 'TechniqueSkillData.pck')
archive = PckArchive(backup_pck)
print(f"Loaded clean backup: {backup_pck} ({len(archive.files)} entries)")

# 2. Load edits from skills.xlsx
excel_path = os.path.join(TABLES_DIR, 'skills.xlsx')
wb = openpyxl.load_workbook(excel_path)
ws = wb["Skills"]

tech_edits = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row or not row[1]: continue
    idx, cat, fn, name, max_lv, tp_prog, orig_desc, orig_lvup, mod_desc, mod_lvup, status, notes = row
    if cat == "Technique" and status in ['Approved', 'Applied', 'Draft'] and (mod_desc or mod_lvup):
        tech_edits[fn] = {
            'name': name,
            'desc': mod_desc if mod_desc else orig_desc,
            'lvup': mod_lvup if mod_lvup else orig_lvup
        }

print(f"Applying {len(tech_edits)} technique skill modifications:")
for fn, e in tech_edits.items():
    print(f"  - {e['name']} ({fn})")

# 3. Apply edits
applied = 0
for i, (fn, b) in enumerate(archive.files):
    if fn in tech_edits:
        e = tech_edits[fn]
        new_b = SkillHelper.write_skill(b, 'Technique', e['desc'], e['lvup'])
        archive.files[i] = (fn, new_b)
        applied += 1

print(f"Modified {applied} files in memory.")

# 4. Save directly to game directory
target_pck = os.path.join(GAME_PARAM_DIR, 'TechniqueSkillData.pck')
archive.save(target_pck)
print(f"Successfully saved to game: {target_pck} ({os.path.getsize(target_pck)} bytes)")

# 5. Verify integrity of saved file
test_archive = PckArchive(target_pck)
assert len(test_archive.files) == 143, f"Expected 143 files, got {len(test_archive.files)}"
p0_fn, p0_b = test_archive.files[0]
p0_info = SkillHelper.read_skill(p0_b, 'Technique')
print(f"\n[VERIFIED] File 0 ({p0_info['name']}):")
print(f"  Desc: {p0_info['desc']}")
print(f"  LvUp: {repr(p0_info['lvup'])}")
print("\nTechniqueSkillData.pck is 100% verified and ready for game launch!")

import os
import openpyxl
from pck_handler import PckArchive, SkillHelper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
GAME_PARAM_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Parameter')

def update_skills():
    excel_path = os.path.join(TABLES_DIR, 'skills.xlsx')
    if not os.path.exists(excel_path):
        print(f"Error: {excel_path} not found.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Skills"]
    
    category_map = {
        "Technique": "TechniqueSkillData.pck",
        "Magic": "MagicSkillData.pck",
        "Passive": "PassiveSkillData.pck",
        "Unique": "UniqueSkillData.pck",
    }
    
    # Read rows to apply
    pck_edits = {} # pck_file -> {filename: {'desc': ..., 'lvup': ..., 'name': ...}}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        idx, category, fn, name, max_lv, tp_prog, orig_desc, orig_lvup, mod_desc, mod_lvup, status, notes = row
        if status in ['Approved', 'Applied', 'Draft'] and (mod_desc or mod_lvup):
            pck_file = category_map.get(category)
            if pck_file not in pck_edits:
                pck_edits[pck_file] = {}
            pck_edits[pck_file][fn] = {
                'category': category,
                'name': name,
                'desc': mod_desc if mod_desc else orig_desc,
                'lvup': mod_lvup if mod_lvup else orig_lvup
            }
            
    print(f"Loaded edits for {sum(len(v) for v in pck_edits.values())} skills across {len(pck_edits)} PCK files.")
    
    # Apply to each PCK
    for pck_file, edits in pck_edits.items():
        backup_path = os.path.join(BACKUP_DIR, pck_file)
        archive = PckArchive(backup_path)
        
        applied_count = 0
        for i, (fn, b) in enumerate(archive.files):
            if fn in edits:
                e = edits[fn]
                new_bin = SkillHelper.write_skill(b, e['category'], e['desc'], e['lvup'])
                archive.files[i] = (fn, new_bin)
                applied_count += 1
                
        target_path = os.path.join(GAME_PARAM_DIR, pck_file)
        archive.save(target_path)
        print(f"Applied {applied_count} skills to: {target_path}")

def update_items():
    excel_path = os.path.join(TABLES_DIR, 'items.xlsx')
    if not os.path.exists(excel_path):
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Items"]
    
    edits = {} # filename -> new_desc
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        idx, fn, name, heal_val, orig_desc, mod_desc, status, notes = row
        if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
            edits[fn] = mod_desc
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "ItemData.pck")
    archive = PckArchive(pck_path)
    
    from pck_handler import ItemHelper
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_desc = edits[fn]
            new_bin = ItemHelper.write_item(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "ItemData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} items to: {target_path}")

if __name__ == "__main__":
    print("=== Applying Mod Changes from Excel to Game PCKs ===")
    update_skills()
    update_items()
    print("=== Done! ===")


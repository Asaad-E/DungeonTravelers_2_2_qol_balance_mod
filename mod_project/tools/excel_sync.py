import os
import struct
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pck_handler import PckArchive, SkillHelper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')

def export_skills_to_excel(excel_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Skills"
    
    headers = [
        "Index", "Category", "Filename", "Skill_Name", "Max_Level", 
        "TP_Progression", "Original_Desc", "Original_LvUp",
        "Modded_Desc", "Modded_LvUp", "Status", "Notes"
    ]
    ws.append(headers)
    
    # Styles
    hdr_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    hdr_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    for col_num, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    pck_configs = [
        ("TechniqueSkillData.pck", "Technique"),
        ("MagicSkillData.pck", "Magic"),
        ("PassiveSkillData.pck", "Passive"),
        ("UniqueSkillData.pck", "Unique"),
    ]
    
    row_idx = 2
    for pck_file, category in pck_configs:
        pck_path = os.path.join(BACKUP_DIR, pck_file)
        if not os.path.exists(pck_path):
            continue
            
        archive = PckArchive(pck_path)
        for i, (fn, b) in enumerate(archive.files):
            info = SkillHelper.read_skill(b, category)
            tp_str = " -> ".join(str(x) for x in info['tp_prog']) if info['tp_prog'] else "N/A"
            
            row = [
                i, category, fn, info['name'], info['max_lv'],
                tp_str, info['desc'], info['lvup'],
                "", "", "Vanilla", ""
            ]
            ws.append(row)
            row_idx += 1
            
    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 60)
        
    wb.save(excel_path)
    print(f"Exported {row_idx - 2} skills to {excel_path}")

def import_skills_from_excel(excel_path, target_dir):
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Skills"]
    
    # Group rows by category
    category_map = {
        "Technique": "TechniqueSkillData.pck",
        "Magic": "MagicSkillData.pck",
        "Passive": "PassiveSkillData.pck",
        "Unique": "UniqueSkillData.pck",
    }
    
    modified_data = {} # pck_file -> {filename: (new_desc, new_lvup, status)}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        idx, category, fn, name, max_lv, tp_prog, orig_desc, orig_lvup, mod_desc, mod_lvup, status, notes = row
        pck_file = category_map.get(category)
        if not pck_file:
            continue
        if pck_file not in modified_data:
            modified_data[pck_file] = {}
        modified_data[pck_file][fn] = {
            'category': category,
            'name': name,
            'desc': mod_desc if mod_desc else orig_desc,
            'lvup': mod_lvup if mod_lvup else orig_lvup,
            'status': status
        }
        
    # Rebuild PCKs
    for pck_file, entries in modified_data.items():
        backup_path = os.path.join(BACKUP_DIR, pck_file)
        archive = PckArchive(backup_path)
        
        mod_count = 0
        for i, (fn, b) in enumerate(archive.files):
            if fn in entries:
                entry = entries[fn]
                if entry['status'] in ['Approved', 'Applied', 'Draft']:
                    new_bin = SkillHelper.write_skill(b, entry['category'], entry['desc'], entry['lvup'])
                    archive.files[i] = (fn, new_bin)
                    mod_count += 1
                    
        out_path = os.path.join(target_dir, pck_file)
        archive.save(out_path)
        print(f"Updated {pck_file} with {mod_count} modified skills -> {out_path}")

if __name__ == "__main__":
    skills_excel = os.path.join(TABLES_DIR, "skills.xlsx")
    export_skills_to_excel(skills_excel)


def export_items_to_excel(excel_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Items"
    
    headers = [
        "Index", "Filename", "Item_Name", "HP_Heal_Val", 
        "Original_Desc", "Modded_Desc", "Status", "Notes"
    ]
    ws.append(headers)
    
    hdr_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    hdr_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    for col_num, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    pck_path = os.path.join(BACKUP_DIR, "ItemData.pck")
    archive = PckArchive(pck_path)
    
    row_idx = 2
    for i, (fn, b) in enumerate(archive.files):
        p0, p1 = struct.unpack('<2Q', b[8:24])
        name = b[p0:b.find(b'\x00', p0)].decode('latin-1')
        desc = b[p1:b.find(b'\x00', p1)].decode('latin-1')
        
        # Check float heal value at 0x28
        heal_val = ""
        f_val = struct.unpack('<f', b[0x28:0x2c])[0]
        if 1.0 <= f_val <= 9999.0 and not f_val.is_integer() == False:
            heal_val = f"{int(f_val)} HP"
            
        row = [i, fn, name, heal_val, desc, "", "Vanilla", ""]
        ws.append(row)
        row_idx += 1
        
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 60)
        
    wb.save(excel_path)
    print(f"Exported {row_idx - 2} items to {excel_path}")

def export_equipment_to_excel(excel_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Equipment"
    
    headers = [
        "Index", "Filename", "Equip_Name", "Equip_Type",
        "Original_Desc", "Modded_Desc", "Status", "Notes"
    ]
    ws.append(headers)
    
    hdr_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    hdr_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    for col_num, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    pck_path = os.path.join(BACKUP_DIR, "EquipmentData.pck")
    archive = PckArchive(pck_path)
    
    row_idx = 2
    for i, (fn, b) in enumerate(archive.files):
        p0, p1 = struct.unpack('<2Q', b[8:24])
        name = b[p0:b.find(b'\x00', p0)].decode('latin-1')
        desc = b[p1:b.find(b'\x00', p1)].decode('latin-1')
        
        # Estimate type by index range
        eq_type = "Weapon"
        if 350 <= i < 365: eq_type = "Shield"
        elif 365 <= i < 415: eq_type = "Headgear"
        elif 415 <= i < 460: eq_type = "Armor"
        elif i >= 460: eq_type = "Accessory"
        
        row = [i, fn, name, eq_type, desc, "", "Vanilla", ""]
        ws.append(row)
        row_idx += 1
        
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 60)
        
    wb.save(excel_path)
    print(f"Exported {row_idx - 2} equipment entries to {excel_path}")

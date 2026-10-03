import os
import openpyxl
from pck_handler import PckArchive, PartySkillHelper, FoodMenuHelper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

def populate_party_skills():
    print("=== Populating party_skills.xlsx ===")
    arc = PckArchive(os.path.join(BACKUP_DIR, 'PartySkillData.pck'))
    
    PARTY_SKILL_EFFECTS = {
        'PartySkillData_0382.bin': 'Max HP +100.',
        'PartySkillData_0383.bin': 'ATK +32.',
        'PartySkillData_0384.bin': 'Max TP +50, Fire Res +20.',
        'PartySkillData_0385.bin': 'Slash Res +25.',
        'PartySkillData_0386.bin': 'INT +20.',
        'PartySkillData_0387.bin': 'DEF +25.',
        'PartySkillData_0388.bin': 'AGI +20.',
        'PartySkillData_0389.bin': 'Stab Res +20.',
        'PartySkillData_0390.bin': 'Max HP +50, Max TP +50.',
        'PartySkillData_0391.bin': 'RES +20.',
        'PartySkillData_0392.bin': 'Bash Res +20.',
        'PartySkillData_0393.bin': 'DEX +20.',
        'PartySkillData_0394.bin': 'Water Res +20, Earth Res +20.',
        'PartySkillData_0395.bin': 'Lightning Res +50.',
        'PartySkillData_0396.bin': 'Wind Res +20, AGI +20.',
        'PartySkillData_0397.bin': 'Bash Res +10, Earth Res +20.',
        'PartySkillData_0398.bin': 'Lightning Res +20, Max HP +100.',
        'PartySkillData_0399.bin': 'Fire Res +10, ATK +20.',
        'PartySkillData_0400.bin': 'DEX +20, AGI +20.',
        'PartySkillData_0401.bin': 'Max TP +50, Fire Res +20.',
    }
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "PartySkills"
    ws.append(["Filename", "Name", "Requirement", "Vanilla_Effect", "Modded_Effect", "Status"])
    
    for fn, data in arc.files:
        info = PartySkillHelper.read_party_skill(data)
        mod_eff = PARTY_SKILL_EFFECTS.get(fn, info['effect'])
        ws.append([fn, info['name'], info['req'], info['effect'], mod_eff, "Approved"])
        
    out_path = os.path.join(TABLES_DIR, 'party_skills.xlsx')
    wb.save(out_path)
    print(f"Saved {len(arc.files)} party skills to {out_path}!")

def populate_food_menu():
    print("=== Populating food_menu.xlsx ===")
    arc = PckArchive(os.path.join(BACKUP_DIR, 'FoodMenuData.pck'))
    
    FOOD_MENU_EFFECTS = {
        'FoodMenuData_0000.bin': 'Restore 20% HP.',
        'FoodMenuData_0001.bin': 'Restore 10% HP. Cure status ailments.',
        'FoodMenuData_0002.bin': 'Restore 30% HP and 20% TP.',
        'FoodMenuData_0003.bin': 'Restore 50% HP. Cure ailments + Sun Veil.',
        'FoodMenuData_0004.bin': 'Restore 50% HP and 40% TP. Cure ailments + Water Enchant.',
        'FoodMenuData_0005.bin': 'Restore 100% TP + Divine Shield.',
        'FoodMenuData_0006.bin': 'Restore 80% HP and TP. Cure ailments + Aim.',
        'FoodMenuData_0007.bin': 'Restore 100% HP and TP + Protect and Accelerator.',
        'FoodMenuData_0008.bin': 'Restore 20% TP.',
        'FoodMenuData_0009.bin': 'Restore 30% TP + Fire Enchant.',
        'FoodMenuData_0010.bin': 'Instantly escape from the dungeon back to base.',
        'FoodMenuData_0011.bin': 'Restore 40% TP. Cure ailments + Light.',
        'FoodMenuData_0012.bin': 'Restore 60% HP and TP. Cure ailments + Brave.',
        'FoodMenuData_0013.bin': 'Restore 100% HP + Protect and Fleet Foot.',
        'FoodMenuData_0014.bin': 'Restore 80% HP and TP + Stab/Slash/Bash Guard.',
        'FoodMenuData_0015.bin': 'Restore 100% HP and TP. Cure ailments + Insurance.',
    }
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "FoodMenu"
    ws.append(["Filename", "Name", "Flavor_Text", "Vanilla_Effect", "Modded_Effect", "Status"])
    
    for fn, data in arc.files:
        info = FoodMenuHelper.read_food_menu(data)
        mod_eff = FOOD_MENU_EFFECTS.get(fn, info['effect'])
        ws.append([fn, info['name'], info['flavor'], info['effect'], mod_eff, "Approved"])
        
    out_path = os.path.join(TABLES_DIR, 'food_menu.xlsx')
    wb.save(out_path)
    print(f"Saved {len(arc.files)} food menu items to {out_path}!")

if __name__ == '__main__':
    populate_party_skills()
    populate_food_menu()

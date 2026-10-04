import os
import openpyxl
from pck_handler import (
    PckArchive, 
    SkillHelper, 
    ItemHelper, 
    SealScrollHelper, 
    JoinSkillHelper,
    EnchantHelper,
    PartySkillHelper,
    FoodMenuHelper,
    EnemyAttackHelper,
    ClassDataHelper,
    StringDataHelper
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
GAME_PARAM_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Parameter')
GAME_SCRIPT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')

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
    
    edits = {}
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

def update_grand_seals():
    excel_path = os.path.join(TABLES_DIR, 'grand_seals.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Grand Seals.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["GrandSeals"]
    
    edits = {} # fn -> mod_desc
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, seal_name, boss_name, vanilla_desc, mod_desc, status = row[:6]
        if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
            edits[fn] = mod_desc
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "SealScrollData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_desc = edits[fn]
            new_bin = SealScrollHelper.write_seal(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "SealScrollData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Grand Sealbooks to: {target_path}")

def update_joint_skills():
    excel_path = os.path.join(TABLES_DIR, 'joint_skills.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Joint Skills.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["JointSkills"]
    
    edits = {} # fn -> mod_desc
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, skill_name, vanilla_desc, mod_desc, status = row[:5]
        if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
            edits[fn] = mod_desc
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "JoinSkillData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_desc = edits[fn]
            new_bin = JoinSkillHelper.write_joint(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "JoinSkillData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Joint Skills to: {target_path}")

def update_teaching_script(bin_data, replacements):
    new_data = bytearray(bin_data)
    for orig_str, new_str in replacements.items():
        orig_bytes = orig_str.encode('ascii') + b'\x00'
        new_bytes = new_str.encode('ascii') + b'\x00'
        idx = new_data.find(orig_bytes)
        if idx == -1:
            continue
        new_data = new_data[:idx] + new_bytes + new_data[idx + len(orig_bytes):]
    return bytes(new_data)

def update_teaching():
    pck_path = os.path.join(BACKUP_DIR, "Teaching.pck")
    if not os.path.exists(pck_path):
        print(f"Notice: Backup {pck_path} not found, skipping Teaching.")
        return
        
    archive = PckArchive(pck_path)
    
    replacements_18 = {
        "If the character has passed certain level thresholds,\nthen it is possible to restore to those thresholds rather\nthan to level 1.": (
            "Thresholds are Lv 1, 15, 30, and 50. Bonus stats require a\n"
            "level gap of >=59 (e.g. Lv 60->1, Lv 90->30) to increase\n"
            "permanent base attributes (+1 to all stats and resists)."
        )
    }

    replacements_20 = {
        "Elemental Zones: Enhance one element: Fire, Water,\nWind, Earth, or Lightning. Increase all damage of that\nelemental type considerably.": (
            "Elemental Zones: +50% damage dealt to favored element,\n"
            "-50% to opposed element (Fire/Water, Earth/Wind, Lightning).\n"
            "Applies to both party and monsters."
        ),
        "Boost Zones: There are Attack, Magic, Armor, and Magic\nResist Zones. They enhance Physical Attack, Magic Attack,\nPhysical Defense, and Magic Defense respectively.": (
            "Boost Zones: Attack, Magic, Armor, and Magic Resist Zones\n"
            "increase Physical ATK, Magic ATK, Physical DEF, and\n"
            "Magic DEF by +25% respectively."
        )
    }

    replacements_25 = {
        "Resetting with an even greater level gap can provide even\ngreater stat increases.": (
            "Stat thresholds: Gap >=59 grants +1 to all stats and resists.\n"
            "Each additional 10 Lv gap (>=69, >=79, >=89, >=99) adds +1\n"
            "cumulative bonus point per attribute."
        ),
        "This will raise your unique skill to Level EX,\ngreatly heightening its effects.": (
            "This raises your unique skill to Level EX (+50% bonus\n"
            "over Lv 9) and unlocks the maximum base attribute cap."
        )
    }

    replacements_09 = {
        "Weapon speed ranks range from A, which is the fastest, to F,\nwhich is the slowest.": (
            "Weapon ranks: A (1.0x delay) to F (1.5x delay). Defending/Guarding\n"
            "reduces delay to 0.67x (50% faster turn recovery)."
        )
    }

    replacements_11 = {
        "While it is possible to attack over long range with a\nshort-range weapon, the damage will be considerably lessened\nas a result.": (
            "Short-range weapons suffer a -50% damage penalty when\n"
            "attacking beyond Front-to-Front. Mid and Long weapons have no penalty."
        )
    }

    replacements_12 = {
        "Also renders you unable to dodge attacks, and incoming\ndamage increases significantly.": (
            "Physical damage received while asleep is multiplied by 1.5x.\n"
            "Wakes up immediately upon receiving a physical attack."
        )
    }

    replacements_16 = {
        "Party skills grow stronger the more Awards you obtain.": (
            "Party skills gain +1% bonus efficacy for every 5 Awards earned."
        )
    }

    replacements_17 = {
        "2. Each participating member needs to have enough TP to\nperform the joint skill.": (
            "2. Each participating member consumes 10% to 25% of their\n"
            "maximum TP, and requires sufficient Pep (30 to 50)."
        )
    }
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn == 'CheatsTeaching_18.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_18))
            applied_count += 1
        elif fn == 'CheatsTeaching_20.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_20))
            applied_count += 1
        elif fn == 'CheatsTeaching_25.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_25))
            applied_count += 1
        elif fn == 'CheatsTeaching_09.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_09))
            applied_count += 1
        elif fn == 'CheatsTeaching_11.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_11))
            applied_count += 1
        elif fn == 'CheatsTeaching_12.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_12))
            applied_count += 1
        elif fn == 'CheatsTeaching_16.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_16))
            applied_count += 1
        elif fn == 'CheatsTeaching_17.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_17))
            applied_count += 1

    target_path = os.path.join(GAME_SCRIPT_DIR, "Teaching.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} ADV tutorial scripts to: {target_path}")

def update_enchants():
    excel_path = os.path.join(TABLES_DIR, 'enchants.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Enchants.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Enchants"] if "Enchants" in wb.sheetnames else wb.active
    
    edits = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, van_name, prefix, suffix, mod_name, status = row[:6]
        if status in ['Approved', 'Applied', 'Draft'] and mod_name:
            edits[fn] = mod_name
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "EnchantData.pck")
    archive = PckArchive(pck_path)
    
    from pck_handler import EnchantHelper
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_name = edits[fn]
            new_bin = EnchantHelper.write_enchant(b, new_name)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "EnchantData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Enchant enhancements to: {target_path}")

def update_party_skills():
    excel_path = os.path.join(TABLES_DIR, 'party_skills.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Party Skills.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["PartySkills"]
    
    edits = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, name, req, van_eff, mod_eff, status = row[:6]
        if status in ['Approved', 'Applied', 'Draft'] and mod_eff:
            edits[fn] = mod_eff
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "PartySkillData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_eff = edits[fn]
            new_bin = PartySkillHelper.write_party_skill(b, new_eff)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "PartySkillData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Party Skills to: {target_path}")

def update_food_menu():
    excel_path = os.path.join(TABLES_DIR, 'food_menu.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Food Menu.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["FoodMenu"]
    
    edits = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, name, flavor, van_eff, mod_eff, status = row[:6]
        if status in ['Approved', 'Applied', 'Draft'] and mod_eff:
            edits[fn] = mod_eff
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "FoodMenuData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_eff = edits[fn]
            new_bin = FoodMenuHelper.write_food_menu(b, new_eff)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "FoodMenuData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Food Menu items to: {target_path}")

def update_lessons():
    pck_path = os.path.join(BACKUP_DIR, "Lesson.pck")
    if not os.path.exists(pck_path):
        print(f"Notice: Backup {pck_path} not found, skipping Lessons.")
        return
        
    archive = PckArchive(pck_path)
    
    replacements_10 = {
        "Party skills also grow stronger according to the number of\nawards you amass.": (
            "Party skills scale up to +100% bonus according to the\n"
            "number of awards you amass (maxed out at 50 awards)."
        ),
        "I would if I could, but I don't even know what half of them\ndo. You sure I shouldn't just stick to my regular skills?": (
            "Check the Joint Skill menu: each skill now lists exact\n"
            "party requirements, Pep costs, and formula breakdown."
        )
    }

    replacements_11 = {
        "Or, after certain level thresholds, you can choose to reset\nback to those specific threshold levels as opposed to level\n1.": (
            "Thresholds are Lv 1, 15, 30, and 50. Resetting with a\n"
            "level gap of >=59 grants permanent stats and resists!"
        )
    }

    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn == 'BattleTeacher_10.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_10))
            applied_count += 1
        elif fn == 'BattleTeacher_11-12.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_11))
            applied_count += 1

    target_path = os.path.join(GAME_SCRIPT_DIR, "Lesson.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} BattleTeacher lecture scripts to: {target_path}")

def update_enemy_attacks():
    excel_path = os.path.join(TABLES_DIR, 'enemy_attacks.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Enemy/Summon Attacks.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["EnemyAttacks"]
    
    edits = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, sk_id, name, h_line, van_desc, mod_desc, is_summon, status = row[:8]
        if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
            edits[fn] = mod_desc
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "EnemyAttackData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_desc = edits[fn]
            new_bin = EnemyAttackHelper.write_enemy_attack(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "EnemyAttackData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Summon/Monster Attacks to: {target_path}")

def update_classes():
    excel_path = os.path.join(TABLES_DIR, 'classes.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Classes.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Classes"] if "Classes" in wb.sheetnames else wb.active
    
    edits = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, code, name, van_desc, mod_desc, status = row[:6]
        if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
            edits[fn] = mod_desc
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "ClassData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_desc = edits[fn]
            new_bin = ClassDataHelper.write_class(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "ClassData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Class overhauls to: {target_path}")

def update_ui_strings():
    excel_path = os.path.join(TABLES_DIR, 'ui_strings.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping UI Strings.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["UIStrings"] if "UIStrings" in wb.sheetnames else wb.active
    
    edits = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        fn, sid, van_text, mod_text, status = row[:5]
        if status in ['Approved', 'Applied', 'Draft'] and mod_text:
            edits[fn] = mod_text
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "StringData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_text = edits[fn]
            new_bin = StringDataHelper.write_string(b, new_text)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "StringData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} UI string improvements to: {target_path}")

if __name__ == "__main__":
    print("=== Applying Comprehensive Mod Suite to Game PCKs ===")
    update_skills()
    update_items()
    update_grand_seals()
    update_joint_skills()
    update_teaching()
    update_enchants()
    update_party_skills()
    update_food_menu()
    update_lessons()
    update_enemy_attacks()
    update_classes()
    update_ui_strings()
    print("=== Complete Mod Execution Finished Successfully! ===")




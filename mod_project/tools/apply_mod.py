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
    StringDataHelper,
    EquipmentHelper,
    TrapHelper,
    TrophyHelper
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
            if fn == 'ItemData_0020.bin':
                # Quality of Life: Expand Flashlight duration from 10 to 30 steps!
                import struct
                b_mod = bytearray(b)
                struct.pack_into('<f', b_mod, 40, 30.0)
                b = bytes(b_mod)
            new_bin = ItemHelper.write_item(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "ItemData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} items to: {target_path}")

def update_equipment():
    excel_path = os.path.join(TABLES_DIR, 'equipment.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Equipment.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Equipment"]
    
    edits = {} # fn -> mod_desc
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        idx, fn, name, eq_type, orig_desc, mod_desc, status = row[:7]
        if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
            edits[fn] = mod_desc
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "EquipmentData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_desc = edits[fn]
            if fn == 'EquipmentData_0744.bin':
                # Slave's Torc training gear: Replace duplicate enchant 66 at 0x68 with 275 (Double EXP)
                b_copy = bytearray(b)
                import struct
                struct.pack_into('<I', b_copy, 0x68, 275)
                b = bytes(b_copy)
            new_bin = EquipmentHelper.write_equipment(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "EquipmentData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} equipment items to: {target_path}")

def update_weapon_ranks():
    pck_path = os.path.join(BACKUP_DIR, "WeaponRankData.pck")
    if not os.path.exists(pck_path):
        print(f"Notice: {pck_path} not found, skipping Weapon Ranks.")
        return
        
    archive = PckArchive(pck_path)
    # Balanced compressed delay floats:
    # A+ 1.00, A 1.15, B+ 1.30, B 1.45, C+ 1.60, C 1.75, D+ 1.85, D 1.95, E+ 2.05, E 2.15, F+ 2.25, F 2.35
    balanced_mults = [1.00, 1.15, 1.30, 1.45, 1.60, 1.75, 1.85, 1.95, 2.05, 2.15, 2.25, 2.35]
    
    import struct
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if i < len(balanced_mults):
            b_new = bytearray(b)
            struct.pack_into('<f', b_new, 0x10, balanced_mults[i])
            archive.files[i] = (fn, bytes(b_new))
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "WeaponRankData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Weapon Rank delay adjustments to: {target_path}")

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
    
    # CheatsTeaching_01 (Turn Order & Delay Tiers)
    replacements_01 = {
        "Turn order is a fundamental aspect of combat, so be sure to\ncheck it often and strategize efficiently.": (
            "Turn delay falls into three tiers: Agile (A+ 1.0x to A 1.15x),\n"
            "Balanced (B to C+ 1.30-1.75x), and Colossal (D to F 1.85-2.35x).\n"
            "Use Defend (0.67x delay) to quickly recover your turn order!"
        )
    }

    # CheatsTeaching_02 (Learning Skills)
    replacements_02 = {
        "Please note that although skills grow more powerful at\nhigher levels, their TP cost and chanting time may also\nincrease, which can make them more difficult to use.": (
            "Higher skill levels increase TP cost and chant delay. Balance\n"
            "sweet spots: Level 1-4 for cheap sustainable loops, Level 5+\n"
            "for burst damage. Reallocate SP freely via Base Level Reset!"
        )
    }

    # CheatsTeaching_03 (Skill Types and Effects)
    replacements_03 = {
        "Techniques and magic are skills that you choose when to\nactivate, whereas passive skills take effect automatically,\nand do not need to be selected.": (
            "Techniques hit instantly but add recovery delay. Spells require\n"
            "chanting time but recover faster. Songs and Dances apply passive\n"
            "auras, while Dolls act as autonomous allies on their own turns."
        )
    }

    # CheatsTeaching_04 (Libras & Monster Sealing)
    replacements_04 = {
        "Each Sealbook offers different enchantments, so make plenty\nand use them to strengthen your party.": (
            "Crafting a Sealbook permanently unlocks monster Level, HP, and\n"
            "Resistances in battle! Equip Sealbooks for stats or forge them\n"
            "onto weapons at Blacksmith (+1 to +9) to inherit enchants."
        )
    }

    # CheatsTeaching_05 (Grand Sealbooks)
    replacements_05 = {
        "They offer a wide range of effects, so you should try each\nGrand Sealbook out as soon as you get it.": (
            "Mutant bosses drop Grand Sealbooks with 100% guarantee.\n"
            "Equipping one provides powerful passive auras that boost the\n"
            "entire party, plus summons the mutant as an autonomous ally!"
        )
    }

    # CheatsTeaching_06 (Sealbook Summons)
    replacements_06 = {
        "The effect can vary depending on the monster. For instance,\na mutant skilled at physical attacks will have her ATK stat\nmost easily influenced by the party.": (
            "Summon stats scale with party averages (level, ATK, INT).\n"
            "Summons act on their own turns and cannot be commanded.\n"
            "Note: Party-wide heals and buffs do NOT affect summons."
        )
    }

    # CheatsTeaching_07 (Scanning and Checking Stats)
    replacements_07 = {
        "More details will be visible in the Stats menu for monsters\nwhose Sealbooks you have created before.": (
            "Press <BUTTON_L> to inspect monsters. Creating their Sealbook\n"
            "permanently reveals Max HP, ATK, DEF, and all 5 elemental\n"
            "resistances, allowing you to exploit their vulnerabilities!"
        )
    }

    # CheatsTeaching_08 (Battle Log & Combat Telemetry)
    replacements_08 = {
        "If you missed something that happened, you can refer to the\nbattle log to see who did what during battle.": (
            "The log reveals hidden combat telemetry: Covered Chant procs,\n"
            "exact status resistance checks, boss Enrage phase triggers,\n"
            "and turn delay immunities. Review it to refine your tactics!"
        )
    }

    # CheatsTeaching_09 (Weapon Speed Ranks) - Exact from WeaponRankData.pck!
    replacements_09 = {
        "Weapon speed ranks range from A, which is the fastest, to F,\nwhich is the slowest.": (
            "Delay ranks: A+ (1.00x), A (1.15x), B+ (1.30x), B (1.45x), C+ (1.60x),\n"
            "C (1.75x), D (1.95x), E (2.15x), F (2.35x delay)! Heavy delay capped\n"
            "at 2.35x. Guarding cuts recovery delay down to 0.67x."
        )
    }

    # CheatsTeaching_10 (Techniques and Magic)
    replacements_10 = {
        "Critical hits, however, have a fixed 1/3 chance of\ninterrupting, regardless of the amount of damage inflicted.": (
            "Chant interrupt chance scales with damage taken vs Max HP.\n"
            "Crucially, ANY Critical Hit has a flat 33.3% interrupt chance!\n"
            "Use high-crit skills or multihits to reliably stop enemy spells."
        )
    }

    # CheatsTeaching_11 (Range and Distance)
    replacements_11 = {
        "While it is possible to attack over long range with a\nshort-range weapon, the damage will be considerably lessened\nas a result.": (
            "Short-range (SR) suffers -50% damage beyond Front-to-Front.\n"
            "Mid-range (Lances/Whips) hits adjacent rows with 0% penalty.\n"
            "Long-range (Bows/Guns/Magic) hits any row at 100% full damage."
        )
    }

    # CheatsTeaching_12 (Status Ailments)
    replacements_12 = {
        "Also renders you unable to dodge attacks, and incoming\ndamage increases significantly.": (
            "Physical damage received while asleep is multiplied by 1.5x.\n"
            "Wakes up immediately upon receiving a physical attack."
        )
    }

    # CheatsTeaching_13 (Status Ailments and Resistances)
    replacements_13 = {
        "If you have 100 resistance to a certain element, you will be\ncompletely immune to its corresponding status ailments.": (
            "Resistances cut damage by 0.5% per point (100 res = 50% cut,\n"
            "200 res = 100% cut). At 100 resistance to an element, you are\n"
            "completely 100% IMMUNE to all of its corresponding ailments!"
        )
    }

    # CheatsTeaching_14 (The Quest Desk)
    replacements_14 = {
        "Complete enough quests to increase your rank, and you will\nalso receive a present.": (
            "Increasing Quest Rank unlocks rare shop items, high-tier gear,\n"
            "and powerful Mercenaries (such as Miranda at Rank 12).\n"
            "Check and complete recommended quests frequently!"
        )
    }

    # CheatsTeaching_15 (Unique Skills)
    replacements_15 = {
        "Instead, they level up by themselves every 10 levels.": (
            "Unique skills auto-level every 10 levels (max Lv 9 at Lv 90).\n"
            "Achieving a Crown elevates Unique Skills to Level EX (+50% bonus),\n"
            "which stays permanently locked even after resetting to Level 1!"
        )
    }

    # CheatsTeaching_16 (Party Skills)
    replacements_16 = {
        "Party skills grow stronger the more Awards you obtain.": (
            "Party skills gain +1% bonus efficacy for every 5 Awards earned."
        )
    }

    # CheatsTeaching_17 (Joint Skills)
    replacements_17 = {
        "2. Each participating member needs to have enough TP to\nperform the joint skill.": (
            "2. Each participating member consumes 10% to 25% of their\n"
            "maximum TP, and requires sufficient Pep (30 to 50)."
        )
    }

    # CheatsTeaching_18 (Level Resetting)
    replacements_18 = {
        "If the character has passed certain level thresholds,\nthen it is possible to restore to those thresholds rather\nthan to level 1.": (
            "Thresholds are Lv 1, 15, 30, and 50. Bonus stats require a\n"
            "level gap of >=59 (e.g. Lv 60->1, Lv 90->30) to increase\n"
            "permanent base attributes (+1 to all stats and resists)."
        )
    }

    # CheatsTeaching_19 (Experience Points)
    replacements_19 = {
        "If you defeat a group of monsters with a single party\nmember, she will gain all the EXP herself, but with a party\nof five, the experience gets split five ways.": (
            "Battle EXP splits equally among living members (5-man = 20% each).\n"
            "Higher-level monsters grant up to 3.0x bonus EXP! Solo or duo\n"
            "runs with a high-tier carry are the fastest way to re-level."
        ),
        "With these things in mind, you might be able to quickly\nbring characters whose levels you have reset back up to\ntheir former strength.": (
            "Equip Slave's Torc (Double EXP) and Grand Seal Dragon Papi\n"
            "(+50% Higher-Level EXP) to power-level under the smoothed\n"
            "-35% Lv 71-99 curve, earning bonus SP in early levels!"
        )
    }

    # CheatsTeaching_20 (Dungeon Zones & Traps) - Exact from TrapData.pck!
    replacements_20 = {
        "Elemental Zones: Enhance one element: Fire, Water,\nWind, Earth, or Lightning. Increase all damage of that\nelemental type considerably.": (
            "Elemental Zones: +50% damage dealt to favored element,\n"
            "-50% to opposed element (Fire/Water, Earth/Wind, Lightning).\n"
            "Boost Zones grant +25% to ATK, M.ATK, DEF, or M.DEF."
        ),
        "Boost Zones: There are Attack, Magic, Armor, and Magic\nResist Zones. They enhance Physical Attack, Magic Attack,\nPhysical Defense, and Magic Defense respectively.": (
            "Dungeon Traps: Damage Floor/Mine: 25% HP; Gas: 33% status;\n"
            "Petrification Gas: 50% party; Dispel Floor: 100% buff wipe;\n"
            "Killer Floor: 25% death check (blocked by 100 Earth Resist!)."
        )
    }

    # CheatsTeaching_21 (Mercenary Buddies)
    replacements_21 = {
        "2. They have a contract period. Once they have fought the\nnumber of battles indicated when hiring, they will leave,\nno matter where you are.": (
            "2. Contract battles tick down ONLY on battle victories (fleeing\n"
            "and boss battles do NOT consume contract battles).\n"
            "3. Mercenaries gain permanent level-ups upon beating key bosses!"
        )
    }

    # CheatsTeaching_23 (Strong Enemies / Mutant Enrage)
    replacements_23 = {
        "There are also some monsters that use different skills after\ntaking a certain amount of damage.": (
            "Mutant bosses enter an Enrage Phase at <50% and <25% HP,\n"
            "unleashing devastating party wipes or full heals.\n"
            "Save high-damage Joint Skills and bursts for execution!"
        )
    }

    # CheatsTeaching_24 (Skill Synergy)
    replacements_24 = {
        "Some skills may have powerful synergies with equipment\nenchantments as well. Keep an eye on your arsenal for new\nopportunities.": (
            "Synergy: Critical skills (Sharp Stab) guarantee 33% interrupts.\n"
            "Adaptation + Moon Curtain grants total status immunity.\n"
            "Forge Sealbooks onto weapons to stack complementary enchants!"
        )
    }

    # CheatsTeaching_25 (Crowns)
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

    teaching_map = {
        'CheatsTeaching_01.adv.bin': replacements_01,
        'CheatsTeaching_02.adv.bin': replacements_02,
        'CheatsTeaching_03.adv.bin': replacements_03,
        'CheatsTeaching_04.adv.bin': replacements_04,
        'CheatsTeaching_05.adv.bin': replacements_05,
        'CheatsTeaching_06.adv.bin': replacements_06,
        'CheatsTeaching_07.adv.bin': replacements_07,
        'CheatsTeaching_08.adv.bin': replacements_08,
        'CheatsTeaching_09.adv.bin': replacements_09,
        'CheatsTeaching_10.adv.bin': replacements_10,
        'CheatsTeaching_11.adv.bin': replacements_11,
        'CheatsTeaching_12.adv.bin': replacements_12,
        'CheatsTeaching_13.adv.bin': replacements_13,
        'CheatsTeaching_14.adv.bin': replacements_14,
        'CheatsTeaching_15.adv.bin': replacements_15,
        'CheatsTeaching_16.adv.bin': replacements_16,
        'CheatsTeaching_17.adv.bin': replacements_17,
        'CheatsTeaching_18.adv.bin': replacements_18,
        'CheatsTeaching_19.adv.bin': replacements_19,
        'CheatsTeaching_20.adv.bin': replacements_20,
        'CheatsTeaching_21.adv.bin': replacements_21,
        'CheatsTeaching_23.adv.bin': replacements_23,
        'CheatsTeaching_24.adv.bin': replacements_24,
        'CheatsTeaching_25.adv.bin': replacements_25,
    }

    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in teaching_map:
            archive.files[i] = (fn, update_teaching_script(b, teaching_map[fn]))
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
    
    replacements_04 = {
        "This information is extremely important during battle, so I\nhighly suggest that you make use of it when battling against\nthreatening enemies.": (
            "This information is crucial. Remember: heavy weapons like 2H swords\n"
            "and rifles have delayed turns (capped at 2.35x delay in Rank F)!\n"
            "Weave in Defend (0.67x delay) to recover your turn order quickly."
        )
    }

    replacements_07 = {
        "Well, that was something of a brief lesson, but let's leave\nit here for today.": (
            "Remember: mid-range spears and whips ignore penalties from back row,\n"
            "while bows and magic strike across all rows at 100% full power!\n"
            "Position your allies carefully, Fried, or expect extra homework."
        )
    }

    replacements_08 = {
        "Precisely. Against certain monsters, raising your\nresistances can be considerably more effective than raising\nyour defense directly.": (
            "Precisely! Stacking 100 resistance also cuts elemental damage by 50%.\n"
            "Pair this with Paladin's 60% Cover or Dark Lord's HP leeching,\n"
            "and your front line will hold fast even against divine spells."
        )
    }

    replacements_09 = {
        "Presents include gold, rare equipment, and even additional\nbag space.": (
            "Bag space expands by +10 at Ranks 2 and 8, reaching the 50-slot\n"
            "maximum early! Rank 16 unlocks The Matrix, and underleveled allies\n"
            "gain +100% catch-up EXP to power-level smoothly."
        )
    }

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
        ),
        "\"So even though level resetting will lower a character's\nlevel, it won't be long before she catches up to the rest of\nthe party as you go about your adventures.\"": (
            "\"Equip the Slave's Torc training gear (Double EXP) and summon\n"
            "Dragon Papi (+50% higher-level EXP) to catch up smoothly\n"
            "under our rebalanced -35% Lv 71-99 Crown leveling curve!\""
        )
    }

    replacements_13 = {
        "Is that right...? There aren't many restaurants around these\nparts, so I've been frequenting it quite often.": (
            "I visit often! Always eat before exploring: food buffs last 900 steps,\n"
            "and top ramen bowls grant +10% all stats and elemental guards that\n"
            "persist across entire floors without being wiped by Dispel traps."
        )
    }

    replacements_sp01 = {
        "\"Abandon hope and make peace with your fate.\"": (
            "\"Survive superboss wipes by stacking 100+ Elemental Resistance\n"
            "(which cuts damage by 50% and grants 100% ailment immunity!),\n"
            "or use Valkyrie's Circle Protection to nullify physical wipes.\""
        )
    }

    replacements_sp02 = {
        "Dark Aura debuffs enemies' stats when they inflict\nshort-range damage. No monsters are immune to such debuffs,\nso you can even use it in boss battles.": (
            "Dark Aura debuffs on contact. When bosses enter Enrage at <25% HP,\n"
            "remember Tinker Squash has diminishing returns, so coordinate your\n"
            "Joint Skills to execute them swiftly before they overwhelm you!"
        )
    }

    replacements_sp03 = {
        "\"There's no real necessity to seek so much power... but if it\nstrikes your fancy, why not shoot for the Crown?\"": (
            "\"A Crown locks your Unique Skill at Level EX (+50% bonus) forever!\n"
            "Reset with a gap of >=59 (Lv 60->1, 90->30) to earn +1 all stats,\n"
            "plus cumulative bonus points at gap thresholds 69, 79, 89, and 99.\""
        )
    }

    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn == 'BattleTeacher_04.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_04))
            applied_count += 1
        elif fn == 'BattleTeacher_07.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_07))
            applied_count += 1
        elif fn == 'BattleTeacher_08.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_08))
            applied_count += 1
        elif fn == 'BattleTeacher_09.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_09))
            applied_count += 1
        elif fn == 'BattleTeacher_10.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_10))
            applied_count += 1
        elif fn == 'BattleTeacher_11-12.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_11))
            applied_count += 1
        elif fn == 'BattleTeacher_13.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_13))
            applied_count += 1
        elif fn == 'BattleTeacher_Sp01.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_sp01))
            applied_count += 1
        elif fn == 'BattleTeacher_Sp02.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_sp02))
            applied_count += 1
        elif fn == 'BattleTeacher_Sp03.adv.bin':
            archive.files[i] = (fn, update_teaching_script(b, replacements_sp03))
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

def update_traps():
    excel_path = os.path.join(TABLES_DIR, 'traps.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Traps.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Traps"]
    
    edits = {} # fn -> mod_name
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        idx, fn, tid, van_name, mod_name, status = row[:6]
        if status in ['Approved', 'Applied', 'Draft'] and mod_name:
            edits[fn] = mod_name
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "TrapData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_name = edits[fn]
            new_bin = TrapHelper.write_trap(b, new_name)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "TrapData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Trap definitions to: {target_path}")

def update_trophies():
    excel_path = os.path.join(TABLES_DIR, 'trophies.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping Trophies.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb["Trophies"]
    
    edits = {} # fn -> mod_desc
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[1]:
            continue
        idx, fn, title, van_desc, mod_desc, status = row[:6]
        if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
            edits[fn] = mod_desc
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "TrophyData.pck")
    archive = PckArchive(pck_path)
    
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn in edits:
            new_desc = edits[fn]
            new_bin = TrophyHelper.write_trophy(b, new_desc)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "TrophyData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Trophy milestones to: {target_path}")

def update_shop_dialogue():
    # 1. ShopQuest.pck
    sq_path = os.path.join(BACKUP_DIR, "ShopQuest.pck")
    if os.path.exists(sq_path):
        arc_sq = PckArchive(sq_path)
        repl_sq = {
            "(Incidentally, quests from below your current rank\nwill still grant their rewards, but no trust points.)": (
                "(Quests below your rank grant rewards but 0 Trust Points.\n"
                "Prioritize current quests: Ranks 2 & 8 grant +10 Bag Storage\n"
                "each (reaching 50 slots early!), and Rank 16 unlocks The Matrix!)"
            )
        }
        repl_sq_10 = {
            "(If you complete many quests... something good might happen.)": (
                "(Extermination quests grant Trust Points to raise your rank,\n"
                "while fetch quests yield rare weapons and heavy gold rewards.)"
            )
        }
        for i, (fn, b) in enumerate(arc_sq.files):
            if fn == "Talk_Random08.adv.bin":
                arc_sq.files[i] = (fn, update_teaching_script(b, repl_sq))
            elif fn == "Talk_Random10.adv.bin":
                arc_sq.files[i] = (fn, update_teaching_script(b, repl_sq_10))
        sq_target = os.path.join(GAME_SCRIPT_DIR, "ShopQuest.pck")
        arc_sq.save(sq_target)
        print(f"Applied Quest Desk progression dialogue to: {sq_target}")

    # 2. ShopBlacksmith.pck
    sb_path = os.path.join(BACKUP_DIR, "ShopBlacksmith.pck")
    if os.path.exists(sb_path):
        arc_sb = PckArchive(sb_path)
        repl_sb_00 = {
            "(You can enchant up to five times... An item\nwon't be able to handle more than that.)": (
                "(Equipment holds up to 5 enchant slots, but can be forged\n"
                "up to +9 level! Each +level boosts base stats and activates\n"
                "Sealbook enchants. Plan your forge progression well...)"
            )
        }
        repl_sb_10 = {
            "(Furthermore, monsters with Petrification\ncan't be sealed either... That's just how it is.)": (
                "(Monsters that flee, self-destruct, or suffer Petrification\n"
                "CANNOT be sealed into Sealbooks! Inflict Paralysis or Sleep\n"
                "instead to ensure 100% seal chances without risk.)"
            )
        }
        repl_sb_11 = {
            "(Grand Sealbooks are outside my expertise,\nand if we tried it blind, anything could happen...)": (
                "(Grand Sealbooks belong in the Grand Seal slot for party\n"
                "auras and summons, not for ordinary equipment enchants!)"
            )
        }
        for i, (fn, b) in enumerate(arc_sb.files):
            if fn == "Talk_Random00.adv.bin":
                arc_sb.files[i] = (fn, update_teaching_script(b, repl_sb_00))
            elif fn == "Talk_Random10.adv.bin":
                arc_sb.files[i] = (fn, update_teaching_script(b, repl_sb_10))
            elif fn == "Talk_Random11.adv.bin":
                arc_sb.files[i] = (fn, update_teaching_script(b, repl_sb_11))
        sb_target = os.path.join(GAME_SCRIPT_DIR, "ShopBlacksmith.pck")
        arc_sb.save(sb_target)
        print(f"Applied Blacksmith strategic forge dialogue to: {sb_target}")

    # 3. ShopBar.pck
    bar_path = os.path.join(BACKUP_DIR, "ShopBar.pck")
    if os.path.exists(bar_path):
        arc_bar = PckArchive(bar_path)
        repl_bar = {
            "When hiring a merc, you can check their stats and skills,\nbut you obviously can't tell how they're going to behave.": (
                "Mercenary AI follows fixed class role archetypes:\n"
                "Paladins prioritize Provoke and Cover, Priests cast\n"
                "Heal at <50% HP, and Dark Lords spam burst physical skills."
            )
        }
        for i, (fn, b) in enumerate(arc_bar.files):
            if fn == "Talk_Random04.adv.bin":
                arc_bar.files[i] = (fn, update_teaching_script(b, repl_bar))
        bar_target = os.path.join(GAME_SCRIPT_DIR, "ShopBar.pck")
        arc_bar.save(bar_target)
        print(f"Applied Tavern mercenary archetype dialogue to: {bar_target}")

    # 4. ShopStore.pck (General Store / Monica)
    ss_path = os.path.join(BACKUP_DIR, "ShopStore.pck")
    if os.path.exists(ss_path):
        arc_ss = PckArchive(ss_path)
        repl_ss_01 = {
            "Do you have Crois-sants and E-mer-gen-cy Ex-its in your\npos-ses-sion? They are es-sen-tial i-tems for rook-ie\nad-ventur-ers.": (
                "Al-so car-ry Flash-lights! They now il-lu-mi-nate dark zones\n"
                "for 30 steps (3x lon-ger) to re-veal hid-den walls\n"
                "and traps with-out wast-ing pre-cious bag space."
            )
        }
        repl_ss_11 = {
            "If you find your-self run-ning out of TP, then I\nre-com-mend you pur-chase Fair-y Ap-ples! They re-cov-er 50\nTP for the low price of 900 gold.": (
                "For bud-get ex-pe-di-tions, try Dried Ber-ries (20 TP for 40 G)\n"
                "or Ba-nan-go Sli-ces (35 TP for 80 G) to sus-tain your loop\n"
                "with-out emp-ty-ing your wal-let on Fair-y Ap-ples!"
            )
        }
        for i, (fn, b) in enumerate(arc_ss.files):
            if fn == "Talk_Random01.adv.bin":
                arc_ss.files[i] = (fn, update_teaching_script(b, repl_ss_01))
            elif fn == "Talk_Random11.adv.bin":
                arc_ss.files[i] = (fn, update_teaching_script(b, repl_ss_11))
        ss_target = os.path.join(GAME_SCRIPT_DIR, "ShopStore.pck")
        arc_ss.save(ss_target)
        print(f"Applied General Store exploration dialogue to: {ss_target}")

def update_quest_ranks():
    pck_path = os.path.join(BACKUP_DIR, "QuestRankData.pck")
    if not os.path.exists(pck_path):
        print(f"Notice: Backup {pck_path} not found, skipping Quest Ranks.")
        return
        
    archive = PckArchive(pck_path)
    
    def make_quest_rank_bag_entry(rank, pts, val):
        import struct
        msg = f"Your bag's storage capacity has increased by {val}."
        s = msg.encode('latin-1') + b'\x00'
        hdr = struct.pack('<10i', rank, pts, 40, 0, 5, -1, -1, -1, -1, val)
        data = bytearray(hdr) + s
        pad = (8 - (len(data) % 8)) % 8
        data += b'\x00' * pad
        return bytes(data)

    def make_quest_rank_gold_entry(rank, pts, amount):
        import struct
        msg = f"You got {amount:,} gold."
        s = msg.encode('latin-1') + b'\x00'
        hdr = struct.pack('<10i', rank, pts, 40, 0, 2, -1, -1, -1, -1, amount)
        data = bytearray(hdr) + s
        pad = (8 - (len(data) % 8)) % 8
        data += b'\x00' * pad
        return bytes(data)

    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        if fn == 'QuestRankData_02.bin':
            # Chapter 1 early boost: +10 bag space (30 -> 40 slots!)
            archive.files[i] = (fn, make_quest_rank_bag_entry(2, 25, 10))
            applied_count += 1
        elif fn == 'QuestRankData_08.bin':
            # Mid-game max bag boost: +10 bag space (40 -> 50 slots, max engine cap!)
            archive.files[i] = (fn, make_quest_rank_bag_entry(8, 200, 10))
            applied_count += 1
        elif fn == 'QuestRankData_11.bin':
            # Replace redundant bag reward (+0 slots due to 50 cap) with 50,000 gold
            archive.files[i] = (fn, make_quest_rank_gold_entry(11, 340, 50000))
            applied_count += 1
        elif fn == 'QuestRankData_15.bin':
            # Replace redundant bag reward with 100,000 gold
            archive.files[i] = (fn, make_quest_rank_gold_entry(15, 560, 100000))
            applied_count += 1
        elif fn == 'QuestRankData_20.bin':
            # Replace redundant bag reward with 500,000 gold for Master Guild Rank
            archive.files[i] = (fn, make_quest_rank_gold_entry(20, 1000, 500000))
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "QuestRankData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} Quest Rank rewards to: {target_path}")

def update_exp_curve():
    excel_path = os.path.join(TABLES_DIR, 'exp_curve.xlsx')
    if not os.path.exists(excel_path):
        print(f"Notice: {excel_path} not found, skipping EXP curve.")
        return
        
    wb = openpyxl.load_workbook(excel_path)
    ws = wb['ExpCurve']
    
    edits = {} # level -> (modded_exp, modded_sp)
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        lv, van_exp, mod_exp, van_sp, mod_sp = row[:5]
        status = row[7] if len(row) > 7 else 'Approved'
        if status in ['Approved', 'Applied', 'Draft']:
            edits[int(lv)] = (int(mod_exp), int(mod_sp))
            
    if not edits:
        return
        
    pck_path = os.path.join(BACKUP_DIR, "LvExpSkptData.pck")
    archive = PckArchive(pck_path)
    
    import struct
    applied_count = 0
    for i, (fn, b) in enumerate(archive.files):
        try:
            lv_num = int(fn.replace('LvExpSkptData_', '').replace('.bin', ''))
        except ValueError:
            continue
            
        if lv_num in edits:
            mod_exp, mod_sp = edits[lv_num]
            new_bin = struct.pack('<III', lv_num, mod_exp, mod_sp)
            archive.files[i] = (fn, new_bin)
            applied_count += 1
            
    target_path = os.path.join(GAME_PARAM_DIR, "LvExpSkptData.pck")
    archive.save(target_path)
    print(f"Applied {applied_count} balanced EXP & SP levels to: {target_path}")

if __name__ == "__main__":
    print("=== Applying Comprehensive Mod Suite to Game PCKs ===")
    update_skills()
    update_items()
    update_equipment()
    update_weapon_ranks()
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
    update_traps()
    update_trophies()
    update_shop_dialogue()
    update_quest_ranks()
    update_exp_curve()
    print("=== Complete Mod Execution Finished Successfully! ===")




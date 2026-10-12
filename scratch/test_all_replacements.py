import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backup_dir = os.path.join(base_dir, 'backups')

def test_script_replacements():
    # Read apply_mod.py
    with open(os.path.join(base_dir, 'tools', 'apply_mod.py'), 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # We will test all replacements used in apply_mod.py
    # 1. Lesson.pck
    repl_04 = {"This information is extremely important during battle, so I\nhighly suggest that you make use of it when battling against\nthreatening enemies.": "new"}
    repl_07 = {"Well, that was something of a brief lesson, but let's leave\nit here for today.": "new"}
    repl_08 = {"Precisely. Against certain monsters, raising your\nresistances can be considerably more effective than raising\nyour defense directly.": "new"}
    repl_09 = {"Presents include gold, rare equipment, and even additional\nbag space.": "new"}
    repl_09_quoted = {"\"Presents include gold, rare equipment, and even additional\nbag space.\"": "new"}
    repl_10 = {
        "Party skills also grow stronger according to the number of\nawards you amass.": "new",
        "\"Try to use one, and you might be surprised.\"": "new"
    }
    repl_11 = {
        "Or, after certain level thresholds, you can choose to reset\nback to those specific threshold levels as opposed to level\n1.": "new",
        "\"So even though level resetting will lower a character's\nlevel, it won't be long before she catches up to the rest of\nthe party as you go about your adventures.\"": "new"
    }
    repl_13 = {"Is that right...? There aren't many restaurants around these\nparts, so I've been frequenting it quite often.": "new"}
    repl_sp01 = {"\"Abandon hope and make peace with your fate.\"": "new"}
    repl_sp02 = {"Dark Aura debuffs enemies' stats when they inflict\nshort-range damage. No monsters are immune to such debuffs,\nso you can even use it in boss battles.": "new"}
    repl_sp03 = {"\"There's no real necessity to seek so much power... but if it\nstrikes your fancy, why not shoot for the Crown?\"": "new"}

    lesson_tests = {
        'BattleTeacher_04.adv.bin': repl_04,
        'BattleTeacher_07.adv.bin': repl_07,
        'BattleTeacher_08.adv.bin': repl_08,
        'BattleTeacher_09.adv.bin (unquoted)': repl_09,
        'BattleTeacher_09.adv.bin (quoted)': repl_09_quoted,
        'BattleTeacher_10.adv.bin': repl_10,
        'BattleTeacher_11-12.adv.bin': repl_11,
        'BattleTeacher_13.adv.bin': repl_13,
        'BattleTeacher_Sp01.adv.bin': repl_sp01,
        'BattleTeacher_Sp02.adv.bin': repl_sp02,
        'BattleTeacher_Sp03.adv.bin': repl_sp03,
    }

    arc_lesson = PckArchive(os.path.join(backup_dir, 'Lesson.pck'))
    print("=== TESTING LESSON.PCK REPLACEMENTS ===")
    for desc, repls in lesson_tests.items():
        fname = desc.split(' ')[0]
        data = [b for fn, b in arc_lesson.files if fn == fname][0]
        for orig, _ in repls.items():
            pos = data.find(orig.encode('ascii') + b'\x00')
            if pos != -1:
                print(f"[PASS] {desc}: Found at offset {pos}")
            else:
                print(f"[FAIL] {desc}: NOT FOUND! Target: {repr(orig)}")

    # 2. Teaching.pck
    # Let's extract all replacements from apply_mod.py
    print("\n=== TESTING TEACHING.PCK REPLACEMENTS ===")
    arc_teach = PckArchive(os.path.join(backup_dir, 'Teaching.pck'))
    
    # We will import the actual functions or parse them from apply_mod.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("apply_mod", os.path.join(base_dir, 'tools', 'apply_mod.py'))
    mod = importlib.util.module_from_spec(spec)
    # We don't run mod, but let's check Teaching lines directly:
    teach_targets = [
        ('CheatsTeaching_01.adv.bin', "Turn order is a fundamental aspect of combat, so be sure to\ncheck it often and strategize efficiently."),
        ('CheatsTeaching_02.adv.bin', "Please note that although skills grow more powerful at\nhigher levels, their TP cost and chanting time may also\nincrease, which can make them more difficult to use."),
        ('CheatsTeaching_03.adv.bin', "Techniques and magic are skills that you choose when to\nactivate, whereas passive skills take effect automatically,\nand do not need to be selected."),
        ('CheatsTeaching_04.adv.bin', "Each Sealbook offers different enchantments, so make plenty\nand use them to strengthen your party."),
        ('CheatsTeaching_05.adv.bin', "They offer a wide range of effects, so you should try each\nGrand Sealbook out as soon as you get it."),
        ('CheatsTeaching_06.adv.bin', "The effect can vary depending on the monster. For instance,\na mutant skilled at physical attacks will have her ATK stat\nmost easily influenced by the party."),
        ('CheatsTeaching_07.adv.bin', "More details will be visible in the Stats menu for monsters\nwhose Sealbooks you have created before."),
        ('CheatsTeaching_08.adv.bin', "If you missed something that happened, you can refer to the\nbattle log to see who did what during battle."),
        ('CheatsTeaching_09.adv.bin', "Weapon speed ranks range from A, which is the fastest, to F,\nwhich is the slowest."),
        ('CheatsTeaching_10.adv.bin', "Critical hits, however, have a fixed 1/3 chance of\ninterrupting, regardless of the amount of damage inflicted."),
        ('CheatsTeaching_11.adv.bin', "While it is possible to attack over long range with a\nshort-range weapon, the damage will be considerably lessened\nas a result."),
        ('CheatsTeaching_12.adv.bin', "Also renders you unable to dodge attacks, and incoming\ndamage increases significantly."),
        ('CheatsTeaching_13.adv.bin', "If you have 100 resistance to a certain element, you will be\ncompletely immune to its corresponding status ailments."),
        ('CheatsTeaching_14.adv.bin', "Complete enough quests to increase your rank, and you will\nalso receive a present."),
        ('CheatsTeaching_15.adv.bin', "Instead, they level up by themselves every 10 levels."),
        ('CheatsTeaching_16.adv.bin', "Party skills grow stronger the more Awards you obtain."),
        ('CheatsTeaching_17.adv.bin', "2. Each participating member needs to have enough TP to\nperform the joint skill."),
        ('CheatsTeaching_18.adv.bin', "If the character has passed certain level thresholds,\nthen it is possible to restore to those thresholds rather\nthan to level 1."),
        ('CheatsTeaching_19.adv.bin', "If you defeat a group of monsters with a single party\nmember, she will gain all the EXP herself, but with a party\nof five, the experience gets split five ways."),
        ('CheatsTeaching_19.adv.bin', "With these things in mind, you might be able to quickly\nbring characters whose levels you have reset back up to\ntheir former strength."),
        ('CheatsTeaching_20.adv.bin', "Elemental Zones: Enhance one element: Fire, Water,\nWind, Earth, or Lightning. Increase all damage of that\nelemental type considerably."),
        ('CheatsTeaching_20.adv.bin', "Boost Zones: There are Attack, Magic, Armor, and Magic\nResist Zones. They enhance Physical Attack, Magic Attack,\nPhysical Defense, and Magic Defense respectively."),
        ('CheatsTeaching_21.adv.bin', "2. They have a contract period. Once they have fought the\nnumber of battles indicated when hiring, they will leave,\nno matter where you are."),
        ('CheatsTeaching_23.adv.bin', "There are also some monsters that use different skills after\ntaking a certain amount of damage."),
        ('CheatsTeaching_24.adv.bin', "Some skills may have powerful synergies with equipment\nenchantments as well. Keep an eye on your arsenal for new\nopportunities."),
        ('CheatsTeaching_25.adv.bin', "Resetting with an even greater level gap can provide even\ngreater stat increases."),
        ('CheatsTeaching_25.adv.bin', "This will raise your unique skill to Level EX,\ngreatly heightening its effects."),
    ]
    for fn, target in teach_targets:
        data = [b for f, b in arc_teach.files if f == fn][0]
        pos = data.find(target.encode('ascii') + b'\x00')
        if pos != -1:
            print(f"[PASS] {fn}: Found at offset {pos}")
        else:
            print(f"[FAIL] {fn}: NOT FOUND! Target: {repr(target)}")

    # 3. Shop PCKs
    print("\n=== TESTING SHOP PCK REPLACEMENTS ===")
    arc_sq = PckArchive(os.path.join(backup_dir, 'ShopQuest.pck'))
    sq_targets = [
        ('Talk_Random08.adv.bin', "(Incidentally, quests from below your current rank\nwill still grant their rewards, but no trust points.)"),
        ('Talk_Random10.adv.bin', "(If you complete many quests... something good might happen.)")
    ]
    for fn, target in sq_targets:
        data = [b for f, b in arc_sq.files if f == fn][0]
        pos = data.find(target.encode('ascii') + b'\x00')
        if pos != -1:
            print(f"[PASS] ShopQuest.pck -> {fn}: Found at {pos}")
        else:
            print(f"[FAIL] ShopQuest.pck -> {fn}: NOT FOUND! Target: {repr(target)}")

    arc_sb = PckArchive(os.path.join(backup_dir, 'ShopBlacksmith.pck'))
    sb_targets = [
        ('Talk_Random00.adv.bin', "(You can enchant up to five times... An item\nwon't be able to handle more than that.)"),
        ('Talk_Random10.adv.bin', "(Furthermore, monsters with Petrification\ncan't be sealed either... That's just how it is.)"),
        ('Talk_Random11.adv.bin', "(Grand Sealbooks are outside my expertise,\nand if we tried it blind, anything could happen...)")
    ]
    for fn, target in sb_targets:
        data = [b for f, b in arc_sb.files if f == fn][0]
        pos = data.find(target.encode('ascii') + b'\x00')
        if pos != -1:
            print(f"[PASS] ShopBlacksmith.pck -> {fn}: Found at {pos}")
        else:
            print(f"[FAIL] ShopBlacksmith.pck -> {fn}: NOT FOUND! Target: {repr(target)}")

    arc_bar = PckArchive(os.path.join(backup_dir, 'ShopBar.pck'))
    bar_targets = [
        ('Talk_Random04.adv.bin', "When hiring a merc, you can check their stats and skills,\nbut you obviously can't tell how they're going to behave.")
    ]
    for fn, target in bar_targets:
        data = [b for f, b in arc_bar.files if f == fn][0]
        pos = data.find(target.encode('ascii') + b'\x00')
        if pos != -1:
            print(f"[PASS] ShopBar.pck -> {fn}: Found at {pos}")
        else:
            print(f"[FAIL] ShopBar.pck -> {fn}: NOT FOUND! Target: {repr(target)}")

    arc_ss = PckArchive(os.path.join(backup_dir, 'ShopStore.pck'))
    ss_targets = [
        ('Talk_Random01.adv.bin', "Do you have Crois-sants and E-mer-gen-cy Ex-its in your\npos-ses-sion? They are es-sen-tial i-tems for rook-ie\nad-ventur-ers."),
        ('Talk_Random11.adv.bin', "If you find your-self run-ning out of TP, then I\nre-com-mend you pur-chase Fair-y Ap-ples! They re-cov-er 50\nTP for the low price of 900 gold.")
    ]
    for fn, target in ss_targets:
        data = [b for f, b in arc_ss.files if f == fn][0]
        pos = data.find(target.encode('ascii') + b'\x00')
        if pos != -1:
            print(f"[PASS] ShopStore.pck -> {fn}: Found at {pos}")
        else:
            print(f"[FAIL] ShopStore.pck -> {fn}: NOT FOUND! Target: {repr(target)}")

if __name__ == '__main__':
    test_script_replacements()

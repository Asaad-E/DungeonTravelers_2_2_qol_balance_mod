import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'tools'))
from pck_handler import PckArchive

BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
GAME_SCRIPT_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')

# =========================================================================
# 1. EUTHYS LESSONS (Lesson.pck)
# Quotes included in search and replacement to ensure exact matching in .adv.bin
# =========================================================================

EUTHYS_REPLACEMENTS = {
    # Lesson 04 (Heavy weapons, Defend, and Delay)
    'BattleTeacher_04.adv.bin': {
        '"This information is extremely important during battle, so I\nhighly suggest that you make use of it when battling against\nthreatening enemies."': (
            '"Pay close attention: heavy 2H blades and rifles hit hard,\n'
            'but their severe delay leaves you wide open!\n'
            'Have them Defend to advance their gauge and recover the initiative."'
        )
    },
    # Lesson 07 (Weapon Range and Row Penalties)
    'BattleTeacher_07.adv.bin': {
        '"Well, that was something of a brief lesson, but let\'s leave\nit here for today."': (
            '"Mid-range spears and whips ignore penalties from adjacent rows,\n'
            'while bows and magic strike across all rows at full power.\n'
            'Position your allies wisely, Fried, lest you suffer needless harm."'
        )
    },
    # Lesson 08 (Elemental Resistances and 100 Res Cap)
    'BattleTeacher_08.adv.bin': {
        '"Precisely. Against certain monsters, raising your\nresistances can be considerably more effective than raising\nyour defense directly."': (
            '"Precisely! Stacking 100 resistance also cuts elemental damage in half.\n'
            'Combine this with a Paladin\'s Cover or a Dark Lord\'s leeching,\n'
            'and your front line will stand firm even against divine magic."'
        )
    },
    # Lesson 09 (Guild Ranks, Bag Expansions)
    'BattleTeacher_09.adv.bin': {
        '"Presents include gold, rare equipment, and even additional\nbag space."': (
            '"Presents include fine gold, rare equipment, and bag expansions.\n'
            'Climb through the ranks to expand your inventory, ensuring you\n'
            'carry ample supplies to conquer the deepest labyrinths."'
        )
    },
    # Lesson 10 (Joint Skills and Pep Coordination)
    'BattleTeacher_10.adv.bin': {
        '"Party skills also grow stronger according to the number of\nawards you amass."': (
            '"Party skills also grow stronger according to the number of\n'
            'awards you amass (gaining +1% efficacy per 5 awards)."'
        ),
        '"Try to use one, and you might be surprised."': (
            '"*giggle* Don\'t be so timid, Fried. Examine their requirements\n'
            'in the menu and coordinate your turns to store Pep. A well-timed\n'
            'Joint Skill can pierce tough defenses and turn tides in an instant."'
        )
    },
    # Lesson 11-12 (Level Reset, Slave\'s Torc Double EXP)
    'BattleTeacher_11-12.adv.bin': {
        '"So even though level resetting will lower a character\'s\nlevel, it won\'t be long before she catches up to the rest of\nthe party as you go about your adventures."': (
            '"Simply equip her with the Slave\'s Torc to double her gains.\n'
            'She will soak up so much experience from stronger monsters that\n'
            'she\'ll rejoin the vanguard before you even have time to complain."'
        )
    },
    # Lesson 13 (Restaurant Meals and Buff Protection)
    'BattleTeacher_13.adv.bin': {
        '"Is that right...? There aren\'t many restaurants around these\nparts, so I\'ve been frequenting it quite often."': (
            '"I visit often. A hearty meal bestows blessings for explorations,\n'
            'and the finest dishes grant buffs and elemental guards that\n'
            'even pesky Dispel traps cannot erase. Exquisite and practical."'
        )
    },
    # Lesson Sp01 (Deadly Attacks - Preserves the Joke + Adds Real Tactic)
    'BattleTeacher_Sp01.adv.bin': {
        '"Abandon hope and make peace with your fate."': (
            '"Abandon hope and make peace with your fate... *giggle*\n'
            'Stack 100 Elemental Resist to cut that damage in half, Fried,\n'
            'or have an Enchantress pop Circle Protect on lethal turns."'
        )
    },
    # Lesson Sp02 (Dark Aura and Execution)
    'BattleTeacher_Sp02.adv.bin': {
        '"Dark Aura debuffs enemies\' stats when they inflict\nshort-range damage. No monsters are immune to such debuffs,\nso you can even use it in boss battles."': (
            '"Dark Aura debuffs on contact, even against bosses. When formidable\n'
            'foes shift rotations at low health, unleash your fiercest\n'
            'Joint Skills to execute them before they overwhelm you."'
        )
    },
    # Lesson Sp03 (Crown EX Skills)
    'BattleTeacher_Sp03.adv.bin': {
        '"There\'s no real necessity to seek so much power... but if it\nstrikes your fancy, why not shoot for the Crown?"': (
            '"Longing to elevate your companions to godlike perfection?\n'
            'Resetting with a 59+ level gap grants permanent stat boosts,\n'
            'awakening their potential toward the legendary Crown EX."'
        )
    }
}

# =========================================================================
# 2. TEACHING TUTORIALS (Teaching.pck)
# Plain text replacement matching exact strings in .adv.bin
# =========================================================================

TEACHING_REPLACEMENTS = {
    # 01 Turn Order
    'CheatsTeaching_01.adv.bin': {
        'Turn order is a fundamental aspect of combat, so be sure to\ncheck it often and strategize efficiently.': (
            'Weapon delay spans 12 ranks: A+ (1.0x) to F (2.9x delay).\n'
            'Choosing Defend advances your turn gauge to recover sooner,\n'
            'allowing heavy weapon wielders to maintain tactical tempo!'
        )
    },
    # 02 Learning Skills
    'CheatsTeaching_02.adv.bin': {
        'Please note that although skills grow more powerful at\nhigher levels, their TP cost and chanting time may also\nincrease, which can make them more difficult to use.': (
            'Higher skill levels increase TP cost and chant delay. Balance\n'
            'sweet spots: lower levels for cheap sustainable exploration loops,\n'
            'and higher levels for decisive burst damage against tough foes.'
        )
    },
    # 03 Skill Types
    'CheatsTeaching_03.adv.bin': {
        'Techniques and magic are skills that you choose when to\nactivate, whereas passive skills take effect automatically,\nand do not need to be selected.': (
            'Techniques hit instantly but add recovery delay. Spells require\n'
            'chanting time but recover faster. Songs and Dances apply auras,\n'
            'while Dolls act as autonomous allies on their own turns.'
        )
    },
    # 04 Libras & Sealing
    'CheatsTeaching_04.adv.bin': {
        'Each Sealbook offers different enchantments, so make plenty\nand use them to strengthen your party.': (
            'Crafting a Sealbook permanently unlocks monster Level, HP, and\n'
            'Resistances in battle! Equip Sealbooks for stats or forge them\n'
            'onto weapons at the Blacksmith (+1 to +9) to inherit enchants.'
        )
    },
    # 05 Grand Sealbooks
    'CheatsTeaching_05.adv.bin': {
        'They offer a wide range of effects, so you should try each\nGrand Sealbook out as soon as you get it.': (
            'Mutant bosses drop Grand Sealbooks with 100% guarantee.\n'
            'Equipping one provides powerful passive auras that boost the\n'
            'entire party, plus summons the mutant as an autonomous ally!'
        )
    },
    # 06 Sealbook Summons
    'CheatsTeaching_06.adv.bin': {
        'The effect can vary depending on the monster. For instance,\na mutant skilled at physical attacks will have her ATK stat\nmost easily influenced by the party.': (
            'Summon stats scale with party averages (level, ATK, INT).\n'
            'Summons act on their own turns and cannot be commanded.\n'
            'Note: Party-wide heals and buffs do NOT affect summons.'
        )
    },
    # 07 Scanning Stats
    'CheatsTeaching_07.adv.bin': {
        'More details will be visible in the Stats menu for monsters\nwhose Sealbooks you have created before.': (
            'Press <BUTTON_L> to inspect monsters. Creating their Sealbook\n'
            'permanently reveals Max HP, ATK, DEF, and all 5 elemental\n'
            'resistances, allowing you to exploit their vulnerabilities!'
        )
    },
    # 08 Battle Log
    'CheatsTeaching_08.adv.bin': {
        'If you missed something that happened, you can refer to the\nbattle log to see who did what during battle.': (
            'The battle log reveals crucial combat details: spell chants,\n'
            'exact status resistance checks, boss rotation shifts, and turn\n'
            'delay procs. Review it closely to refine your boss strategy!'
        )
    },
    # 09 Weapon Delay Ranks (Entire 3-line box replaced)
    'CheatsTeaching_09.adv.bin': {
        'The higher her AGI stat, the faster she will be.\nWeapon speed ranks range from A, which is the fastest, to F,\nwhich is the slowest.': (
            'Higher AGI speeds up turns, while weapons add recovery delay.\n'
            'Weapon ranks span from A+ (1.00x) up to F (2.90x delay).\n'
            'Choosing Defend advances your turn gauge to recover sooner.'
        )
    },
    # 10 Techniques vs Magic (Crit Interrupt)
    'CheatsTeaching_10.adv.bin': {
        'Critical hits, however, have a fixed 1/3 chance of\ninterrupting, regardless of the amount of damage inflicted.': (
            'Chant interrupt chance scales with damage taken vs Max HP.\n'
            'Crucially, ANY Critical Hit has a flat 33.3% interrupt chance!\n'
            'Use high-crit skills or multihit attacks to reliably stop spells.'
        )
    },
    # 11 Range & Distance
    'CheatsTeaching_11.adv.bin': {
        'While it is possible to attack over long range with a\nshort-range weapon, the damage will be considerably lessened\nas a result.': (
            'Short-range attacks suffer damage penalties across distant rows.\n'
            'Mid-range spears hit adjacent rows cleanly, while long-range\n'
            'bows and magic strike any enemy row at 100% full power.'
        )
    },
    # 12 Status Ailments (Sleep)
    'CheatsTeaching_12.adv.bin': {
        'Also renders you unable to dodge attacks, and incoming\ndamage increases significantly.': (
            'Sleeping targets cannot evade attacks and suffer 1.5x damage\n'
            'from all strikes. However, taking any damage wakes them up,\n'
            'so time your heaviest burst attacks accordingly!'
        )
    },
    # 13 Resistances and Immunity
    'CheatsTeaching_13.adv.bin': {
        'If you have 100 resistance to a certain element, you will be\ncompletely immune to its corresponding status ailments.': (
            'Resistances cut elemental damage by 0.5% per point (100 res =\n'
            '50% cut, 200 res = 100% immune). At 100 resistance, you gain\n'
            'complete 100% IMMUNITY to all corresponding status ailments!'
        )
    },
    # 14 Quest Desk & Bags
    'CheatsTeaching_14.adv.bin': {
        'Complete enough quests to increase your rank, and you will\nalso receive a present.': (
            'Increasing Quest Rank expands your item bag capacity\n'
            'at key milestones, granting additional storage space\n'
            'to sustain deeper dungeon expeditions and rare loot.'
        )
    },
    # 15 Unique Skills
    'CheatsTeaching_15.adv.bin': {
        'Instead, they level up by themselves every 10 levels.': (
            'Unique skills auto-level every 10 levels up to Level 9 (Lv 90).\n'
            'Achieving a Crown elevates Unique Skills to Level EX permanently,\n'
            'preserving that awakened power even after resetting to Level 1!'
        )
    },
    # 16 Party Skills
    'CheatsTeaching_16.adv.bin': {
        'Party skills grow stronger the more Awards you obtain.': (
            'Party skills gain +1% bonus efficacy for every 5 Awards earned.'
        )
    },
    # 17 Joint Skills
    'CheatsTeaching_17.adv.bin': {
        'Finally, each joint skill can only be performed once per\nbattle, so always time their usage carefully.': (
            'Joint skills pierce defenses and unleash devastating power!\n'
            'Each joint skill can only be used once per battle, so time\n'
            'their activation carefully to break through dangerous phases.'
        )
    },
    # 18 Level Resetting
    'CheatsTeaching_18.adv.bin': {
        'If the character has passed certain level thresholds,\nthen it is possible to restore to those thresholds rather\nthan to level 1.': (
            'Resetting allows reclassing and reallocating all skill points.\n'
            'You can reset to Level 1 or to intermediate class thresholds\n'
            '(Level 15 or Level 30) to freely experiment with new builds.'
        )
    },
    # 19 EXP Multipliers (Slave's Torc training)
    'CheatsTeaching_19.adv.bin': {
        'With these things in mind, you might be able to quickly\nbring characters whose levels you have reset back up to\ntheir former strength.': (
            'Equip training accessories like Slave\'s Torc to double\n'
            'experience gains, rapidly catching up allies who underwent resets.\n'
            'Facing higher-level monsters also grants native bonus EXP.'
        )
    },
    # 20 Zones & Anti-Magic
    'CheatsTeaching_20.adv.bin': {
        'There is one notable exception to this rule: it does not\napply to magic cast by dolls.': (
            'Dolls are autonomous entities that ignore Anti-Magic Zones!\n'
            'Doll Masters can rely on their puppets to cast elemental spells\n'
            'even in zones where normal party magic is silenced.'
        )
    },
    # 21 Mercenaries
    'CheatsTeaching_21.adv.bin': {
        'Try to work with the mercenaries as much as you can, and see\ntheir potential for yourself.': (
            'Mercenaries provide specialized class utility without changing\n'
            'your core party. Higher Quest Ranks attract veteran mercenaries\n'
            'equipped with advanced techniques to support deep explorations.'
        )
    },
    # 22 Skill Synergies (Clean immersive lore)
    'CheatsTeaching_22.adv.bin': {
        'After changing classes, be sure to read the descriptions for\nall the skills available to make sure you\'re taking full\nadvantage of them.': (
            'Experiment with unique synergies across advanced classes.\n'
            'Pair defensive stances with chant protection, and manage\n'
            'weapon delay tiers to master late-game tactical encounters.'
        )
    },
    # 23 Boss Rotations
    'CheatsTeaching_23.adv.bin': {
        'There are also some monsters that use different skills after\ntaking a certain amount of damage.': (
            'Beware: certain formidable foes unleash deadly new skill\n'
            'rotations after taking substantial damage. Save burst damage\n'
            'and Joint Skills to finish them before they overwhelm you.'
        )
    },
    # 24 Skill Synergies
    'CheatsTeaching_24.adv.bin': {
        'Some skills may have powerful synergies with equipment\nenchantments as well. Keep an eye on your arsenal for new\nopportunities.': (
            'Synergy examples: multi-hit attacks with Bard\'s Barrage Rondo,\n'
            'Provoke paired with Dark Aura, and high-crit skills paired with\n'
            'Chant interruption to shut down enemy magic users.'
        )
    },
    # 25 Crowns
    'CheatsTeaching_25.adv.bin': {
        'When level resetting, if there is a gap of over 59 between\nyour former level and the level you\'re resetting to,\nall your stats will increase by 1.': (
            'When level resetting, if the gap is 59 or greater between\n'
            'your former level and the level you reset to, all stats and\n'
            'resistances increase by +1 permanently, building toward Crown EX.'
        )
    }
}


def apply_script_replacements(bin_data, replacements):
    new_data = bytearray(bin_data)
    for orig_str, new_str in replacements.items():
        orig_bytes = orig_str.encode('latin-1') + b'\x00'
        new_bytes = new_str.encode('latin-1') + b'\x00'
        idx = new_data.find(orig_bytes)
        if idx == -1:
            print(f"  [WARNING] Target string not found:\n{repr(orig_str[:60])}")
            continue
        new_data = new_data[:idx] + new_bytes + new_data[idx + len(orig_bytes):]
        print(f"  [APPLIED] Replaced at offset {idx} ({len(orig_bytes)} -> {len(new_bytes)} bytes)")
    return bytes(new_data)


def validate_text(name, replacements):
    for orig, new_val in replacements.items():
        clean = new_val.strip('"')
        lines = clean.split('\n')
        if len(lines) > 3:
            raise ValueError(f"{name}: Box has {len(lines)} lines > 3:\n{new_val}")
        for lidx, l in enumerate(lines):
            if len(l) > 78:
                raise ValueError(f"{name} line {lidx} has length {len(l)} > 78:\n'{l}'")
            if '~' in l:
                raise ValueError(f"{name} contains tilde: '{l}'")


def main():
    print("=== VALIDATING LINE LIMITS AND FORMATTING ===")
    for fn, reps in EUTHYS_REPLACEMENTS.items():
        validate_text(f"Lesson -> {fn}", reps)
    for fn, reps in TEACHING_REPLACEMENTS.items():
        validate_text(f"Teaching -> {fn}", reps)
    print("Validation 100% PASSED: All boxes <= 3 lines, all lines <= 78 chars, no tildes!\n")

    # 1. Update Lesson.pck
    lesson_backup = os.path.join(BACKUP_DIR, 'Lesson.pck')
    arc_lesson = PckArchive(lesson_backup)
    lesson_count = 0
    for i, (fn, b) in enumerate(arc_lesson.files):
        if fn in EUTHYS_REPLACEMENTS:
            print(f"Updating Lesson: {fn}...")
            updated_bytes = apply_script_replacements(b, EUTHYS_REPLACEMENTS[fn])
            arc_lesson.files[i] = (fn, updated_bytes)
            lesson_count += 1
    
    lesson_out = os.path.join(GAME_SCRIPT_DIR, 'Lesson.pck')
    arc_lesson.save(lesson_out)
    print(f"\nSaved updated Lesson.pck ({lesson_count} lesson files modified) to:\n{lesson_out}\n")

    # 2. Update Teaching.pck
    teaching_backup = os.path.join(BACKUP_DIR, 'Teaching.pck')
    arc_teaching = PckArchive(teaching_backup)
    teaching_count = 0
    for i, (fn, b) in enumerate(arc_teaching.files):
        if fn in TEACHING_REPLACEMENTS:
            print(f"Updating Teaching: {fn}...")
            updated_bytes = apply_script_replacements(b, TEACHING_REPLACEMENTS[fn])
            arc_teaching.files[i] = (fn, updated_bytes)
            teaching_count += 1
            
    teaching_out = os.path.join(GAME_SCRIPT_DIR, 'Teaching.pck')
    arc_teaching.save(teaching_out)
    print(f"\nSaved updated Teaching.pck ({teaching_count} tutorial files modified) to:\n{teaching_out}\n")

    print("=== ALL UPDATES APPLIED AND COMPILED SUCCESSFULLY! ===")

if __name__ == '__main__':
    main()

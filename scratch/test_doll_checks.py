import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive
from extract_vanilla import SKILL_LAYOUTS, SLOT_SIZE, LEVELS, i32, read_array
import text_checks
from text_checks import check_skill_text

BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'backups')
tech_archive = dict(PckArchive(os.path.join(BACKUP_DIR, 'TechniqueSkillData.pck')).files)
magic_archive = dict(PckArchive(os.path.join(BACKUP_DIR, 'MagicSkillData.pck')).files)

DOLL_ACTIONS = {
    49: ('Technique', ['TechniqueSkillData_0106.bin']),
    95: ('Technique', ['TechniqueSkillData_0101.bin']),
    96: ('Technique', ['TechniqueSkillData_0102.bin']),
    97: ('Technique', ['TechniqueSkillData_0104.bin']),
    98: ('Technique', ['TechniqueSkillData_0103.bin']),
    100: ('Magic', ['MagicSkillData_0235.bin']),
}

orig_skill_tables = text_checks.skill_tables

def patched_skill_tables(category, b):
    t = orig_skill_tables(category, b)
    sid = i32(b, 0)
    if sid in DOLL_ACTIONS:
        acat, afiles = DOLL_ACTIONS[sid]
        alay = SKILL_LAYOUTS[acat]
        adict = tech_archive if acat == 'Technique' else magic_archive
        for afn in afiles:
            ab = adict[afn]
            for k in range(i32(ab, alay['count'])):
                off = alay['slots'] + k * SLOT_SIZE
                t['slots'].append((i32(ab, off), i32(ab, off + 4 + 4 * LEVELS), read_array(ab, off + 4)[0][:t['levels']]))
    return t

text_checks.skill_tables = patched_skill_tables

tests = [
    ('TechniqueSkillData_0095.bin', 'Spartan',
     'Summon Spartan for short-range bash damage.',
     'ATK: 144% -> 147 -> 150 -> 154 -> 158 -> 162 -> 166 -> 170 -> 175 -> 180% (L10)\nDuration: 3 -> 6   |   TP Cost: 20 (+2-3/Lv) -> 42   |   Speed: 0.85x -> 0.98x'),
    
    ('TechniqueSkillData_0096.bin', 'Oracles',
     'Summon Oracles for mid-range INT-based damage and possible paralysis.',
     'ATK: 126% (+2-5%/Lv) -> 157%   |   Paralysis: 30% (+3-5%/Lv) -> 64% (L10)\nDuration: 3 -> 5   |   TP Cost: 24 (+2-3/Lv) -> 48   |   Speed: 0.9x'),
    
    ('TechniqueSkillData_0097.bin', 'Catalina',
     "Summon Catalina to heal allies' HP.",
     'Heal Power: 4 -> 6 -> 8 -> 10 -> 12 (L1-5 Max)   |   Duration: 3 -> 5\nTP Cost: 30 -> 33 -> 37 -> 42 -> 48   |   Speed: 0.9x'),
    
    ('TechniqueSkillData_0098.bin', 'Mercidarian',
     'Summon Mercidarian for random long-range stab damage to all foes.',
     'ATK: 100% -> 104 -> 108 -> 112 -> 118 -> 123 -> 128 -> 133 -> 138 -> 143% (L10)\nDuration: 2 -> 4   |   TP Cost: 42 (+2-6/Lv) -> 70   |   Speed: 0.75x'),
    
    ('TechniqueSkillData_0100.bin', 'Musiy',
     'Summon Musiy for immediate single-target attack magic.',
     'Pwr: 180 -> 240 -> 310 -> 390 -> 480 -> 585 -> 700 (L7 Max)\nDuration: 4   |   TP Cost: 38 (+4-6/Lv) -> 68   |   Speed: 0.82x -> 0.92x'),
    
    ('TechniqueSkillData_0049.bin', 'Star Dust Arrow',
     'Bow skill. Shower enemies with a rain of arrows across multiple turns.',
     'ATK: 100% -> 102 -> 104 -> 106 -> 108 -> 110 -> 112 -> 114 -> 117 -> 120% (L10)\n1-3 hits   |   Duration: 2 -> 3   |   TP Cost: 35 (+3/Lv) -> 62   |   Speed: 0.82x'),
]

for fn, name, desc, lvup in tests:
    b = tech_archive[fn]
    full = desc + '\n' + lvup
    lines = full.split('\n')
    max_len = max(len(l) for l in lines)
    probs, ver, loose = check_skill_text('Technique', b, lvup)
    print(f"{name}: probs={probs}, ver={ver}, loose={loose}, max_len={max_len}, lines={len(lines)}")

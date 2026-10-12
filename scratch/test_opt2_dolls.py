import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive
from extract_vanilla import SKILL_LAYOUTS, SLOT_SIZE, LEVELS, i32, read_array
import text_checks
from text_checks import check_skill_text

BACKUP_DIR = os.path.join(os.path.dirname(__file__), '..', 'backups')
tech_archive = dict(PckArchive(os.path.join(BACKUP_DIR, 'TechniqueSkillData.pck')).files)

orig_series_fits = text_checks.series_fits
def patched_series_fits(shown, table):
    table = [round(v, 2) for v in table]
    if len(shown) == 1:
        return all(text_checks.close(shown[0], v) for v in table)
    if len(shown) == len(table) and all(text_checks.close(s, v) for s, v in zip(shown, table)):
        return True
    distinct = [v for k, v in enumerate(table) if k == 0 or not text_checks.close(v, table[k-1])]
    if len(shown) == len(distinct) and all(text_checks.close(s, d) for s, d in zip(shown, distinct)):
        return True
    return len(shown) == 2 and text_checks.close(shown[0], table[0]) and text_checks.close(shown[1], table[-1])

orig_exp = text_checks.expected_tables
def patched_exp(label, category, tables):
    if label == 'Turns':
        t = tables.get('turns')
        if t and any(t):
            return [t]
        st = [v for i, _, v in tables['slots'] if i == 147]
        if st:
            return st
        return [t]
    return orig_exp(label, category, tables)

text_checks.series_fits = patched_series_fits
text_checks.expected_tables = patched_exp

tests = [
    ('TechniqueSkillData_0095.bin', 'Spartan',
     'Summon Spartan for short-range bash damage.',
     'ATK: 144% -> 147 -> 150 -> 154 -> 158 -> 162 -> 166 -> 170 -> 175 -> 180% (L10)\nTurns: 3 (Lv1-3) -> 4 (Lv4-6) -> 5 (Lv7-9) -> 6 (Lv10)   |   TP Cost: 20 -> 42'),
    
    ('TechniqueSkillData_0096.bin', 'Oracles',
     'Summon Oracles for mid-range INT-based damage and possible paralysis.',
     'ATK: 126% (+2-5%/Lv) -> 157%   |   Paralysis: 30% (+3-5%/Lv) -> 64% (L10)\nTurns: 3 (Lv1-4) -> 4 (Lv5-8) -> 5 (Lv9-10)   |   TP Cost: 24 -> 48   |   Speed: 0.9x'),
    
    ('TechniqueSkillData_0097.bin', 'Catalina',
     "Summon Catalina to heal allies' HP.",
     'Heal Power: 4 -> 6 -> 8 -> 10 -> 12 (L1-5 Max)\nTurns: 3 (Lv1-2) -> 4 (Lv3-4) -> 5 (L5 Max)   |   TP Cost: 30 -> 48   |   Speed: 0.9x'),
    
    ('TechniqueSkillData_0098.bin', 'Mercidarian',
     'Summon Mercidarian for random long-range stab damage to all foes.',
     'ATK: 100% -> 104 -> 108 -> 112 -> 118 -> 123 -> 128 -> 133 -> 138 -> 143% (L10)\nTurns: 2 (Lv1-4) -> 3 (Lv5-7) -> 4 (Lv8-10)   |   TP Cost: 42 -> 70   |   Speed: 0.75x'),
    
    ('TechniqueSkillData_0100.bin', 'Musiy',
     'Summon Musiy for immediate single-target attack magic.',
     'Pwr: 180 -> 240 -> 310 -> 390 -> 480 -> 585 -> 700 (L7 Max)\nTurns: 4   |   TP Cost: 38 (+4-6/Lv) -> 68   |   Speed: 0.82x -> 0.92x'),
    
    ('TechniqueSkillData_0049.bin', 'Star Dust Arrow',
     'Bow skill. Shower enemies with a rain of arrows across multiple turns.',
     'ATK: 100% -> 102 -> 104 -> 106 -> 108 -> 110 -> 112 -> 114 -> 117 -> 120% (L10)\n1-3 hits   |   Turns: 2 (Lv1-9) -> 3 (L10 Max)   |   TP Cost: 35 (+3/Lv) -> 62'),
]

for fn, name, desc, lvup in tests:
    b = tech_archive[fn]
    full = desc + '\n' + lvup
    lines = full.split('\n')
    max_len = max(len(l) for l in lines)
    probs, ver, loose = check_skill_text('Technique', b, lvup)
    print(f"{name}: probs={probs}, ver={ver}, loose={loose}, max_len={max_len}, lines={len(lines)}")

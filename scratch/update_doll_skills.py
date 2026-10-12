import os
import openpyxl

XLSX_PATH = os.path.join(os.path.dirname(__file__), '..', 'data_tables', 'qol_skill_text.xlsx')

UPDATES = {
    'TechniqueSkillData_0095.bin': {
        'desc': 'Summon Spartan for short-range bash damage.',
        'lvup': (
            'ATK: 144% -> 147 -> 150 -> 154 -> 158 -> 162 -> 166 -> 170 -> 175 -> 180% (L10)\n'
            'Turns: 3 (Lv1-3) -> 4 (Lv4-6) -> 5 (Lv7-9) -> 6 (L10)   |   TP Cost: 20 -> 42'
        ),
    },
    'TechniqueSkillData_0096.bin': {
        'desc': 'Summon Oracles for mid-range INT-based damage and possible paralysis.',
        'lvup': (
            'ATK: 126% (+2-5%/Lv) -> 157%   |   Paralysis: 30% (+3-5%/Lv) -> 64% (L10)\n'
            'Turns: 3 (Lv1-4) -> 4 (Lv5-8) -> 5 (Lv9-10) | TP Cost: 24 -> 48 | Speed: 0.9x'
        ),
    },
    'TechniqueSkillData_0097.bin': {
        'desc': "Summon Catalina to heal allies' HP.",
        'lvup': (
            'Heal Power: 4 -> 6 -> 8 -> 10 -> 12 (L1-5 Max)\n'
            'Turns: 3 (Lv1-2) -> 4 (Lv3-4) -> 5 (L5 Max) | TP Cost: 30 -> 48 | Speed: 0.9x'
        ),
    },
    'TechniqueSkillData_0098.bin': {
        'desc': 'Summon Mercidarian for random long-range stab damage to all foes.',
        'lvup': (
            'ATK: 100% -> 104 -> 108 -> 112 -> 118 -> 123 -> 128 -> 133 -> 138 -> 143% (L10)\n'
            'Turns: 2 (Lv1-4) -> 3 (Lv5-7) -> 4 (Lv8-10) | TP Cost: 42 -> 70 | Speed: 0.75x'
        ),
    },
    'TechniqueSkillData_0100.bin': {
        'desc': 'Summon Musiy for immediate single-target attack magic.',
        'lvup': (
            'Pwr: 180 -> 240 -> 310 -> 390 -> 480 -> 585 -> 700 (L7 Max)\n'
            'Turns: 4   |   TP Cost: 38 (+4-6/Lv) -> 68   |   Speed: 0.82x -> 0.92x'
        ),
    },
    'TechniqueSkillData_0049.bin': {
        'desc': 'Bow skill. Shower enemies with a rain of arrows across multiple turns.',
        'lvup': (
            'ATK: 100% -> 102 -> 104 -> 106 -> 108 -> 110 -> 112 -> 114 -> 117 -> 120% (L10)\n'
            '1-3 hits   |   Turns: 2 (Lv1-9) -> 3 (L10 Max)   |   TP Cost: 35 (+3/Lv) -> 62'
        ),
    },
}

wb = openpyxl.load_workbook(XLSX_PATH)
ws = wb['Skills']
header = [c.value for c in ws[1]]
col_fn = header.index('Filename')
col_desc = header.index('QoL_Desc')
col_lvup = header.index('QoL_LvUp')
col_edited = header.index('Edited')
col_cov = header.index('Coverage') if 'Coverage' in header else None
col_phrases = header.index('Phrases_Kept_As_Vanilla') if 'Phrases_Kept_As_Vanilla' in header else None
col_tables = header.index('Tables_Not_Shown') if 'Tables_Not_Shown' in header else None

count = 0
for row in ws.iter_rows(min_row=2):
    fn = row[col_fn].value
    if fn in UPDATES:
        u = UPDATES[fn]
        row[col_desc].value = u['desc']
        row[col_lvup].value = u['lvup']
        row[col_edited].value = 'yes'
        if col_cov is not None:
            row[col_cov].value = 'Full'
        if col_phrases is not None:
            row[col_phrases].value = None
        if col_tables is not None:
            row[col_tables].value = None
        count += 1

wb.save(XLSX_PATH)
print(f"Updated {count} doll skills in {XLSX_PATH}")

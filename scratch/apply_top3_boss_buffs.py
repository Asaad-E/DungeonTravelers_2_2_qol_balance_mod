import openpyxl
import os
import sys

BASE_DIR = 'mod_project'
BC_PATH = os.path.join(BASE_DIR, 'data_tables', 'balance_changes.xlsx')

wb = openpyxl.load_workbook(BC_PATH)
ws = wb['Changes']

# Check if G094 is already present
existing_ids = {row[0].value for row in ws.iter_rows(min_row=2)}

new_rows = [
    # C10: Countess of Vrachia (ID 1002) - +15% HP, +4% ATK/DEF
    ('G094', 'enemies', '1002 Countess of Vrachia (C10)', 'hp', None, 1991, 2289, 'L01', 'F15',
     'Top 3 easiest boss buff (user request): C10 Countess of Vrachia HP +15% (1991 -> 2289) to prevent instant trivialization across all parties while preserving 100% win rate parity (rnds 10.5r -> 15.2r).', '2026-10-11', 'decided'),
    ('G095', 'enemies', '1002 Countess of Vrachia (C10)', 'atk', None, 70, 73, 'L01', 'F15',
     'Top 3 easiest boss buff: C10 Countess of Vrachia ATK +4% (70 -> 73) for moderate combat pressure.', '2026-10-11', 'decided'),
    ('G096', 'enemies', '1002 Countess of Vrachia (C10)', 'def', None, 54, 56, 'L01', 'F15',
     'Top 3 easiest boss buff: C10 Countess of Vrachia DEF +4% (54 -> 56).', '2026-10-11', 'decided'),

    # C13: Eros (ID 760) - +20% HP, +5% ATK/DEF
    ('G097', 'enemies', '760 Eros (C13)', 'hp', None, 2277, 2732, 'L01', 'F15',
     'Top 3 easiest boss buff (user request): C13 Eros HP +20% (2277 -> 2732) to extend midgame boss duration moderately from 9.3r to 10.8r across all 5 parties.', '2026-10-11', 'decided'),
    ('G098', 'enemies', '760 Eros (C13)', 'atk', None, 57, 60, 'L01', 'F15',
     'Top 3 easiest boss buff: C13 Eros ATK +5% (57 -> 60).', '2026-10-11', 'decided'),
    ('G099', 'enemies', '760 Eros (C13)', 'def', None, 55, 58, 'L01', 'F15',
     'Top 3 easiest boss buff: C13 Eros DEF +5% (55 -> 58).', '2026-10-11', 'decided'),

    # C24: Afanc (ID 825) - +25% HP, +7% ATK/DEF
    ('G100', 'enemies', '825 Afanc (C24)', 'hp', None, 4582, 5728, 'L01', 'F15',
     'Top 3 easiest boss buff (user request): C24 Afanc HP +25% (4582 -> 5728) to bring boss duration from 7.9r to 9.6r, keeping win rate at 99% while preventing 4-turn trivial melts by Tier 3 physical burst.', '2026-10-11', 'decided'),
    ('G101', 'enemies', '825 Afanc (C24)', 'atk', None, 152, 163, 'L01', 'F15',
     'Top 3 easiest boss buff: C24 Afanc ATK +7% (152 -> 163).', '2026-10-11', 'decided'),
    ('G102', 'enemies', '825 Afanc (C24)', 'def', None, 120, 129, 'L01', 'F15',
     'Top 3 easiest boss buff: C24 Afanc DEF +7% (120 -> 129).', '2026-10-11', 'decided'),
]

added = 0
for row in new_rows:
    if row[0] not in existing_ids:
        ws.append(row)
        added += 1
        print(f"Added {row[0]}: {row[2]} {row[3]} {row[5]} -> {row[6]}")
    else:
        print(f"Already exists: {row[0]}")

if added > 0:
    wb.save(BC_PATH)
    print(f"Successfully saved {added} rows to {BC_PATH}")
else:
    print("No rows added.")

import openpyxl
import os
import sys

base_dir = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project'
rules_path = os.path.join(base_dir, 'data_tables', 'qol_rules.xlsx')

wb = openpyxl.load_workbook(rules_path)
ws = wb['ShortItems']

# Check if Dark Cloud is already in ShortItems
found = False
for row in ws.iter_rows(values_only=True):
    if row[0] == 'Dark Cloud':
        found = True
        print("Dark Cloud already in ShortItems:", row)
        break

if not found:
    print("Dark Cloud NOT in ShortItems. Adding it!")
    ws.append(['Dark Cloud', 'A roiling mass of darkness.'])
    wb.save(rules_path)
    print("Added Dark Cloud to ShortItems and saved qol_rules.xlsx.")

import openpyxl

rules_path = 'mod_project/data_tables/qol_rules.xlsx'
wb = openpyxl.load_workbook(rules_path)
ws_effects = wb['ItemEffects']

for row in ws_effects.iter_rows(min_row=2):
    if row[0].value == 56:
        print("Current Type 56:", row[1].value)
    if row[0].value == 17:
        print("Current Type 17:", row[1].value)

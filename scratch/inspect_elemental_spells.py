import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/skills.xlsx', read_only=True)
ws = wb.active

for row in ws.iter_rows(values_only=True):
    cat = row[1]
    name = row[3]
    max_lv = row[4]
    tp = row[5]
    desc = row[6]
    mod_lvup = row[9]
    if cat == 'Magic' and ('damage' in str(desc).lower() or 'elemental' in str(desc).lower() or 'fire' in str(desc).lower() or 'water' in str(desc).lower()):
        print(f"{name:<18} | MaxLv: {max_lv:<2} | TP: {tp}")
        if mod_lvup:
            print(f"   ModLvUp: {mod_lvup}")

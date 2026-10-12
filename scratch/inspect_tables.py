import openpyxl
import os

def check_table(filename, sheetname=None, max_r=5):
    path = os.path.join('mod_project/data_tables', filename)
    if not os.path.exists(path):
        print(f"File {path} not found")
        return
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb[sheetname] if sheetname else wb.active
    print(f"\n=== {filename} ===")
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            print("Headers:", row[:10])
        elif i <= max_r:
            print(f"Row {i}:", row[:10])
        else:
            break

check_table('equipment.xlsx')
check_table('enchants.xlsx')
check_table('grand_seals.xlsx')
check_table('items.xlsx')
check_table('food_menu.xlsx')
check_table('joint_skills.xlsx')
check_table('party_skills.xlsx')

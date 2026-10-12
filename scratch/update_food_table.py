import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/food_menu.xlsx')
ws = wb['FoodMenu']

for row in ws.iter_rows(min_row=2):
    name = row[1].value
    if name == 'Ultimate Champon':
        row[4].value = 'Restore 80% HP and TP + Stab/Slash/Bash Guard (+10% Stats, 900 Steps).'
    elif name == "Heaven's Ramen":
        row[4].value = 'Restore 100% HP and TP. Cure ailments + Insurance (+10% Stats, 900 Steps).'

wb.save('mod_project/data_tables/food_menu.xlsx')
print('Successfully updated food_menu.xlsx!')

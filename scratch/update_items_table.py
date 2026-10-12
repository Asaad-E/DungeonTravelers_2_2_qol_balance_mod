import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/items.xlsx')
ws = wb['Items']

updates = {
    12: "Restore an ally's TP (small). The flavor is good as well (+50 TP).",
    13: "Restore an ally's TP (medium). Fairies love 'em (+100 TP).",
    14: "Restore an ally's TP (large). Intimidating but delicious (Full TP).",
    17: "Revive a fallen ally. Considerably bitter aftertaste (Revive 30% HP).",
    497: "Cloying, syrupy drink (Party: +250 HP/TP, Clear Debuffs)."
}

count = 0
for row in ws.iter_rows(min_row=2):
    idx = row[0].value
    if idx in updates:
        row[5].value = updates[idx]
        count += 1

wb.save('mod_project/data_tables/items.xlsx')
print(f'Successfully updated {count} items in items.xlsx!')

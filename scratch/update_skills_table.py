import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/skills.xlsx')
ws = wb['Skills']

# Master Spells pierces 50 Elemental Resistance
master_spells = ['Crimson Flare', 'Cocytus', 'Muon Plasma', 'Tempest', 'Gaia Crush']

updated = 0
for row in ws.iter_rows(min_row=2):
    cat = row[1].value
    name = row[3].value
    if cat == 'Magic' and name in master_spells:
        desc = row[8].value
        if desc and 'Pierces 50' not in desc:
            row[8].value = desc.rstrip('.') + '. Pierces 50 Elemental Res.'
            updated += 1
    elif cat == 'Passive' and name == 'Concentrate':
        lvup = row[9].value
        if lvup and '80% Crit Interrupt Res' not in lvup:
            row[9].value = "Interruption Resist: +20% -> +50% (+7.5%/Lv) | 80% Crit Interrupt Res at Lv 5"
            updated += 1
    elif cat == 'Passive' and name == 'Double Puppet':
        desc = row[8].value
        if desc and 'Dolls gain Guts' not in desc:
            row[8].value = "Become capable of controlling two summoned dolls at once. Dolls gain Guts."
            updated += 1

wb.save('mod_project/data_tables/skills.xlsx')
print(f'Successfully updated {updated} skills in skills.xlsx!')

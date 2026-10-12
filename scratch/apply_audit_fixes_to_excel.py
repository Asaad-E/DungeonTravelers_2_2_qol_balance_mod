import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/balance_changes.xlsx')
ws = wb['Changes']

# 1. Update G034 - G093 for Stage 15 common monsters
# Macha: G034-G036, Purski: G058-G060, Highway Star: G091-G093
updates_g = {
    'G034': 8990,  # HP +15% instead of +95% (was 15263)
    'G035': 363,   # ATK vanilla 363 (was 613)
    'G036': 140,   # INT vanilla 132 -> 140 (was 223)
    'G058': 3100,  # Purski HP +16% (was 5212)
    'G059': 335,   # Purski ATK (was 529)
    'G060': 115,   # Purski INT (was 183)
    'G091': 6750,  # Highway Star HP +15% (was 11448)
    'G092': 360,   # Highway Star ATK (was 588)
    'G093': 135,   # Highway Star INT (was 216)
}

for row in ws.iter_rows(min_row=9):
    code = row[0].value
    if code in updates_g:
        row[6].value = updates_g[code]
        print(f'Updated {code}: new value = {row[6].value}')

# 2. Add W042: Slave\'s Torc Double EXP
max_row = ws.max_row
ws.cell(max_row + 1, 1).value = 'W042'
ws.cell(max_row + 1, 2).value = 'equipment'
ws.cell(max_row + 1, 3).value = "744 Slave's Torc"
ws.cell(max_row + 1, 4).value = 'Enchant 3 (0x68)'
ws.cell(max_row + 1, 5).value = None
ws.cell(max_row + 1, 6).value = 66
ws.cell(max_row + 1, 7).value = 275
ws.cell(max_row + 1, 8).value = 'L14'
ws.cell(max_row + 1, 9).value = 'F92'
ws.cell(max_row + 1, 10).value = '2026-10-11'
ws.cell(max_row + 1, 11).value = 'decided'
print(f'Added W042 at row {max_row + 1}')

# 3. Restore Sleep immunity bit (0x8) in rows A001-A073
sleep_bit_restores = {
    'A021': '0x14ef', # Scanner
    'A023': '0x16ef', # Martial Artist
    'A026': '0x326b', # Eros
    'A028': '0x14ef', # Calliope
    'A030': '0x32eb', # Siesta
    'A034': '0x36ef', # Moby Dick
    'A036': '0x11ef', # Iron Maiden
    'A037': '0x12ef', # Dragon Papi
    'A038': '0x12ef', # Death Cataphract
    'A040': '0x35f2', # Samael
    'A042': '0x36ee', # Melek Taus
    'A044': '0x36f6', # Demiurge
    'A052': '0x11ea', # Countess of Vrachia
    'A055': '0x31ea', # Warden of the Wall
    'A058': '0x35ee', # Trafficker Twinny
    'A060': '0x1aee', # Michelle
    'A062': '0x1aee', # Heartless Avenger
    'A063': '0x36ee', # Demon God Fried
    'A064': '0x316a', # Doll
    'A073': '0x177e', # Queen of Darkness
}

for row in ws.iter_rows(min_row=9):
    code = row[0].value
    if code in sleep_bit_restores:
        row[6].value = sleep_bit_restores[code]
        print(f'Restored Sleep immunity for {code}: {row[6].value}')

wb.save('mod_project/data_tables/balance_changes.xlsx')
print('Successfully saved balance_changes.xlsx!')

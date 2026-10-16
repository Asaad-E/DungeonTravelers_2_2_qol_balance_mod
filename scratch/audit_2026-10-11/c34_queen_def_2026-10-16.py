"""C34 Queen of Darkness: DEF x1.15 (new rows G120, G121), decided 2026-10-16, with the HP x1.15 of G114 and G115."""
import os
import openpyxl

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'balance_changes.xlsx')

WHY = ('The length of C34 back into the window of vanilla (R08) with HP x1.15 (G114, G115): DEF x1.15 (decided 2026-10-16). Reference party, '
       '400 runs: vanilla 42.7, HP x1.15 alone 27.6 (under the window), with DEF x1.15 35.1, lowest HP 60% (vanilla 61%). dtcli class-search '
       'final C34 boss with three times the bag of the sheet Kit on both sides (a player who comes ready for the boss): 1.2% of the 14,835 '
       'final-class parties 10 or more points under vanilla, the worst confirmed 38 points; mean wins 79% vanilla, 92% variant; parties without '
       'Diva, Mistress or Etoile 61% and 81%. With the bag of the model (kit_count 8) those parties still lose some; DEF x1.2 left 1.6%, the '
       'worst 50 points.')
ROWS = [
    ('G120', 'enemies', '1036 Queen of Darkness (C34)', 'def', None, 175, 201, 'L01', 'R08, R10', WHY, '2026-10-16', 'built'),
    ('G121', 'enemies', '1037 Queen of Darkness (C34)', 'def', None, 183, 210, 'L01', 'R08, R10', WHY, '2026-10-16', 'built'),
]

wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
head = [c.value for c in ws[1]]
ids = {ws.cell(r, 1).value: r for r in range(2, ws.max_row + 1)}
assert head[:12] == ['ID', 'Table', 'Record', 'Field', 'Level', 'Vanilla', 'New', 'Lever', 'Serves', 'Why', 'Decided', 'State'], head
# the new rows go after G119, the last row of the G block
at = ids['G119'] + 1
for k, row in enumerate(ROWS):
    if row[0] in ids:
        for col, value in enumerate(row, start=1):
            ws.cell(ids[row[0]], col).value = value
        continue
    ws.insert_rows(at + k)
    for col, value in enumerate(row, start=1):
        ws.cell(at + k, col).value = value
wb.save(PATH)
print('written', [r[0] for r in ROWS])

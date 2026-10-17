"""The random-enemy rows of 2026-10-16 (walk_enemies_2026-10-16.py) dropped (decided 2026-10-17, audit finding C-01): the script took
every zone of each floor, not only the zones near the level of the checkpoint that the walks play, so it raised enemies of the early
story (the floor of P08 holds enemies of level 1) and enemies of fixed battles. Corrected to the near zones without the enemies of fixed
battles, the rows changed almost nothing; and with Cook back in the maid plans the walks are within +1 to +4 points of vanilla for five
of the six parties without them."""
import os
import openpyxl

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'balance_changes.xlsx')
WHY = (' | Dropped 2026-10-17 (audit C-01): every zone of the floor was taken, raising enemies of the early story and of fixed battles; '
       'the corrected rows changed almost nothing, and the walks are within +1 to +4 points of vanilla without them.')
wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
n = 0
for r in range(2, ws.max_row + 1):
    if ws.cell(r, 2).value == 'enemies' and ws.cell(r, 11).value == '2026-10-16' and 'walk of 30' in str(ws.cell(r, 10).value) \
            and ws.cell(r, 12).value == 'built':
        ws.cell(r, 12).value = 'dropped'
        ws.cell(r, 10).value = str(ws.cell(r, 10).value) + WHY
        n += 1
assert n == 225, n
wb.save(PATH)
print('dropped', n)

"""One-off edit (decided 2026-10-16): smooth curves where a level gave nothing. Poison, Petrify and Lullaby reached their
cap before level 5, so the last levels only cost more; they now reach it at level 5 (whole percents, as the game rolls
value * 100). Circle Heal healed as much at level 9 as at 10; it now rises evenly from 10 to 14 (the top level as before)."""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
CURVES = {   # first row id of the run, values by level, why
    'A189': ([0.9, 0.91, 0.93, 0.94, 0.95], 'Poison reaches its 95% at level 5, every level a little more (it reached it at level 3)'),
    'A214': ([0.84, 0.86, 0.87, 0.89, 0.9], 'Petrify reaches its 90% at level 5, every level a little more (it reached it at level 4)'),
    'A234': ([0.84, 0.87, 0.9, 0.92, 0.95], 'Lullaby reaches its 95% at level 5, every level a little more (it reached it at level 4)'),
    # Circle Heal: first an even 10 - 14 here; replaced the same day by circle_heal_2026-10-16.py (0.5 a level, 10 to 14.5)
}

wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
ids = [ws.cell(r, 1).value for r in range(2, ws.max_row + 1)]
done = 0
for first, (values, note) in CURVES.items():
    start = ids.index(first) + 2
    record = ws.cell(start, 3).value
    for level, value in enumerate(values, 1):
        r = start + level - 1
        assert ws.cell(r, 3).value == record and ws.cell(r, 5).value == level, (first, level)
        ws.cell(r, 7).value = value
        why = ws.cell(r, 10).value or ''
        if note not in why:
            ws.cell(r, 10).value = f'{why} | 2026-10-16: {note}'
        ws.cell(r, 11).value = '2026-10-16'
        done += 1
wb.save(PATH)
print('rows', done)

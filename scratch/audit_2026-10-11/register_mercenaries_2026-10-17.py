"""Criticisms J13 and F94 (mercenaries) get the figures of dtcli mercenary-battery (2026-10-17, docs/generated/MERCENARY_BATTERY.md):
each mercenary in the place of the summon of the grand sealbook, in the reference party and the five battery parties, from her first
level, at every checkpoint of the difficulty curve and on rows of random battles."""
import json
import os
import openpyxl

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
PATH = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
rows = json.load(open(os.path.join(ROOT, 'docs', 'generated', 'mercenary_battery', 'part_1.json'), encoding='utf-8'))
count = {}
for r in rows:
    count[r['verdict']] = count.get(r['verdict'], 0) + 1
best = sorted(rows, key=lambda r: -r['serves'] / r['cells'])[:4]
worst = [r['guest'] for r in rows if r['verdict'] == 'hurts']
TEXT = ('2026-10-17, dtcli mercenary-battery (docs/generated/MERCENARY_BATTERY.md; each mercenary in the place of the summon of the grand '
        'sealbook, in the reference party and the five battery parties, from her first level, at the bosses of the curve and on rows of random '
        'battles; 20 runs a cell, the 3 best at 200): %d mercenaries, %s. Against the summon most lose a little on the mean (%d of %d below it), '
        'and each serves somewhere: best %s; worse than the summon in most cells: %s. The summon is the stronger use of the slot, a mercenary '
        'a choice for some fights; the four of level 95 and more (Arjuna, Citlalinicue, Marduk, Yoshitsune) join after the last boss measured.'
        % (len(rows), ', '.join('%d %s' % (n, v) for v, n in sorted(count.items())), sum(1 for r in rows if r['mean_wins'] < 0), len(rows),
           ', '.join('%s %d%%' % (r['guest'], round(100 * r['serves'] / r['cells'])) for r in best), ', '.join(worst)))
wb = openpyxl.load_workbook(PATH)
ws = wb['Criticisms']
head = [c.value for c in ws[1]]
col = {n: i + 1 for i, n in enumerate(head)}
for r in range(2, ws.max_row + 1):
    if ws.cell(r, col['ID']).value in ('J13', 'F94'):
        cell = ws.cell(r, col['Balance_Result'])
        if 'mercenary-battery' not in str(cell.value):
            cell.value = (str(cell.value).rstrip() + ' ' if cell.value else '') + TEXT
wb.save(PATH)
print(TEXT)

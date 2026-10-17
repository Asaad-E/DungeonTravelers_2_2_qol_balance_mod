"""Three mercenaries a little stronger (decided 2026-10-17): in dtcli mercenary-battery they were worse than the summon in most cells.
Every stage of Natalia and Rebecca x1.15, of Riesco x1.2, in ATK, DEF, INT and RES: all three niche (Natalia serves in 20% of the
cells, Rebecca 21%, Riesco 24%), still a little below the summon on the mean. The records 101, 102 and 103 (ids 0 - 2, characters 300 -
302, a number for a name) look like placeholders of the data, not mercenaries a player hires: left as they are."""
import json
import os
import openpyxl

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
PATH = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
DECIDED = '2026-10-17'
PLAN = {'Natalia': 1.15, 'Rebecca': 1.15, 'Riesco': 1.2}
STATS = ['atk', 'def', 'int', 'res']   # the builder writes the six stats of a guest ally, not her HP (which did not move the measure)
npcs = json.load(open(os.path.join(ROOT, 'build', 'engine_snapshot.json'), encoding='utf-8'))['sides']['vanilla']['npcs']

wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
head = [c.value for c in ws[1]]
assert head[:12] == ['ID', 'Table', 'Record', 'Field', 'Level', 'Vanilla', 'New', 'Lever', 'Serves', 'Why', 'Decided', 'State'], head
existing = {(ws.cell(r, 3).value, ws.cell(r, 4).value): r for r in range(2, ws.max_row + 1) if ws.cell(r, 2).value == 'npcs' and ws.cell(r, 12).value == 'built'}
ids = [ws.cell(r, 1).value for r in range(2, ws.max_row + 1)]
nxt = 1 + max(int(k[1:]) for k in ids if k and str(k).startswith('V'))
row = ws.max_row + 1
scaled = added = 0
for n in sorted((x for x in npcs if x['name'] in PLAN), key=lambda x: (x['name'], x['level'])):
    f = PLAN[n['name']]
    why = ('%s was worse than the summon in most cells of dtcli mercenary-battery (2026-10-17); every stage x%g in ATK, DEF, INT and RES '
           'made her niche, still a little below the summon on the mean.' % (n['name'], f))
    record = '%d %s (level %d)' % (n['id'], n['name'], n['level'])
    for stat in STATS:
        at = existing.get((record, stat))
        if at:
            ws.cell(at, 7).value = round(ws.cell(at, 7).value * f)
            ws.cell(at, 10).value = str(ws.cell(at, 10).value) + ' ' + why
            scaled += 1
            continue
        for c, v in enumerate(('V%03d' % nxt, 'npcs', record, stat, None, n[stat], round(n[stat] * f), 'L44', 'F94, J13', why, DECIDED, 'built'), start=1):
            ws.cell(row, c).value = v
        row += 1
        nxt += 1
        added += 1
wb.save(PATH)
print('scaled', scaled, 'added', added)

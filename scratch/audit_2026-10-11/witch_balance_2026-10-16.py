"""The Witch brought into the band of the other classes (Criticisms S07, decided 2026-10-16): her INT x0.9 at every level (growth row
18 of ClassLevelData) and the five basic spells of the Magic User at their levels 6 - 10 x0.85 power.

dtcli class-search final C30, C34, C38, C40 boss, 3,000 parties a boss: in vanilla the Witch is in 97% of the fastest 5% of the parties
(the next class 65%); with these rows in 75% (the next 74%), her parties win 49.9% (the median of the other classes 52.4%). Her INT x0.85
or less took her out of the top in speed and to the bottom in wins; the basic spells x0.85 at every level gave the same as at 6 - 10, and
the levels 1 - 5 the early Magic User casts stay as they are."""
import os
import sys
import openpyxl

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import class_data                                   # noqa: E402

PATH = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
DECIDED = '2026-10-16'
WHY = ('The Witch into the band of the other classes (S07, decided 2026-10-16): in vanilla she was in 97% of the fastest final-class '
       'parties (the next class 65%). Her INT x0.9 (growth row 18) and the basic spells at levels 6 - 10 x0.85: class-search final C30 '
       '- C40 boss, 3,000 parties a boss: in 75% of the fastest (the next class 74%), her parties win 49.9% (median of the others 52.4%); '
       'x0.85 or less put her last in wins. She is pushed to her strong spells, which are her own.')
SPELLS = {'Fireball': 143, 'Ice Edge': 147, 'Thunderbolt': 151, 'Air Cutter': 155, 'Stone Hammer': 159}

growth = class_data.growth()[18]
names = class_data.class_names()
NEW = []
for level in range(1, class_data.LEVELS + 1):
    old = growth[level - 1]['int']
    NEW.append(('class_growth', f'18 {names[16]}', 'int', level, old, round(old * 0.9), 'L10', 'S07', WHY))

wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
head = [c.value for c in ws[1]]
assert head[:12] == ['ID', 'Table', 'Record', 'Field', 'Level', 'Vanilla', 'New', 'Lever', 'Serves', 'Why', 'Decided', 'State'], head
ids = {ws.cell(r, 1).value: r for r in range(2, ws.max_row + 1) if ws.cell(r, 1).value}
# the vanilla power of the basic spells from the snapshot of the engine (effect 1, levels 1 - 10)
import json                                          # noqa: E402
snap = json.load(open(os.path.join(ROOT, 'build', 'engine_snapshot.json'), encoding='utf-8'))['sides']['vanilla']['skills']
for name, sid in SPELLS.items():
    skill = next(s for s in snap if s['id'] == sid)
    power = next(e[2] for e in skill['effects'] if e[0] == 1)
    for level in range(6, 11):
        NEW.append(('skills', f'Magic {sid} {name}', 'effect 1', level, power[level - 1], round(power[level - 1] * 0.85), 'L12', 'S07', WHY))
first = 1 + max(int(k[1:]) for k in ids if str(k).startswith('V'))
row = ws.max_row + 1
for k, values in enumerate(NEW):
    rid = 'V%03d' % (first + k)
    for c, value in enumerate((rid,) + values + (DECIDED, 'built'), start=1):
        ws.cell(row, c).value = value
    row += 1
wb.save(PATH)
print('written V%03d - V%03d' % (first, first + len(NEW) - 1), len(NEW), 'rows')

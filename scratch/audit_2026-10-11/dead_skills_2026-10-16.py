"""Three dead skills of the battery raised (decided 2026-10-16), measured by dtcli skill-battery with variants (20 runs a cell, the 3 best
at 200, the five rules and the walk then the boss): Sun Veil TP x0.75, speed and chant speed x1.25 (dead -> niche, fights up to 23%
shorter); Tinker Squash TP x0.6 (dead -> good, 37% of the cells: 98 of 101 bosses are immune to its turn delay, so its worth is its hit);
Mind's Eye 12% -> 18% (dead at the edge -> good, 38%). The values of the variant rows already there are scaled on their New."""
import json
import os
import openpyxl

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
PATH = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
DECIDED = '2026-10-16'
WHY = {
    'Guards': ('The three guards of the Sage were dead in the skill battery (2026-10-16): +36 resistance is 18% less damage of one kind of '
               'blow. Resistance x1.7 and TP x0.75; cast where the foes strike with that blow (condition foes_attack) they are niche: few '
               'foes use one kind of blow most of the time.'),
    'Sun Veil': 'Sun Veil was dead in the skill battery (2026-10-16): TP x0.75, speed and chant speed x1.25 made it niche, fights up to 23% shorter.',
    'Tinker Squash': ('Tinker Squash was dead in the skill battery (2026-10-16): 98 of 101 story bosses are immune to its turn delay, so its '
                      'worth is its hit; TP x0.6 made it good (37% of the cells).'),
    "Mind's Eye": "Mind's Eye was dead at the edge in the skill battery (2026-10-16): 12% -> 18% made it good (38% of the cells).",
}
# (record, field, scale, digits, key of the vanilla array or (effect id), why)
PLAN = [
    ('Magic 184 Stab Guard', 'effect 184', 1.7, 0, 184, 'Guards'), ('Magic 184 Stab Guard', 'TP cost', 0.75, 0, 'tp', 'Guards'),
    ('Magic 185 Slash Guard', 'effect 185', 1.7, 0, 185, 'Guards'), ('Magic 185 Slash Guard', 'TP cost', 0.75, 0, 'tp', 'Guards'),
    ('Magic 186 Bash Guard', 'effect 186', 1.7, 0, 186, 'Guards'), ('Magic 186 Bash Guard', 'TP cost', 0.75, 0, 'tp', 'Guards'),
    ('Magic 195 Sun Veil', 'TP cost', 0.75, 0, 'tp', 'Sun Veil'),
    ('Magic 195 Sun Veil', 'speed factor', 1.25, 2, 'speed', 'Sun Veil'),
    ('Magic 195 Sun Veil', 'chant speed factor', 1.25, 2, 'cast', 'Sun Veil'),
    ('Technique 88 Tinker Squash', 'TP cost', 0.6, 0, 'tp', 'Tinker Squash'),
    ("Passive 260 Mind's Eye", 'effect 250', 1.5, 2, 250, "Mind's Eye"),
]
SERVES = {'Guards': 'T06', 'Sun Veil': 'F47', 'Tinker Squash': 'J31', "Mind's Eye": 'T06'}   # T06: the theme of the skills (no row names it)
snap = {s['id']: s for s in json.load(open(os.path.join(ROOT, 'build', 'engine_snapshot.json'), encoding='utf-8'))['sides']['vanilla']['skills']}

import sys
ONLY = set(sys.argv[1:]) or set(WHY)
wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
head = [c.value for c in ws[1]]
assert head[:12] == ['ID', 'Table', 'Record', 'Field', 'Level', 'Vanilla', 'New', 'Lever', 'Serves', 'Why', 'Decided', 'State'], head
existing = {}
for r in range(2, ws.max_row + 1):
    if ws.cell(r, 12).value == 'built':
        existing[(ws.cell(r, 3).value, ws.cell(r, 4).value, ws.cell(r, 5).value)] = r
ids = [ws.cell(r, 1).value for r in range(2, ws.max_row + 1)]
nxt = 1 + max(int(k[1:]) for k in ids if k and str(k).startswith('V'))
row = ws.max_row + 1
scaled = added = 0
for record, field, f, digits, key, name in [p for p in PLAN if p[5] in ONLY]:
    sid = int(record.split()[1])
    values = snap[sid][key] if isinstance(key, str) else next(e[2] for e in snap[sid]['effects'] if e[0] == key)
    for level, old in enumerate(values, start=1):
        at = existing.get((record, field, level))
        if at:
            cur = ws.cell(at, 7).value
            ws.cell(at, 7).value = round(cur * f) if digits == 0 else round(cur * f, digits)
            ws.cell(at, 10).value = str(ws.cell(at, 10).value) + ' ' + WHY[name]
            scaled += 1
            continue
        new = round(old * f) if digits == 0 else round(old * f, digits)
        vals = ('V%03d' % nxt, 'skills', record, field, level, old, new, 'L12', SERVES[name], WHY[name], DECIDED, 'built')
        for c, value in enumerate(vals, start=1):
            ws.cell(row, c).value = value
        row += 1
        nxt += 1
        added += 1
wb.save(PATH)
print('scaled', scaled, 'added', added)

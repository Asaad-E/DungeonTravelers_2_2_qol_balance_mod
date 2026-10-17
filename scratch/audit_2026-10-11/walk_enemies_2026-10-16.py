"""The random enemies of five floors a little stronger (decided 2026-10-16: too much had been given to the player). dtcli walk-parties,
rows of 30 random battles with one bag, the reference party and the five battery parties: on these floors 3 of the 6 parties walked
easier than in vanilla (wins +10 to +18 points in the mean) and none harder. The factor of each floor is the one that brought the mean
of the six parties back to vanilla in that walk: C26 ATK x1.03; C28 ATK and DEF x1.05; C32 ATK x1.1; C37 ATK x1.1; P08 ATK x1.2 and DEF
x1.1. An enemy met on several of these floors takes the factor of the first in the story. The records are shared with other floors and
some fixed battles, so the whole is checked by the curve, the battery and the walks."""
import json
import os
import openpyxl

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
PATH = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
DECIDED = '2026-10-16'
PLAN = [('C26', {'atk': 1.03}), ('C28', {'atk': 1.05, 'def': 1.05}), ('C32', {'atk': 1.1}), ('C37', {'atk': 1.1}),
        ('P08', {'atk': 1.2, 'def': 1.1})]
STATS = ['atk', 'def', 'int', 'res', 'dex', 'agi']

snap = json.load(open(os.path.join(ROOT, 'build', 'engine_snapshot.json'), encoding='utf-8'))['sides']['vanilla']
enemies = {e['id']: e for e in snap['enemies']}
setup = openpyxl.load_workbook(os.path.join(ROOT, 'data_tables', 'sim_setup.xlsx'), read_only=True)['Checkpoints']
floor_of = {r[0]: r[3] for r in setup.iter_rows(values_only=True) if r[0]}
taken = {}
for cid, scale in PLAN:
    for z in snap['floors']:
        if z['name'].split(' zone')[0] != floor_of[cid]:
            continue
        for f in z['formations']:
            for eid, _ in f['enemies']:
                taken.setdefault(eid, (cid, scale))

wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
head = [c.value for c in ws[1]]
assert head[:12] == ['ID', 'Table', 'Record', 'Field', 'Level', 'Vanilla', 'New', 'Lever', 'Serves', 'Why', 'Decided', 'State'], head
existing = {}
for r in range(2, ws.max_row + 1):
    if ws.cell(r, 2).value == 'enemies' and ws.cell(r, 12).value == 'built':
        existing[(int(str(ws.cell(r, 3).value).split()[0]), ws.cell(r, 4).value)] = r
ids = [ws.cell(r, 1).value for r in range(2, ws.max_row + 1)]
nxt = 1 + max(int(k[1:]) for k in ids if k and str(k).startswith('V'))
row = ws.max_row + 1
scaled = added = 0
for eid in sorted(taken):
    cid, scale = taken[eid]
    e = enemies[eid]
    why = ('Random enemy of the floor of %s made a little stronger (2026-10-16): the walk of 30 random battles was easier than vanilla '
           'for 3 of 6 parties; %s brought the mean back to vanilla (dtcli walk-parties).' % (cid, ', '.join('%s x%g' % kv for kv in scale.items())))
    for stat, f in scale.items():
        old = e[stat] if stat == 'hp' else e[stat]
        at = existing.get((eid, stat))
        if at:
            ws.cell(at, 7).value = round(ws.cell(at, 7).value * f)
            ws.cell(at, 10).value = str(ws.cell(at, 10).value) + ' ' + why
            scaled += 1
            continue
        vals = ('V%03d' % nxt, 'enemies', '%d %s (%s)' % (eid, e['name'], cid), stat, None, old, round(old * f), 'L01', 'R08, R10', why,
                DECIDED, 'built')
        for c, value in enumerate(vals, start=1):
            ws.cell(row, c).value = value
        row += 1
        nxt += 1
        added += 1
wb.save(PATH)
print('enemies', len(taken), 'scaled', scaled, 'added', added)

# Decided after the check of the whole (2026-10-16): three quarters of each change. The full factors left 11 floors of the walks harder
# than vanilla for the six parties (7 of them for Mage-Heavy), since the records are shared; at three quarters 7 harder, and the mean of
# the parties from C30 on +4 / +4 / +2 / -1 / +6 / +11 points of wins against vanilla (it was +8 / +6 / +6 / +2 / +10 / +16).
wb = openpyxl.load_workbook(PATH)
ws = wb['Changes']
done = 0
for r in range(2, ws.max_row + 1):
    if ws.cell(r, 2).value == 'enemies' and ws.cell(r, 11).value == DECIDED and 'walk of 30 random battles' in str(ws.cell(r, 10).value) \
            and 'three quarters' not in str(ws.cell(r, 10).value).lower():
        old, new = ws.cell(r, 6).value, ws.cell(r, 7).value
        ws.cell(r, 7).value = round(old + (new - old) * 0.75)
        ws.cell(r, 10).value = str(ws.cell(r, 10).value) + ' Three quarters of the factor: the full one left 11 floors of the walks harder than vanilla.'
        done += 1
wb.save(PATH)
print('three quarters', done)

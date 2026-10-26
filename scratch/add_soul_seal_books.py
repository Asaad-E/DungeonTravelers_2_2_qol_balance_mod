"""Personal sealbooks for the Soul Summoner before P06: at each checkpoint, the regular enemy with the
highest stat sum met on the floors reached before it (sealbooks drop from regular enemies)."""
import json, os, openpyxl
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
s = json.load(open('build/engine_snapshot.json', encoding='utf-8'))
v, setup = s['sides']['variant'], s['setup']
enemies = {e['id']: e for e in v['enemies']}
floors = {}
for f in v['floors']:
    floors.setdefault(f['floor'], set()).update(e[0] for fm in f['formations'] for e in fm['enemies'])
import statistics
med = {n: statistics.median(enemies[i]['level'] for i in ids if i in enemies) for n, ids in floors.items() if any(i in enemies for i in ids)}
# realistic: drop rare overleveled enemies (level above the floor median + 5), they are not farmable
for n in list(floors): floors[n] = {i for i in floors[n] if i in enemies and enemies[i]['level'] <= med.get(n, 0) + 5}
power = lambda i: sum(enemies[i][k] for k in ('atk', 'def', 'int', 'res', 'dex', 'agi'))

seen_floors, best, rows = [], None, []
for cp in setup['checkpoints']:
    if cp['ID'] == 'P06':
        break
    if best is not None:
        rows.append((cp['ID'], best))
    fl = cp['Floor']
    dungeon = fl.split('_')[0]
    for name in floors:
        if name.split('_')[0] == dungeon and name <= fl and name not in seen_floors:
            seen_floors.append(name)
    pool = [i for n in seen_floors for i in floors[n] if i in enemies]
    if pool:
        best = max(pool, key=power)

wb = openpyxl.load_workbook('data_tables/sim_setup.xlsx')
ws = wb['PersonalSealbooks']
head = [c.value for c in ws[1]]
persephone = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] in ('soul summoner', 'dolls') and r[3] == 'P06']
keep = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] not in ('soul summoner', 'dolls') and r[0]]
ws.delete_rows(2, ws.max_row)
last = None
for r in keep:
    ws.append(list(r))
for cid, eid in rows:
    if eid == last:
        continue
    last = eid
    for role in ('soul summoner', 'dolls'):
        ws.append([role, eid, enemies[eid]['name'], cid,
                   'Derived: the strongest regular enemy (stat sum) of the floors reached before the checkpoint; a sealbook a player carries for Soul Seal'][:len(head)])
for r in persephone:
    ws.append(list(r))
wb.save('data_tables/sim_setup.xlsx')
for cid, eid in rows:
    print(cid, eid, enemies[eid]['name'], power(eid))

"""More facts behind the tutorial texts, from vanilla_source_of_truth.xlsx and the sim data (vanilla and variant)."""
import os
import sys
import openpyxl
sys.path.insert(0, r'C:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = r'C:\Users\user\Personal\Physics\DungeonTraveler2-2'
SOT = os.path.join(ROOT, 'mod_project', 'data_tables', 'vanilla_source_of_truth.xlsx')
wb = openpyxl.load_workbook(SOT, read_only=True, data_only=True)


def table(name):
    rows = list(wb[name].iter_rows(values_only=True))
    return rows[0], rows[1:]


def show(name, pred, cols=None, limit=30):
    head, rows = table(name)
    n = 0
    for r in rows:
        d = dict(zip(head, r))
        if pred(d):
            n += 1
            if n <= limit:
                print('   ', {k: v for k, v in d.items() if (cols is None or k in cols) and v not in (None, '')})
    print(f'    ({n} rows)')


print('== WeaponRanks'); head, rows = table('WeaponRanks'); print('   ', head)
for r in rows:
    print('   ', r)
print('== QuestRanks'); head, rows = table('QuestRanks'); print('   ', head)
for r in rows[:20]:
    print('   ', r)
print('== FoodMenu'); head, rows = table('FoodMenu'); print('   ', head)
for r in rows[:40]:
    print('   ', tuple(str(x)[:60] if x is not None else None for x in r))
print('== Equipment named Slave / Torc')
show('Equipment', lambda d: any('torc' in str(v).lower() or "slave" in str(v).lower() for v in d.values()))
print('== Enchants: EXP related')
show('Enchants', lambda d: any('exp' in str(v).lower() for v in d.values()), limit=12)
print('== Skills: Circle Protection')
show('Skills', lambda d: 'circle' in str(d).lower() and 'protect' in str(d).lower())
print('== Raw_SealScroll header'); head, rows = table('Raw_SealScroll'); print('   ', head[:14]); print('   rows', len(rows))
for r in rows:
    if any('papi' in str(x).lower() for x in r):
        print('   ', r[:16])
print('== Raw_PartySkill'); head, rows = table('Raw_PartySkill'); print('   ', head)
for r in rows[:6]:
    print('   ', tuple(str(x)[:70] if x is not None else None for x in r))

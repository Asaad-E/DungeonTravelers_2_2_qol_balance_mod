"""One-off edit (2026-10-13): the Slave's Torc keeps the enchantments of the game (row W042 dropped: one piece for
EXP is enough, the Bathroom Slippers), and row S13 of the register carries the look at the late dungeons. Run once;
kept as the record of the edit.
"""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
wb = openpyxl.load_workbook(os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx'))
ws = wb['Changes']
head = [c.value for c in ws[1]]
row = next(r for r in ws.iter_rows(min_row=2) if r[0].value == 'W042')
assert row[head.index('State')].value == 'built'
row[head.index('State')].value = 'dropped'
row[head.index('Why')].value = str(row[head.index('Why')].value) + \
    ' | 2026-10-13 : dropped. One piece that speeds EXP up is enough, and it is the Bathroom Slippers (row P090)'
wb.save(os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx'))

SET = {'Vanilla_Result': 'Chance of a battle a step, by the zones of each dungeon (floor files, zone 0x1C): 5 - 8 in the story '
                         'up to its thirteenth dungeon, 6 - 10 in the last two and in the postgame. The mean walk between two '
                         'battles is 20 - 28 steps early and 18 - 25 late (8 + 100 / chance, docs/FORMULAS.md 14)',
       'Why': 'It rises little where it rises: a battle every 18 steps in the worst zones of the end against every 25. Repel '
              'items and a grand sealbook lower it for who wants',
       'Verdict': 'partly true: at most a third more battles in the last dungeons',
       'Decision': '2026-10-13: looked at in the late dungeons, as decided; left as it is'}
path = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
wb = openpyxl.load_workbook(path)
ws = wb['Criticisms']
head = [c.value for c in ws[1]]
row = next(r for r in ws.iter_rows(min_row=2) if r[0].value == 'S13')
for column, value in SET.items():
    row[head.index(column)].value = value
wb.save(path)
print('W042 dropped, S13')

# row F92 named the Torc as the piece that carries Double EXP
wb = openpyxl.load_workbook(path)
ws = wb['Criticisms']
head = [c.value for c in ws[1]]
row = next(r for r in ws.iter_rows(min_row=2) if r[0].value == 'F92')
row[head.index('Why')].value = ('The DLC is ignored (2026-10-06). What it eased is covered by T01: the factors by level gap '
                                '(option B4, without the kept curve) catch a member up faster than a Double EXP piece did, and '
                                'a crown costs about 400 battles instead of 4,393 (docs/generated/CATCH_UP_OPTIONS.md). No '
                                'piece gains Double EXP: the Slave\'s Torc carried it from 2026-10-11 to 2026-10-13 (row W042, '
                                'dropped); the one piece that speeds EXP up is the Bathroom Slippers, with the factor '
                                'enchantment (row P090)')
wb.save(path)
print('F92')

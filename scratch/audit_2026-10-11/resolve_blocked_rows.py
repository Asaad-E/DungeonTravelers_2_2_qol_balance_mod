"""Resolves the rows of balance_changes.xlsx blocked on 2026-10-11, as the user asked that day.

  W038, W039   dropped: Warning Shot and Support Shot stay bow skills. The game holds one gun (Degtyaryov, ATK 97
               against 468 for the best bow), and Spiral Arrow and Divine Cannon do open to it (W036, W037).
  P026 - P030  the gold of quests. Read in the executable (0x55e210 - 0x55e2a0, 0x595996 - 0x5959ce): QuestData 0x38 is
               the kind of the reward, 0 an item, 1 a piece of equipment, 2 experience (the amount goes to the window of
               0x448c60), 3 gold (the amount goes to the party, slot 0x48); the amount is 0x40. Of the five rows only
               P028 named a quest that pays gold. P026, P027, P029, P030 are dropped; P028 and one new row for each of
               the other gold quests raise the gold by the factor of GOLD_FACTOR, rounded as ROUNDING says.
  P011 - P025  left blocked: what the right figure is has to be found first (the user sends another agent).

    python resolve_blocked_rows.py            shows the rows
    python resolve_blocked_rows.py --write
"""
import os
import re
import struct
import sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from pck_handler import PckArchive                          # noqa: E402

WORKBOOK = os.path.join(PROJECT, 'data_tables', 'balance_changes.xlsx')
TODAY = '2026-10-11'
KIND, AMOUNT, GOLD = 0x38, 0x40, 3
GOLD_FACTOR = 1.4                      # the rows of 2026-10-10 asked for +43% to +50%; the register says "+30% to +50%"
ROUNDING = ((1000, 10), (10000, 50), (None, 500))          # below the first figure, to the nearest second figure
WEAPON = ('Dropped on %s (the user): the passive stays a bow skill. A passive record holds one weapon code, and the game '
          'has one gun, the Degtyaryov (ATK 97; the best bow has 468), which Spiral Arrow and Divine Cannon do reach '
          '(W036, W037)' % TODAY)
NOT_GOLD = ('Dropped on %s: the quest does not pay gold. QuestData 0x38 is the kind of its reward (0 an item, 1 a piece of '
            'equipment, 2 experience, 3 gold; 0x55e210 - 0x55e2a0) and the figure this row took for gold is the id of '
            'the item or piece. The gold of quests is raised by row P028 and the rows after P038' % TODAY)
WHY = ('Gold of quests x%.2f (S20; the user, %s, in the place of the five rows of 2026-10-10 that asked for +43%% to +50%% on '
       'figures that were not gold): every quest whose reward is gold, 41 of 471 (QuestData 0x38 = 3, the amount at 0x40, '
       'read at 0x5959ac - 0x5959ce where it goes to the party), rounded to the nearest 10 below 1,000, 50 below 10,000 '
       'and 500 above. The simulator has no quests: the row is checked by the build alone') % (GOLD_FACTOR, TODAY)


def rounded(value):
    for limit, step in ROUNDING:
        if limit is None or value < limit:
            return int(round(value / step) * step)


def gold_quests():
    """[(entry, name, amount)] of the quests that pay gold."""
    found = []
    for name, blob in PckArchive(os.path.join(PROJECT, 'backups', 'QuestData.pck')).files:
        if struct.unpack_from('<i', blob, KIND)[0] == GOLD:
            text = re.search(rb'[\x20-\x7e]{3,}\x00', bytes(blob[0x50:]))
            found.append((name[:-4], text.group()[:-1].decode('latin-1') if text else '', struct.unpack_from('<i', blob, AMOUNT)[0]))
    return found


def main(write):
    wb = openpyxl.load_workbook(WORKBOOK)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    col = {name: k for k, name in enumerate(head)}
    quests = {entry: (name, amount) for entry, name, amount in gold_quests()}
    taken, numbers = set(), []
    for row in ws.iter_rows(min_row=2):
        rid = row[col['ID']].value
        if not rid:
            continue
        if re.fullmatch(r'P\d+', str(rid)):
            numbers.append(int(str(rid)[1:]))
        if rid in ('W038', 'W039') and row[col['State']].value == 'blocked':
            row[col['State']].value, row[col['Why']].value = 'dropped', WEAPON + '. ' + str(row[col['Why']].value)
            print(rid, 'dropped')
        if row[col['Table']].value == 'quests':
            entry = str(row[col['Record']].value).split()[0]
            if entry in quests and row[col['State']].value in ('blocked', 'decided', 'built'):
                name, amount = quests[entry]
                row[col['Field']].value, row[col['Vanilla']].value, row[col['New']].value = 'gold reward', amount, rounded(amount * GOLD_FACTOR)
                row[col['Why']].value, row[col['Decided']].value, row[col['State']].value = WHY, TODAY, 'decided'
                row[col['Lever']].value = 'L19'
                taken.add(entry)
                print(rid, entry, name, amount, '->', rounded(amount * GOLD_FACTOR))
            elif row[col['State']].value == 'blocked':
                row[col['State']].value, row[col['Why']].value = 'dropped', NOT_GOLD + '. ' + str(row[col['Why']].value)
                print(rid, 'dropped: not a gold quest')
    next_id = max(numbers) + 1
    for entry, (name, amount) in quests.items():
        if entry in taken:
            continue
        values = {'ID': f'P{next_id:03d}', 'Table': 'quests', 'Record': f'{entry} ({name})', 'Field': 'gold reward',
                  'Level': None, 'Vanilla': amount, 'New': rounded(amount * GOLD_FACTOR), 'Lever': 'L19', 'Serves': 'S20',
                  'Why': WHY, 'Decided': TODAY, 'State': 'decided'}
        ws.append([values.get(name_) for name_ in head])
        print(values['ID'], entry, name, amount, '->', values['New'])
        next_id += 1
    if write:
        wb.save(WORKBOOK)
        print('written')


if __name__ == '__main__':
    main('--write' in sys.argv)

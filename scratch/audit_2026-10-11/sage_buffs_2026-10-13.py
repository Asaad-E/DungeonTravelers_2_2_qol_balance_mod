"""One-off edit (2026-10-13) of balance_changes.xlsx: the buffs of the Sage line are chanted faster (chant speed
factor 2.5 for Circle Brave, Circle Protect, Sun Veil, Amplify and Accelerator) and the first three a fifth larger.
Run once; kept as the record of the edit.
"""
import os
import sys

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from sim.data import game_data                            # noqa: E402

PATH = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
CHANT, SIZE, TODAY = 2.5, 1.2, '2026-10-13'
SIZED = {'Circle Brave': 'effect 161', 'Circle Protect': 'effect 162', 'Sun Veil': 'effect 163'}
CHANTED = ('Circle Brave', 'Circle Protect', 'Sun Veil', 'Amplify', 'Accelerator')
WHY_SIZE = (f' | {TODAY} : a fifth larger again. Played as she is (her two buffs kept up, then her spells) the Sage won as often '
            'as an attacker in her place and no more (89% and 89% over C30, C36, C38, C40 and P24, 200 battles); a support has '
            'to lift the party. With these values and the faster chant she wins 92% (measures/sage_buffs_trial.py, 300 battles)')
WHY_CHANT = ('The buffs of the Sage line took too long to chant for what they give: with them kept up she attacked late and '
             f'the party won no more than with an attacker in her place. Chant speed factor {CHANT} at every level (Heal has 2); '
             'with it and the larger values she wins 92% of C30, C36, C38, C40 and P24 against 90% '
             '(measures/sage_buffs_trial.py, 300 battles)')


def main():
    data = game_data()
    wb = openpyxl.load_workbook(PATH)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    col = {k: head.index(k) for k in ('ID', 'Record', 'Field', 'Level', 'Vanilla', 'New', 'Why', 'State')}
    grown, ids = 0, set()
    for row in ws.iter_rows(min_row=2):
        ids.add(row[col['ID']].value)
        if row[col['State']].value != 'built':
            continue
        for name, field in SIZED.items():
            if str(row[col['Record']].value).endswith(' ' + name) and str(row[col['Field']].value).startswith(field):
                row[col['New']].value = round(row[col['New']].value * SIZE, 2)
                row[col['Why']].value = str(row[col['Why']].value) + WHY_SIZE
                grown += 1
    assert grown == 15, grown
    last = max(int(str(i)[1:]) for i in ids if str(i).startswith('T') and str(i)[1:].isdigit())
    added = 0
    for name in CHANTED:
        skill = next(s for s in data.skills.values() if s.name == name)
        for level, old in enumerate(skill.cast, 1):
            added += 1
            ws.append((f'T{last + added:03d}', 'skills', f'{skill.category} {skill.id} {name}', 'chant speed factor', level,
                       old, CHANT, 'L12', 'J23', WHY_CHANT, TODAY, 'built'))
    wb.save(PATH)
    print(grown, 'values a fifth larger,', added, 'chant rows')


if __name__ == '__main__':
    main()


def amplify_box():
    """The box of Amplify has no room for its chant in the generated text: worded by hand, with the new chant."""
    path = os.path.join(ROOT, 'data_tables', 'balance_skill_text.xlsx')
    wb = openpyxl.load_workbook(path)
    ws = wb['Skills']
    assert not any(r[2].value == 'Amplify' for r in ws.iter_rows(min_row=2))
    ws.append(('Magic', 'MagicSkillData_0198.bin', 'Amplify', None,
               'Max HP: +20% -> +23 -> +26 -> +29 -> +32 -> +35 -> +38 -> +41 -> +44 -> +47% (L10)' + chr(10) +
               'Turns: 5 (Lv1-2) -> 6 (Lv3-4) -> 7 (Lv5-6) -> 8 (Lv7-8) -> 9 -> 10' + chr(10) +
               'TP Cost: 18 (+3/Lv) -> 45   |   Chant: 2.5x',
               'Rows of the chant speed factor of Amplify (2026-10-13): the generated box had no room for it', None))
    wb.save(path)
    print('Amplify worded')


def amplify_back():
    """Amplify keeps its chant (1.5 to 1.81, already the fastest of the five): its box has no room to show another, and
    the Sage does not keep it up. Its ten chant rows and the box worded by hand are taken out again."""
    wb = openpyxl.load_workbook(PATH)
    ws = wb['Changes']
    gone = [r[0].row for r in ws.iter_rows(min_row=2)
            if str(r[2].value).endswith(' Amplify') and r[3].value == 'chant speed factor']
    assert len(gone) == 10
    for number in sorted(gone, reverse=True):
        ws.delete_rows(number)
    wb.save(PATH)
    path = os.path.join(ROOT, 'data_tables', 'balance_skill_text.xlsx')
    wb = openpyxl.load_workbook(path)
    ws = wb['Skills']
    row = next(r[0].row for r in ws.iter_rows(min_row=2) if r[2].value == 'Amplify')
    ws.delete_rows(row)
    wb.save(path)
    print('Amplify as it was')


def register_row():
    """Row J23 of the register carries the measure of the day."""
    path = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
    wb = openpyxl.load_workbook(path)
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    row = next(r for r in ws.iter_rows(min_row=2) if r[0].value == 'J23')
    row[head.index('Balance_Result')].value = (
        'The Sage in the last place of the reference party, 300 battles at C30, C36, C38, C40 and P24: 92% of wins against '
        '90% with an attacker in her place, and 16 - 23% of the damage of the party (measures/sage_buffs_trial.py, '
        '2026-10-13). Circle Brave and Circle Protect +16% to +31% (x1.6, then a fifth more), Sun Veil a fifth more, and the '
        'chant of the four buffs but Amplify at 2.5')
    row[head.index('Decision')].value = str(row[head.index('Decision')].value) + \
        ' | 2026-10-13: a little larger and chanted faster; the model plays her with her spells'
    wb.save(path)
    print('J23')

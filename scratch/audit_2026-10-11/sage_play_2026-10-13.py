"""One-off edit (2026-10-13) of sim_setup.xlsx: how the model plays the Sage. She holds the spells of the Magic User
she was and Bible Thump, keeps Circle Protect and Circle Brave up and then attacks; Sun Veil, Amplify and Accelerator
leave her rules (they added nothing that could be measured and took her turns). Run once; kept as the record.
"""
import os

import openpyxl

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data_tables', 'sim_setup.xlsx')
PRIORITY = ('Heal; Circle Brave; Circle Protect; Fireball; Ice Edge; Thunderbolt; Air Cutter; Stone Hammer; Accelerator; Amplify; '
            'Sun Veil; Dispel; Esarhaddon; Slow; Stab Guard; Slash Guard; Bash Guard; Prism Dawn; Fast Cast; Sleep; Silence; '
            'Bible Thump')
SOURCE = (' | 2026-10-13 : she holds the five spells of the Magic User she was and Bible Thump (the classes of her path '
          'learn them); without them she dealt none of the damage of the party')
BRAVE = (' | 2026-10-13 : second, after Circle Protect: at the end of the list she never came to cast it. Sun Veil, Amplify and '
         'Accelerator left her rules the same day: each added nothing that could be measured at C30, C36, C38, C40 and P24 '
         '(150 battles, with and without each), and with the five kept up she never attacked. With the two buffs and then her '
         'spells she wins 90% of those fights in the last place of the reference party, against 87%')
DROPPED = ('status:163', 'status:172', 'status:168')


def main():
    wb = openpyxl.load_workbook(PATH)
    ws = wb['Roles']
    head = [c.value for c in ws[1]]
    row = next(r for r in ws.iter_rows(min_row=2) if r[0].value == 'sage')
    row[head.index('Skill priority')].value = PRIORITY
    row[head.index('Source')].value = str(row[head.index('Source')].value) + SOURCE
    ws = wb['Policies']
    gone = [r[0].row for r in ws.iter_rows(min_row=2) if r[0].value == 'sage' and str(r[3].value) in DROPPED]
    assert len(gone) == 3
    for r in ws.iter_rows(min_row=2):
        if r[0].value == 'sage' and r[3].value == 'status:161':
            r[1].value = 6
            r[4].value = str(r[4].value) + BRAVE
    for number in sorted(gone, reverse=True):
        ws.delete_rows(number)
    wb.save(PATH)
    print('sage: priority, Circle Brave second,', len(gone), 'rules out')


if __name__ == '__main__':
    main()

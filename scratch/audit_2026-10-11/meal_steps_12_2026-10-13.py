"""One-off edit (2026-10-13): a turn of a status takes 12 steps of the map, not 20 (row X15, lever L47, row J36,
docs/FORMULAS.md 12.18, the player README): 20 carried the buffs of a battle too far. Run once; kept as the record.
"""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CRITERIA = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
TEXTS = {
    os.path.join(ROOT, 'docs', 'FORMULAS.md'): [('Balance variant makes the first one 20 (row X15', 'Balance variant makes the first one 12 (row X15')],
    os.path.join(ROOT, 'installer', 'README_Balance.txt'): [
        ('* The buff of a meal lasts four times as many steps, enough to carry it into several battles.',
         '* The buff of a meal lasts more than twice as many steps, enough to carry it into a few battles.')],
}
MEANING = ('Steps of the map that count as one turn of a status with a number of turns (cmp dword ptr [esi + 0x2c], 5 at 0x48d5f0, '
           'reached only when the tick is not of a battle: the word at +0x40 of its second argument is 0). 5 -> 12: a meal lasts '
           '36 to 120 steps in the place of 15 to 50. Decided 2026-10-13 (20 at first, lowered the same day: the buffs a '
           'member walks out of a battle with last as much longer)')
J36 = {'Balance_Result': 'Row X15 of the sheet ExePatches: a turn of a status takes 12 steps of the map in the place of 5, so a '
                         'meal lasts 36 to 120 steps, one to five random battles of walking. Battles count turns as before',
       'Why': 'The buff of a meal was gone a battle later. The count of steps is one byte that only the map uses; with it the '
              'buffs and the lowered stats a member carries out of a battle last 2.4 times as long on the map too, which is why '
              'it is 12 and not more, while poison and the other ailments that end on a roll keep their own count',
       'Decision': '2026-10-13: approved at 12 steps a turn (20 was too strong for the buffs kept out of a battle)'}


def main():
    wb = openpyxl.load_workbook(CRITERIA)
    ws = wb['ExePatches']
    head = [c.value for c in ws[1]]
    row = next(r for r in ws.iter_rows() if r[0].value == 'X15')
    assert row[head.index('New_Hex')].value == '14'
    row[head.index('New_Hex')].value = '0c'
    row[head.index('Meaning')].value = MEANING
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    row = next(r for r in ws.iter_rows(min_row=2) if r[0].value == 'J36')
    for column, value in J36.items():
        row[head.index(column)].value = value
    wb.save(CRITERIA)
    for path, pairs in TEXTS.items():
        with open(path, encoding='utf-8') as f:
            text = f.read()
        for old, new in pairs:
            assert text.count(old) == 1, old
            text = text.replace(old, new)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
    print('12 steps')


if __name__ == '__main__':
    main()

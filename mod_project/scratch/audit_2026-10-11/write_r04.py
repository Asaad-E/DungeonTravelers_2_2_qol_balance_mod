"""The verdict of condition R04 written into the sheet Regression of data_tables/balance_criteria.xlsx, from
REGRESSION_R04.md beside this file.

    python write_r04.py
"""
import os
import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKBOOK = os.path.join(PROJECT, 'data_tables', 'balance_criteria.xlsx')
VERDICT = 'met: no new mandatory class; the Diva is needed at the last boss, as in vanilla'
RESULT = ('scratch/audit_2026-10-11/REGRESSION_R04.md (2026-10-12): at the 17 bosses of the battery, 27 pairs of boss and '
          'class on the variant (34 in vanilla) where every winning party of the battery holds the class. With the role '
          'of that class changed for a neighbour of the same job (60 battles), a party without it reaches the floor at '
          '20 of the 27 (27 of 34 in vanilla): without a Diva or a Bard at 14 bosses (67 - 100%), without a Valkyrie at '
          'C29, C32, C36 and C40 (53 - 92%), without a Bishop at C29. Not reached: the Diva at C40 (the best party '
          'without her wins 22%, 13% in vanilla: needed there in vanilla too, and less so on the variant); the Sage and '
          'the Witch at C29, where only the mage party wins on either side (Calliope, which the model does not play as '
          'the guide describes); and the four base classes at C06, where five characters have joined and no other '
          'party can be made')


def main():
    wb = openpyxl.load_workbook(WORKBOOK)
    ws = wb['Regression']
    head = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'R04':
            row[head.index('Verdict')].value = VERDICT
            row[head.index('Result (final pass, 2026-10-11)')].value = RESULT
    wb.save(WORKBOOK)


if __name__ == '__main__':
    main()

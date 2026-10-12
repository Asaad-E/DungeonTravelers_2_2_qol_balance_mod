"""Alluring Samba raised at the user's word of 2026-10-12 (enough to quicken a fight a little, not to break it): the
rows A094 - A103 of data_tables/balance_changes.xlsx take 1.75 times the value they held, which was 1.5 times vanilla.

    python raise_samba.py
"""
import os
import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHANGES = os.path.join(PROJECT, 'data_tables', 'balance_changes.xlsx')
FACTOR = 1.75
WHY = (' | 2026-10-12 (the user): times 1.75 again, 60% of the DEF of the enemies at its top level. The Etoile with Waltz '
       'and Samba in the place of Waltz and Mazurka (scratch/audit_2026-10-11/samba_trial.py, 100 battles): at 1.5 and 2 '
       'times the fights of C30, C36 and P24 are 0 - 11% shorter and those of C38 and C40 4 - 8% longer, the wins within '
       '5 points; before it the pair was never better (fights up to 12% longer, 8 points fewer wins at C38). The dance '
       'for enemies of high DEF, where it weighs most')


def main():
    wb = openpyxl.load_workbook(CHANGES)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    col = {name: head.index(name) for name in head}
    done = 0
    for row in ws.iter_rows(min_row=2):
        if row[col['Record']].value == 'Technique 70 Alluring Samba' and row[col['State']].value != 'dropped' and \
                '2026-10-12' not in str(row[col['Why']].value):
            row[col['New']].value = round(float(row[col['New']].value) * FACTOR, 2)
            row[col['Why']].value = str(row[col['Why']].value) + WHY
            row[col['State']].value = 'decided'
            done += 1
    wb.save(CHANGES)
    print(done, 'rows')


if __name__ == '__main__':
    main()

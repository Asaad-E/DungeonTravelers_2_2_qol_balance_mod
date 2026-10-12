"""Row F01 of the register (every party must hold a Maid) reopened with the figure measured on 2026-10-12
(no_maid_line.py beside this file): it had been closed without one.

    python reopen_f01.py
"""
import os
import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKBOOK = os.path.join(PROJECT, 'data_tables', 'balance_criteria.xlsx')
FIGURE = ('scratch/audit_2026-10-11/no_maid_line.py (2026-10-12, 40 battles): the Meta party with a Bishop or a Sage in the '
          'place of its Diva, so that nobody of the Maid line stands in it, vanilla > variant. Up to C28 it wins as the '
          'party with the Diva or little less (C17 45% > 82% and 95% > 98%, C26 42% > 88% and 52% > 98%, C28 68% > 90% '
          'and 62% > 95%). From C30 on it does not: C30 0% > 2% and 0% > 0%, C34 10% > 2% and 0% > 0%, C36 0% > 10% and '
          '2% > 5%, C40 0% > 0% both; only C38 with the Bishop moves (8% > 62%). The same party with the Diva wins '
          '88 - 100% there. With an Etoile or a Mistress, who are of the Maid line, see Regression R04')
VERDICT = 'true from C30 on, in vanilla and on the variant: no party without a member of the Maid line wins the last third of the story'


def main():
    wb = openpyxl.load_workbook(WORKBOOK)
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    col = {name: head.index(name) for name in head}
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'F01':
            row[col['Status']].value = 'open'
            row[col['Verdict']].value = VERDICT
            row[col['Balance_Result']].value = FIGURE
            row[col['Decision']].value = str(row[col['Decision']].value) + '; 2026-10-12: reopened, the closing held no figure; waits for the user'
    wb.save(WORKBOOK)


if __name__ == '__main__':
    main()

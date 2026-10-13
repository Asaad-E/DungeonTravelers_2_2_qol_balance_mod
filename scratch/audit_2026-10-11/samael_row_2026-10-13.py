"""One-off edit (2026-10-13): row F86 of the register and row P038 of the changes say why Samael opens another way
(the opening was unfair), with its measure; row J32 carries its decision. Run once; kept as the record of the edit.
"""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHANGES = os.path.join(ROOT, 'data_tables', 'balance_changes.xlsx')
CRITERIA = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
P038 = ('Unfair as the game has it: on its first turn the Samael of the postgame (P23) always cast Dark Blast on the whole '
        'party, before anyone could put a guard up, so the fight was lost or won on that one roll. It opens with Forbidden '
        'Fruit, a debuff, in its place; Dark Blast stays in its later turns. Measured on 2026-10-13 (measures/rows_trial.py, '
        '150 battles at P23, without the row > with it): the reference party 21% > 34% of wins, Meta 25% > 37%; no other '
        'party of the battery wins the fight either way, so it stays a superboss')
F86 = {'Vanilla_Result': 'The Samael of the postgame (P23) casts Dark Blast on the whole party on its first turn, every time '
                         '(the weights of its first set of attacks: slot 6 alone). The reference party wins 21% of the fights '
                         'and Meta 25% (measures/rows_trial.py, 150 battles)',
       'Balance_Result': 'Row P038: it opens with Forbidden Fruit, a debuff; Dark Blast stays in its later turns. The reference '
                         'party wins 34% and Meta 37%. First Grid, the passive that may act first, comes up 15% of the times in '
                         'the place of 10% (row P032; it adds nothing that can be measured)',
       'Why': 'An opening no party can answer is unfair, not hard: the guard that stops the spell cannot be up before the '
              'first turn. The fight keeps its spell and its difficulty, without the roll that decided it',
       'Decision': '2026-10-11: the opening of Samael changed because it was unfair; 2026-10-13: measured'}
J32 = '2026-10-09: no change; 2026-10-13, confirmed: the fragility is the flavour of the class'


def main():
    wb = openpyxl.load_workbook(CHANGES)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    row = next(r for r in ws.iter_rows(min_row=2) if r[0].value == 'P038')
    row[head.index('Why')].value = P038
    wb.save(CHANGES)
    wb = openpyxl.load_workbook(CRITERIA)
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'F86':
            for column, value in F86.items():
                row[head.index(column)].value = value
        if row[0].value == 'J32':
            row[head.index('Decision')].value = J32
    wb.save(CRITERIA)
    print('P038, F86, J32')


if __name__ == '__main__':
    main()

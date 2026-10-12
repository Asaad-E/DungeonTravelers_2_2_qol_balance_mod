"""The rows of the unique skills (theme T15 of the sheet Criticisms) closed on the decisions of 2026-10-12:
three raised (Third Eye Wide, Usurper of Souls, Arcane Shield), the others left as they are ("they add little but it
is good to have them").

    python close_unique_rows.py
"""
import os
import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKBOOK = os.path.join(PROJECT, 'data_tables', 'balance_criteria.xlsx')
RAISED = {
    'Third Eye Wide': ('U001 - U010: the chance times 2 (14 - 30% by rank, 50% crowned)',
                       ' Built on 2026-10-12 (1,421 of 1,421 rows): the reference party wins 78.6% of the five bosses '
                       'without it and 80.2% with it (78.0% before); rows of eight random battles at four floors do '
                       'not run away with it'),
    'Usurper of Souls': ('U011 - U020: the chance times 1.6, never over 1 (40 - 91% by rank, certain crowned)',
                         ' Built on 2026-10-12. None of the five fights of the measure holds anything it can remove, '
                         'with or without the raise: its worth is only against the enemies that summon, not measured'),
    'Arcane Shield': ('X13 of the sheet ExePatches (set balance, lever L38): the roll from 15 to 25 in 100; its box '
                      'worded in balance_skill_text.xlsx',
                      ' Built on 2026-10-12. The measure does not move with it (82.2% as it was, 82.0% at 25%, 80.6% '
                      'without the skill): what it sends back is a share of the damage she takes, little beside the HP '
                      'of a boss. Raised for the feel of it, at the word of the user'),
}
LEFT = 'decided 2026-10-12: left as it is; it adds little but it is good to have'


def main():
    wb = openpyxl.load_workbook(WORKBOOK)
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    col = {name: head.index(name) for name in head}
    closed = left = 0
    for row in ws.iter_rows(min_row=2):
        if not str(row[col['Theme']].value).startswith('T15') or row[col['Status']].value != 'open':
            continue
        skill = str(row[col['Subject']].value).split(' (')[0]
        if skill in RAISED:
            proposal, figure = RAISED[skill]
            row[col['Status']].value = 'closed'
            row[col['Proposal']].value = proposal
            row[col['Balance_Result']].value = str(row[col['Balance_Result']].value) + figure
            row[col['Decision']].value = 'decided 2026-10-12: raised'
            row[col['Verdict']].value = 'true: it added nothing that could be measured'
            closed += 1
        else:
            row[col['Status']].value = 'not a problem'
            row[col['Decision']].value = LEFT
            row[col['Verdict']].value = 'measured: within what the others give, none above +8% of length or +6 points of wins'
            left += 1
    wb.save(WORKBOOK)
    print(closed, 'closed,', left, 'left as they are')


if __name__ == '__main__':
    main()

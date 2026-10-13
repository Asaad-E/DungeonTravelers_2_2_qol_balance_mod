"""One-off edit (2026-10-13): the sheet Regression of balance_criteria.xlsx brought up to the pass of that day (the
difficulty curve, the battery, the classes by stage, the verdicts and the build regenerated after Samba, the HP of
C30 and C38 and the dance bonus of the model). Run once; kept as the record of the edit.
"""
import os

import openpyxl

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data_tables',
                    'balance_criteria.xlsx')
HEADER = 'Result (final pass; the date of each row is in it)'
ROWS = {
    'R01': ('2026-10-13. measures/WIN_RATES.md (200 battles): the three parties that work in the game end level, Meta 92%, '
            'Dual-Support 91%, Mage-Heavy 94% of wins over the 17 bosses of the battery (85%, 89%, 90% in the game); Meta, the '
            'one that gains most, was the weakest of the three at C26, C30 and C38 in the game. The weakest party of the game '
            '(Anti-Meta-Plus, 0 - 12% at eight bosses) reaches 41 - 100%. CLASS_STAGES.md: 74 of 76 rows within the band. Limit: '
            'the band has no top, so a class that is too fast is not flagged (row J11, left)', 'met in what is measured'),
    'R02': ('2026-10-13. PARTY_BATTERY.md: 65 of 85 pairs at or above the floor in vanilla, 74 of 85 on the variant; no pair '
            'that met its floor in vanilla lost it. CLASS_STAGES.md: the two slow rows (Assassin and Treasure Hunter of the '
            'treasure hunter role) were slow before the changes (row J26)', 'met'),
    'R06': ('2026-10-13. BALANCE_BUILD.md: 1,456 of 1,456 live rows built, and each names the row it serves (column Serves, '
            'none empty)', 'met'),
    'R08': ('2026-10-13. DIFFICULTY_CURVE.md (40 battles a boss): 33 of 44 checkpoints within the windows of vanilla, 11 easier '
            '(C14, C15, C17, C26, C28, C29, C32, C37, C38, C39, C40), 0 harder. Seven of them were accepted on 2026-10-11; C30 is '
            'back within with its HP x1.15, and C38 keeps 92% of wins against 70% with the same. C15, C17, C28, C39 and C40 '
            'crossed their window since then by one measure each (length, wins or lowest HP), which at 40 battles may be '
            'chance (measures/curve_ablation.py settles it with more battles)',
            'met but for 11 bosses easier: 6 accepted, 5 since then not decided'),
    'R09': ('2026-10-13. VERDICTS.md: of 180 rows, 80 closed, 88 not a problem, 12 out of the balance, 0 open. 17 of them are '
            'closed on an argument with no figure (listed at the end of VERDICTS.md)', 'met; 17 rows rest on an argument'),
    'R10': ('2026-10-13. DIFFICULTY_CURVE.md, columns Lowest HP and Pressure: where a checkpoint leaves the window of vanilla '
            'the party stands higher (lowest HP 31 - 48% > 49 - 61% at C32, C38, C39, C40), never lower; pressure is above the '
            'window at C26 alone (0.07 > 0.10). SIM_ANCHORS.md: 6 of 6 anchors met', 'met'),
}


def main():
    wb = openpyxl.load_workbook(PATH)
    ws = wb['Regression']
    head = [c.value for c in ws[1]]
    result = next(i for i, h in enumerate(head) if str(h).startswith('Result'))
    verdict = head.index('Verdict')
    ws.cell(1, result + 1).value = HEADER
    done = 0
    for row in ws.iter_rows(min_row=2):
        if row[0].value in ROWS:
            row[result].value, row[verdict].value = ROWS[row[0].value]
            done += 1
    assert done == len(ROWS)
    wb.save(PATH)
    print(done, 'rows')


if __name__ == '__main__':
    main()

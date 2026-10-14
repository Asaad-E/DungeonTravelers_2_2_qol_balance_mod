"""One-off edit (2026-10-13, evening): the sheet Regression and rows S07 and S22 of the register carry the figures of
the reports as they stand after the last pass (the model with its four habits, the healer of the back row, Salsa and
Hopak as dances). The second audit found R04, R06, R09, R10, S07 and S22 quoting figures no report supported.
Run once; kept as the record of the edit.
"""
import os

import openpyxl

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data_tables',
                    'balance_criteria.xlsx')
D = '2026-10-13. '
REGRESSION = {
    'R01': (D + 'measures/WIN_RATES.md (200 battles): the three parties that work in the game end level, Meta 93%, '
            'Dual-Support 91%, Mage-Heavy 96% of wins over the 17 bosses of the battery (89%, 90%, 92% in the game); two cells '
            'of them gain 15 points or more (Meta at C38, 58% > 91%; Mage-Heavy at C36, 45% > 80%). The weakest party of the '
            'game (Anti-Meta, 47% on the mean) reaches 79%. CLASS_STAGES.md: 74 of 76 rows within the band. Limit: the band has '
            'no top (row J11, left). The Witch is the case: far ahead at C30 alone, a boss that resists physical damage at 90 - '
            '100 (row S07, decided 2026-10-13: not a problem there)', 'met in what is measured'),
    'R02': (D + 'PARTY_BATTERY.md: 70 of 85 pairs at or above the floor in vanilla, 79 of 85 on the variant; no pair that met '
            'its floor in vanilla lost it. CLASS_STAGES.md: the two slow rows (Assassin and Treasure Hunter of the treasure '
            'hunter role) were slow before the changes (row J26)', 'met'),
    'R04': (D + 'measures/REGRESSION_R04.md: at the 17 bosses of the battery, 24 pairs of boss and class on the variant (31 in '
            'vanilla) where every winning party of the battery holds the class. With the role of that class changed for a '
            'neighbour of the same job, a party without it reaches the floor at 18 of the 24 (25 of 31 in vanilla). The Diva at '
            'the last boss is among them now: the best party without her wins 77% on the variant and 65% in vanilla. Not '
            'reached, the same six pairs on both sides: the Sage and the Witch at C29, where only the mage party wins (Calliope, '
            'which the model does not play as the guide describes), and the four base classes at C06, where five characters '
            'have joined and no other party can be made', 'met: no new mandatory class'),
    'R06': (D + 'BALANCE_BUILD.md: 1,635 of 1,635 live rows built, 166 of them in the floor files, and each names the row it '
            'serves (column Serves, none empty)', 'met'),
    'R09': (D + 'VERDICTS.md: of 181 rows, 83 closed, 86 not a problem, 12 out of the balance, 0 open. 9 of them rest on an '
            'argument with no figure (listed at the end of VERDICTS.md)', 'met; 9 rows rest on an argument'),
    'R10': (D + 'DIFFICULTY_CURVE.md, columns Lowest HP and Pressure: where a checkpoint leaves the window of vanilla the '
            'party stands higher (lowest HP 15% > 31% at C29, 32% > 53% at C38, 30% > 40% at C40), never lower; pressure is '
            'above the window at C26 alone (0.06 > 0.10). SIM_ANCHORS.md: 5 of 6 anchors met, the sixth a known limit (N06)',
            'met'),
}
REGISTER = {
    'S07': {'Vanilla_Result': 'CLASS_STAGES.md (2026-10-13): at the advanced stage her fights last 0.57 of those of the median '
                              'attacker with 47 - 63% of the damage of the party. The peak is one boss: 0.36 at C30, Heartless '
                              'Avenger, who resists slash, stab and bash at 90, 100 and 90 and the elements at 50 to 100. At '
                              'C22, C34 and C40 she stands at 0.67, 0.59 and 0.68; late (P08 - P24) at 0.95'},
    'S22': {'Vanilla_Result': 'The reference party at its level (64), 200 battles: 88% of wins in 32.2 turns in the game, the '
                              'lowest HP of the party 32% (measures/BOSS_ROWS_CHECK.md, 2026-10-13). Of the parties of the '
                              'battery in the game: Meta 92%, Dual-Support 98%, Mage-Heavy 76%, Juggernaut-Plus 42% and the two '
                              'with no healer 0% and 2% (measures/WIN_RATES.md)',
            'Balance_Result': 'On the variant the reference party wins 96% in 29.7 turns: easier, accepted on 2026-10-13 '
                              '(Regression R08)',
            'Verdict': 'partly true: won 88% by a prepared party, never by one with no healer'},
}


def main():
    wb = openpyxl.load_workbook(PATH)
    ws = wb['Regression']
    head = [c.value for c in ws[1]]
    result = next(i for i, h in enumerate(head) if str(h).startswith('Result'))
    done = 0
    for row in ws.iter_rows(min_row=2):
        if row[0].value in REGRESSION:
            row[result].value, row[head.index('Verdict')].value = REGRESSION[row[0].value]
            done += 1
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    for row in ws.iter_rows(min_row=2):
        for column, value in REGISTER.get(row[0].value, {}).items():
            row[head.index(column)].value = value
            done += 1
    assert done == len(REGRESSION) + sum(len(v) for v in REGISTER.values()), done
    wb.save(PATH)
    print(done, 'cells')


if __name__ == '__main__':
    main()

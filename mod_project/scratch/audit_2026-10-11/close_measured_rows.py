"""The rows of the register that waited for a measure, measured on 2026-10-11 (measure_open_rows.py,
worth_with_weapon.py, roulette_chain.py beside this file; docs/generated/SKILL_VALUE.md): state, verdict and figure.

    python close_measured_rows.py
"""
import os
import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKBOOK = os.path.join(PROJECT, 'data_tables', 'balance_criteria.xlsx')
ROWS = {
    'F16': ('not a problem',
            'false in the measure: the fights of the intermediate stage are won as often and as fast without it',
            'SKILL_VALUE.md: the reference party with and without Replenishing Carol wins 100% of C10, C13 and C18 with '
            'the same length (8.3 / 9.0 / 9.6 against 8.3 / 9.1 / 9.1); rows of eight random battles without it end '
            'with 83 - 90% HP from C07 to C22'),
    'F42': ('not a problem',
            'partly true: it needs a tome, which costs the Sage the INT of her staff; with one it is her best strike '
            'against the bosses that resist her spells',
            'scratch/audit_2026-10-11/worth_with_weapon.py (the measure of tools/skill_worth.py, the Sage with a Tome): '
            'Bible Thump is her best option at the bosses of C40 and P08, 90% of it at P18, 74% at C34, 27 - 29% at C22 '
            'and C30; in random battles 43 - 89% (9% where a row falls to one spell)'),
    'F47': ('closed',
            'partly true: it pays only where the boss casts',
            'M rows, Sun Veil x1.5, built and read back; SKILL_VALUE.md: wins of the reference party 80% to 85% and '
            'fights 7% shorter at C40 with it, nothing at C22 and C34 (bosses that do not cast)'),
    'F73': ('not a problem',
            'false with a whip in hand: the best strike of the Joker against groups from C34 on',
            'scratch/audit_2026-10-11/worth_with_weapon.py (the Joker with a Whip): Beast Binder is her best option in '
            'the random battles of C34, C40 and P08, 104 - 134% of her best with her axe at C40; 39 - 82% against the '
            'bosses. Whips forge at rate 2.0 (W rows)'),
    'F52': ('open',
            'true: it fires only after a plain attack of a member (4 - 12% by level), and a party that has TP does not '
            'make plain attacks',
            'scratch/audit_2026-10-11/measure_open_rows.py: the reference party with and without Support Shot at its '
            'top level: C22 100% / 100% wins, length +2%; C30 +6%; C34 -4%; C40 80% / 73% wins (40 fights each: inside '
            'the noise). Waits for the user: leave it as the passive of plain-attack parties, or raise its chance'),
    'F22': ('open',
            'true for Roulette Circus only: Magic Box, Showtime and Heaven or Hell are worth 100% after the L rows',
            'L rows built. Roulette Circus (15 TP, one level; half its results an ailment on every enemy, a fifth a '
            'heal of the party, a tenth damage of level x 15): cast every turn by the dolls role, rows of eight random '
            'battles last 3 - 25% longer (C03, C06, C13, C22) and end with -1 to +3 points of HP; against bosses 6 - 32% '
            'longer (scratch/audit_2026-10-11/roulette_chain.py, measure_open_rows.py). SKILL_WORTH.md gives it 0% '
            'because it counts damage only. Waits for the user: leave it as the gamble of the base class, or raise it'),
}


def main():
    wb = openpyxl.load_workbook(WORKBOOK)
    ws = wb['Criticisms']
    head = [c.value for c in ws[1]]
    col = {name: head.index(name) for name in head}
    for row in ws.iter_rows(min_row=2):
        if row[0].value in ROWS:
            state, verdict, figure = ROWS[row[0].value]
            row[col['Status']].value, row[col['Verdict']].value, row[col['Balance_Result']].value = state, verdict, figure
            row[col['Decision']].value = f"{row[col['Decision']].value or ''}; 2026-10-11: measured".strip('; ')
    wb.save(WORKBOOK)


if __name__ == '__main__':
    main()

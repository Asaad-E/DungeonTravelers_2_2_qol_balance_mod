"""One-off edit: the results of the sheet Regression of balance_criteria.xlsx with the figures of the full suite of
2026-10-16 (after the ATK of C36, Barrage 30% - 50% and the Etoile with Waltz and Salsa)."""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
RESULTS = {
    'R01': ('2026-10-16. measures/WIN_RATES.md (200 battles): the three parties that work in the game end level, Meta 93%, Dual-Support '
            '91%, Mage-Heavy 95% of wins over the 17 bosses of the battery (89%, 90%, 92% in the game); one cell of Meta (C38) and one '
            'of Mage-Heavy (C36) gain more than 15 points, C36 kept with a boss weak to the magic the variant mends'),
    'R02': ('2026-10-16. PARTY_BATTERY.md: 70 of 85 pairs at or above the floor in vanilla, 78 of 85 on the variant; no pair that met its '
            'floor in vanilla lost it (the one below it on the variant that was above it on 2026-10-13, Anti-Meta-Plus at C36, '
            'wins 0% in vanilla). CLASS_STAGES.md: 74 of 76 rows inside the band; the two slow rows (Assassin and Treasure Hunter '
            'of the treasure hunter role) win 98% - 100%'),
    'R04': ('2026-10-16. measures/REGRESSION_R04.md: with the role of the class changed for another, a party without the class reaches '
            'the floor at 19 of 25 pairs of boss and class on the variant, 25 of 31 in vanilla'),
    'R06': '2026-10-16. BALANCE_BUILD.md: 1,636 of 1,636 live rows built, 166 of them in the floor files, and each names the row it serves',
    'R08': ('2026-10-16. DIFFICULTY_CURVE.md (40 battles a boss): 33 of 44 checkpoints within the windows of vanilla, 10 easier (the ten '
            'accepted: C14, C15, C17, C19, C26, C29, C32, C37, C38, C40), 1 harder: C36 on its pressure (0.20 > 0.25), on the edge of the '
            'window; measures/curve_recheck.py C36 400: within every window (pressure 0.21 > 0.25; 1,000 battles: +15%, window 25%)'),
    'R09': ('2026-10-16. VERDICTS.md: of 181 rows, 83 closed, 86 not a problem, 12 out of the balance, 0 open; every row holds a figure '
            '(0 rest on an argument alone)'),
    'R10': ('2026-10-16. DIFFICULTY_CURVE.md, columns Lowest HP and Pressure: where a checkpoint leaves the window of vanilla on the easier '
            'side the party stands higher (lowest HP 15% > 31% at C29, 32% > 53% at C38, 30% > 40% at C40), never lower; C36 asks more '
            'of the party (pressure 0.20 > 0.25) and C26 too (0.06 > 0.10)'),
}

wb = openpyxl.load_workbook(PATH)
ws = wb['Regression']
header = [c.value for c in ws[1]]
col = next(i for i, h in enumerate(header, 1) if str(h).startswith('Result'))
verdict = header.index('Verdict') + 1
done = 0
for r in range(2, ws.max_row + 1):
    rid = ws.cell(r, 1).value
    if rid in RESULTS:
        ws.cell(r, col).value = RESULTS[rid]
        if rid == 'R09':
            ws.cell(r, verdict).value = 'met'
        done += 1
assert done == len(RESULTS), done
wb.save(PATH)
print('rows', done)

"""The abilities of summoned monsters (and of every enemy attack that shares them) say their figure: the rows added on
2026-10-12 to the sheet EnemyEffects of qol_rules.xlsx, with the label the box of the same skill of a party member
uses. Asked by the user from the screen of a summon (Covering Attack shown with no chance). Run once."""
import os
import openpyxl

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data_tables', 'qol_rules.xlsx')
ROWS = ((251, 'Double attack rate', 'pct'), (252, 'Triple attack rate', 'pct'), (259, 'Activation rate', 'pct'),
        (260, 'Activation rate', 'pct'), (283, 'Occurrence rate', 'pct'), (316, 'Speed', 'pct'),
        (211, 'Critical rate', 'plus_num_pct'), (216, 'TP recovery', 'num'), (129, 'TP recovery', 'pct'),
        (218, 'EXP', 'signed_pct'), (202, 'Resistance decrease', 'abs_num'), (193, 'All stats', 'signed_pct'),
        (26, 'ATK', 'signed_pct'), (28, 'DEF', 'signed_pct'), (179, 'Damage reduction rate', 'abs_pct'),
        (136, 'Power decrease', 'abs_pct'), (88, 'Damage vs. unholy', 'signed_pct'), (137, 'Targets', 'num'),
        (66, 'Pep', 'signed_num'))
wb = openpyxl.load_workbook(PATH)
ws = wb['EnemyEffects']
have = {row[0].value for row in ws.iter_rows(min_row=2)}
for row in ROWS:
    if row[0] not in have:
        ws.append(list(row))
wb.save(PATH)
print(len(ROWS), 'rows')

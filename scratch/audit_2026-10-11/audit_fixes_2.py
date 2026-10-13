"""Decided 2026-10-13 after the audit: the two grand sealbooks whose second enchantment cut the TP cost of the whole
party by a fifth lose it (Samael, Sukuna-Hikona); the EXP factor of a member 1 to 4 levels below the enemy is 1.15 in
the place of 1.25. Run once."""
import os
import openpyxl

TABLES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data_tables')
path = os.path.join(TABLES, 'balance_changes.xlsx')
wb = openpyxl.load_workbook(path)
ws = wb['Changes']
col = {c.value: k for k, c in enumerate(ws[1])}
for row in ws.iter_rows(min_row=2):
    if row[0].value in ('P002', 'P003'):
        row[col['State']].value = 'dropped'
        row[col['Why']].value = ('Dropped on 2026-10-13. The enchantment of a grand sealbook acts for every member, so this cut '
                                 'the TP cost of the whole party by a fifth. Measured (measures/grand_sealbook_trial.py, the '
                                 'reference party carrying the book, 150 battles): with Sukuna-Hikona a long fight (C40) goes from '
                                 '36.0 to 27.1 turns and from 91% to 97% of wins; the book of Samael does the same for spells. '
                                 'The other three second enchantments (P001, P004, P005) move nothing that can be measured and stay. '
                                 'Was: ' + str(row[col['Why']].value))
    if row[0].value in ('P001', 'P004', 'P005'):
        row[col['Why']].value = (str(row[col['Why']].value) + ' Measured on 2026-10-13 (measures/grand_sealbook_trial.py, 150 '
                                 'battles at C40, P08, P24 and P27): wins and lowest HP as with the one enchantment of the game; '
                                 'the critical floor of Melek Taus makes a long fight 4% shorter')
wb.save(path)

path = os.path.join(TABLES, 'balance_criteria.xlsx')
wb = openpyxl.load_workbook(path)
ws = wb['ExePatches']
col = {c.value: k for k, c in enumerate(ws[1])}
for row in ws.iter_rows(min_row=2):
    if row[0].value == 'X01':
        row[col['New_Hex']].value = '9c936d00'
        row[col['Float_After']].value = 1.15
        row[col['Meaning']].value = ('EXP factor by gap (member level - enemy level): 1 to 4 below the enemy, no piece. 1.15 since '
                                     '2026-10-13 (it was 1.25): a little less grind near the level of the enemies, closer to the '
                                     'game; the float is the one the game holds for the piece of enchantment 270 in this band')
ws = wb['CatchUpOptions']
for row in ws.iter_rows(min_row=2):
    if row[0].value == 'B4':
        row[2].value = '0.85, 0.9, 1, 1.15, 3, 5, 10'
        row[3].value = ('What is installed: the factors by gap of B4 in the program (1.15 from 1 level below the enemy since '
                        '2026-10-13, 1.25 before), the EXP of a level as in vanilla')
wb.save(path)
print('written')

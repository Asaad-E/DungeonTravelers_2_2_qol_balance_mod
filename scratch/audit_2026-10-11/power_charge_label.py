"""qol_rules.xlsx SkillEffectLabels: Power Charge (effect 191) shown as the multiple it gives, 1 + value (2026-10-16).
docs/FORMULAS.md 2.4: its value is added to the other bonus of the next physical blow, final = damage C * (1 + other bonuses)."""
import os
import openpyxl

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'qol_rules.xlsx')
wb = openpyxl.load_workbook(PATH)
ws = wb['SkillEffectLabels']
head = [c.value for c in ws[1]]
col = {name: i + 1 for i, name in enumerate(head)}
done = 0
for r in range(2, ws.max_row + 1):
    if ws.cell(r, col['Effect_ID']).value == 191:
        ws.cell(r, col['Style']).value = 'one_plus_mult'
        done += 1
assert done == 1, done
wb.save(PATH)
print('effect 191: one_plus_mult')

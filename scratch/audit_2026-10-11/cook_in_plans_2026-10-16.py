"""Roles: the skill plans of the maid and diva roles take Cook at level 1 right after Self Session (2026-10-16). A plan spends the points in
its order; with the SP curve of the variant (rows B001 - B040, one more point a level from 31 to 70) Song Mastery reached level 8 at
level 40 and left nothing for Cook, the TP of the party: the Mage-Heavy party survived 10% of the rows of 30 random battles at C27
(walk-parties) against 75% in vanilla, 65% once the curve was dropped."""
import os
import openpyxl

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'sim_setup.xlsx')
wb = openpyxl.load_workbook(PATH)
ws = wb['Roles']
head = [c.value for c in ws[1]]
col = {name: i + 1 for i, name in enumerate(head)}
done = []
for r in range(2, ws.max_row + 1):
    role = ws.cell(r, col['Role']).value
    if role in ('maid', 'diva'):
        plan = ws.cell(r, col['Skill plan']).value
        assert 'Self Session:1; ' in plan and 'Cook:1;' not in plan, (role, plan)
        ws.cell(r, col['Skill plan']).value = plan.replace('Self Session:1; ', 'Self Session:1; Cook:1; ', 1)
        ws.cell(r, col['Source']).value = str(ws.cell(r, col['Source']).value) + (
            ' | 2026-10-16: Cook:1 right after Self Session, so a plan never spends the points Cook needs (the TP of the party) on a '
            'level of Song Mastery.')
        done.append(role)
assert sorted(done) == ['diva', 'maid'], done
wb.save(PATH)
print('plans written', done)

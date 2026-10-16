"""Criticisms F60, F71, J21, J23, J18, J25: the figures of the skill niches of 2026-10-16 (rows V001 - V030, D061 - D070)."""
import os
import openpyxl

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'balance_criteria.xlsx')
ADD = {
    'F60': ' 2026-10-16: dtcli skill-battery found Shadow Clone still costing the Kunoichi more than it saved (51% of the cells '
           'worse); one more turn at every level (V016 - V020) makes it a niche.',
    'F71': ' 2026-10-16: Oracles took the place of a better doll (skill-battery: hurts); its action x1.5 (D061 - D070, ATK 328 - 421%) '
           'makes it a niche; class-search C34, C38 over the 7,402 final-class parties with a Soul Summoner: wins 70.2% > 70.5%, no '
           'dominant party.',
    'J21': ' 2026-10-16: the Dark Lord of the model lost her charge to Berserk (sheet Policies fixed); Power Charge 1.13 - 1.40, the '
           'charged blow x2.13 - x2.4 (V001 - V005): skill-battery good; class-search C34, C38 over the 7,632 final-class parties with a '
           'Dark Lord: wins 69.9% > 70.6%, no dominant party.',
    'J23': ' 2026-10-16: Accelerator 10 - 15% for 4 turns (V006 - V015), given by the model to the ally who hits hardest, and Prism '
           'Dawn x1.4 power (V021 - V030): both a niche in dtcli skill-battery (they were weak or dead).',
    'J18': ' 2026-10-16: the Soul Summoner herself dealt 1 - 2% of the damage of her party; Soul Eater 20% cheaper and 15% stronger '
           '(V031 - V050), learned by the model: class-search over the 14,804 final-class parties with her, wins 53.2% > 54.0%.',
    'J25': ' 2026-10-16: Magical Change two turns longer and 25% stronger, Magical Spark 20% cheaper (V051 - V061, C098 - C106): '
           'class-search over the 15,289 final-class parties with her, wins 47.5% > 50.6%, fights 9% shorter, no dominant party.',
}

wb = openpyxl.load_workbook(PATH)
ws = wb['Criticisms']
head = [c.value for c in ws[1]]
col = {name: i + 1 for i, name in enumerate(head)}
done = set()
for r in range(2, ws.max_row + 1):
    rid = ws.cell(r, col['ID']).value
    if rid in ADD:
        cell = ws.cell(r, col['Balance_Result'])
        text = cell.value or ''
        if ADD[rid].strip() not in text:
            cell.value = (text.rstrip() + ADD[rid]).strip()
        done.add(rid)
assert done == set(ADD), done
wb.save(PATH)
print('written', sorted(done))

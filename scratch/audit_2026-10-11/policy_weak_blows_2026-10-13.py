"""One-off edit (2026-10-13) of sim/policy.py and of the sheet Settings: no member strikes with a plain blow an enemy
that answers it (Avenger, Dark Aura) when the blow would take less than a set share of the HP of that enemy: she
defends. The Soul Summoner, the Doll Master and the Mistress of the party Anti-Meta-Plus, out of TP at C30, hit a
boss with Dark Aura fifty times a fight for none of the damage of the party and lost a tenth of every stat each
time. Run once; kept as the record of the edit.
"""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POLICY = os.path.join(ROOT, 'sim', 'policy.py')
SETUP = os.path.join(ROOT, 'data_tables', 'sim_setup.xlsx')
EDITS = [
("""        if self.heals(unit) and punished(unit, attack, target):
            return Action(unit, 'defend')             # a healer does not trade blows with an enemy that answers them
""", """        if punished(unit, attack, target) and (self.heals(unit) or self.weak_blow(battle, attack, target)):
            return Action(unit, 'defend')             # a blow that is answered is not struck by a healer, nor for nothing
"""),
("""    def heal_reserve(self, battle, unit):""", """    def weak_blow(self, battle, action, target):
        \"\"\"Whether a plain blow takes less of the max HP of its target than the setting punished_blow_floor: not worth
        the answer of an enemy that punishes it.\"\"\"
        floor = float(self.setup.get('punished_blow_floor', 0) or 0)
        return bool(floor) and battle.expected_damage(action, target) < floor * target.max_hp

    def heal_reserve(self, battle, unit):"""),
("""        if action.kind == 'attack' and policy.heals(unit) and punished(unit, action, target):
            continue
""", """        if action.kind == 'attack' and punished(unit, action, target) and \
                (policy.heals(unit) or policy.weak_blow(battle, action, target)):
            continue
"""),
]
SETTING = ('punished_blow_floor', 0.01, 'A plain blow that takes less than this share of the max HP of an enemy with Avenger or '
           'Dark Aura is not struck: the member defends (sim/policy.py weak_blow)',
           'choice (2026-10-13): a blow worth less than a hundredth of the boss is not worth a tenth of every stat')

with open(POLICY, encoding='utf-8') as f:
    text = f.read()
for old, new in EDITS:
    assert text.count(old) == 1, old
    text = text.replace(old, new)
with open(POLICY, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
wb = openpyxl.load_workbook(SETUP)
ws = wb['Settings']
assert SETTING[0] not in {r[0].value for r in ws.iter_rows()}
ws.append(SETTING)
wb.save(SETUP)
print('weak blows')

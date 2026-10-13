"""One-off edit (2026-10-13) of sim/policy.py: the habits of "a member who heals" are those of a healer of the back row
who holds a healing skill, not of every role with a heal rule: a tank in the front row with Heal, or a Treasure Hunter
who heals with items, fights as before. Run once; kept as the record of the edit.
"""
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sim', 'policy.py')
EDITS = [
('''    def heals(self, unit):
        """Whether one of the rules of the member heals: she is a heal of her party."""
        return any(action == 'heal' for _, _, action, _ in self.rules.get(getattr(unit, 'role', 'attacker'), []))
''', '''    def heal_costs(self, battle, unit):
        """The TP of each healing skill the member holds, at the level she holds it."""
        costs = []
        for skill_id, level in unit.skills.items():
            skill = battle.data.skill_by_id.get(skill_id)
            if skill is not None and usable_in_battle(skill) and any(gives(skill, e) for e in HEAL_EFFECTS):
                costs.append(skill.tp[max(1, min(level, skill.levels)) - 1])
        return costs

    def heals(self, battle, unit):
        """Whether the member is a healer of her party: one of her rules heals, she holds a healing skill, and she
        stands in the back row. A tank of the front row who also has Heal, or a member who heals with items alone,
        is not: she fights."""
        role = getattr(unit, 'role', 'attacker')
        return (not unit.front and any(action == 'heal' for _, _, action, _ in self.rules.get(role, []))
                and bool(self.heal_costs(battle, unit)))
'''),
('''        casts = float(self.setup.get('heal_reserve_casts', 0) or 0)
        role = getattr(unit, 'role', 'attacker')
        if not casts or not any(action == 'heal' for _, _, action, _ in self.rules.get(role, [])):
            return 0.0
        costs = []
        for skill_id, level in unit.skills.items():
            skill = battle.data.skill_by_id.get(skill_id)
            if skill is not None and usable_in_battle(skill) and any(gives(skill, e) for e in HEAL_EFFECTS):
                costs.append(skill.tp[max(1, min(level, skill.levels)) - 1])
        return casts * min(costs) if costs else 0.0
''', '''        casts = float(self.setup.get('heal_reserve_casts', 0) or 0)
        if not casts or not self.heals(battle, unit):
            return 0.0
        return casts * min(self.heal_costs(battle, unit))
'''),
("if punished(unit, attack, target) and (self.heals(unit) or self.weak_blow(battle, attack, target)):",
 "if punished(unit, attack, target) and (self.heals(battle, unit) or self.weak_blow(battle, attack, target)):"),
("(policy.heals(unit) or policy.weak_blow(battle, action, target)):",
 "(policy.heals(battle, unit) or policy.weak_blow(battle, action, target)):"),
('''        """The TP a member who heals keeps back from her buffs and her attacks: the cost of heal_reserve_casts of her
        cheapest heal, when one of her rules heals and she holds a heal.''',
 '''        """The TP a healer (heals) keeps back from her buffs and her attacks: the cost of heal_reserve_casts of her
        cheapest heal.'''),
]
with open(PATH, encoding='utf-8') as f:
    text = f.read()
for old, new in EDITS:
    assert text.count(old) == 1, old
    text = text.replace(old, new)
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
print(len(EDITS), 'edits')

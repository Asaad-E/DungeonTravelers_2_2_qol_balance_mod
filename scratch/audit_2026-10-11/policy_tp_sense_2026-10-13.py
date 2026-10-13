"""One-off edit (2026-10-13) of sim/policy.py and of the sheet Settings of sim_setup.xlsx: two habits of a player the
model lacked. A member whose rules heal keeps the TP of some heals before she spends on a buff or on damage; and a
buff of the whole party is cast again when a share of its members lack it, not when one does. Both sizes are
settings. Run once; kept as the record of the edit.
"""
import os

import openpyxl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POLICY = os.path.join(ROOT, 'sim', 'policy.py')
SETUP = os.path.join(ROOT, 'data_tables', 'sim_setup.xlsx')
EDITS = [
("""    def tp_penalty(self, unit, action):""", """    def heal_reserve(self, battle, unit):
        \"\"\"The TP a member who heals keeps back from her buffs and her attacks: the cost of heal_reserve_casts of her
        cheapest heal, when one of her rules heals and she holds a heal. A player who is the heal of a party does not
        spend her last TP on a spell of fire.\"\"\"
        casts = float(self.setup.get('heal_reserve_casts', 0) or 0)
        role = getattr(unit, 'role', 'attacker')
        if not casts or not any(action == 'heal' for _, _, action, _ in self.rules.get(role, [])):
            return 0.0
        costs = []
        for skill_id, level in unit.skills.items():
            skill = battle.data.skill_by_id.get(skill_id)
            if skill is not None and usable_in_battle(skill) and any(gives(skill, e) for e in HEAL_EFFECTS):
                costs.append(skill.tp[max(1, min(level, skill.levels)) - 1])
        return casts * min(costs) if costs else 0.0

    def tp_penalty(self, unit, action):"""),
("""        if action.tp_cost > unit.tp * (1.0 - policy.setup.get('tp_reserve', 0.0)) and action.tp_cost > 0:
            continue
        total, target = damage_value(battle, action)""", """        if action.tp_cost > unit.tp * (1.0 - policy.setup.get('tp_reserve', 0.0)) and action.tp_cost > 0:
            continue
        if action.tp_cost > 0 and unit.tp - action.tp_cost < reserve:
            continue
        total, target = damage_value(battle, action)"""),
("""    plain_attack = Action(unit, 'attack')
    plain_total, plain_target = damage_value(battle, plain_attack)""", """    reserve = policy.heal_reserve(battle, unit)
    plain_attack = Action(unit, 'attack')
    plain_total, plain_target = damage_value(battle, plain_attack)"""),
("""    effect = int(arg)
    for skill, level in options(battle, unit):
        if not puts(skill, effect):
            continue
        action = Action(unit, 'skill', skill, level)
""", """    effect = int(arg)
    reserve = policy.heal_reserve(battle, unit)
    for skill, level in options(battle, unit):
        if not puts(skill, effect):
            continue
        action = Action(unit, 'skill', skill, level)
        if action.tp_cost > 0 and unit.tp - action.tp_cost < reserve:
            continue
"""),
("""        if code in (ALLIES, ALLY_ROW):
            if all(effect in m.statuses for m in battle.allies(unit) if m.kind == 'member'):
                continue
            return action""", """        if code in (ALLIES, ALLY_ROW):
            # cast again when a share of the members lack it, not for one who was revived or lost it alone
            members = [m for m in battle.allies(unit) if m.kind == 'member']
            lacking = sum(1 for m in members if effect not in m.statuses)
            share = float(policy.setup.get('party_buff_recast_share', 0) or 0)
            if not lacking or lacking < share * len(members):
                continue
            return action"""),
]
SETTINGS = [
    ('heal_reserve_casts', 2, 'TP a member whose rules heal keeps back from her buffs and attacks: this many casts of her '
     'cheapest heal (sim/policy.py heal_reserve)', 'choice (2026-10-13): what a player who is the heal of a party does; without '
     'it the Sage of the party Mage-Heavy spent the TP of the party on Fireball and on casting her buffs again'),
    ('party_buff_recast_share', 0.5, 'A buff of the whole party is cast again when at least this share of its members lack it',
     'choice (2026-10-13): one member who lost it alone does not call for 22 TP'),
]


def main():
    with open(POLICY, encoding='utf-8') as f:
        text = f.read()
    for old, new in EDITS:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    with open(POLICY, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    wb = openpyxl.load_workbook(SETUP)
    ws = wb['Settings']
    have = {r[0].value for r in ws.iter_rows()}
    for row in SETTINGS:
        assert row[0] not in have
        ws.append(row)
    wb.save(SETUP)
    print(len(EDITS), 'edits,', len(SETTINGS), 'settings')


if __name__ == '__main__':
    main()

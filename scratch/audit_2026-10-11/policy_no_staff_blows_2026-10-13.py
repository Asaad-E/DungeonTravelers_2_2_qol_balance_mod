"""One-off edit (2026-10-13) of sim/policy.py: a member who heals does not strike with a plain blow an enemy that
punishes it (Avenger, which strikes back, or Dark Aura, which lowers her stats): she defends. Without it the healer
and the Sage, out of TP, hit the last boss with their staffs and were struck back. Run once; kept as the record.
"""
import os

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sim', 'policy.py')
EDITS = [
("""    def heal_reserve(self, battle, unit):""", """    def heals(self, unit):
        \"\"\"Whether one of the rules of the member heals: she is a heal of her party.\"\"\"
        return any(action == 'heal' for _, _, action, _ in self.rules.get(getattr(unit, 'role', 'attacker'), []))

    def heal_reserve(self, battle, unit):"""),
("""        attack = Action(unit, 'attack')
        target = best_single_target(battle, unit, attack)
        if target is None or battle.expected_damage(attack, target) <= 0:
            return Action(unit, 'defend')             # nothing it can do lands: a player defends
""", """        attack = Action(unit, 'attack')
        target = best_single_target(battle, unit, attack)
        if target is None or battle.expected_damage(attack, target) <= 0:
            return Action(unit, 'defend')             # nothing it can do lands: a player defends
        if self.heals(unit) and punished(unit, attack, target):
            return Action(unit, 'defend')             # a healer does not trade blows with an enemy that answers them
"""),
("""def act_damage(policy, battle, unit, arg):""", """def punished(unit, action, target):
    \"\"\"Whether a physical blow on this enemy is answered: Avenger (249) strikes back at a short or mid reach, Dark Aura
    (262) lowers the stats of who hits at short reach (sim/battle.py, after a hit), unless the member is protected
    (307, 304).\"\"\"
    if target is None or not action.physical:
        return False
    return (target.has(249) and action.reach in (SHORT, MID) and not unit.has(307)) or \\
        (target.has(262) and action.reach == SHORT and not unit.has(304))


def act_damage(policy, battle, unit, arg):"""),
("""        total, target = damage_value(battle, action)
        if total <= 0:
            continue

        wait_time = policy.time_of(battle, action)""", """        total, target = damage_value(battle, action)
        if total <= 0:
            continue
        if action.kind == 'attack' and policy.heals(unit) and punished(unit, action, target):
            continue

        wait_time = policy.time_of(battle, action)"""),
]


def main():
    with open(PATH, encoding='utf-8') as f:
        text = f.read()
    for old, new in EDITS:
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(len(EDITS), 'edits')


if __name__ == '__main__':
    main()

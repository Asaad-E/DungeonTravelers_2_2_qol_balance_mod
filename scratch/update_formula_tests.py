with open('mod_project/tests/test_sim_formulas.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the EngineParityFixes class
target_start = 'class EngineParityFixes(unittest.TestCase):'
assert target_start in text

parts = text.split(target_start)
header = parts[0]

new_class = '''class EngineParityFixes(unittest.TestCase):
    def test_magic_hit_enchant_cap_50(self):
        """FORMULAS 3 (0x44d67b): magic accuracy enchants count 3/1 per piece, capped at 50 in engine."""
        from sim.battle import Battle, Action
        from sim.data import Skill
        from sim.units import Unit, PARTY, ENEMIES
        import random
        member = Unit('Mage', PARTY, 50, 1, 0, {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')})
        member.enchants = {39: 30}  # 30 * 3 = 90, clamped to 50
        target = Unit('Target', ENEMIES, 50, 1, 0, {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')})
        battle = Battle(None, [member], [target], random.Random(0))
        skill = Skill(id=998, name='TestSpell', accuracy=[0.5], effects=[(1, 2, [1.0])])
        action = Action(member, 'skill', skill, 1)
        chance = battle.hit_chance(action, target)
        self.assertAlmostEqual(chance, 0.95)

    def test_fixed_accuracy_physical_floor_preserved(self):
        """FORMULAS 16.5 (0x44afbe): physical blows clamp fixed accuracy (55/72) to 5..100 floor."""
        from sim.battle import Battle, Action
        from sim.data import Skill
        from sim.units import Unit, PARTY, ENEMIES
        import random
        member = Unit('Attacker', PARTY, 50, 1, 0, {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')})
        target = Unit('Defender', ENEMIES, 50, 1, 0, {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')})
        battle = Battle(None, [member], [target], random.Random(0))
        # Fixed accuracy of 0.02 (2%) is clamped up to 5% (0.05) by the second clamp at 0x44afbe
        skill = Skill(id=999, name='TestFixed', effects=[(0, 2, [1.0]), (55, 2, [0.02])])
        action = Action(member, 'skill', skill, 1)
        chance = battle.hit_chance(action, target)
        self.assertEqual(chance, 0.05)

    def test_race_factor_additive_with_effect_88(self):
        """FORMULAS 16.7 (0x44bfa4): race factor is additive 1 + effect 88 + bonus in damage engine."""
        from sim.battle import Battle, Action
        from sim.data import Skill
        from sim.units import Unit, PARTY, ENEMIES
        import random
        member = Unit('Attacker', PARTY, 50, 1, 0, {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')})
        member.enchants = {180: 1}  # Race 5 (Undead) UP: +0.15
        target = Unit('Defender', ENEMIES, 50, 1, 0, {s: 0 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')}, race=5)
        battle = Battle(None, [member], [target], random.Random(0))
        skill = Skill(id=999, name='AntiUndead', effects=[(0, 2, [1.0]), (88, 2, [1.0])])
        action = Action(member, 'skill', skill, 1)
        rf = battle.race_factor(member, target) + action.value(88)
        self.assertAlmostEqual(rf, 2.15)
        dmg = battle.physical_damage(action, target, 0, False)
        self.assertEqual(dmg, 430)


if __name__ == '__main__':
    unittest.main()
'''

with open('mod_project/tests/test_sim_formulas.py', 'w', encoding='utf-8') as f:
    f.write(header + new_class)

print('Updated test_sim_formulas.py!')

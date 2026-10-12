"""The formulas of sim/formulas.py against what the executable states and against a player test."""
import os
import sys
import unittest

import _paths
sys.path.insert(0, _paths.PROJECT_DIR)
from sim import formulas as f
from sim import progression


class TurnOrder(unittest.TestCase):
    def test_reproduces_the_speed_test_of_the_japanese_wiki(self):
        """pages/105.html: A (rank A, AGI 261, five speed UP) and B (rank B, AGI 47, n speed UP) only defend;
        turns of A during 10 turns of B were 80, 76, 71, 67, 63, 58, 58 for n = 0..6. B is a level 1
        crowned character. No constant is fitted."""
        measured = [80, 76, 71, 67, 63, 58, 58]
        wait_a = f.wait(261, 1.20, 1, bonus=f.speed_enchant_bonus(up=5), defending=True)
        self.assertAlmostEqual(wait_a, 0.08)                    # A sits on the cap
        for n, turns in enumerate(measured):
            wait_b = f.wait(47, 1.60, 1, bonus=f.speed_enchant_bonus(up=n), defending=True)
            with self.subTest(speed_up=n):
                self.assertAlmostEqual(10 * wait_b / wait_a, turns, delta=0.7)

    def test_cap_and_slow(self):
        self.assertEqual(f.turn_value(999, 1.0, 1), f.VALUE_CAP)
        fast, slow = f.turn_value(100, 2.0, 50), f.turn_value(100, 2.0, 50, slowed=True)
        self.assertAlmostEqual(slow, fast / 2)

    def test_the_weapon_term_grows_with_level_and_hurts_slow_units_more(self):
        loss = lambda agi, level: 1 - f.turn_value(agi, 2.90, level) / f.turn_value(agi, 1.00, level)
        self.assertGreater(loss(60, 99), loss(60, 1))           # the same weapon costs more at a higher level
        self.assertGreater(loss(60, 50), loss(160, 50))         # and more to a slow unit than to a fast one


class Damage(unittest.TestCase):
    def test_defence_is_subtracted(self):
        self.assertEqual(f.physical_damage(50, 100), 0.0)                       # 100 against 135
        self.assertAlmostEqual(f.physical_damage(100, 100), 200 - 135)
        # a skill of +100% triples what gets through when attack is close to defence
        self.assertAlmostEqual(f.physical_damage(100, 100, modifiers=1.0) / f.physical_damage(100, 100), (400 - 135) / 65)

    def test_buffs_add_to_the_power_of_the_skill(self):
        self.assertAlmostEqual(f.attack_value(100, modifiers=1.0 + 0.18), 100 * 2 * 2.18)

    def test_resistance_is_half_a_percent_per_point(self):
        self.assertAlmostEqual(f.resistance_factor(100), 0.5)
        self.assertAlmostEqual(f.resistance_factor(-20), 1.1)
        self.assertAlmostEqual(f.physical_damage(200, 100, resistance=100), (400 - 135) * 0.5)

    def test_magic_adds_the_power_of_the_spell_to_int(self):
        self.assertAlmostEqual(f.magic_damage(100, 300, 100), 100 * 2 + 300 - 150)

    def test_hit_limits(self):
        self.assertEqual(f.physical_hit(1, 99999), f.HIT_MIN)
        self.assertEqual(f.physical_hit(999, 1), f.HIT_MAX)
        self.assertEqual(f.magic_hit(0.0, 1, 999), f.MAGIC_HIT_MIN)
        self.assertEqual(f.magic_hit(2.0, 999, 1), f.MAGIC_HIT_MAX)


class Interruption(unittest.TestCase):
    def test_grows_with_damage_against_max_hp(self):
        # the divisor is max HP * 1.5 + 1 + modifier (0x44d02b - 0x44d042: the program adds where its message multiplies),
        # and the rate is cut to a whole percent
        self.assertAlmostEqual(f.interruption_chance(300, 1000), 0.19)
        self.assertAlmostEqual(f.interruption_chance(750, 1000), 0.49)
        self.assertEqual(f.interruption_chance(5000, 1000), f.INTERRUPT_MAX)
        # Concentrate at its top level changes nothing that a whole percent can show
        self.assertEqual(f.interruption_chance(300, 1000, modifier=0.5), f.interruption_chance(300, 1000))
        self.assertAlmostEqual(f.interruption_chance(0, 1000, critical=True), 0.33)       # the 1 in 3 of the lessons
        self.assertAlmostEqual(f.interruption_chance(750, 1000, critical=True), 1 - 0.51 * 0.67)



class Range(unittest.TestCase):
    def test_the_lesson_of_the_game_is_what_the_code_does(self):
        """Lesson 7: a short-range weapon does 100, 75 from or into the back row, 50 when both are in the back."""
        self.assertEqual([f.range_factor(f.SHORT, d) for d in (0, 1, 2)], [1.0, 0.75, 0.5])
        self.assertEqual([f.range_factor(f.MID, d) for d in (0, 1, 2)], [1.0, 1.0, 0.75])
        self.assertEqual([f.range_factor(f.LONG, d) for d in (0, 1, 2)], [1.0, 1.0, 1.0])
        self.assertEqual(f.distance(True, True), 2)


class Ailments(unittest.TestCase):
    def test_resistance_removes_a_tenth_of_the_chance_per_ten_points(self):
        self.assertAlmostEqual(f.ailment_chance(0.30, 0), 30.0)
        self.assertAlmostEqual(f.ailment_chance(0.30, 9), 30.0)        # below ten points nothing changes
        self.assertAlmostEqual(f.ailment_chance(0.30, 50), 15.0)
        self.assertAlmostEqual(f.ailment_chance(0.30, 100), 0.0)       # the "block" the game announces
        self.assertAlmostEqual(f.ailment_chance(0.30, -20), 36.0)


class Targets(unittest.TestCase):
    def test_every_formation_shares_out_one_hundred(self):
        for row in f.TARGET_SHARE:
            self.assertEqual(sum(row), 100)

    def test_a_provoke_of_250_draws_about_four_attacks_in_five(self):
        """Three in front and two behind; the first one has put an effect 170 of 250 on the enemy."""
        share = f.TARGET_SHARE[9]
        weights = [f.target_weight(share[0], provoked=250.0)] + [f.target_weight(s) for s in share[1:]]
        chances = f.target_chances(weights)
        self.assertAlmostEqual(chances[0], 274 / 350)
        self.assertAlmostEqual(sum(chances), 1.0)

    def test_enchantments_and_the_floor(self):
        self.assertEqual(f.target_weight(24, up=2), 44)
        self.assertEqual(f.target_weight(14, down=1), 10)          # 9 is lifted to the floor
        self.assertEqual(f.target_weight(14, down=5), f.ENMITY_MIN)



class Critical(unittest.TestCase):
    def test_limits(self):
        self.assertEqual(f.critical_rate(1, 999, 1, 99), f.CRIT_MIN)
        self.assertEqual(f.critical_rate(1, 999, 1, 99, floor_268=True), f.CRIT_MIN_268)
        self.assertEqual(f.critical_rate(999, 1, 99, 1, skill=80), f.CRIT_MAX)
        self.assertEqual(f.critical_rate(1, 999, 1, 99, fixed=1.0), 100.0)

    def test_equal_dex_and_agi_give_ten_and_a_piece_adds_eight_percent_of_it(self):
        self.assertAlmostEqual(f.critical_rate(100, 100, 50, 50), 10.0)
        self.assertAlmostEqual(f.critical_rate(100, 100, 50, 50, enchant=f.critical_enchant(up=1)), 10.8)
        self.assertAlmostEqual(f.critical_rate(100, 100, 50, 50, target_enchant=-f.critical_enchant(up=2)), 8.4)
        self.assertEqual(f.critical_enchant(up=20), f.CRIT_ENCHANT_MAX)

    def test_a_critical_hit_is_a_quarter_more_damage(self):
        self.assertAlmostEqual(f.expected_critical_factor(50.0), 1.125)       # the most a build can average
        self.assertAlmostEqual(f.expected_critical_factor(5.9), 1.0125)       # the rate is cut to an integer



class Healing(unittest.TestCase):
    def test_half_of_res_times_the_coefficient(self):
        self.assertEqual(f.heal(200, 3.0), 300)
        self.assertEqual(f.heal(200, 3.0, mastery=0.5), 450)
        self.assertEqual([f.heal(100, 1.0, random=r) for r in f.HEAL_RANDOM], [48, 49, 50, 51, 52])

    def test_cap_and_its_bonus(self):
        self.assertEqual(f.heal(999, 9.0, cap=500), 500)
        self.assertEqual(f.heal(999, 9.0, cap=500, cap_bonus=0.2), 600)

    def test_recovery_by_fraction_of_the_target(self):
        self.assertEqual(f.fraction_recovery(1234, 0.3), 370)
        self.assertEqual(f.fraction_recovery(1234, 0.5, cap=500), 500)

    def test_doll_pieces_stop_at_one(self):
        self.assertAlmostEqual(f.doll_heal_bonus(up=1), 0.4)
        self.assertAlmostEqual(f.doll_heal_bonus(up=5, mini_up=5), 1.0)



class Experience(unittest.TestCase):
    def test_factor_by_level_gap_is_the_table_of_the_code(self):
        gaps = {12: 0.85, 10: 0.85, 9: 0.9, 5: 0.9, 4: 1.0, 0: 1.0, -1: 1.0, -4: 1.0, -5: 1.1, -9: 1.1, -10: 1.25, -19: 1.25, -20: 1.25, -60: 1.25}
        for gap, factor in gaps.items():
            with self.subTest(gap=gap):
                self.assertEqual(progression.level_gap_factor(50 + gap, 50), factor)
        self.assertEqual([progression.level_gap_factor(50 + gap, 50, more_from_higher=True) for gap in (-1, -5, -10, -20)],
                         [1.15, 1.3, 1.5, 1.75])

    def test_share_among_the_living_and_the_doublings(self):
        enemies = [(30, 1000), (30, 500)]
        self.assertAlmostEqual(progression.battle_exp(30, enemies, living=5), 300.0)
        self.assertAlmostEqual(progression.battle_exp(30, enemies, living=3), 500.0)
        self.assertAlmostEqual(progression.battle_exp(15, enemies, living=5), 375.0)           # 1.25 for the gap
        self.assertAlmostEqual(progression.battle_exp(30, enemies, living=5, double_exp_piece=True, doubled=True), 1200.0)

    def test_battles_to_reach_a_level(self):
        steps = {level: 1000 for level in range(2, 100)}
        formations = [(100, [(50, 500)])]
        self.assertAlmostEqual(progression.battles_to_reach(50, 52, steps, formations, living=5), 20.0)
        behind = progression.battles_to_reach(30, 32, steps, formations, living=5)
        self.assertAlmostEqual(behind, 16.0)                                                     # 1.25 times faster



class LevelReset(unittest.TestCase):
    def test_the_three_recipes_of_the_player_guide_reach_the_cap(self):
        """atwiki dt2-2 page 79: 25 resets from level 70; 16 from 80 and one from 70; 12 from 90 and one from 70."""
        def after(resets):
            bonus = 0
            for level in resets:
                bonus = progression.reset_bonus(level, 1, bonus)
            return bonus
        self.assertEqual(after([70] * 25), progression.RESET_MAX)
        self.assertEqual(after([70] * 24), 48)
        self.assertEqual(after([80] * 16 + [70]), progression.RESET_MAX)
        self.assertEqual(after([90] * 12 + [70]), progression.RESET_MAX)
        self.assertEqual(after([99] * 10), progression.RESET_MAX)
        self.assertEqual(after([59]), 0)                     # 58 levels given up: nothing
        self.assertEqual(after([60]), 1)



class Encounters(unittest.TestCase):
    def test_chance_per_step(self):
        """_CheckEncount (0x4bc6a0): zone chance, plus Whistle, plus the pieces, never below 1; 0 stays 0."""
        self.assertEqual(progression.encounter_chance(6), 6)
        self.assertEqual(progression.encounter_chance(6, alarm=4), 10)
        self.assertEqual(progression.encounter_chance(6, pieces=(211, 212)), 3)
        self.assertEqual(progression.encounter_chance(2, pieces=(211, 212)), 1)
        self.assertEqual(progression.encounter_chance(0, alarm=4), 0)

    def test_steps_between_battles(self):
        self.assertAlmostEqual(progression.steps_between_battles(10), 18)
        self.assertAlmostEqual(progression.steps_between_battles(5), 28)
        self.assertEqual(progression.steps_between_battles(0), float('inf'))


class EngineParityFixes(unittest.TestCase):
    @staticmethod
    def _magic_hit(pieces, accuracy):
        """Hit chance of a spell of this accuracy cast by a member with these enchantment pieces, INT equal to RES."""
        from sim.battle import Battle, Action
        from sim.data import Skill
        from sim.units import Unit, PARTY, ENEMIES
        import random
        member = Unit('Mage', PARTY, 50, 1, 0, {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')})
        member.enchants = dict(pieces)
        target = Unit('Target', ENEMIES, 50, 1, 0, {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')})
        battle = Battle(None, [member], [target], random.Random(0))
        skill = Skill(id=998, name='TestSpell', accuracy=[accuracy], effects=[(1, 2, [1.0])])
        return battle.hit_chance(Action(member, 'skill', skill, 1), target)

    def test_magic_hit_enchant_cap_50(self):
        """0x44d699: the sum of magic accuracy enchantments stops at 50. 30 pieces of 39 are 90 points: with the cap
        an accuracy of 0.30 gives 80%, without it the 95% of the upper limit."""
        self.assertAlmostEqual(self._magic_hit({39: 30}, 0.30), 0.80)
        self.assertAlmostEqual(self._magic_hit({39: 5}, 0.30), 0.45)

    def test_magic_hit_mini_up_counts_one(self):
        """0x44d6a3 - 0x44d6bd: a piece of Magic accuracy MiniUP (40) adds 1 point, a piece of UP (39) adds 3."""
        self.assertAlmostEqual(self._magic_hit({40: 10}, 0.30), 0.40)
        self.assertAlmostEqual(self._magic_hit({39: 10}, 0.30), 0.60)

    def test_ailment_threshold_is_an_integer_in_single_precision(self):
        """0x481fa9 - 0x48201d: value * 100 in single precision, less a tenth for every ten points of resistance,
        cut to an integer. 0.29 * 100 is 29 in single precision (28.999... in double); 0.88 against 30 is 61.6."""
        self.assertEqual(f.ailment_threshold(0.29, 0), 29)
        self.assertEqual(f.ailment_threshold(0.88, 30), 61)
        self.assertEqual(f.ailment_threshold(0.90, 30), 63)
        self.assertEqual(f.ailment_threshold(0.30, 100), 0)
        self.assertEqual(f.ailment_threshold(0.30, -20), 36)

    def test_trap_enchantment_does_not_touch_a_battle_ailment(self):
        """Enchantment 269 ("Less likely to trigger traps") takes 15 points only from a trap (0x481ff3); an ailment
        of a battle lands on its bearer at the same chance."""
        from sim.battle import Battle
        from sim.units import Unit, PARTY, ENEMIES
        import random
        stats = {s: 100 for s in ('atk', 'def', 'int', 'res', 'dex', 'agi')}

        def landed(pieces):
            count = 0
            for seed in range(400):
                target = Unit('Target', PARTY, 50, 100, 0, dict(stats))
                target.enchants = dict(pieces)
                enemy = Unit('Enemy', ENEMIES, 50, 100, 0, dict(stats))
                battle = Battle(None, [target], [enemy], random.Random(seed))
                count += bool(battle.apply_ailment(enemy, target, 113, 0.5, None))
            return count
        self.assertEqual(landed({269: 1}), landed({}))

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

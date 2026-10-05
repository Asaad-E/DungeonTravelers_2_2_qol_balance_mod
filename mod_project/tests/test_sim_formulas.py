"""The formulas of sim/formulas.py against what the executable states and against a player test."""
import os
import sys
import unittest

import _paths
sys.path.insert(0, _paths.PROJECT_DIR)
from sim import formulas as f


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
        self.assertAlmostEqual(f.interruption_chance(300, 1000), 0.2)
        self.assertAlmostEqual(f.interruption_chance(750, 1000), 0.5)
        self.assertEqual(f.interruption_chance(5000, 1000), f.INTERRUPT_MAX)
        self.assertLess(f.interruption_chance(300, 1000, modifier=0.5), f.interruption_chance(300, 1000))


if __name__ == '__main__':
    unittest.main()


class Range(unittest.TestCase):
    def test_the_lesson_of_the_game_is_what_the_code_does(self):
        """Lesson 7: a short-range weapon does 100, 75 from or into the back row, 50 when both are in the back."""
        self.assertEqual([f.range_factor(f.SHORT, d) for d in (0, 1, 2)], [1.0, 0.75, 0.5])
        self.assertEqual([f.range_factor(f.MID, d) for d in (0, 1, 2)], [1.0, 1.0, 0.75])
        self.assertEqual([f.range_factor(f.LONG, d) for d in (0, 1, 2)], [1.0, 1.0, 1.0])
        self.assertEqual(f.distance(True, True), 2)

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

    def test_doll_pieces_stop_at_one(self):
        self.assertAlmostEqual(f.doll_heal_bonus(up=1), 0.4)
        self.assertAlmostEqual(f.doll_heal_bonus(up=5, mini_up=5), 1.0)


if __name__ == '__main__':
    unittest.main()

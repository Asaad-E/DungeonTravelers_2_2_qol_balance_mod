"""The simulator against what players measured in the game (sheet Calibration of data_tables/sim_setup.xlsx).

Each class is one row of the sheet; its docstring names the row and the page the figures come from. The figures are
the players' own and are copied here only as the expected results of a test."""
import math
import sys
import unittest

import _paths
sys.path.insert(0, _paths.PROJECT_DIR)
from sim import formulas as f
from sim import progression
from sim.data import game_data
from sim.battle import Action
from sim.units import Unit, PARTY, build_summon

STATS = ('atk', 'def', 'int', 'res', 'dex', 'agi')


class CriticalFactor(unittest.TestCase):
    def test_the_sealbook_test_fits_a_quarter_more(self):
        """K03, atwiki dt2-2 page 105 (Heqet sealbook): unarmed hits of Yae and Luco on Hola-Orange went from 170 to
        213 and from 52 to 65 on a critical hit. Damage is kept as an integer after the factor, so a normal hit of
        170 is some x with int(x) = 170, and the critical one int(x * 1.25) must be possible for such an x."""
        for normal, critical in ((170, 213), (52, 65)):
            low = max(normal, critical / f.CRIT_FACTOR)
            high = min(normal + 1, (critical + 1) / f.CRIT_FACTOR)
            with self.subTest(normal=normal):
                self.assertLess(low, high)


class SummonStats(unittest.TestCase):
    """K05, atwiki dt2-2 page 105: [best stat of the party, stat of the summon] pairs, and the lowest stats."""
    LOWEST = {'Bigfoot': (33, 31, 16, 24, 17, 10), 'Ghast': (45, 42, 15, 33, 21, 17), 'Cupid': (49, 44, 19, 37, 24, 23)}
    PAIRS = {('Bigfoot', 13): {'atk': [(19, 38), (21, 42), (22, 44), (24, 48), (25, 51)],
                               'def': [(23, 35), (24, 36), (25, 38)],
                               'int': [(24, 18), (25, 19), (27, 20), (28, 21)],
                               'dex': [(19, 18), (20, 19), (22, 20), (23, 21), (26, 24), (27, 25), (29, 27), (30, 28)],
                               'agi': [(13, 11), (15, 13), (17, 15), (19, 17), (20, 18), (21, 19), (22, 20), (23, 20),
                                       (24, 21), (26, 23), (27, 24)]},
             ('Ghast', 12): {'atk': [(23, 46), (24, 48), (25, 50)], 'agi': [(26, 18)]},
             ('Ghast', 18): {'atk': [(22, 50), (27, 61)], 'int': [(28, 17)], 'dex': [(30, 25)], 'agi': [(27, 22)]},
             ('Cupid', 15): {'int': [(22, 20), (24, 22), (27, 24), (28, 25)],
                             'dex': [(23, 25), (26, 29), (29, 32), (30, 33)], 'agi': [(27, 24)]}}

    @classmethod
    def setUpClass(cls):
        cls.data = game_data()

    def form(self, name, level):
        return next(s for s in self.data.summons if s['name'] == name and s['level'] == level)

    def summon(self, form, stat, best):
        member = Unit('test', PARTY, 1, 1, 0, {s: 1 for s in STATS})
        member.base[stat] = best
        return build_summon(self.data, form, [member], 1)

    def test_a_weak_party_gives_the_lowest_stats(self):
        for name, lowest in self.LOWEST.items():
            form = min((s for s in self.data.summons if s['name'] == name), key=lambda s: s['level'])
            unit = self.summon(form, 'atk', 1)
            with self.subTest(summon=name):
                self.assertEqual(tuple(unit.base[s] for s in STATS), lowest)

    def test_each_stat_is_the_best_of_the_party_times_the_factor_of_the_form(self):
        for (name, level), stats in self.PAIRS.items():
            form = self.form(name, level)
            for stat, pairs in stats.items():
                for best, measured in pairs:
                    with self.subTest(summon=name, level=level, stat=stat, best=best):
                        self.assertEqual(self.summon(form, stat, best).base[stat], measured)


class EncounterSteps(unittest.TestCase):
    """K07, atwiki dt2-2 page 105: steps to each of 50 random battles in the Ruined Shrine Cave (St00_0010), version
    1.03, walking a corridor of five steps; merchants and smiths counted as battles. Without a sealbook, 19.64 steps
    when every battle was fled and 22.96 when every enemy was killed; with the Mangochin sealbook (one piece of
    enchantment 214, encounter rate GrandUP), 15.08 and 22.68. A won battle is followed by the grace of the code;
    a fled one is not (the flag of 0x4bc770 is not set). The model must fall within two standard errors of a mean
    of 50 draws."""
    MEASURED = {(False, ()): 19.64, (True, ()): 22.96, (False, (214,)): 15.08, (True, (214,)): 22.68}

    def test_the_mean_steps_fall_within_the_spread_of_fifty_battles(self):
        zone = next(fl for fl in game_data().floors if fl['floor'] == 'St00_0010')['encounter']
        for (won, pieces), measured in self.MEASURED.items():
            chance = progression.encounter_chance(zone, pieces=pieces) / 100
            model = progression.steps_between_battles(zone, pieces=pieces,
                                                      grace=progression.ENCOUNTER_GRACE if won else 0)
            spread = math.sqrt(1 - chance) / chance / math.sqrt(50)
            with self.subTest(won=won, pieces=pieces):
                self.assertLess(abs(model - measured), 2 * spread)


class GenerousHeart(unittest.TestCase):
    def test_two_maids_reach_the_cap(self):
        """K08, atwiki dt2-2 page 120 and GameFAQs (Class Skill info - Maid): Maid Mastery adds a point per level
        to Generous Heart (12% becomes 22% at its top); with two members who have both, the party recovers 30% of
        max HP and TP after a battle, and no more."""
        data = game_data()
        skill = next(s for s in data.skills.values() if s.name == 'Generous Heart')
        mastery = next(s for s in data.skills.values() if s.name == 'Maid Mastery')
        maid = Unit('maid', PARTY, 1, 1, 0, {s: 1 for s in STATS})
        maid.passives[278] = mastery.effects[0][2][-1]
        top = Action(maid, 'skill', skill, len(skill.effects[0][2]))
        hp, tp = top.value(272), top.value(273)
        self.assertAlmostEqual(hp, 0.22)
        self.assertAlmostEqual(progression.after_battle_fraction([hp, hp]), 0.30)
        self.assertAlmostEqual(progression.after_battle_fraction([tp, tp]), 0.30)
        self.assertLess(progression.after_battle_fraction([hp]), 0.30)
        self.assertEqual(progression.after_battle_recovery(1000, 0.30), 300)
        self.assertEqual(progression.after_battle_recovery(1000, 0.0, full=True), 1000)


if __name__ == '__main__':
    unittest.main()

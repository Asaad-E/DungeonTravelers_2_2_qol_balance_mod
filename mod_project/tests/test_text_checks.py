"""The checker accepts true figures in the approved notation and rejects wrong figures and averages."""
import os
import unittest

import _paths
from pck_handler import PckArchive, SkillHelper
from text_checks import check_skill_text


def entry(category, pck, name):
    for _, b in PckArchive(os.path.join(_paths.BACKUP_DIR, pck)).files:
        if SkillHelper.read_skill(b, category)['name'] == name:
            return b
    raise KeyError(name)


class Checker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.halving = entry('Technique', 'TechniqueSkillData.pck', 'Halving Slice')
        cls.shield = entry('Technique', 'TechniqueSkillData.pck', 'Shield Bash')
        cls.first_aid = entry('Technique', 'TechniqueSkillData.pck', 'First Aid')
        cls.flare = entry('Magic', 'MagicSkillData.pck', 'Crimson Flare')
        cls.concentrate = entry('Passive', 'PassiveSkillData.pck', 'Concentrate')
        cls.third_eye = entry('Unique', 'UniqueSkillData.pck', 'Third Eye Wide')

    def problems(self, category, b, text):
        return check_skill_text(category, b, text)[0]

    def test_true_figures_pass_in_every_approved_notation(self):
        good = [
            ('Technique', self.halving, 'ATK: 80% -> 83 -> 86 -> 89 -> 91 -> 94 -> 97 -> 100 -> 105 -> 110% (L10)'),
            ('Technique', self.halving, 'Instakill: 10% -> 20%'),
            ('Technique', self.halving, 'TP Cost: 38 (+4/Lv) -> 74 | Speed: 0.65x -> 0.75x'),
            ('Technique', self.halving, 'TP Cost: 38 -> 42 -> 46 -> 50 -> 54 -> 58 -> 62 -> 66 -> 70 -> 74'),
            ('Technique', self.shield, 'ATK: 85% -> 90% -> 94% -> 98% -> 102% (L1-5 Max)'),
            ('Technique', self.shield, 'Stun: 30% (+2%/Lv) | TP Cost: 6 -> 8 -> 10 -> 12 -> 14 | Speed: 0.55x'),
            ('Technique', self.first_aid, 'Heal: 12% Max HP -> 15% -> 18% -> 21% -> 25% (L1-5 Max)'),
            ('Magic', self.flare, 'Pwr: 620 -> 760 -> 920 -> 1100 -> 1300 (L1-5 Max) | Accuracy: 82% (+2%/Lv)'),
            ('Passive', self.concentrate, 'Interruption rate: -10% -> -20% -> -30% -> -40% -> -50% (L1-5 Max)'),
            ('Unique', self.third_eye, 'Lv1-9: 7% -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15% | Crown EX: 25%'),
        ]
        for category, b, text in good:
            with self.subTest(text=text):
                self.assertEqual(self.problems(category, b, text), [])

    def test_wrong_figures_are_rejected(self):
        bad = [
            ('Technique', self.halving, 'TP Cost: 15 -> 18 -> 21 -> 24 -> 28'),            # the earlier mod's text
            ('Technique', self.halving, 'ATK: 115% -> 175%'),
            ('Technique', self.halving, 'Instakill: 10% -> 25%'),
            ('Technique', self.halving, 'TP Cost: 38 (+5/Lv) -> 74'),                      # right ends, wrong step
            ('Technique', self.halving, 'ATK: 80% (+3%/Lv) -> 110% (L10 Max)'),            # not a linear table
            ('Technique', self.halving, 'TP Cost: 38 (+4/Lv) -> 74 (L5 Max)'),             # wrong level count
            ('Magic', self.flare, 'Pwr: 620 -> 680 -> 750 -> 830 -> 920 -> 1010 -> 1100 -> 1200 -> 1250 -> 1300'),
            ('Unique', self.third_eye, 'Lv1-9: 7% -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15% | Crown EX: 22.5%'),
        ]
        for category, b, text in bad:
            with self.subTest(text=text):
                self.assertNotEqual(self.problems(category, b, text), [])

    def test_averages_are_rejected_even_when_the_numbers_are_true(self):
        problems = self.problems('Technique', self.halving, 'ATK: 80% -> 110% (avg +3.33%/Lv)')
        self.assertTrue(any('averages are not allowed' in p for p in problems), problems)

    def test_reserved_labels_are_held_to_their_own_table(self):
        # 10 -> 20 is the instakill table (in %), so it must not be accepted as a TP cost.
        self.assertNotEqual(self.problems('Technique', self.halving, 'TP Cost: 10 -> 20'), [])

    def test_free_wording_is_allowed_and_reported(self):
        problems, verified, loose = check_skill_text(
            'Technique', self.halving, 'Row attack | Instakill: 10% -> 20% | Hits 3 times')
        self.assertEqual(problems, [])
        self.assertEqual(verified, 1)
        self.assertEqual(loose, ['Hits 3 times'])


if __name__ == '__main__':
    unittest.main()

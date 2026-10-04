"""The number checker accepts true figures and rejects wrong ones, whatever the wording."""
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
        cls.flare = entry('Magic', 'MagicSkillData.pck', 'Crimson Flare')
        cls.concentrate = entry('Passive', 'PassiveSkillData.pck', 'Concentrate')
        cls.third_eye = entry('Unique', 'UniqueSkillData.pck', 'Third Eye Wide')

    def problems(self, category, b, text):
        return check_skill_text(category, b, text)[0]

    def test_true_figures_pass_in_every_notation(self):
        good = [
            ('Technique', self.halving, 'ATK (L1-10): 80% -> 83 -> 86 -> 89 -> 91 -> 94 -> 97 -> 100 -> 105 -> 110%'),
            ('Technique', self.halving, 'ATK: 80% -> 110% (avg +3.33%/Lv, L1-10) | Instakill: 10% -> 20%'),
            ('Technique', self.halving, 'TP Cost: 38 -> 74 (+4/Lv) | Speed: 0.65x -> 0.75x'),
            ('Technique', self.shield, 'Stun: 30% -> 38% (+2%/Lv) | TP Cost: 6 -> 8 -> 10 -> 12 -> 14 (L1-5) | Speed: 0.55x'),
            ('Magic', self.flare, 'Pwr: 620 -> 760 -> 920 -> 1100 -> 1300 (L1-5) | Accuracy: 82% -> 90% (+2%/Lv)'),
            ('Passive', self.concentrate, 'Interruption rate: -10% -> -50% (-10%/Lv, L1-5)'),
            ('Unique', self.third_eye, 'Lv1-9: 7% -> 15% (+1%/Lv) | Crown EX: 25%'),
        ]
        for category, b, text in good:
            with self.subTest(text=text):
                self.assertEqual(self.problems(category, b, text), [])

    def test_wrong_figures_are_rejected(self):
        bad = [
            ('Technique', self.halving, 'TP Cost: 15 -> 18 -> 21 -> 24 -> 28'),            # the earlier mod's text
            ('Technique', self.halving, 'ATK: 115% -> 175% (+15%/Lv)'),
            ('Technique', self.halving, 'Instakill: 10% -> 25%'),
            ('Technique', self.halving, 'TP Cost: 38 -> 74 (+5/Lv)'),                      # right ends, wrong step
            ('Technique', self.halving, 'ATK: 80% -> 110% (+3.33%/Lv)'),                   # not linear: must say avg
            ('Technique', self.halving, 'TP Cost: 38 -> 74 (+4/Lv, L1-5)'),                # wrong level count
            ('Magic', self.flare, 'Pwr (L1-10): 620 -> 680 -> 750 -> 830 -> 920 -> 1010 -> 1100 -> 1200 -> 1250 -> 1300'),
            ('Unique', self.third_eye, 'Lv1-9: 7% -> 15% (+1%/Lv) | Crown EX: 22.5%'),     # "+50% over Lv 9"
        ]
        for category, b, text in bad:
            with self.subTest(text=text):
                self.assertNotEqual(self.problems(category, b, text), [])

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

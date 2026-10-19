"""
Test suite for player reference guide generation (tools/build_guide.py).
Ensures generated guide markdown files match disk and every sampled numeric figure
matches the exact values in build/engine_snapshot.json.
"""
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import _paths
import build_guide

PROJECT_DIR = _paths.PROJECT_DIR
GUIDE_DIR = os.path.join(PROJECT_DIR, 'docs', 'guide')
SNAPSHOT_PATH = os.path.join(PROJECT_DIR, 'build', 'engine_snapshot.json')

FORBIDDEN_EDITORIAL_WORDS = [
    'note that', "it's worth noting", 'keep in mind', 'in summary',
    'crucially', 'robust', 'seamless', 'comprehensive',
    'dive into', 'unverified'
]


class TestGuideGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(SNAPSHOT_PATH, 'r', encoding='utf-8') as f:
            cls.snapshot = json.load(f)['sides']['vanilla']
        cls.growth_dict = {k: v for k, v in cls.snapshot['growth']}
        cls.built = build_guide.build_guide(side='vanilla', out_dir=GUIDE_DIR)

    def test_files_exist_and_match_disk(self):
        for filename in ['README.md', 'classes.md']:
            filepath = os.path.join(GUIDE_DIR, filename)
            self.assertTrue(os.path.exists(filepath), f"{filename} missing from {GUIDE_DIR}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content_on_disk = f.read()
            self.assertEqual(content_on_disk, self.built[filename], f"{filename} content on disk does not match generator output")
            self.assertGreater(len(content_on_disk), 100, f"{filename} is unexpectedly small")

    def test_no_forbidden_editorial_phrases_or_machine_paths(self):
        for filename, content in self.built.items():
            lower_content = content.lower()
            for word in FORBIDDEN_EDITORIAL_WORDS:
                self.assertNotIn(word, lower_content, f"Forbidden editorial phrase '{word}' found in {filename}")
            self.assertNotIn('c:\\users', lower_content, f"Machine path found in {filename}")
            self.assertNotIn('c:/users', lower_content, f"Machine path found in {filename}")
            # Ensure no raw memory addresses in the player guide
            self.assertNotIn('0x', content, f"Hexadecimal memory address found in {filename}")

    def test_sample_growth_figures_match_snapshot(self):
        classes_md = self.built['classes.md']
        growth = self.growth_dict

        # Fighter (row 0)
        f_lv1 = growth[0][0]
        f_lv1_row = f"| 1 | {f_lv1[6]} | {f_lv1[7]} | {f_lv1[0]} | {f_lv1[1]} | {f_lv1[2]} | {f_lv1[3]} | {f_lv1[4]} | {f_lv1[5]} |"
        self.assertIn(f_lv1_row, classes_md, "Fighter Lv1 stat row mismatch")

        f_lv99 = growth[0][98]
        f_lv99_row = f"| 99 | {f_lv99[6]} | {f_lv99[7]} | {f_lv99[0]} | {f_lv99[1]} | {f_lv99[2]} | {f_lv99[3]} | {f_lv99[4]} | {f_lv99[5]} |"
        self.assertIn(f_lv99_row, classes_md, "Fighter Lv99 stat row mismatch")

        # Paladin (row 1)
        pal_lv99 = growth[1][98]
        pal_lv99_row = f"| 99 | {pal_lv99[6]} | {pal_lv99[7]} | {pal_lv99[0]} | {pal_lv99[1]} | {pal_lv99[2]} | {pal_lv99[3]} | {pal_lv99[4]} | {pal_lv99[5]} |"
        self.assertIn(pal_lv99_row, classes_md, "Paladin Lv99 stat row mismatch")

        # Samurai from Paladin (row 4)
        sam_pal_lv99 = growth[4][98]
        sam_pal_row = f"| 99 | {sam_pal_lv99[6]} | {sam_pal_lv99[7]} | {sam_pal_lv99[0]} | {sam_pal_lv99[1]} | {sam_pal_lv99[2]} | {sam_pal_lv99[3]} | {sam_pal_lv99[4]} | {sam_pal_lv99[5]} |"
        self.assertIn(sam_pal_row, classes_md, "Samurai (from Paladin) Lv99 stat row mismatch")

        # Samurai from Berserker (row 5)
        sam_ber_lv99 = growth[5][98]
        sam_ber_row = f"| 99 | {sam_ber_lv99[6]} | {sam_ber_lv99[7]} | {sam_ber_lv99[0]} | {sam_ber_lv99[1]} | {sam_ber_lv99[2]} | {sam_ber_lv99[3]} | {sam_ber_lv99[4]} | {sam_ber_lv99[5]} |"
        self.assertIn(sam_ber_row, classes_md, "Samurai (from Berserker) Lv99 stat row mismatch")

        # Joker (row 37)
        jok_lv99 = growth[37][98]
        jok_row = f"| 99 | {jok_lv99[6]} | {jok_lv99[7]} | {jok_lv99[0]} | {jok_lv99[1]} | {jok_lv99[2]} | {jok_lv99[3]} | {jok_lv99[4]} | {jok_lv99[5]} |"
        self.assertIn(jok_row, classes_md, "Joker Lv99 stat row mismatch")

    def test_sample_skills_and_costs(self):
        classes_md = self.built['classes.md']
        # Provoke: Technique, Max Lv 5, Total SP 30 SP, Single enemy, None, with Enmity
        self.assertIn('| Provoke | Technique | 5 | 30 SP | Single enemy | None |', classes_md)
        self.assertIn('Enmity: 250', classes_md)
        # War Cry: ATK scaling
        self.assertIn('| War Cry | Technique | 5 | 30 SP | All allies | None |', classes_md)
        self.assertIn('+8% -> +10% -> +12% -> +15% -> +18%', classes_md)
        # Raging Smash: Technique, Max Lv 10, Total SP 55 SP, Single enemy, Short
        self.assertIn('| Raging Smash | Technique | 10 | 55 SP | Single enemy | Short |', classes_md)
        self.assertIn('125% -> 134', classes_md)
        # Absolute Attack: Valkyrie, Passive, Max Lv 1, Total SP 20 SP
        self.assertIn('| Absolute Attack | Passive | 1 | 20 SP | - | - | No longer suffer counterattacks from enemies. |', classes_md)

    def test_sample_weapon_modifiers(self):
        classes_md = self.built['classes.md']
        # Fighter: Sword +1%
        self.assertIn('| Weapon | Sword | +1% |', classes_md)
        # Paladin: Sword +2%, Polearm +3%, Shield +2%
        self.assertIn('| Weapon | Polearm | +3% |', classes_md)
        self.assertIn('| Shield | Shield | +2% |', classes_md)
        # Samurai route modifiers
        self.assertIn('| From Paladin | Shield | Shield | +2% |', classes_md)
        self.assertIn('| From Berserker | Weapon | Axe | +2% |', classes_md)


if __name__ == '__main__':
    unittest.main()

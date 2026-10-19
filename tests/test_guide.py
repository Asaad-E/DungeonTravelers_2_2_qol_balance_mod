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
        all_files = [
            'README.md', 'classes.md', 'formulas.md', 'skills.md', 'characters.md',
            'enchantments.md', 'equipment.md', 'enemies.md', 'bosses.md', 'summons.md',
            'mercenaries.md', 'progression.md'
        ]
        for filename in all_files:
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
            self.assertIsNone(re.search(r'\b0x[0-9a-fA-F]+\b', content), f"Hexadecimal memory address found in {filename}")

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

    def test_sample_formulas(self):
        formulas_md = self.built['formulas.md']
        self.assertIn('Base Hit     = 0.885 * (100 + Attacker DEX) / (100 + Target AGI) + Skill Accuracy', formulas_md)
        self.assertIn('Attack A = Base ATK * (2 + Swing)', formulas_md)
        self.assertIn('Defence A = Target DEF * 1.35 * (1 + Sum of Modifiers)', formulas_md)
        self.assertIn('Base Damage    = (Attack B * Damage Multiplier) - Defence A', formulas_md)
        self.assertIn('Base Rate  = (Attacker DEX * 0.2) / (Attacker DEX + Target AGI) * 100', formulas_md)
        self.assertIn('Base Speed   = (AGI + 100) / 200', formulas_md)
        self.assertIn('Damage Rate  = Damage Taken / (Target Max HP * 1.5)', formulas_md)
        self.assertIn('Total at Lv 99   = 685 SP cumulative', formulas_md)
        self.assertIn('Bonus Cap      = +50 to all eight base attributes (10 resets at Lv 99)', formulas_md)

    def test_sample_skills_full(self):
        skills_md = self.built['skills.md']
        self.assertIn('### Provoke', skills_md)
        self.assertIn('- **Type:** Technique | **Classes:** Fighter, Mistress', skills_md)
        self.assertIn('### Raging Smash', skills_md)
        self.assertIn('- **Required Weapon:** Short-range weapon', skills_md)
        self.assertIn('### Fireball', skills_md)
        self.assertIn('- **Type:** Magic | **Classes:** Magic User', skills_md)
        self.assertIn('### Absolute Attack', skills_md)
        self.assertIn('- **Type:** Passive | **Classes:** Valkyrie', skills_md)

    def test_sample_characters(self):
        chars_md = self.built['characters.md']
        self.assertIn('### Siena', chars_md)
        self.assertIn('- **Base Class:** Magic User', chars_md)
        self.assertIn('- **Starting Lv:** 1 (0 EXP)', chars_md)
        self.assertIn('#### Unique Skill: Arcane Shield', chars_md)
        self.assertIn('50% | 55% | 60% | 65% | 70% | 75% | 80% | 90% | 100% | 200%', chars_md)
        self.assertIn('### Alisia', chars_md)
        self.assertIn('- **Base Class:** Fighter', chars_md)
        self.assertIn('- **Starting Lv:** 41 (179,196 EXP)', chars_md)
        self.assertIn('Defeat Heartless Avenger (St10_0010, Battle 43)', chars_md)

    def test_sample_enchantments(self):
        ench_md = self.built['enchantments.md']
        self.assertIn('| 29 | Physical attack UP | +4 | Stacks per piece | +50 |', ench_md)
        self.assertIn('| 51 | Speed UP | +10% | Stacks per piece | +50% (+0.50) |', ench_md)
        self.assertIn('| 66 | Received physical damage DOWN | -10% | Stacks per piece | 25% damage cut |', ench_md)
        self.assertIn('| 78 | Fire magic buff | +20% | Single piece (switch) | +40% (+0.40) |', ench_md)
        self.assertIn('| 275 | Double EXP | 2.0x multiplier | Single piece (switch) | Single piece |', ench_md)

    def test_sample_equipment(self):
        eq_md = self.built['equipment.md']
        self.assertIn('| A+ | 1.00x |', eq_md)
        self.assertIn('| F | 2.90x |', eq_md)
        self.assertIn('| Shortsword | B (1.6x) | 20 | 0 | 0 | 0 | 0 | 0 | +1.25 | Short | No | - |', eq_md)
        self.assertIn('| Claymore | E+ (2.45x) | 37 | 0 | 0 | 0 | 0 | 0 | +2.78 | Short | Yes | - |', eq_md)
        self.assertIn('| Buckler | 3 | 0 | 0 | 0 | 0 | 0 | +1 | - |', eq_md)
        self.assertIn('| Ring | 1 | 0 | 0 | 0 | 0 | 0 | +0.5 | - |', eq_md)

    def test_sample_enemies(self):
        enemies_md = self.built['enemies.md']
        self.assertIn('### Medic (Lv 11)', enemies_md)
        self.assertIn('| 177 | 41 | 28 | 24 | 28 | 16 | 15 | 90 | 16 |', enemies_md)
        self.assertIn('Suspicious Supplement', enemies_md)
        self.assertIn('Gravity Shot', enemies_md)

    def test_sample_bosses(self):
        bosses_md = self.built['bosses.md']
        self.assertIn('### Battle 42: Wanton Witch', bosses_md)
        self.assertIn('GumGumGoo', bosses_md)
        self.assertIn('Melt Away', bosses_md)
        self.assertIn('Wait and See', bosses_md)

    def test_sample_summons(self):
        summons_md = self.built['summons.md']
        self.assertIn('## Bigfoot (Family 833)', summons_md)
        self.assertIn('| Form 1 | 7 | 9 | 1.54x | 1.24x | 0.61x | 0.91x | 0.86x | 0.81x | - |', summons_md)
        self.assertIn('### Bigfoot - Form 1 (Lv 7)', summons_md)
        self.assertIn('### Bigfoot - Form 2 (Lv 13)', summons_md)
        self.assertIn('### Bigfoot - Form 3 (Lv 21)', summons_md)

    def test_sample_mercenaries(self):
        merc_md = self.built['mercenaries.md']
        self.assertIn('## Michelle (Character 411)', merc_md)
        self.assertIn('## Euphemia (Character 310)', merc_md)
        self.assertIn('| 1 | 26 | 400 Gold | 25 battles | 91 | 58 | 18 | 21 | 44 | 35 | 135 |', merc_md)

    def test_sample_progression(self):
        prog_md = self.built['progression.md']
        self.assertIn('| 99 | 100,442 | 3,042,158 | +18 | 685 |', prog_md)
        self.assertIn('| Level 99 | +10 | Level 1 | +50 stats max |', prog_md)
        self.assertIn('| St00_0010 | Ruined Shrine Cave |', prog_md)
        self.assertIn('B41: Slapyon (Lv 2); B42: Wanton Witch (Lv 5); B43: Aradia (Lv 60)', prog_md)


if __name__ == '__main__':
    unittest.main()



"""Line 1 of a skill (the battle bar): damage word and ailment chance. Exact ailment chances of enemy attacks."""
import os
import copy
import struct
import tempfile
import unittest

import _paths
import build_variant as bv
import magnitude_words as mw
from pck_handler import PckArchive, SkillHelper, EnemyAttackHelper
from text_checks import skill_tables, check_enemy_attack_text, enemy_ailments, enemy_ailment_tokens

SKILL_TABLE = os.path.join(_paths.TABLES_DIR, 'qol_skill_text.xlsx')
ENEMY_TABLE = os.path.join(_paths.TABLES_DIR, 'qol_enemy_attack_text.xlsx')
POISON_SHOT = 'EnemyAttackData_0385.bin'        # the Cupid ability the user saw without its chance


def skills():
    found = {}
    for category, pck in (('Technique', 'TechniqueSkillData.pck'), ('Magic', 'MagicSkillData.pck')):
        for fn, b in PckArchive(os.path.join(_paths.BACKUP_DIR, pck)).files:
            info = SkillHelper.read_skill(b, category)
            found.setdefault(info['name'], (category, fn, b, info['desc']))
    return found


class Scales(unittest.TestCase):
    def test_boundaries(self):
        phys = lambda v: mw.tier(v, mw.PHYS_BOUNDS, mw.DAMAGE_WORDS, mw.OUT_OF_SCALE)
        magic = lambda v: mw.tier(v, mw.MAGIC_BOUNDS, mw.DAMAGE_WORDS, mw.OUT_OF_SCALE)
        # The user's rule: negligible only below 80%.
        self.assertEqual([phys(v) for v in (79, 80, 100, 124, 125, 149, 150, 174, 175, 224, 225)],
                         ['negligible', 'minor', 'minor', 'minor', 'moderate', 'moderate', 'major', 'major', 'severe',
                          'severe', 'tremendous'])
        self.assertEqual([magic(v) for v in (79, 80, 250, 400, 500, 699, 700, 1300)],
                         ['negligible', 'minor', 'moderate', 'major', 'severe', 'severe', 'tremendous', 'tremendous'])

    def test_chance_is_the_shortest_true_figure(self):
        chance = lambda values: mw.chance_text([(118, 4, values)], [118])
        self.assertEqual(chance([0.25] * 10), '25%')                     # never changes: the value itself
        self.assertEqual(chance([0.30, 0.32, 0.34, 0.36, 0.38]), '30%+')  # rises by 10 points or less
        self.assertEqual(chance([0.30, 0.40]), '30%+')
        self.assertEqual(chance([0.20, 0.35, 0.50]), '20-50%')            # rises by more: first - last
        self.assertIsNone(chance([10.0]))                                 # always happens: nothing to say
        self.assertIsNone(mw.chance_text([(117, 4, [0.25, 0.37]), (115, 4, [0.20, 0.32])], [117, 115]))


class Line1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills = skills()

    def key(self, name):
        return self.skills[name][:2]

    def propose(self, name):
        category, _, b, desc = self.skills[name]
        return mw.propose(desc, skill_tables(category, b)['slots'], 85)[0]

    def test_words_come_from_the_average_of_the_real_values(self):
        expected = {
            'Fireball': 'Deal moderate fire damage to one enemy.',                       # Pwr 70-520, average 265
            'Inferno': 'Deal severe fire damage to all enemies.',                        # average 523
            'Soul Absorb': 'Deal negligible non-elemental damage to one enemy to regain TP.',    # Pwr 22-82, average 55
            'Shield Bash': 'Shield skill. Deal minor bash damage to one enemy. May stun (30%+).',   # 94%, stun 30-38%
            'Ninja Piledriver': 'Deal major bash damage to one enemy. May stun (10%+).',             # 152%, stun 10-20%
            'Poison Shot': 'Bow/gun skill. Deal moderate damage to one enemy. May poison (20-50%).',
            'Raging Smash': 'Short-range skill. Major strike to one enemy.',             # the game said "Powerful"
            'Panic Voice': 'Deal major non-elemental damage to all enemies. May stun (25%).',    # 25% at every level
            'Stun': 'Stun one enemy (65%+).',                                            # 65-75%
            'Slow': 'Slow an enemy row (50-68%).',
        }
        for name, text in expected.items():
            with self.subTest(skill=name):
                self.assertEqual(self.propose(name), text)

    def test_out_of_scale_keeps_the_games_own_word(self):
        # Pwr 620-1300, average 940: beyond the scale. The game already calls it tremendous.
        self.assertEqual(self.propose('Crimson Flare'), 'Deal tremendous fire damage to one enemy.')
        category, _, b, desc = self.skills['Crimson Flare']
        self.assertEqual(mw.check_line1(desc, desc, skill_tables(category, b)['slots']), ([], 1))

    def test_skill_with_an_effect_that_is_not_understood_is_left_as_written(self):
        # Spiral Arrow: ATK 88% but also effect 73 (3.3 -> 4.0). Its real strength is not known.
        for name in ('Spiral Arrow', 'Holy Gavel', 'Fire Scroll'):
            with self.subTest(skill=name):
                self.assertEqual(self.propose(name), self.skills[name][3])
        # Soul Eater keeps the game's "enormous" (effect 87 is not understood) and gains only its fixed chance.
        self.assertEqual(self.propose('Soul Eater'),
                         'Deal enormous damage to one enemy that possesses life. Low chance of instakill (12%).')

    def test_checker_rejects_a_word_the_binary_does_not_give(self):
        category, _, b, desc = self.skills['Fireball']
        slots = skill_tables(category, b)['slots']
        self.assertEqual(mw.check_line1('Deal moderate fire damage to one enemy.', desc, slots), ([], 1))
        self.assertNotEqual(mw.check_line1('Deal severe fire damage to one enemy.', desc, slots)[0], [])
        category, _, b, desc = self.skills['Shield Bash']
        slots = skill_tables(category, b)['slots']
        self.assertEqual(mw.check_line1(desc.replace('May stun.', 'May stun (30%+).'), desc, slots), ([], 1))
        for wrong in ('(30%)', '(34%)', '(30-38%)', '(40%+)'):
            self.assertNotEqual(mw.check_line1(desc.replace('May stun.', f'May stun {wrong}.'), desc, slots)[0], [], wrong)
        category, _, b, desc = self.skills['Spiral Arrow']        # no grade exists for it
        self.assertNotEqual(mw.check_line1(desc.replace('powerful', 'minor'), desc, skill_tables(category, b)['slots'])[0], [])

    def test_table_line1_has_no_new_figures_and_fits(self):
        table = bv.load_skill_text(SKILL_TABLE)
        changed = 0
        for (category, fn), row in table.items():
            if category not in ('Technique', 'Magic') or row['desc'] == row['vanilla_desc']:
                continue
            changed += 1
            with self.subTest(entry=fn):
                self.assertLessEqual(len(row['desc']), bv.MAX_LINE)
                self.assertNotIn('\n', row['desc'])
                self.assertNotIn('~', row['desc'])           # no glyph in the game font
                self.assertEqual(sorted(c for c in mw.strip_chances(row['desc']) if c.isdigit()),
                                 sorted(c for c in row['vanilla_desc'] if c.isdigit()))
        self.assertGreater(changed, 50)

    def test_wrong_word_in_the_table_stops_the_build(self):
        table = copy.deepcopy(bv.load_skill_text(SKILL_TABLE))
        table[self.key('Fireball')]['desc'] = 'Deal severe fire damage to one enemy.'
        problems = []
        with tempfile.TemporaryDirectory() as out:
            bv.build_skills(out, table, problems)
            bv.verify_skills(out, table, bv.VARIANTS['qol'], problems)
        self.assertTrue(any('says severe damage' in p for p in problems), problems)

    def test_figure_in_line1_stops_the_build(self):
        table = copy.deepcopy(bv.load_skill_text(SKILL_TABLE))
        table[self.key('Fireball')]['desc'] = 'Deal moderate fire damage to one enemy. | Pwr: 70 -> 520'   # the earlier mod's habit
        problems = []
        with tempfile.TemporaryDirectory() as out:
            bv.build_skills(out, table, problems)
            bv.verify_skills(out, table, bv.VARIANTS['qol'], problems)
        self.assertTrue(any('carries a figure' in p for p in problems), problems)


class EnemyAttacks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = bv.load_enemy_attack_text(ENEMY_TABLE)
        cls.entries = dict(PckArchive(os.path.join(_paths.BACKUP_DIR, bv.ENEMY_PCK)).files)

    def test_writer_reproduces_the_originals(self):
        for fn, b in self.entries.items():
            with self.subTest(entry=fn):
                self.assertEqual(EnemyAttackHelper.write_enemy_attack(b, EnemyAttackHelper.read_enemy_attack(b)['desc']),
                                 bytes(b))

    def test_exact_chance_goes_on_the_data_line_and_the_prose_stays(self):
        row = self.table[POISON_SHOT]
        self.assertEqual(enemy_ailments(self.entries[POISON_SHOT]), {'Poison': 30.0})
        self.assertEqual(row['desc'], 'Target: Single / Type: Stab / Range: Long / Poison: 30%\n'
                                      'Fire an arrow doused in some real toxic stuff.\n'
                                      'If it hits, it may inflict poison. Also, ouch.')
        self.assertEqual(row['desc'].split('\n')[1:], row['vanilla_desc'].split('\n')[1:])

    def test_equal_chances_share_one_item(self):
        self.assertEqual(enemy_ailment_tokens(self.entries['EnemyAttackData_0614.bin']), ['Freeze/Silence: 20%'])
        self.assertEqual(enemy_ailment_tokens(self.entries['EnemyAttackData_0943.bin']), ['Poison: 60%', 'Silence: 50%'])

    def test_prose_is_never_changed_in_the_table(self):
        self.assertEqual(set(self.table), set(self.entries))
        changed = 0
        for fn, row in self.table.items():
            changed += row['desc'] != row['vanilla_desc']
            with self.subTest(entry=fn):
                self.assertEqual(row['desc'].split('\n')[1:], row['vanilla_desc'].split('\n')[1:])
                self.assertEqual(check_enemy_attack_text(self.entries[fn], row['desc'], row['vanilla_desc'])[0], [])
        self.assertGreater(changed, 800)

    def build(self, mutate_table=None, mutate_built=None):
        table = copy.deepcopy(self.table)
        if mutate_table:
            mutate_table(table)
        problems = []
        with tempfile.TemporaryDirectory() as out:
            bv.build_enemy_attacks(out, table, problems)
            if mutate_built:
                mutate_built(out)
            if not problems:
                bv.verify_enemy_attacks(out, table, bv.VARIANTS['qol'], problems)
        return problems

    def test_clean_build_has_no_problems(self):
        self.assertEqual(self.build(), [])

    def test_wrong_chance_stops_the_build(self):
        def wrong(table):
            table[POISON_SHOT]['desc'] = table[POISON_SHOT]['desc'].replace('Poison: 30%', 'Poison: 40%')
        self.assertTrue(any('does not match the binary' in p for p in self.build(mutate_table=wrong)))

    def test_edited_joke_stops_the_build(self):
        def no_joke(table):
            table[POISON_SHOT]['desc'] = table[POISON_SHOT]['desc'].replace(' Also, ouch.', '')
        self.assertTrue(any('prose differs' in p for p in self.build(mutate_table=no_joke)))

    def test_changed_chance_in_the_binary_is_detected(self):
        def change(out):
            path = os.path.join(out, bv.ENEMY_PCK)
            archive = PckArchive(path)
            for i, (fn, b) in enumerate(archive.files):
                if fn == POISON_SHOT:
                    patched = bytearray(b)
                    struct.pack_into('<f', patched, 0x4C + 12 + 4, 0.5)
                    archive.files[i] = (fn, bytes(patched))
            archive.save(path)
        problems = self.build(mutate_built=change)
        self.assertTrue(any('numeric data differs' in p for p in problems), problems)


if __name__ == '__main__':
    unittest.main()

"""QoL item text (exact amount in place of a vague size) and the install step into the game folder."""
import os
import copy
import struct
import tempfile
import unittest

import _paths
import build_variant as bv
import install_variant
from pck_handler import PckArchive, ItemHelper
from text_checks import check_item_text, item_pairs

TABLE_PATH = os.path.join(_paths.TABLES_DIR, 'qol_item_text.xlsx')
DANISH = 'ItemData_0001.bin'


class ItemText(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = bv.load_item_text(TABLE_PATH)
        cls.entries = dict(PckArchive(os.path.join(_paths.BACKUP_DIR, bv.ITEM_PCK)).files)

    def test_one_row_per_item_with_the_backup_text(self):
        self.assertEqual(set(self.table), set(self.entries))
        for fn, b in self.entries.items():
            with self.subTest(entry=fn):
                self.assertEqual(self.table[fn]['vanilla_desc'], ItemHelper.read_item(b)['desc'])

    def test_exact_amount_replaces_the_vague_size(self):
        self.assertEqual(self.table[DANISH]['vanilla_desc'], "Restore an ally's HP (medium).")
        self.assertEqual(self.table[DANISH]['desc'], "Restore an ally's HP (+250).")
        self.assertEqual(item_pairs(self.entries[DANISH])[0], (0, 250.0))

    def test_original_sentence_plus_data(self):
        """The user's rule for items: the game's sentence stays and what the item does is added."""
        by_name = {ItemHelper.read_item(b)['name']: self.table[fn] for fn, b in self.entries.items()}
        expected = {
            'Rice Cracker': 'Old-fashioned rice cracker covered in soy sauce. (HP +75)',
            'Egg Sandwich': 'Sandwich filled with soft, fluffy eggs. (HP/TP +10, cures 1 ailment)',
            'Magical Skill Garnish': 'Eat, Skill, Love. (SP +3)',
            # the sentence already says what it does: nothing to add
            'Fumirul Nectar': 'Cure all status ailments for an ally. Sweet to the taste.',
        }
        for name, text in expected.items():
            with self.subTest(item=name):
                self.assertEqual(by_name[name]['desc'], text)
                self.assertTrue(by_name[name]['desc'].startswith(by_name[name]['vanilla_desc']))

    def test_one_line_always_and_shortened_originals_only_where_needed(self):
        from shortened_text import ITEM_SENTENCES
        by_name = {ItemHelper.read_item(b)['name']: self.table[fn] for fn, b in self.entries.items()}
        self.assertEqual(by_name['Killer Curry']['desc'],
                         'Legendary. Eat it and fall in love. (HP/TP +1000, cures all ailments)')
        self.assertEqual(by_name['Rosary of Darkness']['desc'].rsplit(' (', 1)[1], '25% stun)')    # decoded with the JP wiki
        for name, sentence in ITEM_SENTENCES.items():
            row = by_name[name]
            with self.subTest(item=name):
                self.assertTrue(row['desc'].startswith(sentence + ' ('))
                self.assertLess(len(sentence), len(row['vanilla_desc']))
        for fn, row in self.table.items():
            with self.subTest(entry=fn):
                self.assertLessEqual(len(row['desc']), bv.BATTLE_LINE if row['desc'] != row['vanilla_desc'] else 85)
                self.assertEqual(len(row["desc"].splitlines()), 1)

    def test_item_data_is_checked_and_the_sentence_cannot_change(self):
        egg = next(b for b in self.entries.values() if ItemHelper.read_item(b)['name'] == 'Egg Sandwich')
        vanilla = 'Sandwich filled with soft, fluffy eggs.'
        self.assertEqual(check_item_text(egg, vanilla + ' (HP/TP +10, cures 1 ailment)', vanilla), ([], 2))
        self.assertEqual(check_item_text(egg, vanilla + ' (HP/TP +10)', vanilla), ([], 1))
        self.assertNotEqual(check_item_text(egg, vanilla + ' (HP/TP +20, cures 1 ailment)', vanilla)[0], [])
        self.assertNotEqual(check_item_text(egg, vanilla + ' (cures all ailments)', vanilla)[0], [])
        self.assertNotEqual(check_item_text(egg, 'A sandwich. (HP/TP +10)', vanilla)[0], [])

    def test_no_text_states_a_size_word_and_an_amount(self):
        for fn, row in self.table.items():
            with self.subTest(entry=fn):
                self.assertFalse('(+' in row['desc'] and any(w in row['desc'] for w in ('(small)', '(medium)', '(large)')))
                self.assertNotIn('\n', row['desc'])
                self.assertLessEqual(len(row['desc']), bv.MAX_LINE)

    def test_checker_rejects_a_wrong_amount_or_kind(self):
        b = self.entries[DANISH]
        self.assertEqual(check_item_text(b, "Restore an ally's HP (+250)."), ([], 1))
        self.assertNotEqual(check_item_text(b, "Restore an ally's HP (+300).")[0], [])
        self.assertNotEqual(check_item_text(b, "Restore an ally's TP (+250).")[0], [])
        self.assertNotEqual(check_item_text(b, "Restore HP (+250 HP).")[0], [])


class ItemBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = bv.load_item_text(TABLE_PATH)
        cls.variant = bv.VARIANTS['qol']

    def build(self, mutate_table=None, mutate_built=None):
        table = copy.deepcopy(self.table)
        if mutate_table:
            mutate_table(table)
        problems = []
        with tempfile.TemporaryDirectory() as out:
            bv.build_items(out, table, problems)
            if mutate_built:
                mutate_built(out)
            if not problems:
                bv.verify_items(out, table, self.variant, problems)
        return problems

    def test_clean_build_has_no_problems(self):
        self.assertEqual(self.build(), [])

    def test_wrong_amount_stops_the_build(self):
        def wrong(table):
            table[DANISH]['desc'] = "Restore an ally's HP (+300)."
        self.assertNotEqual(self.build(mutate_table=wrong), [])

    def test_size_word_next_to_the_amount_stops_the_build(self):
        def both(table):
            table[DANISH]['desc'] = "Restore an ally's HP (medium) (+250)."     # the earlier mod's text
        problems = self.build(mutate_table=both)
        self.assertTrue(any('both a vague size and an exact amount' in p for p in problems), problems)

    def test_changed_item_value_is_detected(self):
        def change(out):
            path = os.path.join(out, bv.ITEM_PCK)
            archive = PckArchive(path)
            for i, (fn, b) in enumerate(archive.files):
                if fn == DANISH:
                    patched = bytearray(b)
                    struct.pack_into('<f', patched, 0x28, 300.0)
                    archive.files[i] = (fn, bytes(patched))
            archive.save(path)
        problems = self.build(mutate_built=change)
        self.assertTrue(any('numeric data differs' in p for p in problems), problems)


class Install(unittest.TestCase):
    """The install leaves the game with the variant and nothing else, and keeps what it replaces."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        self.game, self.backups, self.build = (os.path.join(root, d) for d in ('game', 'backups', 'build'))
        self.built = os.path.join(self.build, 'qol', install_variant.BUILT_SUBDIR)
        for d in (os.path.join(self.game, 'Parameter'), os.path.join(self.game, 'Script'), self.backups, self.built):
            os.makedirs(d)
        self.write(self.backups, 'ItemData.pck', b'original items')
        self.write(self.backups, 'TrapData.pck', b'original traps')
        self.write(self.backups, 'Teaching.pck', b'original script')
        self.write(self.backups, 'QuestData.pck', b'original quests')
        self.write(self.built, 'ItemData.pck', b'qol items')
        self.write(os.path.join(self.game, 'Parameter'), 'ItemData.pck', b'earlier build items')
        self.write(os.path.join(self.game, 'Parameter'), 'TrapData.pck', b'earlier build traps')
        self.write(os.path.join(self.game, 'Parameter'), 'QuestData.pck', b'original quests')
        self.write(os.path.join(self.game, 'Script'), 'Teaching.pck', b'earlier build script')
        self.write(os.path.join(self.game, 'Parameter'), 'NotBackedUp.pck', b'left alone')

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def write(folder, name, data):
        with open(os.path.join(folder, name), 'wb') as f:
            f.write(data)

    def game_file(self, sub, name):
        return install_variant.read(os.path.join(self.game, sub, name))

    def install(self, stamp):
        return install_variant.install('qol', self.game, self.backups, self.build, stamp)

    def test_game_ends_up_as_the_variant_and_nothing_else(self):
        changes, kept, problems, saved = self.install('first')
        self.assertEqual(problems, [])
        self.assertEqual(self.game_file('Parameter', 'ItemData.pck'), b'qol items')          # built by the variant
        self.assertEqual(self.game_file('Parameter', 'TrapData.pck'), b'original traps')     # not built: original
        self.assertEqual(self.game_file('Script', 'Teaching.pck'), b'original script')
        self.assertEqual(self.game_file('Parameter', 'NotBackedUp.pck'), b'left alone')
        self.assertEqual(sorted(changes), [('Parameter/ItemData.pck', 'qol build'), ('Parameter/TrapData.pck', 'original'),
                                           ('Script/Teaching.pck', 'original')])
        self.assertEqual(kept, 1)

    def test_replaced_files_are_saved_first(self):
        _, _, _, saved = self.install('first')
        self.assertEqual(install_variant.read(os.path.join(saved, 'Parameter', 'ItemData.pck')), b'earlier build items')
        self.assertEqual(install_variant.read(os.path.join(saved, 'Script', 'Teaching.pck')), b'earlier build script')
        self.assertFalse(os.path.exists(os.path.join(saved, 'Parameter', 'QuestData.pck')))

    def test_second_install_changes_nothing(self):
        self.install('first')
        changes, kept, problems, saved = self.install('second')
        self.assertEqual((changes, kept, problems), ([], 4, []))
        self.assertFalse(os.path.exists(saved))

    def test_script_backups_go_to_the_script_folder_even_when_the_name_exists_in_parameter(self):
        os.makedirs(os.path.join(self.backups, 'Script'))
        self.write(os.path.join(self.backups, 'Script'), 'SEV.pck', b'original event script')
        self.write(self.backups, 'SEV.pck', b'original sound table')
        self.write(os.path.join(self.game, 'Script'), 'SEV.pck', b'modded event script')
        self.write(os.path.join(self.game, 'Parameter'), 'SEV.pck', b'modded sound table')
        changes, _, problems, saved = self.install('first')
        self.assertEqual(problems, [])
        self.assertEqual(self.game_file('Script', 'SEV.pck'), b'original event script')
        self.assertEqual(self.game_file('Parameter', 'SEV.pck'), b'original sound table')
        self.assertEqual(install_variant.read(os.path.join(saved, 'Script', 'SEV.pck')), b'modded event script')

    def test_verify_reports_a_file_that_is_not_the_variant(self):
        self.install('first')
        self.write(os.path.join(self.game, 'Parameter'), 'TrapData.pck', b'something else')
        self.assertEqual(len(install_variant.verify('qol', self.game, self.backups, self.build)), 1)


if __name__ == '__main__':
    unittest.main()


class Meals(unittest.TestCase):
    """Ice cream and ramen: the flavour line stays, the vague amount becomes the stored one."""

    @classmethod
    def setUpClass(cls):
        from pck_handler import FoodMenuHelper
        cls.helper = FoodMenuHelper
        cls.entries = PckArchive(os.path.join(_paths.BACKUP_DIR, bv.FOOD_PCK)).files
        cls.table = bv.load_food_text(os.path.join(_paths.TABLES_DIR, 'qol_food_text.xlsx'))

    def test_writer_reproduces_the_originals(self):
        for fn, b in self.entries:
            with self.subTest(entry=fn):
                self.assertEqual(self.helper.write_food_menu(b, self.helper.read_food_menu(b)['effect']), bytes(b))

    def test_exact_amounts(self):
        from text_checks import food_amounts, check_food_text
        by_name = {self.helper.read_food_menu(b)['name']: (b, self.table[fn]) for fn, b in self.entries}
        b, row = by_name['Banango Ice Cream']
        self.assertEqual(food_amounts(b), (30, 20))
        self.assertEqual(row['effect'], 'Heal 30% HP and 20% TP.')
        self.assertEqual(by_name['Raspberry Supreme'][1]['effect'], 'Heal status ailments + 80% HP and TP + gain Aim.')
        self.assertEqual(by_name['Miracle Shake'][1]['effect'], 'Heal all TP + gain Divine Shield.')      # already exact
        self.assertNotEqual(check_food_text(b, 'Heal 40% HP and 20% TP.', row['vanilla'])[0], [])
        self.assertNotEqual(check_food_text(b, 'Restores 30% HP and 20% TP.', row['vanilla'])[0], [])

    def test_clean_build_and_a_wrong_amount(self):
        import copy
        import tempfile
        for mutate, clean in ((False, True), (True, False)):
            table, problems = copy.deepcopy(self.table), []
            if mutate:
                fn = next(f for f, r in table.items() if r['effect'] == 'Heal 20% HP.')
                table[fn]['effect'] = 'Heal 25% HP.'
            with tempfile.TemporaryDirectory() as out:
                bv.build_food(out, table, problems)
                bv.verify_food(out, table, bv.VARIANTS['qol'], problems)
            self.assertEqual(problems == [], clean, problems)


class PartySkills(unittest.TestCase):
    """Party skills: the members stay, the effect line gains the bound of each bonus (from the rules workbook)."""

    @classmethod
    def setUpClass(cls):
        from pck_handler import PartySkillHelper
        cls.helper = PartySkillHelper
        cls.entries = PckArchive(os.path.join(_paths.BACKUP_DIR, bv.PARTY_PCK)).files
        cls.table = bv.load_party_skill_text(os.path.join(_paths.TABLES_DIR, 'qol_party_skill_text.xlsx'))

    def test_writer_reproduces_the_originals(self):
        for fn, b in self.entries:
            with self.subTest(entry=fn):
                self.assertEqual(self.helper.write_party_skill(b, self.helper.read_party_skill(b)['effect']), bytes(b))

    def test_bounds_follow_the_sentence(self):
        by_name = {self.helper.read_party_skill(b)['name']: self.table[fn] for fn, b in self.entries}
        self.assertEqual(by_name['Full of Guts']['effect'], 'Max HP increased (up to +100).')
        self.assertEqual(by_name['Sales Experience']['effect'],
                         'Up to wind resistance +20% and AGI +10.')
        self.assertEqual(by_name['Celebrities']['effect'], 'Lightning resistance increased.')    # no guide gives it

    def test_every_bound_belongs_to_an_effect_of_the_pack(self):
        from text_checks import PARTY_BOUNDS
        ids = {self.helper.read_party_skill(b)['effect_id'] for _, b in self.entries}
        self.assertEqual(set(PARTY_BOUNDS), ids)

    def test_clean_build_and_a_wrong_bound(self):
        for mutate, clean in ((False, True), (True, False)):
            table, problems = copy.deepcopy(self.table), []
            if mutate:
                fn = next(f for f, r in table.items() if r['vanilla'] == 'ATK increased.')
                table[fn]['effect'] = 'ATK increased (up to +40).'
            with tempfile.TemporaryDirectory() as out:
                bv.build_party_skills(out, table, problems)
                bv.verify_party_skills(out, table, bv.VARIANTS['qol'], problems)
            self.assertEqual(problems == [], clean, problems)


class Rules(unittest.TestCase):
    """Nothing shown on screen is written in the tools: wording and guide figures come from qol_rules.xlsx."""

    def test_sheets_listed_in_about_exist(self):
        import rules
        book = rules._book()
        for row in rules.rows('About'):
            if not row['Sheet'].startswith('('):
                self.assertIn(row['Sheet'], book.sheetnames)
        self.assertEqual({ws for ws in book.sheetnames} - {r['Sheet'] for r in rules.rows('About')}, {'About'})

    def test_tools_hold_no_sentences(self):
        import rules
        import shortened_text
        self.assertEqual(len(shortened_text.ITEM_SENTENCES), len(rules.rows('ShortItems')))
        with open(os.path.join(_paths.TOOLS_DIR, 'shortened_text.py'), encoding='utf-8') as f:
            source = f.read()
        self.assertNotIn('Yakisoba', source)


class JointSkills(unittest.TestCase):
    """Joint skills: the sentence of the rules sheet, filled with the values the entry stores."""

    @classmethod
    def setUpClass(cls):
        from pck_handler import JoinSkillHelper
        cls.helper = JoinSkillHelper
        cls.entries = PckArchive(os.path.join(_paths.BACKUP_DIR, bv.JOINT_PCK)).files
        cls.table = bv.load_joint_skill_text(os.path.join(_paths.TABLES_DIR, 'qol_joint_skill_text.xlsx'))
        cls.by_name = {cls.helper.read_joint(b)['name']: (b, cls.table[fn]) for fn, b in cls.entries}

    def test_writer_reproduces_the_originals(self):
        for fn, b in self.entries:
            with self.subTest(entry=fn):
                self.assertEqual(self.helper.write_joint(b, self.helper.read_joint(b)['desc']), bytes(b))

    def test_layout_agrees_with_the_guide(self):
        """DT2-2 wiki, pages/27.html: Rush Zanber costs 1/7 of max TP, Jackpot all of it, Avatara needs five."""
        read = lambda name: self.helper.read_joint(self.by_name[name][0])
        self.assertEqual(read('Rush Zanber')['tp_divisor'], 7)
        self.assertEqual(read('Jackpot')['tp_divisor'], 1)
        self.assertEqual(read('Avatara')['members'], 5)
        self.assertEqual(read("Genocide Rain's Action")['msg'], 'Genocide Rain(St) pours down!')

    def test_stored_value_replaces_the_vague_word(self):
        self.assertEqual(self.by_name['Divine Punishment!'][1]['vanilla'],
                         'Deal physical damage to an enemy row. High chance of instakill.')
        self.assertEqual(self.by_name['Divine Punishment!'][1]['desc'],
                         'Deal physical damage to an enemy row. 85% chance of instakill.')
        self.assertEqual(self.by_name['Bunker Buster'][1]['desc'],
                         'Deal damage through to the back row. Physical attack/defense -25%.')
        for name, (_, row) in self.by_name.items():       # the battle bar holds 70 characters
            if name != "Genocide Rain's Action":
                self.assertLessEqual(len(row['desc']), 70, row['desc'])
        self.assertEqual(self.by_name['Rush Zanber'][1]['desc'], self.by_name['Rush Zanber'][1]['vanilla'])

    def test_clean_build_and_a_wrong_value(self):
        for mutate, clean in ((False, True), (True, False)):
            table, problems = copy.deepcopy(self.table), []
            if mutate:
                fn = next(f for f, r in table.items() if '85% chance of instakill' in r['desc'])
                table[fn]['desc'] = table[fn]['desc'].replace('85%', '95%')
            with tempfile.TemporaryDirectory() as out:
                bv.build_joint_skills(out, table, problems)
                bv.verify_joint_skills(out, table, bv.VARIANTS['qol'], problems)
            self.assertEqual(problems == [], clean, problems)


class Sealbooks(unittest.TestCase):
    """SealScrollData is kept as written (the game lists the enchantments itself); its layout is decoded."""

    def test_writer_reproduces_the_originals_and_enchants_exist(self):
        from pck_handler import SealScrollHelper, EnchantHelper
        enchant_ids = {struct.unpack_from('<i', b, 0)[0]
                       for _, b in PckArchive(os.path.join(_paths.BACKUP_DIR, bv.ENCHANT_PCK)).files}
        entries = PckArchive(os.path.join(_paths.BACKUP_DIR, 'SealScrollData.pck')).files
        self.assertEqual(len(entries), 374)
        for fn, b in entries:
            seal = SealScrollHelper.read_seal(b)
            with self.subTest(entry=fn):
                self.assertEqual(SealScrollHelper.write_seal(b, seal['desc']), bytes(b))
                self.assertEqual(seal['name'], seal['name2'])
                self.assertTrue(set(seal['enchants']) <= enchant_ids)
                if not seal['grand']:
                    self.assertIn(f"(Level {seal['level']})", seal['desc'])


class PartySkillBox(unittest.TestCase):
    """The box of the party skill list: a line of 53 characters ran over its frame on screen
    ("Slash resistance increased. (Up to +25% at 50 awards)"), so the limit is that length minus 3."""
    OVERFLOWED = 'Slash resistance increased. (Up to +25% at 50 awards)'

    def test_limit_is_the_overflowing_line_minus_three(self):
        from text_checks import PARTY_LINE
        self.assertEqual(len(self.OVERFLOWED), 53)
        self.assertEqual(PARTY_LINE, len(self.OVERFLOWED) - 3)

    def test_every_line_fits_and_the_overflowing_one_is_rejected(self):
        from pck_handler import PartySkillHelper
        from text_checks import PARTY_LINE, check_party_skill_text
        table = bv.load_party_skill_text(os.path.join(_paths.TABLES_DIR, 'qol_party_skill_text.xlsx'))
        for fn, b in PckArchive(os.path.join(_paths.BACKUP_DIR, bv.PARTY_PCK)).files:
            skill = PartySkillHelper.read_party_skill(b)
            with self.subTest(skill=skill['name']):
                self.assertLessEqual(len(table[fn]['effect']), PARTY_LINE, table[fn]['effect'])
            if skill['name'] == 'Veteran Soldiers':
                self.assertEqual(table[fn]['effect'], 'Slash resistance increased (up to +25%).')
                self.assertNotEqual(check_party_skill_text(b, self.OVERFLOWED, skill['effect'])[0], [])

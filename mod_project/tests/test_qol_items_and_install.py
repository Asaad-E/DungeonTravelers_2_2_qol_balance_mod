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

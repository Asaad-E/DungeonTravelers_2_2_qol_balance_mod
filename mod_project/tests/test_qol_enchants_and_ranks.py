"""QoL enchant names and weapon rank labels: sourced figures, untouched game values, labels tied to the data."""
import os
import copy
import struct
import tempfile
import unittest

import _paths
import build_variant as bv
import enchant_values
import weapon_rank_labels
from pck_handler import PckArchive, EnchantHelper, WeaponRankHelper

TABLE_PATH = os.path.join(_paths.TABLES_DIR, 'qol_enchant_text.xlsx')
MAX_HP_UP = 'EnchantData_0000.bin'
FIRE_MAGIC = 'EnchantData_0078.bin'
VANILLA_DELAYS = [1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.15, 2.30, 2.45, 2.60, 2.75, 2.90]


class EntryRoundTrip(unittest.TestCase):
    def test_enchant_writer_reproduces_the_originals(self):
        for fn, b in PckArchive(os.path.join(_paths.BACKUP_DIR, bv.ENCHANT_PCK)).files:
            with self.subTest(entry=fn):
                self.assertEqual(EnchantHelper.write_enchant(b, EnchantHelper.read_enchant(b)['name']), bytes(b))

    def test_weapon_rank_writer_reproduces_the_originals(self):
        for fn, b in PckArchive(os.path.join(_paths.BACKUP_DIR, bv.RANK_PCK)).files:
            with self.subTest(entry=fn):
                self.assertEqual(WeaponRankHelper.write_rank(b, WeaponRankHelper.read_rank(b)['name']), bytes(b))


class EnchantValues(unittest.TestCase):
    def test_every_figure_names_a_known_source(self):
        for enchant_id, value in enchant_values.VALUES.items():
            with self.subTest(enchant=enchant_id):
                self.assertIn(value.source, enchant_values.SOURCES)

    def test_names_keep_the_game_wording_and_add_the_sourced_figure(self):
        self.assertEqual(enchant_values.qol_name(0, 'Max HP UP'), 'Max HP +10%')
        self.assertEqual(enchant_values.qol_name(71, 'Received damage MiniDOWN'), 'Received damage -4%')
        # Resistance is written as the status screen writes it: a plain number, no percent sign.
        self.assertEqual(enchant_values.qol_name(93, 'Water resistance DOWN'), 'Water resistance -20')
        # The game says Enmity; the name keeps the game's word.
        self.assertEqual(enchant_values.qol_name(50, 'Enmity DOWN'), 'Enmity -5%')
        # Known only from the first game's guide: shown by decision of the user, and labelled as such.
        self.assertEqual(enchant_values.proposal(78, 'Fire magic buff')[:2], ('Fire magic +20%', 'dt2-wiki'))
        self.assertEqual(enchant_values.qol_name(78, 'Fire magic buff'), 'Fire magic +20%')
        # No guide gives a figure: the vanilla name stays.
        self.assertIsNone(enchant_values.proposal(32, 'Physical accuracy MiniUP'))
        self.assertEqual(enchant_values.qol_name(32, 'Physical accuracy MiniUP'), 'Physical accuracy MiniUP')

    def test_a_source_that_is_not_trusted_is_not_shown(self):
        shown = enchant_values.SHOWN_SOURCES
        try:
            enchant_values.SHOWN_SOURCES = ('dt22-wiki',)
            self.assertEqual(enchant_values.qol_name(78, 'Fire magic buff'), 'Fire magic buff')
            self.assertEqual(enchant_values.qol_name(0, 'Max HP UP'), 'Max HP +10%')
        finally:
            enchant_values.SHOWN_SOURCES = shown


class EnchantTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = bv.load_enchant_text(TABLE_PATH)
        cls.entries = dict(PckArchive(os.path.join(_paths.BACKUP_DIR, bv.ENCHANT_PCK)).files)

    def test_one_row_per_enchant_with_the_backup_name(self):
        self.assertEqual(set(self.table), set(self.entries))
        for fn, b in self.entries.items():
            with self.subTest(entry=fn):
                self.assertEqual(self.table[fn]['vanilla_name'], EnchantHelper.read_enchant(b)['name'])

    def test_a_changed_name_is_sourced_or_marked_as_edited(self):
        renamed = 0
        for fn, row in self.table.items():
            if row['name'] == row['vanilla_name']:
                continue
            renamed += 1
            enchant_id = struct.unpack_from('<i', self.entries[fn], 0)[0]
            with self.subTest(entry=fn):
                self.assertTrue(row['edited'] or row['name'] == enchant_values.qol_name(enchant_id, row['vanilla_name']))
        self.assertGreater(renamed, 90)

    def test_names_fit_where_the_game_draws_them(self):
        for fn, row in self.table.items():
            limit = bv.MAX_NAME_ON_EQUIPMENT if EnchantHelper.read_enchant(self.entries[fn])['prefix'] != '0' else bv.MAX_NAME
            with self.subTest(entry=fn):
                self.assertLessEqual(len(row['name']), limit)


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = bv.load_enchant_text(TABLE_PATH)
        cls.variant = bv.VARIANTS['qol']

    def build(self, mutate_table=None, mutate_built=None):
        table = copy.deepcopy(self.table)
        if mutate_table:
            mutate_table(table)
        problems = []
        with tempfile.TemporaryDirectory() as out:
            bv.build_enchants(out, table, problems)
            bv.build_weapon_ranks(out)
            if mutate_built:
                mutate_built(out)
            if not problems:
                bv.verify_enchants(out, table, self.variant, problems)
                bv.verify_weapon_ranks(out, self.variant, problems)
        return problems

    def test_clean_build_has_no_problems(self):
        self.assertEqual(self.build(), [])

    def test_unsourced_figure_stops_the_build(self):
        def invent(table):
            table[FIRE_MAGIC]['name'] = 'Fire Magic +15%'      # the earlier mod's guess
        problems = self.build(mutate_table=invent)
        self.assertTrue(any('neither the sourced name nor marked as edited' in p for p in problems), problems)

    def test_hand_edit_is_accepted_when_marked(self):
        def approve(table):
            table[FIRE_MAGIC].update(name='Fire magic x1.2', edited=True)
        self.assertEqual(self.build(mutate_table=approve), [])

    def test_overlong_name_stops_the_build(self):
        def long_name(table):
            table[MAX_HP_UP].update(name='Max HP +10% ' + 'x' * 40, edited=True)
        self.assertNotEqual(self.build(mutate_table=long_name), [])

    def test_changed_enchant_flag_is_detected(self):
        def change_flag(out):
            path = os.path.join(out, bv.ENCHANT_PCK)
            archive = PckArchive(path)
            for i, (fn, b) in enumerate(archive.files):
                if fn == MAX_HP_UP:
                    patched = bytearray(b)
                    struct.pack_into('<i', patched, 0x2C, 99)
                    archive.files[i] = (fn, bytes(patched))
            archive.save(path)
        problems = self.build(mutate_built=change_flag)
        self.assertTrue(any('numeric data differs' in p for p in problems), problems)

    def test_changed_multiplier_is_detected(self):
        def change_delay(out):
            path = os.path.join(out, bv.RANK_PCK)
            archive = PckArchive(path)
            fn, b = archive.files[8]
            patched = bytearray(b)
            struct.pack_into('<f', patched, 0x10, 2.05)
            archive.files[8] = (fn, bytes(patched))
            archive.save(path)
        problems = self.build(mutate_built=change_delay)
        self.assertTrue(any('numeric data differs' in p for p in problems), problems)
        self.assertTrue(any("label 'E+ (2.45x)'" in p for p in problems), problems)


class WeaponRankLabels(unittest.TestCase):
    def archive(self):
        return PckArchive(os.path.join(_paths.BACKUP_DIR, bv.RANK_PCK))

    def test_labels_show_the_stored_multiplier(self):
        archive = self.archive()
        weapon_rank_labels.relabel(archive)
        self.assertEqual(weapon_rank_labels.check(archive), [])
        ranks = [WeaponRankHelper.read_rank(b) for _, b in archive.files]
        self.assertEqual([r['name'] for r in ranks][8], 'E+ (2.45x)')
        for rank, delay in zip(ranks, VANILLA_DELAYS):
            self.assertAlmostEqual(rank['delay'], delay, places=5)

    def test_label_follows_a_changed_multiplier(self):
        """A rebalanced multiplier gets its own figure: the label is never written by hand."""
        archive = self.archive()
        fn, b = archive.files[8]
        patched = bytearray(b)
        struct.pack_into('<f', patched, 0x10, 2.05)
        archive.files[8] = (fn, bytes(patched))
        weapon_rank_labels.relabel(archive)
        self.assertEqual(WeaponRankHelper.read_rank(archive.files[8][1])['name'], 'E+ (2.05x)')
        self.assertEqual(weapon_rank_labels.check(archive), [])

    def test_relabelling_twice_changes_nothing(self):
        archive = self.archive()
        weapon_rank_labels.relabel(archive)
        once = archive.build()
        weapon_rank_labels.relabel(archive)
        self.assertEqual(archive.build(), once)

    def test_unlabelled_or_stale_label_is_reported(self):
        self.assertEqual(len(weapon_rank_labels.check(self.archive())), 12)


if __name__ == '__main__':
    unittest.main()

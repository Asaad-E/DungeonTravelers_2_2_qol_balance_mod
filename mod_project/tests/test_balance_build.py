"""
The values of the Balance variant (tools/balance_values.py, tools/balance_readback.py): every live row of
balance_changes.xlsx is written into the packs, nothing else changes, and what the packs hold is what the simulator
plays.
"""
import os
import shutil
import struct
import sys
import tempfile
import unittest

import _paths  # noqa: F401
import balance_readback
import balance_values
from pck_handler import PckArchive
from sim import data as sim_data
from sim.variant import balance_data


class BalanceValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder = tempfile.mkdtemp(prefix='dt22_balance_')
        cls.rows = balance_values.live_rows()
        cls.packs, cls.written, cls.refused = balance_values.apply(cls.rows)
        cls.packs.save(cls.folder)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.folder, ignore_errors=True)

    def test_every_live_row_is_written(self):
        self.assertEqual(self.refused, [])
        self.assertEqual(sum(self.written.values()), len(self.rows))
        self.assertGreater(len(self.rows), 1000)

    def test_only_the_fields_of_the_rows_differ_from_the_originals(self):
        problems, counts = balance_values.check(self.packs, self.folder)
        self.assertEqual(problems, [])
        self.assertEqual(counts['fields'], len(self.packs.ledger))
        self.assertGreater(counts['bytes'], 0)

    def test_a_byte_no_row_wrote_is_found(self):
        """The check must see a change outside every row: one byte of an enemy stat nobody asked to move."""
        folder = tempfile.mkdtemp(prefix='dt22_balance_stray_')
        try:
            shutil.copytree(self.folder, folder, dirs_exist_ok=True)
            path = os.path.join(folder, 'EquipmentData.pck')
            archive = PckArchive(path)
            name, entry = archive.files[0]
            entry[0x28] ^= 0x01                           # DEF of the first piece
            archive.save(path)
            problems, _ = balance_values.check(self.packs, folder)
            self.assertTrue(any('outside every row' in p and name in p for p in problems), problems)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_a_row_whose_vanilla_value_is_wrong_is_refused(self):
        row = dict(next(r for r in self.rows if r['Table'] == 'enemies' and r['Field'] == 'hp'))
        row['Vanilla'] = int(row['Vanilla']) + 1
        _, _, refused = balance_values.apply([row])
        self.assertEqual(len(refused), 1)
        self.assertIn('the original holds', refused[0][1])

    def test_rows_with_no_place_in_the_record_are_refused(self):
        """What the build of 2026-10-11 found in the workbook: a passive holds one weapon code; a quest record has no
        gold field where the rows took it; the word after the drop chance is a count of pieces, not a chance."""
        base = {'ID': 'T1', 'Level': None, 'State': 'decided'}
        cases = [dict(base, Table='skills', Record='Passive 270 Warning Shot', Field='weapon codes', Vanilla='8', New='8, 15'),
                 dict(base, Table='quests', Record='QuestData_0000 (Fruit Fighter)', Field='gold reward', Vanilla=30, New=45),
                 dict(base, Table='enemies', Record='331 Overdue (P06)', Field='equipment drop rate', Vanilla=1, New=3)]
        _, written, refused = balance_values.apply(cases)
        self.assertEqual(written, {})
        self.assertEqual(len(refused), 3)

    def test_a_flag_row_may_only_move_immunity_bits(self):
        row = dict(next(r for r in self.rows if str(r['Field']).startswith('immunity flags')))
        row['New'] = hex(int(str(row['New']), 16) ^ (1 << 13))                 # bit 13: an adult, not an immunity
        _, _, refused = balance_values.apply([row])
        self.assertEqual(len(refused), 1)

    def test_two_rows_cannot_write_the_same_field(self):
        row = next(r for r in self.rows if r['Table'] == 'sp_curve')
        _, _, refused = balance_values.apply([row, dict(row, ID='T2')])
        self.assertEqual([r[0] for r in refused], ['T2'])

    def test_the_packs_hold_what_the_simulator_plays(self):
        """Read back with the readers of the project, the folder equals the variant of the simulator, table by table."""
        source = os.path.join(self.folder, 'source_of_truth.xlsx')
        self.assertEqual(balance_readback.extract(self.folder, source), [])
        differences, counts = balance_readback.compare(balance_readback.built_data(self.folder, source),
                                                       balance_data(sim_data.game_data()))
        self.assertEqual(differences, [])
        self.assertGreater(counts['skills'], 300)
        self.assertGreater(counts['enemies'], 500)

    def test_the_comparison_sees_a_difference(self):
        """The same comparison with one stat of the simulator moved must report it."""
        source = os.path.join(self.folder, 'source_of_truth.xlsx')
        if not os.path.exists(source):
            balance_readback.extract(self.folder, source)
        variant = balance_data(sim_data.game_data())
        some = next(iter(variant.enemies.values()))
        some['hp'] += 1
        differences, _ = balance_readback.compare(balance_readback.built_data(self.folder, source), variant)
        self.assertEqual(len(differences), 1)
        self.assertIn('hp', differences[0])


class BalanceValueFormats(unittest.TestCase):
    def test_a_whole_number_field_refuses_a_fraction(self):
        row = {'ID': 'T3', 'Table': 'sp_curve', 'Record': 'LvExpSkptData', 'Field': 'skill points gained at the level',
               'Level': 2, 'Vanilla': None, 'New': 3.5, 'State': 'decided'}
        packs = balance_values.Packs()
        name = next(fn for fn, b in packs.archive('LvExpSkptData.pck').files if struct.unpack_from('<I', b, 0)[0] == 2)
        row['Vanilla'] = struct.unpack_from('<I', packs.entry('LvExpSkptData.pck', name), balance_values.SP_POINTS)[0]
        _, _, refused = balance_values.apply([row])
        self.assertEqual(len(refused), 1)
        self.assertIn('whole number', refused[0][1])


if __name__ == '__main__':
    unittest.main()

"""The QoL variant: hand-editable text within the limits, true figures, untouched game values."""
import os
import copy
import struct
import tempfile
import unittest

import _paths
import build_variant as bv
from pck_handler import PckArchive, SkillHelper
from text_checks import check_skill_text

TABLE_PATH = os.path.join(_paths.TABLES_DIR, 'qol_skill_text.xlsx')
HALVING = ('Technique', 'TechniqueSkillData_0010.bin')


class TextTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = bv.load_skill_text(TABLE_PATH)
        cls.entries = {}
        for category, (pck, _, _) in bv.SKILL_PCKS.items():
            for fn, b in PckArchive(os.path.join(_paths.BACKUP_DIR, pck)).files:
                cls.entries[(category, fn)] = b

    def test_one_row_per_skill(self):
        self.assertEqual(set(self.table), set(self.entries))

    def test_vanilla_columns_are_the_backup_text(self):
        for key, b in self.entries.items():
            info = SkillHelper.read_skill(b, key[0])
            with self.subTest(skill=info['name']):
                self.assertEqual((self.table[key]['vanilla_desc'], self.table[key]['vanilla_lvup']),
                                 (info['desc'], info['lvup']))

    def test_boxes_fit_the_screen(self):
        """3 lines; a line is chosen for 85 characters, measured on screen, and may reach the wide limit once its
        separators are widened; with narrow separators it is back within 85. No tilde (missing glyph)."""
        for key, row in self.table.items():
            if (row['desc'], row['lvup']) == (row['vanilla_desc'], row['vanilla_lvup']):
                continue
            lines = row['desc'].split('\n') + (row['lvup'].split('\n') if row['lvup'] else [])
            added = lines[len(row['vanilla_desc'].split('\n')):] if row['desc'].startswith(row['vanilla_desc']) else lines
            with self.subTest(skill=key[1]):
                self.assertLessEqual(len(lines), bv.MAX_BOX_LINES)
                self.assertTrue(all(len(l) <= bv.SKILL_LINE for l in added), added)
                self.assertTrue(all(len(' | '.join(part.strip() for part in l.split('|'))) <= bv.MAX_LINE for l in added), added)
                self.assertNotIn('~', row['desc'] + row['lvup'])
                (row['desc'] + row['lvup']).encode('latin-1')

    def test_every_figure_is_the_binary_value(self):
        checked = 0
        for key, row in self.table.items():
            if (row['desc'], row['lvup']) == (row['vanilla_desc'], row['vanilla_lvup']):
                continue
            text = row['lvup'] if key[0] != 'Unique' else row['desc'][len(row['vanilla_desc']):].strip('\n')
            problems, verified, _ = check_skill_text(key[0], self.entries[key], text)
            checked += verified
            with self.subTest(skill=key[1]):
                self.assertEqual(problems, [])
        self.assertGreater(checked, 500)


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = bv.load_skill_text(TABLE_PATH)
        cls.variant = bv.VARIANTS['qol']

    def build(self, mutate_table=None, mutate_built=None):
        table = copy.deepcopy(self.table)
        if mutate_table:
            mutate_table(table)
        problems = []
        with tempfile.TemporaryDirectory() as out:
            bv.build_skills(out, table, problems)
            if mutate_built:
                mutate_built(out)
            if not problems:
                bv.verify_skills(out, table, self.variant, problems)
        return problems

    def test_writers_reproduce_the_originals(self):
        problems = []
        bv.self_test_writers(problems)
        self.assertEqual(problems, [])

    def test_clean_build_has_no_problems(self):
        self.assertEqual(self.build(), [])

    def test_wrong_figure_in_the_text_stops_the_build(self):
        def wrong_tp(table):
            table[HALVING]['lvup'] = table[HALVING]['lvup'].replace('TP Cost: 38', 'TP Cost: 15')
        self.assertIn('TP Cost: 15', self.table[HALVING]['lvup'].replace('TP Cost: 38', 'TP Cost: 15'))
        self.assertNotEqual(self.build(mutate_table=wrong_tp), [])

    def test_overlong_line_stops_the_build(self):
        def long_line(table):
            table[HALVING]['lvup'] += ' | ' + 'x' * 60
        self.assertNotEqual(self.build(mutate_table=long_line), [])

    def test_stale_table_stops_the_build(self):
        def stale(table):
            table[HALVING]['vanilla_lvup'] = 'LvUp: something else'
        self.assertNotEqual(self.build(mutate_table=stale), [])

    def test_changed_game_value_is_detected(self):
        def change_tp(out):
            path = os.path.join(out, 'TechniqueSkillData.pck')
            archive = PckArchive(path)
            for i, (fn, b) in enumerate(archive.files):
                if fn == HALVING[1]:
                    patched = bytearray(b)
                    struct.pack_into('<i', patched, 0x5C, 15)
                    archive.files[i] = (fn, bytes(patched))
            archive.save(path)
        problems = self.build(mutate_built=change_tp)
        self.assertTrue(any('numeric data differs' in p for p in problems), problems)

    def test_lost_battle_message_is_detected(self):
        def drop_message(out):
            path = os.path.join(out, 'PassiveSkillData.pck')
            archive = PckArchive(path)
            for i, (fn, b) in enumerate(archive.files):
                if SkillHelper.read_skill(b, 'Passive')['name'] == 'Guts':
                    patched = bytearray(b)
                    patched[struct.unpack_from('<Q', b, 32)[0]] = 0
                    archive.files[i] = (fn, bytes(patched))
            archive.save(path)
        problems = self.build(mutate_built=drop_message)
        self.assertTrue(any('battle message' in p for p in problems), problems)


if __name__ == '__main__':
    unittest.main()

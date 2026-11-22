"""Automated binary-table and direct .pck round-trip invariants (Phase 3 deliverable).

Asserts 1-to-1 equality between:
  1. Vanilla .exe vtable boolean flag groups in docs/binary_spec/00_INVENTORY.json
     and the constant tables in engine_cs/src/DtEngine/Battle.cs & Data.cs.
  2. Raw backups/**/*.pck records and build/engine_snapshot.json exported by tools/engine_export.py.
"""
import json
import os
import re
import struct
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))

from pck_handler import PckArchive  # noqa: E402

INVENTORY_PATH = os.path.join(ROOT, 'docs', 'binary_spec', '00_INVENTORY.json')
BATTLE_CS = os.path.join(ROOT, 'engine_cs', 'src', 'DtEngine', 'Battle.cs')
DATA_CS = os.path.join(ROOT, 'engine_cs', 'src', 'DtEngine', 'Data.cs')
SNAPSHOT_PATH = os.path.join(ROOT, 'build', 'engine_snapshot.json')


def _parse_cs_int_array(src, name):
    m = re.search(rf'\b{re.escape(name)}\s*=\s*\{{([^}}]+)\}}', src)
    if not m:
        raise AssertionError(f'Could not find C# int array {name}')
    return {int(x.strip()) for x in m.group(1).split(',') if x.strip()}


def _parse_cs_hashset(src, name):
    m = re.search(rf'\b{re.escape(name)}\s*=\s*new\s+HashSet<int>\s*\{{([^}}]+)\}}', src, re.S)
    if not m:
        raise AssertionError(f'Could not find C# HashSet<int> {name}')
    return {int(x.strip()) for x in m.group(1).split(',') if x.strip()}


class BinaryVtableInvariantsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(INVENTORY_PATH, encoding='utf-8') as f:
            cls.inv = json.load(f)
        with open(BATTLE_CS, encoding='utf-8') as f:
            cls.battle_cs = f.read()
        with open(DATA_CS, encoding='utf-8') as f:
            cls.data_cs = f.read()
        # Group vtable slot -> always-1 and dynamic command IDs from 00_INVENTORY.json
        cls.always_one = {}
        cls.dynamic = {}
        for cid_str, info in cls.inv['route_a_ccommand'].items():
            cid = int(cid_str)
            for slot, val in info.get('flags', {}).items():
                if val == 1:
                    cls.always_one.setdefault(slot, set()).add(cid)
                elif isinstance(val, str) and val.startswith('dynamic:'):
                    cls.dynamic.setdefault(slot, set()).add(cid)

    def test_performance_groups_match_vtable_slots(self):
        self.assertEqual(_parse_cs_int_array(self.battle_cs, 'SONG_EFFECTS'), self.always_one['+0x6c'])
        self.assertEqual(_parse_cs_int_array(self.battle_cs, 'DANCE_EFFECTS'), self.always_one['+0x70'])
        self.assertEqual(_parse_cs_int_array(self.battle_cs, 'PUPPET_EFFECTS'), self.always_one['+0x74'])
        self.assertEqual(set(range(335, 342)), self.always_one['+0x78'])

    def test_exclusive_groups_match_vtable_slots(self):
        self.assertEqual({325, 326, 327, 328, 329}, self.always_one['+0x7c'])
        self.assertEqual({101, 102, 181}, self.always_one['+0x84'])
        self.assertEqual({113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 139}, self.always_one['+0x68'])

    def test_buff_debuff_vtable_slots(self):
        self.assertEqual({27, 171, 325, 326, 327, 328, 329}, self.always_one['+0x54'])
        self.assertEqual({30}, self.always_one['+0x5c'])
        self.assertEqual(self.dynamic['+0x54'], self.dynamic['+0x5c'])
        # Command 32 has inverted sign handler (0x479e40)
        self.assertIn(32, self.dynamic['+0x54'])

    def test_command_data_pck_flags38_matches_cs_defaults(self):
        pck = PckArchive(os.path.join(ROOT, 'backups', 'CommandData.pck'))
        raw_sleep = {struct.unpack_from('<i', b, 0)[0] for _, b in pck.files if struct.unpack_from('<I', b, 0x38)[0] & 2}
        raw_death_exempt = {struct.unpack_from('<i', b, 0)[0] for _, b in pck.files if not (struct.unpack_from('<I', b, 0x38)[0] & 4)}
        self.assertEqual(len(raw_sleep), 36)
        self.assertEqual(len(raw_death_exempt), 8)
        self.assertEqual(_parse_cs_hashset(self.data_cs, 'SleepClearedCommands'), raw_sleep)
        self.assertEqual(_parse_cs_hashset(self.data_cs, 'DeathExemptCommands'), raw_death_exempt)


class DirectPckRoundTripTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(SNAPSHOT_PATH):
            raise unittest.SkipTest('build/engine_snapshot.json not built')
        with open(SNAPSHOT_PATH, encoding='utf-8') as f:
            cls.snap = json.load(f)
        cls.vanilla = cls.snap['sides']['vanilla']

    def test_snapshot_exports_patterns_items_commands_and_characters(self):
        # Patterns exported for skills and enemy attacks
        skills = self.vanilla['skills']
        attacks = self.vanilla['attacks']
        self.assertTrue(all('pattern' in s for s in skills))
        self.assertTrue(all('pattern' in a for a in attacks))
        self.assertGreater(sum(1 for s in skills if s['pattern'] != 0), 50)
        self.assertGreater(sum(1 for a in attacks if a['pattern'] != 0), 100)

        # CommandData flags38 round-trip
        pck = PckArchive(os.path.join(ROOT, 'backups', 'CommandData.pck'))
        raw_sleep = sorted(struct.unpack_from('<i', b, 0)[0] for _, b in pck.files if struct.unpack_from('<I', b, 0x38)[0] & 2)
        raw_death_exempt = sorted(struct.unpack_from('<i', b, 0)[0] for _, b in pck.files if not (struct.unpack_from('<I', b, 0x38)[0] & 4))
        self.assertEqual(self.vanilla['command_sleep_cleared'], raw_sleep)
        self.assertEqual(self.vanilla['command_death_exempt'], raw_death_exempt)

        # Items export target_type (16/17/18) and flags
        items = self.vanilla['items']
        self.assertTrue(all('target_type' in it and 'flags' in it for it in items))
        self.assertGreaterEqual(sum(1 for it in items if it['target_type'] == 17), 9)
        self.assertGreaterEqual(sum(1 for it in items if it['target_type'] == 18), 50)

        # Characters export race (+0x30, Ist == 6) and 21-float pep table
        chars = {c['name']: c for c in self.vanilla['characters']}
        self.assertEqual(chars['Ist']['race'], 6)
        self.assertTrue(all(len(c['pep']) == 21 for c in chars.values()))


if __name__ == '__main__':
    unittest.main()

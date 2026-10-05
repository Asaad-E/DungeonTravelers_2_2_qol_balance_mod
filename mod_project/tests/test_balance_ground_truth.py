"""Ground truth of the Balance work: enemies and class growth are data, and they read as the screens show."""
import os
import struct
import unittest

import _paths
import enemy_data
from pck_handler import PckArchive


class NestedArchives(unittest.TestCase):
    def test_enemy_dungeon_and_summon_packs_rebuild_byte_for_byte(self):
        for rel in ('Enemy/Enemy.pck', 'Dungeon/Dungeon.pck', 'Summon/Summon.pck'):
            path = os.path.join(_paths.BACKUP_DIR, *rel.split('/'))
            with open(path, 'rb') as f:
                raw = f.read()
            outer = PckArchive(path)
            with self.subTest(archive=rel):
                self.assertEqual(outer.build(), raw)
                for fn, b in outer.files:
                    self.assertEqual(PckArchive.from_bytes(b).build(), bytes(b), fn)


class Enemies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enemies = enemy_data.enemies()
        cls.by_name = {}
        for e in cls.enemies:
            cls.by_name.setdefault(e['name'], e)

    def test_count_and_levels(self):
        self.assertEqual(len(self.enemies), 516)
        self.assertEqual((min(e['level'] for e in self.enemies), max(e['level'] for e in self.enemies)), (1, 99))

    def test_stats_are_the_ones_of_the_enemy_screen(self):
        """Screenshots of 2026-10-04: Medic Lv 11; Selene Lv 13, Max HP 226, resistances +15 +30 0 +10 0 0 +20 +20."""
        medic, selene = self.by_name['Medic'], self.by_name['Selene']
        self.assertEqual((medic['level'], medic['habitat']), (11, 'Vrachia Town'))
        self.assertEqual((selene['level'], selene['hp']), (13, 226))
        self.assertEqual([selene['res_' + k] for k in enemy_data.RESISTANCES], [15, 30, 0, 10, 0, 0, 20, 20])

    def test_every_attack_exists(self):
        attack_ids = {struct.unpack_from('<i', b, 0)[0]
                      for _, b in PckArchive(os.path.join(_paths.BACKUP_DIR, 'EnemyAttackData.pck')).files}
        for e in self.enemies:
            with self.subTest(enemy=e['name']):
                self.assertTrue(e['attacks'])
                self.assertTrue(set(e['attacks']) <= attack_ids)


class ClassGrowth(unittest.TestCase):
    def test_paladin_level_20_is_the_status_screen_of_luco(self):
        """ClassLevelData: class id, then 99 rows of HP, TP, ATK, DEF, INT, RES, DEX, AGI.
        Luco, Paladin Lv 20 on screen: TP 63, INT 15, RES 18, DEX 25, AGI 19 (stats her gear does not touch)."""
        rows = PckArchive(os.path.join(_paths.BACKUP_DIR, 'ClassLevelData.pck')).files
        self.assertEqual({len(b) for _, b in rows}, {4 + 99 * 32})
        hp, tp, atk, dfn, intel, res, dex, agi = struct.unpack_from('<8i', bytes(rows[1][1]), 4 + 32 * 19)
        self.assertEqual((tp, intel, res, dex, agi), (63, 15, 18, 25, 19))


if __name__ == '__main__':
    unittest.main()

"""The check of a change (sim/measures.py): which checkpoints it touches and what it reports."""
import sys
import unittest

import _paths
sys.path.insert(0, _paths.PROJECT_DIR)
from sim import measures, scenario
from sim import setup as setup_mod
from sim.data import game_data


class CheckOfAChange(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.setup = game_data(), setup_mod.load()
        cp = cls.setup.checkpoint('C07')
        cls.boss = next(e for b in cls.data.fixed if b['floor'] == cp['Floor'] and
                        b['number'] in scenario.battle_numbers(cp) for e, _ in b['enemies'])

    def test_a_boss_change_touches_its_checkpoint_only(self):
        changes = [('enemies', self.boss, 'hp', self.data.enemies[self.boss]['hp'] // 2)]
        self.assertEqual(measures.touched(self.data, self.setup, changes), ['C07'])

    def test_a_change_to_a_table_without_owner_touches_every_checkpoint(self):
        changes = [('weapon_ranks', 5, None, 1.0)]
        self.assertEqual(len(measures.touched(self.data, self.setup, changes)), len(self.setup.checkpoints))

    def test_a_skill_of_the_reference_party_touches_the_checkpoints_where_it_is_learned(self):
        carol = next(k for k, s in self.data.skills.items() if s.name == 'Replenishing Carol')
        found = measures.touched(self.data, self.setup, [('skills', carol, 'tp', None)])
        self.assertIn('C34', found)
        self.assertNotIn(self.setup.checkpoints[0]['ID'], found)

    def test_the_check_reports_vanilla_against_the_change_and_the_windows_left(self):
        half = self.data.enemies[self.boss]['hp'] // 2
        (cid, before, after, out), = measures.check_change(self.data, self.setup, [('enemies', self.boss, 'hp', half)],
                                                           runs=6)
        self.assertEqual(cid, 'C07')
        self.assertGreaterEqual(after['won'], before['won'])
        self.assertTrue(set(out) <= {'won', 'time', 'lowest_hp', 'pressure'})
        self.assertEqual(self.data.enemies[self.boss]['hp'], half * 2 + self.data.enemies[self.boss]['hp'] % 2)


if __name__ == '__main__':
    unittest.main()

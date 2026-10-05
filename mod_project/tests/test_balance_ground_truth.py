"""Ground truth of the Balance work: enemies and class growth are data, and they read as the screens show."""
import os
import struct
import unittest

import _paths
import class_data
import enemy_ai
import enemy_data
import floor_data
import summon_data
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

    def test_flags_and_races_are_named(self):
        """Race values are the ones the "attack vs." enchantments test; the flag bits the ones each ailment tests."""
        by_name = {e['name']: e for e in self.enemies}
        self.assertEqual(by_name['Hola-Orange']['race_name'], 'Fruit')
        self.assertEqual(by_name['Red Dragon']['race_name'], 'Dragons')
        self.assertEqual(by_name['Skeleton']['race_name'], 'Undead')
        weak = [e for e in self.enemies if e['level'] <= 14]
        strong = [e for e in self.enemies if e['level'] >= 85]
        share = lambda group: sum(len(e['immune']) for e in group) / len(group)
        self.assertGreater(share(strong), share(weak))          # set bits are immunities: late enemies carry more

    def test_drops_are_items_with_a_chance(self):
        self.assertEqual({e['name']: e['drops'] for e in self.enemies if e['name'] == 'Medic'}['Medic'], [(588, 14), (24, 15)])
        for enemy in self.enemies:
            for item, chance in enemy['drops']:
                with self.subTest(enemy=enemy['name']):
                    self.assertTrue(item >= 0 and 0 < chance <= 100)

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

    def test_the_row_of_a_class_is_the_one_the_game_picks(self):
        """GetClassLevelID (0x5545b0): Paladin is row 1, and a class with two routes has a row per route."""
        luco = class_data.stats(1, 20)
        self.assertEqual((luco['tp'], luco['int'], luco['res'], luco['dex'], luco['agi']), (63, 15, 18, 25, 19))
        self.assertEqual(class_data.growth_row(4, previous=1), 4)
        self.assertEqual(class_data.growth_row(4, previous=2), 5)
        self.assertEqual(class_data.growth_row(4), 4)               # any other previous class: the first row
        self.assertEqual(sorted(row for _, _, row in class_data.routes()), list(range(38)))

    def test_a_route_only_changes_what_comes_after_it(self):
        """Both Samurai rows have the HP of their second class at level 30 and differ at level 99."""
        table = class_data.growth()
        for final, first, second in ((4, 1, 2), (10, 7, 8), (17, 13, 14), (18, 14, 15), (24, 21, 22)):
            for previous in (first, second):
                with self.subTest(final=final, previous=previous):
                    self.assertEqual(class_data.stats(final, 30, previous, table)['hp'],
                                     class_data.stats(previous, 30, table=table)['hp'])
            self.assertNotEqual(class_data.stats(final, 99, first, table), class_data.stats(final, 99, second, table))



class EnemyBehaviour(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enemies = enemy_data.enemies()
        cls.scripts = {e['id']: enemy_ai.decode(e['ai']) for e in cls.enemies}

    def test_every_script_decodes_to_its_end_and_carries_its_own_id(self):
        self.assertEqual(len(self.scripts), len(self.enemies))
        for enemy in self.enemies:
            self.assertEqual(self.scripts[enemy['id']]['id'], enemy['id'])

    def test_every_set_can_pick_an_attack(self):
        """Lever L05: a set whose weights add up to 0 picks nothing and the choice of attack loops (0x430f10)."""
        for enemy in self.enemies:
            script = self.scripts[enemy['id']]
            with self.subTest(enemy=enemy['name']):
                self.assertIn(0, script['sets'])
                for entry in script['sets'].values():
                    self.assertGreater(sum(entry['weights']), 0)

    def test_weights_only_point_at_attacks_the_enemy_has(self):
        for enemy in self.enemies:
            for entry in self.scripts[enemy['id']]['sets'].values():
                used = [slot for slot, weight in enumerate(entry['weights']) if weight]
                with self.subTest(enemy=enemy['name']):
                    self.assertLess(max(used, default=0), len(enemy['attacks']))

    def test_a_command_after_a_set_speaks_of_a_skill_of_that_set(self):
        """What shows that the commands after a set belong to it (the parser files them at 0x430cd7)."""
        for enemy in self.enemies:
            for entry in self.scripts[enemy['id']]['sets'].values():
                for command in entry['commands']:
                    word = command['args'][0]
                    if word & enemy_ai.SLOT:
                        with self.subTest(enemy=enemy['name']):
                            self.assertGreater(entry['weights'][word & 0x3FFF], 0)

    def test_known_scripts(self):
        by_name = {e['name']: self.scripts[e['id']] for e in self.enemies}
        self.assertEqual(by_name['Pirate']['sets'][0]['weights'][:3], [50, 30, 20])
        medic = by_name['Medic']
        self.assertEqual(enemy_ai.describe(medic['opening'][0]), 'an ally has an ailment -> set 1')
        self.assertEqual(enemy_ai.describe(medic['sets'][1]['commands'][0]),
                         'slot 2 aims at: ally with a more serious ailment')
        selene = by_name['Selene']
        self.assertEqual(enemy_ai.describe(selene['opening'][0]), 'own HP ratio <= 50 -> set 1 (once)')



class Floors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floors = floor_data.floors()
        cls.enemy_ids = {e['id'] for e in enemy_data.enemies()}

    def test_every_zone_shares_out_one_hundred_among_its_formations(self):
        self.assertGreater(len(self.floors), 170)
        self.assertGreater(len({f['floor'] for f in self.floors}), 100)
        for floor in self.floors:
            with self.subTest(floor=floor['name']):
                self.assertEqual(sum(f['chance'] for f in floor['formations']), 100)
                self.assertEqual([f['number'] for f in floor['formations']], list(range(1, len(floor['formations']) + 1)))

    def test_zone_factors_raise_and_lower(self):
        """The five floats a battle copies from its zone (0x44994d): two that raise, two that lower, one for elements."""
        for floor in self.floors:
            factors = floor['zone_factors']
            with self.subTest(floor=floor['name']):
                self.assertTrue(1.5 <= factors['up_a'] <= 3 and 1.5 <= factors['up_b'] <= 3 and 1.5 <= factors['element'] <= 3)
                self.assertTrue(0.3 <= factors['down_a'] <= 1 and 0.3 <= factors['down_b'] <= 1)

    def test_every_formation_holds_known_enemies(self):
        for floor in self.floors:
            for formation in floor['formations']:
                with self.subTest(floor=floor['name'], formation=formation['number']):
                    self.assertTrue(formation['enemies'])
                    self.assertTrue({e for e, _ in formation['enemies']} <= self.enemy_ids)

    def test_a_lone_enemy_stands_in_front(self):
        for floor in self.floors:
            for formation in floor['formations']:
                if len(formation['enemies']) == 1:
                    self.assertTrue(formation['enemies'][0][1], floor['name'])



class LevelTable(unittest.TestCase):
    def test_exp_needed_grows_with_every_level(self):
        """Lever L11: the level-up code walks LvExpSkptData level by level (0x448560)."""
        import openpyxl
        ws = openpyxl.load_workbook(os.path.join(_paths.PROJECT_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx'),
                                    read_only=True)['ExpCurve']
        rows = list(ws.iter_rows(values_only=True))
        level, needed = rows[0].index('Level'), rows[0].index('Req_EXP')
        table = sorted((r[level], r[needed]) for r in rows[1:])
        self.assertEqual([lv for lv, _ in table], list(range(table[0][0], table[0][0] + len(table))))
        for (_, a), (_, b) in zip(table, table[1:]):
            self.assertGreater(b, a)



class FixedBattles(unittest.TestCase):
    def test_every_enemy_is_placed_somewhere(self):
        """Random formations and fixed battles together hold every enemy but the chests that bite."""
        enemies = enemy_data.enemies()
        placed = {e for f in floor_data.floors() for formation in f['formations'] for e, _ in formation['enemies']}
        fixed = floor_data.fixed_battles()
        self.assertGreater(len(fixed), 150)
        placed |= {e for battle in fixed for e, _ in battle['enemies']}
        missing = sorted(e['name'] for e in enemies if e['id'] not in placed)
        self.assertLessEqual(len(missing), 10, missing)
        self.assertTrue(all(battle['enemies'] for battle in fixed))


class Summons(unittest.TestCase):
    def test_three_forms_per_summon_and_each_comes_from_an_enemy(self):
        forms = summon_data.summons()
        enemies = {e['id']: e['name'] for e in enemy_data.enemies()}
        families = {}
        for form in forms:
            families.setdefault(form['family'], []).append(form)
        for family, own in families.items():
            with self.subTest(family=family):
                self.assertEqual(len(own), 3)
                self.assertEqual(enemies[family], own[0]['name'])
                self.assertEqual([f['level'] for f in own], sorted(f['level'] for f in own))
                self.assertTrue(all(len(f['attacks']) > 0 and sum(f['script']['sets'][0]['weights']) > 0 for f in own))

    def test_the_form_follows_the_level_of_the_party(self):
        forms = summon_data.summons()
        bigfoot = [f for f in forms if f['name'] == 'Bigfoot']
        levels = [f['level'] for f in bigfoot]
        family = bigfoot[0]['family']
        self.assertEqual(summon_data.form_for(family, levels[0] - 1, forms)['level'], levels[0])     # below the first: the first
        self.assertEqual(summon_data.form_for(family, levels[1], forms)['level'], levels[1])
        self.assertEqual(summon_data.form_for(family, 99, forms)['level'], levels[2])


if __name__ == '__main__':
    unittest.main()

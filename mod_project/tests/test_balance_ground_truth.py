"""Ground truth of the Balance work: enemies and class growth are data, and they read as the screens show."""
import os
import struct
import unittest

import _paths
import class_data
import class_modifier_data
import character_data
import doll_data
import random_move_data
import skill_tree_data
import enemy_ai
import enemy_data
import exe_patch
import floor_data
import item_effect_data
import npc_data
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

    def test_every_zone_has_an_encounter_chance(self):
        """zone+0x1C is the chance per step of a random battle (0x4bc773): a small percent in every zone that has formations."""
        chances = [zone['encounter'] for zone in floor_data.floors()]
        self.assertTrue(all(0 <= c <= 10 for c in chances), sorted(set(chances)))
        self.assertGreater(sum(1 for c in chances if c >= 5), 0.9 * len(chances))

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



class Characters(unittest.TestCase):
    def test_each_character_has_a_base_class_and_her_unique_skill(self):
        """PlayerStatusData.bin (program table 0x738a08): Alisia is a Fighter with Positive Trance, as the game shows."""
        girls = character_data.characters()
        self.assertEqual(len(girls), 18)
        alisia = girls[0]
        self.assertEqual((alisia['name'], alisia['base_class'], alisia['unique_skill']), ('Alisia', 0, 364))
        self.assertEqual({g['base_class'] for g in girls}, {0, 6, 12, 20, 26})           # the five base classes
        self.assertEqual(len({g['unique_skill'] for g in girls}), 18)

    def test_pep_amounts(self):
        """Falling in battle always costs Pep and felling an enemy never does; Pep is kept between 70 and 130 (0x4f69e0)."""
        for girl in character_data.characters():
            with self.subTest(girl=girl['name']):
                self.assertEqual(len(girl['pep']), 21)
                self.assertLess(girl['pep'][1], 0)
                self.assertGreaterEqual(girl['pep'][0], 0)
        self.assertEqual(character_data.clamp_pep(500), 130)
        self.assertEqual(character_data.clamp_pep(0), 70)


class ClassModifiers(unittest.TestCase):
    def test_tables_of_the_executable(self):
        """_CalculateParameterSpecialty (0x4f7c60): one table per class, two for the six classes with two routes."""
        rows = class_modifier_data.class_modifiers()
        self.assertEqual(sorted({r['class'] for r in rows}), list(range(32)))
        self.assertEqual(len(rows), 38)
        two_routes = sorted({r['class'] for r in rows if r['previous'] is not None})
        self.assertEqual(two_routes, [4, 10, 17, 18, 24, 30])                 # the same classes class_data.GROWTH_ROW splits
        for row in rows:
            for entry in row['entries']:
                self.assertTrue(0.005 < entry['modifier'] < 0.06, (row['class'], entry))
        fighter = next(r for r in rows if r['class'] == 0)
        self.assertEqual([(e['type_name'], round(e['modifier'], 2)) for e in fighter['entries']], [('Sword', 0.01)])

    def test_gain_of_a_stat(self):
        self.assertEqual(class_modifier_data.specialty_gain(200, 100, 0.05), 15)
        self.assertEqual(class_modifier_data.specialty_gain(200, 0, 0.05), 0)             # the piece must give the stat
        self.assertEqual(class_modifier_data.specialty_gain(200, 100, 0.05, yearning=6), 33)


class SkillTree(unittest.TestCase):
    def test_class_masks(self):
        """The mask of a skill file (0x56dc10 tests it with 1 << class): Raging Smash is a Fighter skill, Gold Steal a Scout
        skill, Fireball a Magic User skill; the hidden actions belong to no class."""
        skills = {(s['category'], s['name']): s for s in skill_tree_data.skills()}
        self.assertEqual(skills[('Technique', 'Raging Smash')]['classes'], [0])
        self.assertEqual(skills[('Technique', 'Gold Steal')]['classes'], [6])
        self.assertEqual(skills[('Magic', 'Fireball')]['classes'], [12])
        self.assertEqual(skills[('Technique', "Spartan's Action")]['classes'], [])
        tree = skill_tree_data.by_class()
        self.assertEqual(sorted(tree), list(range(32)))                       # every class learns something
        for class_id, learned in tree.items():
            self.assertGreaterEqual(len(learned), 5, class_id)

    def test_patterns_of_the_random_moves(self):
        """Patterns 10, 11, 12 and 14 of _CreatePattern are the four skills whose tables random_move_data reads."""
        by_pattern = {s['pattern']: s['name'] for s in skill_tree_data.skills() if s['pattern'] in (10, 11, 12, 14)}
        self.assertEqual(by_pattern, {10: 'Roulette Circus', 11: 'Magic Box', 12: 'Showtime', 14: 'Heaven or Hell'})

    def test_range_of_a_technique(self):
        ranges = {s['name']: s['range'] for s in skill_tree_data.skills() if s['category'] == 'Technique'}
        self.assertEqual((ranges['Raging Smash'], ranges['Chain Spike'], ranges['Hard Whipping'], ranges['Provoke']),
                         ('short', 'long', 'mid', 'none'))


class RandomMoves(unittest.TestCase):
    def test_tables_point_at_the_hidden_skills_of_their_skill(self):
        """The four tables of the executable (0x41e060) name hidden skills the game calls "<skill> Effect"."""
        moves = random_move_data.random_moves()
        self.assertEqual([m['name'] for m in moves], ['Roulette Circus', 'Magic Box', 'Showtime', 'Heaven or Hell'])
        by_id = {r['Skill_ID']: r['Name'] for r in random_move_data._rows('Skills') if r['Category'] == 'Technique'}
        for move in moves:
            with self.subTest(move=move['name']):
                for result in move['results']:
                    self.assertEqual(by_id[result['skill']], move['name'] + ' Effect')
                    self.assertGreater(result['weight'], 0)
                self.assertAlmostEqual(sum(r['chance'] for r in move['results']), 1)
                self.assertAlmostEqual(sum(r['joker_chance'] for r in move['results']), 1)

    def test_triple_joker_tilts_heaven_or_hell(self):
        heaven = random_move_data.random_moves()[-1]['results']
        self.assertEqual([r['weight'] for r in heaven], [50, 50])
        self.assertEqual([r['joker_weight'] for r in heaven], [70, 30])


class GuestAllies(unittest.TestCase):
    def test_records(self):
        """NPC.pck (table 0x738a04): Euthys grows through her stages, and every ally has attacks and a script."""
        allies = npc_data.npcs()
        self.assertEqual(len(allies), 107)
        euthys = [a for a in allies if a['name'] == 'Euthys']
        self.assertEqual([a['level'] for a in euthys], sorted(a['level'] for a in euthys))
        self.assertEqual([a['atk'] for a in euthys], sorted(a['atk'] for a in euthys))
        self.assertEqual(euthys[-1]['level'], 99)
        for ally in allies:
            self.assertTrue(1 <= len(ally['attacks']) <= 11, ally['name'])
            self.assertTrue(ally['script']['sets'], ally['name'])


class EnemyPassives(unittest.TestCase):
    def test_passives_are_passive_entries(self):
        """The ids at 0xF4 of an enemy record name EnemyAttackData entries whose text says they are passive skills."""
        text = {r['Skill_ID']: str(r['Vanilla_Desc']) for r in doll_data._rows('EnemyAttacks')}
        enemies = enemy_data.enemies()
        carried = {a for e in enemies for a in e['passives']}
        self.assertGreater(len(carried), 50)
        self.assertTrue(all('Passive' in text[a] for a in carried))
        self.assertTrue(all(len(e['passives']) == e['raw_f0'][0] for e in enemies))


class ItemEffects(unittest.TestCase):
    def test_types_that_perform_a_skill(self):
        """The class of an item effect type (switch at 0x50c596) calls 0x50b030 with a skill id: type 90 is Fireball,
        27 and 29 are the two speed skills the player guides could not tell apart."""
        performs = item_effect_data.skill_items()
        names = item_effect_data.skill_names()
        self.assertEqual(len(performs), 39)
        self.assertEqual(names[performs[90][0]], 'Fireball')
        self.assertEqual((names[performs[27][0]], names[performs[29][0]]), ('Fleet Foot', 'Accelerator'))
        self.assertEqual(names[performs[32][0]], 'War Cry')
        self.assertNotIn(0, performs)                                         # healing has code of its own


class ExePatches(unittest.TestCase):
    def test_every_row_matches_the_program(self):
        """Each row of the sheet ExePatches names bytes that are in the unwrapped executable, replaces them by as many
        bytes, and a repointed constant holds the float the row states."""
        from exe_reader import Exe
        rows = exe_patch.patches()
        self.assertTrue(rows)
        self.assertEqual(exe_patch.problems(Exe(), rows), [])
        self.assertEqual(len({p['va'] for p in rows}), len(rows))

    def test_the_patched_copy_differs_only_where_the_rows_say(self):
        from exe_reader import Exe
        exe = Exe()
        rows = exe_patch.patches('balance')
        after = exe_patch.patched(exe, rows)
        changed = [k for k in range(len(after)) if after[k] != exe.data[k]]
        allowed = {exe.offset(p['va']) + k for p in rows for k in range(len(p['new']))}
        self.assertTrue(set(changed) <= allowed)
        self.assertEqual(len(after), len(exe.data))

    def test_the_set_is_written_into_both_program_files_and_taken_back(self):
        """On copies of the two program files: the set goes into both, the vanilla copies are kept and stay vanilla,
        restore puts both back byte for byte, and a file changed outside the rows stops the install of both."""
        import shutil
        import tempfile
        from exe_reader import Exe, reading_path
        # inside the project: this machine refuses to open a program file copied to the temporary folder of Windows
        os.makedirs(os.path.join(_paths.PROJECT_DIR, 'build'), exist_ok=True)
        folder = tempfile.mkdtemp(prefix='dt22_exe_', dir=os.path.join(_paths.PROJECT_DIR, 'build'))
        try:
            vanilla = {'game file': exe_patch.VANILLA_COPY if os.path.exists(exe_patch.VANILLA_COPY) else exe_patch.GAME_EXE,
                       'unwrapped file': reading_path()}
            targets = []
            for label, source in vanilla.items():
                name = label.replace(' ', '_')
                shutil.copy2(source, os.path.join(folder, name + '.exe'))
                targets.append((label, os.path.join(folder, name + '.exe'), os.path.join(folder, 'kept', name + '.vanilla.exe')))
            rows = exe_patch.patches('balance')
            done = exe_patch.install('balance', targets)
            self.assertEqual([d[2] for d in done], [19, 19])
            for label, path, copy in targets:
                self.assertEqual(exe_patch.sha(copy), exe_patch.sha(vanilla[label]))
                self.assertEqual(exe_patch.problems(Exe(path), rows, expect='new'), [])
            self.assertEqual(exe_patch.install('balance', targets), done)              # a second install changes nothing
            self.assertEqual(set(exe_patch.installed_set(targets)['game file'].values()), {'patched'})
            self.assertEqual(exe_patch.restore(targets), ['game file', 'unwrapped file'])
            for label, path, _ in targets:
                self.assertEqual(exe_patch.sha(path), exe_patch.sha(vanilla[label]))
            with open(targets[1][1], 'r+b') as f:                                       # one byte nobody asked to move
                f.seek(0x1000)
                byte = f.read(1)
                f.seek(0x1000)
                f.write(bytes([byte[0] ^ 1]))
            with self.assertRaises(SystemExit):
                exe_patch.install('balance', targets)
            self.assertEqual(exe_patch.sha(targets[0][1]), exe_patch.sha(vanilla['game file']))
        finally:
            shutil.rmtree(folder, ignore_errors=True)


class Dolls(unittest.TestCase):
    def test_every_doll_has_its_hidden_action(self):
        """The code pairs each doll skill with action skills (0x484150); the game names them after the doll. The same
        function builds the arrows of Star Dust Arrow (0x484491), which have no doll effect."""
        dolls = doll_data.dolls()
        self.assertEqual(len(dolls), 7)
        self.assertEqual([d['skill'] for d in dolls if d['effect'] is None], [49])
        for doll in dolls:
            with self.subTest(doll=doll['name']):
                self.assertTrue(doll['actions'])
                for action in doll['actions']:
                    self.assertTrue(action['name'].startswith(doll['name']), action['name'])
                    self.assertIn('Action', action['name'])
                self.assertTrue(all(2 <= turns <= 9 for turns in doll['turns']))
        musiy = next(d for d in dolls if d['name'] == 'Musiy')
        self.assertEqual(sorted(a['attribute'] for a in musiy['actions']), ['Earth', 'Fire', 'Lightning', 'Water', 'Wind'])

    def test_the_action_holds_the_power_of_the_doll(self):
        spartan = next(d for d in doll_data.dolls() if d['name'] == 'Spartan')
        power = [values for effect, _, values in spartan['actions'][0]['effects'] if effect == 26]
        self.assertEqual(len(power), 1)
        self.assertEqual(len(power[0]), 10)
        self.assertTrue(all(b >= a for a, b in zip(power[0], power[0][1:])))


if __name__ == '__main__':
    unittest.main()

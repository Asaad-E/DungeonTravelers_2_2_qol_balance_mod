"""Phase 3 Python loader / progression fixes (docs/binary_spec/DIFF_REPORT.md), one test per bug, and the paired
vanilla-vs-variant tests of the Balance program patches that the Python side owns: X01..X08 (EXP factors by level
gap), X09..X12 (crown reset steps) and X15 (map steps per status turn).

    M05.09a / M05.09b   tools/item_effect_data.py   party-buff wrappers 35/36/39, MEAL_BUFFS_FALLBACK
    M10.09a             tools/floor_data.py         bossGroups (+0x38 / +0x40)
    M10.10a             tools/map_data.py           cells of kind 5
    M10.11a             tools/map_data.py           .adv.bin framing, no -256 battles
    M11.04b             tools/class_modifier_data.py  specialty_gain: yearning floor, enchantment 264, single precision
    M11.11a             gamedata/progression.py     int(f32(exp) * f32(factor))
"""
import inspect
import json
import math
import os
import struct
import sys
import unittest

import _paths

ROOT = _paths.PROJECT_DIR
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import class_modifier_data  # noqa: E402
import exe_patch  # noqa: E402
import floor_data  # noqa: E402
import item_effect_data  # noqa: E402
import map_data  # noqa: E402
from gamedata import progression  # noqa: E402


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def _exe_or_none():
    try:
        from exe_reader import Exe
        exe = Exe()
        return exe if exe and exe.data else None
    except (SystemExit, Exception):
        return None


def _script(*instructions):
    """Bytes of a framed .adv.bin: each instruction is (opcode, [argument]) where an int is a type-0 argument and
    a str is a type-0x0A string argument (u32 id 287 = bytes 1F 01 00 00, u16be string id, flag, text)."""
    out = bytearray()
    for opcode, args in instructions:
        out += bytes((opcode, len(args)))
        for a in args:
            if isinstance(a, int):
                out += b'\x00' + struct.pack('<i', a)
            else:
                out += b'\x0a' + struct.pack('<I', 0x11f + 0x1c0 - 0x1c0) + b'\xff\xff\xff' + a.encode() + b'\x00'
    return bytes(out)


# ------------------------------------------------------------------------------------------------ M05.09
class ItemEffectFixes(unittest.TestCase):
    WRAPPERS = {35: 226, 36: 227, 39: 195}

    def test_m05_09a_fallback_specs_hold_the_party_buff_wrappers(self):
        for kind, skill in self.WRAPPERS.items():
            self.assertEqual(item_effect_data.SKILL_ITEM_SPECS_FALLBACK[kind], (skill, 0, -1), kind)

    def test_m05_09a_skill_item_specs_without_a_program_fall_back_with_the_wrappers(self):
        class NoExe:
            data = None
        specs = item_effect_data.skill_item_specs(NoExe())
        for kind, skill in self.WRAPPERS.items():
            self.assertEqual(specs[kind], (skill, 0, -1))
        self.assertEqual(len(specs), 41 + 3)             # the 41 direct thunks and the three wrappers

    def test_m05_09a_skill_item_specs_read_from_the_program(self):
        exe = _exe_or_none()
        if exe is None:
            self.skipTest('no program file')
        specs = item_effect_data.skill_item_specs(exe)
        for kind, skill in self.WRAPPERS.items():
            self.assertEqual(specs[kind], (skill, 0, -1), kind)
        # the table read from the program and the fallback agree for every kind
        self.assertEqual(specs, item_effect_data.SKILL_ITEM_SPECS_FALLBACK)

    def test_m05_09b_meal_buffs_fallback_holds_78_79_80(self):
        table = item_effect_data.MEAL_BUFFS_FALLBACK
        self.assertEqual(table[78], (184, 5))
        self.assertEqual(table[79], (185, 5))
        self.assertEqual(table[80], (186, 5))

    def test_m05_09b_meal_buffs_fallback_wrappers_and_all_fourteen_meals(self):
        table = item_effect_data.MEAL_BUFFS_FALLBACK
        self.assertEqual((table[35], table[36], table[39]), ((226, 5), (227, 5), (195, 5)))
        self.assertEqual(sorted(k for k in table if k >= 73), list(range(73, 87)))
        self.assertEqual([table[k][0] for k in range(73, 79)], [179, 180, 181, 182, 183, 184])

    def test_m05_09b_fallback_equals_the_table_read_from_the_program(self):
        exe = _exe_or_none()
        if exe is None:
            self.skipTest('no program file')
        self.assertEqual(item_effect_data.meal_buffs(exe), item_effect_data.MEAL_BUFFS_FALLBACK)


# ------------------------------------------------------------------------------------------------ M10.09
class BossGroups(unittest.TestCase):
    def test_m10_09a_existing_signatures_are_unchanged(self):
        self.assertEqual(list(inspect.signature(floor_data.floors).parameters), ['path'])
        self.assertEqual(list(inspect.signature(floor_data.fixed_battles).parameters), ['path'])
        self.assertEqual((floor_data.BOSS_COUNT, floor_data.BOSS_POINTER), (0x38, 0x40))

    def test_m10_09a_read_bosses_from_a_synthetic_floor(self):
        record = floor_data.RECORD
        blob = bytearray(0x100 + 2 * record)
        struct.pack_into('<i', blob, floor_data.BOSS_COUNT, 2)
        struct.pack_into('<Q', blob, floor_data.BOSS_POINTER, 0x100)
        for k, (number, enemy, flag) in enumerate(((61, 332, 1), (62, 333, 0))):
            base = 0x100 + k * record
            struct.pack_into('<i', blob, base, number)
            struct.pack_into(f'<{floor_data.ENEMY_SLOTS}i', blob, base + 4, enemy, *([-1] * (floor_data.ENEMY_SLOTS - 1)))
            blob[base + 0x34] = 1
            struct.pack_into('<i', blob, base + floor_data.BOSS_FLAG, flag)
        found = floor_data.read_bosses(bytes(blob))
        self.assertEqual([(b['number'], b['group'], b['boss'], b['enemies']) for b in found],
                         [(61, 60, True, [(332, True)]), (62, 61, False, [(333, True)])])

    def test_m10_09a_vanilla_has_182_boss_groups_on_101_floors(self):
        bosses = floor_data.boss_groups()
        self.assertEqual(len(bosses), 182)
        self.assertEqual(len({b['floor'] for b in bosses}), 101)
        self.assertTrue(all(b['boss'] and b['enemies'] and b['group'] >= 60 for b in bosses))

    def test_m10_09a_boss_groups_do_not_change_fixed_battles(self):
        self.assertEqual(len(floor_data.fixed_battles()), 196)
        self.assertTrue(floor_data.floors())

    def test_m10_09a_group_tiers(self):
        self.assertEqual([floor_data.group_tier(g) for g in (0, 39, 40, 59, 60, 0x7fffffff, 0x80000005)],
                         ['normal', 'normal', 'fixed', 'fixed', 'boss', 'boss', 'direct'])


# ------------------------------------------------------------------------------------------------ M10.10 / M10.11
class MapFixes(unittest.TestCase):
    def test_m10_10a_kind_5_cells_are_listed_on_request(self):
        cells = map_data.battle_cells(include_fixed_tiles=True)
        tiles = [c for k, v in cells.items() if k[1] == map_data.FIXED_TILE for c in v]
        self.assertEqual(len(tiles), 927)
        self.assertTrue(all(c['kind'] == 5 and c['script'] is None for c in tiles))

    def test_m10_10a_kind_5_cells_match_the_maps(self):
        counted = sum(1 for m in map_data.maps().values() for c in m['cells'] if c['kind'] == map_data.FIXED_TILE_CELL)
        self.assertEqual(counted, 927)

    def test_m10_10a_default_callers_see_only_event_cells(self):
        default = map_data.battle_cells()
        self.assertFalse([k for k in default if k[1] == map_data.FIXED_TILE])
        full = map_data.battle_cells(include_fixed_tiles=True)
        self.assertEqual({k: v for k, v in full.items() if k[1] != map_data.FIXED_TILE}, default)
        self.assertEqual(list(inspect.signature(map_data.battle_cells).parameters), ['path', 'include_fixed_tiles'])

    def test_m10_11a_string_id_that_looks_like_the_command_is_not_a_battle(self):
        # id 0x11f -> bytes 1F 01 00 00, then FF FF FF: the old byte search read -256 here
        script = _script((0x72, ['x']), (0x1F, [41]))
        self.assertIn(b'\x1f\x01\x00', script[:12])
        self.assertEqual(map_data.battles_of_script(script), [41])

    def test_m10_11a_group_argument_below_one_is_not_a_battle(self):
        self.assertEqual(map_data.battles_of_script(_script((0x1F, [0]), (0x1F, [-256]), (0x1F, [43]))), [43])

    def test_m10_11a_several_battles_in_order(self):
        self.assertEqual(map_data.battles_of_script(_script((0x1F, [42]), (0x72, ['a', 3]), (0x1F, [41]))), [42, 41])

    def test_m10_11a_instruction_framing(self):
        self.assertEqual(map_data.instructions_of_script(_script((0x1F, [41]), (0x59, []))), [(0x1F, [41]), (0x59, [])])
        with self.assertRaises(ValueError):
            map_data.instructions_of_script(b'\x1f\x03\x00\x01')

    def test_m10_11a_vanilla_scripts_frame_and_hold_no_bogus_battle(self):
        import zipfile
        numbers = []
        with zipfile.ZipFile(map_data.MAP_ZIP) as archive:
            for name in archive.namelist():
                if name.endswith('.adv.bin'):
                    blob = archive.read(name)
                    map_data.instructions_of_script(blob)            # frames to the last byte
                    numbers += map_data.battles_of_script(blob)
        self.assertEqual(len(numbers), 198)
        self.assertEqual(min(numbers), 41)
        self.assertFalse([n for n in numbers if n < 1])
        self.assertFalse([k for k in map_data.battle_cells() if k[1] < 1])


# ------------------------------------------------------------------------------------------------ M11.04
class SpecialtyGain(unittest.TestCase):
    gain = staticmethod(class_modifier_data.specialty_gain)

    def test_m11_04b_defaults_keep_the_old_results(self):
        self.assertEqual(self.gain(200, 100, 0.05), 15)
        self.assertEqual(self.gain(200, 0, 0.05), 0)                                  # the piece must give the stat
        self.assertEqual(self.gain(200, 100, 0.05, yearning=6), 33)
        self.assertEqual(list(inspect.signature(self.gain).parameters),
                         ['character_stat', 'piece_stat', 'modifier', 'yearning', 'enchant_264'])

    def test_m11_04b_yearning_is_a_floor(self):
        self.assertEqual(self.gain(10, 1, 0.01, yearning=5), 5)                       # int(11 * 0.06) = 0, floor 5
        self.assertEqual(self.gain(10, 1, 0.01, yearning=3.7), 3)                     # int(yearning)
        self.assertEqual(self.gain(10, 1, 0.01), 0)
        self.assertEqual(self.gain(10, 0, 0.01, yearning=5), 0)                       # no stat on the piece, no floor

    def test_m11_04b_enchantment_264_adds_two_percent(self):
        self.assertEqual(self.gain(100, 100, 0.01, enchant_264=False), 2)
        self.assertEqual(self.gain(100, 100, 0.01, enchant_264=True), 6)

    def test_m11_04b_single_precision_not_double(self):
        # DIFF_REPORT M11.04a: base 0.01, yearning 2, enchantment 264, combined 100 -> binary 4 (double precision gives 5)
        self.assertEqual(self.gain(50, 50, 0.01, yearning=2, enchant_264=True), 4)
        self.assertEqual(int(100 * (0.01 + 0.01 * 2 + 0.02)), 5)
        rate = f32(f32(0.01) + f32(f32(2) * f32(0.01)))
        self.assertEqual(self.gain(50, 50, 0.01, yearning=2), max(2, int(f32(100 * rate))))


# ------------------------------------------------------------------------------------------------ M11.11 / X01..X08
VANILLA_GAP = ((10, None, 0.85, 0.85), (5, 9, 0.90, 0.90), (0, 4, 1.00, 1.00), (-4, -1, 1.00, 1.15),
               (-9, -5, 1.10, 1.30), (-19, -10, 1.25, 1.50), (None, -20, 1.25, 1.75))


def _balance_rows():
    return {p['id']: p for p in exe_patch.patches('balance')}


def _variant_gap(rows):
    f = lambda i: rows[i]['float_after']                                              # noqa: E731
    return ((10, None, 0.85, 0.85), (5, 9, 0.90, 0.90), (0, 4, 1.00, 1.00), (-4, -1, f('X01'), f('X06')),
            (-9, -5, f('X02'), f('X07')), (-19, -10, f('X03'), f('X08')), (None, -20, f('X04'), f('X04')))


class ExpLevelGap(unittest.TestCase):
    def test_m11_11a_f32_product_matches_the_program(self):
        # DIFF_REPORT M11.11a: enemy 0 exp 90 * 1.3f -> 116 (double precision 117); enemy 5 exp 440 * 1.15f -> 506 (505)
        self.assertEqual(progression.gap_exp(90, 1.3), 116)
        self.assertEqual(int(90 * 1.3), 117)
        self.assertEqual(progression.gap_exp(440, 1.15), 506)
        self.assertEqual(int(440 * 1.15), 505)

    def test_m11_11a_151_enemy_factor_pairs_differ_from_double_precision(self):
        import enemy_data
        factors = {f for band in progression.LEVEL_GAP for f in band[2:]}
        differing = sum(1 for e in enemy_data.enemies() for f in factors if int(e['exp'] * f) != progression.gap_exp(e['exp'], f))
        self.assertEqual(differing, 151)

    def test_m11_11a_battle_exp_banks_the_f32_products(self):
        # member 10 levels below an enemy of level 11 (gap -1 .. -4 band, no piece: 1.00) and above (1.15 with the piece)
        self.assertEqual(progression.battle_exp(5, [(6, 440)], 1, more_from_higher=True), 506.0)
        self.assertEqual(progression.battle_exp(5, [(6, 440)], 1, more_from_higher=False), 440.0)
        self.assertEqual(progression.battle_exp(5, [(10, 90), (6, 440)], 2, more_from_higher=True), (116 + 506) / 2)

    def test_m11_11a_exact_factors_are_unchanged_integers(self):
        for exp in (0, 1, 7, 100, 1000, 65535):
            self.assertEqual(progression.gap_exp(exp, 1.0), exp)
            self.assertEqual(progression.gap_exp(exp, 2.0), 2 * exp)

    def test_x01_x08_vanilla_table_is_the_float_before_of_the_patch_rows(self):
        rows = _balance_rows()
        before = {'X01': 1.0, 'X06': 1.15, 'X02': 1.1, 'X07': 1.3, 'X03': 1.25, 'X08': 1.5, 'X04': 1.75}
        for ident, value in before.items():
            self.assertAlmostEqual(rows[ident]['float_before'], value, places=6, msg=ident)
        self.assertEqual(progression.LEVEL_GAP, VANILLA_GAP)

    def test_x01_x08_variant_values_are_the_patch_rows(self):
        rows = _balance_rows()
        self.assertEqual({i: rows[i]['float_after'] for i in ('X01', 'X02', 'X03', 'X04', 'X06', 'X07', 'X08')},
                         {'X01': 1.15, 'X02': 3, 'X03': 5, 'X04': 10, 'X06': 1.5, 'X07': 4, 'X08': 6})
        # X05 makes the "no piece" jump of the last band land on its own instruction: the band is 10 with or without
        self.assertEqual((rows['X05']['old'], rows['X05']['new']), (b'\x1e', b'\x00'))

    def test_x01_x08_constants_exist_in_the_vanilla_program(self):
        exe = _exe_or_none()
        if exe is None:
            self.skipTest('no program file')
        for ident, row in _balance_rows().items():
            if ident in ('X01', 'X02', 'X03', 'X04', 'X06', 'X07', 'X08'):
                old, new = (struct.unpack('<I', row[k])[0] for k in ('old', 'new'))
                self.assertAlmostEqual(exe.f32(old), row['float_before'], places=5, msg=ident)
                self.assertAlmostEqual(exe.f32(new), row['float_after'], places=5, msg=ident)

    def test_x01_x08_paired_factor_by_band(self):
        variant = _variant_gap(_balance_rows())
        cases = [  # (member level, enemy level, vanilla plain, vanilla piece, variant plain, variant piece)
            (30, 10, 0.85, 0.85, 0.85, 0.85), (15, 10, 0.90, 0.90, 0.90, 0.90), (10, 10, 1.0, 1.0, 1.0, 1.0),
            (9, 10, 1.0, 1.15, 1.15, 1.5),                    # X01 / X06
            (5, 10, 1.1, 1.3, 3.0, 4.0),                      # X02 / X07
            (-9 + 20, 20, 1.25, 1.5, 5.0, 6.0) if False else (1, 11, 1.25, 1.5, 5.0, 6.0),     # X03 / X08
            (1, 21, 1.25, 1.75, 10.0, 10.0),                  # X04 / X05
        ]
        for member, enemy, v_plain, v_piece, b_plain, b_piece in cases:
            for more, vanilla_value, variant_value in ((False, v_plain, b_plain), (True, v_piece, b_piece)):
                self.assertEqual(progression.level_gap_factor(member, enemy, more, progression.LEVEL_GAP), vanilla_value,
                                 (member, enemy, more))
                self.assertEqual(progression.level_gap_factor(member, enemy, more, variant), variant_value,
                                 (member, enemy, more))

    def test_x01_x08_paired_banked_exp_vanilla_vs_variant(self):
        variant = _variant_gap(_balance_rows())
        # a level 1 member against a level 3 enemy of 100 EXP (gap -2): vanilla 1.00, variant 1.15; with the piece 1.15 / 1.5
        self.assertEqual(progression.battle_exp(1, [(3, 100)], 1, gap_table=progression.LEVEL_GAP), 100)
        self.assertEqual(progression.battle_exp(1, [(3, 100)], 1, gap_table=variant), progression.gap_exp(100, 1.15))
        self.assertEqual(progression.battle_exp(1, [(3, 100)], 1, more_from_higher=True, gap_table=progression.LEVEL_GAP),
                         progression.gap_exp(100, 1.15))
        self.assertEqual(progression.battle_exp(1, [(3, 100)], 1, more_from_higher=True, gap_table=variant), 150)
        # 20 or more below: vanilla 1.25 plain / 1.75 with the piece, variant 10 either way (X04 + X05)
        self.assertEqual(progression.battle_exp(1, [(40, 8)], 1, gap_table=progression.LEVEL_GAP), 10)
        self.assertEqual(progression.battle_exp(1, [(40, 8)], 1, more_from_higher=True, gap_table=progression.LEVEL_GAP), 14)
        self.assertEqual(progression.battle_exp(1, [(40, 8)], 1, gap_table=variant), 80)
        self.assertEqual(progression.battle_exp(1, [(40, 8)], 1, more_from_higher=True, gap_table=variant), 80)

    def test_x01_x08_variant_never_lowers_a_vanilla_factor(self):
        variant = _variant_gap(_balance_rows())
        for (_, _, p1, w1), (_, _, p2, w2) in zip(progression.LEVEL_GAP, variant):
            self.assertGreaterEqual(p2, p1)
            self.assertGreaterEqual(w2, w1)

    def test_x01_x08_default_arguments_stay_vanilla(self):
        self.assertIs(inspect.signature(progression.level_gap_factor).parameters['gap_table'].default, progression.LEVEL_GAP)
        self.assertEqual(progression.level_gap_factor(1, 3), 1.0)


# ------------------------------------------------------------------------------------------------ X09..X12
class CrownResetSteps(unittest.TestCase):
    def _steps(self, key):
        rows = _balance_rows()
        levels = {'X09': 98, 'X10': 89, 'X11': 79, 'X12': 69}
        steps = dict(zip((98, 89, 79, 69, 59), (5, 4, 3, 2, 1)))
        for ident, level in levels.items():
            steps[level] = rows[ident][key][0]
        return tuple(sorted(steps.items(), reverse=True))

    def test_x09_x12_vanilla_steps_are_the_old_bytes(self):
        self.assertEqual(self._steps('old'), progression.RESET_STEPS)
        self.assertEqual(progression.RESET_MAX, 50)

    def test_x09_x12_variant_steps_are_the_new_bytes(self):
        self.assertEqual(self._steps('new'), ((98, 6), (89, 5), (79, 4), (69, 3), (59, 1)))

    def test_x09_x12_old_bytes_lie_in_the_vanilla_program(self):
        exe = _exe_or_none()
        if exe is None:
            self.skipTest('no program file')
        for ident in ('X09', 'X10', 'X11', 'X12'):
            row = _balance_rows()[ident]
            self.assertEqual(exe.read(row['va'], 1), row['old'], ident)

    def test_x09_x12_paired_bonus_per_dropped_levels(self):
        variant = self._steps('new')
        # (levels dropped, vanilla points, variant points)
        for dropped, vanilla, balance in ((98, 5, 6), (97, 4, 5), (89, 4, 5), (88, 3, 4), (79, 3, 4), (78, 2, 3),
                                          (69, 2, 3), (68, 1, 1), (59, 1, 1), (58, 0, 0)):
            self.assertEqual(progression.reset_bonus(1 + dropped), vanilla, dropped)
            self.assertEqual(progression.reset_bonus(1 + dropped, steps=variant), balance, dropped)

    def test_x09_x12_paired_resets_to_the_crown(self):
        variant = self._steps('new')
        self.assertEqual(progression.resets_to_crown(99), 10)                          # 50 / 5
        self.assertEqual(progression.resets_to_crown(99, variant), 9)                  # ceil(50 / 6)
        self.assertEqual(progression.resets_to_crown(80), 17)                          # 50 / 3 -> 17
        self.assertEqual(progression.resets_to_crown(80, variant), 13)                 # 50 / 4 -> 13
        self.assertEqual(progression.resets_to_crown(60), progression.resets_to_crown(60, variant))     # 59..68 stay 1 point
        self.assertIsNone(progression.resets_to_crown(50))

    def test_x09_x12_cap_holds_for_both_rules(self):
        variant = self._steps('new')
        self.assertEqual(progression.reset_bonus(99, 1, 48), 50)
        self.assertEqual(progression.reset_bonus(99, 1, 48, steps=variant), 50)


# ------------------------------------------------------------------------------------------------ X15
class MapStepsPerStatusTurn(unittest.TestCase):
    def test_x15_vanilla_is_the_old_byte_and_the_design_row(self):
        row = _balance_rows()['X15']
        self.assertEqual((row['old'], row['new']), (b'\x05', b'\x0c'))
        with open(os.path.join(_paths.TABLES_DIR, 'measure_config.json'), encoding='utf-8') as f:
            design = json.load(f)['design_rows']
        self.assertEqual(design['steps_a_turn'], row['old'][0])                       # the measure reads the vanilla count

    def test_x15_old_byte_lies_in_the_vanilla_program(self):
        exe = _exe_or_none()
        if exe is None:
            self.skipTest('no program file')
        row = _balance_rows()['X15']
        self.assertEqual(exe.read(row['va'], 1), row['old'])

    def test_x15_variant_is_twelve(self):
        self.assertEqual(_balance_rows()['X15']['new'][0], 12)

    def test_x15_paired_steps_of_a_meal(self):
        vanilla, variant = 5, _balance_rows()['X15']['new'][0]
        # the meals last 3 to 10 turns (skill table): 15 to 50 steps in vanilla, 36 to 120 in the Balance variant
        self.assertEqual((3 * vanilla, 10 * vanilla), (15, 50))
        self.assertEqual((3 * variant, 10 * variant), (36, 120))

    def test_x15_paired_turns_per_walk(self):
        vanilla, variant = 5, _balance_rows()['X15']['new'][0]
        for steps in (0, 4, 5, 11, 12, 60, 100):
            self.assertEqual(steps // vanilla - steps // variant >= 0, True)
            self.assertEqual(steps // variant, math.floor(steps / 12))
        self.assertEqual(60 // vanilla, 12)
        self.assertEqual(60 // variant, 5)

    def test_x15_export_row_is_read_from_the_config(self):
        import engine_export
        self.assertEqual(engine_export.measure_config()['design_rows']['steps_a_turn'], 5)


if __name__ == '__main__':
    unittest.main()

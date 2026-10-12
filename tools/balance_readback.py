"""
What the built packs of the Balance variant hold, read back with the readers of the project, set against what the
simulator plays. Step 2 of "build_variant.py balance".

    python tools/balance_readback.py

tools/balance_values.py checks its own writes byte by byte; this is the other half, by another road: the folder
build/balance/base/ is extracted like the originals (tools/extract_vanilla.py, into
build/balance/tables/source_of_truth.xlsx) and loaded with the loaders of sim/data.py; the enemies are read by
tools/enemy_data.py. Every skill, enemy attack, piece of equipment, sealbook, enchantment, level and enemy must then
equal the variant of the simulator (sim/variant.py over the vanilla data): the game files and the model say the same
thing, or the build stops. The workbook it leaves is the source the texts of the variant are generated from.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl                                          # noqa: E402
import enemy_ai                                          # noqa: E402
import enemy_data                                        # noqa: E402
import npc_data                                          # noqa: E402
import extract_vanilla                                   # noqa: E402
from sim import data as sim_data                         # noqa: E402
from sim.variant import balance_data                     # noqa: E402

BALANCE_DIR = os.path.join(BASE_DIR, 'build', 'balance')
BUILT_DIR = os.path.join(BALANCE_DIR, 'base')
TABLES_DIR = os.path.join(BALANCE_DIR, 'tables')
SOURCE = os.path.join(TABLES_DIR, 'source_of_truth.xlsx')
TOLERANCE = 1e-4                           # the workbooks hold floats rounded to four decimals
SKILL_FIELDS = ('levels', 'target', 'attr', 'group', 'weapons', 'tp', 'sp', 'speed', 'cast', 'accuracy', 'turns')
ATTACK_FIELDS = ('target', 'attr', 'chant_speed', 'accuracy', 'power', 'turns', 'speed')
ENEMY_FIELDS = tuple(k for k, _ in enemy_data.STATS) + tuple('res_' + r for r in enemy_data.RESISTANCES) + \
    ('flags', 'swing', 'weight', 'race', 'attacks', 'passives', 'raw_68', 'ai')
# raw_f0 is left out: the variant of the simulator changes the list 'passives' and keeps the raw words as read
PIECE_FIELDS = ('stats', 'rate', 'classes', 'swing', 'rank', 'type', 'enchants')


def extract(built_dir=BUILT_DIR, output=SOURCE):
    """The workbook tools/extract_vanilla.py writes, taken from the built folder. Returns its structural problems."""
    saved = extract_vanilla.BACKUP_DIR, extract_vanilla.OUTPUT_PATH
    os.makedirs(os.path.dirname(output), exist_ok=True)
    extract_vanilla.BACKUP_DIR, extract_vanilla.OUTPUT_PATH = built_dir, output
    problems = []
    try:
        extract_vanilla.write_workbook(problems)
    finally:
        extract_vanilla.BACKUP_DIR, extract_vanilla.OUTPUT_PATH = saved
    return problems


def extract_final(built_dir, output_dir, output):
    """The same workbook from the packs the build delivers: each pack from output_dir (the packs with their texts)
    when it is there, else from built_dir. For the last check of the build, on what would be installed."""
    saved = extract_vanilla.load, extract_vanilla.OUTPUT_PATH
    from pck_handler import PckArchive

    def load(pck_name):
        delivered = os.path.join(output_dir, pck_name)
        return PckArchive(delivered if os.path.exists(delivered) else os.path.join(built_dir, pck_name)).files

    extract_vanilla.load, extract_vanilla.OUTPUT_PATH = load, output
    problems = []
    try:
        extract_vanilla.write_workbook(problems)
    finally:
        extract_vanilla.load, extract_vanilla.OUTPUT_PATH = saved
    return problems


def built_data(built_dir=BUILT_DIR, source=SOURCE):
    """The tables a change can touch, loaded from the built folder as sim/data.py loads the originals."""
    data = sim_data.GameData()
    wb = openpyxl.load_workbook(source, read_only=True)
    sim_data._load_skills(wb, data)
    sim_data._load_attacks(wb, data)
    sim_data._load_equipment(wb, data)
    sim_data._load_misc(wb, data)
    for enemy in enemy_data.enemies(os.path.join(built_dir, 'Enemy', 'Enemy.pck')):
        data.enemies[enemy['id']] = enemy
    data.npcs = npc_data.npcs(os.path.join(built_dir, 'NPC', 'NPC.pck'))
    return data


def close(a, b):
    """Equal, floats within the rounding of the workbooks; lists and dicts member by member."""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(close(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k]) for k in a)
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(float(a) - float(b)) <= TOLERANCE
        except (TypeError, ValueError):
            return False
    return a == b


def compare(built, variant):
    """[difference] between the built tables and the variant of the simulator; counts of what was compared."""
    out, counts = [], {}

    def table(name, mine, theirs, fields, get):
        counts[name] = len(theirs)
        if set(mine) != set(theirs):
            out.append(f'{name}: {len(set(mine) ^ set(theirs))} record(s) are not on both sides')
        for key in theirs:
            if key not in mine:
                continue
            for field in fields:
                a, b = get(mine[key], field), get(theirs[key], field)
                if not close(a, b):
                    out.append(f'{name} {key} {field}: the build holds {a}, the simulator plays {b}')

    attr = lambda record, field: getattr(record, field)              # noqa: E731
    item = lambda record, field: record.get(field)                   # noqa: E731
    table('skills', built.skills, variant.skills, SKILL_FIELDS, attr)
    for key, skill in variant.skills.items():                        # effects: (id, kind, values by level)
        mine = built.skills.get(key)
        if mine is not None and not close([list(e) for e in mine.effects], [list(e) for e in skill.effects]):
            out.append(f'skills {key} effects: the build holds {mine.effects}, the simulator plays {skill.effects}')
    table('enemy attacks', built.attacks, variant.attacks, ATTACK_FIELDS, attr)
    for key, attack in variant.attacks.items():
        mine = built.attacks.get(key)
        if mine is not None and not close([list(e) for e in mine.effects], [list(e) for e in attack.effects]):
            out.append(f'enemy attacks {key} effects: the build holds {mine.effects}, the simulator plays {attack.effects}')
    table('equipment', built.equipment, variant.equipment, PIECE_FIELDS, item)
    table('sealbooks', built.sealbooks, variant.sealbooks, ('grand', 'level', 'enchants'), item)
    table('items', built.items, variant.items, ('effects',), item)
    table('unique skills', built.unique, variant.unique, ('effect', 'values'), item)
    table('guest allies', {n['id']: n for n in built.npcs}, {n['id']: n for n in variant.npcs},
          ('level', 'hp', 'attacks') + npc_data.STATS, item)
    counts['enchantments that stack'] = len(variant.enchant_stacks)
    if built.enchant_stacks != variant.enchant_stacks:
        out.append(f'enchantments that stack: {sorted(built.enchant_stacks ^ variant.enchant_stacks)} differ')
    counts['levels'] = len(variant.sp_curve)
    for curve in ('sp_curve', 'exp_curve'):
        if getattr(built, curve) != getattr(variant, curve):
            levels = [lv for lv in getattr(variant, curve) if getattr(built, curve).get(lv) != getattr(variant, curve)[lv]]
            out.append(f'{curve}: levels {levels} differ')
    # an enemy: its record as read, and its script as the simulator plays it (a row on the weights of a set changes
    # the script of the variant, so the bytes are decoded on both sides)
    fields = [f for f in ENEMY_FIELDS if f != 'ai']
    table('enemies', built.enemies, variant.enemies, fields, item)
    for key, enemy in variant.enemies.items():
        mine = built.enemies.get(key)
        if mine is None:
            continue
        try:
            script = enemy_ai.decode(mine['ai']) if mine['ai'] else None
        except ValueError:
            script = None
        theirs = enemy.get('script')
        a = {n: s['weights'] for n, s in script['sets'].items()} if script else None
        b = {n: s['weights'] for n, s in theirs['sets'].items()} if theirs else None
        if a != b:
            out.append(f'enemies {key} AI weights: the build holds {a}, the simulator plays {b}')
    return out, counts


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    problems = extract()
    for p in problems:
        print('  extraction:', p)
    variant = balance_data(sim_data.game_data())
    differences, counts = compare(built_data(), variant)
    for d in differences[:40]:
        print('  differs:', d)
    if problems or differences:
        print(f'[FAIL] {len(problems)} problem(s) of structure, {len(differences)} difference(s) with the simulator')
        sys.exit(1)
    print('[OK] the built packs hold what the simulator plays: ' + ', '.join(f'{n} {k}' for k, n in counts.items()))


if __name__ == '__main__':
    main()

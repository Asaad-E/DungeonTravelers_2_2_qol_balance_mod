"""One-off edit of 2026-10-12: the tools take the names of the game and the offsets of its records from
data_tables/game_profile.json and data_tables/record_layouts.json (tools/game_profile.py) in the place of constants
written in each of them. Kept as the record of what was changed; a second run stops at the first text it no longer
finds."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = chr(10)


def sub(path, pairs):
    full = os.path.join(ROOT, path)
    s = io.open(full, encoding='utf-8').read()
    for old, new in pairs:
        if s.count(old) != 1:
            raise SystemExit(f'{path}: {s.count(old)} matches of {old[:80]!r}')
        s = s.replace(old, new)
    io.open(full, 'w', encoding='utf-8', newline=NL).write(s)


# --- the names of the game ---------------------------------------------------------------------------------------
sub('tools/mod_config.py', [
    ("BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))" + NL,
     "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))" + NL +
     "from game_profile import PROFILE                          # noqa: E402" + NL + NL +
     "BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))" + NL),
    ("DEFAULT_GAME_DIR = os.path.join(BASE_DIR, 'DungeonTravelers2-2_EN')" + NL +
     "DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'AQUAPLUS', 'DUNGEON TRAVELERS 2-2_EN')" + NL,
     "DEFAULT_GAME_DIR = os.path.join(BASE_DIR, PROFILE['game_folder'])" + NL +
     "DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser('~'), *PROFILE['save_dir'])" + NL),
    ("    return os.path.join(game_dir(config), 'Data', 'ENG')", "    return os.path.join(game_dir(config), *PROFILE['data_dir'])"),
])
sub('tools/exe_reader.py', [
    ("EXE_PATH = os.path.join(mod_config.game_dir(), 'DT22_en_unwrapped.exe')",
     "EXE_NAME = __import__('game_profile').PROFILE['formula_exe']" + NL + "EXE_PATH = os.path.join(mod_config.game_dir(), EXE_NAME)"),
    ("VANILLA_PATH = os.path.join(COPY_DIR, 'DT22_en_unwrapped.vanilla.exe')",
     "VANILLA_PATH = os.path.join(COPY_DIR, os.path.splitext(EXE_NAME)[0] + '.vanilla.exe')"),
])
sub('tools/install_variant.py', [
    ("GAME_SUBDIRS = ('Parameter', 'Script')" + NL, "from game_profile import PROFILE        # noqa: E402" + NL +
     "GAME_SUBDIRS = tuple(PROFILE['text_subdirs'])" + NL),
    ("VALUE_SUBDIRS = ('Enemy', 'NPC')", "VALUE_SUBDIRS = tuple(PROFILE['value_subdirs'])"),
])
sub('tools/package_variant.py', [
    ("MOD_DIR = 'DT22_Mod'" + NL,
     "from game_profile import PROFILE                          # noqa: E402" + NL +
     "MOD_DIR = PROFILE['mod_folder']" + NL + "PREFIX = PROFILE['package_prefix']" + NL +
     "UNINSTALL = f'Uninstall_{MOD_DIR}.bat'" + NL),
    ("    path = os.path.join(out_dir, f'DT22_{variant}_{stamp}.zip')", "    path = os.path.join(out_dir, f'{PREFIX}_{variant}_{stamp}.zip')"),
    ("        z.writestr('Uninstall_DT22_Mod.bat', LAUNCHER.format(args='uninstall'))",
     "        z.writestr(UNINSTALL, LAUNCHER.format(args='uninstall'))"),
])
sub('tests/test_qol_items_and_install.py', [
    ("                self.assertEqual(names, {'Install_QoL.bat', 'Uninstall_DT22_Mod.bat', 'DT22_Mod/mod_patch.ps1'," + NL +
     "                                         'DT22_Mod/README.txt', 'DT22_Mod/qol.txt', 'DT22_Mod/qol.ops', 'DT22_Mod/qol.dat'})" + NL +
     "                ops, blob = z.read('DT22_Mod/qol.ops'), z.read('DT22_Mod/qol.dat')" + NL +
     "                lines = [line.split('|') for line in z.read('DT22_Mod/qol.txt').decode('utf-8').splitlines()]" + NL,
     "                mod = package_variant.MOD_DIR" + NL +
     "                self.assertEqual(names, {'Install_QoL.bat', package_variant.UNINSTALL, f'{mod}/mod_patch.ps1'," + NL +
     "                                         f'{mod}/README.txt', f'{mod}/qol.txt', f'{mod}/qol.ops', f'{mod}/qol.dat'})" + NL +
     "                ops, blob = z.read(f'{mod}/qol.ops'), z.read(f'{mod}/qol.dat')" + NL +
     "                lines = [line.split('|') for line in z.read(f'{mod}/qol.txt').decode('utf-8').splitlines()]" + NL),
])
sub('installer/mod_patch.ps1', [
    ("#   mod_patch.ps1 install <variant>    checks every file, keeps a copy of each in DT22_Mod\\backup, then changes it" + NL +
     "#   mod_patch.ps1 uninstall            puts every file back from DT22_Mod\\backup" + NL,
     "#   mod_patch.ps1 install <variant>    checks every file, keeps a copy of each in the folder backup beside this" + NL +
     "#                                      script, then changes it" + NL +
     "#   mod_patch.ps1 uninstall            puts every file back from that folder" + NL),
    ("Write-Host 'A copy of every original is in DT22_Mod\\backup. To take the mod out, run the Uninstall .bat.'",
     "Write-Host \"A copy of every original is in $(Split-Path -Leaf $modDir)\\backup. To take the mod out, run the Uninstall .bat.\""),
])
for tool in ('tools/floor_data.py', 'tools/map_data.py'):
    sub(tool, [("GAME_DUNGEON_DIR = os.path.join(mod_config.data_dir(), 'Dungeon')",
                "GAME_DUNGEON_DIR = os.path.join(mod_config.data_dir(), __import__('game_profile').PROFILE['dungeon_subdir'])")])

# --- the layouts of the records ------------------------------------------------------------------------------------
a = io.open(os.path.join(ROOT, 'tools/extract_vanilla.py'), encoding='utf-8').read()
start = a.index('SKILL_LAYOUTS = {')
end = a.index(NL + '}' + NL, start) + 3
io.open(os.path.join(ROOT, 'tools/extract_vanilla.py'), 'w', encoding='utf-8', newline=NL).write(
    a[:start] + "# data_tables/record_layouts.json, record 'skills' (tools/game_profile.py)" + NL +
    "SKILL_LAYOUTS = {category: dict(fields, weapon=tuple(fields['weapon'])) if 'weapon' in fields else dict(fields)" + NL +
    "                 for category, fields in layout('skills').items() if isinstance(fields, dict)}" + NL + a[end:])
sub('tools/extract_vanilla.py', [
    ("LEVELS = 10" + NL + "SLOT_SIZE = 0x30  # effect slot: id (4) + 10 values (40) + tail (4)" + NL,
     "from game_profile import layout                           # noqa: E402" + NL +
     "LEVELS = layout('skills')['levels']" + NL +
     "SLOT_SIZE = layout('skills')['slot_size']  # effect slot: id (4) + 10 values (40) + tail (4)" + NL),
])
sub('tools/enemy_data.py', [
    ("STATS = (('level', 0x14), ('hp', 0x18), ('atk', 0x1C), ('def', 0x20), ('int', 0x24), ('res', 0x28)," + NL +
     "         ('dex', 0x2C), ('agi', 0x30), ('exp', 0x34), ('gold', 0x38))" + NL,
     "from game_profile import layout                           # noqa: E402" + NL +
     "_RECORD = layout('EnemyStatusData')                       # data_tables/record_layouts.json" + NL +
     "STATS = tuple(_RECORD['stats'].items())" + NL),
    ("RESIST_OFFSET = 0x48" + NL + "ATTACK_COUNT, ATTACK_IDS, ATTACK_SLOTS = 0xAC, 0xB0, 16" + NL,
     "RESIST_OFFSET = _RECORD['resistances']" + NL +
     "ATTACK_COUNT, ATTACK_IDS, ATTACK_SLOTS = _RECORD['attack_count'], _RECORD['attack_ids'], _RECORD['attack_slots']" + NL),
])
sub('tools/npc_data.py', [
    ("ATTACK_COUNT, ATTACK_IDS, ATTACK_SLOTS = 0x38, 0x3C, 11" + NL,
     "from game_profile import layout                           # noqa: E402" + NL +
     "RECORD = layout('NPCData')                                # data_tables/record_layouts.json" + NL +
     "ATTACK_COUNT, ATTACK_IDS, ATTACK_SLOTS = RECORD['attack_count'], RECORD['attack_ids'], RECORD['attack_slots']" + NL),
    ("    name_at = struct.unpack_from('<Q', b, 0x08)[0]", "    name_at = struct.unpack_from('<Q', b, RECORD['name_pointer'])[0]"),
    ("    npc = {'id': i(0x00), 'character': i(0x10), 'level': i(0x18), 'raw_1c': i(0x1C),",
     "    npc = {'id': i(RECORD['id']), 'character': i(RECORD['character']), 'level': i(RECORD['level']), 'raw_1c': i(RECORD['rank']),"),
    ("           'kind': i(0x94), 'extra_attack': i(0x98) if i(0x98) != -1 else None, 'hp': i(0xAC)}",
     "           'kind': i(RECORD['kind']), 'hp': i(RECORD['hp'])," + NL +
     "           'extra_attack': i(RECORD['extra_attack']) if i(RECORD['extra_attack']) != -1 else None}"),
    ("    npc.update(zip(STATS, struct.unpack_from('<6i', b, 0x20)))", "    npc.update(zip(STATS, struct.unpack_from('<6i', b, RECORD['stats'])))"),
])
sub('tools/summon_data.py', [
    ("    count = struct.unpack_from('<i', b, 0x3C)[0]" + NL +
     "    strings = [t.decode('utf-8', 'replace') for t in b[0x40 + 8 * 12:].split(b'\\x00') if t]",
     "    r = RECORD" + NL + "    i = lambda offset: struct.unpack_from('<i', b, offset)[0]" + NL +
     "    count = i(r['attack_count'])" + NL +
     "    strings = [t.decode('utf-8', 'replace') for t in b[r['attack_ids'] + 8 * r['attack_slots']:].split(b'\\x00') if t]"),
    ("    return {'id': struct.unpack_from('<i', b, 0x00)[0], 'character': struct.unpack_from('<i', b, 0x10)[0]," + NL +
     "            'family': struct.unpack_from('<i', b, 0x14)[0], 'enemy': struct.unpack_from('<i', b, 0x14)[0]," + NL +
     "            'level': struct.unpack_from('<i', b, 0x18)[0]," + NL +
     "            'rank': struct.unpack_from('<i', b, 0x20)[0]," + NL +
     "            'factors': dict(zip(STATS, struct.unpack_from('<6f', b, 0x24)))," + NL +
     "            'attacks': [struct.unpack_from('<i', b, 0x40 + 8 * k)[0] for k in range(max(count, 0))]," + NL +
     "            'passive': struct.unpack_from('<i', b, 0x9C)[0] if struct.unpack_from('<i', b, 0x9C)[0] != -1 else None,",
     "    return {'id': i(r['id']), 'character': i(r['character'])," + NL +
     "            'family': i(r['enemy']), 'enemy': i(r['enemy'])," + NL +
     "            'level': i(r['level'])," + NL +
     "            'rank': i(r['rank'])," + NL +
     "            'factors': dict(zip(STATS, struct.unpack_from('<6f', b, r['factors'])))," + NL +
     "            'attacks': [i(r['attack_ids'] + 8 * k) for k in range(max(count, 0))]," + NL +
     "            'passive': i(r['passive']) if i(r['passive']) != -1 else None,"),
    ("def read_summon(blob):" + NL,
     "from game_profile import layout                           # noqa: E402" + NL +
     "RECORD = layout('SummonData')                             # data_tables/record_layouts.json" + NL + NL + NL +
     "def read_summon(blob):" + NL),
])
sub('tools/character_data.py', [
    ("PEP_OFFSET, PEP_COUNT = 0x3C, 21" + NL,
     "from game_profile import layout                           # noqa: E402" + NL +
     "PEP_OFFSET, PEP_COUNT = layout('PlayerStatusData')['pep'], layout('PlayerStatusData')['pep_count']" + NL),
])
sub('tools/floor_data.py', [
    ("ZONE_COUNT, ZONE_POINTER, ZONE_SIZE, COUNT, FORMATIONS, RECORD = 0x98, 0xA0, 0xD0, 0x5C, 0x60, 88" + NL +
     "FIXED_COUNT, FIXED_POINTER = 0x28, 0x30" + NL + "ENEMY_SLOTS = 12" + NL +
     "ZONE_FACTORS, FACTOR_NAMES = 0xB8, ('up_a', 'up_b', 'down_a', 'down_b', 'element')" + NL,
     "_F = __import__('game_profile').layout('FloorParameter')          # data_tables/record_layouts.json" + NL +
     "ZONE_COUNT, ZONE_POINTER, ZONE_SIZE = _F['zone_count'], _F['zone_pointer'], _F['zone_size']" + NL +
     "COUNT, FORMATIONS, RECORD = _F['count'], _F['formations'], _F['record']" + NL +
     "FIXED_COUNT, FIXED_POINTER = _F['fixed_count'], _F['fixed_pointer']" + NL + "ENEMY_SLOTS = _F['enemy_slots']" + NL +
     "ZONE_FACTORS, FACTOR_NAMES = _F['zone_factors'], ('up_a', 'up_b', 'down_a', 'down_b', 'element')" + NL),
    ("ENCOUNTER = 0x1C  ", "ENCOUNTER = _F['encounter']  "),
    ("EQUIPMENT_COUNT, EQUIPMENT_POINTER, EQUIPMENT_RECORD, DROP_KINDS = 0x68, 0x70, 0x24, 4",
     "EQUIPMENT_COUNT, EQUIPMENT_POINTER = _F['equipment_count'], _F['equipment_pointer']" + NL +
     "EQUIPMENT_RECORD, DROP_KINDS = _F['equipment_record'], _F['drop_kinds']"),
])
sub('tools/map_data.py', [
    ("HEADER, CELL = 0x0C, 42" + NL,
     "_M = __import__('game_profile').layout('FloorMap')                # data_tables/record_layouts.json" + NL +
     "HEADER, CELL = _M['header'], _M['cell']" + NL),
    ("SCRIPT_COUNT, SCRIPT_POINTER = 0x78, 0x80", "SCRIPT_COUNT, SCRIPT_POINTER = _M['script_count'], _M['script_pointer']"),
])
sub('tools/balance_values.py', [
    ("NPC_PCK, NPC_RECORD, NPC_ID, NPC_STATS = os.path.join('NPC', 'NPC.pck'), 'NPCData.bin', 0x00, 0x20",
     "from game_profile import layout                          # noqa: E402  (data_tables/record_layouts.json)" + NL +
     "_L = {name: layout(name) for name in ('NPCData', 'EnemyStatusData', 'EnemyAttackData', 'EquipmentData', 'SealScrollData'," + NL +
     "                                      'PartySkillData', 'UniqueSkillData', 'ItemData', 'EnchantData', 'LvExpSkptData'," + NL +
     "                                      'QuestData')}" + NL +
     "NPC_PCK, NPC_RECORD = os.path.join('NPC', 'NPC.pck'), 'NPCData.bin'" + NL +
     "NPC_ID, NPC_STATS = _L['NPCData']['id'], _L['NPCData']['stats']"),
    ("ENEMY_FLAGS, ENEMY_EQUIPMENT_DROP, ENEMY_PASSIVE_COUNT, ENEMY_PASSIVES = 0x3C, 0x7C, 0xF0, 0xF4",
     "_E = _L['EnemyStatusData']" + NL +
     "ENEMY_FLAGS, ENEMY_EQUIPMENT_DROP, ENEMY_PASSIVE_COUNT, ENEMY_PASSIVES = (_E['flags'], _E['equipment_drop']," + NL +
     "                                                                         _E['passive_count'], _E['passives'])"),
    ("ENEMY_EQUIPMENT_SLOTS, ENEMY_EQUIPMENT_SLOT = 0x80, 12 ", "ENEMY_EQUIPMENT_SLOTS, ENEMY_EQUIPMENT_SLOT = _E['equipment_slots'], _E['equipment_slot_size'] "),
    ("ATTACK_COUNT, ATTACK_SLOTS, ATTACK_SLOT = 0x48, 0x4C, 12",
     "ATTACK_COUNT, ATTACK_SLOTS, ATTACK_SLOT = (_L['EnemyAttackData']['slot_count'], _L['EnemyAttackData']['slots']," + NL +
     "                                           _L['EnemyAttackData']['slot_size'])"),
    ("EQUIPMENT = {'ATK (base)': (0x24, 'i'), 'upgrade rate': (0x3C, 'f'), 'class bitmask': (0x40, 'I')}",
     "_Q = _L['EquipmentData']" + NL +
     "EQUIPMENT = {'ATK (base)': (_Q['atk'], 'i'), 'upgrade rate': (_Q['upgrade_rate'], 'f'), 'class bitmask': (_Q['class_mask'], 'I')}"),
    ("EQUIPMENT_ENCHANT_COUNT, EQUIPMENT_ENCHANTS, EQUIPMENT_ENCHANT_SLOTS = 0x5C, 0x60, 4",
     "EQUIPMENT_ENCHANT_COUNT, EQUIPMENT_ENCHANTS, EQUIPMENT_ENCHANT_SLOTS = _Q['enchant_count'], _Q['enchants'], _Q['enchant_slots']"),
    ("SEAL_COUNT, SEAL_ENCHANTS, SEAL_SLOTS = 0x1C, 0x20, 4",
     "SEAL_COUNT, SEAL_ENCHANTS, SEAL_SLOTS = (_L['SealScrollData']['count'], _L['SealScrollData']['enchants']," + NL +
     "                                        _L['SealScrollData']['slots'])"),
    ("PARTY_EFFECT = 0x4C  ", "PARTY_EFFECT = _L['PartySkillData']['effect']  "),
    ("UNIQUE_EFFECT = 0x50  ", "UNIQUE_EFFECT = _L['UniqueSkillData']['effect']  "),
    ("UNIQUE_VALUES, UNIQUE_RANKS = 0x1C, 10  ", "UNIQUE_VALUES, UNIQUE_RANKS = _L['UniqueSkillData']['values'], _L['UniqueSkillData']['ranks']  "),
    ("ITEM_PAIRS, ITEM_PAIR_COUNT = 0x24, 4  ", "ITEM_PAIRS, ITEM_PAIR_COUNT = _L['ItemData']['pairs'], _L['ItemData']['pair_count']  "),
    ("ENCHANT_FLAGS = 0x20" + NL, "ENCHANT_FLAGS = _L['EnchantData']['flags']" + NL),
    ("SP_LEVEL, SP_POINTS = 0x00, 0x08", "SP_LEVEL, SP_POINTS = _L['LvExpSkptData']['level'], _L['LvExpSkptData']['points']"),
    ("QUEST_KIND, QUEST_AMOUNT, QUEST_GOLD = 0x38, 0x40, 3",
     "QUEST_KIND, QUEST_AMOUNT, QUEST_GOLD = _L['QuestData']['kind'], _L['QuestData']['amount'], _L['QuestData']['gold_kind']"),
])
sub('tools/text_checks.py', [
    ("UNIQUE_VALUES = 0x1C" + NL, "from game_profile import layout                           # noqa: E402  (data_tables/record_layouts.json)" + NL +
     "UNIQUE_VALUES = layout('UniqueSkillData')['values']" + NL),
    ("ITEM_PAIRS = 0x24" + NL, "ITEM_PAIRS = layout('ItemData')['pairs']" + NL),
    ("ENEMY_SLOT_COUNT = 0x48  ", "ENEMY_SLOT_COUNT = layout('EnemyAttackData')['slot_count']  "),
    ("ENEMY_SLOTS = 0x4C" + NL, "ENEMY_SLOTS = layout('EnemyAttackData')['slots']" + NL),
    ("ENEMY_POWER = 0x3C  ", "ENEMY_POWER = layout('EnemyAttackData')['power']  "),
    ("FOOD_COUNT = 0x1C  ", "FOOD_COUNT = layout('FoodMenuData')['count']  "),
    ("FOOD_PAIRS = 0x20" + NL, "FOOD_PAIRS = layout('FoodMenuData')['pairs']" + NL),
    ("PARTY_EFFECT = 0x4C" + NL, "PARTY_EFFECT = layout('PartySkillData')['effect']" + NL),
    ("JOINT_SLOTS, JOINT_SLOT_COUNT = 0x54, 0x50", "JOINT_SLOTS, JOINT_SLOT_COUNT = layout('JoinSkillData')['slots'], layout('JoinSkillData')['slot_count']"),
])
sub('tools/build_variant.py', [
    ("    ('Unique', ('UniqueSkillData.pck', 0x60, (8, 16)))," + NL,
     "    ('Unique', (layout('UniqueSkillData')['pck'], layout('UniqueSkillData')['header'], tuple(layout('UniqueSkillData')['pointers'])))," + NL),
    ("ENCHANT_PCK = 'EnchantData.pck'" + NL + "ENCHANT_HEADER = 0x38" + NL + "ENCHANT_POINTERS = (8, 16, 24)" + NL +
     "RANK_PCK = 'WeaponRankData.pck'" + NL + "ITEM_PCK = 'ItemData.pck'" + NL + "ITEM_HEADER = 0x70" + NL +
     "ITEM_POINTERS = (8, 16, 0x60)" + NL + "FOOD_PCK = 'FoodMenuData.pck'" + NL + "PARTY_PCK = 'PartySkillData.pck'" + NL +
     "JOINT_PCK = 'JoinSkillData.pck'" + NL + "ENEMY_PCK = 'EnemyAttackData.pck'" + NL + "ENEMY_HEADER = 0xA0" + NL +
     "ENEMY_POINTERS = (8, 16, 24, 32)" + NL + "CLASS_PCK = 'ClassData.pck'" + NL + "CLASS_HEADER = 0x28" + NL,
     "ENCHANT_PCK = layout('EnchantData')['pck']" + NL + "ENCHANT_HEADER = layout('EnchantData')['header']" + NL +
     "ENCHANT_POINTERS = tuple(layout('EnchantData')['pointers'])" + NL +
     "RANK_PCK = layout('WeaponRankData')['pck']" + NL + "ITEM_PCK = layout('ItemData')['pck']" + NL +
     "ITEM_HEADER = layout('ItemData')['header']" + NL + "ITEM_POINTERS = tuple(layout('ItemData')['pointers'])" + NL +
     "FOOD_PCK = layout('FoodMenuData')['pck']" + NL + "PARTY_PCK = layout('PartySkillData')['pck']" + NL +
     "JOINT_PCK = layout('JoinSkillData')['pck']" + NL + "ENEMY_PCK = layout('EnemyAttackData')['pck']" + NL +
     "ENEMY_HEADER = layout('EnemyAttackData')['header']" + NL +
     "ENEMY_POINTERS = tuple(layout('EnemyAttackData')['pointers'])" + NL +
     "CLASS_PCK = layout('ClassData')['pck']" + NL + "CLASS_HEADER = layout('ClassData')['header']" + NL),
    ("SKILL_PCKS = collections.OrderedDict([" + NL,
     "from game_profile import layout                          # noqa: E402  (data_tables/record_layouts.json)" + NL + NL +
     "SKILL_PCKS = collections.OrderedDict([" + NL),
])
print('applied')

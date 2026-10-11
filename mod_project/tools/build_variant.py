"""
Variant build.

Compiles one variant of the mod into mod_project/build/<variant>/, verifies the result and,
only when the verification passes, installs it into the game folder so it can be looked at
on screen (tools/install_variant.py: everything it replaces is saved first).

    python mod_project/tools/build_variant.py qol
    python mod_project/tools/build_variant.py qol --no-install

Variants
  qol   Shows more information about the base game and changes no value.
        Built so far:
          the four skill PCKs      from data_tables/qol_skill_text.xlsx
          EnchantData.pck          from data_tables/qol_enchant_text.xlsx (enchant names with their figure)
          ItemData.pck             from data_tables/qol_item_text.xlsx (original sentence + what the item does)
          EnemyAttackData.pck      from data_tables/qol_enemy_attack_text.xlsx (exact effects on the data line;
                                   a figure of the prose that the data does not hold is corrected)
          WeaponRankData.pck       rank names generated from the delay multiplier of each rank
  balance   The values of data_tables/balance_changes.xlsx and the same texts over them. Never installed by the
            build: python mod_project/tools/install_variant.py balance, when the user says so.
              [0a] tools/balance_values.py writes every live row into copies of the originals
                   (build/balance/base/) and reads the result byte by byte against the originals;
              [0b] tools/balance_readback.py reads that folder with the readers of the project and sets it
                   against the variant of the simulator: the game files and the model must say the same;
              [0c] the two text tables that state a changed figure (skills, enemy attacks) are generated again
                   from the built values (build/balance/tables/); the rows edited by hand are kept, and a
                   figure of theirs that no longer matches stops the build in step 3;
              then the steps of the qol build, with build/balance/base/ in the place of the originals, so
              "no numeric field differs from the original" means "from the values just checked";
              the packs only values change (Enemy.pck, LvExpSkptData, EquipmentData, SealScrollData) are copied in;
              the rows written move to the state "built" and docs/generated/BALANCE_BUILD.md counts them.

The build fails (exit code 1) when
  * the PCK writers no longer reproduce the original files byte for byte,
  * the text table was generated from other backups than the ones being built,
  * any numeric field of a built entry differs from the original (QoL rule),
  * a built text differs from the table, breaks the box limits,
  * a figure shown in a skill, item or enemy attack text differs from the value stored in the built
    binary (tools/text_checks.py),
  * a magnitude word in line 1 of a skill is not the one the averages of the binary give
    (tools/magnitude_words.py),
  * the prose of an enemy attack differs from the original,
  * an enchant name shows a figure that neither a trusted guide nor a hand edit accounts for
    (the binary holds no enchant magnitudes: tools/enchant_values.py), or
  * a weapon rank label differs from the multiplier stored in the same entry.
"""
import os
import re
import sys
import struct
import argparse
import collections
import openpyxl
from pck_handler import (PckArchive, SkillHelper, EnchantHelper, WeaponRankHelper, ItemHelper, EnemyAttackHelper,
                         FoodMenuHelper, PartySkillHelper, JoinSkillHelper, ClassDataHelper)
from extract_vanilla import SKILL_LAYOUTS
from text_checks import (check_skill_text, check_item_text, check_enemy_attack_text, check_food_text,
                         check_party_skill_text, check_joint_skill_text, skill_tables, out_of_game_words)
import magnitude_words
import enchant_values
import weapon_rank_labels
import install_variant
import rules
from shortened_text import ITEM_SENTENCES
from generate_qol_enchant_text import MAX_NAME, MAX_NAME_ON_EQUIPMENT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
BUILD_DIR = os.path.join(BASE_DIR, 'build')
PARAM_SUBDIR = os.path.join('Data', 'ENG', 'Parameter')

MAX_LINE = 85
SKILL_LINE = rules.setting('skill_wide_line')     # a skill box line with widened separators
BATTLE_LINE = rules.setting('battle_line_width')   # the battle bar: line 1 of techniques, spells, joint skills
MAX_BOX_LINES = 3

# category -> (pck, header size, offsets of the 8-byte string pointers)
SKILL_PCKS = collections.OrderedDict([
    ('Technique', (SKILL_LAYOUTS['Technique']['pck'], SKILL_LAYOUTS['Technique']['header'], (8, 16, 24, 32))),
    ('Magic', (SKILL_LAYOUTS['Magic']['pck'], SKILL_LAYOUTS['Magic']['header'], (8, 16, 24, 32))),
    ('Passive', (SKILL_LAYOUTS['Passive']['pck'], SKILL_LAYOUTS['Passive']['header'], (8, 16, 24, 32))),
    ('Unique', ('UniqueSkillData.pck', 0x60, (8, 16))),
])

ENCHANT_PCK = 'EnchantData.pck'
ENCHANT_HEADER = 0x38
ENCHANT_POINTERS = (8, 16, 24)
RANK_PCK = 'WeaponRankData.pck'
ITEM_PCK = 'ItemData.pck'
ITEM_HEADER = 0x70
ITEM_POINTERS = (8, 16, 0x60)
FOOD_PCK = 'FoodMenuData.pck'
PARTY_PCK = 'PartySkillData.pck'
JOINT_PCK = 'JoinSkillData.pck'
ENEMY_PCK = 'EnemyAttackData.pck'
ENEMY_HEADER = 0xA0
ENEMY_POINTERS = (8, 16, 24, 32)
CLASS_PCK = 'ClassData.pck'
CLASS_HEADER = 0x28
CLASS_POINTERS = (8, 16, 24)

VARIANTS = {
    'qol': {'skill_text': 'qol_skill_text.xlsx', 'enchant_text': 'qol_enchant_text.xlsx',
            'item_text': 'qol_item_text.xlsx', 'enemy_attack_text': 'qol_enemy_attack_text.xlsx',
            'food_text': 'qol_food_text.xlsx', 'party_skill_text': 'qol_party_skill_text.xlsx',
            'joint_skill_text': 'qol_joint_skill_text.xlsx',
            'class_text': 'qol_class_text.xlsx',
            'numeric_changes_allowed': False},
    # values: the rows of balance_changes.xlsx are written first and take the place of the originals for every step
    # after; regenerated: the text tables generated again from those values (the others state no changed figure)
    'balance': {'skill_text': 'qol_skill_text.xlsx', 'enchant_text': 'qol_enchant_text.xlsx',
                'item_text': 'qol_item_text.xlsx', 'enemy_attack_text': 'qol_enemy_attack_text.xlsx',
                'food_text': 'qol_food_text.xlsx', 'party_skill_text': 'qol_party_skill_text.xlsx',
                'joint_skill_text': 'qol_joint_skill_text.xlsx',
                'class_text': 'qol_class_text.xlsx',
                'numeric_changes_allowed': False, 'values': True,
                'regenerated': ('skill_text', 'enemy_attack_text'),
                'tutorial_text': 'balance_tutorial_text.xlsx'},
}
VALUE_ONLY_PCKS = (('LvExpSkptData.pck', 'Parameter'), ('EquipmentData.pck', 'Parameter'),
                   ('SealScrollData.pck', 'Parameter'), ('QuestData.pck', 'Parameter'),
                   (os.path.join('Enemy', 'Enemy.pck'), 'Enemy'))
BALANCE_REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'BALANCE_BUILD.md')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def numeric_part(b, header_size, pointer_offsets):
    """Header of an entry with the string pointers blanked: everything the game reads as a value."""
    head = bytearray(b[:header_size])
    for off in pointer_offsets:
        head[off:off + 8] = b'\x00' * 8
    return bytes(head)


def read_texts(b, category):
    info = SkillHelper.read_skill(b, category)
    return info['desc'], info['lvup'], info['name'], info['msg']


def write_entry(b, category, desc, lvup):
    return SkillHelper.write_skill(b, category, desc, lvup if category != 'Unique' else None)


def load_skill_text(path):
    """The hand-editable text table: the build uses exactly what its QoL_* columns say."""
    ws = openpyxl.load_workbook(path)['Skills']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in
           ('Category', 'Filename', 'Vanilla_Desc', 'Vanilla_LvUp', 'QoL_Desc', 'QoL_LvUp')}
    table = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        table[(r[col['Category']], r[col['Filename']])] = {
            'vanilla_desc': r[col['Vanilla_Desc']] or '', 'vanilla_lvup': r[col['Vanilla_LvUp']] or '',
            'desc': r[col['QoL_Desc']] or '', 'lvup': r[col['QoL_LvUp']] or '',
        }
    return table


def load_enchant_text(path):
    """The hand-editable enchant name table: the build uses exactly what its QoL_Name column says."""
    ws = openpyxl.load_workbook(path)['Enchants']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Filename', 'Vanilla_Name', 'QoL_Name', 'Edited')}
    return {r[col['Filename']]: {'vanilla_name': r[col['Vanilla_Name']] or '', 'name': r[col['QoL_Name']] or '',
                                 'edited': str(r[col['Edited']] or '').strip().lower() == 'yes'}
            for r in ws.iter_rows(min_row=2, values_only=True)}


def load_item_text(path):
    """The hand-editable item text table: the build uses exactly what its QoL_Desc column says."""
    ws = openpyxl.load_workbook(path)['Items']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Filename', 'Vanilla_Desc', 'QoL_Desc')}
    return {r[col['Filename']]: {'vanilla_desc': r[col['Vanilla_Desc']] or '', 'desc': r[col['QoL_Desc']] or ''}
            for r in ws.iter_rows(min_row=2, values_only=True)}


def load_enemy_attack_text(path):
    """The hand-editable enemy attack table: the build uses exactly what its QoL_Desc column says."""
    ws = openpyxl.load_workbook(path)['EnemyAttacks']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Filename', 'Vanilla_Desc', 'QoL_Desc')}
    return {r[col['Filename']]: {'vanilla_desc': r[col['Vanilla_Desc']] or '', 'desc': r[col['QoL_Desc']] or ''}
            for r in ws.iter_rows(min_row=2, values_only=True)}


def read_archive(pck):
    path = os.path.join(BACKUP_DIR, pck)
    with open(path, 'rb') as f:
        return PckArchive(path), f.read()


# ---------------------------------------------------------------------------
# Step 1: the writers must reproduce the originals exactly
# ---------------------------------------------------------------------------
def self_test_writers(problems):
    checked = 0
    for pck, rewrite in ((ENCHANT_PCK, lambda b: EnchantHelper.write_enchant(b, EnchantHelper.read_enchant(b)['name'])),
                         (RANK_PCK, lambda b: WeaponRankHelper.write_rank(b, WeaponRankHelper.read_rank(b)['name'])),
                         (ITEM_PCK, lambda b: ItemHelper.write_item(b, ItemHelper.read_item(b)['desc'])),
                         (FOOD_PCK, lambda b: FoodMenuHelper.write_food_menu(b, FoodMenuHelper.read_food_menu(b)['effect'])),
                         (JOINT_PCK, lambda b: JoinSkillHelper.write_joint(b, JoinSkillHelper.read_joint(b)['desc'])),
                         (PARTY_PCK, lambda b: PartySkillHelper.write_party_skill(
                             b, PartySkillHelper.read_party_skill(b)['effect'])),
                         (CLASS_PCK, lambda b: ClassDataHelper.write_class(
                             b, ClassDataHelper.read_class(b)['desc'])),
                         (ENEMY_PCK, lambda b: EnemyAttackHelper.write_enemy_attack(
                             b, EnemyAttackHelper.read_enemy_attack(b)['desc']))):
        archive, raw = read_archive(pck)
        if archive.build() != raw:
            problems.append(f"{pck}: rebuilding the untouched archive does not reproduce the original file")
        for fn, b in archive.files:
            if rewrite(b) != bytes(b):
                problems.append(f"{pck}/{fn}: rewriting the original name does not reproduce the original entry")
            checked += 1
    for category, (pck, _, _) in SKILL_PCKS.items():
        path = os.path.join(BACKUP_DIR, pck)
        with open(path, 'rb') as f:
            raw = f.read()
        archive = PckArchive(path)
        if archive.build() != raw:
            problems.append(f"{pck}: rebuilding the untouched archive does not reproduce the original file")
        for fn, b in archive.files:
            desc, lvup, _, _ = read_texts(b, category)
            if write_entry(b, category, desc, lvup) != bytes(b):
                problems.append(f"{pck}/{fn}: rewriting the original text does not reproduce the original entry")
            checked += 1
    return checked


# ---------------------------------------------------------------------------
# Step 2: build
# ---------------------------------------------------------------------------
def build_skills(out_dir, table, problems):
    stats = collections.Counter()
    for category, (pck, _, _) in SKILL_PCKS.items():
        archive = PckArchive(os.path.join(BACKUP_DIR, pck))
        for i, (fn, b) in enumerate(archive.files):
            row = table.get((category, fn))
            if row is None:
                problems.append(f"{pck}/{fn}: no row in the text table")
                continue
            desc, lvup, _, _ = read_texts(b, category)
            if (row['vanilla_desc'], row['vanilla_lvup']) != (desc, lvup):
                problems.append(f"{pck}/{fn}: text table is stale (its vanilla text is not the one in the backup)")
                continue
            if (row['desc'], row['lvup']) == (desc, lvup):
                stats['kept'] += 1          # untouched entries stay byte-identical
                continue
            archive.files[i] = (fn, write_entry(b, category, row['desc'], row['lvup']))
            stats['rewritten'] += 1
        archive.save(os.path.join(out_dir, pck))
    return stats


def build_enchants(out_dir, table, problems):
    stats = collections.Counter()
    archive = PckArchive(os.path.join(BACKUP_DIR, ENCHANT_PCK))
    for i, (fn, b) in enumerate(archive.files):
        row = table.get(fn)
        if row is None:
            problems.append(f"{ENCHANT_PCK}/{fn}: no row in the enchant table")
            continue
        name = EnchantHelper.read_enchant(b)['name']
        if row['vanilla_name'] != name:
            problems.append(f"{ENCHANT_PCK}/{fn}: enchant table is stale (its vanilla name is not the one in the backup)")
            continue
        if row['name'] == name:
            stats['kept'] += 1
            continue
        archive.files[i] = (fn, EnchantHelper.write_enchant(b, row['name']))
        stats['rewritten'] += 1
    archive.save(os.path.join(out_dir, ENCHANT_PCK))
    return stats


def build_items(out_dir, table, problems):
    stats = collections.Counter()
    archive = PckArchive(os.path.join(BACKUP_DIR, ITEM_PCK))
    for i, (fn, b) in enumerate(archive.files):
        row = table.get(fn)
        if row is None:
            problems.append(f"{ITEM_PCK}/{fn}: no row in the item table")
            continue
        desc = ItemHelper.read_item(b)['desc']
        if row['vanilla_desc'] != desc:
            problems.append(f"{ITEM_PCK}/{fn}: item table is stale (its vanilla text is not the one in the backup)")
            continue
        if row['desc'] == desc:
            stats['kept'] += 1
            continue
        archive.files[i] = (fn, ItemHelper.write_item(b, row['desc']))
        stats['rewritten'] += 1
    archive.save(os.path.join(out_dir, ITEM_PCK))
    return stats


def build_enemy_attacks(out_dir, table, problems):
    stats = collections.Counter()
    archive = PckArchive(os.path.join(BACKUP_DIR, ENEMY_PCK))
    for i, (fn, b) in enumerate(archive.files):
        row = table.get(fn)
        if row is None:
            problems.append(f"{ENEMY_PCK}/{fn}: no row in the enemy attack table")
            continue
        desc = EnemyAttackHelper.read_enemy_attack(b)['desc']
        if row['vanilla_desc'] != desc:
            problems.append(f"{ENEMY_PCK}/{fn}: enemy attack table is stale (its vanilla text is not the one in the backup)")
            continue
        if row['desc'] == desc:
            stats['kept'] += 1
            continue
        archive.files[i] = (fn, EnemyAttackHelper.write_enemy_attack(b, row['desc']))
        stats['rewritten'] += 1
    archive.save(os.path.join(out_dir, ENEMY_PCK))
    return stats


def load_food_text(path):
    ws = openpyxl.load_workbook(path)['Meals']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Filename', 'Vanilla_Effect', 'QoL_Effect')}
    return {r[col['Filename']]: {'vanilla': r[col['Vanilla_Effect']] or '', 'effect': r[col['QoL_Effect']] or ''}
            for r in ws.iter_rows(min_row=2, values_only=True)}


def build_food(out_dir, table, problems):
    """Meals: the flavour line stays; the effect line states the stored amounts."""
    stats = collections.Counter()
    archive = PckArchive(os.path.join(BACKUP_DIR, FOOD_PCK))
    for i, (fn, b) in enumerate(archive.files):
        meal, row = FoodMenuHelper.read_food_menu(b), table.get(fn)
        if row is None or row['vanilla'] != meal['effect']:
            problems.append(f"{FOOD_PCK}/{fn}: no row in the meal table, or the table is stale")
            continue
        if row['effect'] == meal['effect']:
            stats['kept'] += 1
            continue
        archive.files[i] = (fn, FoodMenuHelper.write_food_menu(b, row['effect']))
        stats['rewritten'] += 1
    archive.save(os.path.join(out_dir, FOOD_PCK))
    return stats


def verify_food(out_dir, table, variant, problems):
    counts = collections.Counter()
    original = PckArchive(os.path.join(BACKUP_DIR, FOOD_PCK)).files
    built = PckArchive(os.path.join(out_dir, FOOD_PCK)).files
    for (fn, old), (_, new) in zip(original, built):
        was, now = FoodMenuHelper.read_food_menu(old), FoodMenuHelper.read_food_menu(new)
        label = f"{FOOD_PCK}/{fn} ({was['name']})"
        counts['entries'] += 1
        head = struct.unpack_from('<Q', old, 8)[0]
        if not variant['numeric_changes_allowed'] and numeric_part(new, head, (8, 16)) != numeric_part(old, head, (8, 16)):
            problems.append(f"{label}: numeric data differs from the original")
        if (now['name'], now['flavor']) != (was['name'], was['flavor']):
            problems.append(f"{label}: name or flavour line changed")
        if now['effect'] != table[fn]['effect'] or len(now['effect']) > MAX_LINE:
            problems.append(f"{label}: built text differs from the meal table, or is too long")
        if now['effect'] == was['effect'] and bytes(new) != bytes(old):
            problems.append(f"{label}: entry with unchanged text is not byte-identical to the original")
        found, verified = check_food_text(new, now['effect'], was['effect'])
        problems.extend(f"{label}: {p}" for p in found)
        counts['numbers'] += verified
    return counts


def load_party_skill_text(path):
    ws = openpyxl.load_workbook(path)['PartySkills']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Filename', 'Vanilla_Effect', 'QoL_Effect')}
    return {r[col['Filename']]: {'vanilla': r[col['Vanilla_Effect']] or '', 'effect': r[col['QoL_Effect']] or ''}
            for r in ws.iter_rows(min_row=2, values_only=True)}


def build_party_skills(out_dir, table, problems):
    """Party skills: the list of members stays; the effect line gains the bound of each bonus."""
    stats = collections.Counter()
    archive = PckArchive(os.path.join(BACKUP_DIR, PARTY_PCK))
    for i, (fn, b) in enumerate(archive.files):
        skill, row = PartySkillHelper.read_party_skill(b), table.get(fn)
        if row is None or row['vanilla'] != skill['effect']:
            problems.append(f"{PARTY_PCK}/{fn}: no row in the party skill table, or the table is stale")
            continue
        if row['effect'] == skill['effect']:
            stats['kept'] += 1
            continue
        archive.files[i] = (fn, PartySkillHelper.write_party_skill(b, row['effect']))
        stats['rewritten'] += 1
    archive.save(os.path.join(out_dir, PARTY_PCK))
    return stats


def verify_party_skills(out_dir, table, variant, problems):
    counts = collections.Counter()
    original = PckArchive(os.path.join(BACKUP_DIR, PARTY_PCK)).files
    built = PckArchive(os.path.join(out_dir, PARTY_PCK)).files
    for (fn, old), (_, new) in zip(original, built):
        was, now = PartySkillHelper.read_party_skill(old), PartySkillHelper.read_party_skill(new)
        label = f"{PARTY_PCK}/{fn} ({was['name']})"
        counts['entries'] += 1
        head = struct.unpack_from('<Q', old, 8)[0]
        if not variant['numeric_changes_allowed'] and numeric_part(new, head, (8, 16, 24)) != numeric_part(old, head, (8, 16, 24)):
            problems.append(f"{label}: numeric data differs from the original")
        if (now['name'], now['req']) != (was['name'], was['req']):
            problems.append(f"{label}: name or list of members changed")
        if now['effect'] != table[fn]['effect'] or len(now['effect']) > MAX_LINE:
            problems.append(f"{label}: built text differs from the party skill table, or is too long")
        if now['s2'] != f"{now['req']}\n{PartySkillHelper.INDENT}{now['effect']}":
            problems.append(f"{label}: the two copies of the text differ")
        if now['effect'] == was['effect'] and bytes(new) != bytes(old):
            problems.append(f"{label}: entry with unchanged text is not byte-identical to the original")
        found, verified = check_party_skill_text(new, now['effect'], was['effect'])
        problems.extend(f"{label}: {p}" for p in found)
        counts['numbers'] += verified
    return counts


def load_joint_skill_text(path):
    ws = openpyxl.load_workbook(path)['JointSkills']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Filename', 'Vanilla_Desc', 'QoL_Desc')}
    return {r[col['Filename']]: {'vanilla': r[col['Vanilla_Desc']] or '', 'desc': r[col['QoL_Desc']] or ''}
            for r in ws.iter_rows(min_row=2, values_only=True)}


def build_joint_skills(out_dir, table, problems):
    """Joint skills: the sentence states the stored value of the effects it speaks of."""
    stats = collections.Counter()
    archive = PckArchive(os.path.join(BACKUP_DIR, JOINT_PCK))
    for i, (fn, b) in enumerate(archive.files):
        skill, row = JoinSkillHelper.read_joint(b), table.get(fn)
        if row is None or row['vanilla'] != skill['desc']:
            problems.append(f"{JOINT_PCK}/{fn}: no row in the joint skill table, or the table is stale")
            continue
        if row['desc'] == skill['desc']:
            stats['kept'] += 1
            continue
        archive.files[i] = (fn, JoinSkillHelper.write_joint(b, row['desc']))
        stats['rewritten'] += 1
    archive.save(os.path.join(out_dir, JOINT_PCK))
    return stats


def verify_joint_skills(out_dir, table, variant, problems):
    counts = collections.Counter()
    original = PckArchive(os.path.join(BACKUP_DIR, JOINT_PCK)).files
    built = PckArchive(os.path.join(out_dir, JOINT_PCK)).files
    for (fn, old), (_, new) in zip(original, built):
        was, now = JoinSkillHelper.read_joint(old), JoinSkillHelper.read_joint(new)
        label = f"{JOINT_PCK}/{fn} ({was['name']})"
        counts['entries'] += 1
        if not variant['numeric_changes_allowed'] and (
                numeric_part(new, JoinSkillHelper.HEADER, JoinSkillHelper.POINTERS)
                != numeric_part(old, JoinSkillHelper.HEADER, JoinSkillHelper.POINTERS)):
            problems.append(f"{label}: numeric data differs from the original")
        if (now['name'], now['msg']) != (was['name'], was['msg']):
            problems.append(f"{label}: name or battle message changed")
        visible = was['name'] != "Genocide Rain's Action"       # internal entry, never drawn
        if now['desc'] != table[fn]['desc'] or '\n' in now['desc'] or (visible and len(now['desc']) > BATTLE_LINE):
            problems.append(f"{label}: built text differs from the joint skill table, or is not one line of {BATTLE_LINE}")
        if now['desc'] == was['desc'] and bytes(new) != bytes(old):
            problems.append(f"{label}: entry with unchanged text is not byte-identical to the original")
        found, verified = check_joint_skill_text(new, was['name'], now['desc'], was['desc'])
        problems.extend(f"{label}: {p}" for p in found)
        counts['numbers'] += verified
    return counts


def load_class_text(path):
    ws = openpyxl.load_workbook(path)['Classes']
    header = [c.value for c in ws[1]]
    col = {name: header.index(name) for name in ('Filename', 'Vanilla_Desc', 'QoL_Desc')}
    return {r[col['Filename']]: {'vanilla': r[col['Vanilla_Desc']] or '', 'desc': r[col['QoL_Desc']] or ''}
            for r in ws.iter_rows(min_row=2, values_only=True)}


def build_classes(out_dir, table, problems):
    """Classes: surgical clarifications of weapons and roles for 7 classes; 42 kept byte-identical."""
    stats = collections.Counter()
    archive = PckArchive(os.path.join(BACKUP_DIR, CLASS_PCK))
    for i, (fn, b) in enumerate(archive.files):
        cls_data, row = ClassDataHelper.read_class(b), table.get(fn)
        if row is None or row['vanilla'] != cls_data['desc']:
            problems.append(f"{CLASS_PCK}/{fn}: no row in class text table, or table is stale")
            continue
        if row['desc'] == cls_data['desc']:
            stats['kept'] += 1
            continue
        archive.files[i] = (fn, ClassDataHelper.write_class(b, row['desc']))
        stats['rewritten'] += 1
    archive.save(os.path.join(out_dir, CLASS_PCK))
    return stats


def verify_classes(out_dir, table, variant, problems):
    counts = collections.Counter()
    original = PckArchive(os.path.join(BACKUP_DIR, CLASS_PCK)).files
    built = PckArchive(os.path.join(out_dir, CLASS_PCK)).files
    for (fn, old), (_, new) in zip(original, built):
        was, now = ClassDataHelper.read_class(old), ClassDataHelper.read_class(new)
        label = f"{CLASS_PCK}/{fn} ({was['name']})"
        counts['entries'] += 1
        if not variant['numeric_changes_allowed'] and (
                numeric_part(new, CLASS_HEADER, CLASS_POINTERS) != numeric_part(old, CLASS_HEADER, CLASS_POINTERS)):
            problems.append(f"{label}: numeric data differs from the original")
        if (now['name'], now['code']) != (was['name'], was['code']):
            problems.append(f"{label}: name or class code changed")
        if now['desc'] != table[fn]['desc']:
            problems.append(f"{label}: built text differs from the class table")
        lines = now['desc'].split('\n')
        if len(lines) > MAX_BOX_LINES:
            problems.append(f"{label}: {len(lines)} lines exceeds limit of {MAX_BOX_LINES}")
        if now['desc'] != was['desc']:
            counts['modified'] += 1
            for l in lines:
                if len(l) > MAX_LINE + 2:
                    problems.append(f"{label}: line length {len(l)} exceeds box limit")
            if '~' in now['desc']:
                problems.append(f"{label}: contains tilde")
        else:
            if bytes(new) != bytes(old):
                problems.append(f"{label}: entry with unchanged text is not byte-identical to the original")
    return counts


def check_game_voice(tables, problems):
    """No text the mod writes may speak from outside the game. tables: (label, rows of (key, vanilla, new))."""
    checked = 0
    for label, rows in tables:
        for key, vanilla, new in rows:
            if new == vanilla:
                continue
            checked += 1
            words = out_of_game_words(new, vanilla)
            if words:
                problems.append(f"{label}/{key}: the text speaks from outside the game ({', '.join(words)}): '{new}'")
    return checked


def backup_path(pck):
    """Parameter packs sit in backups/, the scripts that share a name with one in backups/Script/."""
    path = os.path.join(BACKUP_DIR, pck)
    return path if os.path.exists(path) else os.path.join(BACKUP_DIR, 'Script', pck)


def build_script_fixes(out_dir, problems):
    """Sentences of lessons, tutorials and shops that state a rule wrongly (sheet ScriptFixes).
    A script is bytecode: the replacement has the same number of bytes and nothing else moves."""
    script_dir = os.path.join(os.path.dirname(out_dir), 'Script')
    if os.path.isdir(script_dir):
        for stale in os.listdir(script_dir):
            os.remove(os.path.join(script_dir, stale))
    by_pack = collections.defaultdict(list)
    for row in rules.rows('ScriptFixes'):
        by_pack[row['Pack']].append(row)
    fixed = 0
    for pck, rows in by_pack.items():
        archive = PckArchive(backup_path(pck))
        names = [fn for fn, _ in archive.files]
        for row in rows:
            label = f"{pck}/{row['Entry']}"
            old, new = row['Original'].encode('utf-8'), row['Replacement'].encode('utf-8')
            if row['Entry'] not in names:
                problems.append(f"{label}: no such entry")
                continue
            i = names.index(row['Entry'])
            data = bytes(archive.files[i][1])
            if len(old) != len(new):
                problems.append(f"{label}: the replacement has {len(new)} bytes, the original {len(old)}")
            elif data.count(old + bytes(1)) != 1:
                problems.append(f"{label}: the original sentence is not in the entry exactly once")
            elif out_of_game_words(row['Replacement'], row['Original']):
                problems.append(f"{label}: the replacement speaks from outside the game")
            else:
                archive.files[i] = (row['Entry'], data.replace(old + bytes(1), new + bytes(1)))
                fixed += 1
        os.makedirs(script_dir, exist_ok=True)
        archive.save(os.path.join(script_dir, pck))
        original, built = PckArchive(backup_path(pck)).files, PckArchive(os.path.join(script_dir, pck)).files
        changed = [fn for (fn, a), (_, b) in zip(original, built) if bytes(a) != bytes(b)]
        if sorted(changed) != sorted(r['Entry'] for r in rows) or any(len(a) != len(b) for (_, a), (_, b) in zip(original, built)):
            problems.append(f"{pck}: entries other than the corrected ones changed, or a size changed")
    return fixed, sorted(by_pack)


SCRIPT_TEXT = re.compile(rb'[\x20-\x7e\n]{6,}\x00')


def script_tokens(data):
    """An entry of a script cut into [(is text, bytes)]: the strings it shows or names, and what lies between."""
    tokens, at = [], 0
    for found in SCRIPT_TEXT.finditer(data):
        tokens.append((False, data[at:found.start()]))
        tokens.append((True, found.group()))
        at = found.end()
    tokens.append((False, data[at:]))
    return tokens


def build_tutorials(out_dir, path, problems):
    """Boxes of the lessons of Euthys and of the library rewritten whole: the rows in the state "checked" of the sheet
    Tutorials of the variant's tutorial workbook. An entry of these packs is a stream of commands with named labels
    and strings that end in a zero; no word of it points at a byte (audit of 2026-10-11, 35 entries), so a box may
    change length. The result is read back: only the entries of the rows (and of the sheet ScriptFixes) differ from
    the originals, and in them only the boxes of the rows; every byte between the strings is the original."""
    wb = openpyxl.load_workbook(path, read_only=True)
    limits = {r[0]: r[1] for r in wb['Settings'].iter_rows(min_row=2, values_only=True) if r and r[0]}
    it = wb['Tutorials'].iter_rows(values_only=True)
    head = next(it)
    rows = [dict(zip(head, r)) for r in it if r and r[0]]
    script_dir = os.path.join(os.path.dirname(out_dir), 'Script')
    os.makedirs(script_dir, exist_ok=True)
    fixes = collections.defaultdict(list)
    for fix in rules.rows('ScriptFixes'):
        fixes[(fix['Pack'], fix['Entry'])].append((fix['Original'], fix['Replacement']))
    stats, by_pack = collections.Counter(), collections.defaultdict(list)
    for row in rows:
        by_pack[row['Pack']].append(row)
    for pck, pack_rows in by_pack.items():
        built = os.path.join(script_dir, pck)
        archive = PckArchive(built if os.path.exists(built) else backup_path(pck))
        names = [fn for fn, _ in archive.files]
        wanted = collections.defaultdict(dict)                 # entry -> {original box: new box}, as bytes
        for row in pack_rows:
            label = f"{pck}/{row['Entry']}"
            if row['State'] != 'checked':
                stats[row['State']] += 1
                continue
            text, old_box = row['Text'] or '', row['Original box'] or ''
            lines = text.strip('"').split('\n')
            if len(lines) > int(limits['max_lines']) or max(len(x) for x in lines) > int(limits['max_width']):
                problems.append(f"{label}: {len(lines)} lines, widest {max(len(x) for x in lines)}: over the limits of the sheet Settings")
                continue
            if '~' in text or out_of_game_words(text, old_box):
                problems.append(f"{label}: a tilde, or a word that speaks from outside the game: {out_of_game_words(text, old_box)}")
                continue
            try:
                new = text.encode('latin-1') + bytes(1)
            except UnicodeEncodeError:
                problems.append(f"{label}: a character the game font does not hold")
                continue
            if row['Entry'] not in names:
                problems.append(f"{label}: no such entry")
                continue
            i = names.index(row['Entry'])
            data = bytes(archive.files[i][1])
            candidates = [old_box] + [old_box.replace(a, b) for a, b in fixes.get((pck, row['Entry']), ())]
            needle = next((c.encode('latin-1') + bytes(1) for c in candidates if data.count(c.encode('latin-1') + bytes(1)) == 1), None)
            if needle is None:
                problems.append(f"{label}: the original box is not in the entry exactly once")
                continue
            archive.files[i] = (row['Entry'], bytearray(data.replace(needle, new)))
            wanted[row['Entry']][old_box.encode('latin-1') + bytes(1)] = new
            stats['written'] += 1
            stats['voiced'] += bool(row['Voiced'])
        archive.save(built)
        fixed = {entry for (pack, entry) in fixes if pack == pck}
        for (fn, before), (_, after) in zip(PckArchive(backup_path(pck)).files, PckArchive(built).files):
            before, after = bytes(before), bytes(after)
            if before == after:
                if fn in wanted:
                    problems.append(f"{pck}/{fn}: a row was written and the entry is the original")
                continue
            if fn not in wanted:
                if fn not in fixed:
                    problems.append(f"{pck}/{fn}: changed and no row names it")
                continue
            old_tokens, new_tokens = script_tokens(before), script_tokens(after)
            if len(old_tokens) != len(new_tokens):
                problems.append(f"{pck}/{fn}: the strings of the entry are not the same in number")
                continue
            for (is_text, a), (_, b) in zip(old_tokens, new_tokens):
                if a == b:
                    continue
                if not is_text:
                    problems.append(f"{pck}/{fn}: bytes between two strings changed")
                elif wanted[fn].get(a) != b and fn not in fixed:
                    problems.append(f"{pck}/{fn}: a string no row names changed: {a[:40]!r}")
    return stats, sorted(by_pack)


def build_weapon_ranks(out_dir):
    """Rank names are generated from the multiplier of each entry; the multipliers are not touched."""
    archive = PckArchive(os.path.join(BACKUP_DIR, RANK_PCK))
    changes = weapon_rank_labels.relabel(archive)
    archive.save(os.path.join(out_dir, RANK_PCK))
    return changes


# ---------------------------------------------------------------------------
# Step 3: verify what was written to disk
# ---------------------------------------------------------------------------
def verify_skills(out_dir, table, variant, problems):
    counts, untraced = collections.Counter(), []
    for category, (pck, header_size, pointers) in SKILL_PCKS.items():
        original = PckArchive(os.path.join(BACKUP_DIR, pck)).files
        built = PckArchive(os.path.join(out_dir, pck)).files
        if [fn for fn, _ in built] != [fn for fn, _ in original]:
            problems.append(f"{pck}: entry list differs from the original")
            continue
        for (fn, old), (_, new) in zip(original, built):
            row = table[(category, fn)]
            desc, lvup, name, msg = read_texts(new, category)
            _, _, old_name, old_msg = read_texts(old, category)
            label = f"{pck}/{fn} ({name})"
            counts['entries'] += 1

            if not variant['numeric_changes_allowed'] and \
                    numeric_part(new, header_size, pointers) != numeric_part(old, header_size, pointers):
                problems.append(f"{label}: numeric data differs from the original")
            if (name, msg) != (old_name, old_msg):
                problems.append(f"{label}: name or battle message changed")
            if (desc, lvup) != (row['desc'], row['lvup']):
                problems.append(f"{label}: built text differs from the text table")
            if (row['desc'], row['lvup']) == (row['vanilla_desc'], row['vanilla_lvup']) and bytes(new) != bytes(old):
                problems.append(f"{label}: entry with unchanged text is not byte-identical to the original")

            # Line 1 is what the battle bar shows, without the level: no new figures, and only the
            # magnitude words the binary gives.
            if category in ('Technique', 'Magic', 'Passive'):
                if desc != row['vanilla_desc']:
                    if category in ('Technique', 'Magic') and len(desc) > BATTLE_LINE:
                        problems.append(f"{label}: line 1 has {len(desc)} characters, the battle bar holds {BATTLE_LINE}")
                    if len(desc) > MAX_LINE or desc.count('\n') != row['vanilla_desc'].count('\n'):
                        problems.append(f"{label}: line 1 must keep its line count and stay within {MAX_LINE} chars")
                    if sorted(re.findall(r'\d+', magnitude_words.strip_chances(desc, row['vanilla_desc']))) != sorted(re.findall(r'\d+', row['vanilla_desc'])):
                        problems.append(f"{label}: line 1 carries a figure the vanilla sentence does not have")
                tables = skill_tables(category, new)
                found, verified = magnitude_words.check_line1(
                    desc, row['vanilla_desc'], tables['slots'],
                    [tables[k] for k in ('accuracy', 'turns', 'tp', 'speed', 'cast') if tables.get(k)])
                problems.extend(f"{label}: {p}" for p in found)
                counts['words'] += verified

            lines = desc.split('\n') + (lvup.split('\n') if lvup else [])
            if (desc, lvup) != (row['vanilla_desc'], row['vanilla_lvup']):
                counts['modified'] += 1
                if len(lines) > MAX_BOX_LINES:
                    problems.append(f"{label}: {len(lines)} lines")
                added = lines[len(row['vanilla_desc'].split('\n')):] if category == 'Unique' else lvup.split('\n')
                for line in added:
                    if len(line) > SKILL_LINE:
                        problems.append(f"{label}: line of {len(line)} chars")
                if '~' in desc + lvup:
                    problems.append(f"{label}: contains tilde")
                found, verified, loose = check_skill_text(category, new, '\n'.join(added))
                problems.extend(f"{label}: {p}" for p in found)
                counts['numbers'] += verified
                counts['untraced'] += len(loose)
                untraced.extend(f"{name}: {x}" for x in loose)
    return counts, untraced


def verify_enchants(out_dir, table, variant, problems):
    counts = collections.Counter()
    original = PckArchive(os.path.join(BACKUP_DIR, ENCHANT_PCK)).files
    built = PckArchive(os.path.join(out_dir, ENCHANT_PCK)).files
    if [fn for fn, _ in built] != [fn for fn, _ in original]:
        problems.append(f"{ENCHANT_PCK}: entry list differs from the original")
        return counts
    for (fn, old), (_, new) in zip(original, built):
        row, was, now = table[fn], EnchantHelper.read_enchant(old), EnchantHelper.read_enchant(new)
        label = f"{ENCHANT_PCK}/{fn} ({was['name']})"
        counts['entries'] += 1
        if not variant['numeric_changes_allowed'] and \
                numeric_part(new, ENCHANT_HEADER, ENCHANT_POINTERS) != numeric_part(old, ENCHANT_HEADER, ENCHANT_POINTERS):
            problems.append(f"{label}: numeric data differs from the original")
        if (now['prefix'], now['suffix']) != (was['prefix'], was['suffix']):
            problems.append(f"{label}: prefix or suffix changed")
        if now['name'] != row['name']:
            problems.append(f"{label}: built name differs from the enchant table")
        if now['name'] == was['name']:
            if bytes(new) != bytes(old):
                problems.append(f"{label}: entry with unchanged name is not byte-identical to the original")
            continue
        counts['renamed'] += 1
        limit = MAX_NAME_ON_EQUIPMENT if was['prefix'] != '0' else MAX_NAME
        if len(now['name']) > limit:
            problems.append(f"{label}: name of {len(now['name'])} chars (limit {limit})")
        if '~' in now['name'] or '\n' in now['name']:
            problems.append(f"{label}: name contains a tilde or a line break")
        # No enchant magnitude exists in the binary: a figure must come from a trusted guide or a hand edit.
        enchant_id = struct.unpack_from('<i', old, 0)[0]
        if now['name'] == enchant_values.qol_name(enchant_id, was['name']):
            counts['sourced'] += 1
        elif row['edited']:
            counts['hand worded'] += 1
        else:
            problems.append(f"{label}: '{now['name']}' is neither the sourced name nor marked as edited")
    return counts


def verify_items(out_dir, table, variant, problems):
    counts = collections.Counter()
    original = PckArchive(os.path.join(BACKUP_DIR, ITEM_PCK)).files
    built = PckArchive(os.path.join(out_dir, ITEM_PCK)).files
    if [fn for fn, _ in built] != [fn for fn, _ in original]:
        problems.append(f"{ITEM_PCK}: entry list differs from the original")
        return counts
    for (fn, old), (_, new) in zip(original, built):
        row, was, now = table[fn], ItemHelper.read_item(old), ItemHelper.read_item(new)
        label = f"{ITEM_PCK}/{fn} ({was['name']})"
        counts['entries'] += 1
        if not variant['numeric_changes_allowed'] and \
                numeric_part(new, ITEM_HEADER, ITEM_POINTERS) != numeric_part(old, ITEM_HEADER, ITEM_POINTERS):
            problems.append(f"{label}: numeric data differs from the original")
        if (now['name'], now['name2']) != (was['name'], was['name2']):
            problems.append(f"{label}: name changed")
        if now['desc'] != row['desc']:
            problems.append(f"{label}: built text differs from the item table")
        if now['desc'] == was['desc']:
            if bytes(new) != bytes(old):
                problems.append(f"{label}: entry with unchanged text is not byte-identical to the original")
            continue
        counts['modified'] += 1
        # The same text is the one-line bar shown in battle.
        if '\n' in now['desc'] or len(now['desc']) > BATTLE_LINE or '~' in now['desc']:
            problems.append(f"{label}: text must be one line of at most {BATTLE_LINE} chars without tilde")
        if re.search(r'\((?:small|medium|large)\)', now['desc']) and re.search(r'\(\+\d', now['desc']):
            problems.append(f"{label}: states both a vague size and an exact amount")
        found, verified = check_item_text(new, now['desc'], was['desc'], ITEM_SENTENCES.get(was['name']))
        problems.extend(f"{label}: {p}" for p in found)
        counts['numbers'] += verified
    return counts


def verify_enemy_attacks(out_dir, table, variant, problems):
    counts = collections.Counter()
    original = PckArchive(os.path.join(BACKUP_DIR, ENEMY_PCK)).files
    built = PckArchive(os.path.join(out_dir, ENEMY_PCK)).files
    if [fn for fn, _ in built] != [fn for fn, _ in original]:
        problems.append(f"{ENEMY_PCK}: entry list differs from the original")
        return counts
    for (fn, old), (_, new) in zip(original, built):
        row, was, now = table[fn], EnemyAttackHelper.read_enemy_attack(old), EnemyAttackHelper.read_enemy_attack(new)
        label = f"{ENEMY_PCK}/{fn} ({was['name']})"
        counts['entries'] += 1
        if not variant['numeric_changes_allowed'] and \
                numeric_part(new, ENEMY_HEADER, ENEMY_POINTERS) != numeric_part(old, ENEMY_HEADER, ENEMY_POINTERS):
            problems.append(f"{label}: numeric data differs from the original")
        if bytes(new[ENEMY_HEADER:now['p3']]) != bytes(old[ENEMY_HEADER:was['p3']]):
            problems.append(f"{label}: a name string changed")
        if now['desc'] != row['desc']:
            problems.append(f"{label}: built text differs from the enemy attack table")
        if now['desc'] == was['desc']:
            if bytes(new) != bytes(old):
                problems.append(f"{label}: entry with unchanged text is not byte-identical to the original")
            continue
        counts['modified'] += 1
        if len(now['desc'].split('\n')[0]) > MAX_LINE or '~' in now['desc']:
            problems.append(f"{label}: data line longer than {MAX_LINE} chars, or a tilde")
        found, verified = check_enemy_attack_text(new, now['desc'], was['desc'])
        problems.extend(f"{label}: {p}" for p in found)
        counts['numbers'] += verified
    return counts


def verify_weapon_ranks(out_dir, variant, problems):
    original = PckArchive(os.path.join(BACKUP_DIR, RANK_PCK)).files
    archive = PckArchive(os.path.join(out_dir, RANK_PCK))
    if [fn for fn, _ in archive.files] != [fn for fn, _ in original]:
        problems.append(f"{RANK_PCK}: entry list differs from the original")
        return []
    for (fn, old), (_, new) in zip(original, archive.files):
        header = WeaponRankHelper.HEADER
        if not variant['numeric_changes_allowed'] and bytes(new[:header]) != bytes(old[:header]):
            problems.append(f"{RANK_PCK}/{fn}: numeric data differs from the original")
        if weapon_rank_labels.bare_rank(WeaponRankHelper.read_rank(new)['name']) != WeaponRankHelper.read_rank(old)['name']:
            problems.append(f"{RANK_PCK}/{fn}: rank letter changed")
    problems.extend(f"{RANK_PCK}/{p}" for p in weapon_rank_labels.check(archive))
    return [WeaponRankHelper.read_rank(b)['name'] for _, b in archive.files]


# ---------------------------------------------------------------------------
# The values of a variant that changes them (balance): steps 0a, 0b and 0c
# ---------------------------------------------------------------------------
def apply_skill_text_overrides(target, overrides):
    """The boxes of data_tables/balance_skill_text.xlsx put into a copy of the QoL skill table as rows edited by hand,
    so that the generator keeps them. Returns how many."""
    if not os.path.exists(overrides):
        return 0
    rows = openpyxl.load_workbook(overrides, read_only=True)['Skills'].iter_rows(values_only=True)
    head = next(rows)
    wanted = {(r[head.index('Category')], r[head.index('Filename')]): (r[head.index('Balance_Desc')], r[head.index('Balance_LvUp')])
              for r in rows if r and r[0]}
    wb = openpyxl.load_workbook(target)
    ws = wb['Skills']
    col = {c.value: k for k, c in enumerate(ws[1])}
    done = 0
    for row in ws.iter_rows(min_row=2):
        key = (row[col['Category']].value, row[col['Filename']].value)
        if key in wanted:
            desc, lvup = wanted[key]
            if desc:
                row[col['QoL_Desc']].value = desc
            if lvup:
                row[col['QoL_LvUp']].value = lvup
            row[col['Edited']].value = 'yes'
            done += 1
    if done != len(wanted):
        raise SystemExit(f'{os.path.basename(overrides)}: {len(wanted) - done} of its rows name no entry of the skill table')
    wb.save(target)
    return done


def regenerate_text(module, source_table, target, paths, overrides=None):
    """A text table generated again by its own generator from other sources. The table of the QoL variant is copied
    first, so the rows edited by hand keep their wording; overrides: the workbook of boxes worded by hand for this
    variant, applied to the copy. paths: {attribute of the generator: path to use}."""
    import shutil
    shutil.copyfile(source_table, target)
    if overrides:
        apply_skill_text_overrides(target, overrides)
    saved = {name: getattr(module, name) for name in paths}
    for name, path in paths.items():
        setattr(module, name, path)
    try:
        module.main()
    except SystemExit as stop:
        if stop.code not in (None, 0):
            return f'{os.path.basename(target)}: its generator stopped: {stop.code}'
    finally:
        for name, path in saved.items():
            setattr(module, name, path)
    return None


def prepare_values(name, variant, problems):
    """Steps 0a to 0c. Returns ({text table key: path of the regenerated table}, counts for the report) and leaves
    BACKUP_DIR on the folder of the built values."""
    global BACKUP_DIR
    import balance_values
    import balance_readback
    import generate_qol_skill_text
    import generate_qol_enemy_attack_text
    from sim import data as sim_data
    from sim.variant import balance_data
    base = os.path.join(BUILD_DIR, name, 'base')
    tables = os.path.join(BUILD_DIR, name, 'tables')
    rows = balance_values.live_rows()
    written, refused, bad, counts = balance_values.build(base, rows=rows)
    print(f"[0a] Values: {len(rows)} live rows of balance_changes.xlsx; written "
          + ', '.join(f'{t} {n}' for t, n in sorted(written.items())))
    for rid, reason in refused:
        problems.append(f'row {rid} cannot be written: {reason}')
    problems.extend(bad)
    if problems:
        return {}, {}
    print(f"     {counts['fields']} fields in {counts['changed']} of {counts['packs']} packs; {counts['bytes']} bytes differ "
          f"from the originals, every one inside a field a row wrote")
    os.makedirs(tables, exist_ok=True)
    problems.extend(f'extraction of the built values: {p}' for p in balance_readback.extract(base, os.path.join(tables, 'source_of_truth.xlsx')))
    differences, compared = balance_readback.compare(
        balance_readback.built_data(base, os.path.join(tables, 'source_of_truth.xlsx')), balance_data(sim_data.game_data()))
    problems.extend(f'the build and the simulator differ: {d}' for d in differences)
    if problems:
        return {}, {}
    print('[0b] Read back: the built packs hold what the simulator plays (' + ', '.join(f'{n} {k}' for k, n in compared.items()) + ')')
    paths = {'skill_text': os.path.join(tables, 'skill_text.xlsx'),
             'enemy_attack_text': os.path.join(tables, 'enemy_attack_text.xlsx')}
    for key, module, sources in (
            ('skill_text', generate_qol_skill_text, {'SOURCE_PATH': os.path.join(tables, 'source_of_truth.xlsx')}),
            ('enemy_attack_text', generate_qol_enemy_attack_text, {'BACKUP_PATH': os.path.join(base, ENEMY_PCK)})):
        stopped = regenerate_text(module, os.path.join(TABLES_DIR, variant[key]), paths[key],
                                  dict(sources, OUTPUT_PATH=paths[key]),
                                  os.path.join(TABLES_DIR, 'balance_skill_text.xlsx') if key == 'skill_text' else None)
        if stopped:
            problems.append(stopped)
    print(f"[0c] Text tables generated again from the built values: {', '.join(os.path.basename(p) for p in paths.values())}")
    BACKUP_DIR = base
    import text_checks
    text_checks.use_originals(base)          # the text of a doll skill is checked against the built action skill
    return paths, {'rows': len(rows), 'written': written, 'fields': counts['fields'], 'packs': counts['changed'],
                   'bytes': counts['bytes'], 'compared': compared}


def copy_value_only_packs(name, problems):
    """The packs no text step builds, taken as the values step left them."""
    import shutil
    base, copied = os.path.join(BUILD_DIR, name, 'base'), []
    for pack, sub in VALUE_ONLY_PCKS:
        target_dir = os.path.join(BUILD_DIR, name, 'Data', 'ENG', sub)
        os.makedirs(target_dir, exist_ok=True)
        source = os.path.join(base, pack)
        if not os.path.exists(source):
            problems.append(f'{pack}: not in the folder of the built values')
            continue
        shutil.copyfile(source, os.path.join(target_dir, os.path.basename(pack)))
        copied.append(os.path.join(sub, os.path.basename(pack)))
    return copied


def mark_built(report):
    """The live rows move to the state "built"; the checklist of the build is written."""
    import balance_values
    wb = openpyxl.load_workbook(balance_values.CHANGES)
    ws = wb['Changes']
    head = [c.value for c in ws[1]]
    state, table, rid, why = (head.index(n) for n in ('State', 'Table', 'ID', 'Why'))
    by_state, blocked, moved = collections.Counter(), [], 0
    for row in ws.iter_rows(min_row=2):
        if row[rid].value is None:
            continue
        if row[state].value == 'decided':
            row[state].value = 'built'
            moved += 1
        by_state[(row[table].value, row[state].value)] += 1
        if row[state].value == 'blocked':
            blocked.append((row[rid].value, str(row[why].value).split('. Was:')[0]))
    if moved:
        wb.save(balance_values.CHANGES)
    tables = sorted({t for t, _ in by_state})
    states = ('built', 'checked', 'decided', 'blocked', 'dropped')
    lines = ['# The build of the Balance variant (generated)', '',
             'Generated by `tools/build_variant.py balance`. Do not edit. Rows of `data_tables/balance_changes.xlsx` by '
             'table and state after the build: a live row is built once its value is in the packs of '
             '`build/balance/`, read back and equal to what the simulator plays.', '',
             f"**{sum(n for (_, s), n in by_state.items() if s in ('built', 'checked'))} of "
             f"{sum(n for (_, s), n in by_state.items() if s in ('built', 'checked', 'decided'))} live rows built; "
             f"{len(blocked)} blocked, waiting for a decision.**", '',
             '| Table | ' + ' | '.join(states) + ' |', '|---|' + '---|' * len(states)]
    for t in tables:
        lines.append(f'| {t} | ' + ' | '.join(str(by_state[(t, s)]) for s in states) + ' |')
    lines += ['', f"Values: {report['fields']} fields in {report['packs']} packs, {report['bytes']} bytes that differ from "
              'the originals, every one inside a field a row wrote. Compared with the simulator: '
              + ', '.join(f'{n} {k}' for k, n in report['compared'].items()) + '.', '',
              'Packs: ' + ', '.join(f'`{p}`' for p in report['files']) + '.', '',
              'Not installed: `python mod_project/tools/install_variant.py balance` puts it into the game folder.']
    if blocked:
        lines += ['', '## Blocked rows', '', '| Row | Why it cannot be written |', '|---|---|']
        lines += [f'| {r} | {w} |' for r, w in blocked]
    with open(BALANCE_REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return moved, lines[4]


def main():
    parser = argparse.ArgumentParser(description='Build one variant of the mod into mod_project/build/<variant>/.')
    parser.add_argument('variant', choices=sorted(VARIANTS))
    parser.add_argument('--no-install', action='store_true', help='build and verify only; leave the game folder alone')
    args = parser.parse_args()
    variant = VARIANTS[args.variant]
    out_dir = os.path.join(BUILD_DIR, args.variant, PARAM_SUBDIR)
    built_pcks = [pck for pck, _, _ in SKILL_PCKS.values()] + [ENCHANT_PCK, ITEM_PCK, ENEMY_PCK, FOOD_PCK, PARTY_PCK, JOINT_PCK, CLASS_PCK, RANK_PCK]
    print(f"=== Building variant '{args.variant}' ===")
    regenerated, value_report = {}, {}
    if variant.get('values'):
        early = []
        regenerated, value_report = prepare_values(args.variant, variant, early)
        if early:
            print(f"\n[FAIL] {len(early)} problem(s) in the values; no text was built:")
            for p in early[:60]:
                print(f"    {p}")
            sys.exit(1)
    table_of = lambda key: regenerated.get(key) or os.path.join(TABLES_DIR, variant[key])       # noqa: E731
    table_path = table_of('skill_text')
    enchant_path = table_of('enchant_text')
    item_path = table_of('item_text')
    enemy_path = table_of('enemy_attack_text')
    food_path = table_of('food_text')
    party_path = table_of('party_skill_text')
    joint_path = table_of('joint_skill_text')
    class_path = table_of('class_text')

    for path, generator in ((table_path, 'generate_qol_skill_text.py'), (enchant_path, 'generate_qol_enchant_text.py'),
                            (item_path, 'generate_qol_item_text.py'),
                            (enemy_path, 'generate_qol_enemy_attack_text.py'),
                            (food_path, 'generate_qol_food_text.py'),
                            (party_path, 'generate_qol_party_skill_text.py'),
                            (joint_path, 'generate_qol_joint_skill_text.py'),
                            (class_path, 'generate_qol_class_text.py')):
        if not os.path.exists(path):
            print(f"Error: {path} not found. Run tools/{generator} first.")
            sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    problems = []

    checked = self_test_writers(problems)
    print(f"[1] Writer self-test: {checked} original entries and {len(built_pcks)} archives rewritten unchanged")
    if problems:
        print("    Writers are not exact; nothing was built.")
    else:
        table, enchants, items = load_skill_text(table_path), load_enchant_text(enchant_path), load_item_text(item_path)
        enemy_attacks = load_enemy_attack_text(enemy_path)
        stats = build_skills(out_dir, table, problems)
        print(f"[2] Built {len(SKILL_PCKS)} skill PCKs: {stats['rewritten']} entries with new text, "
              f"{stats['kept']} kept byte-identical")
        stats = build_enchants(out_dir, enchants, problems)
        print(f"    Built {ENCHANT_PCK}: {stats['rewritten']} names with their figure, {stats['kept']} kept byte-identical")
        stats = build_items(out_dir, items, problems)
        print(f"    Built {ITEM_PCK}: {stats['rewritten']} descriptions with their data, {stats['kept']} kept byte-identical")
        stats = build_enemy_attacks(out_dir, enemy_attacks, problems)
        print(f"    Built {ENEMY_PCK}: {stats['rewritten']} entries with data on the data line, {stats['kept']} kept byte-identical")
        meals = load_food_text(food_path)
        stats = build_food(out_dir, meals, problems)
        print(f"    Built {FOOD_PCK}: {stats['rewritten']} effect lines with exact amounts, {stats['kept']} kept byte-identical")
        party = load_party_skill_text(party_path)
        stats = build_party_skills(out_dir, party, problems)
        print(f"    Built {PARTY_PCK}: {stats['rewritten']} effect lines with their bounds, {stats['kept']} kept byte-identical")
        joint = load_joint_skill_text(joint_path)
        stats = build_joint_skills(out_dir, joint, problems)
        print(f"    Built {JOINT_PCK}: {stats['rewritten']} sentences with their stored values, {stats['kept']} kept byte-identical")
        classes = load_class_text(class_path)
        stats = build_classes(out_dir, classes, problems)
        print(f"    Built {CLASS_PCK}: {stats['rewritten']} descriptions with role/weapon notes, {stats['kept']} kept byte-identical")
        voiced = check_game_voice([
            ('skills', [(k, r['vanilla_desc'] + ' ' + r['vanilla_lvup'], r['desc'] + ' ' + r['lvup']) for k, r in table.items()]),
            ('enchants', [(k, r['vanilla_name'], r['name']) for k, r in enchants.items()]),
            ('items', [(k, r['vanilla_desc'], r['desc']) for k, r in items.items()]),
            ('enemy attacks', [(k, r['vanilla_desc'], r['desc']) for k, r in enemy_attacks.items()]),
            ('meals', [(k, r['vanilla'], r['effect']) for k, r in meals.items()]),
            ('party skills', [(k, r['vanilla'], r['effect']) for k, r in party.items()]),
            ('joint skills', [(k, r['vanilla'], r['desc']) for k, r in joint.items()]),
            ('classes', [(k, r['vanilla'], r['desc']) for k, r in classes.items()]),
        ], problems)
        print(f"    Voice of the game: {voiced} modified texts hold no word that speaks from outside it")
        fixed, script_pcks = build_script_fixes(out_dir, problems)
        print(f"    Built {', '.join(script_pcks) or 'no script'}: {fixed} sentence(s) corrected, same length, nothing else touched")
        if variant.get('tutorial_text'):
            stats, tutorial_pcks = build_tutorials(out_dir, os.path.join(TABLES_DIR, variant['tutorial_text']), problems)
            print(f"    Built {', '.join(tutorial_pcks)}: {stats['written']} boxes of the lessons and the library rewritten "
                  f"({stats['voiced']} of them voiced), {stats['held']} held as the original; nothing else touched")
        build_weapon_ranks(out_dir)
        print(f"    Built {RANK_PCK}: rank names generated from their multiplier")
        if not problems:
            counts, untraced = verify_skills(out_dir, table, variant, problems)
            print(f"[3] Verified {counts['entries']} skill entries read back from disk:")
            print(f"    numeric data identical to the original in all of them")
            print(f"    {counts['modified']} modified boxes within {MAX_BOX_LINES} lines / {MAX_LINE} chars")
            print(f"    {counts['numbers']} figures in the text checked against the built binary")
            print(f"    {counts['words']} damage words, chances and values in line 1 checked against the built binary")
            if untraced:
                print(f"    {len(untraced)} figure(s) could not be tied to a table (hand-written notes, not checked):")
                for line in untraced[:20]:
                    print(f"        {line}")
            counts = verify_enchants(out_dir, enchants, variant, problems)
            print(f"    Verified {counts['entries']} enchantments: flags, prefix and suffix identical to the original;")
            print(f"    {counts['sourced']} names carry a figure from a player guide (the binary holds none), "
                  f"{counts['hand worded']} worded by hand (not checked)")
            counts = verify_items(out_dir, items, variant, problems)
            print(f"    Verified {counts['entries']} items: values and names identical to the original;")
            print(f"    {counts['numbers']} pieces of item data checked against the built binary; original sentences intact")
            counts = verify_enemy_attacks(out_dir, enemy_attacks, variant, problems)
            print(f"    Verified {counts['entries']} enemy attacks: values and names identical to the original; prose identical")
            print(f"    except where a figure or word was corrected to what the data holds;")
            print(f"    {counts['numbers']} figures on the data line and in corrected prose checked against the built binary")
            counts = verify_food(out_dir, meals, variant, problems)
            print(f"    Verified {counts['entries']} meals: values, names and flavour lines identical; {counts['numbers']} amounts checked")
            counts = verify_party_skills(out_dir, party, variant, problems)
            print(f"    Verified {counts['entries']} party skills: values, names and members identical; "
                  f"{counts['numbers']} bounds from a player guide (the binary holds none)")
            counts = verify_joint_skills(out_dir, joint, variant, problems)
            print(f"    Verified {counts['entries']} joint skills: values, names and messages identical; "
                  f"{counts['numbers']} values in the text checked against the built binary")
            counts = verify_classes(out_dir, classes, variant, problems)
            print(f"    Verified {counts['entries']} classes: code, name and numeric data identical; "
                  f"{counts['modified']} descriptions clarified")
            labels = verify_weapon_ranks(out_dir, variant, problems)
            print(f"    Verified {len(labels)} weapon ranks: multipliers identical to the original, "
                  f"each label shows its own multiplier")
            print(f"        {', '.join(labels)}")

    if problems:
        print(f"\n[FAIL] {len(problems)} problem(s):")
        for p in problems[:40]:
            print(f"    {p}")
        if len(problems) > 40:
            print(f"    ... and {len(problems) - 40} more")
        sys.exit(1)
    copied = []
    if variant.get('values'):
        copied = copy_value_only_packs(args.variant, problems)
        if problems:
            print(f"\n[FAIL] {len(problems)} problem(s):")
            for p in problems:
                print(f"    {p}")
            sys.exit(1)
        # the last check, on the packs that would be installed: read back with their texts, they still hold what the
        # simulator plays
        import balance_readback
        from sim import data as sim_data
        from sim.variant import balance_data
        base, tables = os.path.join(BUILD_DIR, args.variant, 'base'), os.path.join(BUILD_DIR, args.variant, 'tables')
        final_source = os.path.join(tables, 'final_source_of_truth.xlsx')
        problems.extend(f'extraction of the delivered packs: {p}' for p in balance_readback.extract_final(base, out_dir, final_source))
        delivered = balance_readback.built_data(os.path.join(BUILD_DIR, args.variant, 'Data', 'ENG'), final_source)
        differences, compared = balance_readback.compare(delivered, balance_data(sim_data.game_data()))
        problems.extend(f'the delivered packs and the simulator differ: {d}' for d in differences)
        if problems:
            print(f"\n[FAIL] {len(problems)} problem(s):")
            for p in problems[:40]:
                print(f"    {p}")
            sys.exit(1)
        print('[4] Delivered packs read back: they hold what the simulator plays (' + ', '.join(f'{n} {k}' for k, n in compared.items()) + ')')
        value_report['files'] = sorted(['Parameter/' + p for p in built_pcks] + [c.replace(os.sep, '/') for c in copied])
        moved, headline = mark_built(value_report)
        print(f"[5] {moved} row(s) moved to the state built; {os.path.relpath(BALANCE_REPORT, BASE_DIR)}: {headline.strip('*')}")
    print(f"\n[OK] Variant '{args.variant}' built in: {os.path.join(BUILD_DIR, args.variant)}")
    for pck in built_pcks:
        print(f"    {os.path.join(PARAM_SUBDIR, pck)}  ({os.path.getsize(os.path.join(out_dir, pck)):,} bytes)")
    for pck in copied:
        print(f"    {os.path.join('Data', 'ENG', pck)}  (values only)")
    if variant.get('values'):
        print(f"    Not installed. When the user says so: python mod_project/tools/install_variant.py {args.variant}")
    elif not args.no_install:
        result = install_variant.install(args.variant)
        install_variant.report(args.variant, *result)
        if result[2]:
            sys.exit(1)


if __name__ == "__main__":
    main()

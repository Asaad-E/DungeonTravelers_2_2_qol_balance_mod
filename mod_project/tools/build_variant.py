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
from pck_handler import PckArchive, SkillHelper, EnchantHelper, WeaponRankHelper, ItemHelper, EnemyAttackHelper
from extract_vanilla import SKILL_LAYOUTS
from text_checks import check_skill_text, check_item_text, check_enemy_attack_text, skill_tables
import magnitude_words
import enchant_values
import weapon_rank_labels
import install_variant
from generate_qol_enchant_text import MAX_NAME, MAX_NAME_ON_EQUIPMENT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
BUILD_DIR = os.path.join(BASE_DIR, 'build')
PARAM_SUBDIR = os.path.join('Data', 'ENG', 'Parameter')

MAX_LINE = 85
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
ENEMY_PCK = 'EnemyAttackData.pck'
ENEMY_HEADER = 0xA0
ENEMY_POINTERS = (8, 16, 24, 32)

VARIANTS = {
    'qol': {'skill_text': 'qol_skill_text.xlsx', 'enchant_text': 'qol_enchant_text.xlsx',
            'item_text': 'qol_item_text.xlsx', 'enemy_attack_text': 'qol_enemy_attack_text.xlsx',
            'numeric_changes_allowed': False},
}


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
                    if len(line) > MAX_LINE:
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
        if '\n' in now['desc'] or len(now['desc']) > MAX_LINE or '~' in now['desc']:
            problems.append(f"{label}: text must be one line of at most {MAX_LINE} chars without tilde")
        if re.search(r'\((?:small|medium|large)\)', now['desc']) and re.search(r'\(\+\d', now['desc']):
            problems.append(f"{label}: states both a vague size and an exact amount")
        found, verified = check_item_text(new, now['desc'], was['desc'])
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
def main():
    parser = argparse.ArgumentParser(description='Build one variant of the mod into mod_project/build/<variant>/.')
    parser.add_argument('variant', choices=sorted(VARIANTS))
    parser.add_argument('--no-install', action='store_true', help='build and verify only; leave the game folder alone')
    args = parser.parse_args()
    variant = VARIANTS[args.variant]
    out_dir = os.path.join(BUILD_DIR, args.variant, PARAM_SUBDIR)
    table_path = os.path.join(TABLES_DIR, variant['skill_text'])
    enchant_path = os.path.join(TABLES_DIR, variant['enchant_text'])
    item_path = os.path.join(TABLES_DIR, variant['item_text'])
    enemy_path = os.path.join(TABLES_DIR, variant['enemy_attack_text'])
    built_pcks = [pck for pck, _, _ in SKILL_PCKS.values()] + [ENCHANT_PCK, ITEM_PCK, ENEMY_PCK, RANK_PCK]

    print(f"=== Building variant '{args.variant}' ===")
    for path, generator in ((table_path, 'generate_qol_skill_text.py'), (enchant_path, 'generate_qol_enchant_text.py'),
                            (item_path, 'generate_qol_item_text.py'),
                            (enemy_path, 'generate_qol_enemy_attack_text.py')):
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
    print(f"\n[OK] Variant '{args.variant}' built in: {os.path.join(BUILD_DIR, args.variant)}")
    for pck in built_pcks:
        print(f"    {os.path.join(PARAM_SUBDIR, pck)}  ({os.path.getsize(os.path.join(out_dir, pck)):,} bytes)")
    if not args.no_install:
        result = install_variant.install(args.variant)
        install_variant.report(args.variant, *result)
        if result[2]:
            sys.exit(1)


if __name__ == "__main__":
    main()

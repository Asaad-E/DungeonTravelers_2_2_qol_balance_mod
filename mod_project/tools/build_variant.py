"""
Variant build.

Compiles one variant of the mod into mod_project/build/<variant>/ (never into the game
install) and verifies the result before reporting success.

    python mod_project/tools/build_variant.py qol

Variants
  qol   Shows more information about the base game and changes no value.
        Built so far: the four skill PCKs, from data_tables/qol_skill_text.xlsx.

The build fails (exit code 1) when
  * the PCK writers no longer reproduce the original files byte for byte,
  * the text table was generated from other backups than the ones being built,
  * any numeric field of a built entry differs from the original (QoL rule),
  * a built text differs from the table, breaks the box limits, or
  * a figure shown in a text differs from the value stored in the built binary (tools/text_checks.py).
"""
import os
import re
import sys
import struct
import argparse
import collections
import openpyxl
from pck_handler import PckArchive, SkillHelper
from extract_vanilla import SKILL_LAYOUTS
from text_checks import check_skill_text

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

VARIANTS = {
    'qol': {'skill_text': 'qol_skill_text.xlsx', 'numeric_changes_allowed': False},
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


# ---------------------------------------------------------------------------
# Step 1: the writers must reproduce the originals exactly
# ---------------------------------------------------------------------------
def self_test_writers(problems):
    checked = 0
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


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='Build one variant of the mod into mod_project/build/<variant>/.')
    parser.add_argument('variant', choices=sorted(VARIANTS))
    args = parser.parse_args()
    variant = VARIANTS[args.variant]
    out_dir = os.path.join(BUILD_DIR, args.variant, PARAM_SUBDIR)
    table_path = os.path.join(TABLES_DIR, variant['skill_text'])

    print(f"=== Building variant '{args.variant}' ===")
    if not os.path.exists(table_path):
        print(f"Error: {table_path} not found. Run tools/generate_qol_skill_text.py first.")
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    problems = []

    checked = self_test_writers(problems)
    print(f"[1] Writer self-test: {checked} original entries and {len(SKILL_PCKS)} archives rewritten unchanged")
    if problems:
        print("    Writers are not exact; nothing was built.")
    else:
        table = load_skill_text(table_path)
        stats = build_skills(out_dir, table, problems)
        print(f"[2] Built {len(SKILL_PCKS)} skill PCKs: {stats['rewritten']} entries with new text, "
              f"{stats['kept']} kept byte-identical")
        if not problems:
            counts, untraced = verify_skills(out_dir, table, variant, problems)
            print(f"[3] Verified {counts['entries']} entries read back from disk:")
            print(f"    numeric data identical to the original in all of them")
            print(f"    {counts['modified']} modified boxes within {MAX_BOX_LINES} lines / {MAX_LINE} chars")
            print(f"    {counts['numbers']} figures in the text checked against the built binary")
            if untraced:
                print(f"    {len(untraced)} figure(s) could not be tied to a table (hand-written notes, not checked):")
                for line in untraced[:20]:
                    print(f"        {line}")

    if problems:
        print(f"\n[FAIL] {len(problems)} problem(s):")
        for p in problems[:40]:
            print(f"    {p}")
        if len(problems) > 40:
            print(f"    ... and {len(problems) - 40} more")
        sys.exit(1)
    print(f"\n[OK] Variant '{args.variant}' built in: {os.path.join(BUILD_DIR, args.variant)}")
    for category, (pck, _, _) in SKILL_PCKS.items():
        print(f"    {os.path.join(PARAM_SUBDIR, pck)}  ({os.path.getsize(os.path.join(out_dir, pck)):,} bytes)")


if __name__ == "__main__":
    main()

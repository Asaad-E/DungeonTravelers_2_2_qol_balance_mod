"""
Which class learns which skill, and at what cost.

A skill file carries, after its effect slots, seven ints the workbook keeps as "Trailer". Read in the code:
    [1], [2]  the animation of the skill (0x56cec0)
    [3]       a mask of classes: bit N set means the class with id N learns the skill. The program builds the
              skill list of a class with it (0x56dc10: test [record + 0x1f8 / 0x240 / 0xe0], 1 << class; those are
              the file offsets 0x1E0 of a technique, 0x228 of a spell, 0xC8 of a passive)
    [4]       the pattern of the action (Action::CActionSkill::_CreatePattern, 0x41e060): 10, 11, 12 and 14 are
              the random moves (tools/random_move_data.py)
The hidden skills (the action of a doll, the results of a random move) have an empty mask.

The field the workbook calls Group_0x30 is a set of flags. For a technique: bits 0 to 3 are its range (short, mid,
long, none; 0x418227 reads bit 0 as range 0, and exactly one of the four is set in every technique), bit 4 "can be
used in battle", bit 5 "can be used on the map" (the three map skills have it without bit 4). For a spell the same
two flags sit one bit lower (bits 3 and 4) and the low three bits are not a range.

    python tools/skill_tree_data.py [class name]      prints the skills of every class, or of one
"""
import os
import sys

import openpyxl

import class_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx')
CLASS_MASK, PATTERN = 3, 4                  # positions in the trailer
RANGE_BITS = {1: 'short', 2: 'mid', 4: 'long', 8: 'none'}
LEVELS = [f'Lv{k}' for k in range(1, 11)]


def _rows(sheet):
    it = openpyxl.load_workbook(WORKBOOK, read_only=True)[sheet].iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it]


def skills():
    """[{'category', 'id', 'name', 'levels', 'classes': [class ids], 'pattern', 'range' (techniques), 'sp': per level}]"""
    costs = {}
    for r in _rows('SkillLevels'):
        if r['Field'] == 'sp_cost':
            costs[(r['Category'], r['Skill_ID'])] = [r[k] for k in LEVELS if r[k] is not None]
    found = []
    for r in _rows('Skills'):
        trailer = [int(x) for x in str(r['Trailer']).split(',')]
        mask = trailer[CLASS_MASK] & 0xFFFFFFFF
        group = r['Group_0x30']
        found.append({'category': r['Category'], 'id': r['Skill_ID'], 'name': r['Name'], 'levels': r['Levels'],
                      'classes': [bit for bit in range(32) if mask >> bit & 1], 'pattern': trailer[PATTERN],
                      'range': RANGE_BITS.get(group & 0xF) if r['Category'] == 'Technique' and group is not None else None,
                      'sp': costs.get((r['Category'], r['Skill_ID']), [])[:r['Levels'] or 0]})
    return found


def by_class():
    """{class id: [skill dicts]} in the order of the skill files."""
    tree = {}
    for skill in skills():
        for class_id in skill['classes']:
            tree.setdefault(class_id, []).append(skill)
    return tree


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    names = class_data.class_names()
    wanted = ' '.join(sys.argv[1:]).lower()
    for class_id, learned in sorted(by_class().items()):
        if wanted and names.get(class_id, '').lower() != wanted:
            continue
        print(f"{names.get(class_id, class_id)}: {len(learned)} skills, {sum(sum(s['sp']) for s in learned)} SP to max them all")
        for s in learned:
            print(f"    {s['category']:9s} {s['name']:26s} levels {s['levels']:2d}  SP {s['sp']}")


if __name__ == '__main__':
    main()

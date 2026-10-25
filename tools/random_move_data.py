"""
Random moves: what Roulette Circus, Magic Box, Showtime and Heaven or Hell can turn into, and how likely.

A skill with one of the effects 152 to 155 does nothing by itself: when its action is built
(Action::CActionSkill::_CreatePattern, 0x41e060, cases 10, 11, 12 and 14) the code rolls on a table of hidden
skills and performs the one that comes out (0x42db00). Each skill has two tables in the executable: the usual
one, and one used when the user has the status Triple Joker (effect 315). An entry is twelve bytes: the id of
the hidden skill, a -1, and its weight; the roll is weighted (0x505ad0).

One exception is written in the code (0x41e3c2 - 0x41e4d9): when Magic Box comes out as its Genjimaru result
(effect 427) and Genjimaru is already in the battle, the result with no effect of the same table is used.

    python tools/random_move_data.py        prints the four tables
"""
import os
import struct
import sys

import openpyxl

from exe_reader import Exe

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx')
ENTRY = 12
JOKER_EFFECT = 315
# effect of the skill: (usual table, table with Triple Joker, entries), as pushed at 0x41e342, 0x41e387, 0x41e4ed, 0x41e571
TABLES = {152: (0x64f8c0, 0x64f930, 9),
          153: (0x64fa28, 0x64f9a0, 11),
          154: (0x64fb50, 0x64fab0, 13),
          155: (0x64f458, 0x64f440, 2)}


def _rows(sheet):
    it = openpyxl.load_workbook(WORKBOOK, read_only=True)[sheet].iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it]


def _table(exe, address, entries):
    return [struct.unpack('<iii', exe.read(address + ENTRY * k, ENTRY)) for k in range(entries)]


def random_moves(exe=None):
    """[{'effect', 'skill', 'name', 'results': [{'skill', 'target', 'attribute', 'effects': [(id, name)],
          'weight', 'joker_weight', 'chance', 'joker_chance'}]}]; chances are shares of the sum of the weights"""
    exe = exe or Exe()
    if not exe.data:
        return []
    skills = [r for r in _rows('Skills') if r['Category'] in ('Technique', 'Magic')]   # Heaven or Hell is a spell
    by_id = {r['Skill_ID']: r for r in skills}
    names = {r['Effect_ID']: r['Name'] or r['Game_Name'] for r in _rows('Effects')}
    ids = lambda row: [int(x) for x in str(row['Effect_IDs'] or '').replace('None', '').split(',') if x.strip()]
    effects_of = {r['Skill_ID']: [(e, names.get(e)) for e in ids(r) if e] for r in skills}
    found = []
    for effect, (usual, joker, entries) in TABLES.items():
        parent = next(r for r in skills if effect in [e for e, _ in effects_of.get(r['Skill_ID'], [])])
        plain, with_joker = _table(exe, usual, entries), _table(exe, joker, entries)
        total, joker_total = sum(w for _, _, w in plain), sum(w for _, _, w in with_joker)
        results = []
        for (skill, _, weight), (joker_skill, _, joker_weight) in zip(plain, with_joker):
            assert skill == joker_skill, (effect, skill, joker_skill)
            info = by_id[skill]
            results.append({'skill': skill, 'target': info['Target'], 'attribute': info['Attr'], 'effects': effects_of.get(skill, []),
                            'weight': weight, 'joker_weight': joker_weight,
                            'chance': weight / total, 'joker_chance': joker_weight / joker_total})
        found.append({'effect': effect, 'skill': parent['Skill_ID'], 'name': parent['Name'], 'results': results})
    return found


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for move in random_moves():
        print(f"{move['name']} (skill {move['skill']}, effect {move['effect']})")
        for r in move['results']:
            effects = ', '.join(f'{e} {n}' for e, n in r['effects']) or 'nothing'
            print(f"    {r['chance']:6.1%}  with Triple Joker {r['joker_chance']:6.1%}  skill {r['skill']}: {r['target']}, {r['attribute']}; {effects}")


if __name__ == '__main__':
    main()

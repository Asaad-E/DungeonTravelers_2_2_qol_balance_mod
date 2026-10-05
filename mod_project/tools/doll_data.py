"""
Dolls of the Doll Master line: what each doll skill really does.

A doll skill creates a unit of its own (Battle code 0x484150; classes CGamePlayerStatusETCDoll and its two
siblings). Read from the code (docs/FORMULAS.md 11):
    * the doll is born with 9,999 HP and max HP (0x4fd922): damage does not end it; it lasts the turns of
      effect 147 of its skill
    * on its turn it performs a hidden skill, at the level of the doll skill, picked at random from a list the
      code gives it (0x4fd980); the list is one skill for five dolls and five spells for Musiy
    * its stats are computed by the function of a character (0x4f5d60 through slot 0x104 of its class)
    * a physical hit by a doll adds Doll Mastery and the doll enchantments to its modifiers, and uses the range
      of the doll instead of a weapon's (0x44b4fd, 0x44bb1c); a heal adds twenty times those (0x48d7a1)

The numbers of a doll therefore live in two skill files each: the doll skill (turns, TP cost, speed of the cast)
and its hidden action (power, ailment chance, heal power, spell power). The value of the doll effect itself
(228 to 233) is not what the action uses.

    python mod_project/tools/doll_data.py        prints every doll with its action
"""
import os
import sys

import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx')
SHORT, MID, LONG = 'short', 'mid', 'long'
# doll skill id: (doll effect id, category of its actions, action skill ids, range of its physical hits)
# skill ids and effect ids as 0x484150 pairs them (0x484534 - 0x484883); ranges from 0x44bb1c
DOLLS = {95: (228, 'Technique', (101,), SHORT),
         96: (229, 'Technique', (102,), MID),
         97: (230, 'Technique', (104,), None),
         98: (231, 'Technique', (103,), LONG),
         99: (232, 'Technique', (105,), None),
         100: (233, 'Magic', (235, 236, 237, 238, 239), None)}
DOLL_HP = 9999                 # 0x4fd922, 0x4fd929
TURNS_EFFECT, COUNT_EFFECT, MASTERY_EFFECT = 147, 146, 286
LEVELS = [f'Lv{k}' for k in range(1, 11)]


def _rows(sheet):
    ws = openpyxl.load_workbook(WORKBOOK, read_only=True)[sheet]
    it = ws.iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it]


def dolls():
    """[{'skill', 'name', 'effect', 'range', 'turns': per level, 'tp_cost', 'speed',
         'actions': [{'skill', 'name', 'target', 'attribute', 'speed', 'effects': [(effect id, name, per level)]}]}]"""
    skills = {(r['Category'], r['Skill_ID']): r for r in _rows('Skills')}
    levels = {}
    for r in _rows('SkillLevels'):
        levels.setdefault((r['Category'], r['Skill_ID']), []).append(r)
    series = lambda row: [row[k] for k in LEVELS if row[k] is not None]
    found = []
    for skill_id, (effect, category, actions, reach) in DOLLS.items():
        own = levels[('Technique', skill_id)]
        field = lambda name: next(series(r) for r in own if r['Field'] == name)
        doll = {'skill': skill_id, 'name': skills[('Technique', skill_id)]['Name'], 'effect': effect, 'range': reach,
                'turns': next(series(r) for r in own if r['Effect_ID'] == TURNS_EFFECT),
                'tp_cost': field('tp_cost'), 'speed': field('speed'), 'actions': []}
        for action in actions:
            info = skills[(category, action)]
            rows = levels[(category, action)]
            doll['actions'].append({'skill': action, 'name': info['Name'], 'target': info['Target'], 'attribute': info['Attr'],
                                    'speed': next(series(r) for r in rows if r['Field'] == 'speed'),
                                    'effects': [(r['Effect_ID'], r['Effect_Name'], series(r)) for r in rows
                                                if r['Effect_ID'] is not None]})
        found.append(doll)
    return found


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for doll in dolls():
        print(f"{doll['name']} (skill {doll['skill']}): lasts {doll['turns']} turns, TP {doll['tp_cost']}, range {doll['range']}")
        for action in doll['actions']:
            print(f"    {action['name']}: {action['target']}, {action['attribute']}, speed {action['speed'][0]}-{action['speed'][-1]}")
            for effect, name, values in action['effects']:
                print(f'        effect {effect} ({name}): {values}')


if __name__ == '__main__':
    main()

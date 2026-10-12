"""
Characters: what each girl starts with and how her Pep moves.

Data/ENG/Character/Character.pck holds one package per character (a copy is kept in backups/Character). The game
reads three files of each (0x459ff0): PlayerData.txt (names of her pictures), InitialData.bin and
PlayerStatusData.bin. The last one is the table the code calls by character id (program global 0x738a08).

PlayerStatusData.bin, 144 bytes, as the code reads it:
    0x00 id            0x04 base class (ClassData id)      0x08 unique skill (UniqueSkillData id)
    0x0C 1 for an adult (the actions with effect 149 or 150 test it, 0x44b01e)
    0x10 count and 0x14.. up to three FoodMenu ids; 0x20 count and 0x24.. up to three more
                       (by their place next to the food events of Pep: liked and disliked meals; not followed in code)
    0x30, 0x34, 0x38   three ints, not identified
    0x3C twenty-one floats: what each event adds to her Pep. The code indexes them by event
                       (0x4e4b70 for the whole party, the other writers for one member); PEP_EVENTS names the ones
                       whose trigger was read

InitialData.bin, 64 bytes: id, class, -1, starting EXP, then four (equipment id, upgrade level) pairs, two skill ids
and their two levels. Only the EXP and the class are relied on here.

Pep itself (a float of the character object, 0xd8) is kept between 70 and 130 by 0x4f69e0, which also applies what
fixes it: a piece of enchantment 201 holds it at 70, a piece of 200 keeps it at 100 or more, a piece of 195 holds it
at 130, and a status of effect 81 sets it to its value. docs/FORMULAS.md 13 lists what reads it.

    python tools/character_data.py        prints every character
"""
import os
import re
import struct
import sys

from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARACTER_PCK = os.path.join(BASE_DIR, 'backups', 'Character', 'Character.pck')
PEP_MIN, PEP_MAX = 70.0, 130.0                      # 0x4f69e0
PEP_OFFSET, PEP_COUNT = 0x3C, 21
# index of the float: the trigger read in code, with the address that adds it
PEP_EVENTS = {0: 'fells an enemy (0x43abde)',
              1: 'falls in battle (0x43a6be)',
              2: 'lands a critical hit (0x47ec5a)',
              3: 'takes a critical hit (0x47eb5a)',
              7: 'ends a battle with an ailment (0x509662)',
              13: 'treasure box, results 1 and 2 (0x507e70)',
              14: 'treasure box, result 3 (0x507e6b)',
              15: 'start of a battle, first case (0x44924d)',
              16: 'start of a battle, second case (0x4492c3)',
              17: 'a meal, first case (0x509a8f)',
              18: 'a meal, second case (0x509bdf)',
              19: 'a counter reaches 100 (0x4c5b5c)',
              20: 'a counter reaches 300 (0x4c5b70)'}
PARTY_WIDE = (6, 13, 14, 15, 16, 19, 20)            # added to every living member at once (0x4e4b70)


def read_character(files):
    """One character from the files of her package, or None when she has no status record."""
    status, initial = files.get('PlayerStatusData.bin'), files.get('InitialData.bin')
    if not status:
        return None
    name = re.search(rb'Name="([^"]*)"', files.get('PlayerData.txt', b''))
    ints = struct.unpack_from('<15i', status, 0)
    foods = lambda at: [f for f in ints[at + 1:at + 1 + max(0, min(ints[at], 3))] if f != -1]
    character = {'id': ints[0], 'name': name.group(1).decode('utf-8') if name else '', 'base_class': ints[1],
                 'unique_skill': ints[2] if ints[2] != -1 else None, 'flag': ints[3],
                 'foods_first': foods(4), 'foods_second': foods(8), 'raw_30': list(ints[12:15]),
                 'pep': list(struct.unpack_from(f'<{PEP_COUNT}f', status, PEP_OFFSET)),
                 'start_class': None, 'start_exp': None}
    if initial:
        first = struct.unpack_from('<4i', initial, 0)
        character['start_class'], character['start_exp'] = first[1], first[3]
    return character


def characters(path=CHARACTER_PCK):
    found = []
    for _, blob in PckArchive(path).files:
        character = read_character(dict(PckArchive.from_bytes(blob).files))
        if character and character['unique_skill'] is not None:      # entry 0 is the player, who never fights
            found.append(character)
    return found


def clamp_pep(value):
    return max(PEP_MIN, min(PEP_MAX, value))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for c in characters():
        print(f"{c['id']:2d} {c['name']:11s} class {c['base_class']:2d} unique {c['unique_skill']} start EXP {c['start_exp']}")
        print('     Pep: ' + ', '.join(f'{k}:{v:g}' for k, v in enumerate(c['pep']) if v))


if __name__ == '__main__':
    main()

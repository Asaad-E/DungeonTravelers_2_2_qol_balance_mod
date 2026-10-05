"""
Random encounters of every floor: reader of Data/ENG/Dungeon/stNN/Data.pck (backed up in backups/Dungeon/stNN/).

Data.pck of a dungeon holds, per floor, a parameter file (StNN_FFFF.bin), its map and one .epd file per formation
(where each enemy stands on screen, 24 records of six ints; not read here).

Parameter file of a floor (little endian), as far as it is read:
    0xA0        pointer (8 bytes) to the block of the floor
    block+0x5C  number of formations
    block+0x60  pointer (8 bytes) to the formations, 88 bytes each:
        0x00  number of the formation, from 1
        0x04  twelve enemy ids, -1 where unused
        0x34  twelve bytes, one per enemy: 1 when it stands in the front row, 0 in the back row
              (a lone enemy always has 1; the party's side sets the same flag at 0x43db3c)
        0x40  chance of the formation in percent (they add up to 100 on every floor)
        0x44  five more ints, not decoded (-1, an offset, 0, 1, -1 on every formation)
The rest of the file (the tables of what its chests hold, the events) is not decoded.

    python mod_project/tools/floor_data.py [st02]      prints the formations of those dungeons
"""
import os
import re
import struct
import sys
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUNGEON_DIR = os.path.join(BASE_DIR, 'backups', 'Dungeon')
BLOCK_POINTER, COUNT, FORMATIONS, RECORD = 0xA0, 0x5C, 0x60, 88
ENEMY_SLOTS = 12


def read_floor(blob):
    """Formations of a floor: [{'number', 'chance', 'enemies': [(enemy id, in front row)]}]."""
    blob = bytes(blob)
    block = struct.unpack_from('<Q', blob, BLOCK_POINTER)[0]
    count = struct.unpack_from('<i', blob, block + COUNT)[0]
    start = struct.unpack_from('<Q', blob, block + FORMATIONS)[0]
    found = []
    for k in range(count):
        base = start + RECORD * k
        number = struct.unpack_from('<i', blob, base)[0]
        ids = struct.unpack_from(f'<{ENEMY_SLOTS}i', blob, base + 0x04)
        front = blob[base + 0x34:base + 0x34 + ENEMY_SLOTS]
        found.append({'number': number, 'chance': struct.unpack_from('<i', blob, base + 0x40)[0],
                      'enemies': [(enemy, bool(front[slot])) for slot, enemy in enumerate(ids) if enemy != -1]})
    return found


def floors(directory=DUNGEON_DIR):
    """Every floor with formations: [{'dungeon': 'st02', 'floor': 'St02_0010', 'formations': [...]}]."""
    found = []
    for dungeon in sorted(os.listdir(directory)):
        path = os.path.join(directory, dungeon, 'Data.pck')
        if not re.fullmatch(r'st\d+', dungeon) or not os.path.exists(path):
            continue
        for name, blob in PckArchive(path).files:
            if name.endswith('.bin'):
                formations = read_floor(blob)
                if formations:
                    found.append({'dungeon': dungeon, 'floor': name[:-4], 'formations': formations})
    return found


def main():
    import enemy_data
    sys.stdout.reconfigure(encoding='utf-8')
    names = {e['id']: f"{e['name']} L{e['level']}" for e in enemy_data.enemies()}
    for floor in floors():
        if sys.argv[1:] and floor['dungeon'] not in sys.argv[1:]:
            continue
        print(floor['floor'])
        for f in floor['formations']:
            print(f"  {f['number']:2d}  {f['chance']:3d}%  " + ', '.join(names[e] + ('' if front else ' (back)') for e, front in f['enemies']))


if __name__ == '__main__':
    main()

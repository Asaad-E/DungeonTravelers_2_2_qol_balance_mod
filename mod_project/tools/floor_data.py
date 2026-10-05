"""
Random encounters of every floor: reader of the floor parameter files of Data/ENG/Dungeon/stNN/Data.pck.

Data.pck of a dungeon holds, per floor, a parameter file (StNN_FFFF.bin), its map and one .epd file per formation
(where each enemy stands on screen, 24 records of six ints; not read here). The vanilla parameter files of every
dungeon are kept together in backups/Dungeon/floor_parameters.zip (the whole Data.pck files are 15 MB of maps
and textures); `python mod_project/tools/floor_data.py --collect` rebuilds that file from an unmodified game.

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
import zipfile
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOOR_ZIP = os.path.join(BASE_DIR, 'backups', 'Dungeon', 'floor_parameters.zip')
GAME_DUNGEON_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Dungeon')
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


def collect(game_dir=GAME_DUNGEON_DIR, path=FLOOR_ZIP):
    """Copies the parameter file of every floor of the game into one archive, as stNN/StNN_FFFF.bin."""
    count = 0
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for dungeon in sorted(os.listdir(game_dir)):
            data = os.path.join(game_dir, dungeon, 'Data.pck')
            if not re.fullmatch(r'st\d+', dungeon) or not os.path.exists(data):
                continue
            for name, blob in PckArchive(data).files:
                if name.endswith('.bin'):
                    archive.writestr(zipfile.ZipInfo(f'{dungeon}/{name}', (2000, 1, 1, 0, 0, 0)), bytes(blob))
                    count += 1
    return count


def floors(path=FLOOR_ZIP):
    """Every floor with formations: [{'dungeon': 'st02', 'floor': 'St02_0010', 'formations': [...]}]."""
    found = []
    with zipfile.ZipFile(path) as archive:
        for entry in sorted(archive.namelist()):
            dungeon, name = entry.split('/')
            formations = read_floor(archive.read(entry))
            if formations:
                found.append({'dungeon': dungeon, 'floor': name[:-4], 'formations': formations})
    return found


def main():
    import enemy_data
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1:] == ['--collect']:
        print(f'{collect()} floor parameter files written to {FLOOR_ZIP}')
        return
    names = {e['id']: f"{e['name']} L{e['level']}" for e in enemy_data.enemies()}
    for floor in floors():
        if sys.argv[1:] and floor['dungeon'] not in sys.argv[1:]:
            continue
        print(floor['floor'])
        for f in floor['formations']:
            print(f"  {f['number']:2d}  {f['chance']:3d}%  " + ', '.join(names[e] + ('' if front else ' (back)') for e, front in f['enemies']))


if __name__ == '__main__':
    main()

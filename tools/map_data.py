"""
Maps of the floors: reader of the StNN_FFFF.map files of Data/ENG/Dungeon/stNN/Data.pck.

A copy of every map is kept in backups/Dungeon/floor_maps.zip (`python tools/map_data.py --collect` rebuilds
it from an unmodified game). Read from the loader (0x4b55cf - 0x4b57d3) and the cell conversion (0x4afa40):

    0x00 a word (the format)    0x04 width    0x08 height    0x0C width * height cells of 42 bytes, row by row
    cell + 0   kind of the cell (0 to 11)                     -> +0x00 of the cell in memory
    cell + 2   first zone slot                               -> +0x08
    cell + 3   second zone slot                              -> +0x0C
    cell + 6   the zone of the floor the cell belongs to     -> +0x18 (its encounter table, docs/FORMULAS.md 14)
The rest of the 42 bytes (walls, doors, events) is not read here.

A zone slot of value 2 forbids magic (docs/FORMULAS.md 16.2); 3 and 5 raise and lower physical attack, 4 and 6 magic
attack, for every unit; 7 to 11 raise fire, water, wind, earth or lightning (2.5).

Events: a cell of kind 1 runs the event script whose index is its byte 1, in the list of script names of the floor
parameter file (count at 0x78, pointer at 0x80; a cell of kind 2 is a chest, its byte 1 the index of the chest table at
0x48/0x50). An event script (.adv.bin, in the StNN_FFFF.pck of Data.pck) starts a fixed battle with the command 0x1F
(bytes 1F 01 00, then the battle number as an int). Checked on Rousset 3F: the script that explains the anti-magic zone
stands on a cell of value 2, as do the two battles the Japanese wiki and the GameFAQs guide place in that zone.

    python tools/map_data.py             prints, per floor, the cells of each zone slot value
"""
import os
import re
import struct
import sys
import zipfile
from collections import Counter

from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_ZIP = os.path.join(BASE_DIR, 'backups', 'Dungeon', 'floor_maps.zip')
import mod_config                       # noqa: E402
GAME_DUNGEON_DIR = os.path.join(mod_config.data_dir(), __import__('game_profile').PROFILE['dungeon_subdir'])
_M = __import__('game_profile').layout('FloorMap')                # data_tables/record_layouts.json
HEADER, CELL = _M['header'], _M['cell']
NO_MAGIC = 2


EVENT_CELL, CHEST_CELL = 1, 2
SCRIPT_COUNT, SCRIPT_POINTER = _M['script_count'], _M['script_pointer']
BATTLE_COMMAND = bytes((0x1F, 0x01, 0x00))


def read_map(blob):
    """{'width', 'height', 'cells': [{'x', 'y', 'kind', 'index', 'slots': (a, b), 'zone'}]}"""
    b = bytes(blob)
    width, height = struct.unpack_from('<2i', b, 4)
    cells = []
    for y in range(height):
        for x in range(width):
            c = HEADER + (y * width + x) * CELL
            cells.append({'x': x, 'y': y, 'kind': b[c], 'index': b[c + 1], 'slots': (b[c + 2], b[c + 3]),
                          'zone': b[c + 6]})
    return {'width': width, 'height': height, 'cells': cells}


def script_names(params):
    """The event scripts of a floor, in the order the cells name them."""
    p = bytes(params)
    count, pointer = struct.unpack_from('<i', p, SCRIPT_COUNT)[0], struct.unpack_from('<Q', p, SCRIPT_POINTER)[0]
    names = []
    for k in range(count):
        at = struct.unpack_from('<Q', p, pointer + 8 * k)[0]
        names.append(p[at:p.find(b'\x00', at)].decode('utf-8', 'replace'))
    return names


def battles_of_script(blob):
    """The fixed battle numbers a script starts (command 0x1F)."""
    b, found, pos = bytes(blob), [], 0
    while True:
        pos = b.find(BATTLE_COMMAND, pos)
        if pos < 0 or pos + 7 > len(b):
            return found
        found.append(struct.unpack_from('<i', b, pos + 3)[0])
        pos += 1


def collect(game_dir=GAME_DUNGEON_DIR, path=MAP_ZIP):
    """Copies every map, and the event scripts of every floor, into one archive: stNN/StNN_FFFF.map and
    stNN/StNN_FFFF/<script>.adv.bin."""
    count = 0
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for dungeon in sorted(os.listdir(game_dir)):
            data = os.path.join(game_dir, dungeon, 'Data.pck')
            if not re.fullmatch(r'st\d+', dungeon) or not os.path.exists(data):
                continue
            for name, blob in PckArchive(data).files:
                if name.endswith('.map'):
                    archive.writestr(zipfile.ZipInfo(f'{dungeon}/{name}', (2000, 1, 1, 0, 0, 0)), bytes(blob))
                    count += 1
                elif re.fullmatch(r'St\d+_\d+\.pck', name):
                    for script, sblob in PckArchive.from_bytes(blob).files:
                        if script.endswith('.adv.bin'):
                            archive.writestr(zipfile.ZipInfo(f'{dungeon}/{name[:-4]}/{script}', (2000, 1, 1, 0, 0, 0)),
                                             bytes(sblob))
    return count


def maps(path=MAP_ZIP):
    """{floor name ('St06_0030'): read_map(...)}"""
    found = {}
    with zipfile.ZipFile(path) as archive:
        for entry in sorted(archive.namelist()):
            if entry.endswith('.map'):
                found[entry.split('/')[1][:-4]] = read_map(archive.read(entry))
    return found


def battle_cells(path=MAP_ZIP):
    """{(floor, fixed battle number): [{'x', 'y', 'slots', 'script'}]}: the event cells whose script starts that battle.
    A battle started by an event elsewhere (a town, a story scene) has no cell here."""
    import floor_data
    found = {}
    params = zipfile.ZipFile(floor_data.FLOOR_ZIP)
    with zipfile.ZipFile(path) as archive:
        entries = set(archive.namelist())
        for entry in sorted(entries):
            if not entry.endswith('.map'):
                continue
            dungeon, name = entry.split('/')
            floor = name[:-4]
            try:
                names = script_names(params.read(f'{dungeon}/{floor}.bin'))
            except KeyError:
                continue
            for cell in read_map(archive.read(entry))['cells']:
                if cell['kind'] != EVENT_CELL or cell['index'] >= len(names):
                    continue
                script = names[cell['index']]
                script_entry = f'{dungeon}/{floor}/{script}.adv.bin'
                if script_entry not in entries:
                    continue
                for number in battles_of_script(archive.read(script_entry)):
                    found.setdefault((floor, number), []).append(
                        {'x': cell['x'], 'y': cell['y'], 'slots': cell['slots'], 'zone': cell['zone'],
                         'script': script})
    return found


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1:] == ['--collect']:
        print(f'{collect()} maps written to {MAP_ZIP}')
        return
    for floor, m in maps().items():
        values = Counter(v for c in m['cells'] for v in c['slots'] if v)
        if values:
            print(floor, dict(sorted(values.items())))


if __name__ == '__main__':
    main()

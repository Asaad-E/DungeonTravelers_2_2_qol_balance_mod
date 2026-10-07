"""
Random encounters of every floor: reader of the floor parameter files of Data/ENG/Dungeon/stNN/Data.pck.

Data.pck of a dungeon holds, per floor, a parameter file (StNN_FFFF.bin), its map and one .epd file per formation
(where each enemy stands on screen, 24 records of six ints; not read here). The vanilla parameter files of every
dungeon are kept together in backups/Dungeon/floor_parameters.zip (the whole Data.pck files are 15 MB of maps
and textures); `python mod_project/tools/floor_data.py --collect` rebuilds that file from an unmodified game.

Parameter file of a floor (little endian), as far as it is read:
    0x28        number of fixed battles of the floor (the ones events start: bosses, quest targets)
    0x30        pointer (8 bytes) to them: the same 88-byte record as a formation, with chance 0
    0x98        number of zones of the floor (one to seven)
    0xA0        pointer (8 bytes) to the zones, 0xD0 bytes each
    zone+0x5C   number of formations of the zone
    zone+0x60   pointer (8 bytes) to its formations, 88 bytes each:
        0x00  number of the formation, from 1
        0x04  twelve enemy ids, -1 where unused
        0x34  twelve bytes, one per enemy: 1 when it stands in the front row, 0 in the back row
              (a lone enemy always has 1; the party's side sets the same flag at 0x43db3c)
        0x40  chance of the formation in percent (they add up to 100 in every zone)
        0x44  five more ints, not decoded (-1, an offset, 0, 1, -1 on every formation)
    zone+0x68   number of pieces of equipment the zone can give, and zone+0x70 a pointer (8 bytes) to them,
                36 bytes each: the equipment id, then four (lowest, highest) upgrade levels, one per kind of
                drop; -1 where the piece is not given for that kind. An enemy that drops a piece draws it with
                the number in its record (EnemyStatusData 0x80, 1 to 3): the code keeps the pieces whose lowest
                level for that kind is above 0, picks one with equal chances and gives it a level picked evenly
                between the two figures (0x555c70, called at 0x55862f with the zone of the cell)
    zone+0x1C   chance in percent of a random battle on each step taken in the zone (Dungeon::CDungeonBase::
                _CheckEncount, 0x4bc773; docs/FORMULAS.md 14)
    zone+0x20   five more chances in percent, of the special battles of the zone (0x4bc8a1 - 0x4bca73)
    zone+0xB8   five floats: the factors of the damage zones of the map (docs/FORMULAS.md 2.5), read at the
                start of a battle (0x44994d): physical attack up, magic attack up, physical attack down, magic
                attack down, and the factor of an element zone (the zone slots 3, 4, 5, 6 and 7 - 11 of a cell;
                docs/FORMULAS.md 2.5)
A cell of the map names its zone (offset 0x18 of its 0x230-byte record, 0x44993a); the map files are not read here.
Not decoded: the rest of a zone (what lies between 0x34 and 0x5C, the tables
of what its chests hold after 0x60) and the other tables of the header.

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
ZONE_COUNT, ZONE_POINTER, ZONE_SIZE, COUNT, FORMATIONS, RECORD = 0x98, 0xA0, 0xD0, 0x5C, 0x60, 88
FIXED_COUNT, FIXED_POINTER = 0x28, 0x30
ENEMY_SLOTS = 12
ZONE_FACTORS, FACTOR_NAMES = 0xB8, ('up_a', 'up_b', 'down_a', 'down_b', 'element')
ENCOUNTER = 0x1C               # the chance of a random battle per step, then the five special chances
EQUIPMENT_COUNT, EQUIPMENT_POINTER, EQUIPMENT_RECORD, DROP_KINDS = 0x68, 0x70, 0x24, 4


def read_equipment(blob, block):
    """Pieces a zone can give: [{'equipment': id, 'levels': {kind: (lowest, highest)}}], kinds without the piece left out."""
    count = struct.unpack_from('<i', blob, block + EQUIPMENT_COUNT)[0]
    start = struct.unpack_from('<Q', blob, block + EQUIPMENT_POINTER)[0]
    found = []
    for k in range(count):
        values = struct.unpack_from(f'<{1 + 2 * DROP_KINDS}i', blob, start + EQUIPMENT_RECORD * k)
        levels = {kind: (values[1 + 2 * kind], values[2 + 2 * kind]) for kind in range(DROP_KINDS)
                  if values[1 + 2 * kind] > 0}
        found.append({'equipment': values[0], 'levels': levels})
    return found


def read_formation(blob, base):
    number = struct.unpack_from('<i', blob, base)[0]
    ids = struct.unpack_from(f'<{ENEMY_SLOTS}i', blob, base + 0x04)
    front = blob[base + 0x34:base + 0x34 + ENEMY_SLOTS]
    return {'number': number, 'chance': struct.unpack_from('<i', blob, base + 0x40)[0],
            'enemies': [(enemy, bool(front[slot])) for slot, enemy in enumerate(ids) if enemy != -1]}


def read_fixed(blob):
    """Fixed battles of a floor, in the shape of formations."""
    blob = bytes(blob)
    start = struct.unpack_from('<Q', blob, FIXED_POINTER)[0]
    return [read_formation(blob, start + RECORD * k) for k in range(struct.unpack_from('<i', blob, FIXED_COUNT)[0])]


def read_floor(blob):
    """Zones of a floor, each a list of formations: [{'number', 'chance', 'enemies': [(enemy id, in front row)]}]."""
    return [zone[0] for zone in read_zones(blob)]


def read_zones(blob):
    """[(formations, {factor name: value}, {'encounter': percent per step, 'special': five percents})] for every zone."""
    blob = bytes(blob)
    zones = []
    first = struct.unpack_from('<Q', blob, ZONE_POINTER)[0]
    for zone in range(struct.unpack_from('<i', blob, ZONE_COUNT)[0]):
        block = first + ZONE_SIZE * zone
        count = struct.unpack_from('<i', blob, block + COUNT)[0]
        start = struct.unpack_from('<Q', blob, block + FORMATIONS)[0]
        found = [read_formation(blob, start + RECORD * k) for k in range(count)]
        factors = dict(zip(FACTOR_NAMES, struct.unpack_from('<5f', blob, block + ZONE_FACTORS)))
        chances = struct.unpack_from('<6i', blob, block + ENCOUNTER)
        zones.append((found, factors, {'encounter': chances[0], 'special': list(chances[1:]),
                                       'equipment': read_equipment(blob, block)}))
    return zones


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
    """Every zone with formations: [{'dungeon': 'st02', 'floor': 'St02_0010', 'zone': 0, 'name', 'formations': [...]}].
    'name' is the floor, with the number of the zone when the floor has more than one; 'zone_factors' the five
    factors of its damage zones; 'encounter' the chance in percent of a random battle on each step."""
    found = []
    with zipfile.ZipFile(path) as archive:
        for entry in sorted(archive.namelist()):
            dungeon, name = entry.split('/')
            zones = read_zones(archive.read(entry))
            for zone, (formations, factors, chances) in enumerate(zones):
                if formations:
                    label = name[:-4] if len(zones) == 1 else f'{name[:-4]} zone {zone + 1}'
                    found.append({'dungeon': dungeon, 'floor': name[:-4], 'zone': zone, 'name': label,
                                  'formations': formations, 'zone_factors': factors,
                                  'encounter': chances['encounter'], 'special_encounters': chances['special'],
                                  'equipment': chances['equipment']})
    return found


def fixed_battles(path=FLOOR_ZIP):
    """Every fixed battle: [{'dungeon', 'floor', 'number', 'enemies': [(enemy id, in front row)]}]."""
    found = []
    with zipfile.ZipFile(path) as archive:
        for entry in sorted(archive.namelist()):
            dungeon, name = entry.split('/')
            for battle in read_fixed(archive.read(entry)):
                found.append({'dungeon': dungeon, 'floor': name[:-4], 'number': battle['number'], 'enemies': battle['enemies']})
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
        print(floor['name'])
        for f in floor['formations']:
            print(f"  {f['number']:2d}  {f['chance']:3d}%  " + ', '.join(names[e] + ('' if front else ' (back)') for e, front in f['enemies']))


if __name__ == '__main__':
    main()

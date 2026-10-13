"""
The values of the Balance variant that live in the floor files: the rows of table "zones" of balance_changes.xlsx,
written in place into Data/ENG/Dungeon/stNN/Data.pck of the game.

    python tools/floor_patch.py index            where each floor file sits in its Data.pck: data_tables/floor_file_index.json
    python tools/floor_patch.py status           what the game holds: the values of the game, of the variant, or neither
    python tools/floor_patch.py apply | restore  writes the values of the variant, or puts those of the game back

The Data.pck of the dungeons are 390 MB of maps and textures, so they are not copied into backups/ nor built: a row
is four bytes at one place of one file (a "poke"), written only when the file holds there what the row says the game
has, and put back the same way. The parameter file of each floor is kept in backups/Dungeon/floor_parameters.zip
(tools/floor_data.py); the whole of it is compared with the game before a byte is written.

Writing puts every chance of a wandering shop of every zone in the state the live rows ask for: the value of its row,
or the value of the game where no live row names it. A row dropped or changed since the last install is therefore put
right by the next one, with no record kept of what was written before.

A row: Record is the zone as tools/floor_data.py names it ("St01_0010", "St03_0020 zone 2"), Field one of the names
of "zone_fields" of the record FloorParameter (data_tables/record_layouts.json).
"""
import json
import os
import struct
import sys
import zipfile

import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import floor_data                                         # noqa: E402
import game_profile                                       # noqa: E402
import mod_config                                         # noqa: E402

CHANGES = os.path.join(BASE_DIR, 'data_tables', 'balance_changes.xlsx')
INDEX = os.path.join(BASE_DIR, 'data_tables', 'floor_file_index.json')
TABLE, LIVE = 'zones', ('decided', 'built', 'checked')
_F = game_profile.layout('FloorParameter')
FIELDS = _F['zone_fields']                                # name of the field of a row -> its offset in the zone record
DUNGEON = game_profile.PROFILE['dungeon_subdir']
PACK = 'Data.pck'


class Refused(Exception):
    """A row that cannot be written as it stands, with the reason."""


def rows(path=CHANGES):
    it = openpyxl.load_workbook(path, read_only=True)['Changes'].iter_rows(values_only=True)
    header = next(it)
    found = [dict(zip(header, r)) for r in it if r and r[0] is not None]
    return [r for r in found if r['Table'] == TABLE and r['State'] in LIVE]


def entry_offsets(data):
    """{entry name: (offset, size)} of a pack, read as tools/pck_handler.py reads it."""
    at = data.find(b'Pack                ')
    count = struct.unpack_from('<I', data, at + 24)[0]
    found = {}
    for k in range(count):
        name_at = 0x18 + struct.unpack_from('<I', data, 0x18 + 4 * k)[0]
        name = data[name_at:data.find(b'\x00', name_at)].decode('latin-1')
        found[name] = struct.unpack_from('<II', data, at + 28 + 8 * k)
    return found


def build_index(path=INDEX):
    """Where the parameter file of each floor sits in the Data.pck of its dungeon, read from the game."""
    folder, index = os.path.join(mod_config.data_dir(), DUNGEON), {}
    for dungeon in sorted(os.listdir(folder)):
        pack = os.path.join(folder, dungeon, PACK)
        if os.path.exists(pack):
            with open(pack, 'rb') as f:
                data = f.read()
            index[dungeon] = {'size': len(data),
                              'entries': {n: o for n, (o, _) in sorted(entry_offsets(data).items()) if n.endswith('.bin')}}
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(index, f, indent=1)
    return index


def zone_blocks():
    """{name of a zone: (dungeon, entry, offset of its record in the parameter file)}, named as floor_data.floors()."""
    found = {}
    with zipfile.ZipFile(floor_data.FLOOR_ZIP) as archive:
        for entry in sorted(archive.namelist()):
            dungeon, name = entry.split('/')
            blob = archive.read(entry)
            count = struct.unpack_from('<i', blob, floor_data.ZONE_COUNT)[0]
            first = struct.unpack_from('<Q', blob, floor_data.ZONE_POINTER)[0]
            for zone in range(count):
                label = name[:-4] if count == 1 else f'{name[:-4]} zone {zone + 1}'
                found[label] = (dungeon, name, first + floor_data.ZONE_SIZE * zone)
    return found


def pokes(some=None):
    """[{'id', 'dungeon', 'entry', 'at' (in the parameter file), 'offset' (in Data.pck), 'old', 'new'}] of the live rows,
    each checked against the parameter file kept in backups/. Raises Refused with every row that does not hold."""
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    blocks, found, wrong, seen = zone_blocks(), [], [], {}
    with zipfile.ZipFile(floor_data.FLOOR_ZIP) as archive:
        for row in (some if some is not None else rows()):
            where = blocks.get(str(row['Record']))
            if where is None or str(row['Field']) not in FIELDS:
                wrong.append(f"{row['ID']}: no zone {row['Record']} or no field {row['Field']}")
                continue
            dungeon, entry, block = where
            at = block + FIELDS[str(row['Field'])]
            held = struct.unpack_from('<i', archive.read(f'{dungeon}/{entry}'), at)[0]
            if held != row['Vanilla']:
                wrong.append(f"{row['ID']}: the game holds {held}, the row says {row['Vanilla']}")
            elif not (isinstance(row['New'], int) and 1 <= row['New'] <= 100):
                wrong.append(f"{row['ID']}: a chance is a whole number from 1 to 100, the row asks for {row['New']}")
            elif (dungeon, entry, at) in seen:
                wrong.append(f"{row['ID']}: the field is already written by row {seen[(dungeon, entry, at)]}")
            else:
                seen[(dungeon, entry, at)] = row['ID']
                found.append({'id': row['ID'], 'dungeon': dungeon, 'entry': entry, 'at': at,
                              'offset': index[dungeon]['entries'][entry] + at,
                              'old': struct.pack('<i', held), 'new': struct.pack('<i', row['New'])})
    if wrong:
        raise Refused('; '.join(wrong))
    return found


def relative(dungeon):
    """The path of the pack of a dungeon from the folder of the game."""
    return os.path.relpath(os.path.join(mod_config.data_dir(), DUNGEON, dungeon, PACK), mod_config.game_dir())


def manifest_lines(some=None):
    """['poke|path from the game folder|offset|old|new'] for the archive of the players (tools/package_variant.py)."""
    return [f"poke|{relative(p['dungeon']).replace('/', chr(92))}|{p['offset']:x}|{p['old'].hex()}|{p['new'].hex()}"
            for p in pokes(some)]


def shop_places():
    """{(dungeon, entry): [offset in the parameter file]} of every field a row of this table may write: the chances of
    the wandering shops of every zone of every floor. Whatever the game holds at those places, the rest of the file
    must be the file kept in backups/."""
    found = {}
    for dungeon, entry, block in zone_blocks().values():
        found.setdefault((dungeon, entry), []).extend(block + offset for offset in FIELDS.values())
    return found


def state_of(wanted):
    """({dungeon: 'game' | 'variant' | 'other'}, problems): what each pack of the game holds at the places a row of this
    table may write, against the values of the game and against the rows given. 'other': a value neither of them asks
    for, left by an older build or by a row since changed or dropped; writing puts it right. A pack whose parameter
    files differ from those of backups/ anywhere else is a problem: not the game this mod was made for, and nothing
    is written."""
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    asked = {(p['dungeon'], p['entry'], p['at']): p['new'] for p in wanted}
    states, problems, by_dungeon = {}, [], {}
    for (dungeon, entry), places in shop_places().items():
        by_dungeon.setdefault(dungeon, []).append((entry, places))
    with zipfile.ZipFile(floor_data.FLOOR_ZIP) as archive:
        for dungeon, entries in sorted(by_dungeon.items()):
            path = os.path.join(mod_config.game_dir(), relative(dungeon))
            if not os.path.exists(path) or os.path.getsize(path) != index[dungeon]['size']:
                problems.append(f'{relative(dungeon)}: missing, or not the size of the game this mod was made for')
                continue
            kinds = set()
            with open(path, 'rb') as f:
                for entry, places in sorted(entries):
                    original = bytearray(archive.read(f'{dungeon}/{entry}'))
                    f.seek(index[dungeon]['entries'][entry])
                    held = bytearray(f.read(len(original)))
                    for at in places:
                        now, game = bytes(held[at:at + 4]), bytes(original[at:at + 4])
                        want = asked.get((dungeon, entry, at), game)
                        kinds.add('variant' if now == want and want != game else 'game' if now == game else 'other')
                        held[at:at + 4] = game
                    if held != original:
                        problems.append(f'{relative(dungeon)} {entry}: not the file of the game this mod was made for')
            states[dungeon] = 'other' if 'other' in kinds else 'variant' if 'variant' in kinds else 'game'
    return states, problems


def write(wanted):
    """Puts every place a row of this table may write in the state the rows given ask for: the value of the row where
    one is given, the value of the game everywhere else. So a row that was dropped, or whose value changed since the
    last install, is put right by the next one. Nothing is written when a pack has a problem. Returns the packs and
    the places that changed."""
    states, problems = state_of(wanted)
    if problems:
        raise Refused('; '.join(problems))
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    asked = {(p['dungeon'], p['entry'], p['at']): p['new'] for p in wanted}
    packs, changed = set(), 0
    with zipfile.ZipFile(floor_data.FLOOR_ZIP) as archive:
        for (dungeon, entry), places in sorted(shop_places().items()):
            original = archive.read(f'{dungeon}/{entry}')
            base = index[dungeon]['entries'][entry]
            with open(os.path.join(mod_config.game_dir(), relative(dungeon)), 'r+b') as f:
                for at in places:
                    want = asked.get((dungeon, entry, at), bytes(original[at:at + 4]))
                    f.seek(base + at)
                    if f.read(4) != want:
                        f.seek(base + at)
                        f.write(want)
                        packs.add(dungeon)
                        changed += 1
    return len(packs), changed


def apply():
    """The live rows written; every other place of the table at the value of the game."""
    wanted = pokes()
    packs, changed = write(wanted)
    return packs, len(wanted), changed


def restore():
    """The values of the game at every place a row of this table may write."""
    packs, changed = write([])
    return packs, changed, changed


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    mode = sys.argv[1] if len(sys.argv) > 1 else 'status'
    try:
        if mode == 'index':
            index = build_index()
            print(f'{sum(len(v["entries"]) for v in index.values())} floor files of {len(index)} dungeons: {INDEX}')
        elif mode == 'status':
            wanted = pokes()
            states, problems = state_of(wanted)
            print(f'{len(wanted)} rows; {len(states)} packs: ' + ', '.join(f'{k} {v}' for k, v in sorted(states.items())))
            for line in problems:
                print('   ', line)
        elif mode in ('apply', 'restore'):
            packs, count, changed = apply() if mode == 'apply' else restore()
            print(f"Floors: {count} values {'of the variant held' if mode == 'apply' else 'of the game put back'}; "
                  f'{changed} places written in {packs} packs of {DUNGEON}')
        else:
            raise SystemExit(__doc__)
    except Refused as reason:
        raise SystemExit(f'Refused: {reason}')


if __name__ == '__main__':
    main()

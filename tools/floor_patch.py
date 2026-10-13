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


def state_of(wanted):
    """({dungeon: 'game' | 'variant' | 'mixed'}, problems): what each pack of the game holds at the places of the rows.
    A pack whose parameter files are not those of backups/ outside those places is a problem: not the game this mod
    was made for."""
    with open(INDEX, encoding='utf-8') as f:
        index = json.load(f)
    by_dungeon, states, problems = {}, {}, []
    for p in wanted:
        by_dungeon.setdefault(p['dungeon'], []).append(p)
    with zipfile.ZipFile(floor_data.FLOOR_ZIP) as archive:
        for dungeon, mine in sorted(by_dungeon.items()):
            path = os.path.join(mod_config.game_dir(), relative(dungeon))
            if not os.path.exists(path) or os.path.getsize(path) != index[dungeon]['size']:
                problems.append(f'{relative(dungeon)}: missing, or not the size of the game this mod was made for')
                continue
            kinds = set()
            with open(path, 'rb') as f:
                for entry in sorted({p['entry'] for p in mine}):
                    original = bytearray(archive.read(f'{dungeon}/{entry}'))
                    f.seek(index[dungeon]['entries'][entry])
                    held = bytearray(f.read(len(original)))
                    for p in (q for q in mine if q['entry'] == entry):
                        now = bytes(held[p['at']:p['at'] + 4])
                        kinds.add('game' if now == p['old'] else 'variant' if now == p['new'] else 'other')
                        held[p['at']:p['at'] + 4] = p['old']
                    if held != original:
                        problems.append(f'{relative(dungeon)} {entry}: not the file of the game this mod was made for')
            if 'other' in kinds:
                problems.append(f'{relative(dungeon)}: a value is neither that of the game nor that of the variant')
            states[dungeon] = kinds.pop() if len(kinds) == 1 else 'mixed'
    return states, problems


def write(wanted, key):
    """Writes p[key] ('new' or 'old') at every place; nothing is written when a pack has a problem."""
    states, problems = state_of(wanted)
    if problems:
        raise Refused('; '.join(problems))
    by_dungeon = {}
    for p in wanted:
        by_dungeon.setdefault(p['dungeon'], []).append(p)
    for dungeon, mine in by_dungeon.items():
        with open(os.path.join(mod_config.game_dir(), relative(dungeon)), 'r+b') as f:
            for p in mine:
                f.seek(p['offset'])
                f.write(p[key])
    return len(by_dungeon)


def apply():
    wanted = pokes()
    return (write(wanted, 'new') if wanted else 0), len(wanted)


def restore(path=CHANGES):
    """Puts the values of the game back at the place of every row of the table, whatever its state."""
    it = openpyxl.load_workbook(path, read_only=True)['Changes'].iter_rows(values_only=True)
    header = next(it)
    every = [dict(zip(header, r)) for r in it if r and r[0] is not None and r[header.index('Table')] == TABLE]
    wanted, seen = [], set()
    for row in every:                     # a dropped row may have been written by an older build: its place goes back too
        try:
            for p in pokes([row]):
                if (p['dungeon'], p['offset']) not in seen:
                    seen.add((p['dungeon'], p['offset']))
                    wanted.append(p)
        except Refused:
            pass
    live = {(p['dungeon'], p['offset']): p for p in pokes()}
    wanted = [live.get((p['dungeon'], p['offset']), p) for p in wanted]
    return (write(wanted, 'old') if wanted else 0), len(wanted)


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
            print(f'{len(wanted)} rows in {len(states)} packs: ' + ', '.join(f'{k} {v}' for k, v in sorted(states.items())))
            for line in problems:
                print('   ', line)
        elif mode in ('apply', 'restore'):
            packs, count = apply() if mode == 'apply' else restore()
            print(f"Floors: {count} values {'of the variant written' if mode == 'apply' else 'of the game put back'} in "
                  f'{packs} packs of {DUNGEON}')
        else:
            raise SystemExit(__doc__)
    except Refused as reason:
        raise SystemExit(f'Refused: {reason}')


if __name__ == '__main__':
    main()

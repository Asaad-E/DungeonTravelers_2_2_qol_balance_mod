"""
Growth of the classes: reader of ClassLevelData.pck (backed up in backups/).

A row of ClassLevelData is its number (int) and 99 levels of eight ints: HP, TP, ATK, DEF, INT, RES, DEX, AGI.
There are 38 rows for 32 classes: a class that can be reached from two classes has one row per route.
The row is chosen by Parameter::CParameterClassLevel::GetClassLevelID (0x5545b0, jump table 0x5546fc) from the
current class and the class before it; the character's stats are then read at 0x4f5d60 as

    stat = row[level] + a bonus of the character per stat + one figure added to every stat

(the two bonuses, at offsets 0xdc.. and 0x120 of the character, are not decoded here).

    python mod_project/tools/class_data.py        prints the row of every class and route
"""
import os
import struct
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROWTH_PCK = os.path.join(BASE_DIR, 'backups', 'ClassLevelData.pck')
CLASS_PCK = os.path.join(BASE_DIR, 'backups', 'ClassData.pck')
STATS = ('hp', 'tp', 'atk', 'def', 'int', 'res', 'dex', 'agi')
LEVELS = 99
# class id -> row, or {previous class id: row} for a class with two routes (0x5545b0).
# With any other previous class the code returns the first of the two rows.
GROWTH_ROW = {0: 0, 1: 1, 2: 2, 3: 3, 4: {1: 4, 2: 5}, 5: 6,
              6: 7, 7: 8, 8: 9, 9: 10, 10: {7: 11, 8: 12}, 11: 13,
              12: 14, 13: 15, 14: 16, 15: 17, 16: 18, 17: {13: 19, 14: 20}, 18: {14: 21, 15: 22}, 19: 23,
              20: 24, 21: 25, 22: 26, 23: 27, 24: {21: 28, 22: 29}, 25: 30,
              26: 31, 27: 32, 28: 33, 29: 34, 30: {27: 35, 28: 36}, 31: 37}


def growth_row(class_id, previous=None):
    row = GROWTH_ROW[class_id]
    if isinstance(row, dict):
        return row.get(previous, min(row.values()))
    return row


def routes():
    """Every (class id, previous class id or None, row)."""
    found = []
    for class_id, row in GROWTH_ROW.items():
        if isinstance(row, dict):
            found += [(class_id, previous, r) for previous, r in row.items()]
        else:
            found.append((class_id, None, row))
    return found


def growth(path=GROWTH_PCK):
    """{row: [stats of level 1, ..., stats of level 99]}, each a dict by STATS."""
    table = {}
    for _, blob in PckArchive(path).files:
        blob = bytes(blob)
        number = struct.unpack_from('<i', blob, 0)[0]
        table[number] = [dict(zip(STATS, struct.unpack_from('<8i', blob, 4 + 32 * level))) for level in range(LEVELS)]
    return table


def stats(class_id, level, previous=None, table=None):
    """Stats of a class at a level before any bonus."""
    return (table or growth())[growth_row(class_id, previous)][level - 1]


def class_names(path=CLASS_PCK):
    """{class id: name} from ClassData.pck (id at 0x00, name pointer at 0x10; 0x08 points at its two-letter code)."""
    names = {}
    for _, blob in PckArchive(path).files:
        blob = bytes(blob)
        pointer = struct.unpack_from('<Q', blob, 0x10)[0]
        names[struct.unpack_from('<i', blob, 0)[0]] = blob[pointer:blob.find(b'\x00', pointer)].decode('utf-8', 'replace')
    return names


def route_name(class_id, previous, names):
    return names[class_id] if previous is None else f'{names[class_id]} (from {names[previous]})'


def main():
    names, table = class_names(), growth()
    for class_id, previous, row in routes():
        last = table[row][-1]
        print(f'row {row:2d}  {route_name(class_id, previous, names):34s} Lv99 ' + ' '.join(f'{k} {last[k]}' for k in STATS))


if __name__ == '__main__':
    main()

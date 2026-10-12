"""
What is particular to the game the mod is made for, read from two files of data_tables/ so that no tool holds it:

    game_profile.json      names: the folder of the game, its data folders, its program file, its save folder, the
                           prefix of the archives for players
    record_layouts.json    where each field sits in each record of the game (offsets in hexadecimal)

    from game_profile import PROFILE, layout
    PROFILE['game_folder']                  'DungeonTravelers2-2_EN'
    layout('EnemyStatusData')['flags']      0x3C, as an int

Another game of the same engine is another pair of these files; the tools stay as they are.

    python tools/game_profile.py            prints both, with every offset as the tools read it
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = os.path.join(BASE_DIR, 'data_tables')


def _read(name):
    with open(os.path.join(TABLES, name), encoding='utf-8') as f:
        return json.load(f)


def _numbers(value):
    """The same structure with every '0x..' string as an int."""
    if isinstance(value, dict):
        return {k: _numbers(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_numbers(v) for v in value]
    if isinstance(value, str) and value[:2].lower() == '0x':
        return int(value, 16)
    return value


PROFILE = _read('game_profile.json')
_LAYOUTS = _numbers(_read('record_layouts.json'))


def layout(record):
    """The fields of a record: {name: offset as an int, or a count, a list of offsets, a dict of them}."""
    if record not in _LAYOUTS or record == 'what':
        raise KeyError(f'record_layouts.json has no record {record!r}')
    return _LAYOUTS[record]


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    for key, value in PROFILE.items():
        if key != 'what':
            print(f'{key}: {value}')
    for record, fields in _LAYOUTS.items():
        if record != 'what':
            print(f'{record}: {fields}')


if __name__ == '__main__':
    main()

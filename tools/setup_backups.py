"""
The originals every tool reads, copied from your own copy of the game into backups/ (not in git: they are
files of the game). Run it once, on a game no mod was installed into.

    python tools/setup_backups.py              copies what is missing and checks every file
    python tools/setup_backups.py --check      checks only
    python tools/setup_backups.py --manifest   writes the list again from the backups that are there

The list is data_tables/backups_manifest.json: for each file, where it sits in the game (under Data/ENG), where it is
kept, and its SHA-256. A file of the game whose hash is not the one of the list is not copied: it is not the original
(another version of the game, or a mod already installed; put the originals back first). The two archives of the
dungeon floors are then gathered from the game by tools/floor_data.py and tools/map_data.py.

The folder of the game: config.json (tools/mod_config.py), else DungeonTravelers2-2_EN inside the folder of the repository.
"""
import hashlib
import json
import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mod_config                                          # noqa: E402

BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
MANIFEST = os.path.join(BASE_DIR, 'data_tables', 'backups_manifest.json')
ROOT_SUBDIRS = ('Parameter', 'Script')                     # where a pack kept at the root of backups/ may sit in the game
SUBDIRS = ('Script', 'Enemy', 'NPC', 'Dungeon', 'Summon', 'Character')
GATHERED = (('floor_parameters.zip', 'floor_data'), ('floor_maps.zip', 'map_data'))     # archive of backups/Dungeon, its tool


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def read_manifest():
    with open(MANIFEST, encoding='utf-8') as f:
        return json.load(f)['files']


def write_manifest(game_data=None):
    """The list from the backups that are there: each pack with the folder of the game that holds a file of its name."""
    game_data = game_data or mod_config.data_dir()
    files = []
    for name in sorted(os.listdir(BACKUP_DIR)):
        if name.endswith('.pck'):
            sub = next((s for s in ROOT_SUBDIRS if os.path.exists(os.path.join(game_data, s, name))), None)
            if sub is None:
                raise SystemExit(f'{name}: no file of that name in the game; the list cannot say where it comes from')
            files.append({'backup': name, 'game': f'{sub}/{name}', 'sha256': sha(os.path.join(BACKUP_DIR, name))})
    for sub in SUBDIRS:
        folder = os.path.join(BACKUP_DIR, sub)
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            if name.endswith('.pck'):
                files.append({'backup': f'{sub}/{name}', 'game': f'{sub}/{name}', 'sha256': sha(os.path.join(folder, name))})
    with open(MANIFEST, 'w', encoding='utf-8', newline=chr(10)) as f:
        json.dump({'what': 'The original files of the game the tools read, with the hash each must have. Written by '
                           'tools/setup_backups.py --manifest; no file of the game is in the repository.',
                   'files': files}, f, indent=1)
        f.write(chr(10))
    return len(files)


def setup(copy=True, game_data=None):
    """(files right, [problem]). copy: take from the game what backups/ lacks."""
    game_data = game_data or mod_config.data_dir()
    right, problems = 0, []
    for entry in read_manifest():
        kept = os.path.join(BACKUP_DIR, *entry['backup'].split('/'))
        source = os.path.join(game_data, *entry['game'].split('/'))
        if not os.path.exists(kept):
            if not copy:
                problems.append(f"{entry['backup']}: missing")
                continue
            if not os.path.exists(source):
                problems.append(f"{entry['backup']}: {source} not found (is game_dir right? python tools/mod_config.py)")
                continue
            if sha(source) != entry['sha256']:
                problems.append(f"{entry['backup']}: {source} is not the original file (another version, or a mod is "
                                f"installed): not copied")
                continue
            os.makedirs(os.path.dirname(kept), exist_ok=True)
            shutil.copy2(source, kept)
        if sha(kept) != entry['sha256']:
            problems.append(f"{entry['backup']}: the file kept is not the original (its hash differs from the list)")
            continue
        right += 1
    return right, problems


def gather():
    """The two archives of the dungeon floors, made from the game when they are missing. Returns the lines to print."""
    lines = []
    for name, module in GATHERED:
        path = os.path.join(BACKUP_DIR, 'Dungeon', name)
        if os.path.exists(path):
            lines.append(f'    {name}: there')
            continue
        tool = __import__(module)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        lines.append(f'    {name}: {tool.collect()} files gathered from the game')
    return lines


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.argv[1:] == ['--manifest']:
        print(f'{write_manifest()} files listed in {MANIFEST}')
        return 0
    check_only = sys.argv[1:] == ['--check']
    print(f'Game: {mod_config.game_dir()}')
    right, problems = setup(copy=not check_only)
    total = len(read_manifest())
    print(f'{right} of {total} original files in {BACKUP_DIR}')
    for p in problems:
        print(f'    PROBLEM {p}')
    if not problems and not check_only:
        for line in gather():
            print(line)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())

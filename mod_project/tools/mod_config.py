"""
Where the game is on this machine: mod_project/config.json, written by hand from config.example.json (not in git).

    game_dir        the folder of the game, the one that holds its .exe and its Data folder. Left out: the folder
                    DungeonTravelers2-2_EN beside mod_project.
    program_files   the program files to patch, as paths (relative ones are taken from game_dir). Left out or
                    empty: every .exe of game_dir that is the program, found by what it holds at the addresses of
                    the sheet ExePatches (tools/exe_patch.py program_files).
    formula_exe     the program file the formula tools read (tools/exe_reader.py). Left out: the vanilla copy the
                    patch tool keeps, else DT22_en_unwrapped.exe of game_dir.
    save_dir        the folder of the save files. Left out: Documents/AQUAPLUS/DUNGEON TRAVELERS 2-2_EN.

    python mod_project/tools/mod_config.py        prints what is in force
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
DEFAULT_GAME_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN')
DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'AQUAPLUS', 'DUNGEON TRAVELERS 2-2_EN')
KEYS = ('game_dir', 'program_files', 'formula_exe', 'save_dir')


def load(path=CONFIG_PATH):
    """The file as a dict, {} when there is none. A key it does not know stops the tool: a typo must not pass."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        found = json.load(f)
    unknown = sorted(set(found) - set(KEYS))
    if unknown:
        raise SystemExit(f'{path}: unknown key(s) {", ".join(unknown)}; the keys are {", ".join(KEYS)}')
    return found


def _path(value, base):
    value = os.path.expandvars(os.path.expanduser(str(value)))
    return os.path.normpath(value if os.path.isabs(value) else os.path.join(base, value))


def game_dir(config=None):
    config = load() if config is None else config
    return _path(config['game_dir'], BASE_DIR) if config.get('game_dir') else DEFAULT_GAME_DIR


def data_dir(config=None):
    """Data/ENG of the game: the folder its packs sit in."""
    return os.path.join(game_dir(config), 'Data', 'ENG')


def listed_program_files(config=None):
    """The program files the file names, [] when it leaves the search to tools/exe_patch.py."""
    config = load() if config is None else config
    return [_path(p, game_dir(config)) for p in config.get('program_files') or []]


def formula_exe(config=None):
    config = load() if config is None else config
    return _path(config['formula_exe'], game_dir(config)) if config.get('formula_exe') else None


def save_dir(config=None):
    config = load() if config is None else config
    return _path(config['save_dir'], BASE_DIR) if config.get('save_dir') else DEFAULT_SAVE_DIR


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    config = load()
    print(f"config file: {CONFIG_PATH if os.path.exists(CONFIG_PATH) else 'none (defaults)'}")
    print(f'game_dir: {game_dir(config)}')
    print(f"program_files: {', '.join(listed_program_files(config)) or 'searched in game_dir'}")
    print(f"formula_exe: {formula_exe(config) or 'the vanilla copy, else DT22_en_unwrapped.exe of game_dir'}")
    print(f'save_dir: {save_dir(config)}')


if __name__ == '__main__':
    main()

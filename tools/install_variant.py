"""
Puts a built variant into the game folder, so the work can be looked at in the game.

Called by build_variant.py after a build has passed its verification; it can also be run alone:

    python tools/install_variant.py qol

Originals live in backups/ (the game folder that holds each one is looked up,
Parameter first) and in backups/Script/ (always the game's Script folder; SEV.pck
exists in both). After it runs, every game file that has an original is in the state of the
variant: the file the variant built, or the untouched original when the variant does not
build that file. Nothing of any other build is left behind, so what is on screen is the variant
and nothing else. Run from the command line, it puts the two program files in the same state: the rows of
the sheet ExePatches of the variant (tools/exe_patch.py), or the vanilla files.

Every file it replaces is first copied to build/installed_backup/<date-time>/, in
the same Parameter/ or Script/ subfolder. To undo an install, copy that folder back over
DungeonTravelers2-2_EN/Data/ENG/.
"""
import os
import sys
import shutil
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
BUILD_DIR = os.path.join(BASE_DIR, 'build')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mod_config                       # noqa: E402  (the folder of the game: config.json, else DungeonTravelers2-2_EN in the repository folder)
GAME_DIR = mod_config.data_dir()
from game_profile import PROFILE        # noqa: E402
GAME_SUBDIRS = tuple(PROFILE['text_subdirs'])
# Data/ENG/Enemy/Enemy.pck, Data/ENG/NPC/NPC.pck: only a variant that changes values builds them (balance)
VALUE_SUBDIRS = tuple(PROFILE['value_subdirs'])
BUILT_SUBDIR = os.path.join('Data', 'ENG', 'Parameter')


def read(path):
    with open(path, 'rb') as f:
        return f.read()


def game_location(name, game_dir=GAME_DIR):
    """Subfolder of the game that holds a backed-up file (Parameter first: SEV.pck exists in both)."""
    for sub in GAME_SUBDIRS:
        if os.path.exists(os.path.join(game_dir, sub, name)):
            return sub
    return None


def backup_files(backup_dir=BACKUP_DIR):
    """(key, path, fixed game subfolder or None) of every original. key is 'Name.pck' or 'Script/Name.pck'."""
    found = [(f, os.path.join(backup_dir, f), None) for f in sorted(os.listdir(backup_dir)) if f.endswith('.pck')]
    for sub in GAME_SUBDIRS + VALUE_SUBDIRS:
        folder = os.path.join(backup_dir, sub)
        if os.path.isdir(folder):
            found += [(f'{sub}/{f}', os.path.join(folder, f), sub) for f in sorted(os.listdir(folder)) if f.endswith('.pck')]
    return found


def expected_files(variant, backup_dir=BACKUP_DIR, build_dir=BUILD_DIR, game_dir=GAME_DIR):
    """'Subfolder/Name.pck' in the game -> (bytes the game must hold, where they come from).
    A missing game file is reported under its backup key with the subfolder None."""
    built_dir = os.path.join(build_dir, variant, BUILT_SUBDIR)
    expected = {}
    for key, path, sub in backup_files(backup_dir):
        name = os.path.basename(path)
        sub = sub or game_location(name, game_dir)
        # built script packs sit beside the Parameter ones: build/<variant>/Data/ENG/Script/
        built = os.path.join(os.path.dirname(built_dir), sub, name) if sub else ''
        if sub and os.path.exists(built):
            expected[f'{sub}/{name}'] = (read(built), f'{variant} build')
        else:
            expected[f'{sub}/{name}' if sub else key] = (read(path), 'original')
    return expected


def install(variant, game_dir=GAME_DIR, backup_dir=BACKUP_DIR, build_dir=BUILD_DIR, stamp=None):
    """Returns (changes, kept, problems). changes: (subfolder/name, source) of every file written."""
    changes, kept, problems = [], 0, []
    stamp = stamp or datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    saved_dir = os.path.join(build_dir, 'installed_backup', stamp)
    for key, (data, source) in expected_files(variant, backup_dir, build_dir, game_dir).items():
        path = os.path.join(game_dir, *key.split('/'))
        if '/' not in key or not os.path.exists(path):
            problems.append(f"{key}: not found in the game folder")
            continue
        if read(path) == data:
            kept += 1
            continue
        saved = os.path.join(saved_dir, *key.split('/'))
        os.makedirs(os.path.dirname(saved), exist_ok=True)
        shutil.copy2(path, saved)
        with open(path, 'wb') as f:
            f.write(data)
        changes.append((key, source))
    problems.extend(verify(variant, game_dir, backup_dir, build_dir))
    return changes, kept, problems, saved_dir


def verify(variant, game_dir=GAME_DIR, backup_dir=BACKUP_DIR, build_dir=BUILD_DIR):
    """The game folder must hold exactly the variant."""
    problems = []
    for key, (data, source) in expected_files(variant, backup_dir, build_dir, game_dir).items():
        path = os.path.join(game_dir, *key.split('/'))
        if not os.path.exists(path) or read(path) != data:
            problems.append(f"{key}: the game does not hold the {source} file")
    return problems


def report(variant, changes, kept, problems, saved_dir):
    print(f"[4] Installed variant '{variant}' into {GAME_DIR}")
    for source in sorted({s for _, s in changes}):
        names = [n for n, s in changes if s == source]
        print(f"    {len(names)} file(s) replaced by the {source} file: {', '.join(names)}")
    print(f"    {kept} file(s) were already right")
    if changes:
        print(f"    Previous files saved in {saved_dir}")
    for p in problems:
        print(f"    PROBLEM {p}")


def install_program(variant):
    """The program files of the game in the state of the variant: the rows of the sheet ExePatches whose set carries
    the name of the variant written into both files (tools/exe_patch.py), or both vanilla files put back when the
    variant has no such rows; then the floor files (install_floors). Returns the lines to print."""
    import exe_patch
    rows = exe_patch.patches(variant)
    if rows:
        done = exe_patch.install(variant)
        return [f"    Program: {len(rows)} rows of the set '{variant}' in {label} ({changed} bytes differ from vanilla)"
                for label, _, changed in done] + install_floors(variant)
    done = exe_patch.restore()
    return [f"    Program: vanilla ({', '.join(done)})" if done else '    Program: vanilla, never patched'] + install_floors(variant)


def install_floors(variant):
    """The floor files of the game in the state of the variant: the rows of table zones written in place for the
    Balance variant, the values of the game put back for any other (tools/floor_patch.py). Returns the lines to print."""
    import floor_patch
    try:
        packs, count, changed = floor_patch.apply() if variant == 'balance' else floor_patch.restore()
    except floor_patch.Refused as reason:
        return [f'    Floors: REFUSED, nothing written: {reason}']
    what = f'{count} values of the variant held' if variant == 'balance' else 'the values of the game'
    return [f'    Floors: {what}; {changed} places written in {packs} packs of the dungeons']


def main():
    # a name that has no build would put every original back (it happened with "--help" on 2026-10-12)
    if len(sys.argv) != 2 or not os.path.isdir(os.path.join(BUILD_DIR, sys.argv[1])):
        print(__doc__)
        return 1
    result = install(sys.argv[1])
    report(sys.argv[1], *result)
    for line in install_program(sys.argv[1]):
        print(line)
    return 1 if result[2] else 0


if __name__ == '__main__':
    sys.exit(main())

"""
Packages a built variant for players.

    python mod_project/tools/package_variant.py qol | balance

Writes mod_project/dist/DT22_<variant>_<date>.zip with:
    Data/ENG/Parameter/*.pck, Data/ENG/Script/*.pck   the files of the variant (only those it changes)
    Original/Data/ENG/...                             the untouched version of each, to uninstall
    README.txt                                        mod_project/release/README_<variant>.txt
    Patch_Program.bat, Unpatch_Program.bat, Program_Patch.ps1    balance only: the rows of the sheet ExePatches (set
                                                      balance) as a script the player runs in the folder of the game;
                                                      it checks the bytes it replaces and keeps a copy of the file

Run build_variant.py first: the package is made from mod_project/build/<variant>/ and refuses to
run if a built file is identical to its original (nothing to ship) or has no original (cannot be undone).
"""
import os
import sys
import zipfile
import argparse
import datetime
import install_variant

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(BASE_DIR, 'build')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DIST_DIR = os.path.join(BASE_DIR, 'dist')
RELEASE_DIR = os.path.join(BASE_DIR, 'release')
README_NAMES = {'qol': 'README_QoL.txt', 'balance': 'README_Balance.txt'}
PATCH_SETS = {'balance': 'balance'}                   # variant -> set of the sheet ExePatches its program patch holds
PATCH_TEMPLATE = 'program_patch_template.ps1'
PATCH_SCRIPT = 'Program_Patch.ps1'
LAUNCHER = '@echo off' + chr(10) + 'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0{script}" {mode}' + chr(10) + 'pause' + chr(10)


def changed_files(variant, build_dir=BUILD_DIR, backup_dir=BACKUP_DIR):
    """(subfolder, name, built bytes, original bytes) of every file of the variant that differs from the original."""
    found, problems = [], []
    originals = {}
    for key, path, sub in install_variant.backup_files(backup_dir):
        originals[(sub or 'Parameter', os.path.basename(path))] = path
        if sub is None:                                    # a pack of backups/ may belong to Script/ in the game
            originals.setdefault(('Script', os.path.basename(path)), path)
    for sub in install_variant.GAME_SUBDIRS + install_variant.VALUE_SUBDIRS:
        folder = os.path.join(build_dir, variant, 'Data', 'ENG', sub)
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            built = install_variant.read(os.path.join(folder, name))
            if (sub, name) not in originals:
                problems.append(f'{sub}/{name}: no original in backups, it could not be uninstalled')
                continue
            original = install_variant.read(originals[(sub, name)])
            if built != original:
                found.append((sub, name, built, original))
    return found, problems


def program_patch(variant):
    """The script that writes the program patch of the variant, or None: the template of release/ with a table per
    program file, each row the offset in that file (from its vanilla copy), the original bytes and the new ones."""
    if variant not in PATCH_SETS:
        return None
    import exe_patch
    from exe_reader import Exe
    rows = exe_patch.patches(PATCH_SETS[variant])
    tables = []
    for _, game_file, vanilla_copy in exe_patch.find_targets():
        exe = Exe(vanilla_copy)
        wrong = exe_patch.problems(exe, rows)
        if wrong:
            raise SystemExit(f'{vanilla_copy}: ' + '; '.join(wrong))
        lines = [f"        @('{exe.offset(p['va']):x}', '{p['old'].hex()}', '{p['new'].hex()}')" for p in rows]
        tables.append(f"    '{os.path.basename(game_file)}' = @(" + chr(10) + (',' + chr(10)).join(lines) + chr(10) + '    )')
    with open(os.path.join(RELEASE_DIR, PATCH_TEMPLATE), encoding='utf-8') as f:
        return f.read().replace('#TABLES#', chr(10).join(tables))


def package(variant, out_dir=DIST_DIR, stamp=None):
    files, problems = changed_files(variant)
    readme = os.path.join(RELEASE_DIR, README_NAMES[variant])
    if not os.path.exists(readme):
        problems.append(f'{readme}: player README not found')
    if not files:
        problems.append('no built file differs from the original: run build_variant.py first')
    if problems:
        return None, files, problems
    os.makedirs(out_dir, exist_ok=True)
    stamp = stamp or datetime.date.today().isoformat()
    path = os.path.join(out_dir, f'DT22_{variant}_{stamp}.zip')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(readme, 'README.txt')
        for sub, name, built, original in files:
            z.writestr(f'Data/ENG/{sub}/{name}', built)
            z.writestr(f'Original/Data/ENG/{sub}/{name}', original)
        script = program_patch(variant)
        if script:
            z.writestr(PATCH_SCRIPT, script)
            z.writestr('Patch_Program.bat', LAUNCHER.format(script=PATCH_SCRIPT, mode='patch'))
            z.writestr('Unpatch_Program.bat', LAUNCHER.format(script=PATCH_SCRIPT, mode='unpatch'))
    return path, files, problems


def main():
    parser = argparse.ArgumentParser(description='Package a built variant for players.')
    parser.add_argument('variant', choices=sorted(README_NAMES))
    args = parser.parse_args()
    path, files, problems = package(args.variant)
    if problems:
        print(f'[FAIL] {len(problems)} problem(s):')
        for p in problems:
            print(f'    {p}')
        sys.exit(1)
    print(f'[OK] {path}  ({os.path.getsize(path):,} bytes)')
    for sub, name, built, _ in files:
        print(f'    Data/ENG/{sub}/{name}  ({len(built):,} bytes)')
    print(f'    Original/ holds the untouched version of the same {len(files)} files; README.txt explains install and uninstall')


if __name__ == '__main__':
    main()

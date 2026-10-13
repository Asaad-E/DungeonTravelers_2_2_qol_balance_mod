"""
Packages a built variant for players, as differences: the archive holds no file of the game.

    python tools/package_variant.py qol | balance

Writes dist/DT22_<variant>_<date>.zip, to unpack into the folder of the game:
    Install_<Variant>.bat          applies the variant
    Uninstall_DT22_Mod.bat         puts every file back
    DT22_Mod/mod_patch.ps1         installer/mod_patch.ps1: it checks each file of the game by its SHA-256, keeps a copy,
                                   rebuilds the file of the variant from the original and the differences, and checks
                                   the result. For the balance variant it also patches the program: every .exe of the
                                   folder that holds the original bytes at the places of the sheet ExePatches
    DT22_Mod/<variant>.txt         one line per file (path, hash before, hash after, size, where its steps are) and per
                                   row of the program patch (the offset in the file, the bytes before, the bytes after)
    DT22_Mod/<variant>.ops         the steps: (0 copy from the original | 1 take from .dat, offset, length), 12 bytes each
    DT22_Mod/<variant>.dat         the bytes that are not in the original
    DT22_Mod/README.txt            installer/README_<variant>.txt

Run build_variant.py first: the package is made from build/<variant>/ and the originals of backups/. It is refused if
a built file is identical to its original (nothing to ship), and every file is rebuilt here from its differences and
compared with the built one before the archive is written.
"""
import argparse
import datetime
import hashlib
import os
import struct
import sys
import zipfile

import install_variant

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(BASE_DIR, 'build')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
DIST_DIR = os.path.join(BASE_DIR, 'dist')
RELEASE_DIR = os.path.join(BASE_DIR, 'installer')
README_NAMES = {'qol': 'README_QoL.txt', 'balance': 'README_Balance.txt'}
PATCH_SETS = {'balance': 'balance'}                   # variant -> set of the sheet ExePatches its program patch holds
PATCH_SCRIPT = 'mod_patch.ps1'
from game_profile import PROFILE                          # noqa: E402
MOD_DIR = PROFILE['mod_folder']
PREFIX = PROFILE['package_prefix']
UNINSTALL = f'Uninstall_{MOD_DIR}.bat'
LAUNCHER = ('@echo off' + chr(10) + 'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0' + MOD_DIR + chr(92)
            + PATCH_SCRIPT + '" {args}' + chr(10) + 'pause' + chr(10))
WINDOW, STEP = 16, 4                                  # a run of the original is looked for by blocks of this size
COPY, TAKE = 0, 1


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


def delta(original, built):
    """[(COPY, offset in the original, length) | (TAKE, bytes)] that rebuild `built`. Greedy: at each place of the new
    file the longest run of the original that starts with the same block is copied; what has no such run is taken."""
    index = {}
    for i in range(0, len(original) - WINDOW + 1, STEP):
        index.setdefault(original[i:i + WINDOW], i)
    steps, pending, j, n = [], bytearray(), 0, len(built)
    while j < n:
        i = index.get(built[j:j + WINDOW]) if j + WINDOW <= n else None
        if i is None:
            pending.append(built[j])
            j += 1
            continue
        while pending and i > 0 and original[i - 1] == pending[-1]:       # the bytes just before belong to the run too
            pending.pop()
            i -= 1
            j -= 1
        length = WINDOW
        while i + length < len(original) and j + length < n and original[i + length] == built[j + length]:
            length += 1
        if pending:
            steps.append((TAKE, bytes(pending)))
            pending = bytearray()
        steps.append((COPY, i, length))
        j += length
    if pending:
        steps.append((TAKE, bytes(pending)))
    return steps


def rebuilt(original, steps):
    out = bytearray()
    for step in steps:
        out += original[step[1]:step[1] + step[2]] if step[0] == COPY else step[1]
    return bytes(out)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def program_rows(variant):
    """['exe|layout|offset|old|new'] of the program patch of the variant: one layout per kind of program file (the
    offset of a row in the file comes from the vanilla copy of each), the same layout written once."""
    if variant not in PATCH_SETS:
        return []
    import exe_patch
    from exe_reader import Exe
    rows = exe_patch.patches(PATCH_SETS[variant])
    layouts = []
    for _, _, vanilla_copy in exe_patch.find_targets():
        exe = Exe(vanilla_copy)
        wrong = exe_patch.problems(exe, rows)
        if wrong:
            raise SystemExit(f'{vanilla_copy}: ' + '; '.join(wrong))
        layout = tuple((exe.offset(p['va']), p['old'].hex(), p['new'].hex()) for p in rows)
        if layout not in layouts:
            layouts.append(layout)
    return [f'exe|{k}|{offset:x}|{old}|{new}' for k, layout in enumerate(layouts) for offset, old, new in layout]


def floor_rows(variant):
    """['poke|file|offset|old|new'] of the values the variant writes in place into the packs of the dungeons, which
    are too large to carry as differences of a whole file (tools/floor_patch.py)."""
    if variant not in PATCH_SETS:
        return []
    import floor_patch
    return floor_patch.manifest_lines()


def differences(variant, files):
    """(lines of <variant>.txt, bytes of .ops, bytes of .dat). Each file is rebuilt and compared before it is kept."""
    lines, ops, blob = [f'variant|{variant}'], bytearray(), bytearray()
    for sub, name, built, original in files:
        steps = delta(original, built)
        if rebuilt(original, steps) != built:
            raise SystemExit(f'{sub}/{name}: its differences do not rebuild it')
        start = len(ops) // 12
        for step in steps:
            if step[0] == COPY:
                ops += struct.pack('<3i', COPY, step[1], step[2])
            else:
                ops += struct.pack('<3i', TAKE, len(blob), len(step[1]))
                blob += step[1]
        rel = chr(92).join(('Data', 'ENG', sub, name))
        lines.append(f'file|{rel}|{sha(original)}|{sha(built)}|{len(built)}|{start}|{len(steps)}')
    return lines + program_rows(variant) + floor_rows(variant), bytes(ops), bytes(blob)


def package(variant, out_dir=DIST_DIR, stamp=None):
    files, problems = changed_files(variant)
    readme = os.path.join(RELEASE_DIR, README_NAMES[variant])
    if not os.path.exists(readme):
        problems.append(f'{readme}: player README not found')
    if not files:
        problems.append('no built file differs from the original: run build_variant.py first')
    if problems:
        return None, files, problems
    lines, ops, blob = differences(variant, files)
    os.makedirs(out_dir, exist_ok=True)
    stamp = stamp or datetime.date.today().isoformat()
    path = os.path.join(out_dir, f'{PREFIX}_{variant}_{stamp}.zip')
    title = {'qol': 'QoL', 'balance': 'Balance'}[variant]
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(f'Install_{title}.bat', LAUNCHER.format(args=f'install {variant}'))
        z.writestr(UNINSTALL, LAUNCHER.format(args='uninstall'))
        z.write(os.path.join(RELEASE_DIR, PATCH_SCRIPT), f'{MOD_DIR}/{PATCH_SCRIPT}')
        z.write(readme, f'{MOD_DIR}/README.txt')
        z.writestr(f'{MOD_DIR}/{variant}.txt', chr(10).join(lines) + chr(10))
        z.writestr(f'{MOD_DIR}/{variant}.ops', ops)
        z.writestr(f'{MOD_DIR}/{variant}.dat', blob)
    return path, files, problems


def main():
    parser = argparse.ArgumentParser(description='Package a built variant for players, as differences.')
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
    print(f'    {len(files)} files as differences; no file of the game is in the archive')


if __name__ == '__main__':
    main()

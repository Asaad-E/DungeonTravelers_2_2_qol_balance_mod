"""
Patch of the program files, for the levers classed "Executable" in the sheet Levers.

Every byte it writes is a row of the sheet ExePatches of data_tables/balance_criteria.xlsx: an address, the bytes
that must be there, the bytes to write, and for a repointed constant the two floats involved. The game folder holds
two program files, the one the shop delivers (DT22_en.exe, with its protector) and the same program without the
protector (DT22_en_unwrapped.exe). Their code sits at the same addresses, and both are always written together:
nothing is written into either unless every row of the set checks in both.

    python mod_project/tools/exe_patch.py check balance     says whether every row matches both program files
    python mod_project/tools/exe_patch.py install balance   keeps a copy of each vanilla file, then writes the set
    python mod_project/tools/exe_patch.py restore           puts both vanilla files back
    python mod_project/tools/exe_patch.py status            says which rows each installed file carries
    python mod_project/tools/exe_patch.py saves LABEL       copies the save folder into backups/saves/LABEL and checks it

install refuses to write when a game file differs from its vanilla copy anywhere outside the rows of the sheet,
writes through a temporary file that is read back first, and puts both vanilla files back if a result does not check.

The vanilla copies are backups/exe/<name>.vanilla.exe (not in git), each with its hash beside it. A copy is only
made from a file in which every row of the sheet still holds its old bytes. The tools that read formulas
(tools/exe_reader.py) read the vanilla copy of the unwrapped file once it exists, never the patched one.
"""
import hashlib
import os
import shutil
import struct
import sys

import openpyxl

from exe_reader import Exe, EXE_PATH, VANILLA_PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'balance_criteria.xlsx')
GAME_EXE = os.path.join(os.path.dirname(EXE_PATH), 'DT22_en.exe')
VANILLA_COPY = os.path.join(BASE_DIR, 'backups', 'exe', 'DT22_en.vanilla.exe')
# (what the file is, the file of the game, its vanilla copy)
TARGETS = (('game file', GAME_EXE, VANILLA_COPY), ('unwrapped file', EXE_PATH, VANILLA_PATH))
SAVE_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'AQUAPLUS', 'DUNGEON TRAVELERS 2-2_EN')
LINE_END = chr(10)


def patches(patch_set=None):
    """[{'id', 'set', 'lever', 'va', 'old', 'new', 'float_before', 'float_after', 'meaning'}] of the sheet."""
    rows = openpyxl.load_workbook(WORKBOOK, read_only=True)['ExePatches'].iter_rows(values_only=True)
    header = next(rows)
    found = []
    for r in rows:
        d = dict(zip(header, r))
        if not d.get('VA') or (patch_set and d['Set'] != patch_set):
            continue
        found.append({'id': d['ID'], 'set': d['Set'], 'lever': d['Lever'], 'va': int(d['VA'], 16),
                      'old': bytes.fromhex(d['Old_Hex']), 'new': bytes.fromhex(d['New_Hex']),
                      'float_before': d['Float_Before'], 'float_after': d['Float_After'], 'meaning': d['Meaning']})
    return found


def problems(exe, rows, expect='old'):
    """What stops the set from being written into this executable: [] when every row checks."""
    found = []
    for p in rows:
        if len(p['old']) != len(p['new']):
            found.append(f"{p['id']}: old and new differ in length")
        here = exe.read(p['va'], len(p['old']))
        if here != p[expect]:
            found.append(f"{p['id']}: {here.hex()} at {p['va']:#x}, expected {p[expect].hex()}")
        for key, blob in (('float_before', p['old']), ('float_after', p['new'])):
            if p[key] is not None:
                address = struct.unpack('<I', blob)[0]
                held = struct.unpack('<f', exe.read(address, 4))[0] if exe.offset(address) is not None else None
                if held is None or abs(held - p[key]) > 1e-6:
                    found.append(f"{p['id']}: {address:#x} holds {held}, not {p[key]}")
    return found


def patched(exe, rows):
    data = bytearray(exe.data)
    for p in rows:
        offset = exe.offset(p['va'])
        data[offset:offset + len(p['new'])] = p['new']
    return bytes(data)


def differences(before, after):
    """Offsets where two byte strings of the same length differ."""
    return [k for k in range(len(before)) if before[k] != after[k]]


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def write_checked(path, data):
    """Writes through a temporary file in the same folder, reads it back, and only then puts it in place."""
    temporary = path + '.writing'
    with open(temporary, 'wb') as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    with open(temporary, 'rb') as f:
        if f.read() != data:
            os.remove(temporary)
            raise SystemExit('Nothing installed: the file read back differs from what was written.')
    os.replace(temporary, path)


def keep_vanilla_copy(game_file, copy, every_row):
    """Makes the vanilla copy when there is none, and proves it is byte for byte the file it was made from. A copy is
    only made from a file where every row of the sheet still holds its old bytes: a patched file is never kept as
    vanilla."""
    note = copy + '.sha256'
    if not os.path.exists(copy):
        still_vanilla = problems(Exe(game_file), every_row)
        if still_vanilla:
            raise SystemExit(f'Nothing installed: {game_file} has no vanilla copy and is not the vanilla file.'
                             + LINE_END + LINE_END.join(still_vanilla))
        os.makedirs(os.path.dirname(copy), exist_ok=True)
        shutil.copy2(game_file, copy)
        if sha(copy) != sha(game_file):
            os.remove(copy)
            raise SystemExit('Nothing installed: the copy of the vanilla file does not match the file.')
        with open(note, 'w', encoding='utf-8', newline=LINE_END) as f:
            f.write(f'{sha(copy)}  {os.path.basename(game_file)} as found on the day of the first patch' + LINE_END)
    with open(note, encoding='utf-8') as f:
        if f.read().split()[0] != sha(copy):
            raise SystemExit(f'Nothing installed: {copy} no longer matches the hash written beside it.')


def planned(label, game_file, copy, rows, every_row):
    """The image to write into one game file, or the reasons not to: (bytes, [problem])."""
    vanilla = Exe(copy)
    found = [f'{label}: {m}' for m in problems(vanilla, rows)]
    with open(game_file, 'rb') as f:
        current = f.read()
    known = {vanilla.offset(p['va']) + k for p in every_row for k in range(len(p['new']))}
    if len(current) != len(vanilla.data) or any(k not in known for k in differences(vanilla.data, current)):
        found.append(f'{label}: the file differs from its vanilla copy outside the rows of the sheet')
    if found:
        return None, found
    data = patched(vanilla, rows)
    expected = sorted(vanilla.offset(p['va']) + k for p in rows for k in range(len(p['new'])) if p['new'][k] != p['old'][k])
    if differences(vanilla.data, data) != expected:
        return None, [f'{label}: the patched image differs from vanilla somewhere the rows do not say']
    return data, []


def install(patch_set, targets=TARGETS, rows=None, every_row=None):
    """Writes the set into every target, or into none. Returns [(label, path, bytes changed)]."""
    rows = patches(patch_set) if rows is None else rows
    every_row = patches() if every_row is None else every_row
    if not rows:
        raise SystemExit(f'Nothing written: no rows in set {patch_set}.')
    for _, game_file, copy in targets:
        keep_vanilla_copy(game_file, copy, every_row)
    images, found = [], []
    for label, game_file, copy in targets:
        data, stopped = planned(label, game_file, copy, rows, every_row)
        images.append(data)
        found += stopped
    if found:
        raise SystemExit('Nothing written.' + LINE_END + LINE_END.join(found))
    done = []
    for (label, game_file, copy), data in zip(targets, images):
        write_checked(game_file, data)
        with open(game_file, 'rb') as f:
            installed = f.read()
        if installed != data or problems(Exe(game_file), rows, expect='new'):
            restore(targets)
            raise SystemExit(f'The installed {label} did not check; the vanilla files were put back.')
        with open(copy, 'rb') as f:
            done.append((label, game_file, len(differences(f.read(), installed))))
    return done


def restore(targets=TARGETS):
    """Puts the vanilla copy of every target back. Returns the labels of the files it put back."""
    done = []
    for label, game_file, copy in targets:
        if not os.path.exists(copy):
            continue                                   # no copy: this tool never wrote into the file
        with open(copy + '.sha256', encoding='utf-8') as f:
            if f.read().split()[0] != sha(copy):
                raise SystemExit(f'{copy} no longer matches the hash written beside it.')
        if sha(game_file) != sha(copy):
            shutil.copy2(copy, game_file)
        if sha(game_file) != sha(copy):
            raise SystemExit(f'The {label} put back does not match its vanilla copy.')
        done.append(label)
    return done


def installed_set(targets=TARGETS, every_row=None):
    """What every target carries: {label: {row id: 'patched' | 'vanilla' | the bytes found}}."""
    every_row = patches() if every_row is None else every_row
    found = {}
    for label, game_file, _ in targets:
        exe = Exe(game_file)
        found[label] = {}
        for p in every_row:
            here = exe.read(p['va'], len(p['old']))
            found[label][p['id']] = 'patched' if here == p['new'] else 'vanilla' if here == p['old'] else 'neither: ' + here.hex()
    return found


def keep_saves(label):
    """Copies the save folder of the game into backups/saves/<label>, with a hash per file, and checks the copy."""
    target = os.path.join(BASE_DIR, 'backups', 'saves', label)
    if os.path.exists(target):
        raise SystemExit(f'{target} already exists: choose another label.')
    shutil.copytree(SAVE_DIR, target)
    lines = []
    for name in sorted(os.listdir(SAVE_DIR)):
        source, copy = os.path.join(SAVE_DIR, name), os.path.join(target, name)
        if os.path.isfile(source):
            if sha(source) != sha(copy):
                raise SystemExit(f'The copy of {name} does not match.')
            lines.append(f'{sha(copy)}  {name}')
    with open(os.path.join(target, 'SHA256.txt'), 'w', encoding='utf-8', newline=LINE_END) as f:
        f.write(LINE_END.join(lines) + LINE_END)
    print(f'{len(lines)} save files copied and checked: {target}')


def status():
    carried = installed_set()
    for p in patches():
        states = ', '.join(f'{label} {carried[label][p["id"]]}' for label, _, _ in TARGETS)
        print(f"{p['id']} {p['set']} {p['va']:#x} {states}  {p['meaning'][:80]}")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if command == 'check':
        rows = patches(sys.argv[2])
        found = []
        for label, game_file, copy in TARGETS:
            found += [f'{label}: {m}' for m in problems(Exe(copy if os.path.exists(copy) else game_file), rows)]
        print(LINE_END.join(found) if found else f'{len(rows)} rows of {sys.argv[2]} check in both program files')
    elif command == 'install':
        for label, path, changed in install(sys.argv[2]):
            print(f'{label}: {changed} bytes differ from vanilla in {path}  sha256 {sha(path)[:16]}')
    elif command == 'restore':
        done = restore()
        print(f'vanilla put back: {", ".join(done)}' if done else 'No vanilla copy: nothing was installed by this tool.')
    elif command == 'saves':
        keep_saves(sys.argv[2])
    else:
        status()


if __name__ == '__main__':
    main()

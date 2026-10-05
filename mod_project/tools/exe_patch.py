"""
Patch of the program file, for the levers classed "Executable" in the sheet Levers.

Every byte it writes is a row of the sheet ExePatches of data_tables/balance_criteria.xlsx: an address, the bytes
that must be there, the bytes to write, and for a repointed constant the two floats involved. Nothing is written
unless every row of the set checks, in the executable the game runs (DT22_en.exe) and in the unwrapped copy the
reading was done on.

    python mod_project/tools/exe_patch.py check test1       says whether every row matches both executables
    python mod_project/tools/exe_patch.py install test1     keeps a copy of the vanilla file, then writes the set
    python mod_project/tools/exe_patch.py restore           puts the vanilla file back
    python mod_project/tools/exe_patch.py status            says which rows the installed file carries
    python mod_project/tools/exe_patch.py saves LABEL       copies the save folder into backups/saves/LABEL and checks it

install refuses to write when the game file differs from the vanilla copy anywhere outside the rows of the sheet,
writes through a temporary file that is read back first, and puts the vanilla file back if the result does not check.

The vanilla copy is backups/exe/DT22_en.vanilla.exe (not in git), with its hash beside it. The game file carries a
protector: whether it accepts changed bytes is only known by starting the game.
"""
import hashlib
import os
import shutil
import struct
import sys

import openpyxl

from exe_reader import Exe, EXE_PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'balance_criteria.xlsx')
GAME_EXE = os.path.join(os.path.dirname(EXE_PATH), 'DT22_en.exe')
VANILLA_COPY = os.path.join(BASE_DIR, 'backups', 'exe', 'DT22_en.vanilla.exe')
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


def keep_vanilla_copy():
    """Makes the vanilla copy when there is none, and proves it is byte for byte the file it was made from."""
    note = VANILLA_COPY + '.sha256'
    if not os.path.exists(VANILLA_COPY):
        os.makedirs(os.path.dirname(VANILLA_COPY), exist_ok=True)
        shutil.copy2(GAME_EXE, VANILLA_COPY)
        if sha(VANILLA_COPY) != sha(GAME_EXE):
            os.remove(VANILLA_COPY)
            raise SystemExit('Nothing installed: the copy of the vanilla file does not match the file.')
        with open(note, 'w', encoding='utf-8', newline=LINE_END) as f:
            f.write(f'{sha(VANILLA_COPY)}  DT22_en.exe as found on the day of the first patch' + LINE_END)
    with open(note, encoding='utf-8') as f:
        if f.read().split()[0] != sha(VANILLA_COPY):
            raise SystemExit('Nothing installed: the vanilla copy no longer matches the hash written beside it.')


def install(patch_set):
    rows = patches(patch_set)
    if not rows:
        raise SystemExit(f'Nothing written: no rows in set {patch_set}.')
    keep_vanilla_copy()
    vanilla, unwrapped = Exe(VANILLA_COPY), Exe(EXE_PATH)
    found = [f'vanilla copy: {m}' for m in problems(vanilla, rows)] + [f'unwrapped copy: {m}' for m in problems(unwrapped, rows)]
    if found:
        raise SystemExit('Nothing written.' + LINE_END + LINE_END.join(found))
    with open(GAME_EXE, 'rb') as f:
        current = f.read()
    known = {vanilla.offset(p['va']) + k for p in patches() for k in range(len(p['new']))}
    if len(current) != len(vanilla.data) or any(k not in known for k in differences(vanilla.data, current)):
        raise SystemExit('Nothing written: the game file differs from the vanilla copy outside the rows of the sheet.')
    data = patched(vanilla, rows)
    expected = sorted(vanilla.offset(p['va']) + k for p in rows for k in range(len(p['new'])) if p['new'][k] != p['old'][k])
    if differences(vanilla.data, data) != expected:
        raise SystemExit('Nothing written: the patched image differs from vanilla somewhere the rows do not say.')
    write_checked(GAME_EXE, data)
    with open(GAME_EXE, 'rb') as f:
        installed = f.read()
    if installed != data or problems(Exe(GAME_EXE), rows, expect='new'):
        shutil.copy2(VANILLA_COPY, GAME_EXE)
        raise SystemExit('The installed file did not check; the vanilla file was put back.')
    print(f'{len(rows)} rows, {len(expected)} bytes changed in {GAME_EXE}')
    print(f'vanilla copy: {VANILLA_COPY}  sha256 {sha(VANILLA_COPY)[:16]}')
    print(f'installed:    sha256 {sha(GAME_EXE)[:16]}, same size ({len(installed):,} bytes)')


def restore():
    if not os.path.exists(VANILLA_COPY):
        raise SystemExit('No vanilla copy: nothing was installed by this tool.')
    keep_vanilla_copy()
    shutil.copy2(VANILLA_COPY, GAME_EXE)
    if sha(GAME_EXE) != sha(VANILLA_COPY):
        raise SystemExit('The file put back does not match the vanilla copy.')
    print(f'vanilla file put back: sha256 {sha(GAME_EXE)[:16]}')


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
    game = Exe(GAME_EXE)
    for p in patches():
        here = game.read(p['va'], len(p['old']))
        state = 'patched' if here == p['new'] else 'vanilla' if here == p['old'] else 'neither: ' + here.hex()
        print(f"{p['id']} {p['set']} {p['va']:#x} {state}  {p['meaning'][:90]}")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if command == 'check':
        rows = patches(sys.argv[2])
        source = VANILLA_COPY if os.path.exists(VANILLA_COPY) else GAME_EXE
        found = [f'game file: {m}' for m in problems(Exe(source), rows)] + [f'unwrapped copy: {m}' for m in problems(Exe(EXE_PATH), rows)]
        print(LINE_END.join(found) if found else f'{len(rows)} rows of {sys.argv[2]} check in both executables')
    elif command == 'install':
        install(sys.argv[2])
    elif command == 'restore':
        restore()
    elif command == 'saves':
        keep_saves(sys.argv[2])
    else:
        status()


if __name__ == '__main__':
    main()

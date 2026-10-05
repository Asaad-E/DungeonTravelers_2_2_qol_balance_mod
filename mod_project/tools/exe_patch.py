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

The vanilla copy is backups/exe/DT22_en.vanilla.exe (not in git). The game file carries a protector: whether it
accepts changed bytes is only known by starting the game.
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


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def install(patch_set):
    rows = patches(patch_set)
    source = VANILLA_COPY if os.path.exists(VANILLA_COPY) else GAME_EXE
    game, unwrapped = Exe(source), Exe(EXE_PATH)
    found = [f'game file: {m}' for m in problems(game, rows)] + [f'unwrapped copy: {m}' for m in problems(unwrapped, rows)]
    if not rows or found:
        raise SystemExit('Nothing written.\n' + '\n'.join(found or [f'no rows in set {patch_set}']))
    if not os.path.exists(VANILLA_COPY):
        os.makedirs(os.path.dirname(VANILLA_COPY), exist_ok=True)
        shutil.copy2(GAME_EXE, VANILLA_COPY)
    data = patched(game, rows)
    with open(GAME_EXE, 'wb') as f:
        f.write(data)
    changed = sum(len(p['new']) for p in rows)
    print(f'{len(rows)} rows, {changed} bytes written into {GAME_EXE}')
    print(f'vanilla copy: {VANILLA_COPY} ({sha(VANILLA_COPY)[:16]})')
    print(f'installed:    {sha(GAME_EXE)[:16]}')


def restore():
    if not os.path.exists(VANILLA_COPY):
        raise SystemExit('No vanilla copy: nothing was installed by this tool.')
    shutil.copy2(VANILLA_COPY, GAME_EXE)
    print(f'vanilla file put back: {sha(GAME_EXE)[:16]}')


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
        print('\n'.join(found) if found else f'{len(rows)} rows of {sys.argv[2]} check in both executables')
    elif command == 'install':
        install(sys.argv[2])
    elif command == 'restore':
        restore()
    else:
        status()


if __name__ == '__main__':
    main()

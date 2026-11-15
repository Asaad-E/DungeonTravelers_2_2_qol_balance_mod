#!/usr/bin/env python3
"""
Dungeon Travelers 2-2 (PC, English) mod installer for Linux, Steam Deck, and Windows.
Cross-platform implementation of mod_patch.ps1 using standard library only.

Usage:
    python3 mod_patch.py install <variant>
    python3 mod_patch.py uninstall
"""
import hashlib
import os
import struct
import sys

UPDATED_MSG = [
    "The game was updated or repaired after the mod was installed, so the copies kept in",
    "backup belong to an older game. Delete the folder DT22_Mod/backup and the file",
    "DT22_Mod/installed.txt, have the launcher of the game check its files, and install again."
]


def get_sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def norm_rel(path_str: str) -> str:
    return os.path.normpath(path_str.replace('\\', os.sep).replace('/', os.sep))


def stop_with(lines):
    for line in lines:
        print(line)
    print()
    print("Nothing was changed.")
    sys.exit(1)


def holds_at(path: str, offset: int, expected: bytes) -> bool:
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    if offset + len(expected) > size:
        return False
    with open(path, 'rb') as f:
        f.seek(offset)
        held = f.read(len(expected))
    return held == expected


def put_at(path: str, offset: int, data: bytes):
    with open(path, 'r+b') as f:
        f.seek(offset)
        f.write(data)


def read_state(state_file: str) -> dict:
    state = {}
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) == 2:
                    state[norm_rel(parts[0]).lower()] = parts[1]
    return state


def changed_since(state: dict, root: str, rel: str, known: list) -> bool:
    key = norm_rel(rel).lower()
    if key not in state:
        return False
    game = os.path.join(root, rel)
    if not os.path.exists(game):
        return True
    with open(game, 'rb') as f:
        now_hash = get_sha(f.read())
    return (now_hash != state[key]) and (now_hash not in known)


def backup_files(backup_dir: str) -> list:
    if not os.path.exists(backup_dir):
        return []
    result = []
    for root, _, files in os.walk(backup_dir):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, backup_dir)
            result.append(norm_rel(rel))
    return sorted(result)


def read_pokes(path: str) -> list:
    pokes = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_str = line.strip()
                parts = line_str.split('|')
                if len(parts) >= 5 and parts[0] == 'poke':
                    pokes.append({
                        'rel': norm_rel(parts[1]),
                        'offset': int(parts[2], 16),
                        'old': bytes.fromhex(parts[3]),
                        'new': bytes.fromhex(parts[4]),
                        'line': line_str
                    })
    return pokes


def known_pokes(mod_dir: str) -> list:
    all_pokes = []
    if os.path.exists(mod_dir):
        for fname in sorted(os.listdir(mod_dir)):
            if fname.lower().endswith('.txt'):
                all_pokes.extend(read_pokes(os.path.join(mod_dir, fname)))
    return all_pokes


def undo_pokes(root: str, pokes_list: list) -> int:
    count = 0
    for p in pokes_list:
        path = os.path.join(root, p['rel'])
        if os.path.exists(path) and holds_at(path, p['offset'], p['new']):
            put_at(path, p['offset'], p['old'])
            count += 1
    return count


def write_file_safe(path: str, data: bytes):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)


def _is_writable_exclusive(path: str) -> bool:
    """True when `path` can be opened with exclusive read/write access (matching .NET FileShare.None)."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        generic_read = 0x80000000
        generic_write = 0x40000000
        open_existing = 3
        invalid_handle = wintypes.HANDLE(-1).value
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.CreateFileW(path, generic_read | generic_write, 0, None, open_existing, 0, None)
        if handle == invalid_handle:
            return False
        kernel32.CloseHandle(handle)
        return True
    try:
        with open(path, 'r+b'):
            return True
    except OSError:
        return False


def get_locked(root: str, rels) -> list:
    """Return error lines for any existing target file under `root` currently held open or read-only."""
    locked = []
    seen = set()
    for rel in sorted(rels, key=str.lower):
        key = norm_rel(rel).lower()
        if key in seen:
            continue
        seen.add(key)
        target = os.path.join(root, rel)
        if not os.path.exists(target):
            continue
        if not _is_writable_exclusive(target):
            locked.append(f"{rel}: in use. Close the game and run this again.")
    return locked


def main(script_dir=None):
    args = sys.argv[1:]
    mode = args[0].lower() if args else 'install'
    variant = args[1].lower() if len(args) > 1 else ''

    if script_dir is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    mod_dir = script_dir
    root = os.path.dirname(mod_dir)
    backup = os.path.join(mod_dir, 'backup')
    state_file = os.path.join(mod_dir, 'installed.txt')
    poke_file = os.path.join(mod_dir, 'pokes.txt')

    param_check = os.path.join(root, 'Data', 'ENG', 'Parameter')
    if not os.path.isdir(param_check):
        stop_with([
            f"This is not the folder of the game: {root}",
            "Unpack the archive into the folder that holds the .exe of the game and its folder Data."
        ])

    if mode == 'uninstall':
        kept = backup_files(backup)
        written = known_pokes(mod_dir)
        if not kept and not written:
            print("No backup here: the mod is not installed.")
            sys.exit(0)
        locked = get_locked(root, kept + [p['rel'] for p in written])
        if locked:
            stop_with(locked)
        state = read_state(state_file)
        moved = []
        for rel in kept:
            src_path = os.path.join(backup, rel)
            with open(src_path, 'rb') as f:
                orig_sha = get_sha(f.read())
            if changed_since(state, root, rel, [orig_sha]):
                moved.append(f"{rel}: changed since the mod was installed")
        if moved:
            stop_with(moved + UPDATED_MSG)

        staged = []
        try:
            for rel in kept:
                dest = os.path.join(root, rel)
                stage = dest + '.dt22new'
                staged.append(stage)
                with open(os.path.join(backup, rel), 'rb') as sf:
                    write_file_safe(stage, sf.read())
            for rel in kept:
                dest = os.path.join(root, rel)
                os.replace(dest + '.dt22new', dest)
            undo_pokes(root, written)
            if os.path.exists(poke_file):
                os.remove(poke_file)
        except Exception as e:
            for stage in staged:
                if os.path.exists(stage):
                    try:
                        os.remove(stage)
                    except OSError:
                        pass
            stop_with([f"A file could not be written: {e}", "Close the game and run this again."])

        if os.path.exists(backup):
            import shutil
            shutil.rmtree(backup, ignore_errors=True)
        if os.path.exists(state_file):
            os.remove(state_file)
        print(f"The game is as it was: {len(kept)} file(s) put back.")
        sys.exit(0)

    # ---- INSTALL ----
    manifest_path = os.path.join(mod_dir, f"{variant}.txt")
    if not os.path.exists(manifest_path):
        stop_with([f"No variant '{variant}' in this archive."])

    ops_path = os.path.join(mod_dir, f"{variant}.ops")
    blob_path = os.path.join(mod_dir, f"{variant}.dat")
    with open(ops_path, 'rb') as f:
        ops = f.read()
    with open(blob_path, 'rb') as f:
        blob = f.read()

    files = []
    layouts = {}
    with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            p = line.strip().split('|')
            if p[0] == 'file':
                files.append({
                    'rel': norm_rel(p[1]),
                    'old': p[2],
                    'new': p[3],
                    'size': int(p[4]),
                    'start': int(p[5]),
                    'count': int(p[6])
                })
            elif p[0] == 'exe':
                layout_key = p[1]
                layouts.setdefault(layout_key, []).append({
                    'offset': int(p[2], 16),
                    'old': bytes.fromhex(p[3]),
                    'new': bytes.fromhex(p[4])
                })

    pokes = read_pokes(manifest_path)
    pre_locked = get_locked(root, [f['rel'] for f in files] + [p['rel'] for p in pokes] + backup_files(backup))
    if pre_locked:
        stop_with(pre_locked)

    state = read_state(state_file)
    stale = False
    problems = []
    writes = []
    named = {}

    # 1. Data files
    for f in files:
        named[f['rel'].lower()] = True
        game = os.path.join(root, f['rel'])
        copy_path = os.path.join(backup, f['rel'])
        if not os.path.exists(game) and not os.path.exists(copy_path):
            problems.append(f"{f['rel']}: not found in the game")
            continue
        has_copy = os.path.exists(copy_path)
        path = copy_path if has_copy else game
        if has_copy and changed_since(state, root, f['rel'], [f['old'], f['new']]):
            problems.append(f"{f['rel']}: changed since the mod was installed")
            stale = True
            continue
        with open(path, 'rb') as src_file:
            source = src_file.read()
        if get_sha(source) != f['old']:
            problems.append(f"{f['rel']}: not the original file (another version of the game, or another mod is installed)")
            continue

        out = bytearray(f['size'])
        pos = 0
        for k in range(f['count']):
            at = (f['start'] + k) * 12
            kind, from_pos, length = struct.unpack_from('<3i', ops, at)
            if kind == 0:
                out[pos:pos + length] = source[from_pos:from_pos + length]
            else:
                out[pos:pos + length] = blob[from_pos:from_pos + length]
            pos += length

        out_bytes = bytes(out)
        if pos != f['size'] or get_sha(out_bytes) != f['new']:
            problems.append(f"{f['rel']}: the result does not check")
            continue

        keep = source if not has_copy else None
        writes.append({'rel': f['rel'], 'bytes': out_bytes, 'source': keep})

    # 2. Exe files
    programs = 0
    exe_names = sorted(n for n in os.listdir(root) if n.lower().endswith('.exe')) if os.path.isdir(root) else []
    for exe_name in exe_names:
        if not layouts:
            break
        rel = norm_rel(exe_name)
        copy_path = os.path.join(backup, rel)
        has_copy = os.path.exists(copy_path)
        path = copy_path if has_copy else os.path.join(root, rel)
        with open(path, 'rb') as ef:
            source = bytearray(ef.read())
        if has_copy and changed_since(state, root, rel, [get_sha(source)]):
            problems.append(f"{rel}: changed since the mod was installed")
            stale = True
            continue

        matching_rows = None
        for name, rows in layouts.items():
            fits = True
            for r in rows:
                if source[r['offset']:r['offset'] + len(r['old'])] != r['old']:
                    fits = False
                    break
            if fits:
                matching_rows = rows
                break

        if matching_rows is None:
            if has_copy:
                problems.append(f"{rel}: its copy in the backup is not the program this mod was made for")
            continue

        programs += 1
        named[rel.lower()] = True
        out = bytearray(source)
        for r in matching_rows:
            out[r['offset']:r['offset'] + len(r['new'])] = r['new']
        keep = bytes(source) if not has_copy else None
        writes.append({'rel': rel, 'bytes': bytes(out), 'source': keep})

    if layouts and programs == 0 and not stale:
        problems.append("No program file of the game found here in its original state (is another mod installed?)")

    # Files another variant changed
    for rel in backup_files(backup):
        if rel.lower() in named:
            continue
        with open(os.path.join(backup, rel), 'rb') as bf:
            orig_sha = get_sha(bf.read())
        if changed_since(state, root, rel, [orig_sha]):
            problems.append(f"{rel}: changed since the mod was installed")
            stale = True

    # Pokes
    known = known_pokes(mod_dir)
    before = {}
    for k in known:
        key = f"{k['rel'].lower()}|{k['offset']}"
        before.setdefault(key, []).append(k['new'])

    odd = {}
    for k in pokes:
        if k['rel'] in odd:
            continue
        path = os.path.join(root, k['rel'])
        if not os.path.exists(path):
            odd[k['rel']] = "not found in the game"
            continue
        fine = holds_at(path, k['offset'], k['old']) or holds_at(path, k['offset'], k['new'])
        if not fine:
            for val in before.get(f"{k['rel'].lower()}|{k['offset']}", []):
                if holds_at(path, k['offset'], val):
                    fine = True
                    break
        if not fine:
            odd[k['rel']] = "not the original file (another version of the game, or another mod is installed)"

    for rel, msg in odd.items():
        problems.append(f"{rel}: {msg}")
    if stale:
        problems.extend(UPDATED_MSG)

    # Check writable (including cross-variant restores before any writes)
    cross_back = [rel for rel in backup_files(backup) if rel.lower() not in named]
    touched = [w['rel'] for w in writes] + [p['rel'] for p in pokes] + cross_back
    problems.extend(get_locked(root, touched))

    if problems:
        stop_with(problems)

    # 3. Write
    staged_suffix = '.dt22new'
    try:
        for w in writes:
            if w['source'] is not None:
                copy_path = os.path.join(backup, w['rel'])
                write_file_safe(copy_path + staged_suffix, w['source'])
                os.replace(copy_path + staged_suffix, copy_path)
            target = os.path.join(root, w['rel'])
            write_file_safe(target + staged_suffix, w['bytes'])

        for rel in cross_back:
            src = os.path.join(backup, rel)
            dst = os.path.join(root, rel)
            with open(src, 'rb') as sf:
                write_file_safe(dst + staged_suffix, sf.read())

        for w in writes:
            target = os.path.join(root, w['rel'])
            os.replace(target + staged_suffix, target)

        back_count = 0
        for rel in cross_back:
            dst = os.path.join(root, rel)
            os.replace(dst + staged_suffix, dst)
            back_count += 1

        with open(state_file + staged_suffix, 'w', encoding='utf-8') as sf:
            for w in writes:
                sf.write(f"{w['rel']}|{get_sha(w['bytes'])}\n")
        os.replace(state_file + staged_suffix, state_file)

        # Pokes write
        record = sorted(set(k['line'] for k in known) | set(p['line'] for p in pokes))
        if record:
            with open(poke_file + staged_suffix, 'w', encoding='utf-8') as pf:
                for line in record:
                    pf.write(line + '\n')
            os.replace(poke_file + staged_suffix, poke_file)

        undo_pokes(root, known)
        for k in pokes:
            put_at(os.path.join(root, k['rel']), k['offset'], k['new'])

        if pokes:
            with open(poke_file + staged_suffix, 'w', encoding='utf-8') as pf:
                for k in pokes:
                    pf.write(k['line'] + '\n')
            os.replace(poke_file + staged_suffix, poke_file)
        elif os.path.exists(poke_file):
            os.remove(poke_file)

    except Exception as e:
        cleanup = [os.path.join(root, w['rel']) + staged_suffix for w in writes]
        cleanup += [os.path.join(backup, w['rel']) + staged_suffix for w in writes if w['source'] is not None]
        cleanup += [os.path.join(root, rel) + staged_suffix for rel in cross_back]
        cleanup += [state_file + staged_suffix, poke_file + staged_suffix]
        for left in cleanup:
            if os.path.exists(left):
                try:
                    os.remove(left)
                except OSError:
                    pass
        print(f"A file could not be written: {e}")
        print("Close the game and run this again. To put everything back, run the Uninstall script.")
        sys.exit(1)

    print(f"Done: {len(files)} data file(s) changed, {programs} program file(s) patched.")
    if pokes:
        print(f"{len(pokes)} value(s) changed in the files of the dungeons.")
    if back_count > 0:
        print(f"{back_count} file(s) of another variant put back as the original.")
    print(f"A copy of every original is in DT22_Mod/backup. To take the mod out, run the Uninstall script.")


if __name__ == '__main__':
    main()

"""The player installer run on a copy of the game made from the originals: install, install again, the other variant,
uninstall, and what it does when a file of the game changed after the mod was installed (an update of the game with
an old backup beside it). Works in a temporary folder of build/; the game is not touched. The packs of the dungeons
are copied from the game, which must hold its own values (tools/floor_patch.py status).

    python measures/installer_trial.py              in build/installer_trial_*
    python measures/installer_trial.py --odd-path   in a folder whose name holds Japanese letters and brackets
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import package_variant                                    # noqa: E402


def run(root, *args):
    script = os.path.join(root, package_variant.MOD_DIR, 'mod_patch.ps1')
    done = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script, *args],
                          capture_output=True, text=True)
    return done.returncode, [line for line in (done.stdout + done.stderr).splitlines() if line.strip()]


def main():
    archives = {v: sorted(glob.glob(os.path.join(PROJECT, 'dist', f'DT22_{v}_*.zip')))[-1] for v in ('balance', 'qol')}
    os.makedirs(os.path.join(PROJECT, 'build'), exist_ok=True)
    # --odd-path: a folder name with non-Latin letters and brackets (wildcards to PowerShell's -Path)
    prefix = 'installer_trial_ゲーム [テスト] ' if '--odd-path' in sys.argv else 'installer_trial_'
    root = tempfile.mkdtemp(prefix=prefix, dir=os.path.join(PROJECT, 'build'))
    try:
        rels, pokes = set(), []
        for path in archives.values():
            with zipfile.ZipFile(path) as z:
                z.extractall(root)
                for name in z.namelist():
                    if name.endswith('.txt') and name.startswith(package_variant.MOD_DIR):
                        for line in z.read(name).decode('utf-8').splitlines():
                            if line.startswith('file|'):
                                rels.add(line.split('|')[1])
                            elif line.startswith('poke|'):
                                _, rel, offset, old, new = line.split('|')
                                pokes.append((rel, int(offset, 16), bytes.fromhex(old), bytes.fromhex(new)))
        backups = os.path.join(PROJECT, 'backups')
        originals = {os.path.basename(p): p for p in glob.glob(os.path.join(backups, '**', '*'), recursive=True) if os.path.isfile(p)}
        for rel in rels:                                    # the originals, where the game has them
            target = os.path.join(root, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(originals[os.path.basename(rel)], target)
        programs = {name.replace('.vanilla', ''): path for name, path in originals.items() if name.endswith('.vanilla.exe')}
        for name, path in programs.items():
            shutil.copyfile(path, os.path.join(root, name))
        import mod_config
        for rel in sorted({p[0] for p in pokes}):           # the packs of the dungeons, from the game: they must hold its values
            target = os.path.join(root, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(os.path.join(mod_config.game_dir(), rel), target)

        def held(which):
            # True when every place written in place holds the value of the game (2) or of the variant (3)
            for rel, offset, old, new in pokes:
                with open(os.path.join(root, rel), 'rb') as f:
                    f.seek(offset)
                    if f.read(4) != (old, new)[which - 2]:
                        return False
            return True

        one = os.path.join(root, sorted(rels)[0])
        with open(one, 'rb') as f:
            original = f.read()

        def step(label, expected, *args):
            code, lines = run(root, *args)
            print(f"{'ok  ' if code == expected else 'FAIL'} {label}: exit {code} | {lines[0] if lines else ''} ... {lines[-1] if lines else ''}")
            return code == expected

        good = [held(2), step('install balance', 0, 'install', 'balance'), held(3),
                step('install balance again', 0, 'install', 'balance'), held(3),
                step('change to qol', 0, 'install', 'qol'), held(2),
                step('back to balance', 0, 'install', 'balance'), held(3)]
        print(f'{len(pokes)} values written in place follow the variant:', all(good))
        record = os.path.join(root, package_variant.MOD_DIR, 'pokes.txt')
        os.remove(record)                                   # the record of what was written in place is lost
        good += [step('record lost, change to qol', 0, 'install', 'qol'), held(2),
                 step('back to balance', 0, 'install', 'balance'), held(3)]
        rel, offset, old, new = pokes[0]                    # an older version of the mod wrote another value there
        other = bytes([new[0] + 1]) + new[1:]
        with open(os.path.join(root, rel), 'r+b') as f:
            f.seek(offset)
            f.write(other)
        with open(record, encoding='utf-8') as f:
            lines = f.read().splitlines()
        lines[0] = 'poke|' + rel + f'|{offset:x}|' + old.hex() + '|' + other.hex()
        with open(record, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
        good += [step('an older version wrote another value, install', 0, 'install', 'balance'), held(3)]
        print('a lost record and an older value are put right:', all(good))
        with open(one, 'wb') as f:                          # the game repaired this file: the original again
            f.write(original)
        good.append(step('one file back as the original, install', 0, 'install', 'balance'))
        with open(one, 'wb') as f:                          # the game updated this file
            f.write(original + b'new version')
        good += [step('one file updated by the game, install refused', 1, 'install', 'balance'),
                 step('one file updated by the game, uninstall refused', 1, 'uninstall')]
        with open(one, 'rb') as f:
            good.append(f.read().endswith(b'new version'))
        shutil.rmtree(os.path.join(root, package_variant.MOD_DIR, 'backup'))
        os.remove(os.path.join(root, package_variant.MOD_DIR, 'installed.txt'))
        for name in ('pokes.txt',):                         # the launcher checked the files: nothing of the mod is left
            path = os.path.join(root, package_variant.MOD_DIR, name)
            if os.path.exists(path):
                os.remove(path)
        for rel in sorted({p[0] for p in pokes}):
            shutil.copyfile(os.path.join(mod_config.game_dir(), rel), os.path.join(root, rel))
        with open(one, 'wb') as f:
            f.write(original)
        for rel in rels:                                    # the launcher checked the files: originals again
            shutil.copyfile(originals[os.path.basename(rel)], os.path.join(root, rel))
        for name, path in programs.items():
            shutil.copyfile(path, os.path.join(root, name))
        good += [step('after the advice, install', 0, 'install', 'balance'), held(3), step('uninstall', 0, 'uninstall'), held(2)]
        same = all(open(os.path.join(root, rel), 'rb').read() == open(originals[os.path.basename(rel)], 'rb').read() for rel in rels)
        print('every file as the original after the uninstall:', same)
        print('ALL GOOD' if all(good) and same else 'SOMETHING FAILED')
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

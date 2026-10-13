"""The player installer run on a copy of the game made from the originals: install, install again, the other variant,
uninstall, and what it does when a file of the game changed after the mod was installed (an update of the game with
an old backup beside it). Works in a temporary folder of build/; the game is not touched.

    python measures/installer_trial.py
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
    root = tempfile.mkdtemp(prefix='installer_trial_', dir=os.path.join(PROJECT, 'build'))
    try:
        rels = set()
        for path in archives.values():
            with zipfile.ZipFile(path) as z:
                z.extractall(root)
                for name in z.namelist():
                    if name.endswith('.txt') and name.startswith(package_variant.MOD_DIR):
                        for line in z.read(name).decode('utf-8').splitlines():
                            if line.startswith('file|'):
                                rels.add(line.split('|')[1])
        backups = os.path.join(PROJECT, 'backups')
        originals = {os.path.basename(p): p for p in glob.glob(os.path.join(backups, '**', '*'), recursive=True) if os.path.isfile(p)}
        for rel in rels:                                    # the originals, where the game has them
            target = os.path.join(root, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(originals[os.path.basename(rel)], target)
        programs = {name.replace('.vanilla', ''): path for name, path in originals.items() if name.endswith('.vanilla.exe')}
        for name, path in programs.items():
            shutil.copyfile(path, os.path.join(root, name))
        one = os.path.join(root, sorted(rels)[0])
        with open(one, 'rb') as f:
            original = f.read()

        def step(label, expected, *args):
            code, lines = run(root, *args)
            print(f"{'ok  ' if code == expected else 'FAIL'} {label}: exit {code} | {lines[0] if lines else ''} ... {lines[-1] if lines else ''}")
            return code == expected

        good = [step('install balance', 0, 'install', 'balance'),
                step('install balance again', 0, 'install', 'balance'),
                step('change to qol', 0, 'install', 'qol'),
                step('back to balance', 0, 'install', 'balance')]
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
        with open(one, 'wb') as f:
            f.write(original)
        for rel in rels:                                    # the launcher checked the files: originals again
            shutil.copyfile(originals[os.path.basename(rel)], os.path.join(root, rel))
        for name, path in programs.items():
            shutil.copyfile(path, os.path.join(root, name))
        good += [step('after the advice, install', 0, 'install', 'balance'), step('uninstall', 0, 'uninstall')]
        same = all(open(os.path.join(root, rel), 'rb').read() == open(originals[os.path.basename(rel)], 'rb').read() for rel in rels)
        print('every file as the original after the uninstall:', same)
        print('ALL GOOD' if all(good) and same else 'SOMETHING FAILED')
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

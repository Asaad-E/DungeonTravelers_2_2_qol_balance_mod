"""
The archives for players, from start to end: both variants built, verified and packaged in one command.

    python tools/package_all.py

For each variant (qol, balance), stopping at the first step that fails:
    1. tools/build_variant.py <variant> --no-install    builds it from the workbooks and the originals, and verifies it
    2. tools/package_variant.py <variant>               writes dist/DT22_<variant>_<date>.zip (differences only)

Before it writes, every older archive of dist/ is removed, so the folder holds the two of this run and nothing else.
The game folder is not touched: to put a variant into your own game use tools/apply_mod.py.
"""
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(os.path.dirname(TOOLS), 'dist')
VARIANTS = ('qol', 'balance')


def run(script, *args):
    print(f'--- {script} {" ".join(args)}', flush=True)
    return subprocess.call([sys.executable, os.path.join(TOOLS, script), *args])


def main():
    for variant in VARIANTS:
        if run('build_variant.py', variant, '--no-install'):
            print(f'[FAIL] the {variant} variant did not build: no archive was written or removed')
            return 1
    import datetime
    from package_variant import PREFIX
    old = [n for n in sorted(os.listdir(DIST_DIR)) if n.lower().endswith('.zip')] if os.path.isdir(DIST_DIR) else []
    stamp_before = datetime.date.today().isoformat()
    for variant in VARIANTS:
        if run('package_variant.py', variant):
            print(f'[FAIL] packaging {variant} failed; previous archives in {DIST_DIR} were kept')
            return 1
    stamp_after = datetime.date.today().isoformat()
    keep = {f'{PREFIX}_{v}_{s}.zip'.lower() for v in VARIANTS for s in (stamp_before, stamp_after)}
    for name in old:
        if name.lower() not in keep:
            os.remove(os.path.join(DIST_DIR, name))
    print(f'{len(old)} older archive(s) removed from {DIST_DIR}; it holds:')
    for name in sorted(os.listdir(DIST_DIR)):
        print(f'    {name}  ({os.path.getsize(os.path.join(DIST_DIR, name)):,} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())

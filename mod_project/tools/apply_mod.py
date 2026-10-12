"""
Puts the mod into your game, from start to end: the three steps of the README in one command.

    python mod_project/tools/apply_mod.py balance      the Balance variant (values changed, and the program patched)
    python mod_project/tools/apply_mod.py qol          the QoL variant (more information, no value changed)
    python mod_project/tools/apply_mod.py vanilla      the game as it was: every original file and the program put back

What it runs, stopping at the first step that fails:
    1. tools/setup_backups.py     the originals of your game copied into mod_project/backups/ and checked
    2. tools/build_variant.py     the variant built from them and verified (never installs by itself here)
    3. tools/install_variant.py   the built files put into the game (what they replace is saved), the program files
                                  found in the folder of the game and patched or put back

Close the game first. The folder of the game: mod_project/config.json (see config.example.json), else the folder
DungeonTravelers2-2_EN beside mod_project.
"""
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
VARIANTS = ('balance', 'qol')


def run(script, *args):
    print(f'--- {script} {" ".join(args)}', flush=True)
    return subprocess.call([sys.executable, os.path.join(TOOLS, script), *args])


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in VARIANTS + ('vanilla',):
        print(__doc__)
        return 1
    what = sys.argv[1]
    if run('setup_backups.py'):
        return 1
    if what == 'vanilla':
        sys.path.insert(0, TOOLS)
        import install_variant
        result = install_variant.install('vanilla')
        install_variant.report('vanilla', *result)
        for line in install_variant.install_program('vanilla'):
            print(line)
        return 1 if result[2] else 0
    if run('build_variant.py', what, '--no-install'):
        return 1
    return run('install_variant.py', what)


if __name__ == '__main__':
    sys.exit(main())

"""One-off edit of 2026-10-12: the texts that describe the archive for players follow its new shape (differences and
a script that applies them, no file of the game). Kept as the record of what was changed."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = chr(10)


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


def write(rel, text):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline=NL).write(text)


def cut(text, start, end, new, name):
    a = text.index(start)
    b = text.index(end, a) if end else len(text)
    return text[:a] + new + text[b:]


INSTALL = '''Install
-------
This archive holds no file of the game: only the differences, and a script that applies them to
your own copy.

1. Close the game. It must be the original game, with no other mod installed.
2. Unpack this archive into the folder of the game: the one that holds the game's .exe and its
   folder "Data". You now have there "Install_{title}.bat", "Uninstall_DT22_Mod.bat" and a folder
   "DT22_Mod".
3. Run "Install_{title}.bat" (double click).

It checks every file it is about to change, keeps a copy of each original in "DT22_Mod\\backup",
and then changes them.{program} If a file is not the original one it says which and changes nothing.
The window ends with "Done: ..." when all went well.

Uninstall
---------
Run "Uninstall_DT22_Mod.bat". Every file goes back as it was.

To change from one variant of the mod to the other, unpack the other archive into the same
folder and run its Install .bat: there is no need to uninstall first.

'''
PROGRAM = (' It also changes 19 bytes of the program (the EXP by level gap,' + NL +
           'the Crown, the chance of Arcane Shield and the passive Concentrate) in every .exe of the' + NL +
           'folder that is the game.')

t = read('release/README_Balance.txt')
t = cut(t, 'Install' + NL + '-------', 'Saves' + NL + '-----', INSTALL.format(title='Balance', program=PROGRAM), 'balance')
t = t.replace('DRAFT, to be reviewed by the author before any release.' + NL + NL, '')
write('release/README_Balance.txt', t)

t = read('release/README_QoL.txt')
end = 'Saves' + NL + '-----' if 'Saves' + NL + '-----' in t else None
t = cut(t, 'Install' + NL + '-------', end, INSTALL.format(title='QoL', program=''), 'qol')
write('release/README_QoL.txt', t)

t = read('tests/test_qol_items_and_install.py')
a = t.index('class Package(unittest.TestCase):')
b = t.index(NL + NL + NL, a) if NL + NL + NL in t[a:] else len(t)
new = '''class Package(unittest.TestCase):
    """The player package: differences that rebuild every changed file from its original, and no file of the game."""

    def test_package_rebuilds_every_changed_file_and_holds_no_file_of_the_game(self):
        import struct
        import zipfile
        import package_variant
        if not os.path.isdir(os.path.join(package_variant.BUILD_DIR, 'qol')):
            self.skipTest('variant not built')
        with tempfile.TemporaryDirectory() as out:
            path, files, problems = package_variant.package('qol', out_dir=out, stamp='test')
            self.assertEqual(problems, [])
            with zipfile.ZipFile(path) as z:
                names = set(z.namelist())
                self.assertEqual(names, {'Install_QoL.bat', 'Uninstall_DT22_Mod.bat', 'DT22_Mod/mod_patch.ps1',
                                         'DT22_Mod/README.txt', 'DT22_Mod/qol.txt', 'DT22_Mod/qol.ops', 'DT22_Mod/qol.dat'})
                ops, blob = z.read('DT22_Mod/qol.ops'), z.read('DT22_Mod/qol.dat')
                lines = [line.split('|') for line in z.read('DT22_Mod/qol.txt').decode('utf-8').splitlines()]
            listed = {line[1]: line for line in lines if line[0] == 'file'}
            self.assertEqual(len(listed), len(files))
            self.assertFalse([line for line in lines if line[0] == 'exe'])          # the QoL variant leaves the program alone
            for sub, name, built, original in files:
                _, _, before, after, size, start, count = listed[chr(92).join(('Data', 'ENG', sub, name))]
                self.assertEqual(before, package_variant.sha(original))
                out_bytes = bytearray()
                for k in range(int(start), int(start) + int(count)):                # as release/mod_patch.ps1 applies them
                    kind, at, length = struct.unpack_from('<3i', ops, 12 * k)
                    out_bytes += (original if kind == package_variant.COPY else blob)[at:at + length]
                self.assertEqual(bytes(out_bytes), built)
                self.assertEqual((after, int(size)), (package_variant.sha(built), len(built)))
                self.assertNotIn(built, blob)                                       # the file itself is not shipped
            self.assertLess(len(blob), sum(len(built) for _, _, built, _ in files) // 2)
'''
t = t[:a] + new + t[b:]
write('tests/test_qol_items_and_install.py', t)

t = read('CLAUDE.md')
old = 'the archive for players (balance: with the script that writes the program patch)'
assert t.count(old) == 1
t = t.replace(old, 'the archive for players: differences and a script that applies them to the own game of the player, no file of the game (dist/, to unpack into the game folder)')
write('CLAUDE.md', t)

t = read('docs/QOL_ROADMAP.md')
a = t.index('8. **[done] Release.**')
b = t.index(NL, a)
t = t[:a] + ('8. **[done] Release.** `python tools/package_variant.py qol` writes `dist/DT22_qol_<date>.zip`: the differences of '
             'the files the variant changes and the script that applies them to the own game of the player (`release/mod_patch.ps1`), '
             'with `release/README_QoL.txt`. No file of the game is in the archive (changed on 2026-10-12; it held the files and '
             'their originals before).') + t[b:]
write('docs/QOL_ROADMAP.md', t)

t = read('docs/dungeontravelers2-2.md')
a = t.index('**Package.** `tools/package_variant.py qol`')
b = t.index(NL, a)
t = t[:a] + ('**Package.** `tools/package_variant.py <variant>` -> `dist/DT22_<variant>_<date>.zip`, to unpack into the folder of '
             'the game: for each file that differs from the original, the steps that rebuild it from that original (copy a run '
             'of it, or take bytes the archive carries) with the hash before and after; `release/mod_patch.ps1`, which checks, '
             'keeps a copy, applies and checks again, and for the Balance variant patches every `.exe` of the folder that is the '
             'program; an Install and an Uninstall `.bat`. No file of the game is in the archive.') + t[b:]
write('docs/dungeontravelers2-2.md', t)

t = read('README.md')
old = '## Install, step by step' + NL
assert t.count(old) == 1
t = t.replace(old, '''## Two ways to get the mod

- **To play it:** take the archive of the variant you want from the *Releases* of this repository, unpack it into the
  folder of the game and run its `Install` file. No Python is needed; the steps are in the `README.txt` of the
  archive. It holds only differences, applied to your own copy of the game.
- **To build it yourself**, or to read and change it: the steps below.

## Build and install from this repository, step by step
''')
write('README.md', t)
print('texts updated')

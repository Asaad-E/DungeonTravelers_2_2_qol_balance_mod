"""One-off edit of 2026-10-12: the tools take the folder of the game and its program files from tools/mod_config.py
(config.json) in the place of a path written in each of them; tools/exe_patch.py finds the program files itself.
Kept as the record of what was changed; running it twice stops at the first text it no longer finds."""
import io
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = chr(10)


def sub(path, pairs):
    path = os.path.join(PROJECT, path)
    s = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        if s.count(old) != 1:
            raise SystemExit(f'{path}: {s.count(old)} matches of {old[:70]!r}')
        s = s.replace(old, new)
    io.open(path, 'w', encoding='utf-8', newline=NL).write(s)


sub('tools/exe_reader.py', [
    ("BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))" + NL +
     "EXE_PATH = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'DT22_en_unwrapped.exe')" + NL,
     "import mod_config" + NL + NL +
     "BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))" + NL +
     "# the program file the formulas are read from: the one config.json names, else this one of the game folder" + NL +
     "EXE_PATH = mod_config.formula_exe() or os.path.join(mod_config.game_dir(), 'DT22_en_unwrapped.exe')" + NL),
])

sub('tools/exe_patch.py', [
    ("that must be there, the bytes to write, and for a repointed constant the two floats involved. The game folder holds" + NL +
     "two program files, the one the shop delivers (DT22_en.exe, with its protector) and the same program without the" + NL +
     "protector (DT22_en_unwrapped.exe). Their code sits at the same addresses, and both are always written together:" + NL +
     "nothing is written into either unless every row of the set checks in both." + NL,
     "that must be there, the bytes to write, and for a repointed constant the two floats involved. A game folder may hold" + NL +
     "more than one program file (the one the shop delivers and a copy of the same program under another name). Their code" + NL +
     "sits at the same addresses, and all are always written together: nothing is written into any unless every row of" + NL +
     "the set checks in each." + NL + NL +
     "Which files: every .exe of the game folder that is the program, known by what it holds at the addresses of the" + NL +
     "sheet (each row its old bytes or its new ones); or the files config.json names (tools/mod_config.py)." + NL),
    ("from exe_reader import Exe, EXE_PATH, VANILLA_PATH" + NL, "import mod_config" + NL + "from exe_reader import Exe" + NL),
    ("GAME_EXE = os.path.join(os.path.dirname(EXE_PATH), 'DT22_en.exe')" + NL +
     "VANILLA_COPY = os.path.join(BASE_DIR, 'backups', 'exe', 'DT22_en.vanilla.exe')" + NL +
     "# (what the file is, the file of the game, its vanilla copy)" + NL +
     "TARGETS = (('game file', GAME_EXE, VANILLA_COPY), ('unwrapped file', EXE_PATH, VANILLA_PATH))" + NL +
     "SAVE_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'AQUAPLUS', 'DUNGEON TRAVELERS 2-2_EN')" + NL,
     "COPY_DIR = os.path.join(BASE_DIR, 'backups', 'exe')" + NL + "SAVE_DIR = mod_config.save_dir()" + NL),
    ("def problems(exe, rows, expect='old'):" + NL,
     '''def is_program(path, every_row=None):
    """Whether a file is the program this sheet was written for: a 32-bit executable in which every row holds its
    old bytes or its new ones."""
    every_row = patches() if every_row is None else every_row
    try:
        exe = Exe(path)
        return bool(every_row) and all(exe.read(p['va'], len(p['old'])) in (p['old'], p['new']) for p in every_row)
    except (OSError, ValueError, StopIteration, struct.error, TypeError):
        return False


def program_files(every_row=None):
    """The program files of the game: the ones config.json names, else every .exe of the game folder that is the
    program (is_program). A file the configuration names and that is not the program stops the tool."""
    listed = mod_config.listed_program_files()
    if listed:
        wrong = [p for p in listed if not is_program(p, every_row)]
        if wrong:
            raise SystemExit('config.json names a file that is not the program this mod was made for: ' + ', '.join(wrong))
        return listed
    folder = mod_config.game_dir()
    names = sorted(n for n in os.listdir(folder) if n.lower().endswith('.exe')) if os.path.isdir(folder) else []
    return [os.path.join(folder, n) for n in names if is_program(os.path.join(folder, n), every_row)]


def find_targets(every_row=None):
    """[(the name of the file, the file of the game, its vanilla copy backups/exe/<name>.vanilla.exe)]."""
    found = [(os.path.basename(p), p, os.path.join(COPY_DIR, os.path.splitext(os.path.basename(p))[0] + '.vanilla.exe'))
             for p in program_files(every_row)]
    if not found:
        raise SystemExit(f'No program file of the game found in {mod_config.game_dir()}: name the folder of the game, or the '
                         f'files, in {mod_config.CONFIG_PATH} (see config.example.json).')
    return found


def problems(exe, rows, expect='old'):
'''),
    ("def install(patch_set, targets=TARGETS, rows=None, every_row=None):" + NL +
     '    """Writes the set into every target, or into none. Returns [(label, path, bytes changed)]."""' + NL +
     "    rows = patches(patch_set) if rows is None else rows" + NL +
     "    every_row = patches() if every_row is None else every_row" + NL,
     "def install(patch_set, targets=None, rows=None, every_row=None):" + NL +
     '    """Writes the set into every target, or into none. Returns [(label, path, bytes changed)]."""' + NL +
     "    rows = patches(patch_set) if rows is None else rows" + NL +
     "    every_row = patches() if every_row is None else every_row" + NL +
     "    targets = find_targets(every_row) if targets is None else targets" + NL),
    ("def restore(targets=TARGETS):" + NL +
     '    """Puts the vanilla copy of every target back. Returns the labels of the files it put back."""' + NL +
     "    done = []" + NL,
     "def restore(targets=None):" + NL +
     '    """Puts the vanilla copy of every target back. Returns the labels of the files it put back."""' + NL +
     "    targets = find_targets() if targets is None else targets" + NL +
     "    done = []" + NL),
    ("def installed_set(targets=TARGETS, every_row=None):" + NL +
     '''    """What every target carries: {label: {row id: 'patched' | 'vanilla' | the bytes found}}."""''' + NL +
     "    every_row = patches() if every_row is None else every_row" + NL,
     "def installed_set(targets=None, every_row=None):" + NL +
     '''    """What every target carries: {label: {row id: 'patched' | 'vanilla' | the bytes found}}."""''' + NL +
     "    every_row = patches() if every_row is None else every_row" + NL +
     "    targets = find_targets(every_row) if targets is None else targets" + NL),
    ('''        states = ', '.join(f'{label} {carried[label][p["id"]]}' for label, _, _ in TARGETS)''' + NL,
     '''        states = ', '.join(f'{label} {state[p["id"]]}' for label, state in carried.items())''' + NL),
    ("        for label, game_file, copy in TARGETS:" + NL +
     "            found += [f'{label}: {m}' for m in problems(Exe(copy if os.path.exists(copy) else game_file), rows)]" + NL +
     "        print(LINE_END.join(found) if found else f'{len(rows)} rows of {sys.argv[2]} check in both program files')" + NL,
     "        every = find_targets()" + NL +
     "        for label, game_file, copy in every:" + NL +
     "            found += [f'{label}: {m}' for m in problems(Exe(copy if os.path.exists(copy) else game_file), rows)]" + NL +
     "        print(LINE_END.join(found) if found else f'{len(rows)} rows of {sys.argv[2]} check in {len(every)} program '" + NL +
     "              f\"file(s): {', '.join(label for label, _, _ in every)}\")" + NL),
])

sub('tools/install_variant.py', [
    ("GAME_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG')" + NL,
     "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))" + NL +
     "import mod_config                       # noqa: E402  (the folder of the game: config.json, else the one beside mod_project)" + NL +
     "GAME_DIR = mod_config.data_dir()" + NL),
    ("in the {label} ({changed} bytes differ from vanilla)", "in {label} ({changed} bytes differ from vanilla)"),
])
for tool in ('tools/floor_data.py', 'tools/map_data.py'):
    sub(tool, [("GAME_DUNGEON_DIR = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Dungeon')" + NL,
                "import mod_config                       # noqa: E402" + NL +
                "GAME_DUNGEON_DIR = os.path.join(mod_config.data_dir(), 'Dungeon')" + NL)])
sub('tools/package_variant.py', [
    ("    for _, game_file, vanilla_copy in exe_patch.TARGETS:" + NL, "    for _, game_file, vanilla_copy in exe_patch.find_targets():" + NL),
])
print('applied')

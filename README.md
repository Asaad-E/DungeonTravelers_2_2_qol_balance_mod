# Dungeon Travelers 2-2 (PC, English): QoL and Balance mod

A mod for *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, English version). It is built on
your own machine, from your own copy of the game: **no file of the game is in this repository.**

Two variants, installed one at a time:

| Variant | What it does |
|---|---|
| **QoL** | Shows what the game really does: chances, powers, turns and costs in the box of every skill, item, enchantment and enemy attack. It changes no value. |
| **Balance** | Changes values so that every class, weapon and skill is worth using, and shows the figures of the changed game in the same way. It also changes 19 bytes of the program (the EXP by level gap, the Crown, the chance of Arcane Shield, the passive Concentrate). |

What the Balance variant changes is told in [mod_project/release/README_Balance.txt](mod_project/release/README_Balance.txt).

---

## Install, step by step

### 1. What you need

- **Windows** and the game installed, in its English PC version, **with no other mod installed**. The mod checks
  every file of the game against a list of hashes and refuses a file that is not the original.
- **Python 3.10 or newer** ([python.org](https://www.python.org/downloads/)). During its installation tick
  *"Add python.exe to PATH"*.
- Two Python packages. Open a terminal (press `Win`, type `cmd`, press Enter) and run:

```bash
pip install openpyxl capstone
```

### 2. Get this repository

Either press **Code > Download ZIP** on GitHub and unpack it, or:

```bash
git clone <the address of this repository>
```

You now have a folder that holds `README.md` (this file) and `mod_project/`. Every command below is run **from that
folder**. To get a terminal there: open the folder in the file explorer, click its address bar, type `cmd`, press
Enter.

### 3. Tell the mod where the game is

The folder of the game is the one that holds its `.exe` and its `Data` folder. Choose one of the two:

- **No file to write:** put the folder of the game beside `mod_project/`, named `DungeonTravelers2-2_EN`.
- **Or name the folder:** copy `mod_project/config.example.json` to `mod_project/config.json` and write the path of
  the game in it, with forward slashes:

```json
{
  "game_dir": "D:/Games/DungeonTravelers2-2_EN"
}
```

Check what the mod will use:

```bash
python mod_project/tools/mod_config.py
```

It prints the folder of the game. If the folder is wrong, correct `config.json` before you go on.

The other keys of `config.json` are optional. `program_files` is the list of the `.exe` files to patch, when you do
not want the mod to look for them (see step 5). `save_dir` is the folder of your save files, used only by the
command that copies them.

### 4. Close the game

A running game cannot be patched. Nothing below touches your save files.

### 5. Apply the mod

One command does everything. For the Balance variant:

```bash
python mod_project/tools/apply_mod.py balance
```

For the QoL variant:

```bash
python mod_project/tools/apply_mod.py qol
```

It takes one or two minutes and runs three steps, stopping at the first that fails:

1. **The originals.** The files of your game the mod works from are copied into `mod_project/backups/` and each is
   checked against its hash. A line `52 of 52 original files` means all are there.
2. **The build.** The variant is built from those originals into `mod_project/build/<variant>/` and verified: every
   figure a text states is compared with the value the built file holds. It ends with `[OK] Variant '<variant>' built`.
3. **The install.** The built files are put into `Data/ENG/` of the game. What they replace is saved first, in
   `mod_project/build/installed_backup/<date>/`. For the Balance variant the program is then patched: **every `.exe`
   of the folder of the game that is the program is found by itself** (by what it holds at the addresses the mod
   changes, whatever its name), a copy of each is kept in `mod_project/backups/exe/`, and the same bytes are written
   into each. For the QoL variant the program is left as the game has it.

The last lines look like this:

```text
[4] Installed variant 'balance' into D:\Games\DungeonTravelers2-2_EN\Data\ENG
    20 file(s) replaced by the balance build file: ...
    Program: 14 rows of the set 'balance' in DT22_en.exe (19 bytes differ from vanilla)
```

A line that starts with `PROBLEM` or `[FAIL]` says what stopped it; nothing is half written into the program.

### 6. Check it

```bash
python mod_project/tools/exe_patch.py status
```

Every row says `patched` for each program file (Balance) or `vanilla` (QoL). Then start the game: the box of any
skill shows its figures by level.

### 7. Change variant, or take the mod out

Run step 5 again with the other name to change variant. To put the game back as it was:

```bash
python mod_project/tools/apply_mod.py vanilla
```

Every original file goes back into the game and the program files are put back from their copies.

Save files are not touched and stay compatible both ways.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| `... is not the original file (another version, or a mod is installed): not copied` | Put the original files of the game back (verify the files in your launcher, or reinstall), then run step 5 again. |
| `No program file of the game found in ...` | The folder of the game is wrong: see step 3. If your `.exe` is elsewhere, list it under `program_files` in `config.json`. |
| `Nothing written into ...: the file is in use` | Close the game and run step 5 again. |
| `python` is not recognised | Install Python again with *"Add python.exe to PATH"* ticked, and open a new terminal. |
| `No module named openpyxl` (or `capstone`) | Run the `pip install` line of step 1. |

---

## For those who want to change the mod

Everything that is a value, a rule or a wording lives in a workbook of `mod_project/data_tables/`, never in code:
`balance_changes.xlsx` holds every changed value, one per row, with its reason. Start with
[mod_project/README.md](mod_project/README.md), then `mod_project/docs/BALANCE_PLAN.md` and
`mod_project/docs/FORMULAS.md` (the formulas of the game, as read from its program).

```bash
python -m unittest discover -s mod_project/tests -p "test_*.py"
```

runs the tests (they need step 5 done once, for the originals).

Credits and sources: [mod_project/docs/CREDITS.md](mod_project/docs/CREDITS.md).

# Dungeon Travelers 2-2 — QoL & Balance Mod

A mod for *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, English).

It comes in two variants. Install one or the other.

- **QoL** shows what the game actually does. Skills, items, enchantments and enemy attacks list their real numbers:
  chances, power, turns, costs. No value is changed.
- **Balance** makes every class, weapon and skill worth using, and shows the new numbers the same way. It also
  patches a few bytes of the game's `.exe`. The full list of changes is in
  [release/README_Balance.txt](release/README_Balance.txt).

This repository contains no game files. The mod is applied to your own copy of the game.

## Install

You need Windows and an unmodified copy of the game.

1. Download the zip of the variant you want from [Releases](../../releases).
2. Close the game.
3. Unzip it into the game folder, next to the `.exe` and the `Data` folder.
4. Run `Install_Balance.bat` or `Install_QoL.bat`.

The installer checks every file before touching it and keeps a backup of the originals in `DT22_Mod\backup`. If a
file is not the original one, it tells you which and changes nothing.

To uninstall, run `Uninstall_DT22_Mod.bat`. To switch variants, unzip the other one into the same folder and run its
installer.

Saves are not touched and work with or without the mod.

## Build from source

Only needed if you want to change the mod or see how it is made. Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

Put the game folder inside this one, named `DungeonTravelers2-2_EN`, or copy `config.example.json` to `config.json`
and set the path:

```json
{ "game_dir": "D:/Games/DungeonTravelers2-2_EN" }
```

Then build and install a variant:

```bash
python tools/apply_mod.py balance
```

Use `qol` for the other variant, or `vanilla` to restore the game. The first run copies the original files it needs
from your game into `backups/` and verifies them.

Other commands:

| Command | What it does |
|---|---|
| `python tools/release.py` | Builds both variants and writes the two zips to `dist/` |
| `python -m unittest discover -s tests -p "test_*.py"` | Runs the tests |
| `python tools/exe_patch.py status` | Shows which patches each `.exe` carries |

## Troubleshooting

| Message | Fix |
|---|---|
| `not the original file` | Another mod or game version is installed. Restore the game files and try again. |
| `No program file of the game found` | Wrong game folder. Check `config.json`. |
| `the file is in use` | Close the game. |

## How it works

Every changed value, rule and line of text lives in a spreadsheet under `data_tables/`, not in code.
`balance_changes.xlsx` has one row per change, with the reason for it. The build reads those sheets, writes the game
files, and refuses to finish if any number shown in a text does not match the data behind it.

The battle formulas were read from the game's executable and are documented in [docs/FORMULAS.md](docs/FORMULAS.md).
Balance changes were tested with a battle simulator (`sim/`) built on those formulas.

More in [docs/](docs/README.md).

## Credits

Game by Aquaplus and Sting. Figures were cross-checked against the Japanese community wiki and the GameFAQs guides.
See [docs/CREDITS.md](docs/CREDITS.md).

# Dungeon Travelers 2-2: QoL & Balance Mod

A mod for *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, English).

The game shows very little of how it works. Skills say "damage UP", items heal "a little", and nothing explains the
rules behind a fight. This mod puts the real numbers on screen and, in its second version, rebalances the classes
and skills those numbers show to be weak.

The battle formulas were read from the game's executable, and the balance changes were tested with a simulator
built on them.

There are two versions.

## QoL

Changes nothing about how the game plays. It only makes the game show its numbers.

Skill descriptions list their real values for every level: power, chance to land, duration, TP cost, speed. Items
and enchantments say what they do. Enemy, summon and mercenary abilities show their chances and power as well.
Where the original text had a number wrong, it is fixed. Jokes and flavour text are left alone.

Every number on screen is checked against the game's data when the mod is built, so none of it is guesswork.

## Balance

Everything QoL does, plus a rebalance of the whole game: well over a thousand changes to skills, enemies, items and
gear.

The starting point was a long list of complaints from the Japanese wiki and the English GameFAQs guide. Each one was
checked against the data and the simulator. Many were real and got fixed. Many others were not and those were left as they are.

What you will notice when playing:

- Classes that used to fall behind, like Doll Master, Kunoichi or Mistress, can carry their weight.
- Skills nobody picked, weak weapon types and status ailments are worth using.
- A character who joins late or sat on the bench catches up in a few battles.
- A few outright bugs are fixed. The passive Concentrate, for example, does nothing in the original game.
- Bosses still hit hard. The party gets more options, not more power.

The full list of changes is in [installer/README_Balance.txt](installer/README_Balance.txt).

Neither version includes game files. The mod is applied to your own copy of the game.

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
| `python tools/package_all.py` | Builds both variants and writes the two zips to `dist/` |
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
Balance changes were tested with a battle engine built on those formulas (`engine_cs/`, in C#; the Python simulator
it was proven against was removed once the two gave the same figures).

More in [docs/](docs/README.md). To change the mod, read [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE). It covers this repository, not the game.

## Credits

Game by Aquaplus and Sting. Figures were cross-checked against the Japanese community wiki and the GameFAQs guides.
See [docs/CREDITS.md](docs/CREDITS.md).

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

## The state of the mod in charts

The full test suite (`python tools/full_suite.py`) draws these charts from its reports in `docs/generated/` every time
it runs, so they always show the current Balance variant. "Vanilla" is the original game; a "cell" is one party at one
boss or row of random battles, played many times with the same random seeds on both sides.

### Difficulty along the story

![Difficulty curve](docs/generated/charts/difficulty_curve.png)

The reference party at every story checkpoint, at the level a player is expected to have there: grey is vanilla,
blue is Balance. The top three panels are the share of fights won, how many turns they last and the lowest HP the party
falls to. A shaded checkpoint is outside the window of vanilla (green easier, red harder); the goal is to keep the
back and forth of each fight, so most checkpoints should stay unshaded. The bottom panel is the level of the boss
against the level of the party.

### Random battles along the story

![Random battles](docs/generated/charts/random_battles.png)

The same party and levels at the floor of every checkpoint, walking a row of random battles in a row with one bag of
items that is not refilled until the row ends; HP and TP carry from one battle to the next. Grey is vanilla, blue is
Balance: the share of rows the party survives, the length of a battle, the lowest HP of the row and the TP left at its
end (how much the walk drains the party). Shading as in the difficulty curve.

### The parties of the battery

![Party battery](docs/generated/charts/party_battery.png)

Five party archetypes, from optimised to unusual, against the main bosses. Left: the share of fights each one wins on
Balance; a framed cell is below the least the boss should allow. Right: the change from vanilla in points (blue better,
red worse). A wide range of parties should clear every boss.

### The final classes

![Class balance](docs/generated/charts/class_balance.png)

Every party of the final classes against every story boss of that stage. Each point is a class: hollow is vanilla,
filled is Balance, the arrow the change. The grey band is the mean of the classes plus or minus two standard
deviations: classes may differ, but none should fall outside it. A red name is outside the band. The last two panels
show how often a party with one, or several, of the class is among the fastest 5% of all parties.

### Every class at its stage

![Class stages](docs/generated/charts/class_stages.png)

Each role of the model at the bosses of its stage (base, intermediate, advanced, postgame), in several parties.
Left, the attackers: how long their fights last against the median attacker (1.0); above the red line is slow.
Right, the supports and tanks: their share of wins against the median where some fights are lost (below the red line
is weak), or the length of the fights where every fight is won. Large points are the mean, small points each boss; a
red X and a red name are out of the band.

### Skills

![Skills](docs/generated/charts/skills.png)

Left: every class skill, used against not used, in every party and stage where it can be played. Across: the share of
cells where it helps; up: the share where it makes the fight worse. Green is good, orange a niche (useful in some
fights), grey dead, red harmful. A skill meant for a situation is judged by its best rule of use. Right: the unique
skill of each girl, the same way (right of the line it helps, left it hurts).

### Mercenaries

![Mercenaries](docs/generated/charts/mercenaries.png)

Each mercenary hired beside the summon of the party's grand sealbook (the game fields both), in every party, at the
stage the tavern offers at that point of the story. Left: the share of cells where the party does better with her
(right of the line, coloured by verdict) and worse (left). Right: the mean change of wins over every cell.

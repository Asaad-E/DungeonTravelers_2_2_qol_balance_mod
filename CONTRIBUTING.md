# Contributing

This file is for anyone, person or coding agent, who wants to change the mod. It says where the project stands, how
it is put together, and what a change has to respect.

## Where the project stands

- **QoL** is finished. It only changes when a text is shown to be wrong.
- **Balance** is built and playable. It is being play-tested; fixes and adjustments are welcome.

Known limits, left as they are for now:

- Assassin and Treasure Hunter still come out slower than the other classes in the class measure.
- A handful of postgame fights are not won by any party in the simulator, with or without the mod.
- The simulator does not build the dolls that enemies summon.
- What the enemy passive Murder License does when it kills has not been found in the program.
- A few rows of the register are closed on an argument, with no figure behind them (meals, forging costs, the early
  economy, harmful map zones). They are listed in `docs/generated/VERDICTS.md`.

## Setup

You need Windows, Python 3.10+, and your own unmodified copy of the game.

```bash
pip install -r requirements.txt
```

Put the game folder inside the repository as `DungeonTravelers2-2_EN`, or copy `config.example.json` to
`config.json` and set `game_dir`. Then:

```bash
python tools/setup_backups.py
```

This copies the original game files the tools need into `backups/` and checks each one against a list of hashes.
Nothing works without it, including the tests.

## Layout

| Folder | What it holds |
|---|---|
| `data_tables/` | Every value, rule and line of text of the mod, as spreadsheets. Also what is particular to this game: `game_profile.json` (folder and file names) and `record_layouts.json` (where each field sits in each record) |
| `tools/` | Builders, readers of the game files and of the executable, measures |
| `sim/` | The battle simulator |
| `tests/` | The test suite |
| `installer/` | What goes into the player zips: the installer script and the player READMEs |
| `measures/` | Measures and readings that a spreadsheet row or a document cites |
| `scratch/` | One-off scripts and partial results, kept for reference. Not maintained |
| `docs/` | Documentation. Start with `docs/README.md` |

`backups/`, `build/`, `dist/` and `config.json` are local and not in git.

## Rules

These are checked by the build or the tests wherever possible.

1. **Nothing is hard-coded.** A value, a rule or a wording goes in a spreadsheet of `data_tables/`, never in a
   `.py` file. A balance change is one row of `balance_changes.xlsx`, with the original value, the new one and the
   reason.
2. **The game comes first.** Figures are read from the game files or the executable. A player guide is used only
   for what the game does not store, and the source is recorded next to the figure.
3. **On-screen text never speaks from outside the game.** No sources, caveats or notes to the reader in anything the
   player sees. Use the game's own terms.
4. **Text must match the data.** The build compares every number in a text with the built file and fails if they
   differ. A box has at most 3 lines of 85 characters.
5. **Nothing about the game's files is hard-coded either.** A folder name or the offset of a field goes in
   `game_profile.json` or `record_layouts.json`, read through `tools/game_profile.py`.
6. **Prefer plain value changes.** Changing a number inside an existing record is safe. Changing the executable is
   the last resort: each patch is a row of the sheet `ExePatches`, same length as the bytes it replaces.
7. **No game files in git.** Not the originals, not the built files, not the zips.
8. **Neutral wording.** Documents, comments and commit messages say what was decided and why, not who decided it.
9. **English everywhere** in the repository.

For the reasoning behind these, see `docs/philosophy.md`.

## Making a change

**A balance value.** Add or edit a row in `data_tables/balance_changes.xlsx` (sheet `Changes`). The column `Lever`
names the kind of change, listed in the sheet `Levers` of `balance_criteria.xlsx`. If the kind is new, the writer for
it goes in `tools/balance_values.py`, and the simulator must read it too (`sim/variant.py`).

**A text.** The QoL text lives in the `qol_*_text.xlsx` workbooks, labels and wordings in `qol_rules.xlsx`. Where the
Balance variant needs a different wording, it goes in `balance_skill_text.xlsx`.

**A formula or a rule of the simulator.** Read it in the executable first (`tools/exe_dis.py` and the other `exe_*`
tools), write it in `docs/FORMULAS.md` with its address, then change `sim/`.

After any change:

```bash
python tools/build_variant.py balance
```

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Both must pass. To try it in your game:

```bash
python tools/apply_mod.py balance
```

A change that affects difficulty should be measured before it is proposed:

| Command | What it measures |
|---|---|
| `python tools/difficulty_curve.py all` then `report` | Every boss, mod against original |
| `python tools/party_battery.py all 12` then `report` | Several party types against 17 bosses |
| `python tools/class_stages.py all` then `report` | Each class at each stage of the game |

The curve runs 40 battles per boss. Bosses that sit on the edge of a window can move in or out by chance; before
blaming a change, run those bosses again with more battles (`measures/curve_ablation.py`).

## Commits and pull requests

- Commit messages: `prefix: content`, 72 characters at most. Details go in the body, without repeating the prefix.
  Prefixes in use: `balance`, `qol`, `sim`, `tools`, `data`, `docs`, `test`, `fix`, `feat`, `scratch`.
- One change per pull request. Say what it changes, why, and what was measured.
- Include the regenerated files under `docs/generated/` when a measure was run.
- Do not commit anything from `backups/`, `build/` or `dist/`.

## Releases

```bash
python tools/package_all.py
```

builds both variants and writes the two player zips to `dist/`. They contain only differences and the installer,
never game files. Attach them to a GitHub release.

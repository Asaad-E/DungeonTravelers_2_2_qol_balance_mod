# Dungeon Travelers 2-2: Information & Balance Mod Project

Mod project for *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC). It ships as two variants built separately:

- **QoL**: shows more information about the base game and changes no value.
- **Balance**: rebalances the game and shows the information of the rebalanced game. Not defined yet.

Start with `docs/philosophy.md` (why) and `docs/dungeontravelers2-2.md` (what was done, formats, style guide, what is left).

---

## Layout

```text
DungeonTraveler2-2/
├── mod_project/
│   ├── backups/                 original .pck files; every build reads from here
│   ├── data_tables/
│   │   ├── vanilla_source_of_truth.xlsx   original values, generated, never edited
│   │   ├── qol_skill_text.xlsx            QoL skill text, edited by hand
│   │   ├── qol_enchant_text.xlsx          QoL enchant names, edited by hand
│   │   ├── qol_item_text.xlsx             QoL item descriptions, edited by hand
│   │   └── *.xlsx                         tables of the earlier mixed build
│   ├── build/<variant>/         build output, not versioned
│   ├── tools/
│   │   ├── pck_handler.py                 archive and record reader/writer
│   │   ├── extract_vanilla.py             backups -> vanilla_source_of_truth.xlsx
│   │   ├── generate_qol_skill_text.py     proposes the QoL skill text
│   │   ├── text_checks.py                 figures in text vs values in the binary
│   │   ├── enchant_values.py              enchant figures and the guide each comes from
│   │   ├── generate_qol_enchant_text.py   proposes the QoL enchant names
│   │   ├── generate_qol_item_text.py      proposes the QoL item descriptions
│   │   ├── weapon_rank_labels.py          rank names generated from their delay multiplier
│   │   ├── install_variant.py             puts a built variant into the game, saving what it replaces
│   │   ├── build_variant.py               builds and verifies a variant
│   │   └── apply_mod.py, audit_tool.py, package_release.py   earlier mixed build
│   ├── tests/                   unittest suite
│   └── docs/
├── Data/                        GameFAQs pages (.mhtml), cross-check only
├── docs_example/                method and reference project
└── DungeonTravelers2-2_EN/      game install
```

---

## Build the QoL variant

```bash
python mod_project/tools/extract_vanilla.py
```

```bash
python mod_project/tools/generate_qol_skill_text.py
```

```bash
python mod_project/tools/generate_qol_enchant_text.py
```

```bash
python mod_project/tools/generate_qol_item_text.py
```

```bash
python mod_project/tools/build_variant.py qol
```

```bash
python -m unittest discover -s mod_project/tests -p "test_*.py"
```

The build writes to `mod_project/build/qol/`, verifies it, and only then installs it into the game folder so it can be checked on screen (`--no-install` to skip). After an install the game holds the variant and nothing else; every file it replaces is saved in `mod_project/build/installed_backup/<time>/`. The build stops, and installs nothing, if a figure in a skill or item text is not the value in the binary, if an enchant name shows a figure without a known source, if a weapon rank label differs from its multiplier, if a box breaks the limits, or if any game value differs from the original.

## Edit the skill text

1. Open `mod_project/data_tables/qol_skill_text.xlsx`.
2. Change `QoL_Desc` or `QoL_LvUp` and write `yes` in `Edited` so the row is not regenerated.
3. Run the build. Limits: 3 lines per box (description included), 85 characters per line, no tilde.

---

## Commits

One line, `type: description` (`feat`, `fix`, `docs`, `test`, `build`, `refactor`, `chore`).

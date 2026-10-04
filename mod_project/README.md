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
│   │   └── *.xlsx                         tables of the earlier mixed build
│   ├── build/<variant>/         build output, not versioned
│   ├── tools/
│   │   ├── pck_handler.py                 archive and record reader/writer
│   │   ├── extract_vanilla.py             backups -> vanilla_source_of_truth.xlsx
│   │   ├── generate_qol_skill_text.py     proposes the QoL skill text
│   │   ├── text_checks.py                 figures in text vs values in the binary
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
python mod_project/tools/build_variant.py qol
```

```bash
python -m unittest discover -s mod_project/tests -p "test_*.py"
```

The build writes to `mod_project/build/qol/` and never into the game folder. It stops if a figure in the text is not the value in the binary, if a box breaks the limits, or if any game value differs from the original.

## Edit the skill text

1. Open `mod_project/data_tables/qol_skill_text.xlsx`.
2. Change `QoL_Desc` or `QoL_LvUp` and write `yes` in `Edited` so the row is not regenerated.
3. Run the build. Limits: 3 lines per box (description included), 85 characters per line, no tilde.

---

## Commits

One line, `type: description` (`feat`, `fix`, `docs`, `test`, `build`, `refactor`, `chore`).

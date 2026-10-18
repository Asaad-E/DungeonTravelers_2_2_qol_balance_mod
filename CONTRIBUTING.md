# Contributing Guide

This guide covers the development workflow, project architecture, and verification standards for contributing to the *Dungeon Travelers 2-2* mod project.

---

## 1. Project Status

* **QoL Variant**: Feature-complete. Only updated to correct errata or refine clarity if a tooltip is found to be inaccurate.
* **Balance Variant**: Implemented, verified, and playtested. Adjustments address issues cataloged in `data_tables/balance_criteria.xlsx` (sheet `Criticisms`). Further balance adjustments and fixes are welcome.

### Known Design Boundaries & Outliers
* In `docs/generated/CLASS_STAGES.md`, 67 of 76 class roles sit cleanly within target variance bands. Early Scout, Assassin, and Treasure Hunter are intentionally paced around exploration utility, while Diva (win rate) and Witch (clearing speed) remain distinct specialist outliers by design.
* The Maid archetype remains the party's primary TP sustain engine, preserving the game's core resource-management loop.
* Extreme deep-postgame encounters are kept outside the scope of main story rebalancing.

---

## 2. Environment Setup

Requirements: Windows, Python 3.10+, and .NET 10 SDK (for the C# simulation engine).

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place an unmodified copy of the English PC game directory at the repository root named `DungeonTravelers2-2_EN`, or configure `config.json` with your game path:
   ```json
   { "game_dir": "D:/Games/DungeonTravelers2-2_EN" }
   ```
3. Initialize reference backups:
   ```bash
   python tools/setup_backups.py
   ```
   This extracts untouched game archives into `backups/` and verifies hashes. The build pipeline and test suite require these backups to function.

---

## 3. Repository Layout

| Directory | Purpose |
|---|---|
| `data_tables/` | Spreadsheets defining all balance parameters, rule tables, and text strings. |
| `tools/` | Builders, binary patchers, text generators, and verification scripts. |
| `engine_cs/` | C# combat engine and benchmark battery (`src/DtEngine/Suite`). |
| `gamedata/` | Readers for binary formats, struct offsets, and data snapshots. |
| `tests/` | Unittest suite for binary round-trips and text boundary assertions. |
| `installer/` | Release scripts, batch installers, and user-facing changelogs. |
| `measures/` | Measure scripts and research data supporting balance changes. |
| `docs/` | Architecture guides, formulas, and generated reports. |

*Note: `backups/`, `build/`, `dist/`, and `config.json` are local-only and excluded from version control.*

---

## 4. Engineering Standards

1. **Decoupled Data**: Never hardcode gameplay numbers in script code. All parameters and text modifications belong in spreadsheets under `data_tables/`.
2. **Binary Ground Truth**: Figures are extracted directly from game binaries or decompiled x86 code. External guides are cited only when parameters are not stored in game files.
3. **In-Universe Tone**: In-game tooltips must never use out-of-universe commentary, meta notes, or modder slang. Keep the game's official terminology intact.
4. **Strict Display Boundaries**:
   * Tooltip lines must never exceed 85 characters ($\le 70$ for the battle bar).
   * Tooltips are limited to 3 lines maximum.
   * Never use tildes (`~`); use hyphens or arrows.
5. **Exact Binary Rebuilding**: Binary serializers must produce byte-identical round-trips against unmodified archives.
6. **No Game Assets in Git**: Do not commit original game files, extracted assets, or compiled binaries.

---

## 5. Making Changes

### Modifying Balance Values
1. Add or update rows in `data_tables/balance_changes.xlsx` (sheet `Changes`), specifying target record, field, baseline value, new value, and design rationale.
2. If introducing a new change lever, implement the corresponding writer in `tools/balance_values.py` and map it in `gamedata/variant.py`.

### Updating In-Game Text
* General QoL text lives in `data_tables/qol_*_text.xlsx`.
* Formatting rules and labels are defined in `data_tables/qol_rules.xlsx`.
* Balance-specific text overrides belong in `data_tables/balance_skill_text.xlsx`.

### Updating Simulation Formulas
1. Confirm assembly instructions in the executable (`tools/exe_dis.py` or x86 disassembler).
2. Document the logic and virtual address in `docs/FORMULAS.md`.
3. Update the matching routine in `engine_cs/src/DtEngine`.

---

## 6. Testing & Validation

After any modification, ensure both the build pipeline and test suite pass cleanly:

```bash
# Verify balance build integrity
python tools/build_variant.py balance

# Run automated tests
python -m unittest discover -s tests -p "test_*.py"

# Apply changes to your local test game
python tools/apply_mod.py balance
```

For changes affecting combat balance or difficulty curves, execute the benchmark suite:

```bash
# Run full benchmark battery (updates docs/generated/ and charts)
python tools/full_suite.py

# Run targeted measures
dtcli difficulty-curve
dtcli party-battery
dtcli class-stages
```

---

## 7. Commits & Pull Requests

* Commit messages should be concise and descriptive: `<prefix>: <description>` (max 72 characters).
  Standard prefixes: `balance`, `qol`, `sim`, `tools`, `data`, `docs`, `test`, `fix`, `feat`.
* Ensure automated tests pass before opening a pull request.
* If a change moves simulation outcomes, include updated reports from `docs/generated/` and charts.

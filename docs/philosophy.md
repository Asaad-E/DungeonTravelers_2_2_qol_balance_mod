# Design Principles & Architecture

This document summarizes the core design principles, data standards, and engineering practices behind the *Dungeon Travelers 2-2* mod suite.

---

## 1. Project Scope & Variants

The project produces two distinct variants built from shared tooling:

* **QoL Variant (Informational Only)**: Surfaces hidden combat numbers (percentages, turn counts, multipliers, speed penalties) across skills, items, enchants, and summons. Original gameplay values, formulas, and balance remain completely untouched.
* **Balance Variant (Rebalanced Gameplay)**: Builds upon QoL transparency by rebalancing lagging classes, skills, and equipment. Changes address documented issues from community guides and forums, aiming to make every class and build archetype viable.

Each variant is built independently: QoL tooltips reflect original parameters, while Balance tooltips reflect rebalanced numbers.

---

## 2. Source Data & Integrity

1. **Binary as Ground Truth**: All values and formulas are extracted directly from the compiled game files (`.pck`, `.bin`) and decompiled x86 executable logic. Community walkthroughs are referenced for context and mechanics that the engine does not store in data tables.
2. **Spreadsheet-Driven Architecture**: All changed parameters, text modifications, and rule sets live in versioned spreadsheets within `data_tables/`. Tooling scripts contain no hardcoded balance figures.
3. **In-Universe Nomenclature**: All text additions use the official terms established by the game (e.g., `Enmity`, `Physical accuracy`, elemental attributes) rather than external modding slang.
4. **Preserving Game Character**: Modifications add numerical clarity without rewriting or removing character dialogue, humor, or flavor text.

---

## 3. UI Constraints & Build Verification

1. **Screen Readability**: Tooltips must be readable at a glance during combat. Text formatting uses clean progression steps (`->`) rather than dense algebraic formulas.
2. **Hard Layout Boundaries**:
   * Maximum 3 lines per tooltip.
   * Maximum 85 characters per line for dialog windows.
   * Maximum 70 characters for combat action bars.
   * No tildes (`~`), which are unsupported by the English PC font and result in glyph corruption.
3. **Automated Assertion**: The build pipeline (`tools/build_variant.py`) and test suite automatically verify that every displayed number matches the compiled binary byte-for-byte. A build halts immediately if any figure fails verification or exceeds screen width limits.

---

## 4. Packaging & Safety

* **Zero Game Assets in Git**: The repository contains only tooling, tables, and documentation. Original assets are extracted locally from the user's licensed game copy.
* **Automatic Backups**: Mod installers verify file hashes before applying modifications and maintain untouched originals in `DT22_Mod\backup`. Uninstallation restores original files completely.

# Dungeon Travelers 2-2 Mod Philosophy

This document outlines the scope, principles, and architectural reasoning of the Dungeon Travelers 2-2 mod suite, mirroring the standards established in `docs_example/philosophy.md`.

---

## 1. The Two Pillars

| Pillar | Objective | Targets | Game Balance Risk |
|---|---|---|---|
| **Pillar A: Information (Transparency)** | The player can make optimal tactical decisions from what the screen says. | Text, tooltips, formulas, ranges, speeds, and manuals. | **Zero.** Reflects the exact underlying math executed by the engine. |
| **Pillar B: Balance & Quality of Life (QoL)** | Remove tedious dead ends, elevate underpowered classes, and preserve high-end tactical challenge. | Data tables (`ClassData`, `SkillData`, `WeaponRankData`, `ClassLevelData`). | **Controlled & Tunable.** Grounded in community consensus and raw binary parameters. |

**Each pillar is its own build.** The QoL variant carries Pillar A alone and changes no value; the Balance variant carries both. A text written for one must never ship over the data of the other.

**Core Tenet:** *Make hidden information visible, preserve the humor and soul of the game, and never silently change what the game is.*

---

## 2. Guiding Principles

1. **Hierarchy of Truth:** `Game Binary > Engine Text > Community FAQs/Wikis`.
   - The compiled `.bin` / `.pck` files are what the PC executable actually parses. Community guides often hold stale PS Vita launch assumptions. The binary data is always the primary fact base.
   - A figure shown to the player is read from the binary of the variant being built. If the binary does not hold it, the text does not state it.
   - What a field means is inferred until proven; say so. A guide that agrees is corroboration, not proof.
2. **Single Source of Truth:**
   - Original values live in `data_tables/vanilla_source_of_truth.xlsx`, generated from the backups. Hand-written text lives in the workbooks of `data_tables/`.
   - Binaries are generated from those by a build script into `build/<variant>/`. Never hand-edit a `.pck`, and never build straight into the game folder.
3. **Preserve Game Soul and Humor:**
   - DT2-2 has a distinct comedic personality: puns, 4th-wall breaks, pop culture parodies, and character banter.
   - Information must be additive: `Original Flavor Text + (Concise Data)`. Never overwrite lore with dry spreadsheets.
   - The screen already shows some data. Look at the real box before writing into it, and do not repeat what is there.
4. **Hard Limits Are Tests, Not Guidelines:**
   - Display limits ($\le 3$ lines, $\le 85$ characters per line, measured on screen) and the missing tilde glyph are asserted by `build_variant.py` and the suite in `tests/`. A text that does not fit, or a figure that is not in the binary, fails the build.
5. **Bit-Exact Patching & In-Place Preservation:**
   - A writer must reproduce the original entry byte for byte when the text is unchanged. That round trip is a test; a writer that fails it is not used.
   - A step that cannot do its job (a replacement that does not find its target) stops the build instead of continuing.
6. **Every Balance Change Must Be Grounded in Community Data:**
   - Rebalancing must not be done "because it feels better". It must address documented community pain points (e.g., severe weapon delay gaps, magic chant interruption walls in deep post-game, high-level skill TP traps).

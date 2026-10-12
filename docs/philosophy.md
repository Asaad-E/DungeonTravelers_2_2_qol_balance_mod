# Dungeon Travelers 2-2 Mod Philosophy

This document outlines the scope, principles, and architectural reasoning of the Dungeon Travelers 2-2 mod suite.

---

## 1. The Two Pillars

| Pillar | Objective | Targets | Game Balance Risk |
|---|---|---|---|
| **QoL** | Everything the player needs to make an informed decision is present in the game, in a clean, understandable, easy-to-read form. | Text only: descriptions, names, tooltips, manuals, dialogue. | **Zero.** It shows what the base game does and changes none of it. |
| **Balance** | Address the complaints of the Japanese players and the criticisms of the English guide, each one a row of the register (`data_tables/balance_criteria.xlsx`, sheet `Criticisms`) with the page it comes from. | Data tables, plus the text that describes them. | **Controlled.** Each change answers a documented complaint and is checked against the binary first. |

**Each pillar is its own build.** The QoL variant changes no value; the Balance variant rebalances and carries the same information for the rebalanced game. A text written for one must never ship over the data of the other.

**Order of work.** QoL first, until it is right (closed on 2026-10-04). Balance afterwards. Tools are built once and must serve both: the same extraction, the same checks and the same build, with the variant as a parameter.

**QoL is judged on the screen.** A true figure is necessary, not sufficient. A box that holds every number but is hard to read has failed. Start from the decision the player takes on each screen, what that screen already shows and what is missing; the data and the tools follow from that.

**Core Tenet:** *Make hidden information visible, preserve the humor and soul of the game, and never silently change what the game is.*

---

## 2. Guiding Principles

1. **Hierarchy of Truth:** `Game Binary > Engine Text > Community FAQs/Wikis`.
   - The compiled `.bin` / `.pck` files are what the PC executable actually parses. Community guides often hold stale PS Vita launch assumptions. The binary data is always the primary fact base.
   - A figure shown to the player is read from the binary of the variant being built. If the binary does not hold it, the text does not state it.
   - What a field means is inferred until proven; say so. A guide that agrees is corroboration, not proof.
   - Order of sources: binary first, then player guides of this same game (the Japanese community documented it best). A guide is used only for what the binary does not hold, every such figure names its guide, and it stays tagged as inferred. A figure from another game is a candidate, not a fact.
   - Words are part of the data: use the game's own term for every concept (Enmity, resistance, Physical accuracy). Never rename a concept, and never put a vague word next to its exact value.
2. **Single Source of Truth:**
   - Original values live in `data_tables/vanilla_source_of_truth.xlsx`, generated from the backups. Hand-written text lives in the workbooks of `data_tables/`.
   - Binaries are generated from those by a build script into `build/<variant>/`. Never hand-edit a `.pck`. The game folder is written only by the install step, after the build has passed its verification, and it then holds that variant and nothing else; whatever is replaced is saved first.
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
   - Rebalancing must not be done "because it feels better". It must address a row of the register of complaints (sheet `Criticisms`) (e.g., severe weapon delay gaps, magic chant interruption walls in deep post-game, high-level skill TP traps).
   - The register records what players perceive, not what the engine does. Check each complaint against the binary before acting on it: some are exaggerated or false (Berserk does not reduce DEF to zero; it lowers it by 11% to 25%).

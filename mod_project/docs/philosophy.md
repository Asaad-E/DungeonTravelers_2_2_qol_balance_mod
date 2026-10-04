# Dungeon Travelers 2-2 Mod Philosophy

This document outlines the scope, principles, and architectural reasoning of the Dungeon Travelers 2-2 mod suite, mirroring the standards established in `docs_example/philosophy.md`.

---

## 1. The Two Pillars

| Pillar | Objective | Targets | Game Balance Risk |
|---|---|---|---|
| **Pillar A: Information (Transparency)** | The player can make optimal tactical decisions from what the screen says. | Text, tooltips, formulas, ranges, speeds, and manuals. | **Zero.** Reflects the exact underlying math executed by the engine. |
| **Pillar B: Balance & Quality of Life (QoL)** | Remove tedious dead ends, elevate underpowered classes, and preserve high-end tactical challenge. | Data tables (`ClassData`, `SkillData`, `WeaponRankData`, `ClassLevelData`). | **Controlled & Tunable.** Grounded in community consensus and raw binary parameters. |

**Core Tenet:** *Make hidden information visible, preserve the humor and soul of the game, and never silently change what the game is.*

---

## 2. Guiding Principles

1. **Hierarchy of Truth:** `Game Binary > Engine Text > Community FAQs/Wikis`.
   - The compiled `.bin` / `.pck` files are what the PC executable actually parses. Community guides often hold stale PS Vita launch assumptions. The binary data is always the primary fact base.
2. **Single Source of Truth:**
   - All modded parameters live in `mod_project/data_tables/*.xlsx`.
   - Modded binaries are generated deterministically by `apply_mod.py`. Never hand-edit compiled `.pck` files directly.
3. **Preserve Game Soul and Humor:**
   - DT2-2 has a distinct comedic personality: puns, 4th-wall breaks, pop culture parodies, and character banter.
   - Information must be additive: `Original Flavor Text + (Concise Data)`. Never overwrite lore with dry spreadsheets.
4. **Hard Limits Are Tests, Not Guidelines:**
   - Display limits ($\le 3$ lines, $\le 85$ characters per line) and font encoding constraints (no tilde `~`) are strictly enforced by automated assertions in `audit_tool.py`.
5. **Bit-Exact Patching & In-Place Preservation:**
   - Container alignments (8-byte alignment) and byte budgets must be preserved bit-for-bit to prevent engine pointer corruption or crash on load.
6. **Every Balance Change Must Be Grounded in Community Data:**
   - Rebalancing must not be done "because it feels better". It must address documented community pain points (e.g., severe weapon delay gaps, magic chant interruption walls in deep post-game, high-level skill TP traps).

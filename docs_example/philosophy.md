# Mod philosophy

This document describes the scope and the reasoning of the 7th Dragon 2020 mod so that an agent can apply the same
approach to another game (Mary Skelter, Dungeon Travelers 2, Etrian Odyssey, the other 7th Dragon titles, ...).
It is deliberately game-agnostic. Everything game specific lives in `7thdragon2020.md`.

## 1. What the mod is

The mod has two pillars. They share tooling and rules but have different goals.

| Pillar | Goal | Touches | Risk to game balance |
|---|---|---|---|
| **Information (skills + text)** | The player can make a good decision from what the screen says. | Text only (descriptions, names, manuals, menus). | None. Numbers shown are the real ones. |
| **Quality of life (QoL)** | Remove tedium, keep the challenge. | Data tables and a few engine code patches. | Real. Every knob is documented and defaults to "unchanged" unless the user asked for it. |

One sentence summary: **make hidden information visible, make tedium optional, and never silently change what the
game is.**

### Pillar A: information
* Every skill description answers "what does this do and what should I know before I pick it" within the UI limit.
* Every "next level" text says what the upgrade adds, so the player can weigh its cost.
* The original voice is kept (original tag words, "Major damage", flavour terms). Real data is added to it.
  Rewriting lore or translating again is out of scope.
* Items, town upgrades, enemy names, speaker names and NPC lines are repaired and made informative
  (the base translation had corrupted strings). A spare NPC can become an in-game manual.

### Pillar B: QoL
Walking speed, random encounter rate, map reveal radius, battle speed, reward multipliers, drop chances, EX gauge
gain and a catch-up EXP bonus for under-levelled characters. Each one is a number in one JSON file.

## 2. Principles (and why)

1. **Source of truth hierarchy: game binary > original in-game text > community docs (FAQ/wiki).**
   Community docs go stale and are sometimes wrong (several skill powers differed by 5-60 points in the 7th Dragon
   FAQ). The binary is what the game actually executes. When the binary does not hold a value (it is computed in
   code) say so explicitly in the data and in the notes instead of presenting a FAQ number as verified.
2. **One editable source, everything else generated.** Text lives in one workbook; scripts generate binaries, archives
   and the ISO. Never hand-edit a generated file. Rebuilding from scratch must always work and must be one command.
3. **The UI already shows some data; do not repeat it.** Spend scarce characters on what the screen does not show
   (rates, durations, scope, crit, drain). Check the real screen before deciding what is "missing".
4. **Hard limits are tests, not guidelines.** Character limits, byte budgets and exact file sizes are asserted by the
   test suite. A text that does not fit fails the build; it is never silently truncated.
5. **Patch in place, keep sizes.** Containers (ISO, archives, text pools) keep their exact size and layout so nothing
   else needs relocating. The original ISO is never modified. Every feature set builds into its own ISO.
6. **Every tunable is data.** Do not bury a constant in a script. A JSON file with a `_help` entry lets the user
   (or the next agent) change a number and rebuild in seconds.
7. **Defaults preserve difficulty. Compensate analytically.** If a QoL change moves the game economy (for example fewer
   random encounters means less EXP per walk), derive the compensation from the mechanism instead of guessing,
   apply it only to the part that really changed (random encounters, not bosses), and round in the direction that
   never makes the game easier unless the user asks.
8. **Find the real mechanism before changing a number.** Confirm what a value does with an extreme test build
   (encounters every step, 5x speed) and only then choose moderate values. Do not confuse similar concepts
   (random encounters vs visible field enemies cost a wrong answer once in this project).
9. **Verify without hardware wherever possible.** Re-derive patches in unit tests, execute patched machine code in a
   tiny interpreter, diff the final image against the original and check that only the intended bytes changed.
   Always state plainly what has not been run in an emulator.
10. **Fail closed.** Binary patches assert the original bytes before writing. If the game version differs, stop.
11. **Smallest possible code patch, and prefer data.** Use the data table if one exists. When code must change, reuse
    existing instruction slots and dead code, and respect the relocation table (see 7thdragon2020.md).
12. **Be honest about confidence.** Mark inferred meanings as inferred. Correct earlier statements loudly when new
    evidence contradicts them (this project corrected itself several times; the corrections are listed).

## 3. Scope boundaries

In scope: text accuracy and density, UI-limited wording, quality-of-life knobs, tests and tooling.
Out of scope: new content, new art/audio, retranslation, rebalancing combat numbers "because it feels better",
save-breaking changes, anything that needs a different executable or a custom emulator.
Distribution note: this repository keeps extracted game data for convenience. For a public release prefer shipping
the scripts and a patch that is applied to the user's own ISO, not game files.

## 4. Workflow for a new game

1. **Recon.** Identify the container (ISO / CPK / PAK / NDS filesystem), the executable format and whether it is
   encrypted. Plain relocatable ELF (PSP) can be disassembled directly; encrypted ones need a decrypted dump.
2. **Find the text system.** Encoding, fixed-width glyph tricks, how strings are indexed (ID -> offset tables), per-record
   byte budgets, pool sizes. Measure the real UI limits on screen (box width in characters, not bytes).
3. **Export the binary data to a readable workbook** (skills, effects, classes, enemies, items). Mark each column
   as read, inferred or unknown. This workbook, not the wiki, becomes the fact base.
4. **Build the single source of truth** for text (one row per string, original column next to new column).
5. **Write the generators and the tests first for the limits** (length, bytes, pool size, container size).
6. **Write the style guide with the user** and keep it in the repo (tags, separators, abbreviations).
7. **QoL research per mechanism**: find the variable, prove it with an extreme build, expose it in JSON.
8. **Package** as separate ISOs per feature set, with a one-click build script.
9. **Document** what was verified, what was inferred and what was never run.

Questions to ask the user early: which wording style, which UI limits they see, what difficulty they want to keep,
which QoL pains matter most (speed of battle, menus, encounters), whether they test in an emulator.

## 5. Anti-patterns seen in this project
* Trusting a community FAQ over the binary.
* Assuming a UI limit from a bad constant (the 54 character limit was wrong; the screen allows 44).
* Letting a spreadsheet tool corrupt line breaks (`_x000D_` escapes, dropped CR) without a loader that restores them.
* A disassembler that silently stopped at the first unknown instruction (VFPU) and left 22 % of the code invisible.
* Adding a branch/load to code without a relocation entry (it works in a test and crashes on a real load).
* Multiplying every enemy's rewards when only random-encounter enemies are affected by the encounter rate.
* Stating a mechanism as fact from a half-read function (see the Casual difficulty correction in the game notes).

## 6. What transfers to other games
Transfers directly: the hierarchy of truth, single workbook, limit tests, in-place patching, JSON knobs, compensation maths,
verification without hardware, the style-guide process, separate ISO per feature set.
Needs redoing per game: container parsing, text encoding and pools, record layouts, engine variables (speed, encounter
counter, reward code). Games from the same developer or series (the other 7th Dragon titles, sequels) often reuse
formats and engine habits, so start by checking the old tool against the new files before writing new ones, but never
assume: confirm each offset.

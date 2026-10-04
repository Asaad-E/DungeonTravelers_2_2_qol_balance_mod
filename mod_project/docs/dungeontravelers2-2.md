# Dungeon Travelers 2-2 (PC): what was done, how, and how to continue

Reference for agents and modders working on *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, Aquaplus / Sting engine). Read `philosophy.md` first for the reasoning, and `docs_example/` for the method this project copies.

Confidence tags: **[verified]** read from the binary and confirmed by a byte-identical round trip or a test; **[inferred]** deduced from the data, a guide or the vanilla text; **[untested]** never run in the game.

Language of chat with the user: Spanish. Everything in the repository: English.

---

## 1. Deliverables

The mod ships as **two variants that are built separately**.

| Variant | Goal | May change game values | State |
|---|---|---|---|
| **QoL** | Everything the player needs to make an informed decision is in the game, clean, understandable and easy to read. | No. Every figure shown is the original one. | In progress, and the current focus. Skill text built and verified against the binary; not yet reviewed on screen. Everything else pending. |
| **Balance** | Address the biggest complaints of Japanese players (`COMMUNITY_BALANCE_COMPLAINTS.md`), and show the information of the rebalanced game. | Yes, each change as data. | Starts when QoL is right. Not defined yet. |

Tools are built once for both variants: the variant is a parameter of the build, not a second toolchain.

| Output | Built by | Content |
|---|---|---|
| `build/qol/Data/ENG/Parameter/*SkillData.pck` | `tools/build_variant.py qol` | 4 skill archives, 267 of 330 entries with new text, numeric data identical to the original. **[untested]** in the game. |
| `data_tables/vanilla_source_of_truth.xlsx` | `tools/extract_vanilla.py` | Decoded binaries. The fact base. Generated, never edited. |
| `data_tables/qol_skill_text.xlsx` | `tools/generate_qol_skill_text.py`, then edited by hand | Text of the QoL skills (`QoL_Desc`, `QoL_LvUp`). The editable source for that text. |
| Installed game + `dist/DT22_Definitive_QoL_Balance_Mod_v1.0.zip` | `tools/apply_mod.py`, `tools/package_release.py` | The **earlier mixed build** (text and value changes together). Not releasable: see section 8 and `CROSS_SYSTEM_VALIDATION_REPORT.md`. |

---

## 2. Repository map

```
DungeonTraveler2-2/
├── DungeonTravelers2-2_EN/Data/ENG/   live game files (Parameter/, Script/). Currently hold the earlier mixed build.
├── Data/                              GameFAQs pages (*.mhtml). Cross-check only, never a source of values. Not versioned.
├── docs_example/                      method and reference project (7th Dragon 2020)
└── mod_project/
    ├── backups/                       untouched original .pck files (36). Every build reads from here.
    ├── data_tables/                   workbooks (section 2.1)
    ├── build/<variant>/               output of build_variant.py. Not versioned.
    ├── tools/                         section 2.2
    ├── tests/                         section 7
    └── docs/
```

### 2.1 Workbooks

| Workbook | Edited by hand | Role |
|---|---|---|
| `vanilla_source_of_truth.xlsx` | No (generated) | Original values of skills, items, equipment, enemy attacks, traps, ranks, EXP. `Fields` sheet = meaning and confidence of every column. |
| `qol_skill_text.xlsx` | Yes | QoL skill text. Write `yes` in `Edited` to keep a row from being regenerated. |
| `skills.xlsx`, `items.xlsx`, `equipment.xlsx`, `enchants.xlsx`, `grand_seals.xlsx`, `joint_skills.xlsx`, `party_skills.xlsx`, `food_menu.xlsx`, `enemy_attacks.xlsx`, `classes.xlsx`, `ui_strings.xlsx`, `traps.xlsx`, `trophies.xlsx`, `exp_curve.xlsx`, `quest_ranks.xlsx` | Yes | Tables of the earlier mixed build (15), read by `apply_mod.py`. Their "vanilla" columns match the backups; many of their figures do not match the binaries (section 8). |

### 2.2 Tools

| Tool | Purpose |
|---|---|
| `pck_handler.py` | Archive reader/writer and one helper per record type. |
| `extract_vanilla.py` | Backups -> `vanilla_source_of_truth.xlsx`. Fails if a layout assumption does not hold. `--check-guides` compares with `Data/*.mhtml`. |
| `generate_qol_skill_text.py` | Proposes the QoL skill text in the style of section 6. Leaves rows marked `Edited` alone. |
| `text_checks.py` | Checks that every figure in a skill text is the value stored in a binary. |
| `build_variant.py` | Builds a variant into `build/<variant>/` and verifies it. Never writes into the game. |
| `apply_mod.py`, `audit_tool.py`, `package_release.py` | Earlier mixed build: compiles straight into the game folder, checks line lengths, zips from the game folder. |

Dependencies: Python standard library and `openpyxl`.

Build and test:

```bash
python mod_project/tools/extract_vanilla.py
python mod_project/tools/generate_qol_skill_text.py
python mod_project/tools/build_variant.py qol
python -m unittest discover -s mod_project/tests -p "test_*.py"
```

---

## 3. Data layout

### 3.1 PCK container **[verified]** (36 of 36 backups rebuild byte-identically)

| Part | Layout |
|---|---|
| Name section | `"Filename"` padded with spaces to 20 bytes; `u32` = offset where the names end; at `0x18`: `N x u32` name offsets relative to `0x18`, then the NUL-terminated names; zero padding to 8 bytes. |
| Pack section | `"Pack"` padded with spaces to 20 bytes; `u32` header size (`28 + 8N`); `u32` N; `N x (u32 offset, u32 size)`; 4 zero bytes. |
| Data | Each entry starts on a 16-byte boundary counted from the first entry. |
| End | Data padded to 16 bytes, then 8 zero bytes. |

### 3.2 Skill records **[verified]** (330 of 330 entries rewrite byte-identically)

Four NUL-terminated strings follow the header, each padded to 8 bytes; `u64` pointers at `0x08` name, `0x10` description, `0x18` level-up text, `0x20` **battle message** (`"%name hung in there! Gutsy!"`; empty for most skills). Unique skills have only name and description.

| Field | Technique (`0x1F0`) | Magic (`0x238`) | Passive (`0xD8`) | Type | Tag |
|---|---|---|---|---|---|
| Target code | `0x28` | `0x28` | - | int | [verified] same codes as the enemy attack header lines |
| Damage type / element | `0x2C` | `0x2C` | - | int | [verified] idem |
| SP cost per level | `0x34` | `0x34` | `0x2C` | 10 x int | [inferred] non-zero entries = max level |
| TP cost per level | `0x5C` | `0x5C` | - | 10 x int | [verified] |
| Duration in turns | `0x84` | `0x84` | - | 10 x int | [inferred] matches the guides |
| Turn speed multiplier | `0xAC` | `0xAC` | - | 10 x float | [inferred] higher = acts again sooner |
| Chant speed multiplier | - | `0xD4` | - | 10 x float | [inferred] higher = shorter chant |
| Accuracy | - | `0xFC` | - | 10 x float | [inferred] from the vanilla "Accuracy UP" phrase |
| Unknown value | - | `0x124` | - | float | unknown |
| Required weapon(s) | `0xD4` count, `0xD8`, `0xDC` | - | `0x54` | int | [verified] against "<Weapon> skill." |
| Effect count | `0xE0` | `0x128` | `0x58` | int | [verified] equals the slots in use in all 312 skills |
| Effect slots | `0xE4`, 5 slots | `0x12C`, 5 slots | `0x5C`, 2 slots | 48 bytes each | [verified] |
| Trailer | `0x1D4` | `0x21C` | `0xBC` | 7 x int | unknown |

Effect slot = `int` effect id, 10 values (one per level, `int` or `float`), `int` tail (unknown). Unique skills (`0x60`): `0x1C` = 10 floats, levels 1-9 and EX.

Codes **[verified]**: target `0` single enemy, `1` random, `2` enemy row, `3` piercing, `4` all enemies, `5` single ally, `7` ally row, `8` all allies, `9` self. Type `0` weapon's, `1` slash, `2` stab, `3` bash, `4` fire, `5` water, `6` wind, `7` earth, `8` lightning, `9` neutral. Weapon `1` sword, `2` dagger, `3` axe, `4` lance, `5` mace, `7` tome, `8` bow, `9` katana, `10` projectile, `11` whip, `12` fan, `15` gun, `16` shield.

Effect ids are shared by skills, enemy attacks and traps. Named with evidence (21 of 257): `1` magic power, `26` physical power (damage = 100% + value), `29` accuracy modifier, `74` dispel, `75` HP drain, `76` TP drain, `103` heal power, `113` poison, `114` freeze, `115` paralysis, `116` sleep, `117` silence, `118` stun, `119` instant death, `120` petrification, `122` slow, `137` number of targets, `162` DEF modifier, `169` all-element resistance, `170` aggro, `295` heal cap. The rest are listed in the `Effects` sheet with the skills that use them. The meaning of an id is **[inferred]** (guide, trap names or vanilla text); its values are **[verified]**.

### 3.3 Other records

| Record | Layout | Tag |
|---|---|---|
| `ItemData` (`0x70`, `u64` pointers `0x08` name, `0x10` description, `0x60` second name) | `0x1C` buy price, `0x20` sell price, four `(int type, float value)` effect pairs from `0x24`. Types: `0` HP, `1` TP, `3` party HP, `6` cure ailment, `8` revive, `9` light steps, `10` escape. | prices [verified] against vanilla shop lines; pairs 3-4 unknown |
| `EquipmentData` (`0x80`, `u32` pointers `0x08`, `0x10`, `0x18`, `0x70`) | `0x20` category (`0` weapon, `1` shield, `2` helm, `3` armor, `4` accessory), `0x4C` index into `WeaponRankData` (`-1` if none), `0x5C` number of innate enchants, `0x60-0x6C` enchant ids. | [verified]. `0x24-0x58` stats unidentified (`0x24` looks like ATK, `0x58` like price) |
| `WeaponRankData` | `0x10` float delay, name at `0x18`. Vanilla: A+ 1.00, A 1.20, B+ 1.40, B 1.60, C+ 1.80, C 2.00, D+ 2.15, D 2.30, E+ 2.45, E 2.60, F+ 2.75, F 2.90. | [verified] |
| `TrapData` (`0x20`) | `0x10` effect id, `0x14` float rate, `0x1C` scope. The name is inserted into `"You triggered a %name trap!"`. | [verified] |
| `QuestRankData` | 10 ints: rank, trust points, text offset, 0, reward type, item id, three more, value; then the message. | [verified] |
| `LvExpSkptData` | level, EXP required, SP granted (`3 x u32`). | [verified] |
| `EnemyAttackData` (`0xA0`, four `u64` pointers) | `0x2C` target, `0x30` type, `0x44` float power, `0x48` effect count, five `(id, value, tail)` slots from `0x4C`. | counts [verified] in 2,375 entries; power [inferred] |
| `FoodMenuData` | `0x18` price, `0x1C` effect count, `(id, float)` pairs from `0x20`. No duration field found. | [inferred] |
| `JoinSkillData`, `PartySkillData`, `SealScrollData`, `ClassData` | Not decoded. Dumped word by word in the `Raw_*` sheets. | unknown |
| ADV scripts (`Teaching`, `Lesson`, `Shop*`) | Bytecode with NUL-terminated strings; jumps go by label name, so a string can change length. A spoken line includes its quotes: `"...behave."` + NUL. | [inferred]; no absolute offsets found |

### 3.4 Writers

| Helper | Rewriting the original text reproduces the entry |
|---|---|
| Skills (all four), `ItemHelper`, `EquipmentHelper`, `ClassDataHelper`, `StringDataHelper`, `TrapHelper`, `TrophyHelper` | Yes, every entry **[verified]** |
| `JoinSkillHelper` | 51 of 52. Drops a string in one entry (`"Genocide Rain(St) pours down!"`). |
| `PartySkillHelper` | 0 of 20. Replaces the full-width space of the second string with two normal spaces. |
| `EnemyAttackHelper`, `EnchantHelper`, `SealScrollHelper`, `FoodMenuHelper` | 1,220 of 2,375; 142 of 280; 339 of 374; 10 of 16. Same strings, different padding. |

Fix a writer (make its round trip exact, add it to the tests) before building its table for any variant.

---

## 4. Text system and limits

* **Description boxes: 3 lines, 85 characters per line** **[verified]** measured on screen by the user. The description counts as a line: a skill has 1 description line and at most 2 level-up lines.
* **Equipment box** **[verified]** on a screenshot of the earlier build: the game draws the item's enchantments (their `EnchantData` names) on lines 2 and 3 of the box, in two columns, on top of whatever the description has there. All 551 vanilla equipment descriptions are one line (77 characters at most). An equipment description must stay on **line 1**.
* The equipment title bar already shows `[Sword - 2 Hand - Short Range] Speed E+`: weapon type, hands, range and speed rank. Do not repeat them.
* The game lists innate enchantments there too (seen: Legendary Duster shows `Max HP +10%` and `Interrupt Rate -25%`), and draws the stat change of the item (`ATK+24`) at the right end of line 1. An `Innate:` line in the description repeats the first and a long line 1 would run into the second.
* Because the game lists the enchantments by name, the place to add information about them is the enchant name (`Fire Magic +15%`), not the item description.
* The enchant values shown by the earlier build are **not verified**: vanilla names carry no figure (`Max HP UP`, `Max HP MiniUP`, `Fire magic buff`) and the earlier build assigned one by tier word (`UP` -> +10%, `MiniUP` -> +5%, `buff` -> +15%). No field holding the magnitude has been found in `EnchantData`, and there is no enchant guide in `Data/`. They need a source before QoL shows them.
* Whether item and skill boxes draw anything of their own on lines 2-3 has not been checked on screen. All 576 vanilla item descriptions are one line.
* The tilde `~` has no glyph. Use `->` or `-`.
* Strings are stored as Latin-1 bytes.
* Dialogue boxes (ADV scripts) hold 3 lines in every vanilla script; the longest vanilla line is 62-63 characters in the shops, 69 in `Teaching`, 76 in `Lesson`. Wider lines are **[untested]**.
* Separator between pieces of one line: `' | '`.

---

## 5. The rule for each variant

| | QoL | Balance |
|---|---|---|
| Numeric part of every entry | Identical to the backup. Checked by the build. | Changed only where a data table says so. |
| Figures in the text | The original ones, from `vanilla_source_of_truth.xlsx`. | The ones of the built binary. |
| Text describing a mechanic | Only what the base game does. | Only what the built data implements. |

A figure is never typed from a guide or from memory. If the binary does not hold a value (it is computed in the executable), the text says nothing about it.

---

## 6. Skill text

**The standard is `SKILL_DISPLAY_PHILOSOPHY_AND_SPECIFICATION.md`.** It is a style guide: its mockups show the form, not the figures. Figures always come from `vanilla_source_of_truth.xlsx`.

What the player must see at a glance: what the skill does now, what the next level gives, what it costs.

* **Line 1**: the vanilla description, untouched.
* **Line 2**: the effect, level by level. **Line 3**: `Turns | TP Cost | Speed`.
* One value per level with `->`. Up to 5 levels every value carries its unit; with more, only the first and last: `ATK: 125% -> 134 -> 143 -> ... -> 200% (L10)`.
* A table with the same step at every level may be written as base, exact step and cap when the list does not fit: `ATK: 130% (+8%/Lv) -> 202% (L10 Max)`, `Accuracy: +20% (+2%/Lv)`.
* Speed, chant and long durations are written first -> last: `Speed: 0.8x -> 0.9x`.
* **Never an average.** `text_checks.py` rejects `avg`, and rejects a step that is not exact.
* Labels: `ATK` (damage as % of a normal hit), `Pwr` (magic power), `Turns`, `TP Cost`, `Speed`, `Chant`, `Accuracy`, the ailment name, `HP Absorb`, `TP Absorb`, `Targets`, `Heal Cap`. Buffs and debuffs take the stat with its sign, as in the mockups: `"ATK increase UP"` -> `ATK: +8%`, `"DEF decrease UP"` -> `DEF: -11%`. Any other label is the wording of the vanilla level-up phrase.

How `generate_qol_skill_text.py` applies it when a box cannot hold everything (rule chosen by the user: **every effect of the skill stays in the box**):

1. The main effect is shown level by level.
2. Every other effect stays. If its list does not fit it becomes base + step: `Accuracy: +20% (+2%/Lv)` when the step is the same at every level, or the real bounds of the step when it is not, `Instakill: 10% (+1-2%/Lv) -> 20%`. The bounds are the smallest and largest rise between two levels; this is not an average.
3. The TP cost is shown level by level while it fits; otherwise `TP Cost: 38 (+4/Lv) -> 74` or `TP Cost: 5 (+2-3/Lv) -> 28`.
4. Speed and chant are the first to be left out, then a long duration shrinks to first -> last.

An effect that does not fit on line 2 opens line 3, before the costs. `text_checks.py` verifies exact steps and step bounds against the binary.

The workbook lists, per skill, what is not level by level (`Not_Level_By_Level`) and what was left out (`Left_Out`). Today: 267 boxes, no effect left out; speed is left out in 37 and chant in 39; TP is level by level in 109 boxes, base + exact step in 25, base + step bounds in 27.

Examples:

| Skill | Line 2 | Line 3 |
|---|---|---|
| War Cry | `ATK: +8% -> +10% -> +12% -> +15% -> +18% (L1-5 Max)` | `Turns: 4 -> 5 -> 6 -> 7 -> 8 \| TP Cost: 5 -> 7 -> 9 -> 11 -> 13` |
| Halving Slice | `ATK: 80% -> 83 -> 86 -> 89 -> 91 -> 94 -> 97 -> 100 -> 105 -> 110% (L10)` | `Instakill: 10% (+1-2%/Lv) -> 20% \| TP Cost: 38 (+4/Lv) -> 74 \| Speed: 0.65x -> 0.75x` |
| Fireball | `Pwr: 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520 (L10)` | `Accuracy: 86% (+1%/Lv) \| TP Cost: 5 (+2-4/Lv) -> 32 \| Speed: 2.25x` |
| Mad Zapper | `ATK: 130% (+8%/Lv) -> 202% (L10 Max) \| Slow: 25% -> 45% \| Accuracy: -5% (+2%/Lv)` | `TP Cost: 24 -> 27 -> 30 -> 33 -> 36 -> 39 -> 42 -> 45 -> 48 -> 50 \| Speed: 0.75x` |

How a vanilla phrase is tied to a table:

| Vanilla phrase | Table | Evidence |
|---|---|---|
| TP Cost | TP cost | Phrase present in exactly the 161 skills whose TP varies |
| Time until next turn | Speed | 55 of 55 |
| Chant time | Chant | 69 of 70 |
| Duration | Turns | 38 of 42 |
| Damage | Effect 26 (techniques) or 1 (magic) | 75 of 85, and the guides |
| Accuracy | Effect 29 (techniques) or `0xFC` (magic) | Section 3.2 |
| "X rate" of an ailment | Effect 113-122 | Trap names |
| Anything else | The only unexplained table of the skill | Only when exactly one phrase and one table are left |

Coverage: 246 boxes with every vanilla phrase resolved, 21 partly, 15 left as vanilla, 48 internal skills skipped; 50 per-level tables of 31 skills are not tied to any phrase (`Tables_Not_Shown`).

Editing by hand: change `QoL_Desc` / `QoL_LvUp` in `qol_skill_text.xlsx` and write `yes` in `Edited`; the generator leaves that row alone and the build still checks its figures.

---

## 7. Tests (what each guards)

`python -m unittest discover -s mod_project/tests -p "test_*.py"` (25 tests).

| File | Guards |
|---|---|
| `test_pck_roundtrip.py` | Every backup archive rebuilds byte-identically; every skill entry rewrites identically; the battle message survives a text change. |
| `test_source_of_truth.py` | Layout assumptions on the real files; figures confirmed with the guides; vanilla weapon delays; the saved workbook is not stale. |
| `test_text_checks.py` | The checker accepts every approved notation and rejects wrong values, inexact steps, wrong level counts and averages. |
| `test_qol_variant.py` | Text table within the limits and with true figures; a clean build has no problems; a wrong figure, a long line, a stale table, a changed game value and a lost battle message each stop the build. |

Verified without the game: container and entry round trips, numeric identity of the QoL build, 733 figures in the built text against the built binary. Never run in the game: everything.

---

## 8. State of the earlier mixed build

Audited at commit `28c7d90`; details in `CROSS_SYSTEM_VALIDATION_REPORT.md`. It is what the game folder and the zip currently contain.

* 11 of 47 dialogue replacements never reached the game; the script reports success.
* `WeaponRankData.pck` is changed in the game folder but missing from the zip.
* Skill figures do not match the binary: TP 125 of 141, physical power 37 of 39, magic power 17 of 22, max level 53 of 162.
* Seven mechanics are announced in text with no data behind them (Master Spell resistance pierce, Defend crit immunity, Killer Floor 25%, 900-step meals and others).
* The 200 modified skills have their battle-message pointer past the end of the entry; 17 lost a real message.
* All 551 equipment descriptions use 3 lines, and the game draws the enchantments over lines 2-3 (seen in the game: `Fire Magic +15%` printed over `[Weapon | Range: Short | Delay: E+ (2.05x) | Slots: 0]`). That second line also repeats what the title bar shows, and `Slots` is the count of innate enchants, not a slot capacity.
* On a save made before the mod, a character can show a negative `NEXT` (seen: Lv 20, EXP 22,501, NEXT -1,577): the lighter curve puts her past the next threshold until she gains EXP again.
* Real value changes it contains: EXP curve and +25 SP, weapon delays, 4 items, Slave's Torc enchant, 5 quest rank rewards.

---

## 9. Mistakes made and corrected (do not repeat)

1. **Figures written without reading the binary.** The earlier skill text interpolated or invented most TP costs and powers. Now text is generated from the extracted workbook and checked by `text_checks.py`.
2. **Layouts documented as verified that were not.** An earlier version of this file described a container with a 16-byte header and 48-byte entries, skill headers of `0x28-0x38` bytes and weapon delays `2.2 / 2.4 / 2.6 / 2.7 / 2.8`. None of it matched the files.
3. **Dropping the fourth skill string.** `SkillHelper.write_skill` wrote three strings and left the battle-message pointer dangling. Found by requiring a byte-identical round trip.
4. **Archive tail.** `PckArchive.build` padded the end of the file differently from the original (8-16 bytes short in 22 of 36 archives).
5. **Silent text replacement.** `update_teaching_script` looks for the string plus NUL; spoken lines end in a quote before the NUL, so the search fails and the code continues without a word. A replacement that does not find its target must stop the build.
6. **One build for two goals.** Text for a rebalanced game was shipped over mostly unchanged data. Variants are now built separately, each against its own rule.
7. **A check that only measures line length was reported as a full audit.**
8. **Effect names guessed.** `rebuild_enemy_attacks.py` labels effect 120 as Slow and 122 as Charm; the trap table shows 120 is petrification and 122 is slow (113 enemy attack texts are wrong).
9. **A guide match called "verified".** A value read from the binary is verified; what the field means stays inferred, however well a guide agrees.
10. **Flavor text replaced by data sheets** in class descriptions and enemy attacks, against the rule of adding to the original voice.
11. **A box limit taken as free space.** 3 lines and 85 characters is what a box can hold, not what is free: the equipment box uses lines 2-3 for its own enchant list. Look at the real screen for each kind of box before writing into it, and do not repeat what the screen already shows.

---

## 10. Not done / next

* QoL text for items, equipment, enchants, sealbooks, joint and party skills, meals, traps, trophies, classes, enemy attacks, UI strings, the library and the lessons.
* Exact writers for joint skills, party skills, enemy attacks, enchants, sealbooks and meals.
* Decoding `JoinSkillData`, `PartySkillData`, `SealScrollData`, `ClassData`, the equipment stats and the 236 unnamed effects.
* The Balance variant: its changes as data, and its own verification rule.
* Install and packaging per variant (today `package_release.py` zips the game folder).
* Dialogue replacement that fails loudly, and the corrected lines.
* Running any build in the game.

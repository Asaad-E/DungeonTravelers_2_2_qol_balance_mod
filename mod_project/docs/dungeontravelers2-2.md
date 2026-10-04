# Dungeon Travelers 2-2 (PC): what was done, how, and how to continue

Reference for agents and modders working on *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, Aquaplus / Sting engine). Read `philosophy.md` first for the reasoning, and `docs_example/` for the method this project copies.

Confidence tags: **[verified]** read from the binary and confirmed by a byte-identical round trip or a test; **[inferred]** deduced from the data, a guide or the vanilla text; **[untested]** never run in the game.

Language of chat with the user: Spanish. Everything in the repository: English.

---

## 1. Deliverables

The mod ships as **two variants that are built separately**.

| Variant | Goal | May change game values | State |
|---|---|---|---|
| **QoL** | Everything the player needs to make an informed decision is in the game, clean, understandable and easy to read. | No. Every figure shown is the original one. | In progress, and the current focus. Built, verified and installed in the game: skill text and item amounts (against the binary), enchant names (figures from player guides) and weapon rank labels. Review on screen in progress. Everything else pending. |
| **Balance** | Address the biggest complaints of Japanese players (`COMMUNITY_BALANCE_COMPLAINTS.md`), and show the information of the rebalanced game. | Yes, each change as data. | Starts when QoL is right. Not defined yet. |

Tools are built once for both variants: the variant is a parameter of the build, not a second toolchain.

| Output | Built by | Content |
|---|---|---|
| `build/qol/Data/ENG/Parameter/*SkillData.pck` | `tools/build_variant.py qol` | 4 skill archives, 268 of 330 boxes with level-by-level data; line 1 of 80 techniques and spells with a damage word and the ailment chance; numeric data identical to the original. Skill menu box **[verified]** on screen. |
| `build/qol/Data/ENG/Parameter/EnemyAttackData.pck` | `tools/build_variant.py qol` | 858 of 2,375 enemy attacks (also the abilities of summoned monsters) with the exact ailment chance on their data line; prose identical to the original. **[untested]** on screen. |
| `build/qol/Data/ENG/Parameter/EnchantData.pck` | `tools/build_variant.py qol` | 142 of 280 enchant names carry their figure (`Max HP +10%`, `Water resistance -20%`, `Enmity -5%`); flags, prefix and suffix identical to the original. Installed; **[untested]** on screen. |
| `build/qol/Data/ENG/Parameter/ItemData.pck` | `tools/build_variant.py qol` | 9 of 576 descriptions: the exact amount replaces the vague size (`Restore an ally's HP (+250).`); prices and effects identical to the original. Installed; **[untested]** on screen. |
| `build/qol/Data/ENG/Parameter/WeaponRankData.pck` | `tools/build_variant.py qol` | Rank names generated from the multiplier of each rank (`E+ (2.45x)`); multipliers identical to the original. **[untested]** in the game. |
| `data_tables/vanilla_source_of_truth.xlsx` | `tools/extract_vanilla.py` | Decoded binaries. The fact base. Generated, never edited. |
| `data_tables/qol_skill_text.xlsx` | `tools/generate_qol_skill_text.py`, then edited by hand | Text of the QoL skills (`QoL_Desc`, `QoL_LvUp`). The editable source for that text. |
| `data_tables/qol_enchant_text.xlsx` | `tools/generate_qol_enchant_text.py`, then edited by hand | Name of each enchantment in QoL (`QoL_Name`) and the guide its figure comes from (`Figure_Source`). |
| `data_tables/qol_item_text.xlsx` | `tools/generate_qol_item_text.py`, then edited by hand | Description of each item in QoL (`QoL_Desc`). |
| The game folder | `tools/install_variant.py` (run by `build_variant.py`) | Holds **the QoL variant and nothing else** since 2026-10-04: the 8 built archives over the 39 untouched originals (47 files checked by the install) (section 8.1). |
| `docs/QOL_ROADMAP.md` | by hand, from the build output | Every pack with its state, what is left and the order of work. The checklist for calling QoL finished. |
| Installed game + `dist/DT22_Definitive_QoL_Balance_Mod_v1.0.zip` | `tools/apply_mod.py`, `tools/package_release.py` | The **earlier mixed build** (text and value changes together). Not releasable: see section 8 and `CROSS_SYSTEM_VALIDATION_REPORT.md`. Two files of the installed game were replaced at the user's request (section 8.1). |

---

## 2. Repository map

```
DungeonTraveler2-2/
├── DungeonTravelers2-2_EN/Data/ENG/   live game files (Parameter/, Script/). Hold the last variant installed by build_variant.py.
├── Data/                              GameFAQs pages (*.mhtml). Cross-check only, never a source of values. Not versioned.
├── docs_example/                      method and reference project (7th Dragon 2020)
└── mod_project/
    ├── backups/                       untouched original .pck files (36), and backups/Script/ (11 scripts, among them the SEV.pck that shares its name with a Parameter file). Every build and install reads from here.
    ├── data_tables/                   workbooks (section 2.1)
    ├── build/<variant>/               output of build_variant.py. Not versioned.
    ├── build/installed_backup/<time>/ game files replaced by an install, as they were. Not versioned.
    ├── tools/                         section 2.2
    ├── tests/                         section 7
    └── docs/
```

### 2.1 Workbooks

| Workbook | Edited by hand | Role |
|---|---|---|
| `vanilla_source_of_truth.xlsx` | No (generated) | Original values of skills, items, equipment, enemy attacks, traps, ranks, EXP. `Fields` sheet = meaning and confidence of every column. |
| `qol_skill_text.xlsx` | Yes | QoL skill text. Write `yes` in `Edited` to keep a row from being regenerated. |
| `qol_enchant_text.xlsx` | Yes | QoL enchant names. Same `Edited` rule. `Figure_Source` names the guide of each figure; `Previous_Mod_Check` says how the earlier build's figure stands against the guides. |
| `qol_enemy_attack_text.xlsx` | Yes | QoL enemy attack text (2,375 rows). Same `Edited` rule; only line 1 may change. |
| `qol_item_text.xlsx` | Yes | QoL item descriptions. Same `Edited` rule. `Effect_Pairs` lists the raw effect pairs of each item. |
| `skills.xlsx`, `items.xlsx`, `equipment.xlsx`, `enchants.xlsx`, `grand_seals.xlsx`, `joint_skills.xlsx`, `party_skills.xlsx`, `food_menu.xlsx`, `enemy_attacks.xlsx`, `classes.xlsx`, `ui_strings.xlsx`, `traps.xlsx`, `trophies.xlsx`, `exp_curve.xlsx`, `quest_ranks.xlsx` | Yes | Tables of the earlier mixed build (15), read by `apply_mod.py`. Their "vanilla" columns match the backups; many of their figures do not match the binaries (section 8). |

### 2.2 Tools

| Tool | Purpose |
|---|---|
| `pck_handler.py` | Archive reader/writer and one helper per record type. |
| `extract_vanilla.py` | Backups -> `vanilla_source_of_truth.xlsx`. Fails if a layout assumption does not hold. `--check-guides` compares with `Data/*.mhtml`. |
| `generate_qol_skill_text.py` | Proposes the QoL skill text in the style of section 6. Leaves rows marked `Edited` alone. |
| `text_checks.py` | Checks that every figure in a skill text is the value stored in a binary. |
| `enchant_values.py` | The figure of each enchantment and the guide it comes from (the binary holds none). `SHOWN_SOURCES` decides which guides QoL trusts. |
| `generate_qol_enchant_text.py` | Proposes the QoL enchant names from `enchant_values.py`. Leaves rows marked `Edited` alone. |
| `weapon_rank_labels.py` | Writes the delay multiplier of each weapon rank into its name. Used by the build; also `weapon_rank_labels.py SOURCE.pck DEST.pck` for any `WeaponRankData.pck`. |
| `magnitude_words.py` | Line 1 of a skill: the damage scale, the chance forms, where they go in the sentence, and the check against the binary. |
| `generate_qol_enemy_attack_text.py` | Proposes the enemy attack text: ailment chances on the data line, prose untouched. |
| `generate_qol_item_text.py` | Proposes the QoL item descriptions: the exact amount in place of `(small)` / `(medium)` / `(large)`. Leaves rows marked `Edited` alone. |
| `build_variant.py` | Builds a variant into `build/<variant>/`, verifies it and, only if the verification passes, installs it into the game (`--no-install` to skip). |
| `install_variant.py` | Puts the game folder in the state of a variant: its built files, and the original for every other backed-up file. Saves what it replaces in `build/installed_backup/<time>/`. |
| `apply_mod.py`, `audit_tool.py`, `package_release.py` | Earlier mixed build: compiles straight into the game folder, checks line lengths, zips from the game folder. |

Dependencies: Python standard library and `openpyxl`.

Build and test:

```bash
python mod_project/tools/extract_vanilla.py
python mod_project/tools/generate_qol_skill_text.py
python mod_project/tools/generate_qol_enchant_text.py
python mod_project/tools/generate_qol_item_text.py
python mod_project/tools/generate_qol_enemy_attack_text.py
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

Effect ids are shared by skills, enemy attacks and traps. Named with evidence (69 of 257; the first 21 listed here, the rest in `EFFECT_NAMES` of `extract_vanilla.py` and section 2.5 of `QOL_ROADMAP.md`): `1` magic power, `26` physical power (damage = 100% + value), `29` accuracy modifier, `74` dispel, `75` HP drain, `76` TP drain, `103` heal power, `113` poison, `114` freeze, `115` paralysis, `116` sleep, `117` silence, `118` stun, `119` instant death, `120` petrification, `122` slow, `137` number of targets, `162` DEF modifier, `169` all-element resistance, `170` aggro, `295` heal cap. The rest are listed in the `Effects` sheet with the skills that use them. The meaning of an id is **[inferred]** (guide, trap names or vanilla text); its values are **[verified]**.

### 3.3 Other records

| Record | Layout | Tag |
|---|---|---|
| `ItemData` (`0x70`, `u64` pointers `0x08` name, `0x10` description, `0x60` second name) | `0x1C` buy price, `0x20` sell price, four `(int type, float value)` effect pairs from `0x24`. Types: `0` HP, `1` TP, `3` party HP, `6` cure ailment, `8` revive, `9` light steps, `10` escape. | prices [verified] against vanilla shop lines; pairs 3-4 unknown |
| `EquipmentData` (`0x80`, `u32` pointers `0x08`, `0x10`, `0x18`, `0x70`) | `0x20` category (`0` weapon, `1` shield, `2` helm, `3` armor, `4` accessory), `0x4C` index into `WeaponRankData` (`-1` if none), `0x5C` number of innate enchants, `0x60-0x6C` enchant ids. | [verified]. `0x24-0x58` stats unidentified (`0x24` looks like ATK, `0x58` like price) |
| `WeaponRankData` (`0x18`, `u64` name pointer at `0x08`) | `0x00` index, `0x10` float delay, name at `0x18` padded to 8 bytes. Vanilla: A+ 1.00, A 1.20, B+ 1.40, B 1.60, C+ 1.80, C 2.00, D+ 2.15, D 2.30, E+ 2.45, E 2.60, F+ 2.75, F 2.90. | [verified]. That the title bar prints this name is [inferred] |
| `EnchantData` (`0x38`, `u64` pointers `0x08` name, `0x10` prefix, `0x18` suffix) | `0x00` id, then flag words at `0x20-0x34`; each string padded to 8 bytes, no padding after the last. Prefix and suffix are `"0"` for enchantments that random equipment cannot roll. **No magnitude field**: what an enchantment does is in the executable. `0x2C` takes the values 1, 10, 30, 50, 75 and looks like the minimum item level. | layout [verified] (280 of 280 rewrite identically); `0x2C` [inferred] |
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
| Skills (all four), `ItemHelper`, `EquipmentHelper`, `EnchantHelper`, `EnemyAttackHelper`, `WeaponRankHelper`, `ClassDataHelper`, `StringDataHelper`, `TrapHelper`, `TrophyHelper` | Yes, every entry **[verified]** |
| `JoinSkillHelper` | 51 of 52. Drops a string in one entry (`"Genocide Rain(St) pours down!"`). |
| `PartySkillHelper` | 0 of 20. Replaces the full-width space of the second string with two normal spaces. |
| `SealScrollHelper`, `FoodMenuHelper` | 339 of 374; 10 of 16. Same strings, different padding. |

Fix a writer (make its round trip exact, add it to the tests) before building its table for any variant.

---

## 4. Text system and limits

* **Description boxes: 3 lines, 85 characters per line** **[verified]** measured on screen by the user. The description counts as a line: a skill has 1 description line and at most 2 level-up lines.
* **Equipment box** **[verified]** on a screenshot of the earlier build: the game draws the item's enchantments (their `EnchantData` names) on lines 2 and 3 of the box, in two columns, on top of whatever the description has there. All 551 vanilla equipment descriptions are one line (77 characters at most). An equipment description must stay on **line 1**.
* The equipment title bar already shows `[Sword - 2 Hand - Short Range] Speed E+`: weapon type, hands, range and speed rank. Do not repeat them. The delay multiplier of the rank is shown by putting it in the rank name itself (`Speed E+ (2.45x)`, section 6.1). Whether the longer title still fits the bar is **[untested]**.
* The game lists innate enchantments there too (seen: Legendary Duster shows `Max HP +10%` and `Interrupt Rate -25%`), and draws the stat change of the item (`ATK+24`) at the right end of line 1. An `Innate:` line in the description repeats the first and a long line 1 would run into the second.
* Because the game lists the enchantments by name, the place to add information about them is the enchant name (`Max HP +10%`), not the item description (section 6.1).
* Enchant name length: 40 characters for enchantments that random equipment can roll (they are drawn in two columns in the equipment box), 46 otherwise. These are the longest vanilla names, **[inferred]** as safe, not measured.
* **Battle bar** **[verified]** on screenshots: when a skill or item is highlighted in battle the game shows only its description (line 1), in one line, without the level. A figure that depends on the level cannot be read there, so line 1 of a skill carries only the main points (section 6.2). Its width in characters is **[untested]**.
* **Skill menu box** **[verified]** on a screenshot (Provoke): title bar `Provoke [Technique] Lv 2 TP Cost 2` drawn by the game, then the description and the two level-up lines; nothing is drawn over lines 2-3.
* **Enemy attack box** **[verified]** on a screenshot (summon Cupid, Poison Shot): three lines, the first is a data line written in the text itself (`Target: Single / Type: Stab / Range: Long`), then prose.
* **Title bar with the rank label** **[verified]** on a screenshot: `Dungeon Prez Rod [Staff - 1 Hand - Short Range] Speed C (1.75x)` fits.
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
| Game folder after a build | The variant and nothing else (built files + originals). Checked by the install. | The same, for its own files. |
| Figures in the text | The original ones, from `vanilla_source_of_truth.xlsx`. | The ones of the built binary. |
| Text describing a mechanic | Only what the base game does. | Only what the built data implements. |

Order of sources, set by the user: **binary first, then player guides of this same game** (the Japanese wiki is the most complete). A figure is never typed from memory, and a guide never overrides the binary. When the binary does not hold a value (it is computed in the executable), a figure may be shown only if a guide of this same game gives it; it is recorded with its source in a table (`enchant_values.py`), tagged **[inferred]**, and the build refuses any other figure. A figure known only from another game (the first Dungeon Travelers 2) is weaker: it is shown only because the user decided so, and its source stays written next to it. Without a source, the text says nothing.

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

### 6.1 Enchant names and weapon rank labels

Both are names that the game prints by itself on the equipment screen, so the information goes into the name and the item description stays as the vanilla line.

**Enchant names.** The binary has no magnitude for an enchantment, so the figures come from guides, in this order of trust (`tools/enchant_values.py`):

| Source | What | Used by QoL |
|---|---|---|
| `dt22-wiki` | Japanese wiki of this game: [enchant effects](https://w.atwiki.jp/dt2-2/pages/38.html) ([table](https://w.atwiki.jp/dt2-2/pages/39.html)), [grand sealbooks](https://w.atwiki.jp/dt2-2/pages/40.html), [player tests](https://w.atwiki.jp/dt2-2/pages/105.html) | Yes: 99 names |
| `dt2-wiki` | Japanese wiki of the first Dungeon Travelers 2: [enchant effects](https://w.atwiki.jp/dungeon-travelers2/pages/200.html). Same system, another game. Where both wikis give a figure they agree, except stat DOWN (-10% there, -5% here) and two stacking caps. | Yes, by decision of the user (2026-10-04): 43 names. Not confirmed for this game. |

How a name is written: the tier word of the vanilla name is replaced by the figure, and nothing else changes (`Max HP UP` -> `Max HP +10%`, `Received damage MiniDOWN` -> `Received damage -4%`, `Fire resistance MegaUP` -> `Fire resistance +100`). Names without a tier word are worded by hand in the same table (`HP recovery every turn` -> `Recover 4% HP every turn`). An enchantment without a figure keeps its vanilla name; a name that already has its figure (`Front line ATK 8% UP`) is not touched.

Figures of this game's wiki (all **[inferred]**: a guide, not the binary; the 43 of the first game's guide are listed below the table):

| Family | MiniUP | UP | GrandUP | MegaUP | DOWN | GrandDOWN |
|---|---|---|---|---|---|---|
| Max HP, Max TP, ATK, DEF, INT, RES, DEX, AGI | +5% | +10% | | | -5% (Max TP -10%, Max HP unknown) | |
| One element, or slash / stab / bash | +10% | +20% | +50% | +100% | -20% | -50% |
| All five elements | +7% | +15% | +50% | +75% | -15% | -30% |
| Slash + stab + bash | +5% | +10% | +25% | +50% | -10% (first game's guide) | -20% |
| Received physical or magic damage | -5% | -10% | | | | |
| Received damage (both) | -4% | -8% | | | | |
| HP every turn (slight / normal / large) | 2% | 4% | 8% | | | |
| TP every turn (slight / normal / large) | 2 | 4 | 6 | | | |

Resistance is stored as points where 100 is immunity (the guide, and the skill effects in the binary: Stab Guard 20 to 36), so a point is 1% of the damage taken; it is written with `%` in enchant names and in the 6 skill boxes that show it, as the user asked. **[inferred]**: the damage formula was not read.

Figures from the first game's guide: physical and magic attack +4% / +2%, speed +10% / +5%, chant speed +20% / +10%, enmity +5% / -5%, interruption rate -6% / -3% / +6%, element magic +20%, HP absorb 15% / 50% and TP absorb 5% / 20% of the damage, race bonuses +20% / +40% / +100% (Fruit +50%), 5% of received damage into TP, Max HP DOWN -10%. To stop showing them: remove `'dt2-wiki'` from `SHOWN_SOURCES` and run the generator.

**Glossary.** A name or a text uses the words the game uses. The vanilla name is the base and only its tier word is replaced: `Enmity DOWN` -> `Enmity -5%`, never `Aggro`; `Water resistance DOWN` -> `Water resistance -20%`, never `Water Res`.

**Items.** `generate_qol_item_text.py`: where the vanilla text gives a vague size and the binary holds the amount, the amount replaces the word, and a text never carries both (`Restore an ally's HP (medium).` -> `Restore an ally's HP (+250).`). `text_checks.check_item_text` ties each amount to the first effect pair of the item, by kind (HP, TP, HP of all allies) and value.

**Weapon rank labels.** `weapon_rank_labels.py` writes each rank name from the multiplier stored in the same entry: `E+` -> `E+ (2.45x)`. The label is never typed: when Balance changes a multiplier, the same step produces the new figure, and the build fails if a label and its multiplier differ. The multiplier is the same kind of figure as `Speed: 0.65x` in a skill box: time until the next turn, lower is faster.

### 6.2 Line 1 of a skill, and enemy attacks

**Line 1 of techniques and spells** (`tools/magnitude_words.py`). It is the only line the battle bar shows, and it shows it without the level, so it carries the main points and nothing else:

* Damage as one word, chosen by the average of the real per-level values. The words and the 80% floor are the user's; the other bounds come from the data.

| Word | Physical: average ATK | Magic: average Pwr | Skills today |
|---|---|---|---|
| negligible | below 80% | below 80 | 1 |
| minor | 80% - 124% | 80 - 249 | 17 |
| moderate | 125% - 149% | 250 - 399 | 26 |
| major | 150% - 174% | 400 - 499 | 8 |
| severe | 175% - 224% | 500 - 699 | 16 |
| tremendous | 225% and above | 700 and above | 5 (the game's own word for exactly these spells; out of the scale) |

* Chance of an ailment, of a dispel (`May cancel enemy buffs (68-85%)`) or of a turn delay, as the shortest true figure: `(25%)` when it is the same at every level, `(30%+)` when it rises by 10 points or less, `(20-50%)` when it rises by more. Nothing when it always happens. No tilde: the font has none.
* Where the word goes: before the kind of damage (`Deal minor bash damage`), in place of the game's own grading word (`Powerful strike` -> `Major strike`), or `Attack one enemy` -> `Deal moderate damage to one enemy`. Five sentences that name no damage have a hand-written place (`TEMPLATES`).
* A skill whose damage the power table does not measure gets no word (3 today, listed in `Line1_Notes`): Spiral Arrow is ATK 88% but carries effect 73 at 3.3 to 4.0, which the game describes as "several times ATK in damage". Which effects leave the power table as the measure of a hit is the set `SAFE_EFFECTS`; each of its ids is named with its evidence, and a test holds that.
* Examples: `Shield skill. Deal minor bash damage to one enemy. May stun (30%+).` `Deal moderate fire damage to one enemy.` `Stun one enemy (65%+).` `Deal tremendous fire damage to one enemy.`

The build checks every word and chance against the built binary, and rejects any other figure in line 1.

**Level-up lines after decoding the effects.** Phrases that used to stay as the game wrote them now carry their table: `Critical rate: 5% (+2.5%/Lv) -> 15%` and `Enemy critical rate` (Last Stand), `Damage: 1.05x -> ... -> 1.3x` (Power Charge), `Physical evasion` and `Magic evasion` (Warm-Up), `Max HP damage: 4% -> ... -> 8%` with `Damage cap: 250 -> 500` (the scrolls, Debilitating Salsa), `DEF` and `Magic defense` (Carrot and Stick), `Post-battle HP` and `Post-battle TP` (Generous Heart), `Speed decrease chance` (Phoenix). The parameters of the summoned dolls (228-233) are not guessed: `ATK UP` stays.

**Enemy attacks** (`tools/generate_qol_enemy_attack_text.py`), which are also the abilities of summoned monsters. Their text is a data line followed by prose. The prose, jokes included, is never touched (the build compares it with the original); exact figures are added to the data line in its own format:

```
Target: Single / Type: Stab / Range: Long / Poison: 30%
Fire an arrow doused in some real toxic stuff.
If it hits, it may inflict poison. Also, ouch.
```

An attack has no levels, so its figures are exact. Shown so far: the chance of each of the 9 ailments (858 attacks, 922 chances). Equal chances share an item (`Freeze/Silence: 20%`). Entry layout: header `0xA0`, four `u64` string pointers (name, Japanese name, a third string, description), each string padded to 8 bytes; `0x48` effect count, then `(int id, float value, int tail)` slots of 12 bytes from `0x4C`. **[verified]**: 2,375 of 2,375 rewrite identically.

**Rule for every other text** (set by the user): whatever a screen shows must give the precise data, and the jokes and the in-game prose stay. Data is added beside the prose, in a place that already holds data when there is one.

---

## 7. Tests (what each guards)

`python -m unittest discover -s mod_project/tests -p "test_*.py"` (84 tests).

| File | Guards |
|---|---|
| `test_pck_roundtrip.py` | Every backup archive rebuilds byte-identically; every skill entry rewrites identically; the battle message survives a text change. |
| `test_source_of_truth.py` | Layout assumptions on the real files; figures confirmed with the guides; vanilla weapon delays; the saved workbook is not stale. |
| `test_text_checks.py` | The checker accepts every approved notation and rejects wrong values, inexact steps, wrong level counts and averages. |
| `test_qol_variant.py` | Text table within the limits and with true figures; a clean build has no problems; a wrong figure, a long line, a stale table, a changed game value and a lost battle message each stop the build. |

| `test_qol_enchants_and_ranks.py` | Enchant and weapon rank entries rewrite identically; names keep the game's wording and add the sourced figure; a source that is not trusted is not shown; names fit; an unsourced figure, an overlong name, a changed flag and a changed multiplier each stop the build; a rank label follows its multiplier and is idempotent. |
| `test_qol_items_and_install.py` | Item table matches the backups; the amount replaces the vague size and no text states both; a wrong amount, a wrong kind and a changed item value stop the build. The install leaves the game as the variant and nothing else, saves what it replaces, and a second install changes nothing. |
| `test_qol_line1_and_enemy_attacks.py` | Bounds of the damage scale and forms of the chance; line 1 of real skills; a skill whose damage the power table does not measure stays as written; a wrong word, a wrong chance or a level figure in line 1 stops the build. Enemy attack writer exact; chance on the data line; prose never changed; a wrong chance, an edited joke and a changed value stop the build. |
| `test_effect_decoding.py` | The evidence for the decoded effects is re-read from the files: figures stated by enemy attack texts equal the stored values (fixed crit rate, cap, fixed damage, fixed accuracy), hit-count and ignore-defense wording goes with its id, and the only disagreements are the four known errors of the original text. Every effect treated as harmless for the damage word is named with its evidence. No box leaves an effect out. |

Verified without the game: container and entry round trips, numeric identity of the QoL build, 733 figures in the built skill text and 9 item amounts against the built binary, every rank label against its multiplier, the game folder against the variant after an install. Enchant figures cannot be verified against the binary (it holds none): they are checked against the source table only. Seen on screen by the user: the rank label in the title bar. Everything else of the QoL build is installed and waiting for a look.

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
* Enchant names: of 215 figures it added, 80 agree with a guide (64 with the DT2-2 wiki, 16 with the first game's), 62 contradict one (35 the DT2-2 wiki, 27 the first game's) and 73 have no source at all (`Previous_Mod_Check` column of `qol_enchant_text.xlsx`). Examples: `All Phys Res +15` (guide: +10), `Fire Res +30` for MegaUP (guide: +100), `Damage +100%/empty party slot` (player test: +10%), `Higher-Level Enemy EXP +50%` (guide: +15%).

### 8.1 What the game folder holds now

The user asked for every build to be installed so the work can be checked on screen. Since 2026-10-04 `build_variant.py qol` leaves the game folder holding the QoL variant and nothing else; the earlier mixed build is no longer installed. Its files are kept in `build/installed_backup/2026-10-04_181942/` (23 files) and `build/installed_before_restore/` (2 files).

| File in the game folder | Now | Effect |
|---|---|---|
| `TechniqueSkillData`, `MagicSkillData`, `PassiveSkillData`, `UniqueSkillData`, `EnchantData`, `ItemData`, `EnemyAttackData`, `WeaponRankData` | QoL build. | Text only; every value is the original one. Weapon ranks read `C (2.00x)`, `E+ (2.45x)`: the original multipliers, not the 1.75x / 2.05x of the earlier build. |
| The other 28 backed-up archives, among them `EquipmentData`, `ClassData`, `LvExpSkptData`, `QuestRankData`, `StringData`, `TrapData` and the scripts `Lesson`, `Teaching`, `ShopStore`, `ShopQuest`, `ShopBlacksmith` | The original from `backups/`. | The value changes of the earlier build are gone from the game: EXP curve and +25 SP, weapon delays, 4 items, Slave's Torc, 5 quest rank rewards, and all of its text. |

To undo an install, copy the matching `build/installed_backup/<time>/` folder back over `DungeonTravelers2-2_EN/Data/ENG/`.

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
12. **Enchant figures assigned by tier word.** The earlier build read `UP` as +10%, `MiniUP` as +5%, `MegaUP` as +30 and so on for every family. The families do not share a scale (all-physical resistance is +10 / +5 / +25 / +50, single resistances +20 / +10 / +50 / +100, combined damage reduction -8% / -4%). A figure needs its own source.
13. **Changing the game's glossary.** The earlier build renamed `Enmity` to `Aggro/Enmity`, `resistance` to `Res`, `Physical accuracy` to `Phys Hit`. The player learns one word per concept from the whole game; a name keeps the vanilla words.
14. **A vague word next to the exact value** (`(medium) (+250 HP)`), and **level-dependent figures in line 1** (`Hit Rate: +20% -> +38% (+2%/Lv)` in the battle bar, where the level is not shown). Both from the earlier build; both now stop the build or are excluded by construction.

---

## 10. Not done / next

* QoL text for items, sealbooks, joint and party skills, meals, traps, trophies, classes, enemy attacks, UI strings, the library and the lessons. Equipment descriptions stay vanilla: the title bar, the stat change and the enchant list already cover them.
* Enchant figures: 43 come from the first game's guide and are not confirmed for this one; no guide gives a figure for accuracy, evasion, defense, critical rate, ailment chances on hit and most grand sealbook effects. Finding them means reading the enchant code in the executable or testing in the game.
* Items: only the 9 restoratives with a vague size were touched. About 150 other items have effect pairs of types that are not decoded (sealbook materials); Hipanera Tea and Kuding Tea heal HP and TP but carry a third pair that is not understood, so their text was left alone.
* A scale of words for magnitudes whose exact value cannot be shown (the battle bar, where the level is unknown): proposed to the user on 2026-10-04, five words per kind (damage, modifier, chance) chosen from the average over the levels. Waiting for the user's word list and for the go-ahead to add it to line 1, which the display specification keeps vanilla.
* Stacking limits reported by the DT2-2 wiki (speed UP counts up to 5, chant speed UP up to 3, damage reductions down to -25%, Max HP up to +50%, equal `All stats +N` do not add up) are in the `Note` column only; nothing in the game shows them yet.
* Exact writers for joint skills, party skills, enemy attacks, sealbooks and meals.
* Decoding `JoinSkillData`, `PartySkillData`, `SealScrollData`, `ClassData`, the equipment stats and the 236 unnamed effects.
* The Balance variant: its changes as data, and its own verification rule.
* Packaging per variant (today `package_release.py` zips the game folder). Install is done: `install_variant.py`.
* Dialogue replacement that fails loudly, and the corrected lines.
* Everything still open is listed, pack by pack and with its size, in `QOL_ROADMAP.md`. That file is the checklist for calling QoL finished.

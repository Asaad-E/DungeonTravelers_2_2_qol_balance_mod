# Dungeon Travelers 2-2 (PC): the technical reference

Reference for modders working on *Dungeon Travelers 2-2: The Fallen Maidens & the Book of Beginnings* (PC, Aquaplus / Sting engine): the file formats, the text system and its limits, and the rules the text of the mod follows. Read `philosophy.md` first for the reasoning.

Sections 3 to 7 and 9 were written while the QoL variant was built (2026-10-04) and hold for both variants; the counts they give are those of that day. Where the work stands is in `QOL_ROADMAP.md` (QoL, closed) and `BALANCE_PLAN.md` section 7 (Balance). The battle formulas are in `FORMULAS.md`.

Confidence tags: **[verified]** read from the binary and confirmed by a byte-identical round trip or a test; **[inferred]** deduced from the data, a guide or the vanilla text; **[untested]** never run in the game.

Everything in the repository is in English.

---

## 1. Deliverables

The mod ships as **two variants that are built separately**, from the same tools and the same text template.

| Variant | Goal | May change game values | State |
|---|---|---|---|
| **QoL** | Everything the player needs to make an informed decision is in the game, clean, understandable and easy to read. | No. Every figure shown is the original one. | Closed (`QOL_ROADMAP.md`). |
| **Balance** | Answer the complaints of the Japanese players and the criticisms of the English guide (the register: `data_tables/balance_criteria.xlsx`, sheet `Criticisms`), and show the figures of the changed game. | Yes: each change is a row of `data_tables/balance_changes.xlsx`. It also patches the program (sheet `ExePatches`). | Built and installed; in its final checks (`BALANCE_PLAN.md` section 7). |

`tools/build_variant.py <variant>` builds a variant into `build/<variant>/` and verifies it; `tools/install_variant.py`
puts it into the game, saving what it replaces; `tools/apply_mod.py` runs the whole chain (the README of the
repository tells it step by step).

---

## 2. Repository map

The layout, the workbooks and the tools are listed in `mod_project/README.md`. No file of the game is in the
repository: `backups/` is made by `tools/setup_backups.py` from a copy of the game.

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
| `JoinSkillData` (`0x98`, `u64` pointers `0x08` name, `0x10` description, `0x20` battle message) | `0x18` participants, `0x28` Pep needed, `0x2C` Pep spent, `0x30` target, `0x34` attribute, `0x40` power, `0x44` turns, `0x48` delay (floats), `0x4C` TP divisor, `0x50` effect count, four `(int id, float value, int tail)` slots from `0x54`. | strings, slots and TP divisor [verified] (52 of 52 rewrite exactly; divisor equals the wiki's fraction); Pep and power [inferred] |
| `PartySkillData` (header up to the name, `u64` pointers `0x08`, `0x10`, `0x18`) | `0x20` number of members, `0x24` member ids (9 slots), `0x48` members needed, `0x4C` effect id (entry of `CommandData`). String 2 is `members\neffect`; string 3 repeats it with a full-width space before the effect. No amount is stored. | [verified] (20 of 20) |
| `SealScrollData` (`0x48`, `u64` pointers `0x08` name, `0x10` description, `0x38` name again) | `0x18` kind (`0` sealbook, `1` grand), `0x1C` number of enchantments, `0x20` four enchantment ids, `0x30` price, `0x34` level. | [verified] (374 of 374; every id exists in `EnchantData`; the level equals the one in the text) |
| `ClassData` | Not decoded. Dumped word by word in the `Raw_Class` sheet. | unknown |
| ADV scripts (`Teaching`, `Lesson`, `Shop*`) | Bytecode with NUL-terminated strings; jumps go by label name, so a string can change length. A spoken line includes its quotes: `"...behave."` + NUL. | [inferred]; no absolute offsets found |

### 3.4 Writers

| Helper | Rewriting the original text reproduces the entry |
|---|---|
| Skills (all four), `ItemHelper`, `EquipmentHelper`, `EnchantHelper`, `EnemyAttackHelper`, `WeaponRankHelper`, `FoodMenuHelper`, `PartySkillHelper`, `JoinSkillHelper`, `SealScrollHelper`, `ClassDataHelper`, `StringDataHelper`, `TrapHelper`, `TrophyHelper` | Yes, every entry **[verified]** |

Fix a writer (make its round trip exact, add it to the tests) before building its table for any variant.

---

## 4. Text system and limits

* **Description boxes: 3 lines, 85 characters per line** **[verified]** measured on screen by the user. The description counts as a line: a skill has 1 description line and at most 2 level-up lines.
* **Equipment box** **[verified]** on a screenshot of the earlier build: the game draws the item's enchantments (their `EnchantData` names) on lines 2 and 3 of the box, in two columns, on top of whatever the description has there. All 551 vanilla equipment descriptions are one line (77 characters at most). An equipment description must stay on **line 1**.
* The equipment title bar already shows `[Sword - 2 Hand - Short Range] Speed E+`: weapon type, hands, range and speed rank. Do not repeat them. The delay multiplier of the rank is shown by putting it in the rank name itself (`Speed E+ (2.45x)`, section 6.1). Whether the longer title still fits the bar is **[untested]**.
* The game lists innate enchantments there too (seen: Legendary Duster shows `Max HP +10%` and `Interrupt Rate -25%`), and draws the stat change of the item (`ATK+24`) at the right end of line 1. An `Innate:` line in the description repeats the first and a long line 1 would run into the second.
* Because the game lists the enchantments by name, the place to add information about them is the enchant name (`Max HP +10%`), not the item description (section 6.1).
* Enchant name length: 40 characters for enchantments that random equipment can roll (they are drawn in two columns in the equipment box), 46 otherwise. These are the longest vanilla names, **[inferred]** as safe, not measured.
* **Battle bar width** **[verified]** on a screenshot: a 71-character line is drawn whole, a little wider than the purple band (about 68 characters); the skill list next to it shows the TP cost of the current level.
* **Status screen** **[verified]** on a screenshot: the game itself writes resistance as a plain number with an abbreviated label (`Fi Res 0`, `Bs Res -20`).
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

### 6.3 Rules set by the user on 2026-10-04, second round, and how each is built

| Rule | Built as |
|---|---|
| A value the skill has is in its box, also when every level has the same. | `EXTRA_EFFECTS` in `generate_qol_skill_text.py`: `Speed decrease: 10%` (Phoenix), `DEF: -10%` (Justice), `Damage vs. unholy: +65%` (Cross Slash), `HP Absorb: 100%` (Blood Absorb). An effect leaves a box only as the last resort; a test holds that none does. |
| Line 1 must say the value, also for buffs, heals and passives. When it changes with the level the box has each one. | `put_values` in `magnitude_words.py`, same three forms as the chances: `Raise the party's ATK (8%+).` `ATK bonus with sword equipped (3-15%).` The label goes with the figure when the sentence does not name it: `Revive a dead ally (HP on revival 40-88%).` Skills with several effects list them: `(ATK 20-50%, DEF 11-25%)`. |
| A chance of 100% says 100%. | `chance_text` and `enemy_ailments` cap a stored chance at 100% and write it. |
| When the text and the data disagree, the data wins. Keep as much of the original sentence as possible. | `correct_prose` in `text_checks.py`: a figure the prose states (`STATED_FIGURES`) or a word that names another effect (`WORDING_FIXES`) is replaced, nothing else. 11 enemy attacks; the list is in `QOL_ROADMAP.md` 2.5. The build accepts a changed prose only when it equals this correction. |
| Items: original text + (data). | `generate_qol_item_text.py`: `Sandwich filled with soft, fluffy eggs. (HP/TP +10, cures 1 ailment)`. Data is what the item does on an ally (first two effect pairs); what the sentence already says is not repeated; the sentence itself cannot change. |

**The game's own table of effects.** `CommandData.pck` has one entry per effect id with the game's name for it (317 names: "Fixed Accuracy", "Damage xn", "Power Drops", "Percent HP Damage"). `extract_vanilla.py` reads it into the `Game_Name` column of the `Effects` sheet. Entry layout: `0x00` id, four `u64` name pointers from `0x08`, then battle messages. It confirmed every meaning decoded from the enemy attack texts.

**Enemy attack data line, second pass.** After the ailments: `Fixed damage`, `Max HP damage`, `Cap`, `Accuracy` (fixed), `Critical rate`, `HP Absorb`, `TP Absorb`, `Turn delay rate`, `Buff cancel rate`, `Speed decrease chance`, `Shadow Sew`, the stat changes (`ATK`, `DEF`, `Magic defense`, `Physical evasion`, `Magic evasion`, `Physical accuracy`, `Magic accuracy`, `Speed`) and `Pep`. Stat changes of the same size share an item (`DEF/Magic defense: -25%`, `Physical/Magic accuracy: -25%`). What does not fit in 85 characters is left out in order of importance and named in the `Note` column (32 entries).

**Item effect types** (first two pairs act on an ally, last two on an enemy): `0` HP, `1` TP, `2` HP and TP, `3` party HP, `4` party TP, `6` cure one ailment, `7` cure all ailments, `8` revive (value = % HP), `9` light (value x 5 steps, from the DT2-2 wiki), `10` leave the dungeon, `16` sleep chance, `22` cancel Shadow Sew, `23` restore lowered stats, `24` skill points. **[inferred]** from the DT2-2 wiki item list, which gives the same amounts as the stored values. Other types are not decoded.

---
### 6.4 Nothing hardcoded, party skills and joint skills (2026-10-04, fifth round)

**Rule of the user: nothing hardcoded; everything in a workbook, for quick editing.** `data_tables/qol_rules.xlsx` holds every table that used to be a dict in a tool. `tools/rules.py` reads it (`rules.rows(sheet)`, `rules.setting(key)`); the modules keep their names (`ITEM_SENTENCES`, `PHYS_BOUNDS`, `VALUES`, `ITEM_EFFECTS`...) and fill them from the sheets. Moving the tables changed no generated text (every cell of the five text workbooks was compared before and after). A new wording or guide figure is a new row or sheet there, never code.

| Sheet | Was | Holds |
|---|---|---|
| `Settings` | constants | `small_rise`, `full_restore`, `light_steps_per_unit`, `line_width`, `award_count`, `party_skill_note` |
| `DamageScale`, `Line1Templates` | `magnitude_words.py` | Words and bounds of the damage scale; where the word goes in sentences that name no damage |
| `ShortItems`, `ShortSkills`, `SkillTemplates` | `shortened_text.py` | Sentences shortened by hand |
| `SkillEffectLabels` | `generate_qol_skill_text.py` | Phrase of the game -> effect id, label, number style |
| `EnchantValues`, `EnchantSources` | `enchant_values.py` | Figure or name of each enchantment, its guide, and which guides are shown |
| `ItemEffects` | `text_checks.py` | Wording of each item effect type (`HP +{v}`), scale, harmful or not |
| `EnemyEffects`, `WordingFixes` | `text_checks.py` | Labels of the enemy data line; corrected words of the prose |
| `PartySkillBounds` | new | Bound of each party skill bonus (DT2-2 wiki, pages/72.html) |
| `JointEffects`, `JointSkillSentences` | new | How a joint skill effect is written; the sentences with `{eID}` places |

**Party skills.** The effect line keeps the game's sentence and gains the bounds in the order it names them: `Wind resistance and AGI increased. (Up to +20% and +10 at 50 awards)`. The list of members is not touched. The check accepts the original line or exactly that one.

**Joint skills.** One sentence, one line. Where it speaks of an effect whose value the entry stores, the value is written in and replaces the vague word: `High chance of instakill.` -> `85% chance of instakill.`; `Inflicts slow.` -> `Inflicts slow (100%).`; `multiple bash attacks` -> `3-5 bash attacks` (effect 96, "3~5 Hits" in the game's table). The data wins over the text in one sentence: Psychowave says "lower DEF" and stores physical and magic defense, as its Japanese text says. The build re-renders each sentence from the entry and stops if the text differs.

### 6.5 Limits measured on screen and line 1 without values (2026-10-04, sixth round)

| Place | Limit | Measured on | Setting in `qol_rules.xlsx` |
|---|---|---|---|
| Battle bar: line 1 of techniques and spells, joint skill sentences, item lines | 70 | Self-Sacrifice, 70 characters: "the most that fits well" | `battle_line_width` |
| Box of the party skill list | 50 | A line of 53 ran over the frame; the user set the limit at that minus 3 | `party_line_width` |
| Lines 2-3 of the skill box, enemy attack lines, passive and unique boxes | 85 | Earlier screenshots | `line_width` |

The build stops on a modified line longer than its limit. Texts of the original game that are longer and get nothing added stay as they are.

**Line 1 does not repeat values.** `Distribute all of one's TP to the target (TP transfer bonus 100-140%).` sat right above `TP transfer bonus: 100% -> ... -> 140%`. Line 1 of a skill that deals no damage is now the game's sentence; setting `line1_values` (`no`). The damage word and the chance of an ailment stay: they are the user's own design for the battle bar, where the level is not shown.

**A sentence that does not fit is rewritten by hand, in the workbook**: `ShortSkills` (44), `ShortItems` (201), `JointSkillSentences` (35). Each keeps the joke or the image and drops filler: `Katana skill. Moderate bash damage to an enemy. May paralyze (20-50%).`, `Legendary. Eat it and fall in love. (HP/TP +1000, cures all ailments)`.

**A figure the game data does not hold** comes from a guide of this game, and the screen does not say so. Arcane Shield stores the reflected share only; its third line reads `Activation rate: about 15%` (DT2-2 wiki, pages/42.html; the source is the `Source` column of the sheet `UniqueSkillNotes`).

**Hard rule: the voice of the game is never broken.** The first version of that line read `Activation rate: about 15% (player guide; the game data holds no figure)`; the user: "horrible... nunca hacer esto NUNCA". No text of the mod may speak from outside the game: no source, no caveat, no note to the reader. Provenance and confidence live in the workbooks and in these docs. `check_game_voice` in `build_variant.py` stops the build when a modified text holds a word of the sheet `OutOfGameWords` (guide, wiki, data, binary, source, unknown...) that the game's own text did not have.

### 6.6 Scripts, unique skill labels, packaging (2026-10-04, last round)

**Scripts are patched in place, never resized.** An ADV script (`Lesson`, `Teaching`, `Shop*`) is bytecode with NUL-terminated strings inline; no offset or length of a string was found in it, and none is relied on. A correction is a sentence of exactly the same number of bytes (a trailing space pads it), listed in the sheet `ScriptFixes`; `build_script_fixes` replaces it, checks that it occurs once and that no other entry and no size changed, and writes the pack to `build/<variant>/Data/ENG/Script/`, from where `install_variant.py` installs it into the game's `Script/` folder.

**Unique skills.** `UniqueSkillData` stores one array per skill (9 levels and the Crown) and the sentence does not always say what it measures. The sheet `UniqueSkillLabels` names it (`Activation rate` where the sentence says "may" or "occasionally", `Reflected`, `Weapon modifier`...) in place of `Lv1-9`. `UniqueSkillNotes` adds a line for a figure the entry does not store.

**Item effect types decoded with the wiki's item list** (2026-10-04): `27` chance of speed up; `46` Fire Blast, `47` Ice Storm, `48` Thunder Chain, `49` Air Turbulence, `51` Soul Absorb, `93` Ice Edge, `98` Muon Plasma, `101` Tempest, `102` Stone Hammer, `103` Meteor, `104` Gaia Crush, `106` Rainbow Flash (the value is the spell level; the enemy-side pair is the one shown); `69` party cures freeze; `88` enemies flee.

**Package.** `tools/package_variant.py qol` -> `dist/DT22_qol_<date>.zip`: the files that differ from the original, their originals under `Original/`, and the player README kept in `release/README_QoL.txt`.

### 6.7 QoL closed (2026-10-04)

The user accepted the QoL variant ("todo perfecto") with two last decisions:

* **Resistances are written without `%`**, as the status and enemy screens write them (`Bs Res -20`, `+15`): `Fire resistance +20`, `Resistance: 20 -> 24 -> 28 -> 32 -> 36`, `Slash resistance increased (up to +25).`, Moon Curtain `(+25)` in Gjallarhorn. Critical rate keeps its `%` (setting `percent_points`).
* **The earlier mixed build is deleted**: its tools (an `apply_mod.py` of that time, which the present `tools/apply_mod.py` only shares its name with, `audit_tool.py`, `package_release.py`, the `populate_*`, `update_*`, `generate_enchants`... scripts) and its 15 workbooks. The `Previous_Mod_*` columns of the text workbooks are now empty.

What the Balance variant inherits: the backups, `pck_handler.py` (every writer exact), `vanilla_source_of_truth.xlsx`, the rules workbook and its limits (70 / 50 / 85 characters, the voice of the game, nothing hardcoded), `build_variant.py` with its per-pack build and verify, `install_variant.py` and `package_variant.py`. A Balance build is a new entry in `VARIANTS` with `numeric_changes_allowed: True`, its own table of changed values, and texts generated from the changed values with the same generators.


## 7. Tests (what each guards)

`python -m unittest discover -s mod_project/tests -p "test_*.py"` (98 tests).

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

## 8. The earlier mixed build

Before 2026-10-04 the project was one build that mixed text and value changes. An audit of it found figures in the
text that did not match the data, mechanics announced with nothing behind them, replacements that failed in silence
and boxes drawn over one another. It was removed with its tools and workbooks, and its lessons are the rules of
section 9 and of `philosophy.md`: a text is generated from the data of the variant it ships with, the build proves
every figure, and a step that cannot do its job stops the build.

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

## 10. What is left

Nothing is listed here any more: what the QoL variant shows and leaves unshown, pack by pack and with the reason, is
`QOL_ROADMAP.md`; the state of the Balance variant and its known limits are `BALANCE_PLAN.md` section 7.

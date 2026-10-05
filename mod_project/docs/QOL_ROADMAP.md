# QoL roadmap: what must be true before QoL is called finished

State on 2026-10-04, after steps 2, 3 and 4 of section 4 and, of step 5, the items and the meals. Every number here was read from the files in `mod_project/backups/` or from the output of `build_variant.py qol`; nothing is estimated. Balance is out of scope until this list is closed.

Tags: **[done]** built, verified by the build and installed. **[seen]** also looked at on screen by the user. **[open]** not started or not finished. **[blocked]** needs something that is not known yet.

---

## 1. Definition of finished

QoL is finished when all seven hold. Each one is checked by a tool or by a look at the screen, never by opinion.

| # | Condition | How it is proven | Today |
|---|---|---|---|
| D1 | Every pack whose text reaches a screen has a decision: improved, or kept as written with the reason. | Table of section 2 has no row marked open. | 9 packs built. All 47 packs of `Parameter/` and `Script/` have a backup |
| D2 | Every figure on screen is the value in the binary. Where the binary has none, it comes from a guide of this game and says so. | `build_variant.py` stops otherwise. | Checked on every build: 773 figures of skill boxes, 269 words, chances and values of line 1, 566 pieces of item data, 13 meal amounts, 1,837 figures of enemy attacks, 12 rank labels. 142 enchant figures come from guides |
| D3 | No game value differs from the original. | Numeric part of every built entry compared with the backup. | Holds for the 3,589 entries of the 9 built packs |
| D4 | Jokes, prose and the game's own words are intact. Data is added next to them. Prose changes only where the data contradicts it, or where a sentence had to be shortened to fit one line. | Build check per pack. | 11 corrections of enemy attack prose; 65 item sentences and 23 skill sentences shortened by hand (`tools/shortened_text.py`), nothing else |
| D5 | Every kind of box has been seen on screen after the install, by the user. | Section 3. | 7 of 12 kinds of screen seen |
| D6 | Every pack the build writes has a writer that reproduces the original byte for byte. | Round-trip test. | 9 packs exact; 3 writers still inexact |
| D7 | Tests pass and the docs describe what is there. | `python -m unittest discover -s mod_project/tests -p "test_*.py"` | 98 tests pass |

---

## 2. Every pack, one by one

### 2.1 Packs with text, backed up (27)

"Vague" counts strings that contain words such as may, chance, slightly, small, medium, large, UP or DOWN: places where the game hints at a value without giving it. It is a search, not a judgement; it sizes the work.

| Pack | Entries | Text | Vague | Where the player sees it | State |
|---|---|---|---|---|---|
| `TechniqueSkillData` | 143 | 272 | 80 | Skill menu box, battle bar | **[seen]** box and battle bar. Open items below (2.3) |
| `MagicSkillData` | 98 | 188 | 89 | Skill menu box, battle bar | **[seen]** battle bar. Open items below (2.3) |
| `PassiveSkillData` | 71 | 123 | 43 | Skill menu box | **[done]** 62 boxes with data; line 1 of 60 says how much. Not seen |
| `UniqueSkillData` | 18 | 21 | 4 | Skill menu box | **[done]** 18 with Lv1-9 and Crown EX. Not seen. The text gives the numbers but not what they measure |
| `EnchantData` | 280 | 243 | 104 | Equipment box (two columns), blacksmith, sealbooks | **[seen]** in the equipment box. 142 names with figure (99 from this game's guide, 43 from the first game's), 37 already had one, 101 have none in any guide |
| `ItemData` | 576 | 609 | 41 | Item box, battle bar, shops | **[done]** 391 items state what they do, in one line: 326 as original sentence + (data), 65 with the sentence shortened to fit. **[open]** 55 carry an effect that is not decoded (2.6). Not seen |
| `EnemyAttackData` | 2,375 | 2,521 | 693 | "View the details of your teammates' abilities" (summons); enemy info | **[seen]** for a summon. 1,456 entries with exact data on the data line; 11 corrections of the prose. Open items below (2.4) |
| `WeaponRankData` | 12 | names | 0 | Equipment title bar | **[seen]** `Speed E+ (2.45x)` |
| `CommandData` | 364 | 317 names | 0 | Battle messages ("Critical rate increased!") | It is the game's own table of effects: one entry per effect id with its name (2.5). Nothing to rewrite; it is a source |
| `EquipmentData` | 551 | 584 | 22 | Equipment box | Kept as written: the game already draws type, hands, range, speed, stat change and enchants. **[open]** read the 22 vague texts; stats at `0x24-0x58` not decoded |
| `SealScrollData` | 374 | 374 | 0 | Sealbook list | **[open]** not decoded. Writer exact for 339 of 374 |
| `JoinSkillData` | 52 | 56 | 10 | Joint skill menu, battle | **[open]** not decoded ("Inflict a powerful physical attack on one enemy. Inflicts slow."). Writer exact for 51 of 52 |
| `PartySkillData` | 20 | 24 | 0 | Party skill list | **[open]** next. The entry points to an effect of `CommandData` (360-377, 400-415) and holds no amount; the DT2-2 wiki gives the upper bound of each bonus ("HP +100"). Writer exact for 0 of 20 |
| `FoodMenuData` | 16 | 16 | 8 | Ice cream and ramen shops | **[done]** 11 effect lines with the stored amount (`Heal 30% HP and 20% TP.`); flavour lines untouched; writer exact. **[open]** the level of the buff a meal gives ("gain Sun Veil") is not decoded. Not seen |
| `ClassData` | 49 | 32 | 6 | Class change screen | **[open]** not decoded. Prose only; decide whether any data belongs here |
| `QuestData` | 471 | 49 | 0 | Quest desk | **[open]** 49 reward lines ("Ring +8 that raises all stats by 3"): check each against the item it gives |
| `QuestRankData` | 20 | 15 | 0 | Quest rank messages | **[open]** 8 lines with figures to check against the reward fields |
| `TrophyData` | 50 | 42 | 0 | Trophy list | **[open]** 5 lines with figures to check |
| `IntroductionData` | 21 | 23 | 4 | Character introductions | Prose. **[open]** read once; no data expected |
| `StringData` | 636 | 423 | 6 | UI labels and battle messages | **[open]** 21 lines with figures to check |
| `Lesson` (script) | 65 | 763 | 63 | Euthys' lessons | **[open]** 24 lines state figures or rules: each must match the binary |
| `Teaching` (script) | 25 | 166 | 16 | Tutorials | **[open]** 16 lines with figures: each must match the binary |
| `ShopStore`, `ShopQuest`, `ShopBlacksmith`, `ShopBar` (scripts) | 50, 61, 15, 31 | 357 | 37 | Shop dialogue | **[open]** 16 lines with figures (prices, rules) to check |
| `TrapData` | 12 | names | 0 | "You triggered a %name trap!" | **[open]** each has an effect id and a rate at `0x14`; decide whether the name should carry it |

### 2.2 Packs without text, and the scripts backed up on 2026-10-04

| Pack | Entries | Note |
|---|---|---|
| `CharacterData`, `ClassLevelData`, `LvExpSkptData`, `EffectSequenceData`, `WeaponEffectSequenceData`, `TreasureBoxData`, `ShopVoiceData`, `KeyHelpData`, `SEV` (Parameter) | 250, 38, 99, 680, 22, 26, 11, 111, 226 | No prose. Nothing to show; they are sources of facts (stat growth, EXP, SP) for texts elsewhere. `ClassLevelData` (38 entries of 3,172 bytes) is not decoded |
| `Script/ShopCostume`, `ShopDarkPeddler`, `ShopIce`, `ShopPeddler`, `ShopRamen` | 15, 5, 10, 10, 10 | **[open]** Dialogue. Backed up in `backups/Script/`; not read yet |
| `Script/Battle`, `Item0885`, `evt00`, `evt02`, `evt99`, `Script/SEV` | 1, 2, 1, 10, 0, 226 | **[open]** Story and event scripts (`SEV` 804 KB, `evt02` 608 KB). Backed up in `backups/Script/`. Read for figures only; story text is not to be touched |
| `UI.pck`, `Font1.pck`, `Font2.pck`, `CG_EN.pck` | | Images and fonts. Out of scope. The font has no tilde `~` |

### 2.3 Skills: what is left

Built: 269 of 330 boxes carry data (261 with every vanilla phrase resolved, 8 partly), 48 internal entries skipped, 13 unchanged. A value that is the same at every level is shown too (`Speed decrease: 10%`). Line 1 of 222 techniques, spells and passives says the main point: a damage word, a chance, or how much the skill does. Where it did not fit, the sentence was shortened by hand (7) or its figures were placed inside it (16).

| Open item | Size | What closes it |
|---|---|---|
| Damage word missing | 1 skill | Star Dust Arrow: its damage belongs to the arrows it summons. Spiral Arrow and Holy Gavel are now `tremendous`: effect 73 is "Damage xn" in the game's table and the DT2-2 wiki lists Spiral Arrow as ATK 330% to 400%, the stored 3.3 to 4.0 |
| Vanilla phrases not tied to a table | 8 skills | Star Dust Arrow, Beast Binder (Accuracy), Spartan, Oracles, Catalina, Mercidarian, Musiy (the doll's ATK, healing, magic), Heaven or Hell |
| Per-level tables that no phrase explains | 10 tables of 9 skills | 171 (Cover), 180 (Parry), 146 and 147 (Star Dust Arrow), 228-231 and 233 (summoned dolls), 155 (Heaven or Hell). The game's table names them only by the skill ("Cover", "Parry", "Spartan"), which does not say what the number scales |
| Speed or chant left out for lack of room | 75 boxes | By design (rule B). No effect is left out of any box (a test holds it) |
| Summon skills | 6 skills | "Summon Spartan for short-range bash damage." holds no damage data; the data is in "Spartan's Action" |

### 2.4 Enemy attacks: what is left

Built: 1,456 of 2,375 entries carry exact data on their data line (ailment chances; fixed damage; max-HP damage; fixed accuracy and critical rate; HP and TP absorb; chances of turn delay, buff cancel, speed decrease and Shadow Sew; stat changes; Pep). A figure the prose already gives is not repeated. A chance stored above 100% is written as 100%.

| Open item | Size | What closes it |
|---|---|---|
| No room on the data line for every item | 32 attacks | The line holds what fits, in order of importance; the rest is named in the `Note` column |
| Data but no data line | 8 attacks | Familiars, Oracles' Action: their text is `-1` or has no "Target:" line |
| Ailment stored with chance 0 | 4 attacks | Alluring Song |
| Power (`0x44`, a float) | 2,375 | Meaning inferred, not shown. Confirm against a damage test, then add it to the data line |
| Effects not on the line | | Hit counts and conditions are said by the prose; heal power (103), breath (3) and about 150 ids used by a handful of attacks are not written |
| Where enemy attacks are shown | | Seen for summons. Confirm the enemy info screen uses the same text |

### 2.5 Effect ids: what is decoded and how

An effect id means the same in skills, enemy attacks and traps. Two sources, both inside the game:

1. **`CommandData.pck` is the game's own table of effects**: one entry per effect id, with its name ("Fixed Accuracy", "Damage xn", "Power Drops", "Percent HP Damage"). 317 ids have a name there; the `Effects` sheet of the source of truth lists it as `Game_Name` for each of the 257 ids in use.
2. **Enemy attack descriptions state the effect**, and where they give a figure the figure is the stored value. A test re-reads this on every run:

| Effect | The game's wording | Agreement with the stored value |
|---|---|---|
| 70 fixed critical hit rate | "Has a fixed critical hit rate of 50%" | 5 of 5 |
| 296 damage cap | "(Cap: 200)" | 24 of 26 |
| 8 fixed damage | "does 666 damage", "Deal 1111 fixed damage" | 18 of 19 |
| 55 fixed accuracy | "With 65% accuracy", "a fixed 50% chance to hit" | 3 of 5 |

69 ids carry a meaning with evidence written next to it (`EFFECT_NAMES` in `tools/extract_vanilla.py`); the other 188 are named by the game's table only, and are not used in any text until they are understood.

**Corrections of the original prose** (rule of the user: when the text and the data disagree, the data wins; the sentence stays and only the wrong figure or word changes):

| Enemy attack | The original says | The data holds | Now |
|---|---|---|---|
| Modest Fever | Deal 555 fixed damage | 777 | Deal 777 fixed damage |
| Scream of Despair | With 50% accuracy | 65% | With 65% accuracy |
| Debilitating Salsa | (Cap: 500) | 300 | (Cap: 300) |
| Debilitating Geas | (Cap: 999) | 500 | (Cap: 500) |
| Weathering | a fixed 50% chance to hit | 85% | a fixed 85% chance to hit |
| Heavy Stomp (4 entries), Mega Stomp (2) | Also lowers the victims' defense. | effect 161, "Physical Attack" | Also lowers the victims' physical attack. |

### 2.6 Items: what is left

An item holds four effect pairs: the first two act on an ally, the last two on an enemy (Deep-Fried Mystery, checked against the DT2-2 wiki).

| Open item | Size | What closes it |
|---|---|---|
| Shortened sentences to review | 65 items | `tools/shortened_text.py`. Each keeps the joke and drops filler ("Legendary food. Whoever eats it falls in love."). Worth a read by the user |
| Effect not decoded | 55 items | Items that cast a spell (types 46-51, 90-106), act on a kind of enemy (59, 61) or do something rare (27 and 29, two speed effects the wiki does not tell apart; 54-56, 60, 69, 88, 89). The other types were decoded with the item list of the DT2-2 wiki |
| Effect on an enemy | partly | An item made only of harmful effects shows its figures for an enemy (`25% stun`). A food that also works on enemies shows the ally's side only |
| Light items | 4 items | Steps are written as stored value x 5 (Flashlight stores 10; the wiki measures 50 steps; the ratio holds for the 4 items). Inferred from the guide |

---

## 3. Screens to look at (D5)

The install puts the build in the game after every run. One screenshot of each closes the row.

| Screen | Seen | What it showed, or what to confirm |
|---|---|---|
| Skill menu box | Yes (Provoke) | Three lines render; nothing drawn over lines 2-3. The title bar shows `Lv 2 TP Cost 2` |
| Equipment title bar | Yes | `Firewhorling Claymore of Ability+4 [Sword - 2 Hand - Short Range] Speed E+ (2.45x)` fits (83 characters) |
| Equipment box with two enchants | Yes | `Fire magic +20%` and `Physical accuracy MiniUP` in two columns; the description stays on line 1 |
| Status screen | Yes | The game writes resistance as a plain number and abbreviates: `Fi Res 0`, `Bs Res -20`. The enchant names say `Bash resistance -20%` (decision 2 of section 5) |
| Summon ability box | Yes (Cupid, Poison Shot) | `Target: Single / Type: Stab / Range: Long / Poison: 30%`, prose below, intact |
| Battle bar, skill highlighted | Yes (Freeze Shot, Circle Brave) | `Bow skill. Deal moderate stab damage to one enemy. May freeze (20-50%).` is drawn whole: 71 characters, a little wider than the purple band (about 68). The skill list beside it shows the TP cost of the current level |
| Battle bar, item highlighted | Yes, before the item data | One centred line. To confirm: `Old-fashioned rice cracker covered in soy sauce. (HP +75)` |
| Item box in the menu and in a shop | No | Whether the box draws anything of its own on lines 2-3 (decides how the 25 long items can be done) |
| Passive and unique skill boxes | No | `Lv1-9: ... \| Crown EX: ...`; line 1 with its value |
| Sealbook and grand sealbook lists | No | Which enchant names appear and whether long ones are cut |
| Enemy info (with an item that shows enemy abilities) | No | Whether it uses the enemy attack text |
| A tutorial and a lesson | No | Baseline before any dialogue is touched |

---

## 4. Order of work

Each step ends with a build that passes, an install, and a look at the screen.

1. **Close what is installed.** Screens of section 3. 7 of 12 seen.
2. **[done] Back up the 11 packs that had no backup.** They are in `backups/Script/`. All 47 archives rebuild byte for byte, the round-trip test covers them, and the install checks 47 files.
3. **[done, with a remainder] Decode the effect ids.** 69 ids with evidence, and the game's own name for 317 (`CommandData`). Remainder: how effect 73 combines with the power table (one damage test), and the summon parameters 228-233.
4. **[done] Enemy attacks, second pass.** Exact effects on the data line of 1,456 entries; 11 corrections of the prose. Remainder in 2.4.
5. **One pack at a time, smallest first.** Items done (391; remainder in 2.6). `FoodMenuData` done (16). Next: `PartySkillData` (20), `JoinSkillData` (52), `TrapData` (12), `ClassData` (49), `SealScrollData` (374). For each: decode the layout, make the writer exact, add a sheet to the source of truth, write the generator and its workbook, add the build check and the tests, install, look.
6. **Texts that state rules**: `Lesson` (24 lines), `Teaching` (16), shops (16), `StringData` (21), `QuestData` (49), `QuestRankData` (8), `TrophyData` (5). Every figure they give is compared with the binary. A line is changed only if it is false or vague; its voice stays.
7. **Enchant figures without a source**: 43 from the first game to confirm and 101 with none. They are computed in the executable: read that code, or measure in the game.
8. **Release**: package per variant, player README (what changes, how to undo), full play-through of the first dungeon with the mod, removal of the earlier build's tools and tables from the repository.

---

## 5. Decisions

Answered by the user on 2026-10-04 and applied:

| Question | Answer |
|---|---|
| Values that do not change with the level | Always shown |
| Buffs, heals and passives in line 1 | Line 1 must say the value ("10%"); when it changes with the level, the box below has each one |
| A chance of 100% | Written as `100%` |
| Bounds of the magic scale | Confirmed |
| Text and data disagree | The data wins; keep as much of the original sentence as possible |
| Items | Original text + (data), always one line; where it does not fit, the original is made shorter |
| Skills whose line 1 did not fit | The original is made shorter so that it fits |
| Spiral Arrow and Holy Gavel | Look in the Japanese guides: the wiki lists the multiplier as ATK%, so both are graded by it |

Still open:

| # | Question | Default applied until answered |
|---|---|---|
| 2 | The status screen writes resistance without `%` and abbreviated (`Bs Res -20`); the enchant names and skill boxes say `Bash resistance -20%`. Keep the `%`? | With `%`, as asked |
| 3 | Beyond the damage scale the text uses `tremendous`, the game's own word for exactly those five spells. `ultimate` was the other option. | `tremendous` |

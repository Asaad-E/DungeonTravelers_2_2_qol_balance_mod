# QoL roadmap: what must be true before QoL is called finished

State on 2026-10-04, commit after `d469d1e`. Every number here was read from the files in `mod_project/backups/` or from the output of `build_variant.py qol`; nothing is estimated. Balance is out of scope until this list is closed.

Tags: **[done]** built, verified by the build and installed. **[seen]** also looked at on screen by the user. **[open]** not started or not finished. **[blocked]** needs something that is not known yet.

---

## 1. Definition of finished

QoL is finished when all seven hold. Each one is checked by a tool or by a look at the screen, never by opinion.

| # | Condition | How it is proven | Today |
|---|---|---|---|
| D1 | Every pack whose text reaches a screen has a decision: improved, or kept as written with the reason. | Table of section 2 has no row marked open. | 8 of 36 backed-up packs built; 11 game packs not even backed up |
| D2 | Every figure on screen is the value in the binary. Where the binary has none, it comes from a guide of this game and says so. | `build_variant.py` stops otherwise. | 733 skill figures, 83 line-1 damage words and chances, 9 item amounts, 922 ailment chances, 12 rank labels checked; 142 enchant figures from guides |
| D3 | No game value differs from the original. | Numeric part of every built entry compared with the backup. | Holds for the 3,573 entries of the 8 built packs |
| D4 | Jokes, prose and the game's own words are intact. Data is added next to them, never in their place. | Build check per pack (prose identical; names keep the vanilla words). | Enforced for enemy attacks, enchants, items and line 1 of skills |
| D5 | Every kind of box has been seen on screen after the install, by the user. | Section 3. | 3 of 12 kinds of screen seen |
| D6 | Every pack the build writes has a writer that reproduces the original byte for byte. | Round-trip test. | 8 packs exact; 4 writers still inexact |
| D7 | Tests pass and the docs describe what is there. | `python -m unittest discover -s mod_project/tests -p "test_*.py"` | 72 tests pass |

---

## 2. Every pack, one by one

### 2.1 Packs with text, backed up (27)

"Vague" counts strings that contain words such as may, chance, slightly, small, medium, large, UP or DOWN: places where the game hints at a value without giving it. It is a search, not a judgement; it sizes the work.

| Pack | Entries | Text | Vague | Where the player sees it | State |
|---|---|---|---|---|---|
| `TechniqueSkillData` | 143 | 272 | 80 | Skill menu box, battle bar | **[seen]** box. Open items below (2.3) |
| `MagicSkillData` | 98 | 188 | 89 | Skill menu box, battle bar | **[seen]** box. Open items below (2.3) |
| `PassiveSkillData` | 71 | 123 | 43 | Skill menu box | **[done]** 60 boxes with data, 11 unchanged. Not seen |
| `UniqueSkillData` | 18 | 21 | 4 | Skill menu box | **[done]** 18 with Lv1-9 and Crown EX. Not seen. Meaning of the value is not stated: the text only gives the numbers |
| `EnchantData` | 280 | 243 | 104 | Equipment box (two columns), blacksmith, sealbooks | **[done]** 142 names with figure (99 from this game's guide, 43 from the first game's), 37 already had one, 101 have none in any guide. Not seen |
| `ItemData` | 576 | 609 | 41 | Item box, battle bar, shops | **[done]** 9 restoratives. **[open]** 32 other vague texts; about 150 items carry effect pairs of types that are not decoded |
| `EnemyAttackData` | 2,375 | 2,521 | 693 | "View the details of your teammates' abilities" (summons); enemy info | **[done]** 858 data lines with the exact ailment chance, prose untouched. Open items below (2.4) |
| `WeaponRankData` | 12 | names | 0 | Equipment title bar | **[seen]** `Speed C (2.00x)` |
| `EquipmentData` | 551 | 584 | 22 | Equipment box | Kept as written: the game already draws type, hands, range, speed, stat change and enchants. **[open]** read the 22 vague texts; stats at `0x24-0x58` not decoded |
| `SealScrollData` | 374 | 374 | 0 | Sealbook list | **[open]** not decoded. Writer exact for 339 of 374 |
| `JoinSkillData` | 52 | 56 | 10 | Joint skill menu, battle | **[open]** not decoded ("Inflict a powerful physical attack on one enemy. Inflicts slow."). Writer exact for 51 of 52 |
| `PartySkillData` | 20 | 24 | 0 | Party skill list | **[open]** not decoded ("Max TP and fire resistance increased." with no amount). Writer exact for 0 of 20 |
| `FoodMenuData` | 16 | 16 | 8 | Ice cream and ramen shops | **[open]** ("Heal a little HP."). Effect pairs read but their meaning is inferred; no duration found. Writer exact for 10 of 16 |
| `ClassData` | 49 | 32 | 6 | Class change screen | **[open]** not decoded. Prose only; decide whether any data belongs here |
| `QuestData` | 471 | 49 | 0 | Quest desk | **[open]** 49 reward lines ("Ring +8 that raises all stats by 3"): check each against the item it gives |
| `QuestRankData` | 20 | 15 | 0 | Quest rank messages | **[open]** 8 lines with figures to check against the reward fields |
| `TrophyData` | 50 | 42 | 0 | Trophy list | **[open]** 5 lines with figures to check |
| `IntroductionData` | 21 | 23 | 4 | Character introductions | Prose. **[open]** read once; no data expected |
| `CommandData` | 364 | 111 | 0 | Battle and field messages | **[open]** read once; 1 line with a figure |
| `StringData` | 636 | 423 | 6 | UI labels and battle messages | **[open]** 21 lines with figures to check |
| `Lesson` (script) | 65 | 763 | 63 | Euthys' lessons | **[open]** 24 lines state figures or rules: each must match the binary |
| `Teaching` (script) | 25 | 166 | 16 | Tutorials | **[open]** 16 lines with figures: each must match the binary |
| `ShopStore`, `ShopQuest`, `ShopBlacksmith`, `ShopBar` (scripts) | 50, 61, 15, 31 | 357 | 37 | Shop dialogue | **[open]** 16 lines with figures (prices, rules) to check |
| `TrapData` | 12 | names | 0 | "You triggered a %name trap!" | **[open]** each has an effect id and a rate at `0x14`; decide whether the name should carry it |

### 2.2 Packs without text, and packs not backed up

| Pack | Entries | Note |
|---|---|---|
| `CharacterData`, `ClassLevelData`, `LvExpSkptData`, `EffectSequenceData`, `WeaponEffectSequenceData`, `TreasureBoxData`, `ShopVoiceData`, `KeyHelpData`, `SEV` (Parameter) | 250, 38, 99, 680, 22, 26, 11, 111, 226 | No prose. Nothing to show; they are sources of facts (stat growth, EXP, SP) for texts elsewhere. `ClassLevelData` (38 entries of 3,172 bytes) is not decoded |
| `Script/ShopCostume`, `ShopDarkPeddler`, `ShopIce`, `ShopPeddler`, `ShopRamen` | 15, 5, 10, 10, 10 | **[open]** Dialogue. No backup exists: back them up before anything else |
| `Script/Battle`, `Item0885`, `evt00`, `evt02`, `evt99`, `Script/SEV` | 1, 2, 1, 10, 0, 226 | **[open]** Story and event scripts (`SEV` 804 KB, `evt02` 608 KB). No backup. Read for figures only; story text is not to be touched |
| `UI.pck`, `Font1.pck`, `Font2.pck`, `CG_EN.pck` | | Images and fonts. Out of scope. The font has no tilde `~` |

### 2.3 Skills: what is left

Built: 267 of 330 boxes carry data (246 with every vanilla phrase resolved, 21 partly), 48 internal entries skipped, 15 unchanged.

| Open item | Size | What closes it |
|---|---|---|
| Damage word missing | 24 skills | They carry effects that are not understood: ids 31, 47, 69, 70, 71, 72, 73, 79, 87, 88, 90, 93, 94, 95, 96, 99, 110, 111, 125, 133, 136, 146, 147, 168. Example: Spiral Arrow is ATK 88% with effect 73 at 3.3 to 4.0, so "negligible" would be false. Decode each id (compare skills that share it, test in game), then add it to `SAFE_EFFECTS` or to the damage formula |
| Sentence too long for its word or chance | 5 skills | Frost Slash, Shock Spiral, Rose Queen, Mad Zapper (chance left out), Megaton Press (damage word left out). Needs the real width of the battle bar (section 3), or a hand edit |
| Two ailments with different chances | 1 skill | Absolute Obedience (silence 25-37%, paralysis 20-32%). Hand edit |
| Vanilla phrases not tied to a table | 23 skills | Listed in `Phrases_Kept_As_Vanilla` |
| Per-level tables that no phrase explains | 50 tables of 31 skills | Listed in `Tables_Not_Shown`. Same effect ids as the first row |
| Speed or chant left out for lack of room | 72 boxes | By design (rule B). Review on screen whether a third line reads well |
| Line 1 of buffs, heals and passives | not graded | Only damage and ailment chance are graded today. Decide whether "Raise the party's ATK." should say how much |
| Summon skills | 6 skills | "Summon Spartan for short-range bash damage." holds no data; the data is in "Spartan's Action" |

### 2.4 Enemy attacks: what is left

| Open item | Size | What closes it |
|---|---|---|
| Ailment chance that cannot be written plainly | 14 attacks | 7 have no data line (familiars, Oracles' Action); 3 store a chance above 100% (Homicide Ray 200%, Wide Range Hypnotism 9900%); 4 store 0% |
| Power (`0x44`, a float) | 2,375 | Meaning inferred, not shown. Confirm against a damage test, then add `Power: 0.9x` to the data line |
| Other effects | more than 40 ids | Stat changes (161, 162, 163, 166, 167, 168), HP/TP absorb (75, 76), dispel (74), hit count and the rest. Only the 9 ailments are shown |
| Where enemy attacks are shown | | Seen for summons. Confirm the enemy info screen uses the same text |

---

## 3. Screens to look at (D5)

The install puts the build in the game after every run. One screenshot of each closes the row.

| Screen | Seen | What to confirm |
|---|---|---|
| Skill menu box | Yes (Provoke) | Three lines render; nothing drawn over lines 2-3. The title bar already shows `Lv 2 TP Cost 2` |
| Equipment title bar | Yes (Dungeon Prez Rod) | `Speed C (1.75x)` fits. Now reads `(2.00x)`: original value |
| Summon ability box | Yes, before the fix (Cupid, Poison Shot) | Now `... / Range: Long / Poison: 30%`; that the longer data line fits |
| Battle bar, skill highlighted | No | New line 1 (`Deal minor bash damage to one enemy. May stun (30%+).`); how many characters fit before it is cut |
| Battle bar, item highlighted | No | `Restore an ally's HP (+250).` |
| Item box in the menu and in a shop | No | Same text; whether the box draws anything of its own |
| Equipment box with two or more enchants | No | `Water resistance -20%`, `Enmity -5%`; the longest name (40 characters) in a column |
| Passive and unique skill boxes | No | `Lv1-9: ... \| Crown EX: ...` |
| Status screen | No | How the game itself writes resistance (with or without %) |
| Sealbook and grand sealbook lists | No | Which enchant names appear and whether long ones are cut |
| Enemy info (with an item that shows enemy abilities) | No | Whether it uses the enemy attack text |
| A tutorial and a lesson | No | Baseline before any dialogue is touched |

---

## 4. Order of work

Each step ends with a build that passes, an install, and a look at the screen.

1. **Close what is installed.** Screens of section 3 for skills, items, enchants and summon abilities. Fix what they show. Blocks nothing else, costs the user a few screenshots.
2. **Back up the 11 packs that have no backup** (shop and event scripts), and add them to the round-trip test. Until then the install cannot guarantee their state.
3. **Decode the 24 effect ids** that hold back 24 damage words and 50 hidden tables. One id at a time: list the skills and enemy attacks that share it, read their vanilla text, test one in the game. Each id decoded improves skills and enemy attacks at once.
4. **Enemy attacks, second pass**: power and the stat-change effects on the data line.
5. **One pack at a time, smallest first**: `FoodMenuData` (16), `PartySkillData` (20), `JoinSkillData` (52), `TrapData` (12), `ClassData` (49), `SealScrollData` (374), then the 32 vague item texts. For each: decode the layout, make the writer exact, add a sheet to the source of truth, write the generator and its workbook, add the build check and the tests, install, look.
6. **Texts that state rules**: `Lesson` (24 lines), `Teaching` (16), shops (16), `StringData` (21), `QuestData` (49), `QuestRankData` (8), `TrophyData` (5). Every figure they give is compared with the binary. A line is changed only if it is false or vague; its voice stays.
7. **Enchant figures without a source**: 43 from the first game to confirm and 101 with none. They are computed in the executable: read that code, or measure in the game.
8. **Release**: package per variant, player README (what changes, how to undo), full play-through of the first dungeon with the mod, removal of the earlier build's tools and tables from the repository.

---

## 5. Decisions waiting for the user

| # | Question | Default applied until answered |
|---|---|---|
| 1 | Chance that rises a lot is written as a range, `May poison (20-50%)`. A word was the other option. | Range |
| 2 | `~30%+` cannot be shown: the font has no `~`. | `30%+` |
| 3 | Beyond the damage scale the text uses `tremendous`, the word the game already uses for exactly those five spells, instead of `ultimate`. | `tremendous` |
| 4 | Magic uses the same five words with its own bounds (below 80, 80-249, 250-399, 400-499, 500-699, then tremendous). Fireball and its row version are both `moderate`; the all-enemy spells are `severe`. | As listed |
| 5 | Should buffs, heals and passives get a word or a figure in line 1 too? | Not graded |
| 6 | Enemy attack data goes on the game's own data line (`Target / Type / Range / Poison: 30%`) so that no joke is rewritten. | As built |
| 7 | Resistance is written with `%`. It is inferred from the 0-100 scale; the status screen will confirm. | With `%` |

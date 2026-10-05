# QoL roadmap: what must be true before QoL is called finished

State on 2026-10-04, after steps 2, 3, 4 and 5 of section 4. Every number here was read from the files in `mod_project/backups/` or from the output of `build_variant.py qol`; nothing is estimated. Balance is out of scope until this list is closed.

Tags: **[done]** built, verified by the build and installed. **[seen]** also looked at on screen by the user. **[open]** not started or not finished. **[blocked]** needs something that is not known yet.

---

## 1. Definition of finished

QoL is finished when all ten hold. Each one is checked by a tool or by a look at the screen, never by opinion.

| # | Condition | How it is proven | Today |
|---|---|---|---|
| D1 | Every pack whose text reaches a screen has a decision: improved, or kept as written with the reason. | Table of section 2 has no row marked open. | 11 packs built, 4 kept as written with a reason. All 47 packs of `Parameter/` and `Script/` have a backup |
| D2 | Every figure on screen is the value in the binary. Where the binary has none, it comes from a guide of this game and says so. | `build_variant.py` stops otherwise. | Checked on every build: 773 figures of skill boxes, 115 damage words and chances of line 1, 566 pieces of item data, 13 meal amounts, 1,837 figures of enemy attacks, 36 values of joint skills, 12 rank labels. From guides: 142 enchant figures, 28 bounds of party skills, 1 activation rate (Arcane Shield) |
| D3 | No game value differs from the original. | Numeric part of every built entry compared with the backup. | Holds for the 3,661 entries of the 11 built packs |
| D4 | Jokes, prose and the game's own words are intact. Data is added next to them. Prose changes only where the data contradicts it, or where a sentence had to be shortened to fit its line. | Build check per pack. | 11 corrections of enemy attack prose; 201 item sentences, 44 skill sentences and 35 joint skill sentences worded by hand to fit the battle bar (sheets of `data_tables/qol_rules.xlsx`), nothing else |
| D5 | Every kind of box has been seen on screen after the install, by the user. | Section 3. | 12 of 13 kinds of screen seen |
| D6 | Every pack the build writes has a writer that reproduces the original byte for byte. | Round-trip test. | 11 packs exact. No inexact writer is left (`SealScrollHelper` fixed too) |
| D7 | Tests pass and the docs describe what is there. | `python -m unittest discover -s mod_project/tests -p "test_*.py"` | 112 tests pass |
| D8 | Nothing that reaches the screen is written in the tools: every wording, label, scale and guide figure is in a workbook. | `data_tables/qol_rules.xlsx` and the `qol_*_text.xlsx` workbooks; a test holds it for the shortened sentences. | 15 rule sheets. Still in code: the regular expressions that recognise the game's phrases, and the layout offsets |
| D9 | Every line fits the place that draws it, measured on screen: battle bar 70 characters (line 1 of techniques and spells, joint skills, items), party skill box 50, skill and item boxes 85. | The build stops on a longer modified line; tests hold each limit. | Holds for every modified line. 20 item texts and 14 internal skill entries of the original game are longer than 70 and were not touched (no data to add; see 2.6) |
| D10 | **Hard rule: nothing shown in the game speaks from outside it.** No source, caveat or note to the reader on screen ("player guide", "the game data holds no figure"). | `check_game_voice` in the build: sheet `OutOfGameWords` of `qol_rules.xlsx`; a test holds it. | Holds for the 2,324 modified texts |

---

## 2. Every pack, one by one

### 2.1 Packs with text, backed up (27)

"Vague" counts strings that contain words such as may, chance, slightly, small, medium, large, UP or DOWN: places where the game hints at a value without giving it. It is a search, not a judgement; it sizes the work.

| Pack | Entries | Text | Vague | Where the player sees it | State |
|---|---|---|---|---|---|
| `TechniqueSkillData` | 143 | 272 | 80 | Skill menu box, battle bar | **[seen]** box and battle bar. Open items below (2.3) |
| `MagicSkillData` | 98 | 188 | 89 | Skill menu box, battle bar | **[seen]** battle bar. Open items below (2.3) |
| `PassiveSkillData` | 71 | 123 | 43 | Skill menu box | **[done]** 62 boxes with data; line 1 of 60 says how much. Not seen |
| `UniqueSkillData` | 18 | 21 | 4 | Skill menu box | **[seen]** (Shadow Heart, Arcane Shield). 18 with Lv1-9 and Crown EX. Arcane Shield stores the reflected share and not how often it triggers: a third line gives the rate the DT2-2 wiki measured, in the voice of the game (`Activation rate: about 15%`); the source is in the workbook. **[open]** the line does not say what its numbers measure (Shadow Heart `4% -> ... 12%`) |
| `EnchantData` | 280 | 243 | 104 | Equipment box (two columns), blacksmith, sealbooks | **[seen]** in the equipment box. 142 names with figure (99 from this game's guide, 43 from the first game's), 37 already had one, 101 have none in any guide |
| `ItemData` | 576 | 609 | 41 | Item box, battle bar, shops | **[seen]** in the item box. 391 items state what they do, in one line of at most 70 characters (the battle bar): 190 as original sentence + (data), 201 with the sentence shortened to fit. **[open]** 55 carry an effect that is not decoded (2.6) |
| `EnemyAttackData` | 2,375 | 2,521 | 693 | "View the details of your teammates' abilities" (summons); enemy info | **[seen]** for a summon. 1,456 entries with exact data on the data line; 11 corrections of the prose. Open items below (2.4) |
| `WeaponRankData` | 12 | names | 0 | Equipment title bar | **[seen]** `Speed E+ (2.45x)` |
| `CommandData` | 364 | 317 names | 0 | Battle messages ("Critical rate increased!") | It is the game's own table of effects: one entry per effect id with its name (2.5). Nothing to rewrite; it is a source |
| `EquipmentData` | 551 | 584 | 22 | Equipment box | Kept as written: the game already draws type, hands, range, speed, stat change and enchants. **[open]** read the 22 vague texts; stats at `0x24-0x58` not decoded |
| `SealScrollData` | 374 | 374 | 0 | Sealbook list | Kept as written. The text is one generic sentence (`Sealbook created from monsters' spirits. (Level 11).`, already with its level); what a sealbook does is its 1-4 enchantments, which the entry holds as ids of `EnchantData`. **[seen]** the list draws their names with the figures (`DEX +10%`, `Speed +5%`). Layout decoded, writer exact |
| `JoinSkillData` | 52 | 56 | 10 | Joint skill menu, battle | **[done]** 35 sentences reworded: 29 state the stored value of the effect they speak of (`85% chance of instakill.`) and 6 were only shortened; all fit the 70 characters of the battle bar. Layout decoded, writer exact. **[open]** the cost (share of max TP, Pep) and the power are decoded and not shown: see 2.7. Not seen |
| `PartySkillData` | 20 | 24 | 0 | Party skill list | **[seen]** 19 effect lines carry the bound of each bonus within the 50 characters of their box (`Slash resistance increased (up to +25%).`, `Up to wind resistance +20% and AGI +10.`); the screen shows the award count itself. Celebrities has no figure in any guide. Writer exact |
| `FoodMenuData` | 16 | 16 | 8 | Ice cream and ramen shops | **[done]** 11 effect lines with the stored amount (`Heal 30% HP and 20% TP.`); flavour lines untouched; writer exact. **[open]** the level of the buff a meal gives ("gain Sun Veil") is not decoded. Not seen |
| `ClassData` | 49 | 32 | 6 | Class change screen | Kept as written. Each text is three full lines of prose about the role of the class; it states no figure and has no room for one. The 6 vague hits are words of that prose ("may", "occasionally") |
| `QuestData` | 471 | 49 | 0 | Quest desk | **[open]** 49 reward lines ("Ring +8 that raises all stats by 3"): check each against the item it gives |
| `QuestRankData` | 20 | 15 | 0 | Quest rank messages | **[open]** 8 lines with figures to check against the reward fields |
| `TrophyData` | 50 | 42 | 0 | Trophy list | **[open]** 5 lines with figures to check |
| `IntroductionData` | 21 | 23 | 4 | Character introductions | Prose. **[open]** read once; no data expected |
| `StringData` | 636 | 423 | 6 | UI labels and battle messages | **[open]** 21 lines with figures to check |
| `Lesson` (script) | 65 | 763 | 63 | Euthys' lessons | **[open]** 24 lines state figures or rules: each must match the binary |
| `Teaching` (script) | 25 | 166 | 16 | Tutorials | **[open]** 16 lines with figures: each must match the binary |
| `ShopStore`, `ShopQuest`, `ShopBlacksmith`, `ShopBar` (scripts) | 50, 61, 15, 31 | 357 | 37 | Shop dialogue | **[open]** 16 lines with figures (prices, rules) to check |
| `TrapData` | 12 | names | 0 | "You triggered a %name trap!" | Kept as written. The name is shown inside that message, after the trap has gone off, when there is nothing left to decide. Decoded for the record: `0x10` ailment effect (113-122, or none), `0x14` rate (gas 0.33, petrification 0.5, slow 0.25) |

### 2.2 Packs without text, and the scripts backed up on 2026-10-04

| Pack | Entries | Note |
|---|---|---|
| `CharacterData`, `ClassLevelData`, `LvExpSkptData`, `EffectSequenceData`, `WeaponEffectSequenceData`, `TreasureBoxData`, `ShopVoiceData`, `KeyHelpData`, `SEV` (Parameter) | 250, 38, 99, 680, 22, 26, 11, 111, 226 | No prose. Nothing to show; they are sources of facts (stat growth, EXP, SP) for texts elsewhere. `ClassLevelData` (38 entries of 3,172 bytes) is not decoded |
| `Script/ShopCostume`, `ShopDarkPeddler`, `ShopIce`, `ShopPeddler`, `ShopRamen` | 15, 5, 10, 10, 10 | **[open]** Dialogue. Backed up in `backups/Script/`; not read yet |
| `Script/Battle`, `Item0885`, `evt00`, `evt02`, `evt99`, `Script/SEV` | 1, 2, 1, 10, 0, 226 | **[open]** Story and event scripts (`SEV` 804 KB, `evt02` 608 KB). Backed up in `backups/Script/`. Read for figures only; story text is not to be touched |
| `UI.pck`, `Font1.pck`, `Font2.pck`, `CG_EN.pck` | | Images and fonts. Out of scope. The font has no tilde `~` |

### 2.3 Skills: what is left

Built: 269 of 330 boxes carry data (261 with every vanilla phrase resolved, 8 partly), 48 internal entries skipped, 13 unchanged. A value that is the same at every level is shown too (`Speed decrease: 10%`). Line 1 of techniques and spells carries a damage word and the chance of its ailments and nothing else: it does not repeat the values of the box below (the user: "es solo bloat"), and it fits the 70 characters of the battle bar; 44 sentences were reworded by hand for that (sheet `ShortSkills`).

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
| Shortened sentences to review | 201 items | Sheet `ShortItems` of `data_tables/qol_rules.xlsx`. Each keeps the joke and drops filler so that sentence + (data) fits the 70 characters of the battle bar ("Legendary. Eat it and fall in love."). Worth a read by the user |
| Effect not decoded | 55 items | Items that cast a spell (types 46-51, 90-106), act on a kind of enemy (59, 61) or do something rare (27 and 29, two speed effects the wiki does not tell apart; 54-56, 60, 69, 88, 89). The other types were decoded with the item list of the DT2-2 wiki |
| Effect on an enemy | partly | An item made only of harmful effects shows its figures for an enemy (`25% stun`). A food that also works on enemies shows the ally's side only |
| Light items | 4 items | Steps are written as stored value x 5 (Flashlight stores 10; the wiki measures 50 steps; the ratio holds for the 4 items). Inferred from the guide |
| Original texts longer than 70 | 20 items | Key items and items without decoded data (Octo-pot, Siren Wing, Cat Bell...). Untouched: nothing is added to them. If any is usable in battle its line runs past the bar, as in the original game |


### 2.7 Party and joint skills: what is left

`PartySkillData` holds who must be in the party (`0x20` count, `0x24` ids, `0x48` how many are needed) and the id of its effect (`0x4C`), and no amount. The bounds come from the DT2-2 wiki (pages/72.html) with the rule the game states itself ("Party skills grow stronger the more Awards you obtain"): the bonus reaches its bound with all 50 awards and half of it with 25.

`JoinSkillData` (header `0x98`): `0x18` participants, `0x28` Pep needed, `0x2C` Pep spent, `0x40` power, `0x44` turns of the effect, `0x48` delay, `0x4C` TP divisor, `0x50` effect count, four `(id, value, tail)` slots from `0x54`. The TP divisor agrees with the wiki for every skill it lists (Rush Zanber 1/7, Jackpot 1/1): each participant pays that share of her max TP.

| Open item | Size | What closes it |
|---|---|---|
| Cost of a joint skill not shown | 52 | The share of max TP is exact and the sentences have no room for it (up to 84 characters). A screenshot of the joint skill menu tells whether the game draws the cost itself; if not, the sentences are shortened to make room |
| Pep needed and spent | 52 | Read as such by comparison with the wiki's words ("high", "very high"; "small", "large"); not confirmed by a test, so not shown |
| Power (`0x40`) | 38 attacks | Same field as the power of enemy attacks: inferred, not shown, no damage word |
| Effects named by the game table only | 5 skills | Magical Treasure (68, drop rate 75: unit not known), Sleep with the Fishes (143), Todokanai Koi (121), Hell Raiser (141), Crazy Rush and Magical Assault (72 with 0.5 and 0.8): kept as written |
| Celebrities | 1 | No guide gives the bound of its lightning resistance |
---

## 3. Screens to look at (D5)

The install puts the build in the game after every run. One screenshot of each closes the row.

| Screen | Seen | What it showed, or what to confirm |
|---|---|---|
| Skill menu box | Yes (Provoke; Ice Storm and Self-Sacrifice in the skill learning screen) | Three lines render; nothing drawn over lines 2-3. The title bar shows `Lv 2 TP Cost 2`. Ice Storm: line 3 of 78 characters whole. Self-Sacrifice showed the same range in line 1 and in line 2: line 1 no longer repeats values |
| Equipment title bar | Yes | `Firewhorling Claymore of Ability+4 [Sword - 2 Hand - Short Range] Speed E+ (2.45x)` fits (83 characters) |
| Equipment box with two enchants | Yes | `Fire magic +20%` and `Physical accuracy MiniUP` in two columns; the description stays on line 1 |
| Status screen | Yes | The game writes resistance as a plain number and abbreviates: `Fi Res 0`, `Bs Res -20`. The enchant names say `Bash resistance -20%` (decision 2 of section 5) |
| Summon ability box | Yes (Cupid, Poison Shot; Eros, Bra Unhooker) | `Target: Single / Type: Neutral / Range: Short / DEF/Magic defense: -15%`, prose below, intact |
| Battle bar, skill highlighted | Yes (Freeze Shot, Circle Brave, Self-Sacrifice) | `Bow skill. Deal moderate stab damage to one enemy. May freeze (20-50%).` is drawn whole: 71 characters, a little wider than the purple band (about 68). `Distribute all of one's TP to the target (TP transfer bonus 100-140%).` (70) also whole. The skill list beside it shows the TP cost of the current level |
| Battle bar, item highlighted | Yes, before the item data | One centred line. To confirm: `Old-fashioned rice cracker covered in soy sauce. (HP +75)` |
| Item box in the menu | Yes (Kuding Tea) | `Tea with condensed bitterness. I hear it's an acquired taste... (HP +30, TP +40)` drawn whole on one line (79 characters); lines 2-3 of the box stay empty |
| Passive and unique skill boxes | Unique yes (Shadow Heart, Arcane Shield) | `Lv1-9: 50% -> 55 -> ... -> 100% \| Crown EX: 200%` whole. Passive box not seen |
| Sealbook creation list | Yes (Pirate) | The game draws the generic sentence and, below it, the enchant names in two columns: `DEX +10%`, `Speed +5%`. So the figures of `EnchantData` reach the sealbooks and `SealScrollData` needs no text. Grand sealbooks not seen |
| Enemy info (with an item that shows enemy abilities) | No | Whether it uses the enemy attack text |
| Party skill list | Yes (Veteran Soldiers) | A line of 53 characters ran over the frame; the limit is now 50. The screen shows `Award Count`. Joint skill menu not seen: whether it shows the TP and Pep cost |
| A tutorial and a lesson | Yes (lesson) | Dialogue box of two lines, about 60 characters each. Baseline before any dialogue is touched |

---

## 4. Order of work

Each step ends with a build that passes, an install, and a look at the screen.

1. **Close what is installed.** Screens of section 3. 12 of 13 seen; missing: enemy info, and of the seen kinds the passive box and the joint skill menu.
2. **[done] Back up the 11 packs that had no backup.** They are in `backups/Script/`. All 47 archives rebuild byte for byte, the round-trip test covers them, and the install checks 47 files.
3. **[done, with a remainder] Decode the effect ids.** 69 ids with evidence, and the game's own name for 317 (`CommandData`). Remainder: how effect 73 combines with the power table (one damage test), and the summon parameters 228-233.
4. **[done] Enemy attacks, second pass.** Exact effects on the data line of 1,456 entries; 11 corrections of the prose. Remainder in 2.4.
5. **[done, with a remainder] One pack at a time, smallest first.** Items (391), meals (16), party skills (20) and joint skills (52) built; traps, classes and sealbooks kept as written, each with its reason in 2.1. Remainder: 55 items (2.6), the cost of joint skills (2.7).
6. **Texts that state rules**: `Lesson` (24 lines), `Teaching` (16), shops (16), `StringData` (21), `QuestData` (49), `QuestRankData` (8), `TrophyData` (5). Every figure they give is compared with the binary. A line is changed only if it is false or vague; its voice stays.
7. **Enchant figures without a source**: 43 from the first game to confirm and 101 with none. They are computed in the executable: read that code, or measure in the game.
8. **Release**: package per variant, player README (what changes, how to undo), full play-through of the first dungeon with the mod, removal of the earlier build's tools and tables from the repository.

---

## 5. Decisions

Answered by the user on 2026-10-04 and applied:

| Question | Answer |
|---|---|
| Values that do not change with the level | Always shown |
| Buffs, heals and passives in line 1 | Superseded (see below): line 1 does not repeat values; the box has each one |
| A chance of 100% | Written as `100%` |
| Bounds of the magic scale | Confirmed |
| Text and data disagree | The data wins; keep as much of the original sentence as possible |
| Items | Original text + (data), always one line; where it does not fit, the original is made shorter |
| Skills whose line 1 did not fit | The original is made shorter so that it fits |
| Spiral Arrow and Holy Gavel | Look in the Japanese guides: the wiki lists the multiplier as ATK%, so both are graded by it |
| Tables written in the tools (`shortened_text.py`) | Nothing hardcoded: everything in a workbook, for quick editing. Done as `data_tables/qol_rules.xlsx` |
| Values in line 1 of a skill (`(TP transfer bonus 100-140%)`) | Removed: the box below has them, in line 1 they are bloat. This replaces the earlier answer on buffs, heals and passives |
| Width of the battle bar | The Self-Sacrifice line (70 characters) is the most that fits well; anything longer is rewritten |
| Party skill box | Limit is the line that overflowed minus 3 (50), held by a test |
| Arcane Shield says "occasionally" and shows only the reflected share | The rate is not in the game data; the guide's figure is shown. It was first written with its source on screen: the user called that horrible. Never again: see D10 |

Still open:

| # | Question | Default applied until answered |
|---|---|---|
| 2 | The status screen writes resistance without `%` and abbreviated (`Bs Res -20`); the enchant names and skill boxes say `Bash resistance -20%`. Keep the `%`? | With `%`, as asked |
| 3 | Beyond the damage scale the text uses `tremendous`, the game's own word for exactly those five spells. `ultimate` was the other option. | `tremendous` |

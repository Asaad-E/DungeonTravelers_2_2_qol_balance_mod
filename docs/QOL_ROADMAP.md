# QoL roadmap: what must be true before QoL is called finished

**QoL is closed.** State on 2026-10-04: the user accepted the variant; every step of section 4 that can be done without the executable is done, and what stays unknown is listed in section 6 and carried over to the Balance work. Every number here was read from the files in `backups/` or from the output of `build_variant.py qol`; nothing is estimated.

Tags: **[done]** built, verified by the build and installed. **[seen]** also looked at on screen by the user. **[open]** not started or not finished. **[blocked]** needs something that is not known yet.

---

## 1. Definition of finished

QoL is finished when all ten hold. Each one is checked by a tool or by a look at the screen, never by opinion.

| # | Condition | How it is proven | Today |
|---|---|---|---|
| D1 | Every pack whose text reaches a screen has a decision: improved, or kept as written with the reason. | Table of section 2 has no row marked open. | 12 packs built (11 of `Parameter/`, `Teaching`), the rest kept as written with a reason. Story scripts were not read (2.2) |
| D2 | Every figure on screen is the value in the binary. Where the binary has none, it comes from a guide of this game. | `build_variant.py` stops otherwise. | Checked on every build: 773 figures of skill boxes, 115 damage words and chances of line 1, 604 pieces of item data, 13 meal amounts, 1,837 figures of enemy attacks, 36 values of joint skills, 12 rank labels. From guides: 142 enchant figures, 28 bounds of party skills, 1 activation rate (Arcane Shield) |
| D3 | No game value differs from the original. | Numeric part of every built entry compared with the backup; script packs differ only in the corrected sentence, same length. | Holds for the 3,661 entries of the 11 built packs and for `Teaching` |
| D4 | Jokes, prose and the game's own words are intact. Data is added next to them. Prose changes only where the data contradicts it, or where a sentence had to be shortened to fit its line. | Build check per pack. | 11 corrections of enemy attack prose, 1 of a tutorial; 221 item sentences, 44 skill sentences and 35 joint skill sentences worded by hand to fit the battle bar (sheets of `data_tables/qol_rules.xlsx`), nothing else |
| D5 | Every kind of box has been seen on screen after the install, by the user. | Section 3. | 13 of 14 kinds of screen seen; the joint skill menu is missing |
| D6 | Every pack the build writes has a writer that reproduces the original byte for byte. | Round-trip test. | 11 packs exact; scripts are patched in place without a writer. No inexact writer is left |
| D7 | Tests pass and the docs describe what is there. | `python -m unittest discover -s tests -p "test_*.py"` | 118 tests pass |
| D8 | Nothing that reaches the screen is written in the tools: every wording, label, scale and guide figure is in a workbook. | `data_tables/qol_rules.xlsx` and the `qol_*_text.xlsx` workbooks; a test holds it for the shortened sentences. | 19 rule sheets. Still in code: the regular expressions that recognise the game's phrases, and the layout offsets |
| D9 | Every line fits the place that draws it, measured on screen: battle bar 70 characters (line 1 of techniques and spells, joint skills, items), party skill box 50, skill and item boxes 85. | The build stops on a longer modified line; tests hold each limit. | Holds for every modified line. 20 item texts and 14 internal skill entries of the original game are longer than 70 and were not touched (no data to add; see 2.6) |
| D10 | **Hard rule: nothing shown in the game speaks from outside it.** No source, caveat or note to the reader on screen ("player guide", "the game data holds no figure"). | `check_game_voice` in the build: sheet `OutOfGameWords` of `qol_rules.xlsx`; a test holds it. | Holds for the 2,358 modified texts |

---

## 2. Every pack, one by one

### 2.1 Packs with text, backed up (27)

"Vague" counts strings that contain words such as may, chance, slightly, small, medium, large, UP or DOWN: places where the game hints at a value without giving it. It is a search, not a judgement; it sizes the work.

| Pack | Entries | Text | Vague | Where the player sees it | State |
|---|---|---|---|---|---|
| `TechniqueSkillData` | 143 | 272 | 80 | Skill menu box, battle bar | **[seen]** box and battle bar. Provoke and Attract show the enmity they draw (`Enmity: 250`, `Enmity: 150`: the stored value; its unit is not known). Open items below (2.3) |
| `MagicSkillData` | 98 | 188 | 89 | Skill menu box, battle bar | **[seen]** battle bar. Open items below (2.3) |
| `PassiveSkillData` | 71 | 123 | 43 | Skill menu box | **[seen]** (Sword Mastery: `ATK bonus: 3% -> 5 -> ... -> 15% (L10)`). 62 boxes with data; line 1 is the game's sentence |
| `UniqueSkillData` | 18 | 21 | 4 | Skill menu box | **[seen]** (Shadow Heart, Arcane Shield). 18 with the values of levels 1-9 and of the Crown. 13 say what the numbers measure (`Activation rate: 7% -> ...`, `Reflected: 50% -> ...`, sheet `UniqueSkillLabels`); Shadow Heart, Positive Trance, Undaunted Spirit, Yearning and Demon Wall keep `Lv1-9` (not known, or no room). Arcane Shield has a third line, `Activation rate: 15%`, from the DT2-2 wiki |
| `EnchantData` | 280 | 243 | 104 | Equipment box (two columns), blacksmith, sealbooks | **[seen]** in the equipment box and on sealbooks. 142 names with figure (99 from this game's guide, 43 from the first game's), 37 already had one, 101 have none in any guide. Resistances without `%` (`Fire resistance +20`) |
| `ItemData` | 576 | 609 | 41 | Item box, battle bar, shops | **[seen]** in the item box. 425 items state what they do, in one line of at most 70 characters (the battle bar): 204 as original sentence + (data), 221 with the sentence shortened to fit. 21 carry an effect that is not decoded (2.6) |
| `EnemyAttackData` | 2,375 | 2,521 | 693 | "View the details of your teammates' abilities" (summons); enemy info | **[seen]** for a summon. 1,456 entries with exact data on the data line; 11 corrections of the prose. Open items below (2.4) |
| `WeaponRankData` | 12 | names | 0 | Equipment title bar | **[seen]** `Speed E+ (2.45x)` |
| `CommandData` | 364 | 317 names | 0 | Battle messages ("Critical rate increased!") | It is the game's own table of effects: one entry per effect id with its name (2.5). Nothing to rewrite; it is a source |
| `EquipmentData` | 551 | 584 | 22 | Equipment box | Kept as written: the game already draws type, hands, range, speed, stat change and enchants, and the enchant names carry the figures. Stats at `0x24-0x58` are not decoded |
| `SealScrollData` | 374 | 374 | 0 | Sealbook list | Kept as written. The text is one generic sentence (`Sealbook created from monsters' spirits. (Level 11).`, already with its level); what a sealbook does is its 1-4 enchantments, which the entry holds as ids of `EnchantData`. **[seen]** the list draws their names with the figures (`DEX +10%`, `Speed +5%`). Layout decoded, writer exact |
| `JoinSkillData` | 52 | 56 | 10 | Joint skill menu, battle | **[done]** 35 sentences reworded: 29 state the stored value of the effect they speak of (`85% chance of instakill.`) and 6 were only shortened; all fit the 70 characters of the battle bar. Layout decoded, writer exact. The cost (share of max TP, Pep) is decoded and not shown: see 2.7. Not seen |
| `PartySkillData` | 20 | 24 | 0 | Party skill list | **[seen]** 19 effect lines carry the bound of each bonus within the 50 characters of their box (`Slash resistance increased (up to +25%).`, `Up to wind resistance +20% and AGI +10.`); the screen shows the award count itself. Celebrities has no figure in any guide. Writer exact |
| `FoodMenuData` | 16 | 16 | 8 | Ice cream and ramen shops | **[done]** 11 effect lines with the stored amount (`Heal 30% HP and 20% TP.`); flavour lines untouched; writer exact. **[open]** the level of the buff a meal gives ("gain Sun Veil") is not decoded. Not seen |
| `ClassData` | 49 | 32 | 6 | Class change screen | Kept as written. Each text is three full lines of prose about the role of the class; it states no figure and has no room for one. The 6 vague hits are words of that prose ("may", "occasionally") |
| `QuestData` | 471 | 49 | 0 | Quest desk | Kept as written. **Checked**: the 40 reward lines that name a level (`Ring +8 that raises all stats by 3`) agree with the reward the quest stores (item `0x3C`, level `0x44`, enchantments `0x48`, `0x4C`); a test holds it |
| `QuestRankData` | 20 | 15 | 0 | Quest rank messages | Kept as written. **Checked**: every amount in the messages is the stored reward (2 medicines, 10,000 / 20,000 / 100,000 gold, bag +5, quests 6 / 7 / 8 / 10) |
| `TrophyData` | 50 | 42 | 0 | Trophy list | Kept as written. The thresholds (`Won 300 battles.`) are not in the pack (an entry is an id and two strings), so they cannot be compared; nothing vague in them |
| `IntroductionData` | 21 | 23 | 4 | Character introductions | Kept as written: prose about the characters, no data |
| `StringData` | 636 | 423 | 6 | UI labels and battle messages | Kept as written. Its figures are placeholders filled by the game (`%number0 percent`) and the fixed level of a meal's buff (`Aim Lv 10 was applied to all party members.`), which the game says itself when the meal is eaten |
| `Lesson` (script) | 65 | 763 | 63 | Euthys' lessons | Kept as written. **Checked** against the DT2-2 wiki, since these rules live in the executable: chant interruption 1/3 on a critical hit, damage 100 / 75 / 50 by distance, poison 5% of max HP, paralysis 30%, immunity at 100 resistance, a stat bonus from a level gap of 59. Nothing found wrong. Daedalus Attack "3-5 times" is the stored effect 96 |
| `Teaching` (script) | 25 | 166 | 16 | Tutorials | **[done]** one sentence corrected: the tutorial on level reset said "a gap of over 59"; the lesson and the guide say 59 or greater. Replaced in place with a sentence of the same length (sheet `ScriptFixes`). The rest agrees with the lessons |
| `ShopStore`, `ShopQuest`, `ShopBlacksmith`, `ShopBar` (scripts) | 50, 61, 15, 31 | 357 | 37 | Shop dialogue | Kept as written. **Checked**: every price and amount Rin-Rin quotes is the item's (Danish 450, Fairy Apple 50 TP for 900, Gateau Au Chocolat 100 party HP for 600, Rice Cracker 75 HP, Bagel Sandwich 500 HP); a test holds it. The blacksmith's "MiniUP requires level 1, UP level 10" could not be compared (not in a pack) |
| `TrapData` | 12 | names | 0 | "You triggered a %name trap!" | Kept as written. The name is shown inside that message, after the trap has gone off, when there is nothing left to decide. Decoded for the record: `0x10` ailment effect (113-122, or none), `0x14` rate (gas 0.33, petrification 0.5, slow 0.25) |

### 2.2 Packs without text, and the scripts backed up on 2026-10-04

| Pack | Entries | Note |
|---|---|---|
| `CharacterData`, `ClassLevelData`, `LvExpSkptData`, `EffectSequenceData`, `WeaponEffectSequenceData`, `TreasureBoxData`, `ShopVoiceData`, `KeyHelpData`, `SEV` (Parameter) | 250, 38, 99, 680, 22, 26, 11, 111, 226 | No prose. Nothing to show; they are sources of facts (stat growth, EXP, SP) for texts elsewhere. `ClassLevelData` (38 entries of 3,172 bytes) is not decoded |
| `Script/ShopCostume`, `ShopDarkPeddler`, `ShopIce`, `ShopPeddler`, `ShopRamen` | 15, 5, 10, 10, 10 | Dialogue. Searched for figures: none states a rule or a price |
| `Script/Battle`, `Item0885`, `evt00`, `evt02`, `evt99`, `Script/SEV` | 1, 2, 1, 10, 0, 226 | Story and event scripts (`SEV` 804 KB, `evt02` 608 KB). Not read: story text is not to be touched |
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
| Effect not decoded | 21 items | Types 29 (a second "speed up" the wiki does not tell apart from 27), 32, 54-56 (damage by max HP, with caps the wiki gives and the data does not), 60, 61, 89 (the wiki: lose 5% of gold; the item stores 1), 90 (Fireball; one of its two items does nothing according to the wiki). Decoded on 2026-10-04 with the wiki's item list: 27 speed up, the 12 spell types (`Fire Blast Lv2`: the stored value is the spell level), 69, 88 |
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
| Status screen | Yes | The game writes resistance as a plain number and abbreviates: `Fi Res 0`, `Bs Res -20`. The mod writes resistances the same way, without `%` |
| Summon ability box | Yes (Cupid, Poison Shot; Eros, Bra Unhooker) | `Target: Single / Type: Neutral / Range: Short / DEF/Magic defense: -15%`, prose below, intact |
| Battle bar, skill highlighted | Yes (Freeze Shot, Circle Brave, Self-Sacrifice) | `Bow skill. Deal moderate stab damage to one enemy. May freeze (20-50%).` is drawn whole: 71 characters, a little wider than the purple band (about 68). `Distribute all of one's TP to the target (TP transfer bonus 100-140%).` (70) also whole. The skill list beside it shows the TP cost of the current level |
| Battle bar, item highlighted | Yes, before the item data | One centred line. To confirm: `Old-fashioned rice cracker covered in soy sauce. (HP +75)` |
| Item box in the menu | Yes (Kuding Tea) | `Tea with condensed bitterness. I hear it's an acquired taste... (HP +30, TP +40)` drawn whole on one line (79 characters); lines 2-3 of the box stay empty |
| Passive and unique skill boxes | Yes (Sword Mastery; Shadow Heart, Arcane Shield) | `ATK bonus: 3% -> 5 -> ... -> 15% (L10)` and `Lv1-9: 50% -> ... -> 100% \| Crown EX: 200%` whole |
| Sealbook creation list | Yes (Pirate) | The game draws the generic sentence and, below it, the enchant names in two columns: `DEX +10%`, `Speed +5%`. So the figures of `EnchantData` reach the sealbooks and `SealScrollData` needs no text. Grand sealbooks not seen |
| Enemy info | Yes (Medic, Selene) | It shows habitat, drops, the sealbook with its enchant names (`Recover 2 TP every turn`) and stats; resistances as `+15`, without `%`. It does not use the enemy attack text |
| Party skill list | Yes (Veteran Soldiers) | A line of 53 characters ran over the frame; the limit is now 50. The screen shows `Award Count`. Joint skill menu not seen: whether it shows the TP and Pep cost |
| A tutorial and a lesson | Yes (lesson) | Dialogue box of two lines, about 60 characters each. Baseline before any dialogue is touched |

---

## 4. Order of work

Each step ends with a build that passes, an install, and a look at the screen.

1. **Close what is installed.** Screens of section 3: 13 of 14 seen; the joint skill menu is missing.
2. **[done] Back up the 11 packs that had no backup.** They are in `backups/Script/`. All 47 archives rebuild byte for byte, the round-trip test covers them, and the install checks 47 files.
3. **[done, with a remainder] Decode the effect ids.** 69 ids with evidence, and the game's own name for 317 (`CommandData`). Remainder: the summon parameters 228-233 and the unit of 170 (enmity).
4. **[done] Enemy attacks, second pass.** Exact effects on the data line of 1,456 entries; 11 corrections of the prose. Remainder in 2.4.
5. **[done, with a remainder] One pack at a time, smallest first.** Items (425), meals (16), party skills (20) and joint skills (52) built; traps, classes and sealbooks kept as written, each with its reason in 2.1. Remainder: 21 items (2.6), the cost of joint skills (2.7).
6. **[done] Texts that state rules.** Lessons, tutorials, shops, `StringData`, `QuestData`, `QuestRankData`, `TrophyData`: every figure that a pack holds was compared with it, the rules of the executable with the DT2-2 wiki. One sentence was false (a tutorial) and is corrected; results per pack in 2.1.
7. **[blocked] Enchant figures without a source**: 43 from the first game to confirm and 101 with none. They are computed in the executable; no guide of this game gives them. It needs reading that code or measuring in the game, neither of which was done. Until then those 43 show the first game's figure and the 101 keep the game's word (`Physical accuracy MiniUP`).
8. **[done] Release.** `python tools/package_variant.py qol` writes `dist/DT22_qol_<date>.zip`: the differences of the files the variant changes and the script that applies them to the own game of the player (`release/mod_patch.ps1`), with `release/README_QoL.txt`. No file of the game is in the archive (changed on 2026-10-12; it held the files and their originals before).

---
---

## 6. What is left

For the user:

| # | What | Where |
|---|---|---|
| 1 | Read the sentences reworded by hand: 221 items, 44 skills, 35 joint skills, 19 party skills | `data_tables/qol_rules.xlsx`: `ShortItems`, `ShortSkills`, `JointSkillSentences`, `PartySkillBounds` |
| 2 | A screenshot of the joint skill menu: does the game show the TP and Pep cost? If not, the sentences are shortened to hold the share of max TP | 2.7 |
| 3 | Nothing left to decide: resistances go without `%`, `tremendous` stays, the earlier build is deleted | section 5 |
| 4 | `Enmity: 250` on Provoke is the stored value; whether it is a percentage is not known | 2.1 |
| 5 | Play the first dungeon with the mod | step 8 |

Blocked on something that is not known:

| What | Needs |
|---|---|
| 144 enchant figures (43 unconfirmed, 101 missing) | The formula in the executable, or measurements in the game |
| 21 items, summon doll parameters, Power of enemy attacks and joint skills, Pep cost of joint skills | A damage or effect test in the game for each |
| What the number of Shadow Heart, Positive Trance, Undaunted Spirit and Yearning measures | A guide or a test |
| Celebrities (party skill): bound of its lightning resistance | A guide or a test |


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
| The tools and tables of the earlier mixed build | Deleted |
| Values in line 1 of a skill (`(TP transfer bonus 100-140%)`) | Removed: the box below has them, in line 1 they are bloat. This replaces the earlier answer on buffs, heals and passives |
| Width of the battle bar | The Self-Sacrifice line (70 characters) is the most that fits well; anything longer is rewritten |
| Party skill box | Limit is the line that overflowed minus 3 (50), held by a test |
| Arcane Shield says "occasionally" and shows only the reflected share | The rate is not in the game data; the guide's figure is shown. It was first written with its source on screen: the user called that horrible. Never again: see D10 |

Still open:

| # | Question | Default applied until answered |
|---|---|---|
| 2 | Resistances with or without `%` | **Answered: without**, as the status screen writes them |
| 3 | `tremendous` or `ultimate` beyond the damage scale | **Answered by acceptance** ("todo perfecto"): `tremendous` stays |

## Found after the QoL variant was closed (2026-10-05)

* **Doll skills.** Decoded and implemented on 2026-10-11: Spartan, Oracles, Catalina, Mercidarian, Musiy and Star Dust Arrow now display their verified hidden action power, heal power and magic power directly on their LvUp lines within engine limits (<= 85 chars, 3 lines), replacing all vague vanilla terms ("ATK UP", "Paralysis rate UP", "HP recovery UP", "Doll magic damage UP"). Verified by `text_checks.py` against child action binaries and unit tests.

## Found during Balance phase 0 (2026-10-05) and applied to the QoL build the same day

Reading the program settled things the QoL variant had left open. Applied through the rule sheets of `data_tables/qol_rules.xlsx`, built, verified and installed:

| What | On screen now | Source |
|---|---|---|
| Cover, Parry | `Cover ends per hit: 70% -> ... -> 40%`, `Parry ends per block: 80% -> ... -> 52%` (tables the game never explained) | `docs/FORMULAS.md` 12.12, sheet `EffectRules` |
| Shadow Heart, Undaunted Spirit | `Activation rate` in place of `Lv1-9` | `docs/FORMULAS.md` 12.19 |
| Positive Trance | `Pep over 100 per +1% damage: 10 -> ... -> 2` | `docs/FORMULAS.md` 2.4 |
| Yearning | `Class modifiers (%): 2 -> ... -> 10` | `docs/FORMULAS.md` 10.4 |
| Star Dust Arrow, Perdurabo, Musiy | `Turns on field` | effect 147 |
| Items of types 29, 32, 89, 90 (8 items) | `40% Accelerator`, `20% War Cry`, `lose 5% of gold`, `Fireball Lv3` | `tools/item_effect_data.py`, `docs/FORMULAS.md` 15 |
| Arcane Shield, `Activation rate: 15%` | Unchanged on screen; its source is now the program, not a guide | `docs/FORMULAS.md` 12.19 |

Second pass the same day, on the user's review:

| What | On screen now | Source |
|---|---|---|
| Demon Wall | `Taken: -12% -> ... -> -20%` ("Damage taken" is one character too long) | `docs/FORMULAS.md` 12.19 |
| Perdurabo, Musiy, Star Dust Arrow | `Duration`, the word the other dolls already used | effect 147 |
| Items of types 54, 55, 60, 61 and the ones that had no room (11 items, sentences shortened by hand in `ShortItems`) | `50% max HP damage up to 100`, `silences Apparitions`, `30% HP to Beasts`, `25% Accelerator` | `docs/FORMULAS.md` 15 |
| Power of the attacks of the player's summons (150 data lines) | `Power: +20%` | `EnemyAttackData 0x3C`, `docs/FORMULAS.md` 9.2; setting `enemy_power_scope` |

The player has 35 summons in 105 forms (`tools/summon_data.py`); together they use 413 enemy attacks, 154 with a power. Only those show it.

Third pass, on a screenshot of the Heal box sent by the user ("HP recovery?", "no air"):

* **Heals show the multiple of RES**: `Heals RES: 4x (+1x/Lv) -> 13x`. The stored figure (8 to 26) is the coefficient of `RES * about 0.5 * figure` (`docs/FORMULAS.md` 6b); half of it is what multiplies RES. Heal, Circle Heal, Primevil. Label and style in the sheet `SkillEffectLabels`.
* **Air between the items of a line**: three spaces on each side of the bar (`Turns: 3 -> 7   |   TP Cost: 1 -> 5`) whenever the widened line stays within 92 characters (settings `skill_separator_pad`, `skill_wide_line`). What a line holds is still chosen for 85. 92 is read off the screenshot (73 characters end at three quarters of the box), not measured with a full line: **to be looked at on screen**.

Fourth pass: **the level of the buff a meal gives** is decoded and shown (`gain Aim Lv10`, `gain Protect Lv5 and Accelerator Lv5`). Each meal effect type has a method that writes the level into the effect and performs the skill (`tools/item_effect_data.py`, `meal_buffs`); it is the level the game itself announces when the meal is eaten (`StringData` 183 to 196). Brave, Protect and Sun Veil are performed at the last level of their skill. Phrases in the sheet `MealBuffs`.

Known and **not shown**, each with its reason:

| What | Why not |
|---|---|
| Dark Cloud (type 56 and petrifying 0.8) | Its second value is stored on another scale than the other items of its type (0.8 against 25 or 50): which reading is right is not known |
| Power on 4 summon attacks | No room on their data line |
| Power of the other enemy attacks and of joint skills | Left alone by decision of the user |
| Cost of a joint skill | Left alone by decision of the user (2026-10-05) |
| Chances of the random moves, class modifiers, rules of vague passives | Their boxes are prose with no room for a table |

The QoL variant is closed. A text is still corrected, in both variants, when a reading of the program shows it wrong
(on 2026-10-12: the labels of four unique skills, and the box of Concentrate, which goes back to the sentence of the
game because the program gives the passive no effect; `FORMULAS.md` 2.5).

## The abilities of summons and guest allies (2026-10-12)

Asked by the user from the screen of a summon, where Covering Attack showed no chance. Every ability a summoned
monster or a guest ally can use (747 enemy attacks, shown in "View the details of your teammates' abilities") now
says its figure on its data line, with the label the box of the same skill of a party member uses: the chance of a
passive (`Activation rate`, `Double attack rate`, `Triple attack rate`, `Occurrence rate`), the power of a spell
(`Pwr`) and of a blow (`Power`), what a heal multiplies RES by, the turns of a doll, the size of a song, a dance or a
stance (`Critical rate`, `TP recovery`, `EXP`, `Resistance decrease`, `All stats`, `ATK`, `DEF`,
`Damage reduction rate`), `Power decrease`, `Damage vs. unholy`, `Targets`. The rules are rows of the sheet
`EnemyEffects` of `qol_rules.xlsx` (columns `After_Power`: written after the power, the first left out when the line is
short; `Scope`: `summons` keeps a figure to these abilities). 666 of the 747 carry added data; the 70 with no figure
at all are abilities that hold none to show (Take Break, a plain Attack, Full Heal, the steals) or whose effect has
no label yet (two dances, two songs, Limit Field, Circle Illusion). Where the line has no room the generator says so
in the column `Note` (54 attacks).

## The conditions of side events: looked at and dropped

Reopened on 2026-10-07 for one point, row S25 of the Balance register ("side events with conditions nobody can
guess"): whether the condition of each side event could be read from the data and shown somewhere in the game without
changing the program. Dropped by the user on 2026-10-12 before anything was built.

# Cross-System Validation Report: the mixed build "Definitive QoL & Balance Mod v1.0"

**Audited:** commit `28c7d90` (branch `master`), the installed game files, `mod_project/dist/DT22_Definitive_QoL_Balance_Mod_v1.0.zip`, 25 modified PCK archives, 15 Excel tables, `apply_mod.py`, `audit_tool.py`, `package_release.py`.
**Method:** read only. Every statement was checked against the installed binaries, the original backups and the zip. Nothing was run in the game by the auditor; one screenshot supplied by the user is cited where used.

This build mixes text and value changes. The project now targets two separate variants (QoL: information only; Balance: rebalance plus information); see `dungeontravelers2-2.md`. Section 9 reads the findings against each variant.

---

## 1. Verdict

| Dimension | Result |
|---|---|
| Structural integrity (archives open, Excel = binary, zip = game) | Pass |
| Cross-system synchronisation (dialogue, data, release) | **Fail** |
| Accuracy of the figures shown to the player | **Fail** |
| Persona, tone and humor | Partial |
| Format (3 lines, 85 characters, no tilde) | Partial |

**The zip is not ready for release, as either variant.** `audit_tool.py` reports 100% PASS with 0 errors, but it only measures line length in the Excel tables and that the archives open. It does not look at script dialogue, does not compare text with binary values, and does not include `WeaponRankData.pck`.

Blocking problems:

1. **11 of 47 dialogue replacements never reached the game** (Rin-Rin 2 of 2, tavern 1 of 1, Euthys 8 of 12), and the script reports success.
2. **`WeaponRankData.pck` is modified in the game folder but is not in the zip.** A zip install keeps the original delays while the library says F is 2.35x.
3. **Skill figures do not match the binary:** TP cost in 125 of 141 skills, physical power in 37 of 39, magic power in 17 of 22.
4. **Seven mechanics are announced in the text with no data change behind them.**
5. **The 200 modified skills have a string pointer past the end of their entry, and 17 lost their battle message.**
6. **All 551 equipment descriptions are overdrawn by the game's own enchantment list** (seen on screen).

---

## 2. What the build really changes

Header (non-text) bytes of every entry were compared between backup and installed file.

| Archive | Entries with a value change | Detail |
|---|---|---|
| `LvExpSkptData.pck` | 90 of 99 | EXP required for Lv 10-99; +1 SP per level at Lv 2-26 (+25 SP) |
| `WeaponRankData.pck` | 11 of 12 | Delay multipliers (A+ unchanged) |
| `ItemData.pck` | 4 | Magical Fruit, Fairy Apple, Mui Kuha Medicine, Flashlight |
| `EquipmentData.pck` | 1 | Slave's Torc: enchant 66 -> 275 |
| `QuestRankData.pck` | 5 | Ranks 2, 8, 11, 15, 20 |
| All four skill archives, `ClassData`, `EnemyAttackData`, `SealScrollData`, `JoinSkillData`, `EnchantData`, `PartySkillData`, `FoodMenuData`, `TrapData`, `TrophyData`, `StringData` | **0** | Text only |

The +25 SP are not mentioned in the zip instructions nor in any dialogue.

---

## 3. Cross-system synchronisation

### 3.1 EXP and progression: pass, with reservations

| Check | Result |
|---|---|
| `exp_curve.xlsx` = `LvExpSkptData.pck` | 99 of 99 levels (EXP and SP) |
| Required EXP strictly increasing | Yes; smallest increment +20 (Lv 2->3), +946 at Lv 98->99 |
| EXP for Lv 71-99 | 1,317,866 (vanilla 2,050,065; -35.7%) |
| Cumulative EXP to Lv 50 | 264,055 (vanilla 336,323; 78.5%) |
| Lv 1-9 | Identical to vanilla |
| Factor per level | Falls smoothly from 1.00 (Lv 9) to 0.60 (Lv 99) |

**Lv 70->99 in about 57.2 minutes.** The figure is reproduced exactly by the project's own model: 6,400 EXP per character and battle in Matrix F20-30, 50 s per battle, x2.0 (Slave's Torc), x1.5 (Dragon Papi).

| Scenario | Battles | Minutes |
|---|---|---|
| Mod + Torc + Papi | 68.6 | 57.2 |
| Mod + Torc only | 103.0 | 85.8 |
| Mod, no gear | 205.9 | 171.6 |
| Vanilla, no gear | 320.3 | 266.9 |

* The 6,400 EXP and the 50 s are assumptions; no enemy data is available to check them.
* Dragon Papi's bonus applies only against higher-level enemies (enchant 270). The model applies it to every battle up to Lv 99; if the enemies of F20-30 fall below the character, the real time moves towards 85.8 minutes.
* "Smooth curve": the reduction factor is smooth; the curve keeps vanilla's jumps (the per-level increment doubles at Lv 30->31, 40->41, 50->51, 80->81, 84->85, 90->91, 94->95).
* The Slave's Torc now points to enchant 275, which is vanilla's own "Double EXP" (used by Therion's Crown, Lord Mashiro's Fan and Sinner Sword), so the effect is a real engine mechanic. The Torc had enchant 66 twice and now has it once: it loses one "Phys Damage Taken -10%".
* On a save made before the mod, a character can show a negative `NEXT`. Seen on screen: Lv 20, EXP 22,501, NEXT -1,577, which is exactly 22,501 minus the new cumulative requirement for Lv 21 (20,924).

### 3.2 Quest ranks and bag: pass

| Rank | Vanilla | Mod (binary = Excel) |
|---|---|---|
| 2 | 2 Mui Kuha Medicines | Bag +10 |
| 8 | Bag +5 | Bag +10 |
| 11 | Bag +5 | 50,000 gold |
| 15 | Bag +5 | 100,000 gold |
| 16 | Access to The Matrix | Unchanged |
| 20 | Bag +5 | 500,000 gold |

The total is still +20, as in vanilla; with a base of 30 (not stored in these archives) that gives 40 at Rank 2 and 50 at Rank 8. Mary Conductor's two lines (`ShopQuest` `Talk_Random08` and `Talk_Random10`) match the binary, and so does "Miranda at Rank 12" in `Teaching_14`. Euthys's mention in `Lesson` `BattleTeacher_09` is one of the replacements that did not apply.

### 3.3 Items and shop: fail

| Item | Value (`0x28`) | Buy (`0x1C`) | Sell (`0x20`) |
|---|---|---|---|
| Magical Fruit | 25 -> **50** | 300 | 100 |
| Fairy Apple | 50 -> **100** | 900 | 300 |
| Golden Apple | 100 (unchanged) | 3,000 | 1,000 |
| Mui Kuha Medicine | 10 -> **30** | 1,200 | 400 |
| Flashlight | 10 -> **30** | 150 | 50 |

* Both Rin-Rin lines failed to apply; `ShopStore.pck` holds the original content.
* **Live desync:** Rin-Rin still says Fairy Apples "re-cov-er 50 TP for the low price of 900 gold", and the item now gives 100.
* **The pending line has the prices wrong:** "Mag-i-cal Fruit (50 TP for 100 G)" and "Fair-y Ap-ples (100 TP for 300 G)" quote the sell values. The buy prices are 300 and 900.
* Fairy Apple (medium) now restores the same 100 as Golden Apple (large). The Golden Apple text says "(Full TP)" but its value is 100 and was not changed.
* The syllable hyphenation of the pending lines is correct.

### 3.4 Combat and action economy: fail

Installed delays: A+ 1.00, A 1.15, B+ 1.30, B 1.45, C+ 1.60, C 1.75, D+ 1.85, D 1.95, E+ 2.05, E 2.15, F+ 2.25, F 2.35 (vanilla: 1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.15, 2.30, 2.45, 2.60, 2.75, 2.90).

* `WeaponRankData.pck` is missing from the zip and from the lists of `package_release.py` and `audit_tool.py`.
* `Teaching_01` mislabels the tiers: "Balanced (B to C+ 1.30-1.75x)" should be B+ to C; "Colossal (D to F 1.85-2.35x)" should be D+ to F. `Teaching_09` omits D+, E+ and F+.
* Defend: `StringData_0202` says "Halve damage (50%), cut delay to 0.67x, & prevent crits and interrupts". The crit and interrupt part is listed in `DEFINITIVE_BALANCE_PROPOSAL.md` as a new addition and has no implementation.
* Master Spells: all five say "Pierces 50 Elemental Res."; `MagicSkillData.pck` has no value change and the proposal lists it as "0 -> 50".

### 3.5 Facilities and mechanics

| Table | Excel = binary | Notes |
|---|---|---|
| `EnchantData` (280) | 247 of 247 | The percentages in the names cannot be checked against the header |
| `SealScrollData` (374) | 374 of 374 | Dragon Papi text agrees with enchant 270 |
| `JoinSkillData` (52), `PartySkillData` (20) | all | |
| `FoodMenuData` (16) | 16 of 16 | "900 Steps" on 2 of 16 meals; no duration field changed; the proposal says vanilla is 300 |
| `TrapData` (12) | 12 of 12 | 3 labels contradict their own value |
| `TrophyData` (50) | 50 of 50 | Humor kept in all 50 |
| `ClassData` (32 of 49) | 32 of 32 | Original prose replaced by a spec sheet |
| `StringData` (14 of 636) | 14 of 14 | |

Traps: in 9 of 12 the label equals the float in the binary. Not in three: Killer Floor 0.5 vs "25% KO" (the proposal says vanilla 50%, proposed 25%, never implemented; `Teaching_20` repeats 25%); Damage Floor and Mine 0.5 vs "25% HP" (unclear whether that float is the damage). The element labels contradict `Teaching_13`, still in the game: Poison Gas says "Earth Res" (poison is Water), Sleep Gas says "Water Res" (sleep is Wind), and Paralysis Gas says "Thunder" where the game says "Lightning". The trap name is inserted into "You triggered a %name trap!", so the long labels end up inside that sentence.

---

## 4. Persona, tone and narrative integrity

### 4.1 Replacements that did not reach the game

`update_teaching_script` searches for the original string followed by a NUL byte. A spoken line ends with a quote before the NUL, so nothing matches and the code continues silently; the counters increase anyway ("Applied 10 BattleTeacher lecture scripts").

| Archive | File | Intended content |
|---|---|---|
| `Lesson` | `BattleTeacher_04`, `_07`, `_08`, `_09`, `_10` (1st), `_11-12` (1st), `_13`, `_Sp02` | 2H weapons and Defend; ranges; 100 resistance; bag ranks and Matrix; party skills; reset thresholds; meals; Dark Aura |
| `ShopBar` | `Talk_Random04` | Mercenary habits |
| `ShopStore` | `Talk_Random01`, `Talk_Random11` | Flashlights; fruit prices |

Applied: 27 of 27 in `Teaching`, 4 of 12 in `Lesson`, 2 of 2 in `ShopQuest`, 3 of 3 in `ShopBlacksmith`. `ShopBar.pck` and `ShopStore.pck` travel in the zip with original content.

### 4.2 Euthys (`Lesson.pck`): 4 lines in the game

| File | Assessment |
|---|---|
| `BattleTeacher_10` | Good. "*giggle* Don't be so timid, Fried..." answers Fried and fits her voice. |
| `BattleTeacher_11-12` | Acceptable. "Simply equip her..." lost the antecedent of "her": the replaced line was the one introducing the reset character. |
| `BattleTeacher_Sp01` | **Breaks the original joke.** Fried asks what to do against attacks above his max HP; Euthys answered "Abandon hope and make peace with your fate."; Fried: "Seriously?!"; Euthys: "Well... it's for times like these that you should be saving frequently." She now gives three lines of tactics and the next two replies no longer follow. "Giving up already, Fried?" does not fit either: he asked a question. |
| `BattleTeacher_Sp03` | **Wrong content.** "Achieve a Crown by resetting with a 59+ level gap" contradicts the two original lines just before it and `Teaching_25`: a gap of 59 gives +1 to stats, not the Crown. |

`*giggle*` appears once in Euthys's original text, so the two additions are in character. `*fufufu*` appears nowhere. The four replaced lines are voiced (`VC_81xx_...`); the audio remains the original line. Of the eight pending lines, `BattleTeacher_10` (1st) says "+100% bonus ... maxed out at 50 awards", while `Teaching_16` and `StringData_0312` say +1% per 5 awards (+10% with 50 trophies), and `BattleTeacher_13` speaks of "elemental guards" immune to Dispel where the meal gives Stab/Slash/Bash Guard and no data mentions Dispel.

### 4.3 Mary Conductor (`ShopQuest.pck`): voice kept, format broken

Both lines keep the row of dots and the parenthesised thought. `Talk_Random08` takes 4 lines and one of 66 characters; the longest original line in that archive is 62 and no original box has more than 3 lines.

### 4.4 Blacksmith (`ShopBlacksmith.pck`): voice mismatch

The three lines keep dots and parentheses, but all three boxes have 4 lines, and the voice does not match the neighbouring boxes: the original blacksmith is formal ("I'm afraid I must politely decline your request", "I advise you plan well..."), the new lines use "'em" and "you'll blow my workshop sky-high". `Talk_Random10` also repeats the previous box before adding its advice.

### 4.5 Library (`Teaching.pck`): 27 replacements applied

| File | Problem |
|---|---|
| `_09` | 4-line box. Contains "Heavy delay capped / at 2.35x": the banned term "capped at" is split by the line break, which is why a plain search missed it. |
| `_08` | "hidden combat telemetry", "Covered Chant procs" |
| `_02`, `_19`, `_10`, `_23` | "sweet spots", "sustainable loops", "burst damage", "high-tier carry", "re-level", "multihits" |
| `_21` | Duplicate numbering: the replacement ends with "3. Mercenaries gain permanent level-ups..." and the next original box starts with "3. Unlike Sealbook Summons...". The rule that the mercenary leaves when the contract ends is lost. |
| `_25` | "(>=69, >=79, >=89, >=99)": a gap of 99 is impossible; the maximum is 98. |
| `_15`, `_25` | "Level EX (+50% bonus)": the EX value is +50% over Lv 9 in only 2 of the 18 unique skills; the others range from +25% to +100%. |
| `_20` | A "Dungeon Traps" box inserted in the Zones page; the next original box says "Sometimes these zones can overlap". The list of Boost Zones is lost. |
| `_17` | The new point 2 already mentions Pep and the original point 3 repeats it. |
| `_01` | Wrong tier labels (3.4). |

The tone moves from a neutral manual to an optimisation guide.

### 4.6 Data tables

| Table | Original text kept |
|---|---|
| `items.xlsx` (388 modified of 576) | 388 of 388, with the data in parentheses at the end |
| `equipment.xlsx` (551) | 550 of 551 on line 1 |
| `trophies.xlsx` (50) | 50 of 50 |
| `classes.xlsx` (32) | 0 of 32: prose replaced by "Role / Row / Weapons / Stats" |
| `enemy_attacks.xlsx` (2,375) | Original line 2 removed in 2,150 |
| `joint_skills.xlsx` (52) | 0 of 52 |

* Slave's Torc: "In fact a heavy shackle..." became "In fact a heavy **training** shackle...". The `Original_Desc` column of the Excel was edited too, so a check based on the Excel gives 551 of 551.
* Enemy attacks: 724 descriptions have a line that starts in lower case with no subject ("damage (ATK 125%).") because the template leaves the damage type empty for Neutral attacks. The 16 "Take Break" entries lost their joke. 44 say "Inflicts Slow" where the effect is petrification (id 120) and 69 say "Inflicts Charm" where it is slow (id 122); the trap table confirms those ids.
* Classes: three descriptions use "DPS".
* Item typos: "acquired taste.. (+30 HP, +40 TP)." (Kuding Tea), "side effects.. (+75% DEF)." (Ephemerol), "(Speed DOWN -60%.)." (Supergravity Machine).

---

## 5. Accuracy of the figures shown

### 5.1 Skills

Compared with the binary tables, which the build does not modify.

| Figure shown | Skills that quote it | Match | Do not match |
|---|---|---|---|
| TP cost | 141 | 16 | **125** |
| Physical power ("ATK: a% -> b%") | 39 | 2 | **37** |
| Magic power ("Pwr: ...") | 22 | 5 | **17** |
| Max level ("L1-N") | 162 | 109 | **53** |

| Skill | Text in the game | Binary |
|---|---|---|
| Halving Slice | TP 15 -> 28; ATK 115% -> 175%; instakill 10% -> 25% | TP 38 -> 74; ATK 80% -> 110%; instakill 10% -> 20% |
| Megaton Press | TP 16 -> 28 | TP 26 -> 68; ATK 120% -> 184% |
| Blood Drain | ATK 110% -> 170% | ATK 74% -> 110% |
| Moonlight Purgatory | ATK 70% -> 110% | ATK 118% -> 158% |
| Crimson Flare | 10 levels: power 620, 680, 750 ... 1300 | 5 levels: power 620, 760, 920, 1100, 1300 |
| Inferno | Power 80, 110, 140 ... | Power 300, 350, 400 ... 750 |

The errors go both ways. The text was the same at the earlier "QoL" commits (`4e5ab5f` and before); only 7 skill texts changed afterwards.

### 5.2 Mechanics described but not implemented

All appear as new changes in `DEFINITIVE_BALANCE_PROPOSAL.md`; none has a value change in its archive. The executable was not analysed, so an original engine behaviour cannot be ruled out, but the project itself documents them as new.

| Text in the game | Where |
|---|---|
| "Pierces 50 Elemental Res." | 5 Master Spells |
| "prevent crits and interrupts" | Defend (`StringData_0202`) |
| "80% Crit Interrupt Res at Lv 5" | Concentrate |
| "Dolls gain Guts." | Double Puppet |
| "25% KO" | Killer Floor and `Teaching_20` |
| "(+10% Stats, 900 Steps)" | Ultimate Champon, Heaven's Ramen |
| "(Full TP)" | Golden Apple |

The zip instructions also announce rebalanced tank classes and Soul Summoner dolls; no value in `ClassData` or the skills changed.

### 5.3 Equipment

* **Seen on screen:** the game draws the item's enchantments on lines 2 and 3 of the box. All 551 descriptions put text there, so it is overdrawn (`Fire Magic +15%` printed over `[Weapon | Range: Short | Delay: E+ (2.05x) | Slots: 0]`). All 551 original descriptions are one line.
* That second line repeats what the title bar already shows (`[Sword - 2 Hand - Short Range] Speed E+`).
* `Slots: N` is fed by a field that equals the number of innate enchants in all 551 items. The screenshot shows `Slots: 0` on an item carrying two enchants.
* The `Innate:` lists are incomplete in 200 of 551: 114 stop at three enchants although the item has four, and 86 omit enchant id 0 ("Max HP +10%").

### 5.4 Revive items

Mui Kuha Medicine has 30.0 and says "Revive 30% HP". Peggy's Revivifying Tonic, with the same effect type, has 1.0 and says "Revive 100% HP". Both readings of the field cannot be right.

---

## 6. Technical validation

### 6.1 Format on the real game strings (4,385)

| Rule | Result |
|---|---|
| Tilde | 0 |
| Lines over 85 characters | 0 |
| More than 3 lines per box | **5**: `Teaching_09`, `ShopQuest/Talk_Random08`, `ShopBlacksmith/Talk_Random00`, `_10`, `_11` |
| Trophies, 2 lines at most | 0 violations |

The request speaks of 24 archives and 14 tables; `apply_mod.py` modifies **25 archives** and there are **15 tables**.

### 6.2 Binary integrity

* Excel = installed binary: 0 differences in 4,349 strings of 12 tables, plus EXP and ranks.
* **Battle message of the skills.** Each technique, spell and passive has four strings; the writer wrote three and left the fourth pointer at the end of the entry. The 200 modified skills in the game and the zip have that pointer outside their entry. 17 had a real message that was lost: Power Charge, Fascinating Waltz, Alluring Samba, the summons Spartan, Catalina, Perdurabo and Musiy, Arcane Shield, and the passives Avenger, Guts, Auto-Guard, Pretend, Esarhaddon, Ecstasy, Recycle, Magnificent Steps and Elegant Dancing. Fixed in `pck_handler.py` after this audit; the installed files still have it.
* **Archive tail.** Rebuilt archives were 8-16 bytes shorter than the originals in 22 of 36 cases. Fixed in `pck_handler.py`.
* Other writers that do not reproduce the original entry: `JoinSkillHelper` loses a string in one entry; `PartySkillHelper` changes a full-width space; `EnemyAttackHelper`, `EnchantHelper`, `SealScrollHelper` and `FoodMenuHelper` differ only in padding.
* ADV scripts: sequential bytecode with jumps by label name; no absolute offsets found.

### 6.3 Git and package

* Branch `master`, no remote, no `main`.
* The zip holds 24 archives identical to the installed ones. **`Data/ENG/Parameter/WeaponRankData.pck` is missing.**
* `dist/DT22_QoL_Balance_Mod_v1.0.zip` is an older build (23 files) and should be deleted.
* `scratch/comprehensive_cross_system_audit.py` points to paths and file names that do not exist and reads the price at the wrong offset; its "PASS" lines are not evidence.

---

## 7. Latent risks

1. **Fixing the replacement bug activates dormant errors:** Rin-Rin's prices, "+100%" party skills, Dispel-immune "elemental guards". Fix the text first.
2. **The player cannot trust the skill figures.** 89% of the TP costs shown are wrong.
3. **The zip produces a different game from the one tested locally** (delays).
4. **The 57-minute figure rests on unmeasured assumptions** and on a bonus that may stop applying.
5. **Text and voice no longer agree** on the replaced Euthys lines.
6. **Dialogue boxes of 4 lines and lines wider than any original one** have not been seen on screen.
7. **Golden Apple is redundant** next to the modified Fairy Apple.

---

## 8. What is right

* The 25 archives open, and the Excel tables faithfully describe what is in the game.
* The EXP curve is strictly increasing and matches its table.
* Bag at Ranks 2 and 8, gold at 11, 15 and 20, and Matrix at Rank 16 agree between binary, Excel and Mary Conductor.
* The Slave's Torc uses a double-EXP enchant the engine already supports.
* 388 items, 550 of 551 equipment pieces and 50 trophies keep their original text.
* No tilde and no line over 85 characters anywhere.
* The layout of the skill text (a range with its step, or one value per level; costs on the last line) reads well and was kept as the project style.

---

## 9. Reading the findings by variant

| | QoL (information only) | Balance |
|---|---|---|
| Value changes of section 2 | Must all be left out | Belong here; `WeaponRankData.pck` must ship |
| Skill figures (5.1) | Regenerate from the binary. Done for skills: `build/qol/` | Decide the new values, write them into the binary, then describe them |
| Mechanics without data (5.2) | Remove from the text | Implement or remove. Killer Floor and TP costs are plain data; no field was found for the others |
| Texts quoting Balance values | Must quote the originals: weapon delays, the 4 items, Slave's Torc, bag ranks, `Teaching_19` | Correct as they are |
| Dialogue bug, 4-line boxes, jargon, Sp01 and Sp03, trap elements, equipment overlap, enemy attack template | Common to both | Common to both |

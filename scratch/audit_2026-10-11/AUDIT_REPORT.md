# Audit of the simulator and of the Balance variant, 2026-10-11

Scope: `sim/`, `tests/test_sim_formulas.py`, `data_tables/balance_changes.xlsx`, the party battery, the difficulty
curve, the EXP decisions, and the texts of `Lesson.pck` and `Teaching.pck`. Read-only on the repository: nothing under
`sim/`, `tools/`, `docs/` or `data_tables/` was changed. Every figure below comes from the disassembly of
`DT22_en_unwrapped.exe` or from a run of the simulator; the scripts are in this folder.

Starting state: `python -m pytest mod_project/tests/` gives 199 passed.

## 0. What exists and what does not

| Fact | Evidence |
|---|---|
| No Balance build exists | `tools/build_variant.py` VARIANTS holds `qol` only; `build/` holds `qol` only |
| No change row is built or checked | `balance_changes.xlsx`: 1,367 rows `decided`, 35 `dropped`, 0 `built`, 0 `checked` |
| The register is not closed | sheet `Criticisms`: 162 rows, 110 open, 39 not a problem, 7 closed, 6 out of the balance. T01 6 of 6 open, T03 3 of 3, T06 64 of 65, T12 5 of 5 |
| The game folder holds the QoL build plus two files no build made | 12 files of `Parameter/` equal `build/qol`; `Script/Lesson.pck` and `Script/Teaching.pck` (2026-10-11 12:38) equal neither the backup nor `build/qol` |
| Those two files come from `scratch/update_euthys_and_teaching.py` | It holds its 36 texts in code and saves straight into the game folder |

So everything said about "the mod" below is about the simulated variant (the rows `decided`), not about a build.

## 1. Parity with the executable

Verified in the disassembly (`xdis.py START END`):

| Point | Address | Executable | Simulator |
|---|---|---|---|
| Race factor of a blow | `0x44bf4e - 0x44c055` | `1 + effect 88` only against races 5, 7, 8; the enchantment shares (0.3, 0.15, 0.6) are added to it | Same since f8cbd16. Correct |
| Physical accuracy enchantments | `0x44ad16 - 0x44ae06` | 31 x4 + 32 x2, min 50; target 35 x4 + 36 x2, min 50 | Same |
| Defending, escaping, cap | `0x44a31c - 0x44a349` | gauge value x1.15 (action kind 5), x1.20 (kind 6), min with 0.92 | Same |
| Ailment roll | `0x481fa0 - 0x482028` | `value * 100`, minus `(resistance / 10 as integers) * chance / 10`, minus 15 with enchantment 269 in one context, cut to an integer, roll below 100 | Same formula; see D3 |
| Turn delay | `0x423a41 - 0x423b97` | immune with bit 12 of the enemy flags; roll below 100 under `int(value * 100)`; gauge swapped with the next unit of the order | Same |
| Enmity | `0x44a630 - 0x44a75d` | position share + int(effect 170) for the member who put it + 10 per piece of 49 - 5 per piece of 50, at least 10. Nothing from damage or healing | Same |
| EXP by level gap | `0x450739 - 0x45080d` | 0.85, 0.9, 1, 1, 1.1, 1.25, 1.25; with enchantment 270: 1.15, 1.3, 1.5, 1.75 | Same (`sim/progression.py`) |

Discrepancies:

**D1. Fixed accuracy of a blow is clamped again; commit f8cbd16 removed that clamp and tests the wrong rule.**
`0x44ae84 - 0x44aed2` clamps to 5..100; `0x44aef3 - 0x44af76` sets `value * 100` for effect 55, else 72;
`0x44af7e - 0x44afbb` sets 100 on a sleeping target; **`0x44afbe - 0x44aff8` clamps to 5..100 a second time**; then
effects 149 and 150. The code before f8cbd16 (clamp after the fixed value) was the right one.
`test_fixed_accuracy_bypasses_physical_floor` asserts 2% for a fixed accuracy of 0.02; the executable gives 5%.
The spell function has no second clamp (`0x44da2b - 0x44dab1`), so there the fixed value does pass 25..95.
Effect on results today: none (no blow of the data carries 55 or 72 below 0.05 or above 1; the lowest is Surprise
Fist at 0.5). It is a false rule with a test that locks it in.

**D2. Magic accuracy and evasion MiniUP count 1 per piece, not 2.** `0x44d6a3 - 0x44d6bd` (enchantment 40) and
`0x44d722 - 0x44d742` (enchantment 44) convert the count and add it with no multiplication; 39 and 43 are multiplied
by 3 (`0x44d67b`, `0x44d6f0`). `sim/battle.py` uses `3 * pieces(39) + 2 * pieces(40)` and the same for 43 and 44.
`qol_enchant_text.xlsx` already says +1% ("exe-verified"), `docs/generated/ENCHANT_SIZES.md` still says "?": three
places, three values.

**D3. The ailment chance is not cut to an integer.** `0x48201d` is `cvttss2si`; `Battle.apply_ailment` compares the
roll with a float. Up to 1 point too generous (value 0.88 against resistance 30: 61 in the executable, 62 in the
simulator). The flat -15 of enchantment 269 is never passed.

**D4. The three tests added by f8cbd16 do not test the engine.** `test_magic_hit_enchant_cap_50` asserts the hit is
at most 95, which the clamp of `magic_hit` gives with or without the cap. `test_race_factor_additive_with_effect_88`
writes the formula again inside the test instead of calling `Battle.physical_damage`. The third is D1.

**D5. The "parity fixes" of f8cbd16 change no result.** The reference party at C26 - C40 gives the figures of
`DIFFICULTY_CURVE.md` (generated twelve hours earlier) to the last digit (`e2_e3_result.txt`).

Claims of the brief the executable does not hold:

* "Defend cuts the delay to 0.67x": the constant is 1.15 on the gauge value (`0x6d939c`). The wait is `1 - value`, so
  the cut depends on the unit: x0.85 at a value of 0.50, x0.65 at 0.70, x0.40 at 0.80. No 0.67 exists in the code.
* "DEX of the attacker against RES of the defender" in the ailment roll: neither stat is read. The roll reads the
  elemental resistance of the ailment (water for poison and freeze, wind for sleep and silence, ...).

## 2. The battery of 17 bosses

### 2.1 Reproduction (N = 40, same parties, same seeds; `e1_ablation_result.txt`)

Win share, vanilla > variant:

| | Meta | Dual-Support | Mage-Heavy | Juggernaut | Anti-Meta |
|---|---|---|---|---|---|
| C26 | 95 > 95 | 98 > 95 | 90 > 82 | 12 > 12 | 28 > 58 |
| C28 | 85 > 100 | 68 > 92 | 78 > 95 | 10 > 12 | 5 > 65 |
| C29 | 5 > 45 | 5 > 2 | 92 > 95 | 0 > 0 | 0 > 18 |
| C30 | 100 > 100 | 98 > 100 | 88 > 100 | 0 > 20 | 0 > 2 |
| C32 | 100 > 100 | 98 > 100 | 90 > 100 | 10 > 30 | 10 > 75 |
| C34 | 100 > 100 | 98 > 98 | 100 > 100 | 48 > 65 | 0 > 98 |
| C36 | 100 > 100 | 80 > 82 | 32 > 58 | 0 > 15 | 0 > 2 |
| C38 | 100 > 98 | 100 > 100 | 92 > 92 | 0 > 0 | 0 > 75 |
| C40 | 100 > 100 | 92 > 98 | 10 > 8 | 0 > 0 | 0 > 0 |

It agrees with `PARTY_BATTERY_OLD_VS_NEW_AI.md` within the noise of N = 20 (one run is 5 points; 20 of 20 only says
"at least 84%" at 95% confidence, so the "+5%" and "-5%" cells of that document mean nothing).

### 2.2 The immunity flags are invisible to the battery

The variant changes the flags of 74 bosses: turn delay closed on 58 (16 were immune in vanilla), sleep opened on 18
story bosses, silence on 22, slow on 19, poison on 6. Three more columns were played: the variant with sleep closed
again, and the variant with every vanilla flag. In all 45 cells the three agree within 8 points, and the turns denied
to the enemies stay near 1 per fight. So:

* The jumps of the Anti-Meta party (C28, C32, C34, C38) come from the skill rows (dolls, Magical Spark, whips), not
  from locks. That part of the claim of `SIMULATOR_AI_BENCHMARK_PHILOSOPHY.md` holds.
* The 74 flag rows have no measurement behind them. The policy uses an ailment only at 50% or more and hits a lone
  sleeping boss at once; a player does neither.

What a player gets from them (Sleep Lv5 0.90 and Lullaby Lv5 0.95 on the variant, against wind resistance):

| Boss | Vanilla | Variant |
|---|---|---|
| C21 Trafficker Twinny | immune | 90 / 95% |
| C25 Martial Artist | immune | 100% |
| C29a Dragon Papi | immune | 100% |
| C37 Iron Maiden (16,800 HP) | immune | 90 / 95% |
| C26 Michelle | immune | 72 / 76% |
| C13 Eros, C10 Countess of Vrachia | immune | 72 / 76%, 63 / 66% |
| C32 Moby Dick (13,280 HP) | immune | 63 / 66% |
| C33 Death Cataphract, C36 Demon God Fried | immune | 45 / 48% |

A sleeping unit loses its turn without state 16, so it never wakes by itself (FORMULAS 16.7), is hit for certain and
takes x1.5. Turn delay, the lock the rows set out to remove, is a swap with the next unit at 25 - 43% (Tinker Squash,
unchanged). The variant closes the soft lock on every boss and opens a hard one on eighteen.

**Correction, same day (checked after the user asked whether this is true).** Three things above were overstated:

* The figures of the table are the ailment roll alone. Sleep and Lullaby first pass a magic hit roll that stops at
  95% (`0x44da37`). Per cast at skill level 5: Martial Artist 95%, Trafficker Twinny and Iron Maiden 86 - 90%, Michelle
  68%, Moby Dick 56%, Demon God Fried 40%. In the battery parties nobody takes Lullaby and the Sage has Sleep at
  level 1: 74%, 59%, 49%, 34% (`e5_sleep_real_chance.py`).
* Dragon Papi is fought on a cell that forbids magic (FORMULAS 16.2): Sleep and Lullaby cannot be cast there, only
  Sleep Sting (51% at level 8). "100%" was wrong.
* "A hard lock" was not measured when written. Measured since (`e6_sleeper_policy.py` on the workbook of f8cbd16,
  `e6_result_workbook_f8cbd16.txt`, 30 runs): one member casts sleep at level 5 every time the boss is awake, the
  others play as before. The boss loses 17 - 32% of its turns where sleep lands well (C21, C25, C26, C37; 4 - 8%
  without), 20% at C32, 15% at C36. Wins hardly move and often fall, because the caster gives up her own turns
  (Anti-Meta C32 70% > 0%, Meta C36 100% > 83%); they rise where the party died to burst (Juggernaut C21 10% > 40%,
  C37 27% > 37%). This is a floor: nobody times the cast or holds a hit. It shows a strong tool on four or five
  bosses, not a lock.

Verified in the executable for this: the sleep roll reads wind resistance with the formula of poison
(`0x4828b3 - 0x482928`); a sleeping unit goes to phase 4 (`0x436ca5 - 0x436cf9`), which sets a plain wait and starts
the next turn without the per-turn methods of state 16 (`0x4392ef - 0x43932c`), so the recovery roll is not made on a
turn lost to sleep. Not followed: whether anything else in a battle runs those methods on a sleeping unit.

Commit d25c8ed (14:11, another session) closed sleep again on the 18 bosses. With it, poison was closed again on
Iron Maiden, Samael and Queen of Darkness, silence on Samael, Demiurge and Queen of Darkness, slow on Michelle and
Heartless Avenger; the `Why` of those rows still describes the earlier values. Its ailment change takes the 15 points
of enchantment 269 when the resistance index is 4 (water); the executable takes them when the kind of the command's
source is 4 (`cmp dword ptr [edi + 8], 4`), for every ailment.

The brief describes another rule (immunity only for the last superbosses, Tinker Squash at 15 - 20%). The workbook
holds the opposite: rows A001 - A073, decided 2026-10-09, "no boss lockable by Tinker Squash". One of the two is out
of date; it is the user's call.

### 2.3 What the battery shows

* **Meta and Dual-Support: kept.** 82% or more everywhere but C29.
* **Three of five parties cannot finish the story.** C40: Mage-Heavy 8% (3 of 40; 95% interval 3 - 20%), Juggernaut
  0%, Anti-Meta 0%. C36: 58%, 15%, 2%. The variant does not move these.
* **Anti-Meta: real gains, three walls left**: C30 2%, C36 2%, C40 0%.
* **Juggernaut: not solved.** 0 - 30% from C26 on, C34 apart. Three times the items change nothing
  (`JUGGERNAUT_TRIPLE_ITEMS_REPORT.md`).
* **C29 says nothing.** `GUIDE_CURVE.md` marks it "read: policy gap": the guide calls Calliope normal, the simulator
  gives the reference party 15% in vanilla. Until the policy plays that fight, its column is noise.

Why the losing cells lose, on the variant (`e4_diagnose.py`, 12 runs each): no timeout, every loss is a wipe, and
in every cell the largest single enemy action takes 97 - 133% of a mean member's max HP.

| Cell | Falls in fight | Boss HP left | Party TP left |
|---|---|---|---|
| C40 Mage-Heavy | 1.9 of 2 | 33% | 16% |
| C40 Anti-Meta | 1.8 of 2 | 74% | 17% |
| C30 Anti-Meta | 1.8 of 2 | 65% | 12% |
| C40 Juggernaut | 1.3 of 2 | 68% | 46% |
| C38 Juggernaut | 1 of 1 | 38% | 28% |
| C26 Juggernaut | 1 of 1 | 63% | 45% |

Mage-Heavy and Anti-Meta run dry in the second of two fights in a row: TP is their bottleneck and the TP rows
(costs -20 to -25%, Auto-Refresh +25%) do not reach it. The Juggernaut dies with a third to a half of its TP: its
bottleneck is survival, and the party as defined has no healer at all (Valkyrie, Samurai, Dark Lord, Kunoichi,
Etoile). It measures "five members without a heal", not the worth of those classes.

### 2.4 The parties are not what their names say (`q_parties.py`)

* C06 and C10: every party has 2 to 4 members. Anti-Meta at C06 is two members (Siena in front, Yuni) while four
  characters have joined: the fallback takes only characters whose base class one of the five roles asks for.
* C13 - C21: Mage-Heavy has no healer and two Bards; Juggernaut has two Dancers and no Dark Lord (C13 - C18);
  Anti-Meta has two Mistresses and no doll user until C24.
* The Kunoichi of the Juggernaut stands in the back row at every checkpoint from C19.

The comparison stays symmetric; what fails is reading a cell as "this archetype at this boss" before C24.

### 2.5 Six battery documents, two answers

`docs/generated/` holds six battery reports. `PARTY_BATTERY_EXPANDED.md` gives Juggernaut 100% > 83% at C40 and
Mage-Heavy 91% > 83%; `PARTY_BATTERY_OLD_VS_NEW_AI.md` gives 0% > 0% and 15% > 10% for the same names. They are in
Spanish, their generators are untracked files of `scratch/`, and only one matches the code of today.

## 3. Bosses and common enemies

### 3.1 Boss rows that are live

| Checkpoint | Change | Reference party, vanilla > variant (40 runs) |
|---|---|---|
| C10 | HP +15%, ATK and DEF +4% | 100 > 100%, length 9.2 > 10.8, lowest HP 78 > 75%: within |
| C13 | HP +20%, ATK and DEF +5% | 100 > 100%, 8.8 > 10.3, 75 > 75%: within |
| C24 | HP +25%, ATK and DEF +7% | 100 > 100%, 6.2 > 5.4, 64 > 67%: within (was "time easier") |
| C26 | ATK and INT +16% | 92 > 100%, 21.3 > 11.3: time easier, pressure harder |
| C30 | ATK and INT -8% | 62 > 92%, lowest HP 30 > 48%: won easier |
| C36, C38, C40 | none: G019 - G023 are `dropped` | C38 52 > 92%, lowest HP 26 > 52%: won, time and lowest HP easier |

The brief lists C30, C36, C38 and C40 as buffed. C30 is a cut; the other three carry no stat row.
`DIFFICULTY_CURVE.md` predates the rows of C10, C13 and C24: its count is 33 of 44 within today, not 32.
No boss row is a frustration risk. The late bosses are easier than vanilla for the reference party (C30, C38), which
Regression R10 forbids and the dropped G rows were there to prevent.

### 3.2 Stage 15 common enemies: the real spike

Rows G034 - G093: 17 common enemies HP, ATK and INT x1.30; Macha, Purski and Highway Star HP x1.95, ATK and INT x1.69.

| | Level | HP | ATK | Weight |
|---|---|---|---|---|
| Macha, variant | 65 | 15,263 | **613** | 0.35 |
| Highway Star, variant | 64 | 11,448 | **588** | 0.30 |
| Purski, variant | 62 | 5,212 | 529 | 1.60 |
| Demiurge (C40, last boss) | 68 | 24,000 | 378 | 0.22 |
| Atialuco (C40) | 70 | 21,800 | 400 | 0.20 |
| Melek Taus (level 90) | 90 | 56,000 | 487 | 0.16 |

A random-encounter enemy with 62% more ATK than the last boss. Damage is `ATK * 2 * (1 + power) - DEF * 1.35`, so
x1.69 ATK is x2.0 to x3.3 damage, most on those with most DEF. Mean damage of the strongest attack, as a share of the
target's max HP, at the level and gear of C40 (`e2_stage15_hits.py`, formulas only):

| Enemy | Valkyrie tank (DEF 471, 1,171 HP) | Dark Lord | Witch (627 HP) | Diva |
|---|---|---|---|---|
| Macha | 55% > **132%** | 63 > 148% | 105 > 205% | 85 > 184% |
| Highway Star | 58% > **132%** | 62 > 138% | 153 > 296% | 121 > 254% |
| Purski | 18% > 45% | 17 > 48% | 41 > 93% | 31 > 73% |

Every member of every party, the tank included, falls to one hit of two of them. They are in **47% of the random
battles** of St15_1130, 1140 and 1150, and also in St20_0010 to 1030 (15 - 34%) and St21 (8%), postgame floors the
row did not look at ("found only on the C40 floor of the two").

Eight random battles in a row, 24 rows (`e2_e3_result.txt`), mean battles won of 8 and share of full rows:

| Floor St15_1150 (of C40) | Vanilla | Variant |
|---|---|---|
| Reference party | 6.9 (67%) | 4.4 (29%) |
| Meta | 6.2 (67%) | 5.4 (42%) |
| Dual-Support | 6.0 (58%) | 3.8 (12%) |
| Mage-Heavy | **7.1 (71%)** | **2.5 (0%)** |
| Juggernaut | 2.3 (0%) | 1.4 (0%) |
| Anti-Meta | 4.0 (12%) | 2.2 (0%) |

St15_1120 (of C39): 4.5 > 3.6, 5.5 > 4.5, 5.1 > 2.7, 4.5 > 3.4, 1.9 > 1.1, 3.0 > 1.7.

The row says it brought the variant back to vanilla (5.3 > 5.4). That was measured on 2026-10-09 with the policy of
then; with the policy of ba79eef vanilla is 6.9 and the variant 4.4. Harder than vanilla for all six parties, and the
party that explored that floor best in vanilla now completes no row. The reference party beats the last boss 95% of
the time and finishes 29% of the rows on its floor: the difficulty has moved from the bosses to the corridor.

## 4. EXP, catching up, skill points

| Item | State |
|---|---|
| EXP per level | Vanilla. No row. The "kept curve" the user chose (CATCH_UP_OPTIONS, option "Kept + B4") is another curve and is not in the workbook |
| Factors by level gap, B4 (lever L25, executable) | Not built. The executable has the vanilla table |
| Crown rule "one more point" (lever L27, executable) | Not built |
| Joining level (lever L31, data) | No row. Vanilla already has each newcomer 0 to 4 levels above the reference level (Yuni 13 at 9, Monica 26 at 25, Alisia 41 at 40, Melvy 46 at 44) |
| Skill points, B001 - B040 | +1 per level from 31 to 70; in the simulated variant |
| Register rows closed "through the B4 curve" | S20 (closed), S21 (not a problem), F92 (out of the balance) lean on a rule that exists nowhere |

The catch-up the brief describes is not the one decided, and its pieces do not hold:

* **Slave's Torc has no EXP enchantment**: AGI DOWN and two "Received physical damage DOWN" (EquipmentData 744).
  Double EXP (275) is on Lord Mashiro's Fan and Therion's Crown only. Row F92 records "no new Double EXP item (the
  user, 2026-10-07)".
* **Dragon Papi**: its Grand Sealbook carries enchantment 270 (1.15 to 1.75 from enemies above the member). It comes
  after C29a, level 44, and takes the one Grand Sealbook slot.
* **The native gap rule** tops at 1.25. A member 10 levels behind at level 40 needs 121 battles in vanilla, 60 with a
  Double EXP piece, 34 with B4 (`CATCH_UP_OPTIONS.md`). The user called the vanilla figure not enough on 2026-10-05.

## 5. Texts: `Lesson.pck` and `Teaching.pck` as installed

Structure: the 35 changed entries keep their order; an `.adv.bin` is a stream of commands with named labels and no
byte offsets (no stale offset found), so the longer strings do not break the scripts. Lines: at most 70 characters in
Lesson and 66 in Teaching (the originals reach 75 and 69). No tilde.

Breaches:

1. **One box has four lines**: `CheatsTeaching_09`. The script replaced two lines of a three-line box with three
   lines and checked only the fragment.
2. **Outside the pipeline**: texts in a `.py`, written straight into the game folder, over a QoL build, with the QoL
   variant closed. The QoL line of `CheatsTeaching_25` was overwritten.
3. **All 11 Euthys lines replaced are voiced** (each follows a `VC_81xx` clip). The Japanese line is still spoken; the
   subtitle now says something else. Flavour lines were replaced, not added to (Lesson 07 closing line, Lesson 13
   "Is that right...? There aren't many restaurants around these parts", Sp03 "why not shoot for the Crown?").
4. **Text that speaks from outside the game**: `CheatsTeaching_22`, "Many underutilized skills have enhanced scaling
   and reduced TP costs. Carefully review the updated skill descriptions". False on the installed build too.

Statements set against the executable and the data:

| Entry | Text | Fact |
|---|---|---|
| Teaching 01, 09 | Nine ranks, A+ 1.00x to F 2.35x | Twelve ranks, 1.00, 1.20, 1.40, 1.60, 1.80, 2.00, 2.15, 2.30, 2.45, 2.60, 2.75, 2.90; no row changes them. 01 and 09 also disagree with each other (D is 1.85 in one, 1.95 in the other) |
| Teaching 01, 09 | "Defend (0.67x delay)" | Gauge value x1.15 (section 1) |
| Teaching 11 | "Short-range suffers -50% beyond Front-to-Front" | 0.75 with one unit in the back row, 0.5 with both (`0x44a7d0`) |
| Lesson 07 | Mid-range "ignore penalties from the back row" | 0.75 when both stand in the back row |
| Teaching 13 | "200 res = 100% immune" | Misleading, not contradicted: the factor does reach 0 at 200, but the enchantment sum stops at 100 (`0x4f8490`), so 200 needs the crown bonus and buffs on top; the text gives it as a plain rule |
| Teaching 12 | "Physical damage ... x1.5", "wakes ... upon taking physical damage" | Blows and spells both (`0x44cd3b`, `0x44eff9`); any damage wakes. The true line it replaced ("unable to dodge") is gone |
| Teaching 14, Lesson 09 | Bag +10 at ranks 2 and 8, cap 50 | +5 at ranks 8, 11, 15 and 20; rank 2 gives two Mui Kuha Medicines (QuestRankData) |
| Teaching 19, Lesson 11-12 | Slave's Torc raises EXP | Section 4 |
| Lesson Sp01 | "have a Valkyrie pop Circle Protection" | The spell is Circle Protect, of the Enchantress; it raises DEF |
| Lesson Sp03 | "Achieve a Crown by resetting with a 59+ level gap" | A gap of 59 gives +1; the Crown is a total of 50 |
| Teaching 06 | Summon stats "scale with party averages" | The best member in each stat times the factor of the form (`0x4ffc90`); only the form follows the mean level |
| Teaching 20 | Doll Masters "command their puppets to cast" | A doll picks its action at random each turn (`0x4fd980`) |
| Teaching 10 | Multi-hit attacks "reliably stop spells" | The rate is the damage of each hit against max HP: many small hits interrupt less |
| Teaching 23, Lesson Sp02 | Bosses "enrage": speed and attack surge, "delay tricks lose their efficacy" | Nothing read does that. The lines replaced were true (different skills after damage; Dark Aura works on bosses) |
| Lesson 13 | Meals last 900 steps, ramen "+10% stats with elemental guards" | No reading behind either figure; the ramen give Brave, Protect, the three physical guards or Insurance |
| Teaching 16, Lesson 10 | "+1% per 5 awards" | No reading behind it |

Of the 36 texts, 12 state something the executable or the data contradict (Teaching 01, 06, 09, 11, 12, 14, 19;
Lesson 07, 09, 11-12, Sp01, Sp03), one more is false on the build it sits on (Teaching 22), and 8 are misleading or
have no reading behind them (Teaching 10, 13, 16, 20, 23; Lesson 10, 13, Sp02). Spoilers: Lesson 11-12 names Dragon
Papi (a boss of C29a) and Lesson 09 the Matrix.

## 6. Actions

P1

1. Restore `Lesson.pck` and `Teaching.pck` from `build/qol` and the backup; drop the scratch script from any install
   path. If tutorial text is wanted in the Balance variant, it goes through a workbook and the build, with a check per
   whole box and one source per figure.
2. Rows G034 - G093: take them out or redo them. Macha, Purski and Highway Star first (ATK x1.69). Redo the measure
   with the policy of today and for the six parties, and cap any common enemy below the ATK of the boss of its floor.
3. Decide the lock rule again with the table of 2.2 in hand: turn delay closed on every boss and sleep opened on
   eighteen is the reverse of "no perma-lock". Until the policy uses ailments as a player does, these rows cannot be
   checked by the battery.
4. Sim: put the second clamp back (D1) and replace the three tests of f8cbd16 with ones that call the engine.
5. Catch-up: either build what was decided (L25 and L27 are executable levers; L11 and L31 are data) or reopen the
   decision. Reopen S20, S21 and F92 meanwhile.

P2

6. Sim: MiniUP of magic accuracy and evasion to 1 (D2), integer ailment chance and enchantment 269 (D3); regenerate
   `ENCHANT_SIZES.md`.
7. Battery: N of 100 or more with intervals; full parties from the characters that have joined; a healer or a
   stated "no healer" in the Juggernaut; leave C29 out until its policy gap is read. One generator in `tools/`, one
   document, in English; retire the other five.
8. TP for two fights in a row (C30, C40) is the wall of the caster parties; the TP rows do not reach it.
9. Late bosses easier than vanilla for the reference party (C30, C38) with the G rows dropped: confirm it is wanted.
10. Regenerate `DIFFICULTY_CURVE.md` (C10, C13, C24).

P3

11. A Balance entry in `build_variant.py` and the states `built` and `checked` in use.
12. `FORMULAS.md` 2.1: add the second clamp; section 3: the MiniUP figure.
13. Bring the register up to date: 110 open rows against 1,367 decided changes.

## 7. State after the fixes of the same day (commits d25c8ed, 3a59f15, c057ef8)

Tests: 202 passed.

| Action of section 6 | State | What stands |
|---|---|---|
| 1. Tutorials | Partly | Not restored: rewritten by the scratch script (14:03). Fixed: weapon ranks (12, 1.0 to 2.9), Defend, bag ranks, Circle Protect, the four-line box, the line that spoke of the mod, "enrage". Still wrong: Teaching 06 (party averages), Teaching 13 (200 res), Lesson 13 ("elemental guards"), "+1% per 5 awards" (no reading), and the Slave's Torc lines, false on the installed QoL build until a Balance build exists. Still outside the build; the 11 voiced lines still differ from their subtitle |
| 2. Stage 15 common enemies | Done | HP x1.20, ATK and INT of vanilla, on the 20 enemies (c057ef8); measure in `e7_result_deterministic.txt` |
| 3. Locks | Done | Sleep closed as in vanilla (d25c8ed); poison 6, silence 22, slow 19 restored (3a59f15); turn delay closed on 58 |
| 4. Second clamp, tests | Done | d25c8ed; the cap test rewritten in 3a59f15 |
| 5. Catch-up | Partly | Row W042 (Slave's Torc, Double EXP) and F92. B4, the crown rule and the joining level: no row, no patch. S20 and S21 still lean on B4. Where the Slave's Torc is obtained was not found (no enemy drop, no treasure table, no quest reward) |
| 6. MiniUP, ailment integer | Done | D3 of this report was wrong about enchantment 269: it is "Less likely to trigger traps" and acts on traps only. Removed from the battle roll (3a59f15). `ENCHANT_SIZES.md` still prints "?" for 40 and 44: the tool does not recognise a count added unscaled |
| 7. Battery | Not done | Two parties with a Diva were added; N, full parties and one generator are as before |
| 8. TP for two fights in a row | Not done | |
| 9. Late bosses easier than vanilla | Open | The curve of today: 32 of 44 within, 12 easier, 0 harder |
| 10. Difficulty curve | Done | Regenerated (c057ef8) |
| 11. Balance build | Not done | |
| 12. FORMULAS.md | Done | 3a59f15 |
| 13. Register | Not done | 110 of 162 rows open |

Found on the way: the Auto-Guard rolls were made in the order of a set of units, which follows memory addresses, so
every measure over random battles changed from one run to the next (the same expedition 6.9, 6.8, 6.2). Fixed in
3a59f15; the calibration of 2026-10-09 and E2b of this report were taken with that noise.

## 8. State after the second round (commits 67322e2, ed05df4)

The user, 2026-10-11: fix everything as recommended; the eased bosses a little harder while the five parties (or their
versions with a Diva) stay inside their share.

| Action of section 6 | State | What stands |
|---|---|---|
| 1. Tutorials | Done as recommended | The game folder is the QoL build again (`install_variant.py qol`; what it replaced is in `build/installed_backup/2026-10-11_145318`). The 36 texts are rows of `data_tables/balance_tutorial_text.xlsx`: 27 checked, 7 unverified, 2 held. They wait for a Balance build |
| 7. Battery | Done | `tools/party_battery.py`, parties in the sheet `BatteryParties`, 100 battles, intervals, full parties with one bag. 61 of 85 archetype and boss pairs at or above the floor in vanilla, 71 on the variant |
| 9. Late bosses easier than vanilla | Done within the rule | Six bosses a little harder (C20, C21, C28, C30, C31, C34); five left alone because an archetype is below its floor (C26, C32, C37, C38, P24); C29 not touched. Curve: 37 of 44 within, 7 easier, 0 harder |
| 5. Catch-up | Partly | As in section 7 |
| 8. TP for two fights in a row | Open | C30 is solved by the variant (Mage-Heavy 64% to 92%, Anti-Meta 2% to 66%). C40 is not: Mage-Heavy 15%, floor 50% |
| 11. Balance build | Not done | |
| 13. Register | Not done | 110 of 162 rows open |

Below the floor on the variant, of 85 pairs: C29 (four archetypes; policy gap), C26 Anti-Meta 78%, C32 Juggernaut 69%
and Anti-Meta 56%, C36 Dual-Support 73%, Mage-Heavy 48%, Juggernaut 69% and Anti-Meta 11%, C38 Juggernaut 67%, C40
Mage-Heavy 15% and Anti-Meta 41%.

The battery of this report (sections 2 and 3) gave each member her own bag, five times the items of the reference
party, and parties of two to four members early on; its figures are superseded by `docs/generated/PARTY_BATTERY.md`.

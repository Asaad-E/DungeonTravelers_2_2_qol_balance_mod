# Theme tables for the user

One short table per theme (BALANCE_PLAN.md section 3, phase 2, step 2): each row of the register, its verdict with
the figure that shows it, and the change proposed. **Nothing here is applied**: the user decides each theme. The
full wording of each row, its figure and its source are in the sheet `Criticisms` of
`data_tables/balance_criteria.xlsx` (columns `Verdict`, `Vanilla_Result`, `Proposal`); the count is
`docs/generated/VERDICTS.md`.

**Remeasured on 2026-10-09** after two fixes of the simulator (passive HP and TP regeneration now ticks; the forge
share recalibrated to 0.5): the figures that moved (J05, F26, U02, J01, J07, F08, F09, F11, J12, J28, J02, J11, J14)
are updated in the sheet `Criticisms`; no verdict changed. The cells below keep the first figures; the sheet is the
reference. Decisions of the user are in its column `Decision` and the changes in `data_tables/balance_changes.xlsx`.

Levers are those of the sheet `Levers` (benign first). Verdicts: **true** (the complaint holds, with its size),
**partly true** (holds in part, or overstated), **false** (the data or the code say otherwise).

How the figures were made (2026-10-09): the reference party of the GameFAQs guide at the reference level of each
checkpoint, with the gear, forged enchantments and item bag of phase 1; "expedition" is up to 20 random battles in a
row on one floor zone, HP and TP carried over and the recovery after each battle applied (`sim/measures.py`
`expedition`, 30 runs); bosses 30 to 40 battles each.

---

## Milestone 1: experimenting without punishment

### T01 EXP and progression (decisions already taken)

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| U01 | A member who is behind takes too long to catch up | true | 10 levels behind: 70 - 144 battles (party 30 - 70); 20 behind: 116 - 311 | **Decided 2026-10-05**: kept curve + B4 (L11, L25): 19 - 36 and 23 - 60; joining level may rise (L31) |
| J37 | The crown takes hundreds of hours | true | One crown: 4,393 battles | **Decided**: B4 + one more point per reset (L27): 257 battles |
| F25 | Crown harsher than in the first game | true | Reset bonus 1 - 5; 4,393 battles | **Decided**: as J37 |
| F93 | Level 75 for every sub event | true | Level 1 to 70: 645 battles | **Decided**: B4 gives 79 |
| S11 | No growth after level 70 | partly true | Growth per level is the same after 70 (99 - 100%); the EXP of a level is 2.2 times higher | Nothing more: the kept curve answers it |
| S12 | Skill points too scarce | partly true | 139 points at 50, 295 at 70, 685 at 99; the guide's plans cost 246 - 440 (reached at 66 - 81) | **To decide**: more points per level from 30 to 70 (L11), or nothing |

### T09 Early game

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| J08 | Empty of TP after 3 - 4 battles before the Maid | partly true (overstated) | No Maid skill, no items: 18.7 - 20 of 20 battles chained; 46 - 68% of TP left after 4 battles, 32 - 59% after 8 | No change of its own; J03 and J10 lower the burn |
| J09 | Misses against agile enemies cause early wipes | true | Plain attack in st00 - st02: median 54 - 70%, lowest 47 - 56%; 56 - 85% of the enemies below 80% | Lower the AGI of the agile enemies of st00 - st02 (L01, benign): lowest 70%, median 80% |
| J10 | An early skill at level 3 - 5 is too costly for the pool | partly true | At levels 5 - 15 a skill costs 9 - 48% of the pool (Danger Shoot 48%, Resurrect 31%); War Cry 7 to 11, Heal 3 to 10 from level 1 to 4 | With J03: flatter TP cost per level for the skills raised early (L12, benign) |

### T03 TP

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| J03 | Raising a skill raises its cost faster than its effect | true | 67 of 84 damage skills give less power per TP at the top level (median 66%); 19 below half (Sharp Stab 20%, Aura Eliminate 28%, Raging Smash 29%, the stings 38%, Geo Break 39%) | TP cost per level (L12, benign): power per TP at the top level at least 85% of level 1, or the level buys something stated |
| J05 | Without a Maid sustained crawling is impossible | partly true | Mid story nearly no difference (Rousset 27: 18.2 against 20 of 20 battles; boss C18 100% both); late it collapses (Actim 50: 4.9 against 13.6 battles; weakened Queen 0% against 100%) | TP outside the Maid line: Auto-Refresh and TP recovery values, price of TP items (L12, L19), with J03. Target: Actim without a Maid 10+ battles and the Queen won |
| F26 | A second Maid is suggested just for TP | partly true | Late only: Actim 13.6 battles with one Maid, 17.2 with two (TP after 8 battles 18% against 40%) | As J05 |

### Doll Master (T05 rows taken into milestone 1)

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| U02 | The Doll Master line is far behind | true | Same slot: Doll Master 15 - 24% of party damage against 17 - 36% as Trickster (45 - 90% of it), fights up to 26% longer; Soul Summoner 8 - 10% against 15 - 16% as Papillon | Data, benign (L12, L10): power, chances and spell power of the hidden doll actions, doll life (effect 147), TP and speed of a cast, Doll Mastery, growth row. Target: within 90% of the other Spieler line in the same slot, keeping its identity (autonomous allies, anti-magic zones, Catalina's healing; docs/CLASS_IDENTITY.md) |
| J18 | Dolls die to the first area attack | false | A doll has 9,999 HP and ends by its count of turns | None (close as not a problem); the weakness is U02 |
| S08 | A summon acts too late in late content | false | Wait 0.25 - 0.64 (median 0.42 at level 90): like the slowest member, sooner than most bosses (0.42 - 0.55) | None on its speed |

### What the user decides for milestone 1

1. S12: more skill points from 30 to 70, or nothing.
2. J09: lower the AGI of the agile early enemies (lowest hit 70%, median 80%).
3. J03, J10: flatten the TP cost per level (power per TP at the top level at least 85% of level 1).
4. J05, F26: add TP outside the Maid line (skills and items) until Actim is crossed without a Maid.
5. U02: raise the doll line through its own tools to within 90% of the other Spieler line.
6. J18, S08, J08: close without a change (false, or overstated).

The changes decided are then written into `data_tables/balance_changes.xlsx`, each naming its rows, and checked with
`sim/measures.py` `check_change` (phase 2, steps 3 and 4).

---

## Milestone 2: combat

Figures of 2026-10-09. "Weapon band": the member at the level, gear and forge of a checkpoint, each basic weapon in
turn, expected damage per unit of time of her best action against the boss of the checkpoint
(`sim/measures.py` `weapon_band`; TP and survival not counted).

### T02 Speed and weapons

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| J01 | A fast weapon acts 2 - 3 times per heavy one | partly true | Same character late: Kukri every 0.21, Heavy Axe every 0.40 (1.9 actions); but the heavy weapon gives the most damage per time everywhere (Kukri 29 - 41% of it) | No change; survival in the final pass |
| J06 | Guns are dead | partly true | 3 of 13 bow skills accept a gun; 7 unique guns, ranks 1.4 to 2.9 | **To decide**: more bow skills for guns (L13, structural) or none |
| F10 | A gun is not a bow | true | 10 of 13 bow skills refuse a gun | As J06 |
| J07 | Two-handed axes and swords are dead | false | Two-handed weapons lead damage per time at C18, C34, P24; one-handed 47 - 84% of them | None for damage; survival in the final pass |
| F08 | One-handed better at the end | false (basic pieces) | P24: Heavy Axe 100 / Hand Axe 84, Heavy Lance 100 / Lance 49, Tachi 100 / Tantou 48; unique pieces not modelled | Look again with unique pieces (T10) |
| F09 | Whips are garbage | true | Mistress with a whip: 39% (C34), 12% (P24) of the Dark Lord | Whip stats and whip skills (L14, L12): Mistress at half the Dark Lord or more |
| F11 | Basic attacks useless late | true | Plain attack 15 - 70% of the best action at C18, 0 - 27% at P24 | **To decide**: raise Double / Triple Attack and Barrage (L12), or accept |
| J12 | Promotion to Berserker slows and kills | false | Fighter 14 Longsword to Berserker 15 Claymore: damage per time x2.3, wait +3% | None |
| J28 | Lightning March mandatory for heavy weapons | false | The song adds 5 - 26%; the Heavy Axe is best with or without it | None |
| F24 | Physical skills slower than in the first game | partly true | 73% of 64 damage techniques below speed 1 at top level (median 0.90); no first-game data to compare | Skill by skill in T06 |

### T04 Magic

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| J02 | Casters far worse than physical burst late | false | Witch with top spells: 172 - 191% of the Dark Lord at C38, P24, P49 (resistances counted); 88 - 97% of chants completed | None as stated |
| J11 | Magic spikes mid game, then plateaus | partly true | Mage over Dark Lord: 41% (C07), 98% (C13), 189% (C18), 333% (C25), 309% (C34), 191% (C38), 172% (P24, P49) | **To decide**: soften the peak (tier 1 - 2 power, L12) or keep it |
| J14 | Bosses interrupt casters routinely | false | 85 - 98% of chants completed against 7 bosses; at most 0.7 broken per fight | None |
| J33 | Top spells cost much for little | partly true | Tier 4 single: power x2.5, TP x2.6, chant 34% slower; power per TP about equal | **To decide**: faster chant for tier 4 (L12) |
| F06 | Mage teams need one sealbook; anti-magic bosses | partly true | Anti-magic cells: C29a and P07, P13, P25, P47; no sealbook dependence in the model | None; items and dolls answer those fights |
| F13 | Magic defence buffs barely matter | partly true | +25% magic defence cuts a spell by 11 - 15% | **To decide**: larger values (L12) |

### T07 Ailments, debuffs and locks

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| J31 | Tinker Squash locks a boss or does nothing | true | 25 - 43% delay per hit, no resistance roll; immune: 14% of story bosses, 56% of postgame bosses | Immunity bits or lower chance on bosses (L26): no boss lockable |
| F14 | Resistance 100 makes resistance skills useless | partly true | Model party: elemental resistance 60 at 90 - 99; 100 only with full end-game enchanting | **To decide** in T10 |
| F15 | Ailments blocked by harder bosses | true | Postgame bosses immune: freeze 91%, stun 93%, paralysis 87%, sleep 65%; death and petrification 100% of all bosses | Open some bosses to slow, sleep, silence (L26, L02) |
| F23 | Turn skipping stacks across the party | true | Magnificent Steps 0.07 and Warning Shot 0.06, no immunity: 13% of enemy turns per pair, 33% with three, 49% with five | Lower values or boss resistance (L12, L26) |
| S05 | Ailments waste turns in common fights | true | A random battle lasts 2.6 - 3.3 actions per member | **To decide**: accept, or richer side effects |
| S06 | Debuffs help only marginally | true | DEF -10 to -20% adds 2 - 5% damage | Larger debuff values (L12) |

### T12 Common enemies and pace

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| S01 | Common fights too long for their EXP | partly true | Fights are short (2.6 - 3.3 actions per member); the length is 25 - 35 battles per level | Covered by the decided curve (15 - 19) |
| S02 | Common enemies too resistant | partly true | Lowest physical resistance 50+: 0% early, 30% at 60 - 79, 77% at 80 - 99 | **To decide**: lower late physical resistances (L02) |
| S03 | Enemy passives trigger too often | true | Enemy median above the party's top: Reprisal 0.25 / 0.18, Auto-Guard 0.30 / 0.12, Counter 0.15 / 0.12, Ecstasy 0.5 / 0.15 | Bring the four to the party's top (L08) |
| F12 | Dark Aura punishes short range late | partly true | 21% of enemies of level 60+, 13 of 55 postgame bosses | **To decide**: fewer carriers or lower value |
| S27 | Damage given and taken feels wrong | to measure | Too vague alone | Verdict from R03 and R08 in the final pass |

### What the user decides for milestone 2

The rows marked **To decide**, and whether to apply the proposals of the rows marked true. The rows found false (J07,
F08, J12, J28, J02, J14) close without a change once confirmed.

---

## Milestone 3 (started): T11 Information

The class rows of T05 and the skill rows of T06 rest on the combat rules of milestone 2 (BALANCE_PLAN.md section 3,
phase 3), so their verdicts wait for the decisions of milestone 2. The two data rows of T11:

| Row | Complaint | Verdict | Figure (vanilla) | Proposal |
|---|---|---|---|---|
| J34 | Berserk drops DEF to zero | false | DEF -11 to -25% for 4 - 8 turns, attack +20 to +50% | None |
| J13 | Mercenaries act unpredictably, undocumented | partly true | Weighted random scripts of the enemy kind, 1 - 3 sets each; data, not shown | **To decide**: describe each mercenary in its in-game text (L20) |
| S23 | Order of actions not shown | future idea | Not evaluated (the user, 2026-10-07) | None |

---

## Milestone 3: T05 Classes, first measures (2026-10-09, before the audit of the simulator)

On the Balance variant (milestones 1 and 2 decided), each advanced class in the first Papillon slot of the reference
party (`sim/measures.py` `slot_share`, 15 battles; bosses C34 at 50, C40 at 64, P24 at 90). The user asked for an
audit of the simulator before relying on these figures; they are to be measured again after it.

| Class | Share of party damage C34 / C40 / P24 | Wins C40 / P24 | Reading |
|---|---|---|---|
| Samurai, Sniper (the band) | 37 - 45% | 67 - 87% | reference |
| Kunoichi | 6 / 11 / 4% | 53 / 67% | far behind (F04, J27, F88) |
| Magical Princess | 24 / 30 / 24% | 67 / 73% | behind (F05, J25) |
| Joker | 30 / 28 / 25% | 13 / 40% | weak, dies under Trump Card (F17, J32) |
| Mistress | 29 / 37 / 17% | 87 / 80% | weak late |
| Soul Summoner | 47 / 46 / 24% | 67 / 60% | weak late |
| Papillon | 27 / 37 / 30% | 80 / 60% | a little behind, wins on par |
| Treasure Hunter | 31 / 29 / 46% | 53 / 60% | fine |
| Witch | 67 / 49 / 42% | 40 / 73% | above (T04) |

Supports in an attacker slot, the Diva kept (wins C34 / C40 / P24): Papillon 100 / 80 / 60, Bishop 100 / 87 / 93,
Etoile 100 / 80 / 100, second Maid 100 / 80 / 73, **Sage 100 / 7 / 47** (J23).

## Milestone 3: T05 Classes, measured again after the audit of the simulator (2026-10-09)

The audit (`docs/generated/SIM_AUDIT.md`) fixed faults that hid whole classes: the Kunoichi fought without a throwing
weapon or a second blade (atwiki dt2-2 page 142), Trump Card was never used (the boss condition was never true), the
random skills of the Trickster line scored nothing, buff rules took hit properties for statuses, the Sage had no rule
for her party buffs, nobody cured petrification. Same measure as above.

| Class | Share of party damage C34 / C40 / P24 | Wins C40 / P24 | Before the audit | Reading |
|---|---|---|---|---|
| Samurai, Sniper (the band) | 41 - 51% | 73 - 87% | 37 - 45% | reference |
| Dark Lord | 55 / 66 / 62% | 80 / 100% | | top |
| Kunoichi | 17 / 23 / 15% | 73 / 73% | 6 / 11 / 4% | still the lowest attacker (F04, J27, F88) |
| Magical Princess | 27 / 33 / 31% | 87 / 60% | 24 / 30 / 24% | a little behind (F05, J25) |
| Joker | 42 / 53 / 20% | 47 / 60% | 30 / 28 / 25% | strong early, falls late (F17, J32) |
| Mistress | 36 / 41 / 19% | 100 / 93% | 29 / 37 / 17% | weak late in damage, wins |
| Soul Summoner | 52 / 45 / 32% | 60 / 67% | 47 / 46 / 24% | fine; no sealbook modelled (Soul Seal) |
| Papillon | 30 / 41 / 34% | 73 / 80% | 27 / 37 / 30% | on par |
| Treasure Hunter | 32 / 30 / 53% | 20 / 73% | 31 / 29 / 46% | fine late, weak at C40 |
| Witch (mage) | 69 / 51 / 40% | 53 / 87% | 67 / 49 / 42% | above early (T04) |

Supports in the same slot (wins C34 / C40 / P24): Bishop 100 / 53 / 93, **Sage 100 / 67 / 80** (was 100 / 7 / 47; the
C34 fight lasts 62 s against 37), Etoile 100 / 80 / 100, second Maid 100 / 73 / 87.

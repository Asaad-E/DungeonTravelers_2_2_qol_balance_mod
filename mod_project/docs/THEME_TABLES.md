# Theme tables for the user

One short table per theme (BALANCE_PLAN.md section 3, phase 2, step 2): each row of the register, its verdict with
the figure that shows it, and the change proposed. **Nothing here is applied**: the user decides each theme. The
full wording of each row, its figure and its source are in the sheet `Criticisms` of
`data_tables/balance_criteria.xlsx` (columns `Verdict`, `Vanilla_Result`, `Proposal`); the count is
`docs/generated/VERDICTS.md`.

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

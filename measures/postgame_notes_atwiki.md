# Postgame: what the Japanese pages say, and two effects read (2026-10-11, second reading)

Read with the built-in browser from w.atwiki.jp/dt2-2 (WebFetch gets 403). Paraphrased, never copied. To be written
into `data_tables/sim_setup.xlsx` (sheets PostgameBosses, GuideDifficulty, Preparation) once no pass is running.

## By checkpoint

| ID | Boss | Page | What the page says | Class it suggests |
|---|---|---|---|---|
| P01 | Aradia, 1st | 29 | Only a first showing: a party that beat Demiurge wins with room | easy |
| P05 | Euthys | 186 | His physical blows after his self buff kill in one hit: remove the buff early | normal |
| P06 | Overdue | 227 | High DEF, physical resistance and Auto-Guard: earth enchant for physical parties. Under about 3,000 HP he chants a spell of 2,000 to everyone: burst, break the chant, or Insurance / clones | hard |
| P07 | Vitoria, Siegdrad, Airavata | 225 | Magic forbidden. Fire resistance first (Super Napalm), then water. Siegdrad (back row, party stun, healing doll, counter passives) is the threat; the fight eases once one of the three falls, Vitoria the easiest | hard |
| P10 | Kuchinawa | 29 | Water zone and physical attack zone: a Fighter line member with Enchant Ice deals 2,000 or more; the boss kills in one or two hits. A short fight; hard to win for sure, several tries | hard |
| P11 | Aradia, 3rd | 99 | Stronger than before, but the water zone lets Frost Slash and Enchant Ice hit hard: easier than the last one for some parties | normal |
| P14 | Murasaki Shikibu | 227 | Physical defence zone, two Beard Knights in front | - |
| P16 | Aradia, 5th | 207 | Murder License: before each action of Aradia one member may die at once. Without instant death immunity (two accessories, two sealbooks) or high earth resistance the fight cannot be played; Moon Curtain is dispelled by Dark Blast | hard without the piece, normal with it |
| P41 | Citlalinicue | 333 | Fire zone she barely uses. Mostly single blows: a Valkyrie tank makes it stable. Her Carol heals 2,000 a turn: silence or break it. Fight from range (her gravity passive); dispel her self buff | normal |
| P42 | Marduk | 333 | The hardest of the four: DEF 2,450, physical hardly lands (only Trump Card), his Salsa deals 250 to all each turn, a full self buff, a satellite that cannot be dispelled. Killed with the party's own Salsa and Witch crit magic; several players report not winning without crowns | very hard |
| P43 | Arjuna | 333 | Opens with a wall against short and mid range, and uses it again: ranged or magic. Almost all stab damage in a physical defence zone: with a tank the easiest of the four. Instant death on his plain attack: the cover member needs the immunity | normal |
| P44 | Yoshitsune | 333 | Lightning zone. Shiden (party lightning, paralysis) and his eight clones with a speed and attack buff are the threats: bring a dispel. Lowest defence of the four: a rush with enchanted blows works | normal |
| P45 | Zouchou Kuma | 334 | Physical defence zone; two escorts with Warning Shot: Cover with Parry, or the feather that voids stab. His lightning row spell on turn one and at half HP; after his magic buff a spell deals 2,000 or more: dispel (it lands badly) or break the chant | hard |
| P46 | Jikoku Peggin | 334 | The three hit hard physically; the escorts' Trump Card at half HP. The boss dances (turn cancel) and lowers accuracy | hard |
| P47 | Koumoku Mary | 334 | Magic and songs forbidden: heal with items and dolls. Murder License every turn: instant death immunity or earth resistance on everyone. Two summoners: Lizerietta helps. All three open to slow | hard |
| P48 | Bishamon Peggy | 334 | Dark Blast deals a fixed 1,111 to all: members under that HP cannot fight. High RES on the three: physical, a Valkyrie best (the feather voids two stab skills and Triple Attack). The Geass that lowers every resistance makes ailments land. Kill the Pandarian first | very hard |

A comment on page 333 (2023): at mean level about 95 without resets, every member of the brigade but Marduk fell
easily to element chains and Daedalus Attack.

## Two effects, read in the executable

**Heretic Samsara (291)**, bearers Demiurge (C40), Riko the Reclusive (P35), Ma the Eccentric (P40). Read at
`0x47f739`, `0x438e53 - 0x438fef` and `0x4fc76f - 0x4fc880`:

* Once damage takes the bearer under half its max HP the value of the status becomes 1.
* From then on, at the battle update of its turn, for each of the eight damage types (stat indices 6 to 13: slash,
  stab, bash, fire, water, wind, earth, lightning) a status 416 + n is put with value `(rand(2) + 1) * 50`: 50 or 100.
* When the stats of a unit are recomputed (`0x4fbdd0`), after the clamp of each resistance, a status 416 + n
  **replaces** that resistance with its value (`0x4fc76f`: the eight fields at +0x6C to +0x88).

So under half HP each resistance of the bearer is 50 or 100, drawn again every turn: damage x0.75 or x0.5
(FORMULAS 2: `(100 - resistance * 0.5) * 0.01`), and an ailment of that element halved or blocked (5b). For
Demiurge, whose eight resistances are 50, the second half of the fight takes x0.625 of the first on average instead
of x0.75. The sheet EffectRules says "1 or 2": it is 50 or 100.

**Murder License (319)**, bearers Aradia of the 5th fight (P16), Koumoku Mary (P47), Carmilla (a common enemy). The
rule written in the sheet EffectRules ("its action is replaced") is wrong. Step 12 of the turn (`0x43736a`): a unit
that holds status 319 builds an action from the skill linked to the status, on one target drawn at random
(`0x437416`: rand over the list, then `0x415200`). That much is read. That the bearer's own command still follows
is NOT read in the code yet: it is what the Japanese pages 207 and 334 say (before each action of the bearer one
member may die at once; instant death immunity or earth resistance stops it), and a boss that lost every turn to
this would not match them. Still to read: which skill is linked (the status object, `+0x34` / `+0x3C`), its chance,
and the step after state 0xB.

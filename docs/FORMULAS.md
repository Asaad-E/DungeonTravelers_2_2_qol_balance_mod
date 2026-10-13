# Battle formulas, read from the executable

Source: `DT22_en_unwrapped.exe` (32-bit, image base `0x400000`). The battle code prints every step of its calculations through debug messages, and those messages are still in the binary: they are the formulas in the developers' own words. They are listed, generated, in `docs/generated/EXE_FORMULA_STRINGS.md`. This file is their reading, checked against the instructions around each message (`tools/exe_reader.py`).

Tags: **[message]** stated by a debug message. **[code]** read in the instructions, with the address. **[open]** not read yet.

Nothing here was measured in the game. Constants are quoted from the code, with the address where they are used.

---

## 1. How the code reads its inputs

| In the code | Meaning | Evidence |
|---|---|---|
| `call [vtable+0x34]` with a pushed index | A stat of a unit. `1` DEF, `2` INT, `3` RES, `4` DEX, `5` AGI; `0` ATK | The message next to each call names the stat (`0x44aa84`: index 4 is "own DEX"; `0x44aace`: index 5 is "enemy AGI"; `0x44b97d`: index 1 is "enemy DEF") |
| `mov edx, N` + `call 0x47e340` | The active effect with id `N` on a unit (a buff, a skill in use), then its value through `call [vtable+0x2c]` | `N` are the effect ids of `CommandData` (26 weapon attack, 161 physical attack, 162 physical defence...) |
| `call [vtable+0xf0]` with an id | How many pieces of equipment carry an enchantment | Followed by a multiplication by the size of one enchantment and a cap |
| `call 0x414560` | The debug print | Every message goes through it |
| `call 0x490790` | Random integer below the pushed bound | Used for every roll |
| `call 0x5587c0`, `0x5576a0`, `0x5593f0` | The record of an enemy (`EnemyStatusData`), of an enemy attack (`EnemyAttackData`), of a piece of equipment. They return the record itself, so the offsets after them are the offsets of the file | Each is `map lookup; add eax, 0x18` |
| `mov ecx, [0x7389d8]` (or another map) + `call 0x507310` + `mov eax, [eax]` | The same lookup written inline. Here the offsets are those of the file **plus `0x18`** | `0x4f2150` reads `[eax + 0x5c]`: file offset `0x44` |

---

## 2. Physical attack (`0x44a850`, "物理攻撃の計算")

### 2.1 Hit chance **[message + code]**

```
A     = 0.885 * (100 + own DEX) / (100 + target AGI) + accuracy of the skill        (0x44aac1; skill: effect 29)
B     = (own accuracy buffs - target evasion buffs + A) * 100                        (0x44acdd)
final = (B + own accuracy enchantments - target evasion enchantments) / (1 + the target's Barcarole)   (0x44ae94)
final is kept between 5 and 100                                                      (0x44ae84, 0x44ae8c)
```

* Accuracy buffs read: effects 166, 197, 337. Evasion buffs read: 164, 198, 338; 253 against a stab blow (16.7).
* Enchantments: each piece counts 4, the mini version 2, the sum capped at 50 (`0x44ad3d`, `0x44ad5b`): accuracy UP is +4 points per piece, MiniUP +2, at most +50; the same for evasion.
* Later changes of the final value, each with its own message: fixed accuracy (effect 55), a direct accuracy value (effect 72), sleep, and two effects that work only on adults or only on minors.
* After the fixed value and sleep the chance of a blow is kept between 5 and 100 **a second time** (`0x44afbe - 0x44aff8`), before the two effects of age: a fixed accuracy below 0.05 hits 5% of the time. The spell function has no second limit (`0x44da2b - 0x44dab1`): there a fixed value passes 25 and 95. Read on 2026-10-11.

### 2.2 Attack value **[message + code]**

```
attack A = own ATK * (2 + swing)                                                     (0x44b36e)
swing    = (random integer in [0, 2n] - n) / 100,   n = 100 * swing of the weapon    (0x44b2f1 - 0x44b339)
attack B = attack A * (1 + modifiers) * (1 + enchantments * 0.01)                    (0x44b74a - 0x44b767)
```

* **Swing** is a property of the weapon (float at `0x48` of the equipment record in memory) or of the enemy (float at `0x40` of `EnemyStatusData`: the field so far called "float 0x40" is the enemy's damage spread).
* **Modifiers are added together, not multiplied**: effect 26 (the power of the skill), 443 (Elbow Grease), 111 (Heavy Lance bonus), 286, 161 (physical attack buff, War Cry and the like), 195, 335, 219, and a term from the character (`0x56e160`). A skill of +100% under a +18% buff is `1 + 1.00 + 0.18`, not `2.00 * 1.18`.
* Enchantments: physical attack UP counts 4 per piece, MiniUP 2, capped at 50 (`0x44b6bf`, `0x44b6da`).

### 2.3 Defence value **[message + code]**

```
defence A = target DEF * 1.35 * (1 + modifiers) * (1 + enchantments * 0.01)          (0x44b9c0)
```

* Modifiers, added together: effects 28, 162 (physical defence buff or debuff), 187, 196, 205, 336, 219.
* Enchantments: physical defence UP 4 per piece, MiniUP 2, capped at 50.

### 2.4 Damage **[message + code]**

```
damage A = attack B * n - defence A               n: effect 73 ("Damage xn"), else 1; effect 69 ignores defence
damage B = damage A * range * damage cut
damage C = damage B * race bonus * resistance * zone * defending * element reduction * critical
final    = damage C * (1 + other bonuses)
```

* **Defence is subtracted.** With `ATK * 2` against `DEF * 1.35`, a hit does nothing until attack B passes defence A; past that point every further point of attack is pure damage. This is the "flat" behaviour the guide describes, and the reason a percentage on a skill is worth far more than its figure when defence is close to attack.
* **Damage cut** (`0x44bb82 - 0x44bc67`): 1 minus 0.10 per piece of one enchantment, 0.05 of its mini version, 0.08 and 0.04 of a second pair, never below 0.75. That is the cap of 25% the Japanese wiki reports.
* **Resistance** **[message]**: `(100 - resistance * 0.5) * 0.01`. Each point of resistance removes half a percent; 100 halves the damage; a negative resistance adds.
* **Race bonus** (`0x44bfe3 - 0x44c2cb`): enchantments against a kind of enemy add 0.30, 0.15 or 0.60 per piece according to their tier; effects 87 and 88 are read here.
* **Defending** halves the damage (`0x44c576`).
* Changes of the final value, each with its message: Warning Shot, a guaranteed minimum, wide magic guard, Positive Trance (`(Pep - 100) / 100` of the damage when Pep is above 100, `0x44ccce`), sleep, a bonus against enemies with an ailment (0.15 per piece of an enchantment, `0x44cd83`), double damage against the Magic User line, fixed damage, damage only to the living.
* **Range** (`0x44a7d0`, `_GetAttackRangeRevision`) **[code]**: the distance is 0 when attacker and target are both in the front row, 1 when one of them is in the back row, 2 when both are (`0x44a7a0`). A short-range attack does full damage at distance 0, 0.75 at 1 and 0.5 at 2; a mid-range attack does 0.75 at distance 2 and full damage otherwise; long range and no range always do full damage. The lesson of the game states exactly this.
* **Zones** (`0x44fbb0`): see 2.5. A zone multiplies attack A, before defence is subtracted; this is why a zone that doubles attack more than doubles damage.
* **[open]** the critical multiplier, the size of the guaranteed minimum.

### 2.5 Chant interruption **[message + code]** (`0x44d001 - 0x44d259`)

```
rate A = damage taken / (max HP * 1.5 + (1 + interruption modifier))     kept between 0 and 0.95
rate   = rate A - enchantments                                           kept between 0 and 0.95
```

* The chance to break a chant grows with the damage of the hit against the caster's max HP: a hit for 30% of max HP interrupts 20% of the time, a hit for 75% half of the time.
* The interruption modifier is effect 264 (Concentrate), the first status of that effect in the list of the target
  (`0x44cfad`). Read again on 2026-10-12: the debug message writes `HPMAX * 1.5 * (1 + modifier)`, but the code adds
  the two terms (`0x44d02b` adds 1 to the modifier, `0x44d03a` multiplies max HP by 1.5, `0x44d042` is `addss`, bytes
  `f3 0f 58 c1`). With values of 0.1 to 0.5 against a max HP in the hundreds, **Concentrate changes the rate by less
  than a thousandth: in the game as shipped it does nothing**. One byte (`58` to `59` at `0x44d044`)
  makes it the product the message tells: row X14 of the sheet `ExePatches` (lever L45), in the Balance variant only
  (decided 2026-10-12, for every unit that has the passive). The QoL variant keeps the text of the game for the
  passive, with no figure.
* Enchantments subtract 0.10, 0.06 or 0.03 per piece according to their kind; one adds.
* The roll is a number below 100 against the rate cut to an integer percent (`0x44d1f3`). Only the physical function rolls it; a spell breaks a chant only through the second roll of a critical (16.7). **A critical hit rolls a second time**: a number below 100 under 33 also breaks the chant, whatever the damage (`0x44d228 - 0x44d246`). This is the "1 in 3" of the lessons.

---

### 2.5 Damage zones of the map (`0x44fbb0`; factors loaded at `0x44993a`) **[code]**

A cell of the map has two zone slots (offsets 0x8 and 0xC of its record) and names the zone of the floor it belongs
to (offset 0x18). When a battle starts on it the five factors of that zone are copied from the floor file.

```
attack A = attack A * up factor of the side      when a slot of the cell is 3 (one side) or 4 (the other)
         * down factor of the side                when a slot is 5 or 6
         * element factor                         when a slot is 7, 8, 9, 10 or 11 and the attack has that element
```

The factors are data, five floats per zone of a floor (`tools/floor_data.py`, `zone_factors`): vanilla uses between
2 and 2.35 for the up and element factors and between 0.5 and 0.75 for the down factors. The flag the function receives
is the kind of the attack, not a side: a blow passes 1 (`0x44b39d`) and reads slots 3 and 5, a spell passes 0
(`0x44dcb0`) and reads slots 4 and 6. So 3 and 5 raise and lower physical attack, 4 and 6 magic attack, for every unit
of both sides; 7 to 11 are fire, water, wind, earth and lightning. Read on 2026-10-07.

## 3. Magic attack (in the same file, after `0x44d366`) **[message]**

```
hit:      A = accuracy of the spell + (own INT - target RES) * 0.002 + Loose Spirit
          B = A * 100 + own enchantments - target enchantments
          final = (B * (1 + own magic accuracy buffs) / Nocturne) * (1 - target magic evasion buffs)
attack A  = own INT * (2 + swing)
attack B  = (attack A + power of the spell * (1 + Magic Mastery)) * (1 + modifiers) * (1 + enchantments * 0.01)
attack C  = attack B * (1 + modifiers) * (1 + element boost)
defence A = target RES * 1.5 * (1 + modifiers) * (1 + enchantments * 0.01)
damage A  = attack C - defence A
damage B  = damage A * (1 + power boost) * (1 + damage cut)
damage C  = damage B * resistance                 resistance = (100 - resistance value * 0.5) * 0.01
final     = damage C * (1 + other bonuses) * critical
```

* A spell adds its **power** to `INT * 2` before the multipliers; defence is `RES * 1.5`, also subtracted.
* Read in the code (`0x44d370`): the hit chance is kept between 25 and 95 (`0x44da2b`, `0x44da37`); magic accuracy enchantments count 3 per piece, capped at 50 (`0x44d67b`, `0x44d699`), and their MiniUP versions (40, and 44 for magic evasion) 1 per piece: the count is added as it is (`0x44d6a3 - 0x44d6bd`, `0x44d722 - 0x44d742`); attack A is `INT * (2 + swing)` (`0x44dc97`); the power of the spell is effect 1; the enchantments that boost the magic of one element add 0.20 per piece (`0x44e070` and the five blocks after it, effects 325 to 329).
* **Critical Magic** (`0x44ed9e - 0x44edfa`): when the caster has effect 301 active, a number below 100 under 20 makes the
  spell critical, and the factor is 1.25. Neither figure comes from the skill. A critical spell breaks a chant with the
  same second roll of 33 in 100 as a critical blow (`0x44f13f`).
* **Received magic damage** (`0x44e72e - 0x44e812`): enchantments 68 to 71 take 0.10, 0.05, 0.08 and 0.04 per piece, and
  the sum stops at 0.25. The reductions by race of the attacker (enchantments 227 to 244) follow.
* **Cap** (`0x44f0ce`): a spell whose skill carries effect 296 deals at most that value.
* No floor was found at the end of this function: unlike a blow, a spell has no guaranteed minimum.

## 4. Critical hits (`0x44f190`, returns the factor of the hit) **[message + code]**

```
value A = (own DEX * 0.2) / (own DEX + target AGI) * 100                              (0x44f1d8 - 0x44f20d)
value B = (own level - target level) * 0.5, not below 0                               (0x44f250, 0x44f258)
rate    = (value A + value B + skill) * (1 + own enchantments * 0.02) * (1 + target enchantments * 0.02)
rate    = rate + 5 * hits already landed by this attack        only with effect 125   (0x44f49b)
rate    = between 5 and 50; the floor is 20 with a piece of enchantment 268           (0x44f4c3 - 0x44f4ea)
factor  = 1.25 when a roll below 100 is under the rate (cut to an integer), else 1    (0x44f599 - 0x44f5b2)
```

* skill: effects 31 (critical rate of the skill or buff), 32 (the target's vulnerability), 174 and 211, added together.
* Own enchantments: 4 per piece of 45 and 2 per piece of 46, at most 50. Target's: -4 per piece of 47 and -2 per piece
  of 48, not below -50 (`0x44f325 - 0x44f459`). Through the factor of 0.02 a piece of 45 is worth +8% of the rate.
* After the limits, effect 70 replaces the rate with its own value (`0x44f4f4`), and effect 110 makes it 100 against
  a target of race 2 (`0x44f523 - 0x44f58d`; the message calls it a critical hit on beasts).
* The factor 1.25 is the "critical value" that multiplies basic damage C (section 2.4).

**Minimum damage** (`0x44cb12 - 0x44cb4e`, physical): when the final figure is 0 or less it becomes 3, or 1 or 2 at
random when the hit was critical. Warning Shot (flag 0x105 of the attacker) first cuts the final figure to 3/10.

## 5. Order of turns (`0x4499d0`, `Battle::CBattle::_SetTime`, "行動時間の計算") **[message + code, checked]**

```
base A = (stat + 100) / 200          stat: AGI; INT or RES while chanting, by a flag of the skill          (0x449b4c)
speed  = ( base A * (1 + r)  -  (weight / 12) * (1 + level / 100) ) * F1 * F2 * slow * 0.5
         r: random, one of 0, 0.01 ... 0.05                                                                 (0x449bd4)
value  = speed * (1 + buffs + enchantments)      * 1.15 when defending, * 1.20 when escaping    (0x44a316 - 0x44a335)
value is capped at 0.92                                                                            (0x44a341)
wait until the next turn = 1 - value
```

* **weight** is a virtual call of the unit (slot `0xf4`). For a player it is the delay multiplier of the rank of the equipped weapon (the float of `WeaponRankData`: 1.00 for A+ up to 2.90 for F). **For an enemy it is the float at `0x44` of `EnemyStatusData`** (`0x4f2150`, slot `0xf4` of the enemy class) **[code]**. Summons and mercenaries take a rank index from their own record and return the delay of that weapon rank (`0x4feeb0`, `0x5001d0`). Ordinary enemies carry weights in the range of the weapon ranks; bosses carry a fraction of the lightest weapon, which is why they act several times per turn of the party: it is one number per enemy, in data.
* **The weapon term is subtracted from the base and grows with the level of the unit.** A slow weapon does not multiply the wait: it takes a bite of `weight / 12 * (1 + level / 100)` out of a base that depends on AGI. The slower the class, the larger the share it loses, and the bite doubles between level 1 and level 99. This is the mechanism behind the complaint about two-handed weapons, and it means that changing the twelve multipliers does not act as a percentage.
* **`F1`, `F2`**: factors of the action; 1 for a plain action such as defending. `F1` is the speed of the action itself, the one the skill box shows (higher is sooner): `[vtable+0x154]` of the skill for a player (`0x449cb0`), the float at file offset 0x44 of the attack for an enemy (`0x449d53`), left at 1 for an enemy attack that is chanted. `F2` is the speed of the chant, used while the unit is chanting: `[vtable+0x158]` for a player spell (`0x449d9a`), the float at file offset 0x34 for a chanted enemy attack (`0x449e20`). Neither is a power.
* **slow**: 0.5 while the unit has status 122, else 1 (`0x449e65`).
* **buffs**, added together. Acting: effects 168 (speed buff), 217, 221, and 261 while HP is at or below 40% of max; plus 201, 340, 276, 277 and, in one case, 316. Chanting: effects 214, 265, 281.
* **enchantments**: acting, +0.10 per piece of enchantment 51 (speed UP), +0.05 per piece of 52, -0.10 per piece of 53; chanting, +0.20 per piece of 54 (chant speed UP), +0.10 per piece of 55, -0.20 per piece of 56. Each sum is kept between -0.5 and +0.5 (`0x44a1b3 - 0x44a1d4`): five speed UP or three chant speed UP reach the cap.
* **The cap of 0.92 is the "soft cap" of the guides**: no unit waits less than 0.08. Past it, AGI and speed gear do nothing.
* Enchantment 298: with it, a chant gets +0.25 on the value (still capped at 0.92) (`0x44a359 - 0x44a390`).
* At the start of a battle the gauge of each player unit is random (`0x449194`); in one battle of five the order of everyone is random.

**Check against a player test** (Japanese wiki, pages/105.html, "行動速度アップ・詠唱速度アップの上限について"). Unit A: rank A weapon, AGI 261, five speed UP. Unit B: rank B weapon, AGI 47, from 0 to 6 speed UP. Both only defend; the test counts the turns of A during 10 turns of B.

| Speed UP on B | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Measured by the players | 80 | 76 | 71 | 67 | 63 | 58 | 58 |
| This formula | 80.5 | 76.1 | 71.6 | 67.2 | 62.7 | 58.3 | 58.3 |

Computed with A at the cap (wait 0.08) and B at level 1 (AGI 47 at level 1 is a crowned character, which is how these tests are run): base `(47 + 100) / 200 * 1.025`, weapon term `1.60 / 12 * 1.01`, `F1 = F2 = 1`, defending. The same test with chant speed UP stops improving at three pieces, as the cap of 0.5 on a sum of 0.2 per piece predicts. No constant was fitted.

## 5b. Ailments against resistance (`0x481ea0` for poison; one such method per ailment) **[code]**

Each ailment is a command class of its own (the class of an effect id is set in `Command::CreateCommand`, `0x47b220`); the roll is its virtual method at slot 6.

```
blocked outright if the target already has the ailment, wears an immunity enchantment, or is an enemy flagged immune
chance = value of the effect * 100
chance = chance - (resistance / 10, as integers) * chance / 10          (0x481fc2 - 0x481fea)
the ailment lands if a random number below 100 is below the chance      (0x48201b)
```

* **resistance** is the target's resistance to the element the ailment belongs to, read as a stat (`call [vtable+0x34]` with index 10 for poison: water). The indices 6 to 13 are the eight resistances in the order of the enemy record: slash, stab, bash, fire, water, wind, earth, lightning.
* **Resistance works in steps of ten points**: 0 to 9 change nothing, 50 halves the chance, 100 removes it (the "Block" the game announces). A negative resistance raises the chance.
* When nothing can land (chance at or below 0) the result is "block"; otherwise a failed roll is a "miss".
* In one context (the command comes from a source of kind 4) enchantment 269 on the target takes a flat 15 points off, and enchantment 138 blocks. Those two are "Less likely to trigger traps" and "Nullify gas traps": the context is a trap, and neither acts on an ailment of a battle.
* The chance is worked out in single precision and cut to an integer before the roll (`0x48201d`; `sim/formulas.py` ailment_threshold). Sleep is the same code with wind resistance (`0x4828a9 - 0x482928`, read on 2026-10-11).
* **[open]** turn delay (effect 54) and the skills that skip a turn (Warning Shot, Magnificent Steps): their rolls are separate code.

## 5c. Turn delay (effect 54, `0x423a41`) and the immunity flags of an enemy **[code]**

```
immune  when the target is an enemy whose flag has bit 12 set                              (0x423a9b)
lands   when a roll below 100 is under int(value of the effect * 100)                      (0x423b1b - 0x423b33)
```

* No resistance and no memory enter: the chance is the value of the skill every time, so a delay can be repeated
  without limit against any enemy that lacks the bit. The bit is data, one per enemy.
* When it lands, the target exchanges its place in the order with the unit that comes right after it (their gauge values are swapped, `0x423b86 - 0x423b97`); the last unit of the order cannot be delayed.
* The same flag word of `EnemyStatusData` (0x3C) holds one immunity bit per ailment, each tested by the code of that
  ailment before its roll: 2 stun, 3 sleep, 4 silence, 5 petrification, 6 instant death, 7 freeze, 8 poison,
  9 paralysis, 10 shadow sew, 11 slow, 12 turn delay. Bit 14 works the other way: set, the enemy can be turned into a
  snack. `tools/enemy_data.py` names them; the share of immune enemies per level band is in the generated baseline.

## 6. Other formulas stated by the messages **[message]**

| What | Formula |
|---|---|
| Escape | `0.3 + (own AGI - average enemy AGI) / 50 + skill`, then a correction by the number of attempts |
| Steal | `0.5 * (own DEX + 50) / (target AGI + 50) * factor` |
| Healing | Read from the code: section 6b |
| EXP after a battle | Read from the code: section 6c |
| Pep | Raised or lowered by listed events: giving or taking a critical hit, using a skill, the last blow, being defeated, traps, dodging, eating liked or disliked food, joint skills, ending a battle with an ailment |

The messages also name every chance roll of a passive or unique skill as it is rolled (Auto-Guard, Double and Triple Attack, Counter, Parry, Cover, Warning Shot, Support Shot, First Grid, Arcane Shield, Shadow Heart, Tranquil Song, Overstock Clearance, Undaunted Spirit...), which locates the code of each.

## 6b. Healing (`0x48d730`, called by the command of effect 103 at `0x481838`; cap `0x48c5c0`) **[code]**

```
amount = own RES * r * coefficient * (1 + Heal Mastery)        r = 0.48, 0.49, 0.50, 0.51 or 0.52   (0x48d873)
amount = value of effect 9 of the skill, when it has one       a fixed amount                        (0x48d8ff)
amount = min(amount, cap)                                      cap = effect 295 of the skill         (0x48c5c7)
cap    = cap + cap * effect 317 of the caster                                                        (0x48c5e8)
```

* coefficient: the value of effect 103 of the skill. Heal Mastery: the value of effect 245 on the caster.
* A heal cast by a doll adds to the coefficient `20 * effect 286 + 20 * min(0.05, 0.02 * pieces of 304 + 0.01 *
  pieces of 305)` (`0x48d7a1 - 0x48d865`): a piece of "Doll skill efficacy UP" is +0.4 and the sum stops at +1.
* Nothing of the target enters: not its max HP, not its RES. A heal is worth the same on a tank and on a mage.

## 6c. EXP after a battle (`0x450710` when an enemy falls, `0x445830` at the result) **[code]**

```
banked  += int(EXP of the enemy * factor)        for every member, each time an enemy falls        (0x450815)
received = banked / living members               the members alive when the battle ends           (0x4459bf)
received = received + received * bonus           a fraction handed to the result by its caller    (0x4459c7)
received = received * 2                          with effect 157 on the member                    (0x4459ed)
received = received * 2                          with a piece of enchantment 275, Double EXP      (0x445a1e)
```

Factor by gap = level of the member - level of the enemy (`0x450734 - 0x45080d`):

| Gap | Factor | With a piece of enchantment 270 |
|---|---|---|
| 10 or more | 0.85 | 0.85 |
| 5 to 9 | 0.9 | 0.9 |
| 0 to 4 | 1 | 1 |
| -1 to -4 | 1 | 1.15 |
| -5 to -9 | 1.1 | 1.3 |
| -10 to -19 | 1.25 | 1.5 |
| -20 or less | 1.25 | 1.75 |

* The division is by the members alive at the end, as the player guide says (atwiki dt2-2 page 232: a dead member is
  left out; a petrified one is counted and receives nothing). The comment on that page that gives 10% and 20% is close
  but not exact.
* The factor looks at the enemy, not at the rest of the party: a member far below the enemies of a floor gets 1.25
  whoever it travels with. `sim/progression.py` holds these rules.
* **[open]** where the bonus fraction and effect 157 come from (a party skill, a meal).

## 6d. Other recovery (one command per effect) **[code]**

| Effect | Amount | Read at |
|---|---|---|
| 105, revival | `int(max HP of the target * value)` | `0x4819b2` |
| 128, HP recovery | `int(max HP of the target * value)` | `0x483ac5` |
| 129, TP recovery | `int(max TP of the target * value)` | `0x483bbc` |
| 132, heal by percent | `int(max HP of the target * value)`, then the cap of 6b | `0x483e65` |

These take the target's maximum and a fraction; only effect 103 (6b) uses the caster's RES.

---

## 7. What this already settles

* **Enchantment sizes are constants of the code.** Physical attack and defence UP are 4 points per piece, MiniUP 2, capped at 50; accuracy and evasion the same; damage reductions 10 / 5 and 8 / 4 with a floor at 0.75; race bonuses 30 / 15 / 60. The figures the QoL variant took from the first game's guide can be confirmed or corrected here, and the 101 enchantments without a figure can be read the same way.
* **Buffs of attack add to the power of the skill; they do not multiply it.** The stronger the skill, the less a buff is worth in proportion.
* **Chant interruption is proportional to the damage taken against max HP.** A caster with more HP, or hit by many small hits rather than one large one, is interrupted less. The lever is data (Concentrate, effect 264; HP; the size of enemy hits).
* **Resistance is half a percent per point for every damage type, physical ones included.**
* **Slow halves speed.**
* **The wait until the next turn is `1 - value`, with the value capped at 0.92.** The formula reproduces a player test of the Japanese wiki to the decimal (section 5). Speed is not a ratio: near the cap a small gain in value is a large cut of the wait, which is why speed dominates.

## 8. Left for later, and what needs each

Phase 0 is closed with these points open. None enters the fight of a party against enemies as the simulator of
phase 1 models it; each is read when the work named beside it starts.

| Point | Needed by |
|---|---|
| HP of a summon (set after `0x4ffc90`); for a doll, the class and level its stats are computed from and what removes it before its turns end (11.1) | The rows about summons and dolls (S08, U02, J18) |
| In the magic function, what the roll at `0x44ed8c` decides; what happens to a spell whose damage comes out at 0 or less | The rows about Limit Field and about magic against high RES |
| Turn skipping (stun, paralysis): how many turns are lost | The rows about locks |
| Zones: which side slots 3 and 5 stand for against 4 and 6; the map cells that carry each zone | The row about damage zones (F91) |
| The source of the EXP bonus fraction and of effect 157 (6c) (the recovery after a battle is read: 12.14) | The TP economy and the pace targets (phase 3) |
| Targeting: the code that returns the formation row (the eleven rows are read; which formation each stands for is taken from its figures); the names of the attack scopes | A check of 9.1 before the tank rows are closed |
| In `_SetTime`, the branch for action kind 8 with the chant flag (`0x449e54`) | Enemies that chant |
| The bonus per stat of a character at offsets 0xdc onwards (10) | Units of the simulator beyond growth, resets and equipment |
| The enchantments `generated/ENCHANT_SIZES.md` lists with "?" | Each one when a change touches it |
| Two groups of fields and two ints of the drops of an enemy (`tools/enemy_data.py`) | The economy |

## 9. Enemy AI script (`EnemyAIData.bin`, `cbattleai2.cpp`)

Read from the parser `0x431690`, its value reader `0x4319d0`, the check `0x431aa0`, the result `0x432fd0` and the
runner `0x430f10`. The layout below parses all 516 scripts to their terminator.

**Layout.** Enemy id (u16, big endian), commands, `0xFF`. A command is one id byte, its arguments, a result word
(u16, big endian) and, at top level only, two tail bytes. Command 0 and 1 have no result and no tail.

| Id | Arguments | Passes when |
|---|---|---|
| 0 | set number, 16 weights (one per attack slot) | defines a set of attack weights |
| 1 | skill word, target kind | changes the target of that skill (`0x433350`) |
| 2 | word N | turns taken + 1 <= N |
| 3 | source, N | value of the source <= N |
| 4, 11 | source | the source exists (ailment check, buff check) |
| 5 | skill word | the last skill this unit used is that skill |
| 6 | skill word | that skill is active on itself, on an opponent, or its summon is out |
| 7 | skill word, N | that skill was used N times or more (and is the one chosen, if one is chosen) |
| 9 | none | an ally is dead |
| 10, 12, 13, 14 | source, N | value of the source > N, >= N, < N, == N |
| 15 | skill word | that skill reached its use limit |
| 8 | | not a command (the parser stops with an error) |

**Result word.** `0x2000 + n`: switch to set n. `0x4000 + n`: use attack slot n. `0x8000 + id`: use that attack id.
`0x1000 + c`: a further command c follows (no tail) and must pass too.
**Tail.** First byte not 0: the command fires only once. Second byte not 0: stop reading commands after a set switch.

**Sources** (jump table `0x432fa0`, twelve cases, each named by its debug message): 0 own HP ratio, 1 lowest HP
ratio among allies, 2 among opponents, 3 lowest TP ratio among allies, 4 among opponents, 5 an ally with an
ailment, 6 an opponent with an ailment, 7 a chanting opponent, 8 an opponent in the back row, 9 in the front row,
10 an opponent with a buff, 11 an ally with a debuff.

**Target kinds of command 1** (jump table `0x434754`, sixteen cases, each named by its debug message): 0 ally with
the lowest HP ratio, 1 opponent with the lowest HP ratio, 2 and 3 the same for TP, 4 ally and 5 opponent with the
heaviest ailment, 6 chanting opponent, 7 opponent in the back row, 8 ally without the effect of the skill, 9 ally
with a more serious ailment, 10 opponent in the front row, 11 opponent with a buff, 12 ally with a debuff, 13 ally
and 14 opponent with an ailment, 15 dead ally. How many scripts use each is in `generated/BALANCE_BASELINE.md`.

**Choice of attack** (`0x430f10`): the set is 0 at the start of every turn, and the weights are copied back from the script (`0x430f56`, `0x430f91`): a set chosen on one turn does not carry to the next; the commands before the first set run in order until one decides.
With no attack decided, a number below the sum of the 16 weights of the current set is rolled and the slot it falls
in is taken; then the commands of that set run (the parser files every command under the set read last,
`0x430cd7`). A set switch marks the set as done and rolls again in the new one. Silence, freeze and shadow bind
replace the choice with attack slot 0.

### 9.1 Who gets hit (`0x43b0d0` -> `0x43f450`; weights by `0x44a630`, slot 10 of the battle class) **[code]**

The scope of an attack is the int at file offset 0x2C of its record. Scopes 5 to 12 act on the unit's own side,
the others on the opposing side. A target set by command 1 is used when that unit is alive; otherwise:

- An enemy picking **one target on the party's side** rolls a number below the sum of the members' weights and
  takes the member it falls on (`0x43f7e9`, `0x505ad0`). Every other single pick (the party's automatic targets,
  a pick on the unit's own side) is an even roll among the candidates (`0x490790`).
- Scope 1 and 6 (several random targets) roll evenly, once per hit, with no weights (`0x43f8a2`).
- Scope 2 and 7 take the row of the picked unit, 4 and 8 the whole side, 9 and 10 the unit itself, 14 everyone.

Weight of a living member, recomputed at every pick:

    weight = share of its position                      table 0x6517a0, by formation; each row adds up to 100
           + value of effect 170 on that enemy          only for the member who put it there (cut to an integer)
           + 10 per piece with enchantment 49
           -  5 per piece with enchantment 50
    weight = max(10, weight)

Rows of the table: (100) (50 50) (60 40) (33 34 33) (38 38 24) (40 30 30) (28 28 28 16) (30 30 20 20) (31 23 23 23)
(24 24 24 14 14) (26 26 16 16 16). Read from the figures: one row per party size and number of members in front.
The code that returns the row number (`[party vtable + 0x17c]`) is not read.

Nothing else enters the weight: not damage dealt, not healing, not HP. Enmity in this game is the position, Provoke
and the two enchantments.

### 9.2 The record of an enemy attack (`EnemyAttackData`) **[code]**

    0x2C target code      0x30 attribute        0x34 speed of its chant        0x44 speed of the attack
    0x38 accuracy term    read first by both hit formulas (0x44aa49, 0x44d5c0)
    0x3C power            a physical attack adds it to the modifiers of its attack value (0x44b497), where a skill
                          of the player has effect 26
    0x40 turns            how long its statuses last; a float the code turns into an int (0x557560)
    0x4C five effect slots of (id, value, kind)

The **kind** of an effect slot, in a skill file as in an enemy attack, says how the effect is used. By what carries
each value in the data: 0 a passive, 2 a property of the action (power, accuracy, number of hits, fixed damage),
3 an effect on the map, 4 something done to the target when the action lands (damage, an ailment, a drain), 5 a
status that lasts turns.

A unit record holds current HP at `0x14` and max HP at `0x18`; a party passive of an enemy or of a guest ally is one
more `EnemyAttackData` entry (`tools/enemy_data.py`, `tools/npc_data.py`).

## 10. Stats of a character (`0x4f5d60`; row chosen by `0x5545b0`) **[code]**

    stat = growth row[level] + bonus of the character for that stat + one figure added to every stat

* The growth row is a row of `ClassLevelData` (99 levels of HP, TP, ATK, DEF, INT, RES, DEX, AGI). There are 38
  rows for 32 classes: `Parameter::CParameterClassLevel::GetClassLevelID` takes the current class and the class
  before it, and the six classes that can be reached from two classes have one row per route (Samurai, Treasure
  Hunter, Magical Princess, Sage, Mistress, Papillon). The same class therefore grows differently by route.
  `tools/class_data.py` holds the table; the figures are in `generated/BALANCE_BASELINE.md`.
* The figure added to every stat (offset 0x120 of the character) is the bonus of the level resets (`0x4f94f0`):
  each reset adds 5 when it gives up 98 levels or more, 4 from 89, 3 from 79, 2 from 69, 1 from 59, nothing below,
  and the total stops at 50. It is added to HP and TP as to the other six. The three recipes of the player guide
  (atwiki dt2-2 page 79) come out at exactly 50 with these steps. `sim/progression.py` holds the rule.
* The bonus per stat sits at offsets 0xdc onwards of the character. **[open]** what feeds it. The pieces equipped
  are added afterwards by `0x4f8270` (section 10.1).

### 10.1 Stats of a piece of equipment (six getters from `0x4e12a0`) **[code]**

    stat = base + int(upgrade level * upgrade rate)        a stat whose base is 0 stays 0

`EquipmentData` holds the six bases at 0x24 to 0x38 (ATK, DEF, INT, RES, DEX, AGI), the upgrade rate at 0x3C and the
swing of a weapon at 0x48 (section 2.2). The upgrade level is kept on the piece itself (offset 0x74 of the object).
The columns of the `Equipment` sheet of `vanilla_source_of_truth.xlsx` carry these names.

### 10.3 Which class learns a skill (`0x56dc10`; `tools/skill_tree_data.py`) **[code]**

The seven ints after the effect slots of a skill file hold its animation, a **mask of classes** (bit N: the class with
id N learns it; file offsets `0x1E0` of a technique, `0x228` of a spell, `0xC8` of a passive) and the pattern of its
action. The program builds the skill list of a class by testing `1 << class` on that mask. A skill with an empty mask
is hidden: the action of a doll, a result of a random move.

The field after the attribute is a set of flags. In a technique bits 0 to 3 are the range (short, mid, long, none),
bit 4 "usable in battle", bit 5 "usable on the map"; in a spell the two flags sit at bits 3 and 4.

### 10.4 Class modifiers (`Game::CGamePlayerStatus::_CalculateParameterSpecialty`, `0x4f7c60`) **[code]**

Each class has a short table in the executable (`tools/class_modifier_data.py`): entries of an equipment slot, a
weapon type and a modifier. For the weapon the type must match; the off hand counts when it holds a shield; slots 2
to 4 count whatever they hold. For each stat the piece gives:

    gain = int((stat of the character + stat of the piece) * (modifier + 0.01 * Yearning))        never below 0

and the gains are added to the stats. The modifiers run from 0.01 (a base class) to 0.05 (Valkyrie with a polearm,
Witch with a staff, Sniper with a bow, Dark Lord with an axe). Samurai, Treasure Hunter, Magical Princess, Sage,
Mistress and Papillon have a different table for each class they come from, as their growth does (10).

## 11. Summons (`0x4ffc90`) **[code]**

A summon has three forms (`SummonData`, one record each; `tools/summon_data.py`).

```
form   = the last form of the summon whose level is not above the average level of the party
level  = the level of that form
stat   = max(base, int(stat of a party member * factor of the form))        for ATK, DEF, INT, RES, DEX, AGI,
                                                                            over every member of the party
weight = the delay of the weapon rank the form names                        (order of turns, section 5)
```

* base: the six stats of the enemy the summon comes from: the EnemyData id at 0x14 of the record, shared by its three
  forms (0x10 is the character model). The lowest stats the Japanese wiki measured (page 105) are those records:
  Bigfoot 833, Ghast 913, Cupid 754.
* Its attacks are records of `EnemyAttackData` and its behaviour a script in the format of the enemies (section 9).
* A summon therefore scales with the best member of the party in each stat, not with its summoner.
* **[open]** its HP (set after this function, `[vtable+0x108]`).

### 11.1 Dolls (`0x484150` creates them; `tools/doll_data.py`) **[code]**

A doll skill creates a unit of its own (classes `CGamePlayerStatusETCDoll`, `CGamePlayerStatusOtherETCDoll`,
`CGameEnemyStatusETCDoll`).

```
HP, max HP = 9,999                                   set when it is created                      (0x4fd922)
life       = effect 147 of the doll skill, in turns  plus effect 297 when the skill has it       (0x4843c9, 0x484502)
action     = one of the hidden skills the code lists for that doll, picked at random each turn,
             performed at the level of the doll skill                                            (0x4fd980)
stats      = the function of a character                                                         (slot 0x104 = 0x4f5d60)
```

* The hidden actions are skills of their own ("...'s Action"): one for Spartan, Oracles, Mercidarian, Catalina and
  Perdurabo, five spells for Musiy (one per element, picked at random). **The power, the ailment chance, the heal
  power and the spell power of a doll are the figures of those hidden skills**, not the value the doll skill shows
  under its own effect (228 to 233), which the attack and heal code never reads.
* A physical hit by a doll adds to its modifiers the value of Doll Mastery (effect 286) and
  `min(0.05, 0.02 * pieces of 304 + 0.01 * pieces of 305)` (`0x44b4fd - 0x44b5ad`), and takes its range from the
  doll, not from a weapon: Spartan short, Oracles mid, Mercidarian long (`0x44bb1c`). A heal by a doll adds twenty
  times the same two terms to its coefficient (6b).
* A doll is not ended by ordinary damage: 9,999 HP at every level. What ends it is its count of turns, and the code
  that removes the doll of an owner (`Battle::CBattleBase::DeletePuppetCommand`, `0x43caf0`).
* With effect 314 on its owner a doll adds to each of its six stats that fraction of the stats of an enemy the code
  picks (`0x4fdfdc - 0x4fe0fa`).
* **[open]** which class and level the stat function is fed for a doll (it shares its owner's character number,
  `0x4fd87c`, so the owner's own figures are the likely answer), and when `DeletePuppetCommand` is called.

## 12. What each effect of a skill does

The rule of every effect, as far as it is read, is one row of the sheet `EffectRules` of
`data_tables/balance_criteria.xlsx` and one line of `docs/generated/EFFECT_COVERAGE.md`, which is generated from that
sheet and from a search of the program (`tools/exe_effects.py`) and says for each effect whether it is read, partly
read, located or not found. What follows is how the program is built around them, read while filling that sheet.

### 12.1 How an effect is built

`Command::CreateCommand` (`0x47b220`) switches on the effect id and builds one object per effect; some cases call a
small constructor instead (`0x478000 - 0x47b220`). Every effect class has, among others:

* a method that **applies** it (slot 6): most classes share one that only records "applied" (`0x480090`), so the
  effect lands without a roll and its meaning is wherever a formula asks for it; an ailment has its own, with its
  roll (5b);
* a method run **every turn** (slot 3): regeneration, Carol and Chorale act there; for an ailment it wears the ailment
  off;
* a row of yes/no methods that class it (song, dance and so on).

A formula asks for an effect in one of these ways: by id among the effects of the action (`0x47e340` and its
siblings), by id among the statuses of a unit (slots 0x48 and 0x50 of the unit), as a passive of the unit or of the
whole party (`0x4fab50`, `0x4e4dd0`), or by walking the effects of the action and comparing ids.

### 12.2 Number of hits (`0x417cd0`)

A multi-hit effect sets the count: a fixed number, or a base plus a weighted pick from a table; while effect 210 is in
the action the pick uses a second table that never gives the lowest count. A plain attack with none of them rolls
Triple Attack first (three more hits) and, failing that, Double Attack (two more), each a roll below 100 under
`value * 100`. The tables are in the sheet.

### 12.3 Special damage (`0x44f720`)

Before the cap, an action that carries one of these effects replaces the computed damage: a fixed amount (8), a share of
the user's HP (12), a share of the target's max HP times the resistance factor (138), half or three quarters of the
target's HP (140, 141), all but one of the target's HP (142) or of the user's (434), the user's level times a value
(435). Afterwards effect 2 sends the damage to TP instead of HP (`0x44ce96`).

### 12.4 When a unit is about to act (`0x436c40 - 0x436f8b`)

In order: a petrified unit does not act; a sleeping one loses its turn; a paralysed one loses it on a roll below 100
under 30; then each opponent with Warning Shot, Mesmerized or the Erotic Dance rolls below 100 under `value * 100`.
What a success of those three does next is only partly followed (see the sheet).

### 12.5 Ailments over time (`0x48d180`, `0x482150`) **[read in part]**

An ailment keeps a recovery chance. Each time its turn method runs, a roll below 100 under that chance ends it; on a
failure the chance rises by 10. A piece with enchantment 265 makes the check come sooner outside battle (every two steps
of its counter instead of five). Poison takes `int(max HP * 0.05)` when it ticks. Where the chance starts and how often
the method runs are not followed.

### 12.6 Statuses that change stats (`0x4fbdd0`)

When the stats of a unit are recomputed, each of the six stats gains `int(stat * value)` of its own buff (effects 41 to
46) and of the all-stat ones (189, 193, 194); resistances gain the value of theirs (169, 184 to 186, 202, 248, 341); max
HP gains `max HP * value` (172); Trump Card adds `int(DEF * value)` to ATK and sets the DEF bonus to -10,000; a
petrified unit gains half its DEF and loses half its AGI.

### 12.7 Damage received (`0x47e500`)

TP Conversion and the enchantments 72 and 73 turn part of the damage a unit takes into TP; Resuscitate raises a fallen
unit at `int(max HP * value)`; Stamina is checked against a share of max HP. The sheet has the figures.

Effect 254 (Guts; on the Balance variant also the unique skill of Lizerietta), `0x42389d - 0x423901`: when the HP of
the target minus the damage is 0 or less, the first status of effect 254 in its list rolls `value * 100`, and on a
success the damage becomes HP - 1. It rolls at 1 HP too, so a unit can hold on again and again. Seven bytes of the
same length would skip the roll at 1 HP (`2b 45 40 85 c0 0f 8f` to `48 48 3b 45 40 0f 83` at `0x4238a2`: "HP - 2 >=
damage, unsigned"); built and withdrawn on 2026-10-12, since the code is the one of Guts too. No enemy
has the effect.

### 12.8 Songs and dances (`0x48bf90`)

The bonus of a performer is the value of Song Bonus or Dance Bonus (effects 279, 280) plus
`min(0.05, 0.02 * pieces + 0.01 * mini pieces)` of the matching enchantments. How it enters depends on the class of
the status, in the value getter at `[vtable + 0x2c]` (`measures/status_value_getters.py` lists them):

| Effects | Getter | Value |
|---|---|---|
| 195 Waltz, 196 Samba, 197 Tango, 198 Polka, 201 Mazurka, 205 | `0x487d70` | `value - bonus` (the stat falls further) |
| 202 Hopak | `0x488890` | `value - bonus * 100` |
| 199 Salsa | `0x488400` | `value + bonus` |
| 210, 212, 213, 214, 217, 218, 222 (songs) | `0x488be0` | `value + bonus` |
| 211 Concentration Prelude | `0x488e10` | `value + bonus * 100` |

### 12.9 After a hit (`0x423560 - 0x4247e0`) **[read in part]**

Once a hit has landed the same function runs the passives that answer it: Dark Aura punishes a short-range physical
attacker with stat debuffs of -0.1 each unless it has Anti-Dark Aura; Slow Target rolls `value * 100` to slow the
target (speed modifier -0.75); Survival, Reprisal and Devil's Whisper are rolled here too. Final physical damage has
an "other" bonus (2.4) that Power Charge and Limit Field add to, and that Imperial Guard lowers for a party member in
the back row (the lowest value among the allies who have it).

### 12.10 Random moves (`0x41e060`, `0x42db00`; `tools/random_move_data.py`)

Roulette Circus, Magic Box, Showtime and Heaven or Hell (effects 152 to 155) do nothing themselves. When the action is
built, a weighted roll (`0x505ad0`: below the sum of the weights) on a table of twelve-byte entries in the executable
picks a hidden skill, and that skill is performed. Each has a second table, used when the user has Triple Joker
(effect 315). The tables, with the chance of each result, are generated into `docs/generated/BALANCE_BASELINE.md`.
Magic Box has one exception in code: its Genjimaru result is swapped for its empty result when a Genjimaru is already
in the battle.

The odd results have small commands of their own: 425 ends the chant, song, dance and doll of each target; 426 gives
`int(value)` TP; 427 creates Genjimaru with the constructor of a doll (9,999 HP, hidden skill 107); 432 marks each
enemy as gone when the battle allows running away; 433 takes `int(gold * value)` from the party.

The weights are data inside the executable (`.rdata`, `0x64f440 - 0x64fbec`), not code.

### 12.11 Passives outside the damage formulas

A passive of the party is read by `0x4e4dd0`, which returns **the highest value among the living members who have
it**, not the sum: two members with the same passive do not stack.

    TP cost (0x4fd250)   cost = int(cost * 0.8) with a piece of 246 (techniques) or 248 (spells)
                         cost = int(cost * 0.6) with a piece of 247 (techniques) or 249 (spells); both can apply
                         in battle, Economy (266) then takes away int(ceil(cost * value)); never below 1
    Escape (0x41ad59)    chance = 0.3 + (AGI - average enemy AGI) / 50 + Elusiveness (269)
                         kept between 0.2 (0.5 with a piece of 262) and 0.95; the value of the action is then
                         added, up to 0.95; roll below 100 under chance * 100
    Drops (0x5581ff)     every drop with a chance gains int(Treasure Hunt (270) * 100) points; the last one also
                         gains 20 points per piece of 276 on the unit that felled the enemy
    Gold (0x43aa33)      gold = int(gold * (1 + Lucky Me (271))); four times and at least 100 first with effect 428
    Prices (0x4762c0)    price = int(price - price * Negotiate (282)), at least 1

### 12.12 Who takes the hit (`0x4200e0`, the function that applies an action)

Before the damage of a hit is kept, the target can turn it away, in this order:

* **Cover** (`0x420b60`): for an action aimed at one unit or at random units, one of the other units of the target's
  side that has Cover, picked with equal chances, becomes the target. There is no roll and no test of the kind of
  damage. After the action each covered hit rolls `value * 100` to **end** that Cover: the value of the skill is the
  chance to lose it (0.70 at level 1, 0.40 at level 5).
* **No effect**: a unit with All Resistances 100, or with Nullify Short-Mid against a short or mid range hit.
* **Elegant Dancing**: the first damaging hit deals 0 and the status is spent.
* **Counter** (`0x422553`): roll `value * 100`; the hit does nothing and the target counters.
* **Clone, Illusion, Barrier System** (`0x41f920`): each is a count of hits; a damaging hit (not one that halves or
  quarters HP) or an ailment that would land does nothing and takes one from the count.

### 12.13 Counters and follow-ups

    Counter Whip (0x4203b1)   at the start of an action the first target that has it strikes first; no roll
    Counter (0x422553)        short or mid range; roll value * 100; the hit is void and the target counters
    Reprisal (0x424689)       short or mid range, after the hit landed; roll value * 100; counter when the action ends
    Support Shot (0x424c42)   after a plain attack of an ally; each bearer rolls value * 100; the first success fires
    Absolute Attack           an attacker that has it is never answered by the three counters above

A counter is built by `_SetupCounter` (`0x425930`).

### 12.14 After an action and after a battle (`Battle::CBattleBase::Update`, `0x438cef`)

* Double Action and Triple Action (enemies): roll `value * 100` for two actions; failing that, roll for three.
* Ecstasy (`0x47f59b`): once per battle, when damage takes its bearer from half max HP or more to below half, an ATK
  buff and a DEX buff of its value.
* Paean (`0x439380`): its value is the `bonus` of the EXP share (6c).
* Solo Duet, On Stage, Double Puppet: two songs, dances or dolls at once instead of one; one more ends the oldest.
* Values raised by passives (`0x483a20`, `0x48a8f0`, the getters at slot 0x2c of their classes): the value of
  effects 128 (HP recovery), 129 (TP recovery), 130 (Pass All TP) and 168 (speed modifier) is the figure of the skill
  plus the user's Maid Mastery (278) and Maximum Maid (353); the value of 272 and 273 is the figure plus Maid Mastery.
  `0x48bf90` returns the value of the passive it is asked for, and for songs (279) and dances (280) adds
  `min(0.05, 0.02 * pieces + 0.01 * mini pieces)`. So Maid Mastery 10 turns First Aid 25% into 35% and Cook 15% into
  25%, as the GameFAQs guide says.
* Dispel (effect 74, `0x4226c4`): one roll of `value * 100`; on a success every status of the list the target gives
  (`0x4fb1f0`, the statuses whose class answers yes at slot 0x64) is removed. Always: 27, 171, 325 - 329, 101, 102,
  181, 189, 191, 193, 194; while their value is not negative (`0x479df0`): 21, 26, 28, 31, 41 - 46, 161 - 169,
  172 - 174, 184 - 186. Nothing else: not songs, dances, ailments or effect 32 (`sim/battle.py` DISPEL_ALWAYS).
* Recovery after a battle (`0x43d6a7 - 0x43d8b4`; `sim/progression.py`): over the living members, the values of
  effect 272 (HP) and 273 (TP) of Generous Heart are summed, each sum is capped at 0.30 (`0x6d9330`), and what
  `0x48bf90` adds for effect 353 (Maximum Maid) of each of them is added outside the cap. Every member then recovers
  `int(max * fraction)`, at least 1; a member with a piece of enchantment 193 recovers all its HP (`0x6d938c`).
  Two maids reach the cap, as the guides say (atwiki dt2-2 page 120; GameFAQs, Class Skill info - Maid).

### 12.15 When an effect that lasts acts (`Battle::CBattleBase::Update`, `0x4363bc`; states at `0x439820`)

The turn of a unit goes through numbered states. The ones read:

    0    start: Esarhaddon removes ailments (0x436727)
    4    petrification runs its per-turn method, before anything else (0x436be4)
    6    a unit that cannot act says so and its turn ends (0x436ca1)
    9 - 11   the rolls of the opponents: Warning Shot, Mesmerized, Erotic Dance; a success ends the turn
    12   the command is chosen (Murder License replaces it, 0x437364)
    13 - 15  the action
    16   **every status of the unit runs its per-turn method** (0x437b0c): regeneration, Carol, Chorale, poison,
         the damage of an enemy dance, natural recovery

So regeneration and poison act **after** the action of their bearer, once per turn of that unit. A passive skill
stands on its bearer as a status that never ends (the finder `0x47e340` reads passives and statuses from the same
list), so Auto-Recovery and Auto-Refresh (246, 247) and the HP Regen of enemies tick in state 16 too; the simulator
missed them until 2026-10-09. On the map the same
methods run on every step for each party member (`0x4fb660`, called at `0x4b221f`), and every tenth step a piece of
enchantment 216 acts.

### 12.16 Steal (`Battle::CBattle::_Steal`, `0x44fde0`)

    chance = 0.5 * (DEX of the thief + 50) / (AGI of the target + 50) * value of the effect of the action
             effect 60 steals gold, effect 61 an item: two branches, an action holds one of them
    kept between 0.05 and 0.95; a number below 100 under chance * 100
    gold:  int(gold of the enemy record * factor)      factor = value of effect 62 when the action has it, else 1
           once per enemy (a byte of the enemy, 0x155)
    item:  only from an enemy with bit 15 of its flags (0x4503c5; 381 of the 516 have it: every enemy of the random
           battles but Odin, Myrddin, Asmodeus and Carmilla, and 26 of the 157 that only stand in fixed battles);
           once per enemy (0x154), the byte set only when the steal succeeds, so a failed one can be tried again.
           What is taken: the draw of the drops (0x558180, 12.11) called with its steal flag (0x4504ac). The flag
           leaves out Treasure Hunt and enchantment 276 (0x5581f1) and the "nothing" of the draw (0x558388 -
           0x558392): one weighted roll among the items and the equipment drop with their chances as weights, then,
           for the equipment, the roll among its slots by their weights, as for a drop. No field says "what can be
           stolen"; the drop when the enemy falls does not look at 0x154, so a robbed enemy still drops.
    an enemy thief takes int(gold of the party * value of 62) and carries it; it comes back when that enemy falls

### 12.17 Weapons in the stats of a character (`_CalculateParameterEquipment`, `0x4f6500`)

Each of the six pieces adds its six stats (10.1). For a weapon two of them are scaled:

    ATK and RES of the weapon:   stat + int(stat * (weapon mastery 243 + Weapon Mastery 298))
    DEF, INT, DEX, AGI:          as they are

The mastery multiplies **the weapon's** figure, never the character's; and it reaches RES, not INT, so a mace or a
tome gains RES from it and a staff gains nothing but on its small ATK. A weapon in the off hand adds nothing here:
with Dual Wield each of its stats is added at the end as `int(stat * value)` (`0x4fc26f`), 0.30 at level 1 and 0.72
at level 10.

### 12.18 How long a status lasts and whether two stack (`Command::CCommandTurnBase`, `0x48d590`; `0x4f9930`)

* A status carries a number of turns. Its per-turn method takes one away each time it runs (12.15: after the action of
  its bearer) and removes the status when the count reaches 0. A status created with 0 turns is never counted down:
  it stays until something removes it.
* On the map a turn is **five steps**: the method runs on every step but only every fifth one counts (`0x48d5ed`;
  the count is skipped when the tick comes from a battle, the word at `+0x40` of its second argument). This is the
  tick of the 97 effects whose class is `CCommandTurnBase`: the buffs and the lowered stats with a number of turns,
  the buff of a meal among them (`measures/DESIGN_ROWS.md`). An ailment that ends on a roll has its own count of
  steps (`0x48d1fc - 0x48d208`: 5, or 2 with a piece of enchantment 265), and so has petrification (`0x483038`). The
  Balance variant makes the first one 12 (row X15 of the sheet `ExePatches`), which leaves battles and those ailments
  as they are.
* Some statuses end at the tick of a sleeping bearer (their class answers yes at slot `0x8c`; `0x48d5b5`, 16.7).
* A few classes use the base method `0x48bc50`, which removes the status the first time it runs: they last until
  the next tick of their bearer.
* **Two statuses of the same effect do not stack**: when a unit receives one it already has, the old one is deleted
  and the new one takes its place, with the value and the turns of the new one, even if it is weaker (`0x4f9b72`).
  The only exception read is petrification below its third stage. Statuses of different effects that move the same
  stat do add up, each in its place of the formulas.

### 12.19 Unique skills (`UniqueSkillData`: the effect id is the int at `0x50`, the animation at `0x48`)

Each unique skill is a status of one effect, and its value by level is its chance or its size. All but one roll
`value * 100`:

    Third Eye Wide        start of each opponent's turn: one of poison, paralysis, sleep, freeze, silence, stun, dispel at 0.75
    Sugar Coma            a short-range hit on her: the attacker gets Slow and speed -0.2
    Furious Strike        her physical action ignores defence and cannot miss
    Alter Fate            a hit on her deals nothing
    Usurper of Souls      before her action: the summoned units of the other side are removed
    Did You Call for Me?  after her action: she acts twice
    Undaunted Spirit      end of a turn, while fallen: she rises
    Tranquil Song         before her action: ATK -0.1 and INT -0.1 on every opponent
    Forerunner            a chanted spell is cast at once
    Overstock Clearance   before her action: she first uses an item of her stock
    Shadow Heart          before her action: a unit of her own joins to attack
    Arcane Shield         the roll is 15 in 100, written in the program; the value is the share of the damage sent back

Read on 2026-10-12 (`measures/qol_fields_reading.md` 5 to 7, checked against the program):

* **Shadow Heart**: the shadow takes the stats its owner has at that moment (`0x4fd0b0`) with twice the ATK
  (`0x4fe3ca`), keeps her passives and loses the ailments and the statuses that techniques put (`0x4fe337 - 0x4fe3bf`);
  its life is 3 (`0x437a2e`). The statuses of techniques are those whose skill is found in the map `0x738a5c`
  (records of 0x90 words, the technique file): Power Charge, Berserk and War Cry go, Brave and the songs stay. Both
  guides say Power Charge serves its three blows; the code read says it does not. The doubled ATK is written into
  the stored stat of the shadow, which would be lost if its stats were worked out again: taken as kept for its life
  (not read), so what Berserk or War Cry gave its owner at that moment stays in its ATK.
* **Did You Call for Me?**: the second action belongs to the same turn, so the statuses of the unit do not lose a
  turn between the two, and a flag keeps it from firing twice in a row.
* **Third Eye Wide**: its seventh result, the dispel, removes nothing (`0x47ee6f` jumps over the routine).
* **Murder License** (enemy passive 1580, effect 319), read on 2026-10-12: at step 12 of each turn of its bearer,
  with no roll, an action is built from the attack linked to the status and aimed at one opponent drawn at random
  (`0x43736a - 0x43743a`), and the machine is sent to run it (`0x437488`, the same exit as the item of Overstock
  Clearance at `0x436bd5`); the step counter was already raised (`0x437364`), so the turn then goes on with the
  steps after it and the own action of the bearer. A report of another reader said the action of the bearer is
  replaced: the counter says it is not, and the Japanese pages 207 and 334 describe a bearer that kills one member
  before each of its actions. The linked attack is the passive itself: when the passives of an enemy are set up its
  id is given to the status (`0x4f20a4`), and record 1580 holds nothing but effect 319 of kind 0 and value 1, no power
  and no instant death effect. So the death those pages tell (stopped by instant death immunity or earth resistance)
  is not in the data: it is in the code that runs that action, which was looked for on 2026-10-12 and not found. The
  simulator does not play the passive.
* **Forerunner**: one roll for each chanted command (`0x4176a0`, called at `0x41d69c` and `0x419c55`).

Without a roll: Positive Trance (2.4), Elbow Grease (2.2), Wreathed in Glory (adds to the speed of her skills), Maximum
Maid (the bonus of maid skills), Demon Wall (less damage to its whole side, 16.8), Yearning (0.01 per point on each class
modifier).

## 13. Pep and the data of a character (`tools/character_data.py`) **[code]**

Pep is a float of the character (`0xd8`). `0x4f69e0` keeps it **between 70 and 130** every time it changes, and then
applies what fixes it: a piece of enchantment 201 holds it at 70, a piece of 200 keeps it at 100 or more, a piece of
195 holds it at 130, and a status of effect 81 sets it to the value of the status.

What reads it:

* **Joint skills** (`0x56e676`): a joint skill can be used only when every participant has at least its "Pep needed"
  (`JoinSkillData 0x28`); using it takes its "Pep spent" (`0x2C`) from each (`0x5097f6`), halved by a piece of
  enchantment 266. This confirms by code the two fields the QoL work had named by comparison with the wiki.
* **Positive Trance** (2.4): damage gains `(Pep - 100) / value / 100` of itself when Pep is above 100.
* The mood shown on screen (thresholds 85, 90, 110, 115 at `0x4bea80`).

What changes it: each character has **21 amounts** in her `PlayerStatusData.bin` (`0x3C`), one per event, and the
code adds the one of the event (`History::CHistory`, the log of what happened in a battle). Read so far: felling an
enemy (0), falling (1), landing a critical hit (2), taking one (3), ending a battle with an ailment (7), treasure
boxes (13, 14), the start of a battle (15, 16), meals (17, 18), and a counter reaching 100 and 300 (19, 20). Some are
added to every living member at once (`0x4e4b70`). The skills that move Pep are effects 66, 80 and 204.

The same file gives the base class and the unique skill of each character; `InitialData.bin` gives her starting
class and EXP. These amounts are data: a lever of the kind the plan calls benign.

## 14. Encounter rate (`Dungeon::CDungeonBase::_CheckEncount`, `0x4bc6a0`) **[code]**

The check runs on a step. Nothing happens on cells of kinds 1, 2, 3, 4, 6 and 7; kind 5 starts its own battle.
Otherwise the cell names its zone, and the zone gives the chance:

    chance = zone[0x1C]                      percent; 0 in a zone with no random battles
    chance = 0  while fewer than 8 steps have passed since the last battle (0x4bc77b; not before the first one)
    chance = 0  while game flag 997 is off
    if chance > 0:
        chance += int(Whistle)               status of effect 18 on the party (its value is 4)
        chance += int(status of effect 21)   no skill uses it
        chance += -1 with a piece of enchantment 211, -2 with 212, +1 with 213, +2 with 214 (each counted once)
        chance = max(1, chance)
    a battle starts when a number below 100 is under the chance

So the mean walk between two battles is `8 + 100 / chance` steps: 28 steps at 5, 22.3 at 7, 18 at 10. The figure of
every zone is in `docs/generated/BALANCE_BASELINE.md`. It is one int of the floor file: data, not code.

After that roll the same step rolls five more chances of the zone, in this order, and the first that falls under
its chance fires (`0x4bcb60`): each makes a wandering shop appear, the class the program builds for it named by its
type information (`0x4b28b7`, jump table `0x4b36cc`).

| Chance | Field of the zone | Shop | Game flag | Vanilla values |
|---|---|---|---|---|
| 1 | `0x20` | Peddler (`CShopPeddler`) | 601 | 3 - 10 |
| 2 | `0x24` | Blacksmith (`CShopBlacksmith`) | 602 | 2 - 10 |
| 3 | `0x28` | Ice cream shop (`CShopIce`) | 603 | 0, or 5 - 10 |
| 4 | `0x2C` | Ramen shop (`CShopRamen`) | 604 | 0, or 6 - 12 |
| 5 | `0x30` | Dark peddler (`CShopDarkPeddler`) | 605 | 0 in every zone |

A shop is rolled only when all of this holds (`0x4bc8a1 - 0x4bca94`, `0x556380`):

* its game flag is on (the story has opened that shop);
* it has not appeared yet: a byte of the dungeon for each shop (`+0x781` to `+0x785`), set when it appears
  (`0x4bcbad`) and cleared with the other counters of the dungeon (`0x4b613f - 0x4b6175`);
* the counter of battles of the dungeon (`+0x770`, one more at the start of each battle, `0x4b2730`) is at least 5;
* at least 50 steps were taken since the last shop appeared (`+0x200`, one more a step at `0x4b92b3`, set to 0 when a
  shop appears, `0x4b289b`); 25 steps with a piece of enchantment 259.

Then `chance + shift of the four enchantments above`, at least 1, against a number below 100. The battle is rolled
first and the peddler before the blacksmith, and a shop that appears sets the 50 steps back for the others, so the
blacksmith of a zone at 5 with a peddler at 6 and battles at 6 is the next shop a little under half of the times.
A byte of the dungeon (`+0x7A4`, written at `0x4b2c8f`; what sets it was not followed) puts the ice cream and ramen
chances of the zone at 100 for the next step (`0x4bcaa9 - 0x4bcb52`). The five chances are ints of the floor file, as the chance of a battle: data, not code.

## 15. Items (`0x50c596`; `tools/item_effect_data.py`) **[code]**

An item has up to four (type, value) pairs. The program turns each into an object of a class picked by a switch of
107 cases, and the method at slot 3 of that class does the work.

* **39 types perform a skill**: the method only calls `0x50b030` with a skill id. Type 90 casts Fireball, 46 Fire
  Blast, 25 Brave, 27 Fleet Foot, 29 Accelerator, 32 War Cry, and so on (the generated map is in
  `docs/generated/BALANCE_BASELINE.md`). The figures of such an item are those of the skill file.
* Type 0 heals HP by its value, plus `int(value * Item Mastery)` (`0x50e789`). Recycle may keep the item (12.11).
* Type 6 cures **one** ailment of the target, picked at random among those it carries (`0x50fb30`: the list of the
  unit, a random index by `0x490790`, then the removal at slot 0x64 of the unit; message 0x8d). Type 7 cures **every**
  one (`0x50fe20`, the same list walked to its end; message 0x8e). The descriptions agree: Harunire Leaf "Cure one
  status ailment", Fumirul Nectar "Cure all status ailments" (ItemData 24, 25). Read on 2026-10-09; the simulator
  had type 6 curing all and type 7 doing nothing until then.
* Types 53 and 54 deal `int(max HP of the target * value)`, never more than 100 (`0x511b78`).
* Type 89 takes a twentieth of the party's gold, at least 1 (`0x51438a`); the value the item stores is not used.
* **Which pairs act** (`0x55b550`, `0x55b5b0`; read on 2026-10-12, `measures/qol_fields_reading.md` 1): the first two
  pairs when the target is a member of the party, the last two when it is an enemy, never the four together. Hipanera
  Tea gives a member 50 HP and 20 TP and an enemy 50 HP.
* A meal of the restaurants holds item effect types, not skill effects: 62, 63 and 64 restore
  `int(max * value / 10)` of HP, of TP, or of both to each member (`0x512f37`).
* Types 56, 57, 60 and 61 act only on some enemies (a list of 23 ids, or a race) and then create an ailment for 5
  turns; they were not followed further.

A **joint skill** is computed by the magic formula: when the action is a joint skill, its Power field
(`JoinSkillData 0x40`) is added to the modifiers of attack B (`0x44df1f`), beside effects 195 and 335.

## 16. Read on 2026-10-06 (phase 0 reopened for four pieces, and the assumptions of the simulator)

### 16.1 Sealbooks (`SealScrollData`; map `0x738a14`)

    0x00 id: the id of the enemy it seals      0x18 kind: 0 a sealbook, 1 a grand sealbook
    0x1C number of enchantments                0x20 up to four enchantment ids          0x34 level

* A sealbook carried by a character adds its enchantments to the same list as her pieces of equipment
  (`0x4f7b5d - 0x4f7bdd`), so they count in every formula that counts pieces. Soul Seal (effect 314) gives a doll a
  share of the stats of the enemy of its owner's sealbook (`GetSealScrollID`, `0x4f4fc0`; `0x4fdfe2 - 0x4fe0fa`).
* A grand sealbook has one enchantment (Scanner: 298, chants +0.25 on the gauge value; the roll before it is "a
  number below 10 under 10", so it always applies, `0x44a359 - 0x44a394`). From the GameFAQs guide (Grand Sealbooks):
  one is carried at a time, its enchantment acts for the whole party and its summon stands in the party.
* The piece counter (`0x4f5470`) stops at one for an enchantment whose record has a flag; which field holds the flag
  is not identified (bit 0 of file offset 0x20 is not it: Speed UP has it and stacks in the player test of 5).

### 16.2 Zones that forbid magic

A zone slot of value 2 on the cell forbids the actions whose skill carries the magic flag (`0x41a48b`, `0x41c191`,
`0x41e04f`, the test `0x4e4560`); a battle that starts on it plays the voice `Fleed_Zone_00010` (`0x44906c`). Dolls are
techniques and fight there; the game's own dialogue (event script `St06_c0030`) says the zone nullifies magic for
everybody. Where it lies is read by `tools/map_data.py`: a map is width x height cells of 42 bytes (loader `0x4b55cf`,
cell conversion `0x4afa40`: byte 0 the kind, 1 an index, 2 and 3 the zone slots, 6 the zone of the floor). A cell of
kind 1 runs the event script its index names (the script list of the floor file, count at 0x78), and a script starts a
fixed battle with the command `1F 01 00` and the battle number. 175 of the 196 fixed battles are placed on their cell;
8 stand on a no-magic cell, Dragon Papi the one of the story. The checkpoints of the simulator take the zone slots and
the zone factors of their cell.

### 16.3 Rank of a unique skill (`0x4f615e - 0x4f61e3`)

Rank = level / 10 (no unique skill below level 10); rank 10, the EX value, once the bonus of the resets reaches 50.

### 16.4 Poison (`0x482186 - 0x4821ff`)

`int(max HP * 0.05)`, at most 250; a figure of 0, or one that would take the last HP, leaves 1 HP: poison never kills.
A sleeping unit takes none.

### 16.5 The rest read for the simulator (`data_tables/sim_setup.xlsx`, sheet Assumptions)

* Start of a battle (`0x449130`): a member or an enemy starts at a gauge of (a number below 500, plus 1) / 1000, a guest
  ally or a summon at the value of a plain action; one battle in five every gauge is (a number below 93) / 100.
* Who can be picked (`0x43e6d0`): units numbered below 2000. Dolls (2000 + n, `0x43a205`), guest allies and summons
  (3000, `0x4497ce`) are never picked: they cannot be hurt by the other side.
* Piercing (`0x43fa64`; lists built at `0x43def0`): the target and the units its list names; for the party, the overlap
  of the front and back rows centred on each other.
* Hit (`0x44aef3 - 0x44afbb`, `0x44da4a - 0x44daac`): Fixed accuracy and a direct accuracy value set the chance to
  value * 100; a sleeping target (slot `0xbc`) is hit for certain. Slots `0xb0 - 0xc4` test poison, freeze, paralysis,
  sleep and silence.
* A turn (`0x436c40 - 0x436d4c`): petrified (slot `0xc8`) and asleep lose it, paralysed on 30 in 100; freeze and Shadow
  Sew do not stop a unit.
* Stun (`0x4fa185 - 0x4fa2f2`): ends the chant, song, dance and doll of the target, sets its gauge to 0 and is removed
  at once. No turn is skipped.
* Double and Triple Attack (`0x418045 - 0x4180e3`): Triple rolls and adds 3 hits, Double rolls on its own and adds 2;
  with neither the attack hits once.
* Recovery of an ailment (`0x47bc03`, `0x48d211`): the chance starts at the turns figure of the action that caused it
  (0 for every skill of the player) and rises by 10 after each failed check.
* Enemy chants (`0x449b0d - 0x449b38`): bit 11 of the word at file 0x28 of the attack, INT; bit 12, RES.
* Magic attack (`0x44dcc0 - 0x44e6c6`): attack B = (INT * (2 + swing) + power * (1 + Magic Mastery) * (1 + 195 + 335 +
  joint power)) * (1 + enchantments * 0.01); attack C = attack B * (1 + Spiritual Fantasia) * (1 + element boost), the
  element boost being 0.2 for the matching element status 325 - 329 and 0.2 per piece of its "magic buff" enchantment
  (78 - 82). A spell of a doll adds 500 * (Doll Mastery + min(0.05, 0.02 * pieces of 304 + 0.01 * pieces of 305)) to its
  power. Magic hit terms of decided: 167, 309, 197, 222, 278, 353; of the target: 165, 198. Magic defence modifiers:
  163, 196, 205, 336, 213, 220, 223.
* Effects 71 and 136 (`0x44c60e - 0x44c6b6`): 71 adds its value to the "other" bonus once for every buff or debuff of
  the target; 136 adds value * the number of the hit record.
* Dolls (`0x4f3290` from `0x4fd867`): a copy of the owner's character (class, level, bonuses, equipment), HP 9,999.
* Revive item (`0x5101a4 - 0x5101ca`): int(max HP * the value of the item / 100), at least 1.
* Per-turn damage of effects 199 and 339 is capped by the Damage cap (296) of the action that put it.

### 16.6 Damage taken: waking, and the end of chants, songs, dances and dolls (`0x47ea4d - 0x47eabb`)

When a hit takes HP from a living unit: a sleeping unit wakes (status 116 is removed); and when the interruption roll
of the hit succeeded (section 2.5: damage against max HP, Concentrate, the enchantments, and the second roll of 33 in
100 on a critical hit), the chant, the songs, the dances and the dolls of the target all end. A doll is not hurt by
damage (9,999 HP), but damage to its owner ends it with the same chance as a chant. (Corrected in 16.7: the rate is
rolled by the physical function only; a spell interrupts only through the second roll of a critical.)

### 16.7 Read on 2026-10-07: the simulator checked against the program

Every rule the simulator plays was set beside the code that does it. What follows corrects or completes the sections
above; where the two disagree, this section is the reading.

**Which attack function runs** (`0x420156 - 0x42016d`, `0x421238 - 0x42197d`). An action that carries effect 0 runs the
physical function (`0x44a850`); one without it runs the magic function (`0x44d370`) when it carries effect 1 or 25, and
no attack function otherwise (it lands, and its own rolls decide). With effect 25 the magic function gives the hit roll
and its damage is thrown away (`0x421a83`). The file a skill comes from does not decide it.

**Lists of the attack functions.** Each function searches two lists: the effects of the action followed by the statuses
of the user, and the statuses of the target. The finder `0x47e340` stops at the first match, so the action's own value
of an effect hides a status of the same effect on the user (Berserk's 26 counts for a plain attack, not for a skill
with its own power). Read in the physical function: 26 user; 28, 162, 187, 196, 205, 336, 219 target; 190 (Limit Field)
target; 191 (Power Charge) user; 179 (Material Guard) target. Critical (`0x44f262 - 0x44f301`): 31, 174, 211 user,
32 target. Magic power boost: 27 and 173 user (`0x44e66e`, `0x44e6a2`).

**Hit chance of a blow** (`0x44aa08 - 0x44b0e8`). The divisor is 1 + the Barcarole (221) of the **target**. Flowing
Water Stance (253) is one more evasion term against a stab blow; a roll that lands only without it is a dodge and its
bearer then performs the skill linked to the status (`0x44b10e - 0x44b20f`). An action with 149 cannot hit an adult,
one with 150 a minor (`0x44affd - 0x44b0e8`): adult is the flag at 0x0C of PlayerStatusData, bit 13 of the flags of an
enemy (Conette, Monica, Grishna, Fiora, Souffle, Ist, Yae, Mefmera, Irena, Siena and Luco are adults).

**Hit chance of a spell** (`0x44d759 - 0x44da43`). Own buffs 167, 309, 197, 222, 337, and 278 and 353 for Lullaby
(skill 205) only; target's evasion 165, 198, 338. The divisor is the value of the target's Nocturne (220), else of its
Kotodama Blessing (223), else 1: Fairy Nocturne (value 5) divides it by 5.

**After the attack function** (`0x421a6a - 0x422c4b`). A hit that missed skips every check after it (`0x421ada`).
Then, in order: nullifying enchantments (120 - 123 against blows of slash, stab, bash or any; 124 - 128 against an
element, any action), All Resistances 100 (192), Nullify Short-Mid (182), Alter Fate, Pretend (310, blows: the damage is
0 and the bearer performs the linked skill), Elegant Dancing, Knock Down (305, long-range blows, the same), Parry,
Counter (any action of short or mid range), Sugar Coma, the counts of Clone, Illusion and Barrier System.

**Chant interruption.** The rate of 2.5 is rolled by the physical function only. A spell breaks a chant only through
the second roll of a critical (`0x44f12c - 0x44f146`).

**Damage C of a blow** (`0x44c5b1 - 0x44c5e9`) is the product of separate factors: the race factor, resistance, the
element factor, zone and defence, the race guard and the critical factor.
* Race factor of a member's blow on an enemy (`0x44bfa4 - 0x44c3b0`): 1 + effect 88 + per piece 0.30 (Grand), 0.15
  (UP) or 0.60 (Mega) of the enchantment against the target's race; against Fruit 1.0 (Mega) and 0.5 (Grand); 1.0 per
  piece of 196 and 209 against the enemies the program lists as felines (`0x6d3820`) and sea creatures (`0x6d38b0`).
* Race guard of an enemy's blow on a member (`0x44bd3b - 0x44bf09`; spell `0x44e914 - 0x44eb36`): 1 - 0.05 per piece of
  the 5% enchantment and 0.10 per piece of the 10% one against the attacker's race.
* Element factor (`0x44c3b5 - 0x44c4c5`): 1 + 0.2 per piece of "(element) attack for both sides UP" (251 - 255) on the
  attacker and on the target.
* A sleeping target takes int(damage * 3 / 2), blow (`0x44cd3b`) and spell (`0x44eff9`). Enchantment 280 adds 15% of
  the damage against a target with an ailment (`0x44cd5a`, `0x44f009`); 271 adds 0.1 per piece to the other bonus while
  the attacker is at full HP (`0x44c9af`, `0x44ec6f`).
* Element boost of a spell (`0x44e019 - 0x44e0c2`): 0.2 for the element's status on the caster, plus 0.2 per piece of
  the element's magic buff (78 - 82) and of 251 - 255, counted on the caster **and** on the target.

**Turns.** A turn lost to petrification, sleep, paralysis, Mesmerized or the Erotic Dance ends through phase 4
(`0x4392ef`, `0x436cf9`, `0x4372ea`) without state 16: no status of the unit ticks or counts down on it, so a sleeping
unit gets no recovery check and sleeps until a hit wakes it or it is cured. The next turn comes after the wait of a plain
action (kind 7: `0x449a24`, `0x449d87`, `0x44a31c`). Warning Shot replaces the command with a skill that does nothing
(`0x4371c3`) and state 16 runs.

**What an ailment ends when it lands** (status creation `0x4f9930`; end calls `0x43bc50` chant, `0x43c110` songs,
`0x43c600` dances, `0x43c9b0` dolls): freeze ends dances and dolls; sleep, stun, Shadow Sew and effect 121 end all four;
silence ends the chant and the songs; petrification ends none. A frozen member cannot use techniques, a silenced one
spells and songs (atwiki dt2-2 page 125). Effect 139 kills only a sleeping target (slot `0xbc`). The statuses whose class
answers yes at slot `0x8c` end at the tick of a sleeping bearer (`0x48d5b5 - 0x48d5d7`), not of any bearer that cannot
act.

**Durations set by passives**: the third argument of CreateCommand is the turns of a status and the starting recovery
chance of an ailment (`0x47b2ea`). Dark Aura's debuffs last 4 turns (`0x423e30`); Ecstasy's buffs 3 (`0x47f5fc`); Slow
Target puts Slow with recovery 5 and speed -0.75 for 5 turns (`0x4244c7`, `0x424559`); Sugar Coma Slow with recovery 5
and speed -0.2 for 3 turns (`0x42291d`, `0x4229df`); Tranquil Song 4 (`0x43752e`). The command methods at slots 0x40 and
0x48 take no argument, so the value pushed before them is that third argument.

**Cures** (`0x481a92 - 0x481b15`): effect 106 looks at the first min(int(value), 7) entries of its list and removes each
one present; a value of exactly 8 also clears the second list. The ATK debuff of the table is never reached.

**Enchantments of a character** (`0x4f8270 - 0x4f8fcf`). The stacking flag is bit 0 of EnchantData 0x20 (memory 0x38
of the record of map `0x7389d0`): set, every piece counts; clear, one piece only (`0x4f5499`, `0x4f8311`). Speed UP has
it set, which agrees with the player test of atwiki page 105. Per piece, on the figures before equipment (growth, bonus
and resets): a stat UP adds int(stat / 10), at least 4; MiniUP int(stat / 20), at least 2; DOWN takes int(stat / 10);
"All stats +N" adds N; Max HP and Max TP the same shares, their sums kept within half the base; resistances +20, +10 and
-20 for one, +50, +15, +7, -15 for the five elements, +25, +10, +5, -10 for the three physical kinds, Mega +100 and
Grand +50 for one, each resistance sum kept within -100 and 100; the line enchantments 222 - 225 and 281 add 8%, 4%
(int(stat / 25)) or 2% (int(stat / 50)) of their stats to a member of the front or the back line. The enchantments
129 - 136 and 139 stop their ailment before its roll, 137 all of them and Shadow Sew (`0x481f2d - 0x4838ae`).

**Resistances of a character** (`0x4f5f04 - 0x4f5f74`): each of the eight is the character's own bonus plus the bonus of
the resets, before the enchantments. The resets therefore add up to 50 to every resistance (atwiki page 79 says so).

**Ambushes** (`0x44a3d0`, called at `0x4491cf - 0x4491e8`): only in a random battle (flag 0x32 of the battle), unless a
unit has Absolute Preemptive Attack (321). The party strikes first on a roll below 100 under 6 + Preemptive Attack
Chance (268) * 100 of the party, failing that the enemies on 4 + theirs; Preemptive Attack Evasion (267) of the other
side rolls to stop it. The side that strikes first starts with full gauges.

**Random targets** (`0x43f8a2 - 0x43f9a4`): one target per hit, picked with equal chances; with effect 112 a unit is not
picked twice.

**Piercing against enemies** (`0x43e1ad - 0x43e476`): the units numbered n + 23 to n + 25 (from the front row) or
n - 25 to n - 23 (from the back): the unit behind and its two diagonals on a grid 24 wide. How an enemy's number comes
from the formation is still to be followed (assumption A10).

### 16.8 Read on 2026-10-08: the last effects the simulator lacked

| Effect | What it does | Where |
|---|---|---|
| 77 Sacrifice (Primevil) | After the action the user takes damage equal to its own max HP | `0x481060` |
| 133 (Life Bringer) | The target loses max HP for good, int(damage of the hit * value), through the modifier of its max HP (unit slot 0x2c adds to 0x98) | `0x483ee0 - 0x483f8a` |
| 137 (Megaton Press) | After the chosen target, the next int(value) - 1 units of its side in the order of turns are hit too | `0x42017a - 0x4202f3` |
| 143 Special Sleep (Showtime) | A sleep command of value 10.0, recovery chance starting at 5, through the roll of sleep: certain unless immune, resistance 100 or a nullifying piece | `0x484150 - 0x48424d` |
| 146, 147 | The doll function builds as many units as 146 says, each living 147 turns plus 297 of the owner; Star Dust Arrow goes through it too and builds two or three arrows whose action is hidden skill 106 (a shot at random targets, 1 to 3 hits, one per target) | `0x484330`, `0x484491 - 0x48449d` |
| 258 Murder | A critical blow by an action or a user that carries it applies instant death at its value, through the roll of instant death | `0x44d26f - 0x44d2cf` |
| 263 Dark Quest | Value times the ailments the attacker carries, added to the "other" bonus of a blow | `0x44c81a - 0x44c896` |
| 305 Knock Down | A long-range blow (by a member only when she holds a weapon) on its bearer rolls value * 100; on a success it does nothing and the bearer performs the skill linked to the status | `0x4221ee - 0x422540` |
| 310 Pretend | A blow on its bearer rolls value * 100; on a success it does nothing and the bearer performs the skill linked to the status | `0x421db8 - 0x42206c` |
| 314 Soul Seal | A doll of a bearer adds to each of its six stats int(stat of the enemy its sealbook seals * value) | `0x4fdfd0 - 0x4fe102` |
| 356 Demon Wall | When any unit of the target's side has it, the damage of a blow or a spell becomes max(0, int(damage * (1 + value))); the values are negative. The code tests no race | `0x44cbf0 - 0x44cc4e`, `0x44ef59` |
| 427 Genjimaru | Unless one is in the battle, a unit built like a doll that performs hidden skill 107 | `0x48b1f0` |
| 432 Enemies Flee | Each enemy targeted is marked as gone when the battle allows running away | `0x48b3c0` |

After these, the battle acts on every effect a skill of the player uses (228 of 228). Still not followed: the skill
linked to 253, 305 and 310 (a plain attack in the model, A17), what ends the arrows of Star Dust Arrow beyond their
life (A28: the GameFAQs guide says interruption does not and the death of the Sniper does), how long Genjimaru stays
(A18). Fixed on the way: the range of a doll's plain attack was read as text and never matched.


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
final = (B + own accuracy enchantments - target evasion enchantments) / Barcarolle   (0x44ae94)
final is kept between 5 and 100                                                      (0x44ae84, 0x44ae8c)
```

* Accuracy buffs read: effects 166, 197, 337. Evasion buffs read: 164, 198, 338; 253 when a flag of the attack is set.
* Enchantments: each piece counts 4, the mini version 2, the sum capped at 50 (`0x44ad3d`, `0x44ad5b`): accuracy UP is +4 points per piece, MiniUP +2, at most +50; the same for evasion.
* Later changes of the final value, each with its own message: fixed accuracy (effect 55), a direct accuracy value (effect 72), sleep, and two effects that work only on adults or only on minors.

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
rate A = damage taken / (max HP * 1.5 * (1 + interruption modifier))     kept between 0 and 0.95
rate   = rate A - enchantments                                           kept between 0 and 0.95
```

* The chance to break a chant grows with the damage of the hit against the caster's max HP: a hit for 30% of max HP interrupts 20% of the time, a hit for 75% half of the time.
* The interruption modifier is effect 264 (Concentrate).
* Enchantments subtract 0.10, 0.06 or 0.03 per piece according to their kind; one adds.
* **[open]** where the "1 in 3 on a critical hit" of the lessons is applied; it is not in these lines.

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
2 and 2.35 for the up and element factors and between 0.5 and 0.75 for the down factors. Which side 3 and 5 stand
for against 4 and 6 (the flag the function receives) is not followed to its callers.

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
* Read in the code (`0x44d370`): the hit chance is kept between 25 and 95 (`0x44da2b`, `0x44da37`); magic accuracy enchantments count 3 per piece, capped at 50 (`0x44d67b`, `0x44d699`); attack A is `INT * (2 + swing)` (`0x44dc97`); the power of the spell is effect 1; the enchantments that boost the magic of one element add 0.20 per piece (`0x44e070` and the five blocks after it, effects 325 to 329).
* **[open]** the rest of this function (defence side, the caps of the other enchantments), the zones ("攻撃値Ａ倍率変更": a zone multiplies attack A, before defence, as the guide says).

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
* In one context (the command comes from a source of kind 4) enchantment 269 on the target takes a flat 15 points off, and enchantment 138 blocks.
* **[open]** turn delay (effect 54) and the skills that skip a turn (Warning Shot, Magnificent Steps): their rolls are separate code.

## 5c. Turn delay (effect 54, `0x423a41`) and the immunity flags of an enemy **[code]**

```
immune  when the target is an enemy whose flag has bit 12 set                              (0x423a9b)
lands   when a roll below 100 is under int(value of the effect * 100)                      (0x423b1b - 0x423b33)
```

* No resistance and no memory enter: the chance is the value of the skill every time, so a delay can be repeated
  without limit against any enemy that lacks the bit. The bit is data, one per enemy.
* How far the target is pushed back in the order list (`0x423b39` onwards) is not read yet.
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

---

## 7. What this already settles

* **Enchantment sizes are constants of the code.** Physical attack and defence UP are 4 points per piece, MiniUP 2, capped at 50; accuracy and evasion the same; damage reductions 10 / 5 and 8 / 4 with a floor at 0.75; race bonuses 30 / 15 / 60. The figures the QoL variant took from the first game's guide can be confirmed or corrected here, and the 101 enchantments without a figure can be read the same way.
* **Buffs of attack add to the power of the skill; they do not multiply it.** The stronger the skill, the less a buff is worth in proportion.
* **Chant interruption is proportional to the damage taken against max HP.** A caster with more HP, or hit by many small hits rather than one large one, is interrupted less. The lever is data (Concentrate, effect 264; HP; the size of enemy hits).
* **Resistance is half a percent per point for every damage type, physical ones included.**
* **Slow halves speed.**
* **The wait until the next turn is `1 - value`, with the value capped at 0.92.** The formula reproduces a player test of the Japanese wiki to the decimal (section 5). Speed is not a ratio: near the cap a small gain in value is a large cut of the wait, which is why speed dominates.

## 8. Still to read

1. In `_SetTime`: the branch for action kind 8 with the chant flag (`0x449e54`), not followed to its end.
2. The magic function, instruction by instruction.
3. The "1 in 3" interruption of a chant by a critical hit; the minimum of a spell.
4. Zones: which side slots 3 and 5 stand for; the map files that place them.
5. Turn delay: how far the target is pushed back. Turn skipping (stun, paralysis): how many turns are lost.
6. TP recovery, revival and the recovery after a battle; EXP division and the factor by level gap. Of targeting (section 9.1): the code that
   returns the formation row, and the name of every attack scope.
7. The enchantments `generated/ENCHANT_SIZES.md` lists with "?" (the table is generated by `tools/exe_enchants.py`).

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

**Choice of attack** (`0x430f10`): the set is 0; the commands before the first set run in order until one decides.
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

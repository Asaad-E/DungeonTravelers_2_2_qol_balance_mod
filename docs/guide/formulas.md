# Battle Formulas

Reference for combat mathematics, damage functions, turn order calculations, and status ailment checks in Dungeon Travelers 2-2. Every formula represents the exact logic executed by the game engine.

---

## Physical Hit Chance

```
Base Hit     = 0.885 * (100 + Attacker DEX) / (100 + Target AGI) + Skill Accuracy
Buffed Hit   = (Attacker Accuracy Buffs - Target Evasion Buffs + Base Hit) * 100
Modified Hit = (Buffed Hit + Accuracy Enchants - Evasion Enchants) / (1 + Target Barcarole)
Hit Chance   = Clamped between 5% and 100%
```

Physical hit chance compares attacker DEX against target AGI in a ratio, adds accuracy modifiers additively, and always retains a 5% minimum and 100% maximum probability.

---

## Physical Attack Power

```
Attack A = Base ATK * (2 + Swing)
Swing    = Random integer between -Weapon Swing and +Weapon Swing
Attack B = Attack A * (1 + Sum of Modifiers) * (1 + Attack Enchants * 0.01)
```

Base ATK is doubled before adding variance, and skill power and physical attack buffs combine additively rather than multiplying each other.

---

## Physical Defence Value

```
Defence A = Target DEF * 1.35 * (1 + Sum of Modifiers) * (1 + Defence Enchants * 0.01)
```

Target DEF is multiplied by 1.35 before applying defence buffs, and the resulting total is subtracted directly from incoming attack power.

---

## Physical Damage Calculation

```
Base Damage    = (Attack B * Damage Multiplier) - Defence A
Row Adjusted   = Base Damage * Range Distance Factor * Damage Cut Enchants
Final Damage   = Row Adjusted * Elemental Resistance * Critical * Defending
Minimum Damage = Guaranteed 3 damage (or 1-2 on critical hit) if final damage is 0 or less
```

Because defence is flatly subtracted from attack, any increase in attack beyond enemy defence converts entirely into direct damage.

---

## Attack Range and Row Distance

```
Distance = 0 (both front row), 1 (one back row), 2 (both back rows)
Short-range: Distance 0 = 100%, Distance 1 = 75%, Distance 2 = 50%
Mid-range:   Distance 0 = 100%, Distance 1 = 100%, Distance 2 = 75%
Long-range / No range: Distance 0/1/2 = 100%
```

Short-range attacks lose 25% damage per row of distance, mid-range attacks only lose damage when both attacker and target occupy back rows, and long-range attacks suffer no distance penalty.

---

## Magic Hit Chance

```
Base Hit   = Spell Accuracy + (Attacker INT - Target RES) * 0.002
Buffed Hit = Base Hit * 100 + Accuracy Enchants - Evasion Enchants
Final Hit  = (Buffed Hit * (1 + Magic Accuracy Buffs) / Nocturne) * (1 - Magic Evasion Buffs)
Hit Chance = Clamped between 25% and 95%
```

Spell hit chance scales slightly with the caster's INT advantage over target RES, and offensive spells always have between a 25% minimum and 95% maximum hit chance.

---

## Magic Damage Calculation

```
Attack A  = Attacker INT * (2 + Spell Swing)
Attack B  = (Attack A + Spell Power) * (1 + Modifiers) * (1 + Element Boost)
Defence A = Target RES * 1.5 * (1 + Modifiers)
Base Damage = Attack B - Defence A
Final Damage = Base Damage * Elemental Resistance * Damage Cut * Critical
```

Spell power adds directly to doubled INT before subtracting 1.5x target RES, allowing high-power spells to overcome enemy magic resistance.

---

## Critical Hits

```
Base Rate  = (Attacker DEX * 0.2) / (Attacker DEX + Target AGI) * 100
Level Term = max(0, (Attacker Level - Target Level) * 0.5)
Total Rate = (Base Rate + Level Term + Skill Bonus) * Enchants
Crit Chance = Clamped between 5% and 50%
Damage Multiplier = 1.25x on critical hit
```

Critical rate scales with DEX and level advantage up to a 50% cap, multiplying damage by 1.25 when triggered.

---

## Turn Order and Action Speed

```
Base Speed   = (AGI + 100) / 200
Weight Bite  = (Weapon Weight / 12) * (1 + Level / 100)
Action Speed = (Base Speed * (1 + Random[0 to 0.05]) - Weight Bite) * Action Speed Factor * 0.5
Gauge Value  = min(0.92, Action Speed * (1 + Speed Buffs + Speed Enchants))
Wait Until Next Turn = 1 - Gauge Value
Slow Status  = Halves action speed
Defending    = Multiplies action speed by 1.15
```

Weapon recovery weight is subtracted from AGI speed and doubles in penalty between level 1 and 99, while action speed caps at 0.92 where turn wait reaches its minimum delay of 0.08.

---

## Status Ailments and Resistance

```
Base Chance     = Effect Infliction Value * 100
Resistance Step = int(Target Resistance / 10)
Modified Chance = Base Chance - Resistance Step * Base Chance / 10
Infliction Roll = Random[0 to 99] < int(Modified Chance)
Immunity Check  = Target with immunity flag or 100+ resistance blocks ailment completely
```

Elemental resistance mitigates status ailment chances in discrete 10-point steps: 50 resistance halves infliction chance, and 100 resistance blocks the ailment entirely.

---

## Turn Delay

```
Immunity Check  = Target must lack turn delay immunity flag
Infliction Roll = Random[0 to 99] < int(Skill Value * 100)
Effect          = Target swaps its position in the turn order with the unit immediately behind it
```

Turn delay bypasses elemental resistance and rolls purely against the skill's base rate, swapping the enemy's place with the next combatant in the turn queue.

---

## Chant Interruption

```
Damage Rate  = Damage Taken / (Target Max HP * 1.5)
Final Rate   = Clamped between 0% and 95%
Crit Check   = Any incoming critical hit makes a separate 33% roll to break the chant
```

Chanting units risk interruption in proportion to damage taken relative to maximum HP, and incoming critical hits have an independent 1 in 3 chance to break the chant immediately.

---

## Healing Calculation

```
Heal Base   = Caster RES * Random[0.48 to 0.52] * Skill Heal Coefficient * (1 + Heal Mastery)
Final Heal  = min(Heal Base, Skill Heal Cap)
Fixed Heal  = Fixed HP value stated by skill
```

Healing scales exclusively with the caster's RES and mastery up to the skill's heal cap, restoring the identical amount on high-HP tanks as on low-HP spellcasters.

---

## Floor Damage Zones

```
Physical Zone Factor = 2.00x to 2.35x (Slot 3 Up) | 0.50x to 0.75x (Slot 5 Down)
Magic Zone Factor    = 2.00x to 2.35x (Slot 4 Up) | 0.50x to 0.75x (Slot 6 Down)
Element Zone Factor  = 2.00x to 2.35x (Slots 7 to 11: Fire, Water, Wind, Earth, Lightning)
Zone Damage Attack   = Attack A * Zone Factor
```

Floor zone factors multiply attack power before defence is subtracted, significantly altering damage output for both allies and enemies on designated map cells.

---

## Post-Battle EXP and Level Gap

```
Level Gap    = Member Level - Enemy Level
Gap Factor   = 0.85x (+10 or higher) | 0.90x (+5 to +9) | 1.00x (-4 to +4) | 1.10x (-9 to -5) | 1.25x (-10 or lower)
EXP Received = (Enemy EXP * Gap Factor / Living Members) * Exp Buffs * Double EXP
```

Defeated enemy EXP is scaled by each member's individual level gap and divided equally among all party members alive at the end of combat.

---

## Skill Point (SP) Progression

```
Level 1          = 3 SP initial pool
Levels 2 to 14   = +1 SP per level
Levels 15 to 26  = +2 SP per level
Levels 27 to 32  = +3 SP per level
Levels 33 to 43  = +4 SP per level
Levels 44 to 48  = +5 SP per level
Levels 49 to 53  = +6 SP per level
Levels 54 to 59  = +7 SP per level
Levels 60 to 64  = +8 SP per level
Levels 65 to 68  = +9 SP per level
Levels 69 to 73  = +10 SP per level
Levels 74 to 77  = +11 SP per level
Levels 78 to 81  = +12 SP per level
Levels 82 to 85  = +13 SP per level
Levels 86 to 89  = +14 SP per level
Levels 90 to 93  = +15 SP per level
Levels 94 to 96  = +16 SP per level
Levels 97 to 98  = +17 SP per level
Level 99         = +18 SP
Total at Lv 99   = 685 SP cumulative
```

Skill point gains increase at fixed level milestones, providing a cumulative total of 685 SP by level 99.

---

## Level Reset and Crown Progression

```
Dropped Levels = Level Before Reset - 1
Stat Points    = +5 (Lv 99 reset) | +4 (Lv 90-98) | +3 (Lv 80-89) | +2 (Lv 70-79) | +1 (Lv 60-69)
Bonus Cap      = +50 to all eight base attributes (10 resets at Lv 99)
```

Resetting a level 99 character back to level 1 permanently awards 5 bonus points across all attributes, reaching the maximum cap of 50 after 10 resets.

# Grand Sealbook Summons

Reference for all 35 Grand Sealbook summons, detailing stat growth factors, attack repertoires, AI weights, and passive enchantments across all three forms.

## Deep Slapyon (Family 322)

- **Grand Sealbook Enchantment:** Damage from non-gas traps 90% DOWN

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 28 | 10 | 1.35x | 0.81x | 0.58x | 0.81x | 0.74x | 0.78x | - |
| Form 2 | 38 | 9 | 2.11x | 1.39x | 0.71x | 0.96x | 1.12x | 0.89x | Double Attack |
| Form 3 | 50 | 7 | 2.41x | 1.62x | 0.92x | 1.13x | 1.23x | 0.96x | Double Attack |

### Deep Slapyon - Form 1 (Lv 28)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 0.90x | - | -0.05 | Plain hit that deals damage |
| God Stamp | Single enemy | Bash | 0.75x | - | -0.1 | Plain hit that deals damage; Number of targets (3) |
| I'll Curse You | Single enemy | Neutral | 1.00x | - | - | Deals no damage; Poison (0.6); Silence (0.5) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 4) -> set 1
**Action Sets:**
- **Set 0:** Attack (35%), God Stamp (10%), I'll Curse You (20%), Take Break (15%), Take Break (20%)
- **Set 1:** Attack (20%), God Stamp (80%)

### Deep Slapyon - Form 2 (Lv 38)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Poison (0.1) |
| Bunmawashi | Random enemies | Weapon's | 0.50x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| God Stamp | Single enemy | Bash | 0.85x | - | 0.2 | Plain hit that deals damage; Number of targets (3) |
| I'll Curse Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Poison (0.75); Silence (0.35) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Bunmawashi (slot 1) -> set 1
- last skill used is God Stamp (slot 2) -> set 2
- last skill used is I'll Curse Everyone (slot 3) -> set 3
**Action Sets:**
- **Set 0:** Attack (25%), Bunmawashi (15%), God Stamp (25%), I'll Curse Everyone (20%), Take Break (10%), Take Break (5%)
- **Set 1:** Attack (80%), Take Break (10%), Take Break (10%)
- **Set 2:** Attack (40%), I'll Curse Everyone (40%), Take Break (10%), Take Break (10%)
- **Set 3:** Attack (60%), Bunmawashi (10%), God Stamp (10%), Take Break (10%), Take Break (10%)

### Deep Slapyon - Form 3 (Lv 50)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Poison (0.1) |
| Bunmawashi | Random enemies | Weapon's | 0.65x | - | 0.33 | Plain hit that deals damage; Hits 1-3 times |
| God Stamp | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Number of targets (4) |
| Slapyon Lotion | Single enemy | Neutral | 1.10x | - | - | Deals no damage; Physical accuracy modifier (-0.15) |
| I'll Curse Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Poison (0.75); Silence (0.35) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Bunmawashi (slot 1) -> set 1
- last skill used is God Stamp (slot 2) -> set 2
- last skill used is Slapyon Lotion (slot 3) -> set 3
- last skill used is I'll Curse Everyone (slot 4) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), Bunmawashi (20%), God Stamp (15%), Slapyon Lotion (15%), I'll Curse Everyone (15%), Take Break (10%), Take Break (5%)
- **Set 1:** Attack (80%), Take Break (10%), Take Break (10%)
- **Set 2:** Attack (80%), Take Break (10%), Take Break (10%)
- **Set 3:** Attack (80%), Take Break (10%), Take Break (10%)
- **Set 4:** Attack (80%), Take Break (10%), Take Break (10%)

## Overdue (Family 331)

- **Grand Sealbook Enchantment:** Increase Mimic appearance rate in chests

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 68 | 11 | 1.57x | 1.25x | 0.67x | 1.21x | 0.83x | 0.72x | - |
| Form 2 | 76 | 10 | 2.16x | 1.42x | 0.82x | 1.36x | 0.94x | 0.88x | - |
| Form 3 | 87 | 7 | 2.61x | 1.63x | 1.11x | 1.52x | 1.02x | 0.94x | Triple Attack |

### Overdue - Form 1 (Lv 68)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Slow (0.2) |
| Surprise Fist | All enemies | Neutral | 0.55x | - | 0.15 | Fixed accuracy (0.5); Plain hit that deals damage; Stun (0.4) |
| Sleep | All enemies | Wind | 1.60x | 1.2s | - | Deals no damage; Sleep |
| I'll Torment Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Paralysis (0.35); Slow (0.5) |
| Dispel | All enemies | Neutral | 1.50x | 1.4s | - | Deals no damage; Dispel |
| Honey Great | Single ally | Neutral | 1.00x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Honey Great (slot 5) -> set 3 (stop)
- lowest HP ratio among allies <= 30 -> set 2 (stop)
- an opponent has a buff -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (25%), Surprise Fist (15%), Sleep (10%), I'll Torment Everyone (20%), Take Break (15%), Take Break (15%)
- **Set 1:** Attack (10%), Sleep (10%), I'll Torment Everyone (10%), Dispel (50%), Take Break (20%)
- **Set 2:** Surprise Fist (20%), Honey Great (60%), Take Break (20%)
  - *Condition:* Honey Great (slot 5) aims at: ally with the lowest HP ratio
- **Set 3:** Take Break (100%)

### Overdue - Form 2 (Lv 76)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Slow (0.2) |
| Surprise Fist | All enemies | Neutral | 1.00x | - | 0.3 | Fixed accuracy (0.5); Plain hit that deals damage; Stun (0.5) |
| Sleep | All enemies | Wind | 1.60x | 1.2s | - | Deals no damage; Sleep |
| I'll Torment Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Paralysis (0.35); Slow (0.5) |
| Dispel | All enemies | Neutral | 1.50x | 1.4s | - | Deals no damage; Dispel |
| Honey Excite | Single ally | Neutral | 1.00x | - | - | - |
| Self-Destruct Dry Run | Enemy row | Neutral | 0.10x | - | - | Plain hit that deals damage; Fixed damage (666) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 50 -> set 1 (stop)
- an opponent has a buff -> set 2 (stop)
- last skill used is Sleep (slot 2) -> set 3 (stop)
- last skill used is I'll Torment Everyone (slot 3) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 4 (stop)
- last skill used is Self-Destruct Dry Run (slot 6) -> set 5 (stop)
**Action Sets:**
- **Set 0:** Attack (30%), Surprise Fist (20%), Sleep (15%), I'll Torment Everyone (15%), Take Break (20%)
- **Set 1:** Surprise Fist (20%), Honey Excite (70%), Take Break (10%)
  - *Condition:* Honey Excite (slot 5) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Dispel (60%), Take Break (20%)
  - *Condition:* Dispel (slot 4) aims at: opponent with a buff
- **Set 3:** Attack (20%), Surprise Fist (20%), Take Break (60%)
- **Set 4:** Self-Destruct Dry Run (80%), Take Break (20%)
- **Set 5:** Take Break (100%)

### Overdue - Form 3 (Lv 87)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Slow (0.2) |
| Surprise Fist | All enemies | Neutral | 1.25x | - | 0.4 | Fixed accuracy (0.5); Plain hit that deals damage; Stun (0.5) |
| Sleep | All enemies | Wind | 1.60x | 1.2s | - | Deals no damage; Sleep |
| I'll Torment Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Paralysis (0.35); Slow (0.5) |
| Dispel | All enemies | Neutral | 1.50x | 1.6s | - | Deals no damage; Dispel |
| Double Honey Excite | Single ally | Neutral | 1.00x | - | - | - |
| Self-Destruct Dry Run | Enemy row | Neutral | 0.10x | - | - | Plain hit that deals damage; Fixed damage (666) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 60 -> set 1 (stop)
- an opponent has a buff -> set 2 (stop)
- last skill used is Sleep (slot 2) -> set 3 (stop)
- last skill used is I'll Torment Everyone (slot 3) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 4 (stop)
- last skill used is Self-Destruct Dry Run (slot 6) -> set 5 (stop)
**Action Sets:**
- **Set 0:** Attack (25%), Surprise Fist (25%), Sleep (15%), I'll Torment Everyone (15%), Take Break (20%)
- **Set 1:** Surprise Fist (20%), Double Honey Excite (80%)
  - *Condition:* Double Honey Excite (slot 5) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Surprise Fist (20%), Dispel (60%)
  - *Condition:* Dispel (slot 4) aims at: opponent with a buff
- **Set 3:** Attack (20%), Surprise Fist (20%), Take Break (60%)
- **Set 4:** Self-Destruct Dry Run (80%), Take Break (20%)
- **Set 5:** Take Break (100%)

## Tres Durian (Family 524)

- **Grand Sealbook Enchantment:** Greatly reduce encounter rate

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 44 | 11 | 0.82x | 0.49x | 0.51x | 0.64x | 0.52x | 0.82x | - |
| Form 2 | 57 | 7 | 1.77x | 0.68x | 0.83x | 0.73x | 0.68x | 0.94x | - |
| Form 3 | 70 | 6 | 2.06x | 0.77x | 0.97x | 0.84x | 0.77x | 1.06x | - |

### Tres Durian - Form 1 (Lv 44)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.2) |
| Full Maturity | Self | Neutral | 1.50x | - | - | DEF modifier (-0.2); ATK modifier (0.2) |
| Modest Fever | Enemy row | Neutral | 0.80x | - | - | Plain hit that deals damage; Fixed damage (222) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1
- last skill used is Take Break (slot 5) -> set 2
- last skill used is Modest Fever (slot 2) -> set 3
**Action Sets:**
- **Set 0:** Attack (40%), Full Maturity (40%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (30%), Full Maturity (30%), Take Break (40%)
- **Set 2:** Attack (15%), Full Maturity (15%), Modest Fever (70%)
- **Set 3:** Take Break (50%), Take Break (50%)

### Tres Durian - Form 2 (Lv 57)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.2) |
| Full Maturity | Self | Neutral | 1.50x | - | - | DEF modifier (-0.2); ATK modifier (0.2) |
| Modest Fever | Enemy row | Neutral | 0.80x | - | - | Plain hit that deals damage; Fixed damage (222) |
| Dinner | Single ally | Neutral | 0.65x | - | - | - |
| 2 a.m. | Single enemy | Neutral | 0.90x | - | - | Deals no damage; Petrification (0.5) |
| Summon Slave | None | Neutral | 0.70x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- Summon Slave (slot 5) is active -> set 4 (stop)
- last skill used is Modest Fever (slot 2) -> set 3
- last skill used is Take Break (slot 6) -> set 2
- lowest TP ratio among allies <= 70 -> set 1
**Action Sets:**
- **Set 0:** Attack (35%), Full Maturity (35%), Take Break (30%)
- **Set 1:** Attack (20%), Dinner (80%)
  - *Condition:* Dinner (slot 3) aims at: ally with the lowest TP ratio
- **Set 2:** Attack (15%), Full Maturity (15%), Modest Fever (25%), 2 a.m. (20%), Summon Slave (25%)
- **Set 3:** Attack (40%), Full Maturity (40%), Take Break (20%)
- **Set 4:** Attack (40%), Full Maturity (20%), Take Break (40%)

### Tres Durian - Form 3 (Lv 70)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.6) |
| Full Maturity | Self | Neutral | 1.50x | - | - | DEF modifier (-0.2); ATK modifier (0.2) |
| Modest Fever | Enemy row | Neutral | 0.80x | - | - | Plain hit that deals damage; Fixed damage (333) |
| Dinner | Single ally | Neutral | 0.65x | - | - | - |
| Earth Glaive | Piercing | Earth | 0.95x | - | - | Magic power (450) |
| Summon Slave | None | Neutral | 0.70x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest TP ratio among allies <= 70 -> set 1 (stop)
- last skill used is Full Maturity (slot 1) -> set 2 (stop)
- last skill used is Modest Fever (slot 2) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (30%), Full Maturity (30%), Summon Slave (20%), Take Break (20%)
  - *Condition:* Summon Slave (slot 5) was used 1 times or more -> Full Maturity (slot 1)
- **Set 1:** Attack (20%), Dinner (60%), Take Break (20%)
  - *Condition:* Dinner (slot 3) aims at: ally with the lowest TP ratio
- **Set 2:** Attack (20%), Modest Fever (30%), Earth Glaive (30%), Take Break (20%)
- **Set 3:** Take Break (100%)

## Mangos Queen (Family 526)

- **Grand Sealbook Enchantment:** Greatly increase encounter rate

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 44 | 11 | 0.75x | 0.54x | 0.58x | 0.61x | 0.59x | 0.67x | - |
| Form 2 | 57 | 10 | 1.63x | 0.72x | 0.92x | 0.78x | 0.75x | 0.85x | - |
| Form 3 | 70 | 9 | 1.97x | 0.83x | 1.15x | 0.91x | 0.88x | 0.94x | - |

### Mangos Queen - Form 1 (Lv 44)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Poison (0.2) |
| Full Maturity | Self | Neutral | 1.50x | - | - | DEF modifier (-0.2); ATK modifier (0.2) |
| Fruit Juice Splash | Single enemy | Neutral | 0.90x | - | - | Deals no damage; DEF modifier (-0.12) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1
- last skill used is Take Break (slot 5) -> set 2
- last skill used is Fruit Juice Splash (slot 2) -> set 3
**Action Sets:**
- **Set 0:** Attack (40%), Full Maturity (40%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (30%), Full Maturity (30%), Take Break (40%)
- **Set 2:** Attack (15%), Full Maturity (15%), Fruit Juice Splash (70%)
- **Set 3:** Take Break (50%), Take Break (50%)

### Mangos Queen - Form 2 (Lv 57)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Poison (0.2) |
| Full Maturity | Self | Neutral | 1.50x | - | - | DEF modifier (-0.2); ATK modifier (0.2) |
| Fruit Juice Splash | Single enemy | Neutral | 0.90x | - | - | Deals no damage; DEF modifier (-0.12) |
| Paralyze | All enemies | Lightning | 1.75x | 1.2s | - | Deals no damage; Paralysis |
| Heart Corruption | Single enemy | Neutral | 0.85x | - | 0.05 | Plain hit that deals damage; Hits 3-5 times |
| Piercing Panic Voice | Piercing | Neutral | 0.95x | - | - | Magic power (300); Stun (0.35) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 8) -> set 3
- last skill used is Piercing Panic Voice (slot 5) -> set 2
- last skill used is Heart Corruption (slot 4) -> set 2
- last skill used is Take Break (slot 6) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Full Maturity (20%), Fruit Juice Splash (15%), Paralyze (15%), Take Break (20%), Take Break (10%)
- **Set 1:** Heart Corruption (50%), Piercing Panic Voice (50%)
- **Set 2:** Take Break (100%)
- **Set 3:** Attack (60%), Full Maturity (20%), Fruit Juice Splash (20%)

### Mangos Queen - Form 3 (Lv 70)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | 0.15 | Plain hit that deals damage; Poison (0.6) |
| Full Maturity | Self | Neutral | 1.50x | - | - | DEF modifier (-0.2); ATK modifier (0.2) |
| Fruit Juice Splash | Single enemy | Neutral | 0.90x | - | - | Deals no damage; DEF modifier (-0.12) |
| Paralyze | All enemies | Lightning | 1.75x | 1.2s | - | Deals no damage; Paralysis |
| Heart Corruption | Single enemy | Neutral | 0.85x | - | 0.05 | Plain hit that deals damage; Hits 3-5 times |
| Piercing Panic Voice | Piercing | Neutral | 0.80x | - | - | Magic power (650); Stun (0.35) |
| Experience Paean | All allies | Neutral | 1.35x | 0.5s | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Full Maturity (slot 1) -> set 2 (stop)
- last skill used is Piercing Panic Voice (slot 5) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (70%), Full Maturity (30%)
- **Set 1:** Fruit Juice Splash (30%), Paralyze (30%), Heart Corruption (20%), Take Break (20%)
- **Set 2:** Attack (20%), Piercing Panic Voice (20%), Experience Paean (40%), Take Break (20%)
- **Set 3:** Take Break (100%)

## Iktomi (Family 712)

- **Grand Sealbook Enchantment:** Back line INT + RES 4% UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 66 | 8 | 1.56x | 0.72x | 0.84x | 0.78x | 0.92x | 0.81x | Double Attack |
| Form 2 | 75 | 7 | 2.36x | 0.86x | 1.16x | 0.94x | 1.15x | 0.96x | Double Attack |
| Form 3 | 84 | 5 | 2.62x | 0.99x | 1.27x | 1.09x | 1.28x | 1.06x | Double Attack |

### Iktomi - Form 1 (Lv 66)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Gotcha! | Single enemy | Bash | 0.95x | - | 0.3 | Plain hit that deals damage; Slow (0.3) |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Paralysis (0.4) |
| Bat Spell | All enemies | Neutral | 1.20x | 1.15s | - | Magic power (300); Poison (0.5) |
| Spider Net | All enemies | Neutral | 1.15x | - | - | Deals no damage; Speed modifier (-0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Bat Spell (slot 3) -> set 1 (stop)
- last skill used is Spider Net (slot 4) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Gotcha! (20%), Got Your Heart! (20%), Bat Spell (10%), Spider Net (10%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (30%), Gotcha! (10%), Got Your Heart! (10%), Take Break (50%)
- **Set 2:** Attack (30%), Gotcha! (10%), Got Your Heart! (10%), Take Break (50%)
- **Set 3:** Attack (20%), Gotcha! (40%), Got Your Heart! (40%)

### Iktomi - Form 2 (Lv 75)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Gotcha! | Single enemy | Bash | 1.05x | - | 0.4 | Plain hit that deals damage; Slow (0.4) |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.55 | Plain hit that deals damage; Paralysis (0.4) |
| Got Your Life! | Single enemy | Bash | 0.95x | - | 0.15 | Plain hit that deals damage; Instant death (0.15) |
| Bat Spell | All enemies | Neutral | 1.40x | 1.15s | - | Magic power (400); Poison (0.5) |
| Spider Net | All enemies | Neutral | 1.15x | - | - | Deals no damage; Speed modifier (-0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Spider Net (slot 5) -> set 1 (stop)
- last skill used is Gotcha! (slot 1) -> set 2 (stop)
- last skill used is Got Your Heart! (slot 2) -> set 2 (stop)
- last skill used is Got Your Life! (slot 3) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
- last skill used is Bat Spell (slot 4) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Gotcha! (15%), Got Your Heart! (15%), Got Your Life! (15%), Spider Net (15%), Take Break (20%)
  - *Condition:* Spider Net (slot 5) was used 2 times or more -> Attack (slot 0)
- **Set 1:** Attack (20%), Gotcha! (20%), Got Your Heart! (20%), Got Your Life! (20%), Take Break (20%)
- **Set 2:** Attack (40%), Take Break (60%)
- **Set 3:** Attack (30%), Bat Spell (70%)
- **Set 4:** Take Break (100%)

### Iktomi - Form 3 (Lv 84)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Gotcha! | Single enemy | Bash | 1.05x | - | 0.4 | Plain hit that deals damage; Slow (0.4) |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.55 | Plain hit that deals damage; Paralysis (0.4) |
| Got Your Life! | Single enemy | Bash | 0.95x | - | 0.25 | Plain hit that deals damage; Instant death (0.2) |
| Bat Spell | All enemies | Neutral | 1.40x | 1.15s | - | Magic power (400); Poison (0.5) |
| Spider Net | All enemies | Neutral | 1.15x | - | - | Deals no damage; Speed modifier (-0.1) |
| Frost Slash | Single enemy | Water | 0.80x | - | 0.55 | Plain hit that deals damage; Freeze (0.4) |
| Totemic Fire | Single enemy | Fire | 0.65x | - | - | Magic power (650) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 8) -> set 1 (stop)
- last skill used is Bat Spell (slot 4) -> set 2 (stop)
- last skill used is Totemic Fire (slot 7) -> set 2 (stop)
- last skill used is Spider Net (slot 5) -> set 3 (stop)
- last skill used is Frost Slash (slot 6) -> set 3 (stop)
- last skill used is Take Break (slot 9) -> set 4 (stop)
- last skill used is Take Break (slot 10) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (5%), Gotcha! (15%), Got Your Heart! (15%), Got Your Life! (15%), Spider Net (10%), Frost Slash (15%), Take Break (25%)
- **Set 1:** Bat Spell (50%), Totemic Fire (50%)
- **Set 2:** Gotcha! (30%), Got Your Heart! (30%), Take Break (40%)
- **Set 3:** Got Your Heart! (30%), Got Your Life! (30%), Take Break (40%)
- **Set 4:** Gotcha! (25%), Got Your Heart! (25%), Got Your Life! (25%), Bat Spell (25%)

## Scanner (Family 716)

- **Grand Sealbook Enchantment:** Magic incantations go very fast... sometimes

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 52 | 8 | 1.87x | 0.71x | 1.09x | 0.63x | 1.11x | 0.77x | - |
| Form 2 | 65 | 6 | 2.37x | 0.83x | 1.21x | 0.79x | 1.19x | 0.86x | - |
| Form 3 | 78 | 5 | 2.71x | 0.94x | 1.34x | 0.92x | 1.31x | 0.97x | - |

### Scanner - Form 1 (Lv 52)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Lightning | 1.00x | - | - | Plain hit that deals damage |
| Electric Uppercut | Single enemy | Lightning | 0.85x | - | 0.15 | Plain hit that deals damage; Stun (0.5) |
| Energy Ball | Single enemy | Neutral | 0.90x | - | - | Magic power (300) |
| Energy Wave | All enemies | Lightning | 0.85x | - | - | Magic power (200) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Energy Wave (slot 3) -> set 1 (stop)
- last skill used is Take Break (slot 6) -> set 2 (stop)
- last skill used is Take Break (slot 4) -> set 3 (stop)
- last skill used is Take Break (slot 5) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (25%), Electric Uppercut (20%), Energy Ball (20%), Energy Wave (10%), Take Break (15%), Take Break (10%)
- **Set 1:** Attack (25%), Take Break (75%)
- **Set 2:** Attack (20%), Electric Uppercut (80%)
- **Set 3:** Electric Uppercut (50%), Energy Ball (50%)
- **Set 4:** Attack (50%), Energy Wave (50%)

### Scanner - Form 2 (Lv 65)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Lightning | 1.00x | - | - | Plain hit that deals damage |
| Fleet Foot | Self | Neutral | 1.15x | - | - | Speed modifier (0.25) |
| Electric Uppercut | Single enemy | Lightning | 0.95x | - | 0.3 | Plain hit that deals damage; Stun (0.75) |
| Energy Ball | Single enemy | Neutral | 0.90x | - | - | Magic power (400) |
| Energy Wave | All enemies | Lightning | 0.85x | - | - | Magic power (280) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 5) -> set 2 (stop)
- last skill used is Energy Wave (slot 4) -> set 3 (stop)
- Fleet Foot (slot 1) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Fleet Foot (20%), Electric Uppercut (20%), Energy Ball (10%), Take Break (10%), Take Break (20%)
- **Set 1:** Attack (30%), Electric Uppercut (20%), Energy Ball (20%), Take Break (30%)
- **Set 2:** Energy Ball (20%), Energy Wave (80%)
- **Set 3:** Attack (40%), Electric Uppercut (20%), Take Break (40%)

### Scanner - Form 3 (Lv 78)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Lightning | 1.00x | - | - | Plain hit that deals damage |
| Fleet Foot | Self | Neutral | 1.15x | - | - | Speed modifier (0.25) |
| Electric Uppercut | Single enemy | Lightning | 0.95x | - | 0.3 | Plain hit that deals damage; Stun (0.75) |
| Energy Ball | Single enemy | Neutral | 0.90x | - | - | Magic power (650) |
| Energy Wave | All enemies | Lightning | 0.85x | - | - | Magic power (400) |
| Power Charge | Self | Neutral | 1.25x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 6) -> set 1 (stop)
- last skill used is Energy Ball (slot 3) -> set 3 (stop)
- last skill used is Energy Wave (slot 4) -> set 3 (stop)
- Power Charge (slot 5) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Fleet Foot (15%), Electric Uppercut (20%), Energy Ball (15%), Energy Wave (15%), Power Charge (10%), Take Break (15%)
  - *Condition:* Fleet Foot (slot 1) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (20%), Energy Ball (30%), Power Charge (50%)
- **Set 2:** Attack (50%), Electric Uppercut (50%)
- **Set 3:** Attack (30%), Take Break (70%)

## Murasaki Shikibu (Family 722)

- **Grand Sealbook Enchantment:** TP recovers slightly while defending

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 82 | 8 | 2.45x | 0.92x | 0.89x | 0.93x | 0.84x | 0.93x | Triple Attack |
| Form 2 | 90 | 7 | 3.11x | 1.07x | 1.04x | 1.11x | 0.96x | 1.01x | Triple Attack |
| Form 3 | 97 | 5 | 3.33x | 1.15x | 1.18x | 1.22x | 1.09x | 1.11x | Triple Attack |

### Murasaki Shikibu - Form 1 (Lv 82)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Brushstroke | Single enemy | Weapon's | 0.87x | - | 0.4 | Plain hit that deals damage |
| Kakizome | Enemy row | Bash | 0.75x | - | 0.25 | Plain hit that deals damage; Damage change for each later target or hit (-0.1) |
| Rumbling Thunder | Enemy row | Lightning | 0.80x | - | - | Magic power (475); Paralysis (0.25) |
| Blissful Chorale | All allies | Neutral | 1.35x | 0.6s | - | - |
| Summon Shikigami | None | Neutral | 0.80x | - | - | Number of units summoned; Turns a summon lasts (2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 6) -> set 1 (stop)
- last skill used is Take Break (slot 7) -> set 2 (stop)
- Summon Shikigami (slot 5) is active -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Brushstroke (20%), Kakizome (20%), Blissful Chorale (15%), Take Break (15%), Take Break (15%)
  - *Condition:* Blissful Chorale (slot 4) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Brushstroke (30%), Rumbling Thunder (70%)
- **Set 2:** Rumbling Thunder (30%), Summon Shikigami (70%)
- **Set 3:** Attack (30%), Brushstroke (20%), Kakizome (20%), Take Break (30%)

### Murasaki Shikibu - Form 2 (Lv 90)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Brushstroke | Single enemy | Weapon's | 0.93x | - | 0.55 | Plain hit that deals damage |
| Kakizome | Enemy row | Bash | 0.80x | - | 0.35 | Plain hit that deals damage; Damage change for each later target or hit (-0.05) |
| Rumbling Thunder | Enemy row | Lightning | 0.80x | - | - | Magic power (475); Paralysis (0.25) |
| Blissful Chorale | All allies | Neutral | 1.35x | 0.7s | - | - |
| Summon Shikigami | None | Neutral | 0.80x | - | - | Number of units summoned; Turns a summon lasts (2) |
| Tempest | Single enemy | Wind | 1.40x | 1.1s | - | Magic power (800) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Tempest (slot 6) -> set 1 (stop)
- last skill used is Take Break (slot 7) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
- Summon Shikigami (slot 5) is active -> set 4 (stop)
**Action Sets:**
- **Set 0:** Brushstroke (25%), Kakizome (20%), Blissful Chorale (20%), Tempest (15%), Take Break (20%)
  - *Condition:* Blissful Chorale (slot 4) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (30%), Take Break (70%)
- **Set 2:** Rumbling Thunder (40%), Summon Shikigami (60%)
- **Set 3:** Attack (50%), Brushstroke (50%)
- **Set 4:** Attack (30%), Brushstroke (20%), Kakizome (20%), Take Break (30%)

### Murasaki Shikibu - Form 3 (Lv 97)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.5) |
| Brushstroke | Single enemy | Weapon's | 1.00x | - | 0.75 | Plain hit that deals damage; Physical accuracy modifier (-0.08); Magic accuracy modifier (-0.08) |
| Kakizome | Enemy row | Bash | 0.80x | - | 0.6 | Plain hit that deals damage; Damage change for each later target or hit (-0.05) |
| Calling Thunder | All enemies | Lightning | 0.90x | - | - | Magic power (700); Paralysis (0.75) |
| Blissful Chorale | All allies | Neutral | 1.35x | 0.8s | - | - |
| Summon Shikigami | None | Neutral | 1.00x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Tempest | Single enemy | Wind | 1.25x | 0.9s | - | Magic power (1500) |
| Circle Nurse | All allies | Neutral | 1.00x | 0.85s | - | How many ailments of the listed order it cures (8) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 4 (stop)
- Summon Shikigami (slot 5) is active -> set 3 (stop)
- last skill used is Brushstroke (slot 1) -> set 1 (stop)
- last skill used is Take Break (slot 8) -> set 1 (stop)
- last skill used is Tempest (slot 6) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Brushstroke (20%), Kakizome (25%), Blissful Chorale (20%), Tempest (20%), Take Break (15%)
  - *Condition:* Blissful Chorale (slot 4) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Calling Thunder (40%), Summon Shikigami (60%)
- **Set 2:** Attack (50%), Take Break (50%)
- **Set 3:** Attack (30%), Brushstroke (30%), Kakizome (20%), Take Break (20%)
- **Set 4:** Brushstroke (20%), Kakizome (15%), Calling Thunder (15%), Circle Nurse (50%)
  - *Condition:* Circle Nurse (slot 7) aims at: ally with the heaviest ailment

## Serika (Family 726)

- **Grand Sealbook Enchantment:** Reduce damage penalty for missed spells

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 25 | 10 | 0.66x | 0.54x | 1.12x | 0.83x | 0.72x | 0.87x | - |
| Form 2 | 34 | 7 | 0.75x | 0.63x | 1.33x | 0.91x | 0.84x | 0.96x | Critical Magic |
| Form 3 | 44 | 6 | 0.95x | 0.71x | 1.65x | 1.09x | 0.96x | 1.02x | Critical Magic |

### Serika - Form 1 (Lv 25)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Lightning | 1.00x | - | - | Plain hit that deals damage |
| Fireball | Single enemy | Fire | 1.50x | 1.1s | - | Magic power (100) |
| Fire Blast | Enemy row | Fire | 1.00x | 0.88s | - | Magic power (80) |
| Thunderbolt | Single enemy | Lightning | 1.50x | 1.1s | - | Magic power (100) |
| Thunder Chain | Enemy row | Lightning | 1.00x | 0.88s | - | Magic power (80) |
| Air Cutter | Single enemy | Wind | 1.50x | 1.1s | - | Magic power (100) |
| Stone Hammer | Single enemy | Earth | 1.50x | 1.1s | - | Magic power (100) |
| Broom Attack | Enemy row | Bash | 0.90x | - | 0.25 | Plain hit that deals damage; Damage change for each later target or hit (-0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Fire Blast (slot 2) -> set 1 (stop)
- last skill used is Thunder Chain (slot 4) -> set 1 (stop)
- last skill used is Take Break (slot 8) -> set 2 (stop)
- last skill used is Take Break (slot 9) -> set 2 (stop)
- last skill used is Broom Attack (slot 7) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Fireball (10%), Fire Blast (10%), Thunderbolt (10%), Thunder Chain (10%), Air Cutter (10%), Stone Hammer (10%), Take Break (25%)
- **Set 1:** Attack (25%), Take Break (75%)
- **Set 2:** Broom Attack (100%)
- **Set 3:** Attack (10%), Fireball (10%), Thunderbolt (10%), Air Cutter (10%), Stone Hammer (10%), Take Break (50%)

### Serika - Form 2 (Lv 34)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Lightning | 1.00x | - | 0.15 | Plain hit that deals damage |
| Fireball | Single enemy | Fire | 1.50x | 1.05s | - | Magic power (200) |
| Fire Blast | Enemy row | Fire | 1.20x | 0.88s | - | Magic power (150) |
| Thunderbolt | Single enemy | Lightning | 1.50x | 1.05s | - | Magic power (200) |
| Thunder Chain | Enemy row | Lightning | 1.20x | 0.88s | - | Magic power (150) |
| Air Cutter | Single enemy | Wind | 1.50x | 1.05s | - | Magic power (200) |
| Stone Hammer | Single enemy | Earth | 1.50x | 1.05s | - | Magic power (200) |
| Stone Shower | Enemy row | Earth | 1.20x | 0.88s | - | Magic power (150) |
| Broom Attack | Enemy row | Bash | 0.90x | - | 1 | Plain hit that deals damage; Damage change for each later target or hit (-0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Fire Blast (slot 2) -> set 1 (stop)
- last skill used is Thunder Chain (slot 4) -> set 1 (stop)
- last skill used is Stone Shower (slot 7) -> set 1 (stop)
- last skill used is Take Break (slot 9) -> set 2 (stop)
- last skill used is Broom Attack (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Fireball (10%), Fire Blast (10%), Thunderbolt (10%), Thunder Chain (10%), Air Cutter (10%), Stone Hammer (10%), Stone Shower (10%), Take Break (20%)
- **Set 1:** Attack (25%), Take Break (75%)
- **Set 2:** Broom Attack (100%)
- **Set 3:** Attack (10%), Fireball (10%), Thunderbolt (10%), Air Cutter (10%), Stone Hammer (10%), Take Break (50%)

### Serika - Form 3 (Lv 44)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Lightning | 1.00x | - | 0.3 | Plain hit that deals damage |
| Fire Blast | Enemy row | Fire | 1.20x | 0.82s | - | Magic power (280) |
| Inferno | All enemies | Fire | 1.10x | 0.82s | - | Magic power (200) |
| Thunder Chain | Enemy row | Lightning | 1.20x | 0.82s | - | Magic power (230) |
| Muon Plasma | Single enemy | Lightning | 1.00x | 0.95s | - | Magic power (400) |
| Air Turbulence | Enemy row | Wind | 1.20x | 0.78s | - | Magic power (280) |
| Gaia Crush | Single enemy | Earth | 1.00x | 0.95s | - | Magic power (400) |
| Broom Attack | Enemy row | Bash | 0.90x | - | 1.5 | Plain hit that deals damage; Damage change for each later target or hit (-0.1) |
| Musiy | None | Neutral | 0.80x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Muon Plasma (slot 4) -> set 2 (stop)
- last skill used is Gaia Crush (slot 6) -> set 2 (stop)
- last skill used is Take Break (slot 9) -> set 3 (stop)
- Musiy (slot 8) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Fire Blast (10%), Thunder Chain (10%), Muon Plasma (10%), Air Turbulence (10%), Gaia Crush (10%), Musiy (20%), Take Break (20%)
- **Set 1:** Attack (10%), Fire Blast (20%), Thunder Chain (30%), Air Turbulence (10%), Broom Attack (15%), Take Break (15%)
- **Set 2:** Broom Attack (75%), Take Break (25%)
- **Set 3:** Inferno (60%), Muon Plasma (20%), Gaia Crush (20%)

## Martial Artist (Family 730)

- **Grand Sealbook Enchantment:** Attack vs. high lvl enemies UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 38 | 11 | 2.02x | 1.02x | 0.48x | 0.81x | 1.12x | 0.72x | - |
| Form 2 | 49 | 9 | 2.31x | 1.13x | 0.57x | 0.92x | 1.26x | 0.82x | Triple Attack |
| Form 3 | 62 | 7 | 2.59x | 1.24x | 0.64x | 1.02x | 1.38x | 1.02x | Triple Attack |

### Martial Artist - Form 1 (Lv 38)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 0.90x | - | -0.05 | Plain hit that deals damage |
| Strangle | Single enemy | Neutral | 0.60x | - | 0.1 | Plain hit that deals damage; Stun (0.25) |
| Brawl Punch | Random enemies | Bash | 0.60x | - | -0.2 | Plain hit that deals damage; Hits 1-3 times |
| Cinnabar Palm | Single enemy | Stab | 0.80x | - | - | Plain hit that deals damage; Poison (0.5) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 4) -> set 2
- last skill used is Take Break (slot 5) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Strangle (15%), Brawl Punch (15%), Cinnabar Palm (20%), Take Break (15%), Take Break (10%), Take Break (5%)
- **Set 1:** Attack (25%), Strangle (25%), Brawl Punch (25%), Cinnabar Palm (25%)
- **Set 2:** Strangle (50%), Brawl Punch (50%)

### Martial Artist - Form 2 (Lv 49)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Strangle | Single enemy | Neutral | 0.60x | - | 0.1 | Plain hit that deals damage; Stun (0.25) |
| Brawl Punch | Random enemies | Bash | 0.80x | - | -0.1 | Plain hit that deals damage; Hits 1-3 times |
| Cinnabar Palm | Single enemy | Stab | 0.95x | - | 0.3 | Plain hit that deals damage; Poison (0.75) |
| Air Throw | Single enemy | Bash | 0.80x | - | - | Plain hit that deals damage; Ignores defense; Chance to push the target back in the turn order (0.5) |
| One-Inch Punch | Single enemy | Bash | 0.50x | - | 0.25 | Plain hit that deals damage; Ignores defense |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 7) -> set 3
- last skill used is Cinnabar Palm (slot 3) -> set 2
- last skill used is Attack (slot 0) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Strangle (10%), Brawl Punch (10%), Cinnabar Palm (20%), Air Throw (10%), One-Inch Punch (10%), Take Break (10%), Take Break (10%)
- **Set 1:** Strangle (20%), Air Throw (40%), One-Inch Punch (40%)
- **Set 2:** Attack (25%), Take Break (75%)
- **Set 3:** Strangle (10%), Brawl Punch (90%)

### Martial Artist - Form 3 (Lv 62)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Stun (0.1) |
| Strangle | Single enemy | Neutral | 1.00x | - | 0.2 | Plain hit that deals damage; Stun (0.9) |
| Brawl Punch | Random enemies | Bash | 0.80x | - | -0.1 | Plain hit that deals damage; Hits 1-3 times |
| Cinnabar Palm | Single enemy | Stab | 0.95x | - | 0.3 | Plain hit that deals damage; Poison (0.75) |
| Air Throw | Single enemy | Bash | 0.85x | - | 0.2 | Plain hit that deals damage; Ignores defense; Chance to push the target back in the turn order (0.6) |
| One-Inch Punch | Single enemy | Bash | 0.50x | - | 0.4 | Plain hit that deals damage; Ignores defense |
| Ultimate Tornado Punch | Piercing | Wind | 0.85x | - | 0.1 | Plain hit that deals damage; Speed modifier (-0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Cinnabar Palm (slot 3) -> set 1 (stop)
- last skill used is Take Break (slot 7) -> set 1 (stop)
- last skill used is Brawl Punch (slot 2) -> set 2 (stop)
- last skill used is One-Inch Punch (slot 5) -> set 2 (stop)
- last skill used is Ultimate Tornado Punch (slot 6) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Strangle (10%), Brawl Punch (10%), Cinnabar Palm (10%), Air Throw (10%), One-Inch Punch (10%), Ultimate Tornado Punch (10%), Take Break (10%), Take Break (15%)
- **Set 1:** Attack (30%), One-Inch Punch (35%), Ultimate Tornado Punch (35%)
- **Set 2:** Attack (30%), Take Break (70%)

## Kaguya (Family 745)

- **Grand Sealbook Enchantment:** Higher lvl equipment from treasure boxes

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 60 | 7 | 2.28x | 0.72x | 1.17x | 0.72x | 0.62x | 0.82x | - |
| Form 2 | 73 | 6 | 2.68x | 0.84x | 1.28x | 0.84x | 0.75x | 0.91x | - |
| Form 3 | 85 | 5 | 3.06x | 0.91x | 1.36x | 0.91x | 0.88x | 1.02x | Double Attack |

### Kaguya - Form 1 (Lv 60)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Raging Smash | Single enemy | Weapon's | 0.90x | - | 0.35 | Plain hit that deals damage |
| Halving Slice | Enemy row | Slash | 0.65x | - | -0.1 | Plain hit that deals damage; Damage change for each later target or hit (-0.1); Instant death (0.15) |
| Harvest Moon | All allies | Neutral | 1.25x | 0.9s | - | Heal power; Physical accuracy modifier (0.15); Magic accuracy modifier (0.15) |
| Rainy Crescent | All enemies | Neutral | 1.00x | - | - | Physical accuracy modifier (-0.1) |
| Moonlight | Enemy row | Neutral | 1.25x | 1s | - | Magic power (400) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Harvest Moon (slot 3) -> set 6 (stop)
- lowest HP ratio among allies <= 60 -> set 5 (stop)
- last skill used is Halving Slice (slot 2) -> set 1 (stop)
- last skill used is Rainy Crescent (slot 4) -> set 2 (stop)
- last skill used is Moonlight (slot 5) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Raging Smash (15%), Halving Slice (10%), Rainy Crescent (15%), Moonlight (15%), Take Break (20%), Take Break (5%)
- **Set 1:** Attack (50%), Take Break (25%), Take Break (25%)
- **Set 2:** Attack (40%), Raging Smash (40%), Take Break (20%)
- **Set 3:** Attack (20%), Raging Smash (5%), Halving Slice (5%), Rainy Crescent (10%), Take Break (60%)
- **Set 4:** Attack (40%), Raging Smash (10%), Take Break (25%), Take Break (25%)
- **Set 5:** Attack (20%), Harvest Moon (60%), Take Break (10%), Take Break (10%)
  - *Condition:* Harvest Moon (slot 3) aims at: ally with the lowest HP ratio
- **Set 6:** Attack (30%), Rainy Crescent (30%), Take Break (20%), Take Break (20%)

### Kaguya - Form 2 (Lv 73)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Raging Smash | Single enemy | Weapon's | 0.95x | - | 0.5 | Plain hit that deals damage |
| Halving Slice | Enemy row | Slash | 0.65x | - | -0.1 | Plain hit that deals damage; Damage change for each later target or hit (-0.1); Instant death (0.15) |
| Harvest Moon | All allies | Neutral | 1.25x | 0.9s | - | Heal power (2); Physical accuracy modifier (0.15); Magic accuracy modifier (0.15) |
| Rainy Crescent | All enemies | Neutral | 1.00x | - | - | Physical accuracy modifier (-0.1) |
| Moonlight | Enemy row | Neutral | 1.25x | 1s | - | Magic power (650) |
| Cross Slash | Single enemy | Weapon's | 0.75x | - | 0.4 | Bonus damage to undead, demons and apparitions (0.4); Plain hit that deals damage |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 60 -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
- last skill used is Rainy Crescent (slot 4) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
- last skill used is Halving Slice (slot 2) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Raging Smash (20%), Rainy Crescent (20%), Cross Slash (20%), Take Break (20%)
- **Set 1:** Harvest Moon (50%), Moonlight (30%), Take Break (20%)
- **Set 2:** Raging Smash (20%), Halving Slice (35%), Cross Slash (25%), Take Break (20%)
- **Set 3:** Attack (20%), Raging Smash (40%), Cross Slash (40%)
- **Set 4:** Attack (20%), Take Break (80%)

### Kaguya - Form 3 (Lv 85)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Raging Smash | Single enemy | Weapon's | 0.95x | - | 0.65 | Plain hit that deals damage |
| Halving Slice | Enemy row | Slash | 0.75x | - | 0.1 | Plain hit that deals damage; Damage change for each later target or hit (-0.1); Instant death (0.2) |
| Harvest Moon | All allies | Neutral | 1.25x | 0.9s | - | Heal power (3); Physical accuracy modifier (0.15); Magic accuracy modifier (0.15) |
| Rainy Crescent | All enemies | Neutral | 1.00x | - | - | Physical accuracy modifier (-0.1) |
| Moonlight | Enemy row | Neutral | 1.25x | 1s | - | Magic power (900) |
| Moon Attack | Piercing | Earth | 0.75x | - | 0.35 | Plain hit that deals damage; DEF modifier (-0.07); Fixed critical hit rate (0.5) |
| Meteor | All enemies | Earth | 1.00x | 0.65s | - | Magic power (425) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 50 -> set 1 (stop)
- last skill used is Halving Slice (slot 2) -> set 2 (stop)
- last skill used is Rainy Crescent (slot 4) -> set 2 (stop)
- last skill used is Moonlight (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Raging Smash (20%), Halving Slice (15%), Rainy Crescent (15%), Moonlight (15%), Take Break (20%)
- **Set 1:** Halving Slice (20%), Harvest Moon (60%), Moon Attack (20%)
- **Set 2:** Attack (20%), Take Break (80%)
- **Set 3:** Moon Attack (50%), Meteor (50%)

## Azathoth (Family 751)

- **Grand Sealbook Enchantment:** Joint skill damage MegaUP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 73 | 8 | 1.82x | 0.76x | 1.18x | 1.01x | 0.72x | 0.75x | - |
| Form 2 | 83 | 7 | 2.43x | 0.83x | 1.39x | 1.24x | 0.91x | 0.87x | - |
| Form 3 | 93 | 4 | 2.81x | 0.91x | 1.51x | 1.42x | 1.01x | 0.96x | Critical Magic |

### Azathoth - Form 1 (Lv 73)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Purgatory Flame | Enemy row | Fire | 1.00x | 0.9s | - | Magic power (360); Instant death (0.1) |
| Dark Whisper | All enemies | Lightning | 0.90x | 0.8s | - | Magic power (400); Paralysis (0.2) |
| Magical Spark | Single enemy | Lightning | 0.90x | - | 0.5 | Plain hit that deals damage |
| Slow | All enemies | Earth | 1.20x | 1.1s | - | Deals no damage; Slow |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Dark Whisper (slot 2) -> set 1 (stop)
- last skill used is Purgatory Flame (slot 1) -> set 2 (stop)
- last skill used is Slow (slot 4) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Purgatory Flame (15%), Dark Whisper (10%), Magical Spark (15%), Slow (5%), Take Break (20%), Take Break (15%)
- **Set 1:** Attack (20%), Take Break (80%)
- **Set 2:** Attack (40%), Take Break (60%)
- **Set 3:** Attack (40%), Dark Whisper (40%), Take Break (20%)

### Azathoth - Form 2 (Lv 83)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Poison (0.2) |
| Purgatory Flame | Enemy row | Fire | 1.00x | 0.9s | - | Magic power (500); Instant death (0.1) |
| Dark Whisper | All enemies | Lightning | 0.90x | 0.8s | - | Magic power (400); Paralysis (0.2) |
| Magical Spark | Single enemy | Lightning | 0.95x | - | 0.75 | Plain hit that deals damage |
| Continuum Control | All enemies | Neutral | 1.00x | 1s | - | Deals no damage; Slow (0.35); Speed modifier (-0.07) |
| Cocytus | Single enemy | Water | 1.40x | 1.1s | - | Magic power (800) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 6) -> set 1 (stop)
- last skill used is Dark Whisper (slot 2) -> set 2 (stop)
- last skill used is Cocytus (slot 5) -> set 2 (stop)
- last skill used is Continuum Control (slot 4) -> set 3 (stop)
- last skill used is Take Break (slot 7) -> set 4 (stop)
- last skill used is Take Break (slot 8) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Purgatory Flame (15%), Dark Whisper (15%), Magical Spark (15%), Cocytus (15%), Take Break (20%)
- **Set 1:** Magical Spark (40%), Continuum Control (60%)
- **Set 2:** Attack (30%), Take Break (70%)
- **Set 3:** Attack (30%), Take Break (70%)
- **Set 4:** Purgatory Flame (40%), Magical Spark (60%)

### Azathoth - Form 3 (Lv 93)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | 0.15 | Plain hit that deals damage; Poison (0.6) |
| Cocytus | Single enemy | Water | 1.40x | 1.05s | - | Magic power (1500) |
| Diamond Dust | All enemies | Water | 1.15x | 0.68s | - | Magic power (1000) |
| Continuum Control | All enemies | Neutral | 1.00x | 1s | - | Deals no damage; Slow (0.35); Speed modifier (-0.07) |
| Air of Madness | All enemies | Neutral | 1.00x | 0.85s | - | Magic power (600); Stun (0.2) |
| Purgatory Flame | Enemy row | Fire | 1.00x | 0.9s | - | Magic power (800); Instant death (0.15) |
| Dark Whisper | All enemies | Lightning | 0.90x | 0.8s | - | Magic power (675); Paralysis (0.2) |
| Magical Spark | Single enemy | Lightning | 0.95x | - | 0.75 | Plain hit that deals damage |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Continuum Control (slot 3) -> set 1 (stop)
- last skill used is Cocytus (slot 1) -> set 2 (stop)
- last skill used is Magical Spark (slot 7) -> set 2 (stop)
- last skill used is Attack (slot 0) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
- last skill used is Air of Madness (slot 4) -> set 4 (stop)
- last skill used is Purgatory Flame (slot 5) -> set 4 (stop)
- last skill used is Dark Whisper (slot 6) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Cocytus (20%), Diamond Dust (20%), Continuum Control (25%), Magical Spark (20%), Take Break (15%)
- **Set 1:** Air of Madness (40%), Purgatory Flame (40%), Magical Spark (20%)
- **Set 2:** Attack (20%), Purgatory Flame (40%), Dark Whisper (40%)
- **Set 3:** Air of Madness (35%), Purgatory Flame (30%), Dark Whisper (35%)
- **Set 4:** Magical Spark (20%), Take Break (80%)

## Cupid (Family 754)

- **Grand Sealbook Enchantment:** Higher chance of shop encounters

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 15 | 10 | 1.13x | 0.82x | 0.92x | 1.01x | 1.12x | 0.92x | - |
| Form 2 | 21 | 9 | 1.85x | 0.88x | 1.02x | 1.18x | 1.21x | 1.02x | - |
| Form 3 | 29 | 7 | 2.18x | 0.96x | 1.12x | 1.32x | 1.33x | 1.12x | Warning Shot |

### Cupid - Form 1 (Lv 15)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Two Arrows | Random enemies | Stab | 0.85x | - | - | Plain hit that deals damage; Hits twice |
| Guided Shot | Single enemy | Stab | 0.85x | - | 0.15 | Plain hit that deals damage; Fixed accuracy |
| Poison Shot | Single enemy | Stab | 0.90x | - | 0.15 | Plain hit that deals damage; Poison (0.3) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (20%), Two Arrows (15%), Guided Shot (20%), Poison Shot (15%), Take Break (10%), Take Break (10%), Take Break (10%)

### Cupid - Form 2 (Lv 21)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Two Arrows | Random enemies | Stab | 0.85x | - | - | Plain hit that deals damage; Hits twice |
| Disturbance | Random enemies | Neutral | 0.80x | - | - | Magic power (45); Hits 2-4 times; Silence (0.2) |
| Poison Shot | Single enemy | Stab | 0.90x | - | 0.15 | Plain hit that deals damage; Poison (0.3) |
| Freeze Shot | Single enemy | Stab | 0.90x | - | 0.1 | Plain hit that deals damage; Freeze (0.3) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Disturbance (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Two Arrows (15%), Disturbance (15%), Poison Shot (15%), Freeze Shot (15%), Take Break (10%), Take Break (5%), Take Break (5%)
- **Set 1:** Attack (40%), Poison Shot (25%), Freeze Shot (20%), Take Break (5%), Take Break (5%), Take Break (5%)

### Cupid - Form 3 (Lv 29)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Silence (0.1) |
| Two Arrows | Random enemies | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Hits twice |
| Disturbance | Random enemies | Neutral | 0.85x | - | - | Magic power (135); Hits 2-4 times; Silence (0.2) |
| Freeze Shot | Single enemy | Stab | 0.90x | - | 0.1 | Plain hit that deals damage; Freeze (0.3) |
| Paralysis Shot | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Paralysis (0.6) |
| Tempting Voice | Piercing | Neutral | 1.50x | 0.95s | - | Magic power (80); Dispel |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Tempting Voice (slot 5) -> set 1
**Action Sets:**
- **Set 0:** Attack (15%), Two Arrows (20%), Disturbance (10%), Freeze Shot (15%), Paralysis Shot (15%), Tempting Voice (15%), Take Break (5%), Take Break (5%)
- **Set 1:** Attack (20%), Two Arrows (20%), Freeze Shot (20%), Paralysis Shot (20%), Take Break (10%), Take Break (10%)

## Eros (Family 760)

- **Grand Sealbook Enchantment:** Food likes and dislikes intensify

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 20 | 10 | 1.22x | 0.72x | 1.02x | 0.74x | 0.82x | 0.98x | - |
| Form 2 | 28 | 9 | 2.02x | 0.79x | 1.12x | 0.88x | 0.96x | 1.11x | - |
| Form 3 | 36 | 7 | 2.15x | 0.84x | 1.23x | 0.96x | 1.08x | 1.18x | Magnificent Steps |

### Eros - Form 1 (Lv 20)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Blow Kiss | Single enemy | Neutral | 0.90x | - | - | Plain hit that deals damage; Fixed damage (30); Silence (0.25) |
| Pink Typhoon | Enemy row | Wind | 0.85x | - | - | Magic power (45) |
| (Secret Technique) Bra Unhooker | Single enemy | Neutral | 0.85x | - | 0.15 | Plain hit that deals damage; DEF modifier (-0.15); Magic defense modifier (-0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Pink Typhoon (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (10%), Blow Kiss (20%), Pink Typhoon (15%), (Secret Technique) Bra Unhooker (20%), Take Break (15%), Take Break (20%)
  - *Condition:* (Secret Technique) Bra Unhooker (slot 3) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (30%), Blow Kiss (30%), Take Break (20%), Take Break (20%)

### Eros - Form 2 (Lv 28)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Blow Kiss | Single enemy | Neutral | 0.90x | - | - | Plain hit that deals damage; Fixed damage (100); Silence (0.35) |
| Pink Typhoon | Enemy row | Wind | 0.85x | - | - | Magic power (45) |
| (Secret Technique) Bra Unhooker | Single enemy | Neutral | 0.85x | - | 0.15 | Plain hit that deals damage; DEF modifier (-0.15); Magic defense modifier (-0.15) |
| Love and Thunder | Single enemy | Lightning | 0.90x | - | - | Magic power (135); Paralysis (0.4) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Pink Typhoon (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Blow Kiss (20%), Pink Typhoon (10%), (Secret Technique) Bra Unhooker (20%), Love and Thunder (10%), Take Break (10%), Take Break (10%)
  - *Condition:* (Secret Technique) Bra Unhooker (slot 3) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (40%), Blow Kiss (30%), Take Break (15%), Take Break (15%)

### Eros - Form 3 (Lv 36)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Blow Kiss | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Fixed damage (200); Silence (0.5) |
| Pink Typhoon | Enemy row | Wind | 0.85x | - | - | Magic power (185) |
| Love and Thunder | Single enemy | Lightning | 1.00x | - | - | Magic power (200); Paralysis (0.5) |
| Sexy Wink | Random enemies | Neutral | 1.00x | - | - | Magic power (150); Hits twice; Stun (0.2) |
| (Secret Technique) Bra Unhooker | Single enemy | Neutral | 0.85x | - | 0.15 | Plain hit that deals damage; DEF modifier (-0.15); Magic defense modifier (-0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Pink Typhoon (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Blow Kiss (10%), Pink Typhoon (15%), Love and Thunder (20%), Sexy Wink (15%), (Secret Technique) Bra Unhooker (10%), Take Break (10%)
  - *Condition:* (Secret Technique) Bra Unhooker (slot 5) was used 2 times or more -> Attack (slot 0)
- **Set 1:** Attack (20%), Blow Kiss (30%), Love and Thunder (10%), Sexy Wink (20%), Take Break (20%)

## Sukuna-Hikona (Family 775)

- **Grand Sealbook Enchantment:** Back line DEX + AGI 2% UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 68 | 4 | 1.48x | 0.68x | 0.93x | 0.82x | 1.08x | 0.92x | Double Attack |
| Form 2 | 78 | 3 | 2.23x | 0.74x | 1.26x | 1.11x | 1.32x | 1.09x | Double Attack |
| Form 3 | 88 | 1 | 2.65x | 0.82x | 1.47x | 1.26x | 1.45x | 1.22x | Double Attack |

### Sukuna-Hikona - Form 1 (Lv 68)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Kunitsukami Curse | Single enemy | Neutral | 0.90x | - | - | Plain hit that deals damage; Fixed damage (300); Poison (0.3) |
| Stun Needle | Single enemy | Stab | 0.95x | - | 0.4 | Plain hit that deals damage; Paralysis (0.4) |
| Munchkin Mallet | Single enemy | Bash | 0.60x | - | -0.1 | Plain hit that deals damage; ATK modifier (-0.1); DEF modifier (-0.1) |
| Petrifying Arrow | Single enemy | Stab | 0.85x | - | 0.15 | Plain hit that deals damage; Petrification (0.25) |
| Stone Shower | Enemy row | Earth | 1.20x | 0.78s | - | Magic power (400) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Stone Shower (slot 5) -> set 2 (stop)
- last skill used is Kunitsukami Curse (slot 1) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Kunitsukami Curse (15%), Stun Needle (10%), Munchkin Mallet (10%), Petrifying Arrow (10%), Stone Shower (15%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (50%), Take Break (50%)
- **Set 2:** Attack (50%), Take Break (50%)

### Sukuna-Hikona - Form 2 (Lv 78)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Kunitsukami Curse | Single enemy | Neutral | 0.90x | - | - | Plain hit that deals damage; Fixed damage (300); Poison (0.3) |
| Stun Needle | Single enemy | Stab | 0.95x | - | 0.6 | Plain hit that deals damage; Paralysis (0.4) |
| Munchkin Mallet | Single enemy | Bash | 0.60x | - | -0.1 | Plain hit that deals damage; ATK modifier (-0.1); DEF modifier (-0.1) |
| Petrifying Arrow | Single enemy | Stab | 0.85x | - | 0.3 | Plain hit that deals damage; Petrification (0.4) |
| Stone Shower | Enemy row | Earth | 1.20x | 0.76s | - | Magic power (600) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Kunitsukami Curse (slot 1) -> set 1 (stop)
- last skill used is Munchkin Mallet (slot 3) -> set 1 (stop)
- last skill used is Stone Shower (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 6) -> set 3 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (5%), Kunitsukami Curse (15%), Stun Needle (15%), Munchkin Mallet (15%), Petrifying Arrow (15%), Stone Shower (15%), Take Break (20%)
  - *Condition:* Munchkin Mallet (slot 3) was used 2 times or more -> Attack (slot 0)
- **Set 1:** Attack (60%), Take Break (40%)
- **Set 2:** Petrifying Arrow (20%), Take Break (80%)
- **Set 3:** Attack (20%), Kunitsukami Curse (20%), Stun Needle (20%), Petrifying Arrow (20%), Stone Shower (20%)

### Sukuna-Hikona - Form 3 (Lv 88)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Kunitsukami Curse | Single enemy | Neutral | 0.90x | - | - | Plain hit that deals damage; Fixed damage (500); Poison (0.5) |
| Stun Needle | Single enemy | Stab | 0.95x | - | 0.6 | Plain hit that deals damage; Paralysis (0.4) |
| Munchkin Mallet | Single enemy | Bash | 0.70x | - | 0.2 | Plain hit that deals damage; ATK modifier (-0.1); DEF modifier (-0.1) |
| Petrifying Arrow | Random enemies | Stab | 0.90x | - | 0.5 | Plain hit that deals damage; Hits twice; Petrification (0.4) |
| Gaia Crush | Single enemy | Earth | 1.40x | 1.05s | - | Magic power (1000) |
| Emaciating Hopak | All enemies | Neutral | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Kunitsukami Curse (slot 1) -> set 1 (stop)
- last skill used is Munchkin Mallet (slot 3) -> set 1 (stop)
- last skill used is Gaia Crush (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (5%), Kunitsukami Curse (15%), Stun Needle (15%), Munchkin Mallet (15%), Petrifying Arrow (15%), Gaia Crush (15%), Take Break (20%)
  - *Condition:* Munchkin Mallet (slot 3) was used 2 times or more -> Attack (slot 0)
- **Set 1:** Attack (70%), Take Break (30%)
- **Set 2:** Petrifying Arrow (30%), Take Break (70%)
- **Set 3:** Attack (20%), Stun Needle (30%), Petrifying Arrow (20%), Emaciating Hopak (30%)

## Default (Family 780)

- **Grand Sealbook Enchantment:** TP Cost for spells DOWN

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 42 | 10 | 1.23x | 0.62x | 0.81x | 0.72x | 0.71x | 0.76x | - |
| Form 2 | 55 | 7 | 1.97x | 0.73x | 0.92x | 0.84x | 0.75x | 0.82x | - |
| Form 3 | 69 | 5 | 2.31x | 0.84x | 1.11x | 0.94x | 0.84x | 0.94x | - |

### Default - Form 1 (Lv 42)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Water | 1.00x | - | - | Plain hit that deals damage |
| 2 a.m. | Single enemy | Neutral | 0.85x | - | - | Deals no damage; Petrification (0.25) |
| Wind Scroll | All enemies | Wind | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); Physical evasion modifier (-0.06); Damage cap (200) |
| I'll Curse Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Poison (0.75); Silence (0.35) |
| Ignis Fatuus | Single enemy | Fire | 0.80x | - | - | Magic power (320) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is I'll Curse Everyone (slot 3) -> set 1
- last skill used is Take Break (slot 5) -> set 2
- last skill used is 2 a.m. (slot 1) -> set 3
- last skill used is Wind Scroll (slot 2) -> set 4
**Action Sets:**
- **Set 0:** Attack (25%), 2 a.m. (10%), Wind Scroll (25%), I'll Curse Everyone (10%), Take Break (15%), Take Break (15%)
- **Set 1:** Take Break (100%)
- **Set 2:** Ignis Fatuus (100%)
- **Set 3:** Attack (40%), Wind Scroll (40%), Take Break (10%), Take Break (10%)
- **Set 4:** Attack (40%), 2 a.m. (10%), I'll Curse Everyone (20%), Take Break (15%), Take Break (15%)

### Default - Form 2 (Lv 55)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Water | 1.00x | - | - | Plain hit that deals damage |
| 2 a.m. | Single enemy | Neutral | 0.90x | - | - | Deals no damage; Petrification (0.5) |
| Wind Scroll | All enemies | Wind | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Physical evasion modifier (-0.09); Damage cap (300) |
| I'll Curse Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Poison (0.75); Silence (0.35) |
| Ignis Fatuus | Single enemy | Fire | 0.80x | - | - | Magic power (320) |
| Share Misery | Random enemies | Neutral | 0.55x | - | 0.15 | Plain hit that deals damage; Hits 0-4 times; Freeze (0.15); Silence (0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is 2 a.m. (slot 1) -> set 1
- last skill used is Wind Scroll (slot 2) -> set 2
- last skill used is I'll Curse Everyone (slot 3) -> set 3
- last skill used is Share Misery (slot 5) -> set 4
- last skill used is Take Break (slot 8) -> set 5
**Action Sets:**
- **Set 0:** Attack (20%), 2 a.m. (15%), Wind Scroll (10%), I'll Curse Everyone (10%), Ignis Fatuus (15%), Share Misery (10%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (30%), Wind Scroll (20%), Ignis Fatuus (10%), Take Break (40%)
- **Set 2:** Attack (30%), I'll Curse Everyone (10%), Ignis Fatuus (20%), Take Break (40%)
- **Set 3:** Attack (30%), 2 a.m. (15%), Wind Scroll (15%), Take Break (40%)
- **Set 4:** Attack (40%), 2 a.m. (10%), Wind Scroll (10%), Take Break (40%)
- **Set 5:** Attack (20%), Ignis Fatuus (20%), Share Misery (60%)

### Default - Form 3 (Lv 69)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Water | 1.00x | - | 0.2 | Plain hit that deals damage |
| 2 a.m. | Single enemy | Neutral | 0.95x | - | - | Deals no damage; Petrification (0.75) |
| Wind Scroll | All enemies | Wind | 1.40x | 1.65s | - | Magic power; Damage as a fraction of the target max HP (0.4); Physical evasion modifier (-0.12); Damage cap (400) |
| I'll Curse Everyone | All enemies | Neutral | 1.00x | - | - | Deals no damage; Poison (0.75); Silence (0.35) |
| Spit Fire | All enemies | Fire | 0.85x | - | - | Magic power (475) |
| Share Misery | Random enemies | Neutral | 0.55x | - | 0.15 | Plain hit that deals damage; Hits 0-4 times; Freeze (0.15); Silence (0.15) |
| Terrorize | All enemies | Fire | 1.40x | 1.2s | - | Deals no damage; Stun |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is 2 a.m. (slot 1) -> set 2 (stop)
- last skill used is I'll Curse Everyone (slot 3) -> set 3 (stop)
- last skill used is Spit Fire (slot 4) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (30%), 2 a.m. (20%), I'll Curse Everyone (30%), Take Break (20%)
- **Set 1:** Wind Scroll (40%), Terrorize (40%), Take Break (20%)
- **Set 2:** Share Misery (80%), Take Break (20%)
- **Set 3:** Spit Fire (60%), Terrorize (30%), Take Break (10%)
- **Set 4:** Take Break (100%)

## Calliope (Family 785)

- **Grand Sealbook Enchantment:** Pep decrease rate DOWN

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 42 | 10 | 1.39x | 0.68x | 1.02x | 0.71x | 0.81x | 0.91x | - |
| Form 2 | 53 | 9 | 1.89x | 0.85x | 1.11x | 0.86x | 0.88x | 1.02x | - |
| Form 3 | 64 | 7 | 2.29x | 1.01x | 1.31x | 1.08x | 1.03x | 1.18x | - |

### Calliope - Form 1 (Lv 42)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Harpstring Melody | Single enemy | Neutral | 0.85x | - | - | Magic power (225); Sleep (0.2) |
| Alluring Song | Enemy row | Neutral | 0.75x | - | - | Magic power (180); Stun |
| Concentration Prelude | All allies | Neutral | 1.50x | 1.25s | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- Concentration Prelude (slot 3) was used 1 times or more -> set 1
- last skill used is Harpstring Melody (slot 1) -> set 2
- last skill used is Alluring Song (slot 2) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Harpstring Melody (20%), Alluring Song (15%), Concentration Prelude (20%), Take Break (10%), Take Break (15%)
- **Set 1:** Attack (30%), Harpstring Melody (20%), Alluring Song (20%), Take Break (15%), Take Break (15%)
- **Set 2:** Attack (50%), Take Break (25%), Take Break (25%)
- **Set 3:** Attack (50%), Take Break (25%), Take Break (25%)

### Calliope - Form 2 (Lv 53)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Harpstring Melody | Single enemy | Neutral | 0.85x | - | - | Magic power (225); Sleep (0.2) |
| Alluring Song | Enemy row | Neutral | 0.75x | - | - | Magic power (180); Stun |
| Icy Tentacle | Single enemy | Bash | 0.90x | - | 0.25 | Plain hit that deals damage; Hits 1-3 times; Freeze (0.25) |
| Concentration Prelude | All allies | Neutral | 1.50x | 1.4s | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- Concentration Prelude (slot 4) was used 1 times or more -> set 1
- last skill used is Alluring Song (slot 2) -> set 2
- last skill used is Icy Tentacle (slot 3) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Harpstring Melody (15%), Alluring Song (10%), Icy Tentacle (10%), Concentration Prelude (20%), Take Break (15%), Take Break (10%)
- **Set 1:** Attack (40%), Harpstring Melody (10%), Alluring Song (10%), Icy Tentacle (10%), Take Break (15%), Take Break (15%)
- **Set 2:** Attack (50%), Harpstring Melody (10%), Icy Tentacle (10%), Take Break (15%), Take Break (15%)
- **Set 3:** Attack (50%), Harpstring Melody (10%), Alluring Song (10%), Take Break (15%), Take Break (15%)

### Calliope - Form 3 (Lv 64)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Harpstring Melody | Single enemy | Neutral | 0.85x | - | - | Magic power (400); Sleep (0.2) |
| Alluring Song | Enemy row | Neutral | 0.75x | - | - | Magic power (315); Stun |
| Icy Tentacle | Single enemy | Bash | 0.90x | - | 0.25 | Plain hit that deals damage; Hits 1-3 times; Freeze (0.25) |
| Concentration Prelude | All allies | Neutral | 1.50x | 1.4s | - | - |
| Healing Medicine | Single ally | Neutral | 1.00x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Healing Medicine (slot 5) -> set 4 (stop)
- lowest HP ratio among allies <= 30 -> set 3 (stop)
- last skill used is Harpstring Melody (slot 1) -> set 2 (stop)
- last skill used is Alluring Song (slot 2) -> set 2 (stop)
- last skill used is Icy Tentacle (slot 3) -> set 2 (stop)
- Concentration Prelude (slot 4) was used 1 times or more -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (25%), Harpstring Melody (10%), Alluring Song (10%), Icy Tentacle (10%), Concentration Prelude (25%), Take Break (20%)
- **Set 1:** Attack (30%), Harpstring Melody (15%), Alluring Song (15%), Icy Tentacle (15%), Take Break (25%)
- **Set 2:** Attack (40%), Take Break (60%)
- **Set 3:** Attack (10%), Harpstring Melody (10%), Alluring Song (10%), Icy Tentacle (10%), Healing Medicine (50%), Take Break (10%)
  - *Condition:* Healing Medicine (slot 5) aims at: ally with the lowest HP ratio
- **Set 4:** Attack (20%), Take Break (80%)

## Heqet (Family 789)

- **Grand Sealbook Enchantment:** The smaller your party, the higher your damage

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 18 | 11 | 1.38x | 0.92x | 0.74x | 0.85x | 0.96x | 0.77x | - |
| Form 2 | 24 | 10 | 2.11x | 1.02x | 0.83x | 0.94x | 1.12x | 0.88x | - |
| Form 3 | 30 | 9 | 2.31x | 1.12x | 0.95x | 1.05x | 1.22x | 0.98x | - |

### Heqet - Form 1 (Lv 18)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Water | 1.00x | - | - | Plain hit that deals damage |
| Water Gun | Single enemy | Water | 0.90x | - | - | Magic power (50) |
| Waterjet Cutter | Enemy row | Water | 0.85x | - | - | Magic power (80) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Waterjet Cutter (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (30%), Water Gun (20%), Waterjet Cutter (15%), Take Break (15%), Take Break (20%)
- **Set 1:** Attack (30%), Water Gun (30%), Take Break (20%), Take Break (20%)

### Heqet - Form 2 (Lv 24)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Water | 1.00x | - | 0.2 | Plain hit that deals damage |
| Breath of Ice | Single enemy | Water | 0.80x | - | - | Magic power (100); Freeze (0.1) |
| Waterjet Cutter | Enemy row | Water | 0.85x | - | - | Magic power (80) |
| Acid Rain | All enemies | Water | 0.65x | - | - | Magic power (60); DEF modifier (-0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Acid Rain (slot 3) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Breath of Ice (20%), Waterjet Cutter (20%), Acid Rain (10%), Take Break (20%), Take Break (10%)
- **Set 1:** Attack (20%), Breath of Ice (15%), Waterjet Cutter (15%), Take Break (25%), Take Break (25%)

### Heqet - Form 3 (Lv 30)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Water | 1.00x | - | 0.2 | Plain hit that deals damage |
| Icicle Thrust | Piercing | Water | 0.75x | - | - | Magic power (150); Freeze (0.2) |
| Waterjet Cutter | Enemy row | Water | 0.85x | - | - | Magic power (125) |
| Acid Rain | All enemies | Water | 0.65x | - | - | Magic power (100); DEF modifier (-0.2) |
| Sage Mode | Self | Neutral | 1.00x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- Sage Mode (slot 4) is active -> set 1
- last skill used is Waterjet Cutter (slot 2) -> set 2
**Action Sets:**
- **Set 0:** Attack (15%), Icicle Thrust (20%), Waterjet Cutter (20%), Acid Rain (20%), Sage Mode (10%), Take Break (10%), Take Break (5%)
- **Set 1:** Attack (25%), Icicle Thrust (25%), Waterjet Cutter (25%), Acid Rain (25%)
- **Set 2:** Attack (80%), Icicle Thrust (10%), Acid Rain (10%)

## Siesta (Family 795)

- **Grand Sealbook Enchantment:** Recover 3 TP every 10 steps

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 33 | 10 | 1.32x | 0.82x | 0.91x | 0.72x | 0.82x | 0.81x | - |
| Form 2 | 42 | 9 | 1.84x | 0.94x | 1.08x | 0.84x | 0.93x | 0.93x | Double Attack |
| Form 3 | 51 | 7 | 2.06x | 1.08x | 1.18x | 0.95x | 1.08x | 1.06x | Double Attack |

### Siesta - Form 1 (Lv 33)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 0.90x | - | -0.05 | Plain hit that deals damage |
| Pillow Toss | Single enemy | Bash | 0.75x | - | -0.1 | Plain hit that deals damage; Chance to push the target back in the turn order (0.3); Sleep (0.3) |
| YES/NO Choice | Single enemy | Neutral | 1.00x | - | - | Deals no damage; Fixed accuracy (0.5) |
| Wind Fang | Single enemy | Wind | 0.90x | - | - | Magic power (80) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Pillow Toss (slot 1) -> set 1
- last skill used is Wind Fang (slot 3) -> set 2
- last skill used is Take Break (slot 4) -> set 3
- last skill used is Take Break (slot 5) -> set 4
**Action Sets:**
- **Set 0:** Attack (30%), Pillow Toss (20%), Wind Fang (15%), Take Break (15%), Take Break (20%)
- **Set 1:** YES/NO Choice (100%)
- **Set 2:** Pillow Toss (50%), Take Break (50%)
- **Set 3:** Pillow Toss (50%), Wind Fang (50%)
- **Set 4:** Attack (100%)

### Siesta - Form 2 (Lv 42)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Pillow Toss | Single enemy | Bash | 0.90x | - | 0.15 | Plain hit that deals damage; Chance to push the target back in the turn order (0.6); Sleep (0.4) |
| YES/NO Choice | Single enemy | Neutral | 1.00x | - | - | Deals no damage; Fixed accuracy (0.5) |
| Carry Me! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Slow (0.75) |
| Air Turbulence | Enemy row | Wind | 1.20x | 0.78s | - | Magic power (280) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Pillow Toss (slot 1) -> set 1
- last skill used is Take Break (slot 5) -> set 2
- last skill used is Take Break (slot 6) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Pillow Toss (20%), YES/NO Choice (10%), Carry Me! (20%), Air Turbulence (10%), Take Break (10%), Take Break (10%)
- **Set 1:** YES/NO Choice (70%), Air Turbulence (30%)
- **Set 2:** Attack (20%), Carry Me! (80%)
- **Set 3:** Attack (20%), Air Turbulence (80%)

### Siesta - Form 3 (Lv 51)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Silence (0.1) |
| Pillow Toss | Single enemy | Bash | 0.90x | - | 0.3 | Plain hit that deals damage; Chance to push the target back in the turn order (0.8); Sleep (0.5) |
| YES/NO Choice | Single enemy | Neutral | 1.25x | - | - | Deals no damage; Fixed accuracy (0.5) |
| YES/YES Choice | All enemies | Neutral | 1.50x | - | - | Deals no damage; Fixed accuracy |
| Carry Me! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Slow (0.75) |
| Air Turbulence | Enemy row | Wind | 1.20x | 0.78s | - | Magic power (280) |
| Sleep | All enemies | Wind | 1.35x | 1.1s | - | Deals no damage; Sleep |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is YES/NO Choice (slot 2) -> set 1
- last skill used is Sleep (slot 6) -> set 2
- last skill used is Air Turbulence (slot 5) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Pillow Toss (10%), YES/NO Choice (10%), YES/YES Choice (10%), Carry Me! (10%), Air Turbulence (10%), Sleep (10%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (10%), YES/YES Choice (70%), Take Break (10%), Take Break (10%)
- **Set 2:** Attack (10%), YES/YES Choice (70%), Take Break (10%), Take Break (10%)
- **Set 3:** Attack (40%), Pillow Toss (40%), Take Break (10%), Take Break (10%)

## Genbu (Family 801)

- **Grand Sealbook Enchantment:** Front line ATK + DEF 4% UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 76 | 11 | 2.11x | 1.38x | 0.62x | 0.94x | 0.55x | 0.58x | - |
| Form 2 | 85 | 10 | 2.64x | 1.51x | 0.76x | 1.11x | 0.68x | 0.67x | - |
| Form 3 | 94 | 7 | 2.91x | 1.68x | 0.87x | 1.22x | 0.76x | 0.75x | - |

### Genbu - Form 1 (Lv 76)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Giant Rotation | All enemies | Bash | 0.95x | - | 0.15 | Plain hit that deals damage |
| Turtle's Curse | Single enemy | Earth | 0.80x | - | - | Magic power (450); Slow (0.35) |
| Water Scroll | All enemies | Water | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Magic defense modifier (-0.09); Damage cap (300) |
| Earth Scroll | All enemies | Earth | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); DEF modifier (-0.09); Damage cap (300) |
| Defensive Shielding | All allies | Neutral | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 6) -> set 1 (stop)
- last skill used is Defensive Shielding (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Giant Rotation (15%), Turtle's Curse (15%), Defensive Shielding (20%), Take Break (15%), Take Break (15%)
- **Set 1:** Attack (30%), Giant Rotation (20%), Turtle's Curse (20%), Defensive Shielding (30%)
- **Set 2:** Take Break (100%)
- **Set 3:** Turtle's Curse (20%), Water Scroll (40%), Earth Scroll (40%)

### Genbu - Form 2 (Lv 85)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Giant Rotation | All enemies | Bash | 0.95x | - | 0.4 | Plain hit that deals damage |
| Turtle's Curse | Single enemy | Earth | 0.80x | - | - | Magic power (800); Slow (0.35) |
| Water Scroll | All enemies | Water | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Magic defense modifier (-0.09); Damage cap (300) |
| Earth Scroll | All enemies | Earth | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); DEF modifier (-0.09); Damage cap (300) |
| Defensive Shielding | All allies | Neutral | 0.75x | - | - | - |
| Debilitating Salsa | All enemies | Neutral | 0.75x | - | - | Damage every turn as a fraction of the target max HP (0.15); Damage cap (150) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Giant Rotation (slot 1) -> set 1 (stop)
- last skill used is Turtle's Curse (slot 2) -> set 2 (stop)
- last skill used is Water Scroll (slot 3) -> set 2 (stop)
- last skill used is Earth Scroll (slot 4) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
- last skill used is Take Break (slot 9) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Giant Rotation (15%), Turtle's Curse (10%), Water Scroll (15%), Earth Scroll (15%), Defensive Shielding (15%), Debilitating Salsa (10%), Take Break (20%)
  - *Condition:* Defensive Shielding (slot 5) was used 1 times or more -> Attack (slot 0)
  - *Condition:* Debilitating Salsa (slot 6) was used 1 times or more -> Turtle's Curse (slot 2)
- **Set 1:** Attack (50%), Take Break (50%)
- **Set 2:** Attack (20%), Take Break (80%)
- **Set 3:** Attack (60%), Giant Rotation (20%), Turtle's Curse (20%)

### Genbu - Form 3 (Lv 94)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.3) |
| Giant Rotation | All enemies | Bash | 0.95x | - | 0.4 | Plain hit that deals damage |
| Turtle's Curse | Single enemy | Earth | 0.85x | - | - | Magic power (1200); Slow (0.5) |
| Water Scroll | All enemies | Water | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Magic defense modifier (-0.09); Damage cap (300) |
| Earth Scroll | All enemies | Earth | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); DEF modifier (-0.09); Damage cap (300) |
| Defensive Shielding | All allies | Neutral | 0.75x | - | - | - |
| Debilitating Salsa | All enemies | Neutral | 0.80x | - | - | Damage every turn as a fraction of the target max HP (0.25); Damage cap (300) |
| Turtle Malediction | Enemy row | Neutral | 0.90x | - | - | Deals no damage; Instant death (0.15) |
| Earth Glaive | Piercing | Earth | 0.85x | - | - | Magic power (700) |
| Earth Breath | All enemies | Earth | 0.75x | - | - | Magic power (500); Slow (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Turtle's Curse (slot 2) -> set 1 (stop)
- last skill used is Water Scroll (slot 3) -> set 2 (stop)
- last skill used is Earth Scroll (slot 4) -> set 2 (stop)
- last skill used is Take Break (slot 10) -> set 3 (stop)
- last skill used is Defensive Shielding (slot 5) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Giant Rotation (20%), Turtle's Curse (25%), Water Scroll (20%), Earth Scroll (20%), Debilitating Salsa (15%)
  - *Condition:* Debilitating Salsa (slot 6) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (30%), Turtle Malediction (30%), Take Break (40%)
- **Set 2:** Turtle Malediction (20%), Earth Glaive (40%), Earth Breath (40%)
- **Set 3:** Defensive Shielding (50%), Earth Glaive (25%), Earth Breath (25%)
- **Set 4:** Attack (50%), Turtle Malediction (50%)

## Afanc (Family 825)

- **Grand Sealbook Enchantment:** A-rank speed when no weapon is equipped

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 36 | 8 | 1.66x | 0.85x | 0.62x | 0.74x | 0.81x | 0.84x | - |
| Form 2 | 45 | 6 | 2.09x | 0.99x | 0.71x | 0.83x | 0.92x | 0.92x | - |
| Form 3 | 54 | 4 | 2.38x | 1.15x | 0.88x | 0.97x | 1.04x | 0.99x | - |

### Afanc - Form 1 (Lv 36)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Gnaw Armor | Single enemy | Stab | 0.85x | - | -0.1 | Plain hit that deals damage; DEF modifier (-0.2) |
| Poison Claw | Single enemy | Slash | 0.90x | - | 0.15 | Plain hit that deals damage; Poison (0.4) |
| Paralyzing Claw | Single enemy | Slash | 0.85x | - | - | Plain hit that deals damage; Paralysis (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (20%), Gnaw Armor (20%), Poison Claw (20%), Paralyzing Claw (20%), Take Break (10%), Take Break (10%)

### Afanc - Form 2 (Lv 45)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Gnaw Armor | Single enemy | Stab | 0.90x | - | 0.05 | Plain hit that deals damage; DEF modifier (-0.2) |
| Paralyzing Claw | Single enemy | Slash | 0.95x | - | 0.1 | Plain hit that deals damage; Paralysis (0.35) |
| Levee Breach | All enemies | Water | 1.00x | - | - | Magic power (225); Chance to push the target back in the turn order (0.5) |
| Painful Strike | Single enemy | Neutral | 0.60x | - | 0.75 | Plain hit that deals damage |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Levee Breach (slot 3) -> set 1
- last skill used is Painful Strike (slot 4) -> set 2
- last skill used is Take Break (slot 5) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Gnaw Armor (20%), Paralyzing Claw (20%), Levee Breach (10%), Painful Strike (10%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (20%), Gnaw Armor (20%), Paralyzing Claw (20%), Take Break (40%)
- **Set 2:** Attack (20%), Gnaw Armor (20%), Paralyzing Claw (20%), Take Break (40%)
- **Set 3:** Levee Breach (50%), Painful Strike (50%)

### Afanc - Form 3 (Lv 54)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Gnaw Armor | Single enemy | Stab | 0.90x | - | 0.05 | Plain hit that deals damage; DEF modifier (-0.2) |
| Poison Claw | Single enemy | Slash | 0.95x | - | 0.25 | Plain hit that deals damage; Poison (0.75) |
| Paralyzing Claw | Single enemy | Slash | 0.95x | - | 0.1 | Plain hit that deals damage; Paralysis (0.35) |
| Levee Breach | All enemies | Water | 1.00x | - | - | Magic power (225); Chance to push the target back in the turn order (0.5) |
| Painful Strike | Single enemy | Neutral | 0.60x | - | 0.75 | Plain hit that deals damage |
| Water Gatling | All enemies | Water | 0.85x | - | - | Magic power (250); Fixed accuracy (0.6); Poison (0.5) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 7) -> set 1
- last skill used is Attack (slot 0) -> set 2
- last skill used is Levee Breach (slot 4) -> set 3
- last skill used is Water Gatling (slot 6) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), Gnaw Armor (15%), Poison Claw (15%), Paralyzing Claw (15%), Painful Strike (15%), Take Break (20%)
- **Set 1:** Levee Breach (50%), Water Gatling (50%)
- **Set 2:** Poison Claw (20%), Paralyzing Claw (20%), Levee Breach (30%), Water Gatling (30%)
- **Set 3:** Gnaw Armor (10%), Poison Claw (10%), Paralyzing Claw (10%), Take Break (70%)
- **Set 4:** Gnaw Armor (10%), Poison Claw (10%), Paralyzing Claw (10%), Take Break (70%)

## Molle (Family 829)

- **Grand Sealbook Enchantment:** Escape probability UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 23 | 10 | 1.43x | 1.05x | 0.92x | 0.75x | 0.72x | 0.78x | - |
| Form 2 | 31 | 9 | 2.02x | 1.17x | 1.01x | 0.86x | 0.83x | 0.88x | - |
| Form 3 | 40 | 8 | 2.35x | 1.29x | 1.12x | 0.97x | 0.91x | 0.98x | - |

### Molle - Form 1 (Lv 23)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Paralyzing Claw | Single enemy | Slash | 0.85x | - | - | Plain hit that deals damage; Paralysis (0.2) |
| Drill Rush | Piercing | Stab | 0.80x | - | -0.15 | Plain hit that deals damage |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Drill Rush (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Paralyzing Claw (25%), Drill Rush (20%), Take Break (20%), Take Break (15%)
- **Set 1:** Attack (45%), Paralyzing Claw (15%), Take Break (20%), Take Break (20%)

### Molle - Form 2 (Lv 31)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Paralyzing Claw | Single enemy | Slash | 0.85x | - | - | Plain hit that deals damage; Paralysis (0.2) |
| Drill Rush | Piercing | Stab | 0.80x | - | -0.15 | Plain hit that deals damage |
| Boulder Toss | Single enemy | Earth | 0.80x | - | - | Magic power (200) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Drill Rush (slot 2) -> set 1
- last skill used is Boulder Toss (slot 3) -> set 2
**Action Sets:**
- **Set 0:** Attack (10%), Paralyzing Claw (20%), Drill Rush (20%), Boulder Toss (20%), Take Break (20%), Take Break (10%)
- **Set 1:** Attack (30%), Paralyzing Claw (30%), Take Break (20%), Take Break (20%)
- **Set 2:** Attack (30%), Paralyzing Claw (30%), Take Break (20%), Take Break (20%)

### Molle - Form 3 (Lv 40)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Paralyzing Claw | Single enemy | Slash | 0.95x | - | 0.1 | Plain hit that deals damage; Paralysis (0.35) |
| Drill Rush | Piercing | Stab | 0.80x | - | 0.05 | Plain hit that deals damage |
| Boulder Toss | Single enemy | Earth | 0.85x | - | - | Magic power (275) |
| Dynamite Throw | Random enemies | Earth | 0.85x | - | -0.15 | Plain hit that deals damage; Hits 0-4 times; Stun (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Dynamite Throw (slot 4) -> set 1
- last skill used is Drill Rush (slot 2) -> set 2
- last skill used is Boulder Toss (slot 3) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Paralyzing Claw (20%), Drill Rush (15%), Boulder Toss (20%), Dynamite Throw (10%), Take Break (10%), Take Break (5%)
- **Set 1:** Attack (40%), Paralyzing Claw (40%), Take Break (10%), Take Break (10%)
- **Set 2:** Attack (40%), Paralyzing Claw (40%), Take Break (10%), Take Break (10%)
- **Set 3:** Attack (50%), Paralyzing Claw (40%), Take Break (5%), Take Break (5%)

## Bigfoot (Family 833)

- **Grand Sealbook Enchantment:** Rate of status ailments dissipation UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 7 | 9 | 1.54x | 1.24x | 0.61x | 0.91x | 0.86x | 0.81x | - |
| Form 2 | 13 | 8 | 2.04x | 1.54x | 0.77x | 1.02x | 0.95x | 0.91x | - |
| Form 3 | 21 | 6 | 2.22x | 1.75x | 0.84x | 1.22x | 1.05x | 1.01x | Double Attack |

### Bigfoot - Form 1 (Lv 7)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Bigfoot Kick | Single enemy | Bash | 0.80x | - | 0.18 | Plain hit that deals damage; Chance to push the target back in the turn order (0.6) |
| Throwing Stone | Single enemy | Earth | 0.85x | - | - | Magic power (25) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (40%), Bigfoot Kick (20%), Throwing Stone (15%), Take Break (10%), Take Break (10%), Take Break (5%)

### Bigfoot - Form 2 (Lv 13)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Bigfoot Kick | Single enemy | Bash | 0.85x | - | 0.26 | Plain hit that deals damage; Chance to push the target back in the turn order (0.8) |
| Throwing Stone | Single enemy | Earth | 1.00x | - | - | Magic power (80) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (40%), Bigfoot Kick (25%), Throwing Stone (20%), Take Break (10%), Take Break (5%)

### Bigfoot - Form 3 (Lv 21)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Bigfoot Kick | Single enemy | Bash | 0.85x | - | 0.26 | Plain hit that deals damage; Chance to push the target back in the turn order (0.8) |
| Heavy Rock Press | Enemy row | Earth | 0.95x | - | - | Magic power (200); Slow (0.4) |
| Heavy Stomp | Enemy row | Bash | 0.75x | - | 0.15 | Plain hit that deals damage; ATK modifier (-0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Heavy Rock Press (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (25%), Bigfoot Kick (25%), Heavy Rock Press (15%), Heavy Stomp (20%), Take Break (10%), Take Break (5%)
- **Set 1:** Attack (20%), Bigfoot Kick (20%), Heavy Stomp (20%), Take Break (20%), Take Break (20%)

## Moby Dick (Family 840)

- **Grand Sealbook Enchantment:** Attack vs. low lvl enemies UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 44 | 10 | 1.45x | 0.72x | 0.73x | 0.81x | 1.11x | 0.73x | - |
| Form 2 | 56 | 9 | 2.32x | 0.85x | 0.83x | 0.91x | 1.23x | 0.82x | - |
| Form 3 | 68 | 7 | 2.58x | 0.94x | 0.91x | 1.02x | 1.31x | 0.93x | Covering Attack |

### Moby Dick - Form 1 (Lv 44)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 0.90x | - | -0.05 | Plain hit that deals damage |
| Silence Sting | Single enemy | Stab | 0.90x | - | 0.1 | Plain hit that deals damage; Silence (0.4) |
| Bunmawashi | Random enemies | Weapon's | 0.60x | - | -0.1 | Plain hit that deals damage; Hits 1-3 times |
| Icicle Thrust | Piercing | Water | 0.85x | - | - | Magic power (225); Freeze (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Bunmawashi (slot 2) -> set 1
- last skill used is Icicle Thrust (slot 3) -> set 2
- last skill used is Take Break (slot 4) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Silence Sting (20%), Bunmawashi (20%), Icicle Thrust (10%), Take Break (10%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (40%), Silence Sting (30%), Take Break (15%), Take Break (15%)
- **Set 2:** Attack (40%), Silence Sting (30%), Take Break (15%), Take Break (15%)
- **Set 3:** Attack (10%), Silence Sting (30%), Bunmawashi (30%), Icicle Thrust (30%)

### Moby Dick - Form 2 (Lv 56)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Silence Sting | Single enemy | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; Silence (0.8) |
| Stun Sting | Single enemy | Weapon's | 1.00x | - | 0.15 | Plain hit that deals damage; Stun (0.4) |
| Bunmawashi | Random enemies | Weapon's | 0.50x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Icicle Thrust | Piercing | Water | 0.85x | - | - | Magic power (225); Freeze (0.2) |
| Cocytus | Single enemy | Water | 1.00x | 0.75s | - | Magic power (425) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Bunmawashi (slot 3) -> set 1
- last skill used is Icicle Thrust (slot 4) -> set 2
- last skill used is Cocytus (slot 5) -> set 3
**Action Sets:**
- **Set 0:** Attack (20%), Silence Sting (15%), Stun Sting (15%), Bunmawashi (10%), Icicle Thrust (10%), Cocytus (10%), Take Break (10%), Take Break (10%)
- **Set 1:** Attack (30%), Silence Sting (20%), Stun Sting (20%), Take Break (15%), Take Break (15%)
- **Set 2:** Attack (40%), Silence Sting (10%), Stun Sting (10%), Take Break (20%), Take Break (20%)
- **Set 3:** Attack (50%), Take Break (25%), Take Break (25%)

### Moby Dick - Form 3 (Lv 68)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Silence Sting | Single enemy | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; Silence (0.8) |
| Stun Sting | Single enemy | Weapon's | 1.10x | - | 0.25 | Plain hit that deals damage; Stun (0.8) |
| Bunmawashi | Random enemies | Weapon's | 0.65x | - | 0.33 | Plain hit that deals damage; Hits 1-3 times |
| Icicle Thrust | Piercing | Water | 0.90x | - | - | Magic power (375); Freeze (0.75) |
| Cocytus | Single enemy | Water | 1.00x | 0.75s | - | Magic power (425) |
| Pororoca Heaven | All enemies | Water | 0.75x | - | - | Magic power (375); Speed modifier (-0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Silence Sting (slot 1) -> set 1 (stop)
- last skill used is Stun Sting (slot 2) -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
- last skill used is Pororoca Heaven (slot 6) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Silence Sting (20%), Stun Sting (20%), Cocytus (20%), Take Break (20%)
- **Set 1:** Bunmawashi (40%), Icicle Thrust (40%), Take Break (20%)
- **Set 2:** Bunmawashi (30%), Pororoca Heaven (60%), Take Break (10%)
- **Set 3:** Take Break (100%)

## Qitian Dasheng (Family 848)

- **Grand Sealbook Enchantment:** Critical rate UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 70 | 7 | 1.97x | 0.58x | 0.74x | 0.67x | 1.09x | 0.88x | Triple Attack |
| Form 2 | 81 | 5 | 2.83x | 0.64x | 0.83x | 0.78x | 1.21x | 1.01x | Triple Attack |
| Form 3 | 92 | 3 | 3.22x | 0.71x | 0.92x | 0.84x | 1.38x | 1.17x | Triple Attack |

### Qitian Dasheng - Form 1 (Lv 70)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Chain Club | Single enemy | Bash | 0.90x | - | 0.15 | Plain hit that deals damage; Hits twice |
| Wind Scroll | All enemies | Wind | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); Physical evasion modifier (-0.06); Damage cap (200) |
| Rampage | Random enemies | Weapon's | 0.70x | - | - | Plain hit that deals damage; Hits 0-4 times |
| Ninja Piledriver | Single enemy | Bash | 0.45x | - | 0.16 | Plain hit that deals damage; Stun (0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Wind Scroll (slot 2) -> set 1
- last skill used is Rampage (slot 3) -> set 1
- last skill used is Take Break (slot 5) -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Chain Club (15%), Wind Scroll (10%), Rampage (15%), Ninja Piledriver (15%), Take Break (10%), Take Break (15%)
- **Set 1:** Attack (50%), Take Break (50%)
- **Set 2:** Chain Club (20%), Wind Scroll (20%), Rampage (20%), Ninja Piledriver (20%), Take Break (20%)

### Qitian Dasheng - Form 2 (Lv 81)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Stun (0.1) |
| Lead Poison Club | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Hits twice; Poison (0.5) |
| Fire Scroll | All enemies | Fire | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); ATK modifier (-0.09); Damage cap (300) |
| Wind Scroll | All enemies | Wind | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Physical evasion modifier (-0.09); Damage cap (300) |
| Rampage | Random enemies | Weapon's | 0.80x | - | 0.35 | Plain hit that deals damage; Hits 0-4 times |
| Ninja Piledriver | Single enemy | Bash | 0.55x | - | 0.4 | Plain hit that deals damage; Stun (0.3) |
| Sage Mode | Self | Neutral | 1.00x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 7) -> set 2 (stop)
- last skill used is Fire Scroll (slot 2) -> set 3 (stop)
- last skill used is Wind Scroll (slot 3) -> set 3 (stop)
- last skill used is Rampage (slot 4) -> set 3 (stop)
- Sage Mode (slot 6) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Lead Poison Club (20%), Fire Scroll (10%), Wind Scroll (10%), Rampage (10%), Ninja Piledriver (10%), Sage Mode (15%), Take Break (15%)
  - *Condition:* Sage Mode (slot 6) was used 1 times or more -> Take Break (slot 9)
- **Set 1:** Attack (30%), Lead Poison Club (30%), Rampage (20%), Ninja Piledriver (20%)
- **Set 2:** Attack (20%), Fire Scroll (40%), Wind Scroll (40%)
- **Set 3:** Attack (40%), Take Break (60%)

### Qitian Dasheng - Form 3 (Lv 92)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.10x | - | - | Plain hit that deals damage; Fixed critical hit rate |
| Lead Poison Club | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Hits twice; Poison (0.5) |
| Vulcanized Club | Single enemy | Bash | 0.85x | - | -0.05 | Plain hit that deals damage; Hits twice; Petrification (0.2) |
| Fire Scroll | All enemies | Fire | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); ATK modifier (-0.09); Damage cap (300) |
| Wind Scroll | All enemies | Wind | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Physical evasion modifier (-0.09); Damage cap (300) |
| Sage Mode | Self | Neutral | 1.10x | - | - | - |
| Rampage | Random enemies | Weapon's | 1.00x | - | 0.45 | Plain hit that deals damage; Hits 2-4 times; Dispel (0.75) |
| Firey Combo | Single enemy | Fire | 0.50x | - | 0.25 | Plain hit that deals damage; Hits twice |
| Bloodbath | Single enemy | Weapon's | 0.95x | - | 0.3 | Plain hit that deals damage; Hits 2-4 times; Stun (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Fire Scroll (slot 3) -> set 1 (stop)
- last skill used is Wind Scroll (slot 4) -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
- last skill used is Take Break (slot 9) -> set 2 (stop)
- last skill used is Rampage (slot 6) -> set 4 (stop)
- last skill used is Firey Combo (slot 7) -> set 4 (stop)
- last skill used is Bloodbath (slot 8) -> set 4 (stop)
- Sage Mode (slot 5) is active -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Lead Poison Club (15%), Vulcanized Club (15%), Fire Scroll (15%), Wind Scroll (15%), Rampage (20%), Take Break (10%)
- **Set 1:** Attack (10%), Lead Poison Club (20%), Vulcanized Club (20%), Rampage (50%)
- **Set 2:** Lead Poison Club (10%), Sage Mode (50%), Firey Combo (20%), Bloodbath (20%)
- **Set 3:** Lead Poison Club (20%), Vulcanized Club (20%), Firey Combo (30%), Bloodbath (30%)
- **Set 4:** Vulcanized Club (75%), Take Break (25%)

## Last Judgment (Family 862)

- **Grand Sealbook Enchantment:** May rarely recover all HP when turn starts

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 83 | 6 | 2.24x | 0.73x | 1.02x | 1.16x | 0.81x | 0.84x | - |
| Form 2 | 91 | 5 | 2.46x | 0.84x | 1.69x | 1.32x | 0.93x | 0.96x | - |
| Form 3 | 91 | 5 | 2.46x | 0.84x | 1.69x | 1.32x | 0.93x | 0.96x | - |

### Last Judgment - Form 1 (Lv 83)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Slow (0.2) |
| Great Cry | Enemy row | Fire | 1.00x | - | - | Deals no damage; Stun (0.35) |
| Dark Judgment | Random enemies | Neutral | 0.75x | - | 0.4 | Plain hit that deals damage; Hits three times; Instant death (0.2) |
| Shudderhand | Single enemy | Bash | 0.75x | - | 0.1 | Ignores defense; Plain hit that deals damage; Speed modifier (-0.1) |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (400); Damage based on RES |
| Paralyze | All enemies | Lightning | 1.50x | 1.1s | - | Deals no damage; Paralysis |
| Summon Familiar | None | Neutral | 0.70x | - | - | Number of units summoned (2); Turns a summon lasts (3) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 7) -> set 1 (stop)
- last skill used is Great Cry (slot 1) -> set 3 (stop)
- last skill used is Paralyze (slot 5) -> set 3 (stop)
- last skill used is Dark Judgment (slot 2) -> set 4 (stop)
- last skill used is Prism Dawn (slot 4) -> set 5 (stop)
- last skill used is Take Break (slot 8) -> set 6 (stop)
- Summon Familiar (slot 6) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Great Cry (15%), Dark Judgment (15%), Shudderhand (15%), Prism Dawn (10%), Paralyze (15%), Take Break (20%)
- **Set 1:** Attack (25%), Summon Familiar (75%), Slot 10 (20%)
- **Set 2:** Attack (20%), Great Cry (15%), Dark Judgment (10%), Shudderhand (15%), Paralyze (20%), Take Break (20%)
- **Set 3:** Dark Judgment (20%), Shudderhand (20%), Prism Dawn (60%)
- **Set 4:** Attack (30%), Take Break (70%)
- **Set 5:** Attack (30%), Take Break (70%)
- **Set 6:** Attack (25%), Shudderhand (75%)

### Last Judgment - Form 2 (Lv 91)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Slow (0.2) |
| Great Cry | Enemy row | Fire | 1.00x | - | - | Deals no damage; Stun (0.35) |
| Dark Judgment | Random enemies | Neutral | 0.75x | - | 0.6 | Plain hit that deals damage; Hits three times; Instant death (0.2) |
| Shudderhand | Single enemy | Bash | 0.85x | - | 0.3 | Ignores defense; Plain hit that deals damage; Speed modifier (-0.1) |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (850); Damage based on RES |
| Paralyze | All enemies | Lightning | 1.50x | 1.1s | - | Deals no damage; Paralysis |
| Vitality Absorb | Single enemy | Neutral | 0.85x | - | - | Plain hit that deals damage; Fixed damage (500); Instant death (0.2) |
| Vortex | All enemies | Lightning | 0.70x | - | - | Magic power (700); Fixed accuracy (0.75); Physical accuracy modifier (-0.1); Stun (0.2) |
| Summon Familiar | None | Neutral | 0.70x | - | - | Number of units summoned (2); Turns a summon lasts (3) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Great Cry (slot 1) -> set 3 (stop)
- last skill used is Paralyze (slot 5) -> set 4 (stop)
- last skill used is Take Break (slot 10) -> set 4 (stop)
- Summon Familiar (slot 8) is active -> set 2 (stop)
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 9) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Great Cry (15%), Dark Judgment (15%), Shudderhand (15%), Prism Dawn (15%), Paralyze (15%), Take Break (15%)
- **Set 1:** Shudderhand (20%), Vitality Absorb (20%), Summon Familiar (60%)
- **Set 2:** Attack (20%), Great Cry (15%), Dark Judgment (15%), Shudderhand (15%), Paralyze (15%), Take Break (20%)
- **Set 3:** Dark Judgment (25%), Shudderhand (25%), Vitality Absorb (50%)
- **Set 4:** Prism Dawn (25%), Vortex (75%)

### Last Judgment - Form 3 (Lv 91)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Slow (0.2) |
| Great Cry | Enemy row | Fire | 1.00x | - | - | Deals no damage; Stun (0.35) |
| Dark Judgment | Random enemies | Neutral | 0.75x | - | 0.6 | Plain hit that deals damage; Hits three times; Instant death (0.2) |
| Shudderhand | Single enemy | Bash | 0.85x | - | 0.3 | Ignores defense; Plain hit that deals damage; Speed modifier (-0.1) |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (700); Damage based on RES |
| Paralyze | All enemies | Lightning | 1.50x | 1.1s | - | Deals no damage; Paralysis |
| Vitality Absorb | Single enemy | Neutral | 0.85x | - | - | Plain hit that deals damage; Fixed damage (500); Instant death (0.2) |
| Vortex | All enemies | Lightning | 0.70x | - | - | Magic power (700); Fixed accuracy (0.75); Physical accuracy modifier (-0.1); Stun (0.2) |
| Summon Familiar | None | Neutral | 0.70x | - | - | Number of units summoned (2); Turns a summon lasts (3) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Great Cry (slot 1) -> set 3 (stop)
- last skill used is Paralyze (slot 5) -> set 4 (stop)
- last skill used is Take Break (slot 10) -> set 4 (stop)
- Summon Familiar (slot 8) is active -> set 2 (stop)
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 9) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Great Cry (15%), Dark Judgment (15%), Shudderhand (15%), Prism Dawn (15%), Paralyze (15%), Take Break (15%)
- **Set 1:** Shudderhand (20%), Vitality Absorb (20%), Summon Familiar (60%)
- **Set 2:** Attack (20%), Great Cry (15%), Dark Judgment (15%), Shudderhand (15%), Paralyze (15%), Take Break (20%)
- **Set 3:** Dark Judgment (25%), Shudderhand (25%), Vitality Absorb (50%)
- **Set 4:** Prism Dawn (25%), Vortex (75%)

## Iron Maiden (Family 865)

- **Grand Sealbook Enchantment:** Damage to enemies with status ailments UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 55 | 11 | 1.86x | 1.21x | 0.91x | 0.91x | 0.73x | 0.65x | Double Attack |
| Form 2 | 67 | 10 | 2.29x | 1.32x | 1.01x | 1.02x | 0.83x | 0.72x | Double Attack |
| Form 3 | 80 | 7 | 2.65x | 1.51x | 1.12x | 1.18x | 0.94x | 0.82x | Double Attack |

### Iron Maiden - Form 1 (Lv 55)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Iron Crusher | Single enemy | Weapon's | 0.70x | - | 0.35 | Plain hit that deals damage; Magic accuracy modifier (-0.12) |
| Skull Crusher | Single enemy | Bash | 0.55x | - | - | Plain hit that deals damage; Hits 2-4 times; Physical evasion modifier (-0.15); Magic evasion modifier (-0.15) |
| Stone Shower | Enemy row | Earth | 1.20x | 0.78s | - | Magic power (400) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Skull Crusher (slot 2) -> set 1 (stop)
- last skill used is Take Break (slot 4) -> set 2 (stop)
- last skill used is Stone Shower (slot 3) -> set 3 (stop)
- last skill used is Take Break (slot 6) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (40%), Iron Crusher (15%), Skull Crusher (5%), Stone Shower (15%), Take Break (15%), Take Break (10%)
- **Set 1:** Attack (40%), Take Break (60%)
- **Set 2:** Iron Crusher (40%), Skull Crusher (20%), Stone Shower (40%)
- **Set 3:** Attack (60%), Take Break (40%)
- **Set 4:** Attack (20%), Iron Crusher (40%), Skull Crusher (40%)

### Iron Maiden - Form 2 (Lv 67)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Silence (0.1) |
| Iron Crusher | Single enemy | Weapon's | 0.70x | - | 0.35 | Plain hit that deals damage; Magic accuracy modifier (-0.12) |
| Skull Crusher | Single enemy | Bash | 0.55x | - | - | Plain hit that deals damage; Hits 2-4 times; Physical evasion modifier (-0.15); Magic evasion modifier (-0.15) |
| Stone Shower | Enemy row | Earth | 1.20x | 0.78s | - | Magic power (400) |
| God Stamp | Single enemy | Bash | 0.85x | - | 0.2 | Plain hit that deals damage; Number of targets (3) |
| Sentencing | Enemy row | Bash | 0.75x | - | 0.3 | Plain hit that deals damage; Instant death (0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Iron Crusher (slot 1) -> set 1 (stop)
- last skill used is Sentencing (slot 5) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Iron Crusher (20%), God Stamp (20%), Sentencing (20%), Take Break (20%)
- **Set 1:** Skull Crusher (25%), Stone Shower (25%), God Stamp (25%), Take Break (25%)
- **Set 2:** God Stamp (20%), Take Break (80%)

### Iron Maiden - Form 3 (Lv 80)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Silence (0.3) |
| Iron Crusher | Single enemy | Weapon's | 0.85x | - | 0.55 | Plain hit that deals damage; Magic accuracy modifier (-0.12) |
| Skull Crusher | Single enemy | Bash | 0.70x | - | 0.2 | Plain hit that deals damage; Hits 2-4 times; Physical evasion modifier (-0.15); Magic evasion modifier (-0.15) |
| Meteor | All enemies | Earth | 1.00x | 0.65s | - | Magic power (425) |
| God Stamp | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Number of targets (4) |
| Sentencing | Enemy row | Bash | 0.75x | - | 0.3 | Plain hit that deals damage; Instant death (0.15) |
| Berserk | Self | Neutral | 1.25x | - | - | Physical power modifier (damage = 100% + value) (0.3) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 7) -> set 2 (stop)
- last skill used is Meteor (slot 3) -> set 3 (stop)
- last skill used is Sentencing (slot 5) -> set 3 (stop)
- Berserk (slot 6) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Iron Crusher (10%), Skull Crusher (10%), Meteor (10%), God Stamp (10%), Sentencing (10%), Berserk (15%), Take Break (15%)
  - *Condition:* Berserk (slot 6) was used 2 times or more -> Attack (slot 0)
- **Set 1:** Attack (35%), Iron Crusher (15%), Skull Crusher (15%), God Stamp (20%), Sentencing (15%)
- **Set 2:** Skull Crusher (20%), Meteor (40%), Sentencing (40%)
- **Set 3:** Attack (30%), Take Break (70%)

## Sahohime (Family 873)

- **Grand Sealbook Enchantment:** HP recovers while defending

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 48 | 10 | 1.68x | 1.21x | 0.71x | 0.84x | 0.91x | 0.74x | - |
| Form 2 | 60 | 9 | 2.34x | 1.41x | 0.82x | 0.92x | 0.96x | 0.82x | - |
| Form 3 | 77 | 7 | 2.66x | 1.62x | 1.05x | 1.12x | 1.21x | 0.93x | - |

### Sahohime - Form 1 (Lv 48)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | 0.2 | Plain hit that deals damage |
| Kotatsu Bash | Single enemy | Bash | 0.85x | - | 0.15 | Plain hit that deals damage; Stun (0.2) |
| Heat Wave | Piercing | Fire | 0.80x | - | - | Magic power (260); Stun (0.15) |
| Fire Scroll | All enemies | Fire | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); ATK modifier (-0.06); Damage cap (200) |
| Nurse | Single ally | Neutral | 1.15x | 1s | - | How many ailments of the listed order it cures (8) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 5 (stop)
- last skill used is Heat Wave (slot 2) -> set 1 (stop)
- last skill used is Take Break (slot 8) -> set 2 (stop)
- last skill used is Take Break (slot 6) -> set 3 (stop)
- last skill used is Take Break (slot 7) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Kotatsu Bash (20%), Heat Wave (15%), Fire Scroll (15%), Sun Veil (10%), Take Break (10%), Take Break (10%)
  - *Condition:* Sun Veil (slot 5) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Take Break (100%)
- **Set 2:** Attack (60%), Kotatsu Bash (40%)
- **Set 3:** Attack (70%), Heat Wave (30%)
- **Set 4:** Attack (70%), Fire Scroll (30%)
- **Set 5:** Attack (50%), Nurse (50%)
  - *Condition:* Nurse (slot 4) aims at: ally with a more serious ailment

### Sahohime - Form 2 (Lv 60)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | - | Plain hit that deals damage |
| Kotatsu Bash | Single enemy | Bash | 0.90x | - | 0.3 | Plain hit that deals damage; Stun (0.2) |
| Heat Wave | Piercing | Fire | 0.95x | - | - | Magic power (325); Stun (0.25) |
| Fire Scroll | All enemies | Fire | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); ATK modifier (-0.09); Damage cap (300) |
| Nurse | Single ally | Neutral | 1.15x | 1s | - | How many ailments of the listed order it cures (8) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Slow | All enemies | Earth | 1.20x | 1.1s | - | Deals no damage; Slow |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 5 (stop)
- last skill used is Heat Wave (slot 2) -> set 1 (stop)
- last skill used is Take Break (slot 9) -> set 2 (stop)
- last skill used is Slow (slot 6) -> set 3 (stop)
- last skill used is Take Break (slot 7) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Kotatsu Bash (20%), Heat Wave (15%), Fire Scroll (15%), Sun Veil (10%), Slow (5%), Take Break (10%), Take Break (10%)
  - *Condition:* Sun Veil (slot 5) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Take Break (100%)
- **Set 2:** Attack (30%), Kotatsu Bash (30%), Slow (40%)
- **Set 3:** Attack (30%), Kotatsu Bash (25%), Fire Scroll (25%), Take Break (10%), Take Break (10%)
- **Set 4:** Attack (20%), Kotatsu Bash (15%), Fire Scroll (50%), Sun Veil (15%)
- **Set 5:** Attack (20%), Nurse (80%)
  - *Condition:* Nurse (slot 4) aims at: ally with a more serious ailment

### Sahohime - Form 3 (Lv 77)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | 0.2 | Plain hit that deals damage |
| Kotatsu Bash | Single enemy | Bash | 1.00x | - | 0.5 | Plain hit that deals damage; Stun (0.5) |
| Heat Wave | Piercing | Fire | 0.90x | - | - | Magic power (450); Stun (0.2) |
| Fire Scroll | All enemies | Fire | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); ATK modifier (-0.09); Damage cap (300) |
| Circle Nurse | All allies | Neutral | 1.00x | 0.85s | - | How many ailments of the listed order it cures (8) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Slow | All enemies | Earth | 1.20x | 1.1s | - | Deals no damage; Slow |
| My Kotatsu Is Without Enemies | Ally row | Neutral | 0.20x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 1 (stop)
- last skill used is Heat Wave (slot 2) -> set 2 (stop)
- last skill used is Fire Scroll (slot 3) -> set 2 (stop)
- last skill used is Slow (slot 6) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
- last skill used is My Kotatsu Is Without Enemies (slot 7) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Kotatsu Bash (20%), Heat Wave (15%), Fire Scroll (15%), Sun Veil (15%), Slow (10%), Take Break (15%)
  - *Condition:* Sun Veil (slot 5) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (15%), Kotatsu Bash (5%), Fire Scroll (5%), Circle Nurse (70%), Slow (5%)
  - *Condition:* Circle Nurse (slot 4) aims at: ally with the heaviest ailment
- **Set 2:** Attack (30%), Take Break (70%)
- **Set 3:** Attack (20%), My Kotatsu Is Without Enemies (80%)
- **Set 4:** Take Break (100%)

## Nuwa (Family 887)

- **Grand Sealbook Enchantment:** TP Cost for techniques DOWN

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 79 | 7 | 2.26x | 0.92x | 0.84x | 1.02x | 0.92x | 0.85x | Double Attack |
| Form 2 | 87 | 6 | 2.93x | 1.08x | 0.98x | 1.15x | 1.08x | 0.97x | Double Attack |
| Form 3 | 95 | 5 | 3.14x | 1.17x | 1.09x | 1.24x | 1.17x | 1.08x | Double Attack |

### Nuwa - Form 1 (Lv 79)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Snake Eyes | Random enemies | Neutral | 0.95x | - | - | Deals no damage; Hits 0-4 times; Paralysis (0.2) |
| Bladestorm | Single enemy | Slash | 0.60x | - | 0.1 | Plain hit that deals damage; Hits 1-5 times |
| Strangle | Single enemy | Neutral | 0.60x | - | 0.1 | Plain hit that deals damage; Stun (0.25) |
| Mince | Single enemy | Slash | 0.85x | - | 0.35 | Plain hit that deals damage; ATK modifier (-0.15); DEF modifier (-0.15) |
| Shadow Sew | Single enemy | Neutral | 1.35x | 1.15s | - | Deals no damage; Shadow Sew chance |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Snake Eyes (slot 1) -> set 1 (stop)
- last skill used is Shadow Sew (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Snake Eyes (15%), Bladestorm (10%), Strangle (15%), Mince (10%), Shadow Sew (10%), Take Break (25%)
  - *Condition:* Mince (slot 4) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (40%), Bladestorm (30%), Take Break (30%)
- **Set 2:** Attack (30%), Snake Eyes (20%), Take Break (50%)
- **Set 3:** Bladestorm (50%), Strangle (50%)

### Nuwa - Form 2 (Lv 87)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Snake Stare | Random enemies | Neutral | 1.00x | - | - | Deals no damage; Hits 2-4 times; Paralysis (0.3); Slow (0.3) |
| Bladestorm | Single enemy | Slash | 0.70x | - | 0.3 | Plain hit that deals damage |
| Strangle | Single enemy | Neutral | 0.60x | - | 0.1 | Plain hit that deals damage; Stun (0.25) |
| Mince | Single enemy | Slash | 0.85x | - | 0.35 | Plain hit that deals damage; ATK modifier (-0.15); DEF modifier (-0.15) |
| Shadow Sew RX | Enemy row | Neutral | 1.20x | 0.95s | - | Deals no damage; Shadow Sew chance |
| Skewer | Single enemy | Stab | 0.95x | - | 0.4 | Plain hit that deals damage; Instant death (0.4) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Snake Stare (slot 1) -> set 1 (stop)
- last skill used is Shadow Sew RX (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
- last skill used is Skewer (slot 6) -> set 4 (stop)
- last skill used is Take Break (slot 8) -> set 5 (stop)
**Action Sets:**
- **Set 0:** Snake Stare (15%), Bladestorm (15%), Strangle (15%), Mince (15%), Shadow Sew RX (15%), Take Break (25%)
  - *Condition:* Mince (slot 4) was used 2 times or more -> Attack (slot 0)
- **Set 1:** Attack (40%), Bladestorm (30%), Skewer (30%)
- **Set 2:** Attack (30%), Strangle (70%)
- **Set 3:** Bladestorm (50%), Skewer (50%)
- **Set 4:** Attack (30%), Take Break (70%)
- **Set 5:** Attack (30%), Bladestorm (30%), Strangle (40%)

### Nuwa - Form 3 (Lv 95)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.10x | - | 0.2 | Plain hit that deals damage; Poison (0.75) |
| Snake Glower | Random enemies | Neutral | 0.80x | - | - | Deals no damage; Hits 2-4 times; Fixed damage (300); Paralysis (0.3); Slow (0.3) |
| Bladestorm | Single enemy | Slash | 0.80x | - | 0.45 | Plain hit that deals damage |
| Strangle | Single enemy | Neutral | 1.00x | - | 0.2 | Plain hit that deals damage; Stun (0.9) |
| Mince | Single enemy | Slash | 0.85x | - | 0.35 | Plain hit that deals damage; ATK modifier (-0.15); DEF modifier (-0.15) |
| Shadow Sew RX | Enemy row | Neutral | 1.35x | 1s | - | Deals no damage; Shadow Sew chance |
| Skewer | Single enemy | Stab | 0.95x | - | 0.65 | Plain hit that deals damage; Instant death (0.4) |
| Onikagura | All enemies | Slash | 0.90x | - | 0.35 | Plain hit that deals damage |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Mince (slot 4) -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 2 (stop)
- last skill used is Shadow Sew RX (slot 5) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Bladestorm (20%), Strangle (15%), Mince (15%), Shadow Sew RX (15%), Onikagura (20%), Take Break (15%)
  - *Condition:* Mince (slot 4) was used 2 times or more -> Attack (slot 0)
- **Set 1:** Take Break (100%)
- **Set 2:** Snake Glower (50%), Bladestorm (50%)
- **Set 3:** Skewer (75%), Onikagura (25%)

## Kuchinawa (Family 890)

- **Grand Sealbook Enchantment:** Increase Mercenary Buddy stats by 30

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 75 | 11 | 2.49x | 1.12x | 0.74x | 0.82x | 0.78x | 0.69x | Covering Attack |
| Form 2 | 86 | 10 | 3.01x | 1.23x | 0.86x | 0.89x | 0.86x | 0.75x | Covering Attack |
| Form 3 | 96 | 7 | 3.28x | 1.31x | 1.12x | 0.96x | 0.96x | 0.82x | Covering Attack |

### Kuchinawa - Form 1 (Lv 75)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Dragon Claw | Single enemy | Slash | 0.90x | - | -0.05 | Plain hit that deals damage; Hits twice |
| Masticate | Single enemy | Neutral | 0.95x | - | 0.2 | Plain hit that deals damage; Ignores defense |
| Cursevenom | Single enemy | Earth | 0.90x | - | - | Magic power (400); Silence (0.25); Freeze (0.25); Poison (0.25) |
| Petrify Tail | Single enemy | Stab | 1.00x | - | 0.4 | Plain hit that deals damage; Petrification (0.25) |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 7) -> set 2
- last skill used is Cursevenom (slot 3) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Dragon Claw (15%), Masticate (15%), Cursevenom (15%), Petrify Tail (15%), Take Break (20%)
- **Set 1:** Attack (40%), Wait and See (30%), Take Break (30%)
- **Set 2:** Dragon Claw (35%), Masticate (35%), Cursevenom (30%)

### Kuchinawa - Form 2 (Lv 86)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Dragon Claw | Random enemies | Slash | 0.90x | - | 0.25 | Plain hit that deals damage; Hits three times; ATK modifier (-0.05) |
| Masticate | Single enemy | Neutral | 0.95x | - | 0.2 | Plain hit that deals damage; Ignores defense |
| Cursevenom | Single enemy | Earth | 0.90x | - | - | Magic power (400); Silence (0.25); Freeze (0.25); Poison (0.25) |
| Petrify Tail | Single enemy | Stab | 1.00x | - | 0.4 | Plain hit that deals damage; Petrification (0.25) |
| Gulp | Piercing | Bash | 0.60x | - | 0.15 | Plain hit that deals damage; Ignores defense; Instant death (0.25) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 6) -> set 1 (stop)
- last skill used is Masticate (slot 2) -> set 2 (stop)
- last skill used is Cursevenom (slot 3) -> set 2 (stop)
- last skill used is Gulp (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 7) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Dragon Claw (20%), Masticate (15%), Cursevenom (15%), Petrify Tail (15%), Take Break (15%)
- **Set 1:** Cursevenom (40%), Gulp (60%)
- **Set 2:** Attack (30%), Take Break (70%)
- **Set 3:** Attack (25%), Dragon Claw (25%), Petrify Tail (50%)

### Kuchinawa - Form 3 (Lv 96)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Stun (0.25) |
| Dragon Claw | Random enemies | Slash | 0.90x | - | 0.25 | Plain hit that deals damage; Hits three times; ATK modifier (-0.05) |
| Masticate | Single enemy | Neutral | 0.95x | - | 0.35 | Plain hit that deals damage; Ignores defense |
| Cursevenom | Single enemy | Earth | 0.90x | - | - | Magic power (900); Silence (0.25); Freeze (0.25); Poison (0.25) |
| Petrify Breath | Enemy row | Earth | 0.75x | - | - | Magic power (700); Petrification (0.2) |
| Gulp | Piercing | Bash | 0.75x | - | 0.2 | Plain hit that deals damage; Ignores defense; Instant death (0.25) |
| Earth's Anger | Enemy row | Earth | 0.70x | - | - | Magic power (700); DEF modifier (-0.1); Magic defense modifier (-0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 7) -> set 1 (stop)
- last skill used is Masticate (slot 2) -> set 2 (stop)
- last skill used is Cursevenom (slot 3) -> set 2 (stop)
- last skill used is Gulp (slot 5) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Dragon Claw (20%), Masticate (20%), Cursevenom (20%), Petrify Breath (15%), Take Break (15%)
- **Set 1:** Cursevenom (25%), Gulp (75%)
- **Set 2:** Attack (25%), Take Break (75%)
- **Set 3:** Dragon Claw (20%), Petrify Breath (20%), Earth's Anger (60%)

## Dragon Papi (Family 896)

- **Grand Sealbook Enchantment:** Gain more EXP from higher-level enemies

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 42 | 11 | 1.48x | 0.91x | 0.58x | 0.67x | 0.68x | 0.66x | - |
| Form 2 | 52 | 10 | 2.11x | 1.08x | 0.65x | 0.75x | 0.74x | 0.75x | - |
| Form 3 | 63 | 8 | 2.32x | 1.17x | 0.81x | 0.89x | 0.91x | 0.96x | Double Puppet |

### Dragon Papi - Form 1 (Lv 42)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Dragon Claw | Single enemy | Slash | 0.80x | - | -0.15 | Plain hit that deals damage; Hits twice |
| Mini Breath | Enemy row | Neutral | 0.70x | - | - | Magic power (180) |
| Continuous Bash | Single enemy | Bash | 0.75x | - | -0.1 | Plain hit that deals damage; Number of targets (3); Chance to push the target back in the turn order (0.25) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Mini Breath (slot 2) -> set 1
- last skill used is Continuous Bash (slot 3) -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Dragon Claw (20%), Mini Breath (10%), Continuous Bash (15%), Take Break (20%), Take Break (15%)
- **Set 1:** Attack (40%), Dragon Claw (10%), Take Break (25%), Take Break (25%)
- **Set 2:** Attack (30%), Dragon Claw (30%), Take Break (20%), Take Break (20%)

### Dragon Papi - Form 2 (Lv 52)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Dragon Claw | Single enemy | Slash | 0.95x | - | - | Plain hit that deals damage; Hits twice; ATK modifier (-0.13) |
| Mini Breath | Enemy row | Neutral | 0.70x | - | - | Magic power (215) |
| Poison Breath | Enemy row | Water | 0.70x | - | - | Magic power (190); Poison (0.3) |
| Spartan | None | Neutral | 0.90x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Continuous Bash | Single enemy | Bash | 0.75x | - | -0.1 | Plain hit that deals damage; Number of targets (3); Chance to push the target back in the turn order (0.25) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Dragon Claw (slot 1) -> set 1
- last skill used is Mini Breath (slot 2) -> set 2
- last skill used is Poison Breath (slot 3) -> set 3
- Spartan (slot 4) is active -> set 4
**Action Sets:**
- **Set 0:** Attack (15%), Dragon Claw (10%), Mini Breath (10%), Poison Breath (10%), Spartan (15%), Continuous Bash (10%), Take Break (20%), Take Break (10%)
- **Set 1:** Attack (60%), Continuous Bash (10%), Take Break (15%), Take Break (15%)
- **Set 2:** Attack (60%), Continuous Bash (10%), Take Break (15%), Take Break (15%)
- **Set 3:** Attack (60%), Continuous Bash (10%), Take Break (15%), Take Break (15%)
- **Set 4:** Attack (20%), Dragon Claw (10%), Continuous Bash (20%), Take Break (25%), Take Break (25%)

### Dragon Papi - Form 3 (Lv 63)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Dragon Claw | Single enemy | Slash | 0.95x | - | - | Plain hit that deals damage; Hits twice; ATK modifier (-0.13) |
| Poison Breath | Enemy row | Water | 0.70x | - | - | Magic power (350); Poison (0.5) |
| Spartan | None | Neutral | 0.90x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Catalina | None | Neutral | 0.75x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Continuous Bash | Single enemy | Bash | 0.85x | - | 0.15 | Plain hit that deals damage; Number of targets (3); Chance to push the target back in the turn order (0.5) |
| Move, Big Brother! | Single enemy | Bash | 0.50x | - | 0.25 | Plain hit that deals damage; Instant death |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Poison Breath (slot 2) -> set 4 (stop)
- last skill used is Move, Big Brother! (slot 6) -> set 4 (stop)
- Spartan (slot 3) is active and Catalina (slot 4) is active -> set 3
- Spartan (slot 3) is active -> set 1 (stop)
- Catalina (slot 4) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Dragon Claw (10%), Poison Breath (10%), Spartan (25%), Catalina (25%), Move, Big Brother! (10%), Take Break (10%)
- **Set 1:** Attack (10%), Dragon Claw (10%), Poison Breath (10%), Catalina (25%), Continuous Bash (25%), Move, Big Brother! (5%), Take Break (15%)
- **Set 2:** Attack (10%), Dragon Claw (10%), Poison Breath (10%), Spartan (25%), Continuous Bash (25%), Move, Big Brother! (5%), Take Break (15%)
- **Set 3:** Attack (40%), Dragon Claw (20%), Take Break (40%)
- **Set 4:** Take Break (100%)

## Death Cataphract (Family 908)

- **Grand Sealbook Enchantment:** Class weapon modifier 2% UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 46 | 11 | 1.52x | 1.35x | 0.64x | 0.71x | 0.74x | 0.62x | - |
| Form 2 | 59 | 10 | 2.16x | 1.43x | 0.77x | 0.85x | 0.88x | 0.74x | - |
| Form 3 | 72 | 8 | 2.51x | 1.55x | 0.84x | 0.92x | 1.02x | 0.85x | - |

### Death Cataphract - Form 1 (Lv 46)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Circle Protect | All allies | Neutral | 1.25x | 0.8s | - | DEF modifier (0.12) |
| Clean Sweep | Enemy row | Weapon's | 0.80x | - | -0.1 | Plain hit that deals damage |
| Buster Cannon | Piercing | Stab | 0.90x | - | 0.05 | Plain hit that deals damage |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Circle Protect (slot 1) -> set 1
- last skill used is Take Break (slot 4) -> set 2
- last skill used is Clean Sweep (slot 2) -> set 3
- last skill used is Buster Cannon (slot 3) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), Circle Protect (15%), Clean Sweep (20%), Buster Cannon (20%), Take Break (10%), Take Break (15%)
- **Set 1:** Take Break (100%)
- **Set 2:** Attack (50%), Take Break (25%), Take Break (25%)
- **Set 3:** Attack (50%), Take Break (25%), Take Break (25%)
- **Set 4:** Attack (50%), Take Break (25%), Take Break (25%)

### Death Cataphract - Form 2 (Lv 59)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Stun (0.1) |
| Circle Protect | All allies | Neutral | 1.25x | 0.8s | - | DEF modifier (0.12) |
| Clean Sweep | Enemy row | Weapon's | 1.00x | - | - | Plain hit that deals damage |
| Buster Cannon | Piercing | Stab | 0.90x | - | 0.2 | Plain hit that deals damage |
| Death | Single enemy | Earth | 1.25x | 1.1s | - | Deals no damage; Instant death |
| Overrun | Single enemy | Bash | 0.65x | - | -0.15 | Plain hit that deals damage; Hits 2-4 times; Fixed critical hit rate |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Circle Protect (slot 1) -> set 1
- last skill used is Take Break (slot 8) -> set 2
- last skill used is Overrun (slot 5) -> set 3
- last skill used is Buster Cannon (slot 3) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), Circle Protect (15%), Clean Sweep (20%), Buster Cannon (10%), Death (10%), Take Break (15%), Take Break (10%)
- **Set 1:** Attack (20%), Clean Sweep (10%), Buster Cannon (10%), Death (10%), Take Break (50%)
- **Set 2:** Clean Sweep (10%), Buster Cannon (10%), Overrun (80%)
- **Set 3:** Attack (15%), Death (15%), Take Break (35%), Take Break (35%)
- **Set 4:** Attack (30%), Clean Sweep (20%), Death (20%), Take Break (15%), Take Break (15%)

### Death Cataphract - Form 3 (Lv 72)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Stun (0.1) |
| Circle Protect | All allies | Neutral | 1.25x | 0.8s | - | DEF modifier (0.12) |
| Clean Sweep | Enemy row | Weapon's | 0.80x | - | 0.15 | Plain hit that deals damage |
| Buster Cannon | Piercing | Stab | 0.90x | - | 0.2 | Plain hit that deals damage |
| Soul Harvest | Random enemies | Earth | 0.70x | - | - | Magic power (375); Hits 1-3 times; Instant death (0.15) |
| Overrun | Single enemy | Bash | 1.00x | - | 0.2 | Plain hit that deals damage; Hits 2-4 times; Fixed critical hit rate |
| Painful Strike | Single enemy | Neutral | 0.60x | - | 0.75 | Plain hit that deals damage |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 7) -> set 2 (stop)
- last skill used is Soul Harvest (slot 4) -> set 3 (stop)
- last skill used is Overrun (slot 5) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Circle Protect (20%), Clean Sweep (20%), Painful Strike (20%), Take Break (25%)
  - *Condition:* Circle Protect (slot 1) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Clean Sweep (20%), Buster Cannon (35%), Soul Harvest (35%), Take Break (10%)
- **Set 2:** Soul Harvest (30%), Overrun (70%)
- **Set 3:** Take Break (100%)

## Ghast (Family 913)

- **Grand Sealbook Enchantment:** When max HP, damage inflicted 10% UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 12 | 11 | 2.01x | 1.12x | 0.51x | 0.81x | 0.72x | 0.72x | - |
| Form 2 | 18 | 10 | 2.28x | 1.25x | 0.62x | 0.88x | 0.84x | 0.82x | Covering Attack |
| Form 3 | 26 | 8 | 2.43x | 1.32x | 0.74x | 0.94x | 0.92x | 0.92x | Covering Attack |

### Ghast - Form 1 (Lv 12)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Solvent | Single enemy | Water | 0.85x | - | - | Magic power (50); DEF modifier (-0.2) |
| Slow | All enemies | Earth | 1.10x | 1s | - | Deals no damage; Slow |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Slow (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (30%), Solvent (20%), Slow (25%), Take Break (15%), Take Break (10%)
- **Set 1:** Attack (40%), Solvent (40%), Take Break (10%), Take Break (10%)

### Ghast - Form 2 (Lv 18)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Solvent | Single enemy | Water | 0.90x | - | - | Magic power (80); DEF modifier (-0.2) |
| Slow | All enemies | Earth | 1.10x | 1s | - | Deals no damage; Slow |
| Poison Hammer | Single enemy | Bash | 0.85x | - | 0.15 | Plain hit that deals damage; Poison (0.4) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Slow (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Solvent (20%), Slow (25%), Poison Hammer (20%), Take Break (10%), Take Break (5%)
- **Set 1:** Attack (20%), Solvent (30%), Poison Hammer (50%)

### Ghast - Form 3 (Lv 26)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Solvent | Single enemy | Water | 0.90x | - | - | Magic power (225); DEF modifier (-0.2) |
| Slow | All enemies | Earth | 1.20x | 1.1s | - | Deals no damage; Slow |
| Poison Hammer | Single enemy | Bash | 0.90x | - | 0.2 | Plain hit that deals damage; Poison (0.6) |
| Stab Smash | Single enemy | Bash | 0.80x | - | 0.1 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Slow (slot 2) -> set 1
**Action Sets:**
- **Set 0:** Attack (15%), Solvent (15%), Slow (20%), Poison Hammer (15%), Stab Smash (15%), Take Break (10%), Take Break (10%)
- **Set 1:** Solvent (20%), Poison Hammer (40%), Stab Smash (40%)

## Hell's Angel (Family 921)

- **Grand Sealbook Enchantment:** Unique skill level +1

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 92 | 4 | 2.43x | 1.01x | 1.04x | 0.86x | 1.16x | 0.98x | - |
| Form 2 | 98 | 2 | 3.19x | 1.12x | 1.16x | 0.94x | 1.27x | 1.09x | - |
| Form 3 | 98 | 2 | 3.19x | 1.12x | 1.16x | 0.94x | 1.27x | 1.09x | - |

### Hell's Angel - Form 1 (Lv 92)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Slow (0.25) |
| Ether Strike | Piercing | Stab | 0.95x | - | 0.5 | Plain hit that deals damage |
| Screw Blast | Piercing | Wind | 0.90x | - | - | Magic power (1100); Speed modifier (-0.1); Silence (0.25) |
| Drill Lance Attack | Piercing | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.2) |
| Hell Runneth Over | Piercing | Bash | 0.90x | - | 0.65 | Plain hit that deals damage; Speed modifier (-0.12) |
| Full Throttle | Self | Neutral | 1.00x | 1.3s | - | ATK modifier (0.25); Speed modifier (0.25) |
| Aura Eliminate | Single enemy | Weapon's | 1.00x | - | 0.65 | Plain hit that deals damage; Dispel (0.8) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Take Break (slot 7) -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
- Full Throttle (slot 5) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Ether Strike (10%), Screw Blast (10%), Drill Lance Attack (10%), Hell Runneth Over (10%), Full Throttle (20%), Aura Eliminate (10%), Take Break (15%), Take Break (15%)
- **Set 1:** Attack (15%), Ether Strike (25%), Screw Blast (25%), Aura Eliminate (20%), Take Break (15%)
- **Set 2:** Drill Lance Attack (30%), Hell Runneth Over (30%), Full Throttle (40%)
- **Set 3:** Ether Strike (50%), Aura Eliminate (50%)

### Hell's Angel - Form 2 (Lv 98)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Slow (0.25) |
| Ether Strike | Piercing | Stab | 0.95x | - | 0.5 | Plain hit that deals damage |
| Screw Blast | Piercing | Wind | 0.90x | - | - | Magic power (1100); Speed modifier (-0.1); Silence (0.25) |
| Drill Lance Attack | Piercing | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.2) |
| Hell Runneth Over | Piercing | Bash | 0.90x | - | 0.65 | Plain hit that deals damage; Speed modifier (-0.12) |
| Full Throttle | Self | Neutral | 1.00x | 1.3s | - | ATK modifier (0.25); Speed modifier (0.25) |
| Aura Eliminate | Single enemy | Weapon's | 1.00x | - | 0.65 | Plain hit that deals damage; Dispel (0.8) |
| Let's Charge! | Piercing | Stab | 1.05x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Buchikamashi | All enemies | Bash | 0.80x | - | 0.4 | Plain hit that deals damage; Stun (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Screw Blast (slot 2) -> set 1 (stop)
- last skill used is Drill Lance Attack (slot 3) -> set 1 (stop)
- last skill used is Hell Runneth Over (slot 4) -> set 1 (stop)
- last skill used is Let's Charge! (slot 7) -> set 1 (stop)
- last skill used is Take Break (slot 9) -> set 3 (stop)
- last skill used is Take Break (slot 10) -> set 3 (stop)
- Full Throttle (slot 5) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Ether Strike (10%), Screw Blast (10%), Drill Lance Attack (10%), Hell Runneth Over (10%), Full Throttle (20%), Aura Eliminate (10%), Let's Charge! (15%), Take Break (15%)
- **Set 1:** Aura Eliminate (75%), Take Break (25%)
- **Set 2:** Attack (10%), Ether Strike (20%), Drill Lance Attack (20%), Aura Eliminate (20%), Let's Charge! (10%), Take Break (20%)
- **Set 3:** Attack (25%), Buchikamashi (75%)

### Hell's Angel - Form 3 (Lv 98)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Slow (0.25) |
| Ether Strike | Piercing | Stab | 0.95x | - | 0.5 | Plain hit that deals damage |
| Screw Blast | Piercing | Wind | 0.90x | - | - | Magic power (1100); Speed modifier (-0.1); Silence (0.25) |
| Drill Lance Attack | Piercing | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.2) |
| Hell Runneth Over | Piercing | Bash | 0.90x | - | 0.65 | Plain hit that deals damage; Speed modifier (-0.12) |
| Full Throttle | Self | Neutral | 1.00x | 1.3s | - | ATK modifier (0.25); Speed modifier (0.25) |
| Aura Eliminate | Single enemy | Weapon's | 1.00x | - | 0.65 | Plain hit that deals damage; Dispel (0.8) |
| Let's Charge! | Piercing | Stab | 1.05x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Buchikamashi | All enemies | Bash | 0.80x | - | 0.4 | Plain hit that deals damage; Stun (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Screw Blast (slot 2) -> set 1 (stop)
- last skill used is Drill Lance Attack (slot 3) -> set 1 (stop)
- last skill used is Hell Runneth Over (slot 4) -> set 1 (stop)
- last skill used is Let's Charge! (slot 7) -> set 1 (stop)
- last skill used is Take Break (slot 9) -> set 3 (stop)
- last skill used is Take Break (slot 10) -> set 3 (stop)
- Full Throttle (slot 5) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Ether Strike (10%), Screw Blast (10%), Drill Lance Attack (10%), Hell Runneth Over (10%), Full Throttle (20%), Aura Eliminate (10%), Let's Charge! (15%), Take Break (15%)
- **Set 1:** Aura Eliminate (75%), Take Break (25%)
- **Set 2:** Attack (10%), Ether Strike (20%), Drill Lance Attack (20%), Aura Eliminate (20%), Let's Charge! (10%), Take Break (20%)
- **Set 3:** Attack (25%), Buchikamashi (75%)

## Samael (Family 951)

- **Grand Sealbook Enchantment:** Back line INT 8% UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 88 | 5 | 2.51x | 1.15x | 1.21x | 1.18x | 1.17x | 1.04x | Critical Magic |
| Form 2 | 94 | 4 | 3.22x | 1.24x | 1.37x | 1.24x | 1.29x | 1.12x | Critical Magic |
| Form 3 | 99 | 3 | 3.42x | 1.36x | 1.45x | 1.33x | 1.37x | 1.19x | Critical Magic |

### Samael - Form 1 (Lv 88)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.15x | - | 0.25 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.25) |
| Mini Circle Heal | Ally row | Neutral | 1.00x | 0.5s | - | Heal power |
| Inferno | All enemies | Fire | 1.00x | 0.7s | - | Magic power (1250) |
| Forbidden Fruit | Single enemy | Neutral | 0.80x | - | - | Plain hit that deals damage; Fixed damage (666); Shadow Sew chance |
| Godpoison | All enemies | Water | 0.70x | - | - | Magic power (1400); Paralysis (0.3); Poison |
| Overrun | Single enemy | Bash | 1.00x | - | 0.2 | Plain hit that deals damage; Hits 2-4 times; Fixed critical hit rate |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Mini Circle Heal (slot 1) -> set 1 (stop)
- last skill used is Inferno (slot 2) -> set 1 (stop)
- last skill used is Forbidden Fruit (slot 3) -> set 1 (stop)
- last skill used is Godpoison (slot 4) -> set 1 (stop)
- last skill used is Overrun (slot 5) -> set 1 (stop)
- lowest HP ratio among allies <= 40 -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Inferno (20%), Forbidden Fruit (20%), Godpoison (20%), Overrun (20%)
- **Set 1:** Attack (40%), Take Break (60%)
- **Set 2:** Attack (25%), Mini Circle Heal (50%), Forbidden Fruit (25%)
  - *Condition:* Mini Circle Heal (slot 1) aims at: ally with the lowest HP ratio

### Samael - Form 2 (Lv 94)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.15x | - | 0.25 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.25) |
| Mini Circle Heal | Ally row | Neutral | 1.00x | 0.5s | - | Heal power (2) |
| Inferno | All enemies | Fire | 1.00x | 0.7s | - | Magic power (1250) |
| Forbidden Fruit | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Fixed damage (666); Shadow Sew chance |
| Godpoison | All enemies | Water | 0.70x | - | - | Magic power (1400); Paralysis (0.3); Poison |
| Overrun | Single enemy | Bash | 1.00x | - | 0.2 | Plain hit that deals damage; Hits 2-4 times; Fixed critical hit rate |
| Chaos Eye | Piercing | Neutral | 0.90x | - | - | Magic power (850); Freeze (0.35); Silence (0.35) |
| Heat Erosion | Piercing | Fire | 1.00x | - | - | Magic power (1000) |
| Wing Flap | Random enemies | Wind | 0.90x | - | 0.15 | Plain hit that deals damage; Hits 2-4 times; Sleep (0.25) |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 40 -> set 3 (stop)
- last skill used is Inferno (slot 2) -> set 1 (stop)
- last skill used is Forbidden Fruit (slot 3) -> set 1 (stop)
- last skill used is Godpoison (slot 4) -> set 1 (stop)
- last skill used is Chaos Eye (slot 6) -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
- last skill used is Take Break (slot 9) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Inferno (15%), Forbidden Fruit (15%), Godpoison (20%), Chaos Eye (15%), Take Break (15%)
- **Set 1:** Attack (20%), Heat Erosion (60%), Take Break (20%)
- **Set 2:** Overrun (50%), Wing Flap (50%)
- **Set 3:** Mini Circle Heal (50%), Forbidden Fruit (25%), Chaos Eye (25%)
  - *Condition:* Mini Circle Heal (slot 1) aims at: ally with the lowest HP ratio

### Samael - Form 3 (Lv 99)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.15x | - | 0.25 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.25) |
| Circle Heal | All allies | Neutral | 1.00x | 0.5s | - | Heal power (2) |
| Super Inferno | All enemies | Fire | 1.00x | 0.7s | - | Magic power (1500) |
| Forbidden Fruit | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Fixed damage (888); Shadow Sew chance |
| Godpoison | All enemies | Water | 0.70x | - | - | Magic power (1400); Paralysis (0.3); Poison |
| Overrun | Single enemy | Bash | 1.00x | - | 0.2 | Plain hit that deals damage; Hits 2-4 times; Fixed critical hit rate |
| Chaos Eye | Piercing | Neutral | 0.90x | - | - | Magic power (1000); Freeze (0.35); Silence (0.35) |
| Heat Erosion | Piercing | Fire | 1.00x | - | - | Magic power (1000) |
| Wing Flap | Random enemies | Wind | 0.90x | - | 0.15 | Plain hit that deals damage; Hits 2-4 times; Sleep (0.25) |
| Evil Eye | Enemy row | Earth | 0.85x | - | - | Magic power (600) |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 40 -> set 4 (stop)
- last skill used is Super Inferno (slot 2) -> set 1 (stop)
- last skill used is Forbidden Fruit (slot 3) -> set 1 (stop)
- last skill used is Godpoison (slot 4) -> set 1 (stop)
- last skill used is Chaos Eye (slot 6) -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
- last skill used is Take Break (slot 10) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Super Inferno (15%), Forbidden Fruit (15%), Godpoison (20%), Chaos Eye (15%), Take Break (15%)
- **Set 1:** Godpoison (20%), Chaos Eye (20%), Heat Erosion (60%)
- **Set 2:** Overrun (50%), Wing Flap (50%)
- **Set 3:** Forbidden Fruit (25%), Evil Eye (75%)
- **Set 4:** Circle Heal (50%), Forbidden Fruit (25%), Chaos Eye (25%)
  - *Condition:* Circle Heal (slot 1) aims at: ally with the lowest HP ratio

## Melek Taus (Family 955)

- **Grand Sealbook Enchantment:** Front line ATK 8% UP

| Form | Level | Rank | ATK | DEF | INT | RES | DEX | AGI | Passive |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| Form 1 | 90 | 7 | 2.79x | 1.24x | 1.09x | 1.02x | 1.11x | 0.96x | Triple Attack |
| Form 2 | 96 | 9 | 3.37x | 1.38x | 1.18x | 1.14x | 1.22x | 1.07x | Triple Attack |
| Form 3 | 99 | 8 | 3.51x | 1.45x | 1.25x | 1.22x | 1.29x | 1.11x | Triple Attack |

### Melek Taus - Form 1 (Lv 90)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Freeze (0.25) |
| Iron Hammer of Death | Single enemy | Bash | 0.65x | - | 2.25 | Plain hit that deals damage; Instant death (0.5) |
| Megaton Press | Single enemy | Bash | 0.90x | - | 0.5 | Plain hit that deals damage; Number of targets (3) |
| Rainbow Flash | Enemy row | Neutral | 1.10x | 1s | - | Magic power (1200) |
| Bloodbath | Single enemy | Weapon's | 0.95x | - | 0.3 | Plain hit that deals damage; Hits 2-4 times; Stun (0.2) |
| Heavy Pressure | All enemies | Earth | 1.00x | 1.15s | - | Magic power (1000); Slow (0.25); Speed modifier (-0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 6) -> set 1 (stop)
- last skill used is Rainbow Flash (slot 3) -> set 2 (stop)
- last skill used is Heavy Pressure (slot 5) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (25%), Iron Hammer of Death (25%), Megaton Press (25%), Take Break (25%)
- **Set 1:** Rainbow Flash (30%), Bloodbath (40%), Heavy Pressure (30%)
- **Set 2:** Iron Hammer of Death (25%), Take Break (75%)

### Melek Taus - Form 2 (Lv 96)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Freeze (0.25) |
| Iron Hammer of Death | Single enemy | Bash | 0.65x | - | 2.25 | Plain hit that deals damage; Instant death (0.5) |
| Megaton Press | Single enemy | Bash | 0.90x | - | 0.5 | Plain hit that deals damage; Number of targets (3) |
| Rainbow Flash | Enemy row | Neutral | 1.10x | 1s | - | Magic power (1400) |
| Bloodbath | Single enemy | Weapon's | 0.95x | - | 0.3 | Plain hit that deals damage; Hits 2-4 times; Stun (0.2) |
| Heavy Pressure | All enemies | Earth | 1.00x | 1.15s | - | Magic power (1200); Slow (0.25); Speed modifier (-0.1) |
| Spanking | Single enemy | Bash | 1.00x | - | 0.75 | Plain hit that deals damage; Chance to push the target back in the turn order |
| Crazy Twister | All enemies | Wind | 0.80x | - | - | Magic power (800); DEF modifier (-0.08); Magic defense modifier (-0.08) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 8) -> set 1 (stop)
- last skill used is Rainbow Flash (slot 3) -> set 2 (stop)
- last skill used is Heavy Pressure (slot 5) -> set 2 (stop)
- last skill used is Spanking (slot 6) -> set 3 (stop)
- last skill used is Take Break (slot 9) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Iron Hammer of Death (20%), Megaton Press (20%), Heavy Pressure (10%), Spanking (20%), Take Break (15%)
- **Set 1:** Rainbow Flash (30%), Heavy Pressure (40%), Crazy Twister (30%)
- **Set 2:** Iron Hammer of Death (25%), Take Break (75%)
- **Set 3:** Megaton Press (25%), Bloodbath (75%)

### Melek Taus - Form 3 (Lv 99)

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Freeze (0.25) |
| Iron Hammer of Death | Single enemy | Bash | 0.65x | - | 2.25 | Plain hit that deals damage; Instant death (0.5) |
| Megaton Press | Single enemy | Bash | 0.90x | - | 0.5 | Plain hit that deals damage; Number of targets (3) |
| Rainbow Flash | Enemy row | Neutral | 1.10x | 1s | - | Magic power (1400) |
| Bloodbath | Single enemy | Weapon's | 0.95x | - | 0.3 | Plain hit that deals damage; Hits 2-4 times; Stun (0.2) |
| Heavy Pressure | All enemies | Earth | 1.00x | 1.15s | - | Magic power (1500); Slow (0.25); Speed modifier (-0.1) |
| Spanking | Single enemy | Bash | 1.00x | - | 0.75 | Plain hit that deals damage; Chance to push the target back in the turn order |
| Crazy Twister | All enemies | Wind | 0.80x | - | - | Magic power (800); DEF modifier (-0.08); Magic defense modifier (-0.08) |
| Last Exile | Random enemies | Stab | 0.75x | - | 0.25 | Plain hit that deals damage; Fixed accuracy (0.75); Paralysis (0.2) |
| Take Break | None | -1 | 0.75x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Take Break (slot 9) -> set 1 (stop)
- last skill used is Rainbow Flash (slot 3) -> set 2 (stop)
- last skill used is Heavy Pressure (slot 5) -> set 2 (stop)
- last skill used is Spanking (slot 6) -> set 3 (stop)
- last skill used is Take Break (slot 10) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Iron Hammer of Death (20%), Megaton Press (20%), Heavy Pressure (10%), Spanking (20%), Take Break (15%)
- **Set 1:** Rainbow Flash (30%), Heavy Pressure (40%), Crazy Twister (30%)
- **Set 2:** Iron Hammer of Death (25%), Take Break (75%)
- **Set 3:** Megaton Press (25%), Bloodbath (75%)
- **Set 4:** Last Exile (100%)

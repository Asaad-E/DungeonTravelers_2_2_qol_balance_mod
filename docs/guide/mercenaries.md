# Mercenaries (Guest Allies)

Reference for all hireable mercenaries at the Tavern, including unlock requirements, hiring costs, contract lengths, growth stages, combat stats, attack repertoires, and AI scripts.

## Three Fates (Character 305)

- **Tavern Availability:** postgame: SEV.pck/sev_296.adv.bin (after defeating Three Fates at Khorramshahr, P19)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 85 | 9,000 Gold | 20 battles | 412 | 362 | 258 | 261 | 111 | 78 | 1004 |
| 2 | 93 | 9,999 Gold | 20 battles | 443 | 405 | 333 | 352 | 139 | 87 | 412 |

### Stage 1 (Lv 85)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Sleep (0.6) |
| Bunmawashi | Random enemies | Weapon's | 1.30x | - | 0.75 | Plain hit that deals damage; Hits 1-3 times |
| First Aid | Single ally | Neutral | 0.90x | - | - | Heal power (12) |
| Karma | All enemies | Neutral | 0.90x | 0.8s | - | Magic power (450); Dispel |
| Material Guard | All allies | Neutral | 0.80x | - | - | - |
| Inferno | All enemies | Fire | 1.00x | 0.71s | - | Magic power (520) |
| Diamond Dust | All enemies | Water | 1.00x | 0.71s | - | Magic power (520) |
| Lightning | All enemies | Lightning | 1.00x | 0.71s | - | Magic power (520) |
| Tornado | All enemies | Wind | 1.00x | 0.71s | - | Magic power (520) |
| Meteor | All enemies | Earth | 1.00x | 0.71s | - | Magic power (520) |
| Take Break | None | -1 | 0.50x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |
| Critical Magic | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (5%), Bunmawashi (5%), First Aid (5%), Karma (5%), Material Guard (5%), Inferno (5%), Diamond Dust (5%), Lightning (5%), Tornado (5%), Meteor (5%), Take Break (50%)
  - *Condition:* First Aid (slot 2) aims at: ally with the lowest HP ratio

### Stage 2 (Lv 93)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Sleep (0.6) |
| Bunmawashi | Random enemies | Weapon's | 1.30x | - | 0.75 | Plain hit that deals damage; Hits 1-3 times |
| First Aid | Single ally | Neutral | 0.90x | - | - | Heal power (12) |
| Karma | All enemies | Neutral | 0.90x | 0.8s | - | Magic power (450); Dispel |
| Material Guard | All allies | Neutral | 0.80x | - | - | - |
| Inferno | All enemies | Fire | 1.00x | 0.71s | - | Magic power (520) |
| Diamond Dust | All enemies | Water | 1.00x | 0.71s | - | Magic power (520) |
| Lightning | All enemies | Lightning | 1.00x | 0.71s | - | Magic power (520) |
| Tornado | All enemies | Wind | 1.00x | 0.71s | - | Magic power (520) |
| Meteor | All enemies | Earth | 1.00x | 0.71s | - | Magic power (520) |
| Take Break | None | -1 | 0.50x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |
| Critical Magic | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (5%), Bunmawashi (5%), First Aid (5%), Karma (5%), Material Guard (5%), Inferno (5%), Diamond Dust (5%), Lightning (5%), Tornado (5%), Meteor (5%), Take Break (50%)
  - *Condition:* First Aid (slot 2) aims at: ally with the lowest HP ratio

## Yoshitsune (Character 306)

- **Tavern Availability:** postgame: St23_0040/St23_d0030.adv.bin (after battle 41 Yoshitsune, P44)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 98 | 9,999 Gold | 14 battles | 605 | 412 | 247 | 371 | 182 | 130 | 1006 |
| 2 | 99 | 9,999 Gold | 16 battles | 675 | 512 | 272 | 421 | 192 | 150 | 386 |

### Stage 1 (Lv 98)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | 0.4 | Plain hit that deals damage; Slow (0.25) |
| Raging Smash | Single enemy | Weapon's | 0.95x | - | 0.5 | Plain hit that deals damage |
| Onikagura | All enemies | Slash | 0.85x | - | 0.1 | Plain hit that deals damage |
| Armor Penetration | Single enemy | Slash | 0.90x | - | 0.1 | Plain hit that deals damage; Ignores defense; DEF modifier (-0.1) |
| Rumbling Thunder | Enemy row | Lightning | 0.80x | - | - | Magic power (800); Paralysis (0.3) |
| Lightning Scroll | All enemies | Lightning | 1.40x | 1.65s | - | Magic power; Damage as a fraction of the target max HP (0.4); Speed modifier (-0.12); Damage cap (400) |
| Lifetaker Edge | Single enemy | Slash | 1.00x | - | 0.15 | Plain hit that deals damage; Hits twice; Instant death (0.25); Only works on living targets |
| Backward Swing | Single enemy | Bash | 0.90x | - | 0.2 | Plain hit that deals damage; Paralysis (0.3) |
| Moonlight Purgatory | Single enemy | Slash | 0.50x | - | 0.2 | Critical rate bonus, in points (10); Only works on living targets; Hits three times; Plain hit that deals damage |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Raging Smash (slot 1) -> set 1 (stop)
- last skill used is Lifetaker Edge (slot 6) -> set 1 (stop)
- last skill used is Armor Penetration (slot 3) -> set 2 (stop)
- last skill used is Backward Swing (slot 7) -> set 2 (stop)
- last skill used is Lightning Scroll (slot 5) -> set 3 (stop)
- last skill used is Moonlight Purgatory (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Raging Smash (25%), Armor Penetration (25%), Lifetaker Edge (25%), Backward Swing (25%)
- **Set 1:** Attack (20%), Onikagura (40%), Lightning Scroll (40%)
- **Set 2:** Attack (20%), Rumbling Thunder (40%), Moonlight Purgatory (40%)
- **Set 3:** Attack (50%), Wait and See (50%)

### Stage 2 (Lv 99)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | 0.4 | Plain hit that deals damage; Slow (0.25) |
| Raging Smash | Single enemy | Weapon's | 0.95x | - | 0.65 | Plain hit that deals damage |
| Onikagura | All enemies | Slash | 0.85x | - | 0.1 | Plain hit that deals damage |
| Armor Penetration | Single enemy | Slash | 0.90x | - | 0.1 | Plain hit that deals damage; Ignores defense; DEF modifier (-0.1) |
| Godspeed Triple Thrust | Single enemy | Stab | 0.60x | - | 0.3 | Plain hit that deals damage; Hits three times; Instant death (0.3) |
| Double Roundhouse Kick | Enemy row | Bash | 0.95x | - | - | Plain hit that deals damage; Hits twice |
| Rumbling Thunder | Enemy row | Lightning | 0.80x | - | - | Magic power (1200); Paralysis (0.3) |
| Purple Lightning | All enemies | Lightning | 0.60x | - | - | Magic power (800); Paralysis (0.6); Physical accuracy modifier (-0.1); Magic defense modifier (-0.1) |
| Lightning Scroll | All enemies | Lightning | 1.40x | 1.65s | - | Magic power; Damage as a fraction of the target max HP (0.4); Speed modifier (-0.12); Damage cap (400) |
| Lifetaker Edge | Single enemy | Slash | 1.00x | - | 0.15 | Plain hit that deals damage; Hits twice; Instant death (0.25); Only works on living targets |
| Backward Swing | Single enemy | Bash | 0.90x | - | 0.3 | Plain hit that deals damage; Paralysis (0.4) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Raging Smash (slot 1) -> set 1 (stop)
- last skill used is Lifetaker Edge (slot 9) -> set 1 (stop)
- last skill used is Armor Penetration (slot 3) -> set 2 (stop)
- last skill used is Backward Swing (slot 10) -> set 2 (stop)
- last skill used is Onikagura (slot 2) -> set 3 (stop)
- last skill used is Godspeed Triple Thrust (slot 4) -> set 3 (stop)
- last skill used is Double Roundhouse Kick (slot 5) -> set 4 (stop)
- last skill used is Rumbling Thunder (slot 6) -> set 4 (stop)
- last skill used is Attack (slot 0) -> set 5 (stop)
**Action Sets:**
- **Set 0:** Raging Smash (25%), Armor Penetration (25%), Lifetaker Edge (25%), Backward Swing (25%)
- **Set 1:** Attack (20%), Onikagura (40%), Double Roundhouse Kick (40%)
- **Set 2:** Attack (20%), Godspeed Triple Thrust (40%), Rumbling Thunder (40%)
- **Set 3:** Attack (25%), Purple Lightning (75%)
- **Set 4:** Attack (25%), Lightning Scroll (75%)
- **Set 5:** Purple Lightning (50%), Lightning Scroll (50%)

## Marduk (Character 307)

- **Tavern Availability:** postgame: St21_1010/St21_g0020.adv.bin (after battle 41 Marduk, P42)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 97 | 9,999 Gold | 15 battles | 565 | 2150 | 261 | 408 | 147 | 98 | 1008 |
| 2 | 99 | 9,999 Gold | 17 battles | 615 | 2250 | 286 | 458 | 157 | 118 | 386 |

### Stage 1 (Lv 97)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | 0.35 | Plain hit that deals damage; Paralysis (0.35) |
| All Shots Fired | Random enemies | Stab | 0.70x | - | 0.25 | Plain hit that deals damage; Hits 3-5 times |
| Cherubeam | Enemy row | Neutral | 0.90x | - | - | Magic power (850); Physical accuracy modifier (-0.1); Magic accuracy modifier (-0.1) |
| Silence Bullet | Single enemy | Stab | 1.00x | - | 0.4 | Plain hit that deals damage; Silence (0.75) |
| Thunder Break | Piercing | Lightning | 1.15x | - | - | Magic power (800) |
| Buster Cannon EX | Piercing | Stab | 0.85x | - | 0.35 | Plain hit that deals damage; DEF modifier (-0.1) |
| Material Guard | All allies | Neutral | 0.85x | - | - | - |
| Happy Trigger | Random enemies | Stab | 0.85x | - | 0.1 | Plain hit that deals damage; Hits 1-3 times |
| Energy Ball | Single enemy | Neutral | 0.90x | - | - | Magic power (1200) |
| Limiter Removed | Self | Neutral | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Warning Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
- last skill used is Cherubeam (slot 2) -> set 2 (stop)
- last skill used is Buster Cannon EX (slot 5) -> set 2 (stop)
- Limiter Removed (slot 9) is active -> set 3 (stop)
**Action Sets:**
- **Set 0:** All Shots Fired (25%), Cherubeam (25%), Buster Cannon EX (25%), Material Guard (25%)
  - *Condition:* Material Guard (slot 6) was used 1 times or more -> Attack (slot 0)
- **Set 1:** All Shots Fired (25%), Thunder Break (50%), Limiter Removed (25%)
- **Set 2:** Silence Bullet (75%), Thunder Break (25%)
- **Set 3:** Silence Bullet (20%), Happy Trigger (40%), Energy Ball (40%)

### Stage 2 (Lv 99)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | 0.35 | Plain hit that deals damage; Paralysis (0.35) |
| All Shots Fired | Random enemies | Stab | 0.70x | - | 0.25 | Plain hit that deals damage; Hits 3-5 times |
| Cherubeam | Enemy row | Neutral | 0.90x | - | - | Magic power (850); Physical accuracy modifier (-0.1); Magic accuracy modifier (-0.1) |
| Critical Cartridge | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Fixed critical hit rate |
| Thunder Break | Piercing | Lightning | 1.15x | - | - | Magic power (1000) |
| Buster Cannon EX | Piercing | Stab | 0.85x | - | 0.35 | Plain hit that deals damage; DEF modifier (-0.1) |
| Material Guard | All allies | Neutral | 0.85x | - | - | - |
| Happy Trigger | Random enemies | Stab | 0.85x | - | 0.25 | Plain hit that deals damage; Hits 1-3 times |
| Energy Ball | Single enemy | Neutral | 0.90x | - | - | Magic power (1200) |
| Piercing Panic Voice | Piercing | Neutral | 0.80x | - | - | Magic power (800); Stun (0.25) |
| Limiter Removed | Self | Neutral | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Warning Shot | - |

#### AI Behavior

**Opening Actions:**
- Limiter Removed (slot 10) is active -> set 5 (stop)
- last skill used is Cherubeam (slot 2) -> set 1 (stop)
- last skill used is Critical Cartridge (slot 3) -> set 2 (stop)
- last skill used is Buster Cannon EX (slot 5) -> set 3 (stop)
- last skill used is Attack (slot 0) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Cherubeam (20%), Critical Cartridge (20%), Buster Cannon EX (20%), Happy Trigger (20%), Energy Ball (20%)
- **Set 1:** Attack (25%), Happy Trigger (75%)
- **Set 2:** Attack (20%), Thunder Break (40%), Piercing Panic Voice (40%)
- **Set 3:** Attack (25%), Energy Ball (75%)
- **Set 4:** All Shots Fired (50%), Material Guard (25%), Limiter Removed (25%)
- **Set 5:** Critical Cartridge (25%), Buster Cannon EX (25%), Happy Trigger (25%), Energy Ball (25%)

## Citlalinicue (Character 308)

- **Tavern Availability:** postgame: St20_1040/St20_e0140.adv.bin (after battle 45 Citlalinicue, P41)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 96 | 9,999 Gold | 16 battles | 633 | 441 | 272 | 302 | 153 | 109 | 1010 |
| 2 | 99 | 9,999 Gold | 18 battles | 703 | 541 | 297 | 352 | 163 | 129 | 386 |

### Stage 1 (Lv 96)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | 0.35 | Plain hit that deals damage; Stun (0.2) |
| Buchikamashi | All enemies | Bash | 0.80x | - | 0.35 | Plain hit that deals damage; Stun (0.2) |
| God Stamp | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Number of targets (4) |
| Iron Hammer of Death | Single enemy | Bash | 0.65x | - | 2.25 | Plain hit that deals damage; Instant death (0.5) |
| Demon Sledgehammer | Single enemy | Bash | 0.85x | - | 0.15 | Plain hit that deals damage; ATK modifier (-0.12); DEF modifier (-0.12) |
| Poison Hammer | Single enemy | Bash | 1.00x | - | 0.5 | Plain hit that deals damage; Poison (0.75) |
| Hammer Price | Single enemy | Bash | 0.75x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Charge | Self | Neutral | 1.10x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Buchikamashi (slot 1) -> set 1 (stop)
- last skill used is Iron Hammer of Death (slot 3) -> set 1 (stop)
- last skill used is God Stamp (slot 2) -> set 2 (stop)
- last skill used is Demon Sledgehammer (slot 4) -> set 2 (stop)
- last skill used is Charge (slot 7) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Buchikamashi (20%), God Stamp (20%), Iron Hammer of Death (20%), Demon Sledgehammer (20%), Charge (20%)
- **Set 1:** Attack (75%), Take Break (25%)
- **Set 2:** Attack (50%), Hammer Price (50%)
- **Set 3:** Attack (25%), Demon Sledgehammer (50%), Poison Hammer (25%)

### Stage 2 (Lv 99)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | 0.35 | Plain hit that deals damage; Stun (0.2) |
| Bunmawashi | Random enemies | Weapon's | 0.80x | - | 0.5 | Plain hit that deals damage; Hits 1-3 times |
| Buchikamashi | All enemies | Bash | 0.80x | - | 0.35 | Plain hit that deals damage; Stun (0.2) |
| God Stamp | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Number of targets (4) |
| Iron Hammer of Death | Single enemy | Bash | 0.65x | - | 2.25 | Plain hit that deals damage; Instant death (0.5) |
| Demon Sledgehammer | Single enemy | Bash | 0.90x | - | 0.3 | Plain hit that deals damage; ATK modifier (-0.12); DEF modifier (-0.12) |
| Rampage | Random enemies | Weapon's | 0.65x | - | 0.4 | Plain hit that deals damage; Hits 2-4 times; Dispel (0.25) |
| Stab Smash | Single enemy | Bash | 1.00x | - | 0.15 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.25) |
| Poison Hammer | Single enemy | Bash | 1.00x | - | 0.65 | Plain hit that deals damage; Poison |
| Hammer Price | Single enemy | Bash | 0.75x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Charge | Self | Neutral | 1.10x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Bunmawashi (slot 1) -> set 1 (stop)
- last skill used is Buchikamashi (slot 2) -> set 1 (stop)
- last skill used is God Stamp (slot 3) -> set 2 (stop)
- last skill used is Iron Hammer of Death (slot 4) -> set 2 (stop)
- last skill used is Charge (slot 10) -> set 3 (stop)
- last skill used is Attack (slot 0) -> set 4 (stop)
**Action Sets:**
- **Set 0:** Bunmawashi (20%), Buchikamashi (20%), God Stamp (20%), Iron Hammer of Death (20%), Charge (20%)
- **Set 1:** Attack (25%), Stab Smash (75%)
- **Set 2:** Attack (25%), Rampage (75%)
- **Set 3:** Demon Sledgehammer (50%), Poison Hammer (50%)
- **Set 4:** Demon Sledgehammer (20%), Poison Hammer (20%), Hammer Price (60%)

## Arjuna (Character 309)

- **Tavern Availability:** postgame: St22_1020/St22_b0030.adv.bin (after battle 42 Arjuna, P43)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 95 | 9,999 Gold | 16 battles | 578 | 421 | 294 | 345 | 168 | 126 | 1012 |
| 2 | 99 | 9,999 Gold | 18 battles | 648 | 521 | 319 | 395 | 188 | 146 | 386 |

### Stage 1 (Lv 95)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Poison (0.3) |
| Guided Shot | Single enemy | Stab | 0.90x | - | 0.45 | Plain hit that deals damage; Fixed accuracy |
| Electric Uppercut | Single enemy | Lightning | 0.95x | - | 0.3 | Plain hit that deals damage; Stun (0.75) |
| Divine Cannon | Piercing | Stab | 0.80x | - | 0.15 | Plain hit that deals damage; Fixed critical hit rate (0.5) |
| Hunter's Arrow EX | None | Neutral | 0.70x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Tornado | All enemies | Wind | 1.15x | 0.68s | - | Magic power (1200) |
| Two Arrows | Random enemies | Stab | 1.10x | - | 0.2 | Plain hit that deals damage; Hits twice |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Electric Uppercut (slot 2) -> set 2 (stop)
- last skill used is Divine Cannon (slot 3) -> set 2 (stop)
- last skill used is Tornado (slot 5) -> set 2 (stop)
- Hunter's Arrow EX (slot 4) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Guided Shot (20%), Electric Uppercut (20%), Divine Cannon (20%), Hunter's Arrow EX (20%), Tornado (20%)
- **Set 1:** Attack (25%), Guided Shot (25%), Divine Cannon (25%), Two Arrows (25%)
- **Set 2:** Attack (25%), Guided Shot (25%), Two Arrows (50%)

### Stage 2 (Lv 99)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Poison (0.3) |
| Guided Shot | Single enemy | Stab | 0.95x | - | 0.6 | Plain hit that deals damage; Fixed accuracy |
| Spiral Arrow | Single enemy | Stab | 0.40x | - | 1.5 | Plain hit that deals damage |
| Electric Uppercut | Single enemy | Lightning | 0.95x | - | 0.3 | Plain hit that deals damage; Stun (0.75) |
| Divine Cannon | Piercing | Stab | 0.85x | - | 0.25 | Plain hit that deals damage; Fixed critical hit rate (0.5) |
| Tornado | All enemies | Wind | 1.15x | 0.68s | - | Magic power (1200) |
| Tempest | Single enemy | Wind | 1.00x | 0.7s | - | Magic power (2000) |
| Blooming Quiver | None | Neutral | 1.00x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Petrifying Arrow | Random enemies | Stab | 0.90x | - | 0.25 | Plain hit that deals damage; Hits twice; Petrification (0.3) |
| Chain Spike | Single enemy | Weapon's | 0.60x | - | 0.2 | Plain hit that deals damage; Number of hits (5); Damage change for each later target or hit (-0.05); Critical rate grows with each hit; Plain hit that deals damage |
| Honey Wonderful EX | Single ally | Neutral | 0.90x | - | - | How many ailments of the listed order it cures (8) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Honey Wonderful EX (slot 10) -> set 1 (stop)
- lowest HP ratio among allies <= 50 -> set 2 (stop)
- last skill used is Guided Shot (slot 1) -> set 4 (stop)
- last skill used is Electric Uppercut (slot 3) -> set 4 (stop)
- last skill used is Spiral Arrow (slot 2) -> set 5 (stop)
- last skill used is Divine Cannon (slot 4) -> set 5 (stop)
- last skill used is Chain Spike (slot 9) -> set 5 (stop)
- Blooming Quiver (slot 7) is active -> set 3 (stop)
**Action Sets:**
- **Set 0:** Guided Shot (20%), Spiral Arrow (20%), Electric Uppercut (20%), Divine Cannon (20%), Blooming Quiver (20%)
- **Set 1:** Attack (25%), Electric Uppercut (25%), Tempest (25%), Petrifying Arrow (25%)
- **Set 2:** Spiral Arrow (20%), Divine Cannon (20%), Honey Wonderful EX (60%)
  - *Condition:* Honey Wonderful EX (slot 10) aims at: ally with the lowest HP ratio
- **Set 3:** Guided Shot (25%), Divine Cannon (25%), Tornado (25%), Chain Spike (25%)
- **Set 4:** Tornado (50%), Tempest (50%)
- **Set 5:** Attack (25%), Petrifying Arrow (75%)

## Euphemia (Character 310)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main07_20_Start, chapter 7, the Tavern opens after C24)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 26 | 400 Gold | 25 battles | 91 | 58 | 18 | 21 | 44 | 35 | 135 |
| 2 | 38 | 700 Gold | 26 battles | 138 | 118 | 27 | 38 | 52 | 43 | 319 |
| 3 | 46 | 1,400 Gold | 27 battles | 163 | 132 | 36 | 51 | 61 | 53 | 353 |
| 4 | 55 | 2,200 Gold | 28 battles | 186 | 154 | 44 | 60 | 72 | 62 | 230 |
| 5 | 67 | 3,000 Gold | 30 battles | 249 | 173 | 57 | 82 | 88 | 71 | 385 |

### Stage 1 (Lv 26)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Raging Smash | Single enemy | Weapon's | 0.85x | - | 0.2 | Plain hit that deals damage |
| Move, Big Brother! | Single enemy | Bash | 0.50x | - | 0.1 | Plain hit that deals damage; Instant death (0.75) |
| War Cry | All allies | Neutral | 1.25x | - | - | ATK modifier (0.14) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (60%), Raging Smash (20%), Move, Big Brother! (10%), War Cry (10%)
  - *Condition:* War Cry (slot 3) was used 1 times or more -> Attack (slot 0)

### Stage 2 (Lv 38)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Raging Smash | Single enemy | Weapon's | 0.90x | - | 0.35 | Plain hit that deals damage |
| Move, Big Brother! | Single enemy | Bash | 0.50x | - | 0.1 | Plain hit that deals damage; Instant death (0.75) |
| Painful Strike | Single enemy | Neutral | 0.60x | - | 0.75 | Plain hit that deals damage |
| War Cry | All allies | Neutral | 1.25x | - | - | ATK modifier (0.14) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (25%), Raging Smash (25%), Move, Big Brother! (15%), Painful Strike (15%), War Cry (20%)
  - *Condition:* War Cry (slot 4) was used 1 times or more -> Attack (slot 0)

### Stage 3 (Lv 46)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Raging Smash | Single enemy | Weapon's | 0.90x | - | 0.35 | Plain hit that deals damage |
| Move, Big Brother! | Single enemy | Bash | 0.50x | - | 0.1 | Plain hit that deals damage; Instant death (0.75) |
| Painful Strike | Single enemy | Neutral | 0.60x | - | 0.75 | Plain hit that deals damage |
| Bunmawashi | Random enemies | Weapon's | 0.50x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| War Cry | All allies | Neutral | 1.25x | - | - | ATK modifier (0.14) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Bunmawashi (slot 4) -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Raging Smash (20%), Move, Big Brother! (20%), Painful Strike (10%), Bunmawashi (10%), War Cry (20%)
  - *Condition:* War Cry (slot 5) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (50%), Raging Smash (50%)
- **Set 2:** Raging Smash (25%), Move, Big Brother! (25%), Painful Strike (25%), Bunmawashi (25%)

### Stage 4 (Lv 55)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Raging Smash | Single enemy | Weapon's | 0.90x | - | 0.35 | Plain hit that deals damage |
| Move, Big Brother! | Single enemy | Bash | 0.50x | - | 0.25 | Plain hit that deals damage; Instant death |
| Painful Strike | Single enemy | Neutral | 0.60x | - | 0.75 | Plain hit that deals damage |
| Bunmawashi | Random enemies | Weapon's | 0.50x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Cruciform Slash | Single enemy | Slash | 1.00x | - | 0.6 | Plain hit that deals damage; Only works on living targets |
| War Cry | All allies | Neutral | 1.25x | - | - | ATK modifier (0.14) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is War Cry (slot 6) -> set 1 (stop)
- last skill used is Move, Big Brother! (slot 2) -> set 2 (stop)
- last skill used is Bunmawashi (slot 4) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Raging Smash (10%), Move, Big Brother! (15%), Painful Strike (15%), Bunmawashi (10%), Cruciform Slash (10%), War Cry (20%)
- **Set 1:** Attack (50%), Raging Smash (25%), Cruciform Slash (25%)
- **Set 2:** Attack (60%), Cruciform Slash (40%)

### Stage 5 (Lv 67)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Raging Smash | Single enemy | Weapon's | 0.95x | - | 0.5 | Plain hit that deals damage |
| Move, Big Brother! | Single enemy | Bash | 0.50x | - | 0.25 | Plain hit that deals damage; Instant death |
| Painful Strike | Single enemy | Neutral | 0.80x | - | 1 | Plain hit that deals damage |
| Bunmawashi | Random enemies | Weapon's | 0.50x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Cruciform Slash | Single enemy | Slash | 1.00x | - | 0.6 | Plain hit that deals damage; Only works on living targets |
| Shock Spiral | Enemy row | Lightning | 0.80x | - | 0.2 | Plain hit that deals damage; Paralysis (0.25) |
| War Cry | All allies | Neutral | 1.25x | - | - | ATK modifier (0.14) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is War Cry (slot 7) -> set 1 (stop)
- last skill used is Move, Big Brother! (slot 2) -> set 2 (stop)
- last skill used is Bunmawashi (slot 4) -> set 2 (stop)
- last skill used is Shock Spiral (slot 6) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Raging Smash (10%), Move, Big Brother! (10%), Painful Strike (10%), Bunmawashi (10%), Cruciform Slash (10%), Shock Spiral (10%), War Cry (20%)
- **Set 1:** Raging Smash (40%), Bunmawashi (20%), Cruciform Slash (40%)
- **Set 2:** Attack (80%), Painful Strike (20%)

## Tatiana (Character 311)

- **Tavern Availability:** story: St10_0010/Main08_09.adv.bin (Main08_15_Start, chapter 8 before C30)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 36 | 1,000 Gold | 23 battles | 152 | 116 | 28 | 37 | 48 | 33 | 151 |
| 2 | 43 | 1,400 Gold | 24 battles | 178 | 132 | 35 | 46 | 55 | 39 | 172 |
| 3 | 52 | 2,400 Gold | 25 battles | 212 | 162 | 49 | 55 | 64 | 44 | 215 |
| 4 | 63 | 3,300 Gold | 26 battles | 258 | 191 | 63 | 64 | 71 | 53 | 376 |
| 5 | 72 | 4,400 Gold | 27 battles | 302 | 235 | 72 | 75 | 82 | 61 | 407 |

### Stage 1 (Lv 36)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Aura Eliminate | Single enemy | Weapon's | 0.85x | - | 0.15 | Plain hit that deals damage; Dispel (0.5) |
| Shield Bash | Single enemy | Bash | 0.70x | - | -0.05 | Plain hit that deals damage; Stun (0.35) |
| Charge | Self | Neutral | 1.10x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Charge (slot 3) -> set 1 (stop)
- an opponent has a buff -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (50%), Aura Eliminate (15%), Shield Bash (15%), Charge (20%)
- **Set 1:** Attack (100%)
- **Set 2:** Attack (20%), Aura Eliminate (60%), Shield Bash (20%)
  - *Condition:* Aura Eliminate (slot 1) aims at: opponent with a buff

### Stage 2 (Lv 43)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Aura Eliminate | Single enemy | Weapon's | 0.85x | - | 0.15 | Plain hit that deals damage; Dispel (0.5) |
| Shield Bash | Single enemy | Bash | 0.70x | - | -0.05 | Plain hit that deals damage; Stun (0.35) |
| Mince | Single enemy | Slash | 0.85x | - | 0.1 | Plain hit that deals damage; ATK modifier (-0.18); DEF modifier (-0.18) |
| Charge | Self | Neutral | 1.10x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Charge (slot 4) -> set 1 (stop)
- an opponent has a buff -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (30%), Aura Eliminate (15%), Shield Bash (15%), Mince (20%), Charge (20%)
  - *Condition:* Mince (slot 3) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (100%)
- **Set 2:** Attack (20%), Aura Eliminate (60%), Shield Bash (20%)
  - *Condition:* Aura Eliminate (slot 1) aims at: opponent with a buff

### Stage 3 (Lv 52)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Aura Eliminate | Single enemy | Weapon's | 0.85x | - | 0.15 | Plain hit that deals damage; Dispel (0.5) |
| Shield Bash | Single enemy | Bash | 0.85x | - | 0.1 | Plain hit that deals damage; Stun (0.45) |
| Mince | Single enemy | Slash | 0.85x | - | 0.1 | Plain hit that deals damage; ATK modifier (-0.18); DEF modifier (-0.18) |
| Gust Thrust | Single enemy | Wind | 0.90x | - | 0.35 | Plain hit that deals damage; Silence (0.5) |
| Charge | Self | Neutral | 1.10x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Charge (slot 5) -> set 1 (stop)
- an opponent has a buff -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Aura Eliminate (15%), Shield Bash (15%), Mince (20%), Gust Thrust (10%), Charge (20%)
  - *Condition:* Mince (slot 3) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (70%), Shield Bash (30%)
- **Set 2:** Attack (15%), Aura Eliminate (60%), Shield Bash (15%), Gust Thrust (10%)
  - *Condition:* Aura Eliminate (slot 1) aims at: opponent with a buff

### Stage 4 (Lv 63)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Aura Eliminate | Single enemy | Weapon's | 0.90x | - | 0.3 | Plain hit that deals damage; Dispel (0.6) |
| Shield Bash | Single enemy | Bash | 0.85x | - | 0.1 | Plain hit that deals damage; Stun (0.45) |
| Mince | Single enemy | Slash | 0.85x | - | 0.1 | Plain hit that deals damage; ATK modifier (-0.18); DEF modifier (-0.18) |
| Gust Thrust | Single enemy | Wind | 1.00x | - | 0.55 | Plain hit that deals damage; Silence (0.75) |
| Lifetaker Edge | Single enemy | Slash | 0.85x | - | -0.1 | Plain hit that deals damage; Hits twice; Instant death (0.2); Only works on living targets |
| Charge | Self | Neutral | 1.10x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Charge (slot 6) -> set 1 (stop)
- an opponent has a buff -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Aura Eliminate (15%), Shield Bash (15%), Mince (15%), Gust Thrust (10%), Lifetaker Edge (10%), Charge (20%)
  - *Condition:* Mince (slot 3) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (70%), Shield Bash (30%)
- **Set 2:** Attack (10%), Aura Eliminate (60%), Shield Bash (10%), Gust Thrust (10%), Lifetaker Edge (10%)
  - *Condition:* Aura Eliminate (slot 1) aims at: opponent with a buff

### Stage 5 (Lv 72)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Aura Eliminate | Single enemy | Weapon's | 0.90x | - | 0.3 | Plain hit that deals damage; Dispel (0.6) |
| Shield Bash | Single enemy | Bash | 0.95x | - | 0.3 | Plain hit that deals damage; Stun (0.6) |
| Mince | Single enemy | Slash | 0.85x | - | 0.1 | Plain hit that deals damage; ATK modifier (-0.18); DEF modifier (-0.18) |
| Gust Thrust | Single enemy | Wind | 1.20x | - | 0.75 | Plain hit that deals damage; Silence |
| Lifetaker Edge | Single enemy | Slash | 0.92x | - | - | Plain hit that deals damage; Hits twice; Instant death (0.25); Only works on living targets |
| Material Guard | All allies | Neutral | 0.75x | - | - | - |
| Charge | Self | Neutral | 1.10x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Charge (slot 7) -> set 1 (stop)
- an opponent has a buff -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Aura Eliminate (10%), Shield Bash (10%), Mince (15%), Gust Thrust (10%), Lifetaker Edge (10%), Material Guard (15%), Charge (15%)
  - *Condition:* Mince (slot 3) was used 1 times or more -> Attack (slot 0)
  - *Condition:* Material Guard (slot 6) was used 1 times or more -> Shield Bash (slot 2)
- **Set 1:** Attack (50%), Shield Bash (30%), Gust Thrust (20%)
- **Set 2:** Attack (10%), Aura Eliminate (60%), Gust Thrust (15%), Lifetaker Edge (15%)
  - *Condition:* Aura Eliminate (slot 1) aims at: opponent with a buff

## Luzie (Character 312)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main10_00_Start, start of chapter 10 after C34)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 45 | 1,700 Gold | 20 battles | 171 | 166 | 35 | 41 | 50 | 35 | 172 |
| 2 | 54 | 3,000 Gold | 22 battles | 218 | 192 | 44 | 53 | 63 | 44 | 220 |
| 3 | 65 | 3,800 Gold | 24 battles | 264 | 224 | 61 | 72 | 79 | 59 | 384 |
| 4 | 78 | 4,800 Gold | 26 battles | 327 | 294 | 70 | 81 | 92 | 67 | 318 |
| 5 | 87 | 5,600 Gold | 28 battles | 377 | 338 | 82 | 94 | 113 | 82 | 1419 |

### Stage 1 (Lv 45)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Poison Spear | Single enemy | Stab | 0.85x | - | 0.2 | Plain hit that deals damage; Poison (0.3) |
| Backward Swing | Single enemy | Bash | 0.85x | - | 0.1 | Plain hit that deals damage; Paralysis (0.2) |
| Skewer | Single enemy | Stab | 0.65x | - | 0.25 | Plain hit that deals damage; Instant death (0.1) |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1
- last skill used is Backward Swing (slot 2) -> set 2
**Action Sets:**
- **Set 0:** Attack (25%), Poison Spear (25%), Backward Swing (25%), Skewer (25%)
- **Set 1:** Poison Spear (40%), Backward Swing (30%), Skewer (30%)
- **Set 2:** Attack (20%), Poison Spear (40%), Skewer (40%)

### Stage 2 (Lv 54)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Poison Spear | Single enemy | Stab | 0.85x | - | 0.2 | Plain hit that deals damage; Poison (0.3) |
| Backward Swing | Single enemy | Bash | 0.90x | - | 0.2 | Plain hit that deals damage; Paralysis (0.3) |
| Skewer | Single enemy | Stab | 0.65x | - | 0.25 | Plain hit that deals damage; Instant death (0.1) |
| Let's Charge! | Piercing | Stab | 0.80x | - | -0.1 | Plain hit that deals damage; Hits 1-3 times |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1
**Action Sets:**
- **Set 0:** Attack (15%), Poison Spear (30%), Backward Swing (30%), Skewer (25%)
- **Set 1:** Attack (10%), Poison Spear (5%), Backward Swing (5%), Skewer (5%), Let's Charge! (75%)

### Stage 3 (Lv 65)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Poison Spear | Single enemy | Stab | 0.90x | - | 0.4 | Plain hit that deals damage; Poison (0.5) |
| Backward Swing | Single enemy | Bash | 0.90x | - | 0.2 | Plain hit that deals damage; Paralysis (0.3) |
| Skewer | Single enemy | Stab | 0.65x | - | 0.25 | Plain hit that deals damage; Instant death (0.1) |
| Let's Charge! | Piercing | Stab | 0.95x | - | 0.1 | Plain hit that deals damage; Hits 1-3 times |
| Ether Strike | Piercing | Stab | 0.80x | - | 0.2 | Plain hit that deals damage |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (40%), Poison Spear (15%), Backward Swing (30%), Skewer (15%)
- **Set 1:** Skewer (20%), Let's Charge! (40%), Ether Strike (40%)

### Stage 4 (Lv 78)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Poison Spear | Single enemy | Stab | 0.90x | - | 0.6 | Plain hit that deals damage; Poison (0.5) |
| Backward Swing | Single enemy | Bash | 0.90x | - | 0.3 | Plain hit that deals damage; Paralysis (0.4) |
| Skewer | Single enemy | Stab | 0.75x | - | 0.4 | Plain hit that deals damage; Instant death (0.15) |
| Let's Charge! | Piercing | Stab | 1.05x | - | 0.2 | Plain hit that deals damage; Hits 1-3 times |
| Ether Strike | Piercing | Stab | 0.85x | - | 0.35 | Plain hit that deals damage |
| Circle Protect | All allies | Neutral | 1.25x | 0.8s | - | DEF modifier (0.12) |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (5%), Poison Spear (25%), Backward Swing (25%), Skewer (25%), Circle Protect (20%)
  - *Condition:* Circle Protect (slot 6) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Skewer (20%), Let's Charge! (40%), Ether Strike (40%)

### Stage 5 (Lv 87)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Slow (0.25) |
| Poison Spear | Single enemy | Stab | 0.90x | - | 0.6 | Plain hit that deals damage; Poison (0.5) |
| Backward Swing | Single enemy | Bash | 0.90x | - | 0.3 | Plain hit that deals damage; Paralysis (0.4) |
| Skewer | Single enemy | Stab | 0.95x | - | 0.4 | Plain hit that deals damage; Instant death (0.4) |
| Let's Charge! | Piercing | Stab | 1.05x | - | 0.35 | Plain hit that deals damage; Hits 1-3 times |
| Ether Strike | Piercing | Stab | 0.95x | - | 0.5 | Plain hit that deals damage |
| Mach Stab | Piercing | Stab | 0.85x | - | 0.25 | Plain hit that deals damage; Hits twice; Stun (0.65) |
| Circle Protect | All allies | Neutral | 1.25x | 0.8s | - | DEF modifier (0.12) |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Poison Spear (10%), Backward Swing (10%), Skewer (10%), Let's Charge! (10%), Ether Strike (10%), Mach Stab (10%), Circle Protect (20%)
  - *Condition:* Circle Protect (slot 7) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Poison Spear (25%), Let's Charge! (25%), Ether Strike (25%), Mach Stab (25%)

## Natalia (Character 313)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main07_20_Start, chapter 7, the Tavern opens after C24)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 28 | 700 Gold | 18 battles | 91 | 42 | 38 | 41 | 24 | 24 | 135 |
| 2 | 40 | 1,400 Gold | 20 battles | 120 | 86 | 55 | 82 | 41 | 37 | 319 |
| 3 | 49 | 3,000 Gold | 22 battles | 162 | 130 | 67 | 101 | 54 | 46 | 353 |
| 4 | 57 | 3,800 Gold | 24 battles | 189 | 142 | 89 | 123 | 67 | 55 | 230 |
| 5 | 68 | 4,600 Gold | 26 battles | 234 | 171 | 103 | 148 | 79 | 63 | 402 |

### Stage 1 (Lv 28)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Electric Uppercut | Single enemy | Lightning | 0.85x | - | 0.15 | Plain hit that deals damage; Stun (0.5) |
| Heal | Single ally | Neutral | 1.50x | 1.25s | - | Heal power (10) |
| Poison | All enemies | Water | 1.10x | 1.15s | - | Deals no damage; Poison |
| Terrorize | Single enemy | Fire | 1.10x | 1s | - | Deals no damage; Stun |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 80 -> set 1
**Action Sets:**
- **Set 0:** Attack (30%), Electric Uppercut (30%), Poison (20%), Terrorize (20%)
- **Set 1:** Attack (10%), Electric Uppercut (10%), Heal (80%)
  - *Condition:* Heal (slot 2) aims at: ally with the lowest HP ratio

### Stage 2 (Lv 40)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Electric Uppercut | Single enemy | Lightning | 0.85x | - | 0.15 | Plain hit that deals damage; Stun (0.5) |
| Heal | Single ally | Neutral | 1.50x | 1.25s | - | Heal power (12) |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (300); Damage based on RES |
| Poison | All enemies | Water | 1.35x | 1.25s | - | Deals no damage; Poison |
| Terrorize | Single enemy | Fire | 1.10x | 1s | - | Deals no damage; Stun |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 75 -> set 1
- last skill used is Prism Dawn (slot 3) -> set 2
**Action Sets:**
- **Set 0:** Attack (25%), Electric Uppercut (25%), Prism Dawn (20%), Terrorize (30%)
- **Set 1:** Attack (10%), Electric Uppercut (10%), Heal (80%)
  - *Condition:* Heal (slot 2) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (25%), Electric Uppercut (25%), Poison (50%)

### Stage 3 (Lv 49)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Electric Uppercut | Single enemy | Lightning | 0.95x | - | 0.3 | Plain hit that deals damage; Stun (0.75) |
| Heal | Single ally | Neutral | 1.50x | 1.25s | - | Heal power (14) |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (300); Damage based on RES |
| Poison | All enemies | Water | 1.60x | 1.5s | - | Deals no damage; Poison |
| Terrorize | All enemies | Fire | 1.25x | 1.1s | - | Deals no damage; Stun |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 65 -> set 1
**Action Sets:**
- **Set 0:** Attack (25%), Electric Uppercut (25%), Prism Dawn (20%), Poison (15%), Terrorize (15%)
- **Set 1:** Attack (10%), Electric Uppercut (10%), Heal (80%)
  - *Condition:* Heal (slot 2) aims at: ally with the lowest HP ratio

### Stage 4 (Lv 57)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Lead Poison Club | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Hits twice; Poison (0.5) |
| Electric Uppercut | Single enemy | Lightning | 0.95x | - | 0.3 | Plain hit that deals damage; Stun (0.75) |
| Full Heal | Single ally | Neutral | 1.20x | 0.35s | - | - |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (300); Damage based on RES |
| Poison | All enemies | Water | 1.60x | 1.5s | - | Deals no damage; Poison |
| Terrorize | All enemies | Fire | 1.25x | 1.1s | - | Deals no damage; Stun |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 60 -> set 1
- last skill used is Full Heal (slot 3) -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Lead Poison Club (20%), Electric Uppercut (15%), Prism Dawn (15%), Poison (15%), Terrorize (15%)
- **Set 1:** Attack (10%), Lead Poison Club (10%), Electric Uppercut (10%), Full Heal (60%), Prism Dawn (10%)
  - *Condition:* Full Heal (slot 3) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (30%), Lead Poison Club (30%), Electric Uppercut (30%), Poison (5%), Terrorize (5%)

### Stage 5 (Lv 68)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Electric Uppercut | Single enemy | Lightning | 0.95x | - | 0.55 | Plain hit that deals damage; Stun (0.9) |
| Bloodbath | Single enemy | Weapon's | 1.20x | - | 0.4 | Plain hit that deals damage; Hits 2-4 times; Stun (0.5) |
| Full Heal | Single ally | Neutral | 1.30x | 0.5s | - | - |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (400); Damage based on RES |
| Poison | All enemies | Water | 1.60x | 1.5s | - | Deals no damage; Poison |
| Terrorize | All enemies | Fire | 1.25x | 1.1s | - | Deals no damage; Stun |
| Mini Circle Heal | Ally row | Neutral | 1.50x | 1s | - | Heal power (8) |

#### AI Behavior

**Opening Actions:**
- last skill used is Full Heal (slot 3) -> set 2 (stop)
- last skill used is Mini Circle Heal (slot 7) -> set 2 (stop)
- lowest HP ratio among allies <= 60 -> set 1 (stop)
- last skill used is Poison (slot 5) -> set 3 (stop)
- last skill used is Terrorize (slot 6) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Electric Uppercut (15%), Bloodbath (15%), Prism Dawn (25%), Poison (15%), Terrorize (20%)
- **Set 1:** Attack (5%), Bloodbath (5%), Full Heal (40%), Mini Circle Heal (50%)
  - *Condition:* Full Heal (slot 3) aims at: ally with the lowest HP ratio
  - *Condition:* Mini Circle Heal (slot 7) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Electric Uppercut (40%), Bloodbath (40%)
- **Set 3:** Attack (40%), Electric Uppercut (40%), Bloodbath (20%)

## Carol (Character 314)

- **Tavern Availability:** story: St10_0010/Main08_09.adv.bin (Main08_15_Start, chapter 8 before C30)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 37 | 1,200 Gold | 18 battles | 22 | 64 | 81 | 47 | 44 | 38 | 151 |
| 2 | 44 | 1,900 Gold | 20 battles | 31 | 73 | 119 | 56 | 53 | 43 | 172 |
| 3 | 53 | 3,200 Gold | 22 battles | 42 | 87 | 146 | 64 | 59 | 47 | 215 |
| 4 | 64 | 4,200 Gold | 24 battles | 57 | 101 | 201 | 82 | 65 | 54 | 376 |
| 5 | 91 | 7,200 Gold | 26 battles | 68 | 138 | 276 | 91 | 78 | 70 | 358 |

### Stage 1 (Lv 37)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | - | Plain hit that deals damage |
| Double Face Slap | Single enemy | Bash | 1.10x | - | 0.25 | Plain hit that deals damage; Chance to push the target back in the turn order (0.9) |
| Thunderbolt | Single enemy | Lightning | 2.00x | 1.65s | - | Magic power (240) |
| Thunder Chain | Enemy row | Lightning | 1.20x | 0.88s | - | Magic power (180) |
| Paralyze | All enemies | Lightning | 1.30x | 1s | - | Deals no damage; Paralysis |

#### AI Behavior

**Opening Actions:**
- last skill used is Thunderbolt (slot 2) -> set 1
- last skill used is Thunder Chain (slot 3) -> set 2
- last skill used is Paralyze (slot 4) -> set 3
**Action Sets:**
- **Set 0:** Attack (30%), Double Face Slap (30%), Thunder Chain (20%), Paralyze (20%)
- **Set 1:** Attack (25%), Double Face Slap (75%)
- **Set 2:** Attack (50%), Paralyze (50%)
- **Set 3:** Attack (75%), Thunderbolt (25%)

### Stage 2 (Lv 44)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | - | Plain hit that deals damage |
| Double Face Slap | Single enemy | Bash | 1.10x | - | 0.25 | Plain hit that deals damage; Chance to push the target back in the turn order (0.9) |
| Thunderbolt | Single enemy | Lightning | 2.00x | 1.65s | - | Magic power (240) |
| Ice Edge | Single enemy | Water | 1.50x | 1.05s | - | Magic power (240) |
| Thunder Chain | Enemy row | Lightning | 1.20x | 0.82s | - | Magic power (230) |
| Paralyze | All enemies | Lightning | 1.50x | 1.1s | - | Deals no damage; Paralysis |

#### AI Behavior

**Opening Actions:**
- last skill used is Paralyze (slot 5) -> set 1
- last skill used is Thunder Chain (slot 4) -> set 2
- last skill used is Attack (slot 0) -> set 3
**Action Sets:**
- **Set 0:** Attack (10%), Double Face Slap (10%), Thunderbolt (20%), Ice Edge (20%), Thunder Chain (20%), Paralyze (20%)
- **Set 1:** Thunderbolt (30%), Ice Edge (30%), Thunder Chain (40%)
- **Set 2:** Attack (50%), Double Face Slap (50%)
- **Set 3:** Double Face Slap (25%), Thunderbolt (25%), Ice Edge (25%), Thunder Chain (25%)

### Stage 3 (Lv 53)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | - | Plain hit that deals damage |
| Double Face Slap | Single enemy | Bash | 1.10x | - | 0.25 | Plain hit that deals damage; Chance to push the target back in the turn order (0.9) |
| Thunderbolt | Single enemy | Lightning | 2.00x | 1.65s | - | Magic power (240) |
| Ice Edge | Single enemy | Water | 1.50x | 1.05s | - | Magic power (325) |
| Thunder Chain | Enemy row | Lightning | 1.20x | 0.82s | - | Magic power (230) |
| Stone Shower | Enemy row | Earth | 1.20x | 0.82s | - | Magic power (230) |
| Paralyze | All enemies | Lightning | 1.50x | 1.1s | - | Deals no damage; Paralysis |

#### AI Behavior

**Opening Actions:**
- last skill used is Paralyze (slot 6) -> set 1
- last skill used is Attack (slot 0) -> set 2
- last skill used is Thunder Chain (slot 4) -> set 3
- last skill used is Stone Shower (slot 5) -> set 4
**Action Sets:**
- **Set 0:** Attack (15%), Double Face Slap (15%), Thunderbolt (15%), Ice Edge (15%), Thunder Chain (15%), Stone Shower (15%), Paralyze (10%)
- **Set 1:** Attack (20%), Double Face Slap (20%), Thunderbolt (30%), Ice Edge (30%)
- **Set 2:** Thunderbolt (20%), Ice Edge (20%), Thunder Chain (30%), Stone Shower (30%)
- **Set 3:** Attack (15%), Double Face Slap (20%), Thunderbolt (20%), Ice Edge (20%), Paralyze (25%)
- **Set 4:** Attack (15%), Double Face Slap (20%), Thunderbolt (20%), Ice Edge (20%), Paralyze (25%)

### Stage 4 (Lv 64)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | 0.15 | Plain hit that deals damage |
| Thunder Chain | Enemy row | Lightning | 1.20x | 0.78s | - | Magic power (280) |
| Muon Plasma | Single enemy | Lightning | 1.30x | 1.1s | - | Magic power (450) |
| Ice Edge | Single enemy | Water | 1.50x | 1.05s | - | Magic power (325) |
| Gaia Crush | Single enemy | Earth | 1.40x | 0.95s | - | Magic power (400) |
| Tornado | All enemies | Wind | 1.50x | 1.15s | - | Magic power (180) |
| Paralyze | All enemies | Lightning | 1.75x | 1.2s | - | Deals no damage; Paralysis |

#### AI Behavior

**Opening Actions:**
- last skill used is Muon Plasma (slot 2) -> set 1
- last skill used is Gaia Crush (slot 4) -> set 1
- last skill used is Paralyze (slot 6) -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Thunder Chain (15%), Muon Plasma (15%), Ice Edge (15%), Gaia Crush (10%), Tornado (15%), Paralyze (10%)
- **Set 1:** Attack (75%), Paralyze (25%)
- **Set 2:** Attack (60%), Thunder Chain (20%), Tornado (20%)

### Stage 5 (Lv 91)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Fire | 1.00x | - | 0.3 | Plain hit that deals damage |
| Energy Ball | Single enemy | Neutral | 0.90x | - | - | Magic power (650) |
| Muon Plasma | Single enemy | Lightning | 1.40x | 1.05s | - | Magic power (1000) |
| Lightning | All enemies | Lightning | 1.00x | 0.71s | - | Magic power (520) |
| Diamond Dust | All enemies | Water | 1.00x | 0.71s | - | Magic power (520) |
| Gaia Crush | Single enemy | Earth | 1.40x | 1.05s | - | Magic power (1000) |
| Tornado | All enemies | Wind | 1.00x | 0.71s | - | Magic power (520) |
| Paralyze | All enemies | Lightning | 1.75x | 1.2s | - | Deals no damage; Paralysis |
| Loose Spirit | Self | Neutral | 1.25x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Muon Plasma (slot 2) -> set 2 (stop)
- last skill used is Gaia Crush (slot 5) -> set 2 (stop)
- Loose Spirit (slot 8) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Energy Ball (20%), Lightning (10%), Diamond Dust (10%), Tornado (10%), Loose Spirit (40%)
- **Set 1:** Muon Plasma (20%), Lightning (20%), Diamond Dust (20%), Gaia Crush (20%), Tornado (20%)
- **Set 2:** Energy Ball (50%), Paralyze (50%)

## Sasha (Character 315)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main10_00_Start, start of chapter 10 after C34)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 47 | 2,300 Gold | 18 battles | 13 | 84 | 94 | 128 | 61 | 43 | 172 |
| 2 | 55 | 3,500 Gold | 20 battles | 27 | 106 | 113 | 153 | 66 | 51 | 220 |
| 3 | 66 | 4,400 Gold | 22 battles | 53 | 124 | 140 | 181 | 74 | 63 | 384 |
| 4 | 79 | 5,300 Gold | 24 battles | 72 | 155 | 177 | 233 | 85 | 72 | 318 |
| 5 | 88 | 6,200 Gold | 26 battles | 87 | 183 | 213 | 286 | 97 | 88 | 1419 |

### Stage 1 (Lv 47)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Bible Thump | Single enemy | Bash | 0.85x | - | 0.4 | Plain hit that deals damage; Damage based on RES; Freeze (0.2); Silence (0.2) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Sleep | All enemies | Wind | 1.10x | 1s | - | Deals no damage; Sleep |
| Rainbow Flash | Enemy row | Neutral | 1.25x | 0.85s | - | Magic power (260) |
| Nurse | Single ally | Neutral | 1.15x | 1s | - | How many ailments of the listed order it cures (8) |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 4 (stop)
- last skill used is Sun Veil (slot 2) -> set 1
- last skill used is Attack (slot 0) -> set 2
- last skill used is Rainbow Flash (slot 4) -> set 3
**Action Sets:**
- **Set 0:** Attack (30%), Bible Thump (20%), Sun Veil (20%), Sleep (20%), Rainbow Flash (10%)
- **Set 1:** Attack (50%), Bible Thump (50%)
- **Set 2:** Bible Thump (30%), Rainbow Flash (70%)
- **Set 3:** Attack (20%), Bible Thump (80%)
- **Set 4:** Nurse (100%)
  - *Condition:* Nurse (slot 5) aims at: ally with a more serious ailment

### Stage 2 (Lv 55)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Bible Thump | Single enemy | Bash | 1.00x | - | 0.8 | Plain hit that deals damage; Damage based on RES; Freeze (0.35); Silence (0.35) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Sleep | All enemies | Wind | 1.35x | 1.1s | - | Deals no damage; Sleep |
| Rainbow Flash | Enemy row | Neutral | 1.25x | 0.85s | - | Magic power (260) |
| Tempest | Single enemy | Wind | 1.00x | 0.85s | - | Magic power (320) |
| Nurse | Single ally | Neutral | 1.15x | 1s | - | How many ailments of the listed order it cures (8) |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 1 (stop)
- last skill used is Sleep (slot 3) -> set 3 (stop)
- last skill used is Rainbow Flash (slot 4) -> set 4 (stop)
- last skill used is Tempest (slot 5) -> set 5 (stop)
- last skill used is Sun Veil (slot 2) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (25%), Bible Thump (25%), Sun Veil (15%), Sleep (15%), Rainbow Flash (10%), Tempest (10%)
- **Set 1:** Attack (10%), Bible Thump (10%), Nurse (80%)
  - *Condition:* Nurse (slot 6) aims at: ally with a more serious ailment
- **Set 2:** Attack (20%), Bible Thump (20%), Sleep (20%), Rainbow Flash (20%), Tempest (20%)
- **Set 3:** Attack (25%), Bible Thump (75%)
- **Set 4:** Attack (50%), Bible Thump (50%)
- **Set 5:** Attack (75%), Bible Thump (25%)

### Stage 3 (Lv 66)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Bible Thump | Single enemy | Bash | 1.00x | - | 0.8 | Plain hit that deals damage; Damage based on RES; Freeze (0.35); Silence (0.35) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Sleep | All enemies | Wind | 1.35x | 1.1s | - | Deals no damage; Sleep |
| Rainbow Flash | Enemy row | Neutral | 1.25x | 0.85s | - | Magic power (325) |
| Tempest | Single enemy | Wind | 1.50x | 1.1s | - | Magic power (450) |
| Mini Circle Nurse | Ally row | Neutral | 1.00x | 0.5s | - | How many ailments of the listed order it cures (8) |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 3 (stop)
- last skill used is Sun Veil (slot 2) -> set 1 (stop)
- last skill used is Sleep (slot 3) -> set 2 (stop)
- last skill used is Rainbow Flash (slot 4) -> set 2 (stop)
- last skill used is Tempest (slot 5) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (30%), Bible Thump (20%), Sun Veil (15%), Sleep (10%), Rainbow Flash (15%), Tempest (10%)
- **Set 1:** Attack (30%), Bible Thump (20%), Rainbow Flash (25%), Tempest (25%)
- **Set 2:** Attack (80%), Bible Thump (20%)
- **Set 3:** Attack (10%), Bible Thump (10%), Tempest (10%), Mini Circle Nurse (70%)
  - *Condition:* Mini Circle Nurse (slot 6) aims at: ally with a more serious ailment

### Stage 4 (Lv 79)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.2) |
| Bible Thump | Single enemy | Bash | 1.00x | - | 0.8 | Plain hit that deals damage; Damage based on RES; Freeze (0.35); Silence (0.35) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Sleep | All enemies | Wind | 1.35x | 1.1s | - | Deals no damage; Sleep |
| Rainbow Flash | Enemy row | Neutral | 1.35x | 0.8s | - | Magic power (480) |
| Tempest | Single enemy | Wind | 1.40x | 1.1s | - | Magic power (800) |
| Stab Smash | Single enemy | Bash | 1.00x | - | 0.35 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.45) |
| Mini Circle Nurse | Ally row | Neutral | 1.00x | 0.6s | - | How many ailments of the listed order it cures (8) |

#### AI Behavior

**Opening Actions:**
- an ally has an ailment -> set 1 (stop)
- last skill used is Sun Veil (slot 2) -> set 2 (stop)
- last skill used is Sleep (slot 3) -> set 3 (stop)
- last skill used is Rainbow Flash (slot 4) -> set 3 (stop)
- last skill used is Tempest (slot 5) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Bible Thump (20%), Sun Veil (15%), Sleep (10%), Rainbow Flash (15%), Tempest (10%), Stab Smash (15%)
- **Set 1:** Attack (10%), Bible Thump (10%), Tempest (10%), Mini Circle Nurse (70%)
  - *Condition:* Mini Circle Nurse (slot 7) aims at: ally with the heaviest ailment
- **Set 2:** Attack (15%), Bible Thump (20%), Rainbow Flash (25%), Tempest (25%), Stab Smash (15%)
- **Set 3:** Attack (20%), Bible Thump (40%), Stab Smash (40%)

### Stage 5 (Lv 88)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.6) |
| Bible Thump | Single enemy | Bash | 1.00x | - | 0.8 | Plain hit that deals damage; Damage based on RES; Freeze (0.35); Silence (0.35) |
| Sun Veil | All allies | Neutral | 1.50x | 1s | - | Magic defense modifier (0.15) |
| Sleep | All enemies | Wind | 1.60x | 1.2s | - | Deals no damage; Sleep |
| Rainbow Flash | Enemy row | Neutral | 1.45x | 0.75s | - | Magic power (600) |
| Tempest | Single enemy | Wind | 1.40x | 1.05s | - | Magic power (1000) |
| Stab Smash | Single enemy | Bash | 1.00x | - | 0.35 | Plain hit that deals damage; More damage to targets with buffs or debuffs (0.45) |
| Circle Nurse | All allies | Neutral | 1.00x | 0.85s | - | How many ailments of the listed order it cures (8) |

#### AI Behavior

**Opening Actions:**
- last skill used is Circle Nurse (slot 7) -> set 4 (stop)
- an ally has an ailment -> set 1 (stop)
- last skill used is Sun Veil (slot 2) -> set 2 (stop)
- last skill used is Sleep (slot 3) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Bible Thump (20%), Sun Veil (10%), Sleep (10%), Rainbow Flash (20%), Tempest (20%), Stab Smash (10%)
- **Set 1:** Rainbow Flash (10%), Tempest (10%), Stab Smash (10%), Circle Nurse (70%)
  - *Condition:* Circle Nurse (slot 7) aims at: ally with the heaviest ailment
- **Set 2:** Bible Thump (25%), Rainbow Flash (25%), Tempest (25%), Stab Smash (25%)
  - *Condition:* Stab Smash (slot 6) aims at: opponent with a buff
- **Set 3:** Tempest (50%), Stab Smash (50%)
  - *Condition:* Stab Smash (slot 6) aims at: opponent with a buff
- **Set 4:** Bible Thump (35%), Rainbow Flash (35%), Tempest (15%), Stab Smash (15%)

## Priscilla (Character 316)

- **Tavern Availability:** story: St12_0010/St12_a0130.adv.bin (after battle 42 Death Cataphract, C33)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 39 | 1,400 Gold | 24 battles | 94 | 73 | 51 | 59 | 49 | 41 | 320 |
| 2 | 51 | 2,500 Gold | 25 battles | 138 | 94 | 72 | 75 | 57 | 48 | 211 |
| 3 | 60 | 3,100 Gold | 26 battles | 159 | 122 | 88 | 92 | 68 | 57 | 370 |
| 4 | 69 | 4,200 Gold | 27 battles | 193 | 147 | 107 | 109 | 76 | 66 | 400 |
| 5 | 78 | 5,000 Gold | 28 battles | 232 | 173 | 139 | 143 | 84 | 75 | 418 |

### Stage 1 (Lv 39)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Dust Up | Self | Neutral | 1.00x | - | - | ATK modifier (0.2); Speed modifier (0.2) |
| First Aid | Single ally | Neutral | 0.70x | - | - | Heal power (5) |
| Carry Me! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Slow (0.75) |
| Throwing Stone | Single enemy | Earth | 1.00x | - | - | Magic power (200) |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 60 -> set 1 (stop)
- Dust Up (slot 1) was used 1 times or more -> set 2
**Action Sets:**
- **Set 0:** Attack (30%), Dust Up (20%), Carry Me! (20%), Throwing Stone (30%)
- **Set 1:** Attack (10%), First Aid (80%), Throwing Stone (10%)
  - *Condition:* First Aid (slot 2) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (40%), Carry Me! (30%), Throwing Stone (30%)

### Stage 2 (Lv 51)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Dust Up | Self | Neutral | 1.00x | - | - | ATK modifier (0.2); Speed modifier (0.2) |
| First Aid | Single ally | Neutral | 0.80x | - | - | Heal power (8) |
| Carry Me! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Slow (0.75) |
| Throwing Stone | Single enemy | Earth | 1.00x | - | - | Magic power (200) |
| Holy Gavel | Single enemy | Bash | 0.80x | - | -0.5 | Plain hit that deals damage; Damage multiplier (2.4) |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 70 -> set 1 (stop)
- Dust Up (slot 1) was used 1 times or more -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Dust Up (20%), Carry Me! (20%), Throwing Stone (20%), Holy Gavel (20%)
- **Set 1:** Attack (10%), First Aid (80%), Holy Gavel (10%)
  - *Condition:* First Aid (slot 2) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (30%), Carry Me! (25%), Throwing Stone (25%), Holy Gavel (20%)

### Stage 3 (Lv 60)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Dust Up | Self | Neutral | 1.00x | - | - | ATK modifier (0.2); Speed modifier (0.2) |
| First Aid | Single ally | Neutral | 0.90x | - | - | Heal power (12) |
| Carry Me! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Slow (0.75) |
| Boulder Toss | Single enemy | Earth | 0.85x | - | - | Magic power (275) |
| Holy Gavel | Single enemy | Bash | 0.85x | - | -0.3 | Plain hit that deals damage; Damage multiplier (3.2) |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 70 -> set 1 (stop)
- Dust Up (slot 1) was used 1 times or more -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Dust Up (20%), Carry Me! (20%), Boulder Toss (20%), Holy Gavel (20%)
- **Set 1:** Attack (15%), First Aid (70%), Holy Gavel (15%)
  - *Condition:* First Aid (slot 2) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (30%), Carry Me! (25%), Boulder Toss (25%), Holy Gavel (20%)

### Stage 4 (Lv 69)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Dust Up | Self | Neutral | 1.00x | - | - | ATK modifier (0.25); Speed modifier (0.2) |
| First Aid | Single ally | Neutral | 0.90x | - | - | Heal power (12) |
| Carry Me! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Slow (0.75) |
| Boulder Toss | Single enemy | Earth | 0.85x | - | - | Magic power (275) |
| Holy Gavel | Single enemy | Bash | 0.85x | - | -0.3 | Plain hit that deals damage; Damage multiplier (3.2) |
| Broom Attack | Enemy row | Bash | 0.90x | - | 2 | Plain hit that deals damage; Damage change for each later target or hit (-0.1) |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 70 -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Dust Up (20%), Carry Me! (20%), Boulder Toss (20%), Holy Gavel (20%)
  - *Condition:* Dust Up (slot 1) was used 1 times or more -> Broom Attack (slot 6)
- **Set 1:** Attack (10%), First Aid (70%), Broom Attack (20%)
  - *Condition:* First Aid (slot 2) aims at: ally with the lowest HP ratio

### Stage 5 (Lv 78)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Dust Up | Self | Neutral | 1.00x | - | - | ATK modifier (0.25); Speed modifier (0.2) |
| First Aid | Single ally | Neutral | 1.00x | - | - | Heal power (16) |
| Carry Me! | Single enemy | Bash | 1.00x | - | 0.5 | Plain hit that deals damage; Slow (0.75) |
| Boulder Toss | Single enemy | Earth | 0.90x | - | - | Magic power (400) |
| Holy Gavel | Single enemy | Bash | 0.90x | - | -0.2 | Plain hit that deals damage; Damage multiplier (3.8) |
| Broom Attack | Enemy row | Bash | 0.95x | - | 3 | Plain hit that deals damage; Damage change for each later target or hit (-0.05) |
| Last Order Time! | Single enemy | Neutral | 0.80x | - | - | Magic power (625); Petrification (0.5) |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 70 -> set 1 (stop)
- last skill used is Attack (slot 0) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Dust Up (20%), Carry Me! (20%), Boulder Toss (20%), Holy Gavel (20%)
  - *Condition:* Dust Up (slot 1) was used 1 times or more -> Broom Attack (slot 6)
- **Set 1:** Attack (10%), First Aid (70%), Holy Gavel (10%), Broom Attack (10%)
  - *Condition:* First Aid (slot 2) aims at: ally with the lowest HP ratio
- **Set 2:** Carry Me! (15%), Boulder Toss (20%), Holy Gavel (15%), Last Order Time! (50%)

## Neya (Character 317)

- **Tavern Availability:** story: St13_0140/Main10_25.adv.bin (Dreamscape 14F, after C35 on 14F, before C36 on 15F)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 50 | 3,000 Gold | 20 battles | 164 | 134 | 40 | 43 | 77 | 67 | 197 |
| 2 | 57 | 3,800 Gold | 21 battles | 201 | 148 | 53 | 60 | 84 | 76 | 224 |
| 3 | 69 | 4,900 Gold | 22 battles | 241 | 167 | 66 | 76 | 116 | 89 | 385 |
| 4 | 80 | 5,500 Gold | 23 battles | 298 | 202 | 75 | 84 | 138 | 106 | 318 |
| 5 | 89 | 7,000 Gold | 24 battles | 351 | 231 | 87 | 106 | 153 | 121 | 334 |

### Stage 1 (Lv 50)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Cinnabar Palm | Single enemy | Stab | 0.80x | - | - | Plain hit that deals damage; Instant death (0.2) |
| Silence Sting | Single enemy | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; Silence (0.8) |
| Fire Scroll | All enemies | Fire | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); ATK modifier (-0.06); Damage cap (200) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Fire Scroll (slot 3) -> set 2
- lowest TP ratio among allies <= 50 -> set 1
**Action Sets:**
- **Set 0:** Attack (35%), Cinnabar Palm (20%), Silence Sting (20%), Fire Scroll (25%)
- **Set 1:** Attack (25%), Cook (75%)
  - *Condition:* Cook (slot 4) aims at: ally with the lowest TP ratio
- **Set 2:** Attack (60%), Cinnabar Palm (20%), Silence Sting (20%)

### Stage 2 (Lv 57)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Cinnabar Palm | Single enemy | Stab | 0.80x | - | - | Plain hit that deals damage; Instant death (0.2) |
| Silence Sting | Single enemy | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; Silence (0.8) |
| Fire Scroll | All enemies | Fire | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); ATK modifier (-0.06); Damage cap (200) |
| Wind Scroll | All enemies | Wind | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); Physical evasion modifier (-0.06); Damage cap (200) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |
| Military Rations Pill | Single ally | Neutral | 0.60x | - | - | Heal power (3); How many ailments of the listed order it cures (2) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Fire Scroll (slot 3) -> set 1
- last skill used is Wind Scroll (slot 4) -> set 2
- lowest TP ratio among allies <= 50 -> set 3
- lowest HP ratio among allies <= 75 -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), Cinnabar Palm (20%), Silence Sting (20%), Fire Scroll (20%), Wind Scroll (20%)
- **Set 1:** Attack (50%), Cinnabar Palm (25%), Silence Sting (25%)
- **Set 2:** Attack (50%), Cinnabar Palm (25%), Silence Sting (25%)
- **Set 3:** Attack (20%), Cook (80%)
  - *Condition:* Cook (slot 5) aims at: ally with the lowest TP ratio
- **Set 4:** Attack (20%), Military Rations Pill (80%)
  - *Condition:* Military Rations Pill (slot 6) aims at: ally with the lowest HP ratio

### Stage 3 (Lv 69)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Poison (0.1) |
| Cinnabar Palm | Single enemy | Stab | 0.80x | - | - | Plain hit that deals damage; Instant death (0.2) |
| Silence Sting | Single enemy | Stab | 1.00x | - | 0.25 | Plain hit that deals damage; Silence (0.8) |
| Fire Scroll | All enemies | Fire | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); ATK modifier (-0.09); Damage cap (300) |
| Wind Scroll | All enemies | Wind | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Physical evasion modifier (-0.09); Damage cap (300) |
| (Secret Technique) Bra Unhooker | Single enemy | Neutral | 0.85x | - | 0.15 | Plain hit that deals damage; DEF modifier (-0.08); Magic defense modifier (-0.08) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |
| Military Rations Pill | Single ally | Neutral | 0.60x | - | - | Heal power (6); How many ailments of the listed order it cures (2) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 50 -> set 1 (stop)
- lowest TP ratio among allies <= 50 -> set 2 (stop)
- last skill used is Fire Scroll (slot 3) -> set 3 (stop)
- last skill used is Wind Scroll (slot 4) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (30%), Cinnabar Palm (15%), Silence Sting (15%), Fire Scroll (15%), Wind Scroll (15%), (Secret Technique) Bra Unhooker (10%)
- **Set 1:** Attack (20%), (Secret Technique) Bra Unhooker (20%), Military Rations Pill (60%)
  - *Condition:* Military Rations Pill (slot 7) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Silence Sting (20%), Cook (60%)
  - *Condition:* Cook (slot 6) aims at: ally with the lowest TP ratio
- **Set 3:** Attack (60%), Cinnabar Palm (20%), Silence Sting (20%)

### Stage 4 (Lv 80)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage; Poison (0.3) |
| Cinnabar Palm | Single enemy | Stab | 1.00x | - | 0.15 | Plain hit that deals damage; Instant death (0.2) |
| Silence Sting | Single enemy | Stab | 1.00x | - | 0.5 | Plain hit that deals damage; Silence (0.8) |
| Fire Scroll | All enemies | Fire | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); ATK modifier (-0.09); Damage cap (300) |
| Wind Scroll | All enemies | Wind | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Physical evasion modifier (-0.09); Damage cap (300) |
| (Secret Technique) Bra Unhooker | Single enemy | Neutral | 0.85x | - | 0.3 | Plain hit that deals damage; DEF modifier (-0.08); Magic defense modifier (-0.08) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |
| Military Rations Pill | Single ally | Neutral | 0.60x | - | - | Heal power (6); How many ailments of the listed order it cures (2) |
| Lightning Scroll | All enemies | Lightning | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Speed modifier (-0.09); Damage cap (300) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 50 -> set 1 (stop)
- lowest TP ratio among allies <= 50 -> set 2 (stop)
- last skill used is Fire Scroll (slot 3) -> set 3 (stop)
- last skill used is Wind Scroll (slot 4) -> set 3 (stop)
- last skill used is Lightning Scroll (slot 8) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Cinnabar Palm (15%), Silence Sting (15%), Fire Scroll (15%), Wind Scroll (15%), (Secret Technique) Bra Unhooker (10%), Lightning Scroll (15%)
- **Set 1:** Attack (20%), (Secret Technique) Bra Unhooker (20%), Military Rations Pill (60%)
  - *Condition:* Military Rations Pill (slot 7) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Silence Sting (20%), Cook (60%)
  - *Condition:* Cook (slot 6) aims at: ally with the lowest TP ratio
- **Set 3:** Attack (60%), Cinnabar Palm (20%), Silence Sting (20%)

### Stage 5 (Lv 89)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | 0.35 | Plain hit that deals damage; Poison (0.5) |
| Cinnabar Palm | Single enemy | Stab | 1.10x | - | 0.3 | Plain hit that deals damage; Instant death (0.35) |
| Silence Sting | Single enemy | Stab | 1.00x | - | 0.5 | Plain hit that deals damage; Silence (0.8) |
| Fire Scroll | All enemies | Fire | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); ATK modifier (-0.09); Damage cap (300) |
| Wind Scroll | All enemies | Wind | 1.40x | 1.65s | - | Magic power; Damage as a fraction of the target max HP (0.4); Physical evasion modifier (-0.12); Damage cap (400) |
| (Secret Technique) Bra Unhooker | Single enemy | Neutral | 0.85x | - | 0.3 | Plain hit that deals damage; DEF modifier (-0.08); Magic defense modifier (-0.08) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |
| Military Rations Pill | Single ally | Neutral | 0.60x | - | - | Heal power (9); How many ailments of the listed order it cures (2) |
| Lightning Scroll | All enemies | Lightning | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Speed modifier (-0.09); Damage cap (300) |
| Ultimate Maid Frenzy | Random enemies | Neutral | 0.50x | - | 0.5 | Plain hit that deals damage; Hits 3-5 times; Chance to push the target back in the turn order (0.5) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 70 -> set 1 (stop)
- lowest TP ratio among allies <= 60 -> set 2 (stop)
- last skill used is Fire Scroll (slot 3) -> set 3 (stop)
- last skill used is Wind Scroll (slot 4) -> set 3 (stop)
- last skill used is (Secret Technique) Bra Unhooker (slot 5) -> set 3 (stop)
- last skill used is Lightning Scroll (slot 8) -> set 3 (stop)
- last skill used is Ultimate Maid Frenzy (slot 9) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Cinnabar Palm (15%), Fire Scroll (15%), Wind Scroll (15%), (Secret Technique) Bra Unhooker (15%), Lightning Scroll (15%), Ultimate Maid Frenzy (10%)
- **Set 1:** Silence Sting (15%), Military Rations Pill (65%), Ultimate Maid Frenzy (20%)
  - *Condition:* Military Rations Pill (slot 7) aims at: ally with the lowest HP ratio
- **Set 2:** Silence Sting (15%), Cook (65%), Ultimate Maid Frenzy (20%)
  - *Condition:* Cook (slot 6) aims at: ally with the lowest TP ratio
- **Set 3:** Attack (25%), Silence Sting (75%)

## Estelle (Character 318)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main07_20_Start, chapter 7, the Tavern opens after C24)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 30 | 500 Gold | 20 battles | 68 | 54 | 28 | 31 | 35 | 26 | 135 |
| 2 | 41 | 1,100 Gold | 20 battles | 89 | 85 | 53 | 49 | 48 | 37 | 319 |
| 3 | 50 | 2,400 Gold | 22 battles | 106 | 112 | 61 | 67 | 63 | 50 | 353 |
| 4 | 58 | 3,500 Gold | 22 battles | 133 | 134 | 76 | 83 | 75 | 56 | 230 |
| 5 | 70 | 4,700 Gold | 25 battles | 168 | 155 | 88 | 94 | 82 | 64 | 402 |

### Stage 1 (Lv 30)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Wind Fang | Single enemy | Wind | 0.90x | - | - | Magic power (80) |
| Gravitating Polka | All enemies | Neutral | 0.75x | - | - | - |
| Sacred Hymn | All allies | Neutral | 1.50x | 1.25s | - | - |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### AI Behavior

**Opening Actions:**
- turns taken + 1 <= 1 -> set 1 (stop)
- last skill used is Wait and See (slot 4) -> set 2
**Action Sets:**
- **Set 0:** Attack (60%), Wind Fang (20%), Wait and See (20%)
- **Set 1:** Wind Fang (20%), Gravitating Polka (40%), Sacred Hymn (40%)
- **Set 2:** Attack (20%), Wind Fang (20%), Gravitating Polka (30%), Sacred Hymn (30%)

### Stage 2 (Lv 41)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Wind Fang | Single enemy | Wind | 0.90x | - | - | Magic power (200) |
| Spiritual Fantasia | All allies | Neutral | 1.50x | 1.4s | - | - |
| Reading Requiem | All allies | Neutral | 1.50x | 1.25s | - | - |
| Gravitating Polka | All enemies | Neutral | 0.75x | - | - | - |
| Sacred Hymn | All allies | Neutral | 1.50x | 1.25s | - | - |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### AI Behavior

**Opening Actions:**
- turns taken + 1 <= 1 -> set 1 (stop)
- last skill used is Wind Fang (slot 1) -> set 2
**Action Sets:**
- **Set 0:** Attack (50%), Wind Fang (30%), Wait and See (20%)
- **Set 1:** Attack (20%), Spiritual Fantasia (20%), Reading Requiem (20%), Gravitating Polka (20%), Sacred Hymn (20%)
- **Set 2:** Attack (80%), Wait and See (20%)

### Stage 3 (Lv 50)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Wind Fang | Single enemy | Wind | 0.90x | - | - | Magic power (200) |
| Spiritual Fantasia | All allies | Neutral | 1.50x | 1.4s | - | - |
| Reading Requiem | All allies | Neutral | 1.50x | 1.4s | - | - |
| Sacred Hymn | All allies | Neutral | 1.50x | 1.25s | - | - |
| Gravitating Polka | All enemies | Neutral | 0.75x | - | - | - |
| Gloomy Tango | All enemies | Neutral | 0.75x | - | - | - |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### AI Behavior

**Opening Actions:**
- turns taken + 1 <= 1 -> set 1 (stop)
- Gravitating Polka (slot 5) is active -> set 2 (stop)
- Gloomy Tango (slot 6) is active -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (30%), Wind Fang (25%), Spiritual Fantasia (5%), Reading Requiem (5%), Sacred Hymn (5%), Gravitating Polka (15%), Gloomy Tango (15%)
- **Set 1:** Attack (40%), Spiritual Fantasia (20%), Reading Requiem (20%), Sacred Hymn (20%)
- **Set 2:** Attack (50%), Wind Fang (20%), Gloomy Tango (10%), Wait and See (20%)
- **Set 3:** Attack (50%), Wind Fang (20%), Gravitating Polka (10%), Wait and See (20%)

### Stage 4 (Lv 58)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Silence (0.2) |
| Wind Fang | Single enemy | Wind | 0.95x | - | - | Magic power (400) |
| String Serenade | Single enemy | Neutral | 0.80x | - | - | Magic power (250); Sleep (0.15) |
| Spiritual Fantasia | All allies | Neutral | 1.50x | 1.4s | - | - |
| Reading Requiem | All allies | Neutral | 1.50x | 1.4s | - | - |
| Sacred Hymn | All allies | Neutral | 1.50x | 1.25s | - | - |
| Barrage Rondo | All allies | Neutral | 1.35x | 1s | - | - |
| Gloomy Tango | All enemies | Neutral | 0.75x | - | - | - |
| Gravitating Polka | All enemies | Neutral | 0.75x | - | - | - |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### AI Behavior

**Opening Actions:**
- turns taken + 1 <= 1 -> set 1 (stop)
- last skill used is Spiritual Fantasia (slot 3) -> set 2
- last skill used is Reading Requiem (slot 4) -> set 3
- last skill used is Sacred Hymn (slot 5) -> set 4
- last skill used is Barrage Rondo (slot 6) -> set 5
- last skill used is Gloomy Tango (slot 7) -> set 6
- last skill used is Gravitating Polka (slot 8) -> set 7
**Action Sets:**
- **Set 0:** Attack (10%), Wind Fang (10%), String Serenade (10%), Spiritual Fantasia (10%), Reading Requiem (10%), Sacred Hymn (10%), Barrage Rondo (10%), Gloomy Tango (10%), Gravitating Polka (10%), Wait and See (10%)
- **Set 1:** Attack (20%), Barrage Rondo (40%), Gravitating Polka (40%)
- **Set 2:** Attack (40%), Wind Fang (15%), String Serenade (15%), Wait and See (30%)
- **Set 3:** Attack (40%), Wind Fang (15%), String Serenade (15%), Wait and See (30%)
- **Set 4:** Attack (40%), Wind Fang (15%), String Serenade (15%), Wait and See (30%)
- **Set 5:** Attack (40%), Wind Fang (15%), String Serenade (15%), Wait and See (30%)
- **Set 6:** Attack (40%), Wind Fang (15%), String Serenade (15%), Wait and See (30%)
- **Set 7:** Attack (40%), Wind Fang (15%), String Serenade (15%), Wait and See (30%)

### Stage 5 (Lv 70)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Silence (0.2) |
| Wind Fang | Single enemy | Wind | 0.95x | - | - | Magic power (400) |
| String Serenade | Single enemy | Neutral | 0.85x | - | - | Magic power (350); Sleep (0.2) |
| Spiritual Fantasia | All allies | Neutral | 1.50x | 1.4s | - | - |
| Reading Requiem | All allies | Neutral | 1.50x | 1.4s | - | - |
| Sacred Hymn | All allies | Neutral | 1.50x | 1.25s | - | - |
| Replenishing Carol | All allies | Neutral | 1.50x | 1.5s | - | - |
| Barrage Rondo | All allies | Neutral | 1.35x | 1s | - | - |
| Gravitating Polka | All enemies | Neutral | 0.75x | - | - | - |
| Gloomy Tango | All enemies | Neutral | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- turns taken + 1 <= 1 -> set 1 (stop)
- last skill used is Spiritual Fantasia (slot 3) -> set 2 (stop)
- last skill used is Reading Requiem (slot 4) -> set 2 (stop)
- last skill used is Sacred Hymn (slot 5) -> set 2 (stop)
- last skill used is Replenishing Carol (slot 6) -> set 2 (stop)
- last skill used is Barrage Rondo (slot 7) -> set 2 (stop)
- last skill used is Gravitating Polka (slot 8) -> set 2 (stop)
- last skill used is Gloomy Tango (slot 9) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Wind Fang (10%), String Serenade (10%), Spiritual Fantasia (10%), Reading Requiem (10%), Sacred Hymn (10%), Replenishing Carol (10%), Barrage Rondo (10%), Gravitating Polka (10%), Gloomy Tango (10%)
- **Set 1:** Attack (20%), Spiritual Fantasia (20%), Barrage Rondo (20%), Gravitating Polka (20%), Gloomy Tango (20%)
- **Set 2:** Attack (50%), Wind Fang (25%), String Serenade (25%)

## Rebecca (Character 319)

- **Tavern Availability:** story: St12_0010/St12_a0130.adv.bin (after battle 42 Death Cataphract, C33)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 43 | 2,100 Gold | 22 battles | 140 | 102 | 31 | 36 | 72 | 56 | 320 |
| 2 | 53 | 2,800 Gold | 23 battles | 170 | 130 | 53 | 55 | 89 | 69 | 211 |
| 3 | 62 | 3,800 Gold | 24 battles | 191 | 164 | 62 | 67 | 112 | 80 | 370 |
| 4 | 71 | 4,700 Gold | 25 battles | 244 | 188 | 74 | 86 | 131 | 94 | 400 |
| 5 | 82 | 5,600 Gold | 26 battles | 308 | 212 | 86 | 95 | 153 | 107 | 1419 |

### Stage 1 (Lv 43)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Gold Steal | Single enemy | Neutral | 0.80x | - | - | - |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Paralysis (0.4) |
| Sharp Stab | Single enemy | Stab | 0.90x | - | -0.05 | Plain hit that deals damage; Fixed critical hit rate |
| Hard Whipping | Enemy row | Bash | 0.80x | - | - | Plain hit that deals damage; Fixed critical hit rate (0.25); Damage change for each later target or hit (-0.15) |

#### AI Behavior

**Action Sets:**
- **Set 0:** Attack (5%), Gold Steal (25%), Got Your Heart! (25%), Sharp Stab (25%), Hard Whipping (20%)
  - *Condition:* Gold Steal (slot 1) was used 1 times or more -> Attack (slot 0)

### Stage 2 (Lv 53)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Poison (0.1) |
| Gold Steal | Single enemy | Neutral | 0.80x | - | - | - |
| Item Steal | Single enemy | Neutral | 0.30x | - | - | - |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Paralysis (0.4) |
| Sharp Stab | Single enemy | Stab | 0.90x | - | -0.05 | Plain hit that deals damage; Fixed critical hit rate |
| Hard Whipping | Enemy row | Bash | 0.90x | - | 0.25 | Plain hit that deals damage; Fixed critical hit rate (0.35); Damage change for each later target or hit (-0.1) |

#### AI Behavior

**Opening Actions:**
- last skill used is Hard Whipping (slot 5) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Gold Steal (20%), Item Steal (20%), Got Your Heart! (20%), Sharp Stab (20%), Hard Whipping (10%)
  - *Condition:* Gold Steal (slot 1) was used 1 times or more -> Attack (slot 0)
  - *Condition:* Item Steal (slot 2) was used 1 times or more -> Hard Whipping (slot 5)
- **Set 1:** Attack (80%), Got Your Heart! (10%), Sharp Stab (10%)

### Stage 3 (Lv 62)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Poison (0.1) |
| Gold Steal | Single enemy | Neutral | 0.80x | - | - | - |
| Item Steal | Single enemy | Neutral | 0.35x | - | - | - |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Paralysis (0.4) |
| Sharp Stab | Single enemy | Stab | 0.90x | - | - | Plain hit that deals damage; Fixed critical hit rate |
| Hard Whipping | Enemy row | Bash | 0.90x | - | 0.25 | Plain hit that deals damage; Fixed critical hit rate (0.35); Damage change for each later target or hit (-0.1) |

#### AI Behavior

**Opening Actions:**
- last skill used is Hard Whipping (slot 5) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Gold Steal (20%), Item Steal (20%), Got Your Heart! (20%), Sharp Stab (20%), Hard Whipping (10%)
  - *Condition:* Gold Steal (slot 1) was used 1 times or more -> Attack (slot 0)
  - *Condition:* Item Steal (slot 2) was used 1 times or more -> Hard Whipping (slot 5)
- **Set 1:** Attack (50%), Got Your Heart! (25%), Sharp Stab (25%)

### Stage 4 (Lv 71)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Poison (0.1) |
| Gold Steal | Single enemy | Neutral | 0.80x | - | - | - |
| Item Steal | Single enemy | Neutral | 0.35x | - | - | - |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.25 | Plain hit that deals damage; Paralysis (0.4) |
| Sharp Stab | Single enemy | Stab | 0.90x | - | - | Plain hit that deals damage; Fixed critical hit rate |
| Hard Whipping | Enemy row | Bash | 1.15x | - | 0.4 | Plain hit that deals damage; Fixed critical hit rate (0.5); Damage change for each later target or hit (-0.05) |
| Stun Grenade | All enemies | Neutral | 0.75x | - | - | Deals no damage; Physical accuracy modifier (-0.1); Stun (0.25) |
| Spider Net | All enemies | Neutral | 1.15x | - | - | Deals no damage; Speed modifier (-0.1) |

#### AI Behavior

**Opening Actions:**
- last skill used is Stun Grenade (slot 6) -> set 4 (stop)
- last skill used is Spider Net (slot 7) -> set 4 (stop)
- Gold Steal (slot 1) was used 1 times or more and Item Steal (slot 2) was used 1 times or more -> set 3
- Gold Steal (slot 1) was used 1 times or more -> set 1 (stop)
- Item Steal (slot 2) was used 1 times or more -> set 2 (stop)
**Action Sets:**
- **Set 0:** Gold Steal (30%), Item Steal (30%), Got Your Heart! (15%), Sharp Stab (15%), Hard Whipping (10%)
- **Set 1:** Attack (20%), Item Steal (30%), Got Your Heart! (10%), Sharp Stab (15%), Hard Whipping (15%), Stun Grenade (10%)
- **Set 2:** Attack (20%), Gold Steal (30%), Got Your Heart! (10%), Sharp Stab (15%), Hard Whipping (15%), Spider Net (10%)
- **Set 3:** Attack (20%), Got Your Heart! (20%), Sharp Stab (20%), Hard Whipping (20%), Stun Grenade (10%), Spider Net (10%)
- **Set 4:** Attack (50%), Got Your Heart! (25%), Sharp Stab (25%)

### Stage 5 (Lv 82)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Poison (0.3) |
| Gold Steal | Single enemy | Neutral | 0.80x | - | - | - |
| Item Steal | Single enemy | Neutral | 0.40x | - | - | - |
| Got Your Heart! | Single enemy | Bash | 1.00x | - | 0.55 | Plain hit that deals damage; Paralysis (0.4) |
| Sharp Stab | Single enemy | Stab | 0.90x | - | - | Plain hit that deals damage; Fixed critical hit rate |
| Hard Whipping | Enemy row | Bash | 1.15x | - | 0.4 | Plain hit that deals damage; Fixed critical hit rate (0.5); Damage change for each later target or hit (-0.05) |
| Stun Grenade | All enemies | Neutral | 0.75x | - | - | Deals no damage; Physical accuracy modifier (-0.1); Stun (0.25) |
| Spider Net | All enemies | Neutral | 1.15x | - | - | Deals no damage; Speed modifier (-0.1) |
| Gotcha! | Single enemy | Bash | 1.00x | - | 0.7 | Plain hit that deals damage; Slow (0.4) |

#### AI Behavior

**Opening Actions:**
- last skill used is Stun Grenade (slot 6) -> set 4 (stop)
- last skill used is Spider Net (slot 7) -> set 4 (stop)
- Gold Steal (slot 1) was used 1 times or more and Item Steal (slot 2) was used 1 times or more -> set 3
- Gold Steal (slot 1) was used 1 times or more -> set 1 (stop)
- Item Steal (slot 2) was used 1 times or more -> set 2 (stop)
**Action Sets:**
- **Set 0:** Gold Steal (30%), Item Steal (30%), Got Your Heart! (10%), Sharp Stab (10%), Hard Whipping (10%), Gotcha! (10%)
- **Set 1:** Attack (20%), Item Steal (30%), Got Your Heart! (10%), Sharp Stab (10%), Hard Whipping (10%), Stun Grenade (10%), Gotcha! (10%)
- **Set 2:** Attack (20%), Gold Steal (30%), Got Your Heart! (10%), Sharp Stab (10%), Hard Whipping (10%), Spider Net (10%), Gotcha! (10%)
- **Set 3:** Attack (15%), Got Your Heart! (15%), Sharp Stab (15%), Hard Whipping (15%), Stun Grenade (15%), Spider Net (10%), Gotcha! (15%)
- **Set 4:** Attack (25%), Got Your Heart! (25%), Sharp Stab (25%), Hard Whipping (25%)

## Chloe (Character 320)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main07_20_Start, chapter 7, the Tavern opens after C24)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 30 | 500 Gold | 20 battles | 112 | 64 | 22 | 27 | 47 | 33 | 135 |
| 2 | 42 | 900 Gold | 21 battles | 157 | 91 | 33 | 34 | 64 | 48 | 319 |
| 3 | 52 | 2,600 Gold | 22 battles | 199 | 108 | 45 | 47 | 73 | 60 | 353 |
| 4 | 59 | 3,700 Gold | 23 battles | 236 | 131 | 52 | 55 | 92 | 71 | 230 |
| 5 | 68 | 4,500 Gold | 25 battles | 283 | 155 | 61 | 70 | 123 | 79 | 385 |

### Stage 1 (Lv 30)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Guided Shot | Single enemy | Stab | 0.85x | - | 0.15 | Plain hit that deals damage; Fixed accuracy |
| Poison Shot | Single enemy | Stab | 0.90x | - | 0.15 | Plain hit that deals damage; Poison (0.3) |
| Two Arrows | Random enemies | Stab | 0.85x | - | - | Plain hit that deals damage; Hits twice |

#### AI Behavior

**Opening Actions:**
- last skill used is Two Arrows (slot 3) -> set 1
**Action Sets:**
- **Set 0:** Attack (40%), Guided Shot (20%), Poison Shot (20%), Two Arrows (20%)
- **Set 1:** Attack (50%), Guided Shot (25%), Poison Shot (25%)

### Stage 2 (Lv 42)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Guided Shot | Single enemy | Stab | 0.85x | - | 0.15 | Plain hit that deals damage; Fixed accuracy |
| Freeze Shot | Single enemy | Stab | 0.90x | - | 0.1 | Plain hit that deals damage; Freeze (0.3) |
| Gravity Shot | Single enemy | Stab | 0.90x | - | 0.1 | Plain hit that deals damage; Slow (0.3) |
| Two Arrows | Random enemies | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Hits twice |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1
- last skill used is Two Arrows (slot 4) -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Guided Shot (20%), Freeze Shot (20%), Gravity Shot (20%), Two Arrows (20%)
- **Set 1:** Gravity Shot (50%), Two Arrows (50%)
- **Set 2:** Guided Shot (80%), Freeze Shot (20%)

### Stage 3 (Lv 52)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Guided Shot | Single enemy | Stab | 0.90x | - | 0.45 | Plain hit that deals damage; Fixed accuracy |
| Poison Shot | Single enemy | Stab | 1.00x | - | 0.3 | Plain hit that deals damage; Poison (0.8) |
| Freeze Shot | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Freeze (0.6) |
| Gravity Shot | Single enemy | Stab | 0.90x | - | 0.1 | Plain hit that deals damage; Slow (0.3) |
| Two Arrows | Random enemies | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Hits twice |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1
- last skill used is Two Arrows (slot 5) -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Guided Shot (20%), Poison Shot (15%), Freeze Shot (15%), Gravity Shot (15%), Two Arrows (15%)
- **Set 1:** Guided Shot (30%), Poison Shot (10%), Freeze Shot (10%), Gravity Shot (10%), Two Arrows (40%)
- **Set 2:** Attack (20%), Guided Shot (20%), Poison Shot (20%), Freeze Shot (20%), Gravity Shot (20%)

### Stage 4 (Lv 59)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Guided Shot | Single enemy | Stab | 0.90x | - | 0.45 | Plain hit that deals damage; Fixed accuracy |
| Poison Shot | Single enemy | Stab | 1.00x | - | 0.3 | Plain hit that deals damage; Poison (0.8) |
| Freeze Shot | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Freeze (0.6) |
| Gravity Shot | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Slow (0.6) |
| Two Arrows | Random enemies | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Hits twice |
| Random Shot | Random enemies | Stab | 0.90x | - | -0.05 | Plain hit that deals damage |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Random Shot (slot 6) -> set 1
**Action Sets:**
- **Set 0:** Attack (30%), Guided Shot (10%), Poison Shot (15%), Freeze Shot (15%), Gravity Shot (10%), Two Arrows (10%), Random Shot (10%)
- **Set 1:** Attack (15%), Guided Shot (15%), Poison Shot (20%), Freeze Shot (20%), Gravity Shot (15%), Two Arrows (15%)

### Stage 5 (Lv 68)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Sleep (0.1) |
| Guided Shot | Single enemy | Stab | 0.90x | - | 0.45 | Plain hit that deals damage; Fixed accuracy |
| Poison Shot | Single enemy | Stab | 1.00x | - | 0.3 | Plain hit that deals damage; Poison (0.8) |
| Freeze Shot | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Freeze (0.6) |
| Gravity Shot | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Slow (0.6) |
| Two Arrows | Random enemies | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Hits twice |
| Random Shot | Random enemies | Stab | 0.90x | - | -0.05 | Plain hit that deals damage |
| Chain Spike | Single enemy | Weapon's | 0.70x | - | 0.2 | Plain hit that deals damage; Number of hits (3); Damage change for each later target or hit (-0.25); Critical rate grows with each hit; Number of hits |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Support Shot | - |
| Warning Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (slot 0) -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (40%), Guided Shot (15%), Poison Shot (15%), Freeze Shot (15%), Gravity Shot (15%)
- **Set 1:** Attack (25%), Two Arrows (25%), Random Shot (25%), Chain Spike (25%)
  - *Condition:* Chain Spike (slot 7) aims at: opponent with the lowest HP ratio

## Marion (Character 321)

- **Tavern Availability:** story: St13_0140/Main10_25.adv.bin (Dreamscape 14F, after C35 on 14F, before C36 on 15F)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 48 | 2,280 Gold | 22 battles | 143 | 120 | 61 | 72 | 55 | 38 | 197 |
| 2 | 56 | 3,480 Gold | 23 battles | 168 | 142 | 72 | 86 | 69 | 45 | 220 |
| 3 | 67 | 4,280 Gold | 24 battles | 201 | 171 | 98 | 116 | 83 | 60 | 384 |
| 4 | 73 | 5,680 Gold | 25 battles | 242 | 194 | 128 | 131 | 91 | 72 | 407 |
| 5 | 86 | 6,780 Gold | 26 battles | 294 | 229 | 167 | 174 | 115 | 85 | 1419 |

### Stage 1 (Lv 48)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Spartan | None | Neutral | 0.90x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Catalina | None | Neutral | 0.75x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Stun Needle | Single enemy | Stab | 0.95x | - | 0.25 | Plain hit that deals damage; Paralysis (0.25) |
| Cinnabar Palm | Single enemy | Stab | 0.95x | - | 0.3 | Plain hit that deals damage; Poison (0.75) |

#### AI Behavior

**Opening Actions:**
- Spartan (slot 1) is active -> set 1
- Catalina (slot 2) is active -> set 2
**Action Sets:**
- **Set 0:** Attack (10%), Spartan (40%), Catalina (40%), Stun Needle (5%), Cinnabar Palm (5%)
- **Set 1:** Attack (70%), Stun Needle (15%), Cinnabar Palm (15%)
- **Set 2:** Attack (70%), Stun Needle (15%), Cinnabar Palm (15%)

### Stage 2 (Lv 56)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Spartan | None | Neutral | 0.90x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Catalina | None | Neutral | 0.75x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Stun Needle | Single enemy | Stab | 0.95x | - | 0.4 | Plain hit that deals damage; Paralysis (0.4) |
| Cinnabar Palm | Single enemy | Stab | 0.95x | - | 0.3 | Plain hit that deals damage; Poison (0.75) |
| No Freebies | Single enemy | Neutral | 0.75x | - | - | - |
| Needlework | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Fixed damage (100); Slow (0.2) |

#### AI Behavior

**Opening Actions:**
- Spartan (slot 1) is active -> set 1 (stop)
- Catalina (slot 2) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Spartan (30%), Catalina (20%), Stun Needle (10%), Cinnabar Palm (10%), No Freebies (10%), Needlework (10%)
  - *Condition:* No Freebies (slot 5) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (25%), Stun Needle (25%), Cinnabar Palm (25%), Needlework (25%)
- **Set 2:** Attack (25%), Stun Needle (25%), Cinnabar Palm (25%), Needlework (25%)

### Stage 3 (Lv 67)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Spartan | None | Neutral | 0.95x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Catalina | None | Neutral | 0.75x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Musiy | None | Neutral | 0.80x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Cinnabar Palm | Single enemy | Stab | 0.95x | - | 0.3 | Plain hit that deals damage; Poison (0.75) |
| No Freebies | Single enemy | Neutral | 0.75x | - | - | - |
| Needlework | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Fixed damage (100); Slow (0.2) |

#### AI Behavior

**Opening Actions:**
- Spartan (slot 1) is active -> set 1 (stop)
- Catalina (slot 2) is active -> set 1 (stop)
- Musiy (slot 3) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (5%), Spartan (25%), Catalina (25%), Musiy (25%), No Freebies (20%)
  - *Condition:* No Freebies (slot 5) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (30%), Cinnabar Palm (30%), Needlework (40%)

### Stage 4 (Lv 73)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Spartan | None | Neutral | 0.95x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Catalina | None | Neutral | 0.80x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Musiy | None | Neutral | 0.85x | - | - | Number of units summoned; Turns a summon lasts (5) |
| Cinnabar Palm | Single enemy | Stab | 1.00x | - | 0.5 | Plain hit that deals damage; Poison (0.75) |
| No Freebies | Single enemy | Neutral | 0.75x | - | - | - |
| Circle Illusion | All allies | Neutral | 0.75x | 0.5s | - | - |
| Needlework | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Fixed damage (150); Slow (0.2) |

#### AI Behavior

**Opening Actions:**
- Spartan (slot 1) is active -> set 3 (stop)
- Catalina (slot 2) is active -> set 3 (stop)
- Musiy (slot 3) is active -> set 3 (stop)
- Circle Illusion (slot 6) was used 1 times or more -> set 2 (stop)
- No Freebies (slot 5) was used 1 times or more -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (5%), Spartan (25%), Catalina (25%), Musiy (25%), No Freebies (20%)
- **Set 1:** Attack (10%), Spartan (25%), Catalina (25%), Musiy (25%), Circle Illusion (15%)
- **Set 2:** Attack (25%), Spartan (25%), Catalina (25%), Musiy (25%)
- **Set 3:** Attack (30%), Cinnabar Palm (30%), Needlework (40%)

### Stage 5 (Lv 86)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.3) |
| Spartan | None | Neutral | 0.95x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Catalina | None | Neutral | 0.80x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Musiy | None | Neutral | 0.85x | - | - | Number of units summoned; Turns a summon lasts (5) |
| Cinnabar Palm | Single enemy | Stab | 1.15x | - | 1 | Plain hit that deals damage; Poison |
| Absolutely No Freebies | Single enemy | Neutral | 0.80x | - | - | - |
| Circle Illusion | All allies | Neutral | 0.80x | 0.6s | - | - |
| Needlework | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Fixed damage (200); Slow (0.2) |
| Summon Slave | None | Neutral | 0.85x | - | - | Number of units summoned; Turns a summon lasts (3) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- Spartan (slot 1) is active -> set 3 (stop)
- Catalina (slot 2) is active -> set 4 (stop)
- Musiy (slot 3) is active -> set 5 (stop)
- Summon Slave (slot 8) is active -> set 6 (stop)
- Circle Illusion (slot 6) was used 1 times or more -> set 2 (stop)
- Absolutely No Freebies (slot 5) was used 1 times or more -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (5%), Spartan (20%), Catalina (20%), Musiy (20%), Absolutely No Freebies (20%), Summon Slave (15%)
- **Set 1:** Attack (5%), Spartan (20%), Catalina (20%), Musiy (20%), Circle Illusion (20%), Summon Slave (15%)
- **Set 2:** Attack (10%), Spartan (25%), Catalina (25%), Musiy (25%), Summon Slave (15%)
- **Set 3:** Attack (20%), Cinnabar Palm (40%), Needlework (40%)
- **Set 4:** Attack (20%), Cinnabar Palm (40%), Needlework (40%)
- **Set 5:** Attack (20%), Cinnabar Palm (40%), Needlework (40%)
- **Set 6:** Cinnabar Palm (50%), Needlework (50%)

## Riesco (Character 322)

- **Tavern Availability:** story: St13_0140/Main10_25.adv.bin (Dreamscape 14F, after C35 on 14F, before C36 on 15F)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 49 | 1,900 Gold | 21 battles | 174 | 143 | 73 | 104 | 49 | 51 | 197 |
| 2 | 55 | 2,700 Gold | 23 battles | 193 | 162 | 84 | 121 | 57 | 57 | 220 |
| 3 | 65 | 4,000 Gold | 25 battles | 221 | 178 | 127 | 143 | 73 | 69 | 381 |

### Stage 1 (Lv 49)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Chain Club | Single enemy | Bash | 0.90x | - | 0.15 | Plain hit that deals damage; Hits twice |
| Breath of Ice | Single enemy | Water | 0.90x | - | - | Magic power (200); Freeze (0.2) |
| Frost Slash | Single enemy | Water | 0.70x | - | 0.2 | Plain hit that deals damage; Freeze (0.2) |

#### AI Behavior

**Opening Actions:**
- last skill used is Chain Club (slot 1) -> set 1
- last skill used is Breath of Ice (slot 2) -> set 2
- last skill used is Frost Slash (slot 3) -> set 3
**Action Sets:**
- **Set 0:** Attack (40%), Chain Club (20%), Breath of Ice (20%), Frost Slash (20%)
- **Set 1:** Attack (50%), Breath of Ice (25%), Frost Slash (25%)
- **Set 2:** Attack (50%), Chain Club (25%), Frost Slash (25%)
- **Set 3:** Attack (50%), Chain Club (25%), Breath of Ice (25%)

### Stage 2 (Lv 55)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Chain Club | Single enemy | Bash | 0.90x | - | 0.15 | Plain hit that deals damage; Hits twice |
| Breath of Ice | Single enemy | Water | 0.90x | - | - | Magic power (200); Freeze (0.2) |
| Icy Tentacle | Single enemy | Bash | 0.75x | - | - | Plain hit that deals damage; Hits 1-3 times; Freeze (0.15) |
| Frost Slash | Single enemy | Water | 0.70x | - | 0.2 | Plain hit that deals damage; Freeze (0.2) |
| Limit Field | Indiscriminate | Neutral | 1.25x | 1.75s | - | - |

#### AI Behavior

**Opening Actions:**
- turns taken + 1 <= 1 -> set 1 (stop)
- last skill used is Chain Club (slot 1) -> set 2
- last skill used is Breath of Ice (slot 2) -> set 3
- last skill used is Icy Tentacle (slot 3) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), Chain Club (20%), Breath of Ice (20%), Icy Tentacle (20%), Frost Slash (20%)
- **Set 1:** Attack (25%), Limit Field (75%)
- **Set 2:** Attack (80%), Icy Tentacle (10%), Frost Slash (10%)
- **Set 3:** Attack (80%), Chain Club (10%), Frost Slash (10%)
- **Set 4:** Attack (80%), Breath of Ice (10%), Frost Slash (10%)

### Stage 3 (Lv 65)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Chain Club | Single enemy | Bash | 0.90x | - | 0.15 | Plain hit that deals damage; Hits twice |
| Freezing Sigh | Single enemy | Water | 1.00x | - | - | Magic power (400); Freeze (0.25) |
| Icy Tentacle | Single enemy | Bash | 0.82x | - | 0.1 | Plain hit that deals damage; Hits 1-3 times; Freeze (0.2) |
| Frost Slash | Single enemy | Water | 0.75x | - | 0.4 | Plain hit that deals damage; Freeze (0.3) |
| Limit Field | Indiscriminate | Neutral | 1.35x | 1.75s | - | - |
| Sage Mode | Self | Neutral | 1.00x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Icy Tentacle (slot 3) -> set 1 (stop)
- last skill used is Frost Slash (slot 4) -> set 2 (stop)
- last skill used is Limit Field (slot 5) -> set 3 (stop)
- last skill used is Sage Mode (slot 6) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Chain Club (20%), Freezing Sigh (20%), Icy Tentacle (20%), Frost Slash (20%)
- **Set 1:** Attack (50%), Limit Field (50%)
- **Set 2:** Attack (50%), Sage Mode (50%)
- **Set 3:** Attack (80%), Freezing Sigh (20%)

## Paracas (Character 323)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main10_00_Start, start of chapter 10 after C34)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 42 | 2,300 Gold | 22 battles | 129 | 105 | 84 | 62 | 55 | 54 | 172 |
| 2 | 53 | 3,400 Gold | 23 battles | 161 | 124 | 117 | 75 | 61 | 62 | 215 |
| 3 | 62 | 4,200 Gold | 24 battles | 192 | 153 | 130 | 82 | 67 | 67 | 376 |

### Stage 1 (Lv 42)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Cinnabar Palm | Single enemy | Stab | 0.80x | - | - | Plain hit that deals damage; Poison (0.5) |
| Icy Tentacle | Single enemy | Bash | 0.82x | - | 0.1 | Plain hit that deals damage; Hits 1-3 times; Freeze (0.2) |
| Oracles | None | Neutral | 0.90x | - | - | Number of units summoned; Turns a summon lasts (3) |

#### AI Behavior

**Opening Actions:**
- last skill used is Icy Tentacle (slot 2) -> set 2 (stop)
- Oracles (slot 3) is active -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Cinnabar Palm (10%), Icy Tentacle (10%), Oracles (60%)
- **Set 1:** Attack (40%), Cinnabar Palm (40%), Icy Tentacle (20%)
- **Set 2:** Attack (70%), Cinnabar Palm (30%)

### Stage 2 (Lv 53)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Cinnabar Palm | Single enemy | Stab | 0.80x | - | - | Plain hit that deals damage; Poison (0.5) |
| Icy Tentacle | Single enemy | Bash | 0.90x | - | 0.25 | Plain hit that deals damage; Hits 1-3 times; Freeze (0.25) |
| Water Breath | All enemies | Water | 0.75x | - | - | Magic power (200); Freeze (0.2) |
| Oracles | None | Neutral | 0.90x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Catalina | None | Neutral | 0.75x | - | - | Number of units summoned; Turns a summon lasts (3) |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Puppet | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Icy Tentacle (slot 2) -> set 1 (stop)
- last skill used is Water Breath (slot 3) -> set 2 (stop)
- Oracles (slot 4) is active and Catalina (slot 5) is active -> set 5
- Oracles (slot 4) is active -> set 3
- Catalina (slot 5) is active -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), Cinnabar Palm (20%), Icy Tentacle (15%), Water Breath (15%), Oracles (15%), Catalina (15%)
- **Set 1:** Attack (80%), Cinnabar Palm (20%)
- **Set 2:** Attack (80%), Cinnabar Palm (20%)
- **Set 3:** Attack (40%), Cinnabar Palm (10%), Catalina (20%), Wait and See (30%)
- **Set 4:** Attack (40%), Cinnabar Palm (10%), Oracles (20%), Wait and See (30%)
- **Set 5:** Attack (30%), Cinnabar Palm (30%), Wait and See (40%)

### Stage 3 (Lv 62)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Freeze (0.1) |
| Cinnabar Palm | Single enemy | Stab | 0.80x | - | - | Plain hit that deals damage; Poison (0.5) |
| Icy Tentacle | Single enemy | Bash | 0.90x | - | 0.25 | Plain hit that deals damage; Hits 1-3 times; Freeze (0.25) |
| Water Breath | All enemies | Water | 0.75x | - | - | Magic power (260); Freeze (0.2) |
| Oracles | None | Neutral | 0.95x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Catalina | None | Neutral | 0.80x | - | - | Number of units summoned; Turns a summon lasts (4) |
| Gulp | Piercing | Bash | 0.60x | - | 0.15 | Plain hit that deals damage; Ignores defense; Instant death (0.25) |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Puppet | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Water Breath (slot 3) -> set 4 (stop)
- last skill used is Gulp (slot 6) -> set 4 (stop)
- last skill used is Wait and See (slot 7) -> set 5 (stop)
- Oracles (slot 4) is active and Catalina (slot 5) is active -> set 3
- Oracles (slot 4) is active -> set 1 (stop)
- Catalina (slot 5) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Cinnabar Palm (20%), Oracles (30%), Catalina (30%)
- **Set 1:** Attack (20%), Cinnabar Palm (20%), Icy Tentacle (20%), Catalina (40%)
- **Set 2:** Attack (20%), Cinnabar Palm (20%), Icy Tentacle (20%), Oracles (40%)
- **Set 3:** Attack (40%), Water Breath (30%), Gulp (30%)
- **Set 4:** Wait and See (100%)
- **Set 5:** Attack (50%), Cinnabar Palm (50%)

## Medved (Character 324)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main08_00_Start, start of chapter 8 after C26)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 33 | 800 Gold | 22 battles | 137 | 102 | 3 | 21 | 39 | 22 | 136 |
| 2 | 48 | 1,600 Gold | 24 battles | 177 | 131 | 9 | 36 | 55 | 43 | 204 |
| 3 | 59 | 2,600 Gold | 26 battles | 231 | 144 | 10 | 42 | 61 | 51 | 224 |

### Stage 1 (Lv 33)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Tokatpuci | Single enemy | Neutral | 1.15x | - | - | Plain hit that deals damage; Fixed damage (150); Poison (0.3) |
| Cross Slash | Single enemy | Weapon's | 0.70x | - | 0.25 | Bonus damage to undead, demons and apparitions (0.35); Plain hit that deals damage |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### AI Behavior

**Opening Actions:**
- last skill used is Wait and See (slot 3) -> set 1
**Action Sets:**
- **Set 0:** Attack (40%), Tokatpuci (20%), Cross Slash (20%), Wait and See (20%)
- **Set 1:** Cross Slash (100%)

### Stage 2 (Lv 48)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Tokatpuci | Single enemy | Neutral | 1.20x | - | - | Plain hit that deals damage; Fixed damage (200); Poison (0.3) |
| Cross Slash | Single enemy | Weapon's | 0.70x | - | 0.25 | Bonus damage to undead, demons and apparitions (0.35); Plain hit that deals damage |
| It's a Road Roller! | Enemy row | Bash | 0.65x | - | 0.1 | Plain hit that deals damage; Speed modifier (-0.15) |
| Bear Claw | Single enemy | Slash | 0.70x | - | 0.1 | Plain hit that deals damage; Hits twice; Freeze (0.2) |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### AI Behavior

**Opening Actions:**
- last skill used is It's a Road Roller! (slot 3) -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Tokatpuci (20%), Cross Slash (20%), It's a Road Roller! (20%), Bear Claw (20%)
- **Set 1:** Attack (20%), Wait and See (80%)

### Stage 3 (Lv 59)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Slash | 1.00x | - | - | Plain hit that deals damage |
| Tokatpuci | Single enemy | Neutral | 1.20x | - | - | Plain hit that deals damage; Fixed damage (300); Poison (0.3) |
| Cross Slash | Single enemy | Weapon's | 0.75x | - | 0.4 | Bonus damage to undead, demons and apparitions (0.4); Plain hit that deals damage |
| It's a Road Roller! | Enemy row | Bash | 0.65x | - | 0.1 | Plain hit that deals damage; Speed modifier (-0.15) |
| Bear Claw | Single enemy | Slash | 0.70x | - | 0.1 | Plain hit that deals damage; Hits twice; Freeze (0.2) |
| Gnaw Armor | Single enemy | Stab | 0.90x | - | 0.05 | Plain hit that deals damage; DEF modifier (-0.2) |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |

#### AI Behavior

**Opening Actions:**
- last skill used is Tokatpuci (slot 1) -> set 1
- last skill used is It's a Road Roller! (slot 3) -> set 2
**Action Sets:**
- **Set 0:** Attack (25%), Tokatpuci (15%), Cross Slash (15%), It's a Road Roller! (15%), Bear Claw (15%), Gnaw Armor (15%)
- **Set 1:** Attack (20%), Wait and See (80%)
- **Set 2:** Attack (20%), Wait and See (80%)

## Mekelle (Character 325)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main10_00_Start, start of chapter 10 after C34)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 46 | 2,000 Gold | 21 battles | 151 | 95 | 46 | 57 | 68 | 57 | 172 |
| 2 | 54 | 3,200 Gold | 23 battles | 183 | 135 | 61 | 73 | 91 | 69 | 215 |
| 3 | 63 | 4,200 Gold | 25 battles | 217 | 157 | 77 | 85 | 108 | 83 | 376 |

### Stage 1 (Lv 46)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| I'll Torment You | Single enemy | Neutral | 1.00x | - | - | Deals no damage; Paralysis (0.5); Slow (0.5) |
| Light Scroll | All enemies | Fire | 1.25x | 1.35s | - | Deals no damage; Physical accuracy modifier (-0.1) |
| Water Scroll | All enemies | Water | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); Magic defense modifier (-0.06); Damage cap (200) |
| Earth Scroll | All enemies | Earth | 1.10x | 1.25s | - | Magic power; Damage as a fraction of the target max HP (0.2); DEF modifier (-0.06); Damage cap (200) |
| Ninja Piledriver | Single enemy | Bash | 0.45x | - | 0.16 | Plain hit that deals damage; Stun (0.15) |

#### AI Behavior

**Opening Actions:**
- last skill used is I'll Torment You (slot 1) -> set 1
- last skill used is Light Scroll (slot 2) -> set 2
- last skill used is Water Scroll (slot 3) -> set 3
- last skill used is Earth Scroll (slot 4) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), I'll Torment You (20%), Light Scroll (20%), Water Scroll (20%), Earth Scroll (20%)
- **Set 1:** Attack (20%), Ninja Piledriver (80%)
- **Set 2:** Attack (20%), Ninja Piledriver (80%)
- **Set 3:** Attack (40%), Ninja Piledriver (60%)
- **Set 4:** Attack (40%), Ninja Piledriver (60%)

### Stage 2 (Lv 54)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage; Poison (0.1) |
| I'll Torment You | Single enemy | Neutral | 1.00x | - | - | Deals no damage; Paralysis (0.5); Slow (0.5) |
| Light Scroll | All enemies | Fire | 1.40x | 1.5s | - | Deals no damage; Physical accuracy modifier (-0.2) |
| Water Scroll | All enemies | Water | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Magic defense modifier (-0.09); Damage cap (300) |
| Earth Scroll | All enemies | Earth | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); DEF modifier (-0.09); Damage cap (300) |
| Ninja Piledriver | Single enemy | Bash | 0.50x | - | 0.28 | Plain hit that deals damage; Stun (0.2) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is I'll Torment You (slot 1) -> set 1
- last skill used is Light Scroll (slot 2) -> set 2
- last skill used is Water Scroll (slot 3) -> set 3
- last skill used is Earth Scroll (slot 4) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), I'll Torment You (20%), Light Scroll (20%), Water Scroll (20%), Earth Scroll (20%)
- **Set 1:** Attack (20%), Ninja Piledriver (80%)
- **Set 2:** Attack (20%), Ninja Piledriver (80%)
- **Set 3:** Attack (40%), Ninja Piledriver (60%)
- **Set 4:** Attack (40%), Ninja Piledriver (60%)

### Stage 3 (Lv 63)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Poison (0.3) |
| I'll Torment You | Single enemy | Neutral | 1.00x | - | - | Deals no damage; Paralysis (0.5); Slow (0.5) |
| Light Scroll | All enemies | Fire | 1.60x | 1.75s | - | Deals no damage; Physical accuracy modifier (-0.3) |
| Water Scroll | All enemies | Water | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); Magic defense modifier (-0.09); Damage cap (300) |
| Earth Scroll | All enemies | Earth | 1.30x | 1.4s | - | Magic power; Damage as a fraction of the target max HP (0.3); DEF modifier (-0.09); Damage cap (300) |
| Ninja Piledriver | Single enemy | Bash | 0.55x | - | 0.4 | Plain hit that deals damage; Stun (0.3) |
| Phoenix | Enemy row | Stab | 0.80x | - | - | Plain hit that deals damage; Speed modifier (-0.1); Chance of the speed decrease (0.25) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is I'll Torment You (slot 1) -> set 1
- last skill used is Light Scroll (slot 2) -> set 2
- last skill used is Ninja Piledriver (slot 5) -> set 3
- last skill used is Phoenix (slot 6) -> set 3
- last skill used is Water Scroll (slot 3) -> set 4
- last skill used is Earth Scroll (slot 4) -> set 4
**Action Sets:**
- **Set 0:** Attack (20%), I'll Torment You (15%), Light Scroll (15%), Water Scroll (10%), Earth Scroll (10%), Ninja Piledriver (15%), Phoenix (15%)
- **Set 1:** Attack (20%), Water Scroll (40%), Earth Scroll (40%)
- **Set 2:** Attack (20%), Ninja Piledriver (40%), Phoenix (40%)
- **Set 3:** Attack (60%), I'll Torment You (20%), Light Scroll (20%)
- **Set 4:** Attack (60%), Ninja Piledriver (20%), Phoenix (20%)

## Momona (Character 326)

- **Tavern Availability:** story: evt02.pck/evt02.adv.bin (Main08_00_Start, start of chapter 8 after C26)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 32 | 600 Gold | 20 battles | 26 | 54 | 31 | 53 | 41 | 30 | 136 |
| 2 | 46 | 1,200 Gold | 22 battles | 66 | 87 | 54 | 82 | 57 | 39 | 204 |
| 3 | 58 | 2,700 Gold | 24 battles | 80 | 94 | 67 | 104 | 72 | 45 | 224 |

### Stage 1 (Lv 32)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Here's Some Sweets | Single enemy | Neutral | 1.30x | - | - | Deals no damage; Poison (0.4) |
| Lullaby | Single enemy | Wind | 1.50x | 1.5s | - | Deals no damage; Sleep (0.75) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest TP ratio among allies <= 80 -> set 1
**Action Sets:**
- **Set 0:** Attack (70%), Here's Some Sweets (10%), Lullaby (20%)
- **Set 1:** Attack (20%), Cook (80%)
  - *Condition:* Cook (slot 3) aims at: ally with the lowest TP ratio

### Stage 2 (Lv 46)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Here's Some Suspicious Sweets | Single enemy | Neutral | 1.30x | - | - | Deals no damage; Poison (0.5); Paralysis (0.25) |
| Lullaby | Single enemy | Wind | 1.50x | 1.5s | - | Deals no damage; Sleep (0.95) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |
| 2 a.m. | Single enemy | Neutral | 0.85x | - | - | Deals no damage; Petrification (0.25) |
| Dumbing Mazurka | All enemies | Neutral | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- Dumbing Mazurka (slot 5) is active -> set 2
- lowest TP ratio among allies <= 80 -> set 1
**Action Sets:**
- **Set 0:** Attack (40%), Here's Some Suspicious Sweets (15%), Lullaby (15%), 2 a.m. (15%), Dumbing Mazurka (15%)
- **Set 1:** Attack (20%), Cook (80%)
  - *Condition:* Cook (slot 3) aims at: ally with the lowest TP ratio
- **Set 2:** Attack (70%), Here's Some Suspicious Sweets (10%), Lullaby (10%), 2 a.m. (10%)

### Stage 3 (Lv 58)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Slow (0.1) |
| Here's Some Suspicious Sweets | Single enemy | Neutral | 1.30x | - | - | Deals no damage; Poison (0.5); Paralysis (0.25) |
| Lullaby | Single enemy | Wind | 1.50x | 1.5s | - | Deals no damage; Sleep (0.95) |
| Cook | Single ally | Neutral | 0.65x | - | - | - |
| 2 a.m. | Single enemy | Neutral | 0.90x | - | - | Deals no damage; Petrification (0.5) |
| Debilitating Salsa | All enemies | Neutral | 0.80x | - | - | Damage every turn as a fraction of the target max HP (0.2); Damage cap (250) |
| Dumbing Mazurka | All enemies | Neutral | 0.80x | - | - | - |

#### AI Behavior

**Opening Actions:**
- lowest TP ratio among allies <= 80 -> set 1 (stop)
- Debilitating Salsa (slot 5) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (40%), Here's Some Suspicious Sweets (15%), Lullaby (15%), 2 a.m. (15%), Debilitating Salsa (15%)
- **Set 1:** Attack (20%), Cook (80%)
  - *Condition:* Cook (slot 3) aims at: ally with the lowest TP ratio
- **Set 2:** Attack (20%), Here's Some Suspicious Sweets (20%), Lullaby (20%), 2 a.m. (10%), Dumbing Mazurka (30%)

## Azmaria (Character 327)

- **Tavern Availability:** side event: St10_0010/St10_0390.adv.bin (after battle 52 Azmaria Lv50 in Prizren Woods; party reaches Lv50 at C37)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 50 | 4,000 Gold | 20 battles | 201 | 142 | 1 | 87 | 63 | 55 | 1089 |
| 2 | 62 | 5,000 Gold | 20 battles | 262 | 178 | 1 | 96 | 81 | 66 | 263 |
| 3 | 72 | 6,000 Gold | 20 battles | 324 | 197 | 1 | 125 | 97 | 78 | 384 |
| 4 | 84 | 7,000 Gold | 20 battles | 397 | 212 | 1 | 143 | 112 | 85 | 374 |
| 5 | 93 | 8,000 Gold | 20 battles | 478 | 251 | 1 | 166 | 138 | 96 | 359 |

### Stage 1 (Lv 50)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage |
| Painful Strike | Single enemy | Neutral | 0.60x | - | 0.75 | Plain hit that deals damage |
| Double Face Slap | Single enemy | Bash | 1.10x | - | 0.25 | Plain hit that deals damage; Chance to push the target back in the turn order (0.9) |
| Air Throw | Single enemy | Bash | 0.80x | - | - | Plain hit that deals damage; Ignores defense; Chance to push the target back in the turn order (0.5) |
| Cinnabar Palm | Single enemy | Stab | 1.00x | - | 0.2 | Plain hit that deals damage; Paralysis (0.3) |
| Assess | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Painful Strike (slot 1) -> set 1
- last skill used is Attack (slot 0) -> set 2
**Action Sets:**
- **Set 0:** Attack (20%), Painful Strike (20%), Double Face Slap (20%), Air Throw (20%), Cinnabar Palm (20%)
- **Set 1:** Attack (50%), Assess (50%)
- **Set 2:** Painful Strike (10%), Double Face Slap (30%), Air Throw (30%), Cinnabar Palm (30%)

### Stage 2 (Lv 62)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.1) |
| Painful Strike | Single enemy | Neutral | 0.80x | - | 1 | Plain hit that deals damage |
| Grit Your Teeth! | Single enemy | Bash | 1.25x | - | 0.5 | Plain hit that deals damage; Chance to push the target back in the turn order |
| Air Throw | Single enemy | Bash | 0.85x | - | 0.2 | Plain hit that deals damage; Ignores defense; Chance to push the target back in the turn order (0.6) |
| Azmaria Kick | All enemies | Bash | 0.75x | - | 0.25 | Plain hit that deals damage; Fixed accuracy (0.75) |
| War Cry | All allies | Neutral | 1.25x | - | - | ATK modifier (0.14) |
| Assess | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is War Cry (slot 5) -> set 1 (stop)
- last skill used is Azmaria Kick (slot 4) -> set 2 (stop)
- last skill used is Painful Strike (slot 1) -> set 3 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Painful Strike (15%), Grit Your Teeth! (20%), Air Throw (15%), Azmaria Kick (15%), War Cry (15%)
- **Set 1:** Attack (25%), Painful Strike (15%), Grit Your Teeth! (25%), Air Throw (15%), Azmaria Kick (20%)
- **Set 2:** Attack (25%), Grit Your Teeth! (25%), Assess (50%)
- **Set 3:** Attack (45%), Air Throw (45%), Assess (10%)

### Stage 3 (Lv 72)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Paralysis (0.5) |
| Painful Strike | Single enemy | Neutral | 0.80x | - | 1 | Plain hit that deals damage |
| Grit Your Teeth! | Single enemy | Bash | 1.25x | - | 0.5 | Plain hit that deals damage; Chance to push the target back in the turn order |
| Air Throw | Single enemy | Bash | 0.85x | - | 0.2 | Plain hit that deals damage; Ignores defense; Chance to push the target back in the turn order (0.6) |
| Azmaria Kick | All enemies | Bash | 0.75x | - | 0.25 | Plain hit that deals damage; Fixed accuracy (0.75) |
| War Cry | All allies | Neutral | 1.50x | - | - | ATK modifier (0.18) |
| Justice | Single enemy | Weapon's | 0.88x | - | 0.35 | Plain hit that deals damage; DEF modifier (-0.1) |
| Assess | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is War Cry (slot 5) -> set 1 (stop)
- last skill used is Painful Strike (slot 1) -> set 2 (stop)
- last skill used is Grit Your Teeth! (slot 2) -> set 2 (stop)
- last skill used is Justice (slot 6) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Painful Strike (15%), Grit Your Teeth! (15%), Air Throw (15%), Azmaria Kick (15%), War Cry (15%), Justice (15%)
- **Set 1:** Attack (15%), Painful Strike (15%), Grit Your Teeth! (15%), Air Throw (20%), Azmaria Kick (15%), Justice (20%)
- **Set 2:** Attack (50%), Assess (50%)

### Stage 4 (Lv 84)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Fist of Justice | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Ignores defense |
| Painful Strike | Single enemy | Neutral | 0.80x | - | 1 | Plain hit that deals damage |
| Grit Your Teeth! | Single enemy | Bash | 1.25x | - | 0.5 | Plain hit that deals damage; Chance to push the target back in the turn order |
| Air Throw | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Ignores defense; Chance to push the target back in the turn order (0.7) |
| Super Azmaria Kick | All enemies | Bash | 0.75x | - | 0.65 | Plain hit that deals damage; Fixed accuracy (0.75); Stun (0.2) |
| War Cry | All allies | Neutral | 1.50x | - | - | ATK modifier (0.18) |
| Justice | Single enemy | Weapon's | 0.91x | - | 0.45 | Plain hit that deals damage; DEF modifier (-0.1) |
| Faux Magical Spark | Single enemy | Lightning | 0.80x | - | 0.75 | Plain hit that deals damage |
| Assess | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is War Cry (slot 5) -> set 1 (stop)
- last skill used is Painful Strike (slot 1) -> set 2 (stop)
- last skill used is Air Throw (slot 3) -> set 2 (stop)
- last skill used is Super Azmaria Kick (slot 4) -> set 2 (stop)
- last skill used is Justice (slot 6) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Fist of Justice (15%), Painful Strike (10%), Grit Your Teeth! (10%), Air Throw (15%), Super Azmaria Kick (10%), War Cry (20%), Justice (10%), Faux Magical Spark (10%)
- **Set 1:** Painful Strike (20%), Super Azmaria Kick (40%), Justice (20%), Faux Magical Spark (20%)
- **Set 2:** Fist of Justice (30%), Faux Magical Spark (30%), Assess (40%)

### Stage 5 (Lv 93)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Fist of Justice | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Ignores defense |
| Painful Strike | Single enemy | Neutral | 0.80x | - | 1 | Plain hit that deals damage |
| Grit Your Teeth! | Single enemy | Bash | 1.25x | - | 0.5 | Plain hit that deals damage; Chance to push the target back in the turn order |
| Air Throw | Single enemy | Bash | 0.90x | - | 0.35 | Plain hit that deals damage; Ignores defense; Chance to push the target back in the turn order (0.7) |
| Miracle Azmaria Kick | All enemies | Bash | 0.75x | - | 0.8 | Plain hit that deals damage; Fixed accuracy (0.75); Stun (0.3) |
| War Cry | All allies | Neutral | 1.50x | - | - | ATK modifier (0.18) |
| Justice | Single enemy | Weapon's | 1.00x | - | 0.55 | Plain hit that deals damage; DEF modifier (-0.1) |
| Faux Magical Spark | Single enemy | Lightning | 0.80x | - | 0.75 | Plain hit that deals damage |
| Pseudo-Magical Change | Self | Neutral | 1.00x | - | - | - |
| Assess | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Double Attack | - |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is War Cry (slot 5) -> set 1 (stop)
- last skill used is Painful Strike (slot 1) -> set 2 (stop)
- last skill used is Miracle Azmaria Kick (slot 4) -> set 2 (stop)
- last skill used is Justice (slot 6) -> set 2 (stop)
- last skill used is Assess (slot 9) -> set 3 (stop)
- Pseudo-Magical Change (slot 8) is active -> set 4 (stop)
**Action Sets:**
- **Set 0:** Fist of Justice (15%), Painful Strike (10%), Grit Your Teeth! (10%), Air Throw (15%), Miracle Azmaria Kick (10%), War Cry (10%), Justice (15%), Faux Magical Spark (15%)
- **Set 1:** Painful Strike (20%), Miracle Azmaria Kick (40%), Justice (20%), Faux Magical Spark (20%)
- **Set 2:** Fist of Justice (20%), Faux Magical Spark (30%), Assess (50%)
- **Set 3:** Fist of Justice (25%), Pseudo-Magical Change (75%)
- **Set 4:** Fist of Justice (20%), Grit Your Teeth! (20%), Air Throw (20%), Faux Magical Spark (40%)

## Miranda (Character 328)

- **Tavern Availability:** quest rank: QuestRankData_12.bin (Quest Rank 12, 390 pts; Miranda Lv53, party reaches Lv53 at C38)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 53 | 3,700 Gold | 24 battles | 204 | 117 | 40 | 61 | 68 | 49 | 1094 |
| 2 | 64 | 4,300 Gold | 24 battles | 243 | 146 | 61 | 77 | 92 | 57 | 284 |
| 3 | 70 | 5,200 Gold | 24 battles | 278 | 165 | 72 | 92 | 113 | 76 | 381 |
| 4 | 80 | 6,300 Gold | 24 battles | 351 | 189 | 91 | 104 | 124 | 82 | 400 |
| 5 | 90 | 7,400 Gold | 24 battles | 422 | 212 | 103 | 129 | 148 | 93 | 1419 |

### Stage 1 (Lv 53)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Poison (0.3) |
| Buster Cannon | Piercing | Stab | 0.90x | - | 0.2 | Plain hit that deals damage |
| Charge | Self | Neutral | 1.10x | - | - | - |
| Wait and See | Self | Neutral | 1.15x | - | - | Speed modifier (0.2); Physical evasion modifier (0.2) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Warning Shot | - |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Charge (slot 3) -> set 1
- last skill used is Buster Cannon (slot 2) -> set 2
- last skill used is Wait and See (slot 4) -> set 3
**Action Sets:**
- **Set 0:** Attack (Gun) (20%), Attack (Gun) (25%), Buster Cannon (20%), Charge (20%), Wait and See (15%)
  - *Condition:* Wait and See (slot 4) was used 2 times or more -> Attack (Gun) (slot 0)
- **Set 1:** Attack (Gun) (50%), Attack (Gun) (50%)
- **Set 2:** Attack (Gun) (100%)
- **Set 3:** Buster Cannon (100%)

### Stage 2 (Lv 64)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | - | Plain hit that deals damage |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Poison (0.3) |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.75 | Plain hit that deals damage |
| Buster Cannon | Piercing | Stab | 0.90x | - | 0.5 | Plain hit that deals damage |
| Dynamite Throw | Random enemies | Earth | 0.85x | - | -0.04 | Plain hit that deals damage; Hits 2-4 times; Stun (0.25) |
| Wait and See | Self | Neutral | 1.15x | - | - | Speed modifier (0.2); Physical evasion modifier (0.2) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Warning Shot | - |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Buster Cannon (slot 3) -> set 1
- last skill used is Dynamite Throw (slot 4) -> set 2
- last skill used is Wait and See (slot 5) -> set 3
**Action Sets:**
- **Set 0:** Attack (Gun) (30%), Attack (Gun) (20%), Buster Cannon (20%), Dynamite Throw (20%), Wait and See (10%)
- **Set 1:** Attack (Gun) (40%), Attack (Gun) (30%), Attack (Gun) (10%), Dynamite Throw (10%), Wait and See (10%)
- **Set 2:** Attack (Gun) (40%), Attack (Gun) (30%), Attack (Gun) (10%), Buster Cannon (10%), Wait and See (10%)
- **Set 3:** Attack (Gun) (10%), Attack (Gun) (30%), Buster Cannon (30%), Dynamite Throw (30%)

### Stage 3 (Lv 70)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.75 | Plain hit that deals damage |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Poison (0.3) |
| Buster Cannon | Piercing | Stab | 0.90x | - | 0.3 | Plain hit that deals damage |
| Happy Trigger | Random enemies | Stab | 0.85x | - | 0.1 | Plain hit that deals damage; Hits 1-3 times |
| Dynamite Throw | Random enemies | Earth | 0.80x | - | -0.08 | Plain hit that deals damage; Hits 2-4 times; Stun (0.2) |
| Wait and See | Self | Neutral | 1.15x | - | - | Speed modifier (0.2); Physical evasion modifier (0.2) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Warning Shot | - |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Buster Cannon (slot 2) -> set 1 (stop)
- last skill used is Happy Trigger (slot 3) -> set 1 (stop)
- last skill used is Wait and See (slot 5) -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (Gun) (10%), Attack (Gun) (40%), Buster Cannon (25%), Happy Trigger (25%)
- **Set 1:** Attack (Gun) (40%), Dynamite Throw (30%), Wait and See (30%)
- **Set 2:** Attack (Gun) (60%), Attack (Gun) (20%), Dynamite Throw (20%)

### Stage 4 (Lv 80)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.75 | Plain hit that deals damage |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Poison (0.3) |
| Buster Cannon | Piercing | Stab | 0.90x | - | 0.3 | Plain hit that deals damage |
| Happy Trigger | Random enemies | Stab | 0.85x | - | 0.25 | Plain hit that deals damage; Hits 1-3 times |
| Dynamite Throw | Random enemies | Earth | 0.80x | - | -0.08 | Plain hit that deals damage; Hits 2-4 times; Stun (0.2) |
| Head Shot | Single enemy | Stab | 0.90x | - | 0.35 | Plain hit that deals damage; Instant death (0.5) |
| Lock-On Snipe | Self | Neutral | 1.10x | - | - | Speed modifier (0.2); Physical accuracy modifier (0.35) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Warning Shot | - |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (Gun) (slot 1) -> set 2 (stop)
- last skill used is Head Shot (slot 5) -> set 3 (stop)
- Lock-On Snipe (slot 6) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (Gun) (20%), Attack (Gun) (25%), Buster Cannon (20%), Happy Trigger (20%), Lock-On Snipe (15%)
- **Set 1:** Attack (Gun) (25%), Attack (Gun) (25%), Buster Cannon (20%), Head Shot (30%)
- **Set 2:** Attack (Gun) (25%), Happy Trigger (25%), Dynamite Throw (50%)
- **Set 3:** Attack (Gun) (50%), Happy Trigger (50%)

### Stage 5 (Lv 90)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.75 | Plain hit that deals damage |
| Attack (Gun) | Single enemy | Stab | 1.00x | - | 0.1 | Plain hit that deals damage; Poison (0.3) |
| Buster Cannon EX | Piercing | Stab | 0.90x | - | 0.4 | Plain hit that deals damage; DEF modifier (-0.1) |
| Happy Trigger | Random enemies | Stab | 0.85x | - | 0.25 | Plain hit that deals damage; Hits 1-3 times |
| Dynamite Throw | Random enemies | Earth | 0.80x | - | 0.05 | Plain hit that deals damage; Hits 2-4 times; Stun (0.2) |
| Head Shot | Single enemy | Stab | 0.90x | - | 0.35 | Plain hit that deals damage; Instant death (0.5) |
| Lock-On Snipe | Self | Neutral | 1.10x | - | - | Speed modifier (0.2); Physical accuracy modifier (0.35) |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Warning Shot | - |
| Support Shot | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Attack (Gun) (slot 1) -> set 2 (stop)
- last skill used is Head Shot (slot 5) -> set 3 (stop)
- Lock-On Snipe (slot 6) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (Gun) (20%), Attack (Gun) (20%), Buster Cannon EX (20%), Happy Trigger (20%), Lock-On Snipe (20%)
- **Set 1:** Attack (Gun) (10%), Attack (Gun) (20%), Buster Cannon EX (20%), Head Shot (50%)
- **Set 2:** Buster Cannon EX (25%), Happy Trigger (25%), Dynamite Throw (50%)
- **Set 3:** Attack (Gun) (35%), Buster Cannon EX (30%), Happy Trigger (35%)

## Euthys (Character 329)

- **Tavern Availability:** postgame: evt02.pck/St93.adv.bin (after defeating Euthys on Vrachia North, P05)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 74 | 4,000 Gold | 5 battles | 359 | 318 | 238 | 226 | 116 | 87 | 928 |
| 2 | 82 | 4,500 Gold | 5 battles | 427 | 341 | 267 | 248 | 138 | 96 | 250 |
| 3 | 88 | 5,000 Gold | 5 battles | 495 | 402 | 314 | 302 | 155 | 112 | 374 |
| 4 | 95 | 6,000 Gold | 5 battles | 576 | 449 | 362 | 358 | 179 | 125 | 412 |
| 5 | 99 | 9,000 Gold | 10 battles | 631 | 483 | 401 | 402 | 197 | 138 | 365 |

### Stage 1 (Lv 74)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Instant death (0.2) |
| Blood Carnival | Random enemies | Bash | 0.50x | - | - | Plain hit that deals damage |
| Shock Spiral | Enemy row | Lightning | 0.80x | - | 0.2 | Plain hit that deals damage; Paralysis (0.25) |
| Spit Fire | All enemies | Fire | 0.85x | - | - | Magic power (475) |
| Megingjoro | Self | Neutral | 1.50x | 1s | - | ATK modifier (0.5); DEF modifier (0.5); Speed modifier (0.2) |
| Teatime | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Blood Carnival (slot 1) -> set 1 (stop)
- Megingjoro (slot 4) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (20%), Blood Carnival (10%), Shock Spiral (10%), Spit Fire (10%), Megingjoro (50%)
- **Set 1:** Attack (50%), Teatime (50%)
- **Set 2:** Attack (25%), Blood Carnival (25%), Shock Spiral (25%), Spit Fire (25%)

### Stage 2 (Lv 82)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Instant death (0.2) |
| Blood Carnival | Random enemies | Bash | 0.80x | - | 0.15 | Plain hit that deals damage |
| Shock Spiral | Enemy row | Lightning | 0.80x | - | 0.2 | Plain hit that deals damage; Paralysis (0.25) |
| Spit Fire | All enemies | Fire | 0.85x | - | - | Magic power (475) |
| Megingjoro | Self | Neutral | 1.50x | 1s | - | ATK modifier (0.5); DEF modifier (0.5); Speed modifier (0.2) |
| Million Shredder | Single enemy | Wind | 1.40x | - | - | Magic power (900) |
| Fervent Discipline | Enemy row | Neutral | 0.65x | - | - | Plain hit that deals damage; Fixed damage (555); ATK modifier (-0.1); DEF modifier (-0.1); Physical accuracy modifier (-0.1) |
| Teatime | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Blood Carnival (slot 1) -> set 2 (stop)
- Megingjoro (slot 4) is active -> set 1 (stop)
**Action Sets:**
- **Set 0:** Blood Carnival (10%), Shock Spiral (10%), Spit Fire (10%), Megingjoro (40%), Million Shredder (10%), Fervent Discipline (20%)
  - *Condition:* Fervent Discipline (slot 6) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (20%), Blood Carnival (20%), Shock Spiral (20%), Spit Fire (20%), Million Shredder (20%)
- **Set 2:** Attack (25%), Shock Spiral (25%), Teatime (50%)

### Stage 3 (Lv 88)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Instant death (0.2) |
| Blood Carnival | Random enemies | Bash | 0.80x | - | 0.15 | Plain hit that deals damage |
| Shock Spiral | Enemy row | Lightning | 0.95x | - | 0.4 | Plain hit that deals damage; Paralysis (0.5) |
| Fiery Ring of Iron | All enemies | Fire | 0.70x | - | - | Magic power (600); Stun (0.35) |
| Megingjoro | Self | Neutral | 1.50x | 1s | - | ATK modifier (0.5); DEF modifier (0.5); Speed modifier (0.2) |
| Million Shredder | Single enemy | Wind | 1.40x | - | - | Magic power (1300) |
| Fervent Discipline | Enemy row | Neutral | 0.65x | - | - | Plain hit that deals damage; Fixed damage (555); ATK modifier (-0.1); DEF modifier (-0.1); Physical accuracy modifier (-0.1) |
| Full Heal | Single ally | Neutral | 1.40x | 0.65s | - | - |
| Teatime | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 50 -> set 1 (stop)
- last skill used is Blood Carnival (slot 1) -> set 3 (stop)
- last skill used is Fiery Ring of Iron (slot 3) -> set 4 (stop)
- last skill used is Million Shredder (slot 5) -> set 4 (stop)
- last skill used is Fervent Discipline (slot 6) -> set 4 (stop)
- Megingjoro (slot 4) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Blood Carnival (20%), Shock Spiral (20%), Fiery Ring of Iron (10%), Megingjoro (20%), Million Shredder (10%), Fervent Discipline (20%)
- **Set 1:** Blood Carnival (20%), Million Shredder (20%), Full Heal (60%)
  - *Condition:* Full Heal (slot 7) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Blood Carnival (40%), Shock Spiral (40%)
- **Set 3:** Attack (20%), Shock Spiral (20%), Fiery Ring of Iron (30%), Million Shredder (30%)
- **Set 4:** Attack (50%), Teatime (50%)

### Stage 4 (Lv 95)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage; Instant death (0.5) |
| Blood Carnival | Random enemies | Bash | 0.80x | - | 0.15 | Plain hit that deals damage |
| Shock Spiral | Enemy row | Lightning | 0.95x | - | 0.4 | Plain hit that deals damage; Paralysis (0.5) |
| Fiery Ring of Iron | All enemies | Fire | 1.00x | - | - | Magic power (850); Stun (0.5) |
| Megingjoro | Self | Neutral | 1.50x | 1s | - | ATK modifier (0.5); DEF modifier (0.5); Speed modifier (0.2) |
| Million Shredder | Single enemy | Wind | 1.40x | - | - | Magic power (1700) |
| Thunder Break | Piercing | Lightning | 1.15x | - | - | Magic power (1200) |
| Fervent Discipline | Enemy row | Neutral | 0.75x | - | - | Plain hit that deals damage; Fixed damage (777); ATK modifier (-0.1); DEF modifier (-0.1); Physical accuracy modifier (-0.1) |
| Full Heal | Single ally | Neutral | 1.50x | 0.8s | - | - |
| Teatime | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 50 -> set 1 (stop)
- last skill used is Blood Carnival (slot 1) -> set 3 (stop)
- last skill used is Fiery Ring of Iron (slot 3) -> set 4 (stop)
- last skill used is Million Shredder (slot 5) -> set 4 (stop)
- last skill used is Thunder Break (slot 6) -> set 4 (stop)
- last skill used is Fervent Discipline (slot 7) -> set 4 (stop)
- Megingjoro (slot 4) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Blood Carnival (20%), Shock Spiral (20%), Fiery Ring of Iron (10%), Megingjoro (20%), Fervent Discipline (20%)
- **Set 1:** Blood Carnival (10%), Million Shredder (20%), Thunder Break (20%), Full Heal (50%)
  - *Condition:* Full Heal (slot 8) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Blood Carnival (40%), Shock Spiral (40%)
- **Set 3:** Attack (20%), Fiery Ring of Iron (30%), Million Shredder (25%), Thunder Break (25%)
- **Set 4:** Attack (40%), Teatime (60%)

### Stage 5 (Lv 99)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | 0.25 | Plain hit that deals damage; Instant death (0.5) |
| Blood Carnival | Random enemies | Bash | 0.80x | - | 0.15 | Plain hit that deals damage |
| Shock Spiral | Enemy row | Lightning | 0.95x | - | 0.4 | Plain hit that deals damage; Paralysis (0.5) |
| Fiery Ring of Iron | All enemies | Fire | 1.00x | - | - | Magic power (850); Stun (0.5) |
| Megingjoro | Self | Neutral | 1.50x | 1s | - | ATK modifier (0.5); DEF modifier (0.5); Speed modifier (0.2) |
| Million Shredder | Single enemy | Wind | 1.40x | - | - | Magic power (2100) |
| Thunder Break | Piercing | Lightning | 1.15x | - | - | Magic power (1500) |
| Fervent Discipline | Enemy row | Neutral | 0.75x | - | - | Plain hit that deals damage; Fixed damage (777); ATK modifier (-0.1); DEF modifier (-0.1); Physical accuracy modifier (-0.1) |
| Full Heal | Single ally | Neutral | 1.50x | 1s | - | - |
| Overrun | Random enemies | Bash | 1.00x | - | 0.4 | Plain hit that deals damage; Hits 2-4 times; Fixed critical hit rate |
| Teatime | None | -1 | 0.75x | - | - | - |

#### Passives

| Passive | Effect |
| :--- | :--- |
| Triple Attack | - |

#### AI Behavior

**Opening Actions:**
- lowest HP ratio among allies <= 50 -> set 1 (stop)
- last skill used is Blood Carnival (slot 1) -> set 3 (stop)
- last skill used is Overrun (slot 9) -> set 3 (stop)
- last skill used is Shock Spiral (slot 2) -> set 4 (stop)
- last skill used is Fiery Ring of Iron (slot 3) -> set 4 (stop)
- last skill used is Fervent Discipline (slot 7) -> set 4 (stop)
- Megingjoro (slot 4) is active -> set 2 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Blood Carnival (20%), Shock Spiral (20%), Fiery Ring of Iron (15%), Megingjoro (15%), Fervent Discipline (20%)
- **Set 1:** Blood Carnival (10%), Million Shredder (15%), Thunder Break (15%), Full Heal (60%)
  - *Condition:* Full Heal (slot 8) aims at: ally with the lowest HP ratio
- **Set 2:** Attack (20%), Blood Carnival (40%), Overrun (40%)
- **Set 3:** Attack (10%), Fiery Ring of Iron (10%), Million Shredder (40%), Thunder Break (40%)
- **Set 4:** Attack (50%), Teatime (50%)

## Lolo (Character 330)

- **Tavern Availability:** postgame: St21_1010/St21_g0010.adv.bin (Casino basement after Octopunch; Lv86, party reaches Lv86 at P21)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 86 | 7,777 Gold | 16 battles | 345 | 113 | 172 | 192 | 155 | 122 | 1104 |
| 2 | 93 | 7,777 Gold | 18 battles | 432 | 138 | 236 | 221 | 176 | 138 | 388 |

### Stage 1 (Lv 86)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Wind | 1.00x | - | 0.15 | Plain hit that deals damage |
| Fairy Jibe | Single enemy | Bash | 0.90x | - | 0.6 | Plain hit that deals damage; Stun |
| Fairy Attack | Piercing | Neutral | 0.75x | - | - | Magic power (500); Slow |
| Resurrect | Single ally | Neutral | 1.00x | 0.8s | - | HP on revival, as a fraction of max HP (0.15) |
| Make Way for Lolo! | Single enemy | Bash | 0.50x | - | 1 | Plain hit that deals damage; Instant death |
| Magical Change | Self | Neutral | 1.15x | - | - | - |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- Resurrect (slot 3) aims at: dead ally
- last skill used is Take Break (slot 6) -> set 2
- Magical Change (slot 5) is active -> set 3
- an ally is dead -> set 1
**Action Sets:**
- **Set 0:** Attack (20%), Fairy Jibe (20%), Fairy Attack (20%), Make Way for Lolo! (20%), Take Break (20%)
- **Set 1:** Fairy Jibe (10%), Fairy Attack (10%), Resurrect (70%), Make Way for Lolo! (10%)
- **Set 2:** Attack (20%), Magical Change (80%)
- **Set 3:** Attack (25%), Fairy Jibe (25%), Fairy Attack (25%), Make Way for Lolo! (25%)

### Stage 2 (Lv 93)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Wind | 1.00x | - | 0.3 | Plain hit that deals damage |
| Fairy Jibe | Single enemy | Bash | 1.00x | - | 0.75 | Plain hit that deals damage; Stun |
| Fairy Attack | Piercing | Neutral | 0.80x | - | - | Magic power (625); Slow |
| Resurrect | Single ally | Neutral | 1.05x | 0.85s | - | HP on revival, as a fraction of max HP (0.3) |
| Make Way for Lolo! | Single enemy | Bash | 0.50x | - | 1 | Plain hit that deals damage; Instant death |
| Magical Change | Self | Neutral | 1.15x | - | - | - |
| Tempest | Single enemy | Wind | 1.40x | 1.05s | - | Magic power (1000) |
| Fairy Healing | Single ally | Neutral | 0.70x | - | - | Heal power (6); How many ailments of the listed order it cures (5) |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- an ally is dead -> set 1 (stop)
- lowest HP ratio among allies <= 40 -> set 2 (stop)
- last skill used is Take Break (slot 8) -> set 3 (stop)
- Magical Change (slot 5) is active -> set 4 (stop)
**Action Sets:**
- **Set 0:** Attack (10%), Fairy Jibe (20%), Fairy Attack (20%), Make Way for Lolo! (20%), Tempest (15%), Take Break (15%)
- **Set 1:** Fairy Jibe (10%), Fairy Attack (10%), Resurrect (70%), Make Way for Lolo! (10%)
  - *Condition:* Resurrect (slot 3) aims at: dead ally
- **Set 2:** Make Way for Lolo! (15%), Tempest (15%), Fairy Healing (70%)
  - *Condition:* Fairy Healing (slot 7) aims at: ally with the lowest HP ratio
- **Set 3:** Attack (20%), Magical Change (80%)
- **Set 4:** Attack (20%), Fairy Jibe (20%), Fairy Attack (20%), Make Way for Lolo! (20%), Tempest (20%)

## Michelle (Character 411)

- **Tavern Availability:** never: Michelle, a guest of the story (joined by story event , not hired at the Tavern)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 30 | 0 Gold | Permanent | 85 | 83 | 34 | 55 | 42 | 37 | 1003 |

### Stage 1 (Lv 30)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Bash | 1.00x | - | - | Plain hit that deals damage; Silence (0.1) |
| Bible Thump | Single enemy | Bash | 0.85x | - | 0.4 | Plain hit that deals damage; Damage based on RES; Freeze (0.2); Silence (0.2) |
| Prism Dawn | Piercing | Neutral | 1.20x | 1s | - | Magic power (200); Damage based on RES |
| Death | Single enemy | Earth | 1.00x | 1s | - | Deals no damage; Instant death |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Prism Dawn (slot 2) -> set 1
- last skill used is Death (slot 3) -> set 2
**Action Sets:**
- **Set 0:** Attack (40%), Bible Thump (20%), Prism Dawn (20%), Death (20%)
- **Set 1:** Take Break (100%)
- **Set 2:** Attack (50%), Take Break (50%)

## Peggy & Beard (Character 488)

- **Tavern Availability:** story: St10_0010/cont_09.adv.bin (set in 9th talk event, chapter 8) to St12_0040/cont_10.adv.bin (cleared in 10th, chapter 9)

| Stage | Level | Cost | Contract | ATK | DEF | INT | RES | DEX | AGI | Unlock Flag |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 35 | 1,000 Gold | 1 battles | 114 | 96 | 500 | 41 | 52 | 39 | 1106 |

### Stage 1 (Lv 35)

#### Attacks

| Attack | Target | Element | Spd | Chant | Power | Effect |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- |
| Attack | Single enemy | Neutral | 1.00x | - | - | Plain hit that deals damage |
| Bible Thump | Single enemy | Bash | 0.85x | - | 0.4 | Plain hit that deals damage; Damage based on RES; Freeze (0.2); Silence (0.2) |
| War Cry | All allies | Neutral | 1.25x | - | - | ATK modifier (0.14) |
| Fireball | Single enemy | Fire | 1.50x | 1.15s | - | Magic power (70) |
| Honey | Single ally | Neutral | 1.00x | - | - | - |
| Wait and See | Self | Neutral | 0.90x | - | - | Speed modifier (0.1); Physical evasion modifier (0.1) |
| Take Break | None | -1 | 0.75x | - | - | - |

#### AI Behavior

**Opening Actions:**
- last skill used is Honey (slot 4) -> set 2 (stop)
- lowest HP ratio among allies <= 50 -> set 1 (stop)
**Action Sets:**
- **Set 0:** Attack (15%), Bible Thump (15%), War Cry (20%), Fireball (20%), Wait and See (10%), Take Break (20%)
  - *Condition:* War Cry (slot 2) was used 1 times or more -> Attack (slot 0)
- **Set 1:** Attack (10%), Fireball (10%), Honey (80%)
  - *Condition:* Honey (slot 4) aims at: ally with the lowest HP ratio
- **Set 2:** Take Break (100%)

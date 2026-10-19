# Classes

Progression tables, equipment access, weapon specialty modifiers, and skill trees for all 32 classes. Advanced classes with multiple prerequisite routes list independent growth tables for each path.

Classes are organized into five base lines across three tiers: Base (Tier 1), Intermediate (Tier 2, Level 15), and Advanced (Tier 3, Level 30). Six Advanced classes possess distinct growth tables depending on their intermediate class route.

## Fighter Line

### Fighter

- **Tier:** Base

### Usable Equipment

- **Weapon Types:** Axe (5), Dagger (7), Fan (1), Mace (4), Polearm (6), Sword (18)
- **Defensive Gear:** Accessory (41), Armor (20), Helm (19), Shield (18)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Sword | +1% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 54 | 14 | 5 | 3 | 3 | 2 | 7 | 5 |
| 10 | 165 | 36 | 14 | 11 | 8 | 9 | 15 | 12 |
| 20 | 288 | 61 | 24 | 20 | 14 | 16 | 23 | 18 |
| 30 | 411 | 86 | 33 | 29 | 20 | 24 | 32 | 25 |
| 40 | 534 | 110 | 43 | 38 | 26 | 32 | 40 | 32 |
| 50 | 658 | 135 | 53 | 48 | 31 | 39 | 49 | 38 |
| 60 | 781 | 160 | 63 | 57 | 37 | 47 | 57 | 45 |
| 70 | 904 | 184 | 73 | 66 | 43 | 54 | 66 | 52 |
| 80 | 1027 | 209 | 82 | 75 | 49 | 62 | 74 | 59 |
| 90 | 1150 | 234 | 92 | 84 | 55 | 70 | 83 | 65 |
| 99 | 1261 | 256 | 101 | 92 | 60 | 76 | 90 | 71 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Provoke | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| War Cry | Technique | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Raging Smash | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Sword Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Axe Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Lance Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Avenger | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Double Attack | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Paladin

- **Tier:** Intermediate (Promotion Route: Fighter)

### Usable Equipment

- **Weapon Types:** Axe (5), Dagger (6), Fan (2), Mace (3), Polearm (19), Sword (25)
- **Defensive Gear:** Accessory (42), Armor (20), Helm (19), Shield (27)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Sword | +2% |
| Weapon | Polearm | +3% |
| Shield | Shield | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 60 | 17 | 11 | 7 | 4 | 4 | 8 | 6 |
| 10 | 165 | 36 | 18 | 16 | 8 | 9 | 15 | 11 |
| 20 | 307 | 63 | 29 | 29 | 15 | 18 | 25 | 19 |
| 30 | 469 | 92 | 41 | 44 | 23 | 27 | 35 | 28 |
| 40 | 632 | 121 | 53 | 58 | 30 | 37 | 46 | 37 |
| 50 | 794 | 150 | 65 | 73 | 38 | 47 | 56 | 46 |
| 60 | 956 | 179 | 77 | 87 | 46 | 56 | 66 | 55 |
| 70 | 1118 | 207 | 88 | 101 | 53 | 66 | 76 | 64 |
| 80 | 1280 | 236 | 100 | 116 | 61 | 75 | 86 | 73 |
| 90 | 1443 | 265 | 112 | 130 | 69 | 85 | 97 | 82 |
| 99 | 1588 | 291 | 123 | 143 | 76 | 94 | 106 | 90 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Defender | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Shield Bash | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | Short |
| Cover | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Parry | Technique | 5 | 45 (3, 6, 9, 12, 15) | Self | None |
| Cross Slash | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Heal | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single ally | None |
| Mini Auto-Recovery | Passive | 5 | 15 (1, 2, 3, 4, 5) | - | - |
| Auto-Guard | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Berserker

- **Tier:** Intermediate (Promotion Route: Fighter)

### Usable Equipment

- **Weapon Types:** Axe (29), Dagger (8), Fan (1), Mace (5), Polearm (2), Sword (23)
- **Defensive Gear:** Accessory (43), Armor (23), Helm (20), Shield (22)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Sword | +2% |
| Weapon | Axe | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 58 | 18 | 11 | 5 | 4 | 3 | 9 | 6 |
| 10 | 163 | 37 | 18 | 12 | 10 | 9 | 16 | 12 |
| 20 | 298 | 64 | 30 | 29 | 15 | 17 | 26 | 20 |
| 30 | 441 | 93 | 44 | 43 | 24 | 26 | 37 | 29 |
| 40 | 584 | 122 | 58 | 57 | 33 | 35 | 49 | 39 |
| 50 | 728 | 151 | 72 | 70 | 42 | 44 | 60 | 48 |
| 60 | 871 | 180 | 86 | 84 | 51 | 53 | 71 | 58 |
| 70 | 1014 | 210 | 100 | 98 | 60 | 61 | 83 | 67 |
| 80 | 1157 | 239 | 114 | 112 | 69 | 70 | 94 | 77 |
| 90 | 1301 | 268 | 128 | 126 | 78 | 79 | 106 | 86 |
| 99 | 1430 | 294 | 141 | 138 | 86 | 87 | 116 | 95 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Aura Eliminate | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Berserk | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Frost Slash | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Mid |
| Geo Break | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Blood Rage | Magic | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Adaptation | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Preparation | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Dark Aura | Passive | 6 | 63 (3, 6, 9, 12, 15, 18) | - | - |

### Valkyrie

- **Tier:** Advanced (Promotion Route: Paladin)

### Usable Equipment

- **Weapon Types:** Axe (5), Dagger (6), Fan (2), Mace (4), Polearm (33), Sword (30)
- **Defensive Gear:** Accessory (48), Armor (23), Helm (22), Shield (30)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Sword | +3% |
| Weapon | Polearm | +5% |
| Shield | Shield | +3% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 60 | 17 | 11 | 7 | 4 | 4 | 8 | 6 |
| 10 | 165 | 36 | 18 | 16 | 8 | 9 | 15 | 11 |
| 20 | 312 | 65 | 29 | 29 | 15 | 18 | 25 | 20 |
| 30 | 469 | 92 | 41 | 44 | 23 | 27 | 35 | 27 |
| 40 | 676 | 125 | 55 | 61 | 34 | 42 | 48 | 38 |
| 50 | 882 | 157 | 70 | 78 | 44 | 56 | 61 | 50 |
| 60 | 1089 | 190 | 84 | 95 | 54 | 71 | 75 | 61 |
| 70 | 1295 | 223 | 99 | 112 | 65 | 85 | 89 | 72 |
| 80 | 1502 | 256 | 113 | 129 | 75 | 100 | 102 | 84 |
| 90 | 1709 | 288 | 127 | 145 | 86 | 115 | 116 | 95 |
| 99 | 1895 | 318 | 140 | 161 | 95 | 128 | 128 | 105 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Material Guard | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Spell Guard | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Gust Thrust | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Daedalus Attack | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Random enemies | Short |
| Ether Strike | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Piercing | Mid |
| Circle Heal | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Protect | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Moon Curtain | Magic | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Auto-Refresh | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Guts | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Absolute Attack | Passive | 1 | 20 | - | - |
| Imperial Guard | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Samurai

- **Tier:** Advanced (Promotion Route: Paladin or Berserker)

### Usable Equipment

- **Weapon Types:** Axe (1), Dagger (6), Fan (1), Katana (30), Mace (1), Polearm (10), Sword (21)
- **Defensive Gear:** Accessory (50), Armor (24), Helm (21), Shield (19)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Promotion Route | Slot | Equipment Type | Modifier |
| --- | --- | --- | --- |
| From Paladin | Weapon | Sword | +2% |
| From Paladin | Shield | Shield | +2% |
| From Paladin | Weapon | Katana | +3% |
| From Berserker | Weapon | Sword | +2% |
| From Berserker | Weapon | Axe | +2% |
| From Berserker | Weapon | Katana | +3% |

### Stat Growth

#### Route from Paladin

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 60 | 17 | 11 | 7 | 4 | 4 | 8 | 6 |
| 10 | 165 | 36 | 18 | 16 | 8 | 9 | 15 | 11 |
| 20 | 312 | 66 | 29 | 29 | 15 | 18 | 25 | 20 |
| 30 | 469 | 92 | 41 | 44 | 23 | 27 | 37 | 27 |
| 40 | 631 | 127 | 61 | 57 | 31 | 37 | 52 | 41 |
| 50 | 793 | 162 | 81 | 69 | 39 | 47 | 67 | 54 |
| 60 | 955 | 198 | 101 | 82 | 47 | 57 | 81 | 68 |
| 70 | 1117 | 233 | 121 | 95 | 55 | 67 | 96 | 82 |
| 80 | 1279 | 268 | 141 | 108 | 63 | 78 | 111 | 96 |
| 90 | 1441 | 303 | 161 | 120 | 70 | 88 | 126 | 109 |
| 99 | 1587 | 335 | 179 | 132 | 78 | 97 | 139 | 122 |

#### Route from Berserker

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 58 | 18 | 11 | 5 | 4 | 3 | 9 | 6 |
| 10 | 163 | 38 | 18 | 12 | 10 | 9 | 16 | 12 |
| 20 | 292 | 65 | 32 | 28 | 15 | 17 | 26 | 19 |
| 30 | 441 | 93 | 44 | 43 | 24 | 26 | 39 | 28 |
| 40 | 594 | 130 | 65 | 55 | 33 | 34 | 55 | 42 |
| 50 | 747 | 167 | 85 | 67 | 42 | 42 | 70 | 57 |
| 60 | 900 | 204 | 106 | 79 | 51 | 51 | 85 | 71 |
| 70 | 1053 | 241 | 126 | 91 | 60 | 59 | 101 | 86 |
| 80 | 1207 | 278 | 147 | 104 | 69 | 67 | 117 | 100 |
| 90 | 1360 | 314 | 167 | 116 | 79 | 75 | 132 | 114 |
| 99 | 1497 | 348 | 185 | 126 | 87 | 83 | 146 | 127 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Backward Swing | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Last Stand | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Halving Slice | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | Short |
| Armor Penetration | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Onikagura | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | Short |
| Moonlight Purgatory | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Katana Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Mind's Eye | Passive | 5 | 45 (3, 6, 9, 12, 15) | - | - |
| Triple Attack | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Flowing Water Stance | Passive | 5 | 25 (1, 3, 5, 7, 9) | - | - |

### Dark Lord

- **Tier:** Advanced (Promotion Route: Berserker)

### Usable Equipment

- **Weapon Types:** Axe (32), Dagger (8), Fan (1), Mace (5), Polearm (8), Sword (27)
- **Defensive Gear:** Accessory (48), Armor (26), Helm (22), Shield (25)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Sword | +2% |
| Weapon | Axe | +5% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 58 | 18 | 11 | 5 | 4 | 3 | 9 | 6 |
| 10 | 163 | 38 | 18 | 12 | 10 | 9 | 16 | 12 |
| 20 | 300 | 64 | 31 | 29 | 15 | 17 | 26 | 19 |
| 30 | 441 | 93 | 44 | 43 | 24 | 26 | 40 | 28 |
| 40 | 620 | 126 | 62 | 58 | 37 | 38 | 57 | 41 |
| 50 | 800 | 160 | 79 | 73 | 50 | 49 | 74 | 54 |
| 60 | 979 | 193 | 97 | 88 | 63 | 61 | 91 | 66 |
| 70 | 1159 | 227 | 114 | 103 | 76 | 73 | 108 | 79 |
| 80 | 1338 | 260 | 132 | 118 | 89 | 85 | 125 | 92 |
| 90 | 1517 | 293 | 150 | 132 | 102 | 96 | 142 | 105 |
| 99 | 1679 | 323 | 165 | 146 | 114 | 107 | 157 | 116 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Attract | Technique | 5 | 30 (2, 4, 6, 8, 10) | All enemies | None |
| Blood Drain | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Soul Drain | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Megaton Press | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Shock Spiral | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | Short |
| Power Charge | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Life Bring | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Brave | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Grudge Accumulator | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Dark Quest | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| First Grid | Passive | 1 | 10 | - | - |

## Scout Line

### Scout

- **Tier:** Base

### Usable Equipment

- **Weapon Types:** Axe (4), Bow (6), Dagger (24), Fan (1), Gun (2), Katana (1), Mace (4), Projectile (5), Sword (3)
- **Defensive Gear:** Accessory (39), Armor (17), Helm (14), Shield (11)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +1% |
| Weapon | Bow | +1% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 3 | 4 | 3 | 9 | 7 |
| 10 | 140 | 44 | 12 | 9 | 10 | 11 | 18 | 16 |
| 20 | 245 | 75 | 20 | 16 | 17 | 19 | 27 | 26 |
| 30 | 349 | 106 | 29 | 23 | 23 | 27 | 37 | 35 |
| 40 | 454 | 137 | 37 | 30 | 30 | 36 | 47 | 45 |
| 50 | 559 | 167 | 46 | 36 | 37 | 44 | 57 | 55 |
| 60 | 663 | 198 | 54 | 43 | 44 | 52 | 66 | 65 |
| 70 | 768 | 229 | 63 | 50 | 50 | 60 | 76 | 75 |
| 80 | 872 | 260 | 71 | 57 | 57 | 68 | 86 | 84 |
| 90 | 977 | 291 | 80 | 64 | 64 | 77 | 95 | 94 |
| 99 | 1071 | 319 | 87 | 70 | 70 | 84 | 104 | 103 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Gold Steal | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Sharp Stab | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Evade | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Cleanse | Technique | 5 | 25 (1, 3, 5, 7, 9) | Single ally | None |
| Poison Shot | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Long |
| Dagger Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Elusiveness | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Lucky Me | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Archer

- **Tier:** Intermediate (Promotion Route: Scout)

### Usable Equipment

- **Weapon Types:** Axe (1), Bow (27), Dagger (12), Fan (1), Gun (3), Projectile (3), Sword (3)
- **Defensive Gear:** Accessory (41), Armor (16), Helm (15), Shield (10)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +2% |
| Weapon | Bow | +3% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 3 | 4 | 3 | 9 | 7 |
| 10 | 152 | 48 | 13 | 12 | 10 | 11 | 22 | 18 |
| 20 | 251 | 77 | 24 | 21 | 17 | 18 | 34 | 28 |
| 30 | 369 | 112 | 35 | 30 | 24 | 27 | 48 | 40 |
| 40 | 488 | 148 | 45 | 40 | 31 | 36 | 62 | 52 |
| 50 | 606 | 183 | 55 | 50 | 38 | 45 | 76 | 64 |
| 60 | 724 | 219 | 66 | 59 | 45 | 54 | 90 | 76 |
| 70 | 843 | 254 | 76 | 69 | 53 | 63 | 103 | 87 |
| 80 | 961 | 290 | 87 | 78 | 60 | 72 | 117 | 99 |
| 90 | 1079 | 325 | 97 | 88 | 67 | 81 | 131 | 111 |
| 99 | 1186 | 357 | 106 | 97 | 73 | 89 | 144 | 122 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Freeze Shot | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Long |
| Paralysis Shot | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Long |
| Gravity Shot | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Long |
| Arrow Rain | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | Long |
| Bow Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Caution | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Assassin

- **Tier:** Intermediate (Promotion Route: Scout)

### Usable Equipment

- **Weapon Types:** Axe (5), Bow (3), Dagger (31), Fan (1), Gun (1), Katana (2), Mace (3), Projectile (7), Staff (1), Sword (3)
- **Defensive Gear:** Accessory (41), Armor (18), Helm (16), Shield (11)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +3% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 5 | 3 | 4 | 3 | 9 | 7 |
| 10 | 158 | 46 | 14 | 11 | 10 | 11 | 21 | 18 |
| 20 | 254 | 76 | 24 | 21 | 17 | 18 | 32 | 29 |
| 30 | 378 | 109 | 33 | 30 | 25 | 27 | 45 | 42 |
| 40 | 502 | 142 | 43 | 39 | 34 | 35 | 58 | 55 |
| 50 | 626 | 175 | 53 | 48 | 42 | 43 | 71 | 68 |
| 60 | 750 | 208 | 63 | 57 | 50 | 52 | 84 | 81 |
| 70 | 875 | 241 | 73 | 66 | 59 | 60 | 97 | 93 |
| 80 | 999 | 274 | 82 | 75 | 67 | 69 | 110 | 106 |
| 90 | 1123 | 307 | 92 | 84 | 75 | 77 | 123 | 119 |
| 99 | 1234 | 336 | 101 | 92 | 83 | 85 | 134 | 131 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Sleep Sting | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Silence Sting | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Stun Sting | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Adaptation | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Murder | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Awareness | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Sniper

- **Tier:** Advanced (Promotion Route: Archer)

### Usable Equipment

- **Weapon Types:** Axe (1), Bow (32), Dagger (13), Fan (1), Gun (7), Projectile (3), Sword (3)
- **Defensive Gear:** Accessory (45), Armor (19), Helm (17), Shield (10)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +2% |
| Weapon | Bow | +5% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 3 | 4 | 3 | 9 | 7 |
| 10 | 164 | 52 | 16 | 13 | 12 | 11 | 25 | 19 |
| 20 | 244 | 75 | 23 | 21 | 17 | 18 | 35 | 29 |
| 30 | 369 | 112 | 33 | 30 | 24 | 27 | 48 | 40 |
| 40 | 500 | 152 | 46 | 41 | 32 | 37 | 66 | 54 |
| 50 | 631 | 192 | 59 | 53 | 41 | 48 | 84 | 67 |
| 60 | 762 | 231 | 71 | 64 | 49 | 58 | 101 | 81 |
| 70 | 893 | 271 | 84 | 75 | 58 | 69 | 119 | 95 |
| 80 | 1024 | 311 | 97 | 87 | 66 | 79 | 137 | 109 |
| 90 | 1155 | 351 | 110 | 98 | 74 | 89 | 155 | 122 |
| 99 | 1273 | 387 | 121 | 108 | 82 | 99 | 171 | 135 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Aim | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Self | None |
| Chain Spike | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Long |
| Guided Shot | Technique | 5 | 25 (1, 3, 5, 7, 9) | Single enemy | Long |
| Spiral Arrow | Technique | 5 | 45 (3, 6, 9, 12, 15) | Single enemy | Long |
| Star Dust Arrow | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | None | Long |
| Divine Cannon | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Piercing | Long |
| Warning Shot | Passive | 5 | 45 (3, 6, 9, 12, 15) | - | - |
| Support Shot | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Treasure Hunter

- **Tier:** Advanced (Promotion Route: Archer or Assassin)

### Usable Equipment

- **Weapon Types:** Axe (4), Bow (11), Dagger (31), Fan (1), Gun (3), Katana (1), Mace (2), Projectile (6), Sword (3), Whip (15)
- **Defensive Gear:** Accessory (47), Armor (21), Helm (17), Shield (12)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Promotion Route | Slot | Equipment Type | Modifier |
| --- | --- | --- | --- |
| From Archer | Weapon | Dagger | +3% |
| From Archer | Weapon | Bow | +3% |
| From Assassin | Weapon | Dagger | +5% |
| From Assassin | Weapon | Bow | +2% |
| From Assassin | Weapon | Whip | +3% |

### Stat Growth

#### Route from Archer

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 3 | 4 | 3 | 9 | 7 |
| 10 | 181 | 52 | 13 | 14 | 14 | 11 | 24 | 20 |
| 20 | 244 | 75 | 23 | 21 | 19 | 18 | 35 | 29 |
| 30 | 369 | 112 | 33 | 30 | 24 | 27 | 47 | 40 |
| 40 | 520 | 152 | 43 | 43 | 35 | 39 | 64 | 54 |
| 50 | 670 | 193 | 53 | 55 | 46 | 52 | 81 | 68 |
| 60 | 820 | 233 | 63 | 68 | 57 | 64 | 97 | 83 |
| 70 | 971 | 274 | 73 | 80 | 68 | 76 | 114 | 97 |
| 80 | 1122 | 314 | 84 | 93 | 79 | 89 | 131 | 111 |
| 90 | 1272 | 354 | 94 | 106 | 90 | 101 | 148 | 125 |
| 99 | 1407 | 391 | 103 | 117 | 100 | 112 | 163 | 138 |

#### Route from Assassin

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 3 | 4 | 3 | 9 | 7 |
| 10 | 158 | 46 | 13 | 11 | 10 | 11 | 21 | 18 |
| 20 | 254 | 76 | 24 | 21 | 17 | 18 | 32 | 29 |
| 30 | 378 | 109 | 32 | 30 | 25 | 27 | 47 | 41 |
| 40 | 529 | 148 | 42 | 42 | 36 | 39 | 63 | 55 |
| 50 | 681 | 187 | 52 | 53 | 46 | 50 | 79 | 70 |
| 60 | 832 | 226 | 62 | 65 | 57 | 62 | 95 | 84 |
| 70 | 984 | 265 | 72 | 77 | 68 | 73 | 111 | 99 |
| 80 | 1135 | 305 | 82 | 89 | 78 | 85 | 127 | 113 |
| 90 | 1286 | 344 | 92 | 100 | 89 | 96 | 142 | 127 |
| 99 | 1423 | 379 | 101 | 111 | 99 | 106 | 157 | 140 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Item Steal | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Pursuit Stab | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | Short |
| Fleet Foot | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Self | None |
| Chain Spike | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Long |
| Identify | Technique | 5 | 30 (2, 4, 6, 8, 10) | Item | None |
| Trap Search | Technique | 10 | 35 (1, 2, 2, 3, 3, 4, 4, 5, 5, 6) | All allies | None |
| Treasure Search | Technique | 1 | 5 | Self | None |
| Hard Whipping | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | Mid |
| Light | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Whistle | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Triple Attack | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Treasure Hunt | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Recycle | Passive | 5 | 45 (3, 6, 9, 12, 15) | - | - |
| Item Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Negotiate | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Kunoichi

- **Tier:** Advanced (Promotion Route: Assassin)

### Usable Equipment

- **Weapon Types:** Axe (8), Bow (3), Dagger (29), Fan (3), Katana (16), Mace (3), Projectile (15), Staff (1), Sword (3)
- **Defensive Gear:** Accessory (46), Armor (20), Helm (21), Shield (12)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +3% |
| Weapon | Katana | +3% |
| Weapon | Projectile | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 3 | 4 | 3 | 9 | 7 |
| 10 | 158 | 46 | 13 | 11 | 10 | 11 | 21 | 18 |
| 20 | 254 | 76 | 24 | 21 | 17 | 18 | 32 | 29 |
| 30 | 378 | 109 | 32 | 30 | 25 | 27 | 47 | 41 |
| 40 | 518 | 146 | 43 | 40 | 35 | 37 | 64 | 57 |
| 50 | 658 | 183 | 53 | 50 | 45 | 47 | 82 | 72 |
| 60 | 799 | 219 | 63 | 59 | 55 | 57 | 99 | 88 |
| 70 | 939 | 256 | 74 | 69 | 65 | 67 | 116 | 104 |
| 80 | 1079 | 293 | 84 | 79 | 75 | 77 | 134 | 120 |
| 90 | 1219 | 330 | 95 | 89 | 85 | 87 | 151 | 135 |
| 99 | 1345 | 363 | 104 | 98 | 94 | 96 | 166 | 149 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Phoenix | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | Long |
| Ninja Piledriver | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Shadow Clone | Magic | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Shadow Sew | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Light Scroll | Magic | 5 | 25 (1, 3, 5, 7, 9) | All enemies | None |
| Fire Scroll | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Water Scroll | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Lightning Scroll | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Wind Scroll | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Earth Scroll | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Katana Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Projectile Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Dual Wield | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Barrage | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |

## Magic User Line

### Magic User

- **Tier:** Base

### Usable Equipment

- **Weapon Types:** Dagger (5), Fan (1), Gun (1), Mace (6), Polearm (1), Projectile (2), Staff (10), Tome (6)
- **Defensive Gear:** Accessory (38), Armor (14), Helm (14), Shield (9)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Staff | +1% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 109 | 61 | 8 | 8 | 17 | 14 | 10 | 13 |
| 20 | 191 | 106 | 13 | 13 | 27 | 23 | 18 | 21 |
| 30 | 272 | 150 | 18 | 18 | 36 | 32 | 25 | 30 |
| 40 | 354 | 195 | 23 | 23 | 46 | 40 | 32 | 39 |
| 50 | 435 | 239 | 28 | 28 | 56 | 49 | 39 | 47 |
| 60 | 517 | 284 | 33 | 34 | 66 | 58 | 46 | 56 |
| 70 | 598 | 328 | 38 | 39 | 76 | 67 | 54 | 64 |
| 80 | 680 | 373 | 43 | 44 | 85 | 76 | 61 | 73 |
| 90 | 761 | 417 | 48 | 49 | 95 | 84 | 68 | 82 |
| 99 | 835 | 457 | 53 | 54 | 104 | 92 | 75 | 89 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Fireball | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Ice Edge | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Thunderbolt | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Air Cutter | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Stone Hammer | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Poison | Magic | 5 | 25 (1, 3, 5, 7, 9) | All enemies | None |
| Heal | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single ally | None |

### Sorceress

- **Tier:** Intermediate (Promotion Route: Magic User)

### Usable Equipment

- **Weapon Types:** Dagger (5), Fan (1), Gun (1), Mace (3), Polearm (1), Projectile (2), Staff (17)
- **Defensive Gear:** Accessory (38), Armor (14), Helm (15), Shield (9)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Staff | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 117 | 65 | 8 | 10 | 19 | 16 | 11 | 13 |
| 20 | 195 | 113 | 13 | 16 | 31 | 25 | 19 | 22 |
| 30 | 285 | 172 | 18 | 23 | 45 | 37 | 28 | 31 |
| 40 | 375 | 231 | 23 | 31 | 59 | 48 | 37 | 40 |
| 50 | 464 | 290 | 29 | 39 | 73 | 60 | 45 | 49 |
| 60 | 554 | 349 | 34 | 46 | 87 | 72 | 54 | 58 |
| 70 | 644 | 408 | 39 | 54 | 101 | 83 | 63 | 67 |
| 80 | 734 | 467 | 44 | 61 | 115 | 95 | 72 | 76 |
| 90 | 824 | 526 | 50 | 69 | 129 | 107 | 80 | 85 |
| 99 | 904 | 579 | 55 | 76 | 142 | 117 | 88 | 93 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Fire Blast | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Ice Storm | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Thunder Chain | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Air Turbulence | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Stone Shower | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Blood Absorb | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Magic Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Auto-Refresh | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Concentrate | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Critical Magic | Passive | 1 | 10 | - | - |

### Enchantress

- **Tier:** Intermediate (Promotion Route: Magic User)

### Usable Equipment

- **Weapon Types:** Dagger (5), Fan (3), Gun (1), Mace (9), Polearm (1), Projectile (5), Staff (13), Tome (7)
- **Defensive Gear:** Accessory (40), Armor (15), Helm (15), Shield (12)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Tome | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 109 | 65 | 8 | 9 | 19 | 15 | 13 | 13 |
| 20 | 201 | 111 | 13 | 16 | 31 | 26 | 22 | 22 |
| 30 | 302 | 166 | 19 | 24 | 44 | 39 | 32 | 32 |
| 40 | 403 | 221 | 25 | 33 | 57 | 53 | 41 | 42 |
| 50 | 504 | 276 | 30 | 41 | 71 | 67 | 51 | 51 |
| 60 | 605 | 331 | 36 | 49 | 84 | 80 | 61 | 61 |
| 70 | 706 | 387 | 42 | 58 | 97 | 94 | 70 | 71 |
| 80 | 807 | 442 | 48 | 66 | 110 | 107 | 80 | 81 |
| 90 | 908 | 497 | 53 | 74 | 124 | 121 | 90 | 91 |
| 99 | 998 | 547 | 59 | 82 | 136 | 133 | 98 | 99 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Holy Prayer | Technique | 5 | 15 (1, 2, 3, 4, 5) | Self | None |
| Stun | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Freeze | Magic | 5 | 30 (2, 4, 6, 8, 10) | All enemies | None |
| Paralyze | Magic | 5 | 30 (2, 4, 6, 8, 10) | All enemies | None |
| Silence | Magic | 5 | 30 (2, 4, 6, 8, 10) | All enemies | None |
| Fire Enchant | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single ally | None |
| Water Enchant | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single ally | None |
| Lightning Enchant | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single ally | None |
| Wind Enchant | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single ally | None |
| Earth Enchant | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single ally | None |
| Mini Circle Nurse | Magic | 8 | 32 (1, 1, 3, 3, 5, 5, 7, 7) | Ally row | None |
| Divine Shield | Magic | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Return | Magic | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Circle Brave | Magic | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Circle Protect | Magic | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Heal Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Mini Auto-Refresh | Passive | 5 | 15 (1, 2, 3, 4, 5) | - | - |
| Adaptation | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Fast Cast | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Priestess

- **Tier:** Intermediate (Promotion Route: Magic User)

### Usable Equipment

- **Weapon Types:** Dagger (2), Fan (3), Mace (8), Polearm (1), Projectile (5), Staff (14), Tome (14)
- **Defensive Gear:** Accessory (39), Armor (15), Helm (15), Shield (12)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Mace | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 108 | 64 | 8 | 9 | 19 | 17 | 12 | 13 |
| 20 | 201 | 111 | 13 | 16 | 30 | 27 | 21 | 22 |
| 30 | 304 | 167 | 19 | 25 | 43 | 42 | 30 | 32 |
| 40 | 407 | 224 | 25 | 34 | 56 | 57 | 39 | 41 |
| 50 | 510 | 280 | 31 | 43 | 68 | 72 | 48 | 51 |
| 60 | 613 | 336 | 37 | 52 | 81 | 87 | 57 | 61 |
| 70 | 715 | 393 | 43 | 60 | 94 | 103 | 67 | 70 |
| 80 | 818 | 449 | 49 | 69 | 107 | 118 | 76 | 80 |
| 90 | 921 | 505 | 55 | 78 | 119 | 133 | 85 | 90 |
| 99 | 1014 | 556 | 60 | 86 | 131 | 147 | 93 | 98 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Fire Blast | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Ice Storm | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Thunder Chain | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Air Turbulence | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Stone Shower | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Slow | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Circle Heal | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Nurse | Magic | 8 | 20 (1, 1, 2, 2, 3, 3, 4, 4) | Single ally | None |
| Resurrect | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Divine Shield | Magic | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Light | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Return | Magic | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Heal Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Mini Auto-Recovery | Passive | 5 | 15 (1, 2, 3, 4, 5) | - | - |
| Mini Auto-Refresh | Passive | 5 | 15 (1, 2, 3, 4, 5) | - | - |
| Fast Cast | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Witch

- **Tier:** Advanced (Promotion Route: Sorceress)

### Usable Equipment

- **Weapon Types:** Dagger (6), Fan (1), Gun (1), Mace (3), Polearm (1), Projectile (2), Staff (17), Tome (4)
- **Defensive Gear:** Accessory (43), Armor (19), Helm (16), Shield (9)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Staff | +5% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 117 | 65 | 8 | 10 | 19 | 16 | 11 | 13 |
| 20 | 195 | 113 | 13 | 16 | 31 | 25 | 19 | 22 |
| 30 | 285 | 172 | 18 | 23 | 47 | 37 | 28 | 31 |
| 40 | 386 | 245 | 24 | 32 | 66 | 50 | 39 | 41 |
| 50 | 486 | 319 | 30 | 41 | 85 | 63 | 50 | 51 |
| 60 | 587 | 392 | 36 | 51 | 104 | 76 | 62 | 61 |
| 70 | 687 | 466 | 42 | 60 | 123 | 89 | 73 | 71 |
| 80 | 787 | 539 | 48 | 69 | 143 | 102 | 84 | 82 |
| 90 | 888 | 612 | 54 | 78 | 162 | 115 | 95 | 92 |
| 99 | 978 | 678 | 59 | 86 | 179 | 127 | 105 | 101 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Loose Spirit | Technique | 5 | 45 (3, 6, 9, 12, 15) | Self | None |
| Inferno | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Crimson Flare | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Diamond Dust | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Cocytus | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Lightning | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Muon Plasma | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Tornado | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Tempest | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Meteor | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Gaia Crush | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Soul Absorb | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Slow | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Fast Cast | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Economy | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Nirvana | Passive | 5 | 25 (1, 3, 5, 7, 9) | - | - |

### Magical Princess

- **Tier:** Advanced (Promotion Route: Sorceress or Enchantress)

### Usable Equipment

- **Weapon Types:** Bow (10), Dagger (6), Fan (3), Gun (1), Mace (11), Polearm (2), Projectile (2), Staff (9), Sword (22)
- **Defensive Gear:** Accessory (49), Armor (25), Helm (20), Shield (18)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Promotion Route | Slot | Equipment Type | Modifier |
| --- | --- | --- | --- |
| From Sorceress | Weapon | Staff | +2% |
| From Sorceress | Weapon | Sword | +4% |
| From Enchantress | Weapon | Tome | +2% |
| From Enchantress | Weapon | Sword | +4% |

### Stat Growth

#### Route from Sorceress

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 117 | 65 | 8 | 10 | 19 | 16 | 11 | 13 |
| 20 | 195 | 113 | 13 | 16 | 31 | 25 | 19 | 22 |
| 30 | 285 | 172 | 21 | 23 | 46 | 37 | 36 | 31 |
| 40 | 448 | 235 | 36 | 34 | 61 | 51 | 50 | 43 |
| 50 | 611 | 298 | 51 | 46 | 76 | 64 | 65 | 56 |
| 60 | 774 | 361 | 66 | 57 | 91 | 78 | 79 | 68 |
| 70 | 937 | 424 | 81 | 69 | 106 | 92 | 93 | 80 |
| 80 | 1100 | 487 | 96 | 80 | 121 | 106 | 108 | 93 |
| 90 | 1263 | 550 | 111 | 91 | 135 | 119 | 122 | 105 |
| 99 | 1410 | 607 | 125 | 102 | 149 | 132 | 135 | 116 |

#### Route from Enchantress

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 109 | 65 | 8 | 9 | 19 | 15 | 13 | 13 |
| 20 | 201 | 111 | 16 | 16 | 31 | 26 | 23 | 22 |
| 30 | 302 | 166 | 23 | 24 | 44 | 39 | 38 | 32 |
| 40 | 472 | 223 | 39 | 36 | 58 | 54 | 53 | 45 |
| 50 | 642 | 280 | 55 | 48 | 71 | 68 | 68 | 58 |
| 60 | 812 | 336 | 71 | 60 | 85 | 83 | 83 | 70 |
| 70 | 982 | 393 | 87 | 72 | 99 | 98 | 98 | 83 |
| 80 | 1152 | 450 | 103 | 84 | 113 | 113 | 114 | 96 |
| 90 | 1322 | 507 | 119 | 96 | 126 | 127 | 129 | 109 |
| 99 | 1475 | 558 | 133 | 107 | 139 | 140 | 142 | 120 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Cover | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Magical Slash | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | Short |
| Magic Barrier | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Magical Change | Technique | 5 | 45 (3, 6, 9, 12, 15) | Self | None |
| Magical Spark | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Accelerator | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Illusion | Magic | 3 | 18 (3, 6, 9) | Self | None |
| Rainbow Flash | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | None |
| Sword Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Double Attack | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Guts | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Sage

- **Tier:** Advanced (Promotion Route: Enchantress or Priestess)

### Usable Equipment

- **Weapon Types:** Dagger (3), Fan (5), Mace (9), Polearm (1), Projectile (5), Staff (14), Tome (16)
- **Defensive Gear:** Accessory (48), Armor (19), Helm (16), Shield (13)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Promotion Route | Slot | Equipment Type | Modifier |
| --- | --- | --- | --- |
| From Enchantress | Weapon | Staff | +2% |
| From Enchantress | Weapon | Tome | +5% |
| From Priestess | Weapon | Staff | +3% |
| From Priestess | Weapon | Tome | +3% |

### Stat Growth

#### Route from Enchantress

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 109 | 65 | 8 | 9 | 19 | 15 | 13 | 13 |
| 20 | 201 | 111 | 16 | 16 | 31 | 26 | 23 | 22 |
| 30 | 302 | 166 | 19 | 24 | 44 | 39 | 36 | 32 |
| 40 | 440 | 233 | 26 | 35 | 61 | 54 | 48 | 43 |
| 50 | 578 | 301 | 33 | 45 | 77 | 69 | 61 | 54 |
| 60 | 717 | 368 | 40 | 56 | 94 | 85 | 73 | 65 |
| 70 | 855 | 435 | 47 | 67 | 110 | 100 | 85 | 76 |
| 80 | 993 | 503 | 55 | 77 | 127 | 115 | 98 | 88 |
| 90 | 1131 | 570 | 62 | 88 | 144 | 130 | 110 | 99 |
| 99 | 1256 | 630 | 68 | 98 | 159 | 144 | 121 | 109 |

#### Route from Priestess

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 108 | 64 | 8 | 9 | 19 | 17 | 13 | 13 |
| 20 | 201 | 111 | 13 | 16 | 30 | 27 | 26 | 22 |
| 30 | 304 | 167 | 19 | 25 | 43 | 42 | 39 | 32 |
| 40 | 445 | 237 | 27 | 36 | 59 | 58 | 52 | 43 |
| 50 | 585 | 307 | 34 | 47 | 74 | 74 | 65 | 53 |
| 60 | 725 | 378 | 42 | 58 | 90 | 90 | 78 | 64 |
| 70 | 866 | 448 | 49 | 69 | 106 | 106 | 91 | 75 |
| 80 | 1007 | 518 | 57 | 80 | 122 | 122 | 105 | 85 |
| 90 | 1147 | 588 | 64 | 91 | 137 | 138 | 118 | 96 |
| 99 | 1273 | 651 | 71 | 101 | 151 | 152 | 129 | 106 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Identify | Technique | 5 | 30 (2, 4, 6, 8, 10) | Item | None |
| Bible Thump | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Sleep | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Petrify | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Death | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| Terrorize | Magic | 5 | 30 (2, 4, 6, 8, 10) | Enemy row | None |
| Dispel | Magic | 5 | 25 (1, 3, 5, 7, 9) | All enemies | None |
| Stab Guard | Magic | 5 | 25 (1, 3, 5, 7, 9) | Ally row | None |
| Slash Guard | Magic | 5 | 25 (1, 3, 5, 7, 9) | Ally row | None |
| Bash Guard | Magic | 5 | 25 (1, 3, 5, 7, 9) | Ally row | None |
| Sun Veil | Magic | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Accelerator | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Amplify | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single ally | None |
| Prism Dawn | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Piercing | None |
| Esarhaddon | Passive | 6 | 36 (1, 3, 5, 7, 9, 11) | - | - |
| Economy | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

### Bishop

- **Tier:** Advanced (Promotion Route: Priestess)

### Usable Equipment

- **Weapon Types:** Dagger (3), Fan (3), Mace (13), Polearm (1), Projectile (5), Staff (14), Tome (15)
- **Defensive Gear:** Accessory (46), Armor (19), Helm (16), Shield (13)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Staff | +2% |
| Weapon | Mace | +3% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 36 | 21 | 3 | 3 | 8 | 6 | 4 | 5 |
| 10 | 108 | 64 | 8 | 9 | 19 | 17 | 13 | 13 |
| 20 | 201 | 111 | 13 | 16 | 30 | 27 | 26 | 22 |
| 30 | 304 | 167 | 19 | 25 | 43 | 42 | 39 | 32 |
| 40 | 431 | 236 | 28 | 35 | 58 | 59 | 49 | 43 |
| 50 | 557 | 306 | 37 | 45 | 73 | 77 | 59 | 53 |
| 60 | 683 | 375 | 47 | 56 | 88 | 94 | 68 | 63 |
| 70 | 810 | 445 | 56 | 66 | 103 | 111 | 78 | 74 |
| 80 | 936 | 514 | 65 | 76 | 118 | 129 | 88 | 84 |
| 90 | 1063 | 583 | 74 | 86 | 132 | 146 | 98 | 95 |
| 99 | 1177 | 646 | 82 | 95 | 146 | 161 | 107 | 104 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Holy Gavel | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Justice | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Shine Curse | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Full Heal | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Circle Nurse | Magic | 8 | 36 (1, 2, 3, 4, 5, 6, 7, 8) | All allies | None |
| Moon Curtain | Magic | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Insurance | Magic | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Mace Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Double Attack | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |

## Maid Line

### Maid

- **Tier:** Base

### Usable Equipment

- **Weapon Types:** Axe (2), Dagger (8), Fan (5), Gun (2), Mace (4), Polearm (1), Projectile (2)
- **Defensive Gear:** Accessory (42), Armor (17), Helm (16), Shield (8)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Accessory | Accessory | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 38 | 0 | 3 | 3 | 5 | 5 | 5 | 4 |
| 10 | 120 | 10 | 9 | 9 | 9 | 12 | 12 | 9 |
| 20 | 211 | 22 | 15 | 15 | 14 | 20 | 19 | 16 |
| 30 | 302 | 33 | 21 | 21 | 18 | 27 | 27 | 22 |
| 40 | 394 | 44 | 27 | 27 | 23 | 35 | 34 | 28 |
| 50 | 485 | 56 | 33 | 33 | 28 | 43 | 42 | 34 |
| 60 | 576 | 67 | 40 | 40 | 32 | 50 | 49 | 40 |
| 70 | 667 | 79 | 46 | 46 | 37 | 58 | 57 | 46 |
| 80 | 758 | 90 | 52 | 52 | 41 | 66 | 64 | 52 |
| 90 | 850 | 101 | 58 | 58 | 46 | 74 | 72 | 58 |
| 99 | 932 | 112 | 64 | 64 | 50 | 80 | 78 | 64 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| First Aid | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Cook | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Self-Sacrifice | Technique | 5 | 25 (1, 3, 5, 7, 9) | Single ally | None |
| Clean | Technique | 5 | 25 (1, 3, 5, 7, 9) | Self | None |
| Lullaby | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single enemy | None |
| Generous Heart | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Maid Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |

### Bard

- **Tier:** Intermediate (Promotion Route: Maid)

### Usable Equipment

- **Weapon Types:** Bow (4), Dagger (7), Fan (5), Mace (6), Microphone (14), Polearm (1), Sword (1), Whip (1)
- **Defensive Gear:** Accessory (43), Armor (18), Helm (18), Shield (8)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Accessory | Accessory | +2% |
| Weapon | Microphone | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 38 | 0 | 3 | 3 | 5 | 5 | 5 | 4 |
| 10 | 120 | 10 | 9 | 9 | 9 | 12 | 11 | 9 |
| 20 | 213 | 23 | 15 | 18 | 14 | 22 | 18 | 17 |
| 30 | 309 | 36 | 22 | 27 | 20 | 33 | 27 | 24 |
| 40 | 405 | 49 | 28 | 35 | 27 | 45 | 36 | 31 |
| 50 | 501 | 61 | 35 | 44 | 33 | 57 | 45 | 38 |
| 60 | 597 | 74 | 41 | 52 | 39 | 68 | 54 | 45 |
| 70 | 693 | 87 | 48 | 61 | 46 | 80 | 64 | 53 |
| 80 | 789 | 101 | 54 | 69 | 52 | 91 | 73 | 60 |
| 90 | 885 | 114 | 61 | 78 | 58 | 103 | 82 | 67 |
| 99 | 971 | 125 | 67 | 85 | 64 | 113 | 90 | 73 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Spiritual Fantasia | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Sacred Hymn | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Replenishing Carol | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Blissful Chorale | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Experience Paean | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Song Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |

### Dancer

- **Tier:** Intermediate (Promotion Route: Maid)

### Usable Equipment

- **Weapon Types:** Bow (4), Dagger (9), Fan (7), Instrument (15), Mace (4), Polearm (1), Whip (1)
- **Defensive Gear:** Accessory (44), Armor (19), Helm (19), Shield (8)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Accessory | Accessory | +2% |
| Weapon | Instrument | +3% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 38 | 0 | 3 | 3 | 5 | 5 | 5 | 4 |
| 10 | 120 | 10 | 9 | 9 | 9 | 12 | 11 | 9 |
| 20 | 215 | 23 | 15 | 19 | 14 | 21 | 18 | 16 |
| 30 | 314 | 36 | 22 | 28 | 20 | 32 | 28 | 23 |
| 40 | 413 | 50 | 29 | 37 | 25 | 43 | 37 | 29 |
| 50 | 512 | 64 | 36 | 46 | 31 | 54 | 47 | 35 |
| 60 | 611 | 77 | 43 | 55 | 37 | 65 | 57 | 42 |
| 70 | 710 | 91 | 50 | 64 | 42 | 76 | 66 | 48 |
| 80 | 809 | 104 | 57 | 73 | 48 | 87 | 76 | 55 |
| 90 | 908 | 118 | 64 | 82 | 54 | 98 | 86 | 61 |
| 99 | 997 | 130 | 70 | 90 | 59 | 108 | 94 | 67 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Warm-Up | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Fascinating Waltz | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Alluring Samba | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Gloomy Tango | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Gravitating Polka | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Dance Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |

### Diva

- **Tier:** Advanced (Promotion Route: Bard)

### Usable Equipment

- **Weapon Types:** Bow (6), Dagger (7), Fan (5), Mace (6), Microphone (15), Polearm (1), Sword (1), Whip (1)
- **Defensive Gear:** Accessory (47), Armor (23), Helm (19), Shield (8)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Accessory | Accessory | +2% |
| Weapon | Microphone | +4% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 38 | 0 | 3 | 3 | 5 | 5 | 5 | 4 |
| 10 | 120 | 10 | 9 | 9 | 9 | 12 | 11 | 9 |
| 20 | 213 | 23 | 15 | 18 | 14 | 23 | 19 | 17 |
| 30 | 309 | 40 | 22 | 27 | 20 | 35 | 32 | 26 |
| 40 | 419 | 78 | 29 | 37 | 29 | 51 | 43 | 36 |
| 50 | 529 | 115 | 37 | 46 | 38 | 67 | 54 | 46 |
| 60 | 639 | 153 | 44 | 56 | 46 | 83 | 65 | 57 |
| 70 | 749 | 190 | 51 | 65 | 55 | 99 | 76 | 67 |
| 80 | 860 | 228 | 58 | 75 | 64 | 116 | 87 | 77 |
| 90 | 970 | 265 | 66 | 84 | 73 | 132 | 98 | 87 |
| 99 | 1069 | 299 | 72 | 93 | 81 | 146 | 108 | 96 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Barrage Rondo | Magic | 1 | 10 | All allies | None |
| Concentration Prelude | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Reading Requiem | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Lightning March | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Sorcerous Ballad | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All allies | None |
| Panic Voice | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Auto-Recovery | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Concentrate | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Self Session | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Fast Talk | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |

### Mistress

- **Tier:** Advanced (Promotion Route: Bard or Dancer)

### Usable Equipment

- **Weapon Types:** Bow (4), Dagger (9), Fan (14), Gun (5), Mace (2), Polearm (2), Projectile (1), Whip (16)
- **Defensive Gear:** Accessory (50), Armor (22), Helm (19), Shield (10)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Promotion Route | Slot | Equipment Type | Modifier |
| --- | --- | --- | --- |
| From Bard | Accessory | Accessory | +2% |
| From Bard | Weapon | Microphone | +2% |
| From Bard | Weapon | Whip | +3% |
| From Dancer | Accessory | Accessory | +2% |
| From Dancer | Weapon | Instrument | +2% |
| From Dancer | Weapon | Whip | +3% |

### Stat Growth

#### Route from Bard

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 38 | 0 | 3 | 3 | 5 | 5 | 5 | 4 |
| 10 | 120 | 10 | 9 | 9 | 9 | 12 | 11 | 9 |
| 20 | 213 | 23 | 15 | 18 | 14 | 23 | 19 | 17 |
| 30 | 309 | 36 | 29 | 28 | 20 | 33 | 36 | 25 |
| 40 | 448 | 100 | 41 | 40 | 31 | 47 | 52 | 40 |
| 50 | 587 | 164 | 53 | 51 | 42 | 62 | 69 | 54 |
| 60 | 727 | 228 | 66 | 63 | 54 | 76 | 85 | 69 |
| 70 | 866 | 292 | 78 | 74 | 65 | 90 | 101 | 84 |
| 80 | 1005 | 356 | 90 | 86 | 76 | 105 | 118 | 98 |
| 90 | 1144 | 420 | 102 | 97 | 87 | 119 | 134 | 113 |
| 99 | 1269 | 478 | 113 | 107 | 97 | 132 | 148 | 126 |

#### Route from Dancer

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 38 | 0 | 3 | 3 | 5 | 5 | 5 | 4 |
| 10 | 120 | 10 | 9 | 9 | 9 | 12 | 11 | 9 |
| 20 | 215 | 23 | 21 | 19 | 14 | 21 | 20 | 16 |
| 30 | 314 | 36 | 31 | 29 | 20 | 32 | 37 | 23 |
| 40 | 460 | 102 | 45 | 41 | 29 | 44 | 54 | 37 |
| 50 | 606 | 168 | 58 | 53 | 37 | 56 | 71 | 50 |
| 60 | 752 | 234 | 72 | 64 | 46 | 68 | 89 | 64 |
| 70 | 898 | 300 | 86 | 76 | 55 | 80 | 106 | 77 |
| 80 | 1044 | 366 | 100 | 88 | 63 | 92 | 123 | 91 |
| 90 | 1189 | 432 | 113 | 100 | 72 | 105 | 140 | 105 |
| 99 | 1321 | 491 | 126 | 110 | 80 | 115 | 156 | 117 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Provoke | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | None |
| War Cry | Technique | 5 | 30 (2, 4, 6, 8, 10) | All allies | None |
| Hard Whipping | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Enemy row | Mid |
| Enticing Love | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | Mid |
| Absolute Obedience | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | Short |
| Resurrect | Magic | 5 | 30 (2, 4, 6, 8, 10) | Single ally | None |
| Carrot and Stick | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single enemy | None |
| Whip Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Auto-Refresh | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Knock Down | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Ecstasy | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Counter Whip | Passive | 1 | 20 | - | - |

### Etoile

- **Tier:** Advanced (Promotion Route: Dancer)

### Usable Equipment

- **Weapon Types:** Bow (6), Dagger (9), Fan (7), Instrument (15), Mace (4), Polearm (1), Whip (1)
- **Defensive Gear:** Accessory (47), Armor (24), Helm (20), Shield (8)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Accessory | Accessory | +2% |
| Weapon | Instrument | +4% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 38 | 0 | 3 | 3 | 5 | 5 | 5 | 4 |
| 10 | 120 | 10 | 9 | 9 | 9 | 12 | 11 | 9 |
| 20 | 215 | 23 | 16 | 19 | 14 | 21 | 20 | 16 |
| 30 | 314 | 36 | 22 | 28 | 20 | 32 | 34 | 26 |
| 40 | 444 | 54 | 31 | 38 | 28 | 45 | 45 | 37 |
| 50 | 574 | 72 | 39 | 49 | 36 | 57 | 57 | 47 |
| 60 | 705 | 90 | 48 | 59 | 43 | 70 | 68 | 58 |
| 70 | 835 | 108 | 56 | 70 | 51 | 82 | 79 | 69 |
| 80 | 965 | 127 | 65 | 80 | 59 | 95 | 91 | 79 |
| 90 | 1095 | 145 | 74 | 90 | 67 | 108 | 102 | 90 |
| 99 | 1212 | 161 | 81 | 100 | 74 | 119 | 112 | 100 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Debilitating Salsa | Technique | 10 | 95 (2, 4, 6, 8, 10, 11, 12, 13, 14, 15) | All enemies | None |
| Dumbing Mazurka | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Emaciating Hopak | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | None |
| Primevil | Magic | 8 | 64 (1, 3, 5, 7, 9, 11, 13, 15) | All allies | None |
| Auto-Recovery | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Guts | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Concentrate | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| On Stage | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Magnificent Steps | Passive | 5 | 45 (3, 6, 9, 12, 15) | - | - |

## Spieler Line

### Spieler

- **Tier:** Base

### Usable Equipment

- **Weapon Types:** Axe (1), Dagger (14), Fan (5), Gun (2), Katana (1), Mace (7), Polearm (2), Projectile (7), Sword (3), Whip (8)
- **Defensive Gear:** Accessory (42), Armor (18), Helm (17), Shield (13)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +1% |
| Weapon | Projectile | +1% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 3 | 5 | 3 | 9 | 6 |
| 10 | 134 | 35 | 12 | 9 | 10 | 11 | 19 | 12 |
| 20 | 241 | 57 | 24 | 18 | 15 | 19 | 30 | 19 |
| 30 | 339 | 78 | 33 | 27 | 20 | 27 | 41 | 28 |
| 40 | 438 | 100 | 42 | 36 | 25 | 35 | 53 | 37 |
| 50 | 536 | 121 | 51 | 45 | 30 | 43 | 64 | 45 |
| 60 | 634 | 143 | 60 | 54 | 36 | 51 | 75 | 54 |
| 70 | 733 | 164 | 69 | 62 | 41 | 58 | 86 | 63 |
| 80 | 831 | 186 | 78 | 71 | 46 | 66 | 97 | 72 |
| 90 | 929 | 207 | 87 | 80 | 51 | 74 | 109 | 80 |
| 99 | 1018 | 227 | 95 | 88 | 56 | 81 | 119 | 88 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Fleet Foot | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Self | None |
| Danger Shoot | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Random enemies | Long |
| Coffee Break | Technique | 5 | 25 (1, 3, 5, 7, 9) | Self | None |
| Roulette Circus | Technique | 1 | 10 | None | None |
| Weapon Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Present for Me | Passive | 5 | 25 (1, 3, 5, 7, 9) | - | - |

### Doll Master

- **Tier:** Intermediate (Promotion Route: Spieler)

### Usable Equipment

- **Weapon Types:** Axe (1), Dagger (17), Fan (7), Mace (5), Polearm (1), Projectile (7), Staff (12), Sword (13), Tome (12), Whip (13)
- **Defensive Gear:** Accessory (46), Armor (20), Helm (18), Shield (14)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +1% |
| Weapon | Projectile | +1% |
| Weapon | Staff | +1% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 4 | 4 | 8 | 5 | 9 | 7 |
| 10 | 138 | 44 | 12 | 9 | 18 | 12 | 19 | 16 |
| 20 | 243 | 75 | 22 | 20 | 30 | 22 | 30 | 26 |
| 30 | 345 | 106 | 31 | 29 | 41 | 33 | 41 | 35 |
| 40 | 448 | 138 | 40 | 38 | 52 | 45 | 53 | 45 |
| 50 | 550 | 169 | 49 | 47 | 64 | 57 | 64 | 55 |
| 60 | 652 | 200 | 58 | 56 | 75 | 68 | 75 | 65 |
| 70 | 754 | 231 | 68 | 65 | 87 | 80 | 86 | 75 |
| 80 | 856 | 262 | 77 | 74 | 98 | 91 | 97 | 84 |
| 90 | 959 | 294 | 86 | 83 | 109 | 103 | 109 | 94 |
| 99 | 1050 | 322 | 94 | 91 | 120 | 113 | 119 | 103 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Spartan | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | None | None |
| Oracles | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | None | None |
| Catalina | Technique | 5 | 30 (2, 4, 6, 8, 10) | None | None |
| Mini Auto-Refresh | Passive | 5 | 15 (1, 2, 3, 4, 5) | - | - |
| Doll Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |

### Trickster

- **Tier:** Intermediate (Promotion Route: Spieler)

### Usable Equipment

- **Weapon Types:** Axe (4), Dagger (16), Fan (8), Gun (4), Katana (1), Mace (6), Polearm (2), Projectile (6), Staff (1), Sword (6), Whip (9)
- **Defensive Gear:** Accessory (42), Armor (17), Helm (22), Shield (15)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Dagger | +2% |
| Weapon | Projectile | +2% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 7 | 5 | 7 | 4 | 9 | 7 |
| 10 | 146 | 40 | 17 | 12 | 17 | 12 | 20 | 17 |
| 20 | 248 | 67 | 28 | 22 | 27 | 22 | 32 | 28 |
| 30 | 359 | 93 | 38 | 32 | 38 | 33 | 44 | 39 |
| 40 | 471 | 120 | 49 | 42 | 49 | 44 | 56 | 51 |
| 50 | 582 | 147 | 60 | 51 | 59 | 56 | 68 | 62 |
| 60 | 694 | 174 | 71 | 61 | 70 | 67 | 80 | 73 |
| 70 | 805 | 200 | 82 | 71 | 81 | 78 | 91 | 85 |
| 80 | 917 | 227 | 92 | 81 | 92 | 89 | 103 | 96 |
| 90 | 1028 | 254 | 103 | 91 | 102 | 101 | 115 | 108 |
| 99 | 1129 | 278 | 113 | 99 | 112 | 111 | 126 | 118 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Checkmate | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Surprise Fist | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | Long |
| High Risk, High Return | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Magic Box | Technique | 1 | 10 | None | None |
| Mini Auto-Recovery | Passive | 5 | 15 (1, 2, 3, 4, 5) | - | - |
| Anti-Dark Aura | Passive | 1 | 20 | - | - |
| Pretend | Passive | 5 | 45 (3, 6, 9, 12, 15) | - | - |

### Soul Summoner

- **Tier:** Advanced (Promotion Route: Doll Master)

### Usable Equipment

- **Weapon Types:** Axe (1), Dagger (22), Fan (7), Mace (6), Polearm (1), Projectile (7), Staff (14), Sword (20), Tome (13), Whip (13)
- **Defensive Gear:** Accessory (52), Armor (24), Helm (23), Shield (15)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Sword | +3% |
| Weapon | Staff | +3% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 5 | 4 | 8 | 5 | 9 | 7 |
| 10 | 143 | 48 | 14 | 9 | 19 | 12 | 19 | 16 |
| 20 | 246 | 83 | 24 | 20 | 31 | 22 | 30 | 26 |
| 30 | 354 | 119 | 33 | 29 | 44 | 35 | 41 | 35 |
| 40 | 461 | 154 | 43 | 38 | 56 | 47 | 53 | 45 |
| 50 | 569 | 189 | 53 | 47 | 68 | 59 | 64 | 55 |
| 60 | 677 | 225 | 63 | 56 | 81 | 72 | 75 | 65 |
| 70 | 784 | 260 | 73 | 65 | 93 | 84 | 86 | 75 |
| 80 | 892 | 296 | 82 | 74 | 105 | 97 | 97 | 84 |
| 90 | 1000 | 331 | 92 | 83 | 117 | 109 | 109 | 94 |
| 99 | 1097 | 363 | 101 | 91 | 129 | 120 | 119 | 103 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Mercidarian | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | None | None |
| Perdurabo | Technique | 8 | 36 (1, 2, 3, 4, 5, 6, 7, 8) | None | None |
| Musiy | Technique | 7 | 84 (3, 6, 9, 12, 15, 18, 21) | None | None |
| Divine Shield | Magic | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Soul Eater | Magic | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | None |
| Adaptation | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Double Puppet | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Soul Seal | Passive | 5 | 45 (3, 6, 9, 12, 15) | - | - |
| Destiny Line | Passive | 1 | 20 | - | - |

### Papillon

- **Tier:** Advanced (Promotion Route: Doll Master or Trickster)

### Usable Equipment

- **Weapon Types:** Axe (1), Dagger (21), Fan (16), Gun (4), Katana (1), Mace (6), Polearm (1), Projectile (9), Staff (2), Sword (8), Tome (6), Whip (9)
- **Defensive Gear:** Accessory (56), Armor (28), Helm (20), Shield (16)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Promotion Route | Slot | Equipment Type | Modifier |
| --- | --- | --- | --- |
| From Doll Master | Weapon | Dagger | +1% |
| From Doll Master | Weapon | Staff | +2% |
| From Doll Master | Weapon | Fan | +3% |
| From Trickster | Weapon | Dagger | +2% |
| From Trickster | Weapon | Projectile | +2% |
| From Trickster | Weapon | Fan | +3% |

### Stat Growth

#### Route from Doll Master

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 5 | 5 | 8 | 6 | 9 | 7 |
| 10 | 160 | 44 | 16 | 11 | 19 | 12 | 20 | 16 |
| 20 | 255 | 75 | 27 | 19 | 30 | 22 | 31 | 26 |
| 30 | 383 | 106 | 33 | 30 | 42 | 39 | 43 | 37 |
| 40 | 510 | 137 | 45 | 40 | 54 | 51 | 55 | 47 |
| 50 | 637 | 168 | 57 | 50 | 66 | 63 | 66 | 57 |
| 60 | 763 | 200 | 68 | 60 | 78 | 75 | 78 | 68 |
| 70 | 890 | 231 | 80 | 70 | 90 | 87 | 90 | 78 |
| 80 | 1017 | 262 | 92 | 80 | 102 | 99 | 102 | 88 |
| 90 | 1144 | 293 | 104 | 89 | 113 | 111 | 113 | 98 |
| 99 | 1258 | 321 | 114 | 98 | 124 | 122 | 124 | 107 |

#### Route from Trickster

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 46 | 16 | 5 | 7 | 8 | 5 | 8 | 7 |
| 10 | 163 | 46 | 16 | 11 | 18 | 12 | 19 | 18 |
| 20 | 257 | 78 | 29 | 21 | 30 | 21 | 32 | 29 |
| 30 | 387 | 113 | 42 | 33 | 40 | 34 | 45 | 41 |
| 40 | 517 | 146 | 55 | 44 | 51 | 45 | 58 | 53 |
| 50 | 646 | 179 | 67 | 56 | 63 | 56 | 70 | 64 |
| 60 | 776 | 212 | 80 | 67 | 74 | 67 | 83 | 76 |
| 70 | 906 | 245 | 93 | 78 | 86 | 78 | 96 | 88 |
| 80 | 1036 | 279 | 106 | 90 | 97 | 89 | 109 | 100 |
| 90 | 1165 | 312 | 118 | 101 | 108 | 100 | 121 | 111 |
| 99 | 1282 | 341 | 130 | 111 | 119 | 110 | 133 | 122 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Materialize | Technique | 5 | 25 (1, 3, 5, 7, 9) | Single enemy | None |
| Rose Queen | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | All enemies | Long |
| Tinker Squash | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Short |
| Graceful Rose | Technique | 1 | 5 | Single enemy | Long |
| Illusion | Magic | 3 | 18 (3, 6, 9) | Self | None |
| Insurance | Magic | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Limit Field | Magic | 5 | 30 (2, 4, 6, 8, 10) | Everyone | None |
| Fan Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Double Attack | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Esarhaddon | Passive | 6 | 36 (1, 3, 5, 7, 9, 11) | - | - |
| Elegant Dancing | Passive | 1 | 20 | - | - |

### Joker

- **Tier:** Advanced (Promotion Route: Trickster)

### Usable Equipment

- **Weapon Types:** Axe (31), Dagger (27), Fan (4), Katana (1), Mace (7), Polearm (2), Projectile (4), Staff (1), Sword (12), Whip (16)
- **Defensive Gear:** Accessory (51), Armor (26), Helm (26), Shield (20)

### Weapon Specialty Modifiers

Equipping a specialized weapon or gear type adds a percentage bonus: int((character_stat + piece_stat) * modifier) to all non-zero equipment stats (Address 0x4f7c60).

| Slot | Equipment Type | Modifier |
| --- | --- | --- |
| Weapon | Whip | +3% |
| Weapon | Axe | +4% |

### Stat Growth

| Level | HP | TP | ATK | DEF | INT | RES | DEX | AGI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 48 | 18 | 9 | 3 | 7 | 4 | 9 | 7 |
| 10 | 167 | 36 | 18 | 11 | 15 | 12 | 21 | 18 |
| 20 | 268 | 66 | 29 | 21 | 25 | 20 | 32 | 30 |
| 30 | 401 | 95 | 41 | 30 | 34 | 29 | 47 | 42 |
| 40 | 534 | 124 | 55 | 40 | 43 | 37 | 63 | 54 |
| 50 | 666 | 153 | 69 | 50 | 53 | 46 | 79 | 66 |
| 60 | 799 | 182 | 82 | 59 | 62 | 54 | 95 | 78 |
| 70 | 932 | 210 | 96 | 69 | 71 | 63 | 111 | 91 |
| 80 | 1065 | 239 | 110 | 79 | 80 | 71 | 127 | 103 |
| 90 | 1197 | 268 | 124 | 89 | 90 | 80 | 142 | 115 |
| 99 | 1317 | 294 | 136 | 98 | 98 | 87 | 157 | 126 |

### Learned Skills

| Skill | Type | Max Lv | SP Cost | Target | Range |
| --- | --- | --- | --- | --- | --- |
| Mad Zapper | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Piercing | Mid |
| Life Bringer | Technique | 5 | 30 (2, 4, 6, 8, 10) | Single enemy | Short |
| Trump Card | Technique | 5 | 30 (2, 4, 6, 8, 10) | Self | None |
| Showtime | Technique | 1 | 15 | None | None |
| Beast Binder | Technique | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | Single enemy | Mid |
| Heaven or Hell | Magic | 5 | 25 (1, 3, 5, 7, 9) | Single enemy | None |
| Axe Mastery | Passive | 10 | 55 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10) | - | - |
| Avenger | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Murder | Passive | 5 | 30 (2, 4, 6, 8, 10) | - | - |
| Triple Joker | Passive | 1 | 20 | - | - |

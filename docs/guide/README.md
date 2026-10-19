# Dungeon Travelers 2-2 Reference Guide (Vanilla)

Reference documentation for the original English PC release of Dungeon Travelers 2-2. All data and formulas are extracted directly from the game executable (DT22_en_unwrapped.exe) and packaged archive files.

## How to Read the Tables

Stat tables record raw class attributes at milestone levels from 1 to 99. Modifiers operate additively unless specified by game logic. Equipment usability lists weapon classes and defensive gear categories supported by internal compatibility bitmasks.

## Glossary

Core combat parameters, calculations, and mechanical terms used throughout this guide.

| Term | Definition |
| --- | --- |
| HP | Hit Points. Unit is incapacitated when reduced to 0. |
| TP | Technical Points. Consumed to execute skills and spells. |
| ATK | Attack stat (index 0). Scales physical damage before opponent DEF reduction (0x44b36e). |
| DEF | Physical defence stat (index 1). Mitigates physical damage; subtracted from incoming attack values (0x44b9c0). |
| INT | Intelligence stat (index 2). Determines magic attack strength and magic evasion calculations (0x44dc97). |
| RES | Resistance stat (index 3). Mitigates magic damage and provides base elemental protection (0x44e070). |
| DEX | Dexterity stat (index 4). Influences physical accuracy and critical hit chance (0x44aac1, 0x44f1d8). |
| AGI | Agility stat (index 5). Governs physical evasion and action gauge recovery rate (0x44aac1, 0x449b4c). |
| Chant | Casting interval required by certain spells and skills before execution (0x449d9a). Damage taken relative to max HP creates interruption chance (0x44d001). |
| Weight / Delay | Weapon recovery factor indexed by weapon rank (A+ to F). Increases turn wait time proportionally with unit level (0x449bd4). |
| Swing | Damage variance factor assigned to weapons, spells, and enemies (0x44b2f1, 0x44db97). |
| Hit / Evasion | Accuracy versus evasion check. Physical hit rate is bounded between 5% and 100% (0x44ae84); spell hit rate is bounded between 25% and 95% (0x44da2b). |
| Resistance | Reduces damage of the corresponding attribute by 0.5% per point (0x44c576). Mitigates ailment infliction chance in increments of 10 points (0x481fc2). |
| Target Weight | Position-based enmity value determining probability of being targeted by single-target attacks (0x43f7e9, table 0x6517a0). |
| Range | Distance factor based on combat rows (front vs back). Melee skills lose damage over distance; ranged skills bypass distance penalties (0x44a7d0). |
| Level Reset (Crown) | Process of returning a character to level 1 from level 50 or higher (0x4f94f0). Grants permanent stat bonus points up to a hard cap of 50. |

# Dungeon Travelers 2-2 Reference Guide (Vanilla)

Player reference documentation for the original English PC release of Dungeon Travelers 2-2. All data, mechanics, and formulas are compiled directly from the original game files.

## How to Read the Tables

Stat tables record raw class attributes at milestone levels from 1 to 99. Modifiers operate additively unless specified by game logic. Equipment usability lists weapon classes and defensive gear categories supported by internal compatibility bitmasks.

## Glossary

Core combat parameters, calculations, and mechanical terms used throughout this guide.

| Term | Definition |
| --- | --- |
| HP | Hit Points. The unit is knocked out when reduced to 0. |
| TP | Technical Points. Consumed to execute skills and spells. |
| ATK | Physical attack power. Scales damage of normal attacks and physical skills before enemy DEF reduction. |
| DEF | Physical defence. Reduces incoming physical damage directly from the attacker's attack value. |
| INT | Intelligence. Determines magic attack power and influences magic evasion. |
| RES | Resistance. Reduces incoming magic damage and provides base protection against elemental attacks. |
| DEX | Dexterity. Increases physical hit accuracy and critical hit chance. |
| AGI | Agility. Increases physical evasion rate and speeds up action gauge recovery in the turn order. |
| Chant | Casting preparation time required before executing certain spells and skills. Damage sustained relative to max HP can interrupt the chant. |
| Weight / Delay | Weapon recovery delay determined by weapon rank (A+ to F). Slower weapons increase the wait time before the unit's next turn, scaling with level. |
| Swing | Inherent damage variance factor assigned to weapons, spells, and enemies. |
| Hit / Evasion | Accuracy check between attacker and target. Physical hit rate is bounded between 5% and 100%; offensive spells are bounded between 25% and 95%. |
| Resistance | Reduces damage of that element by 0.5% per point of resistance. Also mitigates status ailment infliction chance in increments of 10 points. |
| Target Weight | Enmity value determining the likelihood of being targeted by single-target attacks, influenced by row position, Provoke, and equipment. |
| Range | Distance between front and back combat rows. Short-range attacks lose damage when targeting or used from the back row; long-range attacks suffer no distance penalty. |
| Level Reset (Crown) | Returning a character to level 1 from level 50 or higher to earn permanent bonus stat points, up to a maximum of 50. |

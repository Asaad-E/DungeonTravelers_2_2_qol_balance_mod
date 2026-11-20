Dungeon Travelers 2-2 - Balance + QoL Mod
==========================================

This package contains the full Balance + QoL Mod for Dungeon Travelers 2-2
(English PC Release). It includes all Quality of Life text clarity updates plus
rebalanced progression, classes, skills, items, enemies, bosses, summons,
mercenaries, zones, and executable fixes.

INSTALLATION (Windows)
----------------------
1. Extract ALL contents of this archive directly into your game folder (the
   folder containing `DT22_en.exe`, `DT22_en_unwrapped.exe`, and `Data/`):
   - `Install_Balance.bat`
   - `Uninstall_DT22_Mod.bat`
   - `DT22_Mod/`
   When extracting an updated archive over an older mod install, allow it to
   overwrite existing files in the game root and `DT22_Mod/`.
2. Double-click `Install_Balance.bat`.
   - Backups of every touched original file are saved automatically under
     `DT22_Mod\backup\` before any file is modified.
   - If another variant (QoL or an earlier Balance build) is already installed,
     the installer restores from `DT22_Mod\backup\` and applies the new files
     cleanly.
   - Note: Because this package ships binary diffs only (zero copyrighted game
     assets), every touched game file must match a clean original copy (or have
     an intact original in `DT22_Mod\backup\`).

INSTALLATION (Linux / Steam Deck / macOS via Proton/Wine)
---------------------------------------------------------
1. Extract all files into the game folder (`chmod +x Install_Balance.sh Uninstall_DT22_Mod.sh`
   if needed; requires `python3`).
2. Run `./Install_Balance.sh`.

UNINSTALLATION
--------------
- Double-click `Uninstall_DT22_Mod.bat` (or run `./Uninstall_DT22_Mod.sh`) to
  restore all original `.pck` archives, dungeon floor files, and executables
  from `DT22_Mod\backup\`.

WHAT THIS MOD CHANGES
---------------------
In total, the Balance build applies 3,586 tuned data entries across 15 game
tables (3,674 fields in 16 parameter/entity `.pck` archives and 166 zone
weights across 20 dungeon floor `.pck` files) plus 17 executable patches
(46 bytes) in both `DT22_en.exe` and `DT22_en_unwrapped.exe`:

1. Quality of Life Text & Teaching Guides (Included)
   - Accurate in-game descriptions for skills, items, enchantments, food,
     enemy attacks, party skills, joint skills, weapon ranks, and classes,
     regenerated directly from the Balance binary values (no mismatched stats
     or missing changes).
   - Updated in-game Battle & Class Tutorials (`Teaching.pck` and `Lesson.pck`).

2. Executable Fixes & Progression Tweaks (17 patches / 46 bytes)
   - Catch-up EXP multipliers (without EXP piece: 1.15x / 3x / 5x / 10x;
     with Enchant 270 piece: 1.5x / 4x / 6x / 10x), plus branch fix enabling the
     20+ level gap tier without an EXP piece.
   - Level Reset / Crown points: +1 stat bonus point per level reset on the top
     4 tiers (5->6, 4->5, 3->4, and 2->3; cap remains 50).
   - Arcane Shield: trigger roll increased from 15% to 25%.
   - Chant interruption bugfix: applies Concentrate multiplicatively instead of
     additively (`addss -> mulss`), matching its formula for all units.
   - Map buff/status tick duration: 5 -> 12 steps per turn outside battle
     (meals and field buffs last ~2.4x longer while exploring).
   - Third Eye Wide bugfix: fixes broken jump blocking buff dispel.
   - Positive Trance (Alisia): Pep threshold lowered from 100 to 85.

3. Classes, Skills, Unique Skills & Party Skills
   - 152 class skills tuned across Magic (61), Passive (20), and Technique (71)
     skills (elemental spells and chant times, Guard spells, Sun Veil, First Grid,
     Graceful Rose, Spartan, dances, stances, ninja skills, summons, etc.).
   - 7 unique skills tuned: Third Eye Wide, Sugar Coma, Alter Fate, Wreathed in
     Glory, Tranquil Song, Arcane Shield, and Usurper of Souls reworked into
     No Miracles Needed.
   - Party skill Eccentrics switched from DEX to AGI bonus.
   - Class stat growth adjusted for Sniper, Witch, and Soul Summoner, plus an
     adjusted overall SP curve (`LvExpSkptData.pck`).

4. Equipment, Sealbooks, Enchantments & Items
   - Weapon & armor tuning across 11 pieces: Tantou (`1.3 -> 2.6` upgrade rate),
     Whip (`1.44 -> 2`), Ougi (`16 -> 24` base ATK), Dagger (`14 -> 20` base ATK),
     Bathroom Slippers secondary enchant updated, Kite Shield and Fluted Armor
     class usability bitmask expanded (`0x3f -> 0x2003f`), and top-end heavy
     weapons tuned (`Heavy Axe`, `Heavy Lance`, `Claymore`, `Tachi`).
   - 4 Grand Sealbooks upgraded with secondary enchantments: Melek Taus, Genbu,
     Murasaki Shikibu, and Death Cataphract.
   - `All stats` (+1/+3/+6/+9/+12) stacking flags enabled (`428 -> 429`).
   - TP recovery fruits boosted (+20%: Magical Fruit 30, Fairy Apple 60,
     Golden Apple 120).

5. Enemies, Bosses, Summons, Mercenaries, Zones & Quests
   - 389 enemy records tuned (HP, ATK, DEF, INT, RES, AGI, DEX, resistances,
     72 immunity flag updates, 77 passive skill updates, AI/steal adjustments)
     plus 6 enemy attack skill records and 23 summon records.
   - 84 mercenary / guest ally records rebalanced, with 30% longer contracts
     (+6 to +7 battles) for Neya, Azmaria, and Miranda, and lower hiring costs
     for Three Fates and Marion.
   - 41 quests grant ~20% more gold.
   - 166 dungeon zones across 20 floor packs have Blacksmith encounter chance x1.5.

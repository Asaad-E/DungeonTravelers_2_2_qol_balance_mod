import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/skills.xlsx')
ws = wb['Skills']

# Master data dictionary: skill_name -> {desc, lvup, notes}
SKILL_DATA = {
    # ==========================================
    # 1. FIGHTER & ADVANCED (PALADIN, DARK LORD, BERSERKER, VALKYRIE)
    # ==========================================
    "Provoke": {
        "desc": "Attract single-target attacks.    |    Fast turn recovery.",
        "lvup": "Turns: 3 -> 4 -> 5 -> 6 -> 7 (L1-5)    |    Speed: +50% -> +100% (+12.5%/Lv)\nTP Cost: 1 -> 2 -> 3 -> 4 -> 5",
        "notes": "Fast turn recovery."
    },
    "Attract": {
        "desc": "Attract all enemies' attacks to user with high speed turn recovery.",
        "lvup": "Turns: 3 -> 4 -> 5 -> 6 -> 7 (L1-5)    |    Speed: +40% -> +80% (+10%/Lv)\nTP Cost: 3 -> 5 -> 7 -> 9 -> 11",
        "notes": "AoE provoke."
    },
    "War Cry": {
        "desc": "Raise party physical ATK & cleanse debuffs. Usable out of battle.",
        "lvup": "ATK: +8% -> +10% -> +12% -> +14% -> +18% (L1-5 Max)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 5 -> 7 -> 9 -> 11 -> 13",
        "notes": "Best party physical buff."
    },
    "Raging Smash": {
        "desc": "Short-range strike.    |    Hit Rate: +20% -> +38% (+2%/Lv)",
        "lvup": "ATK (L1-10): 125% -> 133 -> 141 -> 150 -> 158 -> 166 -> 175 -> 183 -> 191 -> 200%\nTP Cost: 5 -> 8 -> 11 -> 14 -> 17 -> 20 -> 22 -> 24 -> 26 -> 28  (Lv1 to Max)",
        "notes": "Short weapon only."
    },
    "Aura Eliminate": {
        "desc": "Short-range strike to one enemy. May cancel enemy active buffs.",
        "lvup": "Dispel Chance: 30% -> 60% (+7.5%/Lv)    |    Levels: L1-5\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Cancels boss buffs."
    },
    "Berserk": {
        "desc": "Greatly boost own physical ATK at the cost of lowering own DEF.",
        "lvup": "ATK: +25% -> +35% -> +45% -> +55% -> +65% (L1-5)    |    DEF: -15% -> -35%\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "High risk buff."
    },
    "Defender": {
        "desc": "Increase own DEF at the cost of ATK (ATK debuff can be cleansed).",
        "lvup": "DEF: +20% -> +27% -> +35% -> +42% -> +50% (L1-5 Max)\nATK: -11% -> -25% (-3.5%/Lv)    |    TP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Defensive stance."
    },
    "Shield Bash": {
        "desc": "Shield skill. Deal bash damage to one enemy. May stun.",
        "lvup": "ATK: 110% -> 120% -> 130% -> 140% -> 150% (L1-5)    |    Stun: 20% -> 40%\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14    |    Requires equipped shield",
        "notes": "Shield bash stun."
    },
    "Cover": {
        "desc": "Step forward to intercept physical attacks aimed at allies.",
        "lvup": "Turns: 4 -> 5 -> 6 -> 7 -> 8 (L1-5)    |    Guard: 30% -> 60% (+7.5%/Lv)\nTP Cost: 10 -> 13 -> 16 -> 20 -> 24    |    Requires 1H weapon & shield",
        "notes": "Protects allies."
    },
    "Parry": {
        "desc": "Short-range skill. Block physical attacks with equipped weapon.",
        "lvup": "Turns: 3 -> 4 -> 5 -> 6 -> 7 (L1-5)    |    Recovery Speed: 1.30x\nTP Cost: 10 -> 13 -> 16 -> 19 -> 22    |    May break on repeat blocks",
        "notes": "Weapon block."
    },
    "Material Guard": {
        "desc": "Shield skill. Erect a physical barrier mitigating party damage once.",
        "lvup": "Damage Reduction: -30% -> -50% (-5%/Lv)    |    Levels: L1-5\nTP Cost: 14 -> 17 -> 20 -> 23 -> 26    |    Requires shield",
        "notes": "Party physical shield."
    },
    "Spell Guard": {
        "desc": "Shield skill. Erect a magic barrier mitigating party magic damage once.",
        "lvup": "Magic Reduction: -30% -> -50% (-5%/Lv)    |    Levels: L1-5\nTP Cost: 14 -> 17 -> 20 -> 23 -> 26    |    Requires shield",
        "notes": "Party magic shield."
    },
    "Cross Slash": {
        "desc": "Sword and lance skill. Strike one enemy. Effective vs. Unholy foes.",
        "lvup": "ATK: 140% -> 155% -> 170% -> 185% -> 200% (L1-5)    |    Unholy Bonus: 1.50x\nTP Cost: 12 -> 14 -> 16 -> 18 -> 20",
        "notes": "Bonus vs unholy."
    },
    "Daedalus Attack": {
        "desc": "Lance skill. Rapidly strike random enemies 3 to 5 times.",
        "lvup": "ATK: 65% -> 75% -> 85% -> 95% -> 105% per hit (L1-5)\nTP Cost: 15 -> 18 -> 21 -> 24 -> 28    |    Heavy Lance bonus: +20% dmg",
        "notes": "Multi-hit lance skill."
    },
    "Power Charge": {
        "desc": "Concentrate strength to deal massive physical damage next turn.",
        "lvup": "Next Physical Hit: +80% -> +110% -> +140% -> +170% -> +200% (L1-5)\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14    |    Applies to next physical action",
        "notes": "Physical charge."
    },
    "Blood Drain": {
        "desc": "Short-range strike to one enemy. Absorb a portion of damage as HP.",
        "lvup": "ATK: 110% -> 125% -> 140% -> 155% -> 170% (L1-5)\nHP Absorb: 20% -> 30% -> 40% -> 50% -> 60%    |    TP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Life drain strike."
    },
    "Soul Drain": {
        "desc": "Short-range strike to one enemy. Absorb a portion of damage as TP.",
        "lvup": "ATK: 100% -> 110% -> 120% -> 130% -> 140% (L1-5)\nTP Absorb: 5% -> 8% -> 11% -> 14% -> 18%    |    TP Cost: 4 -> 5 -> 6 -> 7 -> 8",
        "notes": "TP drain strike."
    },
    "Frost Slash": {
        "desc": "Short-range strike dealing mid-range water damage. May freeze.",
        "lvup": "ATK: 120% -> 135% -> 150% -> 165% -> 180% (L1-5)    |    Freeze: 20% -> 40%\nTP Cost: 10 -> 12 -> 14 -> 16 -> 18",
        "notes": "Water slash."
    },
    "Geo Break": {
        "desc": "Axe skill. Strike one enemy with earth damage. May petrify.",
        "lvup": "ATK: 130% -> 150% -> 170% -> 190% -> 210% (L1-5)    |    Petrify: 15% -> 30%\nTP Cost: 12 -> 15 -> 18 -> 21 -> 24",
        "notes": "Earth axe hit."
    },
    "Megaton Press": {
        "desc": "Axe skill. Strike target and the next immediate enemy in turn order.",
        "lvup": "ATK: 140% -> 160% -> 180% -> 200% -> 220% (L1-5)\nTP Cost: 16 -> 19 -> 22 -> 25 -> 28    |    Hits 2 sequential turn targets",
        "notes": "Sequential targets."
    },
    "Shock Spiral": {
        "desc": "Short-range skill. Deal lightning damage to an enemy row. May paralyze.",
        "lvup": "ATK: 110% -> 125% -> 140% -> 155% -> 170% (L1-5)    |    Paralysis: 20% -> 40%\nTP Cost: 14 -> 17 -> 20 -> 23 -> 26",
        "notes": "Row lightning."
    },
    "Gust Thrust": {
        "desc": "Lance skill. Strike one enemy with wind damage. May silence.",
        "lvup": "ATK: 125% -> 140% -> 155% -> 170% -> 185% (L1-5)    |    Silence: 20% -> 40%\nTP Cost: 10 -> 12 -> 14 -> 16 -> 18",
        "notes": "Wind lance hit."
    },
    "Halving Slice": {
        "desc": "Katana skill. Deal slash damage to an enemy row. May instakill.",
        "lvup": "ATK: 115% -> 130% -> 145% -> 160% -> 175% (L1-5)    |    Instakill: 10% -> 25%\nTP Cost: 15 -> 18 -> 21 -> 24 -> 28",
        "notes": "Row instakill slice."
    },
    "Armor Penetration": {
        "desc": "Katana skill. Deal defense-piercing damage and lower target DEF.",
        "lvup": "ATK: 120% -> 135% -> 150% -> 165% -> 180% (L1-5)    |    DEF Debuff: -15% -> -30%\nTP Cost: 12 -> 14 -> 16 -> 18 -> 20    |    Bypasses enemy armor",
        "notes": "Pierces armor."
    },
    "Onikagura": {
        "desc": "Katana skill. Strike an enemy row with fierce slashing blades.",
        "lvup": "ATK: 130% -> 145% -> 160% -> 175% -> 190% (L1-5)\nTP Cost: 14 -> 17 -> 20 -> 23 -> 26",
        "notes": "Katana row slash."
    },
    "Moonlight Purgatory": {
        "desc": "Katana skill. Strike 3 times against one living enemy.",
        "lvup": "ATK: 70% -> 80% -> 90% -> 100% -> 110% per hit (3 hits total)\nTP Cost: 18 -> 21 -> 24 -> 27 -> 30    |    Target must be living (not undead)",
        "notes": "3 hit katana strike."
    },

    # ==========================================
    # 2. SCOUT & ADVANCED (ARCHER, SNIPER, TREASURE HUNTER, KUNOICHI)
    # ==========================================
    "Evade": {
        "desc": "Increase own physical evasion rate.",
        "lvup": "EVA: +15% -> +20% -> +25% -> +30% -> +35% (L1-5 Max)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 4 -> 6 -> 8 -> 10 -> 12",
        "notes": "Evasion boost."
    },
    "Aim": {
        "desc": "Concentrate to boost own accuracy and critical hit rate.",
        "lvup": "Accuracy: +20% -> +35% (+3.75%/Lv)    |    Crit: +10% -> +20% (+2.5%/Lv)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 5 -> 7 -> 9 -> 11 -> 13",
        "notes": "Accuracy buff."
    },
    "Fleet Foot": {
        "desc": "Enhance own movement and agility for increased turn speed.",
        "lvup": "Speed: +15% -> +20% -> +25% -> +30% -> +35% (L1-5 Max)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Speed buff."
    },
    "Gold Steal": {
        "desc": "Attempt to pilfer pocket money from an enemy.",
        "lvup": "Success Rate: 40% -> 70% (+7.5%/Lv)    |    Gold: 1.0x -> 2.5x base amount\nTP Cost: 2 -> 3 -> 4 -> 5 -> 6",
        "notes": "Steals gold."
    },
    "Item Steal": {
        "desc": "Attempt to steal an item from an enemy.",
        "lvup": "Success Rate: 25% -> 55% (+7.5%/Lv)    |    Levels: L1-5\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Steals item."
    },
    "Sharp Stab": {
        "desc": "Dagger skill. Strike for guaranteed critical stab damage.",
        "lvup": "ATK: 130% -> 145% -> 160% -> 175% -> 190% (L1-5)    |    100% Critical Hit\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Guaranteed critical."
    },
    "Pursuit Stab": {
        "desc": "Dagger skill. Damage scales higher per buff and debuff on the target.",
        "lvup": "Base ATK: 120% -> 160% (L1-5)    |    +25% damage per active buff/debuff\nTP Cost: 10 -> 12 -> 14 -> 16 -> 18",
        "notes": "Bonus per status icon."
    },
    "Chain Spike": {
        "desc": "Bow and gun skill. Rapid fire multiple shots with escalating crit rate.",
        "lvup": "Hits: 2 -> 3 -> 3 -> 4 -> 4 (L1-5)    |    ATK: 65% -> 85% per hit\nTP Cost: 12 -> 15 -> 18 -> 21 -> 25",
        "notes": "Multi-shot bow skill."
    },
    "Guided Shot": {
        "desc": "Bow and gun skill. Fire a precision shot guaranteed to never miss.",
        "lvup": "ATK: 125% -> 140% -> 155% -> 170% -> 185% (L1-5)    |    100% Accuracy\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Never misses."
    },
    "Spiral Arrow": {
        "desc": "Bow skill. Unleash a piercing arrow with boosted critical strike rate.",
        "lvup": "ATK: 150% -> 170% -> 190% -> 210% -> 230% (L1-5)    |    Crit Rate: +30%\nTP Cost: 14 -> 17 -> 20 -> 23 -> 26",
        "notes": "High crit arrow."
    },
    "Star Dust Arrow": {
        "desc": "Bow skill. Shower random enemies with arrows over multiple turns.",
        "lvup": "Hits: 3-5 arrows per wave    |    ATK: 70% -> 95% per arrow (L1-5)\nDuration: 2 -> 3 turns    |    TP Cost: 20 -> 24 -> 28 -> 32 -> 36",
        "notes": "Multi-turn barrage."
    },
    "Divine Cannon": {
        "desc": "Bow skill. Massive piercing shot that penetrates through to the back row.",
        "lvup": "ATK: 175% -> 200% -> 225% -> 250% -> 280% (L1-5 Max)\nTP Cost: 18 -> 22 -> 26 -> 30 -> 34    |    Hits both front and back target",
        "notes": "Row piercing bow shot."
    },
    "Poison Shot": {
        "desc": "Bow and gun skill. Attack one enemy with a toxic shot. May poison.",
        "lvup": "ATK: 110% -> 125% -> 140% -> 155% -> 170% (L1-5)    |    Poison: 30% -> 60%\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Poison arrow."
    },
    "Freeze Shot": {
        "desc": "Bow skill. Attack one enemy with a chilling shot. May freeze.",
        "lvup": "ATK: 115% -> 130% -> 145% -> 160% -> 175% (L1-5)    |    Freeze: 25% -> 50%\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Freeze arrow."
    },
    "Paralysis Shot": {
        "desc": "Bow skill. Attack one enemy with an electric shot. May paralyze.",
        "lvup": "ATK: 115% -> 130% -> 145% -> 160% -> 175% (L1-5)    |    Paralysis: 25% -> 50%\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Paralysis arrow."
    },
    "Arrow Rain": {
        "desc": "Bow skill. Fire an arrow volley striking all enemies on screen.",
        "lvup": "ATK: 95% -> 110% -> 125% -> 140% -> 155% (L1-5 Max)\nTP Cost: 16 -> 19 -> 22 -> 25 -> 28",
        "notes": "All-target bow attack."
    },
    "Sleep Sting": {
        "desc": "Short-range strike to one enemy. May inflict Sleep.",
        "lvup": "ATK: 110% -> 125% -> 140% -> 155% -> 170% (L1-5)    |    Sleep: 30% -> 60%\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Sleep sting."
    },
    "Silence Sting": {
        "desc": "Short-range strike to one enemy. May inflict Silence.",
        "lvup": "ATK: 110% -> 125% -> 140% -> 155% -> 170% (L1-5)    |    Silence: 30% -> 60%\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Silence sting."
    },
    "Stun Sting": {
        "desc": "Short-range strike to one enemy. May inflict Stun.",
        "lvup": "ATK: 110% -> 125% -> 140% -> 155% -> 170% (L1-5)    |    Stun: 25% -> 50%\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Stun sting."
    },

    # ==========================================
    # 3. MAID & ADVANCED (BARD, DANCER, DOLL MASTER, MISTRESS)
    # ==========================================
    "First Aid": {
        "desc": "Heal one ally's HP.",
        "lvup": "Heal: 12% -> 15% -> 18% -> 21% -> 25% Max HP (L1-5 Max)\nTP Cost: 2 -> 4 -> 6 -> 8 -> 10    |    Affected by Maid Mastery (+10% cap)",
        "notes": "Percent HP healing."
    },
    "Cook": {
        "desc": "Prepare a snack to restore one ally's TP.",
        "lvup": "TP Heal: 10% -> 11% -> 12% -> 13% -> 15% Max TP (L1-5)\nAction delay: 0.85x    |    TP Cost: 0 (Costs no TP to use)",
        "notes": "Percent TP restore."
    },
    "Clean": {
        "desc": "Clean up battle area to grant party action speed boost.",
        "lvup": "Speed: +12% -> +14% -> +16% -> +18% -> +20% (L1-5)\nTurns: 6 -> 7 -> 8 -> 9 -> 10    |    TP Cost: 4 -> 6 -> 8 -> 10 -> 12",
        "notes": "Speed buff."
    },
    "Self-Sacrifice": {
        "desc": "Sacrifice all user TP to transfer a magnified amount to an ally.",
        "lvup": "TP Transferred: 100% -> 110% -> 120% -> 130% -> 140% of user's TP (L1-5)\nLeaves user at 0 TP    |    Fast recovery",
        "notes": "TP battery sacrifice."
    },
    "Lullaby": {
        "desc": "Sing a soothing lullaby. May put target enemy to sleep.",
        "lvup": "Sleep Chance: 40% -> 70% (+7.5%/Lv)    |    Levels: L1-5\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Sleep chant."
    },
    "Replenishing Carol": {
        "desc": "Perform a song that regenerates party HP every turn while singing.",
        "lvup": "HP Regen: 8% -> 11% -> 14% -> 17% -> 20% Max HP per turn (L1-5)\nChant Time: 2 turns -> 1 turn    |    TP Cost: 12 -> 15 -> 18 -> 21 -> 24",
        "notes": "Song HP regen."
    },
    "Blissful Chorale": {
        "desc": "Perform a song that regenerates party TP every turn while singing.",
        "lvup": "TP Regen: 3 -> 5 -> 7 -> 9 -> 12 TP per turn (L1-5)\nChant Time: 2 turns -> 1 turn    |    TP Cost: 10 -> 13 -> 16 -> 19 -> 22",
        "notes": "Song TP regen."
    },
    "Lightning March": {
        "desc": "Perform a lively march boosting party action speed while singing.",
        "lvup": "Party Speed: +15% -> +20% -> +25% -> +30% -> +35% (L1-5)\nTP Cost: 10 -> 13 -> 16 -> 19 -> 22",
        "notes": "Song speed boost."
    },
    "Experience Paean": {
        "desc": "Perform a song that increases combat EXP gained by the party.",
        "lvup": "EXP Bonus: +10% -> +15% -> +20% -> +25% -> +30% (L1-5)\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "EXP song."
    },

    # ==========================================
    # 4. SPIELER & ADVANCED (TRICKSTER, SOUL SUMMONER, PAPILLON, JOKER)
    # ==========================================
    "Coffee Break": {
        "desc": "Take a rest to restore own HP and raise Pep. Fast turn recovery.",
        "lvup": "Heal: 20% -> 25% -> 30% -> 35% -> 40% Max HP (L1-5 Max)\nTP Cost: 6 -> 7 -> 8 -> 9 -> 10    |    Action delay: 1.50x (fast)",
        "notes": "Self heal and pep."
    },
    "Danger Shoot": {
        "desc": "High risk gamble. Unleash 0 to 4 strikes on random enemies.",
        "lvup": "ATK per hit: 90% -> 110% -> 130% -> 150% -> 180% (L1-5)\nTP Cost: 14 -> 17 -> 20 -> 24 -> 28    |    Boosted by Trump / High Risk",
        "notes": "0-4 multi strike."
    },

    # ==========================================
    # 5. MAGIC USER & ADVANCED (WITCH, MAGICAL PRINCESS, SAGE, BISHOP)
    # ==========================================
    "Fireball": {
        "desc": "Deal fire damage to one enemy.",
        "lvup": "Pwr (L1-10): 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520\nTP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32  (Lv1 to Max)",
        "notes": "Single target fire."
    },
    "Icicle": {
        "desc": "Deal water damage to one enemy.",
        "lvup": "Pwr (L1-10): 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520\nTP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32  (Lv1 to Max)",
        "notes": "Single target water."
    },
    "Thunderbolt": {
        "desc": "Deal lightning damage to one enemy.",
        "lvup": "Pwr (L1-10): 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520\nTP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32  (Lv1 to Max)",
        "notes": "Single target lightning."
    },
    "Air Cutter": {
        "desc": "Deal wind damage to one enemy.",
        "lvup": "Pwr (L1-10): 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520\nTP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32  (Lv1 to Max)",
        "notes": "Single target wind."
    },
    "Stone Hammer": {
        "desc": "Deal earth damage to one enemy.",
        "lvup": "Pwr (L1-10): 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520\nTP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32  (Lv1 to Max)",
        "notes": "Single target earth."
    },
    "Heal": {
        "desc": "Heal an ally's HP.",
        "lvup": "Heal Cap (L1-10): 100 -> 150 -> 200 -> 270 -> 350 -> 440 -> 540 -> 650 -> 720 -> 800\nTP Cost: 3 -> 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 23 -> 26  (Lv1 to Max)",
        "notes": "Single target heal."
    },
    "Circle Heal": {
        "desc": "Heal the entire party's HP.",
        "lvup": "Heal Cap (L1-10): 80 -> 120 -> 160 -> 210 -> 270 -> 340 -> 420 -> 510 -> 600 -> 700\nTP Cost: 8 -> 11 -> 14 -> 17 -> 21 -> 25 -> 30 -> 35 -> 40 -> 46  (Lv1 to Max)",
        "notes": "Party heal."
    },
    "Full Heal": {
        "desc": "Fully restore one ally's HP to maximum.",
        "lvup": "Heals 100% Max HP (9,999 HP cap)    |    Chant: 2 turns -> 1 turn\nTP Cost: 35 -> 30 -> 25 -> 20 -> 16 (L1-5)",
        "notes": "Full heal."
    },
    "Nurse": {
        "desc": "Cure status ailments for a single ally.",
        "lvup": "Cures: Poison (L1) -> Paralyze -> Silence -> Freeze -> Sleep -> Petrify -> Slow\nTP Cost: 4 -> 6 -> 8 -> 10 -> 12 -> 14 -> 16 (L1-7)",
        "notes": "Single cure."
    },
    "Circle Nurse": {
        "desc": "Cure status ailments for the entire party.",
        "lvup": "Cures: Poison (L1) -> Paralyze -> Silence -> Freeze -> Sleep -> Petrify -> Slow\nTP Cost: 10 -> 13 -> 16 -> 20 -> 24 -> 28 -> 32 (L1-7)",
        "notes": "Party cure."
    },
    "Mini Circle Nurse": {
        "desc": "Cure status ailments for one row of allies.",
        "lvup": "Cures: Poison (L1) -> Paralyze -> Silence -> Freeze -> Sleep -> Petrify -> Slow\nTP Cost: 7 -> 10 -> 13 -> 16 -> 20 -> 24 -> 28 (L1-7)",
        "notes": "Row cure."
    },
    "Resurrect": {
        "desc": "Revive a fallen ally.",
        "lvup": "Revival HP: 20% -> 35% -> 50% -> 70% -> 100% Max HP (L1-5)\nChant time decreases per level    |    TP Cost: 18 -> 22 -> 26 -> 30 -> 35",
        "notes": "Revives ally."
    },
    "Brave": {
        "desc": "Raise an ally's physical ATK.",
        "lvup": "ATK: +15% -> +20% -> +25% -> +30% -> +35% (L1-5 Max)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Single ATK buff."
    },
    "Protect": {
        "desc": "Raise an ally's physical DEF.",
        "lvup": "DEF: +15% -> +20% -> +25% -> +30% -> +35% (L1-5 Max)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 6 -> 8 -> 10 -> 12 -> 14",
        "notes": "Single DEF buff."
    },
    "Circle Brave": {
        "desc": "Raise the entire party's physical ATK.",
        "lvup": "Party ATK: +10% -> +13% -> +16% -> +20% -> +25% (L1-5)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 14 -> 18 -> 22 -> 26 -> 30",
        "notes": "Party ATK buff."
    },
    "Circle Protect": {
        "desc": "Raise the entire party's physical DEF.",
        "lvup": "Party DEF: +10% -> +13% -> +16% -> +20% -> +25% (L1-5)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 14 -> 18 -> 22 -> 26 -> 30",
        "notes": "Party DEF buff."
    },
    "Sun Veil": {
        "desc": "Raise the party's magical defense against incoming spells.",
        "lvup": "Magic DEF: +15% -> +20% -> +25% -> +30% -> +35% (L1-5)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 12 -> 15 -> 18 -> 21 -> 24",
        "notes": "Magic defense buff."
    },
    "Moon Curtain": {
        "desc": "Raise party resistance to Fire, Water, Lightning, Wind, and Earth.",
        "lvup": "Resist: +15 -> +20 -> +25 -> +30 -> +35 all elements (L1-5)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 12 -> 15 -> 18 -> 21 -> 24",
        "notes": "Elemental resistance."
    },
    "Accelerator": {
        "desc": "Raise an ally's action speed.",
        "lvup": "Speed: +15% -> +20% -> +25% -> +30% -> +35% (L1-5)\nChant time decreases per level    |    TP Cost: 8 -> 10 -> 12 -> 14 -> 16",
        "notes": "Single speed buff."
    },
    "Amplify": {
        "desc": "Temporarily raise an ally's maximum HP cap.",
        "lvup": "Max HP: +15% -> +20% -> +25% -> +30% -> +35% (L1-5)\nTurns: 4 -> 5 -> 6 -> 7 -> 8    |    TP Cost: 10 -> 13 -> 16 -> 19 -> 22",
        "notes": "Max HP boost."
    },
    "Illusion": {
        "desc": "Create magical afterimages that let user dodge incoming attacks.",
        "lvup": "Dodges: 2 guaranteed physical attacks avoided\nTurns: 3 -> 4 -> 5 -> 6 -> 7 (L1-5)    |    TP Cost: 10 -> 13 -> 16 -> 19 -> 22",
        "notes": "Afterimage dodge."
    },
    "Divine Shield": {
        "desc": "Enchant self with a barrier reducing incoming physical damage.",
        "lvup": "Physical Damage Reduction: -20% -> -35% (-3.75%/Lv)    |    Levels: L1-5\nTP Cost: 12 -> 15 -> 18 -> 21 -> 24",
        "notes": "Self physical shield."
    },
    "Light": {
        "desc": "Illuminate dark dungeons to reveal secret passages and hidden doors.",
        "lvup": "Duration: 50 -> 100 -> 150 -> 200 -> 300 steps (L1-5)\nTP Cost: 4 -> 4 -> 4 -> 4 -> 4",
        "notes": "Illumination."
    },
    "Return": {
        "desc": "Immediately teleport the party safely out of the dungeon.",
        "lvup": "TP Cost: 20 -> 15 -> 10 -> 6 -> 2 (L1-5 Max)\nWorks identical to an Emergency Exit item",
        "notes": "Dungeon escape."
    },

    # ==========================================
    # 6. UNIVERSAL & CLASS PASSIVES
    # ==========================================
    "Sword Mastery": {
        "desc": "Increases equipped sword base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK (not total character ATK)",
        "notes": "Weapon mastery."
    },
    "Axe Mastery": {
        "desc": "Increases equipped axe base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Dagger Mastery": {
        "desc": "Increases equipped dagger base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Mace Mastery": {
        "desc": "Increases equipped mace base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Lance Mastery": {
        "desc": "Increases equipped lance base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Bow Mastery": {
        "desc": "Increases equipped bow base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Katana Mastery": {
        "desc": "Increases equipped katana base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Projectile Mastery": {
        "desc": "Increases equipped projectile weapon base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Whip Mastery": {
        "desc": "Increases equipped whip base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Fan Mastery": {
        "desc": "Increases equipped fan base ATK.",
        "lvup": "ATK (L1-10): +3% -> +5% -> +7% -> +9% -> +10% to +15% (+1%/Lv after L4)\nScales off weapon base ATK",
        "notes": "Weapon mastery."
    },
    "Weapon Mastery": {
        "desc": "Increases equipped base ATK for all weapon types.",
        "lvup": "ATK (L1-10): +2% -> +3% -> +4% -> +5% -> +6% -> +7% -> +8% -> +9% -> +10% -> +12%\nUniversal weapon scaling",
        "notes": "All weapon mastery."
    },
    "Magic Mastery": {
        "desc": "Increase magic attack power bonus for all spells.",
        "lvup": "Magic Power (L1-10): +6% (L1) -> +15% (L10 Max)    |    Step: +1%/Lv (+6% base)\nApplies to all offensive spell damage",
        "notes": "Magic power bonus."
    },
    "Heal Mastery": {
        "desc": "Boost potency and maximum HP healing cap of healing magic.",
        "lvup": "Healing Bonus: +10% -> +30% (+2%/Lv up to L5, then +3%/Lv, Max +30%)\nAlso raises baseline healing cap on Heal and Circle Heal",
        "notes": "Healing power bonus."
    },
    "Auto-Recovery": {
        "desc": "Recover HP every turn during battle.",
        "lvup": "HP Regen: 10 -> 20 -> 30 -> 40 -> 50 HP per turn (L1-5)\nTriggers at start of user's action in combat",
        "notes": "HP regen."
    },
    "Auto-Refresh": {
        "desc": "Recover TP every turn during battle.",
        "lvup": "TP Regen (L1-10): 2 -> 3 -> 4 -> 6 -> 8 -> 10 -> 12 -> 14 -> 15 -> 16 TP per turn\nActive on user turn in battle",
        "notes": "TP regen."
    },
    "Mini Auto-Refresh": {
        "desc": "Slightly recover TP every turn during battle.",
        "lvup": "TP Regen: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 TP per turn (L1-8)\nTriggers on user turn in combat",
        "notes": "Minor TP regen."
    },
    "Adaptation": {
        "desc": "Raise innate resistance to all elements.",
        "lvup": "Elemental Resist: +5 -> +10 -> +15 -> +20 -> +25 all elements (L1-5)\nApplies to Fire, Water, Lightning, Wind, and Earth",
        "notes": "All element resist."
    },
    "Avenger": {
        "desc": "Counterattack short/medium physical hits with equipped weapon.",
        "lvup": "Counter Rate: 6% -> 9% -> 12% -> 15% -> 18% (L1-5)    |    Step: +3%/Lv\nNote: Short-range retaliations will trigger enemy Dark Aura",
        "notes": "Physical counter."
    },
    "Mind's Eye": {
        "desc": "Occasionally parry and counterattack when targeted by an enemy.",
        "lvup": "Parry & Counter: 10% -> 25% (+3.75%/Lv)    |    Levels: L1-5\nNullifies incoming attack and strikes back",
        "notes": "Parry counter."
    },
    "Double Attack": {
        "desc": "Chance to attack twice when using normal attacks.",
        "lvup": "Trigger Rate: 9% -> 12% -> 15% -> 18% -> 21% (L1-5)    |    Step: +3%/Lv\nCan stack with Triple Attack (up to 5 strikes total)",
        "notes": "Double strike."
    },
    "Triple Attack": {
        "desc": "Chance to attack thrice when using normal attacks.",
        "lvup": "Trigger Rate: 5% -> 7.5% -> 10% -> 12.5% -> 15% (L1-5)    |    Step: +2.5%/Lv\nStacks with Double Attack",
        "notes": "Triple strike."
    },
    "Guts": {
        "desc": "Occasionally survive at 1 HP after receiving fatal damage.",
        "lvup": "Survival Rate: 20% -> 30% -> 40% -> 50% -> 60% (L1-5)    |    Step: +10%/Lv\nPrevents death when hit by lethal blows",
        "notes": "Fatal survival."
    },
    "Auto-Guard": {
        "desc": "Occasionally Defend automatically when receiving physical attacks.",
        "lvup": "Auto-Guard Rate: 10% -> 15% -> 20% -> 25% -> 30% (L1-5)    |    Step: +5%/Lv\nHalves incoming damage when triggered",
        "notes": "Auto defense."
    },
    "Dual Wield": {
        "desc": "Equip two one-handed weapons simultaneously.",
        "lvup": "Off-Hand ATK: 50% -> 57.5% -> 65% -> 72.5% -> 80% (L1-5)    |    Step: +7.5%/Lv\nMain hand weapon deals 100% ATK",
        "notes": "Dual weapons."
    },
    "Concentrate": {
        "desc": "Make it harder for chants, songs, and dances to be interrupted.",
        "lvup": "Interruption Resist: +20% -> +50% (+7.5%/Lv)    |    Levels: L1-5\nCrucial for casters and performers in front row",
        "notes": "Chant protection."
    },
    "Fast Cast": {
        "desc": "Reduce chant time required to cast spells.",
        "lvup": "Chant Time Reduction: -10% -> -30% (-5%/Lv)    |    Levels: L1-5\nAccelerates offensive and healing magic activation",
        "notes": "Chant acceleration."
    },
    "Economy": {
        "desc": "Reduce TP consumption in battle.",
        "lvup": "TP Cost Reduction: -10% -> -15% -> -20% -> -25% -> -30% (L1-5)\nLowers cost of all techniques and spells",
        "notes": "TP discount."
    },
    "Treasure Hunt": {
        "desc": "Increase enemies' item drop rate after battle.",
        "lvup": "Item Drop Rate: +10% -> +15% -> +20% -> +25% -> +30% (L1-5)\nBoosts party equipment and material acquisition",
        "notes": "Drop rate buff."
    },
    "Lucky Me": {
        "desc": "Increase amount of gold dropped by defeated enemies.",
        "lvup": "Gold Gain: +15% -> +23% -> +32% -> +41% -> +50% (L1-5)\nEarn bonus currency after every battle",
        "notes": "Gold boost."
    },
    "Item Mastery": {
        "desc": "Increase effects of HP and TP recovery items during battle.",
        "lvup": "Item Potency: +20% -> +30% -> +40% -> +50% -> +60% (L1-5)\nApplies to all consumable recovery items used in combat",
        "notes": "Item potency."
    },
    "Maid Mastery": {
        "desc": "Increased potency and effectiveness for all maid skills.",
        "lvup": "Maid Skill Bonus: +2% -> +4% -> +6% -> +8% -> +10% (L1-5)\nEmpowers First Aid, Cook, and Clean",
        "notes": "Maid bonus."
    },
    "Song Mastery": {
        "desc": "Increased potency and effectiveness for all songs.",
        "lvup": "Song Potency: +3% -> +6% -> +9% -> +12% -> +15% (L1-5)\nEmpowers Bard songs and regeneration rates",
        "notes": "Song bonus."
    },
    "Dance Mastery": {
        "desc": "Increased potency and effectiveness for all dances.",
        "lvup": "Dance Potency: +3% -> +6% -> +9% -> +12% -> +15% (L1-5)\nEmpowers Dancer dances and status effects",
        "notes": "Dance bonus."
    },
    "Critical Magic": {
        "desc": "Occasionally land critical hits with offensive spells.",
        "lvup": "Spell Crit Rate: +10% -> +13.75% -> +17.5% -> +21.25% -> +25% (L1-5)\nSpell criticals deal 1.50x normal magic damage",
        "notes": "Spell critical."
    },

    # ==========================================
    # 7. HEROINE UNIQUE PASSIVES (18 GIRLS)
    # ==========================================
    "Positive Trance": {
        "desc": "Significantly increase damage according to Pep.",
        "lvup": "Damage: +1% per Pep point (up to +100% damage at Max Pep)\nHeroine: Luco    |    Scales with high morale",
        "notes": "Luco unique."
    },
    "Third Eye Wide": {
        "desc": "Occasionally inflict enemies with status ailments or Dispel at random.",
        "lvup": "Activation Rate: 15% on enemy action    |    Heroine: Mefmera\nInflicts Poison, Paralyze, Silence, or cancels enemy buffs",
        "notes": "Mefmera unique."
    },
    "Sugar Coma": {
        "desc": "Counter short-range physical attacks with Slow and Speed decrease.",
        "lvup": "Counter Rate: 25% on physical contact    |    Inflicts -30% Speed\nHeroine: Souffle",
        "notes": "Souffle unique."
    },
    "Elbow Grease": {
        "desc": "Increase weapon modifier when attacking with weapon-based skills.",
        "lvup": "Weapon Scaling: +25% damage to all weapon-based techniques\nHeroine: Grishna",
        "notes": "Grishna unique."
    },
    "Furious Strike": {
        "desc": "May guarantee a 100% hit and bypass enemy DEF with physical attacks.",
        "lvup": "Activation Rate: 20% on physical strikes    |    Ignores target DEF\nHeroine: Yae",
        "notes": "Yae unique."
    },
    "Alter Fate": {
        "desc": "Occasionally nullify all damage received from enemies.",
        "lvup": "Nullification Rate: 10% chance to completely negate incoming damage\nHeroine: Lize",
        "notes": "Lize unique."
    },
    "Usurper of Souls": {
        "desc": "Before acting, may erase enemy puppets, familiars, or summons.",
        "lvup": "Banish Rate: 25% chance to instantly eliminate enemy summon entities\nHeroine: Lilian",
        "notes": "Lilian unique."
    },
    "Overstock Clearance": {
        "desc": "Before acting, may use an item from personal stock without cost.",
        "lvup": "Trigger Rate: 20% chance to use free recovery item at turn start\nHeroine: Monica",
        "notes": "Monica unique."
    },
    "Wreathed in Glory": {
        "desc": "Decrease turn delay after using skills or magic.",
        "lvup": "Action Delay Reduction: -20% recovery delay after any action\nHeroine: Alisia",
        "notes": "Alisia unique."
    },
    "Maximum Maid": {
        "desc": "Increased potency and effectiveness for all maid skills.",
        "lvup": "Maid Skill Potency: +15% effectiveness to First Aid, Cook, etc.\nHeroine: Conette",
        "notes": "Conette unique."
    },
    "Did You Call for Me?": {
        "desc": "May occasionally act twice in one turn.",
        "lvup": "Double Action Rate: 15% chance to receive an extra turn immediately\nHeroine: Yuni",
        "notes": "Yuni unique."
    },
    "Undaunted Spirit": {
        "desc": "If killed in battle, revive after 3 turns.",
        "lvup": "Auto-Revive: Resurrects with 50% HP after 3 combat turns\nHeroine: Gina",
        "notes": "Gina unique."
    },
    "Demon Wall": {
        "desc": "Whole row takes less damage from Demons, Undead, and Apparitions.",
        "lvup": "Row Damage Mitigation: -20% incoming damage from specified monster types\nHeroine: Ist",
        "notes": "Ist unique."
    },
    "Tranquil Song": {
        "desc": "May lower all enemies' ATK and INT at start of turn.",
        "lvup": "Trigger Rate: 15% at turn start    |    Inflicts -20% ATK and -20% INT\nHeroine: Fiora",
        "notes": "Fiora unique."
    },
    "Forerunner": {
        "desc": "Magic will occasionally activate immediately without chanting.",
        "lvup": "Instant Cast Rate: 15% chance for cast spells to trigger with 0 chant time\nHeroine: Eltricia",
        "notes": "Eltricia unique."
    },
    "Arcane Shield": {
        "desc": "Occasionally reflects incoming damage back as fixed neutral damage.",
        "lvup": "Reflect Rate: 20% chance to reflect 30% of received damage to attacker\nHeroine: Melvy",
        "notes": "Melvy unique."
    },
    "Shadow Heart": {
        "desc": "Summons a shadow clone on normal attacks to deliver an extra strike.",
        "lvup": "Shadow Strike: Normal attacks trigger an extra hit dealing 75% damage\nHeroine: Tsurara",
        "notes": "Tsurara unique."
    },
    "Yearning": {
        "desc": "Increased effects for all class modifiers and masteries.",
        "lvup": "Class Stat Potency: +10% to all class stat bonuses and weapon masteries\nHeroine: Siena",
        "notes": "Siena unique."
    }
}

count = 0
for row in ws.iter_rows(min_row=2):
    name = row[3].value
    if name in SKILL_DATA:
        s = SKILL_DATA[name]
        row[8].value = s["desc"]
        row[9].value = s["lvup"]
        row[10].value = "Approved"
        row[11].value = s["notes"]
        count += 1

wb.save('mod_project/data_tables/skills.xlsx')
print(f"Successfully populated {count} skills in skills.xlsx")

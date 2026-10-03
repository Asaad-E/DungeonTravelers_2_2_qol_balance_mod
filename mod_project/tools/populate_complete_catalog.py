import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/skills.xlsx')
ws = wb['Skills']

FULL_CATALOG = {
    # ==========================================
    # MAGIC USER / SORCERESS / WITCH / SAGE / BISHOP
    # ==========================================
    "Ice Edge": {
        "desc": "Deal water damage to one enemy.",
        "lvup": "Pwr (L1-10): 70 -> 105 -> 140 -> 175 -> 220 -> 270 -> 320 -> 380 -> 450 -> 520\nTP Cost: 5 -> 7 -> 9 -> 11 -> 14 -> 17 -> 20 -> 24 -> 28 -> 32 (Lv1 to Max)"
    },
    "Fire Blast": {
        "desc": "Deal fire damage to an enemy row.",
        "lvup": "Pwr (L1-10): 90 -> 125 -> 160 -> 200 -> 250 -> 300 -> 360 -> 420 -> 480 -> 530\nTP Cost: 15 -> 19 -> 23 -> 27 -> 32 -> 37 -> 43 -> 49 -> 55 -> 60 (Lv1 to Max)"
    },
    "Ice Storm": {
        "desc": "Deal water damage to an enemy row.",
        "lvup": "Pwr (L1-10): 90 -> 125 -> 160 -> 200 -> 250 -> 300 -> 360 -> 420 -> 480 -> 530\nTP Cost: 15 -> 19 -> 23 -> 27 -> 32 -> 37 -> 43 -> 49 -> 55 -> 60 (Lv1 to Max)"
    },
    "Thunder Chain": {
        "desc": "Deal lightning damage to an enemy row.",
        "lvup": "Pwr (L1-10): 90 -> 125 -> 160 -> 200 -> 250 -> 300 -> 360 -> 420 -> 480 -> 530\nTP Cost: 15 -> 19 -> 23 -> 27 -> 32 -> 37 -> 43 -> 49 -> 55 -> 60 (Lv1 to Max)"
    },
    "Air Turbulence": {
        "desc": "Deal wind damage to an enemy row.",
        "lvup": "Pwr (L1-10): 90 -> 125 -> 160 -> 200 -> 250 -> 300 -> 360 -> 420 -> 480 -> 530\nTP Cost: 15 -> 19 -> 23 -> 27 -> 32 -> 37 -> 43 -> 49 -> 55 -> 60 (Lv1 to Max)"
    },
    "Stone Shower": {
        "desc": "Deal earth damage to an enemy row.",
        "lvup": "Pwr (L1-10): 90 -> 125 -> 160 -> 200 -> 250 -> 300 -> 360 -> 420 -> 480 -> 530\nTP Cost: 15 -> 19 -> 23 -> 27 -> 32 -> 37 -> 43 -> 49 -> 55 -> 60 (Lv1 to Max)"
    },
    "Inferno": {
        "desc": "Deal fire damage to all enemies.",
        "lvup": "Pwr (L1-10): 80 -> 110 -> 140 -> 180 -> 230 -> 280 -> 340 -> 400 -> 460 -> 510\nTP Cost: 25 -> 30 -> 35 -> 41 -> 48 -> 55 -> 63 -> 71 -> 79 -> 88 (Lv1 to Max)"
    },
    "Diamond Dust": {
        "desc": "Deal water damage to all enemies.",
        "lvup": "Pwr (L1-10): 80 -> 110 -> 140 -> 180 -> 230 -> 280 -> 340 -> 400 -> 460 -> 510\nTP Cost: 25 -> 30 -> 35 -> 41 -> 48 -> 55 -> 63 -> 71 -> 79 -> 88 (Lv1 to Max)"
    },
    "Lightning": {
        "desc": "Deal lightning damage to all enemies.",
        "lvup": "Pwr (L1-10): 80 -> 110 -> 140 -> 180 -> 230 -> 280 -> 340 -> 400 -> 460 -> 510\nTP Cost: 25 -> 30 -> 35 -> 41 -> 48 -> 55 -> 63 -> 71 -> 79 -> 88 (Lv1 to Max)"
    },
    "Tornado": {
        "desc": "Deal wind damage to all enemies.",
        "lvup": "Pwr (L1-10): 80 -> 110 -> 140 -> 180 -> 230 -> 280 -> 340 -> 400 -> 460 -> 510\nTP Cost: 25 -> 30 -> 35 -> 41 -> 48 -> 55 -> 63 -> 71 -> 79 -> 88 (Lv1 to Max)"
    },
    "Meteor": {
        "desc": "Deal earth damage to all enemies.",
        "lvup": "Pwr (L1-10): 80 -> 110 -> 140 -> 180 -> 230 -> 280 -> 340 -> 400 -> 460 -> 510\nTP Cost: 25 -> 30 -> 35 -> 41 -> 48 -> 55 -> 63 -> 71 -> 79 -> 88 (Lv1 to Max)"
    },
    "Crimson Flare": {
        "desc": "Unleash devastating master fire magic on one enemy.",
        "lvup": "Pwr (L1-10): 620 -> 680 -> 750 -> 830 -> 920 -> 1010 -> 1100 -> 1200 -> 1250 -> 1300\nTP Cost: 40 -> 44 -> 48 -> 53 -> 58 -> 64 -> 70 -> 76 -> 80 -> 84 (Lv1 to Max)"
    },
    "Cocytus": {
        "desc": "Unleash devastating master water magic on one enemy.",
        "lvup": "Pwr (L1-10): 620 -> 680 -> 750 -> 830 -> 920 -> 1010 -> 1100 -> 1200 -> 1250 -> 1300\nTP Cost: 40 -> 44 -> 48 -> 53 -> 58 -> 64 -> 70 -> 76 -> 80 -> 84 (Lv1 to Max)"
    },
    "Muon Plasma": {
        "desc": "Unleash devastating master lightning magic on one enemy.",
        "lvup": "Pwr (L1-10): 620 -> 680 -> 750 -> 830 -> 920 -> 1010 -> 1100 -> 1200 -> 1250 -> 1300\nTP Cost: 40 -> 44 -> 48 -> 53 -> 58 -> 64 -> 70 -> 76 -> 80 -> 84 (Lv1 to Max)"
    },
    "Tempest": {
        "desc": "Unleash devastating master wind magic on one enemy.",
        "lvup": "Pwr (L1-10): 620 -> 680 -> 750 -> 830 -> 920 -> 1010 -> 1100 -> 1200 -> 1250 -> 1300\nTP Cost: 40 -> 44 -> 48 -> 53 -> 58 -> 64 -> 70 -> 76 -> 80 -> 84 (Lv1 to Max)"
    },
    "Gaia Crush": {
        "desc": "Unleash devastating master earth magic on one enemy.",
        "lvup": "Pwr (L1-10): 620 -> 680 -> 750 -> 830 -> 920 -> 1010 -> 1100 -> 1200 -> 1250 -> 1300\nTP Cost: 40 -> 44 -> 48 -> 53 -> 58 -> 64 -> 70 -> 76 -> 80 -> 84 (Lv1 to Max)"
    },
    "Poison": {
        "desc": "Poison all enemies (5% Max HP damage per enemy turn, cap 250).",
        "lvup": "Accuracy: +15% -> +35% (+5%/Lv) | Chant: 1.20x -> 1.40x\nTP Cost: 4 -> 5 -> 6 -> 7 -> 8 (L1-5)"
    },
    "Stun": {
        "desc": "Deal magic damage to one enemy. May stun.",
        "lvup": "Stun Chance: 30% -> 60% (+7.5%/Lv) | Levels: L1-5\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Freeze": {
        "desc": "Deal water magic damage to one enemy. May freeze.",
        "lvup": "Freeze Chance: 30% -> 60% (+7.5%/Lv) | Levels: L1-5\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Paralyze": {
        "desc": "Deal lightning magic damage to one enemy. May paralyze.",
        "lvup": "Paralysis Chance: 30% -> 60% (+7.5%/Lv) | Levels: L1-5\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Sleep": {
        "desc": "Put an enemy to sleep with magic.",
        "lvup": "Sleep Chance: 40% -> 70% (+7.5%/Lv) | Levels: L1-5\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Silence": {
        "desc": "Silence an enemy to prevent spell casting.",
        "lvup": "Silence Chance: 40% -> 70% (+7.5%/Lv) | Levels: L1-5\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Petrify": {
        "desc": "Turn one enemy to stone with earth magic.",
        "lvup": "Petrify Chance: 20% -> 40% (+5%/Lv) | Levels: L1-5\nTP Cost: 10 -> 13 -> 16 -> 19 -> 22"
    },
    "Death": {
        "desc": "Attempt to instantly slay one living enemy.",
        "lvup": "Instakill Chance: 15% -> 35% (+5%/Lv) | Levels: L1-5\nTP Cost: 15 -> 18 -> 21 -> 24 -> 28"
    },
    "Slow": {
        "desc": "Inflict Slow on an enemy row, cutting action speed by -50%.",
        "lvup": "Slow Chance: 35% -> 65% (+7.5%/Lv) | Inflicts -50% Speed\nTP Cost: 15 -> 17 -> 19 -> 21 -> 23 (L1-5)"
    },
    "Terrorize": {
        "desc": "Terrify an enemy with dark magic to inflict Stun.",
        "lvup": "Stun Chance: 30% -> 60% (+7.5%/Lv) | Levels: L1-5\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16"
    },
    "Blood Absorb": {
        "desc": "Neutral magic strike to one enemy. Absorb damage dealt as HP.",
        "lvup": "Pwr: 60 -> 120 -> 180 -> 260 -> 350 (L1-5) | Bypasses elemental resists\nTP Cost: 9 -> 11 -> 13 -> 15 -> 18"
    },
    "Soul Absorb": {
        "desc": "Neutral magic strike to one enemy. Absorb damage dealt as TP.",
        "lvup": "Pwr: 22 -> 35 -> 50 -> 65 -> 82 (L1-5) | Restores TP equal to damage dealt\nTP Cost: 6 -> 8 -> 10 -> 12 -> 15"
    },
    "Blood Rage": {
        "desc": "Boost own magic attack power at the cost of consuming HP.",
        "lvup": "Magic ATK: +20% -> +40% (+5%/Lv) | HP Cost: 10% Max HP\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 10 -> 12 -> 14 -> 16 -> 18"
    },
    "Life Bring": {
        "desc": "Transfer a portion of user HP to restore an ally's HP.",
        "lvup": "Heal: 30% -> 60% (+7.5%/Lv) of target Max HP | Consumes 20% user HP\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16 (L1-5)"
    },
    "Fire Enchant": {
        "desc": "Imbue an ally's weapon with Fire element.",
        "lvup": "Turns: 4 -> 5 -> 6 -> 7 -> 8 (L1-5) | Adds Fire damage to weapon strikes\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Water Enchant": {
        "desc": "Imbue an ally's weapon with Water element.",
        "lvup": "Turns: 4 -> 5 -> 6 -> 7 -> 8 (L1-5) | Adds Water damage to weapon strikes\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Lightning Enchant": {
        "desc": "Imbue an ally's weapon with Lightning element.",
        "lvup": "Turns: 4 -> 5 -> 6 -> 7 -> 8 (L1-5) | Adds Lightning damage to weapon strikes\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Wind Enchant": {
        "desc": "Imbue an ally's weapon with Wind element.",
        "lvup": "Turns: 4 -> 5 -> 6 -> 7 -> 8 (L1-5) | Adds Wind damage to weapon strikes\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Earth Enchant": {
        "desc": "Imbue an ally's weapon with Earth element.",
        "lvup": "Turns: 4 -> 5 -> 6 -> 7 -> 8 (L1-5) | Adds Earth damage to weapon strikes\nTP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Stab Guard": {
        "desc": "Raise one row of allies' resistance to stab damage.",
        "lvup": "Stab Resistance: +15 -> +35 (+5/Lv) | Levels: L1-5\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 10 -> 12 -> 14 -> 16 -> 18"
    },
    "Slash Guard": {
        "desc": "Raise one row of allies' resistance to slash damage.",
        "lvup": "Slash Resistance: +15 -> +35 (+5/Lv) | Levels: L1-5\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 10 -> 12 -> 14 -> 16 -> 18"
    },
    "Bash Guard": {
        "desc": "Raise one row of allies' resistance to bash damage.",
        "lvup": "Bash Resistance: +15 -> +35 (+5/Lv) | Levels: L1-5\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 10 -> 12 -> 14 -> 16 -> 18"
    },

    # ==========================================
    # PASSIVES REMAINING
    # ==========================================
    "Pretend": {
        "desc": "Occasionally nullify physical damage.",
        "lvup": "Nullify Rate: 8% -> 20% (+3%/Lv) | Levels: L1-5\nCompletely negates incoming physical attacks when triggered"
    },
    "Esarhaddon": {
        "desc": "Automatically cure own status ailments at start of turn.",
        "lvup": "Cures: Poison (L1) -> Paralyze -> Silence -> Freeze -> Sleep -> Slow\nTriggers automatically at start of user's combat turn"
    },
    "Ecstasy": {
        "desc": "Boost physical ATK and DEX when HP drops below 50%.",
        "lvup": "ATK & DEX: +20% -> +40% (+5%/Lv) when HP < 50% | Levels: L1-5\nImmediate combat stat trigger"
    },
    "Nirvana": {
        "desc": "Heighten magic accuracy for all cast spells.",
        "lvup": "Magic Accuracy: +15% -> +35% (+5%/Lv) | Levels: L1-5\nSignificantly reduces spell evasion by high RES targets"
    },
    "Caution": {
        "desc": "Reduce enemy preemptive strike rate in dungeons.",
        "lvup": "Preemptive Reduction: -20% -> -60% (-10%/Lv) | Levels: L1-5\nProtects party from surprise enemy encounters"
    },
    "Awareness": {
        "desc": "Increase party's preemptive strike rate against foes.",
        "lvup": "Party Preemptive Rate: +10% -> +30% (+5%/Lv) | Levels: L1-5\nGrants free initial turn before enemies act"
    },
    "Elusiveness": {
        "desc": "Increase success rate when attempting to flee from battle.",
        "lvup": "Escape Success: +20% -> +50% (+7.5%/Lv) | Levels: L1-5\nDoes not apply to scripted boss battles"
    },
    "Present for Me": {
        "desc": "Occasionally discover items while exploring dungeons.",
        "lvup": "Item Find Rate: +10% -> +30% (+5%/Lv) | Levels: L1-5\nFinds consumables and crafting materials while walking"
    },
    "Generous Heart": {
        "desc": "Restore party HP and TP slightly after winning a battle.",
        "lvup": "Post-Battle Recovery: 5% -> 15% HP & TP (+2.5%/Lv) | Levels: L1-5\nRestores whole party after combat conclusion"
    },
    "Recycle": {
        "desc": "Occasionally retain disposable items after using them in combat.",
        "lvup": "Item Retain Chance: 15% -> 35% (+5%/Lv) | Levels: L1-5\nItem is not consumed from inventory when triggered"
    },
    "Self Session": {
        "desc": "Become capable of performing two songs simultaneously.",
        "lvup": "Singing Speed: +10% -> +30% (+5%/Lv) | Levels: L1-5\nAllows maintaining 2 active Bard songs at once"
    },
    "On Stage": {
        "desc": "Become capable of performing two dances simultaneously.",
        "lvup": "Dancing Speed: +10% -> +30% (+5%/Lv) | Levels: L1-5\nAllows maintaining 2 active Dancer dances at once"
    },
    "Double Puppet": {
        "desc": "Become capable of controlling two summoned dolls at once.",
        "lvup": "Doll Control Speed: +10% -> +30% (+5%/Lv) | Levels: L1-5\nMaintains 2 active summoned dolls simultaneously"
    },
    "Soul Seal": {
        "desc": "Increase doll power with strength of equipped Sealbook.",
        "lvup": "Doll Power Bonus: +10% -> +30% (+5%/Lv) based on Sealbook level\nLevels: L1-5"
    },
    "Doll Mastery": {
        "desc": "Increased potency and effectiveness for all doll skills.",
        "lvup": "Doll Stat Bonus: +3% -> +15% (+3%/Lv) | Levels: L1-5\nIncreases damage, healing, and durability of summoned dolls"
    },
    "Barrage": {
        "desc": "Occasionally attack twice when performing normal attacks.",
        "lvup": "Double Attack Rate: 8% -> 20% (+3%/Lv) | Levels: L1-5\nNormal attack trigger"
    },
    "Fast Talk": {
        "desc": "Reduce chant time required to start songs.",
        "lvup": "Song Chant Reduction: -10% -> -30% (-5%/Lv) | Levels: L1-5\nAccelerates Bard song activation"
    },
    "Negotiate": {
        "desc": "Reduce purchase and identification prices at shops.",
        "lvup": "Shop Discount: -5% -> -25% (-5%/Lv) | Levels: L1-5\nLowers gold cost for item purchases and item identification"
    },
    "Magnificent Steps": {
        "desc": "Mesmerize enemies with dance steps, causing them to lose turns.",
        "lvup": "Mesmerize Rate: 5% -> 15% (+2.5%/Lv) | Levels: L1-5\nEnemy skips turn when mesmerized"
    },
    "Elegant Dancing": {
        "desc": "Nullify first hit of battle against user.",
        "lvup": "100% nullification of the very first physical attack received\nFixed passive (Level 1)"
    },
    "Triple Joker": {
        "desc": "Heighten probability of beneficial results for random skills.",
        "lvup": "Drastically increases odds of favorable outcomes on Gamble skills\nFixed passive (Level 1)"
    },
    "Destiny Line": {
        "desc": "Increase doll summon duration on battlefield.",
        "lvup": "Doll Summon Duration: +1 turn (Summons persist longer in battle)\nFixed passive (Level 1)"
    },

    # ==========================================
    # TECHNIQUES REMAINING
    # ==========================================
    "Backward Swing": {
        "desc": "Katana skill. Deal bash damage to one enemy. May paralyze.",
        "lvup": "ATK: 120% -> 180% (+15%/Lv) | Paralysis: 25% -> 50% (+6.25%/Lv)\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16"
    },
    "Last Stand": {
        "desc": "Greatly boost own critical rate, but increase vulnerability to crits.",
        "lvup": "Crit Rate: +25% -> +55% (+7.5%/Lv) | Enemy Crit: +15% -> +25%\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 8 -> 10 -> 12 -> 14 -> 16"
    },
    "Ether Strike": {
        "desc": "Sword and lance skill. Pierces through to the back row.",
        "lvup": "ATK: 135% -> 195% (+15%/Lv) | Hits front and back target\nTP Cost: 12 -> 14 -> 16 -> 18 -> 20"
    },
    "Cleanse": {
        "desc": "Cure status ailments for a single ally.",
        "lvup": "Cures: Poison (L1) -> Paralyze -> Silence -> Freeze -> Sleep\nTP Cost: 3 -> 5 -> 7 -> 9 -> 11 (L1-5)"
    },
    "Warm-Up": {
        "desc": "Increase own physical evasion and magic evasion.",
        "lvup": "Physical & Magic EVA: +12% -> +28% (+4%/Lv) | Levels: L1-5\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 6 -> 8 -> 10 -> 12 -> 14"
    },
    "Gravity Shot": {
        "desc": "Bow skill. Deal stab damage to one enemy. May slow.",
        "lvup": "ATK: 115% -> 175% (+15%/Lv) | Slow: 25% -> 50% (+6.25%/Lv)\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16"
    },
    "Ninja Piledriver": {
        "desc": "Deal bash damage to one enemy. May stun.",
        "lvup": "ATK: 130% -> 190% (+15%/Lv) | Stun: 30% -> 60% (+7.5%/Lv)\nTP Cost: 10 -> 12 -> 14 -> 16 -> 18"
    },
    "Identify": {
        "desc": "Identify unknown dungeon loot items.",
        "lvup": "Success Rate: 70% -> 98% (+7%/Lv) | Levels: L1-5\nTP Cost: 5 -> 4 -> 3 -> 2 -> 1 (Max)"
    },
    "Holy Gavel": {
        "desc": "Mace skill. Heavy bash strike with boosted accuracy.",
        "lvup": "ATK: 140% -> 200% (+15%/Lv) | Accuracy: +25% -> +45% (+5%/Lv)\nTP Cost: 10 -> 12 -> 14 -> 16 -> 18"
    },
    "Justice": {
        "desc": "Mace skill. Strike target and reduce enemy physical DEF by 10%.",
        "lvup": "ATK: 125% -> 185% (+15%/Lv) | Inflicts -10% DEF debuff\nTP Cost: 8 -> 10 -> 12 -> 14 -> 16 | Fast turn recovery (0.85x delay)"
    },
    "Magical Slash": {
        "desc": "Sword skill. Deal slash damage to all enemies on screen.",
        "lvup": "ATK: 120% -> 160% (+10%/Lv, L1-5) | Hits all foes\nTP Cost: 36 -> 46 -> 57 -> 68 -> 79 | Action delay: 0.80x -> 0.98x"
    },
    "Magical Spark": {
        "desc": "Short-range strike dealing heavy lightning damage to one enemy.",
        "lvup": "ATK: 136% -> 216% (+20%/Lv, L1-5) | Lightning element\nTP Cost: 13 -> 20 -> 28 -> 36 -> 45"
    },
    "Magical Change": {
        "desc": "Transform into Magical Princess, raising all stats.",
        "lvup": "All Stats: +15% -> +35% (+5%/Lv) | Levels: L1-5\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 16 -> 20 -> 24 -> 28 -> 32"
    },
    "Holy Prayer": {
        "desc": "Focus divine power to restore own TP.",
        "lvup": "TP Restore: 16% -> 25% Max TP (+2.25%/Lv) | Levels: L1-5\nTP Cost: 0 | Action delay: 1.00x"
    },
    "Fascinating Waltz": {
        "desc": "Dance skill. Lower all enemies' physical ATK while dance lasts.",
        "lvup": "Enemy ATK: -12% -> -24% (-3%/Lv) | Levels: L1-5\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 8 -> 10 -> 12 -> 14 -> 16"
    },
    "Alluring Samba": {
        "desc": "Dance skill. Lower all enemies' physical DEF while dance lasts.",
        "lvup": "Enemy DEF: -12% -> -24% (-3%/Lv) | Levels: L1-5\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 8 -> 10 -> 12 -> 14 -> 16"
    },
    "Hard Whipping": {
        "desc": "Whip skill. Deal bash damage to an enemy row from mid-range.",
        "lvup": "ATK: 120% -> 180% (+15%/Lv) | Row bash attack\nTP Cost: 12 -> 15 -> 18 -> 21 -> 24 (L1-5)"
    },
    "Checkmate": {
        "desc": "Attack one enemy. May instakill.",
        "lvup": "ATK: 140% -> 200% (+15%/Lv) | Instakill Chance: 15% -> 35% (+5%/Lv)\nTP Cost: 16 -> 19 -> 22 -> 25 -> 28 (L1-5)"
    },
    "High Risk, High Return": {
        "desc": "Greatly boost own physical ATK at the cost of reducing DEF to 0.",
        "lvup": "ATK: +40% -> +80% (+10%/Lv) | User DEF reduced to 0\nTurns: 4 -> 5 -> 6 -> 7 -> 8 | TP Cost: 12 -> 15 -> 18 -> 21 -> 24"
    },
    "Trump Card": {
        "desc": "Convert current DEF to bonus ATK (user DEF becomes 0).",
        "lvup": "ATK Bonus: 100% -> 150% of converted DEF value (+12.5%/Lv)\nTurns: 3 -> 4 -> 5 -> 6 -> 7 | TP Cost: 14 -> 17 -> 20 -> 23 -> 26"
    },
    "Tinker Squash": {
        "desc": "Fan skill. Deal bash damage to one enemy and delay target turn.",
        "lvup": "ATK: 120% -> 180% (+15%/Lv) | Action Delay: -20% -> -40%\nTP Cost: 10 -> 12 -> 14 -> 16 -> 18"
    },
    "Spartan": {
        "desc": "Summon puppet Spartan to attack enemies with short-range bash strikes.",
        "lvup": "Puppet Power: 100% -> 160% (+15%/Lv) | Duration: 4 -> 6 turns\nTP Cost: 14 -> 17 -> 20 -> 23 -> 26 (L1-5)"
    },
    "Catalina": {
        "desc": "Summon puppet Catalina to heal party members' HP.",
        "lvup": "Heal Potency: 20% -> 40% Max HP (+5%/Lv) | Duration: 4 -> 6 turns\nTP Cost: 14 -> 17 -> 20 -> 23 -> 26 (L1-5)"
    },
    "Perdurabo": {
        "desc": "Summon puppet Perdurabo to cure allies' status ailments.",
        "lvup": "Cures status ailments for 2 allies per turn | Duration: 4 -> 6 turns\nTP Cost: 12 -> 15 -> 18 -> 21 -> 24 (L1-5)"
    },
    "Musiy": {
        "desc": "Summon puppet Musiy to cast immediate single-target attack spells.",
        "lvup": "Spell Pwr: 120 -> 240 (+30/Lv) | Duration: 4 -> 6 turns\nTP Cost: 16 -> 20 -> 24 -> 28 -> 32 (L1-5)"
    }
}

count = 0
for row in ws.iter_rows(min_row=2):
    name = row[3].value
    if name in FULL_CATALOG:
        entry = FULL_CATALOG[name]
        row[8].value = entry["desc"]
        row[9].value = entry["lvup"]
        row[10].value = "Approved"
        count += 1
        print(f"Approved skill: {name}")

wb.save('mod_project/data_tables/skills.xlsx')
print(f"Total skills newly approved: {count}")

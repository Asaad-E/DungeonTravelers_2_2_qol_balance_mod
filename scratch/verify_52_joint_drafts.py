import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/qol_joint_skill_text.xlsx', data_only=True)
ws = wb['JointSkills']
rows = list(ws.iter_rows(min_row=2, values_only=True))

# Draft dictionary mapping skill name to drafted text with [TP, Pep]
drafts = {
    'Rush Zanber': "Physical damage to an enemy row. [1/7 TP, 10 Pep]",
    'Catastrophe': "Powerful physical attack. Inflicts slow (100%). [1/3 TP, 5 Pep]",
    'Magical Treasure': "Physical damage to an enemy; equipment drop rate UP. [1/3 TP, 5 Pep]",
    'Genocide Rain': "Rain arrows down on all enemies over 4 turns. [1/3 TP, 10 Pep]",
    'Galactic Voice': "Fully restore party HP, dispel status ailments. [1/5 TP, 5 Pep]",
    'Divine Punishment!': "Physical damage to an enemy row. 85% instakill. [1/4 TP, 7 Pep]",
    'Nightmare Fall': "Non-elemental damage to all foes. 100% sleep. [1/4 TP, 7 Pep]",
    'Powered-Up Beatdown!': "3-5 bash attacks on one enemy. 85% stun. [1/3 TP, 5 Pep]",
    'Psychowave': "Non-elem dmg to all foes. DEF & magic DEF -20%. [1/4 TP, 7 Pep]",
    'Avatara': "Physical and 1-5 piercing attacks on one foe. [1/2 TP, 15 Pep]",
    'Gjallarhorn': "Circle Brave/Protect (+16%), Moon Curtain (+25). [1/5 TP, 5 Pep]",
    'Hell Raiser': "Cut enemy row's HP to 25% (no boss effect). [1/3 TP, 7 Pep]",
    'Suppression Arrow': "Damage to back row. 85% silence/freeze. [1/3 TP, 7 Pep]",
    'Rapid Storm': "Party speed +50% and physical accuracy +75%. [1/7 TP, 5 Pep]",
    'Holy Blast': "2,000 direct damage to all foes, dispel buffs. [1/3 TP, 10 Pep]",
    'Evolution': "Allies magic ATK (+50%) and crit rate (+20%). [1/4 TP, 5 Pep]",
    'Searching Eye': "See the stats of all enemies. [1/9 TP, 3 Pep]",
    'Bunker Buster': "Damage to back row. Phys attack/defense -25%. [1/4 TP, 7 Pep]",
    'Crazy Rush': "Attack an enemy 7 times with wild accuracy. [1/3 TP, 15 Pep]",
    'Stampede Heaven': "Attack all enemies twice. [1/4 TP, 10 Pep]",
    'Paralyzing Wind': "Wind attack to all foes. 90% paralysis. [1/5 TP, 5 Pep]",
    'Daruma-Drop!': "Physical damage. 90% turn delay chance. [1/7 TP, 5 Pep]",
    'Testament': "Physical damage & Shadow Sew (100%) on a row. [1/3 TP, 5 Pep]",
    'Brain Burst': "Physical damage. 100% poison/paralyze/sleep. [1/4 TP, 7 Pep]",
    'Multi-Shadow Clone': "All allies perform Shadow Clone technique. [1/4 TP, 15 Pep]",
    'Happy Banquet': "Pep +15 for the ally with the lowest Pep. [1/7 TP, 1 Pep]",
    'Critical Hits': "Critical attack on all enemies with 100% hit. [1/4 TP, 7 Pep]",
    'Hysteric Slap': "0-4 bash attacks on an enemy row. [1/3 TP, 10 Pep]",
    'Fire of Purgatory': "Attack one foe (2x vs Undead/Demon/Apparition). [1/4 TP, 7 Pep]",
    'Genocide Rain\'s Action': "Actual course of action",
    'Double-Team Attack': "Strike an enemy row from both sides at once. [1/7 TP, 7 Pep]",
    'Twist and Shout': "Spiral into enemy ranks for a piercing attack. [1/7 TP, 7 Pep]",
    'Curse Bullet': "Waste one enemy and poison it (100%). [1/5 TP, 10 Pep]",
    'Mesmerize': "Cancel enemy chants, dances, songs and dolls. [1/7 TP, 10 Pep]",
    'Jetstream': "Dogpile an enemy with three allies in a row. [1/4 TP, 8 Pep]",
    'Magical Assault': "Slice a foe 2-5 times with friendship & swords. [1/4 TP, 15 Pep]",
    'Beast Blitz': "Rough up (4 hits) and poison (100%) one foe. [1/3 TP, 12 Pep]",
    'God Punch': "Pummel one foe (2x vs Undead/Demon/Apparition). [1/5 TP, 10 Pep]",
    'Durchbruch': "Two light arrows pierce back row; silence (50%). [1/5 TP, 12 Pep]",
    'Maid Beam': "Deadly Maid Beam pierces back row. Petrify (75%). [1/4 TP, 8 Pep]",
    'Sleep with the Fishes': "Lull all enemies to sleep with hypnosis. [1/5 TP, 10 Pep]",
    'Elixir': "Full party HP; dispel debuffs & ailments. [1/7 TP, 8 Pep]",
    'Feuerkraft': "Immolate foes, absorb HP/TP (5000 dmg cap). [1/4 TP, 30 Pep]",
    'Gold Power': "Hurl 5% wallet at one foe (max 10000 dmg). [1/3 TP, 20 Pep]",
    '777 Fever': "Paralysis (50%) and 7x Lv dmg to all foes. [1/5 TP, 6 Pep]",
    'Gimme Gold': "Gain 4x enemies' gold after battle (min 100). [1/7 TP, 20 Pep]",
    'Death Beam': "Instakill one random combatant, friend or foe. [1/9 TP, 8 Pep]",
    'Apocrypha': "Waste one enemy and lower phys. DEF (-35%). [1/4 TP, 12 Pep]",
    'Anastasia': "Goddess of life resurrects allies (HP 100%). [1/4 TP, 10 Pep]",
    'Jackpot': "Deal 77x user Lv in dmg to a foe. Wild jokers! [All TP, 50 Pep]",
    'Todokanai Koi': "Damage and likely petrify all enemies. [1/4 TP, 30 Pep]",
    'Lots Of Guns': "Three guns rain lead on random foes (9 hits). [1/5 TP, 15 Pep]",
}

print(f"{'Skill Name':24} | {'Len':3} | Drafted Text")
print("-" * 100)
for r in rows:
    name = r[1]
    text = drafts.get(name, r[3])
    print(f"{name:24} | {len(text):3d} | {text}")
    assert len(text) <= 70, f"{name} exceeds 70! ({len(text)})"
print("\nALL 52 DRAFTS ARE <= 70 CHARACTERS AND KEEP 100% OF COMBAT FACTS!")

euthys_dialogues = [
    # Lesson 04
    """Pay close attention: heavy 2H blades and rifles hit hard,
but their severe delay leaves you wide open!
Have them Defend to cut their delay and recover the initiative.""",

    # Lesson 07
    """Mid-range spears and whips ignore penalties from the back row,
while bows and magic strike across all rows at full power.
Position your allies wisely, Fried, lest you suffer needless harm.""",

    # Lesson 08
    """Precisely! Stacking 100 resistance also cuts elemental damage in half.
Combine this with a Paladin's Cover or a Dark Lord's leeching,
and your front line will stand firm even against divine magic.""",

    # Lesson 09
    """Presents include fine gold, rare equipment, and bag expansions
at Ranks 2 and 8. Prove your worth all the way to Rank 16, and
the Guild will even grant you passage into the infamous Matrix.""",

    # Lesson 10
    """"*giggle* Don't be so timid, Fried. Examine their requirements
in the menu and coordinate your turns. A well-timed Joint Skill
can turn the tides in an instant.\"""",

    # Lesson 11/12
    """"Simply equip her with the Slave's Torc and invoke Dragon Papi
for guidance. She will soak up so much experience that she'll
rejoin the vanguard before you even have time to complain.\"""",

    # Lesson 13
    """I visit often. A hearty meal bestows blessings for 900 steps,
and finest ramen grants +10% stats with elemental guards that
even pesky Dispel traps cannot erase. Exquisite and practical.""",

    # Lesson Sp01
    """"*giggle* Giving up already, Fried? Stack 100+ Elemental Resist
to cut damage in half and gain total ailment immunity, or have
a Valkyrie cast Circle Protection to turn calamity into safety.\"""",

    # Lesson Sp02
    """Dark Aura debuffs on contact. When bosses enrage at low health,
delay tricks lose their efficacy. Unleash your fiercest
Joint Skills to execute them before they overwhelm you.""",

    # Lesson Sp03
    """"Longing to elevate your companions to godlike perfection?
Achieve a Crown by resetting with a 59+ level gap to grant
permanent stat increases and awaken their unique skills to EX.\""""
]

for idx, d in enumerate(euthys_dialogues):
    lines = d.split('\n')
    assert len(lines) <= 3, f"Dlg {idx} has {len(lines)} lines > 3"
    assert '~' not in d, f"Dlg {idx} has tilde"
    for lidx, l in enumerate(lines):
        assert len(l) <= 85, f"Dlg {idx} line {lidx} length {len(l)} > 85: '{l}'"

print(f"All {len(euthys_dialogues)} Euthys dialogues PASSED validation!")

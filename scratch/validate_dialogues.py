dialogues = [
    # Lesson 04
    """Pay close attention: huge 2H blades and rifles hit hard, but\ntheir heavy delay means enemies will lap you in turns!\nHave them Defend to shave that delay and get back in action.""",

    # Lesson 07
    """Remember: mid-range spears and whips ignore penalties from back row,\nwhile bows and magic strike across all rows at 100% full power!\nPosition your allies carefully, Fried, or expect extra homework.""",

    # Lesson 08
    """Precisely! Stacking 100 resistance also cuts elemental damage by 50%.\nPair this with Paladin's 60% Cover or Dark Lord's HP leeching,\nand your front line will hold fast even against divine spells.""",

    # Lesson 09
    """Presents include fat bags of gold, rare gear, and bag expansions\nat Ranks 2 and 8! Prove yourself all the way to Rank 16, and\nthe Guild will even grant you entry to the infamous Matrix!""",

    # Lesson 10
    """"Don't be lazy, Fried! Check your menu to see who needs\nto line up and save your Pep. A proper Joint Skill will turn\nthe tides faster than any basic trick!\"""",

    # Lesson 11/12
    """"Just slap a Slave's Torc on her, summon Dragon Papi for extra\njuice, and she'll soak up so much EXP she'll catch right back\nup to the squad before you can even complain about grinding!\"""",

    # Lesson 13
    """I'm a regular! A hearty bowl keeps you buffed for 900 steps,\nand top ramen grants +10% stats with elemental guards that\neven pesky Dispel traps can't ruin. Delicious and practical!""",

    # Lesson Sp01
    """"Don't just lie down and die, Fried! Stack 100+ Elemental Resist\n(which cuts damage by 50% and grants 100% ailment immunity!),\nor order a Valkyrie to pop Circle Protection on wipe turns!\"""",

    # Lesson Sp02
    """Dark Aura debuffs on contact. When bosses get mad at <25% HP,\ncheap delay tricks stop working on them, so blast them with\nyour heaviest Joint Skills before they turn you into paste!""",

    # Lesson Sp03
    """"Want to turn your favorite girl into a walking calamity?\nEarn a Crown by resetting with a 59+ level gap to permanently\nboost all her stats and supercharge her unique skill to EX!\"""",

    # ShopStore 01
    """Al-so car-ry Flash-lights! They il-lu-mi-nate pitch-black halls\nfor 30 steps to re-veal hid-den traps and paths\nwith-out fum-bling in the dark!""",

    # ShopStore 11
    """For bud-get ex-pe-di-tions, try Mag-i-cal Fruit (50 TP for 100 G)\nor Fair-y Ap-ples (100 TP for 300 G) to sus-tain your loop\nwith-out run-ning out of re-sour-ces in deep dun-geons!""",

    # ShopQuest 08
    """(Quests below your rank still yield bounties, but no Trust Points.\nTake on current assignments: Ranks 2 and 8 award larger adventurer bags,\nand reaching Rank 16 earns you clearance for The Matrix!)""",

    # ShopQuest 10
    """(Monster hunts earn Trust Points to advance your Guild standing,\nwhile item delivery requests reward you with fine weapons\nand generous pouches of gold.)""",

    # ShopBlacksmith 00
    """(I can hammer an item up to +9 to sharpen its bite and harden\nits guard... but 5 enchant slots is the limit. Overload it,\nand the whole thing shatters... So choose your seals carefully...)""",

    # ShopBlacksmith 10
    """(Turn 'em to stone, let 'em blow up, or let 'em run, and you won't\nget any Sealbook from 'em... Put 'em to Sleep or shock 'em\nwith Paralysis if you want a clean seal...)""",

    # ShopBlacksmith 11
    """(Don't bring Grand Sealbooks to my anvil... Those are for\nparty auras and battlefield summons. Try hammering one into\narmor, and you'll blow my workshop sky-high...)""",

    # ShopBar 04
    """Mercs have their own habits in a brawl: Paladins always rush to\nCover and Provoke, Priests save their heals for critical injuries,\nwhile Dark Lords just unleash pure carnage. Pick the right backup!"""
]

for idx, d in enumerate(dialogues):
    lines = d.split('\n')
    assert len(lines) <= 3, f"Dlg {idx} has {len(lines)} lines > 3"
    assert '~' not in d, f"Dlg {idx} has tilde"
    for lidx, l in enumerate(lines):
        assert len(l) <= 85, f"Dlg {idx} line {lidx} length {len(l)} > 85: '{l}'"

print(f"All {len(dialogues)} revised dialogues PASSED validation!")

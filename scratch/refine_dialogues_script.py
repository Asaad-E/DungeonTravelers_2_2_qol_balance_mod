import os
import sys

script_path = r'mod_project/scratch/update_euthys_and_teaching.py'

with open(script_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Exact replacements
replaces = [
    # Lesson 09
    (
        "\"Presents include fine gold, rare equipment, and bag expansions\\n'\n"
        "            'at Ranks 2 and 8. Prove your worth all the way to Rank 16, and\\n'\n"
        "            'the Guild will even grant you passage into the infamous Matrix.\"",
        "\"Presents include fine gold, rare equipment, and bag expansions.\\n'\n"
        "            'Climb through the ranks to expand your inventory, ensuring you\\n'\n"
        "            'carry ample supplies to conquer the deepest labyrinths.\""
    ),
    # Lesson 11-12
    (
        "\"Simply equip her with the Slave's Torc and invoke Dragon Papi\\n'\n"
        "            'for guidance. She will soak up so much experience that she'll\\n'\n"
        "            'rejoin the vanguard before you even have time to complain.\"",
        "\"Simply equip her with the Slave's Torc to double her gains.\\n'\n"
        "            'She will soak up so much experience from stronger monsters that\\n'\n"
        "            'she'll rejoin the vanguard before you even have time to complain.\""
    ),
    # Lesson 13
    (
        "\"I visit often. A hearty meal bestows blessings for 900 steps,\\n'\n"
        "            'and finest ramen grants +10% stats with elemental guards that\\n'\n"
        "            'even pesky Dispel traps cannot erase. Exquisite and practical.\"",
        "\"I visit often. A hearty meal bestows blessings for explorations,\\n'\n"
        "            'and the finest dishes grant buffs and elemental guards that\\n'\n"
        "            'even pesky Dispel traps cannot erase. Exquisite and practical.\""
    ),
    # Lesson Sp01
    (
        "\"Abandon hope and make peace with your fate... *giggle*\\n'\n"
        "            'Stack 100 Elemental Resist to cut that damage in half, Fried,\\n'\n"
        "            'or have a Valkyrie pop Circle Protection on lethal turns.\"",
        "\"Abandon hope and make peace with your fate... *giggle*\\n'\n"
        "            'Stack 100 Elemental Resist to cut that damage in half, Fried,\\n'\n"
        "            'or have an Enchantress pop Circle Protect on lethal turns.\""
    ),
    # Lesson Sp03
    (
        "\"Longing to elevate your companions to godlike perfection?\\n'\n"
        "            'Achieve a Crown by resetting with a 59+ level gap to grant\\n'\n"
        "            'permanent stat increases and awaken their unique skills to EX.\"",
        "\"Longing to elevate your companions to godlike perfection?\\n'\n"
        "            'Resetting with a 59+ level gap grants permanent stat boosts,\\n'\n"
        "            'awakening their potential toward the legendary Crown EX.\""
    ),
    # Teaching 01
    (
        "'Turn delay falls into three tiers: Agile (A+ 1.0x to A 1.15x),\\n'\n"
        "            'Balanced (B to C+ 1.30-1.75x), and Colossal (D to F 1.85-2.35x).\\n'\n"
        "            'Use Defend (0.67x delay) to quickly recover your turn order!'",
        "'Weapon delay spans 12 ranks: A+ (1.0x) to F (2.9x delay).\\n'\n"
        "            'Choosing Defend advances your turn gauge to recover sooner,\\n'\n"
        "            'allowing heavy weapon wielders to maintain tactical tempo!'"
    ),
    # Teaching 09
    (
        "'Weapon speed ranks range from A, which is the fastest, to F,\\nwhich is the slowest.'",
        "'The higher her AGI stat, the faster she will be.\\nWeapon speed ranks range from A, which is the fastest, to F,\\nwhich is the slowest.'"
    ),
    (
        "'Delay ranks: A+ (1.00x), A (1.15x), B+ (1.30x), B (1.45x),\\n'\n"
        "            'C+ (1.60x), C (1.75x), D (1.95x), E (2.15x), and F (2.35x delay).\\n'\n"
        "            'Choosing Defend cuts recovery delay down to 0.67x.'",
        "'Higher AGI speeds up turns, while weapons add recovery delay.\\n'\n"
        "            'Weapon ranks span from A+ (1.00x) up to F (2.90x delay).\\n'\n"
        "            'Choosing Defend advances your turn gauge to recover sooner.'"
    ),
    # Teaching 11
    (
        "'Short-range suffers -50% damage beyond Front-to-Front combat.\\n'\n"
        "            'Mid-range (Spears/Whips) hits adjacent rows with 0% penalty.\\n'\n"
        "            'Long-range (Bows/Guns/Magic) hits any row at 100% full power.'",
        "'Short-range attacks suffer damage penalties across distant rows.\\n'\n"
        "            'Mid-range spears hit adjacent rows cleanly, while long-range\\n'\n"
        "            'bows and magic strike any enemy row at 100% full power.'"
    ),
    # Teaching 12
    (
        "'Physical damage received while asleep is multiplied by 1.5x.\\n'\n"
        "            'A sleeping unit wakes up immediately upon taking physical damage.'",
        "'Sleeping targets cannot evade attacks and suffer 1.5x damage\\n'\n"
        "            'from all strikes. However, taking any damage wakes them up,\\n'\n"
        "            'so time your heaviest burst attacks accordingly!'"
    ),
    # Teaching 14
    (
        "'Increasing Quest Rank expands your bag capacity at Rank 2 (+10)\\n'\n"
        "            'and Rank 8 (+10, reaching the maximum cap of 50 item slots).\\n'\n"
        "            'Rank 16 also grants passage to the secret Matrix.'",
        "'Increasing Quest Rank expands your item bag capacity\\n'\n"
        "            'at key milestones, granting additional storage space\\n'\n"
        "            'to sustain deeper dungeon expeditions and rare loot.'"
    ),
    # Teaching 19
    (
        "'Use Dragon Papi summons and the Slave\'s Torc accessory to\\n'\n"
        "            'greatly amplify experience gains and rapidly catch up allies\\n'\n"
        "            'who recently underwent a level reset.'",
        "'Equip training accessories like Slave\'s Torc to double\\n'\n"
        "            'experience gains, rapidly catching up allies who underwent resets.\\n'\n"
        "            'Facing higher-level monsters also grants native bonus EXP.'"
    ),
    # Teaching 22
    (
        "'Many underutilized skills have enhanced scaling and reduced TP\\n'\n"
        "            'costs. Carefully review the updated skill descriptions to build\\n'\n"
        "            'synergistic rotations across all specialized class paths.'",
        "'Experiment with unique synergies across advanced classes.\\n'\n"
        "            'Pair defensive stances with chant protection, and manage\\n'\n"
        "            'weapon delay tiers to master late-game tactical encounters.'"
    ),
    # Teaching 23
    (
        "'Powerful bosses enter an enrage state when reduced to low HP.\\n'\n"
        "            'Their speed and attack power surge, so save your burst damage\\n'\n"
        "            'and Joint Skills to finish them before they overwhelm you.'",
        "'Beware: certain formidable foes unleash deadly new skill\\n'\n"
        "            'rotations after taking substantial damage. Save burst damage\\n'\n"
        "            'and Joint Skills to finish them before they overwhelm you.'"
    ),
]

for idx, (old, new) in enumerate(replaces):
    assert old in content, f'Missing replace {idx}: {old[:30]}'
    content = content.replace(old, new, 1)

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('All 14 replacements applied cleanly to update_euthys_and_teaching.py!')

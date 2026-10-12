"""Writes data_tables/balance_skill_text.xlsx: the skill boxes worded by hand in the QoL variant whose figures the
Balance variant changes, worded again with the figures of the variant, in the shape the QoL box has.

Each figure is in the built packs: the build checks every one of them (tools/text_checks.py), the doll skills against
the action skill the doll performs.

    python make_balance_skill_text.py
"""
import os
import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT = os.path.join(PROJECT, 'data_tables', 'balance_skill_text.xlsx')
T, M = 'TechniqueSkillData_%04d.bin', 'MagicSkillData_%04d.bin'
SCROLL = ' | Damage cap: 250 -> 500 | TP Cost: 20 (+2-3/Lv) -> 30'
ROWS = [
    ('Technique', T % 95, 'Spartan', None,
     'ATK: 288% -> 294 -> 300 -> 308 -> 316 -> 324 -> 332 -> 340 -> 350 -> 360% (L10)\n'
     'Turns: 3 (Lv1-2) -> 4 (Lv3-5) -> 5 (Lv6-8) -> 6 (Lv9-10)    |    TP Cost: 20 -> 36',
     "Rows D001 - D040, S041, S042: power of Spartan's Action, life, TP cost of levels 9 and 10"),
    ('Technique', T % 96, 'Oracles', None,
     'ATK: 252% (+4-10%/Lv) -> 314%   |   Paralysis: 30% (+3-5%/Lv) -> 64% (L10)\n'
     'Turns: 5 (Lv1-4) -> 6 (Lv5-8) -> 7 (Lv9-10)  |  TP Cost: 24 -> 48  |  Speed: 1.1x',
     "Rows D041 - D080: power of Oracles' Action, life, speed"),
    ('Technique', T % 97, 'Catalina', None,
     'Heal Power: 6 -> 8 -> 10 -> 13 -> 16 (L1-5 Max)\n'
     'Turns: 5 (Lv1-2) -> 6 (Lv3-4) -> 7 (L5 Max)   |   TP Cost: 30 -> 48   |   Speed: 1.1x',
     "Rows D081 - D095 and the heal power of Catalina's Action"),
    ('Technique', T % 98, 'Mercidarian', None,
     'ATK: 150% -> 156 -> 162 -> 168 -> 177 -> 184 -> 192 -> 199 -> 207 -> 215% (L10)\n'
     'Turns: 4 (Lv1-4) -> 5 (Lv5-7) -> 6 (Lv8-10)  |  TP Cost: 42 -> 70  |  Speed: 0.95x',
     "Rows D096 - D135: power of Mercidarian's Action, life, speed"),
    ('Technique', T % 100, 'Musiy', None,
     'Pwr: 270 -> 360 -> 465 -> 585 -> 720 -> 878 -> 1050 (L7 Max)\n'
     'Turns: 6    |    TP Cost: 38 (+4-6/Lv) -> 68    |    Speed: 1.02x -> 1.12x',
     "Rows D160 - D243: power of Musiy's Actions, life, speed"),
    ('Magic', M % 219, 'Fire Scroll', None,
     'Max HP damage: 6% -> 7% -> 9% -> 10% -> 12% (L1-5 Max)   |   Accuracy: 64% (+4%/Lv)\n'
     'ATK: -6% -> -12% (3 Turns)' + SCROLL, 'Rows C068, A139, X001'),
    ('Magic', M % 222, 'Wind Scroll', None,
     'Max HP damage: 6% -> 7% -> 9% -> 10% -> 12% (L1-5 Max)   |   Accuracy: 64% (+4%/Lv)\n'
     'Evasion: -10% -> -23% (3 Turns)' + SCROLL, 'Rows C165, A149, X011'),
    ('Magic', M % 223, 'Earth Scroll', None,
     'Max HP damage: 6% -> 7% -> 9% -> 10% -> 12% (L1-5 Max)   |   Accuracy: 64% (+4%/Lv)\n'
     'DEF: -6% -> -12% (3 Turns)' + SCROLL, 'Rows C064, A154, X016'),
    ('Magic', M % 231, 'Carrot and Stick', None,
     'DEF: -7% -> -9% -> -10% -> -12% -> -15% (L1-5 Max)   |   Magic defense: -15% -> -23%\n'
     'Accuracy: 80% -> 90% | HP recovery: 35 -> 25 | Turns: 3 | TP: 18 (+2-4/Lv) -> 32', 'Rows M081, A159'),
    # what a row adds that the box did not say (decided 2026-10-11): the cure of Heal and Circle Heal, the gun
    ('Magic', M % 187, 'Heal', "Heal an ally's HP and cure poison.",
     'Heals RES: 4x (+1x/Lv) -> 13x (L10 Max)   |   Heal Cap: 100 (+60-80/Lv) -> 800\n'
     'Cures: Poison -> + Paralysis (Lv6+) | TP Cost: 2 (+1-3/Lv) -> 19 | Speed: 1.75x',
     'Row H036: effect 106 added, value 1 at levels 1 - 5 and 2 at 6 - 10: the first entries of the cure list, '
     'poison then paralysis (FORMULAS 16.7, cures). TP: the C rows'),
    ('Magic', M % 188, 'Circle Heal', "Heal the party's HP and cure poison.",
     'Heals RES: 5x -> 5.25 -> 5.5 -> 5.75 -> 6 -> 6.25 -> 6.5 -> 6.75 -> 7 -> 7x (L10)\n'
     'Heal Cap: 200 (+40-60/Lv) -> 600   |   TP Cost: 11 (+3-5/Lv) -> 48   |   Speed: 1.35x',
     'Row H037: effect 106 added, value 1 at every level: poison. The second box is the generated one'),
    ('Technique', T % 43, 'Spiral Arrow', 'Bow/gun skill. Tremendous single shot at an enemy for stab damage.',
     None, 'Row W036: weapon codes 8 and 15, worded as Chain Spike is'),
    ('Technique', T % 50, 'Divine Cannon', 'Bow/gun skill. Severe stab damage to an enemy, piercing the back row.',
     None, 'Row W037: weapon codes 8 and 15, worded as Chain Spike is'),
    ('Technique', T % 38, 'Sleep Sting', 'Short-range/projectile. Severe damage to an enemy. Sleep (20-50%).',
     None, 'Row S037: weapon codes 0 and 10'),
    ('Technique', T % 39, 'Silence Sting', 'Short-range/projectile. Severe damage to an enemy. Silence (20-50%).',
     None, 'Row S038: weapon codes 0 and 10'),
    ('Technique', T % 40, 'Stun Sting', 'Short-range/projectile. Severe damage to an enemy. Stun (20-50%).',
     None, 'Row S039: weapon codes 0 and 10'),
    ('Technique', T % 51, 'Phoenix', 'Short-range/projectile. Minor damage and lower speed, enemy row.',
     None, 'Row S040: weapon codes 0 and 10'),
    # boxes where the generated text of the variant lost a table the QoL box showed (found by the build)
    ('Technique', T % 15, 'Soul Drain', None,
     'ATK: 125% -> 130 -> 135 -> 140 -> 144 -> 148 -> 151 -> 154 -> 157 -> 160% (L10)\n'
     'TP Absorb: 10% (+1-2%/Lv) -> 20%   |   TP Cost: 6 -> 18   |   Speed: 0.9x', 'Rows C152, X046: Speed had no room'),
    ('Magic', M % 164, 'Soul Absorb', None,
     'Pwr: 55 (+10-20/Lv) -> 205   |   Accuracy: 80% -> 90%   |   TP Absorb: 100%\n'
     'TP Cost: 6 (+1/Lv) -> 15   |   Speed: 1.75x   |   Chant: 1.25x -> 1.07x', 'Row X026: Speed and Chant had no room'),
    ('Magic', M % 200, 'Illusion', 'Create magical afterimages that each let you dodge an attack.',
     'Number of dodges: 3 -> 4 -> 5 (L1-3 Max)   |   Turns: 3 -> 4 -> 5\n'
     'TP Cost: 30 -> 38 -> 46   |   Speed: 0.85x   |   Chant: 0.75x -> 0.65x',
     'Row X071: the sentence of the game says 2 afterimages; the variant gives 3, 4 and 5'),
    ('Magic', M % 216, 'Shadow Clone', None,
     'Number of dodges: 1 -> 2 -> 3 -> 4 -> 5 (L1-5 Max)   |   Chant: 0.75x\n'
     'Turns: 3 -> 3 -> 4 -> 4 -> 5   |   TP Cost: 17 -> 20 -> 24 -> 28 -> 33   |   Speed: 0.85x',
     'Rows K001: the generated box fell back to "Number of dodges UP"'),
]


def main():
    wb = openpyxl.Workbook()
    about = wb.active
    about.title = 'About'
    for line in (('Topic', 'Detail'),
                 ('What', 'Skill boxes of the Balance variant worded by hand. The texts of the variant are generated from '
                          'its values (tools/build_variant.py balance, step 0c); a box worded by hand in '
                          'qol_skill_text.xlsx keeps its wording, so where the variant changes one of its figures the box '
                          'is worded again here, in the same shape.'),
                 ('Columns', 'Balance_Desc and Balance_LvUp take the place of the text generated for the variant; an empty '
                             'cell keeps the generated text.'),
                 ('Checked', 'Every figure against the built packs by the build (tools/text_checks.py); a doll skill '
                             'against the action skill its doll performs.')):
        about.append(line)
    ws = wb.create_sheet('Skills')
    ws.append(('Category', 'Filename', 'Skill_Name', 'Balance_Desc', 'Balance_LvUp', 'Note'))
    for row in ROWS:
        ws.append(row)
    wb.save(OUTPUT)
    print(len(ROWS), 'boxes written to', OUTPUT)


if __name__ == '__main__':
    main()

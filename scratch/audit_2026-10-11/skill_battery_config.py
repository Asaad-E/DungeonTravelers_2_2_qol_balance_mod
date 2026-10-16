"""Section skill_battery of data_tables/measure_config.json: the battery of every skill with and without (dtcli skill-battery, 2026-10-16)."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'measure_config.json')

SECTION = {
    'about': 'dtcli skill-battery: every active and passive skill of a class, with and without, in each party of BatteryParties at every '
             'story boss of each stage and on rows of random battles; thresholds as skill_value_contested (wins, length, hp).',
    'categories': ['Technique', 'Magic', 'Passive'],
    'story_prefix': 'C',
    'stages': [
        {'name': 'base', 'low': 1, 'high': 14, 'columns': ['Base class']},
        {'name': 'intermediate', 'low': 15, 'high': 29, 'columns': ['Base class', 'Lv15 class']},
        {'name': 'advanced', 'low': 30, 'high': 99, 'columns': ['Base class', 'Lv15 class', 'Lv30 class']},
    ],
    'chain': 4,
    'chain_seed': 1601,
    'scan_runs': 20,
    'confirm_runs': 200,
    'confirm_cells': 3,
    'batch': 5000,
    'wins': 0.08,
    'length': 0.03,
    'hp': 0.03,
    'good_share': 0.25,
    # docs/FORMULAS.md: 267 / 268 preemptive attacks (before the battle), 269 escape and traps, 270 drops, 271 gold, 282 prices; docs/generated/SIM_AUDIT.md: 306 Present for Me outside battle
    'out_of_fight_effects': [267, 268, 269, 270, 271, 282, 306],
    # the first weapon of each type in EquipmentData (type -> name), for a skill whose role carries no weapon it allows
    'weapon_of_type': {'0': 'Shortsword', '1': 'Dagger', '2': 'Hand Axe', '3': 'Lance', '4': 'Mace', '5': 'Staff', '6': 'Tome',
                       '7': 'Short Bow', '8': 'Tantou', '9': 'Darts', '10': 'Whip', '11': 'Ougi', '12': 'Megaphone', '13': 'Charumera'},
}

with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
config['skill_battery'] = SECTION
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written')

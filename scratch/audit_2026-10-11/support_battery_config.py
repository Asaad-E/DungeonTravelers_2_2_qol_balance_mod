"""Section support_battery of data_tables/measure_config.json: each support and tank class in every battery party (dtcli support-battery, 2026-10-16)."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'measure_config.json')

SECTION = {
    'about': 'dtcli support-battery: each support and tank class of a stage (sheet ClassKinds) in the last place of each BatteryParties party against '
             'the control role there, at every story boss of the stage, on a walk of random battles and on the walk followed by the boss.',
    'kinds': ['support', 'tank'],
    'control': 'attacker',
    'story_prefix': 'C',
    'stages': [
        {'name': 'base', 'low': 1, 'high': 14, 'column': 'Base class'},
        {'name': 'intermediate', 'low': 15, 'high': 29, 'column': 'Lv15 class'},
        {'name': 'advanced', 'low': 30, 'high': 99, 'column': 'Lv30 class'},
    ],
    'contexts': ['boss', 'walk', 'walk_boss'],
    'walk': 10,
    'chain_seed': 1602,
    'runs': 40,
    'batch': 300,
    'wins': 0.08,
    'hp': 0.05,
    'deaths': 0.3,
    'items': 0.5,
    'good_share': 0.25,
}

with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
config['support_battery'] = SECTION
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written')

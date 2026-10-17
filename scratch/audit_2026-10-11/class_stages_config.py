"""Section class_stages_report of data_tables/measure_config.json (2026-10-16): class-stages on the method of the mass tests, each role in the
reference party of the checkpoint and in every party of BatteryParties, more fights than one party alone gave (the Witch at C40 read 65%
or 55% from 40 fights of one party)."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'measure_config.json')

SECTION = {
    'about': 'dtcli class-stages: each role at every checkpoint of its stage, in the reference party of the checkpoint (in its last place) and in '
             'every party of the sheet BatteryParties (in the place of the same role, else of the last member); the same seeds for every role; '
             'wins, length against the median attacker of the same party and share of damage, averaged over the parties.',
    'reference_party': True,
    'battery_parties': True,
    'runs': 40,
}

with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
SECTION['hard_below'] = config['class_stages_report']['hard_below']
config['class_stages_report'] = SECTION
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written')

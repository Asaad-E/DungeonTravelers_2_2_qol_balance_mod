"""Section random_battles of data_tables/measure_config.json (2026-10-16): rows of 10 random battles (as the walks of the mass tests), 40
rows a floor (Settings check_runs, as the difficulty curve), the zones of the floor at most 12 levels over the party."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'measure_config.json')
with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
config['random_battles'] = {'chain': 10, 'ahead': 12, 'runs': None}
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written')

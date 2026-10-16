"""Section class_search of data_tables/measure_config.json: every party of the classes of a stage (dtcli class-search, 2026-10-16).
Method and thresholds of the search for abusive combinations of 2026-10-16 (measures/ABUSE_SEARCH_CLASSES.md)."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'measure_config.json')

SECTION = {
    'about': 'dtcli class-search [stage] [scan runs] [confirm runs] [checkpoints]: every party of the classes of a stage, vanilla and variant, at '
             'every story boss of the stage and on random rows of its floors; candidates confirmed at more runs. On demand, not in the suite.',
    'stages': [
        {'name': 'final', 'low': 30, 'high': 99, 'column': 'Lv30 class'},
        {'name': 'intermediate', 'low': 15, 'high': 29, 'column': 'Lv15 class'},
        {'name': 'base', 'low': 1, 'high': 14, 'column': 'Base class'},
    ],
    'story_prefix': 'C',
    'party_size': 5,
    'contexts': ['boss', 'random'],
    'chain': 8,
    'chain_seed': 1603,
    'seed': 40000,
    'confirm_seed': 50000,
    'scan_runs': 20,
    'confirm_runs': 200,
    'confirm_max': 60,
    'batch': 20000,
    'win': 0.95,
    'time': 0.60,
    'vanilla_win': 0.80,
    'vanilla_length': 1.5,
    'drop': 0.10,
    'fast_share': 0.05,   # the fastest share of the parties of a target, for the class table
}

with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
config['class_search'] = SECTION
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written')

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
    # the band of the classes in the report (section Balance of the classes): a class may be better or worse than another; it is out
    # of the band only as an outlier, more than z standard deviations from the mean of the classes in wins or in speed (2026-10-16)
    'band': {'z': 2.0},
    # named searches: dtcli class-search preset=NAME [more arguments, which win]
    'presets': {
        'balance': {'about': 'the checklist of the suite (dtcli suite, class-balance): every boss of the final classes, a sample, no confirmation',
                    'stage': 'final', 'context': 'boss', 'sample': '400', 'scan': '10', 'confirm': '0', 'out': 'balance',
                    'report': 'docs/generated/CLASS_BALANCE.md'},
        'dolls': {'about': 'parties of two Soul Summoners or more at the bosses where the doll line was fastest',
                  'stage': 'final', 'cids': 'C34,C38', 'context': 'boss', 'with': 'Soul Summoner*2'},
        'dark_lord': {'about': 'parties with a Dark Lord, the class Power Charge serves', 'stage': 'final', 'cids': 'C34,C38',
                      'context': 'boss', 'with': 'Dark Lord'},
        'no_maid_line': {'about': 'parties without a Maid-line member at the long bosses (the TP of a healer runs out)',
                         'stage': 'final', 'cids': 'C30,C34,C38,C40', 'context': 'boss', 'without': 'Diva+Mistress+Etoile'},
        'quick': {'about': 'a look at every boss and floor of the final classes: 1,000 parties a target, fewer runs',
                  'stage': 'final', 'sample': '1000', 'scan': '10', 'confirm': '100'},
    },
}

with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
config['class_search'] = SECTION
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written')

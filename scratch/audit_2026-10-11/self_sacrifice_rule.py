"""measure_config.json, skill_value rules: effect 130 (Pass All TP, Self-Sacrifice) moves from the heal rule to the TP rule (2026-10-16).
docs/FORMULAS.md: 128 HP recovery, 129 TP recovery, 130 Pass All TP; the policy's tp action now passes TP with it."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'measure_config.json')
with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
rules = config['skill_value']['rules']
heal = next(r for r in rules if r['action'].startswith('heal'))
tp = next(r for r in rules if r['action'].startswith('tp'))
if 130 in heal['effects']:
    heal['effects'].remove(130)
if 130 not in tp['effects']:
    tp['effects'].append(130)
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('heal', heal['effects'], 'tp', tp['effects'])

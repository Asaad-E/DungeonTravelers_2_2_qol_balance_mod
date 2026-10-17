"""Section skill_value of data_tables/measure_config.json, rules: the three guards of the Sage (Stab, Slash and Bash Guard, effects 184,
185 and 186) are cast where the foes strike with that kind of blow (condition foes_attack, 2026-10-16). Cast always they were dead in the
skill battery: a guard against one kind of blow serves only against the foes that use it, which a player reads off the fight."""
import json
import os

PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data_tables', 'measure_config.json')
GUARDS = [(184, 2), (185, 1), (186, 3)]          # effect, attribute (2 stab, 1 slash, 3 bash)

with open(PATH, encoding='utf-8') as f:
    config = json.load(f)
rules = [r for r in config['skill_value']['rules'] if r['effects'] not in [[e] for e, _ in GUARDS]]
config['skill_value']['rules'] = [{'effects': [e], 'condition': 'foes_attack:%d' % a, 'action': 'status:%d' % e} for e, a in GUARDS] + rules
with open(PATH, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=1, ensure_ascii=False)
    f.write('\n')
print('written', len(config['skill_value']['rules']), 'rules')

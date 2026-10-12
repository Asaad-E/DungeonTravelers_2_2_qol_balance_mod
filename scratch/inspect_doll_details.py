import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from doll_data import dolls

for d in dolls():
    print("=" * 40)
    print(f"Doll: {d['name']} (Skill ID: {d['skill']})")
    print(f"Turns: {d['turns']}")
    print(f"TP Cost: {d['tp_cost']}")
    print(f"Speed: {d['speed']}")
    print(f"Range: {d['range']}")
    for a in d['actions']:
        print(f"  Action: {a['name']} (Action ID: {a['skill']})")
        print(f"  Target: {a['target']}, Attr: {a['attribute']}, Speed: {a['speed']}")
        for eff_id, eff_name, vals in a['effects']:
            print(f"    Effect {eff_id} ({eff_name}): {vals}")

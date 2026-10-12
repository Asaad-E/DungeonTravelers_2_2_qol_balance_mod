import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
import enemy_data, enemy_ai

all_e = {e['name']: e for e in enemy_data.enemies()}
target_bosses = ["Melek Taus", "Hell's Angel", "Samael", "Last Judgment", "Azathoth"]
for name in target_bosses:
    e = all_e.get(name)
    if e and e.get('ai'):
        print(f"\n==================== {name} (Enemy {e['id']}) ====================")
        try:
            parsed = enemy_ai.decode(e['ai'])
            print(f"Opening commands: {len(parsed['opening'])}")
            for cmd in parsed['opening']:
                print(f"  Opening: {enemy_ai.describe(cmd)}")
            print(f"Sets: {list(parsed['sets'].keys())}")
            for sid, sdata in parsed['sets'].items():
                print(f"  Set {sid}: weights={sdata['weights'][:8]}... commands={len(sdata['commands'])}")
                for cmd in sdata['commands']:
                    print(f"    CMD: {enemy_ai.describe(cmd)}")
        except Exception as ex:
            print("  Error decoding AI:", ex)

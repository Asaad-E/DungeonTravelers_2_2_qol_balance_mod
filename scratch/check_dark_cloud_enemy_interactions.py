import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from enemy_data import enemies, IMMUNITY_BITS

ITEM_ID = 458

print(f"=== SEARCHING ENEMY DROPS, STEALS, SNACKS FOR ITEM {ITEM_ID} (Dark Cloud) ===")

all_e = enemies()
found_drop = []
found_steal = []
found_snack = []
found_raw = []

for e in all_e:
    # Check drops
    for item_id, chance in e.get('drops', []):
        if item_id == ITEM_ID:
            found_drop.append((e, chance))
    # Check steal
    st = e.get('steal')
    if st and st[0] == ITEM_ID:
        found_steal.append((e, st[1]))
    # Check snack
    if e.get('snack_item') == ITEM_ID:
        found_snack.append(e)
    # Check all raw_68 ints for ITEM_ID
    for idx, val in enumerate(e.get('raw_68', [])):
        if val == ITEM_ID:
            found_raw.append((e, idx))

print(f"Drops found: {len(found_drop)}")
for e, chance in found_drop:
    print(f"  Enemy {e['id']} ({e['name']}, Lv {e['level']}): chance={chance}%")

print(f"Steals found: {len(found_steal)}")
for e, chance in found_steal:
    print(f"  Enemy {e['id']} ({e['name']}, Lv {e['level']}): chance={chance}%")

print(f"Snacks found: {len(found_snack)}")
for e in found_snack:
    print(f"  Enemy {e['id']} ({e['name']}, Lv {e['level']})")

print(f"Raw 68 occurrences: {len(found_raw)}")
for e, idx in found_raw:
    print(f"  Enemy {e['id']} ({e['name']}) raw_68[{idx}] = {ITEM_ID}")

print("\n=== PETRIFICATION IMMUNITY IN BOSSES AND ENEMIES ===")
petrify_immune = [e for e in all_e if 'petrification' in e.get('immune', [])]
not_immune = [e for e in all_e if 'petrification' not in e.get('immune', [])]
print(f"Total enemies: {len(all_e)}")
print(f"Immune to Petrification: {len(petrify_immune)}")
print(f"NOT immune to Petrification: {len(not_immune)}")

print("\n--- Are ANY bosses (or high HP enemies) vulnerable to Petrification? ---")
bosses_vuln = [e for e in not_immune if e.get('hp', 0) > 8000 or e.get('level', 0) >= 40]
print(f"High HP / high level enemies vulnerable to petrify: {len(bosses_vuln)}")
for e in bosses_vuln:
    print(f"  ID {e['id']:3d}: {e['name']} (Lv {e['level']}, HP {e['hp']}, RES {e['res']})")

print("\n--- Bosses (HP > 8000): how many are IMMUNE? ---")
bosses_all = [e for e in all_e if e.get('hp', 0) > 8000]
print(f"Total bosses (HP > 8000): {len(bosses_all)}")
bosses_immune = [e for e in bosses_all if 'petrification' in e.get('immune', [])]
print(f"Bosses IMMUNE to Petrification: {len(bosses_immune)} / {len(bosses_all)}")

import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from enemy_data import enemies

all_e = enemies()
print(f"Total enemies: {len(all_e)}")
sample = all_e[0]
print("Keys in enemy record:", list(sample.keys()))

# Check drop and steal fields
drops = []
for e in all_e:
    # check keys related to drop or steal
    d_info = {k: v for k, v in e.items() if 'drop' in k.lower() or 'steal' in k.lower() or 'item' in k.lower()}
    if d_info:
        drops.append((e.get('id'), e.get('name'), d_info))

print(f"Enemies with drop/steal info: {len(drops)}")
for eid, ename, dinfo in drops[:5]:
    print(f"Enemy {eid:3d} ({ename}): {dinfo}")

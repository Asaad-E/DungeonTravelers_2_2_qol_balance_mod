import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from enemy_data import enemies

all_e = enemies()
rare_drops = []
for e in all_e:
    eq = e.get('equipment_drop')
    if eq and eq[1] in [1, 2] and e.get('level', 0) >= 50:
        rare_drops.append((e['id'], e['name'], e['level'], eq[0], eq[1]))

print(f"Postgame/high-level enemies (Lv>=50) with 1% or 2% equipment drop: {len(rare_drops)}")
for eid, ename, lvl, item_id, rate in rare_drops[:20]:
    print(f"Enemy {eid:3d} ({ename:20s}, Lv{lvl:2d}): Item {item_id:3d}, Drop rate {rate}%")

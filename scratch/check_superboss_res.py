import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from enemy_data import enemies

all_e = enemies()
superbosses = [331, 751, 862, 921, 951, 955, 1006] # Overdue, Azathoth, Last Judgment, Hell's Angel, Samael, Melek Taus, etc.
# Also find all enemies with level >= 80
high_lvl = [e for e in all_e if e.get('level', 0) >= 80 and not e.get('name', '').startswith('Generic')]

print(f"High level bosses (Lv >= 80): {len(high_lvl)}")
for e in high_lvl[:15]:
    res_elem = {k: e['res_' + k] for k in ['fire', 'water', 'wind', 'earth', 'lightning']}
    res_phys = {k: e['res_' + k] for k in ['slash', 'stab', 'bash']}
    print(f"Enemy {e['id']:3d} ({e['name']:20s}, Lv{e['level']:2d}): Phys={res_phys} | Elem={res_elem}")

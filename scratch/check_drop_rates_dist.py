import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from enemy_data import enemies
from collections import Counter

all_e = enemies()
eq_rates = Counter()
steal_rates = Counter()
for e in all_e:
    eq = e.get('equipment_drop')
    if eq and eq[0] != 0:
        eq_rates[eq[1]] += 1
    st = e.get('steal')
    if st and st[0] != 0:
        steal_rates[st[1]] += 1

print("Equipment drop rates:", sorted(eq_rates.items()))
print("Steal rates:", sorted(steal_rates.items()))

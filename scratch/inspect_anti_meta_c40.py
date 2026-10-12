import sys
sys.path.insert(0, 'mod_project')
from sim import setup as setup_mod
from sim.data import game_data
from sim.variant import balance_data
from tools.parallel_party_battery import PARTIES, build_party_complete

data = game_data()
setup = setup_mod.load()
variant = balance_data(data)

p_info = PARTIES['Anti-Meta']
party = build_party_complete(variant, setup, p_info['roles'], 'C40')

print(f"Anti-Meta Party at C40 (Size: {len(party)}):")
for u in party:
    role = getattr(u, 'role', 'summon')
    cls = getattr(u, 'class_id', 'N/A')
    cls_name = data.class_names.get(cls, 'Summon') if isinstance(cls, int) else 'Summon'
    print(f"- {u.name} | Role: {role} | Class: {cls_name} ({cls}) | HP: {u.max_hp} | Front: {u.front}")
    if u.kind == 'member':
        skill_names = []
        for sid in u.skills:
            keys = [k for k in data.skills if k[1] == sid]
            if keys:
                skill_names.append(data.skills[keys[0]].name)
        print(f"   Skills ({len(skill_names)}): {', '.join(skill_names[:8])}...")
        print(f"   Items: {u.items}")

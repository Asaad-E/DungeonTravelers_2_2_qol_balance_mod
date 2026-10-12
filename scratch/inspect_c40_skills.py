import sys
sys.path.insert(0, 'mod_project')
from sim import setup as setup_mod, scenario
from sim.data import game_data
from sim.variant import balance_data

data = game_data()
setup = setup_mod.load()
variant = balance_data(data)

c40 = setup.checkpoint('C40')
level = scenario.reference_levels(data, setup)['C40'][0]
gear = scenario.checkpoint_gear(data, setup, 'C40')

party = scenario.reference_party(data, setup, c40['Chapter'], level, gear, int(c40['Crown bonus'] or 0), c40['Floor'])
for m in party:
    if m.kind != 'member': continue
    print(f"=== {m.name} ({m.role}) ===")
    for sid, rank in m.skills.items():
        keys = [k for k in data.skills if k[1] == sid]
        for key in keys:
            s_v = data.skills[key]
            s_m = variant.skills[key]
            slots = ('accuracy', 'cast', 'effects', 'sp', 'speed', 'tp', 'turns')
            diffs = []
            for k in slots:
                if getattr(s_v, k) != getattr(s_m, k):
                    diffs.append((k, getattr(s_v, k), getattr(s_m, k)))
            if diffs:
                print(f"  Skill {key} ({s_v.name}, rank {rank}):")
                for k, old, new in diffs:
                    print(f"    {k}: {old} -> {new}")

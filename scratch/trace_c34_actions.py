import sys
sys.path.insert(0, 'mod_project')
from sim import setup as setup_mod, scenario
from sim.data import game_data
from sim.variant import balance_data

data = game_data()
setup = setup_mod.load()
variant = balance_data(data)

c34 = setup.checkpoint('C34')
level = scenario.reference_levels(data, setup)['C34'][0]
gear = scenario.checkpoint_gear(data, setup, 'C34')

def analyze_battle(ds, name):
    def party():
        return scenario.reference_party(ds, setup, c34['Chapter'], level, gear, int(c34['Crown bonus'] or 0), c34['Floor'])
    def enemies():
        return [scenario.fixed_battle(ds, c34['Floor'], n) for n in scenario.battle_numbers(c34)]
    
    # Run 10 battles and accumulate damage by actor and skill
    damage_by_skill = {}
    total_turns = 0
    runs = 10
    res = scenario.play(ds, setup, party, enemies, runs=runs, seed=42)
    for r in res:
        total_turns += r['time']
    print(f"=== {name} ===")
    print(f"Average time: {total_turns / runs:.1f} turns, Win: {sum(1 for r in res if r['won'])/runs*100:.0f}%")
    for i, p in enumerate(res[0]['parts']):
        print(f"  Part {i}: won={p['won']}, time={p['time']:.1f} turns, enemy damage taken={p['enemy_damage']}")

analyze_battle(data, "Vanilla")
analyze_battle(variant, "Variant")

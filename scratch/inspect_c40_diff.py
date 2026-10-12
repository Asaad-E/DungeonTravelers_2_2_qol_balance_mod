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

runs = 10
r_v = scenario.play(data, setup,
    lambda: scenario.reference_party(data, setup, c40['Chapter'], level, gear, int(c40['Crown bonus'] or 0), c40['Floor']),
    lambda: [scenario.fixed_battle(data, c40['Floor'], n) for n in scenario.battle_numbers(c40)],
    runs=runs, seed=42)

r_m = scenario.play(variant, setup,
    lambda: scenario.reference_party(variant, setup, c40['Chapter'], level, gear, int(c40['Crown bonus'] or 0), c40['Floor']),
    lambda: [scenario.fixed_battle(variant, c40['Floor'], n) for n in scenario.battle_numbers(c40)],
    runs=runs, seed=42)

def summarize_parts(res):
    p0_times = [r['parts'][0]['time'] for r in res if r['parts'][0]['won']]
    p1_times = [r['parts'][1]['time'] for r in res if len(r['parts']) > 1 and r['parts'][1]['won']]
    return {
        'total_time': sum(r['time'] for r in res if r['won']) / max(1, sum(1 for r in res if r['won'])),
        'p0_time': sum(p0_times) / max(1, len(p0_times)),
        'p1_time': sum(p1_times) / max(1, len(p1_times)),
        'won': sum(1 for r in res if r['won']) / len(res)
    }

print("Vanilla summary:", summarize_parts(r_v))
print("Variant summary:", summarize_parts(r_m))

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
from sim.data import game_data
from sim.setup import load
from sim import scenario
from sim.battle import Battle
import sim.policy as P

d = game_data()
s = load()
cp = s.checkpoint('C30')
levels = scenario.reference_levels(d, s)['C30'][0]
gear = scenario.checkpoint_gear(d, s, 'C30')

from scratch.test_ai_live import (
    improved_expected_damage, improved_best_single_target,
    improved_act_damage, improved_act_status, improved_act_dispel
)

def trace_battle(ai_name):
    print(f"=== TRACE {ai_name} RUN 1 ===")
    rng_seed = int(s.settings['seed']) + 1
    party = scenario.reference_party(d, s, cp['Chapter'], levels, gear, 0, cp['Floor'])
    groups = [scenario.fixed_battle(d, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    
    for i, grp in enumerate(groups):
        print(f"\n--- Part {i+1} Start ---")
        scenario.prepare(s, party, grp)
        for m in party:
            print(f"  {m.name} ({getattr(m, 'role', 'unknown')}): HP={m.hp}/{m.max_hp}, TP={m.tp}/{m.max_tp}")
        policy = P.Policy(P.load_rules(s.policies), s.settings)
        b = Battle(d, party, grp, scenario.random.Random(rng_seed), choose_member=policy, setup=s.settings, max_time=400)
        res = b.run()
        print(f"Part {i+1} Result: won={res['won']}, time={res['time']}")
        for (u, skill_name), count in res['record'].skill_uses.items():
            if u.side == 0:
                print(f"    {u.name} used {skill_name}: {count} times")
        if not res['won']:
            print("Enemies alive:")
            for e in grp:
                if e.alive:
                    print(f"    Enemy {e.name}: HP={e.hp}/{e.max_hp}")
            break

print("--- ORIGINAL AI ---")
trace_battle("ORIG")

Battle.expected_damage = improved_expected_damage
P.best_single_target = improved_best_single_target
P.act_damage = improved_act_damage
P.act_status = improved_act_status
P.act_dispel = improved_act_dispel
P.ACTIONS['damage'] = improved_act_damage
P.ACTIONS['status'] = improved_act_status
P.ACTIONS['dispel'] = improved_act_dispel

print("\n--- IMPROVED AI ---")
trace_battle("NEW")

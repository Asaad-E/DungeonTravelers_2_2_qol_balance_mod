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

def test_run(label):
    wins = 0
    for k in range(10):
        res = scenario.play(d, s,
            lambda: scenario.reference_party(d, s, cp['Chapter'], levels, gear, 0, cp['Floor']),
            lambda: [scenario.fixed_battle(d, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
            runs=1, seed=int(s.settings['seed']) + k)[0]
        if res['won']:
            wins += 1
        else:
            parts_won = [p['won'] for p in res['parts']]
            print(f"{label} lost run {k}: hp_left={res['hp_left']}, parts_won={parts_won}")
    print(f"{label} total wins: {wins}/10")

print('--- ORIGINAL AI ---')
test_run('Orig')

Battle.expected_damage = improved_expected_damage
P.best_single_target = improved_best_single_target
P.act_damage = improved_act_damage
P.act_status = improved_act_status
P.act_dispel = improved_act_dispel
P.ACTIONS['damage'] = improved_act_damage
P.ACTIONS['status'] = improved_act_status
P.ACTIONS['dispel'] = improved_act_dispel

print('--- IMPROVED AI ---')
test_run('New')

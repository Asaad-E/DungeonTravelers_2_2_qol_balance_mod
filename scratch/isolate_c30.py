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
    improved_act_damage, improved_act_status, improved_act_dispel,
    orig_best_single_target, orig_act_damage, orig_act_status, orig_act_dispel, orig_expected_damage
)

def eval_config(name):
    res = scenario.play(d, s,
        lambda: scenario.reference_party(d, s, cp['Chapter'], levels, gear, 0, cp['Floor']),
        lambda: [scenario.fixed_battle(d, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
        runs=20, seed=1234)
    win_rate = sum(r['won'] for r in res) / 20
    print(f"{name}: win_rate={win_rate*100:.1f}%")

# Reset to orig
def reset():
    Battle.expected_damage = orig_expected_damage
    P.best_single_target = orig_best_single_target
    P.act_damage = orig_act_damage
    P.act_status = orig_act_status
    P.act_dispel = orig_act_dispel
    P.ACTIONS['damage'] = orig_act_damage
    P.ACTIONS['status'] = orig_act_status
    P.ACTIONS['dispel'] = orig_act_dispel

reset()
eval_config("1. Baseline (Orig)")

reset()
Battle.expected_damage = improved_expected_damage
eval_config("2. Only expected_damage")

reset()
P.best_single_target = improved_best_single_target
eval_config("3. Only best_single_target")

reset()
P.act_damage = improved_act_damage
P.ACTIONS['damage'] = improved_act_damage
eval_config("4. Only act_damage")

reset()
P.act_status = improved_act_status
P.ACTIONS['status'] = improved_act_status
eval_config("5. Only act_status")

reset()
P.act_dispel = improved_act_dispel
P.ACTIONS['dispel'] = improved_act_dispel
eval_config("6. Only act_dispel")

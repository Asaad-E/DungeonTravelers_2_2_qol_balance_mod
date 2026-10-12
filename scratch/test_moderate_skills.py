import sys, copy
sys.path.insert(0, 'mod_project')
from sim import setup as setup_mod, scenario
from sim.data import game_data
from sim.variant import balance_data

data = game_data()
setup = setup_mod.load()

def eval_cps(ds):
    res = {}
    for cid in ('C22', 'C29', 'C34', 'C40'):
        cp = setup.checkpoint(cid)
        level = scenario.reference_levels(ds, setup)[cid][0]
        gear = scenario.checkpoint_gear(ds, setup, cid)
        runs = scenario.play(ds, setup,
            lambda: scenario.reference_party(ds, setup, cp['Chapter'], level, gear, int(cp['Crown bonus'] or 0), cp['Floor']),
            lambda: [scenario.fixed_battle(ds, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
            runs=15, seed=42)
        wins = [r for r in runs if r['won']]
        t = sum(r['time'] for r in wins)/len(wins) if wins else 0
        w = len(wins)/len(runs)*100
        res[cid] = (w, t)
    return res

print("Vanilla:", eval_cps(data))

variant_current = balance_data(data)
print("Current Variant:", eval_cps(variant_current))

# Test Model 1: Revert T031-T040 (Checkmate at S003-S012 level: 0.38 - 1.185)
# And Pursuit Stab at +35% (0.95 - 1.51) instead of +100% (1.40 - 2.24)
var_mod1 = copy.deepcopy(variant_current)
cm_key = ('Technique', 82)
# S003-S012 values
cm_s_vals = [0.38, 0.449, 0.518, 0.587, 0.633, 0.725, 0.817, 0.932, 1.047, 1.185]
for i, (e, kind, v) in enumerate(var_mod1.skills[cm_key].effects):
    if e == 26:
        var_mod1.skills[cm_key].effects[i] = (e, kind, cm_s_vals)

ps_key = ('Technique', 32)
ps_v_vals = [0.7, 0.82, 0.94, 1.04, 1.12]
ps_mod1_vals = [round(x * 1.35, 3) for x in ps_v_vals]  # ~0.945 - 1.512
for i, (e, kind, v) in enumerate(var_mod1.skills[ps_key].effects):
    if e == 26:
        var_mod1.skills[ps_key].effects[i] = (e, kind, ps_mod1_vals)

print("Moderate Model 1 (Checkmate S-pass, Pursuit Stab +35%):", eval_cps(var_mod1))

# Test Model 2: Checkmate at +25% over Vanilla (0.25 - 1.125) and Pursuit Stab at +25% (0.875 - 1.40)
var_mod2 = copy.deepcopy(variant_current)
cm_mod2_vals = [round(x * 1.25, 3) for x in [0.2, 0.26, 0.32, 0.38, 0.42, 0.5, 0.58, 0.68, 0.78, 0.9]]
for i, (e, kind, v) in enumerate(var_mod2.skills[cm_key].effects):
    if e == 26:
        var_mod2.skills[cm_key].effects[i] = (e, kind, cm_mod2_vals)

ps_mod2_vals = [round(x * 1.25, 3) for x in ps_v_vals]
for i, (e, kind, v) in enumerate(var_mod2.skills[ps_key].effects):
    if e == 26:
        var_mod2.skills[ps_key].effects[i] = (e, kind, ps_mod2_vals)

print("Moderate Model 2 (Checkmate +25%, Pursuit Stab +25%):", eval_cps(var_mod2))

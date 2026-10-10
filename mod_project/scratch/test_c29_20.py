import sys, os
sys.path.insert(0, 'mod_project')
from tools.party_battery import PARTIES, build_party
from sim import setup as setup_mod, scenario
from sim.data import game_data
from sim.variant import balance_data

data = game_data()
setup = setup_mod.load()

# Create Variant with +20% HP (9,000 HP)
var_20 = balance_data(data)
var_20.enemies[785]['hp'] = 9000

# Also create Vanilla (7,500 HP) and Mod Original (+30% HP = 9,750 HP)
var_30 = balance_data(data)
var_30.enemies[785]['hp'] = 9750

cp = setup.checkpoint('C29')

print("=================================================================")
print("SIMULACIÓN C29 (Calliope) con +20% HP (9,000 HP) vs Mod vs Vanilla")
print("=================================================================\n")

def run_test_for_variant(var_data, hp_label, runs=12):
    print(f"--- Evaluando Calliope con {hp_label} ---")
    def enemy_factory():
        return [scenario.fixed_battle(var_data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    
    for name, p_info in PARTIES.items():
        def party_factory():
            return build_party(var_data, setup, p_info['roles'], 'C29')
            
        res = scenario.play(var_data, setup, party_factory, enemy_factory, runs=runs)
        
        wins = [r for r in res if r['won']]
        losses = [r for r in res if not r['won']]
        win_pct = len(wins) / len(res) * 100
        
        if wins:
            # Average party rounds (actions / 5) and enemy actions
            party_rounds_win = [sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins]
            cal_turns_win = [sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'enemy' and getattr(u, 'name', '') == 'Calliope') for r in wins]
            avg_pr = sum(party_rounds_win) / len(party_rounds_win)
            avg_cal = sum(cal_turns_win) / len(cal_turns_win)
            win_str = f"VICTORIA en {avg_pr:.1f} rondas de equipo (~{avg_cal:.1f} turnos Calliope)"
        else:
            win_str = "0 victorias (No supera la curación)"
            
        if losses:
            party_rounds_loss = [sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in losses]
            cal_turns_loss = [sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'enemy' and getattr(u, 'name', '') == 'Calliope') for r in losses]
            avg_pr_l = sum(party_rounds_loss) / len(party_rounds_loss)
            avg_cal_l = sum(cal_turns_loss) / len(cal_turns_loss)
            loss_str = f"Derrota tras {avg_pr_l:.1f} rondas (~{avg_cal_l:.1f} turnos Calliope)"
        else:
            loss_str = "Sin derrotas"
            
        print(f"  * {name:22s} [{win_pct:3.0f}% Win]: {win_str}")
        if losses and not wins:
            print(f"      -> {loss_str}")
    print()

run_test_for_variant(var_20, "+20% HP (9,000 HP)", runs=12)
run_test_for_variant(var_30, "+30% HP (9,750 HP, Mod actual)", runs=12)

import sys, os
sys.path.insert(0, 'mod_project')
from tools.party_battery import PARTIES, build_party
from sim import setup as setup_mod, scenario
from sim.data import game_data
from sim.variant import balance_data
from sim.battle import Battle
from sim.units import Status

class SilencingBattle(Battle):
    """Battle where Calliope is silenced every 8 turns (turns 1, 9, 17, 25...)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calliope_turn_count = 0

    def turn(self, unit):
        if getattr(unit, 'name', '') == 'Calliope' and unit.alive:
            self.calliope_turn_count += 1
            if (self.calliope_turn_count - 1) % 8 == 0:
                # Apply Silence (117) for 3 turns
                unit.statuses[117] = Status(117, 1.0, turns=3, kind=5)
                # End chants and songs
                unit.chanting = None
                unit.song = None
                if getattr(self, 'record', None):
                    self.record.add('denied', unit, 1)
        super().turn(unit)

def run_silence_simulation(hp_value, hp_label, runs=12):
    data = game_data()
    setup = setup_mod.load()
    var = balance_data(data)
    var.enemies[785]['hp'] = hp_value
    
    cp = setup.checkpoint('C29')
    
    print(f"================================================================")
    print(f"C29 (Calliope @ {hp_label}): SILENCIADA CADA 8 TURNOS (Duración: 3 turnos)")
    print(f"================================================================\n")
    
    # Save original Battle class in scenario
    old_battle = scenario.Battle
    scenario.Battle = SilencingBattle
    
    try:
        def enemy_factory():
            return [scenario.fixed_battle(var, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
            
        for name, p_info in PARTIES.items():
            def party_factory():
                return build_party(var, setup, p_info['roles'], 'C29')
                
            res = scenario.play(var, setup, party_factory, enemy_factory, runs=runs)
            
            wins = [r for r in res if r['won']]
            losses = [r for r in res if not r['won']]
            win_pct = len(wins) / len(res) * 100
            
            if wins:
                party_rounds_win = [sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins]
                cal_turns_win = [sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'enemy' and getattr(u, 'name', '') == 'Calliope') for r in wins]
                avg_pr = sum(party_rounds_win) / len(party_rounds_win)
                avg_cal = sum(cal_turns_win) / len(cal_turns_win)
                win_str = f"VICTORIA en {avg_pr:.1f} rondas de equipo (~{avg_cal:.1f} turnos Calliope)"
            else:
                win_str = "0 victorias (Aun con silencio no pudo)"
                
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
    finally:
        scenario.Battle = old_battle

if __name__ == '__main__':
    # 1. Run at +20% HP (9,000 HP) as requested
    run_silence_simulation(9000, "+20% HP (9,000 HP)", runs=15)
    # 2. Also run at +30% HP (9,750 HP) for comparison
    run_silence_simulation(9750, "+30% HP (9,750 HP, Mod actual)", runs=15)

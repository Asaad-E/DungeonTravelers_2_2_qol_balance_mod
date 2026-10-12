import sys
sys.path.insert(0, 'mod_project')
from sim import setup as setup_mod, scenario
from sim.data import game_data
from sim.variant import balance_data
from tools.parallel_party_battery import PARTIES, build_party_complete

data = game_data()
setup = setup_mod.load()
variant = balance_data(data)

p_info = PARTIES['Anti-Meta']
cid = 'C40'
cp = setup.checkpoint(cid)

class LoggingBattle(scenario.Battle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = []

    def turn(self, unit):
        action = getattr(unit, 'action', None)
        super().turn(unit)

    def fall(self, unit, source=None):
        src_name = getattr(source, 'name', 'unknown') if source else 'unknown'
        print(f"  [DEATH] {unit.name} ({getattr(unit, 'role', 'enemy')}) fell! Killed by {src_name}.")
        super().fall(unit, source)

    def take_damage(self, unit, amount, *args, **kwargs):
        res = super().take_damage(unit, amount, *args, **kwargs)
        if unit.kind == 'member' and amount > 50:
            print(f"  [DMG] {unit.name} took {amount} dmg! Remaining HP: {unit.hp}/{unit.max_hp}")
        elif unit.kind == 'enemy' and amount > 100:
            print(f"  [BOSS DMG] {unit.name} took {amount} dmg! Remaining HP: {unit.hp}/{unit.max_hp}")
        return res

old_battle = scenario.Battle
scenario.Battle = LoggingBattle

try:
    def party_factory():
        return build_party_complete(variant, setup, p_info['roles'], cid)

    def enemy_factory():
        return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    print(f"=== Simulating C40 with Anti-Meta Party (Seed 42) ===")
    res = scenario.play(variant, setup, party_factory, enemy_factory, runs=1, seed=42)[0]
    print(f"\nFinal Result: Won={res['won']}, Total Time={res['time']}")
    for i, p in enumerate(res['parts']):
        print(f"Part {i}: won={p['won']}, rounds={p['rounds']}, time={p['time']}")
finally:
    scenario.Battle = old_battle

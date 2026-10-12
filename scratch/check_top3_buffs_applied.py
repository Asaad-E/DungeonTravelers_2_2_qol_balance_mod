import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
from sim.data import game_data
from sim.variant import balance_data

d = game_data()
var = balance_data(d)

print("=== VERIFYING LOADED ENEMY DATA FROM BALANCE_DATA() ===")
for eid in [1002, 760, 825]:
    e = var.enemies[eid]
    orig = d.enemies[eid]
    print(f"ID {eid:>4} | {e['name']:<22} | HP: {orig['hp']} -> {e['hp']} (+{(e['hp']/orig['hp']-1)*100:.1f}%) | ATK: {orig['atk']} -> {e['atk']} | DEF: {orig['def']} -> {e['def']}")

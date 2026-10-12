import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
from sim.data import game_data
from sim.setup import load
from sim import scenario

d = game_data()
s = load()

for cid in ['C10', 'C13', 'C18', 'C24']:
    cp = s.checkpoint(cid)
    boss_name = cp.get('Boss (as the story page names it)', '')
    print(f"\n=== Checkpoint {cid}: {boss_name} (Floor {cp['Floor']}) ===")
    for n in scenario.battle_numbers(cp):
        battle = next(b for b in d.fixed if b['floor'] == cp['Floor'] and b['number'] == n)
        for enemy_id, front in battle['enemies']:
            e = d.enemies[enemy_id]
            print(f"  Enemy ID: {enemy_id:>3} | Name: {e.get('name'):<22} | Front: {front} | Level: {e.get('level')} | HP: {e.get('hp'):>5} | ATK: {e.get('atk'):>4} | DEF: {e.get('def'):>4} | INT: {e.get('int'):>4} | RES: {e.get('res'):>4} | AGI: {e.get('agi'):>4}")
            print(f"    Passives: {e.get('passives')}")
            print(f"    Resistances: Fire={e.get('res_fire')} Water={e.get('res_water')} Wind={e.get('res_wind')} Earth={e.get('res_earth')} Light={e.get('res_light')} Dark={e.get('res_dark')}")
            print(f"    Flags: {hex(e.get('flags', 0))} | Immune: {e.get('immune', [])}")
            if e.get('script'):
                print(f"    AI script sets: {list(e['script'].get('sets', {}).keys())}")

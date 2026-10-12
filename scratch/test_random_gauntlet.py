import os
import sys
import random
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import scenario
from sim import setup as setup_mod
from sim.data import game_data
from sim.variant import balance_data
from sim.units import build_enemy
from sim.scenario import Group
from tools.parallel_party_battery import PARTIES, build_party_complete

def get_weighted_formation(fl_data, rng):
    forms = fl_data['formations']
    weights = [f['chance'] for f in forms]
    return rng.choices(forms, weights=weights, k=1)[0]

def run_dungeon_test(cid, gauntlet_len=5, runs=10):
    d = game_data()
    bd = balance_data(d)
    s = setup_mod.load()
    
    cp = s.checkpoint(cid)
    floor = cp['Floor']
    fl_data_v = next(f for f in d.floors if f['floor'] == floor)
    fl_data_m = next(f for f in bd.floors if f['floor'] == floor)
    
    print(f"=== Testing CID {cid} (Floor {floor}) | {gauntlet_len}-battle gauntlet, {runs} runs ===")
    
    for party_name, pinfo in PARTIES.items():
        for variant_name, data_source, fl_data in [('Vanilla', d, fl_data_v), ('Mod', bd, fl_data_m)]:
            def party_factory():
                return build_party_complete(data_source, s, pinfo['roles'], cid)
            
            def enemy_factory():
                # generate gauntlet_len random encounters
                rng = random.Random(42) # dummy, overridden in play by seed
                groups = []
                for _ in range(gauntlet_len):
                    form = get_weighted_formation(fl_data, rng)
                    grp = Group(build_enemy(data_source, eid, front) for eid, front in form['enemies'])
                    grp.floor = floor
                    groups.append(grp)
                return groups

            # In scenario.play, rng inside play is used
            # Let's customize play to generate unique random groups per run seed
            results = []
            seed = int(s.settings.get('seed', 20261005))
            for k in range(runs):
                rng = random.Random(seed + k)
                party = party_factory()
                groups = []
                for _ in range(gauntlet_len):
                    form = get_weighted_formation(fl_data, rng)
                    grp = Group(build_enemy(data_source, eid, front) for eid, front in form['enemies'])
                    grp.floor = floor
                    groups.append(grp)
                
                # play this gauntlet
                res = None
                for grp in groups:
                    for u in party:
                        u.statuses, u.chant, u.song, u.dance = {}, None, [], []
                    party = [u for u in party if u.kind in ('member', 'summon')]
                    b = scenario.Battle(data_source, party, grp, rng, choose_member=scenario.Policy(scenario.load_rules(s.policies), s.settings),
                                        setup=dict(s.settings), zone=getattr(grp, 'zone', None), max_time=300)
                    part = b.run()
                    if res is None:
                        res = dict(part)
                    else:
                        res['actions'] += part['actions']
                        res['time'] += part['time']
                        res['won'] = res['won'] and part['won']
                    if not part['won']:
                        res['won'] = False
                        break
                    scenario.recover_after_battle(party)
                results.append(res)
            
            wins = sum(1 for r in results if r['won'])
            avg_acts = sum(r['actions'] for r in results if r['won']) / max(1, wins)
            avg_hp = sum(r['hp_left'] for r in results if r['won']) / max(1, wins) * 100
            print(f"  {party_name:12s} | {variant_name:7s} | Win: {wins/runs*100:5.1f}% ({wins:2d}/{runs}) | Acts: {avg_acts:5.1f} | HP left: {avg_hp:4.1f}%")

if __name__ == '__main__':
    run_dungeon_test('C30', gauntlet_len=5, runs=10)

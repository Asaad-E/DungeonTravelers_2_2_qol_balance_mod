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

def run_all(cids=['C06', 'C17', 'C30', 'C40', 'P08'], gauntlet_len=5, runs=10):
    d = game_data()
    bd = balance_data(d)
    s = setup_mod.load()
    
    zone_names = {
        'C06': 'Early (St02, Lv9)',
        'C17': 'Mid (St06, Lv25)',
        'C30': 'Late-Mid (St10, Lv44)',
        'C40': 'Endgame (St15, Lv64)',
        'P08': 'Postgame (St21, Lv72)'
    }
    
    all_results = {}
    
    for cid in cids:
        cp = s.checkpoint(cid)
        floor = cp['Floor']
        fl_data_v = next((f for f in d.floors if f['floor'] == floor), None)
        fl_data_m = next((f for f in bd.floors if f['floor'] == floor), None)
        if not fl_data_v or not fl_data_m:
            print(f"Skipping {cid}: floor {floor} not found in floors data")
            continue
            
        print(f"\n=======================================================")
        print(f" ZONE: {zone_names.get(cid, cid)} | Floor: {floor}")
        print(f"=======================================================")
        
        all_results[cid] = {}
        
        for party_name, pinfo in PARTIES.items():
            all_results[cid][party_name] = {}
            for variant_name, data_source, fl_data in [('Vanilla', d, fl_data_v), ('Mod', bd, fl_data_m)]:
                results = []
                seed = int(s.settings.get('seed', 20261005))
                for k in range(runs):
                    rng = random.Random(seed + k)
                    party = build_party_complete(data_source, s, pinfo['roles'], cid)
                    
                    groups = []
                    for _ in range(gauntlet_len):
                        form = get_weighted_formation(fl_data, rng)
                        grp = Group(build_enemy(data_source, eid, front) for eid, front in form['enemies'])
                        grp.floor = floor
                        groups.append(grp)
                    
                    res = None
                    for grp in groups:
                        for u in party:
                            u.statuses, u.chant, u.song, u.dance = {}, None, [], []
                        party = [u for u in party if u.kind in ('member', 'summon')]
                        b = scenario.Battle(data_source, party, grp, rng,
                                            choose_member=scenario.Policy(scenario.load_rules(s.policies), s.settings),
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
                all_results[cid][party_name][variant_name] = {
                    'win_pct': wins / runs * 100,
                    'wins': wins,
                    'runs': runs,
                    'acts': avg_acts,
                    'hp': avg_hp
                }
                print(f"  {party_name:12s} | {variant_name:7s} | Win: {wins/runs*100:5.1f}% ({wins:2d}/{runs}) | Acts: {avg_acts:5.1f} | HP left: {avg_hp:4.1f}%")

    print("\n\n" + "="*80)
    print("MASTER SUMMARY TABLE (Random Encounters Gauntlet: 5 consecutive battles)")
    print("="*80)
    for cid in cids:
        print(f"\n### {zone_names.get(cid, cid)} (Checkpoint {cid})")
        print("| Party | Vanilla Win | Vanilla Acts | Mod Win | Mod Acts | Delta Acts | Mod HP Left |")
        print("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
        for pname in PARTIES.keys():
            v = all_results[cid][pname]['Vanilla']
            m = all_results[cid][pname]['Mod']
            delta = m['acts'] - v['acts']
            print(f"| {pname:12s} | {v['win_pct']:5.1f}% | {v['acts']:5.1f} | {m['win_pct']:5.1f}% | {m['acts']:5.1f} | {delta:+5.1f} | {m['hp']:4.1f}% |")

if __name__ == '__main__':
    run_all()

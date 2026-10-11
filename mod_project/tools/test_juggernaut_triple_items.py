"""
Test Juggernaut (Physical Party) with 3x Items across all 17 Story Bosses (N=50).
Compares:
1. Vanilla (1x Items: 40 items)
2. Mod (1x Items: 40 items)
3. Mod (3x Items: 120 items - backpacker playstyle)
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import scenario
from sim import setup as setup_mod
from sim.battle import Battle, Status
from sim.data import game_data
from sim.variant import balance_data

CHECKPOINTS = ['C06', 'C10', 'C13', 'C17', 'C18', 'C19', 'C21', 'C24', 'C26', 'C28', 'C29', 'C30', 'C32', 'C34', 'C36', 'C38', 'C40']

JUGGERNAUT_ROLES = ['tank', 'attacker', 'dark lord', 'kunoichi', 'etoile']

class SilencingBattle(Battle):
    """Battle for C29 where Calliope is silenced every 8 turns."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calliope_turn_count = 0

    def turn(self, unit):
        if getattr(unit, 'name', '') == 'Calliope' and unit.alive:
            self.calliope_turn_count += 1
            if (self.calliope_turn_count - 1) % 8 == 0:
                unit.statuses[117] = Status(117, 1.0, turns=3, kind=5)
                unit.chanting = None
                unit.song = None
                if getattr(self, 'record', None):
                    self.record.add('denied', unit, 1)
        super().turn(unit)

def build_party_custom(data_source, setup, role_names, cid, item_multiplier=1):
    cp = setup.checkpoint(cid)
    chapter, floor = cp['Chapter'], cp['Floor']
    level = scenario.reference_levels(data_source, setup)[cid][0]
    upgrade = scenario.checkpoint_gear(data_source, setup, cid)
    crown = int(cp['Crown bonus'] or 0)
    
    chars = {c['name']: c for c in data_source.characters}
    pool = scenario.available(setup, chapter)
    sealbook = scenario.grand_sealbook(setup, chapter, floor)
    book = data_source.sealbooks.get(sealbook) if sealbook is not None else None
    party_enchants = tuple(book['enchants']) if book else ()
    size = int(setup.settings.get('party_size', 5))
    taken, party = set(), []
    
    for rname in role_names:
        if len(party) >= size:
            break
        role = setup.roles.get(rname)
        if not role:
            continue
        base = scenario.class_id(data_source, role['Base class'])
        for name in str(role['Characters (order of preference)']).split(';'):
            name = name.strip()
            c = chars.get(name)
            if name in pool and name not in taken and c and c['base_class'] == base:
                j_lvl = scenario.level_of_exp(data_source, c['start_exp'] or 0)
                party.append(scenario.build_role_member(data_source, setup, rname, c, max(level, j_lvl), upgrade, crown,
                                               scenario.forge_open(setup, floor), party_enchants=party_enchants,
                                               pieces=scenario.unique_pieces(setup, rname, chapter, floor),
                                               sealbook=scenario.personal_sealbook(setup, rname, chapter, floor)))
                taken.add(name)
                break
                
    for name in pool:
        if len(party) >= size:
            break
        c = chars.get(name)
        if name in taken or not c:
            continue
        for rname in role_names:
            role = setup.roles.get(rname)
            if role and scenario.class_id(data_source, role['Base class']) == c['base_class']:
                j_lvl = scenario.level_of_exp(data_source, c['start_exp'] or 0)
                party.append(scenario.build_role_member(data_source, setup, rname, c, max(level, j_lvl), upgrade, crown,
                                               scenario.forge_open(setup, floor), party_enchants=party_enchants,
                                               pieces=scenario.unique_pieces(setup, rname, chapter, floor),
                                               sealbook=scenario.personal_sealbook(setup, rname, chapter, floor)))
                taken.add(name)
                break

    front = int(setup.settings.get('front_size', 3))
    if sum(u.front for u in party) > front:
        for u in sorted((u for u in party if u.front), key=lambda u: u.max_hp)[:sum(u.front for u in party) - front]:
            u.front = False
    if not any(u.front for u in party) and party:
        max(party, key=lambda u: u.max_hp).front = True
        
    count = int(setup.settings.get('kit_count', 0) or 0) * item_multiplier
    bag = {int(r['Item_ID']): int(round(count * float(r['Share'] or 1))) for r in setup.kit}
    for u in party:
        u.items = bag
        
    if sealbook is not None:
        summon = scenario.sealbook_summon(data_source, setup, sealbook, party)
        if summon is not None:
            summon.items = {}
            party.append(summon)
            
    return party

_DATA = None
_SETUP = None
_VARIANT = None

def init_worker():
    global _DATA, _SETUP, _VARIANT
    _DATA = game_data()
    _SETUP = setup_mod.load()
    _VARIANT = balance_data(_DATA)

def run_task(args):
    cid, runs, seed = args
    global _DATA, _SETUP, _VARIANT
    data, setup, variant = _DATA, _SETUP, _VARIANT
    cp = setup.checkpoint(cid)

    # 1. Vanilla (1x items)
    def pf_v(): return build_party_custom(data, setup, JUGGERNAUT_ROLES, cid, item_multiplier=1)
    def ef_v(): return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    res_v = scenario.play(data, setup, pf_v, ef_v, runs=runs, seed=seed)

    # 2. Mod (1x items)
    old_battle = scenario.Battle
    if cid == 'C29': scenario.Battle = SilencingBattle
    try:
        def pf_m1(): return build_party_custom(variant, setup, JUGGERNAUT_ROLES, cid, item_multiplier=1)
        def ef_m1(): return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res_m1 = scenario.play(variant, setup, pf_m1, ef_m1, runs=runs, seed=seed)

        # 3. Mod (3x items)
        def pf_m3(): return build_party_custom(variant, setup, JUGGERNAUT_ROLES, cid, item_multiplier=3)
        def ef_m3(): return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        res_m3 = scenario.play(variant, setup, pf_m3, ef_m3, runs=runs, seed=seed)
    finally:
        scenario.Battle = old_battle

    def stats(res):
        w = [r for r in res if r['won']]
        l = [r for r in res if not r['won']]
        pct = len(w) / len(res) * 100.0
        if w:
            rnd = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in w) / len(w)
        else:
            rnd = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in l) / max(1, len(l))
        return pct, rnd, bool(w)

    v_pct, v_rnd, v_won = stats(res_v)
    m1_pct, m1_rnd, m1_won = stats(res_m1)
    m3_pct, m3_rnd, m3_won = stats(res_m3)

    return (cid, (v_pct, v_rnd, v_won), (m1_pct, m1_rnd, m1_won), (m3_pct, m3_rnd, m3_won))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=50)
    parser.add_argument('--workers', type=int, default=10)
    args = parser.parse_args()

    start = time.time()
    print(f"=== Simulacion Juggernaut (Party Fisica) con 3x Items (N={args.runs}, Workers={args.workers}) ===\n")

    tasks = [(cid, args.runs, 42) for cid in CHECKPOINTS]
    results = {}
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init_worker) as executor:
        for cid, v, m1, m3 in executor.map(run_task, tasks):
            results[cid] = {'v': v, 'm1': m1, 'm3': m3}

    print(f"Simulacion finalizada en {time.time() - start:.1f}s.\n")

    lines = []
    lines.append(f"# Impacto de 3x Objetos en Juggernaut (Party Física) - N={args.runs} Runs\n")
    lines.append("| Boss | Vanilla (1x Kit) | Mod Base (1x Kit) | **Mod con 3x Items (Kit Triple)** |")
    lines.append("|:---:|:---:|:---:|:---:|")

    for cid in CHECKPOINTS:
        r = results[cid]
        v_str = f"{r['v'][0]:.0f}% ({r['v'][1]:.1f}r)" if r['v'][2] else f"0% (cae {r['v'][1]:.1f}r)"
        m1_str = f"{r['m1'][0]:.0f}% ({r['m1'][1]:.1f}r)" if r['m1'][2] else f"0% (cae {r['m1'][1]:.1f}r)"
        m3_str = f"**{r['m3'][0]:.0f}%** ({r['m3'][1]:.1f}r)" if r['m3'][2] else f"0% (cae {r['m3'][1]:.1f}r)"
        lines.append(f"| **{cid}** | {v_str} | {m1_str} | {m3_str} |")

    report_md = "\n".join(lines)
    out_path = os.path.join(BASE_DIR, 'docs', 'generated', 'JUGGERNAUT_TRIPLE_ITEMS_REPORT.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report_md)

    print(report_md)

if __name__ == '__main__':
    main()

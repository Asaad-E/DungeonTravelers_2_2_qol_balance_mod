import argparse
from concurrent.futures import ProcessPoolExecutor
import io
import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import scenario
from sim import setup as setup_mod
from sim.data import game_data
from sim.variant import balance_data
from tools.parallel_party_battery import CHECKPOINTS, build_party_complete

TEST_PARTIES = {
    'Jugger (Etoile)': ['tank', 'attacker', 'dark lord', 'kunoichi', 'etoile'],
    'Jugger (Diva)':   ['tank', 'attacker', 'dark lord', 'kunoichi', 'diva'],
    'Anti (Mistress)': ['magical princess', 'mistress', 'soul summoner', 'joker', 'dolls'],
    'Anti (Diva)':     ['magical princess', 'diva', 'soul summoner', 'joker', 'dolls'],
}

_DATA = None
_SETUP = None
_VARIANT = None

def init_worker():
    global _DATA, _SETUP, _VARIANT
    _DATA = game_data()
    _SETUP = setup_mod.load()
    _VARIANT = balance_data(_DATA)

def run_task(args):
    cid, pname, runs, seed = args
    global _DATA, _SETUP, _VARIANT
    data, setup, variant = _DATA, _SETUP, _VARIANT
    cp = setup.checkpoint(cid)
    roles = TEST_PARTIES[pname]

    # 1. Vanilla
    def pf_v(): return build_party_complete(data, setup, roles, cid)
    def ef_v(): return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    res_v = scenario.play(data, setup, pf_v, ef_v, runs=runs, seed=seed)

    # 2. Mod
    def pf_m(): return build_party_complete(variant, setup, roles, cid)
    def ef_m(): return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    res_m = scenario.play(variant, setup, pf_m, ef_m, runs=runs, seed=seed)

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
    m_pct, m_rnd, m_won = stats(res_m)

    return (cid, pname, (v_pct, v_rnd), (m_pct, m_rnd))

def main():
    runs = 20
    workers = 10
    tasks = []
    for cid in CHECKPOINTS:
        for pname in TEST_PARTIES.keys():
            tasks.append((cid, pname, runs, 42))

    start = time.time()
    results = {}
    with ProcessPoolExecutor(max_workers=workers, initializer=init_worker) as executor:
        for cid, pname, v_stat, m_stat in executor.map(run_task, tasks):
            results.setdefault(cid, {})[pname] = {'v': v_stat, 'm': m_stat}

    elapsed = time.time() - start

    # Print nicely
    print(f"=== BATERIA JUGGERNAUT Y ANTI-META CON DIVA (N={runs}, {elapsed:.1f}s) ===\n")
    
    print("### COMPARATIVA 1: JUGGERNAUT (ETOILE vs DIVA)")
    print("| Boss | Van (Etoile) | Mod (Etoile) | Van (Diva) | Mod (Diva) | Impacto Diva en Mod |")
    print("|:---:|:---:|:---:|:---:|:---:|:---:|")
    for cid in CHECKPOINTS:
        e = results[cid]['Jugger (Etoile)']
        d = results[cid]['Jugger (Diva)']
        delta_diva = d['m'][0] - e['m'][0]
        sign = "+" if delta_diva > 0 else ""
        print(f"| {cid} | {e['v'][0]:4.0f}% ({e['v'][1]:4.1f}r) | {e['m'][0]:4.0f}% ({e['m'][1]:4.1f}r) | {d['v'][0]:4.0f}% ({d['v'][1]:4.1f}r) | {d['m'][0]:4.0f}% ({d['m'][1]:4.1f}r) | {sign}{delta_diva:4.0f}% |")

    print("\n### COMPARATIVA 2: ANTI-META (MISTRESS vs DIVA)")
    print("| Boss | Van (Mistress) | Mod (Mistress) | Van (Diva) | Mod (Diva) | Impacto Diva en Mod |")
    print("|:---:|:---:|:---:|:---:|:---:|:---:|")
    for cid in CHECKPOINTS:
        m = results[cid]['Anti (Mistress)']
        d = results[cid]['Anti (Diva)']
        delta_diva = d['m'][0] - m['m'][0]
        sign = "+" if delta_diva > 0 else ""
        print(f"| {cid} | {m['v'][0]:4.0f}% ({m['v'][1]:4.1f}r) | {m['m'][0]:4.0f}% ({m['m'][1]:4.1f}r) | {d['v'][0]:4.0f}% ({d['v'][1]:4.1f}r) | {d['m'][0]:4.0f}% ({d['m'][1]:4.1f}r) | {sign}{delta_diva:4.0f}% |")

if __name__ == '__main__':
    main()

"""
Parallel Party Battery:
Runs all 17 story bosses across 5 party archetypes in parallel using multiprocessing.
Generates a compact Markdown report where each row is a boss (code only) and all
5 parties are formatted within a single cell separated by line breaks.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import math
import os
import random
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

PARTIES = {
    'Meta': {
        'desc': 'Golden Standard (Valkyrie, Dark Lord, Treasure Hunter, Papillon, Diva)',
        'roles': ['valkyrie', 'dark lord', 'treasure hunter', 'papillon', 'diva'],
        'opt': '100% (Meta)'
    },
    'Dual-Support': {
        'desc': 'Classic Dual-Support (Paladin, Dark Lord, Sniper, Bishop, Diva)',
        'roles': ['tank', 'dark lord', 'shooter', 'healer', 'diva'],
        'opt': '85% (Solid)'
    },
    'Mage-Heavy': {
        'desc': 'Mage-Heavy (Paladin, Witch, Sage, Bishop, Maid)',
        'roles': ['tank', 'mage', 'sage', 'healer', 'maid'],
        'opt': '65% (Caster)'
    },
    'Juggernaut': {
        'desc': 'Physical Juggernaut (Paladin, Berserker, Dark Lord, Samurai/Kunoichi, Etoile)',
        'roles': ['tank', 'attacker', 'dark lord', 'kunoichi', 'etoile'],
        'opt': '65% (Physical)'
    },
    'Anti-Meta': {
        'desc': 'Anti-Meta Experimental (Magical Princess, Mistress, Soul Summoner, Joker, Dolls)',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'joker', 'dolls'],
        'opt': '25% (Blacklist)'
    }
}


def build_party_complete(data_source, setup, role_names, cid):
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
        
    count = int(setup.settings.get('kit_count', 0) or 0)
    bag = {int(r['Item_ID']): int(round(count * float(r['Share'] or 1))) for r in setup.kit}
    for u in party:
        u.items = dict(bag)
        
    if sealbook is not None:
        summon = scenario.sealbook_summon(data_source, setup, sealbook, party)
        if summon is not None:
            summon.items = {}
            party.append(summon)
            
    return party

# Global worker state to prevent reloading data on every task
_WORKER_DATA = None
_WORKER_SETUP = None
_WORKER_VARIANT = None

def init_worker():
    global _WORKER_DATA, _WORKER_SETUP, _WORKER_VARIANT
    _WORKER_DATA = game_data()
    _WORKER_SETUP = setup_mod.load()
    _WORKER_VARIANT = balance_data(_WORKER_DATA)

def run_single_task(args):
    cid, p_name, roles, runs, seed = args
    global _WORKER_DATA, _WORKER_SETUP, _WORKER_VARIANT
    data = _WORKER_DATA
    setup = _WORKER_SETUP
    variant = _WORKER_VARIANT
    
    cp = setup.checkpoint(cid)
    
    # Vanilla simulation
    def party_factory_v():
        return build_party_complete(data, setup, roles, cid)
    def enemy_factory_v():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    res_v = scenario.play(data, setup, party_factory_v, enemy_factory_v, runs=runs, seed=seed)
    
    # Mod simulation
    def party_factory_m():
        return build_party_complete(variant, setup, roles, cid)
    def enemy_factory_m():
        return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
    res_m = scenario.play(variant, setup, party_factory_m, enemy_factory_m, runs=runs, seed=seed)

    # Process metrics
    wins_v = [r for r in res_v if r['won']]
    losses_v = [r for r in res_v if not r['won']]
    win_pct_v = len(wins_v) / len(res_v) * 100.0
    if wins_v:
        rounds_v = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins_v) / len(wins_v)
    else:
        rounds_v = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in losses_v) / max(1, len(losses_v))

    wins_m = [r for r in res_m if r['won']]
    losses_m = [r for r in res_m if not r['won']]
    win_pct_m = len(wins_m) / len(res_m) * 100.0
    if wins_m:
        rounds_m = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins_m) / len(wins_m)
    else:
        rounds_m = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in losses_m) / max(1, len(losses_m))

    return (cid, p_name, win_pct_v, rounds_v, bool(wins_v), win_pct_m, rounds_m, bool(wins_m))

def run_parallel_battery(runs=50, max_workers=10):
    start_time = time.time()
    print(f"=== Iniciando Bateria Paralela: {len(CHECKPOINTS)} Jefes x {len(PARTIES)} Parties ===")
    print(f"Muestras N = {runs} por combate | Workers en paralelo = {max_workers}\n")

    tasks = []
    for cid in CHECKPOINTS:
        for p_name, p_info in PARTIES.items():
            tasks.append((cid, p_name, p_info['roles'], runs, 42))

    results_matrix = {cid: {} for cid in CHECKPOINTS}
    
    with ProcessPoolExecutor(max_workers=max_workers, initializer=init_worker) as executor:
        for item in executor.map(run_single_task, tasks):
            cid, p_name, v_pct, v_rnd, v_won, m_pct, m_rnd, m_won = item
            results_matrix[cid][p_name] = {
                'v_pct': v_pct, 'v_rnd': v_rnd, 'v_won': v_won,
                'm_pct': m_pct, 'm_rnd': m_rnd, 'm_won': m_won
            }

    elapsed = time.time() - start_time
    print(f"\nSimulacion completada exitosamente en {elapsed:.1f} segundos.")
    return results_matrix

def generate_compact_markdown(results_matrix, runs=50):
    lines = []
    lines.append(f"# Matriz Compacta de Rendimiento: Vanilla vs Mod (N={runs} Runs)\n")
    lines.append("Cada fila representa un jefe (únicamente código). Todos los arquetipos de equipo están consolidados dentro de la misma celda con saltos de línea para lectura directa y análisis visual rápido.\n")
    lines.append("- **Formato por equipo:** `<Nombre de Party>: <Win% Vanilla> (<Rondas>r) → <Win% Mod> (<Rondas>r)`")
    lines.append("- **Si no gana:** Indica `0% (cae tras Xr)`.\n")
    lines.append("| Boss | Desempeño por Party (Vanilla → Mod) |")
    lines.append("|:---:|---|")

    for cid in CHECKPOINTS:
        party_lines = []
        for p_name in PARTIES.keys():
            res = results_matrix[cid][p_name]
            v_str = f"{res['v_pct']:.0f}% ({res['v_rnd']:.1f}r)" if res['v_won'] else f"0% (cae {res['v_rnd']:.1f}r)"
            m_str = f"**{res['m_pct']:.0f}%** ({res['m_rnd']:.1f}r)" if res['m_won'] else f"0% (cae {res['m_rnd']:.1f}r)"
            party_lines.append(f"**{p_name}:** {v_str} → {m_str}")
        cell_content = "<br>".join(party_lines)
        lines.append(f"| **{cid}** | {cell_content} |")

    return "\n".join(lines)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=50)
    parser.add_argument('--workers', type=int, default=10)
    args = parser.parse_args()

    matrix = run_parallel_battery(runs=args.runs, max_workers=args.workers)
    report_md = generate_compact_markdown(matrix, runs=args.runs)

    out_path = os.path.join(BASE_DIR, 'docs', 'generated', 'COMPACT_BOSS_BATTERY_PARALLEL.md')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report_md)

    print(f"\nReporte generado guardado en: {out_path}\n")
    print(report_md)

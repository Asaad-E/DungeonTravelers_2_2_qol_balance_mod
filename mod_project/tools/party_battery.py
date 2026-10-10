"""
Party Battery Simulation.

Tests a battery of 5 parties with different degrees of optimization (based on the GameFAQs guide)
against key boss checkpoints in both Vanilla and the Balance Variant.

Parties:
  1. Meta / Golden Party: Diva, Dark Lord, Papillon, Valkyrie, Treasure Hunter (100% Optimization)
  2. Classic Dual-Support: Bishop, Etoile, Dark Lord, Valkyrie, Sniper (85% Optimization)
  3. Mage-Heavy: Witch, Sage, Diva, Valkyrie, Dark Lord (65% Optimization)
  4. Physical Juggernaut: Samurai, Dark Lord, Valkyrie, Diva, Sniper (65% Optimization)
  5. Anti-Meta / Blacklist: Mistress, Kunoichi, Magical Princess, Soul Summoner, Valkyrie (25% Optimization)
"""
import os
import sys
import json
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import setup as setup_mod, scenario, measures
from sim.data import game_data
from sim.variant import balance_data

PARTIES = {
    'Meta (Golden)': {
        'desc': 'GameFAQs recommended: Diva (healer+maid), Dark Lord (dispel), Papillon, Valkyrie, TH',
        'opt': '100% (Meta)',
        'roles': ['diva', 'dark lord', 'papillon', 'valkyrie', 'treasure hunter', 'tank']
    },
    'Classic Dual-Support': {
        'desc': 'Dedicated Bishop (healer), Etoile (maid/dances), Dark Lord, Valkyrie, Sniper',
        'opt': '85% (Solid)',
        'roles': ['healer', 'etoile', 'dark lord', 'valkyrie', 'shooter', 'tank']
    },
    'Mage-Heavy': {
        'desc': 'Caster focus: Witch (elemental nukes), Sage (heal+dispel), Diva, Valkyrie, Dark Lord',
        'opt': '65% (Caster)',
        'roles': ['mage', 'sage', 'diva', 'valkyrie', 'dark lord', 'tank']
    },
    'Physical Juggernaut': {
        'desc': 'Pure brute physical: Samurai, Dark Lord, Valkyrie, Diva, Sniper (No mages/thieves)',
        'opt': '65% (Physical)',
        'roles': ['attacker', 'dark lord', 'valkyrie', 'diva', 'shooter', 'tank']
    },
    'Anti-Meta (Blacklist)': {
        'desc': 'Classes GameFAQs says "AVOID": Mistress (whips), Kunoichi, Magical Princess, Soul Summoner, Valkyrie',
        'opt': '25% (Blacklist)',
        'roles': ['mistress', 'kunoichi', 'magical princess', 'soul summoner', 'valkyrie', 'tank']
    }
}

CHECKPOINTS = ['C18', 'C26', 'C29', 'C34', 'C40']


def build_party(data_source, setup, role_names, cid):
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
        if rname not in setup.roles:
            continue
        role = setup.roles[rname]
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
                
    # Fallback to pool if fewer than 5 members
    for name in pool:
        if len(party) >= size:
            break
        c = chars.get(name)
        if name in taken or not c:
            continue
        for rname in role_names:
            if rname in setup.roles:
                role = setup.roles[rname]
                if scenario.class_id(data_source, role['Base class']) == c['base_class']:
                    j_lvl = scenario.level_of_exp(data_source, c['start_exp'] or 0)
                    party.append(scenario.build_role_member(data_source, setup, rname, c, max(level, j_lvl), upgrade, crown,
                                                   scenario.forge_open(setup, floor), party_enchants=party_enchants,
                                                   pieces=scenario.unique_pieces(setup, rname, chapter, floor),
                                                   sealbook=scenario.personal_sealbook(setup, rname, chapter, floor)))
                    taken.add(name)
                    break

    front = int(setup.settings.get('front_size', 3))
    if sum(u.front for u in party) > front:
        for u in reversed(party):
            if u.front and sum(x.front for x in party) > front:
                u.front = False
    return party


def run_battery(runs=15):
    data = game_data()
    setup = setup_mod.load()
    variant = balance_data(data)
    
    results = {}
    
    print(f"=== Starting Party Battery Simulation ({runs} runs per checkpoint) ===\n")
    
    for p_name, p_info in PARTIES.items():
        results[p_name] = {'opt': p_info['opt'], 'checkpoints': {}}
        print(f"--- Testing Party: {p_name} [{p_info['opt']}] ---")
        
        for cid in CHECKPOINTS:
            cp = setup.checkpoint(cid)
            level = scenario.reference_levels(data, setup)[cid][0]
            groups_vanilla = [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
            groups_variant = [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
            
            # Run Vanilla
            res_vanilla = scenario.play(data, setup, 
                                        lambda: build_party(data, setup, p_info['roles'], cid), 
                                        lambda: groups_vanilla, 
                                        runs=runs)
            s_vanilla = measures.summary(res_vanilla)
            
            # Run Variant
            res_variant = scenario.play(variant, setup, 
                                        lambda: build_party(variant, setup, p_info['roles'], cid), 
                                        lambda: groups_variant, 
                                        runs=runs)
            s_variant = measures.summary(res_variant)
            
            results[p_name]['checkpoints'][cid] = {
                'level': level,
                'vanilla': s_vanilla,
                'variant': s_variant
            }
            
            v_win = int(s_vanilla['won'] * 100)
            m_win = int(s_variant['won'] * 100)
            v_time = f"{s_vanilla['time']:.1f}" if s_vanilla['time'] is not None else "-"
            m_time = f"{s_variant['time']:.1f}" if s_variant['time'] is not None else "-"
            print(f"  {cid} (Lv{level:2d}): Vanilla {v_win:3d}% (turns {v_time})  -->  Variant {m_win:3d}% (turns {m_time})")
            
        print()
        
    return results


def print_comparison_markdown(results):
    md = []
    md.append("# Resultados de la Batería de Parties (Vanilla vs. Balance Variant)\n")
    md.append("Evaluación de 5 arquetipos de equipo con distintos grados de optimización basados en la guía de GameFAQs.\n")
    
    for cid in CHECKPOINTS:
        level = results[list(results.keys())[0]]['checkpoints'][cid]['level']
        md.append(f"\n### Checkpoint {cid} (Nivel {level})\n")
        md.append("| Party | Optimización | Victoria (Vanilla) | Turnos (Vanilla) | Victoria (Variant) | Turnos (Variant) | Δ Rendimiento |")
        md.append("|---|---|---|---|---|---|---|")
        
        for p_name, p_data in results.items():
            opt = p_data['opt']
            c_data = p_data['checkpoints'][cid]
            v = c_data['vanilla']
            m = c_data['variant']
            
            v_win = f"{int(v['won']*100)}%"
            v_time = f"{v['time']:.1f}" if v['time'] is not None else "-"
            m_win = f"{int(m['won']*100)}%"
            m_time = f"{m['time']:.1f}" if m['time'] is not None else "-"
            
            diff_win = int(m['won']*100) - int(v['won']*100)
            diff_str = f"{diff_win:+d}%" if diff_win != 0 else "="
            
            md.append(f"| **{p_name}** | {opt} | {v_win} | {v_time} | {m_win} | {m_time} | {diff_str} |")
            
    return "\n".join(md)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=15, help='Number of simulation runs per fight')
    args = parser.parse_args()
    
    res = run_battery(runs=args.runs)
    report_md = print_comparison_markdown(res)
    
    out_path = os.path.join(BASE_DIR, 'docs', 'generated', 'PARTY_BATTERY_RESULTS.md')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
        
    print(f"\nReport written to: {out_path}")

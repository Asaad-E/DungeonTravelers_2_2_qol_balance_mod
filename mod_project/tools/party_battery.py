"""
Party Battery Simulation.

Tests a battery of 5 parties with different degrees of optimization (based on the GameFAQs guide)
across 17 key boss checkpoints throughout the entire story in both Vanilla and the Balance Variant.

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

BOSS_NAMES = {
    'C06': 'Ghast',
    'C10': 'Vrachia Lord',
    'C13': 'Eros',
    'C17': 'Agent M',
    'C18': 'True King Eltricia',
    'C19': 'Siesta',
    'C21': 'Trafficker Twinny',
    'C24': 'Afanc',
    'C26': 'Michelle & Beatrice',
    'C28': 'Spirit of Mag Mell',
    'C29': 'Calliope (Heal Wall)',
    'C30': 'Heartless Avenger',
    'C32': 'Moby Dick',
    'C34': 'Queen of Darkness',
    'C36': 'Demon God Fried',
    'C38': 'Samael',
    'C40': 'Demiurge & Atialuco (Final)'
}

CHECKPOINTS = list(BOSS_NAMES.keys())


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


def run_battery(runs=12):
    data = game_data()
    setup = setup_mod.load()
    variant = balance_data(data)
    
    results = {}
    
    print(f"=== Starting Expanded Party Battery Simulation ({runs} runs across {len(CHECKPOINTS)} bosses) ===\n")
    
    for p_name, p_info in PARTIES.items():
        results[p_name] = {'opt': p_info['opt'], 'checkpoints': {}}
        print(f"--- Testing Party: {p_name} [{p_info['opt']}] ---")
        
        for cid in CHECKPOINTS:
            bname = BOSS_NAMES[cid]
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
                'boss': bname,
                'level': level,
                'vanilla': s_vanilla,
                'variant': s_variant
            }
            
            v_win = int(s_vanilla['won'] * 100)
            m_win = int(s_variant['won'] * 100)
            print(f"  {cid:3s} ({bname:25s} Lv{level:2d}): Vanilla {v_win:3d}%  -->  Variant {m_win:3d}%")
            
        print()
        
    return results


def print_comparison_markdown(results):
    md = []
    md.append("# Resultados Expandidos de la Batería de Parties (17 Jefes de Historia)\n")
    md.append("Evaluación de 5 arquetipos de equipo a lo largo de toda la campaña (Vanilla vs. Balance Variant).\n")
    
    # 1. Summary Matrix: Win rate by boss
    md.append("## Matriz General: Tasa de Victoria por Jefe (Vanilla → Mod)\n")
    md.append("| Checkpoint | Jefe | Nivel | Meta (100%) | Dual-Support (85%) | Mage-Heavy (65%) | Juggernaut (65%) | Anti-Meta (25%) |")
    md.append("|---|---|---|---|---|---|---|---|")
    
    for cid in CHECKPOINTS:
        bname = BOSS_NAMES[cid]
        level = results[list(results.keys())[0]]['checkpoints'][cid]['level']
        
        cells = []
        for p_name in PARTIES.keys():
            c_data = results[p_name]['checkpoints'][cid]
            v_win = int(c_data['vanilla']['won'] * 100)
            m_win = int(c_data['variant']['won'] * 100)
            cells.append(f"{v_win}% → **{m_win}%**")
            
        md.append(f"| **{cid}** | {bname} | {level} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {cells[4]} |")
        
    return "\n".join(md)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=12, help='Number of simulation runs per fight')
    args = parser.parse_args()
    
    res = run_battery(runs=args.runs)
    report_md = print_comparison_markdown(res)
    
    out_path = os.path.join(BASE_DIR, 'docs', 'generated', 'PARTY_BATTERY_EXPANDED.md')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
        
    print(f"\nReport written to: {out_path}")

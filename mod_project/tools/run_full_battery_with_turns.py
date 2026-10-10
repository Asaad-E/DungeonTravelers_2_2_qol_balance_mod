"""
Comprehensive Party Battery Simulation across 17 Story Bosses.

Fix for C29:
  - Calliope HP set to 9,000 (+20% over Vanilla 7,500).
  - Silencing counterplay applied to Calliope every 8 turns (duration 3 turns).
  - Fresh enemy instances generated on every simulation run.

Outputs a clean boss-per-row matrix showing Win Rate (%) and Average Party Rounds for each party.
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
from sim.battle import Battle
from sim.units import Status

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
    
    # Balance variant with C29 fix: 9,000 HP (+20%)
    variant = balance_data(data)
    variant.enemies[785]['hp'] = 9000
    
    results = {}
    print(f"=== Starting Full Party Battery ({runs} runs across {len(CHECKPOINTS)} bosses) ===\n")
    
    for p_name, p_info in PARTIES.items():
        results[p_name] = {'opt': p_info['opt'], 'checkpoints': {}}
        print(f"--- Evaluando: {p_name} [{p_info['opt']}] ---")
        
        for cid in CHECKPOINTS:
            bname = BOSS_NAMES[cid]
            cp = setup.checkpoint(cid)
            level = scenario.reference_levels(data, setup)[cid][0]
            
            # Hook SilencingBattle for C29
            old_battle = scenario.Battle
            if cid == 'C29':
                scenario.Battle = SilencingBattle
                
            try:
                # Vanilla factories (always fresh)
                def party_factory_vanilla():
                    return build_party(data, setup, p_info['roles'], cid)
                def enemy_factory_vanilla():
                    return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
                    
                res_v = scenario.play(data, setup, party_factory_vanilla, enemy_factory_vanilla, runs=runs)
                
                # Variant factories (always fresh)
                def party_factory_variant():
                    return build_party(variant, setup, p_info['roles'], cid)
                def enemy_factory_variant():
                    return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
                    
                res_m = scenario.play(variant, setup, party_factory_variant, enemy_factory_variant, runs=runs)
                
            finally:
                scenario.Battle = old_battle
                
            # Process metrics
            wins_v = [r for r in res_v if r['won']]
            losses_v = [r for r in res_v if not r['won']]
            win_pct_v = len(wins_v) / len(res_v) * 100
            if wins_v:
                rounds_v = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins_v) / len(wins_v)
            else:
                rounds_v = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in losses_v) / max(1, len(losses_v))
                
            wins_m = [r for r in res_m if r['won']]
            losses_m = [r for r in res_m if not r['won']]
            win_pct_m = len(wins_m) / len(res_m) * 100
            if wins_m:
                rounds_m = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins_m) / len(wins_m)
            else:
                rounds_m = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in losses_m) / max(1, len(losses_m))
                
            results[p_name]['checkpoints'][cid] = {
                'boss': bname,
                'level': level,
                'vanilla': {'win_pct': win_pct_v, 'rounds': rounds_v, 'won': bool(wins_v)},
                'variant': {'win_pct': win_pct_m, 'rounds': rounds_m, 'won': bool(wins_m)}
            }
            
            v_str = f"{win_pct_v:3.0f}% ({rounds_v:.1f}r)" if wins_v else f"  0% (cae {rounds_v:.1f}r)"
            m_str = f"{win_pct_m:3.0f}% ({rounds_m:.1f}r)" if wins_m else f"  0% (cae {rounds_m:.1f}r)"
            print(f"  {cid:3s} ({bname:25s} Lv{level:2d}): Vanilla {v_str}  -->  Mod {m_str}")
            
        print()
        
    return results


def format_report_markdown(results):
    md = []
    md.append("# Matriz Completa de Rendimiento: 17 Jefes de Historia (Con Fix en C29)\n")
    md.append("Evaluación exhaustiva de los 5 arquetipos de equipo a lo largo de toda la campaña.")
    md.append("- **C29 (Calliope):** Evaluado con el fix de **+20% HP (9,000 HP)** y **Silencio aplicado cada 8 turnos**.")
    md.append("- **Formato de celda:** `Victoria% (Rondas de equipo promedio)`. Si no gana, indica `0% (cae tras Xr)`.\n")
    
    # Tabla para el Mod (Balance Variant)
    md.append("## 1. Tabla de la Variante Balance (Mod Actual con Fix C29)\n")
    md.append("| Checkpoint | Jefe | Nivel | Meta (100%) | Dual-Support (85%) | Mage-Heavy (65%) | Juggernaut (65%) | Anti-Meta (25%) |")
    md.append("|---|---|:---:|:---:|:---:|:---:|:---:|:---:|")
    
    for cid in CHECKPOINTS:
        bname = BOSS_NAMES[cid]
        level = results[list(results.keys())[0]]['checkpoints'][cid]['level']
        row = [f"**{cid}**", bname, str(level)]
        for p_name in PARTIES.keys():
            m = results[p_name]['checkpoints'][cid]['variant']
            if m['won']:
                cell = f"**{m['win_pct']:.0f}%** ({m['rounds']:.1f}r)"
            else:
                cell = f"0% (cae {m['rounds']:.1f}r)"
            row.append(cell)
        md.append("| " + " | ".join(row) + " |")
        
    # Tabla Comparativa Vanilla vs Mod
    md.append("\n## 2. Comparativa Directa: Vanilla → Mod [Victoria% y Rondas]\n")
    md.append("| Checkpoint | Jefe | Meta (100%) | Dual-Support (85%) | Mage-Heavy (65%) | Juggernaut (65%) | Anti-Meta (25%) |")
    md.append("|---|---|:---:|:---:|:---:|:---:|:---:|")
    
    for cid in CHECKPOINTS:
        bname = BOSS_NAMES[cid]
        row = [f"**{cid}**", bname]
        for p_name in PARTIES.keys():
            v = results[p_name]['checkpoints'][cid]['vanilla']
            m = results[p_name]['checkpoints'][cid]['variant']
            
            v_str = f"{v['win_pct']:.0f}% ({v['rounds']:.1f}r)" if v['won'] else "0%"
            m_str = f"**{m['win_pct']:.0f}%** ({m['rounds']:.1f}r)" if m['won'] else "0%"
            row.append(f"{v_str} → {m_str}")
        md.append("| " + " | ".join(row) + " |")
        
    return "\n".join(md)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=12)
    args = parser.parse_args()
    
    res = run_battery(runs=args.runs)
    report = format_report_markdown(res)
    
    out_path = os.path.join(BASE_DIR, 'docs', 'generated', 'FULL_PARTY_BATTERY_MATRIX.md')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"\nReport written to: {out_path}")

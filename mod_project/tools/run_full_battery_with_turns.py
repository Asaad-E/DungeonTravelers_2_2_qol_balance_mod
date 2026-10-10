"""
Full Party Battery Matrix Simulation (Clean & Complete).

All 17 Story Bosses across all 5 Parties.
Includes:
  - Full gear, unique pieces, personal sealbooks, Grand Sealbook enchants, shared item bag (Kit).
  - Grand Sealbook summon (Eros, etc.).
  - Fresh enemy instances on every run.
  - C29 Calliope fix: 9,000 HP (+20%) and Silence applied every 8 turns.
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


def run_battery(runs=12, no_boss_hp_buffs=False):
    data = game_data()
    setup = setup_mod.load()
    
    variant = balance_data(data)
    if no_boss_hp_buffs:
        for eid in data.enemies:
            if eid in variant.enemies:
                variant.enemies[eid]['hp'] = data.enemies[eid]['hp']
        print(">>> Aumentos de vida en jefes DESACTIVADOS (HP de jefes al 100% Vanilla) <<<")
    else:
        # Balance variant with C29 fix: 9,000 HP (+20%)
        variant.enemies[785]['hp'] = 9000
    
    results = {}
    print(f"=== Starting Complete Party Battery ({runs} runs across {len(CHECKPOINTS)} bosses) ===\n")
    
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
                def party_factory_vanilla():
                    return build_party_complete(data, setup, p_info['roles'], cid)
                def enemy_factory_vanilla():
                    return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
                res_v = scenario.play(data, setup, party_factory_vanilla, enemy_factory_vanilla, runs=runs)
                
                def party_factory_variant():
                    return build_party_complete(variant, setup, p_info['roles'], cid)
                def enemy_factory_variant():
                    return [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
                res_m = scenario.play(variant, setup, party_factory_variant, enemy_factory_variant, runs=runs)
                
            finally:
                scenario.Battle = old_battle
                
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


def format_report_markdown(results, no_boss_hp_buffs=False):
    md = []
    if no_boss_hp_buffs:
        md.append("# Matriz de Simulación: 17 Jefes de Historia SIN Aumento de HP en Jefes\n")
        md.append("Evaluación con equipamiento completo, bolsa de objetos de la tienda, sellos personales, gran sello e invocación.\n")
        md.append("- **Jefes:** HP al 100% Vanilla (sin aumentos de vida del mod).")
        md.append("- **C29 (Calliope):** HP Vanilla (7,500 HP) con **Silencio cada 8 turnos**.")
        md.append("- **Héroes / Clases:** Todas las mejoras y rebalances del Mod activos.")
    else:
        md.append("# Matriz Completa y Rigurosa: 17 Jefes de Historia (Con Gear Completo, Kit y Summon)\n")
        md.append("Evaluación con equipamiento completo, bolsa de objetos de la tienda, sellos personales, gran sello e invocación.\n")
        md.append("- **C29 (Calliope):** Evaluado con **+20% HP (9,000 HP)** y **Silencio cada 8 turnos**.")
    md.append("- **Formato de celda:** `Victoria% (Rondas promedio)`. Si no gana, indica `0% (cae tras Xr)`.\n")
    
    # 1. Tabla para el Mod (Balance Variant)
    title_suffix = " (Sin Aumentos de HP en Jefes)" if no_boss_hp_buffs else " (Mod Actual con Fix C29)"
    md.append(f"## 1. Tabla de la Variante Balance{title_suffix}\n")
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
        
    # 2. Comparativa Directa
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
    parser.add_argument('--no-boss-hp-buffs', action='store_true', help='Revert all enemy HP increases to Vanilla HP')
    args = parser.parse_args()
    
    res = run_battery(runs=args.runs, no_boss_hp_buffs=args.no_boss_hp_buffs)
    report = format_report_markdown(res, no_boss_hp_buffs=args.no_boss_hp_buffs)
    
    filename = 'FULL_PARTY_BATTERY_NO_BOSS_HP_BUFFS.md' if args.no_boss_hp_buffs else 'FULL_PARTY_BATTERY_MATRIX.md'
    out_path = os.path.join(BASE_DIR, 'docs', 'generated', filename)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"\nReport written to: {out_path}")

import os
import sys
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import scenario
from sim import setup as setup_mod
from sim.data import game_data
from sim.variant import balance_data

d = game_data()
bd = balance_data(d)
s = setup_mod.load()

# 16 classes: 5 Tier 1 + 11 Tier 2
TIER1 = [
    (0, 'Fighter', 'tank'),
    (6, 'Scout', 'shooter'),
    (12, 'Magic User', 'mage'),
    (20, 'Maid', 'diva'),
    (26, 'Spieler', 'dolls')
]

TIER2 = [
    (1, 'Paladin', 'tank'),
    (2, 'Berserker', 'attacker'),
    (7, 'Archer', 'shooter'),
    (8, 'Assassin', 'kunoichi'),
    (13, 'Sorceress', 'mage'),
    (14, 'Enchantress', 'sage'),
    (15, 'Priestess', 'healer'),
    (21, 'Bard', 'diva'),
    (22, 'Dancer', 'etoile'),
    (27, 'Doll Master', 'dolls'),
    (28, 'Trickster', 'joker')
]

# Checkpoints
TIER1_CPS = ['C03', 'C06']
TIER2_CPS = ['C10', 'C13', 'C17']

def run_simulation(data_source, role, cid, runs=10):
    cp = s.checkpoint(cid)
    ref_levels = scenario.reference_levels(data_source, s)
    level = ref_levels[cid][0]
    gear = scenario.checkpoint_gear(data_source, s, cid)
    numbers = scenario.battle_numbers(cp)
    
    rdata = s.roles[role]
    
    chars = {c['name']: c for c in data_source.characters}
    def party():
        whole = scenario.reference_party(data_source, s, cp['Chapter'], level, gear, int(cp['Crown bonus'] or 0), cp['Floor'])
        members = [u for u in whole if u.kind == 'member']
        others = [u for u in whole if u.kind != 'member']
        kept = members[:-1]
        names = [n.strip() for n in str(rdata['Characters (order of preference)']).split(';')]
        taken = {u.name for u in kept}
        base = scenario.class_id(data_source, rdata['Base class'])
        who = next((n for n in names if n in chars and n not in taken), None) or \
              next(c['name'] for c in data_source.characters if c['name'] not in taken and c['base_class'] == base)
        tested = scenario.build_role_member(data_source, s, role, chars[who], level, gear, int(cp['Crown bonus'] or 0),
                                            scenario.forge_open(s, cp['Floor']))
        if kept:
            tested.items = kept[0].items
        return kept + [tested] + others
        
    def enemies():
        return [scenario.fixed_battle(data_source, cp['Floor'], n) for n in numbers]
        
    results = scenario.play(data_source, s, party, enemies, runs=runs)
    wins = sum(r['won'] for r in results)
    turns = sum(r.get('actions', 0) for r in results if r['won']) / max(1, wins)
    hp_left = sum(r.get('hp_left', 0) for r in results if r['won']) / max(1, wins) * 100
    
    p_sample = party()
    test_u = next((u for u in p_sample if getattr(u, 'role', None) == role), p_sample[-1])
    class_name = data_source.class_names.get(test_u.class_id, str(test_u.class_id))
    
    return {
        'class_name': class_name,
        'level': level,
        'win_pct': wins / runs * 100,
        'wins': wins,
        'runs': runs,
        'actions': turns,
        'hp_left': hp_left
    }

def collect_skills(data_source, cid):
    cname = data_source.class_names[cid]
    skills = [sk for sk in data_source.skills.values() if cid in sk.classes]
    res = []
    for sk in sorted(skills, key=lambda x: (x.category, x.id)):
        res.append({
            'id': sk.id,
            'name': sk.name,
            'category': sk.category,
            'levels': sk.levels,
            'tp': sk.tp,
            'sp': sk.sp,
            'weapons': sk.weapons
        })
    return res

audit_data = {'tier1': {}, 'tier2': {}}

print("=== Running Tier 1 Audit (C03, C06) ===")
for class_id, cname, role in TIER1:
    audit_data['tier1'][cname] = {
        'class_id': class_id,
        'role': role,
        'skills': collect_skills(bd, class_id),
        'checkpoints': {}
    }
    for cid in TIER1_CPS:
        v_res = run_simulation(d, role, cid, runs=10)
        m_res = run_simulation(bd, role, cid, runs=10)
        audit_data['tier1'][cname]['checkpoints'][cid] = {
            'vanilla': v_res,
            'mod': m_res
        }
        print(f"Tier 1: {cname:12s} at {cid} | Van: {v_res['win_pct']:5.1f}% ({v_res['actions']:5.1f} acts) | Mod: {m_res['win_pct']:5.1f}% ({m_res['actions']:5.1f} acts)")

print("\n=== Running Tier 2 Audit (C10, C13, C17) ===")
for class_id, cname, role in TIER2:
    audit_data['tier2'][cname] = {
        'class_id': class_id,
        'role': role,
        'skills': collect_skills(bd, class_id),
        'checkpoints': {}
    }
    for cid in TIER2_CPS:
        v_res = run_simulation(d, role, cid, runs=10)
        m_res = run_simulation(bd, role, cid, runs=10)
        audit_data['tier2'][cname]['checkpoints'][cid] = {
            'vanilla': v_res,
            'mod': m_res
        }
        print(f"Tier 2: {cname:12s} at {cid} | Van: {v_res['win_pct']:5.1f}% ({v_res['actions']:5.1f} acts) | Mod: {m_res['win_pct']:5.1f}% ({m_res['actions']:5.1f} acts)")

output_path = os.path.join(BASE_DIR, 'scratch', 'tier1_tier2_audit_results.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(audit_data, f, indent=2)

print(f"\nAudit completed! Saved to {output_path}")

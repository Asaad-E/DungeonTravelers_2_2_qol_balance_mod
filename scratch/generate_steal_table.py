import sys
import os
import struct

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.abspath('mod_project/tools'))

from enemy_data import enemies
from pck_handler import PckArchive

# 1. Load equipment names
eq_pck = PckArchive('mod_project/backups/EquipmentData.pck')
eq_names = {}
for fn, data in eq_pck.files:
    eq_id = struct.unpack_from('<i', data, 0)[0]
    name_ptr = struct.unpack_from('<Q', data, 8)[0]
    name = data[name_ptr:].split(b'\x00')[0].decode('utf-8', 'replace')
    eq_names[eq_id] = name

# 2. Load item names
item_pck = PckArchive('mod_project/backups/ItemData.pck')
item_names = {}
for fn, data in item_pck.files:
    item_id = struct.unpack_from('<i', data, 0)[0]
    name_ptr = struct.unpack_from('<Q', data, 8)[0]
    name = data[name_ptr:].split(b'\x00')[0].decode('utf-8', 'replace')
    item_names[item_id] = name

all_e = enemies('mod_project/backups/Enemy/Enemy.pck')
print(f"Loaded {len(all_e)} enemies.")

stealable_enemies = []
for e in all_e:
    flg = e['flags']
    can_steal = bool((flg >> 15) & 1)
    if not can_steal:
        continue
    
    raw = e['raw_68']
    eid = e['id']
    name = e['name']
    lvl = e['level']
    
    # Regular items
    items = []
    item_cnt = raw[0]
    for i in range(item_cnt):
        iid = raw[1 + i*2]
        prob = raw[2 + i*2]
        if prob > 0:
            items.append((iid, prob))
            
    # Equipment
    eq_prob = raw[5]
    eq_slots = raw[6]
    slots = []
    if eq_prob > 0 and eq_slots > 0:
        for s in range(eq_slots):
            off = 7 + s * 3
            flag = raw[off]
            val = raw[off+1]
            wt = raw[off+2]
            if wt > 0:
                slots.append((flag, val, wt))
                
    # Stage 1 weights
    w_items = [prob for iid, prob in items]
    w_eq = eq_prob if (eq_prob > 0 and len(slots) > 0) else 0
    stage1_steal_sum = sum(w_items) + w_eq
    stage1_drop_sum = max(100, sum(w_items) + w_eq)
    
    if stage1_steal_sum == 0:
        continue
        
    candidates = []
    # Items
    for iid, prob in items:
        p_steal = prob / stage1_steal_sum
        p_drop = prob / stage1_drop_sum
        iname = item_names.get(iid, f"Item {iid}")
        candidates.append({
            'type': 'item',
            'id': iid,
            'name': iname,
            'p_steal': p_steal,
            'p_drop': p_drop
        })
        
    # Equipment slots
    if w_eq > 0 and len(slots) > 0:
        sum_slot_wt = sum(wt for flag, val, wt in slots)
        for flag, val, wt in slots:
            slot_share = wt / sum_slot_wt
            p_steal = (w_eq / stage1_steal_sum) * slot_share
            p_drop = (w_eq / stage1_drop_sum) * slot_share
            if flag == 0:
                ename = eq_names.get(val, f"Equip {val}")
                candidates.append({
                    'type': 'fixed_equip',
                    'id': val,
                    'name': ename,
                    'p_steal': p_steal,
                    'p_drop': p_drop
                })
            else:
                candidates.append({
                    'type': 'zone_equip',
                    'id': val,
                    'name': f"Zone Table Kind {val}",
                    'p_steal': p_steal,
                    'p_drop': p_drop
                })
                
    stealable_enemies.append({
        'id': eid,
        'name': name,
        'level': lvl,
        'candidates': candidates
    })

print(f"Total enemies with something to steal: {len(stealable_enemies)}")

# Find items/equipment that can ONLY be obtained by stealing
steal_only = []
for se in stealable_enemies:
    for c in se['candidates']:
        if c['p_drop'] == 0:
            steal_only.append((se['id'], se['name'], c))

print(f"Candidates with p_drop == 0: {len(steal_only)}")

# Flatten all candidates to find the 30 with lowest p_steal
flat_candidates = []
for se in stealable_enemies:
    for c in se['candidates']:
        flat_candidates.append({
            'enemy_id': se['id'],
            'enemy_name': se['name'],
            'enemy_lvl': se['level'],
            'cand_type': c['type'],
            'cand_id': c['id'],
            'cand_name': c['name'],
            'p_steal': c['p_steal'],
            'p_drop': c['p_drop'],
            'ratio': c['p_steal'] / c['p_drop'] if c['p_drop'] > 0 else 999.0
        })

# Sort by p_steal ascending
flat_candidates.sort(key=lambda x: (x['p_steal'], x['enemy_id']))

print("\n--- Bottom 30 Candidates by p_steal ---")
for fc in flat_candidates[:30]:
    print(f"Enemy {fc['enemy_id']:3d} ({fc['enemy_name']:20s} Lv{fc['enemy_lvl']:2d}): {fc['cand_name']:25s} [{fc['cand_type']:11s}] steal={fc['p_steal']*100:6.3f}%, drop={fc['p_drop']*100:6.3f}%")

# Very Powerful Enemies (504-632 and 972-989)
vpe_enemies = [e for e in all_e if (504 <= e['id'] <= 632) or (972 <= e['id'] <= 989)]
print(f"\nTotal VPEs in range: {len(vpe_enemies)}")
vpe_data = []
for e in vpe_enemies:
    flg = e['flags']
    can_steal = bool((flg >> 15) & 1)
    se = next((x for x in stealable_enemies if x['id'] == e['id']), None)
    vpe_data.append({
        'id': e['id'],
        'name': e['name'],
        'level': e['level'],
        'can_steal': can_steal,
        'candidates': se['candidates'] if se else []
    })

print(f"VPEs that can be stolen from: {sum(1 for v in vpe_data if v['can_steal'])}")
print(f"VPEs that CANNOT be stolen from: {sum(1 for v in vpe_data if not v['can_steal'])}")

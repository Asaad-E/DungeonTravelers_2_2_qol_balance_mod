import sys
import os
import struct

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.abspath('mod_project/tools'))

from enemy_data import enemies
from pck_handler import PckArchive

eq_pck = PckArchive('mod_project/backups/EquipmentData.pck')
eq_names = {}
for fn, data in eq_pck.files:
    eq_id = struct.unpack_from('<i', data, 0)[0]
    name_ptr = struct.unpack_from('<Q', data, 8)[0]
    eq_names[eq_id] = data[name_ptr:].split(b'\x00')[0].decode('utf-8', 'replace')

item_pck = PckArchive('mod_project/backups/ItemData.pck')
item_names = {}
for fn, data in item_pck.files:
    item_id = struct.unpack_from('<i', data, 0)[0]
    name_ptr = struct.unpack_from('<Q', data, 8)[0]
    item_names[item_id] = data[name_ptr:].split(b'\x00')[0].decode('utf-8', 'replace')

all_e = enemies('mod_project/backups/Enemy/Enemy.pck')

vpe_enemies = [e for e in all_e if (504 <= e['id'] <= 632) or (972 <= e['id'] <= 989)]

with open('mod_project/scratch/vpe_steal_report.txt', 'w', encoding='utf-8') as f:
    for e in vpe_enemies:
        flg = e['flags']
        can_steal = bool((flg >> 15) & 1)
        eid = e['id']
        name = e['name']
        lvl = e['level']
        raw = e['raw_68']
        
        f.write(f"ID {eid:3d} | {name:22s} | Lv{lvl:2d} | can_steal: {can_steal}\n")
        if not can_steal:
            f.write("   -> CANNOT BE STOLEN FROM (EnemyStatusData 0x3C bit 15 = 0)\n")
            continue
            
        items = []
        for i in range(raw[0]):
            iid, prob = raw[1 + i*2], raw[2 + i*2]
            if prob > 0:
                items.append((iid, prob))
        eq_prob = raw[5]
        eq_slots = raw[6]
        slots = []
        if eq_prob > 0 and eq_slots > 0:
            for s in range(eq_slots):
                off = 7 + s * 3
                flag, val, wt = raw[off], raw[off+1], raw[off+2]
                if wt > 0:
                    slots.append((flag, val, wt))
                    
        w_items = [prob for iid, prob in items]
        w_eq = eq_prob if (eq_prob > 0 and len(slots) > 0) else 0
        s1_steal = sum(w_items) + w_eq
        s1_drop = max(100, sum(w_items) + w_eq)
        
        for iid, prob in items:
            p_s = prob / s1_steal
            p_d = prob / s1_drop
            iname = item_names.get(iid, f"Item {iid}")
            f.write(f"   Item: {iname:20s} (ID {iid:3d}) | Steal: {p_s*100:5.2f}% | Drop: {p_d*100:5.2f}%\n")
            
        if w_eq > 0 and len(slots) > 0:
            sum_s = sum(wt for flag, val, wt in slots)
            for flag, val, wt in slots:
                p_s = (w_eq / s1_steal) * (wt / sum_s)
                p_d = (w_eq / s1_drop) * (wt / sum_s)
                if flag == 0:
                    ename = eq_names.get(val, f"Equip {val}")
                    f.write(f"   Equip (Fixed): {ename:15s} (ID {val:3d}) | Steal: {p_s*100:5.2f}% | Drop: {p_d*100:5.2f}%\n")
                else:
                    f.write(f"   Equip (Zone Kind {val}): Table Kind {val}   | Steal: {p_s*100:5.2f}% | Drop: {p_d*100:5.2f}%\n")

print("Generated VPE report at mod_project/scratch/vpe_steal_report.txt")

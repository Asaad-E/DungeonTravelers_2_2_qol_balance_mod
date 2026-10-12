import struct, sys
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/vanilla_source_of_truth.xlsx', data_only=True)
ws = wb['Skills']
skill_info = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    s_id = row[2]
    if s_id is not None:
        skill_info[s_id] = {
            'cat': row[0],
            'fn': row[1],
            'name': row[3],
            'levels': row[4],
            'desc': row[17],
            'lvup': row[18],
        }

pck = PckArchive('mod_project/backups/MagicSkillData.pck')

acc_up_spells = []
for fn, b in pck.files:
    spell_id = struct.unpack_from('<I', b, 0)[0]
    info = skill_info.get(spell_id, {})
    name = info.get('name', f'Spell {spell_id}')
    lvup = str(info.get('lvup', ''))
    desc = str(info.get('desc', ''))
    accs = [round(struct.unpack_from('<f', b, 0xFC + 4*k)[0], 4) for k in range(10)]
    max_lv = info.get('levels', 10) or 10
    accs_active = accs[:max_lv]
    
    if 'Accuracy UP' in lvup or 'Accuracy UP' in desc or 'accuracy UP' in lvup or 'Accuracy' in lvup:
        acc_up_spells.append((spell_id, name, desc, lvup, accs_active, accs))

print(f"Total spells with Accuracy in lvup/desc: {len(acc_up_spells)}")
constant_spells = []
scaling_spells = []
for s_id, name, desc, lvup, accs_act, accs in acc_up_spells:
    if len(set(accs_act)) == 1:
        constant_spells.append((s_id, name, desc, lvup, accs_act, accs))
    else:
        scaling_spells.append((s_id, name, desc, lvup, accs_act, accs))

print(f"Scaling spells: {len(scaling_spells)}")
print(f"Constant (non-scaling) spells: {len(constant_spells)}")
for s_id, name, desc, lvup, accs_act, accs in constant_spells:
    print(f"\nID {s_id}: {name}")
    print(f"  LvUp: {lvup}")
    print(f"  Active Accs: {accs_act}")
    print(f"  All 10 Accs: {accs}")

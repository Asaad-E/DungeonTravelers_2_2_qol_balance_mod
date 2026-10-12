import struct, sys
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
import openpyxl

pck = PckArchive('mod_project/backups/MagicSkillData.pck')

print(f"Total MagicSkillData files: {len(pck.files)}")

non_scaling_acc_up = []
all_acc_up = []

for fn, b in pck.files:
    spell_id = struct.unpack_from('<I', b, 0)[0]
    name_off = struct.unpack_from('<I', b, 8)[0]
    name = b[name_off:b.find(b'\x00', name_off)].decode('latin-1')
    desc_off = struct.unpack_from('<I', b, 16)[0]
    desc = b[desc_off:b.find(b'\x00', desc_off)].decode('latin-1')
    
    # 10 floats at 0xFC:
    accs = [round(struct.unpack_from('<f', b, 0xFC + 4*k)[0], 4) for k in range(10)]
    max_lv = struct.unpack_from('<I', b, 0x18)[0] # or check where max_level is
    
    # Check if text says "Accuracy UP" or similar
    if 'Accuracy UP' in desc or 'accuracy UP' in desc or 'Accuracy' in desc:
        all_acc_up.append((spell_id, name, desc, accs))
        # check if it scales
        if len(set(accs)) == 1:
            non_scaling_acc_up.append((spell_id, name, desc, accs))

print(f"Total spells with Accuracy in text: {len(all_acc_up)}")
print(f"Non-scaling: {len(non_scaling_acc_up)}")
for s_id, name, desc, accs in non_scaling_acc_up:
    print(f"\nID {s_id}: {name}")
    print(f"  Desc: {desc}")
    print(f"  Accs: {accs}")

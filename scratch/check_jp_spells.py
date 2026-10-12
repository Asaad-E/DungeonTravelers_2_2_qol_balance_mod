import struct, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

pck = PckArchive('mod_project/backups/MagicSkillData.pck')

jp_acc_up = []
for fn, b in pck.files:
    spell_id = struct.unpack_from('<I', b, 0)[0]
    name_off = struct.unpack_from('<I', b, 8)[0]
    name = b[name_off:b.find(b'\x00', name_off)].decode('cp932', errors='replace')
    desc_off = struct.unpack_from('<I', b, 16)[0]
    desc = b[desc_off:b.find(b'\x00', desc_off)].decode('cp932', errors='replace')
    accs = [round(struct.unpack_from('<f', b, 0xFC + 4*k)[0], 4) for k in range(10)]
    # In Japanese, Accuracy UP is "命中率UP" or "命中UP"
    if '命中' in desc:
        jp_acc_up.append((spell_id, name, desc, accs))

print(f"Total spells with '命中' in JP desc: {len(jp_acc_up)}")
scaling = [x for x in jp_acc_up if len(set(x[3])) > 1]
constant = [x for x in jp_acc_up if len(set(x[3])) == 1]
print(f"Scaling: {len(scaling)}, Constant: {len(constant)}")
for s in constant:
    print(s[0], s[1], s[3], repr(s[2]))

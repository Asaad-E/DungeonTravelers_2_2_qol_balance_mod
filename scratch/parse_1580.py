import struct, sys
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

pck = PckArchive('mod_project/backups/EnemyAttackData.pck')
for fn, b in pck.files:
    if '1580' in fn:
        name_off = struct.unpack_from('<I', b, 8)[0]
        name = b[name_off:b.find(b'\x00', name_off)].decode('latin-1')
        desc_off = struct.unpack_from('<I', b, 16)[0]
        desc = b[desc_off:b.find(b'\x00', desc_off)].decode('latin-1')
        target_code = struct.unpack_from('<i', b, 0x2C)[0]
        attr = struct.unpack_from('<i', b, 0x30)[0]
        chant_speed = struct.unpack_from('<f', b, 0x34)[0]
        acc = struct.unpack_from('<f', b, 0x38)[0]
        power = struct.unpack_from('<f', b, 0x3C)[0]
        turns = struct.unpack_from('<f', b, 0x40)[0]
        attack_speed = struct.unpack_from('<f', b, 0x44)[0]
        print(f"ID 1580: {name}")
        print(f"Target code: {target_code}")
        print(f"Attribute: {attr}")
        print(f"Chant speed: {chant_speed}")
        print(f"Accuracy: {acc}")
        print(f"Power: {power}")
        print(f"Turns: {turns}")
        print(f"Attack speed: {attack_speed}")
        # effects at 0x4C
        for k in range(5):
            e_id = struct.unpack_from('<i', b, 0x4C + 12*k)[0]
            val = struct.unpack_from('<f', b, 0x50 + 12*k)[0]
            kind = struct.unpack_from('<i', b, 0x54 + 12*k)[0]
            print(f"Slot {k}: effect={e_id}, value={val}, kind={kind}")

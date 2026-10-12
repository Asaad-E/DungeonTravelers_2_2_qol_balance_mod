import struct, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

pck = PckArchive('mod_project/backups/EnemyAttackData.pck')
for fn, b in pck.files:
    if '1580' in fn:
        name_off = struct.unpack_from('<I', b, 8)[0]
        name = b[name_off:b.find(b'\x00', name_off)].decode('latin-1')
        desc_off = struct.unpack_from('<I', b, 16)[0]
        desc = b[desc_off:b.find(b'\x00', desc_off)].decode('latin-1')
        print(f"Name: {name}")
        print(f"Desc: {desc}")
        print("Raw dwords:")
        for off in range(0, min(len(b), 0x80), 16):
            dws = [hex(struct.unpack_from('<I', b, off+4*k)[0]) for k in range(min(4, (len(b)-off)//4))]
            print(f"  {hex(off)}: {dws}")
        for off in range(0x20, len(b), 8):
            i, f = struct.unpack_from('<if', b, off)
            if i != 0 or f != 0:
                print(f"  off {hex(off)}: int={i}, float={f}")

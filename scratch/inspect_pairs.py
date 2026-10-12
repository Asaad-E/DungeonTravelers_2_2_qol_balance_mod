import struct, sys
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
pck = PckArchive('mod_project/backups/ItemData.pck')
for fn, b in pck.files:
    item_id = struct.unpack_from('<I', b, 0)[0]
    name_off = struct.unpack_from('<I', b, 8)[0]
    name = b[name_off:b.find(b'\x00', name_off)].decode('latin-1')
    p1 = struct.unpack_from('<i', b, 0x24)[0]
    p2 = struct.unpack_from('<i', b, 0x2c)[0]
    p3 = struct.unpack_from('<i', b, 0x34)[0]
    p4 = struct.unpack_from('<i', b, 0x3c)[0]
    if p1 == -1 and p2 == -1 and (p3 != -1 or p4 != -1):
        pairs = [(struct.unpack_from('<i', b, 0x24+8*k)[0], struct.unpack_from('<f', b, 0x28+8*k)[0]) for k in range(4)]
        print(f'{item_id}: {name} -> pairs: {pairs}')

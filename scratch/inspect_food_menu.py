import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

fmd_pck = PckArchive('mod_project/backups/FoodMenuData.pck')
print(f"FoodMenuData count: {len(fmd_pck.files)}")

for i in range(min(5, len(fmd_pck.files))):
    fn, data = fmd_pck.files[i]
    print(f"\nFood {i} ({fn}, len={len(data)}):")
    p0, p1 = struct.unpack('<2Q', data[8:24])
    name = data[p0:data.find(b'\x00', p0)].decode('latin-1')
    desc = data[p1:data.find(b'\x00', p1)].decode('latin-1')
    print(f"  Name: {name} | Desc: {desc}")
    # Inspect 4-byte integers in header
    for off in range(0, min(0x70, len(data)), 16):
        ints = [struct.unpack('<i', data[off+j*4:off+(j+1)*4])[0] for j in range(4) if off+(j+1)*4 <= len(data)]
        print(f"  0x{off:02x}: {ints}")

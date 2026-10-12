import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

wr_pck = PckArchive('mod_project/backups/WeaponRankData.pck')
for i, (fn, data) in enumerate(wr_pck.files):
    # let's see length and unpack
    print(f"Entry {i} ({fn}, len={len(data)}):")
    # print all 4-byte values
    for off in range(0, len(data), 16):
        ints = [struct.unpack('<i', data[off+j*4:off+(j+1)*4])[0] for j in range(4) if off+(j+1)*4 <= len(data)]
        floats = [struct.unpack('<f', data[off+j*4:off+(j+1)*4])[0] for j in range(4) if off+(j+1)*4 <= len(data)]
        print(f"  {off:02x}: ints={ints} | floats={[round(f, 3) if not (f != f or abs(f) > 1e6 or abs(f) < 1e-6) else f for f in floats]}")

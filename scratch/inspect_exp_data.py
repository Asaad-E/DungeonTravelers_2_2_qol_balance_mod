import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

les_pck = PckArchive('mod_project/backups/LvExpSkptData.pck')
print(f"LvExpSkptData count: {len(les_pck.files)}")
for i, (fn, data) in enumerate(les_pck.files):
    print(f"File {i}: {fn}, len={len(data)}")
    # Print first few 32-bit ints
    ints = [struct.unpack('<i', data[j:j+4])[0] for j in range(0, min(64, len(data)), 4)]
    print(f"  First 16 ints: {ints[:16]}")

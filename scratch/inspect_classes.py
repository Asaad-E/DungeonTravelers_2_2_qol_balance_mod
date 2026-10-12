import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

cld_pck = PckArchive('mod_project/backups/ClassLevelData.pck')
print(f"ClassLevelData files count: {len(cld_pck.files)}")

for i in range(min(5, len(cld_pck.files))):
    fn, data = cld_pck.files[i]
    print(f"File {i}: {fn}, length={len(data)} (bytes per level = {len(data)/99})")
    # Let's inspect level 1, level 15, level 30, level 50, level 99
    # Each record length: let's verify if 32 bytes or similar
    rec_len = len(data) // 99
    for lv in [1, 15, 30, 50, 99]:
        rec = data[(lv-1)*rec_len : lv*rec_len]
        # Unpack as ints or shorts
        ints = [struct.unpack('<i', rec[j:j+4])[0] for j in range(0, len(rec), 4)]
        print(f"  Lv {lv:2d}: {ints}")

class_pck = PckArchive('mod_project/backups/ClassData.pck')
print(f"\nClassData files count: {len(class_pck.files)}")
for i in range(min(10, len(class_pck.files))):
    fn, data = class_pck.files[i]
    # find name if any
    p0 = struct.unpack('<Q', data[8:16])[0] if len(data) > 16 else 0
    name = data[p0:data.find(b'\x00', p0)].decode('latin-1') if p0 < len(data) else 'N/A'
    print(f"Class {i}: {fn}, len={len(data)}, name={name}")

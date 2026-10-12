import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

arc = PckArchive('mod_project/backups/EnchantData.pck')
print("Files in EnchantData.pck:", len(arc.files))
for name, data in arc.files:
    if '0222' in name or '0024' in name:
        print(f"File {name}: len={len(data)}")
        # print words
        for off in range(0, min(len(data), 48), 4):
            val = struct.unpack('<I', data[off:off+4])[0]
            val_s = struct.unpack('<i', data[off:off+4])[0]
            print(f"  0x{off:02x}: {val} (signed: {val_s}, float: {struct.unpack('<f', data[off:off+4])[0]:.4f})")

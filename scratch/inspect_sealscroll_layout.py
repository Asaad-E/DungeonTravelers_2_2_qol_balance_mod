import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

arc = PckArchive('mod_project/backups/SealScrollData.pck')
for name, data in arc.files[:5]:
    print(f"\n--- {name} (len={len(data)}) ---")
    for off in range(0, len(data), 16):
        chunk = data[off:off+16]
        hex_str = ' '.join(f"{b:02x}" for b in chunk)
        words = [struct.unpack('<I', chunk[i:i+4])[0] for i in range(0, len(chunk), 4)]
        print(f"  0x{off:02x}: {hex_str:48s} | {words}")

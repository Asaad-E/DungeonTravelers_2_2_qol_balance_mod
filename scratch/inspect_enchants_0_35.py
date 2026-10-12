import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

arc = PckArchive('mod_project/backups/EnchantData.pck')
for name, data in arc.files:
    eid = int(name.split('_')[1].split('.')[0])
    if eid <= 35:
        # get string at offset 56
        str1 = data[56:].split(b'\x00')[0].decode('ascii', errors='ignore')
        w8 = struct.unpack('<I', data[0x20:0x24])[0]
        w9 = struct.unpack('<I', data[0x24:0x28])[0]
        w10 = struct.unpack('<I', data[0x28:0x2c])[0]
        w11 = struct.unpack('<I', data[0x2c:0x30])[0]
        print(f"ID {eid:2d}: w8=0x{w8:04x} ({w8:4d}, bit0={w8&1}), w9={w9}, w10={w10}, w11={w11:3d} | '{str1}'")

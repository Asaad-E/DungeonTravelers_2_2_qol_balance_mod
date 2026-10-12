import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

arc = PckArchive('mod_project/backups/SealScrollData.pck')
for name, data in arc.files:
    if len(data) >= 0x38:
        kind = struct.unpack('<I', data[0x18:0x1C])[0]
        if kind == 1:
            enemy_id = struct.unpack('<I', data[0x00:0x04])[0]
            ench_cnt = struct.unpack('<I', data[0x1c:0x20])[0]
            ench_ids = struct.unpack('<4i', data[0x20:0x30])
            lvl = struct.unpack('<I', data[0x34:0x38])[0]
            # print string at 0x48 or 0xa0
            str_off = struct.unpack('<I', data[0x08:0x0C])[0]
            s = data[str_off:].split(b'\x00')[0].decode('utf-8', errors='ignore')
            print(f"{name}: enemy={enemy_id:3d}, lvl={lvl:2d}, ench_cnt={ench_cnt}, ench_ids={ench_ids}, name='{s}'")

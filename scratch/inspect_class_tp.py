import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

cld_pck = PckArchive('mod_project/backups/ClassLevelData.pck')
class_pck = PckArchive('mod_project/backups/ClassData.pck')

class_names = []
for i, (fn, data) in enumerate(class_pck.files):
    p0 = struct.unpack('<Q', data[8:16])[0] if len(data) > 16 else 0
    name = data[p0:data.find(b'\x00', p0)].decode('latin-1') if p0 < len(data) else f'Class_{i}'
    p1 = struct.unpack('<Q', data[16:24])[0] if len(data) > 24 else 0
    desc = data[p1:data.find(b'\x00', p1)].decode('latin-1') if p1 < len(data) else ''
    class_names.append((name, desc))

print("Class count:", len(class_names))
for i in range(min(len(cld_pck.files), len(class_names))):
    fn, data = cld_pck.files[i]
    cname, cdesc = class_names[i]
    # Header is 4 bytes, then 99 records of 32 bytes
    rec1 = data[4:36]
    rec15 = data[4 + 14*32 : 4 + 15*32]
    rec30 = data[4 + 29*32 : 4 + 30*32]
    rec50 = data[4 + 49*32 : 4 + 50*32]
    rec99 = data[4 + 98*32 : 4 + 99*32]
    
    r1 = struct.unpack('<8i', rec1)
    r15 = struct.unpack('<8i', rec15)
    r30 = struct.unpack('<8i', rec30)
    r50 = struct.unpack('<8i', rec50)
    r99 = struct.unpack('<8i', rec99)
    
    print(f"[{i:2d}] {cname:<4} ({cdesc[:15]}): Lv1 TP={r1[2]}, Lv15 TP={r15[2]}, Lv30 TP={r30[2]}, Lv50 TP={r50[2]}, Lv99 TP={r99[2]} | Lv1 HP={r1[1]}, Lv15 HP={r15[1]}, Lv50 HP={r50[1]}")

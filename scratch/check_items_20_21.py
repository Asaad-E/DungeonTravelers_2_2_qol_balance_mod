import sys
sys.path.insert(0, '.')
import struct
from mod_project.tools.pck_handler import PckArchive

arc = PckArchive('mod_project/backups/ItemData.pck')
for idx in [20, 21]:
    data = arc.files[idx][1]
    ints = struct.unpack('<12I', data[:48])
    flt = struct.unpack('<f', data[40:44])[0]
    name = data[ints[2]:data.find(b'\x00', ints[2])].decode('latin-1')
    desc = data[ints[4]:data.find(b'\x00', ints[4])].decode('latin-1')
    print(f"Item {idx} ({name}): price={ints[6]}, sell={ints[7]}, param={ints[8]}, float={flt}")
    print(f"  Desc: {desc}")

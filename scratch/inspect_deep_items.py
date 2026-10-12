import os
import sys
sys.path.insert(0, '.')
import struct
import openpyxl
from mod_project.tools.pck_handler import PckArchive

def run():
    print("=== INSPECTING ITEMS IN XLSX ===")
    wb = openpyxl.load_workbook('mod_project/data_tables/items.xlsx')
    ws = wb['Items']
    targets = ['Flashlight', 'Dried Berry', 'Banango Slice', 'Mandragora Root', 'Fairy Apple', 'Golden Iron Chunk']
    
    rows = list(ws.iter_rows(values_only=True))
    headers = rows[0]
    for r in rows[1:]:
        name = str(r[2]) if len(r) > 2 else ''
        if any(t.lower() == name.lower() for t in targets):
            print(f"XLSX Row: {r}")

    print("\n=== INSPECTING ACTIVE ItemData.pck ===")
    arc = PckArchive('DungeonTravelers2-2_EN/Data/ENG/Parameter/ItemData.pck')
    for fn, b in arc.files:
        p_name, p_desc = struct.unpack('<2Q', b[:16])
        name = b[p_name:b.find(b'\x00', p_name)].decode('latin-1')
        if any(t.lower() == name.lower() for t in targets):
            desc = b[p_desc:b.find(b'\x00', p_desc)].decode('latin-1')
            # Look at fixed fields
            # Let's inspect offsets from 0 to min(p_name, 72)
            u32s = [struct.unpack('<I', b[i:i+4])[0] for i in range(0, min(p_name, 72), 4)]
            f32s = [struct.unpack('<f', b[i:i+4])[0] for i in range(0, min(p_name, 72), 4)]
            print(f"[{fn}] Name: '{name}'")
            print(f"   Desc: '{desc}'")
            for idx, (u, f) in enumerate(zip(u32s, f32s)):
                off = idx * 4
                print(f"     0x{off:02x} ({off}): int={u} (0x{u:08x}), float={f:.4f}")

if __name__ == '__main__':
    run()

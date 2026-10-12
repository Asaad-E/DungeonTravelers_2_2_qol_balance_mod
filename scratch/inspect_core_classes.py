import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

cld_pck = PckArchive('mod_project/backups/ClassLevelData.pck')

# Let's inspect class indices:
# 0: Fighter (FT)
# 6: Scout (SC)
# 12: Magic User (MU)
# 20: Maid (MA)
# 26: Spieler (SP)

classes_to_check = [(0, 'Fighter (FT)'), (6, 'Scout (SC)'), (12, 'Magic User (MU)'), (20, 'Maid (MA)'), (26, 'Spieler (SP)')]

for c_idx, name in classes_to_check:
    fn, data = cld_pck.files[c_idx]
    print(f"\n=== {name} ({fn}) ===")
    for lv in [1, 5, 10, 15, 20, 30, 50, 99]:
        rec = data[4 + (lv-1)*32 : 4 + lv*32]
        # 8 ints: [lv_idx, HP, TP, STR, VIT, INT, MND, AGI] or similar
        vals = struct.unpack('<8i', rec)
        print(f"  Lv {lv:2d}: Idx={vals[0]} | HP={vals[1]:4d} | TP={vals[2]:3d} | STR={vals[3]:3d} | VIT={vals[4]:3d} | INT={vals[5]:3d} | RES={vals[6]:3d} | AGI={vals[7]:3d}")

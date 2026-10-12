import sys
import os
import struct
import re

sys.path.insert(0, 'mod_project/tools')
from pck_handler import PckArchive

dungeon_arc = PckArchive('DungeonTravelers2-2_EN/Data/ENG/Dungeon/Dungeon.pck')

hits = []
for st_pck_name, st_bytes in dungeon_arc.files:
    if not st_pck_name.endswith('.pck'): continue
    st_arc = PckArchive.from_bytes(st_bytes)
    for map_pck_name, map_bytes in st_arc.files:
        if not map_pck_name.endswith('.pck'): continue
        map_arc = PckArchive.from_bytes(map_bytes)
        for adv_name, adv_bytes in map_arc.files:
            pos = 0
            while True:
                idx = adv_bytes.find(b'\xe8\x02', pos)
                if idx == -1: break
                # Check if it's preceded by category 4 (accessory/equipment) or container opcode
                ctx = adv_bytes[max(0, idx-16):idx+16]
                hits.append((st_pck_name, map_pck_name, adv_name, idx, ctx))
                pos = idx + 1

print(f"Total raw occurrences of 0x02e8 (744) across all dungeon scripts: {len(hits)}")
for st, mp, adv, idx, ctx in hits:
    print(f"{st} -> {mp} -> {adv} at offset {idx:#x}")
    print(f"   bytes: {ctx.hex(' ')}")

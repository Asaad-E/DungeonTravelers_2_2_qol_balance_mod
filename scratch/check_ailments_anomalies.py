import os, struct, sys
sys.path.insert(0, 'mod_project/tools')
from pck_handler import PckArchive, ItemHelper

archive = PckArchive('mod_project/backups/ItemData.pck')
ailment_types = list(range(10, 26))

for fn, b in archive.files:
    item = ItemHelper.read_item(b)
    for k in range(4):
        t, v = struct.unpack_from('<if', b, 0x24 + 8*k)
        if t in ailment_types:
            if v < 1.0 or v > 100.0:
                print(f"ANOMALY: {fn} ({item['name']}) type={t}, slot={k}, val={v}")

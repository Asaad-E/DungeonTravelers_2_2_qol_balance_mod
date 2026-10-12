import os, struct, sys
sys.path.insert(0, 'mod_project/tools')
from pck_handler import PckArchive, ItemHelper

archive = PckArchive('mod_project/backups/ItemData.pck')
for fn, b in archive.files:
    item = ItemHelper.read_item(b)
    for k in range(4):
        t, v = struct.unpack_from('<if', b, 0x24 + 8*k)
        if t == 17:
            print(f"{fn} ({item['name']}) slot {k}: val={v}")

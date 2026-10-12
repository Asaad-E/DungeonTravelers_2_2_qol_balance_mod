import os
import struct
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive, ItemHelper

base_dir = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project'
item_pck = os.path.join(base_dir, 'backups', 'ItemData.pck')

archive = PckArchive(item_pck)

def item_pairs(b):
    return [struct.unpack_from('<if', b, 0x24 + 8 * k) for k in range(4)]

for fn, b in archive.files:
    item = ItemHelper.read_item(b)
    pairs = item_pairs(b)
    if 'Dark Cloud' in item['name'] or '0458' in fn:
        print(f"=== {fn}: {item['name']} ===")
        print(f"Desc: {item['desc']}")
        for k, (t, v) in enumerate(pairs):
            target = "Ally" if k < 2 else "Enemy"
            print(f"  [{k}] ({target}): Type {t}, Val {v}")

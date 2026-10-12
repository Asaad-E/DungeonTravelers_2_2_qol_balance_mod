import os
import sys
import struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive, ItemHelper

base_dir = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project'
item_pck = os.path.join(base_dir, 'backups', 'ItemData.pck')

archive = PckArchive(item_pck)
for fn, b in archive.files:
    item = ItemHelper.read_item(b)
    if 'Dark Cloud' in item['name'] or '0458' in fn:
        print(f"Found: {fn} -> {item['name']}")
        print(f"  Description: {item['desc']}")
        print(f"  Keys: {list(item.keys())}")
        for k, v in item.items():
            if k not in ['name', 'desc']:
                print(f"    {k}: {v}")
        print("  Raw effects at 0x18:", [struct.unpack_from('<if', b, 0x18 + 8*k) for k in range(4)])

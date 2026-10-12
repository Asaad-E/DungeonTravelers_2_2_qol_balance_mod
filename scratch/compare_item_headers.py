import os
import struct
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive, ItemHelper

base_dir = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project'
item_pck = os.path.join(base_dir, 'backups', 'ItemData.pck')
archive = PckArchive(item_pck)

compare_items = ['Dark Cloud', 'Fairy Tonic', 'Hell Pass', 'Misery-Laced Letter', 'Wanted Poster', 'Medicine', 'Bomb']

for fn, b in archive.files:
    item = ItemHelper.read_item(b)
    if any(name == item['name'] for name in compare_items):
        print(f"=== {fn}: {item['name']} ===")
        # Dump header ints
        ints = struct.unpack_from('<28i', b, 0)
        print("  0x00-0x20:", ints[0:8])
        print("  0x20-0x40:", ints[8:16])
        print("  0x40-0x60:", ints[16:24])
        print("  0x60-0x70:", ints[24:28])
        # Also floats at 0x24:
        pairs = [struct.unpack_from('<if', b, 0x24 + 8*k) for k in range(4)]
        print("  Pairs at 0x24:", pairs)

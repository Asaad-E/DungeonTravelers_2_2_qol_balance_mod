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

all_pairs_by_type = {}
for fn, b in archive.files:
    item = ItemHelper.read_item(b)
    pairs = item_pairs(b)
    for k, (t, v) in enumerate(pairs):
        if t != -1:
            all_pairs_by_type.setdefault(t, []).append((fn, item['name'], k, v))

print("=== TYPES AND THEIR VALUES ACROSS ALL ITEMS ===")
for t in sorted(all_pairs_by_type.keys()):
    entries = all_pairs_by_type[t]
    vals = [v for _, _, _, v in entries]
    min_v, max_v = min(vals), max(vals)
    # Check if any value is < 1.0 while others are >= 1.0 or vice versa
    has_small = any(0 < v < 1.0 for v in vals)
    has_large = any(v >= 1.0 for v in vals)
    flag = " *** SUSPICIOUS / MIXED ***" if (has_small and has_large) else ""
    print(f"Type {t:3d} ({len(entries):3d} uses): min={min_v:g}, max={max_v:g} {flag}")
    if flag or has_small:
        for fn, name, slot, v in entries:
            if 0 < v < 1.0 or (has_small and has_large):
                print(f"    {fn} ({name}) slot {slot}: val={v}")

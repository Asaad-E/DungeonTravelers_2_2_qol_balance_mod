import sys
sys.path.insert(0, '.')
import struct
from mod_project.tools.pck_handler import PckArchive

def make_quest_rank_bag_entry(rank, pts, val):
    msg = f"Your bag's storage capacity has increased by {val}."
    s = msg.encode('latin-1') + b'\x00'
    hdr = struct.pack('<10i', rank, pts, 40, 0, 5, -1, -1, -1, -1, val)
    data = bytearray(hdr) + s
    pad = (8 - (len(data) % 8)) % 8
    data += b'\x00' * pad
    return bytes(data)

arc = PckArchive('mod_project/backups/QuestRankData.pck')
orig_08 = arc.files[7][1]
gen_08 = make_quest_rank_bag_entry(8, 200, 5)

print("Orig 08 len:", len(orig_08))
print("Gen 08 len: ", len(gen_08))
print("Match exactly:", orig_08 == gen_08)
if orig_08 != gen_08:
    print("Orig hex:", orig_08.hex())
    print("Gen hex: ", gen_08.hex())

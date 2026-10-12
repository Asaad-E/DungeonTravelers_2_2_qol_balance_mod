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
for i, (fn, b) in enumerate(arc.files):
    if fn == 'QuestRankData_02.bin':
        arc.files[i] = (fn, make_quest_rank_bag_entry(2, 25, 10))
        print('Updated QuestRankData_02 with +10 bag space!')
    elif fn == 'QuestRankData_08.bin':
        arc.files[i] = (fn, make_quest_rank_bag_entry(8, 200, 10))
        print('Updated QuestRankData_08 with +10 bag space!')

arc.save('DungeonTravelers2-2_EN/Data/ENG/Parameter/QuestRankData.pck')
print('Successfully saved QuestRankData.pck!')

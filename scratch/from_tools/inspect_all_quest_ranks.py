import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

arc = PckArchive('mod_project/backups/QuestRankData.pck')
print(f"Total Quest Ranks: {len(arc.files)}")
for fn, d in arc.files:
    rank, pts = struct.unpack('<II', d[:8])
    rew_type = struct.unpack('<i', d[16:20])[0]
    rew_val = struct.unpack('<i', d[36:40])[0]
    txt = d[40:d.find(b'\x00', 40)].decode('latin-1', errors='ignore')
    print(f"Rank {rank:2d} | Pts {pts:4d} | RewType {rew_type:2d} | Val {rew_val:5d} | Msg: '{txt}'")

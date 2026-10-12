import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

q_pck = PckArchive('DungeonTravelers2-2_EN/Data/ENG/Parameter/QuestData.pck')
print(f"Total Quests in QuestData.pck: {len(q_pck.files)}")

for fn, d in q_pck.files[:10]:
    # Let's inspect the binary fields
    print(f"\nFile: {fn} (size: {len(d)})")
    ints = struct.unpack(f'<{min(len(d)//4, 16)}i', d[:min(len(d), 64)])
    print("  First 16 ints:", ints)
    # Search for string text
    zero_pos = d.find(b'\x00', 40)
    if zero_pos != -1:
        text = d[40:zero_pos].decode('latin-1', errors='ignore')
        print("  Text at 40:", text[:60])

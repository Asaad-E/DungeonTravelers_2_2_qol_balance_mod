import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

q_pck = PckArchive('DungeonTravelers2-2_EN/Data/ENG/Parameter/QuestData.pck')

for i in [0, 1, 2, 3, 5, 10, 20, 50, 100, 200]:
    fn, d = q_pck.files[i]
    print(f"=== {fn} (len={len(d)}) ===")
    # Print 4-byte integers up to length of file
    num_ints = len(d) // 4
    ints = struct.unpack(f'<{num_ints}i', d[:num_ints*4])
    print("ints:", ints[:25])
    # Search for strings
    cur = 0
    strings = []
    while cur < len(d):
        end = d.find(b'\x00', cur)
        if end == -1: break
        s = d[cur:end]
        if len(s) > 3 and all(32 <= b < 127 for b in s):
            strings.append((cur, s.decode('latin-1')))
        cur = end + 1
    if strings:
        print("strings:", strings[:4])

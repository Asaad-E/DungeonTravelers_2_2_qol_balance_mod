import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

arc = PckArchive('mod_project/backups/EnchantData.pck')
for name, data in arc.files:
    eid = int(name.split('_')[1].split('.')[0])
    if eid in [0, 1, 2, 3, 4, 5, 6, 24, 25, 26, 27, 28]:
        # print words
        words = [struct.unpack('<I', data[i:i+4])[0] for i in range(0, min(len(data), 48), 4)]
        print(f"ID {eid:2d} ({name}): words={words}")

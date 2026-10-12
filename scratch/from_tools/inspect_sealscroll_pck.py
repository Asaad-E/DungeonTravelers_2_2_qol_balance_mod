import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from pck_handler import PckArchive

game_pck = 'DungeonTravelers2-2_EN/Data/Parameter/SealScrollData.pck'
backup_pck = 'mod_project/backups/SealScrollData.pck'
target = game_pck if os.path.exists(game_pck) else backup_pck

arc = PckArchive(target)
print("Files in SealScrollData.pck:")
for name, data in arc.files:
    print(f"  {name}: {len(data)} bytes")
    if name.endswith('.bin'):
        print(f"    first 64 bytes: {data[:64].hex()}")

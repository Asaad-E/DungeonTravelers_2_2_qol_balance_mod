import os

for root, dirs, files in os.walk('DungeonTravelers2-2_EN/Data'):
    for f in files:
        if 'quest' in f.lower():
            print("Found:", os.path.join(root, f))

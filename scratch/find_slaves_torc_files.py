import os

ROOT = 'DungeonTravelers2-2_EN'
target = b"Slave's Torc"

matches = []
for root, dirs, files in os.walk(ROOT):
    for f in files:
        path = os.path.join(root, f)
        try:
            with open(path, 'rb') as fp:
                data = fp.read()
                if target in data:
                    matches.append(os.path.relpath(path, ROOT))
        except:
            pass

print("Files containing \"Slave's Torc\":")
for m in matches:
    print(" -", m)

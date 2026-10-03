import os
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pck_handler import PckArchive

GAME_PARAM_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Parameter')
pck_path = os.path.join(GAME_PARAM_DIR, 'EnemyAttackData.pck')

arc = PckArchive(pck_path)

skills_by_name = {}
total_entries = len(arc.files)
with_desc = 0
empty_desc = 0

for fn, b in arc.files:
    if len(b) < 40:
        continue
    p0 = struct.unpack('<Q', b[8:16])[0]
    p1 = struct.unpack('<Q', b[16:24])[0]
    p2 = struct.unpack('<Q', b[24:32])[0]
    p3 = struct.unpack('<Q', b[32:40])[0]
    if p0 >= len(b) or p3 >= len(b):
        continue
    name = b[p0:b.find(b'\x00', p0)].decode('latin-1', 'replace')
    desc = b[p3:b.find(b'\x00', p3)].decode('latin-1', 'replace')
    if desc.strip():
        with_desc += 1
    else:
        empty_desc += 1
        
    if name not in skills_by_name:
        skills_by_name[name] = []
    skills_by_name[name].append((fn, desc))

print(f"Total entries in EnemyAttackData.pck: {total_entries}")
print(f"Entries with description: {with_desc}")
print(f"Entries without description: {empty_desc}")
print(f"Total distinct skill names: {len(skills_by_name)}")

names_with_desc = [n for n, l in skills_by_name.items() if any(d[1].strip() for d in l)]
print(f"Distinct skill names with non-empty description: {len(names_with_desc)}")

print("\n--- First 30 skill names with descriptions ---")
for n in names_with_desc[:30]:
    sample_desc = skills_by_name[n][0][1].replace('\n', ' // ')
    print(f"{n} ({len(skills_by_name[n])} variants): {sample_desc[:75]}")

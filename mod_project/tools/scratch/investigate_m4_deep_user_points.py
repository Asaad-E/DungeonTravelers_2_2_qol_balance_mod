import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))

print("=== 1. Check Grand Sealbooks (F89) ===")
from pck_handler import PckArchive
arc = PckArchive('mod_project/backups/SealScrollData.pck')

grand_seals = []
for name, data in arc.files:
    if len(data) >= 0x38:
        # Check kind at 0x18
        enemy_id, unk1 = struct.unpack('<II', data[0x00:0x08])
        kind = struct.unpack('<I', data[0x18:0x1C])[0]
        if kind == 1: # Grand Sealbook
            ench_cnt = struct.unpack('<I', data[0x1C:0x20])[0]
            ench_ids = struct.unpack('<4i', data[0x20:0x30])
            lvl = struct.unpack('<I', data[0x34:0x38])[0]
            grand_seals.append((name, enemy_id, ench_cnt, ench_ids, lvl))

print(f"Total Grand Sealbooks: {len(grand_seals)}")
for gs in grand_seals[:15]:
    print(f"  {gs[0]}: Enemy={gs[1]}, EnchCount={gs[2]}, EnchIDs={gs[3]}, Lvl={gs[4]}")

print("\n=== 2. Check Drops in EnemyStatusData (F90) ===")
# Where is EnemyStatusData?
enemy_pck_path = 'mod_project/backups/Enemy.pck' if os.path.exists('mod_project/backups/Enemy.pck') else 'DungeonTravelers2-2_EN/Data/ENG/Enemy/Enemy.pck'
if os.path.exists(enemy_pck_path):
    print("Enemy pck found:", enemy_pck_path)
    from enemy_data import load_all_enemies
    enemies = load_all_enemies()
    print(f"Loaded {len(enemies)} enemies.")
    # Inspect drops of first 5 enemies
    for e in list(enemies.values())[:5]:
        print(f"Enemy {e.get('id', '?')} ({e.get('name', '?')}): Drops={e.get('drops')}")
else:
    print("Enemy pck not found")

print("\n=== 3. Check Bag size 30 (S18) in code / docs ===")
# Search across mod_project for "bag", "30", "inventory"
with open('mod_project/docs/QOL_ROADMAP.md', 'r', encoding='utf-8') as f:
    qol = f.read()
import re
for m in re.finditer(r'.{0,60}(?:inventory|bag|30 slots).{0,60}', qol, re.IGNORECASE):
    print("  QoL match:", m.group(0).replace('\n', ' '))

print("\n=== 4. Check Quest Data (S20) ===")
for root, dirs, files in os.walk('mod_project'):
    for f in files:
        if 'quest' in f.lower():
            print("  Quest file:", os.path.join(root, f))
for root, dirs, files in os.walk('DungeonTravelers2-2_EN/Data'):
    for f in files:
        if 'quest' in f.lower():
            print("  Game Quest file:", os.path.join(root, f))

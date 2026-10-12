import os
import struct
import sys
sys.path.insert(0, 'mod_project/tools')
from pck_handler import PckArchive

base_dir = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project'
ITEM_ID = 458

print(f"=== SEARCHING FOR ITEM ID {ITEM_ID} (Dark Cloud) ===")

# 1. Quests
quest_pck = os.path.join(base_dir, 'backups', 'QuestData.pck')
if os.path.exists(quest_pck):
    q_archive = PckArchive(quest_pck)
    for fn, b in q_archive.files:
        # quest stores reward item at 0x3C
        reward_item = struct.unpack_from('<i', b, 0x3C)[0]
        if reward_item == ITEM_ID:
            print(f"[Quest] Reward in {fn}!")

# 2. Chests (TreasureBoxData.pck)
chest_pck = os.path.join(base_dir, 'backups', 'TreasureBoxData.pck')
if os.path.exists(chest_pck):
    c_archive = PckArchive(chest_pck)
    print(f"[Chests] Checking {len(c_archive.files)} chest files...")
    for fn, b in c_archive.files:
        # Check all 4-byte ints in chest data
        for off in range(0, len(b) - 3, 4):
            val = struct.unpack_from('<i', b, off)[0]
            if val == ITEM_ID:
                print(f"[Chests] Found {ITEM_ID} in {fn} at offset {hex(off)}")

# 3. Enemy Drops (CharacterData.pck or tables)
# Let's check data_tables/enemy_drops.xlsx if it exists
drops_file = os.path.join(base_dir, 'data_tables', 'enemy_drops.xlsx')
if os.path.exists(drops_file):
    import openpyxl
    wb = openpyxl.load_workbook(drops_file, data_only=True)
    ws = wb.active
    for r in ws.iter_rows(values_only=True):
        if any(c == ITEM_ID or c == 'Dark Cloud' for c in r):
            print(f"[Enemy Drops Table] Found in row: {r}")

# 4. CharacterData.pck
char_pck = os.path.join(base_dir, 'backups', 'CharacterData.pck')
if os.path.exists(char_pck):
    ch_archive = PckArchive(char_pck)
    for fn, b in ch_archive.files:
        for off in range(0, len(b) - 3, 4):
            val = struct.unpack_from('<i', b, off)[0]
            if val == ITEM_ID:
                print(f"[CharacterData] Found {ITEM_ID} in {fn} at offset {hex(off)}")

# 5. Shop scripts
for shop_name in ['ShopStore.pck', 'ShopDarkPeddler.pck', 'ShopIce.pck', 'ShopPeddler.pck', 'ShopRamen.pck']:
    p = os.path.join(base_dir, 'backups', shop_name)
    if os.path.exists(p):
        s_archive = PckArchive(p)
        for fn, b in s_archive.files:
            for off in range(0, len(b) - 3, 4):
                val = struct.unpack_from('<i', b, off)[0]
                if val == ITEM_ID:
                    print(f"[{shop_name}] Found {ITEM_ID} in {fn} at offset {hex(off)}")

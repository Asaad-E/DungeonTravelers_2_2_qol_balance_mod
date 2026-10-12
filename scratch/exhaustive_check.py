import os, sys, struct, re, openpyxl

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
game_param_dir = os.path.join(os.path.dirname(base_dir), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Parameter')
game_script_dir = os.path.join(os.path.dirname(base_dir), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')

sys.path.insert(0, os.path.join(base_dir, 'tools'))
from pck_handler import PckArchive, ItemHelper, EquipmentHelper, SkillHelper, SealScrollHelper

print("==================================================================")
print("       EXHAUSTIVE MOD COHERENCE & DISCREPANCY AUDIT")
print("==================================================================")

# 1. SCAN ALL DIALOGUE IN PCKS (Teaching, Lesson, ShopStore, ShopQuest, ShopBlacksmith, ShopBar)
print("\n[1] SCANNING ALL SCRIPT DIALOGUES FOR OUTDATED NUMBERS...")
script_pcks = [
    ("Teaching.pck", game_script_dir),
    ("Lesson.pck", game_script_dir),
    ("ShopStore.pck", game_script_dir),
    ("ShopQuest.pck", game_script_dir),
    ("ShopBlacksmith.pck", game_script_dir),
    ("ShopBar.pck", game_script_dir),
]

script_hits = []
for pck_name, pck_dir in script_pcks:
    pck_path = os.path.join(pck_dir, pck_name)
    arc = PckArchive(pck_path)
    for fn, b in arc.files:
        # extract latin-1 printable strings of length >= 15
        text_matches = re.findall(b'[\x20-\x7E\r\n]{15,}', b)
        for tm in text_matches:
            s = tm.decode('latin-1', 'ignore')
            # Look for percentage or number references
            if any(k in s for k in ['-35%', '-25%', '-20%', '30 steps', '10 steps', '50,000', '100,000', '500,000', 'Flashlight', 'Dried Berry', 'Banango', 'Slave', 'Dragon Papi']):
                script_hits.append((pck_name, fn, s.strip()))

for pck_name, fn, s in script_hits:
    print(f"  [{pck_name} -> {fn}]")
    print(f"    {repr(s[:100])}")

# 2. CHECK QUEST RANK REWARDS VS BAG CAP
print("\n[2] CHECKING QUEST RANK REWARDS IN QuestRankData.pck...")
qr_pck = PckArchive(os.path.join(game_param_dir, "QuestRankData.pck"))
for fn, b in qr_pck.files:
    rank, pts, off_text, unk1, reward_type = struct.unpack('<5i', b[:20])
    reward_val = struct.unpack('<i', b[36:40])[0]
    s = b[off_text:b.find(b'\x00', off_text)].decode('latin-1')
    print(f"  {fn} (Rank {rank:2d}, {pts:4d} pts): Type {reward_type} (Val: {reward_val:,}) | Text: '{s}'")

# 3. CHECK SLAVE'S TORC & ACCESSORIES
print("\n[3] CHECKING SLAVE'S TORC ENCHANTS IN EquipmentData.pck...")
eq_pck = PckArchive(os.path.join(game_param_dir, "EquipmentData.pck"))
for fn, b in eq_pck.files:
    if fn == 'EquipmentData_0744.bin':
        info = EquipmentHelper.read_equipment(b)
        # enchants start around 0x60
        enchants = struct.unpack('<4I', b[0x60:0x70])
        print(f"  {fn} ({info['name']}): Enchants: {enchants} | Desc: '{info['desc']}'")

# 4. CHECK GRAND SEAL DRAGON PAPI
print("\n[4] CHECKING GRAND SEAL DRAGON PAPI IN SealScrollData.pck...")
ss_pck = PckArchive(os.path.join(game_param_dir, "SealScrollData.pck"))
for fn, b in ss_pck.files:
    if fn == 'SealScrollData_0896.bin':
        info = SealScrollHelper.read_seal(b)
        aura_ench = struct.unpack('<I', b[0x44:0x48])[0]
        print(f"  {fn} ({info['name']}): Aura Enchant: {aura_ench} | Desc: '{info['desc']}'")

# 5. CHECK WEAPON RANK DELAYS IN WeaponRankData.pck
print("\n[5] CHECKING WEAPON RANK DELAY MULTIPLIERS...")
wr_pck = PckArchive(os.path.join(game_param_dir, "WeaponRankData.pck"))
for i, (fn, b) in enumerate(wr_pck.files):
    mult = struct.unpack('<f', b[0x10:0x14])[0]
    rank_letter = ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'E+', 'E', 'F+', 'F'][i]
    print(f"  Rank {rank_letter:<2} ({fn}): delay = {mult:.2f}x")

# 6. CHECK ENCHANTS 270 & 275
print("\n[6] CHECKING ENCHANTS 270 & 275...")
from pck_handler import EnchantHelper
ench_pck = PckArchive(os.path.join(game_param_dir, "EnchantData.pck"))
for idx in [270, 275]:
    fn = f"EnchantData_{idx:04d}.bin"
    for f, b in ench_pck.files:
        if f == fn:
            info = EnchantHelper.read_enchant(b)
            print(f"  Enchant {idx} ({fn}): Name = '{info['name']}'")

# 7. CHECK ALL FOOD MEALS IN FoodMenuData.pck
print("\n[7] CHECKING FOOD MENU MEALS...")
from pck_handler import FoodMenuHelper
fm_pck = PckArchive(os.path.join(game_param_dir, "FoodMenuData.pck"))
for fn, b in fm_pck.files:
    info = FoodMenuHelper.read_food_menu(b)
    print(f"  {fn} ({info['name']}): '{info['desc']}'")

print("\n==================================================================")

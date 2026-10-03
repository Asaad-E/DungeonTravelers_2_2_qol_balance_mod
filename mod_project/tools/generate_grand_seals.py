import struct, sys
sys.path.insert(0, 'mod_project/tools')
from pck_handler import PckArchive
import openpyxl

def read_str(data, ptr):
    if ptr == 0 or ptr >= len(data): return ''
    end = data.find(b'\x00', ptr)
    return data[ptr:end].decode('utf-8', errors='ignore') if end != -1 else data[ptr:].decode('utf-8', errors='ignore')

# 35 Grand Sealbook mechanics dictionary
GRAND_SEALS_DATA = {
    "Deep Slapyon": "Aura: Reduces dungeon trap and hazard damage by 90%.",
    "Overdue": "Aura: Significantly increases Mimic monster encounter rate.",
    "Tres Durian": "Aura: Greatly reduces enemy encounter rate (-50%).",
    "Mangos Queen": "Aura: Increases enemy encounter rate (+50%).",
    "Iktomi": "Aura: +4% INT/RES to back row (scales off party highest raw stats).",
    "Scanner": "Aura: High chance to significantly reduce spell chant time (-50%).",
    "Murasaki Shikibu": "Aura: Defending during combat recovers 5% of maximum TP.",
    "Serika": "Aura: Magic attacks retain 50% damage when grazing or missing.",
    "Martial Artist": "Aura: +10% physical and technique damage against higher-level enemies.",
    "Kaguya": "Aura: Treasure chest equipment drops receive +2 enhancement level.",
    "Azathoth": "Aura: +25% damage dealt by all Joint Skills.",
    "Cupid": "Aura: Increases encounter rate of wandering dungeon merchants and NPCs.",
    "Eros": "Aura: Increases Pep gained and lost from food items by +50%.",
    "Sukuna-Hikona": "Aura: +2% DEX/AGI to back row (scales off party highest raw stats).",
    "Default": "Aura: Reduces TP cost of all Magic spells by 20%.",
    "Calliope": "Aura: Reduces party Pep loss from all sources by 50%.",
    "Heqet": "Aura: +10% damage dealt per missing party member.",
    "Siesta": "Aura: Party recovers 3 TP for every 10 steps taken in dungeons.",
    "Genbu": "Aura: +4% ATK/DEF to front row (scales off party highest raw stats).",
    "Afanc": "Aura: Unarmed characters gain Rank A action speed.",
    "Molle": "Aura: +25% chance to successfully escape from battle.",
    "Bigfoot": "Aura: Party status ailment durations are reduced by 1 turn.",
    "Moby Dick": "Aura: +10% damage dealt against lower-level enemies.",
    "Qitian Dasheng": "Aura: Increases party critical hit rate by +20% (relative).",
    "Last Judgment": "Aura: 10% chance to fully recover HP at turn start.",
    "Iron Maiden": "Aura: +10% damage dealt to enemies afflicted with status ailments.",
    "Sahohime": "Aura: Defending during combat recovers 10% of maximum HP.",
    "Nuwa": "Aura: Reduces TP cost of all Techniques and skills by 20%.",
    "Kuchinawa": "Aura: Hired Tavern Mercenaries gain +30 to all base stats.",
    "Dragon Papi": "Aura: Up to +15% EXP gain when defeating higher-level enemies.",
    "Death Cataphract": "Aura: Increases class favorite weapon stat bonus by +2%.",
    "Ghast": "Aura: +10% damage dealt to all enemies when at 100% HP.",
    "Hell's Angel": "Aura: Increases all heroine unique passive skill ranks by +1.",
    "Samael": "Aura: +8% INT to back row (scales off party highest raw stats).",
    "Melek Taus": "Aura: +8% ATK to front row (scales off party highest raw stats)."
}

arc = PckArchive(r'DungeonTravelers2-2_EN\Data\ENG\Parameter\SealScrollData.pck')

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "GrandSeals"

headers = ["File_Name", "Seal_Name", "Boss_Name", "Vanilla_Desc", "Modded_Desc", "Status"]
ws.append(headers)

for fname, data in arc.files:
    p_name = struct.unpack_from('<I', data, 0x08)[0]
    p_desc = struct.unpack_from('<I', data, 0x10)[0]
    name = read_str(data, p_name)
    desc = read_str(data, p_desc)
    if 'mutant' in desc.lower() or 'grand' in desc.lower():
        # extract boss name inside brackets e.g. "Grand Sealbook [Ghast]"
        boss = name.split('[')[-1].split(']')[0] if '[' in name else name
        mod_desc = GRAND_SEALS_DATA.get(boss, desc)
        ws.append([fname, name, boss, desc, mod_desc, "Approved"])

wb.save('mod_project/data_tables/grand_seals.xlsx')
print(f"Successfully generated grand_seals.xlsx with {ws.max_row - 1} entries!")

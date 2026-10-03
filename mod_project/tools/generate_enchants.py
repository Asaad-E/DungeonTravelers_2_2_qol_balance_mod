import struct, sys
sys.path.insert(0, 'mod_project/tools')
from pck_handler import PckArchive
import openpyxl

arc = PckArchive(r'mod_project\backups\EnchantData.pck')

def read_str(d, ptr):
    if ptr == 0 or ptr >= len(d): return ''
    end = d.find(b'\x00', ptr)
    return d[ptr:end].decode('latin-1') if end != -1 else ''

ENCHANT_MAPPINGS = {
    "Max HP UP": "Max HP +10%",
    "Max HP MiniUP": "Max HP +5%",
    "Max HP DOWN": "Max HP -10%",
    "Max TP UP": "Max TP +10%",
    "Max TP MiniUP": "Max TP +5%",
    "Max TP DOWN": "Max TP -10%",
    "ATK UP": "ATK +10%",
    "ATK MiniUP": "ATK +5%",
    "ATK DOWN": "ATK -10%",
    "DEF UP": "DEF +10%",
    "DEF MiniUP": "DEF +5%",
    "DEF DOWN": "DEF -10%",
    "INT UP": "INT +10%",
    "INT MiniUP": "INT +5%",
    "INT DOWN": "INT -10%",
    "RES UP": "RES +10%",
    "RES MiniUP": "RES +5%",
    "RES DOWN": "RES -10%",
    "DEX UP": "DEX +10%",
    "DEX MiniUP": "DEX +5%",
    "DEX DOWN": "DEX -10%",
    "AGI UP": "AGI +10%",
    "AGI MiniUP": "AGI +5%",
    "AGI DOWN": "AGI -10%",
    "Physical attack UP": "Phys ATK +10%",
    "Physical attack MiniUP": "Phys ATK +5%",
    "Physical accuracy UP": "Phys Hit +10%",
    "Physical accuracy MiniUP": "Phys Hit +5%",
    "Physical defense UP": "Phys DEF +10%",
    "Physical defense MiniUP": "Phys DEF +5%",
    "Physical evasion UP": "Phys Dodge +10%",
    "Physical evasion MiniUP": "Phys Dodge +5%",
    "Magic attack UP": "Magic ATK +10%",
    "Magic attack MiniUP": "Magic ATK +5%",
    "Magic accuracy UP": "Magic Hit +10%",
    "Magic accuracy MiniUP": "Magic Hit +5%",
    "Magic defense UP": "Magic DEF +10%",
    "Magic defense MiniUP": "Magic DEF +5%",
    "Magic evasion UP": "Magic Dodge +10%",
    "Magic evasion MiniUP": "Magic Dodge +5%",
    "Critical rate UP": "Crit Rate +10%",
    "Critical rate MiniUP": "Crit Rate +5%",
    "Enemy critical rate DOWN": "Enemy Crit -10%",
    "Enemy critical rate MiniDOWN": "Enemy Crit -5%",
    "Enmity UP": "Aggro/Enmity +25%",
    "Enmity DOWN": "Aggro/Enmity -25%",
    "Speed UP": "Action Speed +10%",
    "Speed MiniUP": "Action Speed +5%",
    "Speed DOWN": "Action Speed -10%",
    "Chant speed UP": "Chant Speed +15%",
    "Chant speed MiniUP": "Chant Speed +8%",
    "Chant speed DOWN": "Chant Speed -15%",
    "Interruption rate GrandDOWN": "Interrupt Rate -90%",
    "Interruption rate MegaDOWN": "Interrupt Rate -75%",
    "Interruption rate DOWN": "Interrupt Rate -50%",
    "Interruption rate MiniDOWN": "Interrupt Rate -25%",
    "Interruption rate UP": "Interrupt Rate +25%",
    "Received physical damage DOWN": "Phys Damage Taken -10%",
    "Received physical damage MiniDOWN": "Phys Damage Taken -5%",
    "Received magic damage DOWN": "Magic Damage Taken -10%",
    "Received magic damage MiniDOWN": "Magic Damage Taken -5%",
    "Received damage DOWN": "Damage Taken -10%",
    "Received damage MiniDOWN": "Damage Taken -5%",
    "Convert received damage into TP": "Damage -> TP (10%)",
    "Convert received damage into big TP": "Damage -> TP (25%)",
    "Fire magic buff": "Fire Magic +15%",
    "Water magic buff": "Water Magic +15%",
    "Wind magic buff": "Wind Magic +15%",
    "Earth magic buff": "Earth Magic +15%",
    "Lightning magic buff": "Lightning Magic +15%",
    "Normal attack fire add-on": "Attack Adds: Fire",
    "Normal attack water add-on": "Attack Adds: Water",
    "Normal attack wind add-on": "Attack Adds: Wind",
    "Normal attack earth add-on": "Attack Adds: Earth",
    "Normal attack lightning add-on": "Attack Adds: Lightning",
    "HP recovery every turn": "HP Regen +50/turn",
    "HP recovery mini every turn": "HP Regen +20/turn",
    "TP recovery every turn": "TP Regen +10/turn",
    "TP recovery mini every turn": "TP Regen +4/turn",
}

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Enchants"

headers = ["File_Name", "Vanilla_Name", "Prefix", "Suffix", "Modded_Name", "Status"]
ws.append(headers)

approved_count = 0
for fname, data in arc.files:
    p0 = struct.unpack('<I', data[8:12])[0]
    p1 = struct.unpack('<I', data[16:20])[0]
    p2 = struct.unpack('<I', data[24:28])[0] if len(data) > 28 else 0
    name = read_str(data, p0)
    prefix = read_str(data, p1)
    suffix = read_str(data, p2)
    
    mod_name = ENCHANT_MAPPINGS.get(name, name)
    status = "Approved" if mod_name != name else "Vanilla"
    if status == "Approved":
        approved_count += 1
    ws.append([fname, name, prefix, suffix, mod_name, status])

wb.save('mod_project/data_tables/enchants.xlsx')
print(f"Generated enchants.xlsx with {ws.max_row - 1} entries ({approved_count} approved enhancements)!")

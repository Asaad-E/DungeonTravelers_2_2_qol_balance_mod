import struct, re, os, openpyxl
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# -------------------------------------------------------------------------
# 1. POPULATE ALL REMAINING CONSUMABLES IN items.xlsx
# -------------------------------------------------------------------------
print("=== 1. Populating all remaining consumables in items.xlsx ===")
i_arc = PckArchive(os.path.join(BACKUP_DIR, 'ItemData.pck'))

wb_items = openpyxl.load_workbook(os.path.join(TABLES_DIR, 'items.xlsx'))
ws_items = wb_items['Items']

items_by_fn = {}
for r in range(2, ws_items.max_row + 1):
    fn = ws_items.cell(row=r, column=2).value
    items_by_fn[fn] = r

new_items_updated = 0
for fname, data in i_arc.files:
    p0 = struct.unpack('<Q', data[8:16])[0]
    p1 = struct.unpack('<Q', data[16:24])[0]
    name = data[p0:data.find(b'\x00', p0)].decode('latin-1')
    desc = data[p1:data.find(b'\x00', p1)].decode('latin-1')
    target = struct.unpack('<I', data[0x24:0x28])[0]
    flt28 = struct.unpack('<f', data[0x28:0x2c])[0]
    eff2 = struct.unpack('<I', data[0x2c:0x30])[0]
    flt30 = struct.unpack('<f', data[0x30:0x34])[0]
    cat = struct.unpack('<I', data[0x44:0x48])[0]
    subcat = struct.unpack('<I', data[0x48:0x4c])[0]
    
    if cat in [2, 3] and (flt28 > 0 or flt30 > 0):
        # Determine description if currently vanilla
        r = items_by_fn.get(fname)
        if not r:
            continue
        cur_status = ws_items.cell(row=r, column=7).value
        cur_mod = ws_items.cell(row=r, column=6).value
        
        if cur_status == 'Approved' and cur_mod:
            continue # already explicitly curated
            
        scope = "all allies'" if target in [2, 3, 4] else "an ally's"
        scope_tp = "all allies'" if target in [2, 3, 4] else "an ally's"
        
        # Determine if HP, TP or both
        desc_out = ""
        # If item has both HP and TP (e.g. flt28 is HP, flt30 is TP or sleep)
        if flt28 > 0 and flt30 > 1.0:
            if flt30 <= 20 and 'sleep' in desc.lower():
                desc_out = f"Restore {scope} HP by {int(flt28)}. May inflict Sleep."
            elif 'tea' in name.lower() or 'bento' in name.lower() or 'juice' in name.lower() or 'manju' in name.lower() or 'cracker' in name.lower():
                desc_out = f"Restore {scope} HP by {int(flt28)} and TP by {int(flt30)}."
            else:
                desc_out = f"Restore {scope} HP by {int(flt28)}."
        elif flt28 > 0:
            # Check if this item is pure TP (juice, sake, pie, tea)
            if any(k in name.lower() for k in ['juice', 'sake', 'wine', 'soda', 'pie', 'tangerine', 'fruit', 'apple', 'pudding', 'monaka']):
                if subcat in [2, 3] and flt28 <= 100:
                    desc_out = f"Restore {scope_tp} TP by {int(flt28)}."
                else:
                    desc_out = f"Restore {scope} HP by {int(flt28):,}."
            else:
                desc_out = f"Restore {scope} HP by {int(flt28):,}."
        elif flt30 > 0:
            desc_out = f"Restore {scope_tp} TP by {int(flt30)}."
            
        if desc_out:
            ws_items.cell(row=r, column=6, value=desc_out)
            ws_items.cell(row=r, column=7, value="Approved")
            ws_items.cell(row=r, column=8, value="Auto-extracted binary recovery parameters.")
            new_items_updated += 1

wb_items.save(os.path.join(TABLES_DIR, 'items.xlsx'))
print(f"Updated {new_items_updated} additional consumables in items.xlsx!")

# -------------------------------------------------------------------------
# 2. ENRICH RESISTANCE ENCHANTS IN enchants.xlsx
# -------------------------------------------------------------------------
print("\n=== 2. Enriching resistance enchants in enchants.xlsx ===")
wb_enc = openpyxl.load_workbook(os.path.join(TABLES_DIR, 'enchants.xlsx'))
ws_enc = wb_enc['Enchants']

RESISTANCE_MAP = {
    # Fire
    "Fire resistance UP": "Fire Res +20",
    "Fire resistance MiniUP": "Fire Res +10",
    "Fire resistance DOWN": "Fire Res -20",
    "Fire resistance MegaUP": "Fire Res +30",
    "Fire resistance GrandUP": "Fire Res +50",
    "Fire resistance GrandDOWN": "Fire Res -40",
    # Water
    "Water resistance UP": "Water Res +20",
    "Water resistance MiniUP": "Water Res +10",
    "Water resistance DOWN": "Water Res -20",
    "Water resistance MegaUP": "Water Res +30",
    "Water resistance GrandUP": "Water Res +50",
    "Water resistance GrandDOWN": "Water Res -40",
    # Wind
    "Wind resistance UP": "Wind Res +20",
    "Wind resistance MiniUP": "Wind Res +10",
    "Wind resistance DOWN": "Wind Res -20",
    "Wind resistance MegaUP": "Wind Res +30",
    "Wind resistance GrandUP": "Wind Res +50",
    "Wind resistance GrandDOWN": "Wind Res -40",
    # Earth
    "Earth resistance UP": "Earth Res +20",
    "Earth resistance MiniUP": "Earth Res +10",
    "Earth resistance DOWN": "Earth Res -20",
    "Earth resistance MegaUP": "Earth Res +30",
    "Earth resistance GrandUP": "Earth Res +50",
    "Earth resistance GrandDOWN": "Earth Res -40",
    # Lightning
    "Lightning resistance UP": "Lightning Res +20",
    "Lightning resistance MiniUP": "Lightning Res +10",
    "Lightning resistance DOWN": "Lightning Res -20",
    "Lightning resistance MegaUP": "Lightning Res +30",
    "Lightning resistance GrandUP": "Lightning Res +50",
    "Lightning resistance GrandDOWN": "Lightning Res -40",
    # All Elemental
    "Elemental resistance UP": "All Elem Res +15",
    "Elemental resistance MiniUP": "All Elem Res +7",
    "Elemental resistance DOWN": "All Elem Res -15",
    "Elemental resistance MegaUP": "All Elem Res +30",
    "Elemental resistance GrandUP": "All Elem Res +50",
    "Elemental resistance GrandDOWN": "All Elem Res -30",
    # Slash
    "Slash resistance UP": "Slash Res +20",
    "Slash resistance MiniUP": "Slash Res +10",
    "Slash resistance DOWN": "Slash Res -20",
    "Slash resistance MegaUP": "Slash Res +30",
    "Slash resistance GrandUP": "Slash Res +50",
    "Slash resistance GrandDOWN": "Slash Res -40",
    # Stab
    "Stab resistance UP": "Stab Res +20",
    "Stab resistance MiniUP": "Stab Res +10",
    "Stab resistance DOWN": "Stab Res -20",
    "Stab resistance MegaUP": "Stab Res +30",
    "Stab resistance GrandUP": "Stab Res +50",
    "Stab resistance GrandDOWN": "Stab Res -40",
    # Bash
    "Bash resistance UP": "Bash Res +20",
    "Bash resistance MiniUP": "Bash Res +10",
    "Bash resistance DOWN": "Bash Res -20",
    "Bash resistance MegaUP": "Bash Res +30",
    "Bash resistance GrandUP": "Bash Res +50",
    "Bash resistance GrandDOWN": "Bash Res -40",
    # All Physical
    "Physical resistance UP": "All Phys Res +15",
    "Physical resistance MiniUP": "All Phys Res +7",
    "Physical resistance DOWN": "All Phys Res -15",
    "Physical resistance MegaUP": "All Phys Res +30",
    "Physical resistance GrandUP": "All Phys Res +50",
    "Physical resistance GrandDOWN": "All Phys Res -30",
}

enchants_updated = 0
for r in range(2, ws_enc.max_row + 1):
    van_name = ws_enc.cell(row=r, column=2).value
    if van_name in RESISTANCE_MAP:
        ws_enc.cell(row=r, column=5, value=RESISTANCE_MAP[van_name])
        ws_enc.cell(row=r, column=6, value="Approved")
        enchants_updated += 1

wb_enc.save(os.path.join(TABLES_DIR, 'enchants.xlsx'))
print(f"Updated {enchants_updated} resistance enchants in enchants.xlsx!")

# -------------------------------------------------------------------------
# 3. POPULATE NORMAL SEALBOOKS IN grand_seals.xlsx (RENAMED / EXPANDED TO seals.xlsx)
# -------------------------------------------------------------------------
print("\n=== 3. Updating SealScrollData for normal sealbooks ===")
s_arc = PckArchive(os.path.join(BACKUP_DIR, 'SealScrollData.pck'))

wb_seals = openpyxl.load_workbook(os.path.join(TABLES_DIR, 'grand_seals.xlsx'))
ws_seals = wb_seals['GrandSeals']

existing_seal_fns = {ws_seals.cell(row=r, column=1).value: r for r in range(2, ws_seals.max_row + 1)}

normal_seals_added = 0
for fname, data in s_arc.files:
    if fname in existing_seal_fns:
        continue # Already a Grand Sealbook
    p0 = struct.unpack('<I', data[8:12])[0]
    p1 = struct.unpack('<I', data[16:20])[0]
    name = data[p0:data.find(b'\x00', p0)].decode('latin-1')
    desc = data[p1:data.find(b'\x00', p1)].decode('latin-1')
    
    # Extract level e.g. "(Level 16)"
    lvl_match = re.search(r'\(Level\s*(\d+)\)', desc)
    lvl_str = f"Lv {lvl_match.group(1)}" if lvl_match else "Lv ??"
    
    monster_name = name.split('[')[-1].split(']')[0] if '[' in name else name
    mod_desc = f"Monster sealbook ({lvl_str}). Equip for affixes or forge at Blacksmith."
    
    ws_seals.append([fname, name, monster_name, desc, mod_desc, "Approved"])
    normal_seals_added += 1

wb_seals.save(os.path.join(TABLES_DIR, 'grand_seals.xlsx'))
print(f"Added {normal_seals_added} normal monster sealbooks to grand_seals.xlsx!")

import os, openpyxl

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tables_dir = os.path.join(base_dir, 'data_tables')

print("=== CHECKING EQUIPMENT.XLSX (551 WEAPONS/ARMORS) ===")
wb_eq = openpyxl.load_workbook(os.path.join(tables_dir, 'equipment.xlsx'))
ws_eq = wb_eq["Equipment"]
total_eq = ws_eq.max_row - 1
mismatched_lore = 0

for r in range(2, ws_eq.max_row + 1):
    fn = ws_eq.cell(row=r, column=2).value
    name = ws_eq.cell(row=r, column=3).value
    orig_desc = ws_eq.cell(row=r, column=5).value or ""
    mod_desc = ws_eq.cell(row=r, column=6).value or ""
    
    orig_line1 = orig_desc.split('\n')[0].strip()
    mod_line1 = mod_desc.split('\n')[0].strip()
    
    if orig_line1 != mod_line1:
        mismatched_lore += 1
        if mismatched_lore <= 10:
            print(f"[LORE MISMATCH] Row {r} ({name}):")
            print(f"  Orig Line 1: {repr(orig_line1)}")
            print(f"  Mod  Line 1: {repr(mod_line1)}")

print(f"Total Equipment: {total_eq}")
print(f"Mismatched Lore Lines: {mismatched_lore}")

print("\n=== CHECKING ITEMS.XLSX (388 ACTIVE ITEMS) ===")
wb_it = openpyxl.load_workbook(os.path.join(tables_dir, 'items.xlsx'))
ws_it = wb_it["Items"]
total_it = ws_it.max_row - 1
active_it = 0
mismatched_item_flavor = 0

for r in range(2, ws_it.max_row + 1):
    fn = ws_it.cell(row=r, column=2).value
    name = ws_it.cell(row=r, column=3).value
    orig_desc = ws_it.cell(row=r, column=5).value or ""
    mod_desc = ws_it.cell(row=r, column=6).value or ""
    status = ws_it.cell(row=r, column=7).value
    
    if status in ['Approved', 'Applied', 'Draft'] and mod_desc:
        active_it += 1
        orig_clean = orig_desc.strip()
        mod_clean = mod_desc.strip()
        
        # Check if original flavor/joke is preserved as prefix or base
        # In items, mod_desc usually appends ' (+60 HP)' or '\n(+20 HP/TP)'
        if not mod_clean.startswith(orig_clean):
            # Check if line 1 matches
            orig_l1 = orig_clean.split('\n')[0].strip()
            mod_l1 = mod_clean.split('\n')[0].strip()
            if not mod_clean.startswith(orig_l1):
                mismatched_item_flavor += 1
                if mismatched_item_flavor <= 10:
                    print(f"[ITEM FLAVOR MISMATCH] Row {r} ({name}):")
                    print(f"  Orig: {repr(orig_desc)}")
                    print(f"  Mod : {repr(mod_desc)}")

print(f"Total Items: {total_it}")
print(f"Active Modified Items: {active_it}")
print(f"Mismatched Item Flavor: {mismatched_item_flavor}")

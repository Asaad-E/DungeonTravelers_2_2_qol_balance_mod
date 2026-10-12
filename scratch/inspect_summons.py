import sys, os, struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
import openpyxl

def inspect_character_data():
    print("=== CHARACTERDATA.PCK ===")
    arc = PckArchive('mod_project/backups/CharacterData.pck')
    print("Files in CharacterData.pck:", len(arc.files))
    for i, (fn, data) in enumerate(arc.files):
        # find ascii strings
        chars = []
        cur = bytearray()
        for b in data:
            if 32 <= b < 127:
                cur.append(b)
            else:
                if len(cur) >= 3:
                    chars.append(cur.decode('ascii'))
                cur = bytearray()
        print(f"  {fn} ({len(data)}b): {chars[:6]}")

def inspect_skills_excel():
    print("\n=== SKILLS RELATED TO DOLLS / TINKER / WITCH / SAGE ===")
    wb = openpyxl.load_workbook('mod_project/data_tables/skills.xlsx')
    ws = wb['Skills']
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[3]:
            continue
        idx, cat, fn, name, max_lv, tp_prog, orig_desc, orig_lvup, mod_desc, mod_lvup, status, notes = row
        s = f"{name} {orig_desc} {mod_desc}".lower()
        if any(k in s for k in ['doll', 'puppet', 'tinker', 'circle protection', 'chant', 'power charge', 'megaton', 'swallow', 'hissatsu', 'crimson', 'cocytus', 'plasma', 'tempest', 'gaia']):
            print(f"[{cat}] {name} ({fn}) | MaxLv: {max_lv} | TP: {tp_prog}")
            print(f"   Orig: {orig_desc[:70]}")
            print(f"   Mod:  {mod_desc[:70] if mod_desc else 'None'}")

if __name__ == '__main__':
    inspect_character_data()
    inspect_skills_excel()

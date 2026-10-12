import sys, os, struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive, SkillHelper

def inspect_doll_skills():
    print("=== DOLL AND TINKER SKILLS RAW BYTES ===")
    arc = PckArchive('mod_project/backups/TechniqueSkillData.pck')
    skill_indices = [88, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107]
    for idx in skill_indices:
        fn = f"TechniqueSkillData_{idx:04d}.bin"
        match = [b for f, b in arc.files if f == fn]
        if match:
            b = match[0]
            info = SkillHelper.read_skill(b, 'Technique')
            # Let's inspect bytes in header:
            # 0x00..0x28 pointers
            # 0x28..0x5c attributes (target, element, delay, power, etc.)
            hdr_u16 = struct.unpack('<20H', b[0x28:0x50])
            hdr_u32 = struct.unpack('<10I', b[0x28:0x50])
            print(f"{fn} ({info['name']}): MaxLv={info['max_lv']}, TP={info['tp_prog']}")
            print(f"   u32 attrs [0x28..0x50]: {hdr_u32[:6]}")
            print(f"   desc: {info['desc'][:60]}")

def inspect_circle_protection():
    print("\n=== CIRCLE PROTECTION ===")
    arc = PckArchive('mod_project/backups/TechniqueSkillData.pck')
    for fn, b in arc.files:
        if b'Circle Protection' in b:
            info = SkillHelper.read_skill(b, 'Technique')
            hdr_u32 = struct.unpack('<10I', b[0x28:0x50])
            print(f"{fn} ({info['name']}): MaxLv={info['max_lv']}, TP={info['tp_prog']}")
            print(f"   u32 attrs: {hdr_u32[:6]}")
            print(f"   desc: {info['desc']}")
            print(f"   lvup: {info['lvup']}")

def inspect_food_menu():
    print("\n=== FOOD MENU ===")
    arc = PckArchive('mod_project/backups/FoodMenuData.pck')
    for fn, b in arc.files:
        # Header size and step counts
        # Let's see: strings are in b
        p0 = struct.unpack('<Q', b[8:16])[0]
        p1 = struct.unpack('<Q', b[16:24])[0]
        name = b[p0:b.find(b'\x00', p0)].decode('latin-1')
        desc = b[p1:b.find(b'\x00', p1)].decode('latin-1')
        u32s = struct.unpack('<10I', b[:40])
        # search for 300 (step duration) in ints
        ints = [struct.unpack('<I', b[o:o+4])[0] for o in range(0, min(len(b), p0), 4)]
        print(f"{fn} | {name} | ints: {ints[:8]} | desc: {desc[:50]}")

if __name__ == '__main__':
    inspect_doll_skills()
    inspect_circle_protection()
    inspect_food_menu()

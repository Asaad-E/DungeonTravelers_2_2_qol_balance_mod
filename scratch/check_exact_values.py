import sys, os, struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

def check_magic_chant():
    print("=== HIGH-TIER MAGIC CHANT AND POWER ===")
    arc = PckArchive('mod_project/backups/MagicSkillData.pck')
    spells = [146, 150, 154, 158, 162] # Crimson Flare, Cocytus, Muon Plasma, Tempest, Gaia Crush
    for idx in spells:
        fn = f"MagicSkillData_{idx:04d}.bin"
        match = [b for f, b in arc.files if f == fn]
        if match:
            b = match[0]
            # p0, p1, p2
            p0 = struct.unpack('<Q', b[8:16])[0]
            p1 = struct.unpack('<Q', b[16:24])[0]
            name = b[p0:b.find(b'\x00', p0)].decode('latin-1')
            # Let's inspect chant frames and power
            # in DT2 magic skills:
            # chant frames are stored in header
            # let's look at 0x28..0x70
            u16s = struct.unpack('<30H', b[0x28:0x64])
            u32s = struct.unpack('<15I', b[0x28:0x64])
            # let's print u32s
            print(f"{fn} ({name}): u32s[0:10]={u32s[:10]}")

def check_enchants():
    print("\n=== ENCHANTS SAMPLE ===")
    arc = PckArchive('mod_project/backups/EnchantData.pck')
    print("Total enchants:", len(arc.files))
    for i in range(min(5, len(arc.files))):
        fn, b = arc.files[i]
        # let's inspect header
        u32s = struct.unpack('<6I', b[:24])
        print(f"  {fn}: u32s={u32s}, len={len(b)}")

def check_traps():
    print("\n=== TRAPDATA ===")
    arc = PckArchive('mod_project/backups/TrapData.pck')
    for fn, b in arc.files:
        tid = struct.unpack('<I', b[0:4])[0]
        p_name = struct.unpack('<I', b[8:12])[0]
        status_id = struct.unpack('<i', b[0x10:0x14])[0]
        chance = struct.unpack('<f', b[0x14:0x18])[0]
        sfx = struct.unpack('<I', b[0x18:0x1c])[0]
        scope = struct.unpack('<I', b[0x1c:0x20])[0]
        name = b[p_name:b.find(b'\x00', p_name)].decode('latin-1') if p_name < len(b) else ""
        print(f"Trap {tid:2d} | {name:20s} | status={status_id:4d} | chance={chance:.2f} | scope={scope}")

def check_food():
    print("\n=== FOOD MENU RAW STATS ===")
    arc = PckArchive('mod_project/backups/FoodMenuData.pck')
    for fn, b in arc.files:
        p0 = struct.unpack('<Q', b[8:16])[0]
        name = b[p0:b.find(b'\x00', p0)].decode('latin-1')
        # let's unpack u32s before p0
        u32s = [struct.unpack('<I', b[o:o+4])[0] for o in range(0, p0, 4)]
        print(f"{fn} | {name:22s} | ints: {u32s}")

if __name__ == '__main__':
    check_magic_chant()
    check_enchants()
    check_traps()
    check_food()

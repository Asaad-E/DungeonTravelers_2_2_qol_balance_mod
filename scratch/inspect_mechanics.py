import sys, os, struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

def check_classes():
    print("=== CLASSDATA.PCK ===")
    arc = PckArchive('mod_project/backups/ClassData.pck')
    for i, (fn, data) in enumerate(arc.files):
        p_code = struct.unpack('<I', data[0x08:0x0c])[0]
        p_name = struct.unpack('<I', data[0x10:0x14])[0]
        p_desc = struct.unpack('<I', data[0x18:0x1c])[0]
        code = data[p_code:data.find(b'\x00', p_code)].decode('cp932', 'replace')
        name = data[p_name:data.find(b'\x00', p_name)].decode('cp932', 'replace')
        desc = data[p_desc:data.find(b'\x00', p_desc)].decode('cp932', 'replace') if p_desc < len(data) else ""
        fields = struct.unpack('<10I', data[:40])
        print(f"{i:2d} | {fn} | code: {code:6s} | name: {name:20s} | desc: {desc[:30]} | hdr: {fields[:6]}")

def check_weapon_ranks():
    print("\n=== WEAPONRANKDATA.PCK ===")
    arc = PckArchive('mod_project/backups/WeaponRankData.pck')
    for i, (fn, data) in enumerate(arc.files):
        uints = [struct.unpack('<I', data[j:j+4])[0] for j in range(0, len(data), 4)]
        p_name = uints[2]
        name = data[p_name:data.find(b'\x00', p_name)].decode('latin-1', 'replace') if p_name < len(data) else ""
        mult = struct.unpack('<f', data[0x10:0x14])[0]
        print(f"{i:2d} | {fn} | name: {name:10s} | mult: {mult:.2f} | raw: {data.hex()}")

if __name__ == '__main__':
    check_classes()
    check_weapon_ranks()

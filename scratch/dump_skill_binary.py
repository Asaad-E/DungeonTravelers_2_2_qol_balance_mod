import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

def dump_header(pck_path, idx=0):
    pck = PckArchive(pck_path)
    fn, data = pck.files[idx]
    print(f"=== {pck_path} Entry {idx}: {fn} (Length: {len(data)}) ===")
    
    # Let's inspect 4-byte integers up to fixed_hdr
    # Find pointers
    p0, p1 = struct.unpack('<2Q', data[8:24])
    print(f"p0 (Name): 0x{p0:x}, p1 (Desc): 0x{p1:x}")
    name = data[p0:data.find(b'\x00', p0)].decode('latin-1')
    print(f"Skill Name: {name}")
    
    # Print 32-bit words
    print("Dumping 32-bit words from offset 0x00 to 0x1f0:")
    for offset in range(0, min(0x1f0, len(data)), 16):
        hex_bytes = " ".join(f"{b:02x}" for b in data[offset:offset+16])
        ints = [struct.unpack('<i', data[offset+i*4:offset+(i+1)*4])[0] for i in range(4) if offset+i*4+4 <= len(data)]
        print(f"0x{offset:04x}: {hex_bytes:<48} | {ints}")

dump_header('mod_project/backups/TechniqueSkillData.pck', 0)
dump_header('mod_project/backups/MagicSkillData.pck', 0)

import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

def inspect_skill_arrays(pck_path, idx=0):
    pck = PckArchive(pck_path)
    fn, data = pck.files[idx]
    p0, p1 = struct.unpack('<2Q', data[8:24])
    name = data[p0:data.find(b'\x00', p0)].decode('latin-1')
    print(f"=== {name} ({fn}) in {pck_path} ===")
    
    # Check 10-element int and float arrays
    for off in range(0x28, min(0x1f0, len(data)), 4):
        # Check if 10 consecutive ints or floats
        try:
            ints = struct.unpack('<10i', data[off:off+40])
            floats = struct.unpack('<10f', data[off:off+40])
            # If floats are reasonable (between 0.01 and 10000)
            if all(0.0 <= f <= 5000.0 for f in floats) and any(f > 0.0 for f in floats):
                # Check how many distinct
                print(f"  Float array at 0x{off:02x}: {[round(f, 3) for f in floats]}")
            if all(0 <= i <= 500 for i in ints) and any(i > 0 for i in ints) and ints[0] <= ints[-1]:
                print(f"  Int array at 0x{off:02x}: {list(ints)}")
        except Exception:
            pass

inspect_skill_arrays('mod_project/backups/MagicSkillData.pck', 0)
inspect_skill_arrays('mod_project/backups/MagicSkillData.pck', 1) # Fire Blast
inspect_skill_arrays('mod_project/backups/MagicSkillData.pck', 15) # Tempest
inspect_skill_arrays('mod_project/backups/TechniqueSkillData.pck', 0) # Provoke
inspect_skill_arrays('mod_project/backups/TechniqueSkillData.pck', 10) # Halving Slice

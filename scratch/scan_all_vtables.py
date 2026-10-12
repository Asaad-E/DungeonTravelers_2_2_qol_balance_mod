import struct, sys
sys.path.append('mod_project/tools')
from exe_reader import Exe
import capstone

exe = Exe()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

# Scan ALL vtables in .rdata
# We know RDATA range is 0x630000 to 0x720000
vtables = {}
for va in range(0x630000, 0x720000, 4):
    col = exe.u32(va - 4)
    if col and 0x630000 <= col < 0x720000:
        sig = exe.u32(col)
        if sig == 0: # MSVC RTTI CompleteObjectLocator signature
            td = exe.u32(col + 0xc)
            if td and 0x630000 <= td < 0x720000:
                name = exe.cstring(td + 8)
                if name.startswith('.?AV'):
                    vtables[va] = name

print(f"Total vtables found: {len(vtables)}")

# Find vtables that have method slot 0x34 or 0x3c returning a value
results = []
for vt, name in vtables.items():
    m34 = exe.u32(vt + 0x34)
    m3c = exe.u32(vt + 0x3c)
    if m34 and 0x400000 <= m34 < 0x600000 and m3c and 0x400000 <= m3c < 0x600000:
        # Check if name has Command or Status or Action or Effect
        if any(k in name for k in ['Command', 'Status', 'Effect', 'Passive', 'Skill']):
            results.append((vt, name, m34, m3c))

print(f"Matching vtables: {len(results)}")
for vt, name, m34, m3c in results:
    print(f"vt {hex(vt)} ({name}): m34={hex(m34)}, m3c={hex(m3c)}")

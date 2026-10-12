import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
text_va, size = exe.text[1], exe.text[4]
code = exe.read(text_va, size)

# 0.08 in float:
f8 = struct.pack('<f', 0.08)
print("0.08 bytes:", f8.hex())

# search for references to 0.08 in text or rdata
for sname in ['.rdata', '.data', '.text']:
    s = getattr(exe, sname[1:], None)
    if s:
        va, raw_sz = s[1], s[4]
        data = exe.read(va, raw_sz)
        pos = 0
        while True:
            idx = data.find(f8, pos)
            if idx == -1:
                break
            print(f"0.08 found in {sname} at VA 0x{va + idx:06x}")
            pos = idx + 1

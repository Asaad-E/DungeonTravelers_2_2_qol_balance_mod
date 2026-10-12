import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
text_va, size = exe.text[1], exe.text[4]
code = exe.read(text_va, size)

# Look for references to offset 0x20 of enchant record in memory
# Let's search for test ..., 1 or bt ..., 0
# Or let's search for how EnchantData is loaded
print("Searching for EnchantData references...")
for sname in ['.rdata', '.data']:
    s = getattr(exe, sname[1:], None)
    if s:
        va, raw_sz = s[1], s[4]
        data = exe.read(va, raw_sz)
        idx = data.find(b'EnchantData')
        if idx != -1:
            print(f"Found 'EnchantData' in {sname} at 0x{va + idx:06x}")

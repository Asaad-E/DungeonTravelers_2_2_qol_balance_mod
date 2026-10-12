import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
text_va, size = exe.text[1], exe.text[4]
code = exe.read(text_va, size)

# Look for push 309 (0x135) or cmp ..., 309
p309 = bytes([0x68, 0x35, 0x01, 0x00, 0x00])
pos = 0
while True:
    idx = code.find(p309, pos)
    if idx == -1: break
    addr = text_va + idx
    print(f"Push 309 at 0x{addr:06x}")
    dis = list(md.disasm(exe.read(addr - 10, 40), addr - 10))
    for i in dis:
        print(f"  0x{i.address:06x}: {i.mnemonic:10s} {i.op_str}")
    pos = idx + 1

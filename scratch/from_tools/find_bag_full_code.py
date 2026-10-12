import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

s_idx = code.find(b'BAG_FULL')
str_va = 0x630000 + (s_idx - 2289152)
print(f"BAG_FULL string at 0x{str_va:x}")

ptr = struct.pack('<I', str_va)
pos = 0
while True:
    idx = code.find(ptr, pos)
    if idx == -1: break
    va = exe.sections[0][1] + (idx - exe.sections[0][3])
    print(f"\nPointer to BAG_FULL at 0x{va:x}:")
    dis = list(md.disasm(exe.read(va - 40, 100), va - 40))
    for instr in dis:
        print(f"  0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")
    pos = idx + 1

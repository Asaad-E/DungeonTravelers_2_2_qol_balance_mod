import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

print("Disassembly around 0x58b10a:")
dis = list(md.disasm(exe.read(0x58b0e0, 100), 0x58b0e0))
for i in dis:
    print(f"  0x{i.address:06x}: {i.mnemonic:10s} {i.op_str}")

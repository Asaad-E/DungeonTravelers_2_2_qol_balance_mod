import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

print("Disassembly at 0x44a350 - 0x44a3b0:")
dis = list(md.disasm(exe.read(0x44a340, 120), 0x44a340))
for instr in dis:
    print(f"  0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")

import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

table_va = 0x598b40
table_bytes = exe.read(table_va, 24)
cases = struct.unpack('<6I', table_bytes)
for i, target_va in enumerate(cases):
    print(f"\n--- Case {i} -> 0x{target_va:06x} ---")
    dis = list(md.disasm(exe.read(target_va, 50), target_va))
    for instr in dis:
        print(f"  0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")

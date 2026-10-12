import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

# Disassemble from 0x597800 to 0x597bc0 to see the reward handler
dis = list(md.disasm(exe.read(0x597800, 700), 0x597800))
for instr in dis:
    if any(k in instr.op_str for k in ['cmp', 'switch', '0x738a14', 'call']):
        print(f"0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")

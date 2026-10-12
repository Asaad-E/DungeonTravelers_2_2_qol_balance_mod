import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

for addr in [0x602475, 0x62d040]:
    raw = exe.read(addr, 64)
    print(f"\n--- Disassembly at 0x{addr:06x} ---")
    for instr in md.disasm(raw, addr):
        print(f"0x{instr.address:06x}: {instr.mnemonic} {instr.op_str}")

import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
text_va, size = exe.text[1], exe.text[4]
code = exe.read(text_va, size)

for eid in [222, 223, 224, 225, 281, 297]:
    # look for push eid (68 xx xx xx xx or 6a xx)
    pattern1 = bytes([0x68, eid & 0xff, (eid >> 8) & 0xff, 0, 0])
    pattern2 = bytes([0x6a, eid & 0xff]) if eid < 128 else None
    pos = 0
    while True:
        idx = code.find(pattern1, pos)
        if idx == -1:
            break
        addr = text_va + idx
        print(f"ID {eid}: push 0x{eid:x} at 0x{addr:06x}")
        # disassemble next few instructions
        dis = list(md.disasm(exe.read(addr, 30), addr))
        for instr in dis[:5]:
            print(f"    0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")
        pos = idx + 1

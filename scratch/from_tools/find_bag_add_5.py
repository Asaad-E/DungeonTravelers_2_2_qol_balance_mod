import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

import re
text_raw, text_sz, text_va = exe.sections[0][3], exe.sections[0][2], exe.sections[0][1]
text_code = code[text_raw:text_raw+text_sz]

# Search for "add dword ptr [reg + off], 5" (opcode 83 40..47 xx 05 or 83 80..87 xxxxxxxx 05)
matches = [m.start() for m in re.finditer(rb'(\x83[\x40-\x47]..\x05|\x83[\x80-\x87]....\x05)', text_code)]
print(f"Matches for add [reg+off], 5: {len(matches)}")

# Filter matches that are in the 0x500000-0x5a0000 range (game systems / quest)
for m_idx in matches:
    va = text_va + m_idx
    if 0x480000 <= va <= 0x5a0000:
        nearby = text_code[m_idx-10:m_idx+30]
        dis = list(md.disasm(nearby, va - 10))
        for instr in dis:
            if 'add' in instr.mnemonic and '5' in instr.op_str:
                print(f"  0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")

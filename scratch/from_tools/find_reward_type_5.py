import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

# Let's search for instructions that read offset 0x24 (36) or offset 0x10 (16)
# from a QuestRank record
# In QuestRank record:
# 0x00 rank
# 0x04 pts
# 0x08 text_offset
# 0x0c 0
# 0x10 rew_type (0=item, 1=equip, 2=gold, 3=dungeon, 4=quest_limit, 5=bag, 6=mercenary)
# 0x24 rew_val
# Let's search for "cmp ..., 5" followed by reading 0x24
import re
text_raw, text_sz, text_va = exe.sections[0][3], exe.sections[0][2], exe.sections[0][1]
text_code = code[text_raw:text_raw+text_sz]

# Let's search for cmp ..., 5 (opcode 83 f8 05 or 83 f9 05 or 83 fa 05 or 83 fe 05)
matches = [m.start() for m in re.finditer(rb'(\x83[\xf8-\xff]\x05)', text_code)]
print(f"Matches for cmp reg, 5: {len(matches)}")
for m_idx in matches:
    va = text_va + m_idx
    # check if nearby has [reg + 0x24]
    nearby = text_code[m_idx-20:m_idx+60]
    if b'\x24' in nearby:
        print(f"Candidate at 0x{va:x}:")
        dis = list(md.disasm(nearby, va - 20))
        for instr in dis:
            print(f"  0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")
        print("-" * 50)

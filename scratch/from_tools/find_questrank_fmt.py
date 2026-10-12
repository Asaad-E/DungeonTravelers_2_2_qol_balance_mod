import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

s_idx = code.find(b'QuestRank.  %02d')
print("Direct find of 'QuestRank.  %02d':", s_idx)

for name, rva, vsz, raw, rsz in exe.sections:
    if raw <= s_idx < raw + rsz:
        actual_va = 0x400000 + rva + (s_idx - raw)
        print(f"Section {name}: actual_va = 0x{actual_va:x}")
        ptr_bytes = struct.pack('<I', actual_va)
        p_idx = code.find(ptr_bytes)
        print(f"Pointer found at: 0x{p_idx:x}")
        if p_idx != -1:
            for n2, r2, vs2, rw2, rs2 in exe.sections:
                if rw2 <= p_idx < rw2 + rs2:
                    code_va = 0x400000 + r2 + (p_idx - rw2)
                    print(f"Code VA: 0x{code_va:x}")
                    dis = list(md.disasm(exe.read(code_va - 40, 150), code_va - 40))
                    for instr in dis:
                        print(f"  0x{instr.address:06x}: {instr.mnemonic} {instr.op_str}")

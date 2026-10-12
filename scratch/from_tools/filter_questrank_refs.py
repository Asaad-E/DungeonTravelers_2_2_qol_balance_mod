import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

target = struct.pack('<I', 0x738a14)
pos = 0
text_va, text_sz, text_raw = exe.sections[0][1], exe.sections[0][2], exe.sections[0][3]

refs = []
while True:
    idx = code.find(target, pos)
    if idx == -1: break
    if text_raw <= idx < text_raw + text_sz:
        va = text_va + (idx - text_raw)
        refs.append(va)
    pos = idx + 1

print(f"Total references to 0x738a14 in .text: {len(refs)}")
for va in refs:
    print(f"\n--- Ref at 0x{va:06x} ---")
    dis = list(md.disasm(exe.read(va - 20, 80), va - 20))
    for instr in dis:
        print(f"  0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")

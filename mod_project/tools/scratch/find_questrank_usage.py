import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

for target_addr in [0x738a10, 0x738a14]:
    target_bytes = struct.pack('<I', target_addr)
    pos = 0
    print(f"\n=== References to 0x{target_addr:x} ===")
    while True:
        idx = code.find(target_bytes, pos)
        if idx == -1: break
        # check section
        for name, va, vsz, raw, rsz in exe.sections:
            if raw <= idx < raw + rsz:
                code_va = va + (idx - raw)
                print(f"Ref at 0x{code_va:x} ({name}):")
                dis = list(md.disasm(exe.read(code_va - 20, 80), code_va - 20))
                for instr in dis:
                    print(f"  0x{instr.address:06x}: {instr.mnemonic:10s} {instr.op_str}")
        pos = idx + 1

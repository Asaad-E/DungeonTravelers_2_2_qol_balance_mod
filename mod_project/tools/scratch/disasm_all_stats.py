import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
import capstone

exe_path = 'DungeonTravelers2-2_EN/DT22_en_unwrapped.exe'
with open(exe_path, 'rb') as f:
    code = f.read()

# Base address of unwrapped exe is 0x400000
# Text section typically around 0x401000
# Let's search for push 0x18, push 0x19, push 0x1a, push 0x1b, push 0x1c
# opcode for push byte: 6a 18, 6a 19, 6a 1a, 6a 1b, 6a 1c

md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

for eid in [24, 25, 26, 27, 28]:
    pattern = bytes([0x6a, eid])
    pos = 0
    while True:
        idx = code.find(pattern, pos)
        if idx == -1:
            break
        # Check if nearby has call [vtable + 0xf0] or similar
        nearby = code[max(0, idx - 10):min(len(code), idx + 40)]
        va = 0x400000 + idx # approximate raw offset to VA
        print(f"Enchant {eid} (0x{eid:02x}) found at raw 0x{idx:06x}:")
        dis = list(md.disasm(nearby, va - 10))
        for instr in dis:
            print(f"  0x{instr.address:06x}: {instr.mnemonic} {instr.op_str}")
        print("-" * 50)
        pos = idx + 1

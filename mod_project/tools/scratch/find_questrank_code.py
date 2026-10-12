import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

# Find the virtual address of the string "QuestRankData.pck"
# In PE, let's find which section contains raw 0x277d1f
# Section headers
num_sections = struct.unpack('<H', code[0x3c+6:0x3c+8])[0]
opt_hdr_size = struct.unpack('<H', code[0x3c+20:0x3c+22])[0]
sec_start = 0x3c + 24 + opt_hdr_size

str_raw = 0x277d1f
str_va = None
for i in range(num_sections):
    sec = code[sec_start + i*40 : sec_start + (i+1)*40]
    s_name = sec[:8].split(b'\x00')[0].decode('latin-1')
    vsize, rva, rsize, raw_ptr = struct.unpack('<IIII', sec[8:24])
    if raw_ptr <= str_raw < raw_ptr + rsize:
        str_va = 0x400000 + rva + (str_raw - raw_ptr)
        print(f"String in section '{s_name}': Raw 0x{str_raw:x} -> VA 0x{str_va:x}")
        break

if str_va:
    target_bytes = struct.pack('<I', str_va)
    pos = 0
    while True:
        idx = code.find(target_bytes, pos)
        if idx == -1: break
        # Found reference!
        ref_va = None
        for i in range(num_sections):
            sec = code[sec_start + i*40 : sec_start + (i+1)*40]
            vsize, rva, rsize, raw_ptr = struct.unpack('<IIII', sec[8:24])
            if raw_ptr <= idx < raw_ptr + rsize:
                ref_va = 0x400000 + rva + (idx - raw_ptr)
                break
        print(f"Reference to string at Raw 0x{idx:x} (VA 0x{ref_va:x}):")
        # Disassemble around ref_va
        dis = list(md.disasm(exe.read(ref_va - 20, 100), ref_va - 20))
        for instr in dis:
            print(f"  0x{instr.address:06x}: {instr.mnemonic} {instr.op_str}")
        print("="*60)
        pos = idx + 1

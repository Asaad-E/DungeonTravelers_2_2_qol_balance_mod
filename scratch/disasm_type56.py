import capstone
import pefile

exe_path = r'c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project\tools\DT22_en_unwrapped.exe'
pe = pefile.PE(exe_path)

# 0x511e39
target_va = 0x511e39
image_base = pe.OPTIONAL_HEADER.ImageBase
rva = target_va - image_base

# get section containing rva
sect = None
for s in pe.sections:
    if s.VirtualAddress <= rva < s.VirtualAddress + s.Misc_VirtualSize:
        sect = s
        break

if sect:
    offset = rva - sect.VirtualAddress + sect.PointerToRawData
    with open(exe_path, 'rb') as f:
        f.seek(offset - 0x40)
        code = f.read(0xa0)

    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    start_va = target_va - 0x40
    print(f"Disassembly around 0x{target_va:x}:")
    for ins in md.disasm(code, start_va):
        marker = "===> " if ins.address == target_va else "     "
        print(f"{marker}0x{ins.address:08x}: {ins.mnemonic:8s} {ins.op_str}")

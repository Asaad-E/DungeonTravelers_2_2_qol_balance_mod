import struct, sys
sys.path.append('mod_project/tools')
from exe_reader import Exe
import capstone

exe = Exe()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

# Scan vtables
vtables_slot3c = {}
for va in range(0x6c0000, 0x6e0000, 4):
    method = exe.u32(va + 0x3c)
    if method and 0x400000 <= method < 0x600000:
        # check if va looks like a vtable: va - 4 has RTTI CompleteObjectLocator
        col = exe.u32(va - 4)
        if col and 0x630000 <= col < 0x720000:
            td = exe.u32(col + 0xc)
            if td and 0x630000 <= td < 0x720000:
                name = exe.cstring(td + 8)
                if 'Status' in name:
                    vtables_slot3c[va] = (name, method)

print(f"Found {len(vtables_slot3c)} status vtables with slot 0x3c:")
methods = set()
for vt, (name, m) in sorted(vtables_slot3c.items()):
    methods.add(m)
    print(f"  vt {hex(vt)} ({name}): slot 0x3c = {hex(m)}")

print("\nDisassembling unique slot 0x3c methods:")
for m in sorted(methods):
    print(f"--- method {hex(m)}:")
    code = exe.read(m, 32)
    for ins in md.disasm(code, m):
        print(f"    {exe.annotate(ins)}")
        if ins.mnemonic in ['ret', 'jmp']:
            break

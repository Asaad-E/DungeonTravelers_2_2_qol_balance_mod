"""Disassemble around the address of a constant found in the code: exe_around.py ADDR [BEFORE AFTER]. Tries the starts
before the address until the listing passes through an instruction that holds it."""
import os
import sys
import capstone
from exe_reader import Exe

exe = Exe()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
at = int(sys.argv[1], 16)
before = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x40
after = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x60
for start in range(at - before, at - before + 16):
    listing = list(md.disasm(exe.read(start, before + after + 16), start))
    if any(i.address < at < i.address + i.size and i.address + i.size == at + 4 or
           (i.address < at and i.address + i.size >= at + 4 and i.size <= 10) for i in listing):
        for i in listing:
            print(exe.annotate(i))
        break

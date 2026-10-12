"""Disassembles address ranges of the program, each constant it reads noted beside its line.

    python tools/exe_dis.py START END [START END ...]      addresses in hexadecimal
"""
import os
import sys
import struct
import capstone
from exe_reader import Exe

exe = Exe()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def note(ins):
    line = exe.annotate(ins)
    # also annotate immediates that look like floats in mov/push
    return line


args = sys.argv[1:]
for k in range(0, len(args), 2):
    start, end = int(args[k], 16), int(args[k + 1], 16)
    print(f'--- {start:08x} .. {end:08x}')
    code = exe.read(start, end - start + 16)
    for ins in md.disasm(code, start):
        if ins.address > end:
            break
        print(note(ins))

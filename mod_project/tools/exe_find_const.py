"""Where the program holds a 32-bit constant in its code: exe_python mod_project/tools/exe_find_const.py HEX [HEX ...]"""
import struct
import os
import sys
from exe_reader import Exe

exe = Exe()
start, end = 0x401000, 0x640000
code = exe.read(start, end - start)
for arg in sys.argv[1:]:
    needle = struct.pack('<I', int(arg, 16))
    found, at = [], code.find(needle)
    while at >= 0:
        found.append(hex(start + at))
        at = code.find(needle, at + 1)
    print(arg, len(found), ' '.join(found[:60]))

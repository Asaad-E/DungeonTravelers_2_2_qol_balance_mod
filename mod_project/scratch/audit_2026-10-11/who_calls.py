"""The start of the function that holds an address, and who calls it: who_calls.py ADDR [ADDR ...].
The start is the nearest "push ebp; mov ebp, esp" (or a padding of int3 before code) above the address; the callers
are the direct calls (E8) of the code that land on it. Indirect calls through a table are not seen."""
import struct
import sys
sys.path.insert(0, r'C:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project\tools')
from exe_reader import Exe

exe = Exe()
LOW, HIGH = 0x401000, 0x630000
code = exe.read(LOW, HIGH - LOW)
for arg in sys.argv[1:]:
    at = int(arg, 16) - LOW
    start = at
    while start > 0 and not (code[start:start + 3] == bytes([0x55, 0x8b, 0xec]) and code[start - 1] in (0xcc, 0xc3, 0x90)
                             or code[start - 1] == 0xcc and code[start] != 0xcc):
        start -= 1
    target = LOW + start
    callers = []
    k = code.find(b'\xe8')
    while k >= 0:
        if k + 5 <= len(code) and LOW + k + 5 + struct.unpack_from('<i', code, k + 1)[0] == target:
            callers.append(hex(LOW + k))
        k = code.find(b'\xe8', k + 1)
    print(arg, 'function at', hex(target), '| direct callers:', ' '.join(callers) or 'none (called through a table)')

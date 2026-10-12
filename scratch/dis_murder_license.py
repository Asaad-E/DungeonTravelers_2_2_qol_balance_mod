import sys
sys.path.append('mod_project/tools')
from exe_reader import Exe
import capstone

exe = Exe()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
code = exe.read(0x43735e, 0x160)
for ins in md.disasm(code, 0x43735e):
    print(exe.annotate(ins))

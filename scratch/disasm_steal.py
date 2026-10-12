import sys
import os

sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe

exe = Exe('mod_project/backups/exe/DT22_en_unwrapped.vanilla.exe')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

start = 0x44fde0
ins = exe.disassemble(start, limit=0x4000)
print(f"Total instructions in 0x{start:08x}: {len(ins)}")
with open('mod_project/scratch/steal_disasm.txt', 'w', encoding='utf-8') as f:
    for i in ins:
        f.write(exe.annotate(i) + '\n')
print("Saved disassembly to mod_project/scratch/steal_disasm.txt")

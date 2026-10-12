import sys, os, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('mod_project/tools'))
from exe_reader import Exe
import capstone

exe = Exe('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe')
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

with open('DungeonTravelers2-2_EN/DT22_en_unwrapped.exe', 'rb') as f:
    code = f.read()

# In QuestRankData.bin, offset 0x10 is rew_type.
# Let's search for functions that access [eax + 0x10] or [esi + 0x10] and compare with 5 or jump table.
# Also, let's search for initial bag capacity: 30 (0x1e)!
# Where is 30 (0x1e) stored for inventory capacity?
# Let's search for "cmp eax, 0x1e" or "cmp ..., 30" or initial inventory setup
for val in [30, 35, 40, 45, 50]:
    # Look for instructions with immediate 30, 50
    pass

# Let's check VERDICTS.md for S18:
# "Data in part: quest ranks grant slots, and how many is a plain number. The starting 30 is not in the data read so far"
print("Checking VERDICTS.md notes on S18...")
with open('mod_project/docs/generated/VERDICTS.md', 'r', encoding='utf-8') as f:
    for line in f:
        if 'S18' in line:
            print(line.strip())

import struct, sys
sys.path.append('mod_project/tools')
from exe_reader import Exe

exe = Exe()

# In 0x4854b4, what happened?
# Let's check 0x4854b0 to 0x485c30 very carefully:
# Where did the jump 0x485c05 go?
# Let's inspect the caller of 0x4854b4.
# What function is 0x4854b4 inside?
f_start = exe.function_start(0x4854b4)
print(f"Function containing 0x4854b4: {hex(f_start)}")

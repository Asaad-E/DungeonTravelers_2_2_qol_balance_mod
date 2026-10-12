import sys
sys.path.append('mod_project/tools')
from exe_reader import Exe
import capstone

exe = Exe()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
# Let's search for xrefs to vector at 0x8c:
# Specifically, where are enemy passives loaded?
# Let's look at CGameEnemyStatus initialization or battle setup.
# In CGameEnemyStatus constructor (0x4f0530), we saw:
# lea esi, [edi + 0x8c]
# Where is this vector populated?
# Let's search for calls to std::vector::push_back on [edi + 0x8c] or [esi + 0x8c]
# or where EnemyStatusData passives array (0xF4) is read!
p = exe.find_strings('EnemyStatusData')
print('EnemyStatusData strings:', [(hex(va), s) for va, s in p])

# Where is file offset 0xF0 / 0xF4 of EnemyStatusData accessed in code?
# In memory, EnemyStatusData is shifted by +0x18, so 0xF0 becomes 0x108, 0xF4 becomes 0x10C!
# Let's search for instructions with "+ 0x108" or "+ 0x10c"
text_name, text_va, text_vsize, text_raw, text_rsize = exe.text
code = exe.data[text_raw:text_raw + text_rsize]
hits = []
for ins in md.disasm(code, text_va):
    if any(x in ins.op_str for x in ['+ 0x108', '+ 0x10c', '+ 0xf0', '+ 0xf4']):
        hits.append((ins.address, ins.mnemonic, ins.op_str))

print(f"Hits with these offsets: {len(hits)}")
for addr, mnem, op in hits[:15]:
    print(hex(addr), mnem, op)

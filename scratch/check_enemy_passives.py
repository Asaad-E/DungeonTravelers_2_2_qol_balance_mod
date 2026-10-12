import struct, sys
sys.path.append('mod_project/tools')
from exe_reader import Exe

exe = Exe()
# How are passives loaded onto CGameEnemyStatus?
# Let's check xrefs to EnemyStatusData offset 0xF8 (passives count) or 0xFC (passives array)
# Or where EnemyAttackData passives are iterated:
# In EnemyStatusData, passives list is at file offset 0xF8 / 0xFC (or similar).
# Let's check tools/enemy_data.py to see where passives are in EnemyStatusData!
with open('mod_project/tools/enemy_data.py', 'r') as f:
    print(f.read()[:1000])

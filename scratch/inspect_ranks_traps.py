import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

wr_pck = PckArchive('mod_project/backups/WeaponRankData.pck')
print(f"WeaponRankData count: {len(wr_pck.files)}")
fn, data = wr_pck.files[0]
floats = [struct.unpack('<f', data[i:i+4])[0] for i in range(0, len(data), 4)]
print("WeaponRank delays:", [round(f, 2) for f in floats])

trap_pck = PckArchive('mod_project/backups/TrapData.pck')
print(f"\nTrapData count: {len(trap_pck.files)}")
for i, (fn, data) in enumerate(trap_pck.files):
    tid = struct.unpack('<i', data[0:4])[0]
    p_name = struct.unpack('<Q', data[8:16])[0]
    status_id = struct.unpack('<i', data[16:20])[0]
    rate = struct.unpack('<f', data[20:24])[0]
    scope = struct.unpack('<i', data[28:32])[0]
    name = data[p_name:data.find(b'\x00', p_name)].decode('latin-1')
    print(f"Trap {tid}: {name:<16} | Status: {status_id:<4} | Rate: {rate:.2f} | Scope: {scope}")

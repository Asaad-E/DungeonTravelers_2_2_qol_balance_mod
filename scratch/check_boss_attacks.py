import struct, sys
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
import enemy_data

enemies = {e['id']: e for e in enemy_data.enemies()}
target_ids = [444, 619, 1023]

pck = PckArchive('mod_project/backups/EnemyAttackData.pck')
attacks = {}
for fn, b in pck.files:
    a_id = struct.unpack_from('<I', b, 0)[0]
    name_off = struct.unpack_from('<I', b, 8)[0]
    name = b[name_off:b.find(b'\x00', name_off)].decode('latin-1')
    attacks[a_id] = (name, b)

for tid in target_ids:
    e = enemies[tid]
    print(f"\nEnemy {tid}: {e['name']}")
    print(f"  Passives: {e.get('passives')}")
    for p_id in e.get('passives', []):
        if p_id in attacks:
            name, b = attacks[p_id]
            print(f"    Passive {p_id} ({name}):")
            for k in range(5):
                eff = struct.unpack_from('<i', b, 0x4C + 12*k)[0]
                val = struct.unpack_from('<f', b, 0x50 + 12*k)[0]
                kind = struct.unpack_from('<i', b, 0x54 + 12*k)[0]
                if eff != -1:
                    print(f"      Slot {k}: eff={eff}, val={val}, kind={kind}")
    print(f"  Attacks: {e.get('attacks')}")
    for a_id in e.get('attacks', []):
        if a_id in attacks:
            name, b = attacks[a_id]
            # check if any effect is 319
            for k in range(5):
                eff = struct.unpack_from('<i', b, 0x4C + 12*k)[0]
                val = struct.unpack_from('<f', b, 0x50 + 12*k)[0]
                kind = struct.unpack_from('<i', b, 0x54 + 12*k)[0]
                if eff == 319 or eff != -1:
                    if eff == 319:
                        print(f"    Attack {a_id} ({name}) HAS EFFECT 319! val={val}, kind={kind}")

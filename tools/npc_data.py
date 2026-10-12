"""
Guest allies: reader of Data/ENG/NPC/NPC.pck (backed up in backups/NPC/).

The program calls them NPC (CContentsManager::_InitializeNPC, 0x463420; table global 0x738a04). NPC.pck holds one
archive per ally and per stage of its growth, with:
    NPCData.bin      the record below
    NPCAIData.bin    its behaviour, in the format of the enemies (tools/enemy_ai.py decodes it)
    Data.txt         NPCID, CharacterID, DLC
    NPCVoiceData.bin

NPCData (little endian), as the code reads it (the stats at 0x4fed59 - 0x4fee27):
    0x00 id                 0x08 pointer to the name        0x10 character id (the model; shared by the stages)
    0x18 level              0x1C a small int, 0 to 11 (by its place and range the weapon rank index of a summon;
                            not followed in code)
    0x20 six ints: ATK DEF INT RES DEX AGI. The stat of the unit is this figure plus bonuses of the unit object
    0x38 number of attacks, 0x3C their ids (EnemyAttackData), eight bytes each, up to eleven
    0x94 a kind (0, 1, 2) and 0x98 one more EnemyAttackData id or -1 (read at 0x4a33f0 and 0x4ff2bb; not followed)
    0xAC max HP (400 to 9,999; its readers are the status screens)
    0xB0, 0xB4 two ints not identified; 0xC8 - 0xD4 four ints of where its picture sits

    python tools/npc_data.py        prints every guest ally
"""
import os
import struct
import sys

import enemy_ai
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPC_PCK = os.path.join(BASE_DIR, 'backups', 'NPC', 'NPC.pck')
STATS = ('atk', 'def', 'int', 'res', 'dex', 'agi')
ATTACK_COUNT, ATTACK_IDS, ATTACK_SLOTS = 0x38, 0x3C, 11


def read_npc(blob):
    b = bytes(blob)
    i = lambda offset: struct.unpack_from('<i', b, offset)[0]
    name_at = struct.unpack_from('<Q', b, 0x08)[0]
    count = max(0, min(i(ATTACK_COUNT), ATTACK_SLOTS))
    npc = {'id': i(0x00), 'character': i(0x10), 'level': i(0x18), 'raw_1c': i(0x1C),
           'name': b[name_at:b.index(b'\x00', name_at)].decode('utf-8', 'replace'),
           'attacks': [i(ATTACK_IDS + 8 * k) for k in range(count)],
           'kind': i(0x94), 'extra_attack': i(0x98) if i(0x98) != -1 else None, 'hp': i(0xAC)}
    npc.update(zip(STATS, struct.unpack_from('<6i', b, 0x20)))
    return npc


def npcs(path=NPC_PCK):
    """Every guest ally as a dict, with its decoded AI script under 'script'."""
    found = []
    for _, blob in PckArchive(path).files:
        inner = dict(PckArchive.from_bytes(blob).files)
        npc = read_npc(inner['NPCData.bin'])
        npc['script'] = enemy_ai.decode(inner['NPCAIData.bin'])
        found.append(npc)
    return sorted(found, key=lambda n: n['id'])


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for n in npcs():
        print(f"{n['id']:3d} {n['name']:16s} L{n['level']:2d} HP {n['hp']:5d} " + ' '.join(f"{k.upper()} {n[k]}" for k in STATS)
              + f"  attacks {len(n['attacks'])}  sets {len(n['script']['sets'])}")


if __name__ == '__main__':
    main()

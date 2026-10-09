"""
Summoned units: reader of Data/ENG/Summon/Summon.pck (backed up in backups/Summon/).

Summon.pck holds one archive per form of a summon, with:
    SummonData.bin     the record below
    SummonAIData.bin   its behaviour, in the format of the enemies (tools/enemy_ai.py decodes it)
    Data.txt           SummonID, CharacterID, DLC
    SummonVoiceData.bin

SummonData (little endian), read by 0x4ffc90 (docs/FORMULAS.md 11):
    0x00 id of the form            0x10 character id (the model)
    0x14 the enemy the summon is (EnemyData id): the base figure of its stats; the forms of one summon share it
         (atwiki dt2-2 page 105 measures the lowest stats of Bigfoot, Ghast and Cupid: enemies 833, 913 and 754)
    0x18 level of the form: the form used is the last of the family whose level is not above the average
         level of the party
    0x20 weapon rank index: its weight in the order of turns comes from WeaponRankData, like a weapon
    0x24 six floats, ATK DEF INT RES DEX AGI: each stat is the best "stat of a party member * float", and not
         below the base figure of the form
    0x3C number of attacks, 0x40 their ids (EnemyAttackData), eight bytes each
    0x98 a kind and 0x9C the id of a passive skill (EnemyAttackData) or -1, as in a guest ally (tools/npc_data.py)
    the name is the last string of the record

    python mod_project/tools/summon_data.py        prints every form
"""
import os
import struct
import sys

import enemy_ai
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUMMON_PCK = os.path.join(BASE_DIR, 'backups', 'Summon', 'Summon.pck')
STATS = ('atk', 'def', 'int', 'res', 'dex', 'agi')


def read_summon(blob):
    b = bytes(blob)
    count = struct.unpack_from('<i', b, 0x3C)[0]
    strings = [t.decode('utf-8', 'replace') for t in b[0x40 + 8 * 12:].split(b'\x00') if t]
    printable = [t for t in strings if len(t) > 2 and all(32 <= ord(c) < 0x3000 for c in t)]
    return {'id': struct.unpack_from('<i', b, 0x00)[0], 'character': struct.unpack_from('<i', b, 0x10)[0],
            'family': struct.unpack_from('<i', b, 0x14)[0], 'enemy': struct.unpack_from('<i', b, 0x14)[0],
            'level': struct.unpack_from('<i', b, 0x18)[0],
            'rank': struct.unpack_from('<i', b, 0x20)[0],
            'factors': dict(zip(STATS, struct.unpack_from('<6f', b, 0x24))),
            'attacks': [struct.unpack_from('<i', b, 0x40 + 8 * k)[0] for k in range(max(count, 0))],
            'passive': struct.unpack_from('<i', b, 0x9C)[0] if struct.unpack_from('<i', b, 0x9C)[0] != -1 else None,
            'name': printable[-1] if printable else ''}


def summons(path=SUMMON_PCK):
    """Every form as a dict, with its decoded AI script under 'script'."""
    found = []
    for _, blob in PckArchive(path).files:
        inner = dict(PckArchive.from_bytes(blob).files)
        summon = read_summon(inner['SummonData.bin'])
        summon['script'] = enemy_ai.decode(inner['SummonAIData.bin'])
        found.append(summon)
    return sorted(found, key=lambda s: s['id'])


def form_for(family, average_level, forms):
    """The form of a family a party of this average level gets (0x4ffd8a - 0x4ffe13)."""
    own = [s for s in forms if s['family'] == family]
    chosen = own[0]
    for nxt in own[1:]:
        if average_level < nxt['level']:
            break
        chosen = nxt
    return chosen


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    for s in summons():
        factors = ' '.join(f"{k} {v:.2f}" for k, v in s['factors'].items())
        print(f"{s['id']:3d}  {s['name']:22s} family {s['family']:4d}  Lv {s['level']:2d}  rank {s['rank']:2d}  {factors}  attacks {len(s['attacks'])}")


if __name__ == '__main__':
    main()

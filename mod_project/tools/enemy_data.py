"""
Enemies of the game: reader of Data/ENG/Enemy/Enemy.pck (backed up in backups/Enemy/).

Enemy.pck holds one entry per enemy, itself an archive with:
    EnemyStatusData.bin   stats, resistances, drops, attack list, name and habitat
    EnemyAIData.bin       behaviour, variable length, ends in 0xFF
    EnemyVoiceData.bin    only some enemies

EnemyStatusData (little endian; evidence: the enemy screen of Medic and Selene, 2026-10-04):
    0x00 id            0x08 name pointer        0x10 race
    0x14 level         0x18 max HP              0x1C ATK   0x20 DEF   0x24 INT
    0x28 RES           0x2C DEX                 0x30 AGI   0x34 EXP   0x38 gold
    0x3C flags         0x40 float               0x44 float
    0x48 eight resistances: slash, stab, bash, fire, water, wind, earth, lightning
         (Selene: 15, 30, 0, 10, 0, 0, 20, 20, the figures of her status screen)
    0x68..0xA8 drops and materialize (not decoded field by field yet)
    0xAC number of attacks, 0xB0 attack ids (EnemyAttackData), -1 where unused
    0x108 habitat pointer; six ints from 0x110 (not decoded)
"""
import os
import re
import struct
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENEMY_PCK = os.path.join(BASE_DIR, 'backups', 'Enemy', 'Enemy.pck')
STATS = (('level', 0x14), ('hp', 0x18), ('atk', 0x1C), ('def', 0x20), ('int', 0x24), ('res', 0x28),
         ('dex', 0x2C), ('agi', 0x30), ('exp', 0x34), ('gold', 0x38))
RESISTANCES = ('slash', 'stab', 'bash', 'fire', 'water', 'wind', 'earth', 'lightning')
RESIST_OFFSET = 0x48
ATTACK_COUNT, ATTACK_IDS, ATTACK_SLOTS = 0xAC, 0xB0, 16


def cstring(b, pointer):
    return bytes(b[pointer:b.find(b'\x00', pointer)]).decode('utf-8', 'replace') if 0 < pointer < len(b) else ''


def read_status(b):
    b = bytes(b)
    enemy = {'id': struct.unpack_from('<i', b, 0)[0], 'race': struct.unpack_from('<i', b, 0x10)[0],
             'name': cstring(b, struct.unpack_from('<Q', b, 0x08)[0]),
             'habitat': cstring(b, struct.unpack_from('<Q', b, 0x108)[0]),
             'flags': struct.unpack_from('<I', b, 0x3C)[0],
             'f40': struct.unpack_from('<f', b, 0x40)[0], 'f44': struct.unpack_from('<f', b, 0x44)[0]}
    for key, off in STATS:
        enemy[key] = struct.unpack_from('<i', b, off)[0]
    for k, key in enumerate(RESISTANCES):
        enemy['res_' + key] = struct.unpack_from('<i', b, RESIST_OFFSET + 4 * k)[0]
    count = struct.unpack_from('<i', b, ATTACK_COUNT)[0]
    enemy['attacks'] = [a for a in struct.unpack_from(f'<{ATTACK_SLOTS}i', b, ATTACK_IDS) if a != -1][:max(count, 0)]
    enemy['raw_68'] = list(struct.unpack_from('<17i', b, 0x68))
    enemy['raw_f0'] = list(struct.unpack_from('<6i', b, 0xF0))
    enemy['raw_110'] = list(struct.unpack_from('<6i', b, 0x110))
    return enemy


def enemies(path=ENEMY_PCK):
    """Every enemy as a dict, with its AI bytes and the name of its entry."""
    found = []
    for fn, b in PckArchive(path).files:
        inner = dict(PckArchive.from_bytes(b).files)
        enemy = read_status(inner['EnemyStatusData.bin'])
        enemy['entry'] = fn
        enemy['ai'] = bytes(inner.get('EnemyAIData.bin', b''))
        enemy['size'] = len(inner['EnemyStatusData.bin'])
        found.append(enemy)
    return found

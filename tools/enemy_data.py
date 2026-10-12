"""
Enemies of the game: reader of Data/ENG/Enemy/Enemy.pck (backed up in backups/Enemy/).

Enemy.pck holds one entry per enemy, itself an archive with:
    EnemyStatusData.bin   stats, resistances, drops, attack list, name and habitat
    EnemyAIData.bin       behaviour, variable length, ends in 0xFF
    EnemyVoiceData.bin    only some enemies

EnemyStatusData (little endian; evidence: the enemy screen of Medic and Selene, 2026-10-04):
    0x00 id            0x08 name pointer        0x10 race (RACES: the value each "attack vs." enchantment tests,
                                                         helpers 0x557d40 - 0x557ec0; 1 and 3 have no such enchantment)
    0x14 level         0x18 max HP              0x1C ATK   0x20 DEF   0x24 INT
    0x28 RES           0x2C DEX                 0x30 AGI   0x34 EXP   0x38 gold
    0x3C flags: one bit per ailment the enemy cannot receive (IMMUNITY_BITS; each ailment command tests its bit,
                       for example poison at 0x5580c0); bit 13 marks an adult (actions with effect 149 or
                       150, 0x44b047); bit 14 allows snackification; bit 15 allows Item
                      Steal (0x4503c5: without it "You can't steal from this monster!"); bits 0, 1 not decoded
                       0x40 swing: spread of its damage (docs/FORMULAS.md 2.2)
                       0x44 weight: its term in the order of turns (docs/FORMULAS.md 5)
    0x48 eight resistances: slash, stab, bash, fire, water, wind, earth, lightning
         (Selene: 15, 30, 0, 10, 0, 0, 20, 20, the figures of her status screen)
    0x68 number of items it can drop (0 to 2), then (item id, chance in percent) at 0x6C and 0x74
         (the result of a battle walks them, 0x445db1)
    0x7C chance in percent of its third drop, the one enchantment 276 (Equipment drop rate UP) adds 20 to per piece,
         and 0x80 the number that drop is drawn with (0x558517). One weighted roll (0x558180) picks among the
         two items, this drop and nothing; Treasure Hunt adds to every chance above 0 (docs/FORMULAS.md 12.11)
    0x84 the slots of that drop, three words each: 0 a fixed piece or 1 the table of the zone, the id of the piece or
         the kind of the table, a weight (0x558517 - 0x5586fa). Nothing else is "what can be stolen": a steal that
         succeeds runs the same draw without its "nothing" (docs/FORMULAS.md 12.16)
    0x90..0xA4 two more groups of flag, id, chance; not identified
    0xA8 the item it becomes when turned into a snack (0x48151f)
    0xAC number of attacks, 0xB0 attack ids (EnemyAttackData), -1 where unused
    0xF0 number of passive skills (0 to 5), 0xF4 their ids: entries of EnemyAttackData whose text says
         "Passive Skill" (Auto-Recovery, Avenger, Mind's Eye, Heretic Samsara and the like)
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
RACES = {0: 'Fruit', 2: 'Beasts', 4: 'Humans', 5: 'Undead', 6: 'Magic Beings', 7: 'Apparitions', 8: 'Demons', 9: 'Dragons'}
IMMUNITY_BITS = {2: 'stun', 3: 'sleep', 4: 'silence', 5: 'petrification', 6: 'instant death', 7: 'freeze', 8: 'poison',
                 9: 'paralysis', 10: 'shadow sew', 11: 'slow', 12: 'turn delay'}
STEAL_BIT = 15          # set when Item Steal works on the enemy (0x4503c5)
SNACK_BIT = 14          # set when the enemy can be turned into a snack (0x481488: the other way round)


def cstring(b, pointer):
    return bytes(b[pointer:b.find(b'\x00', pointer)]).decode('utf-8', 'replace') if 0 < pointer < len(b) else ''


def read_status(b):
    b = bytes(b)
    enemy = {'id': struct.unpack_from('<i', b, 0)[0], 'race': struct.unpack_from('<i', b, 0x10)[0],
             'name': cstring(b, struct.unpack_from('<Q', b, 0x08)[0]),
             'habitat': cstring(b, struct.unpack_from('<Q', b, 0x108)[0]),
             'flags': struct.unpack_from('<I', b, 0x3C)[0],
             'swing': struct.unpack_from('<f', b, 0x40)[0], 'weight': struct.unpack_from('<f', b, 0x44)[0]}
    enemy['race_name'] = RACES.get(enemy['race'], f"race {enemy['race']}")
    enemy['immune'] = [name for bit, name in IMMUNITY_BITS.items() if enemy['flags'] >> bit & 1]
    enemy['snack'] = bool(enemy['flags'] >> SNACK_BIT & 1)
    for key, off in STATS:
        enemy[key] = struct.unpack_from('<i', b, off)[0]
    for k, key in enumerate(RESISTANCES):
        enemy['res_' + key] = struct.unpack_from('<i', b, RESIST_OFFSET + 4 * k)[0]
    count = struct.unpack_from('<i', b, ATTACK_COUNT)[0]
    enemy['attacks'] = [a for a in struct.unpack_from(f'<{ATTACK_SLOTS}i', b, ATTACK_IDS) if a != -1][:max(count, 0)]
    enemy['raw_68'] = list(struct.unpack_from('<17i', b, 0x68))
    raw = enemy['raw_68']
    enemy['drops'] = [(raw[1 + 2 * k], raw[2 + 2 * k]) for k in range(max(0, min(raw[0], 2))) if raw[1 + 2 * k] != -1]
    enemy['equipment_drop'] = (raw[5], raw[6])        # chance in percent, how many slots it is drawn among
    # the slots (0x558517 - 0x5586fa): (0 a fixed piece | 1 the table of the zone, piece id | kind of the table, weight)
    enemy['equipment_slots'] = [tuple(raw[7 + 3 * k:10 + 3 * k]) for k in range(max(0, min(raw[6], 3)))]
    enemy['can_steal'] = bool(enemy['flags'] >> STEAL_BIT & 1)
    enemy['snack_item'] = raw[16] if raw[16] != -1 else None
    enemy['raw_f0'] = list(struct.unpack_from('<6i', b, 0xF0))
    enemy['passives'] = [a for a in enemy['raw_f0'][1:1 + max(0, min(enemy['raw_f0'][0], 5))] if a != -1]
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

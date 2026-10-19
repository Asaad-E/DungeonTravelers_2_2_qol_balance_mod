"""
The values of the Balance variant: every live row of data_tables/balance_changes.xlsx written into a copy of the
original packs. Step 1 of "build_variant.py balance"; the texts are built on top of what this step leaves.

    python tools/balance_values.py            writes build/balance/base/ and checks it
    python tools/balance_values.py --check    checks the folder that is there

A row is one value of one record. Each kind of row has its address here, with the reader that gives it:

    skills        Technique / Magic / PassiveSkillData (tools/extract_vanilla.py SKILL_LAYOUTS): TP cost, SP cost, speed
                  and chant speed by level, the value of an effect slot by level, the weapon codes, an effect added to
                  an empty slot
    enemies       Enemy.pck, EnemyStatusData of the enemy (tools/enemy_data.py): stats, resistances, immunity flags,
                  passive ids, the chance of the equipment drop; EnemyAIData: the weights of a set
    attacks       EnemyAttackData: the value of an effect slot (0x50 + 12 * slot)
    sp_curve      LvExpSkptData: skill points of a level (0x08)
    equipment     EquipmentData: ATK 0x24, upgrade rate 0x3C, class mask 0x40, innate enchantments 0x5C (count), 0x60
    sealbooks     SealScrollData: number of enchantments 0x1C and their ids 0x20
    items         ItemData: the value of one of its four pairs (type, value) from 0x24, named by its type
    unique        UniqueSkillData: the value of a rank, ten floats from 0x1C (the tenth is the crown value); the id of
                  its effect 0x50
    party_skills  PartySkillData: the id of its effect 0x4C (the size of a bonus is the program's, by effect)
    npcs          NPC.pck, NPCData of a guest ally at one stage of her growth (tools/npc_data.py): one of the six
                  stats from 0x20; NPCAIData: the weights of a set of her script
    summons       Summon.pck, SummonData of one form of a summon (tools/summon_data.py): one of the six factors of its
                  stats from 0x24; SummonAIData: the weights of a set of its script
    enchantments  EnchantData: the flags word 0x20
    quests        QuestData: the amount 0x40 of a quest whose reward is gold (kind 3 at 0x38)
    zones         a floor file of Dungeon/stNN/Data.pck: one of the chances of a wandering shop of a zone. These packs
                  are not copied nor built: the row is checked here against the floor file kept in backups/ and written
                  in place at install time (tools/floor_patch.py)

Rules of the step (docs/philosophy.md 2.5):
  * before a value is written, what the original holds there is compared with the column Vanilla of the row; a
    mismatch refuses the row;
  * a row this step cannot write as it stands is refused with its reason, never skipped in silence: the build stops;
  * only the bytes of the field change. check() reads the result against the originals byte by byte and wants every
    differing byte inside a field a row wrote, and every field a row wrote to hold its new value.
Rows in state "blocked" are not of the variant (gamedata/variant.py leaves them out too): a row that cannot be written, with
its reason in the column Why, waiting for a decision.
"""
import os
import re
import shutil
import struct
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import openpyxl                                          # noqa: E402
import enemy_ai                                          # noqa: E402
import enemy_data                                        # noqa: E402
import npc_data                                          # noqa: E402
import summon_data                                       # noqa: E402
from extract_vanilla import SKILL_LAYOUTS, SLOT_SIZE, LEVELS, looks_float      # noqa: E402
from pck_handler import PckArchive                       # noqa: E402

BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
CHANGES = os.path.join(BASE_DIR, 'data_tables', 'balance_changes.xlsx')
OUT_DIR = os.path.join(BASE_DIR, 'build', 'balance', 'base')
LIVE = ('decided', 'built', 'checked')
ENEMY_PCK = os.path.join('Enemy', 'Enemy.pck')
STATUS, AI = 'EnemyStatusData.bin', 'EnemyAIData.bin'
from game_profile import layout                          # noqa: E402  (data_tables/record_layouts.json)
_L = {name: layout(name) for name in ('NPCData', 'EnemyStatusData', 'EnemyAttackData', 'EquipmentData', 'SealScrollData',
                                      'PartySkillData', 'UniqueSkillData', 'ItemData', 'EnchantData', 'LvExpSkptData',
                                      'QuestData')}
NPC_PCK, NPC_RECORD, NPC_AI = os.path.join('NPC', 'NPC.pck'), 'NPCData.bin', 'NPCAIData.bin'
NPC_ID, NPC_STATS = _L['NPCData']['id'], _L['NPCData']['stats']
SUMMON_PCK, SUMMON_RECORD, SUMMON_AI = os.path.join('Summon', 'Summon.pck'), 'SummonData.bin', 'SummonAIData.bin'
NESTED_PCKS = (ENEMY_PCK, NPC_PCK, SUMMON_PCK)      # packs of a subfolder whose entries are archives themselves
FLOAT_TOLERANCE = 5e-5                    # the workbook holds floats rounded to four decimals
ENEMY_STATS = dict(enemy_data.STATS)
_E = _L['EnemyStatusData']
ENEMY_FLAGS, ENEMY_EQUIPMENT_DROP, ENEMY_PASSIVE_COUNT, ENEMY_PASSIVES = (_E['flags'], _E['equipment_drop'],
                                                                         _E['passive_count'], _E['passives'])
ENEMY_EQUIPMENT_SLOTS, ENEMY_EQUIPMENT_SLOT = _E['equipment_slots'], _E['equipment_slot_size']     # a count, then (zone table or fixed piece, id or kind, weight)
ATTACK_COUNT, ATTACK_SLOTS, ATTACK_SLOT = (_L['EnemyAttackData']['slot_count'], _L['EnemyAttackData']['slots'],
                                           _L['EnemyAttackData']['slot_size'])
_Q = _L['EquipmentData']
EQUIPMENT = {'ATK (base)': (_Q['atk'], 'i'), 'upgrade rate': (_Q['upgrade_rate'], 'f'), 'class bitmask': (_Q['class_mask'], 'I')}
EQUIPMENT_ENCHANT_COUNT, EQUIPMENT_ENCHANTS, EQUIPMENT_ENCHANT_SLOTS = _Q['enchant_count'], _Q['enchants'], _Q['enchant_slots']
SEAL_COUNT, SEAL_ENCHANTS, SEAL_SLOTS = (_L['SealScrollData']['count'], _L['SealScrollData']['enchants'],
                                        _L['SealScrollData']['slots'])
PARTY_EFFECT = _L['PartySkillData']['effect']                              # the effect a party skill gives its members (tools/text_checks.py)
UNIQUE_EFFECT = _L['UniqueSkillData']['effect']                             # the effect of a unique skill (docs/FORMULAS.md 12.19)
UNIQUE_VALUES, UNIQUE_RANKS = _L['UniqueSkillData']['values'], _L['UniqueSkillData']['ranks']           # the ten values of a unique skill (tools/extract_vanilla.py)
ITEM_PAIRS, ITEM_PAIR_COUNT = _L['ItemData']['pairs'], _L['ItemData']['pair_count']            # (type int, value float) pairs of an item (tools/text_checks.py)
ENCHANT_FLAGS = _L['EnchantData']['flags']
SP_LEVEL, SP_POINTS = _L['LvExpSkptData']['level'], _L['LvExpSkptData']['points']
# QuestData: the kind of the reward (0x55e210 - 0x55e2a0 test it against 0, 1, 2, 3) and its amount (0x55e300);
# kind 3 hands the amount to the party at once (0x5959ac - 0x5959ce): gold. Kind 2 is experience (window 0x448c60)
QUEST_KIND, QUEST_AMOUNT, QUEST_GOLD = _L['QuestData']['kind'], _L['QuestData']['amount'], _L['QuestData']['gold_kind']
SKILL_ARRAYS = {'TP cost': 'tp', 'SP cost': 'sp', 'speed factor': 'speed', 'chant speed factor': 'cast', 'turns': 'turns'}


class Refused(Exception):
    """A row that cannot be written as it stands."""


def live_rows(path=CHANGES):
    it = openpyxl.load_workbook(path, read_only=True)['Changes'].iter_rows(values_only=True)
    header = next(it)
    return [row for row in (dict(zip(header, r)) for r in it if r and r[0] is not None) if row['State'] in LIVE]


def same(a, b):
    try:
        return abs(float(a) - float(b)) <= FLOAT_TOLERANCE
    except (TypeError, ValueError):
        try:
            return int(str(a), 16) == int(str(b), 16)
        except (TypeError, ValueError):
            return str(a).strip() == str(b).strip()


def number(value):
    """A value of the workbook as a number: '0x16e7' is read as hexadecimal."""
    if isinstance(value, str):
        return int(value, 16) if value.strip().lower().startswith('0x') else float(value)
    return value


class Packs:
    """The original packs, opened on demand and changed in memory; the fields written are kept in a ledger."""

    def __init__(self, backup_dir=BACKUP_DIR):
        self.backup_dir = backup_dir
        self.archives = {}            # relative path -> PckArchive
        self.inner = {}               # (relative path, entry) -> PckArchive of an entry that is itself an archive
        self.ledger = []              # (pack, entry, inner entry or None, offset, size, new bytes, row id)
        self.claimed = {}             # (pack, entry, inner, offset) -> row id

    def archive(self, pack):
        if pack not in self.archives:
            self.archives[pack] = PckArchive(os.path.join(self.backup_dir, pack))
        return self.archives[pack]

    def entry(self, pack, name, inner=None):
        """The bytes of an entry, to change in place. inner: an entry of the archive that entry is (Enemy.pck)."""
        found = next((b for fn, b in self.archive(pack).files if fn == name), None)
        if found is None:
            raise Refused(f'{pack} has no entry {name}')
        if inner is None:
            return found
        key = (pack, name)
        if key not in self.inner:
            self.inner[key] = PckArchive.from_bytes(found, name)
        buf = next((b for fn, b in self.inner[key].files if fn == inner), None)
        if buf is None:
            raise Refused(f'{name} of {pack} has no {inner}')
        return buf

    def read(self, where, fmt):
        pack, name, inner, offset = where
        return struct.unpack_from('<' + fmt, self.entry(pack, name, inner), offset)[0]

    def write(self, row, where, fmt, new, vanilla=None):
        """Writes one field. vanilla: what the row says the original holds there (the column Vanilla when None)."""
        pack, name, inner, offset = where
        if where in self.claimed:
            raise Refused(f'the field is already written by row {self.claimed[where]}')
        buf = self.entry(pack, name, inner)
        current = struct.unpack_from('<' + fmt, buf, offset)[0]
        expected = row['Vanilla'] if vanilla is None else vanilla
        if not same(expected, current):
            raise Refused(f'the original holds {current}, the row says {expected}')
        if fmt != 'f' and float(new) != int(new):
            raise Refused(f'the field is a whole number and the row asks for {new}')
        packed = struct.pack('<' + fmt, float(new) if fmt == 'f' else int(new))
        buf[offset:offset + len(packed)] = packed
        self.claimed[where] = row['ID']
        self.ledger.append((pack, name, inner, offset, len(packed), packed, row['ID']))

    def write_bytes(self, row, where, old, new):
        """Writes a run of bytes whose original content is known exactly (a set of weights of an AI script)."""
        pack, name, inner, offset = where
        buf = self.entry(pack, name, inner)
        if bytes(buf[offset:offset + len(old)]) != bytes(old):
            raise Refused('the original bytes are not the ones expected')
        buf[offset:offset + len(new)] = new
        self.claimed[where] = row['ID']
        self.ledger.append((pack, name, inner, offset, len(new), bytes(new), row['ID']))

    def save(self, out_dir):
        """Every original pack copied to out_dir, the changed ones rebuilt from memory."""
        if os.path.isdir(out_dir):
            shutil.rmtree(out_dir)
        for pack in NESTED_PCKS:
            os.makedirs(os.path.dirname(os.path.join(out_dir, pack)))
        for (pack, name), archive in self.inner.items():
            entry = next(b for fn, b in self.archive(pack).files if fn == name)
            entry[:] = archive.build()
        written = []
        for name in sorted(os.listdir(self.backup_dir)):
            if name.endswith('.pck'):
                written.append(name)
        written += NESTED_PCKS
        for pack in written:
            target = os.path.join(out_dir, pack)
            if pack in self.archives:
                self.archives[pack].save(target)
            else:
                shutil.copyfile(os.path.join(self.backup_dir, pack), target)
        return written


# --- the address of each kind of row ---------------------------------------------------------------------------
def array_format(buf, offset):
    """'f' or 'i' for a table of ten words, as tools/extract_vanilla.py read_array decides it."""
    raw = struct.unpack_from(f'<{LEVELS}i', buf, offset)
    return 'f' if any(looks_float(v) for v in raw) else 'i'


def effect_id(field):
    found = re.search(r'effect (\d+)', field)
    if not found:
        raise Refused(f'no effect id in the field {field!r}')
    return int(found.group(1))


def skill_row(packs, row):
    category, sid = str(row['Record']).split()[0], int(str(row['Record']).split()[1])
    if category not in SKILL_LAYOUTS:
        raise Refused(f'unknown skill category {category}')
    lay = SKILL_LAYOUTS[category]
    pack, name = lay['pck'], f'{category}SkillData_{sid:04d}.bin'
    buf = packs.entry(pack, name)
    field, level = str(row['Field']), row['Level']
    if field in SKILL_ARRAYS:
        key = SKILL_ARRAYS[field]
        if key not in lay:
            raise Refused(f'a {category} skill has no {field}')
        base = lay[key]
        packs.write(row, (pack, name, None, base + 4 * (int(level) - 1)), array_format(buf, base), row['New'])
    elif field == 'weapon codes':
        new = [int(x) for x in str(row['New']).split(',')]
        old = [int(x) for x in str(row['Vanilla']).split(',')]
        if 'weapon' not in lay:
            raise Refused(f'a {category} skill holds one weapon code (0x54): it cannot ask for {len(new)} weapons')
        count, first, second = lay['weapon']
        if len(new) > 2:
            raise Refused('a technique holds two weapon codes at most')
        packs.write(row, (pack, name, None, count), 'i', len(new), vanilla=len(old))
        for k, offset in enumerate((first, second)):
            packs.write(row, (pack, name, None, offset), 'i', new[k] if k < len(new) else -1,
                        vanilla=old[k] if k < len(old) else -1)
    elif field.startswith('added effect'):
        eid, kind = effect_id(field), int(field.split('kind')[1].strip(' )'))
        values = [float(v) for v in str(row['New']).split(',')]
        used = struct.unpack_from('<i', buf, lay['count'])[0]
        if used >= lay['n_slots'] or len(values) != LEVELS:
            raise Refused('no empty effect slot, or not ten values')
        slot = lay['slots'] + used * SLOT_SIZE
        packs.write(row, (pack, name, None, slot), 'i', eid, vanilla=-1)
        for k, value in enumerate(values):             # an empty slot holds -1 in every word; a value is a float
            packs.write_bytes(row, (pack, name, None, slot + 4 + 4 * k), struct.pack('<i', -1), struct.pack('<f', value))
        packs.write(row, (pack, name, None, slot + 4 + 4 * LEVELS), 'i', kind, vanilla=-1)
        packs.write(row, (pack, name, None, lay['count']), 'i', used + 1, vanilla=used)
    elif 'effect' in field:
        eid = effect_id(field)
        used = struct.unpack_from('<i', buf, lay['count'])[0]
        slots = [lay['slots'] + k * SLOT_SIZE for k in range(used)]
        slot = next((s for s in slots if struct.unpack_from('<i', buf, s)[0] == eid), None)
        if slot is None:
            raise Refused(f'{name} has no effect {eid}')
        packs.write(row, (pack, name, None, slot + 4 + 4 * (int(level) - 1)), array_format(buf, slot + 4), row['New'])
    else:
        raise Refused(f'unknown skill field {field!r}')


def enemy_row(packs, row):
    eid = int(str(row['Record']).split()[0])
    name, field = f'{eid:04d}.pck', str(row['Field'])
    if not any(fn == name for fn, _ in packs.archive(ENEMY_PCK).files):
        name = f'{eid}.pck'
    where = lambda offset: (ENEMY_PCK, name, STATUS, offset)            # noqa: E731
    if field in ENEMY_STATS:
        packs.write(row, where(ENEMY_STATS[field]), 'i', row['New'])
    elif field.startswith('resistance '):
        index = enemy_data.RESISTANCES.index(field.split()[1])
        packs.write(row, where(enemy_data.RESIST_OFFSET + 4 * index), 'i', row['New'])
    elif field.startswith('immunity flags'):
        old, new = int(str(row['Vanilla']), 16), int(str(row['New']), 16)
        decoded = sum(1 << bit for bit in enemy_data.IMMUNITY_BITS)
        if (old ^ new) & ~decoded:
            raise Refused('the row changes a bit of the flags that is not an immunity')       # lever L26
        packs.write(row, where(ENEMY_FLAGS), 'I', new, vanilla=old)
    elif field.startswith('steal flag'):
        # 'steal flag (0x3C bit 15)': Item Steal works on the enemy (0x4503c5). Only that bit may move.
        old, new = int(str(row['Vanilla']), 16), int(str(row['New']), 16)
        if old ^ new != 1 << enemy_data.STEAL_BIT:
            raise Refused('the row changes another bit of the flags than the one of Item Steal')
        packs.write(row, where(ENEMY_FLAGS), 'I', new, vanilla=old)
    elif field.startswith('passive skill id'):
        buf = packs.entry(ENEMY_PCK, name, STATUS)
        count = struct.unpack_from('<i', buf, ENEMY_PASSIVE_COUNT)[0]
        ids = struct.unpack_from('<5i', buf, ENEMY_PASSIVES)[:max(0, min(count, 5))]
        if int(row['Vanilla']) not in ids:
            raise Refused(f"the enemy carries no passive {row['Vanilla']}")
        packs.write(row, where(ENEMY_PASSIVES + 4 * ids.index(int(row['Vanilla']))), 'i', row['New'])
    elif field == 'equipment drop rate':
        packs.write(row, where(ENEMY_EQUIPMENT_DROP), 'i', row['New'])
    elif field.startswith('equipment slot '):
        # 'equipment slot 1 weight (piece 339)': the weight a fixed piece is drawn with once the drop is an equipment
        # (0x558570 - 0x5585a8: one weighted roll over the slots the enemy holds). Only a slot that names a piece.
        slot = int(field.split()[2]) - 1
        buf = packs.entry(ENEMY_PCK, name, STATUS)
        count = struct.unpack_from('<i', buf, ENEMY_EQUIPMENT_SLOTS)[0]
        at = ENEMY_EQUIPMENT_SLOTS + 4 + ENEMY_EQUIPMENT_SLOT * slot
        zone, piece = struct.unpack_from('<2i', buf, at) if 0 <= slot < count else (None, None)
        named = re.search(r'piece (\d+)', field)
        if zone != 0 or named is None or int(named.group(1)) != piece:
            raise Refused(f'slot {slot + 1} of the enemy is not the fixed piece the row names')
        if not 0 < int(row['New']) <= 100:
            raise Refused('a weight outside 1 to 100, what the game holds')
        packs.write(row, where(at + 8), 'i', row['New'])
    elif field.startswith('AI set '):
        number_of_set = int(field.split()[2])
        old_slot, new_slot = (int(re.search(r'slot\s+(\d+)', str(row[c])).group(1)) for c in ('Vanilla', 'New'))
        buf = packs.entry(ENEMY_PCK, name, AI)
        old = [0] * enemy_ai.WEIGHTS
        old[old_slot] = 100
        needle = bytes([enemy_ai.SET, number_of_set] + old)
        at = bytes(buf).find(needle)
        if at == -1 or bytes(buf).find(needle, at + 1) != -1:
            raise Refused(f'set {number_of_set} with all its weight on slot {old_slot} is not found once in the script')
        new = [0] * enemy_ai.WEIGHTS
        new[new_slot] = 100
        packs.write_bytes(row, (ENEMY_PCK, name, AI, at + 2), bytes(old), bytes(new))
    else:
        raise Refused(f'unknown enemy field {field!r}')


def attack_row(packs, row):
    aid = int(str(row['Record']).split()[0])
    pack, name = 'EnemyAttackData.pck', f'EnemyAttackData_{aid:04d}.bin'
    buf = packs.entry(pack, name)
    eid = effect_id(str(row['Field']))
    count = struct.unpack_from('<i', buf, ATTACK_COUNT)[0]
    slot = next((k for k in range(count) if struct.unpack_from('<i', buf, ATTACK_SLOTS + ATTACK_SLOT * k)[0] == eid), None)
    if slot is None:
        raise Refused(f'{name} has no effect {eid}')
    packs.write(row, (pack, name, None, ATTACK_SLOTS + ATTACK_SLOT * slot + 4), 'f', row['New'])


def sp_row(packs, row):
    pack = 'LvExpSkptData.pck'
    name = next((fn for fn, b in packs.archive(pack).files
                 if struct.unpack_from('<I', b, SP_LEVEL)[0] == int(row['Level'])), None)
    if name is None:
        raise Refused(f"no entry for level {row['Level']}")
    packs.write(row, (pack, name, None, SP_POINTS), 'I', row['New'])


def equipment_row(packs, row):
    pid = int(str(row['Record']).split()[0])
    pack, name, field = 'EquipmentData.pck', f'EquipmentData_{pid:04d}.bin', str(row['Field'])
    if field in EQUIPMENT:
        offset, fmt = EQUIPMENT[field]
        packs.write(row, (pack, name, None, offset), fmt, number(row['New']), vanilla=number(row['Vanilla']))
    elif field.startswith('Enchant '):
        index = int(field.split()[1])
        buf = packs.entry(pack, name)
        if not 1 <= index <= min(EQUIPMENT_ENCHANT_SLOTS, struct.unpack_from('<i', buf, EQUIPMENT_ENCHANT_COUNT)[0]):
            raise Refused(f'the piece has no innate enchantment number {index}')           # lever L15: the count stays
        packs.write(row, (pack, name, None, EQUIPMENT_ENCHANTS + 4 * (index - 1)), 'i', row['New'])
    else:
        raise Refused(f'unknown equipment field {field!r}')


def party_skill_row(packs, row):
    """Record 'PartySkillData_<id> (<name>)', field 'effect id'."""
    found = re.match(r'(PartySkillData_\d+)', str(row['Record']))
    if not found or str(row['Field']) != 'effect id':
        raise Refused('only the effect of a party skill has an address here')
    packs.write(row, ('PartySkillData.pck', found.group(1) + '.bin', None, PARTY_EFFECT), 'i', int(row['New']),
                vanilla=int(row['Vanilla']))


def npc_row(packs, row):
    """Record '<id> <name> (level <n>)': the record of a guest ally at one stage; field one of the six stats, or
    'AI set <n> weights' (columns Vanilla and New: the weights of the slots, separated by spaces), the weights of a set
    of her NPCAIData script, one byte a slot after the set marker (tools/enemy_ai.py)."""
    nid, field = int(str(row['Record']).split()[0]), str(row['Field'])
    if field not in npc_data.STATS and not re.fullmatch(r'AI set \d+ weights', field):
        raise Refused(f'unknown field {field!r} of a guest ally')
    for name, _ in packs.archive(NPC_PCK).files:
        if struct.unpack_from('<i', packs.entry(NPC_PCK, name, NPC_RECORD), NPC_ID)[0] == nid:
            if field in npc_data.STATS:
                packs.write(row, (NPC_PCK, name, NPC_RECORD, NPC_STATS + 4 * npc_data.STATS.index(field)), 'i',
                            int(row['New']), vanilla=int(row['Vanilla']))
                return
            number_of_set = int(field.split()[2])
            old, new = ([int(x) for x in str(row[c]).split()] for c in ('Vanilla', 'New'))
            if len(old) != len(new) or len(new) > enemy_ai.WEIGHTS or not all(0 <= w <= 255 for w in new) or sum(new) == 0:
                raise Refused('the weights must be as many as the vanilla ones, bytes, and not all 0')
            old += [0] * (enemy_ai.WEIGHTS - len(old))
            new += [0] * (enemy_ai.WEIGHTS - len(new))
            buf = bytes(packs.entry(NPC_PCK, name, NPC_AI))
            needle = bytes([enemy_ai.SET, number_of_set] + old)
            at = buf.find(needle)
            if at == -1 or buf.find(needle, at + 1) != -1:
                raise Refused(f'set {number_of_set} with the vanilla weights is not found once in the script')
            packs.write_bytes(row, (NPC_PCK, name, NPC_AI, at + 2), bytes(old), bytes(new))
            return
    raise Refused(f'no guest ally has the id {nid}')


def _ai_weights(packs, row, where_pack, name, inner, field):
    """'AI set <n> weights' (columns Vanilla and New: the weights of the slots, separated by spaces): one byte a slot after
    the set marker of a script in the format of the enemies (tools/enemy_ai.py)."""
    number_of_set = int(field.split()[2])
    old, new = ([int(x) for x in str(row[c]).split()] for c in ('Vanilla', 'New'))
    if len(old) != len(new) or len(new) > enemy_ai.WEIGHTS or not all(0 <= w <= 255 for w in new) or sum(new) == 0:
        raise Refused('the weights must be as many as the vanilla ones, bytes, and not all 0')
    old += [0] * (enemy_ai.WEIGHTS - len(old))
    new += [0] * (enemy_ai.WEIGHTS - len(new))
    buf = bytes(packs.entry(where_pack, name, inner))
    needle = bytes([enemy_ai.SET, number_of_set] + old)
    at = buf.find(needle)
    if at == -1 or buf.find(needle, at + 1) != -1:
        raise Refused(f'set {number_of_set} with the vanilla weights is not found once in the script')
    packs.write_bytes(row, (where_pack, name, inner, at + 2), bytes(old), bytes(new))


def summon_row(packs, row):
    """Record '<id> <name> (level <n>)': one form of a summon of a grand sealbook (tools/summon_data.py); field one of the
    six factors of its stats (a float: each stat is the best member's times it, 0x4ffc90), or 'AI set <n> weights', the
    weights of a set of its SummonAIData script."""
    sid, field = int(str(row['Record']).split()[0]), str(row['Field'])
    if field not in summon_data.STATS and not re.fullmatch(r'AI set \d+ weights', field):
        raise Refused(f'unknown field {field!r} of a summon')
    for name, _ in packs.archive(SUMMON_PCK).files:
        if struct.unpack_from('<i', packs.entry(SUMMON_PCK, name, SUMMON_RECORD), summon_data.RECORD['id'])[0] == sid:
            if field in summon_data.STATS:
                packs.write(row, (SUMMON_PCK, name, SUMMON_RECORD, summon_data.RECORD['factors'] + 4 * summon_data.STATS.index(field)), 'f',
                            float(row['New']), vanilla=float(row['Vanilla']))
            else:
                _ai_weights(packs, row, SUMMON_PCK, name, SUMMON_AI, field)
            return
    raise Refused(f'no summon form has the id {sid}')


def unique_row(packs, row):
    """Record 'Unique <id> <name>', field 'value', column Level the rank (10: the crown value); or field 'effect id',
    the effect the skill is a status of."""
    uid = int(str(row['Record']).split()[1])
    if str(row['Field']) == 'effect id':
        packs.write(row, ('UniqueSkillData.pck', f'UniqueSkillData_{uid:04d}.bin', None, UNIQUE_EFFECT), 'i',
                    int(row['New']), vanilla=int(row['Vanilla']))
        return
    rank = int(row['Level'])
    if str(row['Field']) != 'value' or not 1 <= rank <= UNIQUE_RANKS:
        raise Refused('a unique skill has ten values, by rank')
    packs.write(row, ('UniqueSkillData.pck', f'UniqueSkillData_{uid:04d}.bin', None, UNIQUE_VALUES + 4 * (rank - 1)),
                'f', number(row['New']), vanilla=number(row['Vanilla']))


def item_row(packs, row):
    """Field 'effect <type> value': the value of the first pair of the item that holds that type."""
    iid = int(str(row['Record']).split()[0])
    pack, name = 'ItemData.pck', f'ItemData_{iid:04d}.bin'
    found = re.match(r'effect (\d+) value', str(row['Field']))
    if not found:
        raise Refused(f"unknown item field {row['Field']!r}")
    buf = packs.entry(pack, name)
    for k in range(ITEM_PAIR_COUNT):
        if struct.unpack_from('<i', buf, ITEM_PAIRS + 8 * k)[0] == int(found.group(1)):
            packs.write(row, (pack, name, None, ITEM_PAIRS + 8 * k + 4), 'f', number(row['New']),
                        vanilla=number(row['Vanilla']))
            return
    raise Refused(f'the item has no pair of type {found.group(1)}')


def sealbook_row(packs, row):
    found = re.search(r'\((\d+)\)\s*$', str(row['Record']))
    if not found:
        raise Refused('the record does not end with the id of the sealbook in brackets')
    pack, name = 'SealScrollData.pck', f'SealScrollData_{int(found.group(1)):04d}.bin'
    ids = {}
    for column in ('Vanilla', 'New'):
        text = str(row[column])
        count = int(re.search(r'ench_cnt=(\d+)', text).group(1))
        ids[column] = [int(x) for x in re.findall(r'[(,]\s*(\d+)\b', text)]
        if len(ids[column]) != count or count > SEAL_SLOTS:
            raise Refused(f'{column}: the count and the ids listed do not agree')
    if ids['New'][:len(ids['Vanilla'])] != ids['Vanilla']:
        raise Refused('the enchantments the sealbook has must stay first')
    packs.write(row, (pack, name, None, SEAL_COUNT), 'i', len(ids['New']), vanilla=len(ids['Vanilla']))
    for k in range(len(ids['Vanilla']), len(ids['New'])):
        packs.write(row, (pack, name, None, SEAL_ENCHANTS + 4 * k), 'i', ids['New'][k], vanilla=-1)


def enchantment_row(packs, row):
    found = re.match(r'(EnchantData_\d+)', str(row['Record']))
    if not found or not str(row['Field']).startswith('stacking flag'):
        raise Refused('only the stacking flag of an enchantment has an address here')
    if int(row['Vanilla']) ^ int(row['New']) != 1:
        raise Refused('the row changes more than bit 0 of the flags')
    packs.write(row, ('EnchantData.pck', found.group(1) + '.bin', None, ENCHANT_FLAGS), 'I', row['New'])


def quest_row(packs, row):
    found = re.match(r'(QuestData_\d+)', str(row['Record']))
    if not found or str(row['Field']) != 'gold reward':
        raise Refused('only the gold of a quest has an address here')
    pack, name = 'QuestData.pck', found.group(1) + '.bin'
    kind = struct.unpack_from('<i', packs.entry(pack, name), QUEST_KIND)[0]
    if kind != QUEST_GOLD:
        raise Refused(f'the reward of the quest is of kind {kind}, not gold: 0 an item, 1 a piece of equipment, 2 '
                      f'experience, 3 gold (0x55e210 - 0x55e2a0)')
    packs.write(row, (pack, name, None, QUEST_AMOUNT), 'i', row['New'])


def zone_row(packs, row):
    import floor_patch
    try:
        poke = floor_patch.pokes([row])[0]
    except floor_patch.Refused as reason:
        raise Refused(str(reason))
    where = (f"{floor_patch.DUNGEON}/{poke['dungeon']}/{floor_patch.PACK}", poke['entry'], None, poke['at'])
    if where in packs.claimed:
        raise Refused(f'the field is already written by row {packs.claimed[where]}')
    packs.claimed[where] = row['ID']
    packs.ledger.append(where + (4, poke['new'], row['ID']))        # kept in the ledger; no pack of the folder holds it


def class_growth_row(packs, row):
    """ClassLevelData: Record '<row> <class>', Field a stat (tools/class_data.py STATS), Level 1 - 99. A row is its number and
    99 levels of eight ints (tools/class_data.py)."""
    import class_data
    number, field, level = int(str(row['Record']).split()[0]), str(row['Field']), int(row['Level'])
    if field not in class_data.STATS:
        raise Refused(f'no stat {field!r} in a growth row ({", ".join(class_data.STATS)})')
    if not 1 <= level <= class_data.LEVELS:
        raise Refused(f'no level {level} in a growth row')
    pack = 'ClassLevelData.pck'
    name = next((fn for fn, b in packs.archive(pack).files if struct.unpack_from('<i', b, 0)[0] == number), None)
    if name is None:
        raise Refused(f'no growth row {number}')
    packs.write(row, (pack, name, None, 4 + 32 * (level - 1) + 4 * class_data.STATS.index(field)), 'i', row['New'])


WRITERS = {'skills': skill_row, 'class_growth': class_growth_row, 'enemies': enemy_row, 'attacks': attack_row, 'sp_curve': sp_row,
           'equipment': equipment_row, 'sealbooks': sealbook_row, 'enchantments': enchantment_row, 'quests': quest_row,
           'items': item_row, 'unique': unique_row,
           'party_skills': party_skill_row, 'npcs': npc_row, 'zones': zone_row, 'summons': summon_row}


def apply(rows=None, backup_dir=BACKUP_DIR):
    """(packs with every row written in memory, {table: rows written}, [(row id, reason)] of the rows refused)."""
    packs, written, refused = Packs(backup_dir), {}, []
    for row in (rows if rows is not None else live_rows()):
        writer = WRITERS.get(row['Table'])
        try:
            if writer is None:
                raise Refused(f"no field of the table {row['Table']} has an address here")
            before = len(packs.ledger)
            writer(packs, row)
            if len(packs.ledger) == before:
                raise Refused('the row wrote nothing')
            written[row['Table']] = written.get(row['Table'], 0) + 1
        except Refused as reason:
            refused.append((row['ID'], f"{row['Table']} / {row['Record']} / {row['Field']}: {reason}"))
        except (ValueError, TypeError, KeyError, struct.error, AttributeError) as error:
            refused.append((row['ID'], f"{row['Table']} / {row['Record']} / {row['Field']}: {type(error).__name__}: {error}"))
    return packs, written, refused


# --- the check: the folder against the originals, byte by byte ---------------------------------------------------
def spans(packs):
    """{(pack, entry, inner): [(offset, size, new bytes, row id)]} of the ledger."""
    found = {}
    for pack, name, inner, offset, size, new, rid in packs.ledger:
        found.setdefault((pack, name, inner), []).append((offset, size, new, rid))
    return found


def entries(path):
    """{(entry, inner or None): bytes} of a pack; the entries of Enemy.pck are opened."""
    out = {}
    nested = os.path.basename(path) in [os.path.basename(p) for p in NESTED_PCKS]
    for name, blob in PckArchive(path).files:
        if nested:
            for inner, data in PckArchive.from_bytes(blob, name).files:
                out[(name, inner)] = bytes(data)
        else:
            out[(name, None)] = bytes(blob)
    return out


def check(packs, out_dir=OUT_DIR, backup_dir=BACKUP_DIR):
    """Problems of the folder: a differing byte no row wrote, a field a row wrote that does not hold its value, an
    entry that changed size or name. Returns (problems, {'packs': read, 'changed': packs that differ, 'bytes': n})."""
    problems, wrote = [], spans(packs)
    counts = {'packs': 0, 'changed': 0, 'bytes': 0, 'fields': len(packs.ledger)}
    names = [n for n in sorted(os.listdir(backup_dir)) if n.endswith('.pck')] + list(NESTED_PCKS)
    for pack in names:
        counts['packs'] += 1
        built, original = os.path.join(out_dir, pack), os.path.join(backup_dir, pack)
        if not os.path.exists(built):
            problems.append(f'{pack}: not in the folder')
            continue
        with open(built, 'rb') as a, open(original, 'rb') as b:
            if a.read() == b.read():
                if any(key[0] == pack for key in wrote):
                    problems.append(f'{pack}: rows were written to it and it is the original')
                continue
        counts['changed'] += 1
        new, old = entries(built), entries(original)
        if list(new) != list(old):
            problems.append(f'{pack}: the entries are not the same or not in the same order')
            continue
        for (name, inner), data in new.items():
            before = old[(name, inner)]
            fields = wrote.get((pack, name, inner), [])
            if len(data) != len(before):
                problems.append(f'{pack} {name} {inner or ""}: {len(before)} bytes became {len(data)}')
                continue
            allowed = bytearray(len(data))
            for offset, size, value, rid in fields:
                allowed[offset:offset + size] = b'\x01' * size
                if data[offset:offset + size] != value:
                    problems.append(f'{pack} {name} +{offset:#x}: does not hold what row {rid} wrote')
            if data != before:
                stray = [k for k in range(len(data)) if data[k] != before[k] and not allowed[k]]
                counts['bytes'] += sum(1 for k in range(len(data)) if data[k] != before[k])
                if stray:
                    problems.append(f'{pack} {name} {inner or ""}: {len(stray)} byte(s) changed outside every row, '
                                    f'first at +{stray[0]:#x}')
    return problems, counts


def build(out_dir=OUT_DIR, backup_dir=BACKUP_DIR, rows=None):
    """Writes the folder. Returns (written by table, refused, problems of the check, counts)."""
    packs, written, refused = apply(rows, backup_dir)
    if refused:
        return written, refused, [], {}
    packs.save(out_dir)
    problems, counts = check(packs, out_dir, backup_dir)
    return written, refused, problems, counts


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    rows = live_rows()
    if '--check' in sys.argv:
        packs, written, refused = apply(rows)
        problems, counts = ([], {}) if refused else check(packs)
    else:
        written, refused, problems, counts = build(rows=rows)
    print(f'{len(rows)} live rows; written: ' + ', '.join(f'{t} {n}' for t, n in sorted(written.items())))
    for rid, reason in refused:
        print(f'  refused {rid}: {reason}')
    for problem in problems:
        print(f'  problem: {problem}')
    if refused or problems:
        print(f'[FAIL] {len(refused)} row(s) refused, {len(problems)} problem(s)')
        sys.exit(1)
    print(f"[OK] {counts['fields']} fields in {counts['changed']} of {counts['packs']} packs; {counts['bytes']} bytes differ "
          f'from the originals, every one inside a field a row wrote. Folder: {OUT_DIR}')


if __name__ == '__main__':
    main()

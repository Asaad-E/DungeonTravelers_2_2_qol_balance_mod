"""
Every figure of the game the simulator uses, gathered from the readers of tools/ and from the vanilla workbook.

Nothing here is typed: each table comes from a game file through the reader named beside it. The result is cached
in sim/__pycache__ and rebuilt when one of the sources changes. A variant (phase 4) is applied on top of a GameData
with `GameData.with_changes`, never by editing what was read.

    from sim.data import game_data
    data = game_data()
"""
import copy
import os
import pickle
import sys

import openpyxl

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SIM_DIR)
TOOLS_DIR = os.path.join(PROJECT_DIR, 'tools')
WORKBOOK = os.path.join(PROJECT_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx')
CRITERIA = os.path.join(PROJECT_DIR, 'data_tables', 'balance_criteria.xlsx')
CACHE = os.path.join(SIM_DIR, '__pycache__', 'game_data.pkl')
CACHE_VERSION = 4
LEVELS = [f'Lv{k}' for k in range(1, 11)]
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

# Skill target codes (Technique/Magic 0x28, EnemyAttackData 0x2C), named by tools/extract_vanilla.py and
# docs/FORMULAS.md 9.1: 0-4 act on the other side, 5-12 on the user's own side, 14 on everyone.
SINGLE, RANDOM, ROW, PIERCE, ALL = 0, 1, 2, 3, 4
ALLY, RANDOM_ALLY, ALLY_ROW, ALLIES, SELF, NO_TARGET, ALLY_MOST_TP_LOST = 5, 6, 7, 8, 9, 10, 12
EVERYONE, ANYONE = 14, 15
OWN_SIDE = {5, 6, 7, 8, 9, 10, 11, 12, 13}
# Attribute codes (0x2C of a skill, 0x30 of an enemy attack): 0 the weapon's, 1-3 physical, 4-8 elements, 9 neutral
WEAPON_ATTR, SLASH, STAB, BASH, FIRE, WATER, WIND, EARTH, LIGHTNING, NEUTRAL = range(10)
PHYSICAL_ATTRS = (SLASH, STAB, BASH)
# Resistance index of an attribute: the eight resistances of EnemyStatusData 0x48 in their order
RESIST_INDEX = {SLASH: 0, STAB: 1, BASH: 2, FIRE: 3, WATER: 4, WIND: 5, EARTH: 6, LIGHTNING: 7}
# Technique range bits (Group_0x30, bits 0-3; tools/skill_tree_data.py)
SHORT, MID, LONG, NO_RANGE = 0, 1, 2, 3
# Weapon flags, EquipmentData 0x54 (read from the 551 records against the weapon table of the Japanese wiki,
# atwiki dt2-2 page 67): bit 0 two-handed; bits 1, 2, 3 short, mid, long range; bits 6, 7, 8 slash, stab, bash.
WEAPON_TWO_HANDED, WEAPON_RANGE_BITS, WEAPON_ATTR_BITS = 0x1, {0x2: SHORT, 0x4: MID, 0x8: LONG}, {0x40: SLASH, 0x80: STAB, 0x100: BASH}


def _rows(workbook, sheet):
    ws = workbook[sheet]
    it = ws.iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it]


def _series(row, count=None):
    values = [row[k] for k in LEVELS]
    if count is not None:
        values = values[:count]
    return [v if v is not None else 0 for v in values]


class Skill:
    """A technique, spell or passive. Per-level lists are indexed by level - 1.
    effects: [(effect id, kind of the slot, [value per level])]; kind as docs/FORMULAS.md 9.2 (0 passive, 2 property
    of the action, 3 map, 4 done to the target, 5 a status that lasts turns)."""
    __slots__ = ('category', 'id', 'name', 'levels', 'target', 'attr', 'group', 'weapons', 'effects', 'tp', 'sp',
                 'speed', 'cast', 'accuracy', 'turns', 'classes', 'pattern', 'range', 'chant_stat')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def effect(self, effect_id, level, default=None):
        for eid, _, values in self.effects:
            if eid == effect_id:
                return values[min(level, len(values)) - 1]
        return default

    def has(self, effect_id):
        return any(eid == effect_id for eid, _, _ in self.effects)

    @property
    def chanted(self):
        return self.category == 'Magic' and bool(self.cast) and any(self.cast)

    def __repr__(self):
        return f'<{self.category} {self.id} {self.name}>'


class EnemyAttack:
    """An EnemyAttackData record: also the attacks of summons and guest allies, and the passives of enemies."""
    __slots__ = ('id', 'name', 'target', 'attr', 'chant_speed', 'accuracy', 'power', 'turns', 'speed', 'effects',
                 'range', 'passive', 'chant_stat')

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def effect(self, effect_id, default=None):
        for eid, _, value in self.effects:
            if eid == effect_id:
                return value
        return default

    def has(self, effect_id):
        return any(eid == effect_id for eid, _, _ in self.effects)

    @property
    def chanted(self):
        return bool(self.chant_speed)

    def __repr__(self):
        return f'<EnemyAttack {self.id} {self.name}>'


class GameData:
    def __init__(self):
        self.skills = {}            # (category, id) -> Skill
        self.skill_by_id = {}       # id -> Skill (technique and magic ids do not collide; passives are separate)
        self.unique = {}            # unique skill id -> {'name', 'effect', 'values': [Lv1..Lv9, EX]}
        self.attacks = {}           # EnemyAttackData id -> EnemyAttack
        self.enemies = {}           # enemy id -> dict from tools/enemy_data.py, plus 'script'
        self.growth = {}            # ClassLevelData row -> [stats per level]
        self.class_names = {}
        self.class_modifiers = []
        self.characters = []
        self.equipment = {}         # equipment id -> dict
        self.enchants = {}
        self.sealbooks = {}            # sealbook id -> {'name', 'grand', 'level', 'enchants'}
        self.weapon_ranks = {}      # rank index -> delay
        self.items = {}
        self.item_skills = {}       # item effect type -> skill id it performs
        self.exp_curve = {}         # level -> EXP needed from the level below
        self.sp_curve = {}
        self.floors = []
        self.fixed = []
        self.summons = []
        self.dolls = []
        self.npcs = []
        self.random_moves = []
        self.effect_rules = {}      # effect id -> rule text of balance_criteria.xlsx EffectRules
        self.effect_names = {}

    def with_changes(self, changes):
        """A copy with values replaced: changes is [(table, key, field, value)], e.g.
        ('skills', ('Magic', 143), 'tp', [...]). Used by the solve of phase 4; vanilla is never edited."""
        other = copy.deepcopy(self)
        for table, key, field, value in changes:
            target = getattr(other, table)[key]
            if isinstance(target, dict):
                target[field] = value
            else:
                setattr(target, field, value)
        return other

    def stats(self, row, level):
        return self.growth[row][max(1, min(99, level)) - 1]


def _skill_range(category, group):
    if category != 'Technique' or group is None:
        return NO_RANGE if category == 'Magic' else None
    for bit, value in ((1, SHORT), (2, MID), (4, LONG), (8, NO_RANGE)):
        if group & bit:
            return value
    return NO_RANGE


def _load_skills(wb, data):
    import skill_tree_data
    tree = {(s['category'], s['id']): s for s in skill_tree_data.skills()}
    levels = {}
    for r in _rows(wb, 'SkillLevels'):
        levels.setdefault((r['Category'], r['Skill_ID']), []).append(r)
    for r in _rows(wb, 'Skills'):
        key = (r['Category'], r['Skill_ID'])
        rows = levels.get(key, [])
        count = r['Levels'] or 1
        field = lambda name: next((_series(x, count) for x in rows if x['Field'] == name), None)
        effects = [(x['Effect_ID'], x['Slot_Tail'], _series(x, count)) for x in rows
                   if str(x['Field']).startswith('effect_') and x['Effect_ID'] is not None]
        weapons = [int(w) for w in str(r['Weapon_Codes']).split(',')] if r['Weapon_Codes'] not in (None, '') else []
        info = tree.get(key, {})
        skill = Skill(category=r['Category'], id=r['Skill_ID'], name=r['Name'], levels=count, target=r['Target_Code'],
                      attr=r['Attr_Code'], group=r['Group_0x30'], weapons=weapons, effects=effects,
                      tp=field('tp_cost') or [0] * count, sp=field('sp_cost') or [0] * count,
                      speed=field('speed') or [1.0] * count, cast=field('cast'), accuracy=field('arr_0xFC'),
                      turns=field('turns') or [0] * count, classes=info.get('classes', []),
                      pattern=info.get('pattern'), range=_skill_range(r['Category'], r['Group_0x30']),
                      chant_stat=_chant_stat(r['Category'], r['Group_0x30']))
        data.skills[key] = skill
        if r['Category'] != 'Passive':
            data.skill_by_id[r['Skill_ID']] = skill


def _chant_stat(category, group):
    """The stat a spell is chanted with. _SetTime (0x449a58 - 0x449aeb) reads the flags of the magic record at
    +0x48 of the map entry, file offset 0x30 (the workbook's Group_0x30): bit 0 INT, bit 1 RES, bit 2 AGI."""
    if category != 'Magic' or group is None:
        return None
    return 'int' if group & 1 else 'res' if group & 2 else 'agi' if group & 4 else None


def _load_attacks(wb, data):
    for r in _rows(wb, 'EnemyAttacks'):
        effects = []
        for k in range(1, 6):
            if r[f'Eff{k}_ID'] is not None:
                effects.append((r[f'Eff{k}_ID'], r[f'Eff{k}_Tail'], r[f'Eff{k}_Value'] or 0))
        header = r['Header_Line'] or ''
        reach = None
        for word, value in (('Short', SHORT), ('Mid', MID), ('Long', LONG), ('None', NO_RANGE)):
            if f'Range: {word}' in header:
                reach = value
        data.attacks[r['Skill_ID']] = EnemyAttack(
            id=r['Skill_ID'], name=r['Name'], target=r['Target_Code'], attr=r['Attr_Code'],
            chant_speed=r['Chant_Speed'] or 0, accuracy=r['Accuracy'] or 0, power=r['Power'] or 0,
            turns=int(r['Turns'] or 0), speed=r['Speed'] if r['Speed'] else 1.0, effects=effects, range=reach,
            passive='Passive Skill' in str(r['Vanilla_Desc'] or ''),
            chant_stat=_enemy_chant_stat(r['Anim_0x28'] or 0))


def _enemy_chant_stat(word):
    """_SetTime (0x449b0d - 0x449b38) reads the word at file 0x28 of a chanted enemy attack: bit 11 INT, bit 12 RES.
    Of the 2,375 attacks, the 423 that chant have exactly one of the two (334 INT, 89 RES)."""
    return 'int' if word >> 11 & 1 else 'res' if word >> 12 & 1 else None


def _load_equipment(wb, data):
    for r in _rows(wb, 'Equipment'):
        flags = r['w_0x54'] or 0
        piece = {'id': r['Equip_ID'], 'name': r['Name'], 'category': r['Category_Code'],
                 'stats': {s.lower(): r[s] or 0 for s in ('ATK', 'DEF', 'INT', 'RES', 'DEX', 'AGI')},
                 'rate': r['Upgrade_Rate'] or 0.0, 'classes': int(r['mask_0x40'], 16) if r['mask_0x40'] else 0,
                 'swing': r['Swing'] or 0.0, 'rank': r['Rank_Idx'], 'type': r['Type_Code'],
                 'enchants': [r[f'Enchant{k}_ID'] for k in range(1, 5) if r[f'Enchant{k}_ID'] is not None],
                 'two_handed': bool(flags & WEAPON_TWO_HANDED) if r['Category_Code'] == 0 else False,
                 'range': next((v for bit, v in WEAPON_RANGE_BITS.items() if flags & bit), SHORT),
                 'attr': next((v for bit, v in WEAPON_ATTR_BITS.items() if flags & bit), NEUTRAL)}
        data.equipment[r['Equip_ID']] = piece
    for r in _rows(wb, 'Enchants'):
        data.enchants[r['Enchant_ID']] = r['Name']
    # SealScrollData: 0x00 id (the id of the enemy it seals), 0x18 kind (0 a sealbook, 1 a grand sealbook),
    # 0x1C number of enchantments and 0x20 their ids (read into the enchantment list at 0x4f7b5d), 0x34 level
    for r in _rows(wb, 'Raw_SealScroll'):
        count = max(0, min(4, r['w_0x1c'] or 0))
        ids = [r[f'w_0x{0x20 + 4 * k:02x}'] for k in range(count)]
        data.sealbooks[r['w_0x00']] = {'name': r['Name'], 'grand': r['w_0x18'] == 1, 'level': r['w_0x34'],
                                       'enchants': [e for e in ids if e is not None and e >= 0]}
    for r in _rows(wb, 'WeaponRanks'):
        data.weapon_ranks[r['Rank_Idx']] = r['Delay_Mult']


def _load_misc(wb, data):
    for r in _rows(wb, 'UniqueSkills'):
        data.unique[r['Skill_ID']] = {'name': r['Name'], 'effect': r['w_0x50'],
                                      'values': [r[k] for k in LEVELS[:9]] + [r['EX']]}
    for r in _rows(wb, 'Items'):
        data.items[r['Item_ID']] = {'name': r['Name'], 'price': r['Buy_Price'],
                                    'effects': [(r[f'Eff{k}_Type'], r[f'Eff{k}_Value']) for k in range(1, 5)
                                                if r[f'Eff{k}_Type'] not in (None, -1)]}
    for r in _rows(wb, 'ExpCurve'):
        data.exp_curve[r['Level']] = r['Req_EXP']
        data.sp_curve[r['Level']] = r['SP']
    for r in _rows(wb, 'Effects'):
        data.effect_names[r['Effect_ID']] = r['Name'] or r['Game_Name']


def _sources():
    files = [WORKBOOK, CRITERIA, __file__]
    for name in ('enemy_data', 'enemy_ai', 'class_data', 'class_modifier_data', 'character_data', 'floor_data',
                 'summon_data', 'doll_data', 'npc_data', 'random_move_data', 'skill_tree_data', 'item_effect_data'):
        files.append(os.path.join(TOOLS_DIR, name + '.py'))
    return [(f, os.path.getmtime(f)) for f in files]


def build():
    import character_data
    import class_data
    import class_modifier_data
    import doll_data
    import enemy_ai
    import enemy_data
    import floor_data
    import item_effect_data
    import npc_data
    import random_move_data
    import summon_data
    from exe_reader import Exe

    data = GameData()
    wb = openpyxl.load_workbook(WORKBOOK, read_only=True)
    exe = Exe()
    _load_skills(wb, data)
    _load_attacks(wb, data)
    _load_equipment(wb, data)
    _load_misc(wb, data)
    for enemy in enemy_data.enemies():
        try:
            enemy['script'] = enemy_ai.decode(enemy['ai']) if enemy['ai'] else None
        except ValueError:
            enemy['script'] = None
        data.enemies[enemy['id']] = enemy
    data.growth = class_data.growth()
    data.class_names = class_data.class_names()
    data.class_modifiers = class_modifier_data.class_modifiers(exe)
    data.characters = character_data.characters()
    data.floors = floor_data.floors()
    data.fixed = floor_data.fixed_battles()
    data.summons = summon_data.summons()
    data.dolls = doll_data.dolls()
    data.npcs = npc_data.npcs()
    data.random_moves = random_move_data.random_moves(exe)
    data.item_skills = {kind: skill for kind, (skill, _) in item_effect_data.skill_items(exe).items()}
    criteria = openpyxl.load_workbook(CRITERIA, read_only=True)
    data.effect_rules = {r['Effect_ID']: r['Rule'] for r in _rows(criteria, 'EffectRules')}
    return data


def game_data(refresh=False):
    stamp = (CACHE_VERSION, _sources())
    if not refresh and os.path.exists(CACHE):
        try:
            with open(CACHE, 'rb') as f:
                saved_stamp, data = pickle.load(f)
            if saved_stamp == stamp:
                return data
        except (OSError, pickle.UnpicklingError, EOFError, AttributeError):
            pass
    data = build()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, 'wb') as f:
        pickle.dump((stamp, data), f)
    return data

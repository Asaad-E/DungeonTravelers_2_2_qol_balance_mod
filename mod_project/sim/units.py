"""
The units of a battle: party members, enemies, summons, dolls and guest allies.

Every figure is read: growth rows and resets (docs/FORMULAS.md 10), equipment and weapon mastery (10.1, 12.17), class
modifiers (10.4), statuses on stats (12.6), enemy records, summons (11) and dolls (11.1). A unit keeps its statuses
as one entry per effect id, because a status of the same effect replaces the old one (12.18).
"""
from sim import formulas as f
from sim.data import NEUTRAL, SHORT, MID, LONG

STATS = ('atk', 'def', 'int', 'res', 'dex', 'agi')
STAT_BUFF = {'atk': 41, 'def': 42, 'int': 43, 'res': 44, 'dex': 45, 'agi': 46}     # 12.6
ALL_STAT_BUFFS = (189, 193, 194)                                                    # Magical Change, Limiter Removal, Beginning of the End
ELEMENT_RESIST_BUFFS = (169, 202, 248, 341)                                         # each adds to the five elements
PHYSICAL_RESIST_BUFFS = {185: 0, 184: 1, 186: 2}                                    # slash, stab, bash
MAX_HP_BUFF = 172
TRUMP_CARD = 48
ENCHANT_ENMITY_UP, ENCHANT_ENMITY_DOWN = 49, 50
MASTERY, MASTERY_ALL, DUAL_WIELD, YEARNING = 243, 298, 256, 449
DOLL_HP = 9999                                                                      # 0x4fd922
PARTY, ENEMIES = 0, 1
ADULT_BIT = 13                                                                      # EnemyStatusData 0x3C (0x44b047)


class Status:
    """One status on a unit. turns 0 means it stays until removed (12.18)."""
    __slots__ = ('effect', 'value', 'turns', 'source', 'skill', 'kind', 'data')

    def __init__(self, effect, value, turns=0, source=None, skill=None, kind=5, data=None):
        self.effect, self.value, self.turns, self.source, self.skill, self.kind = effect, value, turns, source, skill, kind
        self.data = data

    def __repr__(self):
        return f'<Status {self.effect}={self.value} turns={self.turns}>'


class Unit:
    """What every fighter has. base: the six stats before statuses; resist: the eight resistances."""

    def __init__(self, name, side, level, hp, tp, base, resist=None, weight=1.0, swing=0.0, race=None, kind='member'):
        self.name, self.side, self.level, self.kind = name, side, level, kind
        self.max_hp_base, self.max_tp = hp, tp
        self.hp, self.tp = hp, tp
        self.base = dict(base)
        self.resist_base = list(resist or [0] * 8)
        self.weight, self.swing, self.race = weight, swing, race
        self.front = True
        self.position = 0
        self.statuses = {}                  # effect id -> Status
        self.passives = {}                  # effect id -> value: passive skills, unique skill, enemy passives
        self.enchants = {}                  # enchant id -> pieces
        self.immune = set()                 # names of tools/enemy_data.IMMUNITY_BITS
        self.skills = {}                    # skill id -> level, actions it can choose
        self.attacks = []                   # enemy attack slots
        self.script = None
        self.weapon = None                  # equipment dict of the main hand
        self.attack_range = SHORT
        self.attack_attr = NEUTRAL
        self.alive = True
        self.next_time = 0.0
        self.chant = None                   # the action being chanted
        self.song = []                      # songs it keeps up (Solo Duet allows two)
        self.dance = []
        self.dolls = []
        self.owner = None                   # summoner of a doll or summon
        self.turns_taken = 0
        self.last_skill = None
        self.uses = {}                      # skill key -> times used
        self.once_done = set()              # commands of the AI script fired once
        self.ecstasy_done = False
        self.ai_set = 0
        self.life = None                    # turns left of a doll or summon
        self.action_skill = None            # hidden skill of a doll
        self.provoked_by = {}               # party unit -> value of effect 170 it put on this enemy
        self.pep = 100.0
        self.unique = None                  # (effect id, value)
        self.character = None
        self.class_id = None
        self.defending = False
        self.stolen = False
        self.items = {}
        self.adult = False                  # 21 or older: character flag 0x0C, enemy flag bit 13 (0x44b006 - 0x44b04c)
        self.shield = False                 # wears a shield in the off hand (Material Guard, 0x44c6f9 - 0x44c711)

    # --- stats -------------------------------------------------------------------------------------------
    def status_value(self, effect, default=0.0):
        s = self.statuses.get(effect)
        return s.value if s else default

    def has(self, effect):
        return effect in self.statuses or effect in self.passives

    def value(self, effect, default=0.0):
        """Value of an effect on the unit, as a status or a passive (a status first)."""
        if effect in self.statuses:
            return self.statuses[effect].value
        return self.passives.get(effect, default)

    def stat(self, name):
        """A stat with its statuses (12.6): each gains int(stat * value) of its own buff and of the all-stat ones."""
        base = self.base[name]
        total = base
        if STAT_BUFF[name] in self.statuses:
            total += int(base * self.statuses[STAT_BUFF[name]].value)
        for effect in ALL_STAT_BUFFS:
            if effect in self.statuses:
                total += int(base * self.statuses[effect].value)
        if name == 'atk' and TRUMP_CARD in self.statuses:
            total += int(self.base['def'] * self.statuses[TRUMP_CARD].value)
        if name == 'def' and TRUMP_CARD in self.statuses:
            total = 0
        if 120 in self.statuses:                    # petrified: half its DEF more, half its AGI less
            if name == 'def':
                total += base // 2
            if name == 'agi':
                total -= base // 2
        return max(0, total)

    @property
    def max_hp(self):
        hp = self.max_hp_base
        if MAX_HP_BUFF in self.statuses:
            hp += int(hp * self.statuses[MAX_HP_BUFF].value)
        return hp

    def resistance(self, index):
        value = self.resist_base[index]
        if index >= 3:
            value += sum(int(self.value(e)) for e in ELEMENT_RESIST_BUFFS if self.has(e))   # a passive too (Adaptation)
        else:
            value += sum(int(s.value) for e, i in PHYSICAL_RESIST_BUFFS.items() if i == index
                         for s in [self.statuses.get(e)] if s)
        return value

    def pieces(self, enchant):
        return self.enchants.get(enchant, 0)

    @property
    def can_act(self):
        return self.alive and not any(e in self.statuses for e in (116, 120, 114))   # sleep, petrification, freeze

    @property
    def hp_ratio(self):
        return self.hp / self.max_hp if self.max_hp else 0.0

    @property
    def tp_ratio(self):
        return self.tp / self.max_tp if self.max_tp else 1.0

    def __repr__(self):
        return f'<{self.kind} {self.name} L{self.level} {self.hp}/{self.max_hp}>'


# --- party members ---------------------------------------------------------------------------------------
def piece_stats(piece, upgrade):
    """Stats of a piece of equipment at an upgrade level (10.1): base + int(level * rate); 0 stays 0."""
    return {s: (v + int(upgrade * piece['rate'])) if v else 0 for s, v in piece['stats'].items()}


def class_modifier_entries(data, class_id, previous):
    rows = [m for m in data.class_modifiers if m['class'] == class_id]
    exact = [m for m in rows if m['previous'] == previous]
    chosen = exact or [m for m in rows if m['previous'] is None] or rows[:1]
    return chosen[0]['entries'] if chosen else []


def enchant_bonus(enchants, base, base_hp, base_tp, front):
    """What the enchantments add to a character (0x4f8270): {'hp', 'tp', six stats, 'resist': eight sums}. base: the
    six stats before equipment (growth, bonus and resets: the getters 0x4f98c0 and 0x4f98d0 at that point)."""
    total = {s: 0 for s in STATS}
    hp = tp = 0
    resist = [0] * 8
    for e, n in enchants.items():
        for _ in range(n):
            if e in f.ENCHANT_SHARE:
                figure, divisor, floor = f.ENCHANT_SHARE[e]
                source = base_hp if figure == 'hp' else base_tp if figure == 'tp' else base[figure]
                share = max(floor, int(source / abs(divisor)))
                share = share if divisor > 0 else -share
                if figure == 'hp':
                    hp += share
                elif figure == 'tp':
                    tp += share
                else:
                    total[figure] += share
            if e in f.ENCHANT_ALL_STATS:
                for s in STATS:
                    total[s] += f.ENCHANT_ALL_STATS[e]
            for index, value in f.ENCHANT_RESIST.get(e, {}).items():
                resist[index] += value
            if e in f.ENCHANT_LINE and f.ENCHANT_LINE[e][0] == front:
                for s, share in f.ENCHANT_LINE[e][1].items():
                    total[s] += int(base[s] * share) if share < 1 else int(base[s] / share)
    half_hp, half_tp = int(base_hp / 2), int(base_tp / 2)
    cap = f.ENCHANT_RESIST_CAP
    return dict(total, hp=max(-half_hp, min(half_hp, hp)), tp=max(-half_tp, min(half_tp, tp)),
                resist=[max(-cap, min(cap, r)) for r in resist])


def unique_rank(level, crown_bonus):
    """Which of the ten values of a unique skill a character has (0x4f615e - 0x4f61e3): level / 10, none below level 10;
    the tenth (EX) once the bonus of the resets reaches 50."""
    return 10 if crown_bonus >= 50 else level // 10


def build_member(data, character, class_id, level, previous=None, equipment=(), skills=None, passives=None,
                 crown_bonus=0, unique_level=None, name=None, front=True, items=None, sealbook=None,
                 party_enchants=(), forged=None):
    """A party member. equipment: [(slot, equipment id, upgrade level)], slot 0 main hand, 1 off hand, 2-4 the rest.
    skills: {skill id: level}; passive skills among them are turned into passive effects."""
    import class_data
    row = class_data.growth_row(class_id, previous)
    grown = data.stats(row, level)
    character_stats = {s: grown[s] + crown_bonus for s in STATS}
    hp, tp = grown['hp'] + crown_bonus, grown['tp'] + crown_bonus
    skills = dict(skills or {})
    passive_values = dict(passives or {})
    for skill_id, lv in skills.items():
        skill = data.skills.get(('Passive', skill_id))
        if skill:
            for effect, _, values in skill.effects:
                # two skills of one effect: the larger figure; Imperial Guard (308) is a negative one, kept as it is
                value = values[min(lv, len(values)) - 1]
                passive_values[effect] = max(passive_values.get(effect, value), value, key=abs)
    unique = None
    rank = unique_rank(level, crown_bonus) if unique_level is None else unique_level
    if character is not None and character.get('unique_skill') is not None and rank > 0:
        u = data.unique.get(character['unique_skill'])
        if u:
            unique = (u['effect'], u['values'][min(10, rank) - 1])
            passive_values[u['effect']] = unique[1]
    mastery = passive_values.get(MASTERY, 0.0) + passive_values.get(MASTERY_ALL, 0.0)
    totals = dict(character_stats)
    enchants = {}
    weapon = None
    yearning = passive_values.get(YEARNING, 0.0)
    modifiers = class_modifier_entries(data, class_id, previous)
    gains = {s: 0 for s in STATS}
    for slot, equip_id, upgrade in equipment:
        piece = data.equipment[equip_id]
        stats = piece_stats(piece, upgrade)
        if slot == 0 and piece['category'] == 0:
            weapon = piece
            for s in ('atk', 'res'):
                stats[s] = stats[s] + int(stats[s] * mastery)
        if slot == 1 and piece['category'] == 0:                   # a weapon in the off hand: Dual Wield only
            share = passive_values.get(DUAL_WIELD, 0.0)
            stats = {s: int(v * share) for s, v in stats.items()}
        for s in STATS:
            totals[s] += stats[s]
        for e in piece['enchants']:
            enchants[e] = enchants.get(e, 0) + 1
        for entry in modifiers:
            matches = (entry['slot'] == slot and (slot != 0 or piece['type'] == entry['type'])
                       and (slot != 1 or piece['category'] == 1))
            if matches:
                for s in STATS:
                    if stats[s] > 0:
                        gains[s] += max(0, int((character_stats[s] + stats[s]) * (entry['modifier'] + 0.01 * yearning)))
    for s in STATS:
        totals[s] += gains[s]
    # The sealbook of the character adds its enchantments to the same list as the pieces (0x4f7b5d - 0x4f7bdd); the
    # grand sealbook the party carries adds its one enchantment to every member (party_enchants)
    if sealbook is not None and sealbook in data.sealbooks:
        for e in data.sealbooks[sealbook]['enchants']:
            enchants[e] = enchants.get(e, 0) + 1
    for e in party_enchants:
        enchants[e] = enchants.get(e, 0) + 1
    # enchantments forged onto the pieces (sim/scenario.py forge_enchants): {id: pieces that carry it}
    for e, n in (forged or {}).items():
        enchants[e] = enchants.get(e, 0) + n
    # The piece counter (0x4f5470) and the stat function (0x4f8311) count one piece only of an enchantment whose flag
    # bit 0 (EnchantData 0x20) is clear
    enchants = {e: (n if e in data.enchant_stacks else min(n, 1)) for e, n in enchants.items()}
    bonus = enchant_bonus(enchants, character_stats, hp, tp, front)
    for s in STATS:
        totals[s] += bonus[s]
    hp, tp = hp + bonus['hp'], tp + bonus['tp']
    # each resistance of a character is its own bonus plus the bonus of the resets (0x4f5f04 - 0x4f5f74), then the
    # sum of its enchantments (0x4f8490)
    resist = [crown_bonus + r for r in bonus['resist']]
    rank_delay = data.weapon_ranks[weapon['rank']] if weapon and weapon['rank'] is not None and weapon['rank'] >= 0 \
        else unarmed_delay(data, class_id)
    unit = Unit(name or (character['name'] if character else f'class {class_id}'), PARTY, level, hp, tp, totals,
                resist=resist, weight=rank_delay, swing=weapon['swing'] if weapon else 0.0, kind='member')
    unit.passives = passive_values
    unit.raw = dict(character_stats)         # the stats of level and class alone, what a summon scales from
    unit.enchants = enchants
    unit.sealbook = sealbook
    unit.weapon = weapon
    unit.attack_range = weapon['range'] if weapon else SHORT
    unit.attack_attr = weapon['attr'] if weapon else 3                      # bare hands bash
    unit.skills = {sid: lv for sid, lv in skills.items() if ('Passive', sid) not in data.skills}
    unit.unique = unique
    unit.character = character
    unit.adult = bool(character and character.get('flag') == 1)
    unit.shield = any(slot == 1 and data.equipment[equip_id]['category'] == 1 for slot, equip_id, _ in equipment)
    unit.class_id = class_id
    unit.front = front
    unit.items = dict(items or {})
    return unit


def unarmed_delay(data, class_id):
    """Delay with no weapon. The Japanese wiki (page 67) leaves it unconfirmed by class; the simulator never fields
    an unarmed member except in the player test of page 105, which uses rank values given by the test itself."""
    return data.weapon_ranks[5]


# --- enemies ---------------------------------------------------------------------------------------------
def build_enemy(data, enemy_id, front=True, name=None):
    e = data.enemies[enemy_id]
    unit = Unit(name or e['name'], ENEMIES, e['level'], e['hp'], 0, {s: e[s] for s in STATS},
                resist=[e['res_' + r] for r in ('slash', 'stab', 'bash', 'fire', 'water', 'wind', 'earth', 'lightning')],
                weight=e['weight'], swing=e['swing'], race=e['race'], kind='enemy')
    unit.immune = set(e['immune'])
    unit.attacks = list(e['attacks'])
    unit.script = e['script']
    unit.front = front
    unit.enemy_id = enemy_id
    unit.exp, unit.gold = e['exp'], e['gold']
    unit.snack = e['snack']
    unit.adult = bool(e['flags'] >> ADULT_BIT & 1)
    for attack_id in e['passives']:
        attack = data.attacks.get(attack_id)
        if attack:
            for effect, _, value in attack.effects:
                unit.passives[effect] = value
    return unit


def build_summon(data, form, party, hp):
    """A summoned monster (11): each stat is the best party stat times the factor of the form, not below the base of
    the enemy it comes from. hp: the HP is not read from the program (docs/FORMULAS.md 11), so the caller passes it
    from the rule of data_tables/sim_setup.xlsx."""
    floor = summon_base_floor(data, form)
    stats = {}
    for s in STATS:
        # the raw stat of each member, without equipment (GameFAQs faqs/80834, Grand Sealbooks)
        best = max((getattr(m, 'raw', m.base)[s] for m in party if m.kind == 'member'), default=0)
        stats[s] = max(floor[s], int(f.single(best * form['factors'][s])))
    unit = Unit(form['name'], PARTY, form['level'], hp, 0, stats, weight=data.weapon_ranks.get(form['rank'], 2.0),
                kind='summon')
    unit.attacks = list(form['attacks'])
    unit.script = form['script']
    if form['passive'] is not None and form['passive'] in data.attacks:
        for effect, _, value in data.attacks[form['passive']].effects:
            unit.passives[effect] = value
    return unit


def summon_base_floor(data, form):
    """The base figure a summoned stat never falls below: the stats of the enemy the summon is (SummonData 0x14)."""
    enemy = data.enemies.get(form['enemy'])
    return {s: enemy[s] for s in STATS} if enemy else {s: 0 for s in STATS}


DOLL_RANGES = {'short': SHORT, 'mid': MID, 'long': LONG}
SOUL_SEAL = 314


def build_doll(owner, doll, level, data=None):
    """A doll (11.1): 9,999 HP, the stats of its owner (the code feeds the stat function its owner's character
    number; docs/FORMULAS.md 11.1 leaves the class row unconfirmed), a life in turns, a hidden action each turn.
    Soul Seal (314) of the owner adds int(stat of the enemy its sealbook seals * value) to each of the six stats
    (0x4fdfd0 - 0x4fe102; a sealbook's id is the id of the enemy it seals)."""
    base = dict(owner.base)
    if data is not None and owner.has(SOUL_SEAL) and getattr(owner, 'sealbook', None) in data.enemies:
        sealed = data.enemies[owner.sealbook]
        for s in STATS:
            base[s] += int(sealed[s] * owner.value(SOUL_SEAL))
    unit = Unit(doll['name'], owner.side, owner.level, DOLL_HP, 0, base, weight=owner.weight,
                swing=0.0, kind='doll')
    unit.owner = owner
    unit.life = doll['turns'][level - 1]
    unit.doll = doll
    unit.doll_level = level
    unit.attack_range = DOLL_RANGES.get(doll['range'], SHORT)
    unit.front = owner.front
    return unit

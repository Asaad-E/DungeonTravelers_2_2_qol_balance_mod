"""
A battle of the game, played turn by turn as the program plays it.

    battle = Battle(data, party, enemies, rng, choose_member=policy, setup=setup)
    result = battle.run()

The order of turns is a timeline: a unit acts, and its next turn comes after the wait of docs/FORMULAS.md 5 (1 minus
the gauge value its action wrote). A chanted spell takes two waits: the chant, with the chant stat of the spell and its
chant speed, then the wait after the spell. Inside a turn the states of docs/FORMULAS.md 12.15 run in their order.

Every effect id this file acts on is listed in HANDLED with the place that acts on it. tools/sim_coverage.py counts
them against the effects the skills of the player use; an id is listed only where the code below really uses it.
"""
import math

from sim import formulas as f
from sim.data import (SINGLE, RANDOM, ROW, PIERCE, ALL, ALLY, RANDOM_ALLY, ALLY_ROW, ALLIES, SELF, NO_TARGET,
                      ALLY_MOST_TP_LOST, EVERYONE, ANYONE, OWN_SIDE, WEAPON_ATTR, NEUTRAL, PHYSICAL_ATTRS,
                      RESIST_INDEX, SHORT, MID, LONG, NO_RANGE, SLASH, STAB, BASH, FIRE, WATER, WIND, EARTH,
                      LIGHTNING, Skill, EnemyAttack)
from sim.units import Status, PARTY, ENEMIES, build_doll

HANDLED = {}        # effect id -> where the code acts on it
ASSUMED = {}        # effect id -> id of the row of the sheet Assumptions (data_tables/sim_setup.xlsx) it rests on


def handles(where, *ids, assumption=None):
    """Declares that the code at `where` acts on these effects. assumption: the row of the sheet Assumptions when
    part of the rule is a choice of the model rather than a reading of the program."""
    for i in ids:
        HANDLED.setdefault(i, where)
        if assumption:
            ASSUMED.setdefault(i, assumption)


# --- what the effects are ---------------------------------------------------------------------------------
PLAIN_HIT, MAGIC_POWER = 0, 1
POISON_SHARE, POISON_CAP = 0.05, 250        # 0x482197 (float at 0x6d92ec), 0x4821ed
TRANQUIL_TURNS = 4                          # Tranquil Song asks for 4 turns (docs/FORMULAS.md 12.19)
START_GAUGE, RANDOM_ORDER = 500, 20          # 0x44919a: push 0x1f4 (and /1000.0 at 0x6d96b0); 0x449322 - 0x449329
AMBUSH_CHANCE = {0: 6, 1: 4}                 # 0x4491d1 (the party strikes first), 0x4491e4 (the enemies)
WEAPON_ELEMENTS = {325: 4, 326: 5, 327: 8, 328: 6, 329: 7}            # fire, water, lightning, wind, earth
AILMENTS = {113: 'poison', 114: 'freeze', 115: 'paralysis', 116: 'sleep', 117: 'silence', 118: 'stun',
            119: 'instant death', 120: 'petrification', 122: 'slow', 123: 'shadow sew'}
# Resistance each ailment roll reads (docs/FORMULAS.md 5b: the stat index pushed by the apply method of each class,
# 6-13 being slash ... lightning): poison 0x481ea0 and freeze 0x4822c0 water, paralysis 0x482530 lightning,
# sleep 0x4827a0 and silence 0x482a10 wind, stun 0x482c80 fire, death 0x482e40, petrification 0x4831f0 and slow
# 0x4835d0 earth. Shadow Sew (0x483840) reads none: it compares levels.
AILMENT_RESIST = {113: 4, 114: 4, 115: 7, 116: 5, 117: 5, 118: 3, 119: 6, 120: 6, 122: 6}
# Statuses of the list Cures and Esarhaddon walk (table 0x6cc79c; Esarhaddon 0x6c9a7c stops at slow)
CURE_ORDER = (113, 115, 117, 114, 116, 120, 122)
ACTION_CAPS = (295, 296)                            # heal cap, damage cap: properties of the action, never statuses
RANDOM_MOVES = (152, 153, 154, 155)                # a skill that performs one of a table of skills (Battle.random_move)
ITEM_CURE_ONE, ITEM_CURE_ALL = 6, 7                # item effect types (docs/FORMULAS.md 15)
CURE_ALL = 8                                   # 0x481b12: a value of exactly 8 also clears the second list (slot 0x90)
ESARHADDON_ORDER = (113, 115, 117, 114, 116, 122)
STAT_STATUSES = (41, 42, 43, 44, 45, 46, 189, 193, 194, 48, 172, 169, 184, 185, 186, 202, 248, 341)
handles('units.Unit.stat / resistance / max_hp (docs/FORMULAS.md 12.6)', *STAT_STATUSES)
ATTACK_MODIFIERS = (26, 443, 111, 286, 161, 195, 335, 219)             # added to the modifiers of attack B (2.2)
DEFENCE_MODIFIERS = (28, 162, 187, 196, 205, 336, 219)                 # added to those of defence A (2.3)
ACCURACY_BUFFS, EVASION_BUFFS = (166, 197, 337), (164, 198, 338)
# magic hit (0x44d700 - 0x44d955): the user's terms and the target's
MAGIC_ACCURACY_BUFFS, MAGIC_EVASION_BUFFS = (167, 309, 197, 222, 278, 353), (165, 198)
# magic defence A (0x44e406 - 0x44e57d): modifiers of the target
MAGIC_DEFENCE_MODIFIERS = (163, 196, 205, 336, 213, 220, 223)
# element boost of a spell: the status of the element on the caster and the "<element> magic buff" enchantment
ELEMENT_BOOST = {4: (325, 78), 5: (326, 79), 6: (328, 80), 7: (329, 81), 8: (327, 82)}
DOLL_MAGIC_SCALE = 500.0                     # 0x44de26 (float at 0x6d9640)
SPEED_BUFFS = (168, 217, 221, 201, 340, 316)
CHANT_SPEED_BUFFS = (214, 265, 281)
CRIT_TERMS = (31, 174, 211)
# magic hit (0x44d759 - 0x44da43): Maid Mastery (278) and effect 353 count only for skill 205, Lullaby (0x44d8ea);
# the divisor is the value of the target's Nocturne (220), else of its Kotodama Blessing (223), else 1 (0x44d95f)
LULLABY, LULLABY_ACCURACY = 205, (278, 353)
# the value of an effect of these classes is its figure plus the value of the user's passives of these effects (the
# getters at slot 0x2c: 0x483a20 for 128, 129, 130, 168; 0x48a8f0 for 272, 273; each asks 0x48bf90, which returns the
# passive's value): Maid Mastery and Maximum Maid raise First Aid, Cook, Self-Sacrifice, Clean and the like
# what a dispel removes (0x4fb1f0; slot 0x64 of each status class, 0x4151e0 yes, else slot 0x54): always these, ...
DISPEL_ALWAYS = (27, 171, 325, 326, 327, 328, 329, 101, 102, 181, 189, 191, 193, 194)
# ... and these while their value is not negative (0x479df0: value >= 0), a buff and not a debuff
DISPEL_IF_RAISED = (21, 26, 28, 31, 41, 42, 43, 44, 45, 46, 161, 162, 163, 164, 165, 166, 167, 168, 169, 172, 173,
                    174, 184, 185, 186)
VALUE_BONUS = {128: (278, 353), 129: (278, 353), 130: (278, 353), 168: (278, 353), 272: (278,), 273: (278,)}
MAGIC_HIT_DIVISORS = (220, 223)
AGE_ONLY = {149: False, 150: True}          # an action with 149 cannot hit an adult, one with 150 a minor (0x44affd)
STAB_EVASION = 253                          # Flowing Water Stance: evasion against stab blows, then a counter (0x44b12a)
# hits a piece of these enchantments makes void (0x421ae4 - 0x421c5a): enchantment -> attribute; 123 voids every blow
NULLIFY_ENCHANTS = {120: (SLASH,), 121: (STAB,), 122: (BASH,), 123: PHYSICAL_ATTRS, 124: (FIRE,), 125: (WATER,),
                    126: (WIND,), 127: (EARTH,), 128: (LIGHTNING,)}
NULLIFY_BLOWS_ONLY = (120, 121, 122, 123)
# what an ailment ends when it lands (status creation 0x4f9930: the end-chant, end-song, end-dance and end-doll calls
# 0x43bc50, 0x43c110, 0x43c600, 0x43c9b0 under each id)
AILMENT_ENDS = {114: ('dance', 'doll'), 116: ('chant', 'song', 'dance', 'doll'), 117: ('chant', 'song'),
                118: ('chant', 'song', 'dance', 'doll'), 121: ('chant', 'song', 'dance', 'doll'),
                123: ('chant', 'song', 'dance', 'doll')}
MATERIAL_GUARD = 179
GENJIMARU, GENJIMARU_ACTION = 427, 107       # 0x48b1f0; the hidden skill of the unit it creates
GENJIMARU_LIFE = 3                           # 0x48b325: the life the doll constructor is given (push 3)
ARCANE_CHANCE = 15                           # 0x424766: the roll of Arcane Shield, a figure written in the program
SHADOW_ATTACK = 2                            # 0x4fe3ca: add eax, eax on the ATK of the shadow
SHADOW_LIFE = 3                             # 0x437a2e: the life the shadow of Shadow Heart is given (push 3)
SACRIFICE, MAX_HP_DRAIN, EXTRA_TARGETS = 77, 133, 137
SAMSARA_STEP = 50                            # 0x438f1e: imul 0x32 on rand(2) + 1
SPECIAL_SLEEP = (143, 10.0, 5)               # 0x484150: a sleep command of value 10.0 (0x4841da), recovery 5 (0x484201)
MURDER, DARK_QUEST, KNOCK_DOWN, PRETEND, DEMON_WALL, ENEMIES_FLEE = 258, 263, 305, 310, 356, 432
# the third argument of CreateCommand (0x47b2ea: the turns of a status, the starting recovery chance of an ailment)
# as the passives pass it: Dark Aura 0x423e30, Ecstasy 0x47f5fc, Slow Target 0x4244c7 / 0x424559, Sugar Coma 0x42291d
DARK_AURA_TURNS, ECSTASY_TURNS = 4, 3
SLOW_TARGET, SUGAR_COMA = (5, 5), (5, 3)          # (recovery start of Slow, turns of the speed modifier)
handles('units.build_member (docs/FORMULAS.md 10.4, 12.17)', 243, 298, 256, 449)
handles('Battle.physical_damage (2.2 - 2.4)', 26, 161, 195, 335, 219, 162, 187, 196, 205, 336, 28, 69, 73, 191, 190,
        308, 440, 443, 87, 88, 47, 49, 50, 111, 286, 255, 325, 326, 327, 328, 329, 0)
handles('Battle.physical_damage (2.4, "other" bonus; 0x44c60e - 0x44c75f)', 71, 136, 179)
handles('Battle.hits (2.1, 3)', 29, 55, 72, *ACCURACY_BUFFS, *EVASION_BUFFS, 30, *MAGIC_ACCURACY_BUFFS,
        *MAGIC_EVASION_BUFFS, 220, 221)
handles('Battle.magic_damage (3; 0x44dcc0 - 0x44e6c6)', 1, 27, 173, 183, 163, 244, 296, 301, 212, 196, 205, 336, 213,
        220, 223)
handles('Battle.hit_chance (2.1, 3; 0x44aa08 - 0x44b0e8, 0x44d700 - 0x44db2c)', 309, 197, 198, 222, 278, 353, 223,
        149, 150, 253)
handles('Battle.critical (4)', *CRIT_TERMS, 32, 70, 110, 125)
handles('Battle.wait (5)', *SPEED_BUFFS, *CHANT_SPEED_BUFFS, 261, 276, 277, 352)
handles('Battle.interrupt (2.5)', 264)
handles('Battle.number_of_hits (12.2)', 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 178, 210, 251, 252)
handles('Battle.perform (random targets, 0x43f8a2)', 112)
handles('Battle.special_damage (12.3)', 8, 12, 138, 140, 141, 142, 434, 435)
handles('Battle.apply_ailment (5b, 5c)', *AILMENTS)
handles('Battle.after_hit (12.9)', 74, 75, 76, 2, 54, 60, 61, 84, 106, 235, 262, 304, 293, 320, 121, 139, 25, 170, 66,
        80, 79, 168, 249)
handles('Battle.voided (12.12)', 171, 101, 102, 181, 182, 192, 285, 250, 303, 307, 180, 349, 346, 260)
handles('Battle.heal (6b, 6d)', 103, 9, 245, 295, 317, 104, 105, 128, 129, 130, 131, 132, 426)
handles('Battle.tick and end_of_turn (12.15)', 246, 247, 215, 216, 199, 200, 204, 339, 288, 289, 354, 311, 147, 297)
handles('Battle.resolve (2.4, the changes of the final value; 0x44cda2)', 86)
# Breath Attack: no place of the program asks for effect 3 (sheet EffectRules); the attacks that carry it deal their
# damage through their effect 1, which Battle.magic_damage plays
handles('nothing reads it: the damage of a breath is its effect 1', 3)
handles('Battle.take_damage (12.7)', 257, 188, 254, 312, 447)
handles('Battle.turn and Unit.resistance (Heretic Samsara, 0x438e53, 0x4fc76f)', 291)
handles('Battle.turn and lost_turn (12.4, 12.19)', 259, 283, 203, 345)
handles('Battle.perform', 10, 425, 358, 152, 153, 154, 155, 315, 228, 229, 230, 231, 232, 233, 266, 279, 280, 287, 284,
        313, 123, 300, 348)
handles('Battle.use_item (15)', 274, 275)
handles('Battle.ambush (0x44a3d0)', 267, 268, 321)
handles('Battle: the effects read on 2026-10-08 (docs/FORMULAS.md 16.8)', 77, 133, 137, 143, 146, 147, 258, 263, 305, 310,
        314, 356, 427, 432)
handles('Battle.before_action and undaunted (12.19)', 350, 355, 357, 446, 448)
# zone value 2 (docs/FORMULAS.md 16.2) is applied in Battle.perform
handles('outside battle: acts on the map, in menus or after the battle (sim/expedition.py)', 17, 18, 20, 22, 107, 108,
        306, 272, 273, 269, 270, 271, 282, 428, 433, 218)


class Action:
    """What a unit does on its turn. source: a Skill, an EnemyAttack, or None for a plain attack or a defence."""
    __slots__ = ('actor', 'kind', 'source', 'level', 'target', 'item', 'chanting', 'fixed_targets', 'furious',
                 '_fx', '_first', '_src', '_lvl', '_kind')

    def __init__(self, actor, kind, source=None, level=1, target=None, item=None, fixed_targets=None):
        self.actor, self.kind, self.source, self.level, self.target, self.item = actor, kind, source, level, target, item
        self.chanting = False
        self.fixed_targets, self.furious = fixed_targets, False
        self._src = self._lvl = self._kind = self._first = None

    # what the action carries ------------------------------------------------------------------------
    def effects(self):
        """[(effect id, kind, value)] at the level of the action. Worked out once per action (the policy asks for
        it tens of thousands of times a battle); worked out again if the source, the level or the kind change."""
        if self._first is None or self._src is not self.source or self._lvl != self.level or self._kind != self.kind:
            self._refresh()
        return self._fx

    def _refresh(self):
        self._fx = self._effects()
        first = {}
        for e, _, v in self._fx:
            first.setdefault(e, v)
        self._first, self._src, self._lvl, self._kind = first, self.source, self.level, self.kind

    def _effects(self):
        s = self.source
        if isinstance(s, Skill):
            return [(e, k, values[min(self.level, len(values)) - 1] +
                     sum(self.actor.passives.get(b, 0.0) for b in VALUE_BONUS.get(e, ())))
                    for e, k, values in s.effects]
        if isinstance(s, EnemyAttack):
            return list(s.effects)
        if self.kind == 'attack':
            found = [(PLAIN_HIT, 4, 1.0)]
            for enchant, (effect, value) in f.PLAIN_ATTACK_ENCHANTS.items():
                if self.actor.pieces(enchant) and not any(e == effect for e, _, _ in found):
                    found.append((effect, 4, value))
            return found
        return []

    def value(self, effect, default=None):
        if self._first is None or self._src is not self.source or self._lvl != self.level or self._kind != self.kind:
            self._refresh()
        return self._first.get(effect, default)

    def has(self, effect):
        if self._first is None or self._src is not self.source or self._lvl != self.level or self._kind != self.kind:
            self._refresh()
        return effect in self._first

    @property
    def target_code(self):
        if self.source is None:
            return SINGLE if self.kind == 'attack' else SELF
        return self.source.target

    @property
    def attr(self):
        if self.source is None:
            # Weapon Element (325 - 329): a plain attack counts as that element, unless two of them are on the unit
            elements = [WEAPON_ELEMENTS[e] for e in WEAPON_ELEMENTS if e in self.actor.statuses]
            if len(elements) == 1:
                return elements[0]
            return self.actor.attack_attr
        a = self.source.attr
        if a in (None, -1, WEAPON_ATTR):
            return self.actor.attack_attr
        return a

    @property
    def function(self):
        """The attack function the program runs for the action (0x420156 - 0x42016d, 0x421238 - 0x42197d): the
        physical one when the action carries effect 0, else the magic one when it carries effect 1 or 25 (with 25 the
        damage is thrown away and only the hit counts, 0x421a83); an action with none of the three runs neither: it
        lands, and its own rolls decide, as an ailment of a status skill or a steal does."""
        if self.has(PLAIN_HIT):
            return 'physical'
        if self.has(MAGIC_POWER) or self.has(25):
            return 'magic'
        return None

    @property
    def magic(self):
        """A spell that deals damage: the magic function with a power."""
        return not self.has(PLAIN_HIT) and self.has(MAGIC_POWER)

    @property
    def physical(self):
        return self.has(PLAIN_HIT)

    @property
    def hit_roll(self):
        """Which hit formula decides whether the action lands on an opponent: the one of its attack function."""
        return self.function

    @property
    def spell(self):
        """What an anti-magic zone stops: a skill of the magic file (0x41e04f, the record is in the spell table
        0x738a58) and an enemy attack whose record has bit 2 of the word at file 0x28 (+0x40 in memory, 0x41a483).
        Techniques are not stopped, nor enemy attacks with a magic power but without the bit. The third test
        (0x41c184, +0x50 bit 5 of table 0x738a54) is of the joint skills, which the model leaves out."""
        s = self.source
        return (isinstance(s, Skill) and s.category == 'Magic') or (isinstance(s, EnemyAttack) and bool(s.spell))

    @property
    def reach(self):
        s = self.source
        if s is None:
            return self.actor.attack_range
        if isinstance(s, Skill):
            if s.category == 'Magic':
                return NO_RANGE
            if s.range == SHORT and s.weapons and self.actor.weapon is not None:
                return min(self.actor.attack_range, SHORT) if 0 in s.weapons else s.range
            return s.range if s.range is not None else self.actor.attack_range
        return s.range if s.range is not None else NO_RANGE

    @property
    def tp_cost(self):
        if isinstance(self.source, Skill):
            return self.source.tp[min(self.level, len(self.source.tp)) - 1]
        return 0

    @property
    def speed(self):
        if isinstance(self.source, Skill):
            return self.source.speed[min(self.level, len(self.source.speed)) - 1]
        if isinstance(self.source, EnemyAttack):
            return self.source.speed or 1.0
        return 1.0

    @property
    def chant_speed(self):
        s = self.source
        if isinstance(s, Skill) and s.chanted:
            return s.cast[min(self.level, len(s.cast)) - 1]
        if isinstance(s, EnemyAttack) and s.chanted:
            return s.chant_speed
        return None

    @property
    def turns(self):
        s = self.source
        if isinstance(s, Skill):
            return s.turns[min(self.level, len(s.turns)) - 1]
        if isinstance(s, EnemyAttack):
            return s.turns
        return 0

    def __repr__(self):
        return f'<Action {self.actor.name} {self.kind} {getattr(self.source, "name", "")} L{self.level}>'


class Recorder:
    """What happened in a battle, for the measures of sim/measures.py."""

    def __init__(self):
        self.damage = {}          # unit -> damage dealt to the other side
        self.healing = {}
        self.actions = {}         # unit -> number of actions
        self.skill_uses = {}      # (unit, skill name) -> uses
        self.tp_spent = {}
        self.items_used = {}
        self.chants_started = {}
        self.chants_done = {}
        self.chants_broken = {}
        self.performances_broken = {}   # unit -> songs, dances or dolls ended by damage
        self.turns_lost = {}      # unit -> turns it could not act
        self.denied = {}          # enemy -> turns taken from it by the party (sleep, paralysis, Warning Shot ...)
        self.delayed = {}         # enemy -> time its turns were pushed back (stun, turn delay)
        self.largest_hit = {}     # enemy -> largest damage of one action on one member
        self.deaths = {}
        self.kills = 0

    def add(self, table, key, amount=1):
        table = getattr(self, table)
        table[key] = table.get(key, 0) + amount


class Battle:
    def __init__(self, data, party, enemies, rng, choose_member=None, choose_enemy=None, setup=None, zone=None,
                 max_time=400.0, max_actions=3000):
        from sim import ai
        self.data, self.rng = data, rng
        self.units = list(party) + list(enemies)
        for k, u in enumerate(self.units):
            u.position = k
        self.choose_member = choose_member
        self.choose_enemy = choose_enemy or ai.choose
        self.setup = setup or {}
        self.zone = zone or {}
        self.time = 0.0
        self.max_time, self.max_actions = max_time, max_actions
        self.record = Recorder()
        self.actions = 0
        self.log = None
        self.extra_turns = []
        self.fixed = False        # a fixed battle of the story (the boss fights); set by scenario.play
        self.spent = set()        # (unit, effect): a passive spent in this battle (a passive is a status, 12.15)

    # --- sides --------------------------------------------------------------------------------------------
    def side(self, side, alive=True):
        return [u for u in self.units if u.side == side and (u.alive or not alive)]

    def allies(self, unit, alive=True):
        return self.side(unit.side, alive)

    def opponents(self, unit, alive=True):
        return self.side(1 - unit.side, alive)

    def members(self):
        return [u for u in self.units if u.side == PARTY and u.kind == 'member']

    def over(self):
        party = [u for u in self.units if u.side == PARTY and u.alive and u.kind == 'member']
        return not party or not self.side(ENEMIES)

    # --- the order of turns ---------------------------------------------------------------------------------
    def wait(self, unit, action=None, chanting=False):
        """1 - the gauge value written after this action (docs/FORMULAS.md 5)."""
        stat_name, f1, f2 = 'agi', 1.0, 1.0
        bonus = sum(unit.status_value(e) for e in SPEED_BUFFS) + unit.passives.get(316, 0.0) * (unit.kind == 'doll')
        if unit.hp <= 0.4 * unit.max_hp and unit.has(261):
            bonus += unit.value(261)
        enchant = f.speed_enchant_bonus(unit.pieces(51), unit.pieces(52), unit.pieces(53))
        if action is not None:
            if chanting:
                stat_name = action.source.chant_stat if isinstance(action.source, Skill) else self._enemy_chant_stat(action)
                stat_name = stat_name or 'agi'
                f2 = action.chant_speed or 1.0
                bonus = sum(unit.status_value(e) for e in CHANT_SPEED_BUFFS) + unit.passives.get(265, 0.0) \
                    + unit.passives.get(281, 0.0)
                enchant = f.speed_enchant_bonus(unit.pieces(54), unit.pieces(55), unit.pieces(56), 0.20, 0.10, 0.20)
            elif action.kind in ('skill', 'enemy'):
                f1 = action.speed + (unit.value(352) if unit.unique and unit.unique[0] == 352 else 0.0)
                if isinstance(action.source, Skill) and action.source.category == 'Magic':
                    f2 = f1                       # 0x449dbe - 0x449df6: a spell performed reads its speed twice
                if any(action.has(e) for e in SONG_EFFECTS):
                    bonus += unit.value(276)      # Singing Speed Modifier
                if any(action.has(e) for e in DANCE_EFFECTS):
                    bonus += unit.value(277)      # Dancing Speed Modifier
        stat = unit.stat(stat_name)
        value = f.turn_value(stat, unit.weight, unit.level, f1 * f2, bonus + enchant, slowed=122 in unit.statuses,
                             defending=action is not None and action.kind == 'defend',
                             random=self.rng.choice(f.SPEED_RANDOM))
        if chanting and unit.pieces(298):
            value = min(f.VALUE_CAP, value + 0.25)
        return max(1.0 - f.VALUE_CAP, 1.0 - value)

    def _enemy_chant_stat(self, action):
        """An enemy attack chants with INT (bit 11) or RES (bit 12) of the word at file 0x28 (0x449b0d - 0x449b38);
        every chanted attack of the file has exactly one of the two (sim/data.py)."""
        return getattr(action.source, 'chant_stat', None) or 'agi'

    def start(self):
        """The gauges at the start of a battle (0x449130). A unit acts when its gauge reaches 1, so it first waits
        1 - gauge. A party member or an enemy starts at (a number below 500, plus 1) / 1000; a guest ally or a summon
        (unit number 3000, set at 0x4497ce) at the value of a plain action (slot 0x20 of the battle). Then the party
        may strike first and, failing that, the enemies (ambush); with neither, a roll below 100 under 20 gives every
        unit a gauge of (a number below 93) / 100 (0x44931c - 0x449373). First Grid then rolls for its bearer
        (0x4493d6)."""
        for u in self.units:
            if u.kind in ('summon', 'npc'):
                gauge = 1.0 - self.wait(u)
            else:
                gauge = (self.rng.randrange(START_GAUGE) + 1) / 1000.0
            u.next_time = 1.0 - gauge
        ambush = self.ambush(PARTY) or self.ambush(ENEMIES)
        if not ambush and self.rng.randrange(100) < RANDOM_ORDER:
            for u in self.units:
                u.next_time = 1.0 - self.rng.randrange(93) / 100.0
        for u in self.units:
            if u.has(300) and self.roll(u.value(300)):                  # First Grid
                u.next_time = 0.0

    def ambush(self, side):
        """0x44a3d0, called for the party (6 in 100) then for the enemies (4 in 100) at 0x4491cf - 0x4491e8. Only a
        battle flagged as random (+0x32 of the battle) rolls, unless a unit of the side has Absolute Preemptive
        Attack (321), which makes it certain; Preemptive Attack Chance (268) of the side adds value * 100; Preemptive
        Attack Evasion (267) of the other side then rolls to stop it. On success every unit of the side starts with
        a full gauge."""
        mine = [u for u in self.units if u.side == side and u.alive]
        others = [u for u in self.units if u.side != side and u.alive]
        certain = any(u.has(321) for u in mine)
        if not certain and not self.setup.get('random_battle'):
            return False
        chance = AMBUSH_CHANCE[side] + int(max((u.value(268) for u in mine), default=0.0) * 100)
        if not certain:
            if self.rng.randrange(100) >= chance:
                return False
            if self.rng.randrange(100) < int(max((u.value(267) for u in others), default=0.0) * 100):
                return False
        for u in mine:
            u.next_time = 0.0
        return True

    # --- the battle -----------------------------------------------------------------------------------------
    def run(self):
        self.start()
        self.lowest_hp = self.party_hp_share()
        while not self.over() and self.time < self.max_time and self.actions < self.max_actions:
            unit = min((u for u in self.units if u.alive), key=lambda u: (u.next_time, u.position))
            self.time = unit.next_time
            self.turn(unit)
            self.lowest_hp = min(self.lowest_hp, self.party_hp_share())
        return self.result()

    def party_hp_share(self):
        members = self.members()
        return sum(u.hp for u in members if u.alive) / max(1, sum(u.max_hp for u in members))

    def result(self):
        members = self.members()
        enemies = [u for u in self.units if u.side == ENEMIES]
        return {'won': not self.side(ENEMIES), 'lost': not any(u.alive for u in members), 'time': self.time,
                'actions': self.actions, 'record': self.record,
                # the measures of the back and forth of a fight (Regression R10)
                'lowest_hp': getattr(self, 'lowest_hp', self.party_hp_share()),
                'enemy_damage': sum(self.record.damage.get(u, 0) for u in enemies),
                'enemy_actions': sum(self.record.actions.get(u, 0) for u in enemies),
                'party_max_hp': sum(u.max_hp for u in members),
                'hp_left': sum(u.hp for u in members) / max(1, sum(u.max_hp for u in members)),
                'tp_left': sum(u.tp for u in members) / max(1, sum(u.max_tp for u in members)),
                'alive': sum(1 for u in members if u.alive)}

    def turn(self, unit):
        """One turn of a unit: the states of docs/FORMULAS.md 12.15."""
        self.actions += 1
        unit.turns_taken += 1
        unit.defending = False
        # only the second action of Did You Call for Me? was read as part of the same turn; the extra actions of
        # Double and Triple Action are left as they were played (every rule has its address)
        again = getattr(unit, 'extra_turn', False) and getattr(unit, 'extra_unique', False)
        # state 0: Esarhaddon
        if unit.has(311):
            for effect in ESARHADDON_ORDER[:int(unit.value(311))]:
                unit.statuses.pop(effect, None)
        # Heretic Samsara (0x438e53 - 0x438fef): once under half its HP, at the update of its turn each of the eight
        # resistances of the bearer is set to (rand(2) + 1) * 50
        if unit.samsara is not None and (unit.samsara or unit.hp < unit.max_hp / 2):
            unit.samsara = [(self.rng.randrange(2) + 1) * SAMSARA_STEP for _ in range(8)]
        # state 2: Third Eye Wide of each opponent
        for other in self.opponents(unit):
            if other.unique and other.unique[0] == 345 and self.roll(other.unique[1]):
                effect = self.rng.choice((113, 115, 116, 114, 117, 118, 74))
                if effect == 74:
                    pass        # the seventh result removes nothing: 0x47ee6f jumps over the dispel (scratch/qol_fields_reading.md 7)
                else:
                    self.apply_ailment(other, unit, effect, 0.75, None)
        acted = False
        lost = self.lost_turn(unit)
        if lost:
            self.record.add('turns_lost', unit)
        else:
            self.before_action(unit)
            action = self.next_action(unit) if unit.alive else None
            if action is not None:
                acted = True
                self.perform(action)
        # the action gained by Did You Call for Me? belongs to the same turn: the statuses of the unit run their
        # per-turn method once, after the first (0x439103; scratch/qol_fields_reading.md 6)
        self.end_of_turn(unit, acted, ticks=lost != 'skip' and not again)
        self.undaunted()

    def before_action(self, unit):
        """States 3, 13, 14 and 15 (docs/FORMULAS.md 12.19): the unique skills that act before the action."""
        if not unit.unique:
            return
        effect, value = unit.unique
        if effect == 446 and unit.items and self.roll(value) and self.choose_member:
            from sim.policy import act_item                              # Overstock Clearance: an item of her stock
            hurt = any(m.hp_ratio < 0.6 for m in self.allies(unit) if m.kind == 'member')
            item = act_item(None, self, unit, 'heal' if hurt else 'tp')
            if item is not None:
                self.use_item(item)
        if effect == 357 and self.roll(value):                           # Tranquil Song: ATK and INT -0.1, 4 turns
            for other in self.opponents(unit):
                other.statuses[41] = Status(41, -0.1, TRANQUIL_TURNS, unit)
                other.statuses[43] = Status(43, -0.1, TRANQUIL_TURNS, unit)
        if effect == 350 and self.roll(value):                           # Usurper of Souls
            for other in [u for u in self.units if u.side != unit.side and u.alive and u.kind in ('doll', 'summon')]:
                self.remove_doll(other)
        if effect == 448 and self.roll(value):                           # Shadow Heart
            if not any(u.alive and getattr(u, 'shadow_of', None) is unit for u in self.units):
                self.add_shadow(unit)

    def add_shadow(self, owner):
        """Shadow Heart (0x4379fb - 0x437a44): a copy of its owner (constructor 0x4fe2e0, which passes on to the doll
        constructor) with a life of SHADOW_LIFE turns and no action of its own, so it makes plain attacks; one at a
        time for each owner (0x43793b - 0x4379f5)."""
        unit = build_doll(owner, {'name': owner.name + "'s shadow", 'turns': [SHADOW_LIFE], 'range': None,
                                  'actions': []}, 1)
        # 0x4fd0b0 copies the stats its owner has at that moment and 0x4fe3c1 - 0x4fe3d2 doubles the ATK; the passives
        # stay (Double and Triple Attack among them), the ailments and the statuses of techniques do not
        # (0x4fe337 - 0x4fe3bf; scratch/qol_fields_reading.md 5)
        unit.base = {s: owner.stat(s) for s in unit.base}
        unit.base['atk'] *= SHADOW_ATTACK
        unit.passives = dict(owner.passives)
        unit.enchants = dict(owner.enchants)
        unit.swing = owner.swing
        unit.shadow_of = owner
        unit.position = len(self.units)
        unit.next_time = self.time + self.wait(unit)
        self.units.append(unit)

    def undaunted(self):
        """State 22: each fallen unit with Undaunted Spirit rolls and rises; the record of the revival carries 1."""
        for u in self.units:
            if not u.alive and u.kind == 'member' and u.unique and u.unique[0] == 355 and self.roll(u.unique[1]):
                u.alive, u.hp = True, 1
                u.next_time = self.time + self.wait(u)

    def lost_turn(self, unit):
        """States 4 to 11 (0x436c40 - 0x436d4c): a petrified unit (slot 0xc8) and a sleeping one (slot 0xbc) lose the
        turn; a paralysed one (slot 0xb8) loses it on a roll below 100 under 30. Freeze and Shadow Sew do not stop a
        unit: they narrow what it may do (next_action).
        Returns 'skip' when the turn goes to phase 4 (0x4392ef), which ends it without state 16: no status of the unit
        runs its per-turn method (regeneration, poison, songs, recovery of ailments, the count of turns); petrification,
        sleep, paralysis (0x436cf9), Mesmerized and the Erotic Dance (0x4372ea) do so. Returns 'empty' for Warning
        Shot, which replaces the command with a skill that does nothing (state 12, 0x4371c3): state 16 still runs."""
        if not unit.alive:
            return 'skip'
        if 120 in unit.statuses or 116 in unit.statuses:
            return self.deny(unit, 'skip')
        if 115 in unit.statuses and self.rng.randrange(100) < 30:
            return self.deny(unit, 'skip')
        for other in self.opponents(unit):
            for effect in (259, 283):                 # Warning Shot, Mesmerized
                if other.has(effect) and self.roll(other.value(effect)):
                    return self.deny(unit, 'empty' if effect == 259 else 'skip')
        if unit.has(203) and self.roll(unit.value(203)):
            return self.deny(unit, 'skip')
        return False

    def deny(self, unit, how):
        if unit.side == ENEMIES:
            self.record.add('denied', unit)
        return how

    def next_action(self, unit):
        if unit.chant is not None:
            action, unit.chant = unit.chant, None
            action.chanting = False
            self.record.add('chants_done', unit)
            return action
        if unit.kind == 'doll':
            return self.doll_action(unit)
        if unit.side == PARTY and unit.kind == 'member' and self.choose_member:
            action = self.choose_member(self, unit)
        else:
            action = self.choose_enemy(self, unit)
        if action is None:
            return None
        # silence forbids spells and songs, freeze techniques, dolls and dances (atwiki dt2-2 page 125; an enemy takes
        # attack slot 0 instead, sim/ai.py)
        category = action.source.category if isinstance(action.source, Skill) else None
        if (117 in unit.statuses and category == 'Magic') or (114 in unit.statuses and category == 'Technique'):
            action = Action(unit, 'attack')
        speed = action.chant_speed
        if speed and not (unit.unique and unit.unique[0] == 358 and self.roll(unit.unique[1])):   # Forerunner
            self.pay(action)
            action.chanting = True
            unit.chant = action
            self.record.add('chants_started', unit)
            return Action(unit, 'chant', action.source, action.level)
        return action

    def pay(self, action):
        cost = action.tp_cost
        if cost <= 0:
            return
        unit = action.actor
        technique = isinstance(action.source, Skill) and action.source.category == 'Technique'
        if unit.pieces(246 if technique else 248):
            cost = int(cost * 0.8)
        if unit.pieces(247 if technique else 249):
            cost = int(cost * 0.6)
        cost = max(1, cost)
        if unit.has(266):
            cost = max(1, cost - int(math.ceil(cost * unit.value(266))))
        unit.tp = max(0, unit.tp - cost)
        self.record.add('tp_spent', unit, cost)
        action.item = action.item

    def end_of_turn(self, unit, acted, ticks=True):
        """State 16: each status of the unit runs its per-turn method; then the wait until its next turn. After a turn
        lost to an ailment the wait is the one of a plain action (assumption A22: the gauge phase 4 leaves is not read)."""
        if unit.alive and ticks:
            self.tick(unit)
        if not unit.alive:
            return
        last = self._last_action.get(unit) if hasattr(self, '_last_action') and acted else None
        if unit.chant is not None:
            wait = self.wait(unit, unit.chant, chanting=True)
        else:
            wait = self.wait(unit, last)
        unit.next_time = self.time + wait
        # Double and Triple Action (12.14), Did You Call for Me? (12.19): the unit acts again at once, once or twice
        if getattr(unit, 'extra', 0) > 0:
            unit.extra -= 1
            unit.next_time = self.time
            unit.extra_turn = True
        elif getattr(unit, 'extra_turn', False):
            unit.extra_turn = False                   # the extra actions do not roll again
            unit.extra_unique = False
        elif acted and unit.chant is None and not self.over():
            if unit.has(288) and self.roll(unit.value(288)):
                unit.extra = 1
            elif unit.has(289) and self.roll(unit.value(289)):
                unit.extra = 2
            elif unit.unique and unit.unique[0] == 354 and self.roll(unit.unique[1]):
                unit.extra = 1
                unit.extra_unique = True
            if getattr(unit, 'extra', 0) > 0:
                unit.extra -= 1
                unit.next_time = self.time
                unit.extra_turn = True

    def tick(self, unit):
        # HP and TP regeneration of a passive (Auto-Recovery, Auto-Refresh; the HP Regen of enemies) act each turn of
        # their bearer like the statuses of the same effect (docs/FORMULAS.md 12.15, state 16); a status, if any,
        # takes its place
        if 246 in unit.passives and 246 not in unit.statuses:
            self.restore(unit, int(unit.max_hp * unit.passives[246]))
        if 247 in unit.passives and 247 not in unit.statuses and unit.side == PARTY:
            unit.tp = min(unit.max_tp, unit.tp + int(unit.passives[247]))
        for effect in list(unit.statuses):
            s = unit.statuses.get(effect)
            if s is None:
                continue
            if effect == 246:
                self.restore(unit, int(unit.max_hp * s.value))
            elif effect == 247 and unit.side == PARTY:
                unit.tp = min(unit.max_tp, unit.tp + int(s.value))
            elif effect == 215:
                bonus = s.data or 0.0
                for ally in self.allies(unit):
                    self.restore(ally, int(s.value * (1 + 10 * bonus)))
            elif effect == 216:
                bonus = s.data or 0.0
                ally = self.rng.choice(self.allies(unit))
                ally.tp = min(ally.max_tp, ally.tp + int(s.value + 100 * bonus))
            elif effect == 113 and 116 not in unit.statuses:
                # 0x482186 - 0x4821ff: int(max HP * 0.05), at most 250; a figure of 0 or one that would take the last
                # HP leaves 1 HP (poison never kills); a sleeping unit takes none
                amount = min(POISON_CAP, int(unit.max_hp * POISON_SHARE))
                if amount <= 0 or amount >= unit.hp:
                    amount = unit.hp - 1
                self.lose_hp(unit, amount, None)
            elif effect in (199, 339):
                amount = int(unit.max_hp * s.value)
                if s.data is not None:          # the Damage cap (296) of the action that put it
                    amount = min(amount, int(s.data))
                self.lose_hp(unit, amount, s.source)
            elif effect == 200:                 # Subtle Dance: int(max HP * value) taken from TP, capped the same way
                amount = int(unit.max_hp * s.value)
                if s.data is not None:
                    amount = min(amount, int(s.data))
                unit.tp = max(0, unit.tp - amount)
            elif effect == 204 and unit.side == PARTY:
                # Weird Dance (0x42bbc7 - 0x42bc75): each time it ticks the Pep of the member changes by its value
                unit.pep = max(70.0, min(130.0, unit.pep + s.value))
            if effect in AILMENTS and effect in unit.statuses and effect not in (119, 123):
                # 0x48d211 - 0x48d228: a number below 100 under the recovery chance ends the ailment; otherwise the
                # chance rises by 10. It starts at the turns figure of the action that caused it (0x47bc03: the third
                # argument of CreateCommand), 0 for every skill of the player
                chance = s.data or 0
                if self.rng.randrange(100) < chance:
                    unit.statuses.pop(effect, None)
                    continue
                s.data = chance + 10
            if s.turns > 0 and effect in unit.statuses:
                s.turns -= 1
                if s.turns <= 0:
                    unit.statuses.pop(effect, None)
        if unit.kind == 'doll':
            unit.life -= 1
            if unit.life <= 0:
                self.remove_doll(unit)

    # --- performing an action -------------------------------------------------------------------------------
    def perform(self, action):
        unit = action.actor
        if not hasattr(self, '_last_action'):
            self._last_action = {}
        self._last_action[unit] = action
        self.record.add('actions', unit)
        if action.kind == 'chant':
            self._last_action[unit] = None
            return
        if action.kind == 'defend':
            unit.defending = True
            return
        if action.kind == 'wait':
            return
        if action.kind == 'item':
            self.use_item(action)
            return
        if self.zone.get('no_magic') and unit.kind != 'doll' and action.spell:
            self.record.add('skill_uses', (unit, 'nullified in an anti-magic zone'))
            return                                  # docs/FORMULAS.md 16.2: magic is nullified there, dolls excepted
        if not action.chanting and action.kind == 'skill' and action.chant_speed is None:
            self.pay(action)
        key = getattr(action.source, 'name', 'Attack')
        if self.log is not None:
            self.log.append(f'{self.time:7.3f} {unit.name} ({unit.hp}/{unit.max_hp} HP, {unit.tp} TP): {key}')
        self.record.add('skill_uses', (unit, key))
        unit.last_skill = action.source
        unit.uses[key] = unit.uses.get(key, 0) + 1
        for random_effect in RANDOM_MOVES:
            if action.has(random_effect):
                action = self.random_move(action, random_effect)
                if action is None:
                    return
        if any(action.has(e) for e in (228, 229, 230, 231, 232, 233, 146)):
            self.make_doll(action)
            return
        if action.has(GENJIMARU):
            self.make_genjimaru(action)
            return
        if unit.unique and unit.unique[0] == 348 and action.physical and self.roll(unit.unique[1]):
            action.furious = True                     # Furious Strike: ignores defence and cannot miss (12.19)
        targets = self.targets(action)
        if not targets:
            return
        hits = self.number_of_hits(action)
        if action.target_code == RANDOM:
            # 0x43f8a2 - 0x43f9a4: one target per hit, picked with equal chances; with effect 112 a unit is picked
            # once at most (the picked one leaves the list)
            pool = list(targets)
            if action.has(112):
                targets = self.rng.sample(pool, min(len(pool), max(1, hits)))
            else:
                targets = [self.rng.choice(pool) for _ in range(max(1, hits))]
            hits = 1
        # Counter Whip: the first target that has it strikes first
        for t in targets:
            if t.side != unit.side and t.has(303) and not unit.has(307):
                self.counter(t, unit)
                break
        damage_by_target = {}
        self.covered = {}                   # unit with Cover -> hits it took in place of another (0x42497a)
        # Auto-Guard (0x417309 - 0x417362): before a physical action each target that has it rolls once, in the order
        # of the targets (not of a set: its order follows memory addresses, and the rolls of two bearers would swap
        # from one run to the next)
        self.guarding = {t for t in dict.fromkeys(targets) if action.physical and t.side != unit.side and t.has(255)
                         and self.roll(t.value(255))}
        index = 0                           # the hit record of the action (effect 136, effect 125)
        for target in targets:
            for h in range(hits):
                if not unit.alive or not target.alive and not action.has(105):
                    break
                done = self.resolve(action, target, index, damage_by_target)
                index += 1
                if done == 'stop':
                    break
        # Cover (0x42497a): after the action, each hit covered rolls value * 100 to end the Cover of that unit
        for cover, count in self.covered.items():
            for _ in range(count):
                s = cover.statuses.get(171)
                if s is not None and self.roll(s.value):
                    cover.statuses.pop(171, None)
        self.guarding = set()
        if action.has(SACRIFICE) and unit.alive:
            # 0x481060: the user takes damage equal to its own max HP
            self.lose_hp(unit, unit.max_hp, unit)
        for target, dealt in damage_by_target.items():
            if unit.side == ENEMIES and target.side == PARTY:
                self.record.largest_hit[unit] = max(self.record.largest_hit.get(unit, 0), dealt)
        # Support Shot: after a plain attack, each other unit of the side that has it rolls in order
        if action.kind == 'attack':
            for ally in self.allies(unit):
                if ally is not unit and ally.has(260) and self.roll(ally.value(260)):
                    alive = [t for t in targets if t.alive] or self.opponents(unit)
                    if alive:
                        self.resolve(Action(ally, 'attack'), alive[0], 0, {})
                    break

    def targets(self, action):
        if action.fixed_targets is not None:
            return [t for t in action.fixed_targets if t.alive or action.has(105)]
        unit, code = action.actor, action.target_code
        foes, friends = self.targetable(self.opponents(unit)), self.allies(unit)
        chosen = action.target
        if code in (SINGLE, PIERCE, ROW):
            if chosen is None or not chosen.alive or chosen.side == unit.side:
                chosen = self.pick_opponent(unit, action)
            if chosen is None:
                return []
            if code == SINGLE:
                if action.has(EXTRA_TARGETS):
                    # 0x42017a - 0x4202f3: the next int(value) - 1 units of the target's side in the order of turns
                    order = sorted((t for t in foes if t is not chosen), key=lambda t: (t.next_time, t.position))
                    return [chosen] + order[:max(0, int(action.value(EXTRA_TARGETS)) - 1)]
                return [chosen]
            if code == ROW:
                return [t for t in foes if t.front == chosen.front]
            return [chosen] + [t for t in self.behind(chosen) if t in foes]
        if code == RANDOM:
            return self.targetable(foes)
        if code == ALL:
            return foes
        if code == EVERYONE:
            return [u for u in self.units if u.alive]
        if code == ANYONE:
            return [self.rng.choice([u for u in self.units if u.alive])]
        if code == SELF or code == NO_TARGET:
            return [unit]
        if code == ALLY:
            if action.has(105):
                dead = [u for u in self.allies(unit, alive=False) if not u.alive and u.kind == 'member']
                if chosen is not None and not chosen.alive:
                    return [chosen]
                return dead[:1]
            return [chosen if chosen is not None and chosen.alive and chosen.side == unit.side else unit]
        if code == RANDOM_ALLY:
            return [self.rng.choice(friends)]
        if code == ALLY_ROW:
            row = chosen.front if chosen is not None else unit.front
            return [t for t in friends if t.front == row]
        if code == ALLIES:
            return friends
        if code == ALLY_MOST_TP_LOST:
            return [min(friends, key=lambda u: u.tp_ratio)]
        return [unit]

    def pick_opponent(self, unit, action):
        foes = self.targetable(self.opponents(unit))
        if not foes:
            return None
        if unit.side == ENEMIES:
            return self.weighted_pick(unit, foes)
        return self.rng.choice(foes)

    def behind(self, unit):
        """The units a piercing action (target code 3) adds to its target: the list each unit keeps at 0x64 - 0x68,
        built at the start of a battle (0x43def0). For the party it depends on how many stand in front (F) and behind
        (B), in party order: F = B, front i has back i; B = F + 1, back i and i + 1; B = F + 2, the middle one; and
        the other way round for a back member. Every case is the overlap of two rows centred on each other, which is
        the rule used here. An enemy is numbered 1000 + its slot in front and 1024 + its slot behind (0x439e0e); a
        front enemy n keeps n + 23, n + 24 and n + 25, a back one n - 25 to n - 23 (0x43e1ad - 0x43e476): the enemies
        of the other row whose slot is within one of its own."""
        if unit.side == ENEMIES and getattr(unit, 'slot', None) is not None:
            return [u for u in self.units if u.side == ENEMIES and u.kind == 'enemy' and u.alive
                    and u.front != unit.front and getattr(u, 'slot', None) is not None and abs(u.slot - unit.slot) <= 1]
        rows = {}
        for u in self.units:
            if u.side == unit.side and u.kind not in ('doll', 'summon', 'npc'):
                rows.setdefault(u.front, []).append(u)
        mine, other = rows.get(unit.front, []), rows.get(not unit.front, [])
        if unit not in mine or not other:
            return []
        centre = mine.index(unit) - (len(mine) - 1) / 2.0
        return [u for j, u in enumerate(other) if abs(j - (len(other) - 1) / 2.0 - centre) <= 0.5 and u.alive]

    def targetable(self, units):
        """The candidates of a pick (0x43e6d0, called by the target picker 0x43f450): only units numbered below 2000.
        A doll or another unit of the ETC classes is numbered 2000 + n (0x43a205), a guest ally or a summon 3000
        (0x4497ce): neither can be picked, by a single, random, row or whole-side action."""
        return [u for u in units if u.kind not in ('doll', 'summon', 'npc')]

    def weighted_pick(self, enemy, party):
        """docs/FORMULAS.md 9.1: the share of the position by formation, Provoke, and the two Enmity enchantments."""
        members = [u for u in party]
        front = [u for u in members if u.front]
        back = [u for u in members if not u.front]
        ordered = front + back
        row = target_share_row(len(ordered), len(front))
        weights = []
        for k, u in enumerate(ordered):
            share = row[k] if k < len(row) else row[-1]
            weights.append(f.target_weight(share, enemy.provoked_by.get(u, 0.0) if 170 in enemy.statuses else 0.0,
                                           u.pieces(49), u.pieces(50)))
        roll = self.rng.random() * sum(weights)
        for u, w in zip(ordered, weights):
            roll -= w
            if roll < 0:
                return u
        return ordered[-1]

    def number_of_hits(self, action):
        """docs/FORMULAS.md 12.2 and the multi-hit tables of the sheet EffectRules."""
        rondo = action.has(210) or action.actor.has(210)
        for effect, (base, picks, weights, rondo_weights) in MULTI_HIT.items():
            if action.has(effect):
                table = rondo_weights if rondo else weights
                hits = base + self.weighted(picks, table)
                break
        else:
            hits = int(action.value(93, 1) or 1)
            if action.kind == 'attack':
                # 0x418045 - 0x4180e3: Triple Attack rolls and adds 3, then Double Attack rolls on its own and adds 2;
                # with neither the attack hits once (1, 2, 3 or 5 hits)
                extra = 0
                if action.actor.has(252) and self.roll(action.actor.value(252)):
                    extra += 3
                if action.actor.has(251) and self.roll(action.actor.value(251)):
                    extra += 2
                hits = extra or 1
        if action.has(178):
            hits += int(action.value(178)) + 1
        return max(1, hits)

    def weighted(self, picks, weights):
        roll = self.rng.random() * sum(weights)
        for p, w in zip(picks, weights):
            roll -= w
            if roll < 0:
                return p
        return picks[-1]

    # --- one hit ----------------------------------------------------------------------------------------------
    @staticmethod
    def aimed(action, target):
        """The hit and the ailments of an action land on an opponent, and on a unit of the user's own side only when the
        action is aimed at that side or at everyone: the results of the random skills that strike the party (Magic
        Box's punch on the user and its instant death, Showtime's stun, sleep and half HP on every ally; atwiki dt2-2
        pages 132 and 148)."""
        return target.side != action.actor.side or action.target_code in OWN_SIDE or \
            action.target_code in (EVERYONE, ANYONE)

    def resolve(self, action, target, index, damage_by_target):
        unit = action.actor
        hostile = target.side != unit.side
        if hostile:
            target = self.redirect(action, target)
            if target is None:
                return None
            # the attack function rolls the hit first (2.1, 3); a hit that misses skips every check after it (0x421ada)
            if not self.hits(action, target):
                return None
            if self.voided(action, target):
                return None
        dealt = 0
        if self.aimed(action, target) and not action.has(25) and (action.physical or action.magic):
            dealt = self.damage(action, target, index)
            if dealt is None:
                return None
            damage_by_target[target] = damage_by_target.get(target, 0) + dealt
        self.after_hit(action, target, dealt)
        return None

    def redirect(self, action, target):
        """Cover (12.12, 0x420b60 - 0x420ed6): an action aimed at one unit or at random units goes to one of the other
        units of the side that have Cover, picked with equal chances, with no roll. The roll that ends the Cover comes
        after the action, once per hit covered (perform)."""
        if action.target_code in (SINGLE, RANDOM):
            covers = [u for u in self.allies(target) if u is not target and 171 in u.statuses and u.alive]
            if covers:
                cover = self.rng.choice(covers)
                covered = getattr(self, 'covered', None)
                if covered is not None:
                    covered[cover] = covered.get(cover, 0) + 1
                return cover
        return target

    def voided(self, action, target):
        """The checks that turn a landed hit away, in the order of the program (12.12; 0x421ae4 - 0x422c4b)."""
        unit = action.actor
        attr = action.attr
        for enchant, attrs in NULLIFY_ENCHANTS.items():          # pieces that nullify an attribute
            if target.pieces(enchant) and attr in attrs and (action.physical or enchant not in NULLIFY_BLOWS_ONLY):
                return True
        if target.has(192) and attr != NEUTRAL:
            return True
        if target.has(182) and action.reach in (SHORT, MID):
            return True
        if target.unique and target.unique[0] == 349 and self.roll(target.unique[1]):
            return True
        if target.has(PRETEND) and action.physical and self.roll(target.value(PRETEND)):
            self.counter(target, unit)      # 0x421db8: no damage; the bearer performs the skill linked to it (A17)
            return True
        if target.has(285) and (target, 285) not in self.spent and (action.physical or action.magic):
            target.statuses.pop(285, None)
            self.spent.add((target, 285))       # Elegant Dancing: the first damaging hit, then spent (12.12)
            return True
        if target.has(KNOCK_DOWN) and action.physical and action.reach == LONG and \
                (unit.side == ENEMIES or unit.weapon is not None) and self.roll(target.value(KNOCK_DOWN)):
            self.counter(target, unit)      # 0x4221ee - 0x422540: a long-range blow with a weapon (A17)
            return True
        if 180 in target.statuses and action.physical:
            if self.roll(target.statuses[180].value):
                target.statuses.pop(180)
            return True
        if target.has(250) and action.reach in (SHORT, MID) and not unit.has(307):
            if self.roll(target.value(250)):
                self.counter(target, unit)
                return True
        if target.unique and target.unique[0] == 346 and action.reach == SHORT and self.roll(target.unique[1]):
            # 0x42291d - 0x4229ff: Slow with a recovery chance that starts at 5, speed -0.2 for 3 turns
            unit.statuses[122] = Status(122, 1.0, 0, target, data=SUGAR_COMA[0])
            unit.statuses[168] = Status(168, -0.2, SUGAR_COMA[1], target)
        for effect in (101, 102, 181):
            s = target.statuses.get(effect)
            if s and not any(action.has(e) for e in (140, 141, 142)) and (action.physical or action.magic):
                s.value -= 1
                if s.value <= 0:
                    target.statuses.pop(effect)
                return True
        return False

    def hits(self, action, target):
        """docs/FORMULAS.md 2.1 and 3: a roll below 100 under the chance cut to an integer. A blow that misses only
        because of Flowing Water Stance is answered by a counter of the target (0x44b12a; A17)."""
        if action.furious:
            return True
        chance = self.hit_chance(action, target)
        dodge = self.stab_dodge(action, target)
        roll = self.rng.randrange(100)
        if roll < int(round((chance - dodge) * 100)):
            return True
        if dodge and roll < int(round(chance * 100)) and target.alive:
            self.counter(target, action.actor)
        return False

    def critical(self, action, target, index=0):
        unit = action.actor
        if target.side == ENEMIES and action.has(110) and target.race == 2:
            return True
        earlier = index if action.has(125) else 0
        rate = f.critical_rate(unit.stat('dex'), target.stat('agi'), unit.level, target.level,
                               # 0x44f262 - 0x44f301: 31, 174, 211 first found among the action and the user,
                               # 32 the target's
                               skill=sum(self.first(action, unit, e) for e in CRIT_TERMS) + target.value(32),
                               enchant=f.critical_enchant(unit.pieces(45), unit.pieces(46)),
                               target_enchant=-f.critical_enchant(target.pieces(47), target.pieces(48)),
                               earlier_hits=earlier, floor_268=bool(unit.pieces(268)),
                               fixed=action.value(70))
        return self.rng.randrange(100) < int(rate)

    def special(self, action):
        return any(action.has(e) for e in (8, 12, 138, 140, 141, 142, 434, 435))

    def damage(self, action, target, index):
        critical = False
        amount = None
        if self.special(action):
            amount = self.special_damage(action, target)
        elif action.magic:
            amount, critical = self.magic_damage(action, target)
        else:
            critical = self.critical(action, target, index)
            amount = self.physical_damage(action, target, index, critical)
        if amount is None:
            return None
        if not self.special(action):
            # Demon Wall (0x44cbf0, 0x44ef59): the first unit of the target's side that has it cuts the damage
            wall = next((u for u in self.allies(target) if u.has(DEMON_WALL)), None)
            if wall is not None:
                amount = max(0, int(amount + amount * wall.value(DEMON_WALL)))
        if 116 in target.statuses and not self.special(action):
            # 0x44cd3b (blow), 0x44eff9 (spell): a sleeping target takes int(damage * 3 / 2); the hit wakes it
            amount = amount * f.SLEEP_DAMAGE[0] // f.SLEEP_DAMAGE[1]
        enchant, share = f.AILING_TARGET_BONUS
        if not self.special(action) and action.actor.pieces(enchant) and any(e in target.statuses for e in AILMENTS):
            amount += int(amount * share)               # 0x44cd5a, 0x44f009
        if action.has(86) and target.kind == 'member' and target.class_id in f.MAGIC_USER_LINE:
            amount += amount                            # 0x44cdf1: Witch Test and the like
        if action.magic:
            cap = action.value(296)
            if cap is not None:
                amount = min(amount, int(cap))
        if action.has(2):
            # 0x44ce96, 0x44f10d: effect 2 sends the damage to TP instead of HP
            target.tp = max(0, target.tp - amount)
            return amount
        self.take_damage(target, amount, action, critical)
        if critical and action.physical and target.alive and (action.has(MURDER) or action.actor.has(MURDER)):
            # Murder (0x44d26f - 0x44d2cf): a critical blow applies instant death at the value, through its roll (5b)
            self.apply_ailment(action.actor, target, 119, self.first(action, action.actor, MURDER), action)
        return amount

    def physical_damage(self, action, target, index, critical, expect=False):
        """expect: the mean of the rolls instead of a roll (no swing, critical as its mean factor), for the policies."""
        unit = action.actor
        furious = action.furious
        # 26 is found first among the effects of the action, then among the statuses of the user (Berserk, High Risk,
        # Defender leave theirs there): the first one found counts (0x44b3c3; the finder 0x47e340 stops at the first)
        modifiers = self.first(action, unit, 26) + (getattr(action.source, 'power', 0.0)
                                                    if isinstance(action.source, EnemyAttack) else 0.0)
        modifiers += sum(unit.status_value(e) for e in (161, 195, 335, 219))
        if unit.unique and unit.unique[0] == 443:
            modifiers += unit.unique[1]
        if unit.kind == 'doll' and unit.owner is not None:
            modifiers += unit.owner.passives.get(286, 0.0) + min(0.05, 0.02 * unit.owner.pieces(304) + 0.01 * unit.owner.pieces(305))
        if action.has(111) and unit.weapon is not None and unit.weapon.get('two_handed') and unit.weapon['type'] == 3:
            modifiers += action.value(111)
        swing = 0.0 if expect else self.swing(unit)
        atk = unit.stat('atk')
        if action.has(49):
            atk = unit.stat('int')
        if action.has(47):
            atk = unit.stat('res')
        if action.has(50):
            atk = atk * action.value(50)
        target_mods = sum(target.status_value(e) for e in (28, 162, 187, 196, 205, 336, 219))     # the target's (0x44b792)
        times = action.value(73, 1.0) or 1.0
        reach = action.reach
        dist = f.distance(not unit.front, not target.front)
        cut = 1.0 - (0.10 * target.pieces(66) + 0.05 * target.pieces(67) + 0.08 * target.pieces(70) + 0.04 * target.pieces(71))
        defending = target.defending or target in getattr(self, 'guarding', ())
        resist_index = RESIST_INDEX.get(action.attr)
        resistance = target.resistance(resist_index) if resist_index is not None else 0
        race_bonus = action.value(88) if (action.has(88) and target.race in (5, 7, 8)) else 0.0
        if action.has(87) and target.race == 5:
            return 0
        race = (self.race_factor(unit, target) + race_bonus) * self.element_factor(unit, target, action.attr)
        # 0x44c723 - 0x44c75f: Limit Field of the target, Power Charge of the user
        other = target.value(190) + unit.status_value(191) + self.full_hp_bonus(unit)
        guard = target.statuses.get(MATERIAL_GUARD)
        if guard is not None and (guard.source is None or (guard.source.alive and guard.source.shield)):
            other += guard.value                    # Material Guard (0x44c6bb - 0x44c720)
        if target.side == PARTY and not target.front:
            guards = [m.passives.get(308) for m in self.allies(target) if m.passives.get(308)]
            if guards:
                other += min(guards)
        if unit.unique and unit.unique[0] == 440 and unit.pep > 100:
            other += (unit.pep - 100) / max(1.0, unit.unique[1]) / 100.0
        if action.has(136):
            other += action.value(136) * index
        if action.has(DARK_QUEST) or unit.has(DARK_QUEST):
            # 0x44c81a - 0x44c896: value times the ailments the attacker carries
            other += self.first(action, unit, DARK_QUEST) * sum(1 for e in unit.statuses if e in AILMENTS)
        if action.has(71):                  # 0x44c60e: once for every buff or debuff on the target (slot 0x88 of a status)
            other += action.value(71) * sum(1 for e in target.statuses if e not in AILMENTS)
        attack_zone = self.zone_factor(unit, action)
        value = f.physical_damage(atk * attack_zone, target.stat('def'), modifiers=modifiers, target_modifiers=target_mods,
                                  enchant=min(50, 4 * unit.pieces(29) + 2 * unit.pieces(30)),
                                  target_enchant=min(50, 4 * target.pieces(33) + 2 * target.pieces(34)),
                                  swing=swing, times=times, ignore_defence=action.has(69) or furious,
                                  range_factor=f.range_factor(reach, dist), damage_cut=cut, race=race,
                                  resistance=resistance, defending=defending,
                                  critical=critical if expect else (f.CRIT_FACTOR if critical else 1.0), other=other)
        if expect:
            return max(float(f.MIN_DAMAGE), value)
        damage = int(value)
        if damage <= 0:
            damage = self.rng.choice((1, 2)) if critical else f.MIN_DAMAGE
        return damage

    def magic_damage(self, action, target, expect=False):
        unit = action.actor
        power = action.value(MAGIC_POWER, 0.0)
        if unit.kind == 'doll' and unit.owner is not None:          # 0x44dda8 - 0x44de68
            owner = unit.owner
            power += DOLL_MAGIC_SCALE * (owner.passives.get(286, 0.0)
                                         + min(0.05, 0.02 * owner.pieces(304) + 0.01 * owner.pieces(305)))
        mastery = unit.passives.get(244, 0.0)
        modifiers = sum(unit.value(e) for e in (195, 335))         # multiply the power only
        second = unit.value(212)                                    # Spiritual Fantasia: attack C
        attr = action.attr
        element_boost = 0.0                                         # 0x44e019 - 0x44e3f4, one block per element
        if attr in ELEMENT_BOOST:
            status, enchant = ELEMENT_BOOST[attr]
            # 0x44e019 - 0x44e0c2: the element's magic buff and the both-sides enchantment count on caster and target
            both = f.BOTH_SIDES_ELEMENT[attr]
            element_boost = f.ELEMENT_ENCHANT_SHARE * ((status in unit.statuses) + unit.pieces(enchant)
                                                       + target.pieces(enchant) + unit.pieces(both)
                                                       + target.pieces(both))
        resist_index = RESIST_INDEX.get(attr)
        resistance = target.resistance(resist_index) if resist_index is not None else 0
        power_boost = self.first(action, unit, 27) + self.first(action, unit, 173)      # 0x44e66e, 0x44e6a2
        cut = max(-0.25, -(0.10 * target.pieces(68) + 0.05 * target.pieces(69) + 0.08 * target.pieces(70)
                           + 0.04 * target.pieces(71))) + target.status_value(183)
        if expect:
            critical = 1.0 + (f.MAGIC_CRIT_FACTOR - 1.0) * f.MAGIC_CRIT_CHANCE / 100.0 if unit.has(301) else 1.0
        else:
            critical = unit.has(301) and self.rng.randrange(100) < f.MAGIC_CRIT_CHANCE
        other = target.value(190) + self.full_hp_bonus(unit)       # Limit Field of the target (0x44ed5b)
        cut += self.race_guard(unit, target) - 1.0                  # 0x44e914 - 0x44eb36
        value = f.magic_damage(unit.stat('int') * self.zone_factor(unit, action), power, target.stat('res'),
                               mastery=mastery, modifiers=modifiers,
                               enchant=min(50, 4 * unit.pieces(37) + 2 * unit.pieces(38)),
                               second_modifiers=second, element_boost=element_boost,
                               target_modifiers=sum(target.value(e) for e in MAGIC_DEFENCE_MODIFIERS),
                               target_enchant=min(50, 4 * target.pieces(41) + 2 * target.pieces(42)),
                               swing=0.0 if expect else self.swing(unit), power_boost=power_boost,
                               damage_cut=cut, resistance=resistance,
                               critical=critical if expect else (f.MAGIC_CRIT_FACTOR if critical else 1.0), other=other)
        damage = max(0.0, value) if expect else max(0, int(value))
        if expect and action.value(296) is not None:
            damage = min(damage, int(action.value(296)))
        return damage, critical

    # --- what the policies ask ---------------------------------------------------------------------------------
    def hit_chance(self, action, target):
        """Chance in [0, 1] that the action lands (docs/FORMULAS.md 2.1, 3). After the formula and its limits (5 to
        100 for a blow, 25 to 95 for a spell), Fixed accuracy (55) and a direct accuracy value (72) set the chance to
        value * 100, a sleeping target is hit for certain (0x44aef3 - 0x44afbb; 0x44da4a - 0x44daac), and an action
        that hits only adults or only minors (149, 150) cannot hit the others (0x44affd - 0x44b0e8, 0x44dab9).
        For a stab blow this is the chance before Flowing Water Stance (stab_dodge)."""
        unit = action.actor
        roll = action.hit_roll
        if roll is None:
            return 1.0
        if roll == 'magic':
            if isinstance(action.source, Skill) and action.source.accuracy:
                acc = action.source.accuracy[min(action.level, len(action.source.accuracy)) - 1]
            else:
                acc = getattr(action.source, 'accuracy', 0.0) or 0.0
            buffs = sum(self.first(action, unit, e) for e in MAGIC_ACCURACY_BUFFS)
            if isinstance(action.source, Skill) and action.source.id == LULLABY:
                buffs += sum(self.first(action, unit, e) for e in LULLABY_ACCURACY)
            divisor = next((target.value(e) for e in MAGIC_HIT_DIVISORS if target.has(e)), 1.0) or 1.0
            chance = f.magic_hit(acc, unit.stat('int'), target.stat('res'),
                                 loose_spirit=self.first(action, unit, 30),
                                 enchant=min(50, 3 * unit.pieces(39) + unit.pieces(40)),
                                 target_enchant=min(50, 3 * target.pieces(43) + target.pieces(44)),
                                 buffs=buffs, target_evasion=sum(target.value(e) for e in MAGIC_EVASION_BUFFS),
                                 divisor=divisor)
        else:
            if isinstance(action.source, Skill):
                skill_acc = action.value(29, 0.0)
            else:
                skill_acc = getattr(action.source, 'accuracy', 0.0) or 0.0
            chance = f.physical_hit(unit.stat('dex'), target.stat('agi'), skill_acc or 0.0,
                                    buffs=sum(self.first(action, unit, e) for e in ACCURACY_BUFFS),
                                    target_buffs=sum(target.value(e) for e in EVASION_BUFFS),
                                    enchant=min(50, 4 * unit.pieces(31) + 2 * unit.pieces(32)),
                                    target_enchant=min(50, 4 * target.pieces(35) + 2 * target.pieces(36)),
                                    divisor=1.0 + target.value(221))           # the target's Barcarole (0x44ae0b)
        if action.has(55):
            chance = action.value(55) * 100
        elif action.has(72):
            chance = action.value(72) * 100
        if roll == 'physical':
            chance = f.clamp(chance, f.HIT_MIN, f.HIT_MAX)
        if 116 in target.statuses:
            chance = 100.0
        for effect, adult in AGE_ONLY.items():
            if action.has(effect) and target.adult == adult:
                chance = 0.0
        return int(chance) / 100.0

    def stab_dodge(self, action, target):
        """Flowing Water Stance (253, 0x44abe0 - 0x44ac18 and 0x44b10e - 0x44b20f): against a stab blow its value is
        one more evasion term; a roll that lands only without it is a dodge, and the bearer answers with a counter."""
        if not (action.physical and action.attr == STAB and target.has(STAB_EVASION)) or action.furious:
            return 0.0
        if action.has(55) or action.has(72) or 116 in target.statuses:
            return 0.0
        unit = action.actor
        skill_acc = action.value(29, 0.0) if isinstance(action.source, Skill) else \
            (getattr(action.source, 'accuracy', 0.0) or 0.0)
        kw = dict(buffs=sum(self.first(action, unit, e) for e in ACCURACY_BUFFS),
                  enchant=min(50, 4 * unit.pieces(31) + 2 * unit.pieces(32)),
                  target_enchant=min(50, 4 * target.pieces(35) + 2 * target.pieces(36)),
                  divisor=1.0 + target.value(221))
        evasion = sum(target.value(e) for e in EVASION_BUFFS)
        full = f.physical_hit(unit.stat('dex'), target.stat('agi'), skill_acc or 0.0, target_buffs=evasion, **kw)
        less = f.physical_hit(unit.stat('dex'), target.stat('agi'), skill_acc or 0.0,
                              target_buffs=evasion + target.value(STAB_EVASION), **kw)
        return max(0.0, int(full) - int(less)) / 100.0

    def expected_damage(self, action, target):
        """Mean damage of the whole action on one target: hits, accuracy and critical rate taken at their means."""
        if action.has(25) or not (action.physical or action.magic or self.special(action)):
            return 0.0
        if self.visibly_voided(action, target):
            return 0.0
        hits = self.mean_hits(action)
        chance = self.hit_chance(action, target)
        if action.has(139) and 116 in target.statuses and 'instant death' not in target.immune:
            return chance * target.hp
        if self.special(action):
            return chance * min(target.hp, self.special_damage(action, target))
        if action.magic:
            per_hit, _ = self.magic_damage(action, target, expect=True)
        else:
            unit = action.actor
            rate = f.critical_rate(unit.stat('dex'), target.stat('agi'), unit.level, target.level,
                                   skill=sum(self.first(action, unit, e) for e in CRIT_TERMS) + target.value(32),
                                   enchant=f.critical_enchant(unit.pieces(45), unit.pieces(46)),
                                   target_enchant=-f.critical_enchant(target.pieces(47), target.pieces(48)),
                                   floor_268=bool(unit.pieces(268)), fixed=action.value(70))
            per_hit = self.physical_damage(action, target, 0, f.expected_critical_factor(rate), expect=True)
        if 116 in target.statuses and not self.special(action):
            per_hit = per_hit * f.SLEEP_DAMAGE[0] / f.SLEEP_DAMAGE[1]
        if not self.special(action):
            wall = next((u for u in self.allies(target) if u.has(DEMON_WALL)), None)
            if wall is not None:
                per_hit = max(0.0, per_hit + per_hit * wall.value(DEMON_WALL))
        enchant, share = f.AILING_TARGET_BONUS
        if not self.special(action) and action.actor.pieces(enchant) and any(e in target.statuses for e in AILMENTS):
            per_hit += per_hit * share
        if action.has(86) and target.kind == 'member' and target.class_id in f.MAGIC_USER_LINE:
            per_hit += per_hit
        if action.magic:
            cap = action.value(296)
            if cap is not None:
                per_hit = min(per_hit, float(cap))
        return chance * hits * per_hit

    @staticmethod
    def visibly_voided(action, target):
        """What a player sees will come to nothing on this target: a barrier against all but Neutral (192) and Nullify
        Short-Mid (182) are statuses shown on the unit (the checks of voided, 12.12)."""
        return (target.has(192) and action.attr != NEUTRAL) or (target.has(182) and action.reach in (SHORT, MID))

    def mean_hits(self, action):
        for effect, (base, picks, weights, rondo_weights) in MULTI_HIT.items():
            if action.has(effect):
                table = rondo_weights if (action.has(210) or action.actor.has(210)) else weights
                return base + sum(p * w for p, w in zip(picks, table)) / float(sum(table))
        hits = action.value(93, 1) or 1
        if action.kind == 'attack':
            triple = min(1.0, action.actor.value(252)) if action.actor.has(252) else 0.0
            double = min(1.0, action.actor.value(251)) if action.actor.has(251) else 0.0
            hits = 3 * triple + 2 * double + (1 - triple) * (1 - double)
        return hits

    def special_damage(self, action, target):
        """12.3; then Limit Field of the target: damage + int(damage * value), except for effect 142 (0x44fb17)."""
        amount = self._special_damage(action, target)
        if not action.has(142) and target.has(190):
            amount += int(amount * target.value(190))
        return max(0, amount)

    def _special_damage(self, action, target):
        unit = action.actor
        if action.has(8):
            return int(action.value(8))
        if action.has(12):
            return int(unit.hp * action.value(12))
        if action.has(138):
            index = RESIST_INDEX.get(action.attr)
            res = target.resistance(index) if index is not None else 0
            return int(target.max_hp * action.value(138) * f.resistance_factor(res))
        if action.has(140):
            return target.hp // 2 if target.side == PARTY or self.setup.get('halve_enemies', True) else 0
        if action.has(141):
            return target.hp * 3 // 4
        if action.has(142):
            return max(0, target.hp - 1)
        if action.has(434):
            return max(0, unit.hp - 1)
        if action.has(435):
            return int(unit.level * action.value(435))
        return 0

    def swing(self, unit):
        n = int(round(100 * (unit.swing or 0.0)))
        if n <= 0:
            return 0.0
        return (self.rng.randint(0, 2 * n) - n) / 100.0

    def race_factor(self, unit, target):
        """The race factor of a blow beyond effect 88 (0x44bcd5 - 0x44c3b0): a member hitting an enemy adds the shares of
        her race enchantments; an enemy hitting a member is cut by the member's guard against its race."""
        if unit.side == PARTY and target.side == ENEMIES:
            bonus = sum(unit.pieces(e) * share for e, share in f.RACE_ATTACK.get(target.race, ()))
            enemy_id = getattr(target, 'enemy_id', None)
            bonus += sum(unit.pieces(e) for e, ids in f.RACE_SPECIAL if enemy_id in ids)
            return 1.0 + bonus
        return self.race_guard(unit, target)

    @staticmethod
    def race_guard(unit, target):
        if unit.side == ENEMIES and target.side == PARTY and unit.race in f.RACE_GUARD:
            small, large = f.RACE_GUARD[unit.race]
            return 1.0 - f.RACE_GUARD_SHARE[0] * target.pieces(small) - f.RACE_GUARD_SHARE[1] * target.pieces(large)
        return 1.0

    @staticmethod
    def element_factor(unit, target, attr):
        enchant = f.BOTH_SIDES_ELEMENT.get(attr)
        if enchant is None:
            return 1.0
        return 1.0 + f.ELEMENT_ENCHANT_SHARE * (unit.pieces(enchant) + target.pieces(enchant))

    @staticmethod
    def full_hp_bonus(unit):
        enchant, share = f.FULL_HP_BONUS
        return share * unit.pieces(enchant) if unit.hp == unit.max_hp else 0.0

    def zone_factor(self, unit, action):
        """docs/FORMULAS.md 2.5 (0x44fbb0): the factors of the zone of the cell the battle is fought on, for every unit
        of both sides. A blow (flag 1, 0x44b39d) reads slot 3 (physical attack up) and 5 (down); a spell (flag 0,
        0x44dcb0) reads 4 (magic attack up) and 6 (down); 7 to 11 raise fire, water, wind, earth and lightning for both."""
        factor = 1.0
        factors = self.zone.get('factors', {})
        physical = not action.magic
        for slot in self.zone.get('slots', ()):
            if slot == (3 if physical else 4):
                factor *= factors.get('up_a' if physical else 'up_b', 1.0)
            if slot == (5 if physical else 6):
                factor *= factors.get('down_a' if physical else 'down_b', 1.0)
            if slot in (7, 8, 9, 10, 11) and action.attr == slot - 3:
                factor *= factors.get('element', 1.0)
        return factor

    # --- damage taken -------------------------------------------------------------------------------------------
    def take_damage(self, target, amount, action, critical=False):
        unit = action.actor if action is not None else None
        if amount >= target.hp and target.has(254) and self.roll(target.value(254)):
            amount = target.hp - 1
        before = target.hp
        if self.log is not None:
            self.log.append(f'          -> {target.name} takes {amount}{" (critical)" if critical else ""}, '
                            f'{max(0, target.hp - amount)}/{target.max_hp} left')
        self.lose_hp(target, amount, unit)
        if unit is not None and unit.side != target.side:
            self.record.add('damage', unit, min(before, amount))
        if target.alive and amount > 0:
            # 0x47e64d - 0x47e72e: TP Conversion, then the enchantments 72 and 73
            gained = max(1, int(amount * target.value(257))) if target.has(257) else 0
            share = f.TP_CONVERSION_UP * target.pieces(72)
            floor = f.TP_CONVERSION_FLOOR
            if target.pieces(73):
                share += f.TP_CONVERSION_MINI * target.pieces(73)
                floor = f.TP_CONVERSION_FLOOR_73
            if share:
                gained = max(floor, gained + int(amount * min(f.TP_CONVERSION_MAX, share)))
            if gained:
                target.tp = min(target.max_tp, target.tp + gained)
        if target.alive and target.has(312) and not target.ecstasy_done and before >= target.max_hp / 2 > target.hp:
            target.ecstasy_done = True
            target.statuses[41] = Status(41, target.value(312), ECSTASY_TURNS, target)     # 0x47f5fc, 0x47f633
            target.statuses[45] = Status(45, target.value(312), ECSTASY_TURNS, target)
        if target.samsara is None and target.has(291):
            target.samsara = False              # 0x47f739: the bearer is watched from its first damage on
        if target.alive and amount > 0:
            target.statuses.pop(116, None)               # 0x47ea6b - 0x47ea80: damage wakes a sleeping unit
            if target.chant is not None or self.performing(target):
                self.interrupt(target, amount, critical, action is None or not action.magic)
        if target.unique and target.unique[0] == 447 and unit is not None and not unit.has(307) and amount > 0:
            if self.rng.randrange(100) < (getattr(self.data, 'arcane_chance', None) or ARCANE_CHANCE):
                self.lose_hp(unit, int(amount * target.unique[1]), target)

    def interrupt(self, target, amount, critical, physical=True):
        enchant = 0.10 * target.pieces(57) + 0.06 * target.pieces(58) + 0.03 * target.pieces(59)
        chance = f.interruption_chance(amount, target.max_hp, target.value(264), enchant, critical, physical,
                                       getattr(self.data, 'interrupt_product', False))
        if self.rng.random() < chance:
            # 0x47ea83 - 0x47eabb: the flag of the hit ends the chant, the songs, the dances and the dolls of the target
            if target.chant is not None:
                self.record.add('chants_broken', target)
            if self.performing(target):
                self.record.add('performances_broken', target)
            target.chant = None
            self.end_performances(target)

    def performing(self, unit):
        return bool(unit.song or unit.dance) or any(u.owner is unit and u.alive and u.kind == 'doll' for u in self.units)

    def lose_hp(self, unit, amount, source):
        if not unit.alive or amount <= 0:
            return
        unit.hp -= amount
        if unit.hp <= 0:
            unit.hp = 0
            self.fall(unit, source)

    def fall(self, unit, source):
        if unit.has(188) and 188 in unit.statuses:
            value = unit.statuses.pop(188).value
            unit.hp = max(1, int(unit.max_hp * value))
            return
        unit.alive = False
        unit.chant = None
        unit.statuses = {}
        self.record.add('deaths', unit)
        if unit.side == ENEMIES:
            self.record.kills += 1
        for doll in [u for u in self.units if u.owner is unit and u.kind == 'doll']:
            self.remove_doll(doll)
        for ally in self.units:
            for effect, s in list(ally.statuses.items()):
                if s.source is unit and s.kind == 'song':
                    ally.statuses.pop(effect)

    def restore(self, unit, amount):
        if not unit.alive or amount <= 0:
            return 0
        gained = min(unit.max_hp - unit.hp, amount)
        unit.hp += gained
        return gained

    # --- what follows a hit ------------------------------------------------------------------------------------
    def after_hit(self, action, target, dealt):
        unit = action.actor
        hostile = target.side != unit.side
        song = isinstance(action.source, Skill) and action.source.category == 'Magic' and action.tp_cost == 0 and \
            any(action.has(e) for e in SONG_EFFECTS)
        dance = any(action.has(e) for e in DANCE_EFFECTS)
        for effect, kind, value in action.effects():
            # an ailment is applied whatever the kind of its slot: Magic Box's instant death on the user is kind 2
            if effect in (PLAIN_HIT, MAGIC_POWER, 25) or (kind == 2 and effect not in AILMENTS):
                continue
            if effect in AILMENTS:
                if self.aimed(action, target) or effect == 123:
                    if effect == 123:
                        if hostile and unit.level > target.level and 'shadow sew' not in target.immune \
                                and not target.pieces(f.ENCHANT_NULLIFY_ALL) \
                                and self.roll(value):
                            target.statuses[123] = Status(123, 1, max(1, action.turns or 1), unit)
                            self.end_parts(target, AILMENT_ENDS[123])
                    else:
                        self.apply_ailment(unit, target, effect, value, action)
                continue
            if effect == 74 and hostile:
                if self.roll(value):
                    self.dispel(target)
                continue
            if effect == 75 and dealt:
                self.restore(unit, int(dealt * value))
                continue
            if effect == 76 and dealt:
                unit.tp = min(unit.max_tp, unit.tp + int(dealt * value))
                continue
            if effect == 2:
                continue                                # handled in damage: the hit goes to TP
            if effect == 54 and hostile:
                if 'turn delay' not in target.immune and self.rng.randrange(100) < int(value * 100):
                    self.delay(target)
                continue
            if effect in (103, 9, 104, 105, 128, 129, 130, 131, 132, 426):
                self.heal(action, target, effect, value)
                continue
            if effect == 106 or effect == 235:
                # 0x481a92 - 0x481b0d: the first min(int(value), 7) entries of the list, each removed when present
                for e in CURE_ORDER[:min(int(value), len(CURE_ORDER))]:
                    target.statuses.pop(e, None)
                if int(value) == CURE_ALL:
                    for e in [e for e, s in target.statuses.items() if s.source is not None and s.source.side != target.side]:
                        target.statuses.pop(e, None)
                continue
            if effect in (60, 61) and hostile:
                chance = 0.5 * (unit.stat('dex') + 50) / (target.stat('agi') + 50) * (
                    (action.value(60, 0.0) or 0.0) + (action.value(61, 0.0) or 0.0))
                if not target.stolen and self.rng.randrange(100) < int(f.clamp(chance, 0.05, 0.95) * 100):
                    target.stolen = True
                    self.record.add('items_used', ('stolen', unit))
                continue
            if effect == 84 and hostile:
                if getattr(target, 'snack', False) and target.hp < int(target.max_hp * 0.5) and self.roll(value):
                    target.alive = False
                    self.record.kills += 1
                continue
            if effect == 425:                   # 0x48b060: the four end calls
                self.end_parts(target, ('chant', 'song', 'dance', 'doll'))
                continue
            if effect == MAX_HP_DRAIN and hostile and dealt:
                # 0x483ee0: the target's max HP falls by int(damage * value) (its modifier at 0x98)
                target.max_hp_base = max(1, target.max_hp_base - int(dealt * value))
                target.hp = min(target.hp, target.max_hp)
                continue
            if effect == SPECIAL_SLEEP[0]:
                self.apply_ailment(unit, target, 116, SPECIAL_SLEEP[1], action, start=SPECIAL_SLEEP[2])
                continue
            if effect == ENEMIES_FLEE and hostile:
                if self.setup.get('random_battle'):     # 0x48b3c0: only where running away is allowed
                    target.alive = False
                continue
            if effect == 170:
                if hostile:
                    target.provoked_by[unit] = value
                    target.statuses[170] = Status(170, value, action.turns, unit)
                continue
            if effect == 139 and hostile and 116 in target.statuses and 'instant death' not in target.immune:
                self.lose_hp(target, target.hp, unit)
                continue
            if effect == 121 and hostile and 'petrification' not in target.immune and target.resistance(6) < 100 \
                    and not self.nullified(target, 120):
                target.statuses[120] = Status(120, 1, 0, unit)
                self.end_parts(target, AILMENT_ENDS[121])
                continue
            if effect == 320 and hostile and any(e in target.statuses for e in AILMENTS):
                self.apply_ailment(unit, target, 119, value, action)
                continue
            if effect == 168 and action.has(79):
                if not self.roll(action.value(79)):
                    continue
            if effect in (66, 80) and target.side == PARTY:
                target.pep = max(70.0, min(130.0, target.pep + value)) if effect == 80 or target.pep < 100 else target.pep
                continue
            if effect in ACTION_CAPS:
                continue                # the caps of a heal or a hit are read from the action (Battle.heal, damage)
            if kind in (4, 5) or effect in STATUS_EFFECTS:
                if song or dance:
                    self.perform_song(unit, action, target, effect, value, dance)
                else:
                    target.statuses[effect] = Status(effect, value, action.turns, unit,
                                                     getattr(action.source, 'name', None), kind,
                                                     data=action.value(296) if effect in (199, 200, 339) else None)
        if hostile and dealt:
            if target.has(262) and action.physical and action.reach == SHORT and not unit.has(304):
                points = int(target.value(262))
                for k, stat_effect in enumerate((45, 44, 43, 42, 41, 46)[:points]):
                    old = unit.statuses.get(stat_effect)
                    unit.statuses[stat_effect] = Status(stat_effect, (old.value if old else 0.0) - 0.1,
                                                        DARK_AURA_TURNS, target)
            if unit.has(293) and self.roll(unit.value(293)) and 'slow' not in target.immune:
                # 0x4244c7 - 0x424579: Slow with a recovery chance that starts at 5, speed -0.75 for 5 turns
                target.statuses[122] = Status(122, 1.0, 0, unit, data=SLOW_TARGET[0])
                target.statuses[168] = Status(168, -0.75, SLOW_TARGET[1], unit)
            if target.has(249) and action.physical and action.reach in (SHORT, MID) and not unit.has(307) \
                    and self.roll(target.value(249)) and target.alive:
                self.counter(target, unit)

    @staticmethod
    def performance_slots(unit, dance=False):
        """Songs (or dances) kept up at once: two with Self Session (287) or On Stage (284), else one."""
        return 2 if unit.has(284 if dance else 287) else 1

    def perform_song(self, singer, action, target, effect, value, dance):
        bonus_effect, ench_up, ench_mini = (280, 302, 303) if dance else (279, 300, 301)
        bonus = singer.value(bonus_effect, 0.0) + min(0.05, 0.02 * singer.pieces(ench_up) + 0.01 * singer.pieces(ench_mini))
        keep = self.performance_slots(singer, dance)
        own = singer.dance if dance else singer.song
        name = action.source.name
        if name not in own:
            own.append(name)
            while len(own) > keep:
                old = own.pop(0)
                for u in self.units:
                    for e, s in list(u.statuses.items()):
                        if s.source is singer and s.skill == old:
                            u.statuses.pop(e)
        if effect in (215, 216):
            target.statuses[effect] = Status(effect, value, 0, singer, name, 'song', data=bonus)
        else:
            target.statuses[effect] = Status(effect, value + bonus, 0, singer, name, 'song')

    def apply_ailment(self, unit, target, effect, value, action, start=None):
        """docs/FORMULAS.md 5b: blocked by immunity or the same ailment; then the chance against resistance."""
        name = AILMENTS[effect]
        if name in target.immune or effect in target.statuses:
            return False
        if target.has(192) or self.nullified(target, effect):
            return False
        index = AILMENT_RESIST.get(effect)
        resistance = target.resistance(index) if index is not None else 0
        # the roll is against the chance cut to an integer (0x48201d). The 15 points of enchantment 269 and the block
        # of 138 (0x481ff3 - 0x48200d) are not of a battle: they are "Less likely to trigger traps" and "Nullify gas
        # traps", read only when the source of the command is of kind 4, a trap
        chance = f.ailment_threshold(value, resistance)
        if chance <= 0 or self.rng.randrange(100) >= chance:
            return False
        for effect_count in (101, 102, 181):
            s = target.statuses.get(effect_count)
            if s:
                s.value -= 1
                if s.value <= 0:
                    target.statuses.pop(effect_count)
                return False
        if effect == 119:
            self.lose_hp(target, target.hp, unit)
            return True
        if effect == 118:
            self.stun(target)
            return True
        if start is None:
            start = int(action.turns) if action is not None and action.turns else 0
        target.statuses[effect] = Status(effect, value, 0, unit, data=start)
        self.end_parts(target, AILMENT_ENDS.get(effect, ()))
        return True

    @staticmethod
    def nullified(target, ailment):
        """A piece of the enchantment that nullifies the ailment, or of Nullify all status ailments (137), stops it
        before its roll (0x481f2d poison ... 0x48367a slow; Shadow Sew looks at 137 only, 0x4838ae)."""
        own = [e for e, a in f.ENCHANT_NULLIFY_AILMENT.items() if a == ailment]
        return bool(target.pieces(f.ENCHANT_NULLIFY_ALL) or any(target.pieces(e) for e in own))

    def stun(self, target):
        """Stun (0x4fa185 - 0x4fa2f2): the chant, song, dance and doll of the target end, its gauge is set to 0 (its
        next turn comes after a whole wait of 1), and the status is removed at once: no turn is skipped."""
        self.end_parts(target, AILMENT_ENDS[118])
        lost = self.time + 1.0 - target.next_time
        target.next_time = self.time + 1.0
        if target.side == ENEMIES and lost > 0:
            self.record.add('delayed', target, lost)

    def end_performances(self, unit):
        """Effect 425 and an interrupting hit: the songs and dances the unit keeps up and its dolls end."""
        self.end_parts(unit, ('song', 'dance', 'doll'))

    def end_parts(self, unit, parts):
        """The four end calls of the program (0x43bc50 chant, 0x43c110 songs, 0x43c600 dances, 0x43c9b0 dolls)."""
        if 'chant' in parts:
            unit.chant = None
        for part in ('song', 'dance'):
            if part in parts:
                names = getattr(unit, part)
                for other in self.units:
                    for e, s in list(other.statuses.items()):
                        if s.source is unit and s.kind == 'song' and s.skill in names:
                            other.statuses.pop(e)
                setattr(unit, part, [])
        if 'doll' in parts:
            # the arrows of Star Dust Arrow cannot be interrupted, they end with their owner (GameFAQs guide; A28);
            # Genjimaru is not a doll of a doll skill (A18)
            for doll in [u for u in self.units if u.owner is unit and u.kind == 'doll' and u.alive
                         and not getattr(u, 'arrow', False) and not getattr(u, 'genjimaru', False)]:
                self.remove_doll(doll)

    def delay(self, target):
        """5c: the target swaps its place in the order with the unit right after it."""
        if not target.alive:
            return
        order = sorted((u for u in self.units if u.alive), key=lambda u: (u.next_time, u.position))
        k = order.index(target)
        if k + 1 < len(order):
            nxt = order[k + 1]
            target.next_time, nxt.next_time = nxt.next_time, target.next_time
            self.record.add('denied', target, 0.0)

    @staticmethod
    def dispellable(target):
        """The statuses a dispel (effect 74) removes: the list the unit gives at slot 0x94 (0x4fb1f0), every status
        whose class answers yes at slot 0x64; for most classes that slot asks slot 0x54, which for the stat classes is
        "value >= 0" (0x479df0). See DISPEL_ALWAYS and DISPEL_IF_RAISED."""
        return [e for e, s in target.statuses.items()
                if e in DISPEL_ALWAYS or (e in DISPEL_IF_RAISED and (s.value or 0) >= 0)]

    def dispel(self, target):
        for e in self.dispellable(target):
            target.statuses.pop(e)

    def heal(self, action, target, effect, value):
        unit = action.actor
        cap = action.value(295)
        if effect == 103:
            coefficient = value
            if unit.kind == 'doll' and unit.owner is not None:
                coefficient += f.doll_heal_bonus(unit.owner.passives.get(286, 0.0), unit.owner.pieces(304), unit.owner.pieces(305))
            fixed = action.value(9)
            amount = int(fixed) if fixed else f.heal(unit.stat('res'), coefficient, unit.passives.get(245, 0.0),
                                                      cap, unit.passives.get(317, 0.0), self.rng.choice(f.HEAL_RANDOM))
            self.record.add('healing', unit, self.restore(target, amount))
        elif effect == 9 and not action.has(103):
            # beside 103 it is read there as the fixed amount; alone it is a fixed heal (Magic Box: HP 200 to the
            # whole party, atwiki dt2-2 page 132)
            self.record.add('healing', unit, self.restore(target, int(value)))
        elif effect == 104:
            self.record.add('healing', unit, self.restore(target, target.max_hp))
        elif effect == 105:
            if not target.alive:
                target.alive = True
                target.hp = max(1, int(target.max_hp * value))
                target.next_time = self.time + self.wait(target)
        elif effect in (128, 131):
            amount = int(target.max_hp * value)
            if effect == 131 and cap is not None:
                amount = min(amount, int(cap))
            self.record.add('healing', unit, self.restore(target, amount))
        elif effect == 132:
            self.record.add('healing', unit, self.restore(target, f.fraction_recovery(target.max_hp, value, cap)))
        elif effect == 129:
            target.tp = min(target.max_tp, target.tp + int(target.max_tp * value))
        elif effect == 426:
            target.tp = min(target.max_tp, target.tp + int(value))
        elif effect == 130:
            given = int(unit.tp * value)
            unit.tp = 0
            target.tp = min(target.max_tp, target.tp + given)

    def counter(self, unit, attacker):
        if unit.alive and attacker.alive:
            self.resolve(Action(unit, 'attack'), attacker, 0, {})

    # --- dolls, random moves, items ------------------------------------------------------------------------------
    def make_doll(self, action):
        """0x484330: as many units as effect 146 says (one for every doll, two or three arrows of Star Dust Arrow),
        each with the life of effect 147 plus effect 297 of the owner. The arrows are not dolls of the Doll Master:
        they do not count against Double Puppet, and a new cast replaces the arrows of the one before (A28)."""
        owner = action.actor
        doll = next((d for d in self.data.dolls if d['skill'] == action.source.id), None)
        if doll is None:
            return
        arrow = doll['effect'] is None
        if arrow:
            for u in [u for u in self.units if u.owner is owner and getattr(u, 'arrow', False) and u.alive]:
                self.remove_doll(u)
        else:
            keep = 2 if owner.has(313) else 1
            own = [u for u in self.units if u.owner is owner and u.kind == 'doll' and u.alive
                   and not getattr(u, 'arrow', False)]
            while len(own) >= keep:
                self.remove_doll(own.pop(0))
        for _ in range(max(1, int(action.value(146, 1) or 1))):
            unit = build_doll(owner, doll, action.level, self.data)
            unit.arrow = arrow
            unit.life += int(owner.passives.get(297, 0.0))
            unit.position = len(self.units)
            unit.next_time = self.time + self.wait(unit)
            self.units.append(unit)

    def remove_doll(self, doll):
        doll.alive = False
        doll.chant = None

    def make_genjimaru(self, action):
        """Effect 427 (0x48b1f0): unless one is already in the battle, a unit built like a doll (constructor 0x4fd840,
        9,999 HP) that performs hidden skill 107 on its turns for GENJIMARU_LIFE turns (the constructor's life
        argument, where a doll skill passes its effect 147)."""
        if any(u.alive and getattr(u, 'genjimaru', False) for u in self.units):
            return
        record = {'skill': GENJIMARU_ACTION, 'name': 'Genjimaru', 'effect': GENJIMARU, 'range': None,
                  'turns': [GENJIMARU_LIFE] * 10, 'actions': [{'skill': GENJIMARU_ACTION}]}
        unit = build_doll(action.actor, record, action.level, self.data)
        unit.genjimaru = True
        unit.position = len(self.units)
        unit.next_time = self.time + self.wait(unit)
        self.units.append(unit)

    def doll_action(self, doll):
        actions = doll.doll['actions']
        if not actions:
            return Action(doll, 'attack')
        chosen = self.rng.choice(actions)
        skill = self.data.skills.get(('Magic' if doll.doll['skill'] == 100 else 'Technique', chosen['skill']))
        if skill is None:
            return None
        action = Action(doll, 'skill', skill, doll.doll_level)
        # A doll's action aimed at the party serves the members, not the doll (the targets of its hidden skill read
        # for itself would be the doll; the code of that pick is not read): Catalina heals the member lowest in HP,
        # Perdurabo cures the ailments of doll_cure_targets members (GameFAQs faqs/80834, Class Skill info - Spieler;
        # atwiki dt2-2 page 146).
        members = [u for u in self.allies(doll) if u.kind == 'member']
        if members and action.target_code == ALLY:
            action.target = min(members, key=lambda u: u.hp_ratio)
        elif members and action.target_code == NO_TARGET and action.has(235):
            ailing = sorted(members, key=lambda u: -sum(e in u.statuses for e in AILMENTS))
            action.fixed_targets = ailing[:int(self.setup.get('doll_cure_targets', 2))]
        return action

    def random_move(self, action, effect):
        table = next((t for t in self.data.random_moves if t['effect'] == effect), None)
        if table is None:
            return None
        joker = action.actor.has(315)
        weights = [r['joker_weight' if joker else 'weight'] for r in table['results']]
        result = table['results'][self.weighted(list(range(len(weights))), weights)]
        skill = self.data.skill_by_id.get(result['skill'])
        if skill is None:
            return None
        if any(e == 427 for e, _ in result['effects']) and any(
                u.alive and getattr(u, 'genjimaru', False) for u in self.units):
            empty = next((r for r in table['results'] if not r['effects']), None)
            skill = self.data.skill_by_id.get(empty['skill']) if empty else None
            if skill is None:
                return None
        return Action(action.actor, 'skill', skill, action.level)

    def use_item(self, action):
        unit, item = action.actor, self.data.items.get(action.item)
        if item is None or unit.items.get(action.item, 0) <= 0:
            return
        unit.items[action.item] -= 1
        if unit.has(274) and self.roll(unit.value(274)):
            unit.items[action.item] += 1
        self.record.add('items_used', (unit, item['name']))
        target = action.target or unit
        mastery = unit.passives.get(275, 0.0)
        for kind, value in item['effects']:
            if kind == 0:
                self.restore(target, int(value) + int(value * mastery))
            elif kind == 1:
                target.tp = min(target.max_tp, target.tp + int(value))
            elif kind == 3:
                for ally in self.allies(unit):
                    self.restore(ally, int(value) + int(value * mastery))
            elif kind == 8 and not target.alive:
                # 0x5101a4 - 0x5101ca: int(max HP * the value of the item / 100), at least 1
                target.alive, target.hp = True, max(1, int(target.max_hp * value / 100.0))
                target.next_time = self.time + self.wait(target)
            elif kind == ITEM_CURE_ONE:
                # 0x50fb30: one of the ailments the target carries, picked at random (0x490790)
                present = [e for e in AILMENTS if e in target.statuses]
                if present:
                    target.statuses.pop(self.rng.choice(present))
            elif kind == ITEM_CURE_ALL:
                for e in [e for e in AILMENTS if e in target.statuses]:     # 0x50fe20: every ailment
                    target.statuses.pop(e)
            elif kind in self.data.item_skills:
                skill = self.data.skill_by_id.get(self.data.item_skills[kind])
                if skill:
                    self.perform(Action(unit, 'skill', skill, skill.levels, action.target))

    # --- helpers -----------------------------------------------------------------------------------------------
    @staticmethod
    def first(action, unit, effect):
        """The value the attack functions read for an effect of the user's side: the first found among the effects of
        the action, then among the statuses and passives of the user (0x47e340 stops at the first match)."""
        if action.has(effect):
            return action.value(effect) or 0.0
        return unit.value(effect)

    def roll(self, value):
        """A roll below 100 under int(value * 100), the form of most rolls of the program."""
        return self.rng.randrange(100) < int((value or 0.0) * 100)


SONG_EFFECTS = (211, 212, 213, 214, 215, 216, 217, 218, 220, 222, 223)
DANCE_EFFECTS = (195, 196, 197, 198, 201, 205, 219, 221)
STATUS_EFFECTS = set(STAT_STATUSES) | {161, 162, 163, 164, 165, 166, 167, 168, 171, 183, 187, 188, 191, 101, 102, 180,
                                       246, 247, 285, 301, 190, 264, 27, 173}
# Multi-hit effects (docs/FORMULAS.md 12.2; sheet EffectRules): effect -> (base, picks, weights, weights under Rondo)
MULTI_HIT = {89: (2, [0, 1, 2, 3], [25, 25, 25, 25], [15, 20, 35, 30]),
             90: (3, [0], [1], [1]),
             91: (8, [0], [1], [1]),
             92: (2, [0, 1, 2], [15, 50, 35], [0, 50, 50]),
             94: (0, [0, 1, 2, 3, 4], [10, 15, 30, 25, 20], [0, 15, 25, 30, 30]),
             95: (1, [0, 1, 2, 3, 4], [10, 15, 30, 25, 20], [0, 15, 30, 25, 30]),
             96: (3, [0, 1, 2], [20, 50, 30], [0, 50, 50]),
             97: (2, [0], [1], [1]),
             98: (7, [0], [1], [1]),
             99: (1, [0, 1, 2], [20, 50, 30], [0, 50, 50]),
             100: (4, [0, 1, 2, 3], [20, 20, 30, 30], [0, 20, 30, 50])}


def target_share_row(size, front):
    """The row of TARGET_SHARE for a party of this size with this many members in front (docs/FORMULAS.md 9.1:
    read from the figures of the table, one row per size and front count)."""
    rows = {(1, 1): 0, (1, 0): 0, (2, 2): 1, (2, 1): 2, (3, 3): 3, (3, 2): 4, (3, 1): 5, (4, 3): 6, (4, 2): 7, (4, 1): 8,
            (5, 3): 9, (5, 2): 10}
    if size == 0:
        return (100,)
    front = max(1, min(front, 3, size))
    key = (size, front) if (size, front) in rows else (size, max(k[1] for k in rows if k[0] == size))
    return f.TARGET_SHARE[rows[min(key, max(rows))]] if size <= 5 else f.TARGET_SHARE[9]

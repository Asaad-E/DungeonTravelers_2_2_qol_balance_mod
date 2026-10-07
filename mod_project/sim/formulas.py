"""
The battle formulas of the game as functions, exactly as docs/FORMULAS.md reads them from the executable.

Every constant here is one the code uses; the comment gives the address. Nothing is fitted or estimated.
Parts of the code that are not read yet are not guessed: they are arguments with a neutral default
(a factor of 1, a bonus of 0) so that a caller must supply them once they are known.
"""

# --- constants of the code (address where each is used) -------------------------------------------
HIT_SCALE = 0.885              # 0x44aac1
HIT_MIN, HIT_MAX = 5.0, 100.0  # 0x44ae84, 0x44ae8c
MAGIC_HIT_PER_POINT = 0.002    # 0x44d63f   (own INT - target RES)
MAGIC_HIT_MIN, MAGIC_HIT_MAX = 25.0, 95.0   # 0x44da2b, 0x44da37
ATTACK_BASE = 2.0              # 0x44b36e   ATK * (2 + swing); 0x44dc97 for INT
DEFENCE_FACTOR = 1.35          # 0x44b9c0   DEF * 1.35
MAGIC_DEFENCE_FACTOR = 1.5     # message 0x652fe8: RES * 1.5
RESIST_PER_POINT = 0.5         # message 0x652b64: (100 - resistance * 0.5) * 0.01
DEFENDING = 0.5                # 0x44c576
DAMAGE_CUT_FLOOR = 0.75        # 0x44bc5f
INTERRUPT_HP_FACTOR = 1.5      # 0x44d03a
INTERRUPT_MAX = 0.95           # 0x44d056
INTERRUPT_CRITICAL = 33        # 0x44d238   second roll of a critical hit, in a hundred
SPEED_STAT_BASE, SPEED_STAT_DIV = 100.0, 200.0    # 0x449b4c, 0x449b58
WEIGHT_DIV = 12.0              # 0x449bab
SPEED_HALF = 0.5               # 0x449e72
SLOW = 0.5                     # 0x449e7e   status 122
SPEED_BONUS_MIN, SPEED_BONUS_MAX = -0.5, 0.5      # 0x44a1b3, 0x44a1bf
DEFEND_SPEED = 1.15            # 0x44a326
ESCAPE_SPEED = 1.20            # 0x44a335
VALUE_CAP = 0.92               # 0x44a341
SPEED_RANDOM = (0.0, 0.01, 0.02, 0.03, 0.04, 0.05)   # 0x449bb1 - 0x449bd4: ((x mod 12) / 2) / 100
CRIT_DEX = 0.2                 # message 0x653230
CRIT_LEVEL = 0.5               # message 0x6531b8
CRIT_UP, CRIT_MINI_UP = 4.0, 2.0                  # 0x44f357, 0x44f3eb   enchantments 45, 46 of the attacker
CRIT_ENCHANT_MAX, CRIT_ENCHANT_MIN = 50.0, -50.0  # 0x44f41a, 0x44f459
CRIT_PER_EARLIER_HIT = 5.0     # 0x44f49b   effect 125
CRIT_MIN, CRIT_MIN_268, CRIT_MAX = 5.0, 20.0, 50.0   # 0x44f4cd, 0x44f4c3, 0x44f4db
CRIT_FACTOR = 1.25             # 0x44f5a6
MAGIC_CRIT_CHANCE, MAGIC_CRIT_FACTOR = 20, 1.25   # 0x44eded, 0x44edf2   with effect 301 (Critical Magic) active
MIN_DAMAGE = 3                 # 0x44cb49   1 or 2 at random on a critical hit (0x44cb3c)
WARNING_SHOT = 0.3             # 0x44caed   final damage * 3 / 10
SLEEP_DAMAGE = (3, 2)          # 0x44cd3b (blow), 0x44eff9 (spell): a sleeping target takes int(damage * 3 / 2)
# A plain attack of a unit that wears a piece of these enchantments carries the effect when it has none of its own
# (0x421258 - 0x4216d2; 0x42155a, 0x421604): enchantment -> (effect, value). The first piece found decides.
PLAIN_ATTACK_ENCHANTS = {161: (75, 0.5), 162: (75, 0.15), 163: (76, 0.2), 164: (76, 0.05),
                         153: (113, 0.18), 154: (116, 0.15), 155: (117, 0.18), 156: (114, 0.18), 157: (115, 0.15),
                         158: (118, 0.12), 159: (120, 0.1), 165: (122, 0.12), 197: (119, 0.75), 160: (119, 0.07)}
TP_CONVERSION_UP, TP_CONVERSION_MINI = 0.05, 0.1   # 0x47e6b1, 0x47e6e4: enchantments 72 and 73 on damage taken
TP_CONVERSION_MAX = 0.5                            # 0x47e70e
TP_CONVERSION_FLOOR, TP_CONVERSION_FLOOR_73 = 1, 5  # 0x47e700, 0x47e6f9

# --- what the enchantments of a character add (0x4f8270 - 0x4f8fcf) ---------------------------------------------
# Each piece (one only for an enchantment that does not stack) adds to a sum per figure. HP, TP and the six stats are
# shares of the figure before equipment (growth + bonus + resets): (figure, divisor, floor), int(base / divisor) at
# least the floor; a negative divisor takes the share away. The HP sum and the TP sum stay within half the base
# (0x4f842c - 0x4f8467); each resistance sum within -100 and 100 (0x4f8490 - 0x4f84ae).
ENCHANT_SHARE = {0: ('hp', 10, 4), 1: ('hp', 20, 2), 2: ('hp', -10, 0), 3: ('tp', 10, 4), 4: ('tp', 20, 2),
                 5: ('tp', -10, 0), 6: ('atk', 10, 4), 7: ('atk', 20, 2), 8: ('atk', -10, 0), 9: ('def', 10, 4),
                 10: ('def', 20, 2), 11: ('def', -10, 0), 12: ('int', 10, 4), 13: ('int', 20, 2), 14: ('int', -10, 0),
                 15: ('res', 10, 4), 16: ('res', 20, 2), 17: ('res', -10, 0), 18: ('dex', 10, 4), 19: ('dex', 20, 2),
                 20: ('dex', -10, 0), 21: ('agi', 10, 4), 22: ('agi', 20, 2), 23: ('agi', -10, 0)}
ENCHANT_ALL_STATS = {24: 1, 25: 3, 26: 6, 27: 9, 28: 12}                     # 0x4f88bc - 0x4f8957
# resistances in the order of the eight (slash, stab, bash, fire, water, wind, earth, lightning)
_PHYS, _ELEM = (0, 1, 2), (3, 4, 5, 6, 7)
ENCHANT_RESIST = {88: {3: 20}, 89: {3: 10}, 90: {3: -20}, 91: {4: 20}, 92: {4: 10}, 93: {4: -20},
                  94: {5: 20}, 95: {5: 10}, 96: {5: -20}, 97: {6: 20}, 98: {6: 10}, 99: {6: -20},
                  100: {7: 20}, 101: {7: 10}, 102: {7: -20},
                  103: {i: 50 for i in _ELEM}, 104: {i: 15 for i in _ELEM}, 105: {i: 7 for i in _ELEM},
                  106: {i: -15 for i in _ELEM},
                  107: {0: 20}, 108: {0: 10}, 109: {0: -20}, 110: {1: 20}, 111: {1: 10}, 112: {1: -20},
                  113: {2: 20}, 114: {2: 10}, 115: {2: -20},
                  116: {i: 25 for i in _PHYS}, 117: {i: 10 for i in _PHYS}, 118: {i: 5 for i in _PHYS},
                  119: {i: -10 for i in _PHYS},
                  310: {3: 100}, 311: {3: 50}, 312: {3: -50}, 315: {4: 100}, 316: {4: 50}, 317: {4: -50},
                  320: {5: 100}, 321: {5: 50}, 322: {5: -50}, 325: {6: 100}, 326: {6: 50}, 327: {6: -50},
                  330: {7: 100}, 331: {7: 50}, 332: {7: -50},
                  335: {i: 75 for i in _ELEM}, 336: {i: -30 for i in _ELEM},
                  340: {0: 100}, 341: {0: 50}, 342: {0: -50}, 345: {1: 100}, 346: {1: 50}, 347: {1: -50},
                  350: {2: 100}, 351: {2: 50}, 352: {2: -50},
                  355: {i: 50 for i in _PHYS}, 356: {i: -20 for i in _PHYS}}
ENCHANT_RESIST_CAP = 100
# the enchantments of one line of the party (the party object at 0x71fc24, slot 0x164 for the front line, 0x16c for
# the back line): (front line, {stat: share}); a share of 0.08 is int(stat * 0.08) (0x4f8bde), 25 and 50 are
# int(stat / 25) and int(stat / 50) (0x4f8c31 - 0x4f8d7e)
ENCHANT_LINE = {222: (True, {'atk': 0.08}), 223: (True, {'atk': 25, 'def': 25}), 224: (False, {'int': 0.08}),
                225: (False, {'int': 25, 'res': 25}), 281: (False, {'dex': 50, 'agi': 50})}
# ailments a piece of these enchantments stops (the roll of each ailment: 0x481f2d poison ... 0x48329a; 137 all)
ENCHANT_NULLIFY_AILMENT = {129: 118, 130: 114, 131: 113, 132: 116, 133: 117, 134: 119, 135: 120, 136: 115, 139: 122}
ENCHANT_NULLIFY_ALL = 137


def clamp(value, low, high):
    return max(low, min(high, value))


# --- order of turns --------------------------------------------------------------------------------
def turn_value(stat, weight, level, action_factor=1.0, bonus=0.0, slowed=False, defending=False, escaping=False,
               random=0.025):
    """Value written to the gauge of a unit after it acts. The wait until its next turn is 1 - value.

    stat: AGI (INT or RES while chanting). weight: delay multiplier of the weapon rank.
    action_factor: product of the two factors of the action (1 for a plain action).
    bonus: sum of speed buffs and enchantments, already limited to its range by the caller if it is the
    enchantment part; random: the mean of the six values the code can draw, unless a draw is passed.
    """
    base = (stat + SPEED_STAT_BASE) / SPEED_STAT_DIV
    speed = (base * (1 + random) - (weight / WEIGHT_DIV) * (1 + level / 100.0)) * action_factor * SPEED_HALF
    if slowed:
        speed *= SLOW
    value = speed * (1 + bonus)
    if defending:
        value *= DEFEND_SPEED
    if escaping:
        value *= ESCAPE_SPEED
    return min(VALUE_CAP, value)


def wait(*args, **kwargs):
    """Time until the next turn of a unit: 1 - turn_value."""
    return 1.0 - turn_value(*args, **kwargs)


def speed_enchant_bonus(up=0, mini_up=0, down=0, per_up=0.10, per_mini=0.05, per_down=0.10):
    """Sum of speed enchantments (51, 52, 53), limited as the code limits it. For chant speed (54, 55, 56)
    pass per_up=0.20, per_mini=0.10, per_down=0.20."""
    return clamp(up * per_up + mini_up * per_mini - down * per_down, SPEED_BONUS_MIN, SPEED_BONUS_MAX)


# --- physical attack ------------------------------------------------------------------------------
def physical_hit(dex, target_agi, skill_accuracy=0.0, buffs=0.0, target_buffs=0.0, enchant=0.0, target_enchant=0.0,
                 divisor=1.0):
    """Chance to hit, in percent."""
    a = HIT_SCALE * (100 + dex) / (100 + target_agi) + skill_accuracy
    b = (buffs - target_buffs + a) * 100
    return clamp((b + enchant - target_enchant) / divisor, HIT_MIN, HIT_MAX)


def attack_value(atk, modifiers=0.0, enchant=0.0, swing=0.0):
    """Attack B. modifiers: the sum of the power of the skill and of every attack buff (they add up)."""
    return atk * (ATTACK_BASE + swing) * (1 + modifiers) * (1 + enchant * 0.01)


def defence_value(defence, modifiers=0.0, enchant=0.0):
    return defence * DEFENCE_FACTOR * (1 + modifiers) * (1 + enchant * 0.01)


def resistance_factor(resistance):
    return (100 - resistance * RESIST_PER_POINT) * 0.01


def physical_damage(atk, target_def, modifiers=0.0, target_modifiers=0.0, enchant=0.0, target_enchant=0.0, swing=0.0,
                    times=1.0, ignore_defence=False, range_factor=1.0, damage_cut=1.0, race=1.0, resistance=0.0,
                    zone=1.0, defending=False, critical=1.0, other=0.0):
    """Damage of one physical hit before the final changes (minimum, fixed damage and the like).
    race and zone are factors the caller supplies; critical is CRIT_FACTOR or 1. The floor of a hit that
    comes out at 0 or less (MIN_DAMAGE) is applied by the caller, since it depends on the roll."""
    defence = 0.0 if ignore_defence else defence_value(target_def, target_modifiers, target_enchant)
    a = attack_value(atk, modifiers, enchant, swing) * times - defence
    b = a * range_factor * max(DAMAGE_CUT_FLOOR, damage_cut)
    c = b * race * resistance_factor(resistance) * zone * (DEFENDING if defending else 1.0) * critical
    return max(0.0, c * (1 + other))


# --- magic attack ---------------------------------------------------------------------------------
def magic_hit(spell_accuracy, intel, target_res, loose_spirit=0.0, enchant=0.0, target_enchant=0.0, buffs=0.0,
              target_evasion=0.0, divisor=1.0):
    """Chance of a spell to hit, in percent."""
    a = spell_accuracy + (intel - target_res) * MAGIC_HIT_PER_POINT + loose_spirit
    b = a * 100 + enchant - target_enchant
    return clamp(b * (1 + buffs) / divisor * (1 - target_evasion), MAGIC_HIT_MIN, MAGIC_HIT_MAX)


def magic_damage(intel, power, target_res, mastery=0.0, modifiers=0.0, enchant=0.0, second_modifiers=0.0,
                 element_boost=0.0, target_modifiers=0.0, target_enchant=0.0, swing=0.0, power_boost=0.0,
                 damage_cut=0.0, resistance=0.0, critical=1.0, other=0.0):
    """Damage of a spell before the final changes (0x44dcc0 - 0x44e6c6):
        attack B = (INT * (2 + swing) + power * (1 + mastery) * (1 + modifiers)) * (1 + enchant * 0.01)
        attack C = attack B * (1 + second_modifiers) * (1 + element_boost)
    modifiers (Waltz 195, effect 335, the Power of a joint skill) multiply the power of the spell only;
    second_modifiers is Spiritual Fantasia (212)."""
    a = intel * (ATTACK_BASE + swing)
    b = (a + power * (1 + mastery) * (1 + modifiers)) * (1 + enchant * 0.01)
    c = b * (1 + second_modifiers) * (1 + element_boost)
    defence = target_res * MAGIC_DEFENCE_FACTOR * (1 + target_modifiers) * (1 + target_enchant * 0.01)
    damage = (c - defence) * (1 + power_boost) * (1 + damage_cut) * resistance_factor(resistance)
    return max(0.0, damage * (1 + other) * critical)


# --- chant interruption and critical hits -----------------------------------------------------------
def interruption_chance(damage, max_hp, modifier=0.0, enchant=0.0, critical=False, physical=True):
    """Chance that a hit of this damage breaks the chant of a unit with this max HP.
    modifier: effect 264 (Concentrate); enchant: the sum the code subtracts. The rate is 0 to 0.95 and is rolled
    as an integer percent; a critical hit rolls again at INTERRUPT_CRITICAL in a hundred, whatever the damage.
    Only the physical damage function rolls the rate (0x44d1f3); the magic one has only the critical roll (0x44f12c)."""
    rate = 0.0
    if physical:
        a = clamp(damage / (max_hp * INTERRUPT_HP_FACTOR * (1 + modifier)), 0.0, INTERRUPT_MAX)
        rate = int(clamp(a - enchant, 0.0, INTERRUPT_MAX) * 100) / 100.0
    if critical:
        rate = 1 - (1 - rate) * (1 - INTERRUPT_CRITICAL / 100.0)
    return rate


def critical_enchant(up=0, mini_up=0):
    """Own side: pieces with enchantment 45 and 46. Target's side: pass its pieces of 47 and 48 and negate."""
    return min(CRIT_ENCHANT_MAX, CRIT_UP * up + CRIT_MINI_UP * mini_up)


def critical_rate(dex, target_agi, level, target_level, skill=0.0, enchant=0.0, target_enchant=0.0, earlier_hits=0,
                  floor_268=False, fixed=None):
    """Critical rate in percent (0x44f190). enchant: critical_enchant() of the attacker; target_enchant: minus
    that of the target's pieces of 47 and 48. earlier_hits: only with effect 125. fixed: the value of effect 70,
    which replaces the rate after its limits."""
    if fixed is not None:
        return fixed * 100.0
    a = (dex * CRIT_DEX) / (dex + target_agi) * 100.0
    b = max(0.0, (level - target_level) * CRIT_LEVEL)
    rate = (a + b + skill) * (1 + min(CRIT_ENCHANT_MAX, enchant) * 0.02) * (1 + max(CRIT_ENCHANT_MIN, target_enchant) * 0.02)
    rate += CRIT_PER_EARLIER_HIT * earlier_hits
    return clamp(rate, CRIT_MIN_268 if floor_268 else CRIT_MIN, CRIT_MAX)


def expected_critical_factor(rate):
    """Mean factor on damage of a hit with this critical rate: the roll is an integer below 100 against the rate
    cut to an integer."""
    return 1.0 + (CRIT_FACTOR - 1.0) * int(rate) / 100.0


# --- range (0x44a7d0, _GetAttackRangeRevision) -----------------------------------------------------
SHORT, MID, LONG, NO_RANGE = 0, 1, 2, 3


def distance(attacker_in_back_row, target_in_back_row):
    """0 when both are in the front row, 1 when one is in the back row, 2 when both are (0x44a7a0)."""
    return int(bool(attacker_in_back_row)) + int(bool(target_in_back_row))


def range_factor(attack_range, dist):
    if attack_range == SHORT:
        return {0: 1.0, 1: 0.75, 2: 0.5}[dist]
    if attack_range == MID:
        return 0.75 if dist == 2 else 1.0
    return 1.0


# --- ailments (the roll of each ailment command, e.g. 0x481ea0 for poison) ---------------------------
def ailment_chance(base, resistance, flat_penalty=0.0):
    """Chance in percent that an ailment lands. base: the value of the effect (0.30 is 30%).
    resistance: the target's resistance to the element the ailment belongs to. Every full 10 points remove a
    tenth of the chance (integer division by 10 at 0x481fc2), so 100 blocks it and a negative resistance adds.
    Immunity enchantments and the immunity flag of an enemy are decided before this and are not modelled here."""
    chance = base * 100.0
    steps = int(resistance / 10)          # the code divides as integers, towards zero
    return chance - steps * chance / 10.0 - flat_penalty


# --- who an enemy aims at (0x43f450, weights set by 0x44a630) ----------------------------------------
# Share of each party position by formation, table at 0x6517a0 (five ints per row, each row adds up to 100).
# The row is chosen by a formation number the party object returns; which formation each row stands for is
# read from its figures (members, and how many stand in front), not yet from the code that returns the number.
TARGET_SHARE = ((100,), (50, 50), (60, 40), (33, 34, 33), (38, 38, 24), (40, 30, 30), (28, 28, 28, 16),
                (30, 30, 20, 20), (31, 23, 23, 23), (24, 24, 24, 14, 14), (26, 26, 16, 16, 16))
ENMITY_UP, ENMITY_DOWN = 10, 5     # 0x44a736 (enchantment 49), 0x44a74d (enchantment 50), per piece
ENMITY_MIN = 10                    # 0x44a752


def target_weight(share, provoked=0.0, up=0, down=0):
    """Weight of one party member when an enemy picks a single target on the party's side.
    share: its figure of TARGET_SHARE. provoked: the value of effect 170 on that enemy when this member put
    it there (it is cut to an integer). up, down: equipped pieces with enchantment 49 and 50."""
    return max(ENMITY_MIN, share + int(provoked) + ENMITY_UP * up - ENMITY_DOWN * down)


def target_chances(weights):
    """Chance of each living member to be the one picked: the code rolls a number below the sum of the
    weights and takes the member it falls on (0x505ad0)."""
    total = float(sum(weights))
    return [w / total for w in weights]


# --- healing (0x48d730; cap 0x48c5c0) ---------------------------------------------------------------
HEAL_RANDOM = (0.48, 0.49, 0.50, 0.51, 0.52)      # 0x48d873: (a number below 5, plus 48) / 100
DOLL_HEAL_SCALE = 20.0                            # 0x48d821, 0x48d859
DOLL_HEAL_UP, DOLL_HEAL_MINI_UP, DOLL_HEAL_MAX = 0.02, 0.01, 0.05   # 0x48d7ff, 0x48d847, 0x48d813 (enchantments 304, 305)


def doll_heal_bonus(effect_286=0.0, up=0, mini_up=0):
    """What a heal cast by a doll adds to its coefficient."""
    return DOLL_HEAL_SCALE * effect_286 + DOLL_HEAL_SCALE * min(DOLL_HEAL_MAX, DOLL_HEAL_UP * up + DOLL_HEAL_MINI_UP * mini_up)


def heal(res, coefficient, mastery=0.0, cap=None, cap_bonus=0.0, random=0.50):
    """HP restored by a heal. coefficient: effect 103 of the skill (plus doll_heal_bonus for a doll).
    mastery: effect 245 on the caster. cap: effect 295 of the skill; cap_bonus: effect 317 of the caster.
    random: the middle of the five values the code can draw, unless a draw is passed."""
    amount = int(res * random * coefficient * (1 + mastery))
    if cap is not None:
        limit = int(cap)
        limit += int(limit * cap_bonus)
        amount = min(amount, limit)
    return amount


def fraction_recovery(maximum, value, cap=None):
    """Revival, HP recovery, TP recovery and heal by percent (effects 105, 128, 129, 132): a fraction of the
    target's maximum. cap: only for effect 132, the cap of heal()."""
    amount = int(maximum * value)
    return amount if cap is None else min(amount, int(cap))

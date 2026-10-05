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
    range_factor, race, zone and critical are factors the caller supplies: their code is not read yet."""
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
    """Damage of a spell before the final changes."""
    a = intel * (ATTACK_BASE + swing)
    b = (a + power * (1 + mastery)) * (1 + modifiers) * (1 + enchant * 0.01)
    c = b * (1 + second_modifiers) * (1 + element_boost)
    defence = target_res * MAGIC_DEFENCE_FACTOR * (1 + target_modifiers) * (1 + target_enchant * 0.01)
    damage = (c - defence) * (1 + power_boost) * (1 + damage_cut) * resistance_factor(resistance)
    return max(0.0, damage * (1 + other) * critical)


# --- chant interruption and critical hits -----------------------------------------------------------
def interruption_chance(damage, max_hp, modifier=0.0, enchant=0.0):
    """Chance that a hit of this damage breaks the chant of a unit with this max HP (0 to 0.95).
    modifier: effect 264 (Concentrate); enchant: the sum the code subtracts."""
    a = clamp(damage / (max_hp * INTERRUPT_HP_FACTOR * (1 + modifier)), 0.0, INTERRUPT_MAX)
    return clamp(a - enchant, 0.0, INTERRUPT_MAX)


def critical_rate(dex, target_agi, level, target_level, skill=0.0, enchant=0.0, target_enchant=0.0):
    """Critical rate in percent, as the messages state it (its function is not read yet: no cap applied)."""
    a = (dex * CRIT_DEX) / (dex + target_agi) * 100.0
    b = (level - target_level) * CRIT_LEVEL
    return (a + b + skill) * (1 + enchant * 0.02) * (1 + target_enchant * 0.02)


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

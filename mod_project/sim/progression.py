"""
EXP after a battle and how fast a member who is behind catches up, as the executable computes it.

Read from the code (docs/FORMULAS.md 6c):
    when an enemy falls, every member banks  int(EXP of the enemy * factor by level gap)      0x450710
    at the end of the battle a member receives  banked / living members * (1 + bonus)          0x445830
    doubled by effect 157, and doubled again by a piece with enchantment 275 (Double EXP)

Nothing here is fitted. The table of EXP per level is LvExpSkptData (a step per level).
"""

# (lowest gap, highest gap, factor, factor with enchantment 270). gap = level of the member - level of the enemy.
# 0x450734 - 0x45080d
LEVEL_GAP = ((10, None, 0.85, 0.85), (5, 9, 0.90, 0.90), (0, 4, 1.00, 1.00), (-4, -1, 1.00, 1.15),
             (-9, -5, 1.10, 1.30), (-19, -10, 1.25, 1.50), (None, -20, 1.25, 1.75))
DOUBLE = 2.0                   # 0x4459ed (effect 157) and 0x445a1e (enchantment 275)


def level_gap_factor(member_level, enemy_level, more_from_higher=False, gap_table=LEVEL_GAP):
    """gap_table: another table of the same shape, to evaluate a change of the factors."""
    gap = member_level - enemy_level
    for low, high, plain, with_enchant in gap_table:
        if (low is None or gap >= low) and (high is None or gap <= high):
            return with_enchant if more_from_higher else plain
    raise ValueError(gap)


def battle_exp(member_level, enemies, living, bonus=0.0, doubled=False, double_exp_piece=False, more_from_higher=False,
               gap_table=LEVEL_GAP):
    """EXP one member receives from a battle. enemies: [(level, EXP)] of the enemies defeated.
    living: members alive at the end. bonus: the party-wide fraction the result code is handed."""
    banked = sum(int(exp * level_gap_factor(member_level, level, more_from_higher, gap_table)) for level, exp in enemies)
    gained = banked / float(living)
    gained += gained * bonus
    if doubled:
        gained *= DOUBLE
    if double_exp_piece:
        gained *= DOUBLE
    return gained


def battles_to_reach(start_level, target_level, steps, formations, living=5, **options):
    """Battles a member needs to go from start_level to target_level on a floor.
    steps: {level: EXP needed to reach it from the level below}. formations: [(chance in percent, [(level, EXP)])].
    The expected EXP of a battle is recomputed at every level, since the factor by level gap changes."""
    battles, level = 0.0, start_level
    while level < target_level:
        expected = sum(chance / 100.0 * battle_exp(level, enemies, living, **options) for chance, enemies in formations)
        if expected <= 0:
            return float('inf')
        battles += steps[level + 1] / expected
        level += 1
    return battles


# --- level reset (0x4f94f0) ---------------------------------------------------------------------------
# (levels dropped by the reset, points added to every stat). The bonus of a character never passes RESET_MAX.
RESET_STEPS = ((98, 5), (89, 4), (79, 3), (69, 2), (59, 1))      # 0x4f94f7 - 0x4f9534
RESET_MAX = 50                                                   # 0x4f9540


def reset_bonus(level_before, level_after=1, bonus=0, steps=RESET_STEPS, cap=RESET_MAX):
    """Bonus of a character after a level reset: what it had plus the step for the levels it gave up.
    The bonus is added to each of its eight stats (0x4f5dab). steps, cap: other rules, to evaluate a change."""
    dropped = level_before - level_after
    gained = next((points for levels, points in steps if dropped >= levels), 0)
    return min(cap, bonus + gained)


def resets_to_crown(level, steps=RESET_STEPS, cap=RESET_MAX):
    """Resets from this level, always down to level 1, that reach the cap; None when that level earns nothing."""
    gained = reset_bonus(level, 1, 0, steps, cap)
    return None if gained == 0 else -(-cap // gained)

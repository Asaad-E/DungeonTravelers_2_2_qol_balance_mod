"""
What a party member does on its turn: the rules of its role, read from the sheet Policies of
data_tables/sim_setup.xlsx, tried in order; the first whose condition holds and whose action is possible is taken.

A condition is `name` or `name:argument`; an action likewise. The vocabulary is the one of CONDITIONS and ACTIONS
below; the sheet says, for each role, which of them a sensible player uses and in what order. "damage" picks the
skill (or the plain attack) with the most expected damage per unit of time on the best target, the mean of every roll
of the program taken (Battle.expected_damage), within the TP the role allows itself.
"""
from sim import formulas as f
from sim.battle import (Action, AILMENTS, CURE_ORDER, ITEM_CURE_ONE, ITEM_CURE_ALL, RANDOM_MOVES, SONG_EFFECTS,
                        DANCE_EFFECTS, AILMENT_RESIST)
from sim.data import (Skill, SINGLE, RANDOM, ROW, PIERCE, ALL, ALLY, ALLY_ROW, ALLIES, SELF, NO_TARGET, EVERYONE,
                      SHORT, MID)
from sim.units import PARTY

HEAL_EFFECTS = (103, 104, 128, 132)
DOLL_EFFECTS = (228, 229, 230, 231, 232, 233)
SONG_EFFECTS = (211, 212, 213, 214, 215, 216, 217, 218, 220, 222, 223)
DANCE_EFFECTS = (195, 196, 197, 198, 201, 205, 219, 221)


# --- what a member can do ---------------------------------------------------------------------------------------
def usable_in_battle(skill):
    group = skill.group or 0
    if skill.category == 'Technique':
        return bool(group & 0x10)
    if skill.category == 'Magic':
        return bool(group & 0x08)
    return False


def weapon_allows(unit, skill):
    """A technique that names weapons (Weapon_Codes: equipment type + 1; 0 any short-range weapon; 16 a shield)."""
    if not skill.weapons:
        return True
    weapon = unit.weapon
    for code in skill.weapons:
        if code == 0 and weapon is not None and weapon['range'] == 0:
            return True
        if code == 16 and getattr(unit, 'shield', False):
            return True
        if weapon is not None and weapon['type'] + 1 == code:
            return True
    return False


def options(battle, unit):
    """[(Skill, level)] the member can use now."""
    found = []
    for skill_id, level in unit.skills.items():
        skill = battle.data.skill_by_id.get(skill_id)
        if skill is None or not usable_in_battle(skill) or not weapon_allows(unit, skill):
            continue
        if skill.category == 'Magic' and (117 in unit.statuses or (battle.zone or {}).get('no_magic')):
            continue
        if skill.category == 'Technique' and 114 in unit.statuses:     # frozen (atwiki dt2-2 page 125)
            continue
        level = max(1, min(level, skill.levels))
        if skill.tp[level - 1] > unit.tp:
            continue
        found.append((skill, level))
    return found


def gives(skill, effect):
    return any(e == effect for e, _, _ in skill.effects)


def puts(skill, effect):
    """The skill leaves the effect on its target (a status, kind 5, or a song or dance, kind 4), not as a property
    of its own hit (kind 2: effect 26 is the power of an attack skill and the status of Berserk; FORMULAS.md 9.2)."""
    return any(e == effect and kind != 2 for e, kind, _ in skill.effects)


EVERY_ROLE = '*'           # rules of the sheet Policies under this role come before those of every role

# --- choosing ------------------------------------------------------------------------------------------------------
class Policy:
    def __init__(self, rules, setup):
        self.rules = rules              # {role: [(condition, argument, action, argument)]}
        self.setup = setup

    def __call__(self, battle, unit):
        rules = self.rules.get(EVERY_ROLE, []) + self.rules.get(getattr(unit, 'role', 'attacker'), self.rules.get('attacker', []))
        for condition, c_arg, action, a_arg in rules:
            if not CONDITIONS[condition](battle, unit, c_arg):
                continue
            chosen = ACTIONS[action](self, battle, unit, a_arg)
            if chosen is not None:
                return chosen
        attack = Action(unit, 'attack')
        target = best_single_target(battle, unit, attack)
        if target is None or battle.expected_damage(attack, target) <= 0:
            return Action(unit, 'defend')             # nothing it can do lands: a player defends
        if punished(unit, attack, target) and (self.heals(unit) or self.weak_blow(battle, attack, target)):
            return Action(unit, 'defend')             # a blow that is answered is not struck by a healer, nor for nothing
        attack.target = target
        return attack

    # the cost of time and TP of an action ---------------------------------------------------------------------
    def time_of(self, battle, action):
        unit = action.actor
        t = expected_wait(battle, unit, action)
        if action.chant_speed:
            t += expected_wait(battle, unit, action, chanting=True)
        return t

    def heals(self, unit):
        """Whether one of the rules of the member heals: she is a heal of her party."""
        return any(action == 'heal' for _, _, action, _ in self.rules.get(getattr(unit, 'role', 'attacker'), []))

    def weak_blow(self, battle, action, target):
        """Whether a plain blow takes less of the max HP of its target than the setting punished_blow_floor: not worth
        the answer of an enemy that punishes it."""
        floor = float(self.setup.get('punished_blow_floor', 0) or 0)
        return bool(floor) and battle.expected_damage(action, target) < floor * target.max_hp

    def heal_reserve(self, battle, unit):
        """The TP a member who heals keeps back from her buffs and her attacks: the cost of heal_reserve_casts of her
        cheapest heal, when one of her rules heals and she holds a heal. A player who is the heal of a party does not
        spend her last TP on a spell of fire."""
        casts = float(self.setup.get('heal_reserve_casts', 0) or 0)
        role = getattr(unit, 'role', 'attacker')
        if not casts or not any(action == 'heal' for _, _, action, _ in self.rules.get(role, [])):
            return 0.0
        costs = []
        for skill_id, level in unit.skills.items():
            skill = battle.data.skill_by_id.get(skill_id)
            if skill is not None and usable_in_battle(skill) and any(gives(skill, e) for e in HEAL_EFFECTS):
                costs.append(skill.tp[max(1, min(level, skill.levels)) - 1])
        return casts * min(costs) if costs else 0.0

    def tp_penalty(self, unit, action):
        weight = self.setup.get('tp_weight', 0.0)
        if not unit.max_tp:
            return 1.0
        return 1.0 + weight * action.tp_cost / unit.max_tp


def expected_wait(battle, unit, action, chanting=False):
    """The wait of Battle.wait with the random term at its mean (formulas.turn_value default)."""
    saved = battle.rng
    battle.rng = _MeanRandom(saved)
    try:
        return battle.wait(unit, action, chanting)
    finally:
        battle.rng = saved


class _MeanRandom:
    """Stands in for the random generator of a battle where only the mean of a draw is wanted."""

    def __init__(self, rng):
        self.rng = rng

    def choice(self, seq):
        values = list(seq)
        if values and all(isinstance(v, float) for v in values):
            return sum(values) / len(values)
        return self.rng.choice(values)

    def __getattr__(self, name):
        return getattr(self.rng, name)


def enemies_of(battle, unit):
    return battle.targetable(battle.opponents(unit))


def best_single_target(battle, unit, action):
    foes = enemies_of(battle, unit)
    if not foes:
        return None

    def target_key(t):
        dmg = battle.expected_damage(action, t)
        if dmg <= 0:
            return (3, 999999.0, 0)
        kills = dmg >= t.hp
        chanting = t.chant is not None
        asleep = 116 in t.statuses

        # Sleeping enemies: keep asleep unless lethal or execute (139)
        if asleep and not kills and not action.has(139):
            other_awake = any(f is not t and 116 not in f.statuses for f in foes)
            if other_awake:
                return (2, t.hp / max(1.0, dmg), 0)

        ratio = t.hp / max(1.0, dmg)
        if kills:
            threat = (2.0 if chanting else 1.0) * (1.5 if (battle.fixed and t.max_hp > 3000) else 1.0) * max(1.0, t.stat('atk'))
            return (0, ratio, -threat)

        if chanting:
            ratio /= 2.5

        return (1, ratio, -t.stat('atk'))

    return min(foes, key=target_key)


def random_move_value(battle, action):
    """A skill that performs one skill of a table at random (Roulette, Magic Box, Showtime, Heaven or Hell): the mean
    of the damage of each result, by the weights of the table (those of a Joker with Triple Joker, 315), as
    Battle.random_move draws them. A result aimed at the party counts 0."""
    effect = next(e for e in RANDOM_MOVES if action.has(e))
    table = next((t for t in battle.data.random_moves if t['effect'] == effect), None)
    if table is None:
        return 0.0
    key = 'joker_weight' if action.actor.has(315) else 'weight'
    total = weight = 0.0
    for r in table['results']:
        skill = battle.data.skill_by_id.get(r['skill'])
        weight += r[key]
        if skill is not None and r['effects']:
            total += r[key] * damage_value(battle, Action(action.actor, 'skill', skill, action.level))[0]
    return total / weight if weight else 0.0


def damage_value(battle, action):
    """Expected damage the action deals over its targets (each capped at the target's HP) and the target it is aimed at."""
    if isinstance(action.source, Skill) and any(action.has(e) for e in RANDOM_MOVES):
        return random_move_value(battle, action), None
    code = action.target_code
    foes = enemies_of(battle, action.actor)
    if not foes:
        return 0.0, None
    if code in (SINGLE, PIERCE):
        target = best_single_target(battle, action.actor, action)
        total = min(target.hp, battle.expected_damage(action, target))
        if code == PIERCE:
            behind = [t for t in foes if t.front != target.front]
            if behind and target.front:
                total += min(behind[0].hp, battle.expected_damage(action, behind[0]))
        return total, target
    if code == ROW:
        rows = {}
        for t in foes:
            rows.setdefault(t.front, []).append(t)
        best = max(rows.values(), key=lambda row: sum(min(t.hp, battle.expected_damage(action, t)) for t in row))
        return sum(min(t.hp, battle.expected_damage(action, t)) for t in best), best[0]
    if code == RANDOM:
        hits = battle.mean_hits(action)
        single = Action(action.actor, action.kind, action.source, action.level)
        mean = sum(battle.expected_damage(single, t) / max(1.0, battle.mean_hits(single)) for t in foes) / len(foes)
        return hits * mean, None
    if code in (ALL, EVERYONE):
        return sum(min(t.hp, battle.expected_damage(action, t)) for t in foes), None
    return 0.0, None


# --- conditions -------------------------------------------------------------------------------------------------
def _fraction(arg, default):
    return float(arg) if arg not in (None, '') else default


CONDITIONS = {
    'always': lambda b, u, a: True,
    'ally_hp_below': lambda b, u, a: any(m.hp_ratio < _fraction(a, 0.5) for m in b.allies(u) if m.kind == 'member'),
    'party_hp_below': lambda b, u, a: sum(m.hp for m in b.allies(u) if m.kind == 'member') <
    _fraction(a, 0.6) * sum(m.max_hp for m in b.allies(u) if m.kind == 'member'),
    'ally_down': lambda b, u, a: any(not m.alive for m in b.side(PARTY, alive=False) if m.kind == 'member'),
    'ally_tp_below': lambda b, u, a: any(m.max_tp and m.tp_ratio < _fraction(a, 0.3) for m in b.allies(u)
                                         if m.kind == 'member' and m is not u),
    'self_tp_below': lambda b, u, a: u.max_tp and u.tp_ratio < _fraction(a, 0.3),
    'self_hp_below': lambda b, u, a: u.hp_ratio < _fraction(a, 0.5),
    'enemy_buffed': lambda b, u, a: any(b.dispellable(t) for t in enemies_of(b, u)),
    'ally_ailing': lambda b, u, a: bool(ailing_members(b, u, a)),
    'turn_at_most': lambda b, u, a: u.turns_taken <= int(_fraction(a, 1)),
    'enemies_at_least': lambda b, u, a: len(enemies_of(b, u)) >= int(_fraction(a, 2)),
    'boss': lambda b, u, a: b.fixed or b.setup.get('boss', False),
    'no_doll': lambda b, u, a: not any(x.owner is u and x.alive and x.kind == 'doll' for x in b.units),
    # a doll slot is free: fewer living dolls of her own (arrows aside) than she can keep, two with Double Puppet (313)
    'doll_slot_free': lambda b, u, a: sum(1 for x in b.units if x.owner is u and x.alive and x.kind == 'doll'
                                          and not getattr(x, 'arrow', False)) < (2 if u.has(313) else 1),
}


# --- actions ----------------------------------------------------------------------------------------------------
def punished(unit, action, target):
    """Whether a physical blow on this enemy is answered: Avenger (249) strikes back at a short or mid reach, Dark Aura
    (262) lowers the stats of who hits at short reach (sim/battle.py, after a hit), unless the member is protected
    (307, 304)."""
    if target is None or not action.physical:
        return False
    return (target.has(249) and action.reach in (SHORT, MID) and not unit.has(307)) or \
        (target.has(262) and action.reach == SHORT and not unit.has(304))


def act_damage(policy, battle, unit, arg):
    best, best_score = None, 0.0
    candidates = [Action(unit, 'attack')]
    for skill, level in options(battle, unit):
        action = Action(unit, 'skill', skill, level)
        hits = action.target_code in (SINGLE, RANDOM, ROW, PIERCE, ALL, EVERYONE) and (
            action.physical or action.magic or battle.special(action))
        if hits or any(action.has(e) for e in RANDOM_MOVES):
            candidates.append(action)

    reserve = policy.heal_reserve(battle, unit)
    plain_attack = Action(unit, 'attack')
    plain_total, plain_target = damage_value(battle, plain_attack)
    plain_kills = plain_target is not None and plain_total >= plain_target.hp

    for action in candidates:
        if action.tp_cost > unit.tp * (1.0 - policy.setup.get('tp_reserve', 0.0)) and action.tp_cost > 0:
            continue
        if action.tp_cost > 0 and unit.tp - action.tp_cost < reserve:
            continue
        total, target = damage_value(battle, action)
        if total <= 0:
            continue
        if action.kind == 'attack' and punished(unit, action, target) and                 (policy.heals(unit) or policy.weak_blow(battle, action, target)):
            continue

        wait_time = policy.time_of(battle, action)
        penalty = policy.tp_penalty(unit, action)

        # 1. Anti-overkill when plain attack already kills
        if action.tp_cost > 0 and plain_kills and target is plain_target:
            penalty *= 1.0 + 3.0 * (action.tp_cost / max(1, unit.max_tp))

        # 2. General overkill penalty on wasted damage
        if action.tp_cost > 0 and target is not None and target.hp > 0:
            raw_dmg = battle.expected_damage(action, target) if action.target_code in (SINGLE, PIERCE) else total
            if raw_dmg > total * 1.5:
                waste_ratio = raw_dmg / max(1.0, total)
                penalty *= 1.0 + min(2.0, (waste_ratio - 1.0) * 0.5)

        # 3. Kill bonus (tempo & action economy)
        kill_mult = 1.0
        if target is not None and total >= target.hp:
            kill_mult = 1.35
        elif action.target_code in (ALL, EVERYONE, ROW, RANDOM):
            foes = enemies_of(battle, unit)
            kills = sum(1 for f in foes if battle.expected_damage(action, f) >= f.hp)
            if kills > 0:
                kill_mult = 1.0 + 0.25 * kills

        # 4. Chant interruption bonus
        chant_mult = 1.0
        if target is not None and target.chant is not None:
            chant_mult = 1.25

        score = (total * kill_mult * chant_mult) / wait_time / penalty
        if score > best_score:
            best, best_score = action, score
            best.target = target
    return best


def act_heal(policy, battle, unit, arg):
    """Restore the most HP per unit of time to the members who miss it (arg: the share of max HP below which a
    member counts as hurt)."""
    threshold = _fraction(arg, 0.6)
    hurt = [m for m in battle.allies(unit) if m.kind == 'member' and m.hp_ratio < threshold]
    if not hurt:
        return None
    best, best_score = None, 0.0
    for skill, level in options(battle, unit):
        if not any(gives(skill, e) for e in HEAL_EFFECTS):
            continue
        action = Action(unit, 'skill', skill, level)
        if action.target_code == ALLY:
            target = min(hurt, key=lambda m: m.hp_ratio)
            restored = min(target.max_hp - target.hp, expected_heal(battle, action, target))
            if target.hp_ratio < 0.25:
                restored *= 1.3
        elif action.target_code in (ALLIES, ALLY_ROW, SELF):
            group = battle.allies(unit) if action.target_code != SELF else [unit]
            target = None
            restored = sum(min(m.max_hp - m.hp, expected_heal(battle, action, m)) * (1.3 if m.hp_ratio < 0.25 else 1.0)
                           for m in group if m.kind == 'member')
        else:
            continue
        score = restored / policy.time_of(battle, action) / policy.tp_penalty(unit, action)
        if score > best_score:
            best, best_score = action, score
            best.target = target
    if best is None and unit.items:
        return act_item(policy, battle, unit, 'heal')
    return best


def expected_heal(battle, action, target):
    value = action.value(103)
    if value is not None:
        amount = f.heal(action.actor.stat('res'), value, action.actor.passives.get(245, 0.0), action.value(295),
                        action.actor.passives.get(317, 0.0))
        return action.value(9) or amount
    if action.has(104):
        return target.max_hp
    if action.has(128):
        return int(target.max_hp * action.value(128))
    if action.has(132):
        return f.fraction_recovery(target.max_hp, action.value(132), action.value(295))
    return 0


def act_revive(policy, battle, unit, arg):
    dead = [m for m in battle.side(PARTY, alive=False) if not m.alive and m.kind == 'member']
    if not dead:
        return None
    for skill, level in options(battle, unit):
        if gives(skill, 105):
            return Action(unit, 'skill', skill, level, target=dead[0])
    return act_item(policy, battle, unit, 'revive', dead[0])


def act_item(policy, battle, unit, arg, target=None):
    """Use an item the member carries: arg 'heal', 'tp' or 'revive' (item effect types 0/3, 1, 8)."""
    kinds = {'heal': (0, 3), 'tp': (1,), 'revive': (8,), 'cure': (ITEM_CURE_ALL, ITEM_CURE_ONE)}.get(arg, ())
    hurt = sum(1 for m in battle.allies(unit) if m.kind == 'member' and m.alive and m.hp_ratio < 0.6)
    usable = []
    for item_id, count in unit.items.items():
        item = battle.data.items.get(item_id)
        if count > 0 and item and any(k in kinds for k, _ in item['effects']):
            # a party item when two or more members are hurt, else the largest single one
            party = any(k == 3 for k, _ in item['effects'])
            size = max((v or 0) for k, v in item['effects'] if k in kinds) if arg != 'cure' else                 any(k == ITEM_CURE_ALL for k, _ in item['effects'])          # a cure of all before a cure of one
            usable.append(((party == (hurt >= 2)), size, item_id))
    if not usable:
        return None
    item_id = max(usable)[2]
    if target is None:
        members = [m for m in battle.allies(unit) if m.kind == 'member']
        target = min(members, key=lambda m: m.hp_ratio if arg != 'tp' else m.tp_ratio)
    return Action(unit, 'item', item=item_id, target=target)


def act_status(policy, battle, unit, arg):
    """Put a status of effect `arg` (a buff, a song, a dance, Provoke, Cover) where it is missing."""
    effect = int(arg)
    reserve = policy.heal_reserve(battle, unit)
    for skill, level in options(battle, unit):
        if not puts(skill, effect):
            continue
        action = Action(unit, 'skill', skill, level)
        if action.tp_cost > 0 and unit.tp - action.tp_cost < reserve:
            continue
        # a performer whose song or dance slots are full keeps what it performs instead of swapping one for another
        dance = effect in DANCE_EFFECTS
        if effect in SONG_EFFECTS + DANCE_EFFECTS and skill.name not in (unit.dance if dance else unit.song) and \
                len(unit.dance if dance else unit.song) >= battle.performance_slots(unit, dance):
            continue
        code = action.target_code
        if code in (SELF, NO_TARGET):
            if effect in unit.statuses:
                continue
            # Tactical Safety Check: Berserk (26) lowers DEF by 25%.
            # A smart player never casts Berserk when HP is critical (< 35%),
            # or when the fight is already virtually over (only 1 low-HP mob).
            if effect == 26:
                if unit.hp_ratio < 0.35:
                    continue
                foes = enemies_of(battle, unit)
                if len(foes) == 1 and foes[0].hp < max(100.0, unit.stat('atk') * 1.5):
                    continue
            return action
        if code == ALLY:
            lacking = [m for m in battle.allies(unit) if m.kind == 'member' and effect not in m.statuses]
            if not lacking:
                continue
            # Cover (171): prioritize chanting allies, critical HP allies, or frailest members
            if effect == 171:
                action.target = min(lacking, key=lambda m: (
                    0 if m.chant is not None else 1,
                    0 if m.hp_ratio < 0.4 else 1,
                    m.stat('def')
                ))
            else:
                action.target = max(lacking, key=lambda m: m.stat('atk') if effect == 161 else -m.stat('def')
                                    if effect == 162 else m.stat('int') if effect in (27, 173) else 0)
            return action
        if code in (ALLIES, ALLY_ROW):
            # cast again when a share of the members lack it, not for one who was revived or lost it alone
            members = [m for m in battle.allies(unit) if m.kind == 'member']
            lacking = sum(1 for m in members if effect not in m.statuses)
            share = float(policy.setup.get('party_buff_recast_share', 0) or 0)
            if not lacking or lacking < share * len(members):
                continue
            return action
        if code in (SINGLE, ALL, ROW):
            foes = [t for t in enemies_of(battle, unit) if (effect not in t.statuses or
                    (effect == 170 and unit not in t.provoked_by)) and not battle.visibly_voided(action, t)]
            if not foes:
                continue
            # Provoke (170) or offensive debuff: prioritize highest threat enemy (chanting, boss, highest ATK)
            action.target = max(foes, key=lambda t: (
                1 if t.chant is not None else 0,
                1 if (battle.fixed and t.max_hp > 3000) else 0,
                t.stat('atk')
            ))
            return action
    return None


def act_ailment(policy, battle, unit, arg):
    """Put one of the ailments named (arg: effect ids, '117;116', in order of preference) on an enemy that can take
    it: not immune, not carrying it, and the chance of the roll (formulas.ailment_chance against its resistance) at
    least ailment_min_chance of the settings. Shadow Sew (123) asks only for a target of lower level."""
    floor = float(policy.setup.get('ailment_min_chance', 0.5)) * 100
    best, best_key = None, None             # among the targets the roll can reach, the one of most max HP (the boss)
    for effect in ailments_of(arg):
        name = AILMENTS[effect]
        for skill, level in options(battle, unit):
            action = Action(unit, 'skill', skill, level)
            value = next((v for e, kind, v in action.effects() if e == effect and kind != 2), None)
            if value is None or action.target_code not in (SINGLE, RANDOM, ROW, PIERCE, ALL):
                continue
            for target in enemies_of(battle, unit):
                if name in target.immune or effect in target.statuses or battle.nullified(target, effect):
                    continue
                if effect == 123:
                    chance = value * 100 if unit.level > target.level else 0.0
                else:
                    index = AILMENT_RESIST.get(effect)
                    chance = f.ailment_chance(value, target.resistance(index) if index is not None else 0)
                key = (target.max_hp, chance)
                if chance >= floor and (best_key is None or key > best_key):
                    best, best_key = Action(unit, 'skill', skill, level), key
                    best.target = target
        if best is not None:
            return best                     # the first ailment of the list that can land is preferred
    return None


def act_dispel(policy, battle, unit, arg):
    buffed = [t for t in enemies_of(battle, unit) if battle.dispellable(t)]
    if not buffed:
        return None
    for skill, level in options(battle, unit):
        if gives(skill, 74):
            action = Action(unit, 'skill', skill, level)
            reachable = [t for t in buffed if not battle.visibly_voided(action, t)]
            if reachable:
                def dispel_priority(t):
                    has_barrier = t.has(192) or t.has(182)
                    is_boss = battle.fixed and t.max_hp > 3000
                    has_atk_buff = 161 in t.statuses or 26 in t.statuses
                    return (1 if has_barrier else 0, 1 if has_atk_buff else 0, 1 if is_boss else 0, t.stat('atk'))
                action.target = max(reachable, key=dispel_priority)
                return action
    return None


def act_doll(policy, battle, unit, arg):
    """Call a doll: arg is an order of preference, doll skill names joined by | (the first the member knows is called),
    or with no arg the doll skill of highest level."""
    dolls = [(s, lv) for s, lv in options(battle, unit) if any(gives(s, e) for e in DOLL_EFFECTS)]
    if not dolls:
        return None
    if arg:
        for name in str(arg).split('|'):
            found = [(s, lv) for s, lv in dolls if s.name == name.strip()]
            if found:
                return Action(unit, 'skill', *found[0])
        return None
    skill, level = max(dolls, key=lambda x: x[1])
    return Action(unit, 'skill', skill, level)


def act_tp(policy, battle, unit, arg):
    low = [m for m in battle.allies(unit) if m.kind == 'member' and m.max_tp and m.tp_ratio < _fraction(arg, 0.5)]
    if not low:
        return None
    # Smart TP battery triage: prioritize high TP consumers (nukers, casters, healers) over low-cost units
    def tp_need_key(m):
        heavy_roles = ('attacker', 'mage', 'healer', 'valkyrie', 'dark lord', 'magical princess', 'sage')
        role_prio = 0 if getattr(m, 'role', '') in heavy_roles else 1
        return (role_prio, m.tp_ratio)
    target = min(low, key=tp_need_key)
    for skill, level in options(battle, unit):
        if gives(skill, 129) or gives(skill, 426):
            return Action(unit, 'skill', skill, level, target=target)
    return act_item(policy, battle, unit, 'tp', target)


def ailments_of(arg):
    """The ailments an argument names ('120;116', effect ids), all of them when it names none."""
    return [int(x) for x in str(arg).split(';') if x.strip()] if arg not in (None, '') else list(AILMENTS)


def ailing_members(battle, unit, arg):
    wanted = ailments_of(arg)
    return [m for m in battle.allies(unit) if m.kind == 'member' and any(e in m.statuses for e in wanted)]


def act_cure(policy, battle, unit, arg):
    """Cure the member who carries the most of the ailments named (arg, as ally_ailing), with a skill of effect 106
    whose level reaches one of them (it walks the first int(value) entries of CURE_ORDER), else an item."""
    wanted = ailments_of(arg)
    ailing = ailing_members(battle, unit, arg)
    if not ailing:
        return None
    target = max(ailing, key=lambda m: sum(e in m.statuses for e in wanted))
    carried = [e for e in wanted if e in target.statuses]
    for skill, level in options(battle, unit):
        action = Action(unit, 'skill', skill, level)
        if gives(skill, 106) and any(e in CURE_ORDER[:int(action.value(106) or 0)] for e in carried):
            action.target = target if action.target_code == ALLY else None
            return action
    if unit.items:
        return act_item(policy, battle, unit, 'cure', target)
    return None


def act_skill(policy, battle, unit, arg):
    """Use the named skill on the best target."""
    for skill, level in options(battle, unit):
        if skill.name == arg:
            action = Action(unit, 'skill', skill, level)
            if action.target_code in (SINGLE, PIERCE):
                action.target = best_single_target(battle, unit, action)
            return action
    return None


ACTIONS = {
    'damage': act_damage, 'heal': act_heal, 'revive': act_revive, 'status': act_status, 'dispel': act_dispel,
    'doll': act_doll, 'tp': act_tp, 'cure': act_cure, 'ailment': act_ailment, 'item': act_item, 'skill': act_skill,
    'defend': lambda p, b, u, a: Action(u, 'defend'),
}


def load_rules(rows):
    """rows of the sheet Policies: Role, Order, Condition, Action. Returns {role: [(condition, arg, action, arg)]}."""
    rules = {}
    for r in sorted(rows, key=lambda r: (r['Role'], r['Order'])):
        cond, _, c_arg = str(r['Condition']).partition(':')
        act, _, a_arg = str(r['Action']).partition(':')
        if cond not in CONDITIONS:
            raise ValueError(f'unknown condition {cond!r} in role {r["Role"]}')
        if act not in ACTIONS:
            raise ValueError(f'unknown action {act!r} in role {r["Role"]}')
        rules.setdefault(r['Role'], []).append((cond, c_arg or None, act, a_arg or None))
    return rules

"""
What a party member does on its turn: the rules of its role, read from the sheet Policies of
data_tables/sim_setup.xlsx, tried in order; the first whose condition holds and whose action is possible is taken.

A condition is `name` or `name:argument`; an action likewise. The vocabulary is the one of CONDITIONS and ACTIONS
below; the sheet says, for each role, which of them a sensible player uses and in what order. "damage" picks the
skill (or the plain attack) with the most expected damage per unit of time on the best target, the mean of every roll
of the program taken (Battle.expected_damage), within the TP the role allows itself.
"""
from sim import formulas as f
from sim.battle import Action, AILMENTS, SONG_EFFECTS, DANCE_EFFECTS
from sim.data import (Skill, SINGLE, RANDOM, ROW, PIERCE, ALL, ALLY, ALLY_ROW, ALLIES, SELF, NO_TARGET, EVERYONE)
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


# --- choosing ------------------------------------------------------------------------------------------------------
class Policy:
    def __init__(self, rules, setup):
        self.rules = rules              # {role: [(condition, argument, action, argument)]}
        self.setup = setup

    def __call__(self, battle, unit):
        for condition, c_arg, action, a_arg in self.rules.get(getattr(unit, 'role', 'attacker'), self.rules.get('attacker', [])):
            if not CONDITIONS[condition](battle, unit, c_arg):
                continue
            chosen = ACTIONS[action](self, battle, unit, a_arg)
            if chosen is not None:
                return chosen
        attack = Action(unit, 'attack')
        target = best_single_target(battle, unit, attack)
        if target is None or battle.expected_damage(attack, target) <= 0:
            return Action(unit, 'defend')             # nothing it can do lands: a player defends
        attack.target = target
        return attack

    # the cost of time and TP of an action ---------------------------------------------------------------------
    def time_of(self, battle, action):
        unit = action.actor
        t = expected_wait(battle, unit, action)
        if action.chant_speed:
            t += expected_wait(battle, unit, action, chanting=True)
        return t

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
    # the foe this action can bring down soonest: least HP left per expected damage
    return min(foes, key=lambda t: t.hp / max(1.0, battle.expected_damage(action, t)))


def damage_value(battle, action):
    """Expected damage the action deals over its targets (each capped at the target's HP) and the target it is aimed at."""
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
    'ally_ailing': lambda b, u, a: any(any(e in m.statuses for e in AILMENTS) for m in b.allies(u) if m.kind == 'member'),
    'turn_at_most': lambda b, u, a: u.turns_taken <= int(_fraction(a, 1)),
    'enemies_at_least': lambda b, u, a: len(enemies_of(b, u)) >= int(_fraction(a, 2)),
    'boss': lambda b, u, a: b.setup.get('boss', False),
    'no_doll': lambda b, u, a: not any(x.owner is u and x.alive and x.kind == 'doll' for x in b.units),
}


# --- actions ----------------------------------------------------------------------------------------------------
def act_damage(policy, battle, unit, arg):
    best, best_score = None, 0.0
    candidates = [Action(unit, 'attack')]
    for skill, level in options(battle, unit):
        action = Action(unit, 'skill', skill, level)
        if action.target_code in (SINGLE, RANDOM, ROW, PIERCE, ALL, EVERYONE) and (action.physical or action.magic
                                                                                    or battle.special(action)):
            candidates.append(action)
    for action in candidates:
        if action.tp_cost > unit.tp * (1.0 - policy.setup.get('tp_reserve', 0.0)) and action.tp_cost > 0:
            continue
        total, target = damage_value(battle, action)
        if total <= 0:
            continue
        score = total / policy.time_of(battle, action) / policy.tp_penalty(unit, action)
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
        elif action.target_code in (ALLIES, ALLY_ROW, SELF):
            group = battle.allies(unit) if action.target_code != SELF else [unit]
            target = None
            restored = sum(min(m.max_hp - m.hp, expected_heal(battle, action, m)) for m in group if m.kind == 'member')
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
    kinds = {'heal': (0, 3), 'tp': (1,), 'revive': (8,)}.get(arg, ())
    hurt = sum(1 for m in battle.allies(unit) if m.kind == 'member' and m.alive and m.hp_ratio < 0.6)
    usable = []
    for item_id, count in unit.items.items():
        item = battle.data.items.get(item_id)
        if count > 0 and item and any(k in kinds for k, _ in item['effects']):
            # a party item when two or more members are hurt, else the largest single one
            party = any(k == 3 for k, _ in item['effects'])
            size = max((v or 0) for k, v in item['effects'] if k in kinds)
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
    for skill, level in options(battle, unit):
        if not gives(skill, effect):
            continue
        action = Action(unit, 'skill', skill, level)
        # a performer whose song or dance slots are full keeps what it performs instead of swapping one for another
        dance = effect in DANCE_EFFECTS
        if effect in SONG_EFFECTS + DANCE_EFFECTS and skill.name not in (unit.dance if dance else unit.song) and \
                len(unit.dance if dance else unit.song) >= battle.performance_slots(unit, dance):
            continue
        code = action.target_code
        if code in (SELF, NO_TARGET):
            if effect in unit.statuses:
                continue
            return action
        if code == ALLY:
            lacking = [m for m in battle.allies(unit) if m.kind == 'member' and effect not in m.statuses]
            if not lacking:
                continue
            action.target = max(lacking, key=lambda m: m.stat('atk') if effect == 161 else -m.stat('def')
                                if effect == 162 else m.stat('int') if effect in (27, 173) else 0)
            return action
        if code in (ALLIES, ALLY_ROW):
            if all(effect in m.statuses for m in battle.allies(unit) if m.kind == 'member'):
                continue
            return action
        if code in (SINGLE, ALL, ROW):
            foes = [t for t in enemies_of(battle, unit) if (effect not in t.statuses or
                    (effect == 170 and unit not in t.provoked_by)) and not battle.visibly_voided(action, t)]
            if not foes:
                continue
            action.target = max(foes, key=lambda t: t.stat('atk'))
            return action
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
                action.target = reachable[0]
                return action
    return None


def act_doll(policy, battle, unit, arg):
    """Call the doll named by arg (its skill name) or, with no arg, the doll skill of highest level."""
    dolls = [(s, lv) for s, lv in options(battle, unit) if any(gives(s, e) for e in DOLL_EFFECTS)]
    if arg:
        dolls = [(s, lv) for s, lv in dolls if s.name == arg]
    if not dolls:
        return None
    skill, level = max(dolls, key=lambda x: x[1])
    return Action(unit, 'skill', skill, level)


def act_tp(policy, battle, unit, arg):
    low = [m for m in battle.allies(unit) if m.kind == 'member' and m.max_tp and m.tp_ratio < _fraction(arg, 0.5)]
    if not low:
        return None
    target = min(low, key=lambda m: m.tp_ratio)
    for skill, level in options(battle, unit):
        if gives(skill, 129) or gives(skill, 426):
            return Action(unit, 'skill', skill, level, target=target)
    return act_item(policy, battle, unit, 'tp', target)


def act_cure(policy, battle, unit, arg):
    ailing = [m for m in battle.allies(unit) if m.kind == 'member' and any(e in m.statuses for e in AILMENTS)]
    if not ailing:
        return None
    for skill, level in options(battle, unit):
        if gives(skill, 106):
            return Action(unit, 'skill', skill, level, target=ailing[0])
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
    'doll': act_doll, 'tp': act_tp, 'cure': act_cure, 'item': act_item, 'skill': act_skill,
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

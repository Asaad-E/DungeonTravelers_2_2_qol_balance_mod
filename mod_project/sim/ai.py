"""
What an enemy, a summon or a guest ally does on its turn: its script of EnemyAIData run as the program runs it
(docs/FORMULAS.md 9; decoded by tools/enemy_ai.py).

The set is 0 at the start of every turn (0x430f56). The commands before the first set run in order until one decides; with no attack decided
the code rolls a number below the sum of the 16 weights of the current set and takes the slot it falls in, then runs
the commands of that set: one that passes may name another attack or switch to another set, which rolls again there.
Silence, freeze and shadow bind replace the choice with attack slot 0.
"""
from sim import data as _data          # puts tools/ on the path
from sim.battle import Action, AILMENTS

import enemy_ai as code

MAX_SWITCHES = 8
BUFF_SOURCE_SIDE = True          # a buff is a status put by the unit's own side; a debuff one put by the other side


def choose(battle, unit):
    attacks = unit.attacks
    if not attacks:
        return Action(unit, 'defend')
    if any(e in unit.statuses for e in (117, 114, 123)):
        return attack_action(battle, unit, 0)
    script = unit.script
    if not script:
        return attack_action(battle, unit, roll_uniform(battle, attacks))
    unit.ai_set = 0                     # 0x430f56: every turn the runner starts again from set 0
    decided = run(battle, unit, script['opening'])
    switches = 0
    while decided is None or decided[0] == 'set':
        if decided is not None:
            unit.ai_set = decided[1]
            switches += 1
            if switches > MAX_SWITCHES:
                break
        entry = script['sets'].get(unit.ai_set) or script['sets'].get(min(script['sets'], default=0))
        if entry is None:
            decided = ('slot', roll_uniform(battle, attacks))
            break
        slot = roll_weights(battle, entry['weights'], len(attacks))
        found = run(battle, unit, entry['commands'], rolled=slot)
        decided = found if found is not None else ('slot', slot)
    if decided is None or decided[0] == 'set':
        decided = ('slot', 0)
    if decided[0] == 'slot':
        return attack_action(battle, unit, decided[1])
    return attack_action(battle, unit, None, attack_id=decided[1])


def roll_uniform(battle, attacks):
    return battle.rng.randrange(len(attacks))


def roll_weights(battle, weights, count):
    usable = [(slot, w) for slot, w in enumerate(weights) if w and slot < count]
    if not usable:
        return 0
    roll = battle.rng.randrange(sum(w for _, w in usable))
    for slot, w in usable:
        roll -= w
        if roll < 0:
            return slot
    return usable[-1][0]


def run(battle, unit, commands, rolled=None):
    """The first command that passes and decides: ('slot', n), ('attack', id) or ('set', n)."""
    for k, command in enumerate(commands):
        if command['cmd'] == code.TARGET:
            unit.__dict__.setdefault('ai_targets', {})[command['args'][0]] = command['args'][1]
            continue
        key = (id(commands), k)
        if command.get('once') and key in unit.once_done:
            continue
        if not passes(battle, unit, command, rolled):
            continue
        result = final_result(battle, unit, command, rolled)
        if result is None:
            continue
        if command.get('once'):
            unit.once_done.add(key)
        return result
    return None


def final_result(battle, unit, command, rolled):
    result = command['result']
    while result & code.CHAIN:
        command = command['and']
        if not passes(battle, unit, command, rolled):
            return None
        result = command['result']
    if result & code.TO_SET:
        return ('set', result & 0x0FFF)
    if result & code.SLOT:
        return ('slot', result & 0x0FFF)
    if result & code.ATTACK_ID:
        return ('attack', result & 0x0FFF)
    return None


def skill_of(unit, word):
    """The attack id a skill word names."""
    if word & code.SLOT:
        slot = word & 0x3FFF
        return unit.attacks[slot] if slot < len(unit.attacks) else None
    if word & code.ATTACK_ID:
        return word & 0x3FFF
    return None


def passes(battle, unit, command, rolled):
    cid, args = command['cmd'], command.get('args', [])
    if cid == 2:
        return unit.turns_taken <= args[0]
    if cid in (3, 10, 12, 13, 14):
        value = source_value(battle, unit, args[0])
        n = args[1]
        return {3: value <= n, 10: value > n, 12: value >= n, 13: value < n, 14: value == n}[cid]
    if cid in (4, 11):
        return source_value(battle, unit, args[0]) > 0
    if cid == 5:
        last = getattr(unit.last_skill, 'id', None)
        return last is not None and last == skill_of(unit, args[0])
    if cid == 6:
        attack = battle.data.attacks.get(skill_of(unit, args[0]))
        name = attack.name if attack else None
        return any(s.source is unit and s.skill == name for u in battle.units if u.alive for s in u.statuses.values())
    if cid == 7:
        attack = battle.data.attacks.get(skill_of(unit, args[0]))
        return attack is not None and unit.uses.get(attack.name, 0) >= args[1]
    if cid == 9:
        return any(not u.alive for u in battle.allies(unit, alive=False) if u.kind != 'doll')
    if cid == 15:
        return False
    return False


def source_value(battle, unit, source):
    allies, foes = battle.allies(unit), battle.targetable(battle.opponents(unit))
    if source == 0:
        return int(unit.hp_ratio * 100)
    if source == 1:
        return min((int(u.hp_ratio * 100) for u in allies), default=100)
    if source == 2:
        return min((int(u.hp_ratio * 100) for u in foes), default=100)
    if source == 3:
        return min((int(u.tp_ratio * 100) for u in allies), default=100)
    if source == 4:
        return min((int(u.tp_ratio * 100) for u in foes), default=100)
    if source == 5:
        return sum(1 for u in allies if any(e in u.statuses for e in AILMENTS))
    if source == 6:
        return sum(1 for u in foes if any(e in u.statuses for e in AILMENTS))
    if source == 7:
        return sum(1 for u in foes if u.chant is not None)
    if source == 8:
        return sum(1 for u in foes if not u.front)
    if source == 9:
        return sum(1 for u in foes if u.front)
    if source == 10:
        return sum(1 for u in foes if has_buff(u))
    if source == 11:
        return sum(1 for u in allies if has_debuff(u))
    return 0


def has_buff(unit):
    return any(s.source is not None and s.source.side == unit.side and e not in AILMENTS for e, s in unit.statuses.items())


def has_debuff(unit):
    return any(s.source is not None and s.source.side != unit.side and e not in AILMENTS for e, s in unit.statuses.items())


def attack_action(battle, unit, slot, attack_id=None):
    if attack_id is None:
        attack_id = unit.attacks[min(slot, len(unit.attacks) - 1)]
    attack = battle.data.attacks.get(attack_id)
    if attack is None:
        return Action(unit, 'defend')
    action = Action(unit, 'enemy', attack, 1)
    targets = getattr(unit, 'ai_targets', {})
    kind = None
    for word, k in targets.items():
        if skill_of(unit, word) == attack_id:
            kind = k
    if kind is not None:
        action.target = pick_by_kind(battle, unit, kind, attack)
    return action


def pick_by_kind(battle, unit, kind, attack):
    """Target kinds of command 1 (jump table 0x434754)."""
    allies, foes = battle.allies(unit), battle.targetable(battle.opponents(unit))
    if kind == 0:
        return min(allies, key=lambda u: u.hp_ratio, default=None)
    if kind == 1:
        return min(foes, key=lambda u: u.hp_ratio, default=None)
    if kind == 2:
        return min(allies, key=lambda u: u.tp_ratio, default=None)
    if kind == 3:
        return min(foes, key=lambda u: u.tp_ratio, default=None)
    if kind in (4, 9, 13):
        hurt = [u for u in allies if any(e in u.statuses for e in AILMENTS)]
        return hurt[0] if hurt else None
    if kind in (5, 14):
        hurt = [u for u in foes if any(e in u.statuses for e in AILMENTS)]
        return hurt[0] if hurt else None
    if kind == 6:
        return next((u for u in foes if u.chant is not None), None)
    if kind == 7:
        return next((u for u in foes if not u.front), None)
    if kind == 8:
        effects = {e for e, _, _ in attack.effects}
        return next((u for u in allies if not effects & set(u.statuses)), None)
    if kind == 10:
        return next((u for u in foes if u.front), None)
    if kind == 11:
        return next((u for u in foes if has_buff(u)), None)
    if kind == 12:
        return next((u for u in allies if has_debuff(u)), None)
    if kind == 15:
        return next((u for u in battle.allies(unit, alive=False) if not u.alive), None)
    return None

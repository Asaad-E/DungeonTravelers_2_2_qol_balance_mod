"""
Experiment script to test improved policy logic and measure the effect on Vanilla and Mod.
"""
import sys
import copy
import random
sys.path.insert(0, 'mod_project')

from sim.data import game_data
from sim.setup import load
from sim.variant import balance_data
from sim import measures, scenario
from sim.battle import Battle, Action, DEMON_WALL, AILMENTS
from sim import formulas as f
import sim.policy as P

# Backup original functions
orig_best_single_target = P.best_single_target
orig_act_damage = P.act_damage
orig_act_status = P.act_status
orig_act_dispel = P.act_dispel
orig_act_heal = P.act_heal
orig_expected_damage = Battle.expected_damage

def improved_expected_damage(self, action, target):
    """Enhanced expected damage with Sleep, Demon Wall, Ailing Target and Execution (139)."""
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
                               skill=sum(self.first(action, unit, e) for e in (31, 174, 211)) + target.value(32),
                               enchant=f.critical_enchant(unit.pieces(45), unit.pieces(46)),
                               target_enchant=-f.critical_enchant(target.pieces(47), target.pieces(48)),
                               floor_268=bool(unit.pieces(268)), fixed=action.value(70))
        per_hit = self.physical_damage(action, target, 0, f.expected_critical_factor(rate), expect=True)
    
    # 0x44cd3b, 0x44eff9: sleeping target takes 1.5x damage
    if 116 in target.statuses and not self.special(action):
        per_hit = per_hit * f.SLEEP_DAMAGE[0] / f.SLEEP_DAMAGE[1]
    
    # Demon Wall cuts damage
    if not self.special(action):
        wall = next((u for u in self.allies(target) if u.has(DEMON_WALL)), None)
        if wall is not None:
            per_hit = max(0.0, per_hit + per_hit * wall.value(DEMON_WALL))
            
    # Ailing target bonus
    enchant, share = f.AILING_TARGET_BONUS
    if not self.special(action) and action.actor.pieces(enchant) and any(e in target.statuses for e in AILMENTS):
        per_hit += per_hit * share
        
    if action.magic:
        cap = action.value(296)
        if cap is not None:
            per_hit = min(per_hit, float(cap))
            
    return chance * hits * per_hit

def improved_best_single_target(battle, unit, action):
    foes = P.enemies_of(battle, unit)
    if not foes:
        return None

    def target_key(t):
        dmg = battle.expected_damage(action, t)
        if dmg <= 0:
            return (3, 999999.0, 0)
        
        kills = dmg >= t.hp
        chanting = t.chant is not None
        asleep = 116 in t.statuses
        
        # If sleeping and non-lethal, don't wake if others awake
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

def improved_act_damage(policy, battle, unit, arg):
    best, best_score = None, 0.0
    candidates = [Action(unit, 'attack')]
    for skill, level in P.options(battle, unit):
        action = Action(unit, 'skill', skill, level)
        hits = action.target_code in (P.SINGLE, P.RANDOM, P.ROW, P.PIERCE, P.ALL, P.EVERYONE) and (
            action.physical or action.magic or battle.special(action))
        if hits or any(action.has(e) for e in P.RANDOM_MOVES):
            candidates.append(action)
            
    plain_attack = Action(unit, 'attack')
    plain_total, plain_target = P.damage_value(battle, plain_attack)
    plain_kills = plain_target is not None and plain_total >= plain_target.hp

    for action in candidates:
        if action.tp_cost > unit.tp * (1.0 - policy.setup.get('tp_reserve', 0.0)) and action.tp_cost > 0:
            continue
        total, target = P.damage_value(battle, action)
        if total <= 0:
            continue
            
        wait_time = policy.time_of(battle, action)
        penalty = policy.tp_penalty(unit, action)
        
        # 1. Anti-overkill when plain attack already kills
        if action.tp_cost > 0 and plain_kills and target is plain_target:
            penalty *= 1.0 + 3.0 * (action.tp_cost / max(1, unit.max_tp))
            
        # 2. General overkill penalty on wasted damage
        if action.tp_cost > 0 and target is not None and target.hp > 0:
            raw_dmg = battle.expected_damage(action, target) if action.target_code in (P.SINGLE, P.PIERCE) else total
            if raw_dmg > total * 1.5:
                waste_ratio = raw_dmg / max(1.0, total)
                penalty *= 1.0 + min(2.0, (waste_ratio - 1.0) * 0.5)
                
        # 3. Kill bonus (tempo & action economy)
        kill_mult = 1.0
        if target is not None and total >= target.hp:
            kill_mult = 1.35
        elif action.target_code in (P.ALL, P.EVERYONE, P.ROW, P.RANDOM):
            foes = P.enemies_of(battle, unit)
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

def improved_act_status(policy, battle, unit, arg):
    effect = int(arg)
    for skill, level in P.options(battle, unit):
        if not P.puts(skill, effect):
            continue
        action = Action(unit, 'skill', skill, level)
        dance = effect in P.DANCE_EFFECTS
        if effect in P.SONG_EFFECTS + P.DANCE_EFFECTS and skill.name not in (unit.dance if dance else unit.song) and \
                len(unit.dance if dance else unit.song) >= battle.performance_slots(unit, dance):
            continue
        code = action.target_code
        if code in (P.SELF, P.NO_TARGET):
            if effect in unit.statuses:
                continue
            if effect == 26:
                if unit.hp_ratio < 0.35:
                    continue
                foes = P.enemies_of(battle, unit)
                if len(foes) == 1 and foes[0].hp < max(100.0, unit.stat('atk') * 1.5):
                    continue
            return action
        if code == P.ALLY:
            lacking = [m for m in battle.allies(unit) if m.kind == 'member' and effect not in m.statuses]
            if not lacking:
                continue
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
        if code in (P.ALLIES, P.ALLY_ROW):
            if all(effect in m.statuses for m in battle.allies(unit) if m.kind == 'member'):
                continue
            return action
        if code in (P.SINGLE, P.ALL, P.ROW):
            foes = [t for t in P.enemies_of(battle, unit) if (effect not in t.statuses or
                    (effect == 170 and unit not in t.provoked_by)) and not battle.visibly_voided(action, t)]
            if not foes:
                continue
            action.target = max(foes, key=lambda t: (
                1 if t.chant is not None else 0,
                1 if (battle.fixed and t.max_hp > 3000) else 0,
                t.stat('atk')
            ))
            return action
    return None

def improved_act_dispel(policy, battle, unit, arg):
    buffed = [t for t in P.enemies_of(battle, unit) if battle.dispellable(t)]
    if not buffed:
        return None
    for skill, level in P.options(battle, unit):
        if P.gives(skill, 74):
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

def run_comparison():
    data = game_data()
    setup = load()
    mod = balance_data(data)
    checkpoints = ['C06', 'C17', 'C30', 'C34', 'C40']
    
    print(">>> 1. BASELINE (ORIGINAL AI)")
    res_orig = measures.check_change(data, setup, [], checkpoints, runs=10, changed=mod)
    for cid, b, a, out in res_orig:
        print(f"[{cid}] Vanilla: won={b['won']*100:.0f}%, time={b['time']:.1f}s | Mod: won={a['won']*100:.0f}%, time={a['time']:.1f}s | Out: {out}")
        
    # Apply monkeypatches to BOTH module globals and ACTIONS dict
    Battle.expected_damage = improved_expected_damage
    P.best_single_target = improved_best_single_target
    P.act_damage = improved_act_damage
    P.act_status = improved_act_status
    P.act_dispel = improved_act_dispel
    P.ACTIONS['damage'] = improved_act_damage
    P.ACTIONS['status'] = improved_act_status
    P.ACTIONS['dispel'] = improved_act_dispel
    
    print("\n>>> 2. WITH IMPROVED SMART AI (BOTH VANILLA & MOD)")
    res_new = measures.check_change(data, setup, [], checkpoints, runs=10, changed=mod)
    for cid, b, a, out in res_new:
        print(f"[{cid}] Vanilla: won={b['won']*100:.0f}%, time={b['time']:.1f}s | Mod: won={a['won']*100:.0f}%, time={a['time']:.1f}s | Out: {out}")

if __name__ == '__main__':
    run_comparison()

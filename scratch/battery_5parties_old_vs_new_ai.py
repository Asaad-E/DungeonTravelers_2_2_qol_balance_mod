"""
Comprehensive Battery: All 17 Story Bosses across 5 Parties comparing Old AI vs New AI.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
import io
import json
import math
import os
import random
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import scenario
from sim import setup as setup_mod
from sim.battle import Battle, Action, Status, DEMON_WALL, AILMENTS
from sim.data import game_data
from sim import formulas as f
from sim.variant import balance_data
import sim.policy as P
from tools.parallel_party_battery import CHECKPOINTS, PARTIES, build_party_complete

# --- NEW AI REFERENCES (Current in codebase) ---
new_expected_damage = Battle.expected_damage
new_best_single_target = P.best_single_target
new_act_damage = P.act_damage
new_act_heal = P.act_heal
new_act_status = P.act_status
new_act_dispel = P.act_dispel
new_act_tp = P.act_tp

# --- OLD AI DEFINITIONS ---
def old_expected_damage(self, action, target):
    if action.has(25) or not (action.physical or action.magic or self.special(action)):
        return 0.0
    if self.visibly_voided(action, target):
        return 0.0
    hits = self.mean_hits(action)
    chance = self.hit_chance(action, target)
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
    return chance * hits * per_hit

def old_best_single_target(battle, unit, action):
    foes = P.enemies_of(battle, unit)
    if not foes:
        return None
    return min(foes, key=lambda t: t.hp / max(1.0, battle.expected_damage(action, t)))

def old_act_damage(policy, battle, unit, arg):
    best, best_score = None, 0.0
    candidates = [Action(unit, 'attack')]
    for skill, level in P.options(battle, unit):
        action = Action(unit, 'skill', skill, level)
        hits = action.target_code in (P.SINGLE, P.RANDOM, P.ROW, P.PIERCE, P.ALL, P.EVERYONE) and (
            action.physical or action.magic or battle.special(action))
        if hits or any(action.has(e) for e in P.RANDOM_MOVES):
            candidates.append(action)
    for action in candidates:
        if action.tp_cost > unit.tp * (1.0 - policy.setup.get('tp_reserve', 0.0)) and action.tp_cost > 0:
            continue
        total, target = P.damage_value(battle, action)
        if total <= 0:
            continue
        score = total / policy.time_of(battle, action) / policy.tp_penalty(unit, action)
        if score > best_score:
            best, best_score = action, score
            best.target = target
    return best

def old_act_heal(policy, battle, unit, arg):
    threshold = P._fraction(arg, 0.6)
    hurt = [m for m in battle.allies(unit) if m.kind == 'member' and m.hp_ratio < threshold]
    if not hurt:
        return None
    best, best_score = None, 0.0
    for skill, level in P.options(battle, unit):
        if not any(P.gives(skill, e) for e in P.HEAL_EFFECTS):
            continue
        action = Action(unit, 'skill', skill, level)
        if action.target_code == P.ALLY:
            target = min(hurt, key=lambda m: m.hp_ratio)
            restored = min(target.max_hp - target.hp, P.expected_heal(battle, action, target))
        elif action.target_code in (P.ALLIES, P.ALLY_ROW, P.SELF):
            group = battle.allies(unit) if action.target_code != P.SELF else [unit]
            target = None
            restored = sum(min(m.max_hp - m.hp, P.expected_heal(battle, action, m)) for m in group if m.kind == 'member')
        else:
            continue
        score = restored / policy.time_of(battle, action) / policy.tp_penalty(unit, action)
        if score > best_score:
            best, best_score = action, score
            best.target = target
    if best is None and unit.items:
        return P.act_item(policy, battle, unit, 'heal')
    return best

def old_act_status(policy, battle, unit, arg):
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
            return action
        if code == P.ALLY:
            lacking = [m for m in battle.allies(unit) if m.kind == 'member' and effect not in m.statuses]
            if not lacking:
                continue
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
            action.target = max(foes, key=lambda t: t.stat('atk'))
            return action
    return None

def old_act_dispel(policy, battle, unit, arg):
    buffed = [t for t in P.enemies_of(battle, unit) if battle.dispellable(t)]
    if not buffed:
        return None
    for skill, level in P.options(battle, unit):
        if P.gives(skill, 74):
            action = Action(unit, 'skill', skill, level)
            reachable = [t for t in buffed if not battle.visibly_voided(action, t)]
            if reachable:
                action.target = reachable[0]
                return action
    return None

def old_act_tp(policy, battle, unit, arg):
    low = [m for m in battle.allies(unit) if m.kind == 'member' and m.max_tp and m.tp_ratio < P._fraction(arg, 0.5)]
    if not low:
        return None
    target = min(low, key=lambda m: m.tp_ratio)
    for skill, level in P.options(battle, unit):
        if P.gives(skill, 129) or P.gives(skill, 426):
            return Action(unit, 'skill', skill, level, target=target)
    return P.act_item(policy, battle, unit, 'tp', target)

def set_ai(mode='new'):
    if mode == 'old':
        Battle.expected_damage = old_expected_damage
        P.best_single_target = old_best_single_target
        P.act_damage = old_act_damage
        P.act_heal = old_act_heal
        P.act_status = old_act_status
        P.act_dispel = old_act_dispel
        P.act_tp = old_act_tp
        P.ACTIONS['damage'] = old_act_damage
        P.ACTIONS['heal'] = old_act_heal
        P.ACTIONS['status'] = old_act_status
        P.ACTIONS['dispel'] = old_act_dispel
        P.ACTIONS['tp'] = old_act_tp
    else:
        Battle.expected_damage = new_expected_damage
        P.best_single_target = new_best_single_target
        P.act_damage = new_act_damage
        P.act_heal = new_act_heal
        P.act_status = new_act_status
        P.act_dispel = new_act_dispel
        P.act_tp = new_act_tp
        P.ACTIONS['damage'] = new_act_damage
        P.ACTIONS['heal'] = new_act_heal
        P.ACTIONS['status'] = new_act_status
        P.ACTIONS['dispel'] = new_act_dispel
        P.ACTIONS['tp'] = new_act_tp

# Worker state
_WORKER_DATA = None
_WORKER_SETUP = None
_WORKER_VARIANT = None

def init_worker():
    global _WORKER_DATA, _WORKER_SETUP, _WORKER_VARIANT
    _WORKER_DATA = game_data()
    _WORKER_SETUP = setup_mod.load()
    _WORKER_VARIANT = balance_data(_WORKER_DATA)

def run_task(args):
    cid, p_name, roles, runs, seed = args
    global _WORKER_DATA, _WORKER_SETUP, _WORKER_VARIANT
    data = _WORKER_DATA
    setup = _WORKER_SETUP
    variant = _WORKER_VARIANT
    cp = setup.checkpoint(cid)

    # 1. EVALUATE OLD AI ON MOD
    set_ai('old')
    res_m_old = scenario.play(
        variant, setup,
        lambda: build_party_complete(variant, setup, roles, cid),
        lambda: [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
        runs=runs, seed=seed
    )

    # 2. EVALUATE NEW AI ON MOD
    set_ai('new')
    res_m_new = scenario.play(
        variant, setup,
        lambda: build_party_complete(variant, setup, roles, cid),
        lambda: [scenario.fixed_battle(variant, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
        runs=runs, seed=seed
    )

    # 3. EVALUATE OLD AI ON VANILLA
    set_ai('old')
    res_v_old = scenario.play(
        data, setup,
        lambda: build_party_complete(data, setup, roles, cid),
        lambda: [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
        runs=runs, seed=seed
    )

    # 4. EVALUATE NEW AI ON VANILLA
    set_ai('new')
    res_v_new = scenario.play(
        data, setup,
        lambda: build_party_complete(data, setup, roles, cid),
        lambda: [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
        runs=runs, seed=seed
    )

    def stats(res):
        wins = [r for r in res if r['won']]
        losses = [r for r in res if not r['won']]
        pct = len(wins) / len(res) * 100.0
        if wins:
            rnds = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in wins) / len(wins)
        else:
            rnds = sum(sum(r['record'].actions.get(u, 0) for u in r['record'].actions if getattr(u, 'kind', '') == 'member') / 5.0 for r in losses) / max(1, len(losses))
        return pct, rnds, bool(wins)

    m_old_pct, m_old_rnd, m_old_won = stats(res_m_old)
    m_new_pct, m_new_rnd, m_new_won = stats(res_m_new)
    v_old_pct, v_old_rnd, v_old_won = stats(res_v_old)
    v_new_pct, v_new_rnd, v_new_won = stats(res_v_new)

    return (cid, p_name, 
            (m_old_pct, m_old_rnd, m_old_won),
            (m_new_pct, m_new_rnd, m_new_won),
            (v_old_pct, v_old_rnd, v_old_won),
            (v_new_pct, v_new_rnd, v_new_won))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=int, default=20, help='Number of runs per battle')
    parser.add_argument('--workers', type=int, default=6, help='Number of parallel workers')
    args = parser.parse_args()

    start_time = time.time()
    print(f"=== INICIANDO BATERÍA COMPLETA: OLD AI vs NEW AI (5 PARTIES x 17 BOSSES) ===")
    print(f"N = {args.runs} runs por combate | Workers = {args.workers}\n")

    tasks = []
    for cid in CHECKPOINTS:
        for p_name, p_info in PARTIES.items():
            tasks.append((cid, p_name, p_info['roles'], args.runs, 42))

    matrix = {cid: {} for cid in CHECKPOINTS}
    
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init_worker) as executor:
        for item in executor.map(run_task, tasks):
            cid, p_name, m_old, m_new, v_old, v_new = item
            matrix[cid][p_name] = {
                'm_old': m_old, 'm_new': m_new,
                'v_old': v_old, 'v_new': v_new
            }
            print(f"[{cid}] {p_name}: Mod Old={m_old[0]:.0f}% -> Mod New={m_new[0]:.0f}% | Van Old={v_old[0]:.0f}% -> Van New={v_new[0]:.0f}%", flush=True)

    elapsed = time.time() - start_time
    print(f"\nBatería completada en {elapsed:.1f} segundos.")

    # Guardar resultados JSON
    out_json = os.path.join(BASE_DIR, 'scratch', 'battery_old_vs_new_ai_results.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(matrix, f, indent=2)
    print(f"Resultados guardados en: {out_json}")

if __name__ == '__main__':
    main()

"""E5. Is the sleep claim true? The real chance of each sleep skill on each story boss the variant opens to sleep:
the hit roll of the action (when it has one) times the ailment roll, for the members of the battery parties who know
the skill at that checkpoint, on the variant. Also lists which skills carry sleep, their classes and whether the action
goes through a hit roll first."""
import os
import sys
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_lib as A
from sim import formulas as f
from sim.battle import Battle, Action, AILMENT_RESIST
from sim.units import build_enemy
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
data, setup, variant = A.state()

print('skills of the player that carry sleep (effect 116), variant:')
sleepers = {}
for key, s in variant.skills.items():
    vals = [v for e, k, v in s.effects if e == 116]
    if vals and s.classes:
        fx = [e for e, _, _ in s.effects]
        roll = 'physical hit' if 0 in fx else ('magic hit' if (1 in fx or 25 in fx) else 'no hit roll')
        sleepers[key] = s
        v0 = [v for e, k, v in data.skills[key].effects if e == 116][0]
        print(f"  {key[0]} {key[1]} {s.name!r}: chance {v0[0]}..{v0[-1]} -> {vals[0][0]}..{vals[0][-1]}; {roll}; target {s.target}; "
              f"classes {[variant.class_names.get(c) for c in s.classes]}")

BOSSES = [('C10', 1002), ('C13', 760), ('C21', 1008), ('C25', 730), ('C26', 1010), ('C29a', 896), ('C32', 840),
          ('C33', 908), ('C36', 1015), ('C37', 865)]
print('\nreal chance per cast = hit roll x ailment roll, for the members of the battery parties who know a sleep skill')
for cid, eid in BOSSES:
    v, m = data.enemies[eid], variant.enemies[eid]
    line = [f"{cid:4} {m['name'][:20]:20} wind res {m['res_wind']:4} RES {m['res']:4} vanilla: {'immune' if 'sleep' in v['immune'] else 'open'}"]
    found = {}
    for pname, info in A.B.PARTIES.items():
        try:
            party = A.B.build_party_complete(variant, setup, info['roles'], cid)
        except Exception as exc:                      # a checkpoint the battery does not hold
            line.append(f'({pname}: {exc})')
            continue
        enemy = build_enemy(variant, eid)
        battle = Battle(variant, party, [enemy], random.Random(1))
        for u in party:
            if u.kind != 'member':
                continue
            for key, s in sleepers.items():
                lv = u.skills.get(key[1]) if hasattr(u, 'skills') and isinstance(u.skills, dict) else None
                if not lv:
                    continue
                action = Action(u, 'skill', s, lv)
                hit = battle.hit_chance(action, enemy)
                ail = max(0.0, f.ailment_chance(action.value(116), enemy.resistance(AILMENT_RESIST[116]))) / 100.0
                found[(u.role, s.name, lv)] = (hit, min(1.0, ail), hit * min(1.0, ail))
    if not found:
        line.append('| nobody in the five parties knows a sleep skill here')
    for (role, name, lv), (hit, ail, both) in sorted(found.items(), key=lambda kv: -kv[1][2])[:4]:
        line.append(f'| {role} {name} Lv{lv}: hit {hit:.0%} x ailment {ail:.0%} = {both:.0%}')
    print(' '.join(line))

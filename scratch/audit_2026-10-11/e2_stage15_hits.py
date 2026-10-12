"""E2a. What the Stage 15 buffs of common enemies (rows G034 - G093) do to one hit, by the formulas alone.
For each buffed common enemy: the mean damage of its strongest attack on each member of each battery party at the level
and gear of C40, vanilla against the variant, as a share of the member's max HP. No battle is played."""
import sys
import random
import os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import audit_lib as A
from sim.battle import Battle, Action
from sim.units import build_enemy
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

data, setup, variant = A.state()
BIG = (78, 296, 919)                       # Macha, Purski, Highway Star: HP x1.95, ATK and INT x1.69
SOME = (403, 841, 120, 189)                # Fafnir, Space Whale, Stheno, Leprechaun: x1.30
print('enemy stats vanilla -> variant')
for eid in BIG + SOME:
    v, m = data.enemies[eid], variant.enemies[eid]
    print(f"  {v['name']:14} L{v['level']} HP {v['hp']}->{m['hp']}  ATK {v['atk']}->{m['atk']}  INT {v['int']}->{m['int']}  weight {v['weight']:.2f}  habitat {v['habitat']}")


def strongest(source, enemy_id, member, party):
    enemy = build_enemy(source, enemy_id)
    battle = Battle(source, party, [enemy], random.Random(1))
    best = (0.0, 'plain attack')
    plain = battle.expected_damage(Action(enemy, 'attack'), member)
    best = (plain, 'plain attack')
    for aid in enemy.attacks:
        attack = source.attacks.get(aid)
        if attack is None:
            continue
        d = battle.expected_damage(Action(enemy, 'enemy', attack, 1), member)
        if d > best[0]:
            best = (d, attack.name)
    return best


for pname in ('Meta', 'Dual-Support', 'Mage-Heavy', 'Juggernaut', 'Anti-Meta'):
    roles = A.B.PARTIES[pname]['roles']
    pv = [u for u in A.B.build_party_complete(data, setup, roles, 'C40') if u.kind == 'member']
    pm = [u for u in A.B.build_party_complete(variant, setup, roles, 'C40') if u.kind == 'member']
    print(f'== {pname} at C40 (level {pv[0].level})')
    for eid in BIG + SOME[:2]:
        cells = []
        for uv, um in zip(pv, pm):
            dv, nv = strongest(data, eid, uv, pv)
            dm, nm = strongest(variant, eid, um, pm)
            cells.append(f"{uv.role[:9]:9} {100 * dv / uv.max_hp:3.0f}%->{100 * dm / um.max_hp:3.0f}% (x{dm / max(1.0, dv):.1f})")
        print(f"  {data.enemies[eid]['name']:13} " + ' | '.join(cells))
    print('  member DEF / RES / max HP (variant): ' + ', '.join(f"{u.role[:9]} {u.stat('def')}/{u.stat('res')}/{u.max_hp}" for u in pm))

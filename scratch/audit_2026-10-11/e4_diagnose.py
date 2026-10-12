"""E4. Why the cells that stay near 0% lose, on the variant: where the boss stands when the party falls, what is left
of the party's TP, how long it lasted, how hard the largest hit was."""
import sys
import random
import os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import audit_lib as A
from sim.units import ENEMIES
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
data, setup, variant = A.state()
CELLS = [('C40', 'Meta'), ('C40', 'Mage-Heavy'), ('C40', 'Juggernaut'), ('C40', 'Anti-Meta'), ('C38', 'Juggernaut'),
         ('C36', 'Anti-Meta'), ('C36', 'Juggernaut'), ('C30', 'Anti-Meta'), ('C26', 'Juggernaut'), ('C17', 'Juggernaut')]
N = 12
for cid, pname in CELLS:
    roles = A.B.PARTIES[pname]['roles']
    cp = setup.checkpoint(cid)
    res = A.scenario.play(variant, setup, lambda: A.B.build_party_complete(variant, setup, roles, cid),
                          lambda: [A.scenario.fixed_battle(variant, cp['Floor'], n) for n in A.scenario.battle_numbers(cp)],
                          runs=N, seed=42)
    wins = sum(r['won'] for r in res)
    lost = [r for r in res if not r['won']]
    line = f'{cid} {pname:12} wins {wins}/{N}'
    if lost:
        parts = [len(r['parts']) for r in lost]
        last = [r['parts'][-1] for r in lost]
        boss_left, dealt_share, tp, time_, hit, timeouts, member_actions, enemy_actions = [], [], [], [], [], 0, [], []
        for p in last:
            rec = p['record']
            enemies = [u for u in rec.actions if u.side == ENEMIES] or [u for u in rec.damage if u.side == ENEMIES]
            units = {u for t in (rec.damage, rec.actions, rec.deaths) for u in t}
            foes = [u for u in units if u.side == ENEMIES and u.kind == 'enemy']
            boss = max(foes, key=lambda u: u.max_hp) if foes else None
            if boss is not None:
                boss_left.append(max(0, boss.hp) / boss.max_hp)
            tp.append(p['tp_left'])
            time_.append(p['time'])
            if not p['lost']:
                timeouts += 1
            members = [u for u in units if u.side != ENEMIES and u.kind == 'member']
            member_actions.append(sum(rec.actions.get(u, 0) for u in members))
            enemy_actions.append(p['enemy_actions'])
            if rec.largest_hit and members:
                hit.append(max(rec.largest_hit.values()) / (sum(u.max_hp for u in members) / len(members)))
        avg = lambda xs: sum(xs) / len(xs) if xs else float('nan')
        line += (f' | losses: fell in fight {avg(parts):.1f} of {len(A.scenario.battle_numbers(cp))}; boss HP left {avg(boss_left):.0%}; '
                 f'party TP left {avg(tp):.0%}; length {avg(time_):.0f}; party actions {avg(member_actions):.0f} vs enemy {avg(enemy_actions):.0f}; '
                 f'largest single action on one member {avg(hit):.0%} of a mean max HP; timeouts {timeouts}')
    print(line)

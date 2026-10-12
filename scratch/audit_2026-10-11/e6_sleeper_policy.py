"""E6. What a player gets from the sleep the variant opens on bosses. The policy of the simulator hardly uses
ailments on bosses, so here one member of the party (the Sage with Sleep, else the member of the Maid line with
Lullaby, at skill level 5) casts sleep on the boss every time the boss is awake and she can pay; everybody else plays
the policy of the simulator unchanged (they hit the sleeping boss and wake it: no timing is exploited, so this is a
floor of what a player does).

Columns: vanilla with the plain policy, the variant with the plain policy, the variant with the sleeper.
For each: wins, share of the boss's turns lost to sleep, lowest HP of the party."""
import os
import sys
import json
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_lib as A
from sim import scenario, policy as P
from sim.battle import Action
from sim.units import ENEMIES

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
CIDS = ['C21', 'C25', 'C26', 'C29a', 'C32', 'C36', 'C37']
PARTIES = ['Meta', 'Mage-Heavy', 'Juggernaut', 'Anti-Meta']
SLEEP, LULLABY = ('Magic', 171), ('Magic', 205)
MAID_LINE = ('diva', 'maid', 'etoile', 'mistress')


class Sleeper(P.Policy):
    def __call__(self, battle, unit):
        action = self.sleep(battle, unit)
        return action if action is not None else super().__call__(battle, unit)

    @staticmethod
    def caster(battle):
        members = [u for u in battle.members() if u.alive]
        sage = [u for u in members if getattr(u, 'role', '') == 'sage']
        if sage:
            return sage[0], SLEEP
        maid = [u for u in members if getattr(u, 'role', '') in MAID_LINE]
        return (maid[0], LULLABY) if maid else (None, None)

    def sleep(self, battle, unit):
        who, key = self.caster(battle)
        if who is not unit or 117 in unit.statuses:
            return None
        foes = [t for t in P.enemies_of(battle, unit) if t.alive]
        if not foes:
            return None
        boss = max(foes, key=lambda t: t.max_hp)
        if 'sleep' in boss.immune or 116 in boss.statuses or battle.nullified(boss, 116):
            return None
        action = Action(unit, 'skill', battle.data.skills[key], 5)
        if unit.tp < action.tp_cost:
            return None
        action.target = boss
        return action


def cell(args):
    cid, pname, which, n = args
    data, setup, variant = A.state()
    source = data if which == 'vanilla' else variant
    roles = A.B.PARTIES[pname]['roles']
    cp = setup.checkpoint(cid)
    saved = scenario.Policy
    scenario.Policy = Sleeper if which == 'mod+sleeper' else P.Policy
    try:
        res = scenario.play(source, setup, lambda: A.B.build_party_complete(source, setup, roles, cid),
                            lambda: [scenario.fixed_battle(source, cp['Floor'], k) for k in scenario.battle_numbers(cp)],
                            runs=n, seed=42)
    finally:
        scenario.Policy = saved
    wins = sum(r['won'] for r in res)
    denied = acted = casts = 0
    for r in res:
        for part in r['parts']:
            rec = part['record']
            foes = [u for u in set(rec.actions) | set(rec.denied) if u.side == ENEMIES and u.kind == 'enemy']
            if not foes:
                continue
            boss = max(foes, key=lambda u: u.max_hp)
            denied += rec.denied.get(boss, 0)
            acted += rec.actions.get(boss, 0)
            casts += sum(v for (u, name), v in rec.skill_uses.items() if name in ('Sleep', 'Lullaby'))
    return cid, pname, which, {'wins': wins, 'n': len(res), 'denied': denied, 'acted': acted, 'casts': casts / len(res),
                               'lowest': sum(r['lowest_hp'] for r in res) / len(res)}


if __name__ == '__main__':
    tasks = [(c, p, w, N) for c in CIDS for p in PARTIES for w in ('vanilla', 'mod', 'mod+sleeper')]
    out = {}
    with ProcessPoolExecutor(max_workers=10) as ex:
        for cid, pname, which, r in ex.map(cell, tasks, chunksize=2):
            out.setdefault(cid, {}).setdefault(pname, {})[which] = r
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'e6_result.json'), 'w'), indent=1)
    print(f'N = {N}. wins | boss turns lost to its ailments, share of its turns | lowest HP of the party')
    print(f'{"":5}{"party":12}{"vanilla":>22}{"variant":>22}{"variant + sleeper":>26}   sleep casts per fight')
    for cid in CIDS:
        for pname in PARTIES:
            row = out[cid][pname]
            cells = []
            for w in ('vanilla', 'mod', 'mod+sleeper'):
                r = row[w]
                share = r['denied'] / max(1, r['denied'] + r['acted'])
                cells.append(f"{100 * r['wins'] / r['n']:4.0f}% | {share:4.0%} | {r['lowest']:4.0%}")
            print(f"{cid:5}{pname:12}{cells[0]:>22}{cells[1]:>22}{cells[2]:>26}   {row['mod+sleeper']['casts']:.1f}")

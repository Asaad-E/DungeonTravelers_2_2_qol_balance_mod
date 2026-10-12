"""Why a party of the battery loses at a boss, vanilla and variant: how the battles end, what the boss kills with,
and for each member what she does and how much TP she has left as the battle goes on.

    python boss_diagnosis.py CHECKPOINT PARTY [runs]
"""
import collections
import os
import random
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import scenario, setup as setup_mod                      # noqa: E402
from sim.battle import Battle                                     # noqa: E402
from sim.data import game_data                                    # noqa: E402
from sim.policy import Policy, load_rules                         # noqa: E402
from sim.variant import balance_data                              # noqa: E402

ACTION = re.compile(r'^\s*([\d.]+) (.+?) \((\d+)/(\d+) HP, (-?\d+) TP\): (.+)$')
HIT = re.compile(r'^\s+-> (.+?) takes (\d+).*?, (\d+)/')


def play(data, setup, cid, roles, runs):
    cp = setup.checkpoint(cid)
    policy = Policy(load_rules(setup.policies), setup.settings)
    ends, kills, boss_uses, hits = collections.Counter(), collections.Counter(), collections.Counter(), collections.defaultdict(list)
    acts = collections.defaultdict(collections.Counter)             # member -> action -> count
    tp = collections.defaultdict(lambda: [[], [], []])              # member -> TP share in each third of the battle
    dealt = collections.Counter()                                   # actor -> damage on the enemies
    lengths, left, max_tp = [], [], {}
    for k in range(runs):
        rng = random.Random(int(setup.settings['seed']) + k)
        party = scenario.party_of_roles(data, setup, cid, roles)
        groups = [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]
        enemies = groups[-1]                                         # the boss is the last battle of the checkpoint
        scenario.prepare(setup, party, enemies)
        foes = {u.name for u in enemies}
        label = {u.name: f"{u.name} ({getattr(u, 'role', u.kind)})" for u in party}
        for u in party:
            max_tp[label[u.name]] = max(1, u.max_tp)
        battle = Battle(data, party, enemies, rng, choose_member=policy, setup=dict(setup.settings),
                        zone=getattr(enemies, 'zone', None), max_time=float(setup.settings.get('max_time', 400)))
        battle.fixed = True
        battle.log = []
        result = battle.run()
        ends['won' if result['won'] else 'wiped' if result['lost'] else 'time ran out'] += 1
        lengths.append(result['time'])
        left.append(sum(u.hp for u in enemies if u.alive) / float(sum(u.max_hp for u in enemies)))
        actor = key = None
        for line in battle.log:
            m = ACTION.match(line)
            if m:
                when, actor, key = float(m.group(1)), m.group(2), m.group(6)
                if actor in foes:
                    boss_uses[key] += 1
                else:
                    if actor not in label:                       # a doll: it joins the battle after the start
                        label[actor] = f'{actor} (doll)'
                        max_tp[label[actor]] = 1
                    acts[label[actor]][key] += 1
                    third = min(2, int(3 * when / max(result['time'], 1e-9)))
                    tp[label[actor]][third].append(int(m.group(5)) / float(max_tp[label[actor]]))
                continue
            m = HIT.match(line)
            if not m:
                continue
            if actor in foes and m.group(1) in label:
                hits[key].append(int(m.group(2)))
                if int(m.group(3)) == 0:
                    kills[key] += 1
            elif actor in label and m.group(1) in foes:
                dealt[label[actor]] += int(m.group(2))
    print(f'  {dict(ends)}  mean time {sum(lengths) / runs:.1f}  boss HP left {sum(left) / runs:.0%}')
    print('  boss: ' + ', '.join(f'{k} {boss_uses[k] / runs:.1f} uses, mean hit {sum(v) / len(v):.0f}, kills {kills[k] / runs:.1f}'
                                 for k, v in sorted(hits.items(), key=lambda kv: -sum(kv[1]))[:6]))
    total = float(sum(dealt.values())) or 1.0
    for name in sorted(acts, key=lambda n: -dealt[n]):
        thirds = ' / '.join(f'{sum(t) / len(t):.0%}' if t else '-' for t in tp[name])
        top = ', '.join(f'{k} {v / runs:.1f}' for k, v in acts[name].most_common(5))
        print(f'    {name}: {dealt[name] / total:.0%} of the damage | TP by third {thirds} | {top}')


def main():
    cid, name = sys.argv[1], sys.argv[2]
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    roles = setup.battery[name][1]
    cp = setup.checkpoint(cid)
    foes = scenario.fixed_battle(variant, cp['Floor'], scenario.battle_numbers(cp)[-1])
    print(f"=== {cid} {name}: " + ', '.join(f'{u.name} lv{u.level} {u.max_hp} HP' for u in foes))
    print('  ' + ', '.join(f"{u.name} {getattr(u, 'role', u.kind)} lv{u.level} {u.max_hp}HP {u.max_tp}TP"
                           for u in scenario.party_of_roles(variant, setup, cid, roles)))
    for label, source in (('vanilla', data), ('variant', variant)):
        print(' ' + label)
        play(source, setup, cid, roles, runs)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

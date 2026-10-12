"""What decides C36 (Demon God Fried) for each party of the battery, vanilla and variant: how the battles end, and
which actions of the boss take the HP of the party.

    python c36_diagnosis.py [checkpoint] [runs]
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

ACTION = re.compile(r'^\s*[\d.]+ (.+?) \((\d+)/(\d+) HP, (-?\d+) TP\): (.+)$')
HIT = re.compile(r'^\s+-> (.+?) takes (\d+).*?, (\d+)/')


def play(data, setup, cid, roles, runs):
    cp = setup.checkpoint(cid)
    policy = Policy(load_rules(setup.policies), setup.settings)
    ends, taken, used, lengths, boss_hp = collections.Counter(), collections.Counter(), collections.Counter(), [], []
    kills, member_acts = collections.Counter(), collections.Counter()
    for k in range(runs):
        rng = random.Random(int(setup.settings['seed']) + k)
        party = scenario.party_of_roles(data, setup, cid, roles)
        enemies = scenario.fixed_battle(data, cp['Floor'], scenario.battle_numbers(cp)[0])
        scenario.prepare(setup, party, enemies)
        names = {u.name for u in enemies}
        members = {u.name for u in party}
        battle = Battle(data, party, enemies, rng, choose_member=policy, setup=dict(setup.settings),
                        zone=getattr(enemies, 'zone', None), max_time=float(setup.settings.get('max_time', 400)))
        battle.fixed = True
        battle.log = []
        result = battle.run()
        ends['won' if result['won'] else 'wiped' if result['lost'] else 'time ran out'] += 1
        lengths.append(result['time'])
        boss_hp.append(sum(u.hp for u in enemies if u.alive) / float(sum(u.max_hp for u in enemies)))
        actor, key = None, None
        for line in battle.log:
            m = ACTION.match(line)
            if m:
                actor, key = m.group(1), m.group(5)
                if actor in names:
                    used[key] += 1
                elif actor in members:
                    member_acts[key.split(' on ')[0].split(' -> ')[0]] += 1
                continue
            m = HIT.match(line)
            if m and actor in names and m.group(1) in members:
                taken[key] += int(m.group(2))
                if int(m.group(3)) == 0:
                    kills[key] += 1
    print('     killing blows: ' + ', '.join(f'{k} {v / runs:.1f}' for k, v in kills.most_common(6)))
    print('     party actions a battle: ' + ', '.join(f'{k} {v / runs:.1f}' for k, v in member_acts.most_common(14)))
    return ends, taken, used, sum(lengths) / len(lengths), sum(boss_hp) / len(boss_hp)


def main():
    cid = sys.argv[1] if len(sys.argv) > 1 else 'C36'
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    cp = setup.checkpoint(cid)
    for unit in scenario.fixed_battle(variant, cp['Floor'], scenario.battle_numbers(cp)[0]):
        print('ENEMY', unit.name, 'lv', unit.level, 'HP', unit.max_hp, {k: v for k, v in vars(unit).items() if k in ('stats', 'immune', 'passives')})
    for name, (_, roles) in setup.battery.items():
        party = [u for u in scenario.party_of_roles(variant, setup, cid, roles) if u.kind == 'member']
        print()
        print('==', name, '|', ', '.join(f'{u.name} {u.role} lv{u.level} {u.max_hp}HP' for u in party))
        for label, source in (('vanilla', data), ('variant', variant)):
            ends, taken, used, length, left = play(source, setup, cid, roles, runs)
            total = float(sum(taken.values())) or 1.0
            print(f'  {label}: {dict(ends)}  mean time {length:.1f}  boss HP left {left:.0%}')
            print('     damage taken by action: ' + ', '.join(f'{k} {v / total:.0%} ({used[k] / runs:.1f} uses)'
                                                               for k, v in taken.most_common(6)))


if __name__ == '__main__':
    main()

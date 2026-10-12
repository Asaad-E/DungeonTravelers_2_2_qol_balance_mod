"""What a role does in the last place of the reference party at a checkpoint, on the variant: her skills, what she
uses, her TP as the battle goes on, the damage of each kind of action. The party of tools/class_stages.py.

    python role_diagnosis.py CHECKPOINT ROLE [runs]
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


def main():
    cid, role = sys.argv[1], sys.argv[2]
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    setup = setup_mod.load()
    data = balance_data(game_data())
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}
    policy = Policy(load_rules(setup.policies), setup.settings)

    def party():
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        members = [u for u in whole if u.kind == 'member']
        others = [u for u in whole if u.kind != 'member']
        kept = members[:-1]
        names = [n.strip() for n in str(setup.roles[role]['Characters (order of preference)']).split(';')]
        taken = {u.name for u in kept}
        base = scenario.class_id(data, setup.roles[role]['Base class'])
        who = next((n for n in names if n in chars and n not in taken), None) or \
            next(c['name'] for c in data.characters if c['name'] not in taken and c['base_class'] == base)
        tested = scenario.build_role_member(data, setup, role, chars[who], level, gear, 0,
                                            scenario.forge_open(setup, cp['Floor']))
        for u in kept:
            tested.items = u.items
        return kept + [tested] + others, tested

    sample, tested = party()
    names = {s.id: s.name for s in data.skills.values()}
    print(f"=== {cid} {role}: {tested.name} lv{tested.level} {tested.max_hp}HP {tested.max_tp}TP | with "
          + ', '.join(getattr(u, 'role', u.kind) for u in sample if u is not tested))
    print('  skills: ' + ', '.join(f'{names.get(k, k)} {v}' for k, v in tested.skills.items()))
    print('  weapon: ' + str([getattr(p, 'get', lambda *_: None)('name') if isinstance(p, dict) else p
                              for p in getattr(tested, 'equipment', [])][:2]))
    wins, lengths = 0, []
    acts, dmg, hits, tp = collections.Counter(), collections.Counter(), collections.Counter(), [[], [], []]
    party_dmg = mine_dmg = 0
    for k in range(runs):
        rng = random.Random(int(setup.settings['seed']) + k)
        members, tested = party()
        result = None
        for n in scenario.battle_numbers(cp):
            enemies = scenario.fixed_battle(data, cp['Floor'], n)
            for unit in members:
                unit.statuses, unit.chant, unit.song, unit.dance = {}, None, [], []
            members = [u for u in members if u.kind in ('member', 'summon')]
            scenario.prepare(setup, members, enemies)
            foes = {u.name for u in enemies}
            battle = Battle(data, members, enemies, rng, choose_member=policy, setup=dict(setup.settings),
                            zone=getattr(enemies, 'zone', None), max_time=float(setup.settings.get('max_time', 400)))
            battle.fixed = True
            battle.log = []
            result = battle.run()
            actor = key = None
            for line in battle.log:
                m = ACTION.match(line)
                if m:
                    actor, key = m.group(2), m.group(6)
                    if actor == tested.name:
                        acts[key] += 1
                        tp[min(2, int(3 * float(m.group(1)) / max(result['time'], 1e-9)))].append(int(m.group(5)) / float(tested.max_tp))
                    continue
                m = HIT.match(line)
                if m and actor not in foes and m.group(1) in foes:
                    party_dmg += int(m.group(2))
                    if actor == tested.name:
                        mine_dmg += int(m.group(2))
                        dmg[key] += int(m.group(2))
                        hits[key] += 1
            if not result['won']:
                break
            scenario.recover_after_battle(members)
        wins += bool(result['won'])
        lengths.append(result['time'])
    print(f'  won {wins}/{runs}, mean length of the last battle {sum(lengths) / runs:.1f}, her own blows '
          f'{mine_dmg / float(party_dmg or 1):.0%} of the damage (her dolls apart)')
    print('  TP by third: ' + ' / '.join(f'{sum(t) / len(t):.0%}' if t else '-' for t in tp))
    for key, count in acts.most_common(8):
        per = f', {dmg[key] / count:.0f} damage a use' if dmg[key] else ''
        print(f'    {key}: {count / runs:.1f} a run{per}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

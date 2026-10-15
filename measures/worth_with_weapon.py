"""The worth of a strike that needs a weapon the role does not wear in the sheet Roles (rows F42, F73): the measure of
tools/skill_worth.py with the role's weapon changed for the trial, and beside it the best option of the role with her
usual weapon, to see what the change of weapon costs.

    python worth_with_weapon.py "Bible Thump" sage Tome
    python worth_with_weapon.py "Beast Binder" joker Whip
    (add --engine to score the options on the C# engine, engine_cs/)
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import class_stages                                       # noqa: E402
import skill_worth                                        # noqa: E402
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim import policy as P                               # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402


ENGINE = False                               # --engine: the battles are played by the C# engine


def contexts(data, setup, role, cid, policy):
    if ENGINE:
        return skill_worth.contexts_engine(data, setup, cid, role)
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    boss = scenario.fixed_battle(data, cp['Floor'], scenario.battle_numbers(cp)[-1])
    zones = [z for z in data.floors if z['name'].split(' zone')[0] == cp['Floor'] and z['formations']] or \
            [z for z in data.floors if z['name'][:4] == cp['Floor'][:4] and z['formations']]
    rng = random.Random(1)
    groups = [measures.random_group(data, rng.choice(zones), rng)
              for _ in range(int(setup.settings['skill_worth_groups']))] if zones else []
    member = skill_worth.full_member(data, setup, role, level, gear, cp)
    base = [u for u in scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
            if u.kind == 'member' and u.name != member.name][:4]
    out = [('boss', skill_worth.scores(data, setup, member, base + [member], boss, policy))]
    out += [('random', skill_worth.scores(data, setup, member, base + [member], g, policy)) for g in groups]
    return out


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    name, role, weapon = sys.argv[1:4]
    data, setup = balance_data(game_data()), setup_mod.load()
    policy = P.Policy(P.load_rules(setup.policies), setup.settings)
    usual = setup.roles[role]['Weapon']
    for st in class_stages.stages(setup):
        if st['Stage'] not in ('advanced', 'late'):
            continue
        for cid in [c.strip() for c in str(st['Checkpoints']).split(';')]:
            setup.roles[role]['Weapon'] = usual
            plain = contexts(data, setup, role, cid, policy)
            setup.roles[role]['Weapon'] = weapon
            trial = contexts(data, setup, role, cid, policy)
            for (ctx, a), (_, b) in zip(plain, trial):
                if name not in b:
                    print(cid, ctx, name, 'is not an option')
                    continue
                best_a, best_b = max(a, key=a.get), max(b, key=b.get)
                print(f'{cid} {ctx:6} {name} {b[name] / b[best_b]:.0%} of {best_b} (with a {weapon}); '
                      f'{b[name] / a[best_a]:.0%} of {best_a} (usual weapon)', flush=True)
    setup.roles[role]['Weapon'] = usual


if __name__ == '__main__':
    main()

import sys; sys.path.insert(0, 'mod_project')
from sim import data, setup, scenario, variant
from sim.battle import Battle
from sim.policy import Policy, load_rules
import random

d = data.game_data()
bd = variant.balance_data(d)
s = setup.load()

cid = 'C40'
cp = s.checkpoint(cid)
ref_levels = scenario.reference_levels(bd, s)
level = ref_levels[cid][0]
gear = scenario.checkpoint_gear(bd, s, cid)
numbers = scenario.battle_numbers(cp)

def party_factory():
    p = scenario.reference_party(bd, s, cp['Chapter'], level, gear, int(cp['Crown bonus'] or 0), cp['Floor'])
    role = 'attacker'
    rdata = s.roles[role]
    cname = rdata['Characters (order of preference)'].split(';')[0].strip()
    char = next(c for c in bd.characters if c['name'] == cname)
    u = scenario.build_role_member(bd, s, role, char, level, gear)
    p[4] = u
    return p

base_seed = int(s.settings['seed'])
options = dict(s.settings)
policy = Policy(load_rules(s.policies), s.settings)

for k_run in [2, 5, 7, 10, 11]: # Seeds for runs 3, 6, 8, 11, 12
    rng = random.Random(base_seed + k_run)
    party = party_factory()
    groups = [scenario.fixed_battle(bd, cp['Floor'], n) for n in numbers]
    print(f'=== SEED {base_seed + k_run} (Run {k_run + 1}) ===')
    for part_idx, enemies in enumerate(groups):
        for u in party:
            u.statuses, u.chant, u.song, u.dance = {}, None, [], []
        scenario.prepare(s, party, enemies)
        b = Battle(bd, party, enemies, rng, choose_member=policy, setup=options,
                   zone=getattr(enemies, 'zone', None), max_time=float(s.settings.get('max_time', 400)))
        reported = set()
        step_cnt = 0
        b.start()
        while not b.over() and b.time < b.max_time and b.actions < b.max_actions:
            unit = min((u for u in b.units if u.alive), key=lambda u: (u.next_time, u.position))
            b.time = unit.next_time
            b.turn(unit)
            step_cnt += 1
            for u in party:
                if not u.alive and u.name not in reported:
                    reported.add(u.name)
                    print(f'  Part {part_idx+1} act {step_cnt} (time {b.time:.1f}): {u.name} DIED! (role: {u.role}, killer acting: {unit.name})')
        res = b.result()
        if not res['won']:
            print(f'  LOST Part {part_idx + 1}!')
            break
        scenario.recover_after_battle(party)

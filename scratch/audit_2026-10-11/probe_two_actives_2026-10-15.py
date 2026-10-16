"""Why the audit of actives sees nothing of 34 Cleanse and 142 Heaven or Hell Effect: their records, their target and
what one perform of each does to every unit of the prepared battle of tools/sim_audit.py. Nothing is written."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'tools')]
import sim_audit                                            # noqa: E402

data = sim_audit.game_data()
for (cat, sid), s in data.skills.items():
    if sid in (34, 142) and cat in ('Technique', 'Magic'):
        print(sid, s.name, cat, 'effects', s.effects, 'target', getattr(s, 'target', None), 'levels', s.levels,
              'classes', s.classes)

import random                                               # noqa: E402
from sim.battle import Battle, Action, Status               # noqa: E402
from sim.units import build_enemy                           # noqa: E402
from sim import scenario                                    # noqa: E402
setup = sim_audit.setup_mod.load()
cp = setup.checkpoint(sim_audit.LATE[1])
gear = scenario.checkpoint_gear(data, setup, sim_audit.LATE[1])
skills = {sid: s for (cat, sid), s in data.skills.items() if sid in (34, 142) and cat in ('Technique', 'Magic')}
for sid, skill in skills.items():
    party = [u for u in scenario.reference_party(data, setup, cp['Chapter'], sim_audit.LATE[0], gear, 0, cp['Floor'])
             if u.kind == 'member'][:5]
    for u in party:
        u.hp, u.tp = max(1, u.max_hp // 2), 999
    party[1].statuses[113] = Status(113, 0, 3)
    party[1].statuses[116] = Status(116, 0, 3)
    foes = [build_enemy(data, sim_audit.ACTIVES_ENEMY, True)]
    b = Battle(data, party, foes, random.Random(1), setup=setup.settings)
    user = party[4]
    action = Action(user, 'skill', skill, skill.levels or 1)
    print(sid, 'target code', action.target_code, 'user', user.name)
    before = [(u.name, u.hp, sorted(u.statuses)) for u in b.units]
    b.perform(action)
    after = [(u.name, u.hp, sorted(u.statuses)) for u in b.units]
    for x, y in zip(before, after):
        print('  ', x, '->', y[1:], '' if x == y else 'CHANGED')

# again with what each needs to show: Cleanse aimed at the member with the ailments, the foe at half HP for the heal
for sid, skill in skills.items():
    party = [u for u in scenario.reference_party(data, setup, cp['Chapter'], sim_audit.LATE[0], gear, 0, cp['Floor'])
             if u.kind == 'member'][:5]
    for u in party:
        u.tp = 999
    party[1].statuses[113] = Status(113, 0, 3)
    party[1].statuses[116] = Status(116, 0, 3)
    foes = [build_enemy(data, sim_audit.ACTIVES_ENEMY, True)]
    foes[0].hp = foes[0].max_hp // 2
    b = Battle(data, party, foes, random.Random(1), setup=setup.settings)
    action = Action(party[4], 'skill', skill, skill.levels or 1)
    action.target = party[1] if sid == 34 else foes[0]
    before = [(u.name, u.hp, sorted(u.statuses)) for u in b.units]
    b.perform(action)
    print(sid, 'aimed')
    for x, u in zip(before, b.units):
        y = (u.name, u.hp, sorted(u.statuses))
        if x != y:
            print('  ', x, '->', y[1:])

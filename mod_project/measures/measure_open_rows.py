"""The skills of the register that had no measure (rows F22, F42, F52, F73): each played by the reference party with
and without it, as tools/skill_value.py does, at the checkpoints of the stage where its class is played. Bible Thump
needs a tome, so the Sage wears one for its measure; Support Shot is a passive, so no rule is added for it.

    python measure_open_rows.py "Roulette Circus"      one skill; writes open_rows_<skill>.json beside this file
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import skill_value                                        # noqa: E402
from sim import setup as setup_mod                        # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

WEAPON = {'Bible Thump': 'Tome'}
ROLE = {'Support Shot': 'shooter'}
STAGE = {'Support Shot': 'advanced'}


def main():
    name = sys.argv[1]
    data, setup = balance_data(game_data()), setup_mod.load()
    skill = next(s for s in data.skills.values() if s.name == name and s.classes)
    if name in ROLE:
        role = ROLE[name]
        st = next(s for s in skill_value.class_stages.stages(setup) if s['Stage'] == STAGE[name])
    else:
        role, st = skill_value.place(data, setup, skill)
    if name in WEAPON:
        setup.roles[role]['Weapon'] = WEAPON[name]
    passive = skill.category == 'Passive'
    rule = skill_value.rule_for
    out = {'skill': name, 'role': role, 'stage': st['Stage'], 'cells': []}
    for cid in [c.strip() for c in str(st['Checkpoints']).split(';')]:
        cell = {'checkpoint': cid}
        for use in (False, True):
            if passive and use:
                # a passive needs no rule: the one added is a copy of the role's own damage rule, placed just before it
                own = next(r for r in sorted((r for r in setup.policies if r['Role'] == role), key=lambda r: r['Order'])
                           if str(r['Action']).startswith('damage'))
                skill_value.rule_for = lambda s, own=own: (own['Condition'], own['Action'])
            try:
                cell['with' if use else 'without'] = skill_value.play(data, setup, role, cid, skill, use)
            finally:
                skill_value.rule_for = rule
        out['cells'].append(cell)
        print(name, role, cell, flush=True)
    with open(os.path.join(HERE, 'open_rows_' + name.replace(' ', '_') + '.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()

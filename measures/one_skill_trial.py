"""What one skill adds: the member of a role in the last place of the reference party, without the skill and with it
at its top level, at the bosses given. A skill used in battle gets the rule tools/skill_value.py gives it; a passive
gets none. Balance variant; nothing is written.

    python measures/one_skill_trial.py mistress Ecstasy C26;C30;C36;C38;C40 150
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))

_STATE = {}


def cell(task):
    role, name, cid, use, runs = task
    import skill_value
    from sim import setup as setup_mod
    from sim.data import game_data
    from sim.variant import balance_data
    if not _STATE:
        _STATE.update(data=balance_data(game_data()), setup=setup_mod.load())
    data, setup = _STATE['data'], _STATE['setup']
    setup.settings = dict(setup.settings, check_runs=runs)
    skill = next(s for s in data.skills.values() if s.name == name)
    if skill.category == 'Passive':
        kept, skill_value.rule_for = skill_value.rule_for, lambda s: ('ally_down', 'revive')
        try:
            res = skill_value.play(data, setup, role, cid, skill, use)
        finally:
            skill_value.rule_for = kept
    else:
        res = skill_value.play(data, setup, role, cid, skill, use)
    return cid, use, res


def main():
    role, name, bosses, runs = sys.argv[1], sys.argv[2], sys.argv[3].split(';'), int(sys.argv[4])
    with ProcessPoolExecutor(12) as pool:
        at = {(c, u): r for c, u, r in pool.map(cell, [(role, name, c, u, runs) for c in bosses for u in (False, True)])}
    print(f'{name} ({role}), {runs} battles: without > with | wins | length of the won fights | HP left')
    for c in bosses:
        a, b = at[(c, False)], at[(c, True)]
        length = f"{a['time_won']:.1f} > {b['time_won']:.1f}" if a['time_won'] and b['time_won'] else '-'
        print(f"{c} | {a['won']:.0%} > {b['won']:.0%} | {length} | {a['hp_left']:.0%} > {b['hp_left']:.0%}")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

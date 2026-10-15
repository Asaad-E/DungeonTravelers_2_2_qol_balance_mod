"""What lowering the DEF of a boss is worth: a physical party with an Etoile who keeps Alluring Samba up (raised first,
in place of Dumbing Mazurka), in the game and on the variant, against the same party with her usual dances. Defence
modifiers add with no floor (docs/FORMULAS.md 2.3), so the last case gives Samba the size of Samba and Armor
Penetration together, as if both were kept up. Nothing is written.

    python measures/def_debuff_trial.py C30;C36;C38;C40 150 [processes]
    (add --engine to play the cells on the C# engine, engine_cs/)
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))

PARTIES = {'Physical': ['tank', 'attacker', 'dark lord', 'etoile', 'diva'],
           'Meta, Etoile for Papillon': ['valkyrie', 'dark lord', 'treasure hunter', 'etoile', 'diva']}
CASES = ('game, usual dances', 'game, Samba', 'variant, usual dances', 'variant, Samba', 'variant, Samba of the game',
         'variant, Samba + Armor Penetration')
SAMBA, PIERCE, DEF_DOWN, USUAL = 'Alluring Samba', 'Armor Penetration', 196, ('status:195', 'status:201')
ENGINE = False                               # --engine: the battles are played by the C# engine
_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod
        from sim.data import game_data
        from sim.variant import balance_data
        vanilla = game_data()
        _STATE.update(vanilla=vanilla, variant=balance_data(vanilla), setup=setup_mod.load())
    return _STATE


def skill(data, name):
    return next(s for s in data.skills.values() if s.name == name)


def values(data, name, effect):
    return next(list(v) for e, _, v in skill(data, name).effects if e == effect)


def cell(task):
    party, cid, case, runs = task
    from sim import scenario
    state = _load()
    setup = state['setup']
    data = state['vanilla'] if case.startswith('game') else state['variant']
    samba = skill(data, SAMBA)
    kept = (samba.effects, setup.policies, setup.roles['etoile'])
    if 'Samba' in case:
        size = values(data, SAMBA, DEF_DOWN)
        if 'of the game' in case:
            size = values(state['vanilla'], SAMBA, DEF_DOWN)
        elif PIERCE in case:
            size = [a + values(data, PIERCE, 162)[-1] for a in size]
        samba.effects = [(e, k, size if e == DEF_DOWN else v) for e, k, v in samba.effects]
        first, second = [r for r in setup.policies if r['Role'] == 'etoile' and str(r['Action']) in USUAL]
        setup.policies = [dict(r, Action=f'status:{DEF_DOWN}') if r is first else dict(r, Action=USUAL[0]) if r is second else r
                          for r in setup.policies]
        setup.roles['etoile'] = dict(kept[2], **{'Skill priority': SAMBA + '; ' + str(kept[2]['Skill priority'])})
    try:
        res = (__import__('engine_client').play_party_sim if ENGINE else scenario.play_party)(data, setup, cid, PARTIES[party], runs)
        level = scenario.allocate_skills(data, setup.roles['etoile'], scenario.reference_levels(data, setup)[cid][0]).get(samba.id, 0)
    finally:
        samba.effects, setup.policies, setup.roles['etoile'] = kept
    won = [r for r in res if r['won']]
    return party, cid, case, len(won) / len(res), sum(r['time'] for r in won) / len(won) if won else 0, level


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    bosses, runs = sys.argv[1].split(';'), int(sys.argv[2])
    tasks = [(p, c, k, runs) for p in PARTIES for c in bosses for k in CASES]
    with (__import__('engine_client').SerialPool() if ENGINE else ProcessPoolExecutor(int(sys.argv[3]) if len(sys.argv) > 3 else 12)) as pool:
        at = {(p, c, k): (w, t, lv) for p, c, k, w, t, lv in pool.map(cell, tasks)}
    for p in PARTIES:
        print(p, PARTIES[p])
        for k in CASES:
            print(f'  {k:36s} ' + ' | '.join(f'{c} {at[(p, c, k)][0]:.0%} ({at[(p, c, k)][1]:.0f}t, Samba {at[(p, c, k)][2]})'
                                              for c in bosses))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

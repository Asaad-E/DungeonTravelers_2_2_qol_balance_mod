"""A trial of a small cut to the Dark Lord and the Valkyrie (the user, 2026-10-12): the power of every strike only the
Dark Lord learns and the values of every skill only the Valkyrie learns, times a factor, and what the Meta party and
the two roles alone (the reference party with the role in its last place) then win. Nothing is written.

    python meta_nerf_trial.py C40 0.9 [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

CROWN = {'P06': 0, 'P23': 20, 'P27': 40, 'P52': 0, 'P54': 0}
POWER = 26                       # the power of a strike
GUARDS = (171, 180, 183, 161, 162)   # Cover, Parry, Spell Guard, War Cry, Protect
USED = {'Power Charge': (191,), 'Geo Break': (POWER,), 'Frost Slash': (POWER,), 'Raging Smash': (POWER,),
        'Cover': (171,), 'Parry': (180,), 'War Cry': (161,), 'Berserk': (26, 41)}


def cut(data, factor):
    names = {v: k for k, v in data.class_names.items()}
    lord, valkyrie = names['Dark Lord'], names['Valkyrie']
    changes, touched = [], []
    for key, s in data.skills.items():
        if key[0] == 'Passive' or not s.classes:
            continue
        only = set(s.classes)
        if s.name in USED:                               # the skills the two roles use, shared with other classes or not
            wanted = USED[s.name]
        elif only == {lord}:
            wanted = (POWER,)
        elif only == {valkyrie}:
            wanted = (POWER,) + GUARDS
        else:
            continue
        if any(e in wanted for e, _, _ in s.effects):
            changes.append(('skills', key, 'effects', [(e, k, [v * factor for v in vals] if e in wanted else vals)
                                                       for e, k, vals in s.effects]))
            touched.append(s.name)
    return data.with_changes(changes), touched


def main():
    cid, factor = sys.argv[1], float(sys.argv[2])
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    setup = setup_mod.load()
    variant = balance_data(game_data())
    lower, touched = cut(variant, factor)
    cp = setup.checkpoint(cid)
    if cid in CROWN:
        cp['Crown bonus'] = CROWN[cid]
    print(cid, 'skills cut:', ', '.join(sorted(set(touched))), flush=True)
    for name in ('Meta', 'Dual-Support', 'Juggernaut-Plus'):
        roles = setup.battery[name][1]
        cells = []
        for source in (variant, lower):
            def party():
                return scenario.party_of_roles(source, setup, cid, roles)

            def enemies():
                return [scenario.fixed_battle(source, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

            res = measures.summary(scenario.play(source, setup, party, enemies, runs=runs))
            cells.append(f"{res['won']:.0%} / {res.get('time') or 0:.1f}")
        print(f'{cid} | {name} | {cells[0]} | {cells[1]}', flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

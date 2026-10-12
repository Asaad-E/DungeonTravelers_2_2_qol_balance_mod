"""Condition R04 of the sheet Regression (no new mandatory piece): at every boss of the battery, for every class, a
party without that class that reaches the floor of the boss.

    python regression_r04.py witnesses          from the battery as it stands (docs/generated/party_battery): the pairs
                                                of boss and class that every winning party holds, vanilla and variant
    python regression_r04.py play k/n [runs]    for those pairs, the parties of the battery with the role of that class
                                                changed for each role of SUBSTITUTES, until one reaches the floor;
                                                writes regression_r04_k.json beside this file
    python regression_r04.py report             REGRESSION_R04.md beside this file
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

BATTERY = os.path.join(PROJECT, 'docs', 'generated', 'party_battery')
# the roles tried in the place of a role whose class every winning party holds: its neighbours of the same job
SUBSTITUTES = {'diva': ('etoile', 'mistress', 'healer', 'sage'), 'maid': ('etoile', 'mistress', 'healer', 'sage'),
               'tank': ('attacker', 'dark lord', 'kunoichi'), 'valkyrie': ('attacker', 'dark lord', 'kunoichi'),
               'dark lord': ('attacker', 'shooter', 'kunoichi'), 'healer': ('sage', 'diva', 'etoile'),
               'treasure hunter': ('shooter', 'kunoichi', 'attacker'), 'papillon': ('joker', 'kunoichi', 'attacker')}


def classes_of(data, setup, cid, roles):
    level = scenario.reference_levels(data, setup)[cid][0]
    return {role: data.class_names.get(scenario.class_path(data, setup.roles[role], level)[0]) for role in roles}


def floors(setup, ids):
    return {c: float(setup.settings[f"guide_{setup.guide_difficulty.get(c, 'normal')}_min_won"]) for c in ids}


def battery_rows():
    rows = []
    for name in glob.glob(os.path.join(BATTERY, 'part_*.json')):
        with open(name, encoding='utf-8') as f:
            rows += json.load(f)
    return rows


def lacking(data, setup):
    """[(boss, side, class, roles that hold it in the winning parties)] where no winning party lacks the class."""
    rows = battery_rows()
    ids = sorted({r['id'] for r in rows})
    floor = floors(setup, ids)
    out = []
    for cid in ids:
        for side in ('vanilla', 'variant'):
            winners = []
            for r in rows:
                if r['id'] == cid and r[side]['wins'] / r[side]['runs'] >= floor[cid]:
                    roles = [m.split('(')[1].rstrip(')') for m in r[side]['members']]
                    winners.append((r['party'], classes_of(data, setup, cid, roles)))
            every = {c for _, held in winners for c in held.values()}
            for cls in sorted(every):
                if all(cls in held.values() for _, held in winners):
                    out.append((cid, side, cls, sorted({role for _, held in winners for role, c in held.items() if c == cls}),
                                [name for name, _ in winners]))
    return out


def witnesses():
    data, setup = game_data(), setup_mod.load()
    found = lacking(data, setup)
    for cid, side, cls, roles, winners in found:
        print(cid, side, cls, roles, 'winning parties:', ', '.join(winners))
    print(len(found), 'pairs of boss and class without a witness in the battery')


def play(part, runs=60):
    k, n = (int(x) for x in part.split('/'))
    vanilla, setup = game_data(), setup_mod.load()
    variant = balance_data(vanilla)
    found = [f for f in lacking(vanilla, setup)]
    floor = floors(setup, {f[0] for f in found})
    out = []
    for cid, side, cls, _, winners in found[(k - 1) * len(found) // n: k * len(found) // n]:
        source = vanilla if side == 'vanilla' else variant
        cp = setup.checkpoint(cid)
        best = None
        for name in winners:
            roles = list(setup.battery[name][1])
            held = classes_of(source, setup, cid, roles)
            mine = [r for r in roles if held[r] == cls]
            for new in SUBSTITUTES.get(mine[0], ()) if mine else ():
                trial = [new if r in mine else r for r in roles]
                if cls in classes_of(source, setup, cid, trial).values() or len(set(trial)) < len(trial):
                    continue

                def party():
                    return scenario.party_of_roles(source, setup, cid, trial)

                def enemies():
                    return [scenario.fixed_battle(source, cp['Floor'], b) for b in scenario.battle_numbers(cp)]

                units = party()
                if cls in {source.class_names.get(getattr(u, 'class_id', None)) for u in units}:
                    continue                                  # a fallback member brought the class back
                won = measures.summary(scenario.play(source, setup, party, enemies, runs=int(runs)))['won']
                if best is None or won > best[0]:
                    best = (won, f'{name} with {new} for {mine[0]}')
                if won >= floor[cid]:
                    break
            if best and best[0] >= floor[cid]:
                break
        out.append({'id': cid, 'side': side, 'class': cls, 'floor': floor[cid], 'won': best[0] if best else None,
                    'party': best[1] if best else None})
        print(cid, side, cls, best, flush=True)
    with open(os.path.join(HERE, f'regression_r04_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def report():
    rows = []
    for name in glob.glob(os.path.join(HERE, 'regression_r04_*.json')):
        with open(name, encoding='utf-8') as f:
            rows += json.load(f)
    rows.sort(key=lambda r: (r['id'], r['side'], r['class']))
    count = {side: (sum(1 for r in rows if r['side'] == side and r['won'] is not None and r['won'] >= r['floor']),
                    sum(1 for r in rows if r['side'] == side)) for side in ('vanilla', 'variant')}
    lines = ['# Regression R04: no mandatory class (generated by measures/regression_r04.py)', '',
             'The pairs of boss and class that every winning party of the battery holds, and the best party found without '
             'that class (the role changed for a neighbour of the same job).', '',
             f"**A party without the class reaches the floor at {count['variant'][0]} of {count['variant'][1]} such pairs "
             f"on the variant, {count['vanilla'][0]} of {count['vanilla'][1]} in vanilla.**", '',
             '| Boss | Side | Class | Floor | Best party without it | Wins |', '|---|---|---|---|---|---|']
    for r in rows:
        won = '-' if r['won'] is None else f"{r['won']:.0%}"
        mark = '' if r['won'] is not None and r['won'] >= r['floor'] else ' **below**'
        lines.append(f"| {r['id']} | {r['side']} | {r['class']} | {r['floor']:.0%} | {r['party'] or 'none could be built'} | {won}{mark} |")
    with open(os.path.join(HERE, 'REGRESSION_R04.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print(lines[4])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'witnesses': witnesses, 'play': play, 'report': report}[sys.argv[1]](*sys.argv[2:])

"""
The battery of parties: each party of the sheet BatteryParties of data_tables/sim_setup.xlsx against each story boss of
Settings battery_checkpoints, in vanilla and on the Balance variant. Generated: docs/generated/PARTY_BATTERY.md.

    python tools/party_battery.py all [processes]      every party at every boss
    python tools/party_battery.py only C26;C30 [processes]     again, the bosses a change touched
    python tools/party_battery.py report

Same parties, same seeds and same policy on both sides (docs/SIMULATOR_AI_BENCHMARK_PHILOSOPHY.md), Settings
battery_runs battles a cell. A party is built by sim/scenario.py party_of_roles: its roles at the reference level and
gear of the checkpoint; a place nobody can fill goes to a member who has joined, so the party is full whenever five
characters have joined, and the whole party shares one bag. Several parties of one archetype count as one: the
archetype has the best figure among them.

The report gives each win share with its 95% interval (Wilson) and sets it against the floor of the class the guide
gives the boss (sheet GuideDifficulty, Settings guide_<class>_min_won): the least share a party that works should win.
"""
import json
import math
import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'party_battery')
REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'PARTY_BATTERY.md')

from sim import scenario                                 # noqa: E402
from sim import setup as setup_mod                       # noqa: E402
from sim.data import game_data                           # noqa: E402
from sim.variant import balance_data                     # noqa: E402

Z95 = 1.96


def checkpoints(setup):
    return [c.strip() for c in str(setup.settings['battery_checkpoints']).split(';') if c.strip()]


def wilson(wins, runs):
    """The 95% interval of a share of wins out of runs."""
    if not runs:
        return 0.0, 1.0
    p, z2 = wins / runs, Z95 * Z95
    centre = (p + z2 / (2 * runs)) / (1 + z2 / runs)
    half = Z95 * math.sqrt(p * (1 - p) / runs + z2 / (4 * runs * runs)) / (1 + z2 / runs)
    return max(0.0, centre - half), min(1.0, centre + half)


def cell(source, setup, cid, roles, runs):
    results = scenario.play_party(source, setup, cid, roles, runs)
    won = [r for r in results if r['won']]
    party = [u for u in scenario.party_of_roles(source, setup, cid, roles) if u.kind == 'member']
    return {'runs': len(results), 'wins': len(won),
            'time': sum(r['time'] for r in won) / len(won) if won else None,
            'lowest_hp': sum(r['lowest_hp'] for r in results) / len(results),
            'tp_left': sum(r['tp_left'] for r in won) / len(won) if won else None,
            'members': [f'{u.name} ({u.role})' for u in party]}


def run(part='1/1', only=None):
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    runs = int(setup.settings['battery_runs'])
    wanted = [c.strip() for c in only.split(';')] if only else checkpoints(setup)
    tasks = [(cid, name) for cid in wanted for name in setup.battery]
    rows = []
    for cid, name in tasks[k - 1::n]:
        roles = setup.battery[name][1]
        rows.append({'id': cid, 'party': name, 'vanilla': cell(data, setup, cid, roles, runs),
                     'variant': cell(variant, setup, cid, roles, runs)})
        print(cid, name, flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    # a part of "only" is read after the parts of "all" (load sorts the names) and takes the place of their cells
    with open(os.path.join(OUT_DIR, f"{'update' if only else 'part'}_{k}.json"), 'w', encoding='utf-8') as f:
        json.dump(rows, f)


def run_all(processes=None, only=None):
    setup = setup_mod.load()
    n = int(processes or setup.settings.get('parallel_workers', 1))
    for name in os.listdir(OUT_DIR) if os.path.isdir(OUT_DIR) else []:
        if name.startswith('update_') or not only:
            os.remove(os.path.join(OUT_DIR, name))
    started = time.time()
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'run', f'{k}/{n}'] + ([only] if only else []),
                              stdout=subprocess.DEVNULL) for k in range(1, n + 1)]
    for p in procs:
        p.wait()
    print(f'{n} parts in {time.time() - started:.0f} s')


def run_only(only, processes=None):
    run_all(processes, only)


def load():
    rows = []
    for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
        with open(os.path.join(OUT_DIR, name), encoding='utf-8') as f:
            rows += json.load(f)
    return {(r['id'], r['party']): r for r in rows}


def archetypes(setup):
    found = {}
    for name, (archetype, _) in setup.battery.items():
        found.setdefault(archetype, []).append(name)
    return found


def best(rows, cid, names, side):
    """The cell of the party of an archetype that wins most at this boss on this side."""
    return max((rows[(cid, n)][side] for n in names if (cid, n) in rows), key=lambda c: c['wins'] / c['runs'])


def share(c):
    return c['wins'] / c['runs']


def report():
    data, setup = game_data(), setup_mod.load()
    rows = load()
    if not rows:
        print('no parts: run "all" first')
        return
    groups = archetypes(setup)
    every = [c for c in checkpoints(setup) if any((c, n) in rows for n in setup.battery)]
    runs = next(iter(rows.values()))['vanilla']['runs']
    floor = {c: float(setup.settings[f"guide_{setup.guide_difficulty.get(c, 'normal')}_min_won"]) for c in every}
    boss = {c['ID']: c['Boss (as the story page names it)'] for c in setup.checkpoints}
    names = {}
    for cp in setup.checkpoints:
        if cp['ID'] in every:
            ids = [e for n in scenario.battle_numbers(cp) for b in data.fixed
                   if b['floor'] == cp['Floor'] and b['number'] == n for e, _ in b['enemies']]
            names[cp['ID']] = max((data.enemies[e] for e in ids), key=lambda e: e['hp'])['name']
    above = {side: sum(1 for c in every for a in groups if share(best(rows, c, groups[a], side)) >= floor[c])
             for side in ('vanilla', 'variant')}
    cells = len(every) * len(groups)
    width = wilson(runs // 2, runs)
    lines = ['# The battery of parties (generated)', '',
             'Generated by `tools/party_battery.py`. Do not edit. Parties: sheet `BatteryParties` of `sim_setup.xlsx`; '
             f'bosses: Settings `battery_checkpoints`; {runs} battles a cell, the same seeds in vanilla and on the '
             f'variant. At {runs} battles a share near 50% is known to about {100 * (width[1] - width[0]) / 2:.0f} '
             'points either way (95%). Floor: the least win share the class the guide gives the boss allows.', '',
             f"**Archetype and boss pairs at or above the floor: {above['vanilla']} of {cells} in vanilla, "
             f"{above['variant']} of {cells} on the variant.**", '',
             '## Archetypes: win share, vanilla > variant', '',
             'An archetype with several parties shows the best of them on each side. **Bold**: the variant is below the '
             'floor.', '',
             '| Checkpoint | Boss | Floor | ' + ' | '.join(groups) + ' |', '|---|---|---|' + '---|' * len(groups)]
    for c in every:
        parts = []
        for a in groups:
            v, m = best(rows, c, groups[a], 'vanilla'), best(rows, c, groups[a], 'variant')
            text = f'{share(v):.0%} > {share(m):.0%}'
            parts.append(f'**{text}**' if share(m) < floor[c] else text)
        lines.append(f'| {c} | {names.get(c, boss.get(c, ""))} | {floor[c]:.0%} | ' + ' | '.join(parts) + ' |')
    lines += ['', '## Every party on the variant: win share and its 95% interval', '',
              '| Checkpoint | ' + ' | '.join(setup.battery) + ' |', '|---|' + '---|' * len(setup.battery)]
    for c in every:
        parts = []
        for n in setup.battery:
            m = rows[(c, n)]['variant']
            low, high = wilson(m['wins'], m['runs'])
            parts.append(f'{share(m):.0%} ({low:.0%} - {high:.0%})')
        lines.append(f'| {c} | ' + ' | '.join(parts) + ' |')
    lines += ['', '## Every party in vanilla: win share', '',
              '| Checkpoint | ' + ' | '.join(setup.battery) + ' |', '|---|' + '---|' * len(setup.battery)]
    for c in every:
        lines.append(f'| {c} | ' + ' | '.join(f"{share(rows[(c, n)]['vanilla']):.0%}" for n in setup.battery) + ' |')
    lines += ['', '## Who stands in each party', '',
              'The first and the last boss of the battery where five members have joined.', '',
              '| Party | Checkpoint | Members (role) |', '|---|---|---|']
    full = [c for c in every if all(len(rows[(c, n)]['variant']['members']) >= 5 for n in setup.battery)]
    for n in setup.battery:
        for c in ([full[0], full[-1]] if full else every[:1]):
            lines.append(f"| {n} | {c} | {', '.join(rows[(c, n)]['variant']['members'])} |")
    short = [(c, n, len(rows[(c, n)]['variant']['members'])) for c in every for n in setup.battery
             if len(rows[(c, n)]['variant']['members']) < 5]
    if short:
        lines += ['', 'Fewer than five characters have joined at: ' +
                  ', '.join(sorted({f'{c} ({k} members)' for c, _, k in short})) + '.']
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(lines[4])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'run': run, 'all': run_all, 'only': run_only, 'report': report}[sys.argv[1]](*sys.argv[2:])

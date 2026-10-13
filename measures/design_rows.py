"""Figures for the rows of the register that were closed on a reading of the design (J17, J35, J36, F95, S14, S16,
S19), each by the test its row names, from the data of the game and the simulator. The game as it is, not the variant.

    python measures/design_rows.py            writes DESIGN_ROWS.md beside this file
"""
import collections
import os
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import win_rates                                          # noqa: E402

TRUTH = os.path.join(PROJECT, 'data_tables', 'vanilla_source_of_truth.xlsx')
NO_MAGIC, DOWN = 2, (5, 6)
RESTORE = {62, 63, 64, 72}                # item effect types of a meal that restore HP or TP or cure (docs/FORMULAS.md 15)
# F95: the same party with and without the Treasure Hunter
SWAPS = {'Meta': 'valkyrie; dark lord; treasure hunter; papillon; diva',
         'Meta, an attacker in her place': 'valkyrie; dark lord; attacker; papillon; diva',
         'Dual-Support': 'tank; dark lord; shooter; healer; diva',
         'Dual-Support, she in the place of the shooter': 'tank; dark lord; treasure hunter; healer; diva'}
_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod
        from sim.data import game_data
        _STATE.update(data=game_data(), setup=setup_mod.load())
    return _STATE


def sheet(name):
    rows = list(openpyxl.load_workbook(TRUTH, read_only=True)[name].iter_rows(values_only=True))
    return [dict(zip(rows[0], r)) for r in rows[1:]]


def spike(task):
    """J17: the largest damage one enemy action does to one member, against the max HP of the frailest member."""
    cid, runs = task
    from sim import scenario
    state = _load()
    data, setup = state['data'], state['setup']
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)

    def party():
        return scenario.reference_party(data, setup, cp['Chapter'], level, gear, int(cp['Crown bonus'] or 0), cp['Floor'])

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    members = [u for u in party() if u.kind == 'member']
    frail, mean = min(u.max_hp for u in members), sum(u.max_hp for u in members) / len(members)
    res = scenario.play(data, setup, party, enemies, runs=runs)
    hits = [max([h for part in r['parts'] for h in part['record'].largest_hit.values()] or [0]) for r in res]
    return cid, statistics.median(hits) / frail, max(hits) / frail, statistics.median(hits) / mean, sum(r['won'] for r in res) / len(res)


def no_magic_cell(task):
    """F95: a party with no Treasure Hunter at a boss that stands in an anti-magic zone."""
    party, cid, runs = task
    from sim import scenario
    state = _load()
    roles = [r.strip() for r in (SWAPS.get(party) or win_rates.PARTIES[party][0]).split(';')]
    res = scenario.play_party(state['data'], state['setup'], cid, roles, runs)
    return party, cid, sum(r['won'] for r in res) / len(res)


def zones(out):
    import map_data
    maps = map_data.maps()
    floors = _load()['data'].floors
    count = collections.Counter()
    shares = collections.defaultdict(list)
    for name, m in maps.items():
        cells = m['cells']
        for label, wanted in (('no magic', {NO_MAGIC}), ('lowers an attack', set(DOWN))):
            hit = sum(1 for c in cells if wanted & set(c['slots']))
            if hit:
                count[label] += 1
                shares[label].append(hit / len(cells))
    down = sorted({round(f['zone_factors'][k], 2) for f in floors for k in ('down_a', 'down_b') if f.get('zone_factors')})
    out += ['## S14 Harmful map zones', '',
            f'Of the {len(maps)} floors of the game, {count["no magic"]} have cells that forbid magic and '
            f'{count["lowers an attack"]} have cells that lower physical or magic attack. Where a floor has them they cover '
            f'a median of {statistics.median(shares["no magic"]):.0%} (no magic) and '
            f'{statistics.median(shares["lowers an attack"]):.0%} (lowered attack) of all the cells of its map, walls '
            f'counted, at most {max(shares["no magic"]):.0%} and {max(shares["lowers an attack"]):.0%}. A lowering zone '
            f'multiplies attack by {down[0]} to {down[-1]} for both sides (docs/FORMULAS.md 2.5).', '']


def forging(out):
    data = _load()['data']
    eq = sheet('Equipment')
    plain = [e for e in eq if e['Upgrade_Rate']]
    fixed = [e for e in eq if not e['Upgrade_Rate']]
    weapons = [e for e in plain if e['Category'] == 'Weapon' and e['ATK']]
    step = sorted(e['Upgrade_Rate'] / e['ATK'] for e in weapons)
    by_dungeon = {}
    for f in data.floors:
        top = max((hi for p in f['equipment'] for lo, hi in p['levels'].values()), default=0)
        by_dungeon[f['dungeon']] = max(by_dungeon.get(f['dungeon'], 0), top)
    top_level = max(by_dungeon.values())
    out += ['## J35 Forging, S16 Forged pieces against unique ones', '',
            f'{len(plain)} of the {len(eq)} pieces of equipment take upgrade levels ({len(weapons)} of them weapons with ATK, '
            f'none with an enchantment of its own); the other {len(fixed)} are fixed pieces with '
            f'{min(e["Enchant_Count"] for e in fixed)} to {max(e["Enchant_Count"] for e in fixed)} enchantments and no upgrade. '
            f'Each level adds `int(level * rate)` to every stat the piece has (docs/FORMULAS.md 10.1): for a weapon '
            f'{step[0]:.1%} to {step[-1]:.1%} of its base ATK a level, median {statistics.median(step):.1%}. The highest level a '
            f'zone gives is {top_level}.', '',
            '| Weapon type | Best piece that takes levels | Its ATK at +0 | at the top level | Best fixed piece | Its ATK |',
            '|---|---|---|---|---|---|']
    kinds = collections.defaultdict(dict)
    for e in eq:
        if e['Category'] == 'Weapon' and e['ATK']:
            key = 'plain' if e['Upgrade_Rate'] else 'fixed'
            if key not in kinds[e['Type_Code']] or e['ATK'] > kinds[e['Type_Code']][key]['ATK']:
                kinds[e['Type_Code']][key] = e
    above = pairs = 0
    for kind, found in sorted(kinds.items()):
        if 'plain' in found and 'fixed' in found:
            p, f = found['plain'], found['fixed']
            forged = p['ATK'] + int(top_level * p['Upgrade_Rate'])
            pairs += 1
            above += forged > f['ATK']
            out.append(f"| {kind} | {p['Name']} | {p['ATK']} | {forged} | {f['Name']} | {f['ATK']} |")
    out += ['', f'At the top level the plain piece has more ATK than the best fixed one in {above} of {pairs} weapon types. '
            'What an upgrade level costs in gold is in the program and was not read.', '']


def economy(out):
    data = _load()['data']
    items = {i['Name']: i for i in sheet('Items')}
    by = collections.defaultdict(list)
    for f in data.floors:
        if len(f['formations']) < 2:
            continue
        total = sum(max(1, x['chance']) for x in f['formations'])
        gold = sum(max(1, x['chance']) * sum(data.enemies[e]['gold'] for e, _ in x['enemies'] if e in data.enemies)
                   for x in f['formations']) / total
        by[f['dungeon']].append(gold)
    out += ['## S19 Early economy', '', 'Gold of one random battle, the mean over the formations of each zone by their chance, '
            'by dungeon in the order of the files:', '', '| Dungeon | Gold a battle (lowest zone - highest) |', '|---|---|']
    for dungeon in sorted(by)[:6]:
        out.append(f'| {dungeon} | {min(by[dungeon]):.0f} - {max(by[dungeon]):.0f} |')
    cheap = [items[n] for n in ('Croissant', 'Danish', 'Egg Sandwich', 'Gateau Au Chocolat') if n in items]
    out += ['', 'Shop prices: ' + ', '.join(f"{i['Name']} {i['Buy_Price']}" for i in cheap) + '. A piece sells for a third of '
            'its price. The prices of equipment are not decoded.', '']


def meals(out):
    food = sheet('FoodMenu')
    buffs = [m for m in food if any(m.get(f'Eff{k}_ID') is not None and m[f'Eff{k}_ID'] not in RESTORE for k in range(1, 6))]
    out += ['## J36 Meals', '',
            f'{len(food)} meals; {len(food) - len(buffs)} only restore HP or TP or cure, at once; {len(buffs)} also give a buff '
            '(a skill performed at a fixed level, tools/item_effect_data.py). How many steps such a buff lasts outside a battle '
            'is in the program and was not read, so the test of the row (steps a meal lasts against steps to the boss) is '
            'not answered.', '']


def main():
    state = _load()
    data, setup = state['data'], state['setup']
    from sim import scenario
    story = [c['ID'] for c in setup.checkpoints if str(c['ID']).startswith('C')]
    walled = [c['ID'] for c in setup.checkpoints
              if any((scenario.battle_zone(data, c['Floor'], n) or {}).get('no_magic') for n in scenario.battle_numbers(c))]
    parties = [p for p, (roles, _, _) in win_rates.PARTIES.items() if 'treasure hunter' not in roles]
    with ProcessPoolExecutor(12) as pool:
        spikes = list(pool.map(spike, [(c, 30) for c in story]))
        won = {(p, c): w for p, c, w in pool.map(no_magic_cell, [(p, c, 100) for p in parties + list(SWAPS) for c in walled])}
    out = ['# Figures for the rows closed on a reading of the design (generated by measures/design_rows.py)', '',
           'The game as it is. Each section answers the test its row of the register names.', '']
    over = [s for s in spikes if s[2] >= 1]
    usual = [s for s in spikes if s[1] >= 1]
    out += ['## J17 Area damage spikes', '',
            f'The reference party at the {len(spikes)} boss fights of the story, 30 battles each, guards and Cover played as '
            f'its policy has them. The largest damage one enemy action did to one member, against the max HP of the frailest '
            f'member: at least once above her whole HP in {len(over)} fights, and in the median battle in {len(usual)} '
            f'({", ".join(s[0] for s in usual)}). The action may be an area attack or several hits on one member.', '',
            '| Boss | Median largest hit / HP of the frailest | Largest seen | Median / mean HP of the party | Wins |',
            '|---|---|---|---|---|']
    out += [f'| {c} | {a:.0%} | {b:.0%} | {m:.0%} | {w:.0%} |' for c, a, b, m, w in spikes if b >= 0.75]
    out += ['', 'Fights where no hit reached 75% of her HP are left out of the table.', '']
    out += ['## F95 Anti-magic bosses', '',
            f'Boss fights that stand on a cell that forbids magic: {", ".join(walled)}. Share of wins of the parties with no '
            'Treasure Hunter, 100 battles:', '', '| Party | ' + ' | '.join(walled) + ' |', '|---|' + '---|' * len(walled)]
    out += [f'| {p} | ' + ' | '.join(f'{won[(p, c)]:.0%}' for c in walled) + ' |' for p in parties]
    out += ['', 'The same party with and without her:', '', '| Party | ' + ' | '.join(walled) + ' |', '|---|' + '---|' * len(walled)]
    out += [f'| {p} | ' + ' | '.join(f'{won[(p, c)]:.0%}' for c in walled) + ' |' for p in SWAPS]
    out.append('')
    zones(out)
    forging(out)
    economy(out)
    meals(out)
    with open(os.path.join(HERE, 'DESIGN_ROWS.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

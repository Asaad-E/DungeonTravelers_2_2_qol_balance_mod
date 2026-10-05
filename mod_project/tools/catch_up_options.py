"""
Evaluation of the ways to let a member who is behind catch up, and of the crown. Nothing is changed in the game.

    python mod_project/tools/catch_up_options.py

Writes docs/generated/CATCH_UP_OPTIONS.md. Every option is defined in the sheet CatchUpOptions of
data_tables/balance_criteria.xlsx (so it can be edited and run again), and is computed with the rules of
sim/progression.py on the vanilla enemies, zones and table of EXP per level.

Kinds of option:
    vanilla     nothing changed
    curve       EXP needed per level multiplied by a factor that goes through the given (level, factor) points
    steep       EXP needed per level AND EXP of every enemy multiplied by rate ** (level - from_level): the pace of
                a member on level stays what it is, a member below the zone rises faster
    piece       the member wears a piece with Double EXP
    gap         the eight factors by level gap of the program replaced (the only kind that patches the program)
Any option may also give a curve in the column Curve; it is applied on top of its kind.
"""
import os
import statistics
import sys

import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
import enemy_data                      # noqa: E402
import floor_data                      # noqa: E402
from sim import progression            # noqa: E402

TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
OUTPUT_PATH = os.path.join(BASE_DIR, 'docs', 'generated', 'CATCH_UP_OPTIONS.md')
PARTY = 5
CHECKPOINTS = (20, 30, 40, 50, 60, 70, 80, 90)
NEAR = 4                               # "with the party" = within this many levels: the gap the program does not reward
FLOAT_EXACT = 2 ** 24                  # above this a 32-bit float no longer holds every integer


def rows_of(name, sheet):
    ws = openpyxl.load_workbook(os.path.join(TABLES_DIR, name), read_only=True)[sheet]
    it = ws.iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it if r and r[0] is not None]


def numbers(text):
    return [float(x) for x in str(text).replace(';', ',').split(',') if x.strip()]


def interpolate(points, level):
    """Factor at a level from (level, factor) points, straight between them and flat outside."""
    points = sorted(points)
    if level <= points[0][0]:
        return points[0][1]
    for (l0, f0), (l1, f1) in zip(points, points[1:]):
        if level <= l1:
            return f0 + (f1 - f0) * (level - l0) / float(l1 - l0)
    return points[-1][1]


class Option:
    def __init__(self, row):
        self.name, self.kind, self.note = row['Option'], row['Kind'], row['Note'] or ''
        values = numbers(row['Values']) if row['Values'] is not None else []
        self.step_factor = lambda level: 1.0
        self.enemy_factor = lambda level: 1.0
        self.options = {}
        self.gap_table = None
        if self.kind == 'curve':
            points = list(zip(values[0::2], values[1::2]))
            self.step_factor = lambda level: interpolate(points, level)
        elif self.kind == 'steep':
            rate, start = values[0], int(values[1])
            self.step_factor = self.enemy_factor = lambda level: rate ** max(0, level - start)
        elif self.kind == 'piece':
            self.options = {'double_exp_piece': True}
        elif self.kind == 'gap':
            self.gap_table = tuple((low, high, values[k], max(values[k], with_enchant))
                                   for k, (low, high, _, with_enchant) in enumerate(progression.LEVEL_GAP))
            self.options = {'gap_table': self.gap_table}
        elif self.kind != 'vanilla':
            raise ValueError(f'kind of option: {self.kind}')
        if row.get('Curve'):                       # any option can also carry a curve of EXP per level
            curve = numbers(row['Curve'])
            points, own = list(zip(curve[0::2], curve[1::2])), self.step_factor
            self.step_factor = lambda level: own(level) * interpolate(points, level)

    def steps(self, vanilla_steps):
        return {level: step * self.step_factor(level) for level, step in vanilla_steps.items()}

    def formations(self, zone, by_id):
        return [(f['chance'], [(by_id[e]['level'], by_id[e]['exp'] * self.enemy_factor(by_id[e]['level'])) for e, _ in f['enemies']])
                for f in zone['formations']]

    def battles(self, start, target, zone, vanilla_steps, by_id, living=PARTY):
        return progression.battles_to_reach(start, target, self.steps(vanilla_steps), self.formations(zone, by_id),
                                            living=living, **self.options)


def table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '---|' * len(headers)]
    return out + ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]


def main():
    enemies = enemy_data.enemies()
    by_id = {e['id']: e for e in enemies}
    vanilla_steps = {r['Level']: r['Req_EXP'] for r in rows_of('vanilla_source_of_truth.xlsx', 'ExpCurve')}
    zones = floor_data.floors()
    mean_level = lambda z: sum(f['chance'] * statistics.mean(by_id[e]['level'] for e, _ in f['enemies']) for f in z['formations']) / 100.0
    zone_exp = lambda z: sum(f['chance'] * sum(by_id[e]['exp'] for e, _ in f['enemies']) for f in z['formations']) / 100.0
    on_level = {level: min(zones, key=lambda z: (abs(mean_level(z) - level), z['name'])) for level in CHECKPOINTS}
    options = [Option(r) for r in rows_of('balance_criteria.xlsx', 'CatchUpOptions') if r['Kind']]      # rows without a kind are notes

    lines = ['# Catching up and the crown: options compared (generated)', '',
             'Generated by `tools/catch_up_options.py` from the sheet `CatchUpOptions` of `balance_criteria.xlsx`. '
             'Do not edit: change the sheet and run the tool again. Nothing here is applied to the game.', '',
             f'Random battles with {PARTY} members alive, in the zone whose enemies are closest to the level of the party, with no '
             'other EXP bonus. Bosses, quests and what the party gains meanwhile are left out.', '',
             '## The options', '']
    lines += table(['Option', 'Kind', 'What it is'], [[o.name, o.kind, o.note] for o in options])

    for behind in (10, 20):
        lines += ['', f'## A member {behind} levels behind: battles until it is within {NEAR} levels of the party', '']
        rows = []
        for level in CHECKPOINTS:
            start = max(1, level - behind)
            rows.append([level, on_level[level]['name']]
                        + [f'{o.battles(start, level - NEAR, on_level[level], vanilla_steps, by_id):.0f}' for o in options])
        lines += table(['Party level', 'Zone'] + [o.name for o in options], rows)

    lines += ['', '## A member at level 1: battles until it is within ' + f'{NEAR} levels of the party', '']
    rows = [[level, on_level[level]['name']] + [f'{o.battles(1, level - NEAR, on_level[level], vanilla_steps, by_id):.0f}' for o in options]
            for level in CHECKPOINTS]
    lines += table(['Party level', 'Zone'] + [o.name for o in options], rows)

    lines += ['', '## What each option does to a party that is on level', '',
              '"Own pace" is the battles one more level costs a member on level in its zone. "A zone above" is the EXP a battle '
              'gives a party that fights in the zone 7 and 12 levels above its own, as a multiple of what vanilla gives there: '
              'above 1 the option pays for running ahead of the curve.', '']
    rows = []
    for o in options:
        pace = [o.battles(level, level + 1, on_level[level], vanilla_steps, by_id) for level in (30, 50, 70, 90)]
        ahead = []
        for jump in (7, 12):
            level = 40
            zone = min(zones, key=lambda z: (abs(mean_level(z) - (level + jump)), z['name']))
            gain = lambda option: sum(c / 100.0 * progression.battle_exp(level, e, PARTY, **option.options) for c, e in option.formations(zone, by_id))
            # in units of the option's own cost of a level, against vanilla in units of vanilla's
            ahead.append((gain(o) / o.steps(vanilla_steps)[level + 1]) / (gain(options[0]) / vanilla_steps[level + 1]))
        total = sum(o.steps(vanilla_steps)[l] for l in range(2, 100))
        top_enemy = max(e['exp'] * o.enemy_factor(e['level']) for e in enemies)
        rows.append([o.name] + [f'{p:.0f}' for p in pace] + [f'{a:.2f}' for a in ahead]
                    + [f'{total:,.0f}', f'{top_enemy:,.0f}', 'no' if max(total, top_enemy * 1.75) < FLOAT_EXACT else '**yes**'])
    lines += table(['Option', 'Own pace at 30', 'at 50', 'at 70', 'at 90', 'A zone 7 above (party level 40)', '12 above',
                    'EXP from level 1 to 99', 'Largest EXP of one enemy', f'Passes {FLOAT_EXACT:,}'], rows)
    lines += ['', f'The last column matters because the result of a battle handles EXP as 32-bit floats (`0x445964 - 0x445a29`): above '
              f'{FLOAT_EXACT:,} not every integer exists, so small gains would be rounded. Vanilla stays far below it.']

    best = max(zones, key=lambda z: (zone_exp(z), z['name']))
    crowns = []
    for r in rows_of('balance_criteria.xlsx', 'CrownOptions'):
        if r['Steps']:
            pairs = [part.split(':') for part in str(r['Steps']).split(',')]
            crowns.append((r['Rule'], tuple(sorted(((int(a), int(b)) for a, b in pairs), reverse=True)), int(r['Cap']), r['Note'] or ''))
    lines += ['', '## The crown', '',
              f'A crown is the full bonus of the level resets (`docs/FORMULAS.md` 10). One member is raised from level 1 in the zone that gives '
              f'most EXP ({best["name"]}, enemies around level {mean_level(best):.0f}), carried by four members who stay alive, and reset as '
              'many times as the rule asks. For every rule and option the table gives the cheapest way: battles in all, and in brackets '
              'the level to reset from and how many resets.', '',
              '### The rules compared', '']
    lines += table(['Rule', 'Points for the levels given up', 'Cap', 'What it is'],
                   [[name, ', '.join(f'{levels}+: {points}' for levels, points in steps), cap, note] for name, steps, cap, note in crowns])
    lines += ['', '### Battles for one crown', '']
    rows = []
    for o in options:
        climb = {}
        level, total = 1, 0.0
        step_table, forms = o.steps(vanilla_steps), o.formations(best, by_id)
        for target in range(2, 100):                      # one pass: cost of reaching every level from 1
            total += progression.battles_to_reach(target - 1, target, step_table, forms, living=PARTY, **o.options)
            climb[target] = total
        row = [o.name]
        for _, steps, cap, _ in crowns:
            choices = [(progression.resets_to_crown(lv, steps, cap) * climb[lv], lv, progression.resets_to_crown(lv, steps, cap))
                       for lv in range(2, 100) if progression.resets_to_crown(lv, steps, cap)]
            cost, lv, resets = min(choices)
            row.append(f'{cost:,.0f} ({resets} from {lv})')
        rows.append(row)
    lines += table(['Option'] + [name for name, _, _, _ in crowns], rows)
    lines += ['', 'The rules of the crown are in the program (lever L27): every rule but the first is a patch of single bytes.', '']
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {OUTPUT_PATH}: {len(options)} options')


if __name__ == '__main__':
    main()

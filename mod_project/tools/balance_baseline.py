"""
Vanilla figures for the Balance work, generated. Nothing in the Balance documents is typed by hand.

    python mod_project/tools/balance_baseline.py

Writes mod_project/docs/generated/BALANCE_BASELINE.md from:
    backups/ClassLevelData.pck              growth of every class and route (tools/class_data.py)
    backups/Dungeon/stNN/Data.pck           random formations of every floor (tools/floor_data.py)
    backups/Enemy/Enemy.pck                 enemies (tools/enemy_data.py) and their behaviour (tools/enemy_ai.py)
    data_tables/qol_skill_text.xlsx         the box of every skill, itself generated from the binary and
                                            checked against it by the build
    data_tables/balance_criteria.xlsx       which skills the complaints and the guide speak of

Rule of the user (2026-10-05): vanilla figures written by hand get fixed in one revision and broken in the
next. The documents hold decisions; the figures are regenerated here.
"""
import os
import statistics
import collections
import openpyxl
import class_data
import enemy_ai
import enemy_data
import floor_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
OUTPUT_PATH = os.path.join(BASE_DIR, 'docs', 'generated', 'BALANCE_BASELINE.md')
BANDS = ((1, 14), (15, 29), (30, 49), (50, 69), (70, 84), (85, 98), (99, 99))    # class changes at 15 and 30
STATS = ('hp', 'atk', 'def', 'int', 'res', 'dex', 'agi', 'exp', 'gold')
ELEMENTS = enemy_data.RESISTANCES[3:]
PHYSICAL = enemy_data.RESISTANCES[:3]


def rows_of(path, sheet):
    ws = openpyxl.load_workbook(path, read_only=True)[sheet]
    it = ws.iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it]


def table(headers, rows):
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '---|' * len(headers)]
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return out


def number(v):
    return f'{v:,.0f}' if abs(v) >= 100 else f'{v:g}'


def enemy_sections(enemies):
    lines = ['## Enemies', '', f'{len(enemies)} entries of `Enemy.pck`. Medians per level band.', '']
    rows = []
    for lo, hi in BANDS:
        group = [e for e in enemies if lo <= e['level'] <= hi]
        if not group:
            continue
        rows.append([f'{lo}-{hi}' if lo != hi else str(lo), len(group)]
                    + [number(statistics.median(e[s] for e in group)) for s in STATS]
                    + [number(statistics.median(max(e['res_' + k] for k in PHYSICAL) for e in group)),
                       number(statistics.median(max(e['res_' + k] for k in ELEMENTS) for e in group)),
                       number(statistics.median(min(e['res_' + k] for k in ELEMENTS) for e in group)),
                       f"{statistics.median(e['weight'] for e in group):.2f}"])
    lines += table(['Level', 'Enemies'] + [s.upper() if s not in ('exp', 'gold') else s.capitalize() for s in STATS]
                   + ['Highest physical resistance', 'Highest elemental resistance', 'Lowest elemental resistance', 'Weight (turn order)'], rows)
    lines += ['', '### The 40 enemies with most HP', '']
    top = sorted(enemies, key=lambda e: (-e['hp'], e['id']))[:40]
    lines += table(['Enemy', 'Habitat', 'Lv', 'HP', 'ATK', 'DEF', 'INT', 'RES', 'DEX', 'AGI', 'EXP', 'Slash', 'Stab', 'Bash',
                    'Fire', 'Water', 'Wind', 'Earth', 'Lightning', 'Swing', 'Weight', 'Attacks'],
                   [[e['name'], e['habitat'], e['level'], number(e['hp']), e['atk'], e['def'], e['int'], e['res'], e['dex'], e['agi'],
                     number(e['exp'])] + [e['res_' + k] for k in enemy_data.RESISTANCES]
                    + [f"{e['swing']:.2f}", f"{e['weight']:.2f}", len(e['attacks'])] for e in top])
    lines += ['', '### Resistances of enemies of level 85 and above', '']
    late = [e for e in enemies if e['level'] >= 85]
    rows = []
    for key in enemy_data.RESISTANCES:
        values = [e['res_' + key] for e in late]
        rows.append([key.capitalize(), number(statistics.median(values)), min(values), max(values),
                     sum(v >= 100 for v in values), sum(v <= 0 for v in values)])
    lines += table(['Resistance', 'Median', 'Lowest', 'Highest', 'Enemies at 100 or more', 'Enemies at 0 or less'], rows)
    all_100 = [e['name'] for e in late if all(e['res_' + k] >= 100 for k in ELEMENTS)]
    lines += ['', f"Enemies of level 85+ with 100 or more in all five elements: {len(all_100)} of {len(late)}"
              + (' (' + ', '.join(sorted(set(all_100))) + ').' if all_100 else '.')]
    return lines


def skill_sections():
    criteria = rows_of(os.path.join(TABLES_DIR, 'balance_criteria.xlsx'), 'Criticisms')
    skills = {}
    for r in rows_of(os.path.join(TABLES_DIR, 'qol_skill_text.xlsx'), 'Skills'):
        skills.setdefault(r['Skill_Name'], r)
    named = collections.OrderedDict()
    for c in criteria:
        if c['Scope'] == 'Skill' and c['Subject'] in skills:
            named.setdefault(c['Subject'], []).append(c['ID'])
    lines = ['## Skills named by the complaints and by the guide', '',
             'The box of each skill as the QoL variant shows it: every figure is read from the binary and checked by the build.', '']
    rows = []
    for name, ids in named.items():
        s = skills[name]
        box = (s['QoL_LvUp'] or s['Vanilla_LvUp'] or '').replace('|', '/').replace('\n', '<br>')
        rows.append([name, s['Category'], ', '.join(ids), (s['Vanilla_Desc'] or '').replace('\n', ' '), box])
    lines += table(['Skill', 'Kind', 'Criticism', 'Sentence of the game', 'Values'], rows)
    missing = sorted({c['Subject'] for c in criteria if c['Scope'] == 'Skill' and c['Subject'] not in skills})
    if missing:
        lines += ['', 'Named in the register but not found under that name among the skills: ' + ', '.join(missing) + '.']
    return lines


def behaviour_sections(enemies):
    scripts = [enemy_ai.decode(e['ai']) for e in enemies]
    conditions, targets, sets = collections.Counter(), collections.Counter(), collections.Counter()
    for script in scripts:
        sets[len(script['sets'])] += 1
        seen = set()
        for command in enemy_ai.commands_of(script):
            if command['cmd'] == enemy_ai.TARGET:
                targets[command['args'][1]] += 1
            else:
                text = enemy_ai.COMMANDS[command['cmd']]
                if command['cmd'] in enemy_ai.USES_SOURCE:
                    text = text.replace('source', enemy_ai.SOURCES[command['args'][0]])
                seen.add(text)
        conditions.update(seen)
    lines = ['## Enemy behaviour', '',
             f'{len(scripts)} scripts of `EnemyAIData.bin`, decoded by `tools/enemy_ai.py`.', '',
             '### Sets of attack weights per enemy', '']
    lines += table(['Sets', 'Enemies'], sorted(sets.items()))
    lines += ['', '### Conditions (enemies whose script uses each)', '']
    lines += table(['Condition', 'Enemies'], sorted(conditions.items(), key=lambda kv: (-kv[1], kv[0])))
    lines += ['', '### Target changes written in the scripts', '',
              'Any other single target on the party is the weighted roll of `docs/FORMULAS.md` 9.', '']
    lines += table(['Target', 'Commands'], [[name, targets.get(kind, 0)] for kind, name in enumerate(enemy_ai.TARGETS)])
    return lines


GROWTH_LEVELS = (1, 15, 30, 50, 70, 99)


def class_sections():
    names, growth = class_data.class_names(), class_data.growth()
    lines = ['## Growth of the classes', '',
             'Stats of each class and route before any bonus (`ClassLevelData`; the row is chosen as `docs/FORMULAS.md` 10 reads).']
    for level in GROWTH_LEVELS:
        lines += ['', f'### Level {level}', '']
        rows = [[class_data.route_name(class_id, previous, names)] + [growth[row][level - 1][k] for k in class_data.STATS]
                for class_id, previous, row in class_data.routes()]
        lines += table(['Class'] + [k.upper() for k in class_data.STATS], rows)
    return lines


def floor_sections(enemies):
    by_id = {e['id']: e for e in enemies}
    floors = floor_data.floors()
    lines = ['## Random formations per floor', '',
             f"{sum(len(f['formations']) for f in floors)} formations on {len(floors)} floors. Every figure of a floor is "
             'weighted by the chance of each formation (the chances of a floor add up to 100).', '']
    rows = []
    for floor in floors:
        forms = floor['formations']
        mean = lambda value: sum(f['chance'] * value(f) for f in forms) / 100.0
        levels = [by_id[e]['level'] for f in forms for e, _ in f['enemies']]
        total = lambda key: (lambda f: sum(by_id[e][key] for e, _ in f['enemies']))
        rows.append([floor['floor'], len(forms), f"{mean(lambda f: len(f['enemies'])):.1f}",
                     max(len(f['enemies']) for f in forms), f'{min(levels)}-{max(levels)}',
                     number(mean(total('hp'))), number(mean(total('exp'))), number(mean(total('gold'))),
                     f"{100 * mean(lambda f: sum(not front for _, front in f['enemies']) / len(f['enemies'])):.0f}%"])
    lines += table(['Floor', 'Formations', 'Enemies per battle', 'Most enemies', 'Enemy levels', 'HP per battle',
                    'EXP per battle', 'Gold per battle', 'Enemies in the back row'], rows)
    seen = {e for floor in floors for f in floor['formations'] for e, _ in f['enemies']}
    lines += ['', f'{len(seen)} of the {len(enemies)} enemies appear in a random formation; the others are placed by events.']
    return lines


def main():
    enemies = enemy_data.enemies()
    lines = ['# Balance baseline (generated)', '',
             'Generated by `tools/balance_baseline.py`. Do not edit: run the tool again.',
             'Every figure here is read from the game files; none is typed.', '']
    lines += class_sections() + [''] + enemy_sections(enemies) + [''] + floor_sections(enemies) + [''] + behaviour_sections(enemies) + [''] + skill_sections() + ['']
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {OUTPUT_PATH}: {len(lines)} lines')


if __name__ == '__main__':
    main()

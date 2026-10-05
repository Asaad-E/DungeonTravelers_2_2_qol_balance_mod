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
import sys
import openpyxl
import character_data
import class_data
import class_modifier_data
import doll_data
import random_move_data
import skill_tree_data
import enemy_ai
import enemy_data
import floor_data
import summon_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from sim import progression
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
    lines += ['', '### Enemies that cannot receive an ailment, by level band', '',
              'From the flag of each enemy (one bit per ailment, tested by the code of that ailment).', '']
    ailments = list(enemy_data.IMMUNITY_BITS.values())
    rows = []
    for lo, hi in BANDS:
        group = [e for e in enemies if lo <= e['level'] <= hi]
        if group:
            rows.append([f'{lo}-{hi}' if lo != hi else str(lo), len(group)]
                        + [f"{100 * sum(a in e['immune'] for e in group) / len(group):.0f}%" for a in ailments])
    lines += table(['Level', 'Enemies'] + [a.capitalize() for a in ailments], rows)
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
    lines = ['## Random formations per zone', '',
             f"{sum(len(f['formations']) for f in floors)} formations in {len(floors)} zones of {len({f['floor'] for f in floors})} floors "
             '(a floor has one to seven zones, each with its own table). Every figure of a zone is weighted by the chance '
             'of each formation (the chances of a zone add up to 100).', '']
    rows = []
    for floor in floors:
        forms = floor['formations']
        mean = lambda value: sum(f['chance'] * value(f) for f in forms) / 100.0
        levels = [by_id[e]['level'] for f in forms for e, _ in f['enemies']]
        total = lambda key: (lambda f: sum(by_id[e][key] for e, _ in f['enemies']))
        rows.append([floor['name'], len(forms), f"{mean(lambda f: len(f['enemies'])):.1f}",
                     max(len(f['enemies']) for f in forms), f'{min(levels)}-{max(levels)}',
                     number(mean(total('hp'))), number(mean(total('exp'))), number(mean(total('gold'))),
                     f"{100 * mean(lambda f: sum(not front for _, front in f['enemies']) / len(f['enemies'])):.0f}%"])
    lines += table(['Zone', 'Formations', 'Enemies per battle', 'Most enemies', 'Enemy levels', 'HP per battle',
                    'EXP per battle', 'Gold per battle', 'Enemies in the back row'], rows)
    seen = {e for floor in floors for f in floor['formations'] for e, _ in f['enemies']}
    fixed = floor_data.fixed_battles()
    in_fixed = {e for battle in fixed for e, _ in battle['enemies']}
    events = sorted((e for e in enemies if e['id'] not in seen), key=lambda e: (e['level'], e['habitat'], e['id']))
    loose = sorted({e['name'] for e in events if e['id'] not in in_fixed})
    lines += ['', f'{len(seen)} of the {len(enemies)} enemies appear in a random formation. The other {len(events)} are placed by events; '
              f'{len(events) - len(loose)} of them stand in the fixed battles below'
              + (f' and {len(loose)} in none ({", ".join(loose)}).' if loose else '.'), '',
              '### Fixed battles (bosses, quest targets)', '',
              f'{len(fixed)} battles the events of a floor start, read from the same floor files.', '']
    label = lambda e, front: f"{by_id[e]['name']} L{by_id[e]['level']}" + ('' if front else ' (back)')
    lines += table(['Floor', 'Battle', 'Enemies', 'HP in all', 'Highest level'],
                   [[b['floor'], b['number'], ', '.join(label(e, front) for e, front in b['enemies']),
                     number(sum(by_id[e]['hp'] for e, _ in b['enemies'])), max(by_id[e]['level'] for e, _ in b['enemies'])] for b in fixed])
    lines += ['', '### Enemies placed by events', '']
    lines += table(['Enemy', 'Habitat', 'Race', 'Lv', 'HP', 'ATK', 'DEF', 'INT', 'RES', 'DEX', 'AGI', 'EXP', 'Weight', 'Attacks', 'Cannot receive'],
                   [[e['name'], e['habitat'], e['race_name'], e['level'], number(e['hp']), e['atk'], e['def'], e['int'], e['res'], e['dex'],
                     e['agi'], number(e['exp']), f"{e['weight']:.2f}", len(e['attacks']), ', '.join(e['immune'])] for e in events])
    return lines


CHECKPOINTS = (20, 30, 40, 50, 60, 70, 80, 90)     # levels of the party at which catching up is measured
BEHIND = (10, 20)                                  # how far behind the member starts
PARTY = 5


def catch_up_sections(enemies):
    by_id = {e['id']: e for e in enemies}
    steps = {r['Level']: r['Req_EXP'] for r in rows_of(os.path.join(TABLES_DIR, 'vanilla_source_of_truth.xlsx'), 'ExpCurve')}
    floors = floor_data.floors()
    mean_level = lambda floor: sum(f['chance'] * statistics.mean(by_id[e]['level'] for e, _ in f['enemies'])
                                   for f in floor['formations']) / 100.0
    lines = ['## Catching up', '',
             'Random battles a member needs to reach the level of the party, fighting in the zone whose enemies are closest '
             f'to that level, with {PARTY} members alive and no EXP bonus (`sim/progression.py`, `docs/FORMULAS.md` 6c). '
             '"Own pace" is what one more level costs a member who is already on level, in the same zone. Bosses, quests and '
             'the EXP the party itself keeps gaining are left out.', '']
    rows = []
    for level in CHECKPOINTS:
        floor = min(floors, key=lambda f: (abs(mean_level(f) - level), f['name']))
        forms = [(f['chance'], [(by_id[e]['level'], by_id[e]['exp']) for e, _ in f['enemies']]) for f in floor['formations']]
        cost = lambda start, **options: progression.battles_to_reach(start, level, steps, forms, living=PARTY, **options)
        row = [level, floor['name'], f'{mean_level(floor):.0f}', f'{progression.battles_to_reach(level, level + 1, steps, forms, living=PARTY):.0f}']
        for behind in BEHIND:
            start = max(1, level - behind)
            row += [f'{cost(start):.0f}', f'{cost(start, double_exp_piece=True):.0f}']
        row.append(f'{cost(1):.0f}')
        rows.append(row)
    headers = ['Party level', 'Zone', 'Mean enemy level', 'Own pace (battles per level)']
    for behind in BEHIND:
        headers += [f'{behind} levels behind', f'{behind} behind, Double EXP piece']
    lines += table(headers + ['From level 1'], rows)
    return lines


def summon_sections(enemies):
    by_id = {e['id']: e for e in enemies}
    forms = summon_data.summons()
    lines = ['## Summons', '',
             f"{len(forms)} forms of {len({s['family'] for s in forms})} summons (`tools/summon_data.py`, `docs/FORMULAS.md` 11). The form used "
             'is the last whose level is not above the average level of the party; each stat is the best "stat of a party member * factor", '
             'and not below the figure of the enemy the summon comes from.', '']
    lines += table(['Summon', 'Level of the form', 'Weapon rank'] + [k.upper() + ' factor' for k in summon_data.STATS]
                   + ['Attacks', 'Sets of its script'] + ['Base ' + k.upper() for k in summon_data.STATS],
                   [[s['name'], s['level'], s['rank']] + [f"{s['factors'][k]:.2f}" for k in summon_data.STATS]
                    + [len(s['attacks']), len(s['script']['sets'])] + [by_id[s['family']][k] for k in summon_data.STATS] for s in forms])
    return lines


def doll_sections():
    arrow = lambda values: ' -> '.join(f'{v:g}' for v in values)
    lines = ['## Dolls', '',
             f'Every doll has {doll_data.DOLL_HP:,} HP and lasts a number of turns; on its turn it performs a hidden skill at the level '
             'of the doll skill (`tools/doll_data.py`, `docs/FORMULAS.md` 11.1). The figures below are those of the doll skill '
             '(turns, TP) and of the hidden action (everything else), per level.', '']
    rows = []
    for doll in doll_data.dolls():
        for action in doll['actions']:
            effects = '<br>'.join(f"{name or 'effect ' + str(effect)}: {arrow(values)}" for effect, name, values in action['effects'])
            rows.append([doll['name'], arrow(doll['turns']), arrow(doll['tp_cost']), action['name'], action['target'], action['attribute'],
                         doll['range'] or '', arrow(sorted(set(action['speed']))), effects])
    lines += table(['Doll', 'Turns it lasts', 'TP cost', 'Action', 'Target', 'Attribute', 'Range', 'Speed of the action', 'Effects of the action'], rows)
    return lines


def random_move_sections():
    lines = ['## Random moves', '',
             'A skill of this kind rolls on a table written in the executable and performs the hidden skill that comes out '
             '(`tools/random_move_data.py`, `docs/FORMULAS.md` 12.10). The second column of chances is the table used when the user '
             'has Triple Joker.', '']
    rows = []
    for move in random_move_data.random_moves():
        for r in move['results']:
            effects = ', '.join(name or f'effect {effect}' for effect, name in r['effects']) or 'nothing'
            rows.append([move['name'], r['skill'], f"{r['chance']:.1%}", f"{r['joker_chance']:.1%}", r['target'], r['attribute'], effects])
    lines += table(['Skill', 'Hidden skill', 'Chance', 'Chance with Triple Joker', 'Target', 'Attribute', 'Effects'], rows)
    return lines


def character_sections():
    names = class_data.class_names()
    steps = {r['Level']: r['Req_EXP'] for r in rows_of(os.path.join(TABLES_DIR, 'vanilla_source_of_truth.xlsx'), 'ExpCurve')}
    unique = {r['Skill_ID']: r['Name'] for r in rows_of(os.path.join(TABLES_DIR, 'vanilla_source_of_truth.xlsx'), 'UniqueSkills')}
    events = sorted(character_data.PEP_EVENTS)
    lines = ['## Characters', '',
             'Read from the package of each character (`tools/character_data.py`, `docs/FORMULAS.md` 13). The level is the one her '
             f'starting EXP gives on the EXP curve. Pep stays between {character_data.PEP_MIN:g} and {character_data.PEP_MAX:g}; '
             'the columns after it are what each event adds to it, for the events whose trigger was read in code.', '']
    rows = []
    for c in character_data.characters():
        level, left = 1, c['start_exp'] or 0                      # the curve holds the EXP of each step, not a running total
        while level + 1 in steps and left >= steps[level + 1]:
            level, left = level + 1, left - steps[level + 1]
        rows.append([c['name'], names.get(c['base_class'], c['base_class']), unique.get(c['unique_skill'], c['unique_skill']),
                     c['start_exp'], level] + [f"{c['pep'][k]:g}" for k in events])
    lines += table(['Character', 'Base class', 'Unique skill', 'Starting EXP', 'Starting level']
                   + [character_data.PEP_EVENTS[k].split(' (')[0].capitalize() for k in events], rows)
    return lines


def encounter_sections():
    zones = floor_data.floors()
    lines = ['## Encounter rate', '',
             'Each step in a zone rolls the chance of the zone for a random battle; for the first '
             f'{progression.ENCOUNTER_GRACE} steps after a battle none can start (`docs/FORMULAS.md` 14). The mean number of steps '
             'between two battles follows from both. Zones with the same figures are counted together.', '']
    groups = collections.defaultdict(list)
    for zone in zones:
        groups[(zone['dungeon'], zone['encounter'])].append(zone)
    rows = []
    for (dungeon, chance), members in sorted(groups.items()):
        steps = progression.steps_between_battles(chance)
        rows.append([dungeon, len(members), chance, 'none' if chance == 0 else f'{steps:.1f}',
                     'none' if chance == 0 else f'{progression.steps_between_battles(chance, pieces=(212,)):.1f}',
                     'none' if chance == 0 else f'{progression.steps_between_battles(chance, pieces=(214,)):.1f}'])
    lines += table(['Dungeon', 'Zones', 'Chance per step (%)', 'Mean steps between battles', 'With the strongest piece that lowers it',
                    'With the strongest piece that raises it'], rows)
    return lines


def skill_tree_sections():
    names = class_data.class_names()
    lines = ['## Skills of each class', '',
             'Each skill file names the classes that learn it in a mask of bits (`tools/skill_tree_data.py`). SP is the cost of every '
             'level of every skill of the class added up. The range is the one of a technique; a spell has none.', '']
    rows = []
    for class_id, learned in sorted(skill_tree_data.by_class().items()):
        listed = ', '.join(f"{s['name']} ({s['levels']})" if not s['range'] or s['range'] == 'none' else f"{s['name']} ({s['levels']}, {s['range']})"
                           for s in learned)
        rows.append([names.get(class_id, class_id), len(learned), sum(sum(s['sp']) for s in learned), listed])
    lines += table(['Class', 'Skills', 'SP to max them all', 'Skills (levels, range)'], rows)
    return lines


def class_modifier_sections():
    names = class_data.class_names()
    lines = ['## Class modifiers', '',
             'What a class gains from the piece it specialises in: for every stat the piece gives, '
             '`int((stat of the character + stat of the piece) * modifier)` (`tools/class_modifier_data.py`, `docs/FORMULAS.md` 10.4). '
             'The tables are written in the executable. Six advanced classes have one table per class they can come from.', '']
    rows = []
    for row in class_modifier_data.class_modifiers():
        rows.append([names.get(row['class'], row['class']), '' if row['previous'] is None else names.get(row['previous'], row['previous']),
                     ', '.join(f"{e['type_name']} {e['modifier'] * 100:+.0f}%" for e in row['entries'])])
    lines += table(['Class', 'Coming from', 'Modifiers'], rows)
    return lines


def main():
    enemies = enemy_data.enemies()
    lines = ['# Balance baseline (generated)', '',
             'Generated by `tools/balance_baseline.py`. Do not edit: run the tool again.',
             'Every figure here is read from the game files; none is typed.', '']
    lines += class_sections() + [''] + class_modifier_sections() + [''] + skill_tree_sections() + [''] + character_sections() + [''] + enemy_sections(enemies) + [''] + floor_sections(enemies) + [''] + encounter_sections() + [''] + summon_sections(enemies) + [''] + doll_sections() + [''] + random_move_sections() + [''] + catch_up_sections(enemies) + [''] + behaviour_sections(enemies) + [''] + skill_sections() + ['']
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {OUTPUT_PATH}: {len(lines)} lines')


if __name__ == '__main__':
    main()

"""
The checklist that closes phase 1 (the simulator), generated: docs/generated/SIM_COVERAGE.md.

    python mod_project/tools/sim_coverage.py

It counts, from the code of sim/ and the workbooks, never by hand, the five steps of phase 1 (BALANCE_PLAN.md
section 3, approach of 2026-10-07) and the engine they rest on:
    effects   every effect a skill of the player uses (or a unique skill), and whether sim/battle.py acts on it
              (HANDLED), with an assumption of data_tables/sim_setup.xlsx (ASSUMED), or not at all
    AI        the commands, sources and target kinds of the enemy scripts sim/ai.py runs, and the scripts that use
              something it does not run
    builds    the roles of the sheet Roles with a reference build of the guides (a skill plan or priority, and a source)
    tests     the calibration tests of the sheet Calibration that exist in tests/
    anchors   the boss fights of the sheet Anchors the reference party wins as the guides say, as last written by
              tools/sim_anchors.py (it plays battles, so it runs apart)
    check     the check of a change (sim/measures.py, function check_change)
    postgame  the checkpoints of the postgame and the superbosses (rows of the sheet Checkpoints) against the bosses the
              postgame pages of the GameFAQs guide list (sheet PostgameBosses)
    assumptions  the rows of the sheet Assumptions still open
Phase 1 is closed when every count of the table "To close" is at its target. The verdicts of the rows of Criticisms
are the checklist of phase 2, written by tools/verdicts.py.
"""
import ast
import os
import sys

import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
OUTPUT = os.path.join(BASE_DIR, 'docs', 'generated', 'SIM_COVERAGE.md')
CRITERIA = os.path.join(BASE_DIR, 'data_tables', 'balance_criteria.xlsx')
SETUP = os.path.join(BASE_DIR, 'data_tables', 'sim_setup.xlsx')
TESTS = os.path.join(BASE_DIR, 'tests')

import enemy_ai                                        # noqa: E402  (tools/ is on the path through sim.data)
from sim import ai, battle, measures                   # noqa: E402
from sim.data import game_data                         # noqa: E402


def rows(path, sheet):
    it = openpyxl.load_workbook(path, read_only=True)[sheet].iter_rows(values_only=True)
    header = next(it)
    return [dict(zip(header, r)) for r in it if any(v is not None for v in r)]


def optional_rows(path, sheet):
    """The rows of a sheet that a later step of phase 1 creates; none while it does not exist."""
    wb = openpyxl.load_workbook(path, read_only=True)
    return rows(path, sheet) if sheet in wb.sheetnames else []


def anchors_count():
    """The count of anchors met that tools/sim_anchors.py wrote last, or None when it has not run."""
    path = os.path.join(BASE_DIR, 'docs', 'generated', 'SIM_ANCHORS.md')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('Anchors met: **'):
                parts = line.split('**')
                return int(parts[1].split()[0]), int(parts[3]) if len(parts) > 3 else 0
    return None


def player_effects(data):
    used = {}
    for skill in data.skills.values():
        for effect, _, _ in skill.effects:
            used.setdefault(effect, []).append(skill.name)
    for unique in data.unique.values():
        used.setdefault(unique['effect'], []).append(unique['name'])
    return used


def ai_parts():
    """The commands, sources and target kinds sim/ai.py has a branch for, read from its source."""
    source = open(ai.__file__, encoding='utf-8').read()
    tree = ast.parse(source)
    commands, sources, targets = set(), set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ('passes', 'source_value', 'pick_by_kind'):
            found = {'passes': commands, 'source_value': sources, 'pick_by_kind': targets}[node.name]
            for sub in ast.walk(node):
                if isinstance(sub, ast.Compare):
                    for comp in sub.comparators:
                        if isinstance(comp, ast.Constant) and isinstance(comp.value, int):
                            found.add(comp.value)
                        if isinstance(comp, ast.Tuple):
                            found.update(e.value for e in comp.elts if isinstance(e, ast.Constant))
    commands |= {enemy_ai.SET, enemy_ai.TARGET}                     # handled in run()
    return commands, sources, targets


def script_gaps(data, commands, sources, targets):
    gaps = []
    for enemy in data.enemies.values():
        script = enemy['script']
        if script is None:
            if enemy['ai']:
                gaps.append((enemy['id'], enemy['name'], 'the script does not decode'))
            continue
        for c in enemy_ai.commands_of(script):
            if c['cmd'] not in commands:
                gaps.append((enemy['id'], enemy['name'], f'command {c["cmd"]}'))
            elif c['cmd'] in enemy_ai.USES_SOURCE and c['args'][0] not in sources:
                gaps.append((enemy['id'], enemy['name'], f'source {c["args"][0]}'))
            elif c['cmd'] == enemy_ai.TARGET and c['args'][1] not in targets:
                gaps.append((enemy['id'], enemy['name'], f'target kind {c["args"][1]}'))
    return gaps


def test_names():
    found = set()
    for name in os.listdir(TESTS):
        if name.startswith('test_') and name.endswith('.py'):
            tree = ast.parse(open(os.path.join(TESTS, name), encoding='utf-8').read())
            module = name[:-3]
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    found.add(f'{module}.{node.name}')
    return found


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    data = game_data()
    used = player_effects(data)
    names = data.effect_names
    exact = sorted(e for e in used if e in battle.HANDLED and e not in battle.ASSUMED)
    assumed = sorted(e for e in used if e in battle.ASSUMED)
    missing = sorted(e for e in used if e not in battle.HANDLED)

    commands, sources, targets = ai_parts()
    all_commands = set(enemy_ai.COMMANDS)
    gaps = script_gaps(data, commands, sources, targets)
    gap_scripts = sorted({g[0] for g in gaps})
    scripts = sum(1 for e in data.enemies.values() if e['ai'])

    roles = rows(SETUP, 'Roles')
    with_build = [r for r in roles if (r.get('Skill plan') or r.get('Skill priority')) and r.get('Source')]
    has_check = hasattr(measures, 'check_change')
    checkpoints = rows(SETUP, 'Checkpoints')
    postgame_bosses = optional_rows(SETUP, 'PostgameBosses')
    postgame = [r for r in checkpoints if r['ID'] in {b['ID'] for b in postgame_bosses}]

    calibration = rows(SETUP, 'Calibration')
    tests = test_names()
    # a row checked by playing battles names tools/sim_anchors.py and its anchors instead of a test class
    calibrated = [r for r in calibration if r['Test in tests/'] in tests
                  or str(r['Test in tests/'] or '').startswith('tools/sim_anchors.py')]
    anchors_total = len(optional_rows(SETUP, 'Anchors'))
    anchors_met, anchors_limits = anchors_count() or (None, 0)
    assumptions = rows(SETUP, 'Assumptions')
    open_rows = [r for r in assumptions if r['State'] not in ('read', 'read in a guide', 'choice')]

    out = ['# Phase 1 checklist: the simulator (generated)', '',
           'Generated by `tools/sim_coverage.py` from the code of `sim/` and the workbooks. Do not edit: run the tool '
           'again. Phase 1 is closed when every line of the first table is at its target.', '',
           '## To close', '',
           '| Item | Count | Target |', '|---|---|---|',
           f'| Effects used by the skills of the player that the battle acts on | {len(exact) + len(assumed)} of {len(used)} | all |',
           f'| ... of them on an assumption of `sim_setup.xlsx` | {len(assumed)} | 0 |',
           f'| AI commands run | {len(commands & all_commands)} of {len(all_commands)} | all |',
           f'| AI sources read | {len(sources)} of {len(enemy_ai.SOURCES)} | all |',
           f'| AI target kinds | {len(targets)} of {len(enemy_ai.TARGETS)} | all |',
           f'| Enemy scripts that use nothing the runner lacks | {scripts - len(gap_scripts)} of {scripts} | all |',
           f'| Roles with a reference build of the guides (sheet `Roles`) | {len(with_build)} of {len(roles)} | all |',
           f'| Calibration tests written | {len(calibrated)} of {len(calibration)} | all |',
           f'| Boss anchors met (`docs/generated/SIM_ANCHORS.md`, run `tools/sim_anchors.py`) | '
           f'{"?" if anchors_met is None else anchors_met} of {anchors_total}, known limits {anchors_limits} | all, or met '
           f'plus known limits the user confirms |',
           f'| Check of a change (`sim/measures.py`, `check_change`) | {"yes" if has_check else "no"} | yes |',
           f'| Postgame and superboss checkpoints | {len(postgame)} of {len(postgame_bosses) or "?"} '
           f'(sheet `PostgameBosses`{"" if postgame_bosses else " not written yet"}) | all |',
           f'| Assumptions still open | {len(open_rows)} of {len(assumptions)} | 0 (a "choice" row is a stated decision) |',
           '']
    out += ['## Effects the battle does not act on yet', '', '| Effect | Name | Used by |', '|---|---|---|']
    out += [f'| {e} | {names.get(e) or ""} | {", ".join(sorted(set(used[e]))[:4])} |' for e in missing] or ['| - | - | - |']
    out += ['', '## Effects acted on with an assumption', '', '| Effect | Name | Assumption |', '|---|---|---|']
    out += [f'| {e} | {names.get(e) or ""} | {battle.ASSUMED[e]} |' for e in assumed] or ['| - | - | - |']
    out += ['', '## Assumptions', '', '| ID | State | Rule |', '|---|---|---|']
    out += [f'| {r["ID"]} | {r["State"]} | {r["Rule used by the model"]} |' for r in assumptions]
    out += ['', '## Enemy scripts the runner cannot follow in full', '', '| Enemy | What |', '|---|---|']
    out += [f'| {name} ({eid}) | {what} |' for eid, name, what in gaps[:60]] or ['| - | - |']
    out += ['', '## Roles without a reference build', '', '| Role |', '|---|']
    out += [f'| {r["Role"]} |' for r in roles if r not in with_build] or ['| - |']
    out += ['', '## Calibration', '', '| ID | Test | In tests/ |', '|---|---|---|']
    out += [f'| {r["ID"]} | {r["Test"]} | {"yes" if r in calibrated else "no"} |' for r in calibration]
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    print(f'effects {len(exact) + len(assumed)}/{len(used)} (assumed {len(assumed)}), missing {len(missing)}; '
          f'AI commands {len(commands & all_commands)}/{len(all_commands)}, sources {len(sources)}/{len(enemy_ai.SOURCES)}, '
          f'targets {len(targets)}/{len(enemy_ai.TARGETS)}, scripts {scripts - len(gap_scripts)}/{scripts}; '
          f'builds {len(with_build)}/{len(roles)}; calibration {len(calibrated)}/{len(calibration)}; '
          f'anchors {"?" if anchors_met is None else anchors_met}/{anchors_total} (+{anchors_limits} known limit); '
          f'check {"yes" if has_check else "no"}; postgame {len(postgame)}/{len(postgame_bosses) or "?"}; '
          f'assumptions open {len(open_rows)}/{len(assumptions)}')
    print(f'written {OUTPUT}')


if __name__ == '__main__':
    main()

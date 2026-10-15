"""
The tools and scripts that play battles, on the C# engine against the Python simulator, on the same inputs, value by value.

    python engine_cs/parity/gate_tools.py [name ...]        all the gates, or the ones named (--list for the names)

Each gate runs one tool twice, once as it always ran (sim/) and once on the engine (its `engine` command or its `--engine` flag), on a
small part of its input, and compares what the tool computes: the figures it writes (compared as the values it would write) or, for the
scripts that only print, what it prints. Nothing under docs/ or measures/ is written: the tools write into build/gate_out/.
The output files the tools write are compared with the committed ones where those are current (the line "committed" of a gate).
"""
import contextlib
import glob
import importlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
for path in (PROJECT, os.path.join(PROJECT, 'tools'), os.path.join(PROJECT, 'measures')):
    if path not in sys.path:
        sys.path.insert(0, path)

OUT = os.path.join(PROJECT, 'build', 'gate_out')
GATES = {}


def gate(fn):
    GATES[fn.__name__] = fn
    return fn


def fresh(*names):
    for name in names:
        folder = os.path.join(OUT, name)
        os.makedirs(folder, exist_ok=True)
        for f in glob.glob(os.path.join(folder, '*')):
            os.remove(f)
    return [os.path.join(OUT, n) for n in names]


def count(a, b, where=''):
    """(values compared, values that differ) of two nested structures."""
    if isinstance(a, dict) and isinstance(b, dict):
        total = bad = 0
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                total += 1
                bad += 1
                continue
            t, d = count(a[k], b[k])
            total, bad = total + t, bad + d
        return total, bad
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return max(len(a), len(b)), abs(len(a) - len(b)) or 1
        total = bad = 0
        for x, y in zip(a, b):
            t, d = count(x, y)
            total, bad = total + t, bad + d
        return total, bad
    return 1, 0 if a == b else 1


def timed(fn, *args, **kw):
    t = time.time()
    out = fn(*args, **kw)
    return out, time.time() - t


def captured(fn, *args):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        t = time.time()
        fn(*args)
        t = time.time() - t
    return buffer.getvalue(), t


def row(name, what, values, bad, tp, te, extra=''):
    return {'gate': name, 'what': what, 'values': values, 'differences': bad, 'python_s': round(tp, 1), 'engine_s': round(te, 1), 'note': extra}


def setup_balance():
    from sim import setup as setup_mod
    from sim.data import game_data
    from sim.variant import balance_data
    vanilla = game_data()
    return vanilla, balance_data(vanilla), setup_mod.load()


def read_json_dir(folder, prefix=''):
    out = {}
    for f in sorted(glob.glob(os.path.join(folder, prefix + '*.json'))):
        with open(f, encoding='utf-8') as fh:
            out[os.path.basename(f)] = json.load(fh)
    return out


# --- tools ---------------------------------------------------------------------------------------------------------------------
@gate
def class_stages():
    import class_stages as tool
    _, data, setup = setup_balance()
    cells = [(cid, role) for cid in ('C03', 'C10', 'C24', 'C36', 'P24') for role in (None, 'tank', 'healer', 'diva', 'mage', 'papillon')]
    a, tp = timed(lambda: [tool.play(data, setup, cid, role, 12) for cid, role in cells])
    b, te = timed(lambda: [tool.play_engine(data, setup, cid, role, 12) for cid, role in cells])
    t, d = count(a, b)
    return row('class_stages', f'{len(cells)} cells (base party and 5 roles at 5 checkpoints), 12 battles', t, d, tp, te)


@gate
def class_stages_pass():
    """The whole pass of `engine` against the files of docs/generated/class_stages, and the cells that differ from them against live Python."""
    import class_stages as tool
    _, data, setup = setup_balance()
    committed = tool.OUT_DIR
    (mine,) = fresh('class_stages')
    tool.OUT_DIR = mine
    _, te = timed(tool.run_engine)
    tool.OUT_DIR = committed

    def load(folder):
        found = {}
        for name in sorted(os.listdir(folder)):
            if name.endswith('.json'):
                d = json.load(open(os.path.join(folder, name), encoding='utf-8'))
                e = found.setdefault(name.split('_')[0], {'base': None, 'roles': {}})
                if d['base'] is not None:
                    e['base'] = d['base']
                e['roles'].update(d['roles'])
        return found
    old, new = load(committed), load(mine)
    total = bad = live = live_bad = 0
    runs = int(setup.settings['check_runs'])
    tp = 0.0
    for cid in sorted(set(old) & set(new)):
        cells = [(None, old[cid]['base'], new[cid]['base'])] + [(r, old[cid]['roles'].get(r), new[cid]['roles'].get(r)) for r in sorted(new[cid]['roles'])]
        for role, was, now in cells:
            total += 1
            if was != now:
                bad += 1
                result, t = timed(tool.play, data, setup, cid, role, runs)     # the committed file is older than the data: Python live decides
                tp += t
                if role is not None:
                    result['class'] = now['class']
                live += 1
                live_bad += result != now
    return row('class_stages_pass', f'{total} cells of the whole pass; {bad} differ from the committed files and were played live in Python ({live_bad} differ from the engine)',
               total, live_bad, tp, te, f'{total - bad} equal to the committed files')


@gate
def skill_value():
    import skill_value as tool
    from sim import setup as setup_mod
    _, data, setup = setup_balance()
    setup.settings['check_runs'] = 10
    every, hostile = tool.candidates(data), tool.hostile_skills(data)
    picks = every[::13][:8] + hostile[::4][:3]
    cells = []
    for skill in picks:
        found = tool.place(data, setup, skill)
        if found:
            role, st = found
            cid = [c.strip() for c in str(st['Checkpoints']).split(';')][0]
            cells += [(role, cid, skill, use, chain) for use in (False, True) for chain in (0, 8)]
    a, tp = timed(lambda: [tool.play(data, setup, *c) for c in cells])
    b, te = timed(lambda: [tool.play_engine(data, setup, *c) for c in cells])
    t, d = count(a, b)
    return row('skill_value', f'{len(cells)} cells (boss fights and rows of 8 random battles, with and without the skill), 10 battles', t, d, tp, te)


@gate
def skill_value_pass():
    """`engine` and `engine-ailments` against the committed files (current for this data)."""
    import skill_value as tool
    committed, committed_a = tool.OUT_DIR, os.path.join(tool.BASE_DIR, 'docs', 'generated', 'skill_ailments')
    (mine,) = fresh('skill_value')
    tool.OUT_DIR = mine
    _, te = timed(tool.run_engine)
    tool.OUT_DIR = committed
    (fresh_a,) = fresh('skill_ailments')
    saved = tool.BASE_DIR
    os.makedirs(os.path.join(OUT, 'skill_ailments_root', 'docs', 'generated'), exist_ok=True)
    tool.BASE_DIR = os.path.join(OUT, 'skill_ailments_root')
    _, te2 = timed(tool.run_engine_ailments)
    tool.BASE_DIR = saved
    new_a = read_json_dir(os.path.join(OUT, 'skill_ailments_root', 'docs', 'generated', 'skill_ailments'))
    old = [r for f in read_json_dir(committed).values() for r in f]
    new = [r for f in read_json_dir(mine).values() for r in f]
    old_a = [r for f in read_json_dir(committed_a).values() for r in f]
    new_a = [r for f in new_a.values() for r in f]
    key = lambda r: r['skill']       # noqa: E731
    t, d = count(sorted(old, key=key), sorted(new, key=key))
    t2, d2 = count(sorted(old_a, key=key), sorted(new_a, key=key))
    return row('skill_value_pass', f'the whole pass ({len(new)} skills) and the ailments pass ({len(new_a)} skills) against the committed files',
               t + t2, d + d2, 0.0, te + te2, 'Python time: see the committed run')


@gate
def boss_fit():
    import boss_fit as tool
    from sim import measures, scenario
    vanilla, data, setup = setup_balance()
    todo = tool.easier(setup)[:3]
    runs = int(setup.settings['check_runs'])
    pairs = [(1.0, 1.0), (1.1, 1.05), (1.2, 1.1)]
    tasks = [(row_, pair) for row_ in todo for pair in pairs]

    def python():
        out = []
        for r, (hp, attack) in tasks:
            ids = tool.boss_enemies(vanilla, setup, r['id'])
            source = data if (hp, attack) == (1.0, 1.0) else tool.scaled(data, ids, hp, attack)
            _, fig = measures.play_checkpoint(source, setup, r['id'], runs)
            parties = {n: sum(1 for x in scenario.play_party(source, setup, r['id'], roles, 6) if x['won']) / 6
                       for n, (_, roles) in list(setup.battery.items())[:2]}
            out.append((fig, parties))
        return out
    a, tp = timed(python)
    setup.settings['boss_fit_party_runs'] = 6
    full, te = timed(tool.gentle_figures, vanilla, setup, data, tasks)
    b = [(fig, {n: parties[n] for n in list(setup.battery)[:2]}) for fig, parties in full]
    t, d = count(a, b)
    return row('boss_fit', f'{len(tasks)} (checkpoint, factors) cells: the figures of the reference party and the share of wins of two parties', t, d, tp, te)


@gate
def sim_audit_passives():
    return sim_audit_phase('passives', '1/1')


@gate
def sim_audit_usage():
    return sim_audit_phase('usage', '1/1')


@gate
def sim_audit_actives():
    return sim_audit_phase('actives', '1/1')


def sim_audit_phase(phase, part):
    import sim_audit
    py, en = fresh('sim_audit_py', 'sim_audit_en')
    saved = sim_audit.OUT_DIR
    k, n = part.split('/')
    name = f'{phase}.md' if n == '1' else f'{phase}_{k}.md'
    sim_audit.OUT_DIR = py
    with contextlib.redirect_stdout(io.StringIO()):
        _, tp = timed(getattr(sim_audit, phase), part)
    sim_audit.OUT_DIR = en
    with contextlib.redirect_stdout(io.StringIO()):
        _, te = timed(getattr(sim_audit, phase + '_engine'), part)
    sim_audit.OUT_DIR = saved
    a = open(os.path.join(py, name), encoding='utf-8').read().splitlines()
    b = open(os.path.join(en, name), encoding='utf-8').read().splitlines()
    t, d = count(a, b)
    return row('sim_audit_' + phase, f'{len(a)} lines of the {phase} phase (part {part})', t, d, tp, te)


@gate
def skill_worth():
    import skill_worth as tool
    import class_stages
    from sim import setup as setup_mod
    _, data, setup = setup_balance()
    (py,) = fresh('skill_worth_py')
    committed = tool.OUT_DIR
    total = bad = 0
    tp = te = 0.0
    stages = [s['Stage'] for s in class_stages.stages(setup)]
    for stage in stages:
        tool.OUT_DIR = py
        with contextlib.redirect_stdout(io.StringIO()):
            _, t = timed(tool.run, stage)
        tp += t
        rows, t = timed(tool.run_engine_stage, data, setup, stage)
        te += t
        mine = json.load(open(os.path.join(py, stage + '.json'), encoding='utf-8'))
        t_, d_ = count(mine, rows)
        total, bad = total + t_, bad + d_
    tool.OUT_DIR = committed
    return row('skill_worth', f'{len(stages)} stages, every role at every checkpoint, boss and random groups', total, bad, tp, te)


@gate
def guide_curve():
    import guide_curve as tool
    py, en = fresh('guide_curve_py', 'guide_curve_en')
    committed = tool.OUT_DIR
    tool.OUT_DIR = py
    with contextlib.redirect_stdout(io.StringIO()):
        _, tp = timed(tool.run, '1/1')
        tool.OUT_DIR = en
        _, te = timed(tool.run_engine)
    tool.OUT_DIR = committed
    a = json.load(open(os.path.join(py, 'part_1.json'), encoding='utf-8'))
    b = json.load(open(os.path.join(en, 'part_1.json'), encoding='utf-8'))
    old = [r for f in read_json_dir(committed).values() for r in f]
    t, d = count(a, b)
    _, dc = count(sorted(old, key=lambda r: r['id']), sorted(b, key=lambda r: r['id']))
    return row('guide_curve', f'{len(a)} bosses of the sheet GuideDifficulty, 40 battles', t, d, tp, te, f'{dc} differences from the committed files')


@gate
def sim_anchors():
    import sim_anchors as tool
    committed = tool.OUTPUT
    tool.OUTPUT = os.path.join(OUT, 'sim_anchors_py.md')
    os.makedirs(OUT, exist_ok=True)
    with contextlib.redirect_stdout(io.StringIO()):
        _, tp = timed(tool.main)
        tool.OUTPUT = os.path.join(OUT, 'sim_anchors_en.md')
        _, te = timed(tool.main_engine)
    tool.OUTPUT = committed
    a = open(os.path.join(OUT, 'sim_anchors_py.md'), encoding='utf-8').read().splitlines()
    b = open(os.path.join(OUT, 'sim_anchors_en.md'), encoding='utf-8').read().splitlines()
    old = open(committed, encoding='utf-8').read().splitlines()
    t, d = count(a, b)
    return row('sim_anchors', f'{len(a)} lines (the anchors of the sheet, win shares)', t, d, tp, te, f'{count(old, b)[1]} differences from the committed file')


# --- scripts of measures/ ------------------------------------------------------------------------------------------------------
def patched_dir(module, name):
    """Makes a module of measures/ write its files into build/gate_out/<name> (its HERE)."""
    (folder,) = fresh(name)
    saved = module.HERE
    module.HERE = folder
    return folder, saved


@gate
def win_rates():
    import win_rates as m
    tasks = [(p, c, s) for p in ('Meta', 'Juggernaut', 'Anti-Meta') for c in ('C24', 'C40') for s in ('vanilla', 'variant')]
    a, tp = timed(lambda: [m.cell(t) for t in tasks])
    b, te = timed(m.cells_engine, tasks)
    t, d = count(a, b)
    return row('win_rates', f'{len(tasks)} cells (party, boss, side) of the 7 parties x 17 bosses x 2 sides', t, d, tp, te)


@gate
def win_rates_pass():
    """The whole pass of `engine` against measures/win_rates.json (current for this data)."""
    import win_rates as m
    from sim import setup as setup_mod
    bosses = [c.strip() for c in str(setup_mod.load().settings['battery_checkpoints']).split(';') if c.strip()]
    tasks = [(p, c, s) for p in m.PARTIES for c in bosses for s in ('vanilla', 'variant')]
    b, te = timed(m.cells_engine, tasks)
    old = json.load(open(m.OUT, encoding='utf-8'))
    t, d = count(old, b)
    return row('win_rates_pass', f'{len(tasks)} cells of measures/win_rates.json (100 or 200 battles each)', t, d, 0.0, te, 'compared with the committed file')


@gate
def curve_recheck():
    import curve_recheck as m
    bosses = ['C15', 'C28', 'C40']
    a, tp = timed(lambda: [m.cell((c, 20)) for c in bosses])
    b, te = timed(m.rows_engine, bosses, 20)
    t, d = count([list(x) for x in a], [list(x) for x in b])
    return row('curve_recheck', f'{len(bosses)} checkpoints, 20 battles, the game against the variant', t, d, tp, te)


@gate
def curve_ablation():
    import curve_ablation as m
    folder, saved = patched_dir(m, 'curve_ablation_py')
    # the workbook of commit dc1a09b that the script reads is not in the repository: the current one stands in for it, so the cases
    # that take a change back still differ from 'now' by the flags of the data (the rate of interruptions, the roll of Arcane Shield)
    m.THEN = os.path.join(PROJECT, 'data_tables', 'balance_changes.xlsx')
    total = bad = 0
    tp = te = 0.0
    for case in ('now', 'samba', 'interruption', 'arcane shield', 'then'):
        with contextlib.redirect_stdout(io.StringIO()):
            m.HERE = folder
            _, t = timed(m.run, case, 6)
            tp += t
            a = json.load(open(os.path.join(folder, f"curve_ablation_{case.replace(' ', '_')}_6.json"), encoding='utf-8'))
            os.remove(os.path.join(folder, f"curve_ablation_{case.replace(' ', '_')}_6.json"))
            _, t = timed(m.run_engine, case, 6)
            te += t
        b = json.load(open(os.path.join(folder, f"curve_ablation_{case.replace(' ', '_')}_6.json"), encoding='utf-8'))
        t_, d_ = count(a, b)
        total, bad = total + t_, bad + d_
    m.HERE = saved
    return row('curve_ablation', '5 cases (now, samba, interruption, arcane shield, then) at the 8 checkpoints, 6 battles', total, bad, tp, te,
               'the workbook of dc1a09b is not in the repository: the current one stands in for it')


@gate
def random_battles():
    import random_battles as m
    vanilla, variant, setup = setup_balance()
    import engine_client as engine
    ids = ['C05', 'C20', 'C35']
    a, tp = timed(lambda: [(m.play(vanilla, setup, c, 6), m.play(variant, setup, c, 6)) for c in ids])

    def engine_side():
        jobs, index = [], {}
        for c in ids:
            for tag, d in (('vanilla', vanilla), ('variant', variant)):
                index[(c, tag)] = len(jobs)
                jobs.append(m.jobs_engine(d, setup, c, 6, engine.side_of(d), f'{c}|{tag}'))
        done = engine.run_jobs(jobs)
        return [(m.figures_engine(vanilla, setup, c, done[index[(c, 'vanilla')]]), m.figures_engine(variant, setup, c, done[index[(c, 'variant')]])) for c in ids]
    b, te = timed(engine_side)
    t, d = count(a, b)
    return row('random_battles', f'{len(ids)} floors, rows of 8 random battles, 6 rows, both sides', t, d, tp, te)


def slice_gate(name, module_name, part, runs=None):
    m = importlib.import_module(module_name)
    folder, saved = patched_dir(m, name + '_py')
    prefix = {'mercenaries': 'mercenaries_', 'unique_skills': 'unique_skills_', 'party_skills': 'party_skills_', 'postgame_compare': 'postgame_compare_',
              'skill_value_contested': 'skill_value_contested_'}[module_name]
    k = part.split('/')[0]
    args = (part,) if runs is None else (part, runs)
    with contextlib.redirect_stdout(io.StringIO()):
        _, tp = timed(m.run, *args)
    a = json.load(open(os.path.join(folder, f'{prefix}{k}.json'), encoding='utf-8'))
    os.remove(os.path.join(folder, f'{prefix}{k}.json'))
    with contextlib.redirect_stdout(io.StringIO()):
        _, te = timed(m.run_engine, *args)
    b = json.load(open(os.path.join(folder, f'{prefix}{k}.json'), encoding='utf-8'))
    m.HERE = saved
    t, d = count(a, b)
    return t, d, tp, te


@gate
def mercenaries():
    t, d, tp, te = slice_gate('mercenaries', 'mercenaries', '2/13', 8)
    return row('mercenaries', 'a slice of the guests (summon and mercenaries) at 3 bosses, 8 battles', t, d, tp, te)


@gate
def unique_skills():
    t, d, tp, te = slice_gate('unique_skills', 'unique_skills', '3/18', 8)
    return row('unique_skills', 'one girl with and without her unique skill at 5 places, 8 battles', t, d, tp, te)


@gate
def party_skills():
    t, d, tp, te = slice_gate('party_skills', 'party_skills', '5/21', 8)
    return row('party_skills', 'a party skill and the party without, at 4 bosses, 8 battles', t, d, tp, te)


@gate
def postgame_compare():
    t, d, tp, te = slice_gate('postgame_compare', 'postgame_compare', '2/12')
    return row('postgame_compare', 'a slice of the postgame bosses, vanilla against the variant at the crown the floor of their class asks', t, d, tp, te)


@gate
def skill_value_contested():
    import skill_value_contested as m
    t, d, tp, te = slice_gate('skill_value_contested', 'skill_value_contested', '2/10', 8)
    return row('skill_value_contested', 'a slice of the skills left to read, at the contested bosses, 8 battles', t, d, tp, te)


def cells_gate(name, module_name, tasks, what, cell='cell'):
    """A script whose cells are a function of a task: the function twice, with the module's ENGINE flag off and on."""
    m = importlib.import_module(module_name)
    fn = getattr(m, cell)
    m.ENGINE = False
    with contextlib.redirect_stdout(io.StringIO()):
        a, tp = timed(lambda: [fn(t) for t in tasks])
    m.ENGINE = True
    with contextlib.redirect_stdout(io.StringIO()):
        b, te = timed(lambda: [fn(t) for t in tasks])
    m.ENGINE = False
    t, d = count(a, b)
    return row(name, what, t, d, tp, te)


@gate
def support_chains():
    return cells_gate('support_chains', 'support_chains', [('C10', 'healer', 8, 6), ('C24', 'tank', 8, 6), ('C36', 'diva', 8, 6), ('C36', 'attacker', 8, 6)],
                      '4 cells (role, checkpoint): rows of 8 random battles, 6 rows')


@gate
def support_stages():
    return cells_gate('support_stages', 'support_stages', [('C05', 'tank', 10), ('C10', 'healer', 10), ('C18', 'diva', 10)], '3 cells, 10 battles')


@gate
def boss_rows_check():
    return cells_gate('boss_rows_check', 'boss_rows_check', [('C26', 'game', 8), ('C26', 'variant', 8), ('C26', 'without', 8), ('C30', 'without', 8)],
                      '4 cells (the game, the variant, the variant without the rows of the boss), 8 battles')


@gate
def win_causes():
    return cells_gate('win_causes', 'win_causes', [('Meta', 'C26', 'game', 8), ('Meta', 'C26', 'variant', 8), ('Meta', 'C26', 'S', 8), ('Meta', 'C30', 'only S', 8)],
                      '4 cells (a family of rows taken out, or alone), 8 battles')


@gate
def record_causes():
    return cells_gate('record_causes', 'record_causes', [('Meta', 'C26', 'game', (), 8), ('Meta', 'C26', 'variant', (), 8),
                                                         ('Meta', 'C26', 'Graceful Rose', ('Graceful Rose',), 8), ('Meta', 'C30', 'Protect', ('194 Protect', 'Circle Protect'), 8)],
                      '4 cells (a group of rows taken out), 8 battles')


@gate
def rows_trial():
    return cells_gate('rows_trial', 'rows_trial', [('reference', 'C26', True, ('P031',), 8), ('reference', 'C26', False, ('P031',), 8),
                                                   ('Meta', 'C30', True, ('P031', 'P032'), 8), ('Dual-Support', 'C30', False, ('P031',), 8)],
                      '4 cells (rows taken out or not), 8 battles')


@gate
def boss_trim_trial():
    return cells_gate('boss_trim_trial', 'boss_trim_trial', [('reference', 'C30', '', 8), ('reference', 'C30', 'hp*1.15', 8), ('Meta', 'C30', 'atk=game,int=game', 8),
                                                              ('Juggernaut', 'C26', 'hp*1.15,atk=game', 8)], '4 cells (a change to the enemies of the boss), 8 battles')


@gate
def dance_trial():
    return cells_gate('dance_trial', 'dance_trial', [('Juggernaut', 'C26', 'game', 8), ('Juggernaut', 'C26', 'variant', 8), ('Physical, Diva', 'C30', 'variant, dances halfway', 8),
                                                     ('Physical, Diva', 'C30', 'variant, dances of the game', 8)], '4 cells (the values of two dances), 8 battles')


@gate
def def_debuff_trial():
    return cells_gate('def_debuff_trial', 'def_debuff_trial', [('Physical', 'C30', 'game, usual dances', 8), ('Physical', 'C30', 'game, Samba', 8),
                                                                ('Meta, Etoile for Papillon', 'C30', 'variant, Samba', 8), ('Physical', 'C36', 'variant, Samba + Armor Penetration', 8)],
                      '4 cells (policy, role, data and skill changed in the process), 8 battles')


@gate
def graceful_rose_trial():
    return cells_gate('graceful_rose_trial', 'graceful_rose_trial', [('Meta', 'C26', 0.6, 8), ('papillon', 'C30', 0.5, 8), ('Meta', 'C30', 0.2, 8)],
                      '3 cells (the power of a skill, a party and a role), 8 battles')


@gate
def sage_buffs_trial():
    return cells_gate('sage_buffs_trial', 'sage_buffs_trial', [((None, 1.0, 2), 'C30', 8), ((2.0, 1.2, 5), 'C30', 8), ((3.0, 1.0, 5), 'C36', 8)],
                      '3 cells (chant, size and rules of the Sage changed), 8 battles')


@gate
def one_skill_trial():
    return cells_gate('one_skill_trial', 'one_skill_trial', [('mistress', 'Ecstasy', 'C26', False, 8), ('mistress', 'Ecstasy', 'C26', True, 8), ('tank', 'Provoke', 'C30', True, 8)],
                      '3 cells (a skill with and without), 8 battles')


@gate
def design_rows():
    m = importlib.import_module('design_rows')
    m.ENGINE = False
    spikes = [('C10', 10), ('C26', 10)]
    cells = [('Meta', 'C30', 10), ('Dual-Support', 'C30', 10)]
    with contextlib.redirect_stdout(io.StringIO()):
        a, tp = timed(lambda: ([m.spike(t) for t in spikes], [m.no_magic_cell(t) for t in cells]))
        m.ENGINE = True
        b, te = timed(lambda: ([m.spike(t) for t in spikes], [m.no_magic_cell(t) for t in cells]))
    m.ENGINE = False
    t, d = count(a, b)
    return row('design_rows', '2 spike cells (largest hit from the recorder) and 2 anti-magic cells, 10 battles', t, d, tp, te)


def main_gate(name, module_name, argv, what, env_flag=True):
    """A script that only prints: its main() with and without --engine, the printed text compared."""
    m = importlib.import_module(module_name)
    old = sys.argv
    try:
        sys.argv = [module_name + '.py'] + list(argv)
        a, tp = captured(m.main)
        sys.argv = [module_name + '.py'] + list(argv) + ['--engine']
        b, te = captured(m.main)
    finally:
        sys.argv = old
        if hasattr(m, 'ENGINE'):
            m.ENGINE = False
    t, d = count(a.splitlines(), b.splitlines())
    return row(name, what, t, d, tp, te)


@gate
def etoile_dances():
    return main_gate('etoile_dances', 'etoile_dances', ['C26', '8'], '6 pairs of dances, 8 battles')


@gate
def samba_trial():
    return main_gate('samba_trial', 'samba_trial', ['C26', '8'], 'Samba at 4 factors, 8 battles')


@gate
def provoke_trial():
    return main_gate('provoke_trial', 'provoke_trial', ['C26', '8', '300,400,500,600,700'], 'Provoke at 3 sizes, 8 battles')


@gate
def etoile_trial():
    return main_gate('etoile_trial', 'etoile_trial', ['C30', '8'], 'two parties with the dances at 2 factors, 8 battles')


@gate
def tp_items_trial():
    return main_gate('tp_items_trial', 'tp_items_trial', ['C30', '8'], '4 bags of fruit, 8 battles')


@gate
def grand_sealbook_trial():
    return main_gate('grand_sealbook_trial', 'grand_sealbook_trial', ['955', 'P24', '8'], 'a grand sealbook with one and two enchantments, 8 battles')


@gate
def lize_ideas():
    return main_gate('lize_ideas', 'lize_ideas', ['papillon', 'C26', '8'], '5 ideas for a unique skill, 8 battles')


@gate
def unique_trial():
    return main_gate('unique_trial', 'unique_trial', ['Lilian', '1.5', '2', '8'], 'a unique skill at 2 sizes, 8 battles')


@gate
def unique_trial_random():
    return main_gate('unique_trial_random', 'unique_trial_random', ['Lilian', 'C36', '2', '6'], 'a unique skill at 1 size on rows of random battles, 6 rows')


@gate
def random_parties():
    return main_gate('random_parties', 'random_parties', ['C26', '4', 'Meta'], 'one party on rows of random battles on 7 data sets, 4 rows')


@gate
def mercenary_trial():
    return main_gate('mercenary_trial', 'mercenary_trial', ['Marion', 'C40', '8', 'atk=1.5'], 'a guest with her ATK scaled, 8 battles')


@gate
def magic_wall():
    return main_gate('magic_wall', 'magic_wall', [], 'the best option of the mage and the Dark Lord at every boss from C30, both sides')


@gate
def worth_with_weapon():
    return main_gate('worth_with_weapon', 'worth_with_weapon', ['Bible Thump', 'sage', 'Tome'], 'a skill that needs another weapon, at the advanced and late stages')


@gate
def measure_open_rows():
    import measure_open_rows as m
    folder, saved = patched_dir(m, 'measure_open_rows_py')
    path = os.path.join(folder, 'open_rows_Bible_Thump.json')
    old = sys.argv
    try:
        sys.argv = ['measure_open_rows.py', 'Bible Thump']
        with contextlib.redirect_stdout(io.StringIO()):
            _, tp = timed(m.main)
        a = json.load(open(path, encoding='utf-8'))
        os.remove(path)
        sys.argv = ['measure_open_rows.py', 'Bible Thump', '--engine']
        with contextlib.redirect_stdout(io.StringIO()):
            _, te = timed(m.main)
        b = json.load(open(path, encoding='utf-8'))
    finally:
        sys.argv = old
        m.HERE = saved
        m.ENGINE = False
    t, d = count(a, b)
    return row('measure_open_rows', 'one skill with and without it at the checkpoints of its stage', t, d, tp, te)


@gate
def regression_r04():
    import regression_r04 as m
    folder, saved = patched_dir(m, 'regression_r04_py')
    path = os.path.join(folder, 'regression_r04_3.json')
    m.ENGINE = False
    with contextlib.redirect_stdout(io.StringIO()):
        _, tp = timed(m.play, '3/40', 6)
        a = json.load(open(path, encoding='utf-8'))
        os.remove(path)
        m.ENGINE = True
        _, te = timed(m.play, '3/40', 6)
    m.ENGINE = False
    b = json.load(open(path, encoding='utf-8'))
    m.HERE = saved
    t, d = count(a, b)
    return row('regression_r04', 'a slice of the pairs of boss and class: parties without the class, 6 battles', t, d, tp, te)


def main():
    args = sys.argv[1:]
    if args == ['--list']:
        print('\n'.join(GATES))
        return
    names = args or list(GATES)
    rows = []
    for name in names:
        try:
            r = GATES[name]()
        except Exception as ex:           # a gate that fails to run is a failure of the gate, said plainly
            import traceback
            r = {'gate': name, 'what': 'FAILED TO RUN: ' + repr(ex), 'values': 0, 'differences': -1, 'python_s': 0, 'engine_s': 0, 'note': traceback.format_exc()[-400:]}
        rows.append(r)
        print(f"{r['gate']:24s} values {r['values']:7d}  differences {r['differences']:3d}  python {r['python_s']:7.1f} s  engine {r['engine_s']:6.1f} s  | {r['what']}"
              + (f"  [{r['note']}]" if r['note'] else ''), flush=True)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'gate_tools.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=1)
    print(sum(r['values'] for r in rows), 'values compared,', sum(max(0, r['differences']) for r in rows), 'differences,',
          sum(1 for r in rows if r['differences'] < 0), 'gates that failed to run')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

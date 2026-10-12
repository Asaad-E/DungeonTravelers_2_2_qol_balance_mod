"""
Every class at the stage of the game where it is played, against several bosses of that stage. Generated:
docs/generated/CLASS_STAGES.md.

    python tools/class_stages.py all [stage]          every checkpoint, slices in parallel processes
    python tools/class_stages.py run <checkpoint> [k/n]  one checkpoint (or a slice of its roles)
    python tools/class_stages.py report               joins the checkpoints measured

The sheet ClassStages of data_tables/sim_setup.xlsx names the stages (base, intermediate, advanced, late) and their
checkpoints; a role has at each checkpoint the class its path gives at the reference level (scenario.class_path: the
Lv15 class from 15, the Lv30 class from 30). On the Balance variant (sim/variant.py), the reference party of the
checkpoint plays its boss fights once as it is and once for each role of the sheet Roles, that role taking the place
of the last member (the role's first character not already in the party). For each role: wins, the mean length of
the fights and its share of the party's damage (its dolls and summons counted as its own). The report gives, stage by
stage, each class's length against the median of the stage: a figure above class_slow_ratio (Settings) is slow.
"""
import json
import os
import statistics
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
# CLASS_STAGES_PROPOSED=1: the variant with the rows of balance_changes.xlsx still proposed, measured apart
PROPOSED = os.environ.get('CLASS_STAGES_PROPOSED') == '1'
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'class_stages_proposed' if PROPOSED else 'class_stages')
REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'CLASS_STAGES_PROPOSED.md' if PROPOSED else 'CLASS_STAGES.md')

from sim import scenario                                # noqa: E402
from sim import setup as setup_mod                      # noqa: E402
from sim.data import game_data                          # noqa: E402
from sim.units import PARTY                             # noqa: E402
from sim.variant import balance_data                    # noqa: E402


def stages(setup):
    import openpyxl
    wb = openpyxl.load_workbook(setup_mod.SETUP, read_only=True)
    rows = list(wb['ClassStages'].iter_rows(values_only=True))
    return [dict(zip(rows[0], r)) for r in rows[1:] if r[0]]


def play(data, setup, cid, role, runs):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}
    tested_name = [None]

    def party():
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        members = [u for u in whole if u.kind == 'member']
        others = [u for u in whole if u.kind != 'member']
        if role is None:
            return whole
        kept = members[:-1]
        names = [n.strip() for n in str(setup.roles[role]['Characters (order of preference)']).split(';')]
        taken = {u.name for u in kept}
        base = scenario.class_id(data, setup.roles[role]['Base class'])
        who = next((n for n in names if n in chars and n not in taken), None) or \
            next(c['name'] for c in data.characters if c['name'] not in taken and c['base_class'] == base)
        tested = scenario.build_role_member(data, setup, role, chars[who], level, gear, 0,
                                            scenario.forge_open(setup, cp['Floor']))
        tested_name[0] = who
        for u in kept:
            tested.items = u.items
        return kept + [tested] + others

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    res = scenario.play(data, setup, party, enemies, runs=runs)
    share = 0.0
    for r in res:
        for p in r['parts']:
            dmg = p['record'].damage
            total = sum(v for u, v in dmg.items() if u.side == PARTY) or 1
            mine = sum(v for u, v in dmg.items() if u.side == PARTY and
                       (getattr(u, 'owner', None) or u).name == tested_name[0] and
                       getattr(getattr(u, 'owner', None) or u, 'role', None) == role)
            share += mine / total / len(r['parts'])
    won = [r for r in res if r['won']]
    return {'won': len(won) / runs, 'time': sum(r['time'] for r in res) / runs,
            'time_won': sum(r['time'] for r in won) / len(won) if won else None,
            'share': share / runs, 'character': tested_name[0], 'level': level}


def run(cid, part='1/1'):
    """One checkpoint, or the k-th of n slices of its roles (part 'k/n')."""
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    if PROPOSED:
        from sim.variant import apply, rows
        data = apply(data, rows(states=('decided', 'built', 'checked', 'proposed')))
    else:
        data = balance_data(data)
    runs = int(setup.settings['check_runs'])
    level = scenario.reference_levels(data, setup)[cid][0]
    out = {'base': play(data, setup, cid, None, runs) if k == 1 else None, 'roles': {}}
    roles = list(setup.roles.items())
    for role, row in roles[(k - 1) * len(roles) // n: k * len(roles) // n]:
        cls, _ = scenario.class_path(data, row, level)
        r = play(data, setup, cid, role, runs)
        r['class'] = data.class_names.get(cls)
        out['roles'][role] = r
        print(cid, role, r['class'], f"won {r['won']:.0%} t {r['time']:.1f} share {r['share']:.0%}", flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f'{cid}_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def run_all(stage=None):
    """Every checkpoint of the sheet (or of one stage), each split in slices of roles, run in parallel_workers
    processes at once (Settings): each process loads the data alone (about 80 MB) and frees it when it ends."""
    import subprocess
    import time
    setup = setup_mod.load()
    workers = int(setup.settings.get('parallel_workers', 1))
    slices = int(setup.settings.get('parallel_slices', 1))
    jobs = [(c.strip(), f'{k}/{slices}') for st in stages(setup) if stage in (None, st['Stage'])
            for c in str(st['Checkpoints']).split(';') for k in range(1, slices + 1)]
    running, done = [], 0
    started = time.time()
    while jobs or running:
        while jobs and len(running) < workers:
            cid, part = jobs.pop(0)
            running.append((cid, part, subprocess.Popen([sys.executable, os.path.abspath(__file__), 'run', cid, part],
                                                        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)))
        for item in list(running):
            if item[2].poll() is not None:
                running.remove(item)
                done += 1
                err = item[2].stderr.read().decode('utf-8', 'replace').strip()
                print(f'{item[0]} {item[1]} {"failed: " + err.splitlines()[-1] if item[2].returncode else "done"} '
                      f'({done}, {time.time() - started:.0f} s)', flush=True)
        time.sleep(0.5)


def kinds():
    import openpyxl
    wb = openpyxl.load_workbook(setup_mod.SETUP, read_only=True)
    return {r[0]: r[1] for r in wb['ClassKinds'].iter_rows(min_row=2, values_only=True) if r[0]}


def report():
    """Stage by stage. A checkpoint where the median role wins less than half is hard for every class: it is listed
    apart and left out of the verdicts. An attacker is judged by the length of the fights it wins against the
    median attacker of the checkpoint (slow above class_slow_ratio); a support or a tank by its share of wins in the
    contested fights of the stage (those the median role does not always win), against the median role (weak below it
    by class_weak_wins). Kinds: sheet ClassKinds."""
    setup = setup_mod.load()
    slow, weak = float(setup.settings['class_slow_ratio']), float(setup.settings['class_weak_wins'])
    by_class = kinds()

    def kind_of(role, cls):
        """The kind a role is judged as: the kind of the class she has at the stage, unless the class her path ends in
        is a support. Her build is then the one of a support from level 1, whatever her first class deals with: a
        healer of level 5 is a Magic User, an attacker by her class, and holds Heal."""
        return 'support' if by_class.get(setup.roles[role]['Lv30 class']) == 'support' else by_class.get(cls, 'attacker')

    text = ['# Every class at its stage (generated)', '',
            'Generated by `tools/class_stages.py`. Do not edit. Balance variant; each role takes the last place of the '
            'reference party of the checkpoint (15 fights each). Cells: wins / length of the won fights against the '
            'median attacker / share of the party damage. An attacker is slow above '
            f'{slow:.2f}; a support or tank is weak when its wins in the contested fights fall {weak:.0%} below the '
            'median. Kinds of class: sheet ClassKinds; a role whose path ends in a support class is a support at every stage.', '']
    rows_out = []
    for st in stages(setup):
        cids = [c.strip() for c in str(st['Checkpoints']).split(';')]
        measured = {}
        for c in cids:
            for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
                if name.startswith(c + '_') and name.endswith('.json'):
                    with open(os.path.join(OUT_DIR, name), encoding='utf-8') as f:
                        part = json.load(f)
                    measured.setdefault(c, {'roles': {}})['roles'].update(part['roles'])
        text += [f"## {st['Stage']} ({', '.join(cids)})", '']
        if not measured:
            text += ['Not measured yet.', '']
            continue
        hard = [c for c, m in measured.items() if statistics.median(r['won'] for r in m['roles'].values()) < 0.5]
        usable = [c for c in measured if c not in hard]
        contested = [c for c in usable if statistics.median(r['won'] for r in measured[c]['roles'].values()) < 1.0]
        att_median = {}
        for c in usable:
            times = [r['time_won'] for name, r in measured[c]['roles'].items()
                     if kind_of(name, r['class']) == 'attacker' and r.get('time_won')]
            att_median[c] = statistics.median(times) if times else None
        win_median = {c: statistics.median(r['won'] for r in measured[c]['roles'].values()) for c in contested}
        if hard:
            text += ['Hard for every class (median wins below half; out of the verdicts): ' + ', '.join(
                f"{c} ({statistics.median(r['won'] for r in measured[c]['roles'].values()):.0%})" for c in hard) + '.', '']
        text += ['| Role | Class | Kind | ' + ' | '.join(measured) + ' | Measure | Verdict |',
                 '|' + '---|' * (5 + len(measured))]
        for role in setup.roles:
            cells, cls = [], None
            for c, m in measured.items():
                r = m['roles'].get(role)
                if r is None:
                    cells.append('-')
                    continue
                cls = r['class']
                ratio = r['time_won'] / att_median[c] if c in usable and att_median.get(c) and r.get('time_won') else None
                cells.append(f"{r['won']:.0%} / {'-' if ratio is None else f'{ratio:.2f}'} / {r['share']:.0%}")
            kind = kind_of(role, cls)
            if kind == 'attacker':
                ratios = [measured[c]['roles'][role]['time_won'] / att_median[c] for c in usable
                          if att_median.get(c) and measured[c]['roles'].get(role, {}).get('time_won')]
                value = sum(ratios) / len(ratios) if ratios else None
                verdict = 'slow' if value is not None and value > slow else 'within'
                measure = f'length {value:.2f}' if value is not None else 'no win'
            else:
                gaps = [measured[c]['roles'][role]['won'] - win_median[c] for c in contested if role in measured[c]['roles']]
                value = sum(gaps) / len(gaps) if gaps else None
                verdict = 'weak' if value is not None and value < -weak else 'within'
                measure = f'wins {value:+.0%} on the median' if value is not None else 'no contested fight'
            rows_out.append(verdict)
            text.append(f'| {role} | {cls} | {kind} | ' + ' | '.join(cells) + f' | {measure} | {verdict} |')
        text.append('')
    bad = sum(1 for v in rows_out if v != 'within')
    text[4:4] = [f'**{len(rows_out) - bad} of {len(rows_out)} role and stage rows within the band, {bad} slow or weak.**', '']
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print(text[4])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'run': run, 'all': run_all, 'report': report}[sys.argv[1]](*sys.argv[2:])

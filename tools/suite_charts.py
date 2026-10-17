"""Charts of the generated reports (run by tools/full_suite.py after dtcli suite); docs/generated/charts, kept in git.

class_balance.png      CLASS_BALANCE.md (class-balance): the final classes in six figures, vanilla and the variant, the band of section
                       class_search (mean +- z standard deviations)
class_stages.png       CLASS_STAGES.md (class-stages): by stage, the attackers by length against the median attacker, the supports and
                       tanks by wins against the median (by length where no fight is contested); thresholds class_slow_ratio and
                       class_weak_wins of the sheet Settings
difficulty_curve.png   DIFFICULTY_CURVE.md and CHECKPOINT_LEVELS.md: wins, length and lowest HP of the reference party at every checkpoint,
                       vanilla and the variant, the checkpoints out of the windows of vanilla; the reference level and the level of the boss
random_battles.png     measures/RANDOM_BATTLES.md: rows of random battles at the floor of each checkpoint, one bag for the row, vanilla and
                       the variant: rows survived, length of a battle, lowest HP, TP left; out of the window shaded
party_battery.png      PARTY_BATTERY.md: the wins of each archetype at each boss on the variant (a cell under its floor framed) and the change
                       from vanilla
skills.png             SKILL_BATTERY.md (with SKILL_BATTERY_VARIANTS.md for the skills played again under every rule of use) and
                       UNIQUE_BATTERY.md: each skill by the share of the cells where it serves and where it hurts, coloured by verdict;
                       each unique skill the same, by girl

The figures come from the reports; the thresholds from the workbooks. Nothing here plays a battle. A report that is missing is skipped.
"""
import json
import os
import re
import statistics
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib.ticker import PercentFormatter      # noqa: E402
import openpyxl                                     # noqa: E402

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED = os.path.join(PROJECT, 'docs', 'generated')
OUT = os.path.join(GENERATED, 'charts')
OUT_OF_BAND = 'tab:red'


def settings():
    ws = openpyxl.load_workbook(os.path.join(PROJECT, 'data_tables', 'sim_setup.xlsx'), read_only=True)['Settings']
    return {r[0]: r[1] for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}


def table(lines, header_start):
    """The rows of the first markdown table whose header starts so, as lists of cells."""
    i = next(k for k, line in enumerate(lines) if line.startswith(header_start))
    rows = []
    for line in lines[i + 2:]:
        if not line.startswith('|'):
            break
        rows.append([c.strip() for c in line.strip().strip('|').split('|')])
    return rows


def num(text):
    return float(re.sub(r'[^0-9.+-]', '', text))


def colours(names):
    maps = [plt.get_cmap('tab20'), plt.get_cmap('tab20b'), plt.get_cmap('tab20c')]
    return {n: maps[i // 20](i % 20) for i, n in enumerate(sorted(names))}


def mark_labels(ax, labels, out):
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=60, ha='right', fontsize=8)
    for lab, bad in zip(ax.get_xticklabels(), out):
        if bad:
            lab.set_color(OUT_OF_BAND)
            lab.set_fontweight('bold')


def pad(ax, values, low=None, high=None, share=0.15):
    """Limits that fit the points with a margin, and keep the given lines in view."""
    vals = [v for v in values if v is not None and v == v] + [x for x in (low, high) if x is not None]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or abs(hi) or 1
    ax.set_ylim(lo - span * share, hi + span * share)


def class_balance(z):
    lines = open(os.path.join(GENERATED, 'CLASS_BALANCE.md'), encoding='utf-8').read().splitlines()
    band = {r[0]: r for r in table(lines, '| Class | Wins | Deviations')}
    scan = {r[0]: r for r in table(lines, '| Class | Cells')}
    classes = sorted(band, key=lambda c: -num(band[c][1]))
    pair = lambda s: [num(x) for x in s.split('>')]
    metrics = [
        ('Wins of the parties that hold the class', lambda c: pair(scan[c][2])[0], lambda c: pair(scan[c][2])[1], '% of fights won'),
        ('Length of the fights won', lambda c: pair(scan[c][3])[0], lambda c: pair(scan[c][3])[1], 'turns (lower = faster)'),
        ('Lowest HP of the party', lambda c: pair(scan[c][4])[0], lambda c: pair(scan[c][4])[1], '% of HP'),
        ('Among the fastest 5%', lambda c: pair(scan[c][5])[0], lambda c: pair(scan[c][5])[1], '% of the fastest parties'),
        ('Speed: one of the class', None, lambda c: num(band[c][3]), 'times the mean (1 = mean)'),
        ('Speed: two or more of the class', None, lambda c: num(band[c][5]) if band[c][5] != '-' else float('nan'), 'times the mean'),
    ]
    colour = colours(classes)
    fig, axes = plt.subplots(3, 2, figsize=(15, 15))
    for ax, (title, vanilla, variant, label) in zip(axes.flat, metrics):
        ys = [variant(c) for c in classes]
        good = [y for y in ys if y == y]
        mean, sd = statistics.mean(good), statistics.stdev(good)
        ax.axhspan(mean - z * sd, mean + z * sd, color='0.92', zorder=0, label='band (mean +- %g sd)' % z)
        ax.axhline(mean, color='0.5', lw=1, ls='--', zorder=1, label='mean')
        out = []
        shown = list(ys)
        for x, c in enumerate(classes):
            y = ys[x]
            if vanilla:
                v = vanilla(c)
                shown.append(v)
                ax.scatter(x, v, s=70, facecolors='none', edgecolors=colour[c], lw=1.5, zorder=2)
                ax.annotate('', (x, y), (x, v), arrowprops=dict(arrowstyle='->', color=colour[c], lw=1), zorder=2)
            ax.scatter(x, y, s=110, color=colour[c], edgecolors='k', lw=0.6, zorder=3)
            out.append(y == y and abs(y - mean) > z * sd)
        pad(ax, shown, mean - z * sd, mean + z * sd, 0.08)
        mark_labels(ax, classes, out)
        ax.set_title(title + ('  (hollow: vanilla, filled: Balance)' if vanilla else '  (Balance)'), fontsize=11)
        ax.set_ylabel(label)
        ax.grid(axis='y', alpha=0.3)
    axes.flat[0].legend(loc='lower left', fontsize=9)
    head = next(line for line in lines if line.startswith('Over the '))
    fig.suptitle('Final classes, class-balance of the suite: ' + head.split(',')[0].replace('Over the ', '') + '; red: out of the band',
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    path = os.path.join(OUT, 'class_balance.png')
    fig.savefig(path, dpi=100, metadata={'Software': None})
    plt.close(fig)
    return path


def class_stages(slow, weak):
    lines = open(os.path.join(GENERATED, 'CLASS_STAGES.md'), encoding='utf-8').read().splitlines()
    stages, cur = [], None
    for line in lines:
        m = re.match(r'## (\w+) \((.*)\)', line)
        if m:
            cur = {'name': m.group(1), 'cids': [x.strip() for x in m.group(2).split(',')], 'rows': []}
            stages.append(cur)
        elif cur and line.startswith('| ') and not line.startswith('| Role') and '---' not in line:
            cells = [x.strip() for x in line.strip().strip('|').split('|')]
            pts = []
            for p in cells[3:-2]:
                parts = [x.strip() for x in p.split('/')]
                if len(parts) == 3:
                    pts.append((float(parts[0].rstrip('%')) / 100, None if parts[1] == '-' else float(parts[1])))
            length = re.search(r'length ([\d.]+)', cells[-2])
            gap = re.search(r'wins ([+-]\d+)%', cells[-2])
            cur['rows'].append({'role': cells[0], 'cls': cells[1], 'kind': cells[2], 'pts': pts, 'out': cells[-1] != 'within',
                                'length': float(length.group(1)) if length else None,
                                'gap': int(gap.group(1)) / 100 if gap else None})
    colour = colours({r['cls'] for s in stages for r in s['rows']})
    head = next(line for line in lines if line.startswith('Generated by'))
    fights = re.search(r'(\d+) a cell', head)
    fig, axes = plt.subplots(len(stages), 2, figsize=(16, 4.8 * len(stages)), gridspec_kw={'width_ratios': [3, 2]})
    for row, st in enumerate(stages):
        attackers = sorted([r for r in st['rows'] if r['kind'] == 'attacker'], key=lambda r: r['length'] or 9)
        others = [r for r in st['rows'] if r['kind'] != 'attacker']
        label = lambda r: r['cls'] + ('\n(' + r['role'] + ')' if r['role'].lower() != r['cls'].lower() else '')
        # attackers: length against the median attacker of the party, each boss and the mean
        ax = axes[row][0]
        ax.axhline(1.0, color='0.5', ls='--', lw=1)
        ax.axhline(slow, color=OUT_OF_BAND, ls=':', lw=1.2, label='slow above %g' % slow)
        shown = []
        for x, r in enumerate(attackers):
            for _, ratio in r['pts']:
                if ratio is not None:
                    ax.scatter(x, ratio, s=18, color=colour[r['cls']], alpha=0.45, zorder=2)
                    shown.append(ratio)
            if r['length'] is not None:
                ax.scatter(x, r['length'], s=120, color=colour[r['cls']], edgecolors='k', lw=0.7, zorder=3, marker='X' if r['out'] else 'o')
                shown.append(r['length'])
        pad(ax, shown, 1.0, slow)
        mark_labels(ax, [label(r) for r in attackers], [r['out'] for r in attackers])
        ax.set_ylabel('length against the median attacker\n(lower = faster)')
        ax.set_title(st['name'] + ' (' + ', '.join(st['cids']) + '): attackers', fontsize=11)
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(axis='y', alpha=0.3)
        # supports and tanks: wins against the median in the contested fights; where none is contested, the length of the fights
        ax = axes[row][1]
        contested = [r for r in others if r['gap'] is not None]
        if contested:
            others.sort(key=lambda r: -(r['gap'] if r['gap'] is not None else 0))
            ax.axhline(0, color='0.5', ls='--', lw=1)
            ax.axhline(-weak, color=OUT_OF_BAND, ls=':', lw=1.2, label='weak below -%d%%' % round(100 * weak))
            shown = []
            for x, r in enumerate(others):
                if r['gap'] is None:
                    continue
                ax.scatter(x, r['gap'], s=120, color=colour[r['cls']], edgecolors='k', lw=0.7, zorder=3, marker='X' if r['out'] else 'o')
                shown.append(r['gap'])
            pad(ax, shown, 0, -weak)
            ax.yaxis.set_major_formatter(PercentFormatter(1.0))
            ax.set_ylabel('wins against the median\n(contested fights)')
            ax.set_title(st['name'] + ': supports and tanks, wins', fontsize=11)
            ax.legend(loc='lower left', fontsize=8)
        else:
            means = {}
            for r in others:
                ratios = [ratio for _, ratio in r['pts'] if ratio is not None]
                means[r['role']] = sum(ratios) / len(ratios) if ratios else None
            others.sort(key=lambda r: means[r['role']] if means[r['role']] is not None else 9)
            ax.axhline(1.0, color='0.5', ls='--', lw=1)
            shown = []
            for x, r in enumerate(others):
                for _, ratio in r['pts']:
                    if ratio is not None:
                        ax.scatter(x, ratio, s=18, color=colour[r['cls']], alpha=0.45, zorder=2)
                        shown.append(ratio)
                if means[r['role']] is not None:
                    ax.scatter(x, means[r['role']], s=120, color=colour[r['cls']], edgecolors='k', lw=0.7, zorder=3)
                    shown.append(means[r['role']])
            pad(ax, shown, 1.0)
            ax.set_ylabel('length of the party\'s fights against\nthe median attacker (lower = faster)')
            ax.set_title(st['name'] + ': supports and tanks (every fight won: by length)', fontsize=11)
        mark_labels(ax, [label(r) for r in others], [r['out'] for r in others])
        ax.grid(axis='y', alpha=0.3)
    fig.suptitle('class-stages: each role at the bosses of its stage' + (', ' + fights.group(1) + ' fights a cell' if fights else '')
                 + '. Large point: mean; small points: each boss; red X: out of the band', fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    path = os.path.join(OUT, 'class_stages.png')
    fig.savefig(path, dpi=100, metadata={'Software': None})
    plt.close(fig)
    return path


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=100, metadata={'Software': None})
    plt.close(fig)
    return path


def lines_of(name):
    return open(os.path.join(GENERATED, name), encoding='utf-8').read().splitlines()


def difficulty_curve():
    curve = [r for r in table(lines_of('DIFFICULTY_CURVE.md'), '| Checkpoint | Level')]
    levels = {r[0]: r for r in table(lines_of('CHECKPOINT_LEVELS.md'), '| Checkpoint | Boss')}
    cids = [r[0] for r in curve]
    pair = lambda s: [num(x) for x in s.split('>')]
    x = list(range(len(cids)))
    fig, axes = plt.subplots(4, 1, figsize=(17, 15), sharex=True)
    panels = [('Wins of the reference party', 2, '% of fights won', True), ('Length of the fights', 3, 'turns', False),
              ('Lowest HP of the party', 4, '% of HP', True)]
    for ax, (title, col, label, pct) in zip(axes, panels):
        van = [pair(r[col])[0] for r in curve]
        var = [pair(r[col])[1] for r in curve]
        ax.plot(x, van, color='0.55', lw=1.4, marker='o', ms=4, label='vanilla')
        ax.plot(x, var, color='tab:blue', lw=1.8, marker='o', ms=5, label='Balance')
        for k, r in enumerate(curve):
            verdict = r[-1]
            if verdict == 'within':
                continue
            colour = 'tab:green' if 'easier' in verdict and 'harder' not in verdict else 'tab:red' if 'harder' in verdict else 'tab:orange'
            ax.axvspan(k - 0.45, k + 0.45, color=colour, alpha=0.12, zorder=0)
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(label)
        ax.grid(alpha=0.3)
    axes[0].legend(loc='lower left', fontsize=9)
    ax = axes[3]
    ref = [num(levels[c][5]) if c in levels and levels[c][5] not in ('', '-') else float('nan') for c in cids]
    boss = [num(levels[c][2]) if c in levels and levels[c][2] not in ('', '-') else float('nan') for c in cids]
    ax.plot(x, boss, color='tab:red', lw=1.2, marker='s', ms=4, label='level of the boss')
    ax.plot(x, ref, color='tab:blue', lw=1.8, marker='o', ms=5, label='reference level of the party')
    ax.set_title('Levels', fontsize=11)
    ax.set_ylabel('level')
    ax.grid(alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(cids, rotation=90, fontsize=8)
    head = next(line for line in lines_of('DIFFICULTY_CURVE.md') if line.startswith('**'))
    fig.suptitle('Difficulty curve: ' + head.strip('*') + ' Shaded: out of the window (green easier, red harder)', fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return save(fig, 'difficulty_curve.png')


def random_battles():
    lines = lines_of(os.path.join('..', '..', 'measures', 'RANDOM_BATTLES.md'))
    rows = table(lines, '| Floor of | Level')
    cids = [r[0] for r in rows]
    x = list(range(len(cids)))

    def pair(s):
        return [None if v.strip() == '-' else num(v) for v in s.split('>')]
    panels = [('Rows survived', 2, '% of the rows'), ('Length of a battle', 3, 'turns'), ('Lowest HP of the party in the row', 4, '% of HP'),
              ('TP the row ends with', 7, '% of TP')]
    fig, axes = plt.subplots(len(panels), 1, figsize=(17, 13), sharex=True)
    for ax, (title, col, label) in zip(axes, panels):
        van = [pair(r[col])[0] for r in rows]
        var = [pair(r[col])[1] for r in rows]
        ax.plot(x, [float('nan') if v is None else v for v in van], color='0.55', lw=1.4, marker='o', ms=4, label='vanilla')
        ax.plot(x, [float('nan') if v is None else v for v in var], color='tab:blue', lw=1.8, marker='o', ms=5, label='Balance')
        for k, r in enumerate(rows):
            verdict = r[-1]
            if verdict == 'within':
                continue
            colour = 'tab:green' if 'easier' in verdict and 'harder' not in verdict else 'tab:red' if 'harder' in verdict else 'tab:orange'
            ax.axvspan(k - 0.45, k + 0.45, color=colour, alpha=0.12, zorder=0)
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(label)
        ax.grid(alpha=0.3)
    axes[0].legend(loc='lower left', fontsize=9)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(cids, rotation=90, fontsize=8)
    head = next(line for line in lines if line.startswith('**'))
    about = next(line for line in lines if line.startswith('Generated by'))
    size = re.search(r'(\d+) rows of (\d+) random battles', about)
    fig.suptitle('Random battles: ' + (size.group(1) + ' rows of ' + size.group(2) + ' battles in a row at the floor of each checkpoint, one bag for the row'
                                        if size else '') + '\n' + head.strip('*') + '\nShaded: out of the window (green easier, red harder)', fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return save(fig, 'random_battles.png')


def party_battery():
    lines = lines_of('PARTY_BATTERY.md')
    rows = table(lines, '| Checkpoint | Boss | Floor')
    i = next(k for k, line in enumerate(lines) if line.startswith('| Checkpoint | Boss | Floor'))
    parties = [c.strip() for c in lines[i].strip().strip('|').split('|')][3:]
    van, var, below, labels = [], [], [], []
    for r in rows:
        floor = num(r[2]) / 100
        labels.append(r[0] + ' ' + r[1][:22])
        a, b, under = [], [], []
        for cell in r[3:]:
            bold = '**' in cell
            v, w = [num(x) / 100 for x in cell.replace('*', '').split('>')]
            a.append(v)
            b.append(w)
            under.append(bold or w < floor)
        van.append(a)
        var.append(b)
        below.append(under)
    fig, axes = plt.subplots(1, 2, figsize=(16, 0.42 * len(rows) + 3))
    im = axes[0].imshow(var, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
    for k, under in enumerate(below):
        for j, u in enumerate(under):
            axes[0].text(j, k, '%d' % round(100 * var[k][j]), ha='center', va='center', fontsize=8, fontweight='bold' if u else None)
            if u:
                axes[0].add_patch(plt.Rectangle((j - 0.5, k - 0.5), 1, 1, fill=False, edgecolor='k', lw=2))
    fig.colorbar(im, ax=axes[0], fraction=0.04, format=PercentFormatter(1.0))
    axes[0].set_title('Wins on the variant (framed: under the floor of the boss)', fontsize=11)
    change = [[var[k][j] - van[k][j] for j in range(len(parties))] for k in range(len(rows))]
    im = axes[1].imshow(change, cmap='coolwarm_r', vmin=-0.5, vmax=0.5, aspect='auto')
    for k in range(len(rows)):
        for j in range(len(parties)):
            if abs(change[k][j]) >= 0.005:
                axes[1].text(j, k, '%+d' % round(100 * change[k][j]), ha='center', va='center', fontsize=8)
    fig.colorbar(im, ax=axes[1], fraction=0.04, format=PercentFormatter(1.0))
    axes[1].set_title('Change from vanilla (points of wins)', fontsize=11)
    for ax in axes:
        ax.set_xticks(range(len(parties)))
        ax.set_xticklabels(parties, rotation=30, ha='right', fontsize=9)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(labels, fontsize=8)
    head = next(line for line in lines if line.startswith('**'))
    fig.suptitle('Party battery: ' + head.strip('*'), fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return save(fig, 'party_battery.png')


VERDICT_COLOURS = {'good': 'tab:green', 'niche': 'tab:orange', 'dead': '0.4', 'hurts': 'tab:red', 'no effect': 'tab:purple'}


def skills():
    have_skills = os.path.exists(os.path.join(GENERATED, 'SKILL_BATTERY.md'))
    have_unique = os.path.exists(os.path.join(GENERATED, 'UNIQUE_BATTERY.md'))
    if not (have_skills or have_unique):
        return None
    fig, axes = plt.subplots(1, 2, figsize=(17, 9), gridspec_kw={'width_ratios': [3, 2]})
    if have_skills:
        lines = lines_of('SKILL_BATTERY.md')
        rows = table(lines, '| Skill | Kind')
        # a skill the suite played again under the rules of rule_variants is read by that pass (SKILL_BATTERY_VARIANTS.md)
        again = {}
        if os.path.exists(os.path.join(GENERATED, 'SKILL_BATTERY_VARIANTS.md')):
            again = {r[0]: r for r in table(lines_of('SKILL_BATTERY_VARIANTS.md'), '| Skill | Kind')}
        rows = [again.get(r[0], r) for r in rows]
        ax = axes[0]
        for verdict, colour in VERDICT_COLOURS.items():
            pts = [(num(r[4]) / 100, num(r[5]) / 100, r[0]) for r in rows if r[-1] == verdict]
            if pts:
                ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=36, color=colour, alpha=0.75, edgecolors='k', lw=0.3,
                           label='%s (%d)' % (verdict, len(pts)))
            # the names of the skills that hurt or are dead, so they can be found
            if verdict in ('hurts', 'dead'):
                for sx, sy, name in pts:
                    ax.annotate(name, (sx, sy), textcoords='offset points', xytext=(4, 2), fontsize=6.5, color=colour)
        ax.set_xlabel('share of the cells where the skill serves')
        ax.set_ylabel('share of the cells where it makes the fight worse')
        ax.xaxis.set_major_formatter(PercentFormatter(1.0))
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=9, loc='upper right')
        counts = {v: sum(1 for r in rows if r[-1] == v) for v in VERDICT_COLOURS}
        ax.set_title('Skill battery: %d skills, ' % len(rows) + ', '.join('%d %s' % (n, v) for v, n in counts.items())
                     + ('\n(%d read under their best rule of use)' % len(again) if again else ''), fontsize=11)
    else:
        axes[0].axis('off')
    if have_unique:
        lines = lines_of('UNIQUE_BATTERY.md')
        rows = sorted(table(lines, '| Girl | Unique skill'), key=lambda r: num(r[4]))
        ax = axes[1]
        y = range(len(rows))
        serve = [num(r[4]) / 100 for r in rows]
        hurt = [num(r[5]) / 100 for r in rows]
        ax.barh(y, serve, color=[VERDICT_COLOURS.get(r[-1], '0.5') for r in rows], edgecolor='k', lw=0.4)
        ax.barh(y, [-h for h in hurt], color='tab:red', alpha=0.45, edgecolor='k', lw=0.4)
        for verdict in sorted({r[-1] for r in rows}):
            ax.barh([0], [0], color=VERDICT_COLOURS.get(verdict, '0.5'), label=verdict)
        ax.barh([0], [0], color='tab:red', alpha=0.45, label='makes it worse')
        ax.axvline(0, color='k', lw=0.8)
        ax.set_yticks(list(y))
        ax.set_yticklabels([r[0] + ' - ' + r[1] for r in rows], fontsize=8)
        ax.xaxis.set_major_formatter(PercentFormatter(1.0))
        ax.set_xlabel('share of the cells (left: worse, right: serves; colour: verdict)')
        ax.grid(axis='x', alpha=0.3)
        ax.legend(fontsize=8, loc='lower right')
        head = next(line for line in lines if line.startswith('**'))
        ax.set_title('Unique battery: ' + head.strip('*').split('.')[0].split(': ')[-1], fontsize=11)
    else:
        axes[1].axis('off')
    fig.tight_layout()
    return save(fig, 'skills.png')


def main():
    os.makedirs(OUT, exist_ok=True)
    s = settings()
    z = json.load(open(os.path.join(PROJECT, 'data_tables', 'measure_config.json'), encoding='utf-8'))['class_search']['band']['z']
    charts = [lambda: class_balance(z), lambda: class_stages(float(s['class_slow_ratio']), float(s['class_weak_wins'])),
              difficulty_curve, random_battles, party_battery, skills]
    for chart in charts:
        path = chart()
        if path:
            print('written', os.path.relpath(path, PROJECT))
    return 0


if __name__ == '__main__':
    sys.exit(main())

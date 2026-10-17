"""Charts of the balance of the classes, drawn from the generated reports (run by tools/full_suite.py after dtcli suite).

docs/generated/charts/class_balance.png   docs/generated/CLASS_BALANCE.md (class-balance): the final classes in six figures, vanilla and the
                                          variant, the band of section class_search (mean +- z standard deviations)
docs/generated/charts/class_stages.png    docs/generated/CLASS_STAGES.md (class-stages): by stage, the attackers by length against the median
                                          attacker, the supports and tanks by wins against the median (by length where no fight is contested);
                                          thresholds class_slow_ratio and class_weak_wins of the sheet Settings

The figures come from the reports; the thresholds from the workbooks. Nothing here plays a battle.
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


def main():
    os.makedirs(OUT, exist_ok=True)
    s = settings()
    z = json.load(open(os.path.join(PROJECT, 'data_tables', 'measure_config.json'), encoding='utf-8'))['class_search']['band']['z']
    for path in (class_balance(z), class_stages(float(s['class_slow_ratio']), float(s['class_weak_wins']))):
        print('written', os.path.relpath(path, PROJECT))
    return 0


if __name__ == '__main__':
    sys.exit(main())

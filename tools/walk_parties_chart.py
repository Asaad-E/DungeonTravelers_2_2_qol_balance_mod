"""Charts of dtcli walk-parties (on demand, not part of the suite): build/walk_parties.json -> build/charts/walk_<party>.png, one chart a
party in the layout of docs/generated/charts/random_battles.png: rows survived, length of a battle, lowest HP of the row and TP left,
vanilla and the variant, a checkpoint shaded where the variant leaves the windows of vanilla (Settings check_won_window and
check_lowest_hp_window).

    dotnet .../dtcli.dll walk-parties [battles] [rows] --snapshot build/engine_snapshot.json --root .
    python tools/walk_parties_chart.py
"""
import json
import os
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                     # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suite_charts                                 # noqa: E402

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(PROJECT, 'build', 'walk_parties.json')
OUT = os.path.join(PROJECT, 'build', 'charts')
PANELS = [('Rows survived', 'won', '% of the rows', 100), ('Length of a battle', 'time', 'turns', 1),
          ('Lowest HP of the party in the row', 'lowest_hp', '% of HP', 100), ('TP the row ends with', 'tp_left', '% of TP', 100)]


def value(cell, side, key, scale):
    side = cell.get(side)
    if not side or side.get(key) is None:
        return float('nan')
    return side[key] * scale


def chart(data, party, windows):
    cells = party['cells']
    cids = [c['id'] for c in cells]
    x = list(range(len(cids)))
    fig, axes = plt.subplots(len(PANELS), 1, figsize=(17, 13), sharex=True)
    easier = harder = 0
    for k, c in enumerate(cells):
        if not c.get('vanilla') or not c.get('variant'):
            continue
        dw = c['variant']['won'] - c['vanilla']['won']
        dh = c['variant']['lowest_hp'] - c['vanilla']['lowest_hp']
        out = [d for d, w in ((dw, windows['won']), (dh, windows['lowest_hp'])) if abs(d) > w]
        if not out:
            continue
        better = any(d > 0 for d in out)
        easier += better
        harder += not better
        for ax in axes:
            ax.axvspan(k - 0.45, k + 0.45, color='tab:green' if better else 'tab:red', alpha=0.12, zorder=0)
    for ax, (title, key, label, scale) in zip(axes, PANELS):
        ax.plot(x, [value(c, 'vanilla', key, scale) for c in cells], color='0.55', lw=1.4, marker='o', ms=4, label='vanilla')
        ax.plot(x, [value(c, 'variant', key, scale) for c in cells], color='tab:blue', lw=1.8, marker='o', ms=5, label='Balance')
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(label)
        ax.grid(alpha=0.3)
    axes[0].legend(loc='lower left', fontsize=9)
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(cids, rotation=90, fontsize=8)
    roles = ', '.join(party['roles']) if party.get('roles') else 'the reference party of each checkpoint'
    fig.suptitle('Walk of %s (%s): %d rows of %d random battles at the floor of each checkpoint, one bag for the row\n'
                 '%d checkpoints easier, %d harder in wins or lowest HP (shaded)'
                 % (party['name'], roles, data['rows'], data['battles'], easier, harder), fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    path = os.path.join(OUT, 'walk_' + re.sub(r'[^A-Za-z0-9]+', '_', party['name']).strip('_').lower() + '.png')
    fig.savefig(path, dpi=100, metadata={'Software': None})
    plt.close(fig)
    return path


def main():
    data = json.load(open(SOURCE, encoding='utf-8'))
    s = suite_charts.settings()
    windows = {'won': float(s['check_won_window']), 'lowest_hp': float(s['check_lowest_hp_window'])}
    os.makedirs(OUT, exist_ok=True)
    for party in data['parties']:
        print('written', os.path.relpath(chart(data, party, windows), PROJECT))
    return 0


if __name__ == '__main__':
    sys.exit(main())

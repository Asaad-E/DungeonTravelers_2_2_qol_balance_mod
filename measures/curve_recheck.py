"""The checkpoints of the difficulty curve measured again with more battles than its 40, to tell a real change from
chance when one crosses its window by little. The same measure and windows as tools/difficulty_curve.py. Nothing is
written.

    python measures/curve_recheck.py C15;C17;C28;C39;C40 200
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))

KEYS = ('won', 'time', 'lowest_hp', 'pressure')
_STATE = {}


def cell(task):
    cid, runs = task
    from sim import measures, setup as setup_mod
    from sim.data import game_data
    from sim.variant import balance_data
    if not _STATE:
        data = game_data()
        _STATE.update(data=data, variant=balance_data(data), setup=setup_mod.load())
    return measures.check_change(_STATE['data'], _STATE['setup'], [], [cid], runs=runs, changed=_STATE['variant'])[0]


def fmt(v, key):
    if v is None:
        return '-'
    return f'{v:.0%}' if key in ('won', 'lowest_hp') else f'{v:.2f}' if key == 'pressure' else f'{v:.1f}'


def main():
    bosses, runs = sys.argv[1].split(';'), int(sys.argv[2])
    with ProcessPoolExecutor(min(12, len(bosses))) as pool:
        rows = list(pool.map(cell, [(c, runs) for c in bosses]))
    print(f'{runs} battles: the game > the variant | wins | length | lowest HP | pressure | out of the window')
    for cid, before, after, out in rows:
        print(f'{cid} | ' + ' | '.join(f'{fmt(before[k], k)} > {fmt(after[k], k)}' for k in KEYS) + f" | {', '.join(out) or 'within'}")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

"""Shared helpers of the audit experiments (read-only on the repository)."""
import os
import sys
import copy
import math
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from sim import scenario, measures, setup as setup_mod      # noqa: E402
from sim.data import game_data                               # noqa: E402
from sim.variant import balance_data                         # noqa: E402
import parallel_party_battery as B                           # noqa: E402

_STATE = {}


def state():
    if not _STATE:
        _STATE['data'] = game_data()
        _STATE['setup'] = setup_mod.load()
        # AUDIT_CHANGES: another version of balance_changes.xlsx to build the variant from (e.g. the one of a commit)
        path = os.environ.get('AUDIT_CHANGES')
        _STATE['variant'] = balance_data(_STATE['data'], path) if path else balance_data(_STATE['data'])
    return _STATE['data'], _STATE['setup'], _STATE['variant']


def wilson(wins, n, z=1.96):
    if n == 0:
        return 0.0, 1.0
    p = wins / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def play_cell(source, setup, roles, cid, runs, seed=42):
    cp = setup.checkpoint(cid)
    res = scenario.play(source, setup, lambda: B.build_party_complete(source, setup, roles, cid),
                        lambda: [scenario.fixed_battle(source, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
                        runs=runs, seed=seed)
    wins = sum(1 for r in res if r['won'])
    denied = sum(sum(v for u, v in r['record'].denied.items()) for r in res) / len(res)
    acts = sum(r['enemy_actions'] for r in res) / len(res)
    hp = sum(r['hp_left'] for r in res if r['won']) / max(1, wins)
    return {'wins': wins, 'n': len(res), 'denied': denied, 'enemy_actions': acts, 'hp_left': hp,
            'time': sum(r['time'] for r in res) / len(res)}

"""E1. Where do the win-rate jumps of the variant come from? Ablation of the boss immunity flags.

  vanilla      : vanilla data
  mod          : the Balance variant (balance_changes.xlsx, rows decided)
  mod-sleep    : the variant, but every enemy that was immune to sleep in vanilla is immune again
  mod-flags    : the variant, with every immunity flag of vanilla (turn delay open again, sleep / silence / slow / poison closed)

Same parties, same seeds, same policy for the four. N runs per cell."""
import sys
import copy
import json
from concurrent.futures import ProcessPoolExecutor
import os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import audit_lib as A

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
CIDS = ['C26', 'C28', 'C29', 'C30', 'C32', 'C34', 'C36', 'C38', 'C40']
PARTIES = ['Meta', 'Dual-Support', 'Mage-Heavy', 'Juggernaut', 'Anti-Meta']
_W = {}


def sources():
    if not _W:
        data, setup, variant = A.state()
        no_sleep = copy.copy(variant)
        no_sleep.enemies = dict(variant.enemies)
        van_flags = copy.copy(variant)
        van_flags.enemies = dict(variant.enemies)
        for eid, e in variant.enemies.items():
            v = data.enemies.get(eid)
            if v is None:
                continue
            if 'sleep' in v['immune'] and 'sleep' not in e['immune']:
                ne = dict(e)
                ne['immune'] = list(e['immune']) + ['sleep']
                ne['flags'] = e['flags'] | (1 << 3)
                no_sleep.enemies[eid] = ne
            if v['flags'] != e['flags']:
                ne = dict(e)
                ne['immune'], ne['flags'], ne['snack'] = list(v['immune']), v['flags'], v['snack']
                van_flags.enemies[eid] = ne
        _W.update({'vanilla': data, 'mod': variant, 'mod-sleep': no_sleep, 'mod-flags': van_flags, 'setup': setup})
    return _W


def task(args):
    cid, party, which, n = args
    w = sources()
    r = A.play_cell(w[which], w['setup'], A.B.PARTIES[party]['roles'], cid, n)
    return cid, party, which, r


if __name__ == '__main__':
    tasks = [(c, p, w, N) for c in CIDS for p in PARTIES for w in ('vanilla', 'mod', 'mod-sleep', 'mod-flags')]
    out = {}
    with ProcessPoolExecutor(max_workers=10) as ex:
        for cid, party, which, r in ex.map(task, tasks, chunksize=2):
            out.setdefault(cid, {}).setdefault(party, {})[which] = r
    json.dump(out, open(SP + r'\e1_result.json', 'w'), indent=1)
    print(f'N = {N} per cell. win% [denied enemy turns per fight]')
    print(f'{"":5}{"party":13}{"vanilla":>14}{"mod":>14}{"mod-sleep":>14}{"mod-flags":>14}')
    for cid in CIDS:
        for party in PARTIES:
            row = out[cid][party]
            cells = ''.join(f"{100 * row[w]['wins'] / row[w]['n']:>7.0f}% [{row[w]['denied']:4.1f}]" for w in ('vanilla', 'mod', 'mod-sleep', 'mod-flags'))
            print(f'{cid:5}{party:13}{cells}')

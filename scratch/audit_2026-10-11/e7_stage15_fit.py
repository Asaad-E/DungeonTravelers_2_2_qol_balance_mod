"""E7. Which factor on the common enemies of Stage 15 keeps the last floors inside vanilla (Regression R08, R10)?
The twenty enemies of rows G034 - G093 get HP, ATK and INT of vanilla times one factor; rows of eight random battles
on the floors of C39 and C40 (24 rows), for the reference party and the five battery parties, with the policy of
today. 'rows' is the workbook as it stands."""
import os
import sys
import copy
import json
import openpyxl
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audit_lib as A

FLOORS = (('St15_1120', 'C39'), ('St15_1150', 'C40'))
PARTIES = [('Reference', None)] + [(k, A.B.PARTIES[k]['roles']) for k in ('Meta', 'Dual-Support', 'Mage-Heavy', 'Juggernaut', 'Anti-Meta')]
# a number: HP, ATK and INT times it; 'hpX': HP times X, ATK and INT of vanilla
FACTORS = tuple(sys.argv[1].split(',')) if len(sys.argv) > 1 else ('vanilla', '1.0', '1.1', '1.2', 'rows')
_COMMON = []


def common_ids():
    if not _COMMON:
        wb = openpyxl.load_workbook(os.path.join(A.ROOT, 'data_tables', 'balance_changes.xlsx'), read_only=True, data_only=True)
        for r in wb['Changes'].iter_rows(min_row=2, values_only=True):
            if r[0] and r[1] == 'enemies' and '(common, St15)' in str(r[2]) and r[-1] != 'dropped':
                eid = int(str(r[2]).split()[0])
                if eid not in _COMMON:
                    _COMMON.append(eid)
    return _COMMON


def source(which):
    data, setup, variant = A.state()
    if which == 'vanilla':
        return data
    if which == 'rows':
        return variant
    scaled = copy.copy(variant)
    scaled.enemies = dict(variant.enemies)
    for eid in common_ids():
        v = data.enemies[eid]
        e = dict(variant.enemies[eid])
        hp_only = str(which).startswith('hp')
        factor = float(str(which)[2:] if hp_only else which)
        for stat in ('hp', 'atk', 'int'):
            e[stat] = int(round(v[stat] * (factor if (stat == 'hp' or not hp_only) else 1.0)))
        scaled.enemies[eid] = e
    return scaled


def task(args):
    floor, cid, pname, roles, which = args
    data, setup, variant = A.state()
    src = source(which)
    level = A.scenario.reference_levels(src, setup)[cid][0]
    r = A.measures.expedition(src, setup, floor, level, cid, roles=roles, battles=8, runs=24)
    return floor, pname, str(which), r['won'], r['reached_limit'], r['tp_after']


if __name__ == '__main__':
    tasks = [(f, c, p, r, w) for f, c in FLOORS for p, r in PARTIES for w in FACTORS]
    out = {}
    with ProcessPoolExecutor(max_workers=10) as ex:
        for floor, pname, which, won, full, tp in ex.map(task, tasks):
            out.setdefault(floor, {}).setdefault(pname, {})[which] = (won, full, tp)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'e7_result_%s.json' % '_'.join(FACTORS)), 'w'), indent=1)
    print(f'{len(common_ids())} common enemies. Mean battles won of 8 (share of rows that won all 8)')
    for floor, parties in out.items():
        print(f'floor {floor}')
        print(f'  {"":13}' + ''.join(f'{str(w):>14}' for w in FACTORS))
        for pname, row in parties.items():
            print(f'  {pname:13}' + ''.join(f'{row[str(w)][0]:6.1f} ({row[str(w)][1]:4.0%}) ' for w in FACTORS))

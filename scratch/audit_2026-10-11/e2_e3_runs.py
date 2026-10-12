"""E2b. Rows of eight random battles on the last story floors (the measure rows G034 - G093 were tuned on), for the
reference composition AND the five battery parties, vanilla against the variant.
E3. The reference party at the checkpoints whose bosses were buffed after DIFFICULTY_CURVE.md was generated
(C10, C13, C24) and at the late ones, vanilla against the variant, with the windows of the sheet Settings."""
import sys
import json
from concurrent.futures import ProcessPoolExecutor
import os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import audit_lib as A

FLOORS = (('St15_1120', 'C39'), ('St15_1150', 'C40'))
PARTIES = [('Reference', None)] + [(k, v['roles']) for k, v in A.B.PARTIES.items()]
CURVE = ['C10', 'C13', 'C24', 'C26', 'C29', 'C30', 'C36', 'C38', 'C40']


def expedition(args):
    floor, cid, pname, roles, which = args
    data, setup, variant = A.state()
    source = data if which == 'vanilla' else variant
    level = A.scenario.reference_levels(source, setup)[cid][0]
    r = A.measures.expedition(source, setup, floor, level, cid, roles=roles, battles=8, runs=24)
    return 'exp', floor, cid, pname, which, r


def curve(args):
    cid, which = args
    data, setup, variant = A.state()
    source = data if which == 'vanilla' else variant
    level, s = A.measures.play_checkpoint(source, setup, cid, 40)
    return 'curve', cid, which, level, s


def run(task):
    return expedition(task[1]) if task[0] == 'exp' else curve(task[1])


if __name__ == '__main__':
    tasks = [('exp', (f, c, p, r, w)) for f, c in FLOORS for p, r in PARTIES for w in ('vanilla', 'mod')]
    tasks += [('curve', (c, w)) for c in CURVE for w in ('vanilla', 'mod')]
    exp, cur = {}, {}
    with ProcessPoolExecutor(max_workers=10) as ex:
        for out in ex.map(run, tasks):
            if out[0] == 'exp':
                _, floor, cid, pname, which, r = out
                exp.setdefault((floor, cid), {}).setdefault(pname, {})[which] = r
            else:
                _, cid, which, level, s = out
                cur.setdefault(cid, {})[which] = (level, s)
    print('E2b. eight random battles in a row (24 rows): mean battles won of 8, share of rows that won all 8')
    for (floor, cid), parties in exp.items():
        print(f'  floor {floor} (of {cid})')
        for pname, r in parties.items():
            v, m = r['vanilla'], r['mod']
            print(f"    {pname:13} vanilla {v['won']:.1f} of 8 ({v['reached_limit']:.0%} full rows)   variant {m['won']:.1f} of 8 ({m['reached_limit']:.0%} full rows)")
    print('E3. reference party, 40 runs: wins | length | lowest HP | pressure   (vanilla > variant)')
    data, setup, variant = A.state()
    win = {k: float(setup.settings['check_%s_window' % k]) for k in ('won', 'time', 'lowest_hp', 'pressure')}
    for cid in CURVE:
        (lv, v), (_, m) = cur[cid]['vanilla'], cur[cid]['mod']
        flags = []
        if abs(m['won'] - v['won']) > win['won']:
            flags.append('won ' + ('easier' if m['won'] > v['won'] else 'HARDER'))
        if v['time'] and m['time'] and abs(m['time'] / v['time'] - 1) > win['time']:
            flags.append('time ' + ('easier' if m['time'] < v['time'] else 'HARDER'))
        if abs(m['lowest_hp'] - v['lowest_hp']) > win['lowest_hp']:
            flags.append('lowest_hp ' + ('easier' if m['lowest_hp'] > v['lowest_hp'] else 'HARDER'))
        if v['pressure'] and abs(m['pressure'] / v['pressure'] - 1) > win['pressure']:
            flags.append('pressure ' + ('easier' if m['pressure'] < v['pressure'] else 'HARDER'))
        t = lambda x: f"{x:.1f}" if x else '-'
        print(f"  {cid} L{lv}: {v['won']:.0%} > {m['won']:.0%} | {t(v['time'])} > {t(m['time'])} | {v['lowest_hp']:.0%} > {m['lowest_hp']:.0%} | "
              f"{v['pressure']:.2f} > {m['pressure']:.2f} | {', '.join(flags) or 'within'}")
    json.dump({'exp': {f'{k[0]}|{k[1]}': v for k, v in exp.items()}, 'curve': cur}, open(SP + r'\e2_e3_result.json', 'w'), indent=1, default=str)

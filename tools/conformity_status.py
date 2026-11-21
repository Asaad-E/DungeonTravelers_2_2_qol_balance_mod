"""
Print live machine-verified status of the Clean-Room Binary Conformity Campaign from
docs/binary_spec/STATE.json (and DIFF_TABLE.json when present).

    python tools/conformity_status.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(ROOT, 'docs', 'binary_spec')
STATE_PATH = os.path.join(SPEC_DIR, 'STATE.json')
DIFF_PATH = os.path.join(SPEC_DIR, 'DIFF_TABLE.json')


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if not os.path.exists(STATE_PATH):
        print('STATE.json not found. Run `python tools/exe_inventory.py` first.')
        return 1
    with open(STATE_PATH, encoding='utf-8') as f:
        st = json.load(f)

    diff_counts = {}
    if os.path.exists(DIFF_PATH):
        with open(DIFF_PATH, encoding='utf-8') as f:
            diff = json.load(f)
        for row in diff.get('items', []):
            mod = row.get('module', '?')
            sev = row.get('verdict', '?')
            status = row.get('status', 'open')
            if status == 'open' and sev in ('S0', 'S1', 'S2', 'ENGINE-ONLY'):
                diff_counts.setdefault(mod, {'S0': 0, 'S1': 0, 'S2': 0, 'ENGINE-ONLY': 0})[sev] += 1

    print(f"Campaign: {st['campaign_status']} | Active Phase: {st['active_phase']} | SHA-256: {st['exe_sha256'][:16]}...")
    print('\nPhases:')
    for k in sorted(st['phases'], key=int):
        p = st['phases'][k]
        print(f"  Phase {k}: {p['status']:12s}  commit={p.get('signoff_commit') or '-'}")

    print('\nModules (M00..M11):')
    print(f"  {'ID':4s} {'P1 Spec':10s} {'audit_chk':10s} {'P2 Diff':10s} {'Open S0/S1/S2':14s} {'P3 Fix':10s} File")
    for mid, m in st['modules'].items():
        dc = diff_counts.get(mid)
        s_str = f"{dc['S0']}/{dc['S1']}/{dc['S2']}" if dc else f"{m['open_s0']}/{m['open_s1']}/{m['open_s2']}"
        print(f"  {mid:4s} {m['phase1_spec']:10s} {m['phase1_audit_check']:10s} {m['phase2_diff']:10s} {s_str:14s} {m['phase3_fix']:10s} {m['file']}")

    p4 = st['phase4']
    print(f"\nPhase 4 Circuit Breaker: {p4['consecutive_failed_rounds']}/3 consecutive fails | cumulative S2: {p4['cumulative_s2']} | sampled items: {len(p4['sampled_item_ids'])}")
    if st.get('claims'):
        print('\nActive Claims:')
        for c in st['claims']:
            print(' ', c)
    return 0


if __name__ == '__main__':
    sys.exit(main())

import sys, os, struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
import character_data

arc = PckArchive('mod_project/backups/LvExpSkptData.pck')
entries = sorted([struct.unpack('<III', d[:12])[:2] for f, d in arc.files])
cum = 0
cum_levels = []
for lv, req in entries:
    cum += req
    cum_levels.append((lv, cum))

def exp_to_lv(e):
    if e == 0:
        return 1
    res = 1
    for lv, c in cum_levels:
        if e >= c:
            res = lv
        else:
            break
    return res


chars = character_data.characters()
print(f"{'ID':2s} | {'Name':11s} | {'Join Level':10s} | {'Start EXP':10s}")
print("-" * 45)
for c in chars:
    lv = exp_to_lv(c['start_exp'])
    print(f"{c['id']:2d} | {c['name']:11s} | Level {lv:2d}   | {c['start_exp']:9d}")

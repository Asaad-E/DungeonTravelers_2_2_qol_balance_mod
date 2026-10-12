"""The readings of the postgame bosses that stand below the floor of their class in the guide curve, written into the
sheet AuditReadings of data_tables/sim_setup.xlsx from the comparison of postgame_compare.py (beside this file): the
least crown bonus at which the vanilla party reaches the floor, the stand-in of the model for what a player prepares.

    python postgame_readings.py
"""
import json
import os
import sys
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import guide_curve                                        # noqa: E402
from sim import setup as setup_mod                        # noqa: E402

LEVERS = ('Measured on 2026-10-12 on the bosses below their floor (postgame_levers.py): a crown bonus of 50 alone brings '
          '18 of 28 above it; max HP x1.5 with three pieces of "received damage DOWN" 11 of 28; the order of the '
          "Valkyrie's Cover and Parry changes nothing")


def main():
    setup = setup_mod.load()
    measured, compared = {}, {}
    for name in os.listdir(guide_curve.OUT_DIR):
        with open(os.path.join(guide_curve.OUT_DIR, name), encoding='utf-8') as f:
            measured.update({m['id']: m for m in json.load(f)})
    for name in os.listdir(HERE):
        if name.startswith('postgame_compare_') and name.endswith('.json'):
            with open(os.path.join(HERE, name), encoding='utf-8') as f:
                compared.update({m['id']: m for m in json.load(f)})
    wb = openpyxl.load_workbook(setup_mod.SETUP)
    ws = wb['AuditReadings']
    have = {r[0].value: r for r in ws.iter_rows(min_row=2)}
    written = 0
    for r in guide_curve.sheet(setup):
        cid = r['Checkpoint']
        floor = float(setup.settings[f"guide_{r['Class']}_min_won"])
        if not cid.startswith('P') or measured[cid]['won'] >= floor:
            continue
        c = compared[cid]
        reached = c['vanilla']['won'] >= floor
        result = 'preparation gap' if reached else 'known limit'
        reading = (f"The party of the sheets wins {measured[cid]['won']:.0%} at level {measured[cid]['level']} (floor of a "
                   f"{r['Class']} boss {floor:.0%}): it wears the gear of the guide and none of the answers a player "
                   f"prepares for the fight. " +
                   (f"With a crown bonus of {c['crown']}, the stand-in of the model for that preparation (it adds to every "
                    f"stat and to the eight resistances), it wins {c['vanilla']['won']:.0%}. "
                    if reached else
                    f"Even with a crown bonus of 50 it wins {c['vanilla']['won']:.0%}: the fight asks for an answer the "
                    f"policy does not play (sheet PostgameBosses, what the pages say). ") + LEVERS)
        if f'curve {cid}' in have:
            have[f'curve {cid}'][1].value, have[f'curve {cid}'][2].value = result, reading
        else:
            ws.append((f'curve {cid}', result, reading))
        written += 1
    wb.save(setup_mod.SETUP)
    print(written, 'readings')


if __name__ == '__main__':
    main()

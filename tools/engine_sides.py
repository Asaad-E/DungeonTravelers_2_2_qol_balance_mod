"""
Sides of data that a trial command of dtcli needs and the snapshot does not hold: the game as a set of rows of balance_changes.xlsx
builds it, for a trial that takes some rows out (rows_trial) or puts old rows back (curve_ablation). The sides are written as an
extra file that `dtcli <command> --extra <file>` loads next to the snapshot (the format of engine_cs/README.md, "Bridge").

    python tools/engine_sides.py rows P031,P032              build/engine_extra_rows.json: the side 'rows|without' (the variant without those rows)
    python tools/engine_sides.py ablation [case ...]         build/engine_extra_ablation.json: for each case of measures/curve_ablation.py the sides
                                                             'ablation|<case>|vanilla' and 'ablation|<case>|variant' (all the cases when none is given)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PROJECT, 'measures'))

import engine_export                                      # noqa: E402


def write(name, sides):
    path = os.path.join(PROJECT, 'build', f'engine_extra_{name}.json')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('{"sides":{' + ','.join(json.dumps(k) + ':' + engine_export.text_of(v) for k, v in sides.items()) + '}}')
    return path


def side_of(data):
    return engine_export.side_json(data, engine_export.flags_of(data))


def rows_without(ids):
    """The variant built from the rows of the workbook but those named (the variant of the snapshot is the one with every row)."""
    from gamedata import variant
    from gamedata.data import game_data
    wanted = set(ids)
    data = variant.apply(game_data(), [r for r in variant.rows() if str(r['ID']) not in wanted])
    data.arcane_chance = variant.arcane_chance()
    data.interrupt_product = variant.interrupt_product()
    return data


def rows(ids):
    return write('rows', {'rows|without': side_of(rows_without(ids))})


def ablation(cases):
    import curve_ablation
    sides = {}
    for case in cases or curve_ablation.CASES:
        data, changed = curve_ablation.build(case)
        sides[f'ablation|{case}|vanilla'] = side_of(data)
        sides[f'ablation|{case}|variant'] = side_of(changed)
    return write('ablation', sides)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if len(sys.argv) < 2 or sys.argv[1] not in ('rows', 'ablation'):
        raise SystemExit(__doc__)
    done = rows(sys.argv[2].split(',')) if sys.argv[1] == 'rows' else ablation(sys.argv[2:])
    print(os.path.relpath(done, PROJECT), os.path.getsize(done), 'bytes')

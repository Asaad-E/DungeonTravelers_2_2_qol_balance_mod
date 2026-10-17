"""Criticisms I01 - I18 (unique skills) given the figures of dtcli unique-battery (2026-10-16, docs/generated/UNIQUE_BATTERY.md): every
role that names the girl, every battery party, every story boss from the chapter she joins in and rows of random battles."""
import json
import os
import re
import openpyxl

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
PATH = os.path.join(ROOT, 'data_tables', 'balance_criteria.xlsx')
rows = json.load(open(os.path.join(ROOT, 'docs', 'generated', 'unique_battery', 'part_1.json'), encoding='utf-8'))
by_girl = {r['girl']: r for r in rows}


def pct(x, sign=False):
    return ('%+d%%' if sign else '%d%%') % round(100 * x)


wb = openpyxl.load_workbook(PATH)
ws = wb['Criticisms']
head = [c.value for c in ws[1]]
col = {name: i + 1 for i, name in enumerate(head)}
done = []
for r in range(2, ws.max_row + 1):
    rid = str(ws.cell(r, col['ID']).value or '')
    if not re.fullmatch(r'I\d\d', rid):
        continue
    girl = re.search(r'\((\w+)\)', ws.cell(r, col['Subject']).value).group(1)
    g = by_girl[girl]
    b = g['best']
    text = ('2026-10-16, dtcli unique-battery (docs/generated/UNIQUE_BATTERY.md; ' + g['skill'] + ' in every role that names her, the five '
            'battery parties, every story boss from the chapter she joins in and rows of random battles; 20 runs a cell, the 3 best again '
            'at 200): ' + g['verdict'] + ', it serves in ' + pct(g['serves'] / g['cells']) + ' of ' + str(g['cells']) + ' cells and makes '
            + pct(g['hurts'] / g['cells']) + ' worse; best cell ' + b['checkpoint'] + ' ' + b['context'] + ', ' + b['party'] + ' (' + b['role']
            + '): wins ' + pct(b['wins'], True) + ', fights ' + pct(b['length'], True) + ' shorter, HP left ' + pct(b['hp_left'], True)
            + '. 14 of the 18 unique skills good, 4 niche, none dead.')
    cell = ws.cell(r, col['Balance_Result'])
    old = str(cell.value or '').rstrip()
    assert 'unique-battery' not in old, rid
    cell.value = (old + ' ' + text).strip()
    done.append(rid + ' ' + girl)
assert len(done) == 18, done
wb.save(PATH)
print('\n'.join(done))

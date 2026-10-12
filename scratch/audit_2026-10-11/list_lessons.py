"""The boxes of the lessons of Euthys (Lesson.pck), in order, with the voice clip before each and whether the Balance
variant already words it: list_lessons.py [ENTRY SUBSTRING]"""
import os
import re
import sys

import openpyxl

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from pck_handler import PckArchive                          # noqa: E402

BOX = re.compile(rb'[\x20-\x7e\n]{3,}\x00')


def main():
    wanted = sys.argv[1] if len(sys.argv) > 1 else None
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    rows = openpyxl.load_workbook(os.path.join(PROJECT, 'data_tables', 'balance_tutorial_text.xlsx'),
                                  read_only=True)['Tutorials'].iter_rows(min_row=2, values_only=True)
    worded = {(r[1], r[2]): r[5] for r in rows if r and r[0]}
    for name, blob in PckArchive(os.path.join(PROJECT, 'backups', 'Lesson.pck')).files:
        found = [m.group()[:-1].decode('latin-1') for m in BOX.finditer(bytes(blob))]
        texts = [(k, t) for k, t in enumerate(found) if ' ' in t and len(t) > 8]
        if wanted is None:
            first = next((t for _, t in texts), '')
            print(f'{name}: {len(texts)} boxes | {first[:90]!r}')
            continue
        if wanted not in name:
            continue
        print('==', name)
        for k, t in texts:
            voice = next((s for s in reversed(found[max(0, k - 2):k]) if s.startswith('VC_')), '')
            lines = t.strip('"').split('\n')
            mark = worded.get((name, t), '')
            print(f'  [{len(lines)} lines, widest {max(len(x) for x in lines)}] {voice:14s} {mark:8s} {t!r}')


if __name__ == '__main__':
    main()

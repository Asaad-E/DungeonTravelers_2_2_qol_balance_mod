"""Text boxes of the event scripts that tell who a girl is: every box of an entry of the script packs that names her,
kept when the box itself holds one of the words given (her name, her craft). A reading aid for the character.

    python girl_lines.py Lize doll puppet thought mind
"""
import os
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from pck_handler import PckArchive                          # noqa: E402

SCRIPTS = os.path.join(os.path.dirname(PROJECT), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')
BOX = re.compile(rb'[\x20-\x7e\n]{12,}\x00')


def main():
    name, words = sys.argv[1], [w.lower() for w in sys.argv[2:]]
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    seen, shown = set(), 0
    for pack in ('SEV.pck', 'evt00.pck', 'evt02.pck', 'evt99.pck', 'Battle.pck'):
        path = os.path.join(SCRIPTS, pack)
        for entry, blob in PckArchive(path).files:
            blob = bytes(blob)
            if name.encode() not in blob:
                continue
            for m in BOX.finditer(blob):
                text = m.group()[:-1].decode('latin-1').replace('\n', ' ')
                low = text.lower()
                if text in seen or not any(w in low for w in words):
                    continue
                seen.add(text)
                shown += 1
                if shown <= 70:
                    print(f'{pack}/{entry}: {text[:230]}')
    print(shown, 'boxes')


if __name__ == '__main__':
    main()

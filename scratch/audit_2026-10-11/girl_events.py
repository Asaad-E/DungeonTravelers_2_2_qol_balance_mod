"""The sub events that are most about a girl: the entries of SEV.pck ranked by how often they name her, and the text
boxes of the first of them. A reading aid for the character.

    python girl_events.py Lize [entries] [boxes]
"""
import os
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from pck_handler import PckArchive                          # noqa: E402

SCRIPTS = os.path.join(os.path.dirname(PROJECT), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')
BOX = re.compile(rb'[\x20-\x7e\n]{12,}\x00')

name = sys.argv[1]
entries = int(sys.argv[2]) if len(sys.argv) > 2 else 3
boxes = int(sys.argv[3]) if len(sys.argv) > 3 else 30
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ranked = sorted(((bytes(b).count(name.encode()), e, bytes(b)) for e, b in PckArchive(os.path.join(SCRIPTS, 'SEV.pck')).files),
                reverse=True)
print([(e, n) for n, e, _ in ranked[:10]])
for n, entry, blob in ranked[:entries]:
    print('===', entry, n)
    for m in list(BOX.finditer(blob))[:boxes]:
        print('  ', m.group()[:-1].decode('latin-1').replace('\n', ' ')[:210])

"""The lines a girl speaks (the boxes that follow a voice tag ending with her number) that hold one of the words
given, in every script pack. A reading aid for the character.

    python girl_voice.py 008 doll game play
"""
import os
import re
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from pck_handler import PckArchive                          # noqa: E402

SCRIPTS = os.path.join(os.path.dirname(PROJECT), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')
BOX = re.compile(rb'[\x20-\x7e\n]{6,}\x00')

voice, words = sys.argv[1], [w.lower() for w in sys.argv[2:]]
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
seen, shown, total = set(), 0, 0
for pack in ('SEV.pck', 'evt00.pck', 'evt02.pck', 'evt99.pck', 'Battle.pck'):
    for entry, blob in PckArchive(os.path.join(SCRIPTS, pack)).files:
        boxes = [m.group()[:-1].decode('latin-1').replace('\n', ' ') for m in BOX.finditer(bytes(blob))]
        for tag, text in zip(boxes, boxes[1:]):
            if tag.startswith('VC_') and tag.endswith('_' + voice) and text.startswith('"'):
                total += 1
                if text not in seen and any(w in text.lower() for w in words):
                    seen.add(text)
                    shown += 1
                    if shown <= 45:
                        print(f'{entry}: {text[:200]}')
print(shown, 'of', total, 'lines')

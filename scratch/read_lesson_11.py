import os, sys, re
sys.path.insert(0, r"c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project\tools")
from pck_handler import PckArchive

pck = PckArchive(r"c:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project\backups\Lesson.pck")
for fn, b in pck.files:
    if fn == 'BattleTeacher_11-12.adv.bin':
        lines = re.findall(b'[\x20-\x7E\r\n]{5,}', b)
        for i, l in enumerate(lines):
            s = l.decode('latin-1', 'ignore')
            if '"' in s:
                print(f"{i:2d}: {repr(s)}")

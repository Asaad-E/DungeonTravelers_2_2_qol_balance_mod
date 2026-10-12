import sys
import re
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

archive = PckArchive('DungeonTravelers2-2_EN/Data/ENG/Script/Lesson.pck')
for item in archive.files:
    name = item[0] if isinstance(item, tuple) else item.name
    if 'BattleTeacher' not in name:
        continue
    data = item[1] if isinstance(item, tuple) else item.data
    strs = [s.decode('latin1', 'ignore') for s in re.findall(b'[\x20-\x7e\n\r]{6,}', data)]
    dialogues = [s for s in strs if ('"' in s or '.' in s) and len(s) > 20 and not s.startswith('VC_')]
    if dialogues:
        print(f"\n==================== {name} ====================")
        for d in dialogues:
            print("---")
            print(d)


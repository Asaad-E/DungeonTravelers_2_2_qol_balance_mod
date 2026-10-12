import sys
import re
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

arc = PckArchive('DungeonTravelers2-2_EN/Data/ENG/Script/Lesson.pck')
print(f"Total Lesson files: {len(arc.files)}")
for fn, data in arc.files:
    if 'BattleTeacher' in fn:
        strings = re.findall(b'[\x20-\x7E]{8,}', data)
        # Find if Euthys is mentioned
        has_euthys = any(b'Euthys' in s for s in strings)
        print(f"{fn} (len={len(data)}): has_euthys={has_euthys}, string_count={len(strings)}")
        for s in strings[:3]:
            try:
                print(f"   {s.decode('utf-8', errors='ignore')}")
            except:
                pass

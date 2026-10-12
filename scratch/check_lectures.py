import sys
sys.path.insert(0, '.')
from mod_project.tools.pck_handler import PckArchive

arc = PckArchive('mod_project/backups/Lesson.pck')
for f_name, data in arc.files:
    if f_name == 'BattleTeacher_14.adv.bin':
        print(f"=== {f_name} ===")
        for s in data.split(b'\x00'):
            if b'"' in s:
                clean = s.decode('latin-1', errors='replace').replace('\n', ' ')
                print(' ', clean.encode('ascii', errors='replace').decode('ascii'))

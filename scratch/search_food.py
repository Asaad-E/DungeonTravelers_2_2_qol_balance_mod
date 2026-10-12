import sys
sys.path.insert(0, '.')
from mod_project.tools.pck_handler import PckArchive

for pck in ['Teaching.pck', 'Lesson.pck']:
    arc = PckArchive(f'mod_project/backups/{pck}')
    for fn, data in arc.files:
        for s in data.split(b'\x00'):
            sl = s.lower()
            if b'300' in s or (b'step' in sl and (b'food' in sl or b'meal' in sl or b'buff' in sl or b'eat' in sl)):
                if len(s) > 15:
                    print(f'{pck} {fn}: {s.decode("latin-1", errors="replace").strip().replace(chr(10), " ")}')

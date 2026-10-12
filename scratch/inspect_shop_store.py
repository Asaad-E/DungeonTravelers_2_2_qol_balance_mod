import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backup_path = os.path.join(BASE_DIR, 'backups', 'ShopStore.pck')

arc = PckArchive(backup_path)
for fn, d in arc.files:
    if fn in ['Talk_Random01.adv.bin', 'Talk_Random11.adv.bin']:
        print(f'=== {fn} ===')
        chunks = d.split(b'"')
        for c in chunks:
            if len(c) > 30 and b'\n' in c:
                print('  Line:', repr(c.decode('latin-1')))

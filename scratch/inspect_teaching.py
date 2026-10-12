import sys, re, os
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

arc = PckArchive('mod_project/backups/Teaching.pck')
for fn, data in sorted(arc.files):
    strs = [s.decode('latin1', 'ignore') for s in re.findall(b'[\x20-\x7e\n\r]{6,}', data)]
    dialogues = [s for s in strs if len(s) > 15 and not any(s.startswith(x) for x in ('VC_', 'BG_', 'BGM_', 'EFF_', 'SE_'))]
    print(f"\n==================== {fn} ====================")
    for d in dialogues:
        print("---")
        print(d)

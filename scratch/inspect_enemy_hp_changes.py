import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
from sim.variant import rows

changes = rows()
hp_changes = [r for r in changes if r['Table'] == 'enemies' and r['Field'] == 'hp']
for r in hp_changes:
    print(f"{r['ID']} | {r['Record']:<22} | Van: {r['Vanilla']:<6} -> New: {r['New']:<6} | Note: {r.get('Note', '')}")

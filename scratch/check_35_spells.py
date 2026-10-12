import struct, sys
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/vanilla_source_of_truth.xlsx', data_only=True)
ws = wb['Skills']
skill_info = {row[2]: {'name': row[3], 'levels': row[4], 'desc': row[17], 'lvup': row[18]}
              for row in ws.iter_rows(min_row=2, values_only=True) if row[2] is not None}

pck = PckArchive('mod_project/backups/MagicSkillData.pck')

acc_up_exact = []
for fn, b in pck.files:
    spell_id = struct.unpack_from('<I', b, 0)[0]
    info = skill_info.get(spell_id, {})
    lvup = str(info.get('lvup', ''))
    if 'Accuracy UP' in lvup:
        accs = [round(struct.unpack_from('<f', b, 0xFC + 4*k)[0], 4) for k in range(10)]
        max_lv = info.get('levels', 10) or 10
        acc_up_exact.append((spell_id, info.get('name'), max_lv, accs[:max_lv], accs, lvup))

print(f"Total spells with 'Accuracy UP': {len(acc_up_exact)}")
scaling = [x for x in acc_up_exact if len(set(x[3])) > 1]
constant = [x for x in acc_up_exact if len(set(x[3])) == 1]
print(f"Scaling: {len(scaling)}, Constant: {len(constant)}")
for s in constant:
    print(s[0], s[1], s[2], s[3], repr(s[5]))

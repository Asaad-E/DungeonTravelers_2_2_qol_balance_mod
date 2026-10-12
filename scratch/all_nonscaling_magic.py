import struct, sys
sys.path.append('mod_project/tools')
from pck_handler import PckArchive
import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/vanilla_source_of_truth.xlsx', data_only=True)
ws = wb['Skills']
skill_info = {row[2]: {'name': row[3], 'levels': row[4], 'desc': row[17], 'lvup': row[18]}
              for row in ws.iter_rows(min_row=2, values_only=True) if row[2] is not None}

pck = PckArchive('mod_project/backups/MagicSkillData.pck')

for fn, b in pck.files:
    spell_id = struct.unpack_from('<I', b, 0)[0]
    info = skill_info.get(spell_id, {})
    name = info.get('name', f'Spell {spell_id}')
    lvup = str(info.get('lvup', ''))
    accs = [round(struct.unpack_from('<f', b, 0xFC + 4*k)[0], 4) for k in range(10)]
    max_lv = info.get('levels', 10) or 10
    accs_act = accs[:max_lv]
    # check if any scaling
    if len(set(accs_act)) > 1:
        pass # scaling
    else:
        # non-scaling
        if accs_act[0] != 1.0 or 'Accuracy' in lvup:
            print(f'{spell_id:3d}: {name:20s} max_lv={max_lv} accs={accs_act} lvup={repr(lvup)}')

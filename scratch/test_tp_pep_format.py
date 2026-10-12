import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/qol_joint_skill_text.xlsx', data_only=True)
ws = wb['JointSkills']

skills = []
for row in list(ws.iter_rows(min_row=2, values_only=True)):
    name, van, qol, l, members, tp, pep_n, pep_s = row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
    tp_div = tp.replace(' of max TP', '')
    if tp_div == '1/1':
        tp_str = 'All TP'
    else:
        tp_str = f"{tp_div} TP"
    pep = int(pep_s)
    skills.append({
        'name': name,
        'van': van,
        'qol': qol,
        'members': members,
        'tp_str': tp_str,
        'pep': pep,
        'cost_tag': f" [{tp_str}, {pep}P]" if pep > 0 else f" [{tp_str}]"
    })

print("Testing `[1/4 TP, 7P]` format length on all 52 skills:")
for s in skills[:15]:
    print(f"{s['name']:24} | cost: {s['cost_tag']:15} (len {len(s['cost_tag'])}) | {s['qol']}")

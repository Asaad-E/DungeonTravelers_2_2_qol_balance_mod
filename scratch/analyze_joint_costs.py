import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/qol_joint_skill_text.xlsx', data_only=True)
ws = wb['JointSkills']

print(f"{'Skill Name':24} | {'Len':3} | {'TP':12} | {'Pep':5} | Current QoL Text")
print("-" * 110)

skills = []
for row in list(ws.iter_rows(min_row=2, values_only=True)):
    name, van, qol, l, members, tp, pep_n, pep_s = row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
    skills.append({
        'name': name,
        'van': van,
        'qol': qol,
        'len': l,
        'members': members,
        'tp': tp,
        'pep_s': int(pep_s),
        'tp_div': tp.replace(' of max TP', '') if ' of max TP' in tp else tp
    })

for s in skills:
    print(f"{s['name']:24} | {s['len']:3d} | {s['tp_div']:12} | {s['pep_s']:5d} | {s['qol']}")

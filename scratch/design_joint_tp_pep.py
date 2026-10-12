import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/qol_joint_skill_text.xlsx', data_only=True)
ws = wb['JointSkills']

rows = list(ws.iter_rows(min_row=2, values_only=True))

print("Designing [TP, Pep] for all 52 Joint Skills:")
print("=" * 110)

for r in rows:
    name, van, qol, members, tp, pep_n, pep_s = r[1], r[2], r[3], r[5], r[6], r[7], r[8]
    tp_div = tp.replace(' of max TP', '')
    tp_str = 'All TP' if tp_div == '1/1' else f'{tp_div} TP'
    pep = int(pep_s)
    tag_pep = f" [{tp_str}, {pep} Pep]" if pep > 0 else f" [{tp_str}]"
    tag_p = f" [{tp_str}, {pep}P]" if pep > 0 else f" [{tp_str}]"
    print(f"{name:24} | TP:{tp_str:6} | Pep:{pep:2d} | tag_len:{len(tag_pep):2d} | {qol}")

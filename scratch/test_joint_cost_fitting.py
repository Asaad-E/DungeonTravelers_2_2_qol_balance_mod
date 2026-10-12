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
    skills.append({
        'name': name,
        'van': van,
        'qol': qol,
        'members': members,
        'tp_str': tp_str,
        'pep': int(pep_s),
        'effects': row[12]
    })

print(f"Total joint skills: {len(skills)}")

# Let's test appending [tp_str] to current qol text:
can_fit_tp_direct = []
overflow_tp_direct = []

for s in skills:
    tag = f" [{s['tp_str']}]"
    combined = s['qol'] + tag
    if len(combined) <= 70:
        can_fit_tp_direct.append((s['name'], len(combined), combined))
    else:
        overflow_tp_direct.append((s['name'], len(s['qol']), len(combined), s['qol'], tag))

print(f"\nDirect fit of '[TP]' without touching text: {len(can_fit_tp_direct)} / {len(skills)}")
print(f"Overflows needing slight rewording: {len(overflow_tp_direct)}")

print("\n--- Overflows that need slight wording trim (without cutting ANY facts): ---")
for name, qlen, clen, qol, tag in overflow_tp_direct:
    print(f"{name:24} | cur:{qlen} -> {clen} | {qol} + {tag}")

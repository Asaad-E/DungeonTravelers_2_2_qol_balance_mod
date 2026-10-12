import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/qol_skill_text.xlsx')
ws = wb['Skills']
header = [c.value for c in ws[1]]
name_idx = header.index('Skill_Name')
cat_idx = header.index('Category')
desc_idx = header.index('QoL_Desc')
lvup_idx = header.index('QoL_LvUp')

rows = list(ws.iter_rows(min_row=2, values_only=True))

findings = []

for r in rows:
    name = r[name_idx]
    cat = r[cat_idx]
    desc = str(r[desc_idx] or '')
    lvup = str(r[lvup_idx] or '')
    
    lvup_lines = lvup.split('\n')
    l2 = lvup_lines[0] if len(lvup_lines) > 0 else ''
    l3 = lvup_lines[1] if len(lvup_lines) > 1 else ''
    
    len_desc = len(desc)
    len_l2 = len(l2)
    len_l3 = len(l3)
    
    max_len = max(len_desc, len_l2, len_l3)
    
    reasons = []
    if len_l2 >= 80:
        reasons.append(f'L2 very long ({len_l2} chars)')
    if len_l3 >= 80:
        reasons.append(f'L3 very long ({len_l3} chars)')
        
    if 'turn' in l2.lower() or 'turn' in l3.lower():
        if '->' in l2 or '->' in l3:
            reasons.append('Turns with progression')
            
    if l2.count('|') >= 3 or l3.count('|') >= 3:
        reasons.append('Heavy pipe chaining (>=3 pipes)')
        
    if l2.count('(') >= 3 or l3.count('(') >= 3:
        reasons.append('Cluttered parentheses (>=3)')
        
    if l2.count('->') >= 7 or l3.count('->') >= 7:
        reasons.append('Dense 10-level arrow chain')
        
    # Check for abbreviations or awkward shorthand
    for word in ['w/', 'dmg', 'lvl', 'spd', 'atk', 'matk', 'def', 'mdef']:
        if f' {word} ' in f' {lvup.lower()} ':
            # normal stats are fine, but let's check strange abbreviations
            pass
            
    if reasons:
        findings.append({
            'name': name,
            'cat': cat,
            'desc': desc,
            'l2': l2,
            'l3': l3,
            'max_len': max_len,
            'reasons': reasons
        })

print(f'Total skills flagged: {len(findings)}')
findings.sort(key=lambda x: (len(x['reasons']), x['max_len']), reverse=True)

for f in findings[:25]:
    r_str = ', '.join(f['reasons'])
    print(f"{f['name']} ({f['cat']}) - Reasons: {r_str}")
    print(f"  L1 ({len(f['desc'])}): {f['desc']}")
    print(f"  L2 ({len(f['l2'])}): {f['l2']}")
    print(f"  L3 ({len(f['l3'])}): {f['l3']}")
    print('-' * 70)

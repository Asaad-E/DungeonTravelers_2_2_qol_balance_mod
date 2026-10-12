import openpyxl

wb_ch = openpyxl.load_workbook('mod_project/data_tables/balance_changes.xlsx', data_only=True)
ws_ch = wb_ch['Changes']
headers = [c.value for c in ws_ch[1]]

w_rows = []
for row in ws_ch.iter_rows(min_row=2, values_only=True):
    rd = dict(zip(headers, row))
    cid = str(rd.get('Change_ID') or '')
    if cid.startswith('W'):
        w_rows.append((cid, rd.get('Target'), rd.get('Field'), rd.get('Vanilla_Value'), rd.get('Modified_Value'), rd.get('Serves_Row'), rd.get('Description')))

print(f"Total W rows: {len(w_rows)}")
for r in w_rows[:20]:
    print(r)

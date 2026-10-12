import openpyxl

wb_ch = openpyxl.load_workbook('mod_project/data_tables/balance_changes.xlsx', data_only=True)
ws_ch = wb_ch['Changes']
headers = [c.value for c in ws_ch[1]]

for row in ws_ch.iter_rows(min_row=2, values_only=True):
    rd = dict(zip(headers, row))
    cid = str(rd.get('ID') or '')
    if cid.startswith('W'):
        print(f"{cid} | Table: {rd.get('Table')} | Record: {rd.get('Record')} | Field: {rd.get('Field')} | Vanilla: {rd.get('Vanilla')} -> New: {rd.get('New')} | Serves: {rd.get('Serves')} | Why: {rd.get('Why')}")

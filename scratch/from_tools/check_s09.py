import openpyxl

wb_crit = openpyxl.load_workbook('mod_project/data_tables/balance_criteria.xlsx', data_only=True)
ws_crit = wb_crit['Criticisms']
headers_crit = [c.value for c in ws_crit[1]]

for row in ws_crit.iter_rows(min_row=2, values_only=True):
    rd = dict(zip(headers_crit, row))
    if rd['ID'] == 'S09':
        print("S09 details:")
        for k, v in rd.items():
            if v:
                print(f"  {k}: {v}")

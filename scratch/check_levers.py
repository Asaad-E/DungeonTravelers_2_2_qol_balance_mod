import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/balance_criteria.xlsx', read_only=True)
ws = wb['Levers']
for r in ws.iter_rows(values_only=True):
    print(r)

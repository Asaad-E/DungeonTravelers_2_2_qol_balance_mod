import sys, os, struct
sys.path.insert(0, os.path.abspath('mod_project/tools'))
import openpyxl

wb = openpyxl.load_workbook('mod_project/data_tables/vanilla_source_of_truth.xlsx', data_only=True)
ws_lvl = wb['SkillLevels']
for r in ws_lvl.iter_rows(min_row=2, values_only=True):
    if r[1] == 309:
        print("First Grid level row:", r)
    if r[1] == 270:
        print("Warning Shot level row:", r)

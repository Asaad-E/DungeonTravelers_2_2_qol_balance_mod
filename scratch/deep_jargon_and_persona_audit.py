import os, sys, re, openpyxl
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'tools'))
from pck_handler import PckArchive
tables_dir = os.path.join(base_dir, 'data_tables')

jargon_words = [
    'patch', 'rebalance', 'rebalanced', 'developer', 'devs', 'capped at', 
    'diminishing returns', 'our curve', 'buffed', 'nerfed', 'our mod', 'modded'
]

print("=== AUDITING APPLY_MOD.PY FOR FORBIDDEN JARGON ===")
with open(os.path.join(base_dir, 'tools', 'apply_mod.py'), 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    # Only check script replacement definitions (lines 270 to 1065)
    if 270 <= idx <= 1065:
        for jw in jargon_words:
            if jw in line.lower():
                print(f"Line {idx+1}: [{jw}] -> {line.strip()}")

print("\n=== AUDITING ALL EXCEL TABLES FOR FORBIDDEN JARGON ===")
for root, dirs, files in os.walk(tables_dir):
    for f in sorted(files):
        if f.endswith('.xlsx'):
            path = os.path.join(root, f)
            wb = openpyxl.load_workbook(path)
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
                    # Check description / modded text columns
                    for c_idx, val in enumerate(row):
                        if isinstance(val, str):
                            for jw in jargon_words:
                                # avoid checking 'Status' or 'Notes' developer columns
                                # check if column header or value
                                if r_idx > 1 and c_idx not in [len(row)-1, len(row)-2]:
                                    if jw in val.lower():
                                        print(f"{f} [{sheet}] Row {r_idx} Col {c_idx+1}: [{jw}] -> {val[:80]}")

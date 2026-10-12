import re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('mod_project/docs/FORMULAS.md', 'r', encoding='utf-8') as f:
    text = f.read()

for m in re.finditer(r'.{0,100}(?:First Grid|Warning Shot).{0,100}', text):
    print("MATCH:", m.group(0).strip().replace('\n', ' '))

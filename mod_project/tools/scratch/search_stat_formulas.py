with open('mod_project/docs/FORMULAS.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'.{0,100}(?:base stat|equipment stat|all stat|stat bonus).{0,100}', text, re.IGNORECASE)
for m in matches[:10]:
    print("MATCH:", m.strip().replace('\n', ' '))

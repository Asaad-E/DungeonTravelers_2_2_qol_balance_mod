with open('mod_project/tools/exe_enchants.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'.{0,100}(?:24|all stat|stack).{0,100}', text, re.IGNORECASE)
for m in matches[:10]:
    print("ENCHANT MATCH:", m.strip().replace('\n', ' '))

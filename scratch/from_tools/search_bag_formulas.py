with open('mod_project/docs/FORMULAS.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'.{0,100}(?:item bag|30 item|inventory|bag size|bag of 30).{0,100}', text, re.IGNORECASE)
for m in matches[:10]:
    print("BAG MATCH:", m.strip().replace('\n', ' '))

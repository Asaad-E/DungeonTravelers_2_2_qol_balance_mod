import re

with open('mod_project/docs/FORMULAS.md', 'r', encoding='utf-8') as f:
    content = f.read()

def search_kw(kw):
    print(f"=== Keyword: {kw} ===")
    matches = re.findall(rf'.{{0,80}}{kw}.{{0,120}}', content, re.IGNORECASE)
    for m in matches[:5]:
        print("  ", m.strip().replace('\n', ' '))

for kw in ['forge', 'enchantment', 'grand sealbook', 'meal', 'inventory', 'quest', 'trap', 'zone']:
    search_kw(kw)

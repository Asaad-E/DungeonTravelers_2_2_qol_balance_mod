import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('mod_project/docs/FORMULAS.md', 'r', encoding='utf-8') as f:
    formulas = f.read()

def show_section(title, pattern):
    print(f"\n--- {title} ---")
    m = re.search(pattern, formulas, re.DOTALL | re.IGNORECASE)
    if m:
        snippet = m.group(0)[:800]
        print(snippet)
    else:
        print("Not found")

show_section("Enchantments stacking (S09)", r"(?:stacking flag|enchantment.*all stats|all stats.*enchantment|0x44ae|0x44b6)")
show_section("Damage zones (F91, F96, S14)", r"### 2\.5 Damage zones of the map.*?(?=###)")
show_section("Grand sealbooks (F89)", r"grand sealbook.*?(?=\n\n\n|\Z)")
show_section("Traps and Trap Search (S15)", r"trap.*?(?=\n\n|\Z)")

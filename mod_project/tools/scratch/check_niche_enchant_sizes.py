import sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Search for enchantments 222-225, 264, 281, 292, 297 in ENCHANT_SIZES.md
with open('mod_project/docs/generated/ENCHANT_SIZES.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

target_ids = {217, 222, 223, 224, 225, 246, 248, 257, 264, 281, 292, 293, 297}
for l in lines:
    for tid in target_ids:
        if f"| {tid} |" in l:
            print(l.strip())

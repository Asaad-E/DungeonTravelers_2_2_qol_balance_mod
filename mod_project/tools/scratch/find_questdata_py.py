import os

for root, dirs, files in os.walk('mod_project'):
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                c = fh.read()
                if 'QuestData' in c:
                    print("Found QuestData in:", p)

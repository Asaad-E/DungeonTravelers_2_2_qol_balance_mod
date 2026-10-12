import os, re

for root, dirs, files in os.walk('mod_project'):
    for f in files:
        if f.endswith(('.py', '.md', '.txt')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
                if 'S18' in content or 'bag of 30' in content.lower():
                    print(f"Found in {path}")
                    for line in content.splitlines():
                        if 'S18' in line or 'bag' in line.lower() and '30' in line:
                            print("  ", line.strip())

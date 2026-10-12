import os, re

sim_dir = 'mod_project/sim'
files = [os.path.join(sim_dir, f) for f in os.listdir(sim_dir) if f.endswith('.py')]

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    for sid, sname in [(270, 'Warning Shot'), (309, 'First Grid')]:
        matches = re.findall(rf'.{{0,50}}(?:{sid}|{sname}).{{0,50}}', content, re.IGNORECASE)
        if matches:
            print(f"File {os.path.basename(path)} matches for {sname} ({sid}):")
            for m in matches[:5]:
                print(f"  {m.strip().replace(chr(10), ' ')}")

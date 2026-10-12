import subprocess, os, json

# 1. Get old DIFFICULTY_CURVE.md content from git commit e2cf414
old_curve_text = subprocess.check_output(
    ['git', 'show', 'e2cf414:mod_project/docs/generated/DIFFICULTY_CURVE.md'],
    text=True, encoding='utf-8'
)

# 2. Get new DIFFICULTY_CURVE.md content
with open('mod_project/docs/generated/DIFFICULTY_CURVE.md', 'r', encoding='utf-8') as f:
    new_curve_text = f.read()

def parse_curve_table(text):
    data = {}
    for line in text.splitlines():
        if (line.startswith('| C') or line.startswith('| P')) and not line.startswith('| Checkpoint'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            cid = parts[0]
            lvl = parts[1]
            # Wins: vanilla > variant
            wins_v, wins_m = parts[2].split('>')
            # Length: vanilla > variant
            len_v, len_m = parts[3].split('>')
            # Lowest HP: vanilla > variant
            hp_v, hp_m = parts[4].split('>')
            # Out of window
            status = parts[6] if len(parts) > 6 else ''
            data[cid] = {
                'lvl': lvl,
                'vanilla': f"{wins_v.strip()} / {len_v.strip()}t / {hp_v.strip()}",
                'mod': f"{wins_m.strip()} / {len_m.strip()}t / {hp_m.strip()}",
                'status': status
            }
    return data

old_data = parse_curve_table(old_curve_text)
new_data = parse_curve_table(new_curve_text)

print("| Checkpoint | Lvl | Vanilla (Wins / Turns / HP) | Old Mod | New Mod | Diff / Notes |")
print("|---|---|---|---|---|---|")

for cid in new_data:
    old = old_data.get(cid, {})
    new = new_data.get(cid, {})
    lvl = new.get('lvl', '')
    v_str = new.get('vanilla', '')
    old_mod = old.get('mod', '-')
    new_mod = new.get('mod', '-')
    diff = "Unchanged" if old_mod == new_mod else f"Changed ({new.get('status')})"
    print(f"| {cid} | {lvl} | {v_str} | {old_mod} | {new_mod} | {diff} |")

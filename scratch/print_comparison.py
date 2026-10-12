import sys, subprocess, json
sys.path.insert(0, 'mod_project')
from sim import setup as setup_mod

setup = setup_mod.load()
cp_map = {}
for c in setup.checkpoints:
    cid = str(c.get('ID', ''))
    cp_map[cid] = {
        'level': c.get('Level', ''),
        'boss': str(c.get('Boss (as the story page names it)', '') or ''),
        'chapter': str(c.get('Chapter', '') or '')
    }

old_curve_text = subprocess.check_output(
    ['git', 'show', 'e2cf414:mod_project/docs/generated/DIFFICULTY_CURVE.md'],
    text=True, encoding='utf-8'
)

with open('mod_project/docs/generated/DIFFICULTY_CURVE.md', 'r', encoding='utf-8') as f:
    new_curve_text = f.read()

def parse_curve_table(text):
    data = {}
    for line in text.splitlines():
        if (line.startswith('| C') or line.startswith('| P')) and not line.startswith('| Checkpoint'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            cid = parts[0]
            lvl = parts[1]
            wins_v, wins_m = parts[2].split('>')
            len_v, len_m = parts[3].split('>')
            hp_v, hp_m = parts[4].split('>')
            status = parts[6] if len(parts) > 6 else ''
            data[cid] = {
                'lvl': lvl,
                'vanilla': f"{wins_v.strip()} | {len_v.strip()}t | {hp_v.strip()}",
                'mod': f"{wins_m.strip()} | {len_m.strip()}t | {hp_m.strip()}",
                'wins_v': wins_v.strip(),
                'wins_m': wins_m.strip(),
                'len_v': len_v.strip(),
                'len_m': len_m.strip(),
                'hp_v': hp_v.strip(),
                'hp_m': hp_m.strip(),
                'status': status
            }
    return data

old_data = parse_curve_table(old_curve_text)
new_data = parse_curve_table(new_curve_text)

with open('mod_project/scratch/comparison_out.txt', 'w', encoding='utf-8') as out_f:
    out_f.write("| Checkpoint | Boss / Zona | Nivel | Vanilla (Win / Turnos / HP min) | Old Mod (e2cf414) | New Mod (HEAD) | Estado / Impacto |\n")
    out_f.write("|---|---|---|---|---|---|---|\n")

    changed_count = 0
    unchanged_count = 0

    for cid, n in new_data.items():
        o = old_data.get(cid, {})
        meta = cp_map.get(cid, {})
        boss = meta.get('boss', 'Desconocido')
        lvl = n.get('lvl', meta.get('level', ''))
        v_str = n.get('vanilla', '-')
        old_mod = o.get('mod', '-')
        new_mod = n.get('mod', '-')
        
        if old_mod != new_mod:
            changed_count += 1
            status_note = f"**Modificado**: {n.get('status', 'cambio')}"
        else:
            unchanged_count += 1
            status_note = "Sin cambios (idéntico)"
            
        out_f.write(f"| {cid} | {boss} | Lvl {lvl} | {v_str} | {old_mod} | {new_mod} | {status_note} |\n")

    out_f.write(f"\nResumen: {len(new_data)} checkpoints analizados. {changed_count} cambiaron respecto al Old Mod, {unchanged_count} permanecieron idénticos.\n")

print(f"Generated comparison. Changed: {changed_count}, Unchanged: {unchanged_count}")

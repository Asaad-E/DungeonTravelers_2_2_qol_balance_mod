import json
import os
import sys

BASE_DIR = 'mod_project'
JSON_PATH = os.path.join(BASE_DIR, 'scratch', 'battery_old_vs_new_ai_results.json')
OUT_MD = os.path.join(BASE_DIR, 'docs', 'generated', 'PARTY_BATTERY_OLD_VS_NEW_AI.md')

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    matrix = json.load(f)

CHECKPOINTS = ['C06', 'C10', 'C13', 'C17', 'C18', 'C19', 'C21', 'C24', 'C26', 'C28', 'C29', 'C30', 'C32', 'C34', 'C36', 'C38', 'C40']
PARTIES = ['Meta', 'Dual-Support', 'Mage-Heavy', 'Juggernaut', 'Anti-Meta']

BOSS_NAMES = {
    'C06': 'Ghast', 'C10': 'Vrachia Lord', 'C13': 'Eros', 'C17': 'Agent M',
    'C18': 'True King Eltricia', 'C19': 'Siesta', 'C21': 'Trafficker Twinny',
    'C24': 'Afanc', 'C26': 'Michelle & Beatrice', 'C28': 'Spirit of Mag Mell',
    'C29': 'Calliope', 'C30': 'Heartless Avenger', 'C32': 'Moby Dick',
    'C34': 'Queen of Darkness', 'C36': 'Demon God Fried', 'C38': 'Samael',
    'C40': 'Demiurge & Atialuco'
}

lines = []
lines.append("# Batería Completa: Rendimiento de las 5 Parties bajo Old AI vs New AI\n")
lines.append("Auditoría exhaustiva de los **17 Jefes de la Historia** a lo largo de las **5 Parties canónicas** (N = 20 ejecuciones por combate, 6,800 batallas simuladas).\n")
lines.append("Compara directamente el comportamiento bajo:\n")
lines.append("- **Old AI:** IA anterior (evaluación aislada, ceguera a combos de grupo, gasto excesivo de TP por overkill, despertar de enemigos dormidos, uso suicida de Berserk).\n")
lines.append("- **New AI:** IA inteligente táctica (enlace de habilidades, prioridad letal focus fire, interrupción de cánticos, disciplina de sueño CC, anti-overkill, triaje de cobertura del tanque y disipación de barreras).\n")
lines.append("\n---\n")

lines.append("## 1. Tabla Comparativa: Variante Mod (Old AI → New AI)\n")
lines.append("Muestra cómo la IA inteligente potencia o estabiliza cada party en el Mod:\n")
lines.append("| Checkpoint | Jefe | Meta | Dual-Support | Mage-Heavy | Juggernaut | Anti-Meta |")
lines.append("|:---:|---|:---:|:---:|:---:|:---:|:---:|")

for cid in CHECKPOINTS:
    bname = BOSS_NAMES.get(cid, cid)
    row = [f"**{cid}**", bname]
    for p in PARTIES:
        d = matrix[cid][p]
        m_old_pct, m_old_rnd, m_old_won = d['m_old']
        m_new_pct, m_new_rnd, m_new_won = d['m_new']
        
        old_str = f"{m_old_pct:.0f}%" if m_old_won else "0%"
        new_str = f"{m_new_pct:.0f}%" if m_new_won else "0%"
        
        if m_new_pct > m_old_pct:
            cell = f"{old_str} → **{new_str}** (+{m_new_pct - m_old_pct:.0f}%)"
        elif m_new_pct < m_old_pct:
            cell = f"{old_str} → {new_str} ({m_new_pct - m_old_pct:.0f}%)"
        else:
            cell = f"**{new_str}**"
        row.append(cell)
    lines.append("| " + " | ".join(row) + " |")

lines.append("\n---\n")
lines.append("## 2. Tabla Comparativa: Vanilla (Old AI → New AI)\n")
lines.append("Muestra el efecto de la IA inteligente sobre los números base de Vanilla:\n")
lines.append("| Checkpoint | Jefe | Meta | Dual-Support | Mage-Heavy | Juggernaut | Anti-Meta |")
lines.append("|:---:|---|:---:|:---:|:---:|:---:|:---:|")

for cid in CHECKPOINTS:
    bname = BOSS_NAMES.get(cid, cid)
    row = [f"**{cid}**", bname]
    for p in PARTIES:
        d = matrix[cid][p]
        v_old_pct, v_old_rnd, v_old_won = d['v_old']
        v_new_pct, v_new_rnd, v_new_won = d['v_new']
        
        old_str = f"{v_old_pct:.0f}%" if v_old_won else "0%"
        new_str = f"{v_new_pct:.0f}%" if v_new_won else "0%"
        
        if v_new_pct > v_old_pct:
            cell = f"{old_str} → **{new_str}** (+{v_new_pct - v_old_pct:.0f}%)"
        elif v_new_pct < v_old_pct:
            cell = f"{old_str} → {new_str} ({v_new_pct - v_old_pct:.0f}%)"
        else:
            cell = f"**{new_str}**"
        row.append(cell)
    lines.append("| " + " | ".join(row) + " |")

lines.append("\n---\n")
lines.append("## 3. Matriz de Paridad Cruzada: Vanilla (New AI) vs Mod (New AI)\n")
lines.append("Verificación de que bajo la misma IA inteligente, el Mod mantiene paridad y no introduce roturas desproporcionadas:\n")
lines.append("| Checkpoint | Jefe | Meta (Van → Mod) | Dual-Support (Van → Mod) | Mage-Heavy (Van → Mod) | Juggernaut (Van → Mod) | Anti-Meta (Van → Mod) |")
lines.append("|:---:|---|:---:|:---:|:---:|:---:|:---:|")

for cid in CHECKPOINTS:
    bname = BOSS_NAMES.get(cid, cid)
    row = [f"**{cid}**", bname]
    for p in PARTIES:
        d = matrix[cid][p]
        v_new_pct = d['v_new'][0]
        m_new_pct = d['m_new'][0]
        row.append(f"{v_new_pct:.0f}% → **{m_new_pct:.0f}%**")
    lines.append("| " + " | ".join(row) + " |")

with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines) + "\n")

print(f"Reporte generado exitosamente en: {OUT_MD}")

"""
QoL text of the party skills: proposes it and keeps it in a workbook edited by hand.

    python tools/generate_qol_party_skill_text.py

Workbook: data_tables/qol_party_skill_text.xlsx
  * A party skill has two lines: who must be in the party (never touched) and what it gives.
  * The second line keeps the game's sentence and gains the upper bound of each bonus:
        "Max HP increased."  ->  "Max HP increased (up to +100)."
    The box of the list holds about 50 characters, so a line that names two bonuses is reworded:
        "Wind resistance and AGI increased."  ->  "Up to wind resistance +20% and AGI +10."
    The screen itself shows the award count.
  * PartySkillData.pck holds no amount (an entry is its members and the id of its effect). The bounds
    come from the DT2-2 wiki, pages/72.html, which also gives the rule the game itself states: the
    bonus grows with the awards earned and reaches the bound with all 50.
  * The sentences and their bounds are the sheet PartySkillBounds of qol_rules.xlsx.
    A skill without a sentence there keeps its line.
"""
import os
import sys
import collections
import openpyxl
import rules
from pck_handler import PckArchive, PartySkillHelper
from text_checks import party_skill_text, check_party_skill_text, party_skill_bounds

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_PATH = os.path.join(BASE_DIR, 'backups', 'PartySkillData.pck')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data_tables', 'qol_party_skill_text.xlsx')
HEADERS = ['Filename', 'Skill', 'Members', 'Vanilla_Effect', 'QoL_Effect', 'Edited', 'Effect_ID', 'Bounds', 'Source']
MAX_LINE = rules.setting('party_line_width')


def load_edited():
    if not os.path.exists(OUTPUT_PATH):
        return {}
    ws = openpyxl.load_workbook(OUTPUT_PATH)['PartySkills']
    header = [c.value for c in ws[1]]
    fn, text, edited = header.index('Filename'), header.index('QoL_Effect'), header.index('Edited')
    return {r[fn]: r[text] or '' for r in ws.iter_rows(min_row=2, values_only=True)
            if str(r[edited] or '').strip().lower() == 'yes'}


def main():
    edited, stats, rows = load_edited(), collections.Counter(), []
    sources = {int(r['Effect_ID']): r['Source'] for r in rules.rows('PartySkillBounds')}
    for fn, b in PckArchive(BACKUP_PATH).files:
        skill = PartySkillHelper.read_party_skill(b)
        effect = edited.get(fn) or party_skill_text(b, skill['effect'])
        problems, _ = check_party_skill_text(b, effect, skill['effect'])
        if len(effect) > MAX_LINE:
            problems.append(f'{len(effect)} characters, the line holds {MAX_LINE}')
        if problems:
            raise SystemExit(f"{fn} ({skill['name']}): {problems}")
        stats['bounds added' if effect != skill['effect'] else 'kept as written (no bound in any guide)'] += 1
        rows.append([fn, skill['name'], skill['req'], skill['effect'], effect, 'yes' if fn in edited else '',
                     skill['effect_id'], ', '.join(party_skill_bounds(b)), sources.get(skill['effect_id'], '')])
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'PartySkills'
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    for col, width in zip('ABCDEFGHI', (26, 20, 50, 46, 80, 8, 10, 14, 26)):
        ws.column_dimensions[col].width = width
    wb.save(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}: {len(rows)} party skills")
    for key in sorted(stats):
        print(f"    {stats[key]:4d}  {key}")
    for r in rows:
        print(f"        {len(r[4]):3d}  {r[1]}: {r[4]}")


if __name__ == '__main__':
    sys.exit(main())

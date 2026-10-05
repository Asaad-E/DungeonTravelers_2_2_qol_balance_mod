"""
QoL text of the joint skills: fills the sentences of the rules workbook with the stored values.

    python mod_project/tools/generate_qol_joint_skill_text.py

Workbook written: mod_project/data_tables/qol_joint_skill_text.xlsx (generated; read by the build)
  * A joint skill has one sentence of one line. Where it speaks of an effect whose value the entry
    stores, the value goes into the sentence and takes the place of the vague word:
        "Deal physical damage to an enemy row. High chance of instakill."
     -> "Deal physical damage to an enemy row. 85% chance of instakill."
  * To change a sentence, edit the sheet JointSkillSentences of qol_rules.xlsx ({e119} is the value of
    effect 119) and run this again. A skill without a row there keeps the game's text.
  * The other columns are what the entry stores and no text says yet: participants, the share of max
    TP each one pays (the DT2-2 wiki lists the same fractions, pages/27.html), Pep needed and spent,
    power, turns, delay and every effect. They are there to read, not built into the game.
"""
import os
import sys
import collections
import openpyxl
import rules
from pck_handler import PckArchive, JoinSkillHelper
from text_checks import joint_skill_text, check_joint_skill_text, JOINT_SENTENCES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_PATH = os.path.join(BASE_DIR, 'backups', 'JoinSkillData.pck')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data_tables', 'qol_joint_skill_text.xlsx')
HEADERS = ['Filename', 'Skill', 'Vanilla_Desc', 'QoL_Desc', 'Length', 'Participants', 'TP_Cost', 'Pep_Needed',
           'Pep_Spent', 'Power', 'Turns', 'Delay', 'Effects (id:value)']
MAX_LINE = rules.setting('line_width')


def main():
    stats, rows, names = collections.Counter(), [], set()
    for fn, b in PckArchive(BACKUP_PATH).files:
        skill = JoinSkillHelper.read_joint(b)
        names.add(skill['name'])
        text, problems = joint_skill_text(b, skill['name'], skill['desc'])
        problems += check_joint_skill_text(b, skill['name'], text, skill['desc'])[0]
        if len(text) > MAX_LINE:
            problems.append(f'{len(text)} characters, the line holds {MAX_LINE}')
        if problems:
            raise SystemExit(f"{fn} ({skill['name']}): {problems}")
        stats['stored values written into the sentence' if text != skill['desc'] else 'kept as written'] += 1
        rows.append([fn, skill['name'], skill['desc'], text, len(text), skill['members'],
                     f"1/{skill['tp_divisor']} of max TP", round(skill['pep_needed'], 2), round(skill['pep_cost'], 2),
                     round(skill['power'], 3), round(skill['turns'], 2), round(skill['delay'], 3),
                     ', '.join(f'{i}:{v:g}' for i, v, _ in skill['effects'])])
    unknown = set(JOINT_SENTENCES) - names
    if unknown:
        raise SystemExit(f"qol_rules.xlsx/JointSkillSentences names skills that do not exist: {sorted(unknown)}")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'JointSkills'
    ws.append(HEADERS)
    for r in rows:
        ws.append(r)
    for col, width in zip('ABCDEFGHIJKLM', (24, 24, 85, 85, 8, 12, 16, 11, 10, 8, 7, 7, 50)):
        ws.column_dimensions[col].width = width
    wb.save(OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH}: {len(rows)} joint skills")
    for key in sorted(stats):
        print(f"    {stats[key]:4d}  {key}")
    for r in rows:
        if r[2] != r[3]:
            print(f"        {r[4]:3d}  {r[1]}: {r[3]}")


if __name__ == '__main__':
    sys.exit(main())

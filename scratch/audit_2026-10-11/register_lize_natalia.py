"""The decisions of the user of 2026-10-12 (evening) written into the workbooks: the unique skill of Lizerietta becomes
evasion (effect 338 in the place of 350, new values, a name and a box for the variant), and the RES of Natalia, the
guest healer, times 1.5 on her five stages. Run once.

    python register_lize_natalia.py
"""
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
TABLES = os.path.join(PROJECT, 'data_tables')
TODAY = '2026-10-12'
EVASION = [0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.24, 0.26, 0.35]
NAME = 'Small Target'
BOX = ('Enemy attacks and spells are less likely to hit her.\n'
       'Evasion: 10% -> 12 -> 14 -> 16 -> 18 -> 20 -> 22 -> 24 -> 26%   |   Crown EX: 35%')
NATALIA = ((76, 28, 41), (77, 40, 82), (78, 49, 101), (79, 57, 123), (80, 68, 148))
WHY_LIZE = ('Decided 2026-10-12: her unique skill becomes evasion: it tells what she is in the game (the smallest of the '
            'team), it serves in every class and every fight, and it suits her dolls without being tied to them (a blow '
            'that misses her cannot end her dolls, her chant or her dance: docs/FORMULAS.md 16.6). Effect 338 is read '
            'among the evasion buffs of the target of a blow (0x44ac56) and of a spell (0x44d8cb), in the list of '
            'statuses where the unique skills are found (443 and 440 at 0x44b3db, 0x44ccb2). Tried '
            '(scratch/audit_2026-10-11/lize_ideas.py, 100 battles a cell, as papillon, doll master and joker at C36, '
            'C40, P24): from +0.10 to +0.30 the wins stay within the noise of the party without it or a little above; '
            'nothing breaks at +0.30')
WHY_NATALIA = ('Decided 2026-10-12: approved. Measured (scratch/audit_2026-10-11/mercenary_log.py, mercenary_trial.py): '
               'the last of the named mercenaries (78% / 93% / 100% at C36, C40, P24); she heals 368 and 626 HP a fight '
               'where Priscilla heals 1,019 and 2,496. Her heal spells are shared with enemies, her RES is hers alone and '
               'is what her Heal is worked from: times 1.5 takes C36 from 81% to 87% (Priscilla 90%)')


def main():
    path = os.path.join(TABLES, 'balance_changes.xlsx')
    wb = openpyxl.load_workbook(path)
    ws = wb['Changes']
    col = {c.value: k for k, c in enumerate(ws[1])}
    ids = {row[0].value for row in ws.iter_rows(min_row=2)}
    for row in ws.iter_rows(min_row=2):
        if str(row[col['Record']].value) == 'Unique 370 Usurper of Souls' and row[col['Field']].value == 'value':
            row[col['New']].value = EVASION[int(row[col['Level']].value) - 1]
            row[col['Why']].value = WHY_LIZE
            row[col['Lever']].value = 'L41'
            row[col['Decided']].value = TODAY
            row[col['State']].value = 'decided'
    new = [('U051', 'unique', 'Unique 370 Usurper of Souls', 'effect id', None, 350, 338, 'L43', 'I11', WHY_LIZE, TODAY, 'decided')]
    for k, (nid, level, res) in enumerate(NATALIA):
        new.append((f'N{k + 1:03d}', 'npcs', f'{nid} Natalia (level {level})', 'res', None, res, int(res * 1.5), 'L44', 'F94',
                    WHY_NATALIA, TODAY, 'decided'))
    for values in new:
        if values[0] in ids:
            raise SystemExit(f'{values[0]} is already in the workbook')
        ws.append(list(values))
    wb.save(path)

    path = os.path.join(TABLES, 'balance_criteria.xlsx')
    wb = openpyxl.load_workbook(path)
    ws = wb['Levers']
    ws.append(['L43', 'Which effect a unique skill is a status of', 'UniqueSkillData.pck', '0x50, one int', 'Benign',
               'The effect is one the program reads among the statuses of its bearer, with no skill or roll of its own',
               'docs/FORMULAS.md 12.19; the unique skills are looked up as any status (0x47e340 on the lists of the blow '
               'function). Not seen working in the game yet'])
    ws.append(['L44', 'A stat of a guest ally at one stage', 'NPC/NPC.pck, NPCData.bin', '0x20, six ints', 'Benign',
               'The value stays a whole number above 0', 'tools/npc_data.py (the stats are read at 0x4fed59 - 0x4fee27). '
               'Not seen working in the game yet'])
    ws = wb['Criticisms']
    col = {c.value: k for k, c in enumerate(ws[1])}
    for row in ws.iter_rows(min_row=2):
        if row[0].value == 'I11':
            row[col['Proposal']].value = ('U011 - U020, U051: the skill becomes evasion (effect 338, 10 - 26% by rank, 35% '
                                          'with the crown), named again in the variant')
            row[col['Decision']].value = (str(row[col['Decision']].value or '') + f' | {TODAY} (evening), decided: the '
                                          'effect is changed for evasion, which serves in every class and fight').strip(' |')
        if row[0].value == 'F94':
            row[col['Decision']].value = (str(row[col['Decision']].value or '') + f' | {TODAY}: every mercenary measured '
                                          '(scratch/audit_2026-10-11/MERCENARIES.md); none above the summon of the grand '
                                          'sealbook; Natalia, the last, gets RES x1.5 (N001 - N005)')
    wb.save(path)

    path = os.path.join(TABLES, 'balance_skill_text.xlsx')
    wb = openpyxl.load_workbook(path)
    ws = wb['Skills']
    head = [c.value for c in ws[1]]
    if 'Balance_Name' not in head:
        ws.cell(row=1, column=len(head) + 1, value='Balance_Name')
        head.append('Balance_Name')
    line = {'Category': 'Unique', 'Filename': 'UniqueSkillData_0370.bin', 'Skill_Name': 'Usurper of Souls',
            'Balance_Desc': BOX, 'Balance_Name': NAME,
            'Note': 'Rows U011 - U020, U051: the skill is evasion in the variant, with a name and a sentence of its own'}
    ws.append([line.get(h) for h in head])
    wb['About'].append(['Balance_Name', 'The name the variant gives a skill whose effect it changes; empty keeps the name of the game.'])
    wb.save(path)

    path = os.path.join(TABLES, 'qol_rules.xlsx')
    wb = openpyxl.load_workbook(path)
    wb['UniqueSkillLabels'].append([NAME, 'Evasion', 'The name the Balance variant gives the unique skill of Lizerietta '
                                    '(balance_skill_text.xlsx): its value is taken from the hit chance of a blow or a '
                                    'spell on her (effect 338, docs/FORMULAS.md 2.1)'])
    wb.save(path)
    print('written')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

"""Sheet MercenaryUnlocks of data_tables/sim_setup.xlsx (2026-10-17): when each flag that unlocks a stage of a mercenary is set, as a
checkpoint of the model. The bar offers, of the stages whose flag is set, the one of the highest level (0x58adb0 - 0x58b060, read
2026-10-17; docs/FORMULAS.md 16.5). The flag of each stage is the int at 0xB4 of its NPCData.

Story flags: by the chapter the research gives (the code and spoiler.jp, 傭兵バディ pages), set at the first checkpoint of that part of the
chapter. Flags of the postgame, of side events and of the quest rank: where they are set is not mapped, so the stage is taken as open
from the first checkpoint whose reference level reaches its level (Basis says "approximate"). 1000 - 1003 are never open (placeholders and
Michelle, a guest of the story); 1106 (Peggy & Beard) is open from the middle of chapter 8 to the middle of chapter 9."""
import os
import re
import sys
import openpyxl

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import npc_data                                       # noqa: E402

PATH = os.path.join(ROOT, 'data_tables', 'sim_setup.xlsx')
SOURCE = 'docs/FORMULAS.md 16.5 (the flag at 0xB4 of NPCData; the bar 0x58adb0); spoiler.jp dt2-2 傭兵バディ pages'
STORY = {   # flag: (from checkpoint, the moment the research gives)
    135: ('C25', 'chapter 7, the Tavern opens (temple of Wrappl)'),
    136: ('C26', 'chapter 7, after the event of the chapter'),
    151: ('C27', 'chapter 8, its start'),
    319: ('C32', 'chapter 9, its start'),
    320: ('C33', 'chapter 9, its progress'),
    172: ('C35', 'chapter 10, its start'),
    197: ('C37', 'chapter 11, its start'),
    204: ('C37', 'chapter 10 or 11 (the research gives both): taken at the start of chapter 11'),
    353: ('C38', 'chapter 11, its progress: after the one checkpoint of the chapter (C37)'),
}
NEVER = {1000: 'placeholder record 101', 1001: 'placeholder record 102', 1002: 'placeholder record 103',
         1003: 'Michelle, a guest of the story, not hired at the Tavern'}
PEGGY = (1106, 'C28', 'C32', 'from the 9th talk event (chapter 8) to the 10th (chapter 9)')

ref, order = {}, []
for line in open(os.path.join(ROOT, 'docs', 'generated', 'CHECKPOINT_LEVELS.md'), encoding='utf-8'):
    c = [x.strip() for x in line.strip().strip('|').split('|')]
    if len(c) > 5 and re.fullmatch(r'[CP]\d+a?', c[0]) and c[5].isdigit() and c[0] not in ref:
        ref[c[0]] = int(c[5])
        order.append(c[0])
levels = {}
for n in npc_data.npcs():
    levels.setdefault(n['unlock_flag'], []).append(n['level'])

rows = []
for flag in sorted(levels):
    if flag in NEVER:
        rows.append((flag, None, None, 'never: ' + NEVER[flag], SOURCE))
    elif flag == PEGGY[0]:
        rows.append((flag, PEGGY[1], PEGGY[2], 'story: ' + PEGGY[3], SOURCE))
    elif flag in STORY:
        rows.append((flag, STORY[flag][0], None, 'story: ' + STORY[flag][1], SOURCE))
    else:
        lv = min(levels[flag])
        postgame = flag not in (1089, 1094)
        pool = [c for c in order if c.startswith('P')] if postgame else order
        first = next((c for c in pool if ref[c] >= lv), pool[-1])
        rows.append((flag, first, None, 'approximate: %s, where the flag is set is not mapped; open from the first %scheckpoint whose '
                     'reference level reaches the stage (level %d)' % ('postgame' if postgame else 'side event', 'postgame ' if postgame else '', lv),
                     SOURCE))

wb = openpyxl.load_workbook(PATH)
if 'MercenaryUnlocks' in wb.sheetnames:
    del wb['MercenaryUnlocks']
ws = wb.create_sheet('MercenaryUnlocks')
ws.append(['Flag', 'From checkpoint', 'Until checkpoint', 'Basis', 'Source'])
for r in rows:
    ws.append(list(r))
wb.save(PATH)
print(len(rows), 'flags;', sum(1 for r in rows if r[3].startswith('approximate')), 'approximate')

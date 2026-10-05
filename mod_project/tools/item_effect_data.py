"""
Item effects: what the program does with each effect type of ItemData.

An item carries up to four (type, value) pairs. When it is used the program builds one object per pair through a
switch of 107 cases (0x50c596, table 0x50e538); each case is a class of its own, and the method at slot 3 of that
class does the work. For 39 types that method is three pushes and a call: the item performs a skill of the game
(0x50b030 with the skill id), so its numbers are those of the skill file. This tool reads that map from the
executable.

The other types have code of their own. Read so far (docs/FORMULAS.md 15):
    0        heals HP by the value, plus int(value * Item Mastery) (0x50e789)
    53, 54   damage of int(max HP of the target * value), at most 100 (0x511b78)
    89       the party loses a twentieth of its gold, at least 1 (0x51438a); the value of the item is not used

    python mod_project/tools/item_effect_data.py        prints the map
"""
import os
import re
import struct
import sys

import openpyxl

from exe_reader import Exe

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx')
SWITCH_TABLE, TYPES = 0x50e538, 107
APPLY_SLOT = 3
RDATA = (0x630000, 0x720000)              # where the class tables of the program live
# push -1; push flag; push skill id (one byte or four); call
PERFORMS_A_SKILL = re.compile(rb'\x6a\xff\x6a(.)(?:\x6a(.)|\x68(....))\xe8', re.S)


def skill_items(exe=None):
    """{item effect type: (skill id, flag)} for the types whose class only performs a skill."""
    exe = exe or Exe()
    cases = struct.unpack(f'<{TYPES}I', exe.read(SWITCH_TABLE, 4 * TYPES))
    found = {}
    for kind, case in enumerate(cases):
        stores = [struct.unpack('<I', m.group(1))[0] for m in re.finditer(rb'\xc7[\x00-\x07](....)', exe.read(case, 0x60), re.S)]
        vtables = [v for v in stores if RDATA[0] <= v < RDATA[1]]
        if not vtables:
            continue
        method = exe.u32(vtables[-1] + 4 * APPLY_SLOT)
        m = PERFORMS_A_SKILL.match(exe.read(method, 16))
        if m:
            found[kind] = (m.group(2)[0] if m.group(2) else struct.unpack('<I', m.group(3))[0], m.group(1)[0])
    return found


def skill_names():
    rows = openpyxl.load_workbook(WORKBOOK, read_only=True)['Skills'].iter_rows(min_row=2, values_only=True)
    return {r[2]: r[3] for r in rows}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    names = skill_names()
    for kind, (skill, flag) in sorted(skill_items().items()):
        print(f'type {kind:3d}: performs skill {skill} ({names.get(skill)}), flag {flag}')


if __name__ == '__main__':
    main()

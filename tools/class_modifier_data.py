"""
Class modifiers: what each class gains from the equipment it specialises in.

Game::CGamePlayerStatus::_CalculateParameterSpecialty (0x4f7c60) switches on the class of a character (and, for six
advanced classes, on the class it came from) and picks a table written in the executable. An entry is twelve bytes:

    slot (int)     the equipment slot it looks at: 0 the weapon, 1 the off hand, 2 to 4 the other pieces
    type (int)     for slot 0, the weapon type the piece must have (EquipmentData 0x50); unused for the others.
                   Slot 1 counts only when it holds a piece of category 1 (EquipmentData 0x20)
    modifier (float)

For every stat that piece gives (above 0), the character gains
    int((stat of the character + stat of the piece) * modifier)
where the modifier is the entry plus 0.01 per point of Yearning (effect 449). The gains are added to the six stats
after the equipment (docs/FORMULAS.md 10.4).

The tables are data of the executable (.rdata, 0x6d3b64 - 0x6d40a0), not of a game file.

    python tools/class_modifier_data.py        prints the table of every class
"""
import os
import re
import struct
import sys

import capstone
import openpyxl

import class_data
from exe_reader import Exe

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKBOOK = os.path.join(BASE_DIR, 'data_tables', 'vanilla_source_of_truth.xlsx')
JUMP_TABLE, CLASSES = 0x4f81e8, 32
LOOP_WITH_COUNT, LOOP_OF_TWO = 0x4f7eb1, 0x4f7eac          # the two ways into the loop: count in edi, or a count of 2
ENTRY = 12
SLOTS = {0: 'weapon', 1: 'Shield', 2: 'slot 2', 3: 'slot 3', 4: 'slot 4'}      # category 1 of the equipment file is the shields


def _cases(exe):
    """{class id: [(previous class or None, table address, entries)]} decoded from the code of each case."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    starts = struct.unpack(f'<{CLASSES}I', exe.read(JUMP_TABLE, 4 * CLASSES))
    order = sorted(set(starts))
    found = {}
    for class_id, start in enumerate(starts):
        end = min([s for s in order if s > start] + [LOOP_OF_TWO])
        previous = count = table = None
        rows = []
        for i in md.disasm(exe.read(start, end - start), start):
            text = f'{i.mnemonic} {i.op_str}'
            m = re.fullmatch(r'cmp eax, (0x[0-9a-f]+|\d+)', text)
            if m:
                previous, count, table = int(m.group(1), 0), None, None
            m = re.fullmatch(r'mov edi, (0x[0-9a-f]+|\d+)', text)
            if m:
                count = int(m.group(1), 0)
            m = re.fullmatch(r'lea edi, \[eax ([+-]) (0x[0-9a-f]+|\d+)\]', text)
            if m:
                count = previous + int(m.group(2), 0) * (1 if m.group(1) == '+' else -1)
            m = re.fullmatch(r'mov esi, (0x[0-9a-f]+)', text)
            if m:
                table = int(m.group(1), 16)
            m = re.fullmatch(r'jmp (0x[0-9a-f]+)', text)
            if m and table:
                rows.append((previous, table, count if int(m.group(1), 16) == LOOP_WITH_COUNT else 2))
                table = count = None
        if table:                                           # the last case falls into the loop of two
            rows.append((previous, table, 2))
        found[class_id] = rows
    return found


def _weapon_types():
    ws = openpyxl.load_workbook(WORKBOOK, read_only=True)['Equipment']
    it = ws.iter_rows(values_only=True)
    header = next(it)
    names = {}
    for r in it:
        d = dict(zip(header, r))
        if d['Category_Code'] == 0 and d['Unidentified_Name']:
            names.setdefault(d['Type_Code'], d['Unidentified_Name'].replace('??? ', ''))
    return names


def class_modifiers(exe=None):
    """[{'class', 'previous' (None when the route does not matter), 'entries': [{'slot', 'type', 'type_name', 'modifier'}]}]"""
    exe = exe or Exe()
    types = _weapon_types()
    found = []
    for class_id, rows in _cases(exe).items():
        for previous, table, count in rows:
            entries = []
            for k in range(count):
                slot, kind, modifier = struct.unpack('<iif', exe.read(table + ENTRY * k, ENTRY))
                entries.append({'slot': slot, 'type': kind if slot == 0 else None,
                                'type_name': types.get(kind, f'type {kind}') if slot == 0 else SLOTS.get(slot, f'slot {slot}'),
                                'modifier': modifier})
            found.append({'class': class_id, 'previous': previous, 'entries': entries})
    return found


def specialty_gain(character_stat, piece_stat, modifier, yearning=0):
    """What one stat gains from one specialised piece (0x4f8025 - 0x4f8044). yearning: the value of effect 449."""
    if piece_stat <= 0:
        return 0
    return max(0, int((character_stat + piece_stat) * (modifier + 0.01 * yearning)))


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    names = class_data.class_names()
    for row in class_modifiers():
        route = '' if row['previous'] is None else f" (from {names.get(row['previous'], row['previous'])})"
        print(f"{names.get(row['class'], row['class'])}{route}: "
              + ', '.join(f"{e['type_name']} {e['modifier']:+.2f}" for e in row['entries']))


if __name__ == '__main__':
    main()

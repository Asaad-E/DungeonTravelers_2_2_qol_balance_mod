"""
The events of a stretch of the executable that matter to read a rule, in order.

    python tools/exe_digest.py 0xSTART 0xEND

Keeps: effect lookups (the id and its name), counts of pieces with an enchantment, stat reads, rolls, float
constants used in arithmetic or comparisons, small integer comparisons, debug messages, and calls into the
functions docs/FORMULAS.md names. Everything else is dropped, so the output is a reading aid, not the code.
"""
import os
import re
import sys

import capstone
import openpyxl
from exe_reader import Exe

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
FINDERS = {0x47e340: 'effect', 0x47e290: 'effect?', 0x47e390: 'effect on', 0x48cbf0: 'effect index', 0x48c680: 'has effect',
           0x557620: 'attack has effect', 0x56ce70: 'skill has effect', 0x47b220: 'CREATE command'}
KNOWN = {0x490790: 'ROLL below', 0x505ac0: 'ROLL below (ecx)', 0x505ad0: 'weighted roll', 0x44fbb0: 'zone factor', 0x48c5c0: 'heal cap',
         0x48d730: 'heal amount', 0x43f450: 'pick targets', 0x414560: None, 0x507310: None, 0x61edf4: None,
         # plumbing: result records, lists, allocation, float to int, error exit
         0x419640: None, 0x429320: None, 0x428fd0: None, 0x419990: None, 0x48b580: None, 0x61e650: None, 0x418c80: None,
         0x603045: None, 0x603075: None, 0x5b0480: None, 0x418f60: None, 0x419900: None, 0x419920: None, 0x419940: None,
         0x428740: None, 0x4286f0: None, 0x428640: None, 0x5728c0: None, 0x428560: None, 0x418bc0: None, 0x418c00: None,
         0x5c24c0: None, 0x5c2660: None, 0x5c28d0: None, 0x606150: None, 0x604bc0: None}
ARITH = ('mulss', 'addss', 'subss', 'divss', 'comiss', 'ucomiss', 'maxss', 'minss', 'fmul', 'fadd', 'fsub', 'fdiv', 'fcom', 'fcomp', 'movss')
STATS = ('ATK', 'DEF', 'INT', 'RES', 'DEX', 'AGI', 'slash', 'stab', 'bash', 'fire', 'water', 'wind', 'earth', 'lightning')
SLOTS = {0x10: 'level', 0x24: 'HP', 0x28: 'max HP', 0x2c: 'value', 0x34: 'stat', 0x38: 'dead?', 0x48: 'status', 0xf0: 'pieces with enchantment',
         0x50: 'magic attack', 0x60: 'critical', 0x6c: 'physical attack'}


def names(sheet, key, value, book='vanilla_source_of_truth.xlsx'):
    ws = openpyxl.load_workbook(os.path.join(TABLES_DIR, book), read_only=True)[sheet]
    rows = list(ws.iter_rows(values_only=True))
    k, v = rows[0].index(key), rows[0].index(value)
    return {r[k]: r[v] for r in rows[1:] if r[k] is not None}


def digest(exe, start, end):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    effects = names('Effects', 'Effect_ID', 'Game_Name')
    better = names('Effects', 'Effect_ID', 'Name')
    enchants = names('Enchants', 'Enchant_ID', 'Name')
    effect = lambda n: f"{n} ({better.get(n) or effects.get(n) or '?'})"
    out, edx, pushed = [], None, []
    for i in md.disasm(exe.read(start, end - start), start):
        at = f'{i.address:08x}'
        if i.mnemonic == 'mov' and re.fullmatch(r'edx, (0x[0-9a-f]+|\d+)', i.op_str):
            edx = int(i.op_str.split(', ')[1], 0)
        if i.mnemonic == 'push':
            pushed = (pushed + [int(i.op_str, 0) if re.fullmatch(r'(0x[0-9a-f]+|\d+)', i.op_str) else None])[-3:]
            if re.fullmatch(r'0x6[0-9a-f]{5}', i.op_str):
                text = exe.cstring(int(i.op_str, 16), 90)
                if text and len(text) > 3 and not text.isascii() and '�' not in text and sum(c.isalnum() or '぀' <= c <= '鿿' for c in text) >= 3:
                    out.append(f'{at}  MESSAGE {text.strip()}')
        elif i.mnemonic == 'call':
            last = next((p for p in reversed(pushed) if p is not None), None)
            if re.fullmatch(r'0x[0-9a-f]+', i.op_str):
                target = int(i.op_str, 16)
                if target in FINDERS and edx is not None:
                    out.append(f'{at}  {FINDERS[target]} {effect(edx)}')
                elif target in KNOWN:
                    if KNOWN[target]:
                        out.append(f'{at}  {KNOWN[target]}' + (f' {last}' if 'ROLL below' == KNOWN[target] and last is not None else ''))
                else:
                    out.append(f'{at}  call {target:#x}')
            else:
                m = re.fullmatch(r'dword ptr \[e.. \+ (0x[0-9a-f]+)\]', i.op_str)
                slot = int(m.group(1), 16) if m else None
                if slot == 0xf0 and last is not None:
                    out.append(f"{at}  pieces with enchantment {last} ({enchants.get(last, '?')})")
                elif slot == 0x34 and last is not None and last < len(STATS):
                    out.append(f'{at}  stat {STATS[last]}')
                elif slot == 0x48 and len(pushed) >= 2 and pushed[-2] is not None:
                    out.append(f'{at}  status {effect(pushed[-2])}')
                elif slot in SLOTS:
                    out.append(f'{at}  {SLOTS[slot]}')
            pushed = []
        elif i.mnemonic in ARITH:
            m = re.search(r'dword ptr \[(0x6[0-9a-f]{5})\]', i.op_str)
            if m:
                out.append(f'{at}  {i.mnemonic} {exe.f32(int(m.group(1), 16)):g}')
        elif i.mnemonic == 'cmp' and re.fullmatch(r'e.., (0x[0-9a-f]+|\d+)', i.op_str):
            value = int(i.op_str.split(', ')[1], 0)
            if 1 < value < 1000:
                out.append(f'{at}  cmp {value}')
        elif i.mnemonic == 'mov' and re.fullmatch(r'dword ptr \[.*\], 0x[34][0-9a-f]{7}', i.op_str):
            import struct
            out.append(f"{at}  set {struct.unpack('<f', struct.pack('<I', int(i.op_str.split(', ')[1], 16)))[0]:g}")
    return out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print('\n'.join(digest(Exe(), int(sys.argv[1], 16), int(sys.argv[2], 16))))

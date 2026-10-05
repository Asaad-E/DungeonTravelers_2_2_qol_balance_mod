"""
Size of every equipment enchantment, read from the executable.

    python mod_project/tools/exe_enchants.py

The battle code reads an enchantment as "number of equipped pieces that carry it" (a call through slot 0xf0 of
the unit, with the enchantment id pushed) and then scales that number, most often by a float constant. This tool
lists every such read with the scaling that follows it and writes docs/generated/ENCHANT_SIZES.md, next to the
figure the QoL variant shows for the same enchantment (sheet EnchantValues of qol_rules.xlsx).

What it recognises after the call:  a test for zero ("any piece": the enchantment is a switch), mulss by a constant, "addss xmm, xmm" (doubling), "lea r, [r + r*4]" (five
times), "add eax, eax" (twice), "shl". A read whose scaling it does not recognise is listed with "?" and must be
read by hand; the limits (minss, maxss) that follow within the window are listed as they appear.
"""
import collections
import os
import re
import struct
import sys

import capstone
import openpyxl
from exe_reader import Exe

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, 'docs', 'generated', 'ENCHANT_SIZES.md')
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
COUNT_SLOT = 0xf0
WINDOW = 16                    # instructions looked at after the call
LOOK_BACK = 20                 # and before it, for the id
MAX_ENCHANT = 400
ANY_PIECE = 'any piece'          # the code only asks whether a piece carries it


def reads(exe):
    """Every (function, address, enchantment id, scale text, limits) in the code."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    text_va, size = exe.text[1], exe.text[4]
    code = exe.read(text_va, size)
    functions = collections.OrderedDict()
    for m in re.finditer(rb'\xff[\x90-\x97]' + struct.pack('<I', COUNT_SLOT), code):
        try:
            start = exe.function_start(text_va + m.start())
        except Exception:
            start = None
        if start:
            functions.setdefault(start, []).append(text_va + m.start())
    found = []
    for start, calls in functions.items():
        ins = list(md.disasm(exe.read(start, max(calls) - start + 0x80), start))
        index = {i.address: k for k, i in enumerate(ins)}
        for call in calls:
            k = index.get(call)
            if k is None:
                continue
            enchant = None
            for back in ins[max(0, k - LOOK_BACK):k][::-1]:       # the id is the last constant pushed since the call before
                if back.mnemonic == 'call':
                    break
                if back.mnemonic == 'push' and re.fullmatch(r'(0x[0-9a-f]+|\d+)', back.op_str):
                    enchant = int(back.op_str, 0)
                    break
            if enchant is None or not 0 < enchant < MAX_ENCHANT:
                continue
            scale, limits = [], []
            for nxt in ins[k + 1:k + 1 + WINDOW]:
                text = f'{nxt.mnemonic} {nxt.op_str}'
                if nxt.mnemonic == 'call':
                    break
                constant = re.search(r'dword ptr \[(0x6[0-9a-f]{5})\]', nxt.op_str)
                if text == 'test eax, eax' and not scale:
                    scale.append(ANY_PIECE)
                    break
                if nxt.mnemonic == 'mulss' and constant:
                    scale.append(f'{exe.f32(int(constant.group(1), 16)):g}')
                    break
                if nxt.mnemonic in ('minss', 'maxss') and constant:
                    limits.append(f"{'at most' if nxt.mnemonic == 'minss' else 'at least'} {exe.f32(int(constant.group(1), 16)):g}")
                if re.fullmatch(r'lea e.., \[(e..) \+ \1\*4\]', text):
                    scale.append('5')
                elif re.fullmatch(r'lea e.., \[(e..) \+ \1\*2\]', text):
                    scale.append('3')
                elif re.fullmatch(r'add (e..), \1', text):
                    scale.append('2')
                elif re.fullmatch(r'addss (xmm\d), \1', text):
                    scale.append('2')
                elif nxt.mnemonic == 'shl' and re.fullmatch(r'e.., \d+', nxt.op_str):
                    scale.append(str(2 ** int(nxt.op_str.split(', ')[1])))
            for nxt in ins[k + 1:k + 1 + 3 * WINDOW]:
                constant = re.search(r'dword ptr \[(0x6[0-9a-f]{5})\]', nxt.op_str)
                if nxt.mnemonic in ('minss', 'maxss') and constant:
                    limit = f"{'at most' if nxt.mnemonic == 'minss' else 'at least'} {exe.f32(int(constant.group(1), 16)):g}"
                    if limit not in limits:
                        limits.append(limit)
            found.append((start, call, enchant, ' x '.join(scale) if scale else '?', limits))
    return found


def workbook_rows(name, sheet):
    ws = openpyxl.load_workbook(os.path.join(TABLES_DIR, name), read_only=True)[sheet]
    rows = ws.iter_rows(values_only=True)
    header = next(rows)
    return [dict(zip(header, r)) for r in rows]


def product(scale):
    if scale in ('?', ANY_PIECE):
        return None
    value = 1.0
    for part in scale.split(' x '):
        value *= float(part)
    return value


def main():
    exe = Exe()
    found = reads(exe)
    names = {r['Enchant_ID']: r['Vanilla_Name'] for r in workbook_rows('qol_enchant_text.xlsx', 'Enchants')}
    shown = collections.defaultdict(list)
    for r in workbook_rows('qol_rules.xlsx', 'EnchantValues'):
        key = next((k for k in r if k and 'ID' in str(k).upper()), None)
        if key and r[key] is not None:
            shown[r[key]].append(r)
    by_enchant = collections.defaultdict(list)
    for start, call, enchant, scale, limits in found:
        by_enchant[enchant].append((start, call, scale, limits))
    lines = ['# Enchantment sizes read from the executable (generated)', '',
             'Generated by `tools/exe_enchants.py`. Do not edit: run the tool again.', '',
             f'{len(found)} reads of {len(by_enchant)} enchantments. "Per piece" is the scaling the code applies to the number of '
             'equipped pieces right after counting them; "?" means the scaling is not one the tool recognises. The unit '
             'depends on the formula that uses it (`docs/FORMULAS.md`): a figure may be percent points, a fraction or a flat amount.', '',
             '| Id | Enchantment | Per piece | Limits seen after it | Read at | Shown by QoL |', '|---|---|---|---|---|---|']
    for enchant in sorted(by_enchant):
        entries = by_enchant[enchant]
        scales = sorted({s for _, _, s, _ in entries})
        limits = sorted({l for _, _, _, ls in entries for l in ls})
        where = ', '.join(sorted({f'`{call:#x}`' for _, call, _, _ in entries})[:4]) + (' ...' if len(entries) > 4 else '')
        qol = '; '.join(sorted({str(v) for r in shown.get(enchant, []) for k, v in r.items()
                                if v is not None and k and 'ID' not in str(k).upper() and 'NAME' not in str(k).upper()}))[:80]
        lines.append(f"| {enchant} | {names.get(enchant, '')} | {' / '.join(scales)} | {', '.join(limits)} | {where} | {qol} |")
    never = sorted(set(names) - set(by_enchant))
    lines += ['', f'Enchantments with no such read ({len(never)}): they act through another path (a stat bonus added when the '
              'piece is equipped, an effect, a flag) or are not used. Ids: ' + ', '.join(str(i) for i in never) + '.', '']
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(f'Wrote {OUTPUT_PATH}: {len(found)} reads, {len(by_enchant)} enchantments, '
          f"{sum(1 for e in by_enchant.values() if all(s == '?' for _, _, s, _ in e))} without a recognised scaling")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()

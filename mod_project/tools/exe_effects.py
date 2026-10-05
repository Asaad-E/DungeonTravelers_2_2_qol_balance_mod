"""
Where the program handles every skill effect: the list that says what is still to read before the simulator.

    python mod_project/tools/exe_effects.py

For each effect id that a skill or an enemy attack uses (sheet Effects of vanilla_source_of_truth.xlsx) the tool
looks in the executable for:
    * the class Command::CreateCommand (0x47b220) builds for it: an effect with a class acts by itself
      (an ailment, a heal, a summon) and its methods hold its rule
    * every place that asks "is effect N in this action / on this unit": mov edx, N + a call to one of the lookup functions (FINDERS), and
      push N + push 0 + call [vtable + 0x48]. The function that asks is the formula the effect enters
Writes docs/generated/EFFECT_COVERAGE.md and the sheet EffectCoverage of data_tables/balance_criteria.xlsx.

The state of an effect:
    read      every place that handles it lies in a function docs/FORMULAS.md covers (table READ below), or its
              rule is written in the sheet EffectRules as read
    partly read  its rule in EffectRules says how far it was followed
    located   the program handles it, in code not read yet: the addresses say where
    not found no handler found by these three searches: it is handled some other way, or by nothing
An effect read by hand in a place the searches cannot see (an id compared in a register, a lookup far from
its id) has its rule in the sheet EffectRules of balance_criteria.xlsx, which also counts as read.
"""
import collections
import os
import re
import struct
import sys

import capstone
import openpyxl
import exe_digest
from exe_reader import Exe

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
OUTPUT_PATH = os.path.join(BASE_DIR, 'docs', 'generated', 'EFFECT_COVERAGE.md')
CREATE_COMMAND, FIND_EFFECT, STATUS_SLOT = 0x47b220, 0x47e340, 0x48
CASE_TABLE, JUMP_TABLE, FIRST_ID, LAST_ID = 0x47e0a4, 0x47de14, 9, 9 + 0x1b8
# functions that take an effect id in edx: find it among the effects of an action or of a unit (0x47e340 and its
# siblings), ask whether an enemy attack carries it (0x557620), or build its command at once (0x47b220)
FINDERS = {0x47e340, 0x47e290, 0x47e390, 0x48cbf0, 0x48c680, 0x557620, 0x56ce70, 0x47b220}
# functions (first address, last address, section of docs/FORMULAS.md) whose handling of an effect is read
READ = ((0x44a850, 0x44d36f, '2 physical attack'), (0x44d370, 0x44f18f, '3 magic attack'), (0x44f190, 0x44f5c7, '4 critical hits'),
        (0x4499d0, 0x44a62f, '5 order of turns'), (0x44a630, 0x44a79f, '9.1 targets'), (0x481ea0, 0x483a5f, '5b ailments'),
        (0x423a30, 0x423ca8, '5c turn delay'), (0x48d730, 0x48d930, '6b healing'), (0x48c5c0, 0x48c680, '6b heal cap'),
        (0x4817c0, 0x481a1f, '6b, 6d recovery'), (0x483a60, 0x483ee0, '6d recovery'), (0x450710, 0x45082f, '6c EXP'),
        (0x445830, 0x445aa5, '6c EXP'), (0x484150, 0x485d5b, '11.1 dolls'), (0x4fdfd0, 0x4fe11b, '11.1 dolls'),
        (0x431aa0, 0x434760, '9 enemy AI'))
PLAIN_APPLY = 0x480090         # the apply method most effects share: it records "applied" and rolls nothing


def section_of(address):
    for low, high, name in READ:
        if low <= address <= high:
            return name
    return None


def command_classes(exe, md):
    """{effect id: vtable of the class CreateCommand builds for it}. CreateCommand switches on id - 9 through a byte
    table (0x47e0a4) and a jump table (0x47de14); each case builds one class and jumps to the common end."""
    table = {}
    default = exe.u32(JUMP_TABLE + 4 * exe.read(CASE_TABLE + LAST_ID - FIRST_ID, 1)[0])
    for eid in range(FIRST_ID, LAST_ID + 1):
        target = exe.u32(JUMP_TABLE + 4 * exe.read(CASE_TABLE + eid - FIRST_ID, 1)[0])
        vtable = None
        for k, i in enumerate(md.disasm(exe.read(target, 0x140), target)):
            if i.mnemonic == 'mov':
                m = re.fullmatch(r'dword ptr \[e..\], (0x6[0-9a-f]{5})', i.op_str)
                if m:
                    vtable = int(m.group(1), 16)                           # the last store wins: the class itself, after its bases
            if i.mnemonic in ('jmp', 'ret') or k > 70:              # a case ends in a return or a jump to the common end
                break
        if vtable:
            table[eid] = vtable
    return table


_PLAIN = {}


def is_plain(exe, md, method):
    """True when an apply method has no rule of its own: up to its first return it rolls nothing, reads no stat,
    HP or enchantment and uses no constant; it only records the effect on the target (and builds its message)."""
    if method not in _PLAIN:
        end = method + 0x400
        for i in md.disasm(exe.read(method, 0x400), method):
            if i.mnemonic == 'ret':
                end = i.address
                break
        events = [ev[10:] for ev in exe_digest.digest(exe, method, end)]
        quiet = lambda ev: ev.startswith('call ') or ev in ('cmp 16', 'cmp 31', 'cmp 15', 'value', 'dead?', 'level')
        _PLAIN[method] = method == PLAIN_APPLY or all(quiet(ev) for ev in events)
    return _PLAIN[method]


def askers(exe, md, ids):
    """{effect id: set of addresses that ask for it}."""
    text_va, size = exe.text[1], exe.text[4]
    code = exe.read(text_va, size)
    found = collections.defaultdict(set)
    for m in re.finditer(rb'\xba(....)', code, re.S):                      # mov edx, imm32 ... call FIND_EFFECT
        eid = struct.unpack('<I', m.group(1))[0]
        if eid not in ids:
            continue
        for k, i in enumerate(md.disasm(code[m.start():m.start() + 80], text_va + m.start())):
            if k > 14 or (k > 0 and i.mnemonic == 'mov' and i.op_str.startswith('edx,')):
                break
            if i.mnemonic == 'call':                                       # the first call after it decides
                if re.fullmatch(r'0x[0-9a-f]+', i.op_str) and int(i.op_str, 16) in FINDERS:
                    found[eid].add(text_va + m.start())
                break
    for m in re.finditer(rb'(?:\x6a(.)|\x68(....))', code, re.S):          # push id ... call [reg + 0x48 or 0x50]: a status of a unit
        eid = m.group(1)[0] if m.group(1) else struct.unpack('<I', m.group(2))[0]
        if eid not in ids or eid < 2:
            continue
        for k, i in enumerate(md.disasm(code[m.start():m.start() + 60], text_va + m.start())):
            if k > 10:
                break
            if i.mnemonic == 'call':                                       # the first call after it decides
                if re.fullmatch(r'dword ptr \[e.. \+ 0x(48|50)\]', i.op_str):
                    found[eid].add(text_va + m.start())
                break
    # a walk over the effects of an action: call [effect + 0x24] returns its id, compared with a constant
    for m in re.finditer(rb'\xff[\x50-\x57]\x24(?:\x83\xf8(.)|\x3d(....))', code, re.S):
        eid = m.group(1)[0] if m.group(1) else struct.unpack('<I', m.group(2))[0]
        if eid in ids and eid >= 2:
            found[eid].add(text_va + m.start())
    return found


def main():
    exe = Exe()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    wb = openpyxl.load_workbook(os.path.join(TABLES_DIR, 'vanilla_source_of_truth.xlsx'), read_only=True)
    rows = list(wb['Effects'].iter_rows(values_only=True))
    header = rows[0]
    effects = [dict(zip(header, r)) for r in rows[1:]]
    ids = {e['Effect_ID'] for e in effects}
    classes = command_classes(exe, md)
    rules = [r for r in openpyxl.load_workbook(os.path.join(TABLES_DIR, 'balance_criteria.xlsx'), read_only=True)['EffectRules'].iter_rows(min_row=2, values_only=True) if r and r[0] is not None]
    notes = {r[0]: r[1] for r in rules}
    partly = {r[0] for r in rules if len(r) > 4 and r[4] == 'partly'}
    asked = askers(exe, md, ids)
    slot6 = {}
    out = []
    for e in effects:
        eid = e['Effect_ID']
        places = sorted(asked.get(eid, ()))
        sections = sorted({section_of(a) for a in places if section_of(a)})
        unread = [a for a in places if not section_of(a)]
        vtable = classes.get(eid)
        apply_method = exe.u32(vtable + 24) if vtable else None
        own_section = section_of(apply_method) if apply_method else None
        plain = bool(apply_method) and not own_section and is_plain(exe, md, apply_method)
        class_read = bool(apply_method and (plain or own_section))
        if eid in notes:                                    # its rule is written in the sheet EffectRules
            sections = sorted(set(sections) | {notes[eid]})
            unread, class_read = [], True
            places = places or [0]
        if own_section:
            sections = sorted(set(sections) | {own_section})
        if (places or own_section) and not unread and (not vtable or class_read):   # a class that only records the effect needs a reader
            state = 'read'
        elif places or (vtable and not plain):
            state = 'located'
        else:
            state = 'not found'
        if eid in partly:
            state = 'partly read'
        out.append({'id': eid, 'name': e['Name'] or e['Game_Name'], 'named': e['Status'], 'uses': (e['Skill_Uses'] or 0, e['EnemyAttack_Uses'] or 0),
                    'state': state, 'sections': sections, 'class': None if plain else apply_method, 'unread': unread, 'used_by': e['Used_By'] or ''})
    counts = collections.Counter(o['state'] for o in out)
    lines = ['# Skill effects and the code that handles them (generated)', '',
             'Generated by `tools/exe_effects.py`. Do not edit: run the tool again.', '',
             f"{len(out)} effects are used by a skill or an enemy attack: **{counts['read']} read**, {counts['partly read']} partly read "
             f"(the place and the roll are known, the consequence is not followed), {counts['located']} located in code not read "
             f"yet, {counts['not found']} with no handler found by the searches of the tool.", '',
             '"Read" means every place that handles the effect lies in a function `docs/FORMULAS.md` covers; it does not mean the '
             'figure of that one effect was checked by hand.', '',
             '| Id | Effect | Skills | Enemy attacks | State | In the formula of | Its own command | Other places that ask for it | Used by |',
             '|---|---|---|---|---|---|---|---|---|']
    order = {'located': 0, 'not found': 1, 'partly read': 2, 'read': 3}
    for o in sorted(out, key=lambda o: (order[o['state']], -(o['uses'][0] + o['uses'][1]), o['id'])):
        other = ', '.join(f'`{a:#x}`' for a in o['unread'][:5]) + (' ...' if len(o['unread']) > 5 else '')
        lines.append(f"| {o['id']} | {o['name']} | {o['uses'][0]} | {o['uses'][1]} | {o['state']} | {', '.join(o['sections'])} | "
                     f"{'`%#x`' % o['class'] if o['class'] else ''} | {other} | {str(o['used_by'])[:70]} |")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    path = os.path.join(TABLES_DIR, 'balance_criteria.xlsx')
    book = openpyxl.load_workbook(path)
    if 'EffectCoverage' in book.sheetnames:
        del book['EffectCoverage']
    ws = book.create_sheet('EffectCoverage')
    ws.append(['Effect_ID', 'Effect', 'Skill_Uses', 'EnemyAttack_Uses', 'State', 'In_Formula', 'Own_Command', 'Other_Places'])
    for o in sorted(out, key=lambda o: o['id']):
        ws.append([o['id'], o['name'], o['uses'][0], o['uses'][1], o['state'], ', '.join(o['sections']),
                   f"{o['class']:#x}" if o['class'] else None, ', '.join(f'{a:#x}' for a in o['unread'])])
    book.save(path)
    print(f"Wrote {OUTPUT_PATH}: {dict(counts)}; command classes found: {len(classes)}")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()

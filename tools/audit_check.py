"""
The check of the result file of the engine audit (docs/ENGINE_AUDIT.md): what an auditor wrote is held against the
program and the engine, so that a quoted line that does not exist, a missing field or a missing item is caught.

    python tools/audit_check.py            every item; exit 1 when anything fails
    python tools/audit_check.py P5.2       one item

For every item (a section '### <ID> <title>' of docs/result_engine_audit.md):
  * the fields its verdict needs are present, the verdict and the severity are words of the rules;
  * every quoted line of the program ('0043f6c8  comiss   xmm0, xmm1', as tools/exe_dis.py prints it) is
    disassembled again at its address and must be the same instruction (the note after ';' is ignored);
  * every quoted line of the engine, in a code block after a reference 'engine_cs/....cs:<line>', must be a line of
    that file (spaces at the ends ignored; a line '...' is a gap);
  * the item quotes at least as many verified lines as its verdict needs, and names the command it ran;
  * words of guessing are reported.
At the end: the IDs of the plan's tables that have no item, the IDs written twice, the items not in the plan without
the marker that says why they were added. The rules (fields, counts, words) are in data_tables/audit_rules.json.
Reads the program; plays no battle.
"""
import json
import os
import re
import sys

import capstone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exe_reader import Exe          # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = json.load(open(os.path.join(ROOT, 'data_tables', 'audit_rules.json'), encoding='utf-8'))
PROGRAM_LINE = re.compile(r'^\s*([0-9a-f]{8})\s{2,}(\S.*?)\s*$')
ENGINE_REF = re.compile(r'(engine_cs/[\w/.\-]+\.cs):(\d+)')
ITEM = re.compile(r'^### (P\d+\.\d+)\b(.*)$')
PLAN_ID = re.compile(r'^\| (P\d+\.\d+) \|')

exe = Exe()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)


def norm(text):
    return re.sub(r'\s+', ' ', text.split(';')[0]).strip()


def instruction_at(address):
    for ins in md.disasm(exe.read(address, 16), address):
        return norm(exe.annotate(ins)[10:]) if ins.address == address else None
    return None


def blocks(text):
    """The code blocks of an item: (the text before the block, its lines)."""
    out, at = [], 0
    for m in re.finditer(r'```[^\n]*\n(.*?)```', text, re.S):
        out.append((text[at:m.start()], m.group(1).splitlines()))
        at = m.end()
    return out


def field(text, name):
    m = re.search(re.escape(name) + r'\s*(.*)', text)
    return m.group(1).strip() if m else None


def check_item(item_id, text, files):
    errors, warnings = [], []
    verdict_text = field(text, '**Verdict.**')
    verdict = next((v for v in RULES['verdicts'] if verdict_text and verdict_text.split()[0].rstrip('.') == v), None) \
        if verdict_text else None
    if verdict is None:
        errors.append(f'no verdict, or not one of {RULES["verdicts"]}: {verdict_text!r}')
        verdict = 'UNREAD'
    phase = item_id.split('.')[0]
    baseline = phase in RULES['baseline_phases']
    no_program = baseline or phase in RULES['no_program_phases']
    every = RULES['baseline_fields'] if baseline else RULES['no_program_fields'] if no_program else RULES['fields']['every']
    for name in every + ([] if baseline else RULES['fields'].get(verdict, [])):
        if name not in text:
            errors.append(f'missing field {name}')
    if verdict in ('MISMATCH', 'PARTIAL'):
        sev = field(text, '**Severity**') or ''
        if not any(re.search(r'\b' + re.escape(s) + r'\b', sev) for s in RULES['severities']):
            errors.append(f'severity not one of {RULES["severities"]}: {sev!r}')
    program_ok, engine_ok = 0, 0
    for before, lines in blocks(text):
        ref = ENGINE_REF.findall(before)
        if ref:
            path, line_no = ref[-1]
            full = os.path.join(ROOT, path)
            if path not in files:
                files[path] = [ln.strip() for ln in open(full, encoding='utf-8').read().splitlines()] \
                    if os.path.exists(full) else None
            source = files[path]
            if source is None:
                errors.append(f'{path}: no such file')
                continue
            if int(line_no) > len(source):
                errors.append(f'{path}:{line_no}: the file has {len(source)} lines')
            for ln in lines:
                s = ln.strip()
                if not s or s == '...':
                    continue
                if s in source:
                    engine_ok += 1
                else:
                    errors.append(f'{path}: quoted line not in the file: {s[:100]!r}')
            continue
        for ln in lines:
            m = PROGRAM_LINE.match(ln)
            if not m:
                continue
            address, quoted = int(m.group(1), 16), norm(m.group(2))
            real = instruction_at(address)
            if real is None:
                errors.append(f'{m.group(1)}: no instruction starts at this address')
            elif real != quoted:
                errors.append(f'{m.group(1)}: quoted {quoted!r}, the program holds {real!r}')
            else:
                program_ok += 1
    if not no_program and program_ok < RULES['least_program_lines'][verdict]:
        errors.append(f'{program_ok} verified program lines; {verdict} needs {RULES["least_program_lines"][verdict]}')
    if not baseline and engine_ok < RULES['least_engine_lines'][verdict]:
        errors.append(f'{engine_ok} verified engine lines; {verdict} needs {RULES["least_engine_lines"][verdict]}')
    if not no_program and verdict in RULES['need_command'] and 'tools/exe_' not in text:
        errors.append('no command of a tools/exe_* reader is named')
    # every case listed under Cases. is answered ("Case <n>") in the Program and the Engine sections
    if verdict in RULES['answer_every_case'] and not no_program:
        cases_at = text.find('**Cases.**')
        after = text[cases_at:] if cases_at >= 0 else ''
        listed = re.findall(r'^\s*(\d+)\.\s', after.split('**Program.**')[0], re.M)
        marks = [text.find(name) for name in RULES['case_sections']] + [len(text)]
        for k, name in enumerate(RULES['case_sections']):
            start = marks[k]
            ends = [m for m in marks[k + 1:] + [text.find('**Verdict.**')] if m > start]
            part = text[start:min(ends)] if start >= 0 and ends else ''
            unanswered = [n for n in listed if not re.search(r'\bCases?\s+(?:\d+\s*(?:,|and|-)\s*)*' + n + r'\b', part)]
            if unanswered:
                errors.append(f'{name} answers no "Case {unanswered[0]}"' + (f' (nor {", ".join(unanswered[1:])})'
                                                                              if len(unanswered) > 1 else ''))
    low = text.lower()
    for word in RULES['guessing_words']:
        if word in low:
            warnings.append(f'word of guessing: {word!r}')
    return verdict, errors, warnings


def main(args):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    plan_ids = [m.group(1) for ln in open(os.path.join(ROOT, RULES['plan']), encoding='utf-8')
                for m in [PLAN_ID.match(ln)] if m]
    path = os.path.join(ROOT, RULES['result'])
    if not os.path.exists(path):
        print(f'no result file {RULES["result"]}')
        return 1
    text = open(path, encoding='utf-8').read()
    items, current, buf = [], None, []
    for ln in text.splitlines():
        m = ITEM.match(ln)
        if m:
            if current:
                items.append((current, '\n'.join(buf)))
            current, buf = m.group(1), [ln]
        elif current:
            if ln.startswith('## '):
                items.append((current, '\n'.join(buf)))
                current, buf = None, []
            else:
                buf.append(ln)
    if current:
        items.append((current, '\n'.join(buf)))
    only = set(args)
    files, failed, counts = {}, 0, {}
    for item_id, body in items:
        if only and item_id not in only:
            continue
        verdict, errors, warnings = check_item(item_id, body, files)
        counts[verdict] = counts.get(verdict, 0) + 1
        if item_id not in plan_ids and RULES['added_item_marker'] not in body:
            errors.append(f'not in the plan and no line "{RULES["added_item_marker"]} ..."')
        mark = 'FAIL' if errors else 'ok  '
        failed += bool(errors)
        print(f'{mark} {item_id} {verdict}')
        for e in errors:
            print('       error:', e)
        for w in warnings:
            print('       warning:', w)
    if not only:
        written = [i for i, _ in items]
        missing = [i for i in plan_ids if i not in written]
        twice = sorted({i for i in written if written.count(i) > 1})
        print(f'\nitems written {len(written)}, failing {failed}; verdicts {counts}')
        print(f'plan items {len(plan_ids)}, not written {len(missing)}' + (': ' + ' '.join(missing) if missing else ''))
        if twice:
            print('written more than once:', ' '.join(twice))
            failed += 1
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

"""The texts of the repository say what was decided, not who decided it: the mentions of the person the work was done
for leave the documents, the comments and the cells of the workbooks. "The user" of a skill, in the sense of the game
(the unit that uses it), stays.

    python neutral_tone.py count      what would be left, by file
    python neutral_tone.py apply      rewrites the tracked text files (not this folder) and the workbooks
"""
import glob
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NL = chr(10)
DATE = r'\d{4}-\d{2}-\d{2}'
VERBS = ('decided|asked|set|confirmed|accepted|approved|chosen|dropped|parked|settled|answered|left|withdrawn|rejected|'
         'given|taken|kept|raised|requested|changed|lowered|made|named|closed|reported|seen|supplied|tested|played')
RULES = [
    (r'\bThe user, (the same (?:day|night|evening)|' + DATE + r')((?: \([^)]*\))?)(, [^:]{0,40})?:', r'Decided \1\2\3:'),
    (r'\(the user, (' + DATE + r'(?:[^)]{0,40})?)\)', r'(decided \1)'),
    (r'\(the user\)', ''),
    (r'\bthe user, (' + DATE + r')', r'decided \1'),
    (r'\bThe user, (' + DATE + r')', r'Decided \1'),
    (r'\b(' + VERBS + r') by the user\b', r'\1'),
    (r' by the user\b', ''),
    (r'\bat the user\'s (request|word)\b', r'on request'),
    (r'\b([Tt])he user\'s (decision|decisions|choice|choices|request|reasons|answers|answer|own list|list|goal|mandate|spec|specification|rule|rules|priorities|test|tests)\b',
     r'\1he \2'),
    (r'\bThe user: ', 'Decided: '),
    (r'\bthe user: ', 'decided: '),
    (r'\bthe user (' + DATE + r')', r'decided \1'),
    (r'\(the user; ', '('),
    (r'\bThe user asked to\b', 'It was asked to'),
    (r'\bthe user asked to\b', 'it was asked to'),
    (r'\bas the user asked\b', 'as asked'),
    (r'\bbecause the user decided so\b', 'by decision'),
    (r'\bthe date the user decided it\b', 'the date it was decided'),
    (r'\bor the user set it aside\b', 'or it was set aside'),
    (r'\bor that the user set aside; its reason written and agreed with him\b', 'or that was set aside; its reason written'),
    (r'\bthe user left it to judgement\b', 'left to judgement'),
    (r'\bThe user allows it; ', 'Allowed; '),
    (r'\ba choice the user took\b', 'a choice taken'),
    (r'\bthe user meets cancellations in play\b', 'cancellations are met in play'),
    (r'\bthe earlier proposal the user asked to keep, through the five steps he gave\b',
     'the earlier proposal kept on request, through the five steps given'),
    (r'\bThe user chose no on\b', 'Chosen: no, on'),
    (r'\bThe user chose this on\b', 'Chosen on'),
    (r'\bThe user chose to show the first game\'s figures too\b', 'The figures of the first game are shown too'),
    (r'\bRows the user marked as\b', 'Rows marked as'),
    (r'\(the user\'s standard\)', '(the standard of the project)'),
    (r'\bare the user\'s; the other bounds\b', 'were set by hand; the other bounds'),
    (r'\bthe user set the limit at\b', 'the limit was set at'),
    (r'\bthe Cupid ability the user saw without\b', 'the Cupid ability first seen without'),
    (r'Not installed\. When the user says so: ', 'Not installed. To install: '),
    (r'; the user: "horrible\.\.\. nunca hacer esto NUNCA"\.', '; it was rejected outright.'),
    (r'\bThe user accepted the QoL variant \("todo perfecto"\) with two last decisions:', 'The QoL variant was accepted with two last decisions:'),
    (r'\bthe user accepted the variant\b', 'the variant was accepted'),
    (r'\bFor the user:', 'To check in the game:'),
    (r': the user called that horrible\.', ': that was rejected as horrible.'),
    (r'\bThe user and engineering team have established that\b', 'It is established that'),
    (r'\bThe User\'s (Complaint|Directive)\b', r'\1'),
    (r'\bThe user explicitly rejected this format\.', 'This format was explicitly rejected.'),
    (r'\bmeasured by the user on\b', 'measured on'),
    (r'\bThe user asked for air on\b', 'Air was asked for on'),
    (r'\bis a choice to take with the user before\b', 'is a choice to take before'),
    (r'\bfor the user to decide\b', 'to be decided'),
    (r'\b[Tt]he user decides\b', 'the decision is taken on'),
    (r'\bwaiting for the user\b', 'waiting for a decision'),
    (r'\b[Ww]aits for the user\b', 'waits for a decision'),
    (r'\bwhen the user says so\b', 'on request'),
    (r'\bunless the user asks\b', 'unless asked'),
    (r'\bwhen the user asks\b', 'when asked'),
    (r'\bthe user asked for\b', 'it was asked for'),
    (r'\bThe user asked for\b', 'Asked for:'),
    (r'\bto the user\b', ''),
    (r'\bfor the user\b', ''),
    (r'\bwith the user\b', ''),
    (r'\bof the same author\b', ''),
    (r', written for an earlier project of the same author', ''),
    (r'  +', ' '),
]
GAME_SENSE = re.compile(r'(?i)(on|of|to|its|by) the user\b|the user (takes|has|is|gains|loses|keeps|acts|performs|rolls|casts|uses)|'
                        r"the user's (own|current|side|hp|tp|passives|statuses|stats|turn|action|maid|party|weapon|level)")
LEFT = re.compile(r"(?i)\bthe user\b|\buser's\b")


def fix(text):
    out = []
    for line in text.split(NL):
        if LEFT.search(line):
            new = line
            for pattern, repl in RULES[:-1]:
                new = re.sub(pattern, repl, new)
            if new != line:
                lead = len(new) - len(new.lstrip(' '))
                new = new[:lead] + re.sub('  +', ' ', new[lead:])
            line = new
        out.append(line)
    return NL.join(out)


def left(text):
    return [l for l in text.split(NL) if LEFT.search(l) and not GAME_SENSE.search(l)]


def files():
    listed = subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True).stdout.split(NL)
    here = 'scratch/audit_2026-10-11/neutral_tone.py'
    return [f for f in listed if f and f != here and f.endswith(('.py', '.md', '.txt', '.ps1', '.json'))]


def main():
    apply = sys.argv[1] == 'apply'
    total = 0
    for f in files():
        path = os.path.join(ROOT, f)
        text = io.open(path, encoding='utf-8', errors='replace').read()
        new = fix(text)
        rest = left(new)
        total += len(rest)
        if rest and not apply and not f.startswith('scratch/'):
            print(f'{len(rest):4d} {f}')
            for l in rest[:400] if len(sys.argv) > 2 and sys.argv[2] in f else []:
                print('       ' + l.strip()[:230])
        if apply and new != text:
            io.open(path, 'w', encoding='utf-8', newline=NL).write(new)
    import openpyxl
    for wbp in glob.glob(os.path.join(ROOT, 'data_tables', '*.xlsx')):
        wb = openpyxl.load_workbook(wbp)
        touched = rest_cells = 0
        for ws in wb:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str) and LEFT.search(c.value):
                        new = fix(c.value)
                        rest_cells += len(left(new))
                        if new != c.value:
                            touched += 1
                            if apply:
                                c.value = new
        if apply and touched:
            wb.save(wbp)
        if touched or rest_cells:
            print(f'{os.path.basename(wbp)}: {touched} cells rewritten, {rest_cells} lines left')
        total += rest_cells
    print('left in all:', total)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

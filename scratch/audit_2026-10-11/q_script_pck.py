"""Compare Lesson.pck / Teaching.pck installed in the game against the backups: which entries changed, line
lengths (original max vs new max), and the structure of an .adv.bin (does it hold offsets a longer string would break?)."""
import os
import re
import sys
import struct
sys.path.insert(0, r'C:\Users\user\Personal\Physics\DungeonTraveler2-2\mod_project\tools')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pck_handler import PckArchive

ROOT = r'C:\Users\user\Personal\Physics\DungeonTraveler2-2'
GAME = os.path.join(ROOT, 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Script')
BACK = os.path.join(ROOT, 'mod_project', 'backups')
mode = sys.argv[1] if len(sys.argv) > 1 else 'diff'


def strings(b, minimum=6):
    out = []
    for m in re.finditer(rb'[\x20-\x7e\n]{%d,}\x00' % minimum, b):
        out.append((m.start(), m.group()[:-1].decode('latin-1')))
    return out


for name in ('Lesson.pck', 'Teaching.pck'):
    old = PckArchive(os.path.join(BACK, name))
    new = PckArchive(os.path.join(GAME, name))
    od, nd = dict(old.files), dict(new.files)
    print(f'===== {name}: {len(od)} entries in backup, {len(nd)} installed; order same: {[f for f, _ in old.files] == [f for f, _ in new.files]}')
    omax, nmax = 0, 0
    owide, nwide = [], []
    olines, nlines = 0, 0
    for fn, b in old.files:
        for off, s in strings(b):
            for line in s.strip('"').split('\n'):
                olines += 1
                if len(line) > omax:
                    omax = len(line)
                owide.append(len(line))
    changed = [fn for fn, b in old.files if nd.get(fn) != b]
    print(f'   changed entries: {len(changed)}')
    owide.sort()
    print(f'   ORIGINAL line length: max {omax}; 99th pct {owide[int(len(owide) * 0.99)]}; lines over 62: {sum(1 for w in owide if w > 62)} of {len(owide)}')
    over = {}
    for fn in changed:
        ob, nb = od[fn], nd[fn]
        os_, ns_ = {s for _, s in strings(ob)}, [(o, s) for o, s in strings(nb)]
        for off, s in ns_:
            if s not in os_:
                lines = s.strip('"').split('\n')
                w = max(len(l) for l in lines)
                nmax = max(nmax, w)
                over[fn] = max(over.get(fn, 0), w)
                if mode == 'text':
                    print(f'   [{fn}] {len(lines)} lines, widest {w}')
                    for l in lines:
                        print(f'        |{l}|  ({len(l)})')
        if mode == 'diff':
            print(f'   {fn}: {len(ob)} -> {len(nb)} bytes ({len(nb) - len(ob):+d}); widest new line {over.get(fn)}')
    print(f'   NEW text widest line: {nmax}  (original widest anywhere in the file: {omax})')

if mode == 'struct':
    old = PckArchive(os.path.join(BACK, 'Teaching.pck'))
    new = PckArchive(os.path.join(GAME, 'Teaching.pck'))
    for arc, tag in ((old, 'backup'), (new, 'installed')):
        fn, b = arc.files[1]
        print(f'--- {tag} {fn} ({len(b)} bytes)')
        print('   head:', b[:64].hex(' '))
        words = struct.unpack_from('<16I', b, 0)
        print('   u32 :', words)
        for off, s in strings(b)[:6]:
            print(f'   string at {off:#x} len {len(s) + 1}: {s[:50]!r}')
        print('   tail:', b[-48:].hex(' '))

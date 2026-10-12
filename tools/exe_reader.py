"""
Reader of the game's executable, for recovering formulas (never for running it).

    python tools/exe_reader.py strings  REGEX        names and messages kept in the binary
    python tools/exe_reader.py xrefs    "TEXT"       code that refers to a string
    python tools/exe_reader.py func     0xADDRESS    disassembly of the function at or around an address
    python tools/exe_reader.py floats   0xADDRESS    float and double constants a function reads

The executable is DT22_en_unwrapped.exe: 32-bit x86, image base 0x400000. It keeps, in its assertion
messages, the qualified names of about 730 functions ("Battle::CBattleAI2::Task_s::_Check") and the names
of 248 source files. A function is found through the string it mentions.
Requires the capstone package.
"""
import os
import re
import sys
import struct
import functools

import mod_config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# the program file the formulas were read from while the mod was made
EXE_PATH = os.path.join(mod_config.game_dir(), 'DT22_en_unwrapped.exe')
# the copy tools/exe_patch.py keeps before it writes into the game file: once it exists, formulas are read from it
COPY_DIR = os.path.join(BASE_DIR, 'backups', 'exe')
VANILLA_PATH = os.path.join(COPY_DIR, 'DT22_en_unwrapped.vanilla.exe')


def reading_path():
    """The program file the formulas are read from, as the game shipped it whenever that can be had: the file
    config.json names; else the vanilla copy of the file above, or that file; else any vanilla copy the patch tool
    keeps; else the first .exe of the game folder. The file the shop delivers holds the same code and the same tables
    at the same addresses (its .data section is identical, its code differs in 48 bytes of its start-up)."""
    named = mod_config.formula_exe()
    if named:
        return named
    for path in (VANILLA_PATH, EXE_PATH):
        if os.path.exists(path):
            return path
    copies = sorted(n for n in os.listdir(COPY_DIR) if n.endswith('.vanilla.exe')) if os.path.isdir(COPY_DIR) else []
    if copies:
        return os.path.join(COPY_DIR, copies[0])
    folder = mod_config.game_dir()
    found = sorted(n for n in os.listdir(folder) if n.lower().endswith('.exe')) if os.path.isdir(folder) else []
    if not found:
        raise SystemExit(f'No program file of the game in {folder}: name the folder of the game in {mod_config.CONFIG_PATH}.')
    return os.path.join(folder, found[0])


class Exe:
    def __init__(self, path=None):
        with open(path or reading_path(), 'rb') as f:
            self.data = f.read()
        d = self.data
        pe = struct.unpack_from('<I', d, 0x3C)[0]
        if d[pe:pe + 4] != b'PE\x00\x00' or struct.unpack_from('<H', d, pe + 24)[0] != 0x10B:
            raise ValueError('not the 32-bit executable this reader was written for')
        count = struct.unpack_from('<H', d, pe + 6)[0]
        opt_size = struct.unpack_from('<H', d, pe + 20)[0]
        self.base = struct.unpack_from('<I', d, pe + 24 + 28)[0]
        self.sections = []
        sec = pe + 24 + opt_size
        for _ in range(count):
            name = d[sec:sec + 8].rstrip(b'\x00').decode('latin-1')
            vsize, vaddr, rsize, raddr = struct.unpack_from('<IIII', d, sec + 8)
            self.sections.append((name, self.base + vaddr, vsize, raddr, rsize))
            sec += 40
        self.text = next(s for s in self.sections if s[0] == '.text')

    def offset(self, va):
        for _, start, vsize, raw, rsize in self.sections:
            if start <= va < start + rsize:
                return raw + (va - start)
        return None

    def va(self, offset):
        for _, start, vsize, raw, rsize in self.sections:
            if raw <= offset < raw + rsize:
                return start + (offset - raw)
        return None

    def read(self, va, size):
        off = self.offset(va)
        return self.data[off:off + size] if off is not None else b''

    def cstring(self, va, limit=200):
        raw = self.read(va, limit)
        return raw.split(b'\x00')[0].decode('utf-8', 'replace')

    def f32(self, va):
        raw = self.read(va, 4)
        return struct.unpack('<f', raw)[0] if len(raw) == 4 else None

    def f64(self, va):
        raw = self.read(va, 8)
        return struct.unpack('<d', raw)[0] if len(raw) == 8 else None

    def u32(self, va):
        raw = self.read(va, 4)
        return struct.unpack('<I', raw)[0] if len(raw) == 4 else None

    # -- strings and references ------------------------------------------------------------
    @functools.lru_cache(maxsize=None)
    def strings(self):
        """(va, text) of every printable string of 5 characters or more outside the code."""
        found = []
        for m in re.finditer(rb'[\x20-\x7e]{5,}', self.data):
            va = self.va(m.start())
            if va is not None and not (self.text[1] <= va < self.text[1] + self.text[4]):
                found.append((va, m.group().decode('latin-1')))
        return found

    def find_strings(self, pattern):
        rx = re.compile(pattern)
        return [(va, s) for va, s in self.strings() if rx.search(s)]

    def xrefs(self, target_va):
        """Addresses in the code where the 32-bit value target_va appears (push, mov, lea of an absolute address)."""
        needle = struct.pack('<I', target_va)
        start, raw, size = self.text[1], self.text[3], self.text[4]
        code = self.data[raw:raw + size]
        hits, at = [], code.find(needle)
        while at != -1:
            hits.append(start + at)
            at = code.find(needle, at + 1)
        return hits

    # -- functions -------------------------------------------------------------------------
    def function_start(self, va, back=0x4000):
        """Start of the function that holds va: the nearest earlier 'push ebp; mov ebp, esp' that follows
        padding (int3 or nop) or a return."""
        off = self.offset(va)
        lo = max(self.text[3], off - back)
        chunk = self.data[lo:off]
        at = len(chunk)
        while True:
            at = chunk.rfind(b'\x55\x8b\xec', 0, at)
            if at == -1:
                return None
            if at == 0 or chunk[at - 1] in (0xCC, 0x90, 0xC3) or chunk[at - 3:at - 2] == b'\xc2':
                return self.va(lo + at)

    def disassemble(self, start, limit=0x3000):
        """Instructions from start up to the end of the function (the last return before padding)."""
        import capstone
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        md.detail = False
        code = self.read(start, limit)
        out, furthest = [], start
        for ins in md.disasm(code, start):
            out.append(ins)
            if ins.mnemonic.startswith('j') and ins.op_str.startswith('0x'):
                try:
                    furthest = max(furthest, int(ins.op_str, 16))
                except ValueError:
                    pass
            if ins.mnemonic in ('ret', 'retn') and ins.address >= furthest:
                break
        return out

    def annotate(self, ins):
        """Text of an instruction with what its absolute operand points at: a string, a float, a double."""
        notes = []
        for m in re.finditer(r'0x([0-9a-f]{6,8})', ins.op_str):
            va = int(m.group(1), 16)
            if not any(start <= va < start + rsize for _, start, _, _, rsize in self.sections):
                continue
            if self.text[1] <= va < self.text[1] + self.text[4]:
                continue
            if 'qword' in ins.op_str:
                notes.append(f'double {self.f64(va):.6g}')
            elif ins.mnemonic.startswith(('movss', 'mulss', 'addss', 'subss', 'divss', 'comiss', 'ucomiss', 'cvtss', 'maxss', 'minss',
                                         'fld', 'fmul', 'fadd', 'fsub', 'fdiv', 'fcom')) and 'dword' in ins.op_str:
                notes.append(f'float {self.f32(va):.6g}')
            else:
                text = self.cstring(va, 120)
                if len(text) >= 4 and all(32 <= ord(c) < 127 for c in text[:4]):
                    notes.append(repr(text[:90]))
        return f'{ins.address:08x}  {ins.mnemonic:8s} {ins.op_str}' + ('    ; ' + ' | '.join(notes) if notes else '')


def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    exe = Exe()
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == 'strings':
        for va, s in exe.find_strings(arg):
            print(f'{va:08x}  {s}')
    elif cmd == 'xrefs':
        for va, s in exe.find_strings(re.escape(arg)):
            refs = exe.xrefs(va)
            print(f'{va:08x}  {s!r}: {len(refs)} reference(s)')
            for r in refs:
                start = exe.function_start(r)
                print(f'    at {r:08x}, in the function at {start:08x}' if start else f'    at {r:08x}')
    elif cmd in ('func', 'floats'):
        va = int(arg, 16)
        start = exe.function_start(va + 3) or va
        ins = exe.disassemble(start)
        print(f'function at {start:08x}, {len(ins)} instructions, to {ins[-1].address:08x}')
        for i in ins:
            line = exe.annotate(i)
            if cmd == 'func' or '; ' in line:
                print(line)


if __name__ == '__main__':
    main()

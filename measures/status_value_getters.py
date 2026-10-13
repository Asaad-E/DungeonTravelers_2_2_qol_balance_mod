"""Which value getter each status effect uses: the method at [vtable + 0x2c] of the class Command::CreateCommand
builds for the effect. The getters that call the dance and song bonus (0x48bf90) differ in how they use it, so a
dance that lowers a stat does not grow the way one that raises it does. Nothing is written but the list.

    python measures/status_value_getters.py
"""
import collections
import os
import sys

import capstone

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import exe_effects                                        # noqa: E402
from exe_reader import Exe                                # noqa: E402

VALUE_SLOT, BONUS = 0x2c, 0x48bf90


def main():
    exe = Exe()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    classes = exe_effects.command_classes(exe, md)
    by_getter = collections.defaultdict(list)
    for eid, vtable in sorted(classes.items()):
        by_getter[exe.u32(vtable + VALUE_SLOT)].append(eid)
    for getter, ids in sorted(by_getter.items()):
        body = list(md.disasm(exe.read(getter, 0x90), getter))
        end = next((k for k, i in enumerate(body) if i.mnemonic == 'ret'), len(body) - 1)
        body = body[:end + 1]
        if not any(i.mnemonic == 'call' and i.op_str == hex(BONUS) for i in body):
            continue
        print(hex(getter), 'effects', ids)
        for i in body:
            if i.mnemonic in ('call', 'addss', 'subss', 'mulss', 'divss', 'movss', 'mov') and ('xmm' in i.op_str or i.mnemonic == 'call'
                                                                                             or 'edx' in i.op_str):
                print('     ', hex(i.address), i.mnemonic, i.op_str)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

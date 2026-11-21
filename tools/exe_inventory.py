"""
Phase 0 Mechanical Binary Inventory (Clean-Room: Vanilla Exe + Vanilla .pck/.zip ONLY).

    python tools/exe_inventory.py

Reads ONLY:
  - backups/exe/DT22_en_unwrapped.vanilla.exe (asserting pinned SHA-256)
  - backups/**/*.pck and backups/Dungeon/floor_*.zip
  - data_tables/record_layouts.json

NEVER reads or writes quarantined docs or spreadsheets (docs/FORMULAS.md, docs/ENGINE_AUDIT.md,
balance_criteria.xlsx, qol_rules.xlsx, vanilla_source_of_truth.xlsx, engine_cs/, gamedata/).

Writes:
  - docs/binary_spec/00_INVENTORY.json
  - docs/binary_spec/00_INVENTORY.md
  - docs/binary_spec/STATE.json (initialized if missing)
"""
import collections
import datetime
import json
import os
import re
import struct
import sys
import zipfile

import capstone

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)

from exe_reader import Exe, VANILLA_PATH, VANILLA_SHA256, verify_vanilla_sha256  # noqa: E402
import exe_effects  # noqa: E402
import exe_enchants  # noqa: E402
from pck_handler import PckArchive  # noqa: E402

BACKUPS = os.path.join(ROOT, 'backups')
SPEC_DIR = os.path.join(ROOT, 'docs', 'binary_spec')
LAYOUTS_PATH = os.path.join(ROOT, 'data_tables', 'record_layouts.json')

COMBAT_LOW, COMBAT_HIGH = 0x413000, 0x570000
TARGET_NAMESPACES = ('Action', 'Battle', 'Command', 'Game', 'ItemResult', 'Parameter')
VTABLE_FLAG_SLOTS = (0x54, 0x5c, 0x64, 0x68, 0x6c, 0x70, 0x74, 0x78, 0x7c, 0x84, 0x8c)
RDATA_RANGE = (0x630000, 0x720000)

# Known vanilla VAs of intentional Balance mod hooks X01..X17 (vanilla bytes read from pinned exe)
MOD_PATCH_VAS = [
    ('X01..X08', 'python_progression', 0x450781, 0x450815, 'EXP level-gap factors'),
    ('X09..X12', 'python_progression', 0x4f9502, 0x4f9530, 'Level-reset crown steps'),
    ('X13', 'cs_combat', 0x424768, 0x424769, 'Arcane Shield proc chance byte'),
    ('X14', 'cs_combat', 0x44d044, 0x44d04c, 'Chant interruption product'),
    ('X15', 'out_of_combat', 0x48d5f3, 0x48d5f8, 'Dungeon map steps per status turn'),
    ('X16', 'cs_combat', 0x47ee73, 0x47ee75, 'Third Eye Wide buff dispel jump'),
    ('X17', 'cs_combat', 0x44ccd2, 0x44ccd5, 'Positive Trance threshold'),
]


def hex_va(va):
    return f'0x{va:06x}'


def cstring(buf, off):
    if off <= 0 or off >= len(buf):
        return ''
    end = buf.find(b'\x00', off)
    if end < 0:
        end = len(buf)
    return bytes(buf[off:end]).decode('utf-8', 'replace')


def scan_rtti_vtables(exe):
    """Discover all MSVC 32-bit RTTI classes and their vtable VAs across the executable."""
    d = exe.data
    rdata_sec = next(s for s in exe.sections if s[0] == '.rdata')
    _, r_va, _, r_off, r_size = rdata_sec
    r_bytes = d[r_off:r_off + r_size]

    # 1. Locate TypeDescriptors ('.?AV...@...@@') in .data/.rdata
    td_map = {}  # td_va -> (namespace, class_name, raw_mangled)
    for m in re.finditer(rb'\.\?AV([A-Za-z0-9_@]+)@@\x00', d):
        raw = m.group(1).decode('ascii', 'ignore')
        parts = [p for p in raw.split('@') if p]
        if not parts:
            continue
        cls = parts[0]
        ns = parts[-1] if len(parts) > 1 else ''
        # TypeDescriptor starts 8 bytes before the '.?AV' name string
        name_va = exe.va(m.start())
        if name_va is None:
            continue
        td_va = name_va - 8
        td_map[td_va] = (ns, cls, '::'.join(reversed(parts)))

    # 2. Find CompleteObjectLocators in .rdata referencing td_va at offset +12 (signature=0, offset, cdOffset, pTypeDescriptor, pClassDescriptor)
    col_map = {}  # col_va -> (ns, cls, qual_name)
    for off in range(0, r_size - 20, 4):
        sig, offset, cd_off, p_td, p_cd = struct.unpack_from('<IIIII', r_bytes, off)
        if sig == 0 and offset == 0 and cd_off == 0 and p_td in td_map and RDATA_RANGE[0] <= p_cd < RDATA_RANGE[1]:
            col_map[r_va + off] = td_map[p_td]

    # 3. Vtable pointers sit immediately after the pointer to CompleteObjectLocator in .rdata
    vtables = {}  # vtable_va -> {'namespace', 'class', 'qualified', 'methods_sample'}
    for off in range(0, r_size - 8, 4):
        p_col = struct.unpack_from('<I', r_bytes, off)[0]
        if p_col in col_map:
            vt_va = r_va + off + 4
            m0 = struct.unpack_from('<I', r_bytes, off + 4)[0]
            if 0x401000 <= m0 < 0x630000:
                ns, cls, qual = col_map[p_col]
                # Read up to 40 contiguous code pointers in vtable
                methods = []
                for slot in range(48):
                    if off + 4 + 4 * slot + 4 > r_size:
                        break
                    ptr = struct.unpack_from('<I', r_bytes, off + 4 + 4 * slot)[0]
                    if 0x401000 <= ptr < 0x630000:
                        methods.append(ptr)
                    else:
                        break
                vtables[vt_va] = {
                    'vtable': hex_va(vt_va),
                    'namespace': ns,
                    'class': cls,
                    'qualified': qual,
                    'method_count': len(methods),
                    'methods': [hex_va(x) for x in methods[:12]],
                    '_raw_methods': methods,
                }
    return vtables


def scan_assert_strings(exe):
    """Find all C++ Namespace::Class::Method strings referenced from 0x413000..0x570000."""
    d = exe.data
    text_va, text_off, text_size = exe.text[1], exe.text[3], exe.text[4]
    low_off = exe.offset(COMBAT_LOW)
    high_off = exe.offset(COMBAT_HIGH)
    combat_code = d[low_off:high_off]

    # Map string VA -> string for Namespace::... strings in target namespaces
    ns_pat = rb'(?:' + b'|'.join(n.encode('ascii') for n in TARGET_NAMESPACES) + rb')::[A-Za-z0-9_:~<>]+'
    by_ns = collections.defaultdict(list)
    seen = set()
    for m in re.finditer(ns_pat, d):
        s_va = exe.va(m.start())
        if s_va is None:
            continue
        txt = m.group(0).decode('ascii', 'ignore')
        packed = struct.pack('<I', s_va)
        xrefs = [COMBAT_LOW + x.start() for x in re.finditer(re.escape(packed), combat_code)]
        if xrefs:
            ns = txt.split('::', 1)[0]
            key = (ns, txt)
            if key not in seen:
                seen.add(key)
                funcs = sorted({exe.function_start(x) or x for x in xrefs})
                by_ns[ns].append({
                    'name': txt,
                    'string_va': hex_va(s_va),
                    'funcs': [hex_va(f) for f in funcs],
                })
    for ns in by_ns:
        by_ns[ns].sort(key=lambda r: r['funcs'][0])
    return dict(by_ns)


def scan_jump_tables(exe, md):
    """Scan 0x413000..0x570000 for indirect indexed jumps: jmp dword ptr [reg*4 + disp32] (FF 24 XX disp32)."""
    low_off = exe.offset(COMBAT_LOW)
    high_off = exe.offset(COMBAT_HIGH)
    code = exe.data[low_off:high_off]
    tables = []
    seen_tables = set()
    # FF 24 (ModRM=0x24 -> SIB, disp32) where SIB scale=2 (bits 7..6 = 10 -> 0x80..0xBF) and base=5 (disp32 -> low 3 bits = 5)
    for m in re.finditer(rb'\xff\x24[\x85\x8d\x95\x9d\xad\xb5\xbd](....)', code, re.S):
        jmp_va = COMBAT_LOW + m.start()
        tbl_va = struct.unpack('<I', m.group(1))[0]
        if not (0x401000 <= tbl_va < 0x720000):
            continue
        # Verify at least 3 consecutive entries point into .text
        ptrs = []
        for k in range(3):
            raw = exe.read(tbl_va + 4 * k, 4)
            if len(raw) < 4:
                break
            p = struct.unpack('<I', raw)[0]
            if 0x401000 <= p < 0x630000:
                ptrs.append(p)
            else:
                break
        if len(ptrs) < 3:
            continue
        # Look backward up to 64 bytes for 'cmp reg, N' bound
        bound = None
        back_start = max(COMBAT_LOW, jmp_va - 64)
        back_ins = list(md.disasm(exe.read(back_start, jmp_va - back_start), back_start))
        for ins in reversed(back_ins):
            if ins.mnemonic == 'cmp':
                cm = re.search(r',\s*(0x[0-9a-f]+|\d+)$', ins.op_str)
                if cm:
                    bound = int(cm.group(1), 0)
                    break
            elif ins.mnemonic in ('ret', 'int3'):
                break
        # Count contiguous valid .text pointers if bound is missing or verify up to bound+1
        max_n = (bound + 1) if (bound is not None and 1 <= bound <= 512) else 64
        targets = []
        for k in range(max_n):
            raw = exe.read(tbl_va + 4 * k, 4)
            if len(raw) < 4:
                break
            p = struct.unpack('<I', raw)[0]
            if 0x401000 <= p < 0x630000:
                targets.append(p)
            else:
                break
        if tbl_va in seen_tables:
            continue
        seen_tables.add(tbl_va)
        fn = exe.function_start(jmp_va) or jmp_va
        tables.append({
            'table_va': hex_va(tbl_va),
            'jmp_va': hex_va(jmp_va),
            'func_va': hex_va(fn),
            'cmp_bound': bound,
            'entry_count': len(targets),
            'unique_targets': len(set(targets)),
            'first_targets': [hex_va(x) for x in targets[:8]],
        })
    tables.sort(key=lambda t: int(t['jmp_va'], 16))
    return tables


def decode_vtable_flag(exe, md, method_va):
    """Decode a CCommand vtable boolean/constant stub into 0, 1, int const, or 'dynamic:0x...'."""
    ins = list(md.disasm(exe.read(method_va, 16), method_va))
    if not ins:
        return f'dynamic:{hex_va(method_va)}'
    i0 = ins[0]
    if i0.mnemonic == 'xor' and i0.op_str in ('eax, eax', 'al, al') and len(ins) > 1 and ins[1].mnemonic == 'ret':
        return 0
    if i0.mnemonic == 'mov' and i0.op_str.startswith('eax, ') and len(ins) > 1 and ins[1].mnemonic == 'ret':
        try:
            return int(i0.op_str.split(', ')[1], 0)
        except ValueError:
            pass
    if i0.mnemonic == 'mov' and i0.op_str in ('al, 1', 'al, 0') and len(ins) > 1 and ins[1].mnemonic == 'ret':
        return int(i0.op_str.split(', ')[1], 0)
    return f'dynamic:{hex_va(method_va)}'


def extract_route_a_ccommand(exe, md, vtables):
    """Route (a): CCommand factory (0x47b220) + full vtable flag matrix."""
    classes = exe_effects.command_classes(exe, md)
    result = {}
    vtable_groups = collections.defaultdict(list)
    for eid in sorted(classes):
        vt = classes[eid]
        info = vtables.get(vt, {})
        tick_va = exe.u32(vt + 0x0c)
        apply_va = exe.u32(vt + 0x18)
        flags = {}
        for slot in VTABLE_FLAG_SLOTS:
            m_va = exe.u32(vt + slot)
            val = decode_vtable_flag(exe, md, m_va)
            flags[f'+0x{slot:02x}'] = val
            if val == 1 or (isinstance(val, str) and val.startswith('dynamic:')):
                vtable_groups[f'+0x{slot:02x}'].append((eid, val))
        result[str(eid)] = {
            'id': eid,
            'vtable': hex_va(vt),
            'class': info.get('qualified', ''),
            'tick_va': hex_va(tick_va),
            'apply_va': hex_va(apply_va),
            'plain_apply': apply_va == exe_effects.PLAIN_APPLY,
            'flags': flags,
        }
    group_summary = {}
    for slot, items in sorted(vtable_groups.items()):
        const_ones = sorted(eid for eid, v in items if v == 1)
        dyn = sorted((eid, v) for eid, v in items if v != 1)
        group_summary[slot] = {
            'always_1_ids': const_ones,
            'dynamic_ids': [{'id': eid, 'handler': v} for eid, v in dyn],
        }
    return result, group_summary


def extract_route_d_patterns(exe, md, vtables):
    """Route (d): CActionSkill::_CreatePattern (0x41e060), CActionEnemyAttack::_CreatePattern (0x41a4a0), and special patterns."""
    def parse_switch_vtable(cases_vas):
        out = []
        for idx, target in enumerate(cases_vas):
            vt = None
            for k, i in enumerate(md.disasm(exe.read(target, 0x120), target)):
                if i.mnemonic == 'mov':
                    m = re.fullmatch(r'dword ptr \[e..\], (0x6[0-9a-f]{5})', i.op_str)
                    if m:
                        vt = int(m.group(1), 16)
                elif i.mnemonic == 'call' and re.fullmatch(r'0x4[12][0-9a-f]{4}', i.op_str):
                    # Follow 1-level constructor call to find vtable store
                    callee = int(i.op_str, 16)
                    for ck, ci in enumerate(md.disasm(exe.read(callee, 0x80), callee)):
                        if ci.mnemonic == 'mov':
                            cm = re.fullmatch(r'dword ptr \[e..\], (0x6[0-9a-f]{5})', ci.op_str)
                            if cm:
                                vt = int(cm.group(1), 16)
                        if ci.mnemonic == 'ret' or ck > 30:
                            break
                if i.mnemonic in ('jmp', 'ret') or k > 50:
                    break
            info = vtables.get(vt, {}) if vt else {}
            out.append({
                'pattern_id': idx,
                'case_va': hex_va(target),
                'vtable': hex_va(vt) if vt else None,
                'class': info.get('qualified', ''),
            })
        return out

    skill_cases = [exe.u32(0x41e5fc + 4 * k) for k in range(16)]
    enemy_byte_idx = list(exe.read(0x41a838, 18))
    enemy_cases = [exe.u32(0x41a814 + 4 * b) for b in enemy_byte_idx]
    pattern_classes = sorted(
        [{'vtable': v['vtable'], 'class': v['qualified'], 'method_count': v['method_count']}
         for v in vtables.values() if 'CActionPattern' in v['qualified']],
        key=lambda x: x['class']
    )
    direct_update_patterns = [
        {'name': 'CActionPatternE0822', 'ctor_va': '0x42b240', 'caller_va': '0x438066'},
        {'name': 'CActionPatternE0835', 'ctor_va': '0x42b8a0', 'caller_va': '0x438211'},
        {'name': 'CActionPatternT0094', 'ctor_va': '0x42ec90', 'caller_va': '0x438411'},
        {'name': 'CActionPatternU0008', 'ctor_va': '0x42f870', 'caller_va': '0x436b6a'},
    ]
    return {
        'skill_create_pattern_va': '0x41e060',
        'skill_cases': parse_switch_vtable(skill_cases),
        'enemy_create_pattern_va': '0x41a4a0',
        'enemy_cases': parse_switch_vtable(enemy_cases),
        'direct_update_patterns': direct_update_patterns,
        'random_enemy_attack_table_va': '0x64f1c0',
        'rtti_pattern_classes': pattern_classes,
    }


def extract_route_e_item_results(exe, vtables):
    """Route (e): ItemResult 107-case switch table (0x50c570 / 0x50e538)."""
    cases = struct.unpack('<107I', exe.read(0x50e538, 4 * 107))
    pat_skill = re.compile(rb'\x6a(.)\x6a(.)(?:\x6a(.)|\x68(....))\xe8', re.S)
    out = []
    for kind, case_va in enumerate(cases):
        stores = [struct.unpack('<I', m.group(1))[0]
                  for m in re.finditer(rb'\xc7[\x00-\x07](....)', exe.read(case_va, 0x60), re.S)]
        vts = [v for v in stores if RDATA_RANGE[0] <= v < RDATA_RANGE[1]]
        vt = vts[-1] if vts else None
        method_va = exe.u32(vt + 12) if vt else None
        cast_skill = None
        if method_va:
            m = pat_skill.match(exe.read(method_va, 16))
            if m:
                fixed_lv = struct.unpack('<b', m.group(1))[0]
                use_val = m.group(2)[0]
                sid = m.group(3)[0] if m.group(3) else struct.unpack('<I', m.group(4))[0]
                cast_skill = {'skill_id': sid, 'use_val_as_level': use_val, 'fixed_level': fixed_lv}
        info = vtables.get(vt, {}) if vt else {}
        out.append({
            'item_effect_type': kind,
            'case_va': hex_va(case_va),
            'vtable': hex_va(vt) if vt else None,
            'class': info.get('qualified', ''),
            'apply_va': hex_va(method_va) if method_va else None,
            'cast_skill': cast_skill,
        })
    return out


def scan_vanilla_pck_usage():
    """Scan raw vanilla backups/** directly (zero quarantined xlsx files) for used IDs and counts."""
    with open(LAYOUTS_PATH, encoding='utf-8') as f:
        lay = json.load(f)

    def h(v):
        return int(v, 16) if isinstance(v, str) else int(v)

    # 1. Raw command names from backups/CommandData.pck
    raw_cmd_names = {}
    cmd_pck = os.path.join(BACKUPS, 'CommandData.pck')
    if os.path.exists(cmd_pck):
        arc = PckArchive(cmd_pck)
        for _, b in arc.files:
            if len(b) >= 16:
                cid = struct.unpack_from('<i', b, 0)[0]
                ptr = struct.unpack_from('<Q', b, 8)[0]
                raw_cmd_names[cid] = cstring(b, ptr)

    # 2. Raw enchant names + stacking flags from backups/EnchantData.pck
    raw_enchants = {}
    enc_pck = os.path.join(BACKUPS, 'EnchantData.pck')
    if os.path.exists(enc_pck):
        arc = PckArchive(enc_pck)
        fl_off = h(lay['EnchantData']['flags'])
        for _, b in arc.files:
            if len(b) >= fl_off + 4:
                eid = struct.unpack_from('<i', b, 0)[0]
                flags = struct.unpack_from('<I', b, fl_off)[0]
                p0 = struct.unpack_from('<Q', b, 8)[0]
                raw_enchants[eid] = {'name': cstring(b, p0), 'flags': hex(flags), 'stacks': bool(flags & 1)}

    effect_counts = collections.Counter()
    effect_sources = collections.defaultdict(lambda: collections.Counter())
    skill_patterns = collections.Counter()
    attack_patterns = collections.Counter()
    item_types = collections.Counter()
    enchant_uses = collections.Counter()
    enemy_flag_bits = collections.Counter()
    ai_opcodes = collections.Counter()

    # 3. Skills: Technique, Magic, Passive
    for cat in ('Technique', 'Magic', 'Passive'):
        spec = lay['skills'][cat]
        arc = PckArchive(os.path.join(BACKUPS, spec['pck']))
        cnt_off = h(spec['count'])
        slots_off = h(spec['slots'])
        n_slots = spec['n_slots']
        slot_sz = h(lay['skills']['slot_size'])
        tr_off = h(spec['trailer'])
        for _, b in arc.files:
            if len(b) < tr_off + 20:
                continue
            cnt = max(0, min(struct.unpack_from('<i', b, cnt_off)[0], n_slots))
            for k in range(cnt):
                eid = struct.unpack_from('<i', b, slots_off + k * slot_sz)[0]
                if eid >= 0:
                    effect_counts[eid] += 1
                    effect_sources[eid][cat] += 1
            if cat in ('Technique', 'Magic'):
                pat = struct.unpack_from('<i', b, tr_off + 16)[0]
                skill_patterns[pat] += 1

    # 4. UniqueSkills
    uspec = lay['UniqueSkillData']
    arc = PckArchive(os.path.join(BACKUPS, uspec['pck']))
    ue_off = h(uspec['effect'])
    for _, b in arc.files:
        if len(b) >= ue_off + 4:
            eid = struct.unpack_from('<i', b, ue_off)[0]
            if eid >= 0:
                effect_counts[eid] += 1
                effect_sources[eid]['Unique'] += 1

    # 5. EnemyAttackData
    aspec = lay['EnemyAttackData']
    arc = PckArchive(os.path.join(BACKUPS, aspec['pck']))
    acnt_off, aslots_off, aslot_sz = h(aspec['slot_count']), h(aspec['slots']), aspec['slot_size']
    for _, b in arc.files:
        if len(b) < 0x94:
            continue
        cnt = max(0, min(struct.unpack_from('<i', b, acnt_off)[0], 5))
        for k in range(cnt):
            eid = struct.unpack_from('<i', b, aslots_off + k * aslot_sz)[0]
            if eid >= 0:
                effect_counts[eid] += 1
                effect_sources[eid]['EnemyAttack'] += 1
        pat = struct.unpack_from('<i', b, 0x90)[0]
        attack_patterns[pat] += 1

    # 6. ItemData
    ispec = lay['ItemData']
    arc = PckArchive(os.path.join(BACKUPS, ispec['pck']))
    ip_off = h(ispec['pairs'])
    for _, b in arc.files:
        if len(b) < ip_off + 32:
            continue
        for k in range(ispec['pair_count']):
            t = struct.unpack_from('<i', b, ip_off + k * 8)[0]
            if t >= 0:
                item_types[t] += 1

    # 7. EquipmentData & SealScrollData enchants
    eq_spec = lay['EquipmentData']
    arc = PckArchive(os.path.join(BACKUPS, 'EquipmentData.pck'))
    ec_off, es_off = h(eq_spec['enchant_count']), h(eq_spec['enchants'])
    for _, b in arc.files:
        if len(b) < es_off + 16:
            continue
        cnt = max(0, min(struct.unpack_from('<i', b, ec_off)[0], eq_spec['enchant_slots']))
        for k in range(cnt):
            eid = struct.unpack_from('<i', b, es_off + k * 4)[0]
            if eid > 0:
                enchant_uses[eid] += 1

    ss_spec = lay['SealScrollData']
    arc = PckArchive(os.path.join(BACKUPS, 'SealScrollData.pck'))
    sc_off, ss_off = h(ss_spec['count']), h(ss_spec['enchants'])
    for _, b in arc.files:
        if len(b) < ss_off + 16:
            continue
        cnt = max(0, min(struct.unpack_from('<i', b, sc_off)[0], ss_spec['slots']))
        for k in range(cnt):
            eid = struct.unpack_from('<i', b, ss_off + k * 4)[0]
            if eid > 0:
                enchant_uses[eid] += 1

    # 8. Enemy/Enemy.pck flags & AI opcodes (+ Summon + NPC AI)
    def scan_ai_blob(blob):
        if not blob:
            return
        i = 0
        while i < len(blob):
            b0 = blob[i]
            if b0 == 0xFF:
                break
            ai_opcodes[b0] += 1
            i += 1

    epck = PckArchive(os.path.join(BACKUPS, 'Enemy', 'Enemy.pck'))
    for _, eb in epck.files:
        inner = PckArchive.from_bytes(eb)
        imap = {n: d for n, d in inner.files}
        if 'EnemyStatusData.bin' in imap:
            sb = imap['EnemyStatusData.bin']
            if len(sb) >= 0x40:
                fl = struct.unpack_from('<I', sb, 0x3C)[0]
                for bit in range(32):
                    if (fl >> bit) & 1:
                        enemy_flag_bits[bit] += 1
        if 'EnemyAIData.bin' in imap:
            scan_ai_blob(imap['EnemyAIData.bin'])

    # 9. Dungeon/floor_maps.zip fixed-battle count
    fmaps_zip = os.path.join(BACKUPS, 'Dungeon', 'floor_maps.zip')
    floor_map_count = 0
    if os.path.exists(fmaps_zip):
        with zipfile.ZipFile(fmaps_zip) as zf:
            floor_map_count = len(zf.namelist())

    return {
        'raw_command_names': {str(k): v for k, v in sorted(raw_cmd_names.items())},
        'raw_enchants': {str(k): v for k, v in sorted(raw_enchants.items())},
        'used_effects': {
            str(eid): {
                'id': eid,
                'raw_name': raw_cmd_names.get(eid, ''),
                'total_uses': cnt,
                'by_source': dict(effect_sources[eid]),
            }
            for eid, cnt in sorted(effect_counts.items())
        },
        'skill_patterns': {str(k): v for k, v in sorted(skill_patterns.items())},
        'attack_patterns': {str(k): v for k, v in sorted(attack_patterns.items())},
        'used_item_effect_types': {str(k): v for k, v in sorted(item_types.items())},
        'used_enchants_in_gear_sealbooks': {str(k): v for k, v in sorted(enchant_uses.items())},
        'enemy_0x3c_flag_bits': {str(k): v for k, v in sorted(enemy_flag_bits.items())},
        'floor_maps_entries': floor_map_count,
    }


def build_audit_catalog(ccommand, askers, enchants_reads, route_d, route_e, pck_usage):
    """Build the stratified Phase-4 atomic audit catalog directly from the binary inventory."""
    catalog = []

    def add(item_id, stratum, module, title, va_hints, pck_refs=None):
        catalog.append({
            'id': item_id,
            'stratum': stratum,
            'module': module,
            'title': title,
            'va_hints': va_hints,
            'pck_refs': pck_refs or 0,
        })

    # Stratum 1: core_combat (M00-M05)
    core_items = [
        ('CC01', 'M00', 'End-to-end action pipeline & hand-off order', ['0x4360f0', '0x41e060', '0x41a4a0', '0x423560']),
        ('CC02', 'M01', 'CBattleBase::Update outer & inner state tables (0x4397e0/0x439820/0x439884)', ['0x436254', '0x43670c', '0x438ea4']),
        ('CC03', 'M01', 'ATB _SetTime, weapon/chant speed weights & caps', ['0x4499d0', '0x4f7280', '0x4f54d0', '0x557590']),
        ('CC04', 'M01', 'Extra turns (288/289/354) re-entry & state skip', ['0x4365ff', '0x438cd2', '0x43903b']),
        ('CC05', 'M01', 'Battle start gauges, ambush, preemptive 300 & tie-breaking', ['0x449130', '0x44a3d0', '0x440b50']),
        ('CC06', 'M01', 'Chant & performance interruption (physical & magic crit)', ['0x44cf90', '0x44f12a']),
        ('CC07', 'M02', 'Physical base ATK/DEF, swing, power modifiers & caps', ['0x44b221', '0x44b3b4']),
        ('CC08', 'M02', 'Physical range/row factor, defending, min damage & zones', ['0x44a790', '0x44fbb0', '0x44cf00']),
        ('CC09', 'M02', 'Physical critical rate, multiplier & crit-linked procs (Murder 258)', ['0x44f190', '0x44d26f']),
        ('CC10', 'M02', 'Physical multi-hit weight tables (89..100) & Rondo shift', ['0x417d50', '0x6c94c0']),
        ('CC11', 'M02', 'Physical slayer/element/race/resistance & SpecialDamage', ['0x44f5d0', '0x44f720', '0x44bf19']),
        ('CC12', 'M02', 'Physical mitigation: cuts (66..71), Material Guard 179, Limit Field 190, Imperial Guard 308, Demon Wall 356', ['0x44bb82', '0x44c6c0', '0x44c780', '0x44cbb9']),
        ('CC13', 'M03', 'Magic base INT/RES (incl. effect 47), power, mastery & swing', ['0x44db97', '0x44dc50']),
        ('CC14', 'M03', 'Magic element boosts, cuts (68..71, 183), RaceGuard & additive other (88/190/267)', ['0x44e72e', '0x44eabb', '0x44eb59', '0x44ed53']),
        ('CC15', 'M03', 'Magic hit/miss grazed damage (1/2, 3/4 w/ 272), 1..5 floor, crit 301 & living-only 87', ['0x44ee33', '0x44eb25', '0x44e86c']),
        ('CC16', 'M04', 'Physical hit/evasion formula, Barcarole/220/223 divisors, fixed hit 55/72 & caps', ['0x44a850']),
        ('CC17', 'M04', 'Magic hit/evasion formula & missed-spell AfterHit trigger', ['0x44d370', '0x421a83']),
        ('CC18', 'M04', 'Target selection: Provoke 170, formation shares 0x43daca, pierce/row/random/137 scopes', ['0x44a630', '0x43daca', '0x43fde8', '0x42017a']),
        ('CC19', 'M05', 'Healing 103/104/105/128..132, Heal Mastery 245/317, caps & Doll heal bonus', ['0x48d730', '0x48c5c0', '0x481800', '0x483a60']),
        ('CC20', 'M05', 'After-battle Generous Heart 272/273, Maid Mastery 278/353 & regen ticks', ['0x43d6a7', '0x437bb5', '0x48a640']),
        ('CC21', 'M05', 'ItemResult switch (0x50e538): 41 skill-cast items vs custom item handlers (0, 53/54, 89, cures)', ['0x50c570', '0x50e538', '0x50b030']),
    ]
    for cid, mod, title, vas in core_items:
        add(cid, 'core_combat', mod, title, vas)

    # Stratum 2: status_procs (M06-M08)
    sp_items = [
        ('SP01', 'M06', 'AddStatus (0x4f9930) overwrite & exclusive vtable groups (+0x7c enchants, +0x84 barriers)', ['0x4f9930', '0x4f9bff', '0x4f9c7c']),
        ('SP02', 'M06', 'Stat recalculation (0x4fbdd0): 41..46, 189/193/194, Trump Card 48, Petrify 120, Dual-Wield offhand, [0,9999]', ['0x4fbdd0', '0x4fc01d', '0x4fc26f']),
        ('SP03', 'M06', 'Resistance recalculation (0x4fc050..0x4fc75f): 192 (+10000), 169/202/341/248, 184..186, Samsara & [-100,+100]', ['0x4fc050', '0x4fc1b0', '0x4fc6c7']),
        ('SP04', 'M06', 'MaxHP buff 172 (BaseHp scaling + expiry HP clamp) & timed status countdown (0x48d590)', ['0x4fc089', '0x4fc63a', '0x48d590']),
        ('SP05', 'M06', 'Dispel 74 (vtable+0x64: DispelAlways vs DispelIfRaised) & Cure 106 order', ['0x4226c4', '0x4fb1f0', '0x481a92']),
        ('SP06', 'M06', 'Performance groups: Songs (210..223), Dances (195..205), Geass (335..341), slot caps (284/287) & dancer-turn ticks', ['0x43bdd0', '0x43cb80', '0x42b560']),
        ('SP07', 'M07', 'AilmentThreshold f32 formula, 0x3C immunity bits, nullify enchants 129..137/139 & barrier consumption', ['0x481fa0', '0x557fd0', '0x41f920']),
        ('SP08', 'M07', 'Ailment natural recovery (5% start, +10/turn, Third Eye 0%), re-application & sleep-decay (+0x8c)', ['0x43692f', '0x48d180', '0x48d5b5']),
        ('SP09', 'M07', 'Gradual & Instant Petrify (120/121) Stage 1->2->3, barrier cure & Alive/status-wipe semantics', ['0x48305a', '0x4f99c1', '0x4fa870']),
        ('SP10', 'M07', 'Hard/Soft turn loss (Sleep 116, Paralysis 115, Stun 118, Warning Shot 259, Mag Steps 283, Mesmerized 203, Poison 113, Shadow Sew 123, Delay 54)', ['0x436c3f', '0x482150', '0x483840', '0x423a41']),
        ('SP11', 'M08', 'Cover 171 (physical-only, end roll) & Parry 180 / Auto-Guard 255', ['0x420b70', '0x42496b', '0x4223b5', '0x4172dd']),
        ('SP12', 'M08', 'Counter 250, Reprisal/Avenger 249, Knock Down 305, Pretend 310 & !inCounter guards', ['0x422553', '0x424689', '0x4221ee', '0x421db8']),
        ('SP13', 'M08', 'Arcane Shield 447 (!inCounter, vanilla 15% vs X13 25%, single-bearer post-action)', ['0x424714', '0x425157']),
        ('SP14', 'M08', 'AfterHit reactive procs: Dark Aura 262, Slow Target 293, Sugar Coma 346, Ecstasy 312, Devil Whisper 320, Alter Fate 349', ['0x423cd0', '0x4227d5', '0x422b82', '0x47f59b', '0x421ca7']),
        ('SP15', 'M08', 'Death/Revive/Special procs: Resuscitate 188, Undaunted 355, Sacrifice 77, Life Bringer 133, Murder License 319, Third Eye 345, Samsara 291', ['0x43851e', '0x481060', '0x483ee0', '0x437364', '0x47ee00']),
        ('SP16', 'M08', 'Specialized CActionPattern* subclasses (T0105, M0124, M0140, E2520, E0822, E0835, T0094, U0008)', ['0x41e060', '0x41a4a0', '0x42b240', '0x42ec90']),
    ]
    for cid, mod, title, vas in sp_items:
        add(cid, 'status_procs', mod, title, vas)

    # Stratum 3: effects_passives (every active non-trivial Effect ID used in vanilla .pck across routes a/b/c)
    used_effects = pck_usage['used_effects']
    for eid_str, uinfo in sorted(used_effects.items(), key=lambda kv: int(kv[0])):
        eid = int(eid_str)
        cc = ccommand.get(eid_str)
        ask_vas = sorted(askers.get(eid, set()))
        if not cc and not ask_vas:
            continue
        vas = []
        if cc:
            vas.append(cc['apply_va'])
            if cc['tick_va'] not in ('0x48bc50', '0x48d160'):
                vas.append(cc['tick_va'])
        vas.extend(hex_va(a) for a in ask_vas[:4])
        rname = uinfo['raw_name'] or (cc['class'] if cc else f'Effect {eid}')
        add(f'EF{eid:03d}', 'effects_passives', 'M06/M08', f'Effect {eid} ({rname})', vas, uinfo['total_uses'])

    # Stratum 4: units_ai_loaders (M09-M11)
    ual_items = [
        ('UL01', 'M09', 'Doll creation, stats (0x4f7c00), Soul Seal 314, crown/cap 12, gauge & life (147+297)', ['0x484150', '0x4f7c00', '0x4fdfd0', '0x43a1a0']),
        ('UL02', 'M09', 'Star Dust Arrow (146/106), Genjimaru 427 & Shadow clone units', ['0x484491', '0x48b1f0']),
        ('UL03', 'M09', 'Summons (Summon.pck, multi-passive loading, SummonAIData.bin) & Hired Guests (NPC.pck, enchants 295/297)', ['0x4fecc0', '0x4ff630']),
        ('UL04', 'M09', 'Enchantment stat/resist/line/pep/speed/regen aggregation & stacking bit 0 (0x4f8270..0x4f8fcf)', ['0x4f8270', '0x4f5499', '0x4f69e0']),
        ('UL05', 'M10', 'Enemy/NPC/Summon AI VM: sources (0x432fa0), targets (0x434754), opcodes, once/switch flags & breath 3 bypass', ['0x431aa0', '0x432fa0', '0x434754']),
        ('UL06', 'M10', 'Fixed-battle triggers (floor_maps.zip 0x1F) & floor formations/zones (floor_parameters.zip)', ['0x44fbb0']),
        ('UL07', 'M10', 'Skill/Attack/Item/Equip binary extraction & pattern/trailer fields (extract_vanilla.py + engine_export.py + Loader.cs)', ['0x41e060', '0x41a4a0']),
        ('UL08', 'M10', 'Direct tools/*_data.py binary readers (enemy_data, class_data, character_data, summon_data, npc_data, doll_data, random_move_data)', ['0x64f8c0', '0x4f81e8']),
        ('UL09', 'M11', 'Unit build: ClassLevelData growth, GROWTH_ROW selection, reset bonuses & class modifiers (0x6d3b64)', ['0x4f81e8', '0x6d3b64']),
        ('UL10', 'M11', 'Unarmed weapon rank (ClassData+0x24 / 0x4f5585), dual-wield offhand rules & equipment stat caps', ['0x4f5585', '0x4fc26f']),
        ('UL11', 'M11', 'EXP/SP curves (LvExpSkptData.pck), level-gap factors (X01..X08) & crown reset steps (X09..X12)', ['0x450710', '0x4f9502']),
        ('UL12', 'M08', 'Random Move tables (T0111/T0118/T0130/M0129, 0x64f8c0..0x64fb50) & EffectSequence triggers', ['0x64f8c0']),
    ]
    for cid, mod, title, vas in ual_items:
        add(cid, 'units_ai_loaders', mod, title, vas)

    return catalog


def main():
    os.makedirs(SPEC_DIR, exist_ok=True)
    verify_vanilla_sha256(VANILLA_PATH)
    exe = Exe(VANILLA_PATH)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

    print('Scanning RTTI vtables...')
    vtables = scan_rtti_vtables(exe)
    ns_vtables = collections.defaultdict(list)
    for vt_va, info in sorted(vtables.items()):
        if info['namespace'] in TARGET_NAMESPACES:
            clean = {k: v for k, v in info.items() if not k.startswith('_')}
            ns_vtables[info['namespace']].append(clean)

    print('Scanning assert strings across 6 namespaces...')
    asserts = scan_assert_strings(exe)

    print('Scanning combat jump tables (0x413000..0x570000)...')
    jump_tables = scan_jump_tables(exe, md)

    print('Extracting Route (a) CCommand factory & vtable flags...')
    ccommand, vtable_groups = extract_route_a_ccommand(exe, md, vtables)

    print('Extracting Route (b)/(c) inline FINDERS, vtable+0x48/+0x50, [eff+0x24], pushed passives & enchants...')
    all_ids = set(range(0, 500))
    askers = exe_effects.askers(exe, md, all_ids)
    askers_json = {str(eid): sorted(hex_va(a) for a in vas) for eid, vas in sorted(askers.items()) if vas}
    enchant_reads_raw = exe_enchants.reads(exe)
    enchant_reads = collections.defaultdict(list)
    for fn, call_va, eid, scale, limits in enchant_reads_raw:
        enchant_reads[str(eid)].append({
            'func_va': hex_va(fn), 'call_va': hex_va(call_va), 'scale': scale, 'limits': limits
        })

    print('Extracting Route (d) Action::CAction*::_CreatePattern & CActionPattern*...')
    route_d = extract_route_d_patterns(exe, md, vtables)

    print('Extracting Route (e) ItemResult 107-case switch...')
    route_e = extract_route_e_item_results(exe, vtables)

    print('Scanning raw vanilla backups/**/*.pck & floor_maps.zip...')
    pck_usage = scan_vanilla_pck_usage()

    # Record exact vanilla bytes at X01..X17 patch VAs
    mod_patches = []
    for pid, owner, lo, hi, desc in MOD_PATCH_VAS:
        raw_bytes = exe.read(lo, hi - lo).hex()
        mod_patches.append({
            'id': pid, 'owner': owner, 'va_start': hex_va(lo), 'va_end': hex_va(hi),
            'vanilla_hex': raw_bytes, 'description': desc,
        })

    catalog = build_audit_catalog(ccommand, askers, enchant_reads, route_d, route_e, pck_usage)
    strata_counts = dict(collections.Counter(item['stratum'] for item in catalog))

    # Cross-check: which used_effects in vanilla .pck have neither Route (a) nor Route (b/c) handler?
    unhandled_used_effects = []
    for eid_str, uinfo in pck_usage['used_effects'].items():
        if eid_str not in ccommand and eid_str not in askers_json:
            unhandled_used_effects.append({'id': int(eid_str), 'raw_name': uinfo['raw_name'], 'uses': uinfo['total_uses'], 'by_source': uinfo['by_source']})

    inventory = {
        'meta': {
            'generated_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'exe_path': 'backups/exe/DT22_en_unwrapped.vanilla.exe',
            'exe_sha256': VANILLA_SHA256,
            'exe_size': len(exe.data),
            'combat_va_range': [hex_va(COMBAT_LOW), hex_va(COMBAT_HIGH)],
        },
        'summary': {
            'rtti_vtables_total_in_exe': len(vtables),
            'rtti_vtables_by_namespace': {ns: len(ns_vtables[ns]) for ns in TARGET_NAMESPACES},
            'assert_strings_by_namespace': {ns: len(asserts.get(ns, [])) for ns in TARGET_NAMESPACES},
            'combat_jump_tables_count': len(jump_tables),
            'route_a_ccommand_ids': len(ccommand),
            'route_bc_asker_effect_ids': len(askers_json),
            'route_c_enchant_ids_read_in_exe': len(enchant_reads),
            'route_d_rtti_pattern_classes': len(route_d['rtti_pattern_classes']),
            'route_e_item_result_cases': len(route_e),
            'pck_used_effects': len(pck_usage['used_effects']),
            'pck_used_effects_without_abc_handler': len(unhandled_used_effects),
            'audit_catalog_total': len(catalog),
            'audit_catalog_by_stratum': strata_counts,
        },
        'namespaces': {
            ns: {'rtti_vtables': ns_vtables[ns], 'assert_strings': asserts.get(ns, [])}
            for ns in TARGET_NAMESPACES
        },
        'combat_jump_tables': jump_tables,
        'route_a_ccommand': ccommand,
        'route_a_vtable_flag_groups': vtable_groups,
        'route_bc_effect_askers': askers_json,
        'route_c_enchant_reads': dict(sorted(enchant_reads.items(), key=lambda kv: int(kv[0]))),
        'route_d_action_patterns': route_d,
        'route_e_item_results': route_e,
        'pck_usage': pck_usage,
        'pck_used_effects_without_abc_handler': unhandled_used_effects,
        'mod_patches_vanilla_bytes': mod_patches,
        'audit_catalog': catalog,
    }

    json_path = os.path.join(SPEC_DIR, '00_INVENTORY.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=1, ensure_ascii=False)

    # Human-readable concise summary 00_INVENTORY.md
    s = inventory['summary']
    md_lines = [
        '# Phase 0 — Mechanical Binary Inventory (Generated)',
        '',
        f'Generated by `tools/exe_inventory.py` from `backups/exe/DT22_en_unwrapped.vanilla.exe` (SHA-256 `{VANILLA_SHA256}`) and raw `backups/**`. Zero quarantined docs or spreadsheets read.',
        '',
        '## 1. Combat Surface Denominator (`0x413000..0x570000`)',
        '',
        '| Namespace | RTTI Vtables | Assert Strings |',
        '|---|---:|---:|',
    ]
    for ns in TARGET_NAMESPACES:
        md_lines.append(f'| `{ns}::*` | {s["rtti_vtables_by_namespace"][ns]} | {s["assert_strings_by_namespace"][ns]} |')
    md_lines += [
        f'| **Total (6 combat/data namespaces)** | **{sum(s["rtti_vtables_by_namespace"].values())}** | **{sum(s["assert_strings_by_namespace"].values())}** |',
        '',
        f'- Combat jump tables found (`FF 24 ...` in `0x413000..0x570000`): **{s["combat_jump_tables_count"]}**',
        f'- Route (a) `CCommand` factory (`0x47b220`): **{s["route_a_ccommand_ids"]}** effect IDs',
        f'- Route (b/c) inline `FINDERS` / `vt+0x48/+0x50` / `[eff+0x24]` / `0x4e4dd0` / `0x4fab50`: **{s["route_bc_asker_effect_ids"]}** effect IDs',
        f'- Route (c) enchant slot `0xf0` reads: **{s["route_c_enchant_ids_read_in_exe"]}** enchantment IDs',
        f'- Route (d) `CActionPattern*` RTTI classes: **{s["route_d_rtti_pattern_classes"]}** (`CActionSkill` 16 cases, `CActionEnemyAttack` 18 cases, 4 direct `Update` patterns)',
        f'- Route (e) `ItemResult` switch (`0x50e538`): **{s["route_e_item_result_cases"]}** item effect types ({sum(1 for x in route_e if x["cast_skill"])} skill-casters)',
        f'- Vanilla `.pck` used Effect IDs: **{s["pck_used_effects"]}** (without Route a/b/c handler: **{s["pck_used_effects_without_abc_handler"]}**)',
        '',
        '## 2. `CCommand` Vtable Boolean Flag Groups (Exact Binary Ground Truth)',
        '',
        '| Vtable Slot | Always-1 Effect IDs | Dynamic Handlers |',
        '|---|---|---|',
    ]
    for slot, g in sorted(vtable_groups.items()):
        ones = ', '.join(str(x) for x in g['always_1_ids']) or '—'
        dyns = ', '.join(f'{x["id"]} ({x["handler"]})' for x in g['dynamic_ids']) or '—'
        md_lines.append(f'| `{slot}` | {ones} | {dyns} |')
    md_lines += [
        '',
        '## 3. Phase 4 Stratified Audit Catalog',
        '',
        f'Total atomic catalog items: **{s["audit_catalog_total"]}** (plus 3 out-of-catalog `Trace.cs` events per round).',
        '',
        '| Stratum | Items |',
        '|---|---:|',
    ]
    for st, cnt in sorted(strata_counts.items()):
        md_lines.append(f'| `{st}` | {cnt} |')
    md_lines += [
        '',
        '## 4. Vanilla `.pck` Used Effect IDs Without Route (a)/(b)/(c) Handler',
        '',
        '| Effect ID | Raw Name (`CommandData.pck`) | Uses | Sources |',
        '|---:|---|---:|---|',
    ]
    for u in unhandled_used_effects:
        md_lines.append(f'| {u["id"]} | {u["raw_name"]} | {u["uses"]} | {u["by_source"]} |')

    md_path = os.path.join(SPEC_DIR, '00_INVENTORY.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines) + '\n')

    # Initialize STATE.json if it doesn't exist yet
    state_path = os.path.join(SPEC_DIR, 'STATE.json')
    if not os.path.exists(state_path):
        modules = [
            ('M00', 'M00_PIPELINE.md', 'Global Action & Turn Call-Graph Pipeline'),
            ('M01', 'M01_TURN_LOOP_AND_ATB.md', 'Turn Loop, 3 Update Jump Tables, ATB & Extra Turns'),
            ('M02', 'M02_PHYSICAL_DAMAGE.md', 'Physical Damage, Range, Crit, Multi-Hit & Zones'),
            ('M03', 'M03_MAGICAL_DAMAGE.md', 'Magical Damage, Elements & Missed Spells'),
            ('M04', 'M04_HIT_EVASION_AND_TARGETING.md', 'Hit / Evasion, Targeting Scopes & Formation'),
            ('M05', 'M05_HEALING_RECOVERY_AND_ITEMS.md', 'Healing, Recovery, After-Battle & ItemResult (0..106)'),
            ('M06', 'M06_STATUS_LIFECYCLE_AND_RECALC.md', 'Status Lifecycle, Vtable Groups, Recalc & Dispel'),
            ('M07', 'M07_AILMENTS_AND_CONTROL.md', 'Ailments, Immunities, Barriers & Recovery'),
            ('M08', 'M08_PROCS_COUNTERS_AND_AFTERHIT.md', 'Procs, Counters, Cover, Parry, Patterns & AfterHit'),
            ('M09', 'M09_DOLLS_SUMMONS_NPCS_AND_ENCHANTS.md', 'Dolls, Summons, Guests & Enchantments'),
            ('M10', 'M10_ENEMY_AI_AND_DATA_LOADERS.md', 'Enemy/Summon/NPC AI VM, Map Triggers & Binary Readers'),
            ('M11', 'M11_UNIT_BUILD_AND_STATS.md', 'Unit Build, Growth, Unarmed Rank, Caps & EXP/SP Curves'),
        ]
        state = {
            'campaign_status': 'IN PROGRESS',
            'active_phase': 0,
            'exe_sha256': VANILLA_SHA256,
            'phases': {str(k): {'status': 'pending', 'signoff_commit': None} for k in range(6)},
            'modules': {
                mid: {
                    'file': fname, 'title': title,
                    'phase1_spec': 'pending', 'phase1_audit_check': 'pending',
                    'phase2_diff': 'pending', 'phase3_fix': 'pending',
                    'open_s0': 0, 'open_s1': 0, 'open_s2': 0,
                }
                for mid, fname, title in modules
            },
            'claims': [],
            'phase4': {
                'consecutive_failed_rounds': 0,
                'cumulative_s2': 0,
                'sampled_item_ids': [],
                'rounds': [],
            },
        }
        state['phases']['0']['status'] = 'done'
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)

    print(f'Wrote {json_path} ({os.path.getsize(json_path):,} bytes) and {md_path}')
    print('Summary:', json.dumps(s, indent=2))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

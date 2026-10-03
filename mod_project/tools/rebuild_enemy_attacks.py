import os
import struct
import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
TABLES_DIR = os.path.join(BASE_DIR, 'data_tables')
GAME_SUMMON_PCK = os.path.join(os.path.dirname(BASE_DIR), 'DungeonTravelers2-2_EN', 'Data', 'ENG', 'Summon', 'Summon.pck')

AILMENT_NAMES = {
    113: 'Poison', 114: 'Freeze', 115: 'Paralysis', 116: 'Sleep', 117: 'Silence',
    118: 'Stun', 119: 'Instant Death', 120: 'Slow', 121: 'Blind', 122: 'Charm',
    161: 'DEF Down', 162: 'ATK Down', 166: 'RES Down', 168: 'AGI Down', 173: 'AGI Up',
    70: 'Guaranteed Crit', 71: 'Extra Sleep Damage', 74: 'Dispel Buffs',
    75: 'HP Drain', 76: 'TP Drain', 54: 'Delay Turn', 55: 'Guaranteed Hit',
    90: 'Critical', 97: 'Accuracy Penalty', 138: 'Fire Res Down'
}

HIT_MAP = {
    91: '8 hits',
    92: '2-4 hits',
    93: '5 hits',
    94: '0-8 hits',
    95: '1-5 hits',
    96: '3-5 hits',
    98: '7 hits',
    100: '4-7 hits',
    89: '2-5 hits'
}

def get_summon_skill_ids():
    summon_arc = PckArchive(GAME_SUMMON_PCK)
    summon_skill_ids = set()
    for s_fn, data in summon_arc.files:
        pack_idx = data.find(b'Pack                ')
        if pack_idx == -1: continue
        file_count = struct.unpack('<I', data[pack_idx+24:pack_idx+28])[0]
        entry_pos = pack_idx + 28
        fns = []
        for i in range(file_count):
            fn_rel = struct.unpack('<I', data[0x18 + i*4:0x18 + (i+1)*4])[0]
            fns.append(data[0x18 + fn_rel:data.find(b'\x00', 0x18 + fn_rel)].decode('latin-1'))
        for i in range(file_count):
            off, sz = struct.unpack('<II', data[entry_pos:entry_pos+8])
            if fns[i] == 'SummonData.bin':
                sd = data[off:off+sz]
                for o in range(64, min(len(sd), 140), 4):
                    sk_id = struct.unpack('<I', sd[o:o+4])[0]
                    if 0 < sk_id < 3000:
                        summon_skill_ids.add(sk_id)
            entry_pos += 8
    return sorted(summon_skill_ids)

def format_enemy_attack(name, h_line, pwr, ail_id, ail_rate, orig_lines):
    if name == 'Take Break':
        return f"{h_line}\nSkips turn (Monster break)."
        
    lines = [h_line]
    
    # Determine damage type label
    dmg_type = 'damage'
    if 'Slash' in h_line: dmg_type = 'Slash damage'
    elif 'Stab' in h_line: dmg_type = 'Stab damage'
    elif 'Bash' in h_line: dmg_type = 'Bash damage'
    elif 'Fire' in h_line: dmg_type = 'Fire magic damage'
    elif 'Water' in h_line: dmg_type = 'Water magic damage'
    elif 'Wind' in h_line: dmg_type = 'Wind magic damage'
    elif 'Earth' in h_line: dmg_type = 'Earth magic damage'
    elif 'Lightning' in h_line: dmg_type = 'Lightning magic damage'
    elif 'Weapon\'s' in h_line: dmg_type = 'Weapon damage'
    
    pwr_pct = int(round(pwr * 100)) if 0 < pwr < 10.0 else 100
    
    # Check multi-hit
    hit_str = ''
    if ail_id in HIT_MAP:
        hit_str = f" ({HIT_MAP[ail_id]})"
    elif 'Two Arrows' in name:
        hit_str = " (2 hits)"
    elif 'Three Arrows' in name:
        hit_str = " (3 hits)"
        
    if name == 'Attack':
        if ail_id in AILMENT_NAMES and 0 < ail_rate <= 1.0:
            lines.append(f"Regular physical attack (ATK {pwr_pct}%).")
            lines.append(f"Inflicts {AILMENT_NAMES[ail_id]} ({int(round(ail_rate*100))}% chance).")
        else:
            lines.append(f"Regular physical attack (ATK {pwr_pct}%).")
        return '\n'.join(lines)
        
    if 'Heal' in name:
        lines.append(f"Restore HP (Spell Power {pwr_pct}%).")
        return '\n'.join(lines)
        
    # Attack with ailment / special
    if ail_id == 55: # Guaranteed hit
        lines.append(f"{dmg_type} (ATK {pwr_pct}%).")
        lines.append("100% Hit Rate (guaranteed hit).")
    elif ail_id == 97 or 'Two Arrows' in name or 'Three Arrows' in name:
        lines.append(f"{dmg_type} (ATK {pwr_pct}%){hit_str}.")
        lines.append("Reduced accuracy.")
    elif ail_id == 54: # Knockback / Turn delay
        lines.append(f"{dmg_type} (ATK {pwr_pct}%).")
        lines.append(f"Delays target's turn ({int(round(ail_rate*100))}% chance).")
    elif ail_id in AILMENT_NAMES and 0 < ail_rate <= 1.0:
        lines.append(f"{dmg_type} (ATK {pwr_pct}%){hit_str}.")
        lines.append(f"Inflicts {AILMENT_NAMES[ail_id]} ({int(round(ail_rate*100))}% chance).")
    elif 'Target: Self' in h_line:
        clean_flavor = ' '.join(orig_lines[1:])[:75] if len(orig_lines) > 1 else "Self buff / special effect."
        lines.append(clean_flavor.replace('~', '-'))
    else:
        lines.append(f"{dmg_type} (ATK {pwr_pct}%){hit_str}.")
        if len(orig_lines) > 2 and len(orig_lines[2]) <= 80:
            lines.append(orig_lines[2].replace('~', '-'))
            
    # Guarantee max 3 lines
    return '\n'.join(lines[:3])

def generate_table():
    print("=== Generating enemy_attacks.xlsx for All Monster & Summon Skills ===")
    summon_ids = set(get_summon_skill_ids())
    print(f"Loaded {len(summon_ids)} distinct skills used by Summons.")
    
    enemy_arc = PckArchive(os.path.join(BACKUP_DIR, 'EnemyAttackData.pck'))
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "EnemyAttacks"
    ws.append(["Filename", "SkillID", "Name", "HeaderLine", "Vanilla_Desc", "Modded_Desc", "IsSummon", "Status"])
    
    errors = []
    count = 0
    
    for fn, b in enemy_arc.files:
        p0 = struct.unpack('<Q', b[8:16])[0]
        p3 = struct.unpack('<Q', b[32:40])[0]
        name = b[p0:b.find(b'\x00', p0)].decode('latin-1')
        orig_desc = b[p3:b.find(b'\x00', p3)].decode('latin-1')
        orig_lines = orig_desc.split('\n')
        h_line = orig_lines[0] if orig_lines else "Target: Single / Type: ? / Range: ?"
        
        sk_id = struct.unpack('<I', b[0:4])[0]
        is_summon = "Yes" if sk_id in summon_ids else "No"
        
        pwr = struct.unpack('<f', b[0x44:0x48])[0]
        ail_id = struct.unpack('<i', b[0x58:0x5c])[0]
        ail_rate = struct.unpack('<f', b[0x5c:0x60])[0]
        
        mod_desc = format_enemy_attack(name, h_line, pwr, ail_id, ail_rate, orig_lines)
        
        # Validation checks
        flines = mod_desc.split('\n')
        if len(flines) > 3:
            errors.append(f"Row {fn} ({name}): >3 lines ({len(flines)})")
        for l in flines:
            if len(l) > 85:
                errors.append(f"Row {fn} ({name}): >85 chars ({len(l)}): '{l}'")
            if '~' in l:
                errors.append(f"Row {fn} ({name}): contains invalid tilde (~)")
                
        ws.append([fn, sk_id, name, h_line, orig_desc, mod_desc, is_summon, "Approved"])
        count += 1
        
    out_path = os.path.join(TABLES_DIR, 'enemy_attacks.xlsx')
    wb.save(out_path)
    print(f"Successfully saved all {count} skills to: {out_path}")
    print(f"Validation Errors: {len(errors)}")
    for err in errors:
        print(f"  [ERROR] {err}")
    return len(errors) == 0

if __name__ == '__main__':
    generate_table()

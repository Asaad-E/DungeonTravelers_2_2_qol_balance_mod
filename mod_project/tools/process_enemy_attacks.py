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
    161: 'DEF Down', 162: 'ATK Down', 166: 'RES Down', 168: 'AGI Down',
    70: 'Guaranteed Crit', 71: 'Extra Sleep Damage', 74: 'Dispel Buffs',
    75: 'HP Absorb', 76: 'TP Absorb', 54: 'Delay Turn', 55: 'Guaranteed Hit',
    90: 'Critical', 92: 'Multi-Hit', 97: 'Accuracy Penalty', 138: 'Fire Res Down'
}

def analyze_summon_skills():
    summon_arc = PckArchive(GAME_SUMMON_PCK)
    enemy_arc = PckArchive(os.path.join(BACKUP_DIR, 'EnemyAttackData.pck'))
    enemy_dict = dict(enemy_arc.files)

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

    print(f"Total distinct summon skills found: {len(summon_skill_ids)}")
    return sorted(summon_skill_ids), enemy_dict

if __name__ == '__main__':
    analyze_summon_skills()

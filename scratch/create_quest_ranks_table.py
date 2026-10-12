import openpyxl
import struct
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backup_path = os.path.join(BASE_DIR, 'backups', 'QuestRankData.pck')
target_xlsx = os.path.join(BASE_DIR, 'data_tables', 'quest_ranks.xlsx')

arc = PckArchive(backup_path)

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'QuestRanks'

ws.append(['Rank', 'Trust_Points', 'Vanilla_Type', 'Vanilla_Reward', 'Modded_Reward', 'Status', 'Notes'])

for fn, d in arc.files:
    rank, pts, unk2, unk3, rew_type, rew_val = struct.unpack('<IIIIii', d[:24])
    van_text = d[40:d.find(b'\x00', 40)].decode('latin-1', errors='ignore')
    
    mod_text = van_text
    notes = ''
    if rank == 2:
        mod_text = "Your bag's storage capacity has increased by 10."
        notes = "Chapter 1 early bag boost: 30 to 40 slots"
    elif rank == 8:
        mod_text = "Your bag's storage capacity has increased by 10."
        notes = "Midgame max bag boost: 40 to 50 slots (engine cap)"
    elif rank == 11:
        mod_text = 'You got 50,000 gold.'
        notes = 'Replaced dead bag reward (+0 slots) with 50,000 Gold'
    elif rank == 15:
        mod_text = 'You got 100,000 gold.'
        notes = 'Replaced dead bag reward (+0 slots) with 100,000 Gold'
    elif rank == 20:
        mod_text = 'You got 500,000 gold.'
        notes = 'Replaced dead bag reward (+0 slots) with 500,000 Gold for Max Rank'
        
    ws.append([rank, pts, rew_type, van_text, mod_text, 'Approved', notes])

wb.save(target_xlsx)
print(f'Successfully created {target_xlsx} with 20 quest ranks!')

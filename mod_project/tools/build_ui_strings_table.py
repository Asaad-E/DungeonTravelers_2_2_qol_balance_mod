import os
import sys
sys.path.insert(0, '.')
import pandas as pd

ui_data = [
    {
        'File_Name': 'StringData_0216.bin',
        'String_ID': 216,
        'Vanilla_Text': 'The strength of Sealbook Summon monsters is affected by the party.',
        'Modified_Text': 'Sealbook Summon level and stats scale with party level and equipment.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'StringData_0251.bin',
        'String_ID': 251,
        'Vanilla_Text': "Reset a teammate's level to a specific point.",
        'Modified_Text': 'Reset level to reallocate SP and earn permanent stat bonus points.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'StringData_0312.bin',
        'String_ID': 312,
        'Vanilla_Text': "Your party skills grow in power based on the number of awards you've earned.",
        'Modified_Text': 'Party skills increase in efficacy based on the number of awards earned.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'StringData_0452.bin',
        'String_ID': 452,
        'Vanilla_Text': 'Combine a piece of equipment and a Sealbook to add an enchantment.,',
        'Modified_Text': 'Forge equipment with Sealbooks to increase +level and add enchants.',
        'Status': 'Approved'
    }
]

df = pd.DataFrame(ui_data)
out_path = r'mod_project\data_tables\ui_strings.xlsx'
with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='UIStrings', index=False)

print(f"Successfully generated {out_path} with {len(df)} validated UI strings!")

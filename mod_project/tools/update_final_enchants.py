import sys
sys.path.insert(0, '.')
import pandas as pd

excel_path = r'mod_project\data_tables\enchants.xlsx'
df = pd.read_excel(excel_path)

upgrades = {
    # Race damage taken reductions
    'EnchantData_0227.bin': 'Damage from Demons -5%',
    'EnchantData_0228.bin': 'Damage from Demons -10%',
    'EnchantData_0229.bin': 'Damage from Apparitions -5%',
    'EnchantData_0230.bin': 'Damage from Apparitions -10%',
    'EnchantData_0231.bin': 'Damage from Magic Beings -5%',
    'EnchantData_0232.bin': 'Damage from Magic Beings -10%',
    'EnchantData_0233.bin': 'Damage from Humans -5%',
    'EnchantData_0234.bin': 'Damage from Humans -10%',
    'EnchantData_0235.bin': 'Damage from Undead -5%',
    'EnchantData_0236.bin': 'Damage from Undead -10%',
    'EnchantData_0237.bin': 'Damage from Dragons -5%',
    'EnchantData_0238.bin': 'Damage from Dragons -10%',
    'EnchantData_0239.bin': 'Damage from Beasts -5%',
    'EnchantData_0240.bin': 'Damage from Beasts -10%',
    'EnchantData_0241.bin': 'Damage from Fruit -5%',
    'EnchantData_0242.bin': 'Damage from Fruit -10%',
    'EnchantData_0243.bin': 'Damage from Therians -5%',
    'EnchantData_0244.bin': 'Damage from Therians -10%',
    
    # Elemental both sides
    'EnchantData_0251.bin': 'Fire Attack for all allies & foes +25%',
    'EnchantData_0252.bin': 'Water Attack for all allies & foes +25%',
    'EnchantData_0253.bin': 'Wind Attack for all allies & foes +25%',
    'EnchantData_0254.bin': 'Earth Attack for all allies & foes +25%',
    'EnchantData_0255.bin': 'Lightning Attack for all allies & foes +25%',
    
    # Traps & Mimics
    'EnchantData_0269.bin': 'Trap Trigger Rate -50%',
    'EnchantData_0291.bin': 'Chest Mimic Appearance Rate +50%',
    
    # Support skill potency
    'EnchantData_0300.bin': 'Song Potency +20% (Carol/Chorale etc.)',
    'EnchantData_0301.bin': 'Song Potency +10%',
    'EnchantData_0302.bin': 'Dance Potency +20%',
    'EnchantData_0303.bin': 'Dance Potency +10%',
    'EnchantData_0304.bin': 'Doll Potency +20%',
    'EnchantData_0305.bin': 'Doll Potency +10%',
    
    # Attack status ailments
    'EnchantData_0153.bin': 'Normal attacks: Poison chance (20%)',
    'EnchantData_0154.bin': 'Normal attacks: Sleep chance (20%)',
    'EnchantData_0155.bin': 'Normal attacks: Silence chance (20%)',
    'EnchantData_0156.bin': 'Normal attacks: Freeze chance (20%)',
    'EnchantData_0157.bin': 'Normal attacks: Paralysis chance (20%)',
    'EnchantData_0158.bin': 'Normal attacks: Stun chance (20%)',
    'EnchantData_0159.bin': 'Normal attacks: Petrify chance (15%)',
    'EnchantData_0160.bin': 'Normal attacks: Instakill chance (15%)',
    'EnchantData_0165.bin': 'Normal attacks: Slow chance (15%)',
    'EnchantData_0197.bin': 'Normal attacks: High Instakill chance (50%)',
}

updated_count = 0
for fn, mod_desc in upgrades.items():
    idx = df[df['File_Name'] == fn].index
    if len(idx) > 0:
        df.loc[idx, 'Modded_Name'] = mod_desc
        df.loc[idx, 'Status'] = 'Approved'
        updated_count += 1
        print(f"Updated {fn} -> {mod_desc}")

df.to_excel(excel_path, index=False)
print(f"Total upgrades written: {updated_count}. Approved total: {len(df[df['Status'] == 'Approved'])}")

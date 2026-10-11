"""
Generates data_tables/qol_class_text.xlsx from backups/ClassData.pck.
Applies surgical QoL improvements to 9 key classes (Paladin, Berserker, Valkyrie, Sniper,
Kunoichi, Diva, Mistress, Etoile, Papillon) while keeping all other 40 classes untouched.
"""
import os
import sys
import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from tools.pck_handler import PckArchive, ClassDataHelper

BACKUP_PCK = os.path.join(BASE_DIR, 'backups', 'ClassData.pck')
OUT_XLSX = os.path.join(BASE_DIR, 'data_tables', 'qol_class_text.xlsx')

EDITED_CLASSES = {
    # 1: Paladin
    'ClassData_01.bin': (
        "Holy knights of the front line who protect their comrades by using themselves\n"
        "as human shields. Wielding one-handed weapons and heavy shields, they specialize\n"
        "in Cover and guard stances to withstand lethal single-target physical blows."
    ),
    # 2: Berserker
    'ClassData_02.bin': (
        "Short-range battle experts who excel at using two-handed swords and axes.\n"
        "They trade shields and turn speed for crushing physical blows that can cleave\n"
        "foes in a single strike. Devastating power tempered by heavy weapon recovery delay."
    ),
    # 3: Valkyrie
    'ClassData_03.bin': (
        "They have no superior when it comes to short-range fortitude. Wielding spears\n"
        "and swords, these war angels guard the front line with Circle Protection, shielding\n"
        "the entire party from physical assaults while executing swift counterattacks."
    ),
    # 9: Sniper
    'ClassData_09.bin': (
        "With their god-like speed, these long-range specialists pierce every target they set\n"
        "their eyes on. Master archers whose techniques require bows rather than firearms.\n"
        "They provide lethal precision, warning shots, and long-range covering fire."
    ),
    # 11: Kunoichi
    'ClassData_11.bin': (
        "Spies who utilize blazing speed to harass foes. Skilled in dual-wielding daggers and\n"
        "katanas, they use shadow clones to completely nullify physical attacks, alongside\n"
        "ranged shuriken strikes and debilitating status ninjutsu."
    ),
    # 23: Diva
    'ClassData_23.bin': (
        "Support class specializing in skills that boost the abilities of their comrades. With\n"
        "vocals that rattle the cosmos, their continuous songs replenish party TP, boost ATK,\n"
        "and accelerate chanting without consuming active turns once begun."
    ),
    # 24: Mistress (Alternativa A)
    'ClassData_24.bin': (
        "Hard workers who finally reached the status of master after extensive work as\n"
        "subordinate maids. Their trauma fuels a sadistic fighting style, wielding whips to\n"
        "punish foes with ranged status ailments, vicious counterattacks, and revival magic."
    ),
    # 25: Etoile
    'ClassData_25.bin': (
        "Admired by all as they soar across the battlefield. Even enemies are captivated\n"
        "by their ravishing dances. Once initiated, their continuous dances cripple enemy\n"
        "attack, speed, and accuracy, shifting the tempo of battle in your favor."
    ),
    # 30: Papillon
    'ClassData_30.bin': (
        "Using hand-fans proficiently as weapons, they are skilled in both short and long\n"
        "distance combat. Masters of turn delay, they boast unique skills, not least of which\n"
        "is an ultimate skill that turns a weakened enemy into... food?"
    ),
}

def generate():
    archive = PckArchive(BACKUP_PCK)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Classes'
    
    header = ['ID', 'Code', 'Filename', 'Class_Name', 'Vanilla_Desc', 'QoL_Desc', 'Edited', 'Max_Line_Len']
    ws.append(header)
    
    for idx, (fname, b) in enumerate(archive.files):
        data = ClassDataHelper.read_class(b)
        code = data.get('code', '')
        name = data.get('name', '')
        vanilla_desc = data.get('desc', '')
        
        if fname in EDITED_CLASSES:
            qol_desc = EDITED_CLASSES[fname]
            edited = 'Yes'
        else:
            qol_desc = vanilla_desc
            edited = 'No'
            
        max_len = max(len(l) for l in qol_desc.splitlines()) if qol_desc else 0
        ws.append([idx, code, fname, name, vanilla_desc, qol_desc, edited, max_len])

    wb.save(OUT_XLSX)
    print(f"Generated {OUT_XLSX} with {len(archive.files)} entries ({len(EDITED_CLASSES)} edited).")

if __name__ == '__main__':
    generate()

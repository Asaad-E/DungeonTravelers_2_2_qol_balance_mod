import os
import struct
import sys
sys.path.insert(0, os.path.abspath('mod_project/tools'))
import openpyxl
from pck_handler import PckArchive, JoinSkillHelper
from text_checks import joint_effects, JOINT_EFFECTS, JOINT_STYLES, JOINT_PLACE_RE

BACKUP_PATH = 'mod_project/backups/JoinSkillData.pck'
archive = PckArchive(BACKUP_PATH)

print("Mapping effect IDs in each joint skill:")
for fn, b in archive.files:
    skill = JoinSkillHelper.read_joint(b)
    effs = {i: v for i, v, _ in skill['effects']}
    eff_str = ', '.join(f'e{i}:{v:g}' for i, v in effs.items())
    print(f"{skill['name']:24} | TP: 1/{skill['tp_divisor']} | Pep: {skill['pep_cost']:2.0f} | {eff_str}")

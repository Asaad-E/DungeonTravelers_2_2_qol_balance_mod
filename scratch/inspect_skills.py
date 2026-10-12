import sys
import struct
sys.path.append('mod_project/tools')
from pck_handler import PckArchive, SkillHelper

tech_pck = PckArchive('mod_project/backups/TechniqueSkillData.pck')
print('TechniqueSkillData files count:', len(tech_pck.files))
magic_pck = PckArchive('mod_project/backups/MagicSkillData.pck')
print('MagicSkillData files count:', len(magic_pck.files))

print("\n--- SAMPLE TECHNIQUES ---")
for i in [0, 1, 2, 5, 10, 15, 20]:
    if i < len(tech_pck.files):
        fn, data = tech_pck.files[i]
        skill = SkillHelper.read_skill(data, 'Technique')
        print(f"Tech {i} ({fn}): {skill['name']} | max_lv={skill['max_lv']} | TP={skill['tp_prog']}")
        print(f"  Desc: {skill['desc'][:60]}")
        print(f"  LvUp: {skill['lvup'][:60]}")

print("\n--- SAMPLE MAGIC ---")
for i in [0, 1, 2, 5, 10, 15, 20]:
    if i < len(magic_pck.files):
        fn, data = magic_pck.files[i]
        skill = SkillHelper.read_skill(data, 'Magic')
        print(f"Magic {i} ({fn}): {skill['name']} | max_lv={skill['max_lv']} | TP={skill['tp_prog']}")
        print(f"  Desc: {skill['desc'][:60]}")
        print(f"  LvUp: {skill['lvup'][:60]}")

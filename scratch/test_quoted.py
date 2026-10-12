import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backup_dir = os.path.join(base_dir, 'backups')

tests = [
    ('Lesson.pck', 'BattleTeacher_04.adv.bin', 'This information is extremely important during battle, so I\nhighly suggest that you make use of it when battling against\nthreatening enemies.'),
    ('Lesson.pck', 'BattleTeacher_07.adv.bin', "Well, that was something of a brief lesson, but let's leave\nit here for today."),
    ('Lesson.pck', 'BattleTeacher_08.adv.bin', 'Precisely. Against certain monsters, raising your\nresistances can be considerably more effective than raising\nyour defense directly.'),
    ('Lesson.pck', 'BattleTeacher_09.adv.bin', 'Presents include gold, rare equipment, and even additional\nbag space.'),
    ('Lesson.pck', 'BattleTeacher_10.adv.bin', 'Party skills also grow stronger according to the number of\nawards you amass.'),
    ('Lesson.pck', 'BattleTeacher_11-12.adv.bin', 'Or, after certain level thresholds, you can choose to reset\nback to those specific threshold levels as opposed to level\n1.'),
    ('Lesson.pck', 'BattleTeacher_13.adv.bin', "Is that right...? There aren't many restaurants around these\nparts, so I've been frequenting it quite often."),
    ('Lesson.pck', 'BattleTeacher_Sp02.adv.bin', "Dark Aura debuffs enemies' stats when they inflict\nshort-range damage. No monsters are immune to such debuffs,\nso you can even use it in boss battles."),
    ('ShopBar.pck', 'Talk_Random04.adv.bin', "When hiring a merc, you can check their stats and skills,\nbut you obviously can't tell how they're going to behave."),
    ('ShopStore.pck', 'Talk_Random01.adv.bin', "Do you have Crois-sants and E-mer-gen-cy Ex-its in your\npos-ses-sion? They are es-sen-tial i-tems for rook-ie\nad-ventur-ers."),
    ('ShopStore.pck', 'Talk_Random11.adv.bin', "If you find your-self run-ning out of TP, then I\nre-com-mend you pur-chase Fair-y Ap-ples! They re-cov-er 50\nTP for the low price of 900 gold."),
]

for pck_name, fname, target in tests:
    arc = PckArchive(os.path.join(backup_dir, pck_name))
    for fn, b in arc.files:
        if fn == fname:
            q_target = f'"{target}"'
            idx = b.find(q_target.encode('ascii') + b'\x00')
            if idx != -1:
                print(f"[FOUND WITH QUOTES] {pck_name} -> {fname}: offset {idx}")
            else:
                print(f"[NOT FOUND EVEN WITH QUOTES] {pck_name} -> {fname}")

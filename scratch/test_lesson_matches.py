import sys
sys.path.insert(0, '.')
from mod_project.tools.pck_handler import PckArchive

arc = PckArchive('mod_project/backups/Lesson.pck')

tests = {
    'BattleTeacher_04.adv.bin': 'This information is extremely important during battle, so I highly suggest that you make use of it when battling against threatening enemies.',
    'BattleTeacher_07.adv.bin': "Well, that was something of a brief lesson, but let's leave it here for today.",
    'BattleTeacher_08.adv.bin': 'Precisely. Against certain monsters, raising your resistances can be considerably more effective than raising your defense directly.',
    'BattleTeacher_09.adv.bin': 'Presents include gold, rare equipment, and even additional bag space.',
    'BattleTeacher_13.adv.bin': "Is that right...? There aren't many restaurants around these parts, so I've been frequenting it quite often.",
    'BattleTeacher_Sp02.adv.bin': "Dark Aura debuffs enemies' stats when they inflict short-range damage. No monsters are immune to such debuffs, so you can even use it in boss battles."
}

for fn, data in arc.files:
    if fn in tests:
        target = tests[fn]
        found = False
        for s in data.split(b'\x00'):
            decoded = s.decode('latin-1', errors='replace')
            if target.replace('\n', ' ') in decoded.replace('\n', ' '):
                print(f"{fn}: FOUND! Raw newline string:\n{repr(decoded)}\n")
                found = True
                break
        if not found:
            print(f"{fn}: NOT FOUND!")

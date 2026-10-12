import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from pck_handler import PckArchive

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backup_dir = os.path.join(base_dir, 'backups')

def dump_strings(pck_name, file_name, keywords):
    arc = PckArchive(os.path.join(backup_dir, pck_name))
    for fn, b in arc.files:
        if fn == file_name:
            print(f"=== {pck_name} -> {fn} ===")
            matches = [m.decode('latin-1') for m in re.findall(b'[\x20-\x7E\r\n]{15,}', b)]
            for m in matches:
                if any(k.lower() in m.lower() for k in keywords):
                    print("  FOUND:", repr(m))

print("1. Lesson files:")
dump_strings('Lesson.pck', 'BattleTeacher_04.adv.bin', ['important', 'information', 'delay', 'order', 'turn'])
dump_strings('Lesson.pck', 'BattleTeacher_07.adv.bin', ['lesson', 'brief', 'today', 'range'])
dump_strings('Lesson.pck', 'BattleTeacher_08.adv.bin', ['precisely', 'resistance', 'defense'])
dump_strings('Lesson.pck', 'BattleTeacher_10.adv.bin', ['party skill', 'award', 'amass'])
dump_strings('Lesson.pck', 'BattleTeacher_11-12.adv.bin', ['threshold', 'reset', 'level 1'])
dump_strings('Lesson.pck', 'BattleTeacher_13.adv.bin', ['restaurant', 'frequenting', 'often'])
dump_strings('Lesson.pck', 'BattleTeacher_Sp02.adv.bin', ['dark aura', 'debuff', 'short-range'])

print("\n2. Shop files:")
dump_strings('ShopBar.pck', 'Talk_Random04.adv.bin', ['merc', 'hiring', 'behave'])
# Let's search all files in ShopBar.pck for 'merc' or 'hiring'
arc_bar = PckArchive(os.path.join(backup_dir, 'ShopBar.pck'))
print("Scanning all ShopBar files for 'merc' / 'hiring' / 'behave':")
for fn, b in arc_bar.files:
    matches = [m.decode('latin-1') for m in re.findall(b'[\x20-\x7E\r\n]{15,}', b)]
    for m in matches:
        if any(k in m.lower() for k in ['merc', 'hiring', 'behave', 'check their stats']):
            print(f"  {fn}: {repr(m)}")

print("\n3. ShopStore files:")
arc_ss = PckArchive(os.path.join(backup_dir, 'ShopStore.pck'))
print("Scanning all ShopStore files for 'Crois-sant' / 'Fair-y Ap-ple' / 'TP':")
for fn, b in arc_ss.files:
    matches = [m.decode('latin-1') for m in re.findall(b'[\x20-\x7E\r\n]{15,}', b)]
    for m in matches:
        if any(k in m.lower() for k in ['crois', 'fair-y', 'apple', '900 gold', 'flashlight']):
            print(f"  {fn}: {repr(m)}")

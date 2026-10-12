import sys
import re
sys.path.append('mod_project/tools')
from pck_handler import PckArchive

def inspect_dialogues(pck_path, target_names):
    arc = PckArchive(pck_path)
    for fn, data in arc.files:
        strs = [s.decode('latin1', 'ignore') for s in re.findall(b'[\x20-\x7e\n\r]{4,}', data)]
        for idx, s in enumerate(strs):
            for t in target_names:
                if t.lower() in s.lower():
                    print(f"[{pck_path} -> {fn}] Target '{t}' in string: {s}")
                    # print next few strings
                    for j in range(max(0, idx-2), min(len(strs), idx+5)):
                        print(f"   [{j}] {strs[j]}")

print("=== RIN-RIN ===")
inspect_dialogues('DungeonTravelers2-2_EN/Data/ENG/Script/ShopStore.pck', ['Rin-Rin', 'RinRin'])
inspect_dialogues('DungeonTravelers2-2_EN/Data/ENG/Script/ShopQuest.pck', ['Rin-Rin'])

print("\n=== MARY CONDUCTOR ===")
inspect_dialogues('DungeonTravelers2-2_EN/Data/ENG/Script/ShopPeddler.pck', ['Mary', 'Conductor'])
inspect_dialogues('DungeonTravelers2-2_EN/Data/ENG/Script/ShopQuest.pck', ['Mary'])
inspect_dialogues('DungeonTravelers2-2_EN/Data/ENG/Script/evt02.pck', ['Mary Conductor', 'Rin-Rin'])

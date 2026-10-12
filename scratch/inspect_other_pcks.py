import sys
sys.path.insert(0, '.')
from mod_project.tools.pck_handler import PckArchive

for pck in ['ShopStore.pck', 'CommandData.pck', 'KeyHelpData.pck', 'IntroductionData.pck']:
    try:
        path = f'DungeonTravelers2-2_EN/Data/ENG/Script/{pck}'
        import os
        if not os.path.exists(path):
            path = f'DungeonTravelers2-2_EN/Data/ENG/Parameter/{pck}'
        arc = PckArchive(path)
        print(f"\n=== {pck} ({len(arc.files)} files) ===")
        found = 0
        for fn, data in arc.files:
            for s in data.split(b'\x00'):
                if len(s) > 10 and all(32 <= c <= 126 for c in s[:10]):
                    print(f"  {fn}: {s.decode('ascii', errors='replace')[:70]}")
                    found += 1
                    if found >= 5:
                        break
            if found >= 5:
                break
    except Exception as e:
        print(f"Error {pck}: {e}")

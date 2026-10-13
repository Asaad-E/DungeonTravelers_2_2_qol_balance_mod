"""One-off edit (2026-10-13): the two player READMEs say what to do when the game is updated while the mod is in."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OLD = """Saves
-----
"""
NEW = """If the game is updated
----------------------
An update or a repair of the game puts its own files back over the mod. The Install and Uninstall
.bat notice it and change nothing, since the copies in "DT22_Mod\\backup" then belong to the older
game. Delete the folder "DT22_Mod\\backup" and the file "DT22_Mod\\installed.txt", have the launcher
check the files of the game, and run the Install .bat again.

Saves
-----
"""

for name in ('README_Balance.txt', 'README_QoL.txt'):
    path = os.path.join(ROOT, 'installer', name)
    with open(path, encoding='utf-8') as f:
        text = f.read()
    assert text.count(OLD) == 1
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text.replace(OLD, NEW))
    print(name)

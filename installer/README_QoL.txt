Dungeon Travelers 2-2 (PC, English) - QoL mod
=============================================

What it is
----------
A text-only mod. It changes no game value: damage, costs, chances, prices and drops are exactly
those of the original game. It only makes the game tell you what it already does.

What you will see
-----------------
* Skills: the box under each skill lists its real values level by level
  (Pwr: 90 -> 120 -> ... , TP Cost, Speed, chances of ailments). The first line names how hard
  the skill hits (negligible / minor / moderate / major / severe / tremendous) and the chance
  of its ailment, e.g. "May freeze (20-50%)".
* Unique skills: the values of levels 1-9 and of the Crown.
* Items: the original sentence, then what the item does: "(HP +30, TP +40)".
* Enchantments: the figure in place of UP / MiniUP: "DEX +10%", "Fire resistance +20", "Recover 2 TP every turn".
  They show on equipment and on sealbooks.
* Weapons: the title shows the speed rank with its multiplier: "Speed E+ (2.45x)".
* Summons and enemy abilities: exact chances and amounts on the data line
  ("Target: Single / Type: Stab / Range: Long / Poison: 30%").
* Party skills: the most each bonus can reach. Joint skills: exact chances and amounts.
* Ice cream and ramen: the share of HP and TP a meal restores.
* A handful of sentences of the original that stated a wrong figure are corrected.

Jokes and flavour text are kept. Some sentences were shortened so that the added data fits
on one line.

Install
-------
This archive holds no file of the game: only the differences, and a script that applies them to
your own copy.

1. Close the game. It must be the original game, with no other mod installed.
2. Unpack this archive into the folder of the game: the one that holds the game's .exe and its
   folder "Data". You now have there "Install_QoL.bat", "Uninstall_DT22_Mod.bat" and a folder
   "DT22_Mod".
3. Run "Install_QoL.bat" (double click).

It checks every file it is about to change, keeps a copy of each original in "DT22_Mod\backup",
and then changes them. If a file is not the original one it says which and changes nothing.
The window ends with "Done: ..." when all went well.

Uninstall
---------
Run "Uninstall_DT22_Mod.bat". Every file goes back as it was.

To change from one variant of the mod to the other, unpack the other archive into the same
folder and run its Install .bat: there is no need to uninstall first.

If the game is updated
----------------------
An update or a repair of the game puts its own files back over the mod. The Install and Uninstall
.bat notice it and change nothing, since the copies in "DT22_Mod\backup" then belong to the older
game. Delete the folder "DT22_Mod\backup" and the file "DT22_Mod\installed.txt", have the launcher
check the files of the game, and run the Install .bat again.

Saves
-----
Saves are not touched and stay compatible both ways.

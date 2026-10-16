Dungeon Travelers 2-2 (PC, English) - Balance mod
=================================================

What it is
----------
A mod that changes values of the game so that every class, weapon and skill is worth using, and
that tells you, as the QoL mod does, what the game really does. It answers the complaints of the
Japanese community and of the English guide of the game, one by one.

What changes
------------
* Catching up: a member below the level of the enemies gains much more EXP, so a character who
  joins late or stayed in the base is back with the party in a few battles. The Crown costs far
  fewer battles.
* Classes that lagged behind (the Doll Master line, the Kunoichi, the Mistress, the Magical
  Princess, the Treasure Hunter, the Trickster) hit harder or pay less TP.
* Skills nobody used (chance skills, drains, single buffs, several support skills) are worth
  their TP.
* Whips, daggers, guns and plain attacks are stronger; two-handed weapons a little weaker.
* Ailments and debuffs land more often and weigh more; most story bosses can be poisoned, slowed
  or silenced. No boss can be locked out of its turns.
* Heal and Circle Heal also cure poison.
* Common enemies of the last dungeons resist physical damage a little less.
* Quests pay more gold. Seven rare drops fall a little more often, and four strong common enemies
  can be robbed.
* The bosses the stronger party made too easy hold more HP, the last boss of the story among them;
  the Queen of Darkness also defends better, and Demon God Fried hits harder instead.
* The unique skills of the girls that did little do more (Third Eye Wide, Arcane Shield, Alter
  Fate, Tranquil Song). Lizerietta has a new one, No Miracles Needed: she may hold on with 1 HP
  when a hit would fell her.
* Concentrate works: the game left it without effect.
* A fruit gives a fifth more TP, so a party without a Maid can go on with a full bag.
* The dances of the Etoile weigh more; the party skill Eccentrics gives AGI; Natalia, the
  mercenary, heals more.
* Every level from 31 to 70 gives one more skill point.
* Provoke draws more attacks as it is raised; Magic Barrier cuts more magic damage; First Grid
  comes up more often; the Kunoichi may use her Stings and Phoenix with a dagger or a projectile,
  and her Barrage strikes twice more often (30% at its first level, 50% at its last).
* Three grand sealbooks of the postgame (Melek Taus, Genbu, Murasaki Shikibu) carry a second
  enchantment. One postgame superboss no longer opens with a spell that can fell the party.
* The party buffs of the Enchantress and the Sage (Circle Brave, Circle Protect, Sun Veil) are
  larger and, with Accelerator, chanted much faster. Accelerator also gives more speed and lasts a
  turn longer, and Prism Dawn hits harder. Ecstasy gives twice as much.
* Power Charge makes the next blow stronger than before (its box shows the real multiple), the
  Shadow Clone of the Kunoichi lasts a turn longer, and the Oracles doll hits much harder.
* The Magical Princess stays transformed longer and Magical Change gives more; Magical Spark costs
  less TP. The Soul Eater of the Soul Summoner costs less and hits harder.
* The Witch grows a little less INT, and the five first spells of the Magic User hit a little less
  at their higher levels: her strong spells are now her best tools.
* The Bathroom Slippers, the reward of quest rank 3, give Double EXP in the place of their
  physical defense.
* The wandering blacksmith shows up more often in every dungeon.
* The buff of a meal lasts more than twice as many steps, enough to carry it into a few battles.
  So does any buff or lowered stat a girl walks out of a battle with; poison and the other
  ailments wear off as before.

Every skill, item and enchantment shows its new figures in the game.

Install
-------
This archive holds no file of the game: only the differences, and a script that applies them to
your own copy.

1. Close the game. It must be the original game, with no other mod installed.
2. Unpack this archive into the folder of the game: the one that holds the game's .exe and its
   folder "Data". You now have there "Install_Balance.bat", "Uninstall_DT22_Mod.bat" and a folder
   "DT22_Mod".
3. Run "Install_Balance.bat" (double click).

It checks every file it is about to change, keeps a copy of each original in "DT22_Mod\backup",
and then changes them. In the large files of the dungeons it changes a few bytes in place and
keeps the list of them instead of a copy. It also changes 20 bytes of the program (the EXP by level gap,
the Crown, the chance of Arcane Shield, the passive Concentrate and how long a buff lasts
while you walk) in every .exe of the
folder that is the game. If a file is not the original one it says which and changes nothing.
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

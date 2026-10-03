import os
import sys
sys.path.insert(0, '.')
import pandas as pd
import openpyxl

classes_data = [
    # Base Classes (5)
    {
        'File_Name': 'ClassData_00.bin',
        'Class_Code': 'FT',
        'Class_Name': 'Fighter',
        'Vanilla_Desc': 'With high physical strength and extraordinary stamina, these soldiers can wield \na variety of short-range weapons. They act as vanguards who rout their foes\nwhilst also shielding their comrades from attack.',
        'Modified_Desc': 'Role: Physical Vanguard / Tank | Row: Front | Weapons: 1H Sword, 2H Sword, Axe\nStats: High HP / DEF / ATK | Key Skills: War Cry, Provoke, Defender\nVanguard who shields allies, draws single-target aggro, and buffs party ATK.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_01.bin',
        'Class_Code': 'PL',
        'Class_Name': 'Paladin',
        'Vanilla_Desc': 'Holy knights of the front line who protect their comrades by using themselves \nas human shields. They excel in defense and can handle skills which provide even \nmore stability. Their purpose is to protect allies rather than defeat enemies.',
        'Modified_Desc': 'Role: Main Shield Tank | Row: Front | Weapons: 1H Sword, Spear, Heavy Shield\nStats: Top DEF / RES / HP | Key Skills: Cover, Parry, Daedalus Attack, Holy Shield\nAbsorbs physical strikes for wounded allies and neutralizes lethal enemy blows.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_02.bin',
        'Class_Code': 'BE',
        'Class_Name': 'Berserker',
        'Vanilla_Desc': 'Short-range battle experts who excel at using two-handed swords and axes. \nThey care little for weak attacks; instead, they obliterate enemies with a single \npowerful blow. An absolute must-have for an attack-focused party.',
        'Modified_Desc': 'Role: Heavy Physical DPS / Bruiser | Row: Front | Weapons: 2H Sword, 2H Axe\nStats: Massive ATK / HP | Key Skills: Berserk, Moon Drop, Blood Drain, Bone Crusher\nTrades defenses to unleash colossal single-target and multi-target devastation.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_03.bin',
        'Class_Code': 'VL',
        'Class_Name': 'Valkyrie',
        'Vanilla_Desc': 'They have no superior when it comes to short-range fortitude. With their immense \nstrength and beauty, they are oft likened to war angels leading armies into battle.\nTheir strong counterattack as they defend their allies seals the victory.',
        'Modified_Desc': 'Role: Vanguard Counter Fortress | Row: Front | Weapons: Spear, 1H Sword, Shield\nStats: Top DEF / HP / ATK | Key Skills: Cross Counter, Daedalus, Frost Slash, Aegis\nInvulnerable defensive bulwark that retaliates against all incoming strikes.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_04.bin',
        'Class_Code': 'SA',
        'Class_Name': 'Samurai',
        'Vanilla_Desc': 'Swordswomen who inflict deadly slash damage with each swing. A single hit from \none of their masterful skills can slice a foe in half. They also show great technical \nnous with their ability to dodge enemy strikes before mounting a swift counterattack.',
        'Modified_Desc': 'Role: Master Slash Duelist | Row: Front | Weapons: Katana, 2H Sword\nStats: Top ATK / DEX / AGI | Key Skills: Swallow Return, Helm Splitter, Hissatsu\nSpecializes in armor-piercing critical slash strikes and lethal counter stances.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_05.bin',
        'Class_Code': 'DL',
        'Class_Name': 'Dark Lord',
        'Vanilla_Desc': 'Drawing power from the darkness, these battle goddesses will not stop until they \nhave wholly consumed the lives and spirits of their opponents. The merciless blows \ndelivered by these jet-black soldiers leave their enemies with nothing.',
        'Modified_Desc': 'Role: Dark Drain Behemoth | Row: Front | Weapons: 2H Sword, 2H Axe\nStats: Supreme ATK / HP | Key Skills: Dark Blade, Drain, Megaton Press, Blood Pact\nCrushes enemy ranks with darkness-imbued physical brutality and massive HP drain.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_06.bin',
        'Class_Code': 'SC',
        'Class_Name': 'Scout',
        'Vanilla_Desc': 'Using nimble body movements, they can create opportunities to not only attack, but \nalso steal money. Their strength lies in how they can change battle styles depending \non the situation, as they are skilled in both shortsword and bow techniques.',
        'Modified_Desc': 'Role: Agile Physical Support / Thief | Row: Front/Back | Weapons: Dagger, Bow\nStats: Top AGI / DEX | Key Skills: Steal, Evade, Warning Shot, Shadow Stitch\nStrikes first with rapid attacks, steals items/gold, and disrupts formations.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_07.bin',
        'Class_Code': 'AR',
        'Class_Name': 'Archer',
        'Vanilla_Desc': 'Archers, adept at providing support from long distances. They attack with great \naccuracy and can inflict various status ailments upon their targets. When faced \nwith numerous adversaries, they can blacken the skies with a shower of arrows.',
        'Modified_Desc': 'Role: Long-Range Physical Sniper | Row: Back | Weapons: Bow\nStats: High DEX / ATK | Key Skills: Arrow Rain, Million Strike, Warning Shot\nRains arrows from safe backline distance with pinpoint accuracy and critical hits.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_08.bin',
        'Class_Code': 'AS',
        'Class_Name': 'Assassin',
        'Vanilla_Desc': 'Shortsword users who employ agility to trick their foes, sneaking behind them to \nstrike critical hits. Can both lead the attack and provide support by inflicting various \nstatus ailments. Their sharp strikes will occasionally dispatch an enemy in one hit.',
        'Modified_Desc': 'Role: Critical Infiltrator / Ailment DPS | Row: Front | Weapons: Dagger, Shortsword\nStats: Top AGI / DEX | Key Skills: Shadow Stitch, Sneak Attack, Assassinate\nStrikes vital points with lethal critical hits, high evade, and instant kill chances.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_09.bin',
        'Class_Code': 'SN',
        'Class_Name': 'Sniper',
        'Vanilla_Desc': 'With their god-like speed, these long-range specialists pierce every target they set \ntheir eyes on. Their ultimate strikes are lethal to foes. Can use both warning shots \nand covering fire to provide support from a distance.',
        'Modified_Desc': 'Role: Long-Range Executioner | Row: Back | Weapons: Bow\nStats: Supreme DEX / AGI | Key Skills: Covering Fire, Warning Shot, Million Strike\nEliminates high-priority targets from safety with perfect accuracy and lethal crits.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_10.bin',
        'Class_Code': 'TH',
        'Class_Name': 'Treasure Hunter',
        'Vanilla_Desc': "Able to wield a variety of weapons including shortswords, whips, and bows, as well \nas steal treasure from enemies. Using their trained judgement, they can also expertly \nmanage and identify inventory. Treasurers who serve to enrich the party's wallet.",
        'Modified_Desc': 'Role: Dungeon Fortune Master | Row: Front/Back | Weapons: Dagger, Bow, Whip\nStats: High AGI / DEX / LUK | Key Skills: Eye of Truth, Steal, Danger Detect\nMaximizes party item drop rates, detects dungeon traps, and identifies rare relics.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_11.bin',
        'Class_Code': 'KN',
        'Class_Name': 'Kunoichi',
        'Vanilla_Desc': 'Spies who utilize their blazing speed to battle opponents. They use shadow clones \nto nullify enemy attacks, and sometimes fight with a sword in each hand. In addition \nto far-range shuriken strikes, they are also skilled in a multitude of martial arts.',
        'Modified_Desc': 'Role: Shadow Striker / Dual Wielder | Row: Front | Weapons: Katana, Dagger, Shuriken\nStats: Supreme AGI / DEX | Key Skills: Dual Wield, Shadow Clone, Cicada Shell, Stun\nDual-wields blades with blinding speed, nullifying attacks with shadow decoys.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_12.bin',
        'Class_Code': 'MU',
        'Class_Name': 'Magic User',
        'Vanilla_Desc': 'A basic magician type who can use all general elements of magic. Their ability to \nreplenish HP with Heal makes them a necessary member of any party.',
        'Modified_Desc': 'Role: Elemental Magic Nuker / Healer | Row: Back | Weapons: Staff\nStats: High INT / RES | Key Spells: Fire/Water/Wind/Earth/Lightning Spells, Heal\nExploits 5 elemental weaknesses from the back row and provides single-target healing.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_13.bin',
        'Class_Code': 'SO',
        'Class_Name': 'Sorceress',
        'Vanilla_Desc': 'Adept at magic attacks which cover a wide area. Their low defense can be \na problem, but they provide stellar support with extraordinarily powerful magic. \nCapable of either dabbling in multiple elements or mastering one in particular.',
        'Modified_Desc': 'Role: Area Elemental Nuker | Row: Back | Weapons: Staff\nStats: Top INT | Key Spells: Crimson Flare, Cocytus, Muon Plasma, Deep Sea, Tempest\nWipes out enemy rows with wide-area advanced elemental spells. Low physical defense.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_14.bin',
        'Class_Code': 'EN',
        'Class_Name': 'Enchantress',
        'Vanilla_Desc': "Technical masters who can imbue allies' weapons with various elemental abilities. \nThis skill can be difficult to properly manage, especially when taking into account \nvarying enemy weaknesses. Their true worth is in the excellent support they provide.",
        'Modified_Desc': "Role: Elemental Buffer / Debuffer | Row: Front/Back | Weapons: Staff, 1H Sword\nStats: High INT / DEX / RES | Key Spells: Weapon Enchants, Dispel, Slow, Mind Control\nImbues ally weapons with elemental damage to exploit enemy vulnerabilities.",
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_15.bin',
        'Class_Code': 'PR',
        'Class_Name': 'Priestess',
        'Vanilla_Desc': 'A rear support class that specializes in healing magic. They can heal the party, \nrevive fallen comrades, and use a wide-reaching, albeit single-element, magic attack. \nThere can be no doubt regarding their importance in lengthy dungeon explorations.',
        'Modified_Desc': 'Role: Restorative Healer / Buffer | Row: Back | Weapons: Staff, Mace\nStats: Top RES / INT | Key Spells: Circle Heal, Revive, Refresh, Holy Light\nSustains party longevity with row heals, ailment cures, and holy revival magic.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_16.bin',
        'Class_Code': 'WT',
        'Class_Name': 'Witch',
        'Vanilla_Desc': 'Attack experts, able to cast the most powerful spells of each elemental set. \nTop-rank area attacks wipe out enemy parties, whilst destructive solo attacks \nobliterate single enemies, leaving not even a trace of their meager existence.',
        'Modified_Desc': 'Role: Supreme Destruction Archmage | Row: Back | Weapons: Staff\nStats: Supreme INT | Key Spells: Crimson Flare, Cocytus, Muon Plasma, Apocalypse\nThe ultimate spellcaster, unleashing cataclysmic spells across the battlefield.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_17.bin',
        'Class_Code': 'MP',
        'Class_Name': 'Magical Princess',
        'Vanilla_Desc': 'Magical girls who can handle even hand-to-hand combat with love and vigor. After \nusing Magical Change to heighten their abilities, they clean up their foes with area \nattacks. Per their name, they also wield magic, making them great all-around fighters.',
        'Modified_Desc': 'Role: Battle Magician / Hybrid Striker | Row: Front/Back | Weapons: 1H Sword, Staff\nStats: High ATK / INT / AGI | Key Skills: Magical Change, Spark, Starlight, Aura\nTransforms into an agile heroine blending high-speed strikes with radiant magic.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_18.bin',
        'Class_Code': 'SG',
        'Class_Name': 'Sage',
        'Vanilla_Desc': 'A support class specializing in magic that provides buffs to their allies. Possessing \nskills which automatically heal status ailments, they display their true power \nin lengthy encounters. They can swing the inevitable tough battles in your favor.',
        'Modified_Desc': 'Role: Master Tactical Buffer | Row: Back | Weapons: Staff, Mace\nStats: High INT / RES | Key Spells: Dispel, Fast Cast, All Element Shield\nEmpowers party with supreme tactical buffs, element immunities, and fast casts.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_19.bin',
        'Class_Code': 'BS',
        'Class_Name': 'Bishop',
        'Vanilla_Desc': 'Healing gurus in control of powerful restorative magic, such as party-wide healing \nof status ailments. They are formidable in attack as well, with mighty skills like \nHoly Gavel or Justice. Bishops greatly increase the survival rate of their party.',
        'Modified_Desc': 'Role: Supreme Divine Cleric | Row: Back | Weapons: Mace, Staff\nStats: Supreme RES / HP | Key Spells: Circle Heal, Holy Gavel, Circle Nurse\nUnsurpassed healing, party-wide ailment purges, and radiant holy destruction.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_20.bin',
        'Class_Code': 'MA',
        'Class_Name': 'Maid',
        'Vanilla_Desc': 'Skilled at neither physical attack nor magic, but can activate a wide range of \nspecial effects in battle without needing to chant beforehand or expend TP. \nThey tend to fill the role of the unsung hero.',
        'Modified_Desc': 'Role: Support Specialist / Turn Engine | Row: Front/Back | Weapons: Whip, Knife\nStats: Balanced TP / RES / AGI | Key Skills: First Aid, Cheer, Clean Up, Service\nInstant support skills without chanting or TP costs. Recovers party HP and TP.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_21.bin',
        'Class_Code': 'BD',
        'Class_Name': 'Bard',
        'Vanilla_Desc': 'Singers whose stunning voices strengthen the entire party. Since their battle \ncapabilities are limited, they primarily reside in the back row where their allies \ncan defend them. Their songs motivate, heal, and overall act as a huge support.',
        'Modified_Desc': 'Role: Party Song Buffer | Row: Back | Weapons: Instrument, Mic\nStats: High INT / RES | Key Skills: Hymnus, Fantasia, Carol, Chorale, Paean\nSustains ongoing party buffs, continuous HP regeneration, and EXP boosts with song.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_22.bin',
        'Class_Code': 'DN',
        'Class_Name': 'Dancer',
        'Vanilla_Desc': 'A technical class that is primarily responsible for debuffing their adversaries. \nMembers of this class captivate their enemies by performing a whole-body dance \nroutine. Those who observe their dazzling techniques become weakened and cursed.',
        'Modified_Desc': 'Role: Continuous Debuff Dancer | Row: Front/Back | Weapons: Fan, Dagger\nStats: High AGI / DEX | Key Skills: Waltz, Tango, Polka, Samba, Mazurka\nDances in rhythm to continuously cripple enemy ATK, DEF, speed, and evasion.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_23.bin',
        'Class_Code': 'DI',
        'Class_Name': 'Diva',
        'Vanilla_Desc': 'Support class specializing in skills that boost the abilities of their comrades. With \nvocals that could rattle even the Milky Way, they provide courage to all who listen \nand send off their comrades in a much improved state.',
        'Modified_Desc': 'Role: Supreme Song Virtuoso | Row: Back | Weapons: Mic, Instrument\nStats: Supreme INT / RES | Key Skills: Self Session, Rondo, Prelude, Requiem, Ballad\nPerforms multiple songs simultaneously with Self Session, supercharging party stats.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_24.bin',
        'Class_Code': 'MI',
        'Class_Name': 'Mistress',
        'Vanilla_Desc': 'Hard workers who finally reached the status of master after extensive work as \nsubordinate maids. As if affected by past trauma, they tend to exhibit quite sadistic \nbehavior. Their favorite weapon is the whip, and they love to castigate their rivals.',
        'Modified_Desc': 'Role: Sadistic Disciplinarian | Row: Front/Back | Weapons: Whip\nStats: High ATK / AGI / DEX | Key Skills: Discipline, Iron Maiden, Love Whip\nControls the flow of battle with punishing whip lashes, binds, and morale boosts.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_25.bin',
        'Class_Code': 'ET',
        'Class_Name': 'Etoile',
        'Vanilla_Desc': 'Admired by all as they soar across the battlefield. Even enemies are captivated \nby their ravishing dances. Not only are they delightfully dainty, but they are \nknown to rescue their comrades from danger, even at the cost of their own lives!',
        'Modified_Desc': 'Role: Primadonna Debuff Virtuoso | Row: Front/Back | Weapons: Fan, Dagger\nStats: Supreme AGI / DEX | Key Skills: On Stage, Salsa of Ruin, Paso Doble, Hop\nMaintains dual dances with On Stage, inflicting continuous party-wide enemy debuffs.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_26.bin',
        'Class_Code': 'SP',
        'Class_Name': 'Spieler',
        'Vanilla_Desc': 'An eccentric class with many skills, the effects of which are left completely up \nto chance. It is an utter mystery whether or not they are actually useful...',
        'Modified_Desc': 'Role: Gambler / Hybrid Utility | Row: Front/Back | Weapons: Dagger, Card, Dice\nStats: High DEX / AGI / LUK | Key Skills: Roulette, Dice, Coffee Break, Dance\nUnpredictable utility and gambling skills. Powers up as Pep builds during combat.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_27.bin',
        'Class_Code': 'DM',
        'Class_Name': 'Doll Master',
        'Vanilla_Desc': 'By breathing life into puppets, members of this class are able to create their own \nunderlings. Since the puppets take on lives of their own and act without any direct \ninput from their masters, the summoner herself is able to maneuver freely.',
        'Modified_Desc': 'Role: Puppet Summoner / Extra Turn DPS | Row: Front/Back | Weapons: Puppet, Dagger\nStats: High ATK / INT | Key Skills: Spartan, Katerina, Oracle, Doll Mastery\nDeploys autonomous puppets that attack and heal independently of the summoner.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_28.bin',
        'Class_Code': 'TS',
        'Class_Name': 'Trickster',
        'Vanilla_Desc': 'Rather than consistency, members of this class relish the instability that comes \nwith not knowing what will happen. In times of great danger, they may be able to \nturn the tables in your party\'s favor... Maybe.',
        'Modified_Desc': 'Role: Tactical Disrupter / Item Stealer | Row: Front/Back | Weapons: Dagger, Card\nStats: High AGI / DEX | Key Skills: Surprise, Doppelganger, Steal, Trick\nConfuses opponents with clones, unpredictable debuffs, and treasure pilfering.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_29.bin',
        'Class_Code': 'SS',
        'Class_Name': 'Soul Summoner',
        'Vanilla_Desc': 'The highest rank of puppeteer, this class can employ immensely powerful puppets. \nThey possess skills such as the ability to breathe life into two puppets at once or \nto absorb the power of the equipped Sealbook and bestow it upon their servants.',
        'Modified_Desc': 'Role: Master Puppet Architect | Row: Front/Back | Weapons: Puppet, Dagger\nStats: Top ATK / INT | Key Skills: Double Puppet, Seal Imbue, Auto-Puppet, Overdrive\nControls two high-tier puppets at once, transferring equipped Grand Sealbook powers.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_30.bin',
        'Class_Code': 'PA',
        'Class_Name': 'Papillon',
        'Vanilla_Desc': 'Using hand-fans proficiently as weapons, they are skilled in both short and long \ndistance combat. They are unique not only in weapon choice, but also skill selection, \nmost notable of which is an ultimate skill that turns a weakened enemy into... food?',
        'Modified_Desc': 'Role: Fan Aerialist / Gourmet Finisher | Row: Front/Back | Weapons: Fan, Card\nStats: High ATK / AGI / DEX | Key Skills: Fan Dance, Cooking, Butterfly Flight\nSlices through rows with fan aerial strikes and converts foes into meal items.',
        'Status': 'Approved'
    },
    {
        'File_Name': 'ClassData_31.bin',
        'Class_Code': 'JO',
        'Class_Name': 'Joker',
        'Vanilla_Desc': 'Death gods who wander the battlefield in search of enemy blood. However, \nthey quickly tire of this hunt, so instead drink their own blood in order to transform \ninto a destroyer. This haunting visage strikes fear into the hearts of all onlookers.',
        'Modified_Desc': 'Role: High-Risk Reaper / Blood Frenzy | Row: Front | Weapons: 2H Sword, Dagger\nStats: Extreme ATK / Crit | Key Skills: Blood Lust, Russian Roulette, Grim Reaper\nSacrifices HP and defenses to enter a bloodthirsty trance with terrifying damage.',
        'Status': 'Approved'
    }
]

df = pd.DataFrame(classes_data)

# Validation check
errors = []
for idx, r in df.iterrows():
    desc = r['Modified_Desc']
    lines = desc.split('\n')
    if len(lines) > 3:
        errors.append(f"[{r['Class_Name']}] Exceeds 3 lines: {len(lines)}")
    for li, line in enumerate(lines, 1):
        if len(line) > 85:
            errors.append(f"[{r['Class_Name']}] Line {li} exceeds 85 chars ({len(line)}): '{line}'")
        if '~' in line:
            errors.append(f"[{r['Class_Name']}] Line {li} contains invalid tilde (~)")

if errors:
    print("VALIDATION ERRORS:")
    for e in errors:
        print("  ", e)
    sys.exit(1)

out_path = r'mod_project\data_tables\classes.xlsx'
with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Classes', index=False)

print(f"Successfully generated {out_path} with {len(df)} validated classes! (0 errors)")

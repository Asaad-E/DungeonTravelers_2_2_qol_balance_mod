import os
import sys
import struct
import openpyxl

sys.path.insert(0, 'tools')
from pck_handler import PckArchive

def build_adv_script(title, start_label, header, boxes, end_label, start_id=0):
    cur_id = start_id
    out = bytearray()
    
    # 1. Title: 0x017f, type 0x0a
    out.extend(b'\x7f\x01\n')
    out.extend(struct.pack('<i', cur_id))
    out.extend(b'\xff\xff\xff')
    out.extend(title.encode('latin-1') + b'\x00')
    cur_id += 1
    
    # 2. Start label: 0x0158, type 0x12
    out.extend(b'\x58\x01\x12')
    out.extend(struct.pack('<i', cur_id))
    out.extend(b'\xff\xff\xff')
    out.extend(start_label.encode('latin-1') + b'\x00')
    cur_id += 1
    
    # 3. Header: 0x0025, 0x0122, type 0x0a
    out.extend(b'\x25\x00\x22\x01\n')
    out.extend(struct.pack('<i', cur_id))
    out.extend(b'\xff\xff\xff')
    out.extend(header.encode('latin-1') + b'\x00')
    cur_id += 1
    
    # 4. Content boxes: 0x0025, 0x0122, type 0x0a
    for box in boxes:
        out.extend(b'\x25\x00\x22\x01\n')
        out.extend(struct.pack('<i', cur_id))
        out.extend(b'\xff\xff\xff')
        out.extend(box.encode('latin-1') + b'\x00')
        cur_id += 1
        
    # 5. End label: 0x0158, type 0x12
    out.extend(b'\x58\x01\x12')
    out.extend(struct.pack('<i', cur_id))
    out.extend(b'\xff\xff\xff')
    out.extend(end_label.encode('latin-1') + b'\x00')
    cur_id += 1
    
    # 6. Return: 0x0057
    out.extend(b'\x57\x00')
    return bytes(out)

# Lesson definitions
LESSON_07_BOXES = [
    "Press <BUTTON_R> in battle to check enemy names and statuses.\nThis lets you view active buffs, debuffs, and spell chants.\nPreviously created Sealbooks will also reveal their level.",
    "In Options, set Battle Check Display to Save for auto-scan.\nPress <BUTTON_L> on a target to open the detailed Stats menu,\nrevealing combat attributes, weaknesses, and ailments.",
    "Press <BUTTON_SQUARE> during battle to open the Battle Log.\nIf an action passes too quickly, check the log to review\nexact damage dealt, skills cast, and status ailments."
]

LESSON_08_BOXES = [
    "Fighter: Frontline anchor who absorbs heavy blows.\nProvoke draws dangerous attacks from fragile allies,\nkeeping your spellcasters alive during boss fights.",
    "Magic User: Casts elemental spells across all rows.\nChants take time to cast, but strike with heavy power,\nexploiting enemy weaknesses for massive burst damage.",
    "Scout: Agile skirmisher with speed, evasion, and crits.\nDisarms traps, spots shortcuts, and steals rare loot,\ndelivering rapid strikes to pick off backline foes.",
    "Maid: Indispensable support that restores TP each turn.\nCleanses nasty ailments with Cheer and pacifies foes,\nallowing attackers to use their best skills sustainably.",
    "Spieler: Chaotic wildcard using cards, coins, and luck.\nOffers unpredictable buffs, bonus EXP, and doll allies,\nturning the tides of battle through daring gambles.",
    "Every party begins with these five basic archetypes.\nAt Level 15, they branch into Intermediate roles,\nand at Level 30 unlock their ultimate Advanced classes."
]

LESSON_12_BOXES = [
    "Poison drains 5% Max HP each turn (cannot drop below 1 HP).\nFreeze disables all physical techniques, dances, and dolls.\nBoth of these crippling conditions belong to Water.",
    "Silence prevents the use of all magic and song skills.\nSleep cancels actions, drops evasion, and increases damage\nreceived from physical hits by 1.5x. Both belong to Wind.",
    "Paralysis causes a 30% chance to lose actions (Lightning).\nSlow cuts turn speed in half (Earth). Progressing stones\nhalve AGI and must be cured before turning completely.",
    "Stun (Fire) pushes the victim's turn to round end.\nAilments wear off in time or cure with Nurse and Cleanse.\nStacking 100 resistance grants full elemental immunity."
]

LESSON_13_BOXES = [
    "At Level 15, your basic classes promote into Intermediate roles.\nThese 11 specialized classes define your mid-game battle strategy.\nChoose wisely to balance party survival, burst, and sustain.",
    "Paladin: The frontline protector wielding heavy armor and shields.\nGuards frail allies from lethal hits and cuts incoming damage.\nEssential when boss hits start wiping out your backline mages.",
    "Berserker: Savage powerhouse wielding giant axes and two-handers.\nTrades defense for raw fury, shattering enemy armor with huge hits.\nPick her to shred high-DEF foes before they outlast your team.",
    "Sorceress: Pure offensive spellcaster wielding destructive magic.\nUnleashes tier-2 elemental nukes that obliterate entire mob rows.\nThe go-to class when you need pure magic burst on bosses.",
    "Enchantress: Versatile battle-mage focused on buffs and utility.\nGrants party speed with Accelerator, elemental covers, and sleep.\nBrings essential tactical control to difficult encounters.",
    "Priestess: Divine restorative healer wielding holy maces and wands.\nRestores party HP with Heal, cures ailments, and revives allies.\nYour foundational insurance against attrition in labyrinths.",
    "Archer: Dedicated long-range marksman striking from safe back rows.\nFires full-power arrows ignoring row penalties, inflicting crits.\nGreat for safely picking off high-threat backline foes.",
    "Assassin: Lethal skirmisher striking from shadows with daggers.\nSpecializes in fatal sneak attacks, poison, silence, and bleeds.\nShuts down dangerous enemies before they can even strike.",
    "Bard: Musical supporter whose songs bolster the entire party.\nSings passive auras that replenish party TP and boost attributes.\nActs on her rhythm, sustaining the team without turn cost.",
    "Dancer: Rhythmic debuffer whose dances cripple the enemy line.\nDrains enemy attack power, slows turn gauges, and breaks defense.\nTurns grueling, protracted boss fights heavily in your favor.",
    "Trickster: Evasive gambler slinging cards and sudden ailments.\nDodges heavy blows while spreading chaos, confusion, and seals.\nAn agile disturber that keeps enemy lines off balance.",
    "Doll Master: Puppet commander crafting and directing battle dolls.\nSummons autonomous doll allies that attack, defend, and heal.\nGrants extra party actions every round without spending TP."
]

LESSON_23_BOXES = [
    "A single solitary enemy is often exceptionally dangerous.\nThey wield lethal skills and change rotations at low HP.\nDispel their buffs and unleash burst damage to finish them.",
    "Combine multi-hit skills like Danger Shoot with songs such as\nBarrage Rondo for maximum hits, or Sharp Stab with Murder.\nDark Aura pairs naturally with Provoke to manage threat.",
    "Defensively, pair Adaptation with Moon Curtain for safety.\nEquipment enchants with speed or critical bonuses further\namplify your loops. Experiment to find winning synergies."
]

LESSON_24_BOXES = [
    "At Level 30, characters unlock their pinnacle Advanced classes.\nThese 16 specialized roles wield game-changing master skills,\nforming the backbone needed to conquer deep postgame depths.",
    "Valkyrie: The ultimate frontline bastion wielding holy spears.\nDainger Guard automatically intercepts fatal blows aimed at allies.\nAllows you to run fragile glass-cannon mages in safety.",
    "Dark Lord: Ruthless vanguard titan who trades health for carnage.\nSacrifices HP and defense to unleash blood-draining group sweeps.\nBrings massive burst and self-sustain to your frontline.",
    "Samurai: Deadly counter-striker wielding razor-sharp katanas.\nStances let her parry incoming attacks and strike back with crits.\nDevastating against multi-attacking physical bosses.",
    "Witch: The pinnacle of destructive single and multi-target magic.\nCasts tier-3 elemental spells that incinerate enemy resistances.\nThe premier choice for wiping rooms and crushing boss HP.",
    "Magical Princess: Hybrid battle-mage with instant spell blades.\nTransforms into an empowered form, ignoring slow casting chants.\nBypasses mage fragility with high physical and magical output.",
    "Sage: Tactical spellmaster controlling the tempo of the battle.\nAccelerator speeds up party casting while barriers absorb nukes.\nUnrivaled utility that ensures your team always moves first.",
    "Bishop: Divine beacon of recovery, resurrection, and protection.\nCircle Heal, Circle Nurse, and Holy Light restore fallen allies.\nGuarantees full recovery even after catastrophic boss rounds.",
    "Sniper: Precision marksman firing armor-piercing ballistic shots.\nUnmissable long-range snipes shatter defenses and bypass guards.\nDeletes high-evasion and high-armor priority targets on sight.",
    "Treasure Hunter: Agile dungeoneer maximizing exploration profits.\nGuarantees rare monster drops while unleashing fast dagger flurries.\nDisarms every trap effortlessly and speeds up dungeon looting.",
    "Kunoichi: Shadow warrior wielding ninjutsu and lethal illusions.\nShadow clones absorb attacks while dual-wielding lands double hits.\nIncredible burst damage paired with top-tier survival tricks.",
    "Diva: Potent party buffs and massive sonic TP disruption.\nSupercharges party stats while devastating enemy TP reserves.\nDisrupts enemy chants and keeps your team at their peak.",
    "Mistress: Ruthless dominator wielding whips and severe commands.\nInflicts crippling debuffs and forces enemies into obedience.\nPunishes afflicted foes with amplified execution damage.",
    "Etoile: Supreme prima ballerina whose dances dominate the tempo.\nDebilitating dances cripple enemy turn gauges and halve stats.\nThe single best counter against hyper-fast superbosses.",
    "Joker: High-stakes executioner wielding cards and sudden death.\nDeals explosive critical damage that scales with daring gambles.\nIf the hand is right, can vaporize boss health bars instantly.",
    "Soul Summoner: Spiritual conduit calling forth boss monster souls.\nSummons formidable sealbook spirits to fight with boss abilities.\nActs as an extra party member absorbing enemy attacks.",
    "Papillon: Whimsical skirmisher sweeping fields with kitchen fans.\nPiercing fan sweeps hit full rows, bypassing enemy armor entirely.\nOne of the fastest, most efficient room-clearers in the game."
]

NEW_TEACHING_SCRIPTS = {
    'CheatsTeaching_07.adv.bin': (
        'Battle Info & Battle Log', 'CheatsTeaching_07_start', 'Regarding Battle Info and the Battle Log:',
        LESSON_07_BOXES, 'CheatsTeaching_07_SCENE_END', 54
    ),
    'CheatsTeaching_08.adv.bin': (
        'Basic Classes', 'CheatsTeaching_08_start', 'Regarding Basic Classes:',
        LESSON_08_BOXES, 'CheatsTeaching_08_SCENE_END', 68
    ),
    'CheatsTeaching_12.adv.bin': (
        'Status Ailments & Resistances', 'CheatsTeaching_12_start', 'Regarding Status Ailments and Resistances:',
        LESSON_12_BOXES, 'CheatsTeaching_12_SCENE_END', 104
    ),
    'CheatsTeaching_13.adv.bin': (
        'Intermediate Classes', 'CheatsTeaching_13_start', 'Regarding Intermediate Classes:',
        LESSON_13_BOXES, 'CheatsTeaching_13_SCENE_END', 121
    ),
    'CheatsTeaching_23.adv.bin': (
        'Tactics & Skill Synergy', 'CheatsTeaching_23_start', 'Regarding Combat Tactics and Synergies:',
        LESSON_23_BOXES, 'CheatsTeaching_23_SCENE_END', 217
    ),
    'CheatsTeaching_24.adv.bin': (
        'Advanced Classes', 'CheatsTeaching_24_start', 'Regarding Advanced Classes:',
        LESSON_24_BOXES, 'CheatsTeaching_24_SCENE_END', 230
    )
}

def get_built_scripts():
    return {fn: build_adv_script(*args) for fn, args in NEW_TEACHING_SCRIPTS.items()}

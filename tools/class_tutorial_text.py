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
    "Press <BUTTON_R> in battle to check enemy names and statuses.\nThis lets you view active buffs, debuffs, and spell chants.\nPreviously created Sealbooks will reveal their level.",
    "In Options, set Battle Check Display to Save for auto-scan.\nPress <BUTTON_L> on a target to open the detailed Stats menu,\nrevealing enemy attributes, weaknesses, and ailments.",
    "Press <BUTTON_SQUARE> during battle to open the Battle Log.\nIf an action passes too quickly, check the log to review\nexact damage dealt, skills cast, and status ailments."
]

LESSON_08_BOXES = [
    "Every party begins with these five basic archetypes.\nAt Level 15, they branch into Intermediate roles,\nand at Level 30 unlock their ultimate classes.",
    "Fighter: Frontline anchor who absorbs heavy blows.\nProvoke draws dangerous attacks from fragile allies,\nkeeping your spellcasters alive during boss fights.",
    "Magic User: Casts elemental spells across all rows.\nChants take time to cast, but strike with heavy power,\nexploiting enemy weaknesses for massive burst damage.",
    "Scout: Agile skirmisher with speed, evasion, and crits.\nStrikes fast with Sharp Stab and Poison Shot, cures self\nwith Cleanse, and steals gold while dodging enemy blows.",
    "Maid: Indispensable support keeping the party's TP full.\nUses Cook, Self-Sacrifice, and First Aid to sustain allies,\nwhile Lullaby puts dangerous foes to sleep in battle.",
    "Spieler: Chaotic wildcard relying on luck and gambles.\nFires Danger Shoot, heals with Coffee Break, spins wild\nRoulette Circus outcomes, and finds items as you walk."
]

LESSON_12_BOXES = [
    "Poison drains 5% Max HP each turn (cannot drop below 1 HP).\nFreeze disables all physical techniques, dances, and dolls.\nBoth of these crippling conditions belong to Water.",
    "Silence prevents the use of all magic and song skills.\nSleep cancels actions, drops evasion, and increases damage\ntaken from any attack by 1.5x. Both belong to Wind.",
    "Paralysis causes a 30% chance to lose actions (Lightning).\nSlow cuts turn speed in half (Earth). Progressing stones\nhalve AGI and must be cured before turning solid.",
    "Stun (Fire) resets turn gauge and cancels chants or dances.\nAilments wear off in time or cure with Nurse and Cleanse.\n100 resistance blocks ailments and halves matching hits."
]

LESSON_13_BOXES = [
    ("At Level 15, basic classes promote to Intermediate roles.\n"
     "These 11 classes shape your advancing battle strategy.\n"
     "Choose wisely to balance party survival and offense."),
    "Paladin: Frontline protector wielding heavy armor and shield.\nGuards frail allies from lethal hits and cuts damage taken.\nEssential when boss hits threaten backline mages.",
    "Berserker: Savage warrior wielding giant axes and blades.\nTrades defense for fury, shattering armor with huge hits.\nShreds high-DEF foes before they outlast your team.",
    "Sorceress: Pure offensive spellcaster of destructive magic.\nUnleashes wide elemental spells that sweep entire enemy rows.\nA focused specialist when you need decisive magical burst.",
    "Enchantress: Versatile battle-mage of buffs and control.\nBoosts allies with Circle Brave, Circle Protect, and weapon\nenchants, while shutting down foes with status spells.",
    "Priestess: Divine restorative healer wielding holy wands.\nRestores party HP with Heal, cures ailments, and revives.\nYour foundational insurance in deep labyrinths.",
    "Archer: Dedicated marksman striking from safe back rows.\nFires full-power arrows ignoring row penalties with crits.\nGreat for safely picking off high-threat foes.",
    "Assassin: Lethal skirmisher striking from the shadows.\nSpecializes in critical strikes, sleep, silence, and stun.\nShuts down dangerous enemies before they can act.",
    "Bard: Musical supporter whose songs bolster the party.\nSings passive auras that replenish TP and boost stats.\nSustains allies continuously without TP cost.",
    "Dancer: Rhythmic debuffer whose dances cripple foes.\nDrains enemy attack power, slows turn gauges, and defense.\nTurns grueling boss fights heavily in your favor.",
    "Trickster: Evasive gambler dealing risky burst and chaos.\nTrades DEF for ATK with High Risk, High Return, springs\nCheckmate and Magic Box, and evades hits with Pretend.",
    "Doll Master: Puppet commander crafting battle dolls.\nSummons autonomous doll allies to attack and defend.\nOnce summoned, dolls act on their own turns without TP cost."
]

LESSON_23_BOXES = [
    "A single solitary enemy is often exceptionally dangerous.\nThey wield lethal skills and change rotations at low HP.\nDispel their buffs and unleash burst damage quickly.",
    "Combine multi-hit skills like Danger Shoot with songs such\nas Barrage Rondo for max hits, or Sharp Stab with Murder.\nDark Aura pairs with Provoke to manage enemy threat.",
    "Defensively, pair Adaptation with Moon Curtain for safety.\nEquipment enchants with speed or critical bonuses further\namplify your loops. Find winning synergies."
]

LESSON_24_BOXES = [
    "At Level 30, characters unlock their Advanced classes.\nThese 16 roles wield decisive master techniques and spells,\nforming the backbone needed to conquer the depths.",
    "Valkyrie: Frontline bastion wielding spears, swords, shields.\nMaterial Guard and Spell Guard shield allies from heavy blows.\nPairs sturdy defenses with fierce lance strikes and heals.",
    "Dark Lord: Ruthless vanguard titan trading health for fury.\nSacrifices HP and defense to unleash blood group sweeps.\nBrings massive burst and sustain to your frontline.",
    "Samurai: Deadly counter-striker wielding sharp katanas.\nStances let her parry incoming attacks and strike back.\nDevastating against multi-attacking physical bosses.",
    "Witch: Dedicated arcanist of devastating elemental sorcery.\nChannels supreme all-target and single-target spells.\nExcels at exploiting elemental weaknesses with burst power.",
    "Magical Princess: Hybrid battle-mage with instant blades.\nTransforms to an empowered form, ignoring cast chants.\nBypasses mage fragility with heavy hybrid output.",
    "Sage: Tactical spellmaster controlling battle tempo.\nAccelerator speeds party casting while barriers shield.\nUnrivaled utility ensuring your team moves first.",
    "Bishop: Divine beacon of recovery and resurrection.\nFull Heal, Circle Nurse, and Insurance protect every ally,\nbacked by Moon Curtain and Circle Heal in lethal fights.",
    "Sniper: Precision marksman striking cleanly from afar.\nWields bows and firearms for guided, armor-piercing shots.\nSupports allies with Warning Shot and bow covering fire.",
    "Treasure Hunter: Agile explorer built to maximize spoils.\nCombines Treasure Hunt, Item Steal, and Trap Search utility.\nStrikes reliably with quick dagger, whip, and ranged skills.",
    "Kunoichi: Shadow warrior wielding lethal illusions.\nShadow clones absorb hits while dual-wielding strikes.\nIncredible burst damage paired with top survival.",
    "Diva: Master vocalist whose continuous songs empower all.\nSongs raise crits, speed, magic hit, chant speed, and hits.\nSelf Session lets her sustain two songs at once, faster.",
    "Mistress: Ruthless dominator wielding whips and commands.\nInflicts crippling debuffs, forcing foes to obedience.\nPunishes afflicted foes with amplified execution.",
    "Etoile: Supreme ballerina who commands battle tempo.\nOn Stage lets her keep two dances active at once, sapping\nfoe speed, resistance, and HP; Primevil revives the party.",
    "Joker: Reckless destroyer trading safety for burst power.\nTrump Card converts DEF to ATK; Mad Zapper pierces rows.\nWields whips, axes, and unpredictable gambles in combat.",
    "Soul Summoner: Master puppeteer commanding supreme dolls.\nDouble Puppet fields two dolls empowered by Soul Seal.\nUnleashes Mercidarian, Perdurabo, Musiy, and Soul Eater.",
    "Papillon: Agile hand-fan fighter sweeping wide fields.\nRose Queen poisons all foes while Tinker Squash delays.\nEvades blows with Illusion and turns foes into food."
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

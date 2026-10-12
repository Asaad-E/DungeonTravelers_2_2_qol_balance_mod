import os
import sys
sys.path.insert(0, os.path.abspath('mod_project/tools'))
import openpyxl
from pck_handler import PckArchive, JoinSkillHelper
from text_checks import joint_effects, JOINT_EFFECTS, JOINT_STYLES, JOINT_PLACE_RE

BACKUP_PATH = 'mod_project/backups/JoinSkillData.pck'
archive = PckArchive(BACKUP_PATH)

joint_templates = {
    'Rush Zanber': "Physical damage to an enemy row. [1/7 TP, 10 Pep]",
    'Catastrophe': "Powerful physical attack. Inflicts slow ({e122}). [1/3 TP, 5 Pep]",
    'Magical Treasure': "Physical damage to an enemy; drop rate UP. [1/3 TP, 5 Pep]",
    'Genocide Rain': "Rain arrows down on all foes across {e147} turns. [1/3 TP, 10 Pep]",
    'Galactic Voice': "Fully restore party HP, dispel status ailments. [1/5 TP, 5 Pep]",
    'Divine Punishment!': "Physical damage to an enemy row. {e119} instakill. [1/4 TP, 7 Pep]",
    'Nightmare Fall': "Non-elemental damage to all foes. {e116} sleep. [1/4 TP, 7 Pep]",
    'Powered-Up Beatdown!': "{e96} bash attacks on one enemy. {e118} stun. [1/3 TP, 5 Pep]",
    'Psychowave': "Non-elem dmg to all foes. DEF & magic DEF {e162}. [1/4 TP, 7 Pep]",
    'Avatara': "Physical and {e95} piercing attacks on one foe. [1/2 TP, 15 Pep]",
    'Gjallarhorn': "Circle Brave/Protect ({e161}), Moon Curtain ({e169}). [1/5 TP, 5 Pep]",
    'Hell Raiser': "Cut enemy row's HP to 25% (no boss effect). [1/3 TP, 7 Pep]",
    'Suppression Arrow': "Damage to back row. {e117} silence/freeze. [1/3 TP, 7 Pep]",
    'Rapid Storm': "Party speed {e168} and physical accuracy {e166}. [1/7 TP, 5 Pep]",
    'Holy Blast': "2,000 direct damage to all foes, dispel buffs. [1/3 TP, 10 Pep]",
    'Evolution': "Allies magic ATK ({e173}) and crit rate ({e174}). [1/4 TP, 5 Pep]",
    'Searching Eye': "See the stats of all enemies. [1/9 TP, 3 Pep]",
    'Bunker Buster': "Damage to back row. Phys attack/defense {e161}. [1/4 TP, 7 Pep]",
    'Crazy Rush': "Attack an enemy 7 times with wild accuracy. [1/3 TP, 15 Pep]",
    'Stampede Heaven': "Attack all enemies twice. [1/4 TP, 10 Pep]",
    'Paralyzing Wind': "Wind attack to all foes. {e115} paralysis. [1/5 TP, 5 Pep]",
    'Daruma-Drop!': "Physical damage. {e54} turn delay chance. [1/7 TP, 5 Pep]",
    'Testament': "Physical damage & Shadow Sew ({e123}) on a row. [1/3 TP, 5 Pep]",
    'Brain Burst': "Physical damage. {e113} poison/paralyze/sleep. [1/4 TP, 7 Pep]",
    'Multi-Shadow Clone': "All allies perform Shadow Clone technique. [1/4 TP, 15 Pep]",
    'Happy Banquet': "Pep {e66} for the ally with the lowest Pep. [1/7 TP, 1 Pep]",
    'Critical Hits': "Critical attack on all enemies with 100% hit. [1/4 TP, 7 Pep]",
    'Hysteric Slap': "{e94} bash attacks on an enemy row. [1/3 TP, 10 Pep]",
    'Fire of Purgatory': "Attack one foe ({e88} vs Undead/Demon/Apparition). [1/4 TP, 7 Pep]",
    'Genocide Rain\'s Action': "Actual course of action",
    'Double-Team Attack': "Strike an enemy row from both sides at once. [1/7 TP, 7 Pep]",
    'Twist and Shout': "Spiral into enemy ranks for a piercing attack. [1/7 TP, 7 Pep]",
    'Curse Bullet': "Waste one enemy and poison it ({e113}). [1/5 TP, 10 Pep]",
    'Mesmerize': "Cancel enemy chants, dances, songs and dolls. [1/7 TP, 10 Pep]",
    'Jetstream': "Dogpile an enemy with three allies in a row. [1/4 TP, 8 Pep]",
    'Magical Assault': "Slice a foe 2-5 times with friendship & swords. [1/4 TP, 15 Pep]",
    'Beast Blitz': "Rough up ({e93} hits) and poison ({e113}) one foe. [1/3 TP, 12 Pep]",
    'God Punch': "Pummel one foe ({e88} vs Undead/Demon/Apparition). [1/5 TP, 10 Pep]",
    'Durchbruch': "Two light arrows pierce back row; silence ({e117}). [1/5 TP, 12 Pep]",
    'Maid Beam': "Deadly Maid Beam pierces back row. Petrify ({e120}). [1/4 TP, 8 Pep]",
    'Sleep with the Fishes': "Lull all enemies to sleep with hypnosis. [1/5 TP, 10 Pep]",
    'Elixir': "Full party HP; dispel debuffs & ailments. [1/7 TP, 8 Pep]",
    'Feuerkraft': "Immolate foes, absorb HP/TP ({e296} dmg cap). [1/4 TP, 30 Pep]",
    'Gold Power': "Hurl {e433} wallet at one foe (max {e296} dmg). [1/3 TP, 20 Pep]",
    '777 Fever': "Paralysis ({e115}) and 7x Lv dmg to all foes. [1/5 TP, 6 Pep]",
    'Gimme Gold': "Gain 4x enemies' gold after battle (min 100). [1/7 TP, 20 Pep]",
    'Death Beam': "Instakill one random combatant, friend or foe. [1/9 TP, 8 Pep]",
    'Apocrypha': "Waste one enemy and lower phys. DEF ({e162}). [1/4 TP, 12 Pep]",
    'Anastasia': "Goddess of life resurrects allies (HP {e105}). [1/4 TP, 10 Pep]",
    'Jackpot': "Deal 77x user Lv in dmg to a foe. Wild jokers! [All TP, 50 Pep]",
    'Todokanai Koi': "Damage and likely petrify all enemies. [1/4 TP, 30 Pep]",
    'Lots Of Guns': "Three guns rain lead on random foes ({e93} hits). [1/5 TP, 15 Pep]",
}

for fn, b in archive.files:
    skill = JoinSkillHelper.read_joint(b)
    name = skill['name']
    tmpl = joint_templates.get(name, skill['desc'])
    stored = {i: v for i, v, _ in skill['effects']}
    
    def repl(m):
        eid = int(m.group(1))
        style, text = JOINT_EFFECTS[eid]
        return text if style == 'text' else JOINT_STYLES[style](stored[eid])
        
    resolved = JOINT_PLACE_RE.sub(repl, tmpl)
    print(f"{name:24} | len={len(resolved):2d} | {resolved}")
    assert len(resolved) <= 70, f"{name} is too long: {len(resolved)}"

print("\nALL 52 TEMPLATES RESOLVED AND FIT WITHIN 70 CHARACTERS!")

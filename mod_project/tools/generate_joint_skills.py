import openpyxl, sys
sys.path.insert(0, 'mod_project/tools')
from pck_handler import PckArchive

JOINT_SKILLS_DATA = {
    "Rush Zanber": (
        "[Req: 3 Front Row with Short weapons (Fighter/Pri/Bish/Mis/Pap/Jok)]\n"
        "TP: 14% | Physical weapon damage to an enemy row."
    ),
    "Catastrophe": (
        "[Req: 2 of DL/Sage/Diva/Joker + 1 Any Class]\n"
        "TP: 33% | Powerful short-range physical strike. Inflicts Slow."
    ),
    "Magical Treasure": (
        "[Req: 3 of Valk/Pri/Sage/TH/Mis/Pap]\n"
        "TP: 33% | Short-range physical strike. Increases equipment drop rate."
    ),
    "Genocide Rain": (
        "[Req: 1 Sniper + 1 of Valk/Witch/SS + 1 Any Class]\n"
        "TP: 25% | Multi-turn rain of arrows upon all enemies."
    ),
    "Galactic Voice": (
        "[Req: 1 Diva + 1 of Diva/Etoile/Mistress/Papillon/Witch]\n"
        "TP: 20% | Fully restores party HP and dispels all status ailments."
    ),
    "Divine Punishment!": (
        "[Req: 1 Samurai (initiator) + 1 Kunoichi + 2 Tier 3 Classes]\n"
        "TP: 25% | Physical weapon damage to an enemy row. High instakill chance."
    ),
    "Nightmare Fall": (
        "[Req: 1 Witch + 2 of DL/Witch/Sage/Bish/Kuno/Eto/SS/Jok]\n"
        "TP: 25% | Long-range neutral damage to all enemies. High Sleep chance."
    ),
    "Powered-Up Beatdown!": (
        "[Req: 3 Bash weapon users (at least 1 Dark Lord or Bishop)]\n"
        "TP: 33% | Short-range multi-hit bash strikes. High Stun chance."
    ),
    "Psychowave": (
        "[Req: 3 of Witch/Princess/TH/Diva/Mistress/SS/Papillon]\n"
        "TP: 25% | Long-range neutral damage to all enemies. Debuffs P.DEF/M.DEF."
    ),
    "Avatara": (
        "[Req: 5 Different Base Classes (Fighter/Mage/Scout/Maid/Spieler)]\n"
        "TP: 50% | Multi-hit DEF-piercing physical strike to one enemy."
    ),
    "Gjallarhorn": (
        "[Req: 3 of Valkyrie/Sage/Bishop/Diva/Etoile]\n"
        "TP: 20% | Casts Circle Brave, Circle Protect, and Moon Curtain on party."
    ),
    "Hell Raiser": (
        "[Req: 4 Different Tier 2 Classes (Ber/Enc/Tri/Bar/Dan/Ass/Sor)]\n"
        "TP: 33% | Reduces enemy row HP to 25% (ineffective vs. bosses)."
    ),
    "Suppression Arrow": (
        "[Req: 3 of Valkyrie/Witch/TH/Sniper/SS/Joker]\n"
        "TP: 20% | Mid-range stab attack piercing to back row. Silence/Freeze."
    ),
    "Rapid Storm": (
        "[Req: 1 Maid Class + 1 Scout Class + 1 Spieler Class]\n"
        "TP: 14% | Greatly increases action speed and physical accuracy for party."
    ),
    "Holy Blast": (
        "[Req: 5 of Valk/Sam/Any Mage/TH/Mistress/Papillon]\n"
        "TP: 33% | Deals 2000 fixed neutral damage to all enemies and dispels buffs."
    ),
    "Evolution": (
        "[Req: 1 Front Valk/Sam + 1 Back Mage Class]\n"
        "TP: 25% | Greatly increases party Magic ATK and Critical Rate."
    ),
    "Searching Eye": (
        "[Req: 4 Different Base Classes]\n"
        "TP: 11% | Reveals stats, weaknesses, and HP of all enemies."
    ),
    "Bunker Buster": (
        "[Req: 3 of Pal/Ber/DL/SS with Stab weapons]\n"
        "TP: 25% | Mid-range stab attack piercing back row. Debuffs ATK/DEF."
    ),
    "Crazy Rush": (
        "[Req: 1 Dark Lord + 1 Kunoichi + 1 Joker + 2 Any Classes]\n"
        "TP: 33% | Attacks one enemy 7 times with physical strikes."
    ),
    "Stampede Heaven": (
        "[Req: 4 of Sam/DL/Pri/Bish/TH/Kuno/SS/Pap/Jok]\n"
        "TP: 25% | Short-range physical attack striking all enemies twice."
    ),
    "Paralyzing Wind": (
        "[Req: 3 of Valkyrie/Any Mage/TH/Diva/SS/Joker]\n"
        "TP: 20% | Long-range wind damage to all enemies. High Paralysis chance."
    ),
    "Daruma-Drop!": (
        "[Req: 3 of Sam/Sage/Bish/TH/Diva/Eto/Pap]\n"
        "TP: 14% | Bash damage to one enemy. High chance to delay target's turn."
    ),
    "Testament": (
        "[Req: 3 of Dark Lord/Witch/TH/Kunoichi/Diva/Mistress/Joker]\n"
        "TP: 33% | Mid-range physical weapon damage. Inflicts Shadow Sew."
    ),
    "Brain Burst": (
        "[Req: 3 of DL/Bishop/Kunoichi/Mistress/SS/Joker]\n"
        "TP: 25% | Long-range physical hit. High Poison, Paralysis, Sleep chance."
    ),
    "Multi-Shadow Clone": (
        "[Req: 1 Kunoichi + 3 Tier 3 Classes]\n"
        "TP: 25% | Grants Shadow Clone (nullify next physical hit) to all allies."
    ),
    "Happy Banquet": (
        "[Req: 1 Ally at Low Pep (<100) + 1 Any Ally]\n"
        "TP: 14% | Restores Pep of the ally with lowest morale back to baseline."
    ),
    "Critical Hits": (
        "[Req: 3 Front Row with Short weapons]\n"
        "TP: 25% | Guaranteed 100% accuracy critical physical strike on all foes."
    ),
    "Hysteric Slap": (
        "[Req: 3 Unarmed Allies (no weapons equipped)]\n"
        "TP: 33% | Multiple short-range bash hits across an enemy row."
    ),
    "Fire of Purgatory": (
        "[Req: 3 Tier 2 Classes (Pal/Ber/Enc/Sor/Pri/DM)]\n"
        "TP: 25% | Fire strike to 1 foe. 2x damage to Undead, Demon, Apparition."
    ),
    "Genocide Rain's Action": (
        "[Internal multi-turn action tick]\n"
        "Automatic arrow rain on all foes."
    ),
    "Double-Team Attack": (
        "[Req: 2 Front Row with Short weapons (Ftr/TH/Pri/Bish/Mis/Pap/Jok)]\n"
        "TP: 14% | Pincer physical strike hitting an enemy row from both sides."
    ),
    "Twist and Shout": (
        "[Req: 1 Maid/Bard/Dancer + 1 Spieler/Doll Master/Trickster]\n"
        "TP: 14% | Mid-range piercing stab attack into enemy formation."
    ),
    "Curse Bullet": (
        "[Req: 1 Gun user + 1 Any Class]\n"
        "TP: 20% | Long-range firearm strike to one enemy. Inflicts Poison."
    ),
    "Mesmerize": (
        "[Req: 1 Diva/Etoile + 1 Joker/Papillon (Trickster line)]\n"
        "TP: 14% | Guaranteed cancellation of all enemy chants, dances, & songs."
    ),
    "Jetstream": (
        "[Req: 1 Treasure Hunter or Kunoichi + 2 Any Classes]\n"
        "TP: 25% | Short-range physical combo attack against one enemy."
    ),
    "Magical Assault": (
        "[Req: 1 Magical Princess with Sword + 2 Tier 3 Classes]\n"
        "TP: 25% | Slices a random enemy 2 to 5 times with magical sword strikes."
    ),
    "Beast Blitz": (
        "[Req: 1 Dark Lord + 1 Kunoichi + 1 Any Class]\n"
        "TP: 33% | Short-range physical attack to one enemy. Inflicts Poison."
    ),
    "God Punch": (
        "[Req: 1 Bash weapon user + 3 Any Classes]\n"
        "TP: 20% | Bash strike to 1 foe. 2x damage to Undead, Demon, Apparition."
    ),
    "Durchbruch": (
        "[Req: 3 Tier 2 Stab weapon users (Pal/Ass/Enc/Dan/DM)]\n"
        "TP: 20% | Mid-range stab attacks piercing back row. May inflict Silence."
    ),
    "Maid Beam": (
        "[Req: 1 Maid Class (initiator) + 2 Any Classes]\n"
        "TP: 25% | Long-range neutral beam piercing row. Petrify in progress."
    ),
    "Sleep with the Fishes": (
        "[Req: 1 Spieler Class + 2 Any Classes]\n"
        "TP: 20% | Massive hypnotic wave. Inflicts Sleep on all enemies."
    ),
    "Elixir": (
        "[Req: 2 Princesses + 1 Papillon + 1 Tier 3 Class]\n"
        "TP: 14% | Fully heals party HP and cleanses all debuffs and ailments."
    ),
    "Feuerkraft": (
        "[Req: 1 Berserker + 1 Sorceress + 1 Archer]\n"
        "TP: 25% | Magic fire attack on all foes. Absorbs damage as HP and TP."
    ),
    "Gold Power": (
        "[Req: 1 Merchant / Spieler Class + 2 Any Classes]\n"
        "TP: 33% | Consumes 5% current gold to deal heavy neutral damage (cap 10k)."
    ),
    "777 Fever": (
        "[Req: 1 Joker + 3 Any Classes]\n"
        "TP: 20% | Deals caster Lv x 7 fixed damage to all foes. May Paralyze."
    ),
    "Gimme Gold": (
        "[Req: 5 Different Final Classes]\n"
        "TP: 14% | Multiplies total gold earned from battle by 4x."
    ),
    "Death Beam": (
        "[Req: 1 Papillon or Joker + 2 Any Classes]\n"
        "TP: 11% | Instantly eliminates 1 random combatant (friend or foe)."
    ),
    "Apocrypha": (
        "[Req: 1 Gun user + 3 Any Classes]\n"
        "TP: 25% | Long-range firearm strike to 1 foe. Debuffs enemy Phys. DEF."
    ),
    "Anastasia": (
        "[Req: 2 of Valkyrie/Soul Summoner/Papillon]\n"
        "TP: 25% | Summons goddess of life to resurrect and revive all allies."
    ),
    "Jackpot": (
        "[Req: 2 Jokers + 3 Any Classes]\n"
        "TP: 100% | Deals caster Lv x 77 fixed true damage to one target (cap 7623)."
    ),
    "Todokanai Koi": (
        "[Req: 1 Diva (Microphone) + 1 Etoile (Instrument) + 1 Any]\n"
        "TP: 25% | Magic love song damaging all foes. High Petrify chance."
    ),
    "Lots Of Guns": (
        "[Req: 3 Gun users (all in back row)]\n"
        "TP: 20% | Long-range barrage firing 3 to 8 random firearm strikes."
    )
}

arc = PckArchive(r'DungeonTravelers2-2_EN\Data\ENG\Parameter\JoinSkillData.pck')

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "JointSkills"

headers = ["File_Name", "Skill_Name", "Vanilla_Desc", "Modded_Desc", "Status"]
ws.append(headers)

for fname, data in arc.files:
    p_name = int.from_bytes(data[8:12], 'little')
    p_desc = int.from_bytes(data[16:20], 'little')
    name = data[p_name:data.find(b'\x00', p_name)].decode('utf-8', errors='ignore')
    desc = data[p_desc:data.find(b'\x00', p_desc)].decode('utf-8', errors='ignore')
    mod_desc = JOINT_SKILLS_DATA.get(name, desc)
    ws.append([fname, name, desc, mod_desc, "Approved"])

wb.save('mod_project/data_tables/joint_skills.xlsx')
print(f"Successfully generated joint_skills.xlsx with {ws.max_row - 1} entries!")

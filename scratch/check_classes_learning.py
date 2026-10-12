import sys, os
sys.path.insert(0, os.path.abspath('mod_project/tools'))
import skill_tree_data

class_names = [
    'Fighter', 'Paladin', 'Berserker', 'Valkyrie', 'Samurai', 'Dark Lord',
    'Scout', 'Archer', 'Assassin', 'Sniper', 'Treasure Hunter', 'Kunoichi',
    'Magic User', 'Sorceress', 'Enchantress', 'Priestess', 'Witch', 'Magical Princess',
    'Sage', 'Bishop', 'Maid', 'Bard', 'Dancer', 'Diva',
    'Mistress', 'Etoile', 'Spieler', 'Doll Master', 'Trickster', 'Soul Summoner',
    'Papillon', 'Joker'
]

for s in skill_tree_data.skills():
    if s['name'] in ['Warning Shot', 'First Grid']:
        cnames = [class_names[cid] if cid < len(class_names) else str(cid) for cid in s['classes']]
        print(f"{s['name']} (ID {s['id']}): learned by {cnames} (raw class IDs: {s['classes']})")

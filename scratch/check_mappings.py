import os
import sys
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim import scenario
from sim import setup as setup_mod
from sim.data import game_data
from sim.variant import balance_data

d = game_data()
bd = balance_data(d)
s = setup_mod.load()

# Class mappings:
# Tier 1 (Base):
#  0: Fighter
#  6: Scout
# 12: Magic User
# 20: Maid
# 26: Spieler
# Tier 2 (Intermediate):
#  1: Paladin
#  2: Berserker
#  7: Archer
#  8: Assassin
# 13: Sorceress
# 14: Enchantress
# 15: Priestess
# 21: Bard
# 22: Dancer
# 27: Doll Master
# 28: Trickster

TIER1_CLASSES = {
    0: 'Fighter',
    6: 'Scout',
    12: 'Magic User',
    20: 'Maid',
    26: 'Spieler'
}

TIER2_CLASSES = {
    1: 'Paladin',
    2: 'Berserker',
    7: 'Archer',
    8: 'Assassin',
    13: 'Sorceress',
    14: 'Enchantress',
    15: 'Priestess',
    21: 'Bard',
    22: 'Dancer',
    27: 'Doll Master',
    28: 'Trickster'
}

# Roles that correspond to these classes at base and intermediate levels
# From sim_setup.xlsx Roles:
# 'tank' -> Fighter -> Paladin -> Valkyrie
# 'attacker' -> Fighter -> Berserker -> Samurai
# 'dark lord' -> Fighter -> Berserker -> Dark Lord
# 'shooter' -> Scout -> Archer -> Sniper
# 'treasure hunter' -> Scout -> Assassin -> Treasure Hunter
# 'kunoichi' -> Scout -> Assassin -> Kunoichi
# 'mage' -> Magic User -> Sorceress -> Witch
# 'magical princess' -> Magic User -> Sorceress -> Magical Princess
# 'sage' -> Magic User -> Enchantress -> Sage
# 'healer' -> Magic User -> Priestess -> Bishop
# 'maid' -> Maid -> Bard -> Diva
# 'diva' -> Maid -> Bard -> Diva
# 'mistress' -> Maid -> Bard -> Mistress
# 'etoile' -> Maid -> Dancer -> Etoile
# 'dolls' -> Spieler -> Doll Master -> Papillon
# 'soul summoner' -> Spieler -> Doll Master -> Soul Summoner
# 'trickster'/'joker' -> Spieler -> Trickster -> Joker

ROLES_MAP = {
    # Tier 1 Base:
    'Fighter': ['tank', 'attacker'],
    'Scout': ['shooter', 'treasure hunter'],
    'Magic User': ['mage', 'healer'],
    'Maid': ['maid', 'diva'],
    'Spieler': ['dolls', 'joker'],
    # Tier 2 Intermediate:
    'Paladin': ['tank'],
    'Berserker': ['attacker', 'dark lord'],
    'Archer': ['shooter'],
    'Assassin': ['treasure hunter', 'kunoichi'],
    'Sorceress': ['mage', 'magical princess'],
    'Enchantress': ['sage'],
    'Priestess': ['healer'],
    'Bard': ['maid', 'diva'],
    'Dancer': ['etoile'],
    'Doll Master': ['dolls', 'soul summoner'],
    'Trickster': ['papillon', 'joker']
}

def extract_class_details(data_source, cid):
    cname = data_source.class_names[cid]
    skills = [s for s in data_source.skills.values() if cid in s.classes]
    skill_list = []
    for sk in sorted(skills, key=lambda x: (x.category, x.id)):
        skill_list.append({
            'id': sk.id,
            'name': sk.name,
            'category': sk.category,
            'levels': sk.levels,
            'tp_cost': sk.tp,
            'sp_cost': sk.sp,
            'weapons': sk.weapons
        })
    return {
        'id': cid,
        'name': cname,
        'skills': skill_list
    }

print("Base mappings defined!")

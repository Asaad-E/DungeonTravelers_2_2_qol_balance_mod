import os

# 1. Update parallel_party_battery.py
path1 = 'mod_project/tools/parallel_party_battery.py'
with open(path1, 'r', encoding='utf-8') as f:
    text1 = f.read()

old1 = """    'Anti-Meta': {
        'desc': 'Anti-Meta Experimental (Magical Princess, Mistress, Soul Summoner, Joker, Dolls)',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'joker', 'dolls'],
        'opt': '25% (Blacklist)'
    }
}"""

new1 = """    'Anti-Meta': {
        'desc': 'Anti-Meta Experimental (Magical Princess, Mistress, Soul Summoner, Joker, Dolls)',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'joker', 'dolls'],
        'opt': '25% (Blacklist)'
    },
    'Juggernaut-Plus': {
        'desc': 'Physical Juggernaut + Diva (Paladin, Berserker, Dark Lord, Kunoichi, Diva)',
        'roles': ['tank', 'attacker', 'dark lord', 'kunoichi', 'diva'],
        'opt': '80% (Juggernaut+)'
    },
    'Anti-Meta-Plus': {
        'desc': 'Anti-Meta + Diva (Magical Princess, Mistress, Soul Summoner, Dolls, Diva)',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'dolls', 'diva'],
        'opt': '60% (Anti-Meta+)'
    }
}"""

assert old1 in text1, 'old1 not found'
text1 = text1.replace(old1, new1, 1)

with open(path1, 'w', encoding='utf-8') as f:
    f.write(text1)

print('Updated parallel_party_battery.py!')

# 2. Update party_battery.py
path2 = 'mod_project/tools/party_battery.py'
with open(path2, 'r', encoding='utf-8') as f:
    text2 = f.read()

old2 = """    'Anti-Meta (Blacklist)': {
        'desc': 'Classes GameFAQs says "AVOID": Mistress (whips), Kunoichi, Magical Princess, Soul Summoner, Valkyrie',
        'opt': '25% (Blacklist)',
        'roles': ['mistress', 'kunoichi', 'magical princess', 'soul summoner', 'valkyrie', 'tank']
    }
}"""

new2 = """    'Anti-Meta (Blacklist)': {
        'desc': 'Classes GameFAQs says "AVOID": Mistress (whips), Kunoichi, Magical Princess, Soul Summoner, Valkyrie',
        'opt': '25% (Blacklist)',
        'roles': ['mistress', 'kunoichi', 'magical princess', 'soul summoner', 'valkyrie', 'tank']
    },
    'Juggernaut-Plus': {
        'desc': 'Physical Juggernaut + Diva (Paladin, Berserker, Dark Lord, Kunoichi, Diva)',
        'opt': '80% (Juggernaut+)',
        'roles': ['tank', 'attacker', 'dark lord', 'kunoichi', 'diva']
    },
    'Anti-Meta-Plus': {
        'desc': 'Anti-Meta + Diva (Magical Princess, Mistress, Soul Summoner, Dolls, Diva)',
        'opt': '60% (Anti-Meta+)',
        'roles': ['magical princess', 'mistress', 'soul summoner', 'dolls', 'diva']
    }
}"""

assert old2 in text2, 'old2 not found'
text2 = text2.replace(old2, new2, 1)

with open(path2, 'w', encoding='utf-8') as f:
    f.write(text2)

print('Updated party_battery.py!')

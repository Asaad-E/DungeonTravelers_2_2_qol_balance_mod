with open('mod_project/sim/battle.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. MiniUP
s1 = '                                 enchant=min(50, 3 * unit.pieces(39) + 2 * unit.pieces(40)),\n                                 target_enchant=min(50, 3 * target.pieces(43) + 2 * target.pieces(44)),'
r1 = '                                 enchant=min(50, 3 * unit.pieces(39) + unit.pieces(40)),\n                                 target_enchant=min(50, 3 * target.pieces(43) + target.pieces(44)),'
assert s1 in text, 's1 not found'
text = text.replace(s1, r1, 1)

# 2. Second physical clamp
s2 = "        elif roll == 'physical':\n            chance = f.clamp(chance, f.HIT_MIN, f.HIT_MAX)"
r2 = "        if roll == 'physical':\n            chance = f.clamp(chance, f.HIT_MIN, f.HIT_MAX)"
assert s2 in text, 's2 not found'
text = text.replace(s2, r2, 1)

# 3. Ailment int truncation and flat penalty
s3 = '        chance = f.ailment_chance(value, resistance)\n        if chance <= 0 or self.rng.randrange(100) >= chance:'
r3 = '        flat_penalty = 15.0 if (target.pieces(269) > 0 and index == 4) else 0.0\n        chance = int(f.ailment_chance(value, resistance, flat_penalty=flat_penalty))\n        if chance <= 0 or self.rng.randrange(100) >= chance:'
assert s3 in text, 's3 not found'
text = text.replace(s3, r3, 1)

with open('mod_project/sim/battle.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated sim/battle.py successfully!')

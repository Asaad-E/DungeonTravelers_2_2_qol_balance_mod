"""What the bonus of each party skill is worth: the reference party plays four late bosses without it and with its
full bonus (the bound of the sheet PartySkillBounds of qol_rules.xlsx: every proof gathered) on as many of its members
as the skill needs, the first of the party. The skill gives its bonus to the members that form it and to nobody else
(atwiki dt2-2 page 72), so this measures the bonus, not who can form it. Variant; nothing is written but the result.

    python party_skills.py run k/n [runs]     writes party_skills_k.json beside this file
    python party_skills.py report             PARTY_SKILLS.md beside this file
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

PLACES = ('C36', 'C38', 'C40', 'P24')
RESIST = {'slash': 0, 'stab': 1, 'bash': 2, 'fire': 3, 'water': 4, 'wind': 5, 'earth': 6, 'lightning': 7}
# skill: (members it needs, {what: bonus at every proof}); from the sheet PartySkills of qol_party_skill_text.xlsx
SKILLS = {
    'Full of Guts': (4, {'hp': 100}), 'Vigor Trio': (3, {'atk': 32}), 'Kindred Spirits': (4, {'tp': 50, 'fire': 20}),
    'Veteran Soldiers': (2, {'slash': 25}), 'Attentive': (3, {'int': 20}), 'Libra Guard': (3, {'def': 25}),
    'Vagabonds': (3, {'agi': 20}), 'Beyond Human': (3, {'stab': 20}), 'NegaPosi': (4, {'hp': 50, 'tp': 50}),
    'Dark and Light': (3, {'res': 20}), 'Natural Klutzes': (2, {'bash': 20}), 'Eccentrics': (3, {'dex': 32}),
    'Flawless Poise': (3, {'water': 20, 'earth': 20}), 'Celebrities': (3, {'lightning': 50}),
    'Sales Experience': (4, {'wind': 20, 'agi': 10}), 'Royal Squadron': (4, {'bash': 10, 'earth': 20}),
    'Graceful Agers': (4, {'lightning': 20, 'hp': 50}), 'Mission Ongoing': (4, {'fire': 10, 'atk': 20}),
    'Board Members': (3, {'dex': 20, 'agi': 20}), 'The New Magi': (3, {'tp': 50, 'fire': 20}),
}


def play(data, setup, cid, skill, runs):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)

    def party():
        units = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        if skill:
            count, bonus = SKILLS[skill]
            for u in [u for u in units if u.kind == 'member'][:count]:
                for what, amount in bonus.items():
                    if what == 'hp':
                        u.max_hp_base += amount
                        u.hp = u.max_hp
                    elif what == 'tp':
                        u.max_tp += amount
                        u.tp = u.max_tp
                    elif what in RESIST:
                        u.resist_base[RESIST[what]] += amount
                    else:
                        u.base[what] += amount
        return units

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    res = scenario.play(data, setup, party, enemies, runs=runs)
    won = [r for r in res if r['won']]
    return {'won': len(won) / len(res), 'time': sum(r['time'] for r in won) / len(won) if won else None,
            'hp_left': sum(r['hp_left'] for r in res) / len(res)}


def run(part, runs=100):
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    names = [None] + sorted(SKILLS)
    out = []
    for name in names[(k - 1) * len(names) // n: k * len(names) // n]:
        cells = {cid: play(data, setup, cid, name, int(runs)) for cid in PLACES}
        out.append({'skill': name, 'cells': cells})
        print(name, {c: round(v['won'], 2) for c, v in cells.items()}, flush=True)
    with open(os.path.join(HERE, f'party_skills_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def report():
    rows = []
    for name in glob.glob(os.path.join(HERE, 'party_skills_*.json')):
        with open(name, encoding='utf-8') as f:
            rows += json.load(f)
    base = next(r for r in rows if r['skill'] is None)['cells']
    scored = []
    for r in rows:
        if r['skill'] is None:
            continue
        wins = sum(r['cells'][c]['won'] - base[c]['won'] for c in PLACES) / len(PLACES)
        lengths = [1 - r['cells'][c]['time'] / base[c]['time'] for c in PLACES if r['cells'][c]['time'] and base[c]['time']]
        hp = sum(r['cells'][c]['hp_left'] - base[c]['hp_left'] for c in PLACES) / len(PLACES)
        count, bonus = SKILLS[r['skill']]
        scored.append((wins + sum(lengths) / len(lengths), r['skill'], count,
                       ', '.join(f'{k} +{v}' for k, v in bonus.items()), wins, sum(lengths) / len(lengths), hp))
    lines = ['# What the bonus of each party skill is worth (generated by measures/party_skills.py)', '',
             f"The reference party at {', '.join(PLACES)}, with the full bonus on as many members as the skill needs, "
             'against the same party without it. Sorted by wins and length gained.', '',
             '| Party skill | Members | Bonus at every proof | Wins | Fights shorter | HP left |', '|---|---|---|---|---|---|']
    for _, name, count, bonus, wins, length, hp in sorted(scored, reverse=True):
        lines.append(f'| {name} | {count} | {bonus} | {wins * 100:+.0f} | {length:+.0%} | {hp * 100:+.0f} |')
    with open(os.path.join(HERE, 'PARTY_SKILLS.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    for line in lines[4:]:
        print(line)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'run': run, 'report': report}[sys.argv[1]](*sys.argv[2:])

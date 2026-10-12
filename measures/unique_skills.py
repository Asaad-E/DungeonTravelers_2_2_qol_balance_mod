"""What the unique skill of each girl adds: the reference party with her in its last place, in the role the guides
give her, with her unique skill and without it, on the variant. At three bosses of the end of the story (rank 5 - 6 of
the skill), a postgame boss (rank 9) and a harder one with every member crowned (the EX value).

Positive Trance reads Pep, which the simulator holds at 100: Alisia is played at the Pep of the row PEP (the guides
say hers stays high while she fights). Nothing is written but the result.

    python unique_skills.py run k/n [runs]     writes unique_skills_k.json beside this file
    python unique_skills.py report             UNIQUE_SKILLS.md beside this file
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

# girl -> the role she is played in (the class the guides recommend for her unique skill)
ROLES = {'Luco': 'dark lord', 'Yae': 'dark lord', 'Grishna': 'attacker', 'Alisia': 'attacker', 'Siena': 'magical princess',
         'Irena': 'mage', 'Eltricia': 'magical princess', 'Fiora': 'healer', 'Melvy': 'magical princess',
         'Tsurara': 'treasure hunter', 'Monica': 'shooter', 'Souffle': 'treasure hunter', 'Yuni': 'diva',
         'Conette': 'mistress', 'Ist': 'etoile', 'Lizerietta': 'papillon', 'Mefmera': 'papillon', 'Lilian': 'soul summoner'}
# (checkpoint, crown bonus of every member)
PLACES = (('C36', 0), ('C38', 0), ('C40', 0), ('P24', 0), ('P27', 50))
PEP = {'Alisia': 130.0}


def play(data, setup, cid, crown, girl, with_skill, runs):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}
    role = ROLES[girl]

    def party():
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, crown, cp['Floor'])
        members = [u for u in whole if u.kind == 'member' and u.name != girl]
        kept = members[:4]
        # without: the same girl with no unique skill at all, so that what it gives her stats is left out too
        who = chars[girl] if with_skill else dict(chars[girl], unique_skill=None)
        tested = scenario.build_role_member(data, setup, role, who, level, gear, crown,
                                            scenario.forge_open(setup, cp['Floor']), None,
                                            pieces=scenario.unique_pieces(setup, role, cp['Chapter'], cp['Floor']),
                                            sealbook=scenario.personal_sealbook(setup, role, cp['Chapter'], cp['Floor']))
        tested.items = kept[0].items if kept else {}
        tested.pep = PEP.get(girl, tested.pep)
        return kept + [tested] + [u for u in whole if u.kind != 'member']

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    res = scenario.play(data, setup, party, enemies, runs=runs)
    won = [r for r in res if r['won']]
    return {'won': len(won) / len(res), 'time': sum(r['time'] for r in won) / len(won) if won else None,
            'hp_left': sum(r['hp_left'] for r in res) / len(res)}


def run(part, runs=60):
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    girls = sorted(ROLES)
    out = []
    for girl in girls[(k - 1) * len(girls) // n: k * len(girls) // n]:
        unique = next(c for c in data.characters if c['name'] == girl)['unique_skill']
        row = {'girl': girl, 'role': ROLES[girl], 'skill': data.unique[unique]['name'], 'values': data.unique[unique]['values'],
               'cells': []}
        for cid, crown in PLACES:
            a = play(data, setup, cid, crown, girl, False, int(runs))
            b = play(data, setup, cid, crown, girl, True, int(runs))
            row['cells'].append({'checkpoint': cid, 'crown': crown, 'without': a, 'with': b})
            print(girl, cid, crown, a, b, flush=True)
        out.append(row)
    with open(os.path.join(HERE, f'unique_skills_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def report():
    rows = []
    for name in glob.glob(os.path.join(HERE, 'unique_skills_*.json')):
        with open(name, encoding='utf-8') as f:
            rows += json.load(f)
    scored = []
    for r in rows:
        cells, wins, lengths, hps = [], [], [], []
        for c in r['cells']:
            a, b = c['without'], c['with']
            wins.append(b['won'] - a['won'])
            hps.append(b['hp_left'] - a['hp_left'])
            length = 1 - b['time'] / a['time'] if a['time'] and b['time'] else None
            if length is not None:
                lengths.append(length)
            cells.append(f"{a['won']:.0%} > {b['won']:.0%}" + (f" ({length:+.0%})" if length is not None else ''))
        mean = lambda xs: sum(xs) / len(xs) if xs else 0.0          # noqa: E731
        scored.append((mean(wins), r, cells, mean(lengths), mean(hps)))
    scored.sort(key=lambda s: -(s[0] + s[3]))
    head = ' | '.join(f"{cid}{' crowned' if crown else ''}" for cid, crown in PLACES)
    lines = ['# What each unique skill adds (generated by measures/unique_skills.py)', '',
             'The reference party with the girl in its last place, without her unique skill > with it: wins, and in '
             'brackets how much shorter the won fights are with it. Variant; sorted by the mean of wins and length gained.', '',
             f'| Girl | Unique skill | Role | {head} | Wins, mean | Length, mean | HP left, mean |',
             '|---|---|---|' + '---|' * (len(PLACES) + 3)]
    for wins, r, cells, length, hp in scored:
        lines.append(f"| {r['girl']} | {r['skill']} | {r['role']} | " + ' | '.join(cells) +
                     f" | {wins * 100:+.0f} | {length:+.0%} | {hp * 100:+.0f} |")
    with open(os.path.join(HERE, 'UNIQUE_SKILLS.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    for line in lines[4:]:
        print(line)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'run': run, 'report': report}[sys.argv[1]](*sys.argv[2:])

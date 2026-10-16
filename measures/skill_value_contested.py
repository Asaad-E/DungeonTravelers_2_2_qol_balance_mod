"""The skills docs/generated/SKILL_VALUE.md leaves "to read", measured where a skill that protects can show: the
bosses the reference party does not win every time. tools/skill_value.py plays the first stage of the class, where
the party wins 100% with or without the skill, and counts wins and length only; here each skill is played at the
contested bosses below with the same two parties (with the skill used where it serves, without it), and the HP the
party ends with counts too.

    python skill_value_contested.py run k/n [runs]     writes skill_value_contested_k.json beside this file
    python skill_value_contested.py report             SKILL_VALUE_CONTESTED.md beside this file
    python skill_value_contested.py engine k/n [runs]  the same as `run`, played by the C# engine (engine_cs/)
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import skill_value                                        # noqa: E402
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.battle import AILMENTS                           # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

CONTESTED = ('C30', 'C38', 'C40', 'P24')     # the reference party wins 92%, 92%, 92% and 98% of them on the variant
NOT_BATTLE = {'Gold Steal': 'gold, not the fight', 'Item Steal': 'drops, not the fight',
              'Experience Paean': 'EXP, not the fight'}
ENGINE = False                               # `engine`: the battles are played by the C# engine
WINS, LENGTH, HP = 0.08, 0.03, 0.03          # what counts as serving: 8 points of wins, 3% of length, 3 points of HP left


def to_read():
    names = []
    with open(skill_value.REPORT, encoding='utf-8') as f:
        for line in f:
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) == 6 and cells[5] == 'to read':
                names.append((cells[0], cells[1].split(' (')[0]))
    return names


def run(part, runs=30):
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    setup.settings['check_runs'] = int(runs)
    names = to_read()
    out = []
    for name, role in names[(k - 1) * len(names) // n: k * len(names) // n]:
        skill = next(s for s in data.skills.values() if s.name == name and s.classes)
        row = {'skill': name, 'role': role, 'cells': []}
        if name in NOT_BATTLE:
            row['kind'] = NOT_BATTLE[name]
        elif any(e in AILMENTS and kind != 2 for e, kind, _ in skill.effects):
            row['kind'] = 'ailment'
        else:
            levels = scenario.reference_levels(data, setup)
            for cid in CONTESTED:
                learnable = set(scenario.classes_so_far(data, setup.roles[role], levels[cid][0]))
                if not set(skill.classes) & learnable:
                    continue
                without = (skill_value.play_engine if ENGINE else skill_value.play)(data, setup, role, cid, skill, False)
                with_it = (skill_value.play_engine if ENGINE else skill_value.play)(data, setup, role, cid, skill, True)
                row['cells'].append({'checkpoint': cid, 'without': without, 'with': with_it})
        out.append(row)
        print(name, role, len(row['cells']), flush=True)
    with open(os.path.join(HERE, f'skill_value_contested_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def run_engine(part='all', runs=30):
    if part == 'all':                          # every part at once, one process each
        import engine_client
        engine_client.all_parts(__file__, os.path.join(HERE, 'skill_value_contested_*.json'), extra=(runs, ))
        return
    global ENGINE
    ENGINE = True
    try:
        run(part, runs)
    finally:
        ENGINE = False


def report():
    rows = []
    for name in glob.glob(os.path.join(HERE, 'skill_value_contested_*.json')):
        with open(name, encoding='utf-8') as f:
            rows += json.load(f)
    rows.sort(key=lambda r: r['skill'])
    lines, tally = [], {}
    for r in rows:
        if r.get('kind'):
            verdict = 'see SKILL_AILMENTS.md' if r['kind'] == 'ailment' else 'out of the fight: ' + r['kind']
            best = '-'
        elif not r['cells']:
            verdict, best = 'not learnt by the role at these bosses', '-'
        else:
            found = []
            for c in r['cells']:
                a, b = c['without'], c['with']
                wins = b['won'] - a['won']
                length = 1 - b['time_won'] / a['time_won'] if a['time_won'] and b['time_won'] else 0.0
                hp = b['hp_left'] - a['hp_left']
                found.append((max(wins / WINS, length / LENGTH, hp / HP), c['checkpoint'], wins, length, hp))
            score, cid, wins, length, hp = max(found)
            verdict = 'serves' if score >= 1 else 'nothing shown'
            best = f'{cid}: wins {wins:+.0%}, length {length:+.0%}, HP left {hp * 100:+.0f} points'
        key = verdict.split(':')[0]
        tally[key] = tally.get(key, 0) + 1
        lines.append(f"| {r['skill']} | {r['role']} | {best} | {verdict} |")
    text = ['# The support skills left "to read", at the contested bosses (generated by measures/skill_value_contested.py)', '',
            f"Bosses: {', '.join(CONTESTED)}. Each skill with and without, as tools/skill_value.py plays it; the best of its "
            f'bosses is shown. Serves: {WINS:.0%} of wins, {LENGTH:.0%} of length or {HP * 100:.0f} points of the HP the party '
            'ends with.', '',
            '**' + '; '.join(f'{v} {k}' for k, v in sorted(tally.items(), key=lambda kv: -kv[1])) + f' (of {len(rows)}).**', '',
            '| Skill | Played as | Best boss | Verdict |', '|---|---|---|---|'] + lines
    with open(os.path.join(HERE, 'SKILL_VALUE_CONTESTED.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(text) + '\n')
    print(text[4])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'run': run, 'engine': run_engine, 'report': report}[sys.argv[1]](*sys.argv[2:])

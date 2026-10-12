"""The six support skills that show nothing at the contested bosses (SKILL_VALUE_CONTESTED.md beside this file): each
with and without, as tools/skill_value.py plays it, on the variant and with its value, its length in turns or its TP
cost changed. A trial to be decided on; nothing is written.

    python six_candidates.py "Aim" [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import skill_value                                        # noqa: E402
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

# skill -> (role, the effect its value is)
SKILLS = {'Aim': ('shooter', 166), 'Evade': ('shooter', 164), 'Attract': ('dark lord', 170),
          'Light Scroll': ('kunoichi', 166), 'Shadow Clone': ('kunoichi', 101), 'Perdurabo': ('soul summoner', 232)}
BOSSES = ('C38', 'C40', 'P24')
# label -> (factor on the value, turns added, factor on the TP cost)
TRIALS = {'as built': (1.0, 0, 1.0), 'value x1.5': (1.5, 0, 1.0), 'TP x0.5': (1.0, 0, 0.5), 'turns +3': (1.0, 3, 1.0),
          'all three': (1.5, 3, 0.5)}


def changed(data, name, effect, value, turns, tp):
    key, s = next((k, s) for k, s in data.skills.items() if s.name == name and s.classes)
    changes = [('skills', key, 'effects', [(e, k, [v * value for v in vals] if e == effect else vals)
                                           for e, k, vals in s.effects]),
               ('skills', key, 'tp', [max(1, int(t * tp)) for t in s.tp])]
    if turns and s.turns and any(s.turns):
        changes.append(('skills', key, 'turns', [t + turns for t in s.turns]))
    return data.with_changes(changes)


def main():
    name = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    role, effect = SKILLS[name]
    base, setup = balance_data(game_data()), setup_mod.load()
    setup.settings['check_runs'] = runs
    levels = scenario.reference_levels(base, setup)
    for label, (value, turns, tp) in TRIALS.items():
        data = changed(base, name, effect, value, turns, tp)
        skill = next(s for s in data.skills.values() if s.name == name and s.classes)
        cells = []
        for cid in BOSSES:
            if not set(skill.classes) & set(scenario.classes_so_far(data, setup.roles[role], levels[cid][0])):
                continue
            a = skill_value.play(data, setup, role, cid, skill, False)
            b = skill_value.play(data, setup, role, cid, skill, True)
            length = 1 - b['time_won'] / a['time_won'] if a['time_won'] and b['time_won'] else 0.0
            cells.append(f"{cid} wins {b['won'] - a['won']:+.0%} length {length:+.0%} HP {(b['hp_left'] - a['hp_left']) * 100:+.0f}")
        print(f'{name} | {label} | ' + ' | '.join(cells), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

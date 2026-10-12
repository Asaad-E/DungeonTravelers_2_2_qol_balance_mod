"""What a mercenary does in the model: her actions counted over the fights of a checkpoint, and the damage and the
healing the log gives her. A reading aid for mercenaries.py.

    python mercenary_log.py Marion C40 [runs]
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import mercenaries                                         # noqa: E402
from sim import battle as battle_mod, setup as setup_mod   # noqa: E402
from sim.data import game_data                             # noqa: E402
from sim.variant import balance_data                       # noqa: E402

LOGS = []
_init = battle_mod.Battle.__init__


def logged(self, *args, **kwargs):
    _init(self, *args, **kwargs)
    self.log = []
    LOGS.append(self.log)


HEALED = collections.Counter()
CASTS = collections.Counter()
_heal = battle_mod.Battle.heal


def heal(self, action, target, effect, value):
    before = target.hp
    _heal(self, action, target, effect, value)
    actor = action.actor
    who = actor.owner.name + ' (doll)' if actor.kind == 'doll' and actor.owner is not None else actor.name
    if target.hp > before or effect in (103, 104, 106):
        HEALED[who, target.kind] += target.hp - before
        CASTS[who, target.kind] += 1


def main():
    battle_mod.Battle.heal = heal
    name, cid = sys.argv[1], sys.argv[2]
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    battle_mod.Battle.__init__ = logged
    data, setup = balance_data(game_data()), setup_mod.load()
    print(mercenaries.play(data, setup, cid, name, runs))
    acts, dealt, hits = collections.Counter(), collections.Counter(), collections.Counter()
    for log in LOGS:
        mine = None
        for line in log:
            if line.startswith('          ->'):
                if mine and ' takes ' in line:
                    amount = line.split(' takes ')[1].split(',')[0].split(' ')[0]
                    try:
                        dealt[mine] += int(amount)
                        hits[mine] += 1
                    except ValueError:
                        pass
                continue
            who = line[8:].split(' (')[0]
            mine = line.rsplit(': ', 1)[1] if who == name else None
            if mine:
                acts[mine] += 1
    for key, count in acts.most_common():
        print(f'{key}: {count / runs:.1f} per fight, {dealt[key] / max(1, hits[key]):.0f} per hit over {hits[key] / runs:.1f} hits')
    for (who, kind), amount in sorted(HEALED.items()):
        if who.startswith(name):
            print(f'healing by {who} on a {kind}: {amount / runs:.0f} HP per fight over {CASTS[who, kind] / runs:.1f} heals')
    for line in [l for log in LOGS[:1] for l in log if name in l][:12]:
        print(line[:200])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

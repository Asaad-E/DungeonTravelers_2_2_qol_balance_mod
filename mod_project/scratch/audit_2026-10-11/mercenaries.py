"""What each mercenary adds (rows J13 and F94 of the register, never measured): the reference party at three bosses
with no guest, with the summon of its grand sealbook, and with each mercenary in the place of that summon, at the
stage of her growth whose level is the highest not above the party's. A mercenary is built as the summon is: a unit of
the party side with the stats, the attacks and the script of her record (tools/npc_data.py), which the enemy AI plays;
her delay is taken from the weapon rank index of the record (0x1C, not followed in the code: an assumption), and the
attack of her field 0x98 is taken as a passive when it is one. Variant; nothing is written but the result.

    python mercenaries.py run k/n [runs]     writes mercenaries_k.json beside this file
    python mercenaries.py report             MERCENARIES.md beside this file
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import battle as battle_mod, scenario, setup as setup_mod      # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.units import Unit, STATS, PARTY                  # noqa: E402
from sim.variant import balance_data                      # noqa: E402

PLACES = ('C36', 'C40', 'P24')
DOLL_EFFECTS = (228, 229, 230, 231, 232, 233)
DOLL_LEVEL = [None]         # None: the lowest level at which the doll skill of a member gives the same life; else that level
_make_doll = battle_mod.Battle.make_doll


def guest_doll(self, action):
    """The doll of a guest: her attack names the doll by its effect (228 - 233) and its life (147), not by the id of
    the skill of the Doll Master, which is how the model finds a doll. What level its hidden action is read at is not
    read in the program: DOLL_LEVEL says the assumption."""
    owner = action.actor
    doll = next((d for d in self.data.dolls if d['effect'] is not None and action.has(d['effect'])), None)
    if owner.kind == 'member' or doll is None or doll['effect'] not in DOLL_EFFECTS:
        return _make_doll(self, action)
    life = int(action.value(147, 3))
    level = DOLL_LEVEL[0] or next((k + 1 for k, t in enumerate(doll['turns']) if t >= life), len(doll['turns']))
    for u in [u for u in self.units if u.owner is owner and u.kind == 'doll' and u.alive]:
        self.remove_doll(u)
    unit = battle_mod.build_doll(owner, doll, level, self.data)
    unit.arrow = False
    unit.life = life
    unit.position = len(self.units)
    unit.next_time = self.time + self.wait(unit)
    self.units.append(unit)


# sim/battle.py builds the doll of a guest itself since 2026-10-12 (make_guest_doll): the patch above is kept for DOLL_LEVEL
if DOLL_LEVEL[0]:
    battle_mod.Battle.make_doll = guest_doll


def build(data, record):
    unit = Unit(record['name'], PARTY, record['level'], record['hp'], 0, {s: record[s] for s in STATS},
                weight=data.weapon_ranks.get(record['raw_1c'], 2.0), kind='summon')
    unit.attacks = list(record['attacks'])
    unit.script = record['script']
    extra = data.attacks.get(record['extra_attack'])
    if extra is not None and getattr(extra, 'passive', False):
        for effect, _, value in extra.effects:
            unit.passives[effect] = value
    return unit


def stage(data, name, level):
    mine = sorted((r for r in data.npcs if r['name'] == name), key=lambda r: r['level'])
    under = [r for r in mine if r['level'] <= level]
    return (under or mine)[-1 if under else 0]


def play(data, setup, cid, guest, runs):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)

    def party():
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        if guest == 'summon':
            return whole
        members = [u for u in whole if u.kind == 'member']
        return members if guest is None else members + [build(data, stage(data, guest, level))]

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    res = scenario.play(data, setup, party, enemies, runs=runs)
    won = [r for r in res if r['won']]
    return {'won': len(won) / len(res), 'time': sum(r['time'] for r in won) / len(won) if won else None,
            'hp_left': sum(r['hp_left'] for r in res) / len(res)}


def run(part, runs=60):
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    names = [None, 'summon'] + sorted({r['name'] for r in data.npcs})
    out = []
    for name in names[(k - 1) * len(names) // n: k * len(names) // n]:
        cells = {}
        for cid in PLACES:
            try:
                cells[cid] = play(data, setup, cid, name, int(runs))
            except Exception as error:                     # a record the model cannot play: said, not hidden
                cells[cid] = {'error': f'{type(error).__name__}: {error}'}
        level = scenario.reference_levels(data, setup)['C40'][0]
        out.append({'guest': name, 'cells': cells,
                    'level': stage(data, name, level)['level'] if name not in (None, 'summon') else None})
        print(name, {c: (round(v['won'], 2) if 'won' in v else v['error'][:60]) for c, v in cells.items()}, flush=True)
    with open(os.path.join(HERE, f'mercenaries_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def report():
    rows = []
    for name in glob.glob(os.path.join(HERE, 'mercenaries_*.json')):
        with open(name, encoding='utf-8') as f:
            rows += json.load(f)
    base = next(r for r in rows if r['guest'] is None)['cells']
    scored, failed = [], []
    for r in rows:
        if r['guest'] is None:
            continue
        if any('error' in c for c in r['cells'].values()):
            failed.append(r['guest'])
            continue
        wins = sum(r['cells'][c]['won'] - base[c]['won'] for c in PLACES) / len(PLACES)
        lengths = [1 - r['cells'][c]['time'] / base[c]['time'] for c in PLACES if r['cells'][c]['time'] and base[c]['time']]
        hp = sum(r['cells'][c]['hp_left'] - base[c]['hp_left'] for c in PLACES) / len(PLACES)
        scored.append((wins + (sum(lengths) / len(lengths) if lengths else 0), r['guest'], wins,
                       sum(lengths) / len(lengths) if lengths else 0, hp,
                       ' '.join(f"{r['cells'][c]['won']:.0%}" for c in PLACES)))
    lines = ['# What each mercenary adds (generated by scratch/audit_2026-10-11/mercenaries.py)', '',
             f"The reference party at {', '.join(PLACES)} with the guest, against the same party with none "
             f"({' '.join(f'{base[c]}' if False else format(base[c]['won'], '.0%') for c in PLACES)} of wins).", '',
             '| Guest | Wins at the three | Wins, mean | Fights shorter | HP left |', '|---|---|---|---|---|']
    for _, name, wins, length, hp, cells in sorted(scored, reverse=True):
        lines.append(f"| {'the summon of the grand sealbook' if name == 'summon' else name} | {cells} | {wins * 100:+.0f} | {length:+.0%} | {hp * 100:+.0f} |")
    if failed:
        lines += ['', 'Not played (the model failed on their record): ' + ', '.join(failed)]
    with open(os.path.join(HERE, 'MERCENARIES.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    for line in lines[2:]:
        print(line)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'run': run, 'report': report}[sys.argv[1]](*sys.argv[2:])

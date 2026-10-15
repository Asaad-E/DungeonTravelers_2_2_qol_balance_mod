"""The random battles along the game, vanilla against the variant: at the floor of every checkpoint of the difficulty
curve the reference party, at its reference level, plays rows of eight random battles of the floor in a row (HP and
TP carried over, as a stretch of dungeon between two rests; the groups are those of the zones of the floor, drawn as
sim/measures.py random_group draws them, the same rows on both sides).

    python random_battles.py run k/n [rows]     writes random_battles_k.json beside this file
    python random_battles.py report             RANDOM_BATTLES.md beside this file
    python random_battles.py engine [rows]      the same as `run` for every floor, played by the C# engine (engine_cs/) in one call
"""
import glob
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import difficulty_curve                                   # noqa: E402
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

CHAIN = 8
AHEAD = 12


def play(data, setup, cid, rows):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    zones = [z for z in data.floors if z['name'].split(' zone')[0] == cp['Floor'] and z['formations']] or \
            [z for z in data.floors if z['name'][:4] == cp['Floor'][:4] and z['formations']]
    if not zones:
        return None
    # a floor may hold a zone that opens later in the story (Prizren Woods holds one of level 68 beside its zones of
    # level 40): the zones whose enemies stand more than AHEAD levels over the party are left out
    probe = random.Random(5)
    near = [z for z in zones if max(u.level for _ in range(12) for u in measures.random_group(data, z, probe)) <= level + AHEAD]
    zones = near or zones
    rng = random.Random(11)

    def party():
        return scenario.reference_party(data, setup, cp['Chapter'], level, gear, int(cp['Crown bonus'] or 0), cp['Floor'])

    def enemies():
        return [measures.random_group(data, rng.choice(zones), rng) for _ in range(CHAIN)]

    res = scenario.play(data, setup, party, enemies, runs=rows)
    won = [r for r in res if r['won']]
    return {'level': level, 'won': len(won) / len(res),
            'time': sum(r['time'] for r in won) / len(won) / CHAIN if won else None,
            'hp_left': sum(r['hp_left'] for r in res) / len(res)}


def zones_of(data, setup, cid):
    """The zones play() draws from (None when the floor has none)."""
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    zones = [z for z in data.floors if z['name'].split(' zone')[0] == cp['Floor'] and z['formations']] or \
            [z for z in data.floors if z['name'][:4] == cp['Floor'][:4] and z['formations']]
    if not zones:
        return None
    probe = random.Random(5)
    near = [z for z in zones if max(u.level for _ in range(12) for u in measures.random_group(data, z, probe)) <= level + AHEAD]
    return near or zones


def jobs_engine(data, setup, cid, rows, side, name):
    """The job of the C# engine that plays what play() plays (None when the floor has no zone)."""
    import engine_client as engine
    zones = zones_of(data, setup, cid)
    if zones is None:
        return None
    return engine.make_job(side, cid, runs=rows, setup=engine.setup_of(setup), name=name,
                           enemies={'kind': 'chain', 'zones': [z['name'] for z in zones], 'seed': 11, 'battles': CHAIN})


def figures_engine(data, setup, cid, done):
    res = done['runs']
    won = [r for r in res if r['won']]
    return {'level': scenario.reference_levels(data, setup)[cid][0], 'won': len(won) / len(res),
            'time': sum(r['time'] for r in won) / len(won) / CHAIN if won else None,
            'hp_left': sum(r['hp_left'] for r in res) / len(res)}


def run_engine(rows=20):
    """run() for every floor, played by the C# engine; written as the one part 1."""
    import engine_client as engine
    vanilla, setup = game_data(), setup_mod.load()
    variant = balance_data(vanilla)
    rows = int(rows)
    ids = difficulty_curve.checkpoints(setup)
    jobs, index = [], {}
    for cid in ids:
        for tag, data in (('vanilla', vanilla), ('variant', variant)):
            job = jobs_engine(data, setup, cid, rows, engine.side_of(data), f'{cid}|{tag}')
            if job is not None:
                index[(cid, tag)] = len(jobs)
                jobs.append(job)
    done = engine.run_jobs(jobs)
    out = []
    for cid in ids:
        a = figures_engine(vanilla, setup, cid, done[index[(cid, 'vanilla')]]) if (cid, 'vanilla') in index else None
        b = figures_engine(variant, setup, cid, done[index[(cid, 'variant')]]) if (cid, 'variant') in index else None
        out.append({'id': cid, 'vanilla': a, 'variant': b})
        print(cid, a, b, flush=True)
    for name in glob.glob(os.path.join(HERE, 'random_battles_*.json')):
        os.remove(name)
    with open(os.path.join(HERE, 'random_battles_1.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def run(part, rows=20):
    k, n = (int(x) for x in part.split('/'))
    vanilla, setup = game_data(), setup_mod.load()
    variant = balance_data(vanilla)
    ids = difficulty_curve.checkpoints(setup)
    out = []
    for cid in ids[(k - 1) * len(ids) // n: k * len(ids) // n]:
        a, b = play(vanilla, setup, cid, int(rows)), play(variant, setup, cid, int(rows))
        out.append({'id': cid, 'vanilla': a, 'variant': b})
        print(cid, a, b, flush=True)
    with open(os.path.join(HERE, f'random_battles_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


def report():
    rows = []
    for name in glob.glob(os.path.join(HERE, 'random_battles_*.json')):
        with open(name, encoding='utf-8') as f:
            rows += json.load(f)
    order = {cid: k for k, cid in enumerate(difficulty_curve.checkpoints(setup_mod.load()))}
    rows = sorted((r for r in rows if r['vanilla']), key=lambda r: order[r['id']])
    lines = ['# Random battles along the game, vanilla against the variant (generated by measures/random_battles.py)', '',
             f'Rows of {CHAIN} random battles in a row at the floor of each checkpoint, the reference party at its reference '
             'level. Rows survived; mean length of a battle of the rows survived; share of HP the party ends the row with.', '',
             '| Floor of | Level | Rows survived | Length of a battle | HP left |', '|---|---|---|---|---|']
    shorter = []
    for r in rows:
        a, b = r['vanilla'], r['variant']
        length = f"{a['time']:.1f} > {b['time']:.1f}" if a['time'] and b['time'] else '-'
        if a['time'] and b['time']:
            shorter.append(1 - b['time'] / a['time'])
        lines.append(f"| {r['id']} | {a['level']} | {a['won']:.0%} > {b['won']:.0%} | {length} | {a['hp_left']:.0%} > {b['hp_left']:.0%} |")
    mean = sum(shorter) / len(shorter) if shorter else 0.0
    lines.insert(4, f'**{len(rows)} floors; a battle is {mean:.0%} shorter on the variant in the mean '
                    f'({min(shorter):.0%} to {max(shorter):.0%}).**')
    lines.insert(5, '')
    with open(os.path.join(HERE, 'RANDOM_BATTLES.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print(lines[4])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'run': run, 'engine': run_engine, 'report': report}[sys.argv[1]](*sys.argv[2:])

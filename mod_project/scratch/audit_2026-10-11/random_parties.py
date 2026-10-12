"""The random battles of one floor with every party (the reference party and those of the sheet BatteryParties):
rows of eight in a row, as random_battles.py beside this file plays them, in vanilla, on the variant, and on the
variant with the HP or the ATK and INT of the enemies of the floor's zones times a factor. A trial; nothing written.

    python random_parties.py C40 [rows] [party]
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import random_battles                                     # noqa: E402
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

# label -> (factor on HP, factor on ATK and INT) of the enemies of the floor, over the variant
TRIALS = {'HP x1.15': (1.15, 1.0), 'HP x1.3': (1.3, 1.0), 'ATK and INT x1.1': (1.0, 1.1), 'ATK and INT x1.2': (1.0, 1.2),
          'HP x1.15, ATK and INT x1.1': (1.15, 1.1)}


def zones_of(data, setup, cid):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    zones = [z for z in data.floors if z['name'].split(' zone')[0] == cp['Floor'] and z['formations']] or \
            [z for z in data.floors if z['name'][:4] == cp['Floor'][:4] and z['formations']]
    probe = random.Random(5)
    near = [z for z in zones if max(u.level for _ in range(12) for u in measures.random_group(data, z, probe))
            <= level + random_battles.AHEAD]
    return near or zones


def play(data, setup, cid, roles, rows):
    cp = setup.checkpoint(cid)
    zones = zones_of(data, setup, cid)
    rng = random.Random(11)

    def party():
        if roles is None:
            level = scenario.reference_levels(data, setup)[cid][0]
            return scenario.reference_party(data, setup, cp['Chapter'], level, scenario.checkpoint_gear(data, setup, cid),
                                            int(cp['Crown bonus'] or 0), cp['Floor'])
        return scenario.party_of_roles(data, setup, cid, roles)

    def enemies():
        return [measures.random_group(data, rng.choice(zones), rng) for _ in range(random_battles.CHAIN)]

    res = scenario.play(data, setup, party, enemies, runs=rows)
    return f"{sum(r['won'] for r in res) / len(res):.0%} / {sum(r['hp_left'] for r in res) / len(res):.0%}"


def main():
    cid = sys.argv[1]
    rows = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    vanilla, setup = game_data(), setup_mod.load()
    variant = balance_data(vanilla)
    ids = {e for z in zones_of(variant, setup, cid) for f in z['formations'] for e, _ in f['enemies'] if e in variant.enemies}
    sides = {'vanilla': vanilla, 'variant': variant}
    for label, (hp, attack) in TRIALS.items():
        changes = []
        for e in ids:
            enemy = variant.enemies[e]
            changes += [('enemies', e, 'hp', int(enemy['hp'] * hp)), ('enemies', e, 'atk', int(enemy['atk'] * attack)),
                        ('enemies', e, 'int', int(enemy['int'] * attack))]
        sides[label] = variant.with_changes(changes)
    print(cid, len(ids), 'enemies of the floor | rows survived / HP left | ' + ' | '.join(sides), flush=True)
    only = sys.argv[3] if len(sys.argv) > 3 else None          # one party, to split a long run over processes
    for name, roles in [('reference', None)] + [(n, v[1]) for n, v in setup.battery.items()]:
        if only and name != only:
            continue
        print(f'{cid} | {name} | ' + ' | '.join(play(source, setup, cid, roles, rows) for source in sides.values()), flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

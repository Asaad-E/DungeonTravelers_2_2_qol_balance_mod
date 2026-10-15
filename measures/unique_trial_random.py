"""The same trial as unique_trial.py on random battles: rows of eight in a row at the floor of a checkpoint (the zones
random_parties.py keeps), the girl in the last place of the reference party. Nothing is written.

    python unique_trial_random.py Lilian C36 2 3 [rows]
    (add --engine to play the battles on the C# engine, engine_cs/)
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import random_parties                                     # noqa: E402
import unique_skills                                      # noqa: E402
from sim import measures, scenario, setup as setup_mod    # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

CHAIN = 8


def engine_runs(data, setup, cid, girl, role, factor, zones, rows):
    """The runs scenario.play gives for one trial, played by the C# engine."""
    import engine_client as engine
    cp = setup.checkpoint(cid)
    tested = {'role': role, 'character': girl, 'no_unique': factor is None, 'forge': bool(scenario.forge_open(setup, cp['Floor']))}
    recipe = {'name_not': girl, 'first': 4, 'items': 'first_kept', 'tested': [tested]}
    return engine.play(engine.make_job(engine.side_of(data), cid, runs=rows, crown=0, setup=engine.setup_of(setup), recipe=recipe,
                                       name=f'{girl}|{cid}|{factor}',
                                       enemies={'kind': 'chain', 'zones': [z['name'] for z in zones], 'seed': 11, 'battles': CHAIN}))


def main():
    engine = '--engine' in sys.argv
    if engine:
        sys.argv.remove('--engine')
    girl, cid = sys.argv[1], sys.argv[2]
    numbers = [float(a) for a in sys.argv[3:]]
    rows = int(numbers[-1]) if numbers and numbers[-1] > 10 else 60
    factors = [a for a in numbers if a <= 10]
    base, setup = balance_data(game_data()), setup_mod.load()
    uid = next(c for c in base.characters if c['name'] == girl)['unique_skill']
    values = base.unique[uid]['values']
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(base, setup)[cid][0]
    gear = scenario.checkpoint_gear(base, setup, cid)
    role = unique_skills.ROLES[girl]
    for label, factor in [('without', None), ('as built', 1.0)] + [(f'x{f:g}', f) for f in factors]:
        data = base if factor in (None, 1.0) else base.with_changes(
            [('unique', uid, 'values', [round(v * factor, 4) for v in values])])
        chars = {c['name']: c for c in data.characters}
        zones = random_parties.zones_of(data, setup, cid)
        rng = random.Random(11)

        def party():
            whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
            kept = [u for u in whole if u.kind == 'member' and u.name != girl][:4]
            who = chars[girl] if factor is not None else dict(chars[girl], unique_skill=None)
            tested = scenario.build_role_member(data, setup, role, who, level, gear, 0,
                                                scenario.forge_open(setup, cp['Floor']), None)
            tested.items = kept[0].items if kept else {}
            return kept + [tested] + [u for u in whole if u.kind != 'member']

        def enemies():
            return [measures.random_group(data, rng.choice(zones), rng) for _ in range(CHAIN)]

        res = engine_runs(data, setup, cid, girl, role, factor, zones, rows) if engine else scenario.play(data, setup, party, enemies, runs=rows)
        won = [r for r in res if r['won']]
        length = sum(r['time'] for r in won) / len(won) / CHAIN if won else 0.0
        print(f"{girl} {cid} | {label} | rows survived {len(won) / len(res):.0%} | length of a battle {length:.2f} | "
              f"HP left {sum(r['hp_left'] for r in res) / len(res):.0%}", flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

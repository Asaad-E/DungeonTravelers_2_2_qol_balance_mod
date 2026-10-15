"""A mercenary tried with her stats scaled, or the worth of her healing: the reference party at a checkpoint with her
as mercenaries.py plays her, each stat named multiplied by its factor on every stage of her growth. With 'without=role'
the member of that role leaves the party first (the healer, to see what the healing of a guest holds up alone).
Variant; nothing is written.

    python mercenary_trial.py Marion C40 100 atk=1.5 dex=1.5
    python mercenary_trial.py Natalia C40 100 without=diva
    python mercenary_trial.py none C40 100 without=diva
    (add --engine to play the battles on the C# engine, engine_cs/)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import mercenaries                                         # noqa: E402
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402


def main():
    engine = '--engine' in sys.argv
    if engine:
        sys.argv.remove('--engine')
    name, cid, runs = sys.argv[1], sys.argv[2], int(sys.argv[3])
    factors = dict(a.split('=') for a in sys.argv[4:])
    without = factors.pop('without', None)
    data, setup = balance_data(game_data()), setup_mod.load()
    for record in data.npcs:
        if record['name'] == name:
            for stat, factor in factors.items():
                record[stat] = int(record[stat] * float(factor))
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)

    def party():
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        if name == 'summon':
            return [u for u in whole if getattr(u, 'role', None) != without]
        members = [u for u in whole if u.kind == 'member' and getattr(u, 'role', None) != without]
        return members if name == 'none' else members + [mercenaries.build(data, mercenaries.stage(data, name, level))]

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    if engine:
        import engine_client
        res = engine_client.play(engine_client.make_job(
            engine_client.side_of(data), cid, runs=runs, crown=0, setup=engine_client.setup_of(setup), name=f'{name}|{cid}',
            guest=None if name == 'summon' else 'none' if name == 'none' else name, recipe={'role_not': without} if without else None))
    else:
        res = scenario.play(data, setup, party, enemies, runs=runs)
    won = [r for r in res if r['won']]
    print(f"{name} {cid} {' '.join(sys.argv[4:]) or 'as she is'} | won {len(won) / len(res):.0%} | length "
          f"{sum(r['time'] for r in won) / len(won) if won else 0:.1f} | HP left "
          f"{sum(r['hp_left'] for r in res) / len(res):.0%}", flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

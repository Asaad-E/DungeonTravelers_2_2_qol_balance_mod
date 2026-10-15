"""Which records make a party win so much more on the variant: the party at a boss on the variant with the rows of one
group taken out, against the whole variant and the game. A group is a name and the texts that pick its rows: a row
belongs when one of them is in its record, or is the name of its table. Nothing is written.

    python measures/record_causes.py Meta C26;C30;C38 200 "Graceful Rose" "SP curve=sp_curve" "Protect=194 Protect|Circle Protect"
    (add --engine to play the cells on the C# engine, engine_cs/)
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import win_rates                                          # noqa: E402

ENGINE = False                               # --engine: the battles are played by the C# engine
_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod, variant
        from sim.data import game_data
        _STATE.update(setup=setup_mod.load(), vanilla=game_data(), rows=variant.rows(), variant=variant)
    return _STATE


def picked(row, texts):
    return any(t == str(row['Table']) or t in str(row['Record']) for t in texts)


def cell(task):
    party, cid, label, texts, runs = task
    from sim import scenario
    state = _load()
    variant = state['variant']
    if label == 'game':
        data, count = state['vanilla'], 0
    else:
        rows = [r for r in state['rows'] if not picked(r, texts)]
        count = len(state['rows']) - len(rows)
        data = variant.apply(state['vanilla'], rows)
        data.arcane_chance = variant.arcane_chance()
        data.interrupt_product = variant.interrupt_product()
    roles = [r.strip() for r in win_rates.PARTIES[party][0].split(';')]
    res = (__import__('engine_client').play_party_sim if ENGINE else scenario.play_party)(data, state['setup'], cid, roles, runs)
    won = [r for r in res if r['won']]
    return label, cid, len(won) / len(res), sum(r['time'] for r in won) / len(won) if won else 0, count


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    party, bosses, runs = sys.argv[1], sys.argv[2].split(';'), int(sys.argv[3])
    groups = [('game', ()), ('variant', ())]
    for arg in sys.argv[4:]:
        label, _, texts = arg.partition('=')
        groups.append((label, tuple((texts or label).split('|'))))
    tasks = [(party, c, label, texts, runs) for label, texts in groups for c in bosses]
    with (__import__('engine_client').SerialPool() if ENGINE else ProcessPoolExecutor(12)) as pool:
        at = {(label, c): (w, t, n) for label, c, w, t, n in pool.map(cell, tasks)}
    print(f'{party}: wins (length) on the variant without the rows of the group')
    for label, _ in groups:
        print(f'  {label:22s} {at[(label, bosses[0])][2]:4d} rows | '
              + ' | '.join(f'{c} {at[(label, c)][0]:.0%} ({at[(label, c)][1]:.0f}t)' for c in bosses))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

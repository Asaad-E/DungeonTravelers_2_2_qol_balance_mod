"""What some rows of balance_changes.xlsx do: the reference party and the parties of measures/win_rates.py at the
bosses given, on the variant and on the variant without those rows (named by their ids, or by the start of an id).
Nothing is written.

    python measures/rows_trial.py P031,P032 C30;C36;C38;C40 150
    python measures/rows_trial.py P038 P23 150
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


def cell(task):
    party, cid, without, ids, runs = task
    from sim import measures, scenario, setup as setup_mod, variant
    from sim.data import game_data
    if not _STATE:
        _STATE.update(vanilla=game_data(), setup=setup_mod.load(), rows=variant.rows())
    rows = [r for r in _STATE['rows'] if not (without and str(r['ID']) in ids)]
    data = variant.apply(_STATE['vanilla'], rows)
    data.arcane_chance = variant.arcane_chance()
    data.interrupt_product = variant.interrupt_product()
    if party == 'reference':
        res = (__import__('engine_client').play_checkpoint_sim if ENGINE else measures.play_checkpoint)(data, _STATE['setup'], cid, runs)[1]
        return party, cid, without, res['won'], res['time'] or 0, res['lowest_hp']
    roles = [r.strip() for r in win_rates.PARTIES[party][0].split(';')]
    res = (__import__('engine_client').play_party_sim if ENGINE else scenario.play_party)(data, _STATE['setup'], cid, roles, runs)
    won = [r for r in res if r['won']]
    return (party, cid, without, len(won) / len(res), sum(r['time'] for r in won) / len(won) if won else 0,
            sum(r['lowest_hp'] for r in res) / len(res))


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    ids, bosses, runs = tuple(sys.argv[1].split(',')), sys.argv[2].split(';'), int(sys.argv[3])
    parties = ['reference'] + list(win_rates.PARTIES)
    tasks = [(p, c, w, ids, runs) for p in parties for c in bosses for w in (True, False)]
    with (__import__('engine_client').SerialPool() if ENGINE else ProcessPoolExecutor(12)) as pool:
        at = {(p, c, w): (won, t, low) for p, c, w, won, t, low in pool.map(cell, tasks)}
    print(f"without {', '.join(ids)} > with: wins (length, lowest HP), {runs} battles")
    for p in parties:
        print(f'  {p:16s} ' + ' | '.join(
            f'{c} {at[(p, c, True)][0]:.0%} > {at[(p, c, False)][0]:.0%} ({at[(p, c, True)][1]:.0f} > {at[(p, c, False)][1]:.0f}t, '
            f'{at[(p, c, True)][2]:.0%} > {at[(p, c, False)][2]:.0%})' for c in bosses))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

"""What the power of Graceful Rose (rows S001, S002) is worth: the Meta party of measures/win_rates.py, and the
Papillon alone in the reference party (tools/class_stages.py), on the variant with each power given. Nothing is written.

    python measures/graceful_rose_trial.py C26;C29;C30;C38;C40 200 0.8 0.6 0.5 0.2
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

SKILL, POWER = 'Graceful Rose', 26
ENGINE = False                               # --engine: the battles are played by the C# engine
_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod
        from sim.data import game_data
        from sim.variant import balance_data
        _STATE.update(setup=setup_mod.load(), variant=balance_data(game_data()))
    return _STATE


def cell(task):
    who, cid, power, runs = task
    import class_stages
    from sim import scenario
    state = _load()
    data, setup = state['variant'], state['setup']
    skill = next(s for s in data.skills.values() if s.name == SKILL)
    kept = skill.effects
    skill.effects = [(e, k, [power] * len(v) if e == POWER else v) for e, k, v in kept]
    try:
        if who == 'Meta':
            roles = [r.strip() for r in win_rates.PARTIES[who][0].split(';')]
            res = (__import__('engine_client').play_party_sim if ENGINE else scenario.play_party)(data, setup, cid, roles, runs)
            won = [r for r in res if r['won']]
            out = len(won) / len(res), sum(r['time'] for r in won) / len(won) if won else 0
        else:
            res = (class_stages.play_engine if ENGINE else class_stages.play)(data, setup, cid, who, runs)
            out = res['won'], res['time']
    finally:
        skill.effects = kept
    return who, cid, power, out


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    bosses, runs, powers = sys.argv[1].split(';'), int(sys.argv[2]), [float(x) for x in sys.argv[3:]]
    tasks = [(w, c, p, runs) for w in ('Meta', 'papillon') for c in bosses for p in powers]
    with (__import__('engine_client').SerialPool() if ENGINE else ProcessPoolExecutor(12)) as pool:
        at = {(w, c, p): out for w, c, p, out in pool.map(cell, tasks)}
    for w in ('Meta', 'papillon'):
        print(w)
        for p in powers:
            print(f'  power {p:<5} ' + ' | '.join(f'{c} {at[(w, c, p)][0]:.0%} ({at[(w, c, p)][1]:.0f}t)' for c in bosses))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

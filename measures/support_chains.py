"""The supports and tanks measured where they show: a row of random battles of a floor, fought one after another with
the HP and TP carried over, and what the party has left at the end. Each role takes the last place of the reference
party of a checkpoint and walks the floor of that checkpoint; an attacker in the same place is the control (what the
party has left with no support there). Balance variant.

    python measures/support_chains.py [battles in a row, 8] [rows a cell, 40]     writes SUPPORT_CHAINS.md beside this file
    python measures/support_chains.py [battles in a row, 8] [rows a cell, 40] --engine     the same, played by the C# engine (engine_cs/)
"""
import os
import random
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))

CONTROL = 'attacker'
ENGINE = False                               # --engine: the cells are played by the C# engine
_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod
        from sim.data import game_data
        from sim.variant import balance_data
        _STATE.update(data=balance_data(game_data()), setup=setup_mod.load())
    return _STATE


def cell_engine(task):
    """cell(), played by the C# engine."""
    cid, role, chain, runs = task
    import engine_client as engine
    from sim import scenario
    state = _load()
    data, setup = state['data'], state['setup']
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    zones = scenario.walked_zones(data, setup, cp['Floor'], level)
    recipe = {'drop_last': True, 'items': 'first_kept', 'tested': [{'role': role, 'forge': bool(scenario.forge_open(setup, cp['Floor']))}]}
    job = engine.make_job(engine.side_of(data), cid, runs=runs, crown=0, setup=engine.setup_of(setup), recipe=recipe,
                          options={'random_battle': True}, name=f'{cid}|{role}|{chain}',
                          enemies={'kind': 'chain', 'zones': [z['name'] for z in zones], 'seed': 7, 'battles': chain})
    res = engine.run_jobs([job])[0]['runs']
    done = [r for r in res if r['won']]
    return cid, role, {'won': len(done) / len(res),
                       'hp': sum(r['hp_left'] for r in done) / len(done) if done else 0.0,
                       'tp': sum(r['tp_left'] for r in done) / len(done) if done else 0.0,
                       'fought': sum(len(r['parts']) for r in res) / len(res),
                       'time': sum(r['time'] for r in done) / len(done) if done else 0.0}


def cell(task):
    if ENGINE:
        return cell_engine(task)
    cid, role, chain, runs = task
    from sim import measures, scenario
    state = _load()
    data, setup = state['data'], state['setup']
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}
    names = [n.strip() for n in str(setup.roles[role]['Characters (order of preference)']).split(';')]

    def party():
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        kept = [u for u in whole if u.kind == 'member'][:-1]
        taken = {u.name for u in kept}
        base = scenario.class_id(data, setup.roles[role]['Base class'])
        who = next((n for n in names if n in chars and n not in taken), None) or \
            next(c['name'] for c in data.characters if c['name'] not in taken and c['base_class'] == base)
        tested = scenario.build_role_member(data, setup, role, chars[who], level, gear, 0,
                                            scenario.forge_open(setup, cp['Floor']))
        for u in kept:
            tested.items = u.items
        return kept + [tested] + [u for u in whole if u.kind != 'member']

    zones = scenario.walked_zones(data, setup, cp['Floor'], level)
    rng = random.Random(7)                       # the same rows of battles for every role

    def enemies():
        return [measures.random_group(data, rng.choice(zones), rng) for _ in range(chain)]

    res = scenario.play(data, setup, party, enemies, runs=runs, battle_setup={'random_battle': True})
    done = [r for r in res if r['won']]
    return cid, role, {'won': len(done) / len(res),
                       'hp': sum(r['hp_left'] for r in done) / len(done) if done else 0.0,
                       'tp': sum(r['tp_left'] for r in done) / len(done) if done else 0.0,
                       'fought': sum(len(r['parts']) for r in res) / len(res),
                       'time': sum(r['time'] for r in done) / len(done) if done else 0.0}


def judged(setup, data):
    """{stage: ([checkpoints], [(role, class at the stage, kind)])}: the supports and tanks, and the control."""
    import class_stages
    from sim import scenario
    by_class = class_stages.kinds()
    levels = scenario.reference_levels(data, setup)
    found = {}
    for st in class_stages.stages(setup):
        cids = [c.strip() for c in str(st['Checkpoints']).split(';')]
        roles = []
        for role, row in setup.roles.items():
            cls = data.class_names[scenario.class_path(data, row, levels[cids[-1]][0])[0]]
            kind = 'support' if by_class.get(row['Lv30 class']) == 'support' else by_class.get(cls, 'attacker')
            if kind in ('support', 'tank') or role == CONTROL:
                roles.append((role, cls, 'control' if role == CONTROL else kind))
        found[st['Stage']] = (cids, roles)
    return found


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    chain = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    state = _load()
    plan = judged(state['setup'], state['data'])
    tasks = [(c, role, chain, runs) for cids, roles in plan.values() for c in cids for role, _, _ in roles]
    with (__import__('engine_client').SerialPool() if ENGINE else ProcessPoolExecutor(12)) as pool:
        at = {(c, role): res for c, role, res in pool.map(cell, tasks)}
    out = ['# Supports and tanks over a row of random battles (generated by measures/support_chains.py)', '',
           f'Balance variant. {chain} random battles of the floor of each checkpoint in a row, HP and TP carried over, '
           f'{runs} rows a cell, the same rows for every role. Each role in the last place of the reference party. Cells: '
           'rows walked to the end / HP the party has left / TP it has left. The last columns: the mean over the checkpoints '
           f'of the HP and the TP left, as points above the party with an {CONTROL} in that place (the control).', '']
    for stage, (cids, roles) in plan.items():
        out += [f'## {stage} ({", ".join(cids)})', '',
                '| Role | Class | Kind | ' + ' | '.join(cids) + ' | HP left against the control | TP left against the control |',
                '|' + '---|' * (5 + len(cids))]
        for role, cls, kind in roles:
            mine = [at[(c, role)] for c in cids]
            cells = ' | '.join(f"{m['won']:.0%} / {m['hp']:.0%} / {m['tp']:.0%}" for m in mine)
            hp = statistics.mean(at[(c, role)]['hp'] - at[(c, CONTROL)]['hp'] for c in cids)
            tp = statistics.mean(at[(c, role)]['tp'] - at[(c, CONTROL)]['tp'] for c in cids)
            out.append(f'| {role} | {cls} | {kind} | {cells} | {hp * 100:+.0f} | {tp * 100:+.0f} |')
        out.append('')
    with open(os.path.join(HERE, 'SUPPORT_CHAINS.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

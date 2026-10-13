"""Which rows make a party win so much more on the variant: the party at a boss with each family of rows of
balance_changes.xlsx taken out alone, and with the game given that family alone (a family is the letter its row ids
start with), against the whole variant and against the game. The family whose removal brings the share of wins back down is what lifted it. Nothing is written
but the result.

    python measures/win_causes.py run Meta C26;C30;C38 200 [processes]     writes win_causes_<party>.json
    python measures/win_causes.py report Meta
"""
import collections
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import win_rates                                          # noqa: E402

_STATE = {}


def _load():
    if not _STATE:
        from sim import setup as setup_mod, variant
        from sim.data import game_data
        _STATE.update(setup=setup_mod.load(), vanilla=game_data(), rows=variant.rows(), variant=variant)
    return _STATE


def cell(task):
    party, cid, family, runs = task
    from sim import scenario
    state = _load()
    variant = state['variant']
    if family == 'game':
        data = state['vanilla']
    else:
        if family.startswith('only '):                  # the game with this family alone
            rows = [r for r in state['rows'] if str(r['ID']).startswith(family[5:])]
        else:
            rows = [r for r in state['rows'] if family == 'variant' or not str(r['ID']).startswith(family)]
        data = variant.apply(state['vanilla'], rows)
        data.arcane_chance = variant.arcane_chance()
        data.interrupt_product = variant.interrupt_product()
    roles = [r.strip() for r in win_rates.PARTIES[party][0].split(';')]
    res = scenario.play_party(data, state['setup'], cid, roles, runs)
    won = [r for r in res if r['won']]
    return {'id': cid, 'family': family, 'won': len(won) / len(res), 'time': sum(r['time'] for r in won) / len(won) if won else None}


def run(party, bosses, runs=200, processes=12):
    state = _load()
    letters = sorted({str(r['ID'])[0] for r in state['rows']})
    families = ['game', 'variant'] + letters + ['only ' + k for k in letters]
    tasks = [(party, c.strip(), f, int(runs)) for f in families for c in bosses.split(';')]
    with ProcessPoolExecutor(int(processes)) as pool:
        cells = list(pool.map(cell, tasks))
    counts = collections.Counter(str(r['ID'])[0] for r in state['rows'])
    tables = {k: sorted({str(r['Table']) for r in state['rows'] if str(r['ID']).startswith(k)}) for k in counts}
    with open(os.path.join(HERE, f'win_causes_{party}.json'), 'w', encoding='utf-8') as f:
        json.dump({'cells': cells, 'rows': counts, 'tables': tables}, f, indent=1)
    print(len(cells), 'cells')


def report(party):
    with open(os.path.join(HERE, f'win_causes_{party}.json'), encoding='utf-8') as f:
        found = json.load(f)
    at = {(c['family'], c['id']): c for c in found['cells']}
    bosses = sorted({c['id'] for c in found['cells']})
    print(f'{party}: share of wins with one family of rows taken out (difference from the whole variant)')
    print('family | rows | ' + ' | '.join(bosses))
    letters = sorted(found['rows'])
    for family in ['game', 'variant'] + letters + ['only ' + k for k in letters]:
        key = family[5:] if family.startswith('only ') else family
        label = family if family in ('game', 'variant') else f"{family} {'/'.join(found['tables'][key])}"
        cells = ' | '.join(f"{at[(family, c)]['won']:.0%} ({(at[(family, c)]['won'] - at[('variant', c)]['won']) * 100:+.0f})"
                           for c in bosses)
        print(f"{label} | {found['rows'].get(family[5:] if family.startswith('only ') else family, '')} | {cells}")


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    {'run': run, 'report': report}[sys.argv[1]](*sys.argv[2:])

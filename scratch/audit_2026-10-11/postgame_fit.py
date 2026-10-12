"""The postgame bosses the variant leaves easier than vanilla at the same preparation (postgame_compare.py beside this
file, over 15 points of wins): for each, the vanilla party and the variant party again over more battles, and the
variant with the HP of the enemies of the fight times each factor. A proposal ; nothing is written.

    python postgame_fit.py k/n [runs]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
sys.path.insert(0, HERE)
import postgame_compare                                   # noqa: E402
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

FACTORS = (1.1, 1.2, 1.3)


def main():
    k, n = (int(x) for x in sys.argv[1].split('/'))
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    data, setup = game_data(), setup_mod.load()
    variant = balance_data(data)
    rows = []
    for name in sorted(os.listdir(HERE)):
        if name.startswith('postgame_compare_') and name.endswith('.json'):
            with open(os.path.join(HERE, name), encoding='utf-8') as f:
                rows += json.load(f)
    easier = sorted((r for r in rows if r['vanilla']['won'] >= r['floor'] and
                     r['variant']['won'] - r['vanilla']['won'] > 0.15), key=lambda r: r['id'])
    out = []
    for r in easier[(k - 1) * len(easier) // n: k * len(easier) // n]:
        cid, crown = r['id'], r['crown']
        cp = setup.checkpoint(cid)
        ids = {eid for number in scenario.battle_numbers(cp)
               for b in data.fixed if b['floor'] == cp['Floor'] and b['number'] == number for eid, _ in b['enemies']}
        cells = {'vanilla': postgame_compare.play(data, setup, cid, crown, runs),
                 'variant': postgame_compare.play(variant, setup, cid, crown, runs)}
        for factor in FACTORS:
            harder = variant.with_changes([('enemies', e, 'hp', int(variant.enemies[e]['hp'] * factor)) for e in ids])
            cells[f'HP x{factor}'] = postgame_compare.play(harder, setup, cid, crown, runs)
        out.append({'id': cid, 'boss': r['boss'], 'crown': crown, 'cells': cells})
        print(cid, r['boss'], 'crown', crown, '| ' + ' | '.join(
            f"{label} {c['won']:.0%} / {c['time'] or 0:.1f}" for label, c in cells.items()), flush=True)
    with open(os.path.join(HERE, f'postgame_fit_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

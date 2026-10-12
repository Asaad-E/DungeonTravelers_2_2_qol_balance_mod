"""What each piece of preparation is worth at the postgame bosses the reference party loses (vanilla data): the win
share under a crown bonus, a factor on max HP and a cut of the damage taken, alone and together. A trial to choose
what to model, nothing is written.

    python postgame_levers.py k/n [runs]      the k-th of n slices of the checkpoints below their floor
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import guide_curve                                        # noqa: E402
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402

# (label, crown bonus, factor on max HP, pieces of "received damage DOWN" (enchantment 70) on each member)
TRIALS = (('base', 0, 1.0, 0), ('crown 50', 50, 1.0, 0), ('HP x1.5', 0, 1.5, 0), ('cut x3', 0, 1.0, 3),
          ('HP x1.5, cut x3', 0, 1.5, 3), ('all', 50, 1.5, 3))


def main():
    k, n = (int(x) for x in sys.argv[1].split('/'))
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    data, setup = game_data(), setup_mod.load()
    measured = {}
    for name in os.listdir(guide_curve.OUT_DIR):
        with open(os.path.join(guide_curve.OUT_DIR, name), encoding='utf-8') as f:
            measured.update({m['id']: m for m in json.load(f)})
    low = [r['Checkpoint'] for r in guide_curve.sheet(setup) if r['Checkpoint'].startswith('P') and
           measured[r['Checkpoint']]['won'] < float(setup.settings[f"guide_{r['Class']}_min_won"])]
    out = {}
    for cid in low[(k - 1) * len(low) // n: k * len(low) // n]:
        cp = setup.checkpoint(cid)
        level = scenario.reference_levels(data, setup)[cid][0]
        gear = scenario.checkpoint_gear(data, setup, cid)
        cells = {}
        for label, crown, hp, cut in TRIALS:
            def party():
                units = scenario.reference_party(data, setup, cp['Chapter'], level, gear, crown, cp['Floor'])
                for u in units:
                    if u.kind == 'member':
                        u.max_hp_base = int(u.max_hp_base * hp)
                        u.hp = u.max_hp
                        if cut:
                            u.enchants[70] = u.enchants.get(70, 0) + cut
                return units

            def enemies():
                return [scenario.fixed_battle(data, cp['Floor'], b) for b in scenario.battle_numbers(cp)]

            res = scenario.play(data, setup, party, enemies, runs=runs)
            cells[label] = sum(r['won'] for r in res) / len(res)
        out[cid] = cells
        print(cid, ' | '.join(f'{label} {won:.0%}' for label, won in cells.items()), flush=True)
    with open(os.path.join(HERE, f'postgame_levers_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()

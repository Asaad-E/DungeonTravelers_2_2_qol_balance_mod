"""Alluring Samba stronger (the user, 2026-10-12: enough to quicken a fight a little, not to break it): the Etoile in
the last place of the reference party with Waltz and Mazurka, and with Samba in the place of Mazurka at each factor on
its value. Variant; nothing is written.

    python samba_trial.py C40 [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
import class_stages                                       # noqa: E402
from sim import setup as setup_mod                        # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

FACTORS = (1.0, 1.5, 2.0, 2.5)


def main():
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    base, setup = balance_data(game_data()), setup_mod.load()
    usual = setup.policies
    second = [r for r in usual if r['Role'] == 'etoile' and str(r['Action']) == 'status:201'][0]
    key, skill = next((k, s) for k, s in base.skills.items() if s.name == 'Alluring Samba')
    res = class_stages.play(base, setup, cid, 'etoile', runs)
    print(f"{cid} | Waltz + Mazurka | won {res['won']:.0%} | length {res['time']:.1f}", flush=True)
    setup.policies = [dict(r, Action='status:196') if r is second else r for r in usual]
    for factor in FACTORS:
        data = base.with_changes([('skills', key, 'effects', [(e, k, [round(v * factor, 3) for v in vals] if e == 196 else vals)
                                                              for e, k, vals in skill.effects])])
        res = class_stages.play(data, setup, cid, 'etoile', runs)
        print(f"{cid} | Waltz + Samba x{factor:g} ({skill.effects[0][2][-1] * factor:.0%} DEF at the top level) | "
              f"won {res['won']:.0%} | length {res['time']:.1f}", flush=True)
    setup.policies = usual


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

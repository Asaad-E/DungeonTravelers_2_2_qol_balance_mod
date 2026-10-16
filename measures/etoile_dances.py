"""The dances of the Etoile the model never performs (Alluring Samba, Gloomy Tango, Gravitating Polka): she keeps two
dances at a time and her rules of the sheet Policies fill both with Fascinating Waltz and Dumbing Mazurka. Here she is
played in the last place of the reference party with each pair of dances in their place, on the variant. Nothing is
written.

    python etoile_dances.py C40 [runs]
    python etoile_dances.py C40 [runs] --engine     the same, played by the C# engine (engine_cs/)
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

ENGINE = False                               # --engine: the battles are played by the C# engine
DANCES = {'Waltz': 195, 'Samba': 196, 'Tango': 197, 'Polka': 198, 'Salsa': 199, 'Mazurka': 201}
PAIRS = (('Waltz', 'Mazurka'), ('Waltz', 'Salsa'), ('Salsa', 'Mazurka'), ('Samba', 'Waltz'), ('Samba', 'Mazurka'), ('Tango', 'Waltz'), ('Polka', 'Waltz'),
         ('Samba', 'Tango'))


def main():
    global ENGINE
    ENGINE = '--engine' in sys.argv
    if ENGINE:
        sys.argv.remove('--engine')
    cid = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    data, setup = balance_data(game_data()), setup_mod.load()
    usual = setup.policies
    first, second = [r for r in usual if r['Role'] == 'etoile' and str(r['Action']) in ('status:195', 'status:201')]
    for a, b in PAIRS:
        setup.policies = [dict(r, Action=f'status:{DANCES[a]}') if r is first else
                          dict(r, Action=f'status:{DANCES[b]}') if r is second else r for r in usual]
        res = (class_stages.play_engine if ENGINE else class_stages.play)(data, setup, cid, 'etoile', runs)
        print(f"{cid} | {a} + {b} | won {res['won']:.0%} | length {res['time']:.1f}", flush=True)
    setup.policies = usual


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

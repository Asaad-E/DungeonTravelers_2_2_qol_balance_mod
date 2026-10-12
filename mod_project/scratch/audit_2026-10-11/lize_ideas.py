"""Ideas for the unique skill of Lizerietta, the puppeteer (the user, 2026-10-12), tried before anything is
chosen: her dolls act faster (effect 316, the one Double Puppet holds), hit and heal harder (286, the one of Doll
Mastery), or last longer (297, the one of Destiny Line). She is played in the last place of the reference party in a
doll role, with no unique skill, with the one she has, and with each idea (the fourth of 2026-10-12: she is harder to hit, effect 338, read among the evasion buffs of the target of a blow and of a spell, 0x44ac56 and 0x44d8cb). The sizes are on top of what
the passives of her class give. Variant; nothing is written.

    python lize_ideas.py dolls C18 [runs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, PROJECT)
sys.path.insert(0, os.path.join(PROJECT, 'tools'))
from sim import scenario, setup as setup_mod              # noqa: E402
from sim.data import game_data                            # noqa: E402
from sim.variant import balance_data                      # noqa: E402

GIRL = 'Lizerietta'
# label -> (effect added to her passives, amount), or None for no unique skill, 'own' for the one she has
IDEAS = (('no unique skill', None), ('as built', 'own'),
         ('survives a killing blow 0.20', (254, 0.20)), ('survives a killing blow 0.35', (254, 0.35)),
         ('survives a killing blow 0.50', (254, 0.50)))


def main():
    role, cid = sys.argv[1], sys.argv[2]
    runs = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    data, setup = balance_data(game_data()), setup_mod.load()
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}
    for label, idea in IDEAS:
        def party():
            whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
            kept = [u for u in whole if u.kind == 'member' and u.name != GIRL][:4]
            who = chars[GIRL] if idea == 'own' else dict(chars[GIRL], unique_skill=None)
            tested = scenario.build_role_member(data, setup, role, who, level, gear, 0,
                                                scenario.forge_open(setup, cp['Floor']), None,
                                                pieces=scenario.unique_pieces(setup, role, cp['Chapter'], cp['Floor']),
                                                sealbook=scenario.personal_sealbook(setup, role, cp['Chapter'], cp['Floor']))
            tested.items = kept[0].items if kept else {}
            if isinstance(idea, tuple):
                tested.passives[idea[0]] = tested.passives.get(idea[0], 0.0) + idea[1]
            return kept + [tested] + [u for u in whole if u.kind != 'member']

        def enemies():
            return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

        res = scenario.play(data, setup, party, enemies, runs=runs)
        won = [r for r in res if r['won']]
        print(f"{role} {cid} | {label} | won {len(won) / len(res):.0%} | length "
              f"{sum(r['time'] for r in won) / len(won) if won else 0:.1f} | HP left "
              f"{sum(r['hp_left'] for r in res) / len(res):.0%}", flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()

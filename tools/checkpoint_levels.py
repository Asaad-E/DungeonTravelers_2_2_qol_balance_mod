"""
The level curve of the story: the reference level of every checkpoint and the jumps of the curve.

The reference level is the user's decision of 2026-10-07 (assumption A15 of data_tables/sim_setup.xlsx): the level the
guides give (sheet GuideLevels), else the level of the random enemies of the zone where the boss stands, never below
the checkpoint before. A jump is a rise of at least `level_jump_step` levels from one checkpoint to the next, or a boss
at least `boss_gap` levels above its reference (sheet Settings). The mod keeps every jump in its place, none larger
(Regression R03 of data_tables/balance_criteria.xlsx).

    python tools/checkpoint_levels.py        writes docs/generated/CHECKPOINT_LEVELS.md
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sim.data import game_data                      # noqa: E402
from sim import setup as setup_mod, scenario        # noqa: E402

OUTPUT = os.path.join(BASE_DIR, 'docs', 'generated', 'CHECKPOINT_LEVELS.md')
SOURCES = {'guide': 'guide', 'zone': 'zone', 'before': 'checkpoint before'}


def curve(data, setup):
    """[{id, boss, boss_level, zone, guide, level, source, gap, step}] in the order of the sheet Checkpoints."""
    share = float(setup.settings['zone_level_share'])
    levels = scenario.reference_levels(data, setup)
    rows, previous = [], None
    for cp in setup.checkpoints:
        numbers = scenario.battle_numbers(cp)
        bosses = [data.enemies[e]['level'] for n in numbers
                  for b in data.fixed if b['floor'] == cp['Floor'] and b['number'] == n for e, _ in b['enemies']]
        level, source = levels[cp['ID']]
        guide = setup.guide_levels.get(cp['ID'])
        rows.append({'id': cp['ID'], 'boss': cp['Boss (as the story page names it)'], 'boss_level': max(bosses),
                     'zone': scenario.zone_level(data, cp['Floor'], numbers[0], share),
                     'guide': guide, 'level': level, 'source': source,
                     'gap': max(bosses) - level, 'step': None if previous is None else level - previous})
        previous = level
    return rows


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    data, setup = game_data(), setup_mod.load()
    step_mark, gap_mark = int(setup.settings['level_jump_step']), int(setup.settings['boss_gap'])
    rows = curve(data, setup)
    out = ['# Level curve of the story (generated)', '',
           'Written by `tools/checkpoint_levels.py` from the game data and `data_tables/sim_setup.xlsx`. Reference '
           'level: the guides (sheet `GuideLevels`), else the level of the random enemies of the zone where the boss '
           f'stands (the lowest level covering {float(setup.settings["zone_level_share"]):.0%} of its encounters), never '
           'below the checkpoint before (assumption A15, decided by the user on 2026-10-07). Gap: boss level minus '
           'reference. Step: reference minus the reference of the checkpoint before. The mod keeps every jump in its '
           'place and none larger (Regression R03).', '',
           '| Checkpoint | Boss | Boss level | Zone level | Guide | Reference | From | Gap | Step |',
           '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        guide = f"{r['guide']['Range in the guide']} ({r['guide']['Source']})" if r['guide'] else ''
        step = '' if r['step'] is None else f"+{r['step']}"
        out.append(f"| {r['id']} | {r['boss']} | {r['boss_level']} | {r['zone'] if r['zone'] is not None else '-'} | "
                   f"{guide} | {r['level']} | {r['source']} | {r['gap']:+d} | {step} |")
    jumps = [r for r in rows if (r['step'] or 0) >= step_mark or r['gap'] >= gap_mark]
    out += ['', f'## Jumps of vanilla ({len(jumps)})', '',
            f'A rise of {step_mark} levels or more, or a boss {gap_mark} levels or more above its reference.', '',
            '| Checkpoint | Boss | Step | Gap |', '|---|---|---|---|']
    out += [f"| {r['id']} | {r['boss']} | {'' if r['step'] is None else '+' + str(r['step'])} | {r['gap']:+d} |"
            for r in jumps]
    with open(OUTPUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')
    print(f'{len(rows)} checkpoints, {len(jumps)} jumps; written {OUTPUT}')


if __name__ == '__main__':
    main()

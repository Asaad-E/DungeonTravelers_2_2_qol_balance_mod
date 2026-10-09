"""
The measures of phase 2: each turns a row of the sheet Criticisms of balance_criteria.xlsx (or of Regression) into a
number. The sheet Measures of data_tables/sim_setup.xlsx names, for each row, the function of this file that measures
it and its arguments. Every function takes (data, setup, **arguments) and returns a dict of figures.

check_change is the check of a change (phase 1, step 4; BALANCE_PLAN.md principle 3): the story checkpoints the change
touches, each played by the reference party in vanilla and with the change, and the figures of Regression R08 (win
share, length) and R10 (lowest HP of the party, damage of the enemies per action against the party's max HP) set
against the windows of the sheet Settings. Whether the change solves its own row is the measure of that row.
"""
from sim import scenario


def summary(results):
    """The figures of a set of battles of one checkpoint."""
    runs = max(1, len(results))
    wins = [r for r in results if r['won']]
    actions = sum(r['enemy_actions'] for r in results)
    max_hp = sum(r['party_max_hp'] for r in results) / runs
    return {'won': len(wins) / runs,
            'time': sum(r['time'] for r in wins) / len(wins) if wins else None,
            'lowest_hp': sum(r['lowest_hp'] for r in results) / runs,
            'pressure': sum(r['enemy_damage'] for r in results) / actions / max_hp if actions and max_hp else 0.0}


def touched(data, setup, changes):
    """The ids of the checkpoints a change can move: the bosses whose records, attacks or the reference party's
    skills and gear it edits; every checkpoint for a change to anything else (EXP, items, ranks, growth...)."""
    levels = scenario.reference_levels(data, setup)
    found = []
    for cp in setup.checkpoints:
        cid = cp['ID']
        enemies = {e for n in scenario.battle_numbers(cp) for b in data.fixed
                   if b['floor'] == cp['Floor'] and b['number'] == n for e, _ in b['enemies']}
        party = None
        hit = False
        for table, key, _, _ in changes:
            if table == 'enemies':
                hit = key in enemies
            elif table == 'attacks':
                hit = any(key in data.enemies[e]['attacks'] or key in data.enemies[e]['passives'] for e in enemies)
            elif table in ('skills', 'equipment'):
                if party is None:
                    party = scenario.reference_party(data, setup, cp['Chapter'], levels[cid][0], 0)
                if table == 'skills':
                    hit = any(key[1] in scenario.allocate_skills(data, setup.roles[m.role], m.level) for m in party)
                else:
                    name = data.equipment[key]['name']
                    hit = any(name in str(setup.roles[m.role][c]).split('|') for m in party
                              for c in ('Weapon', 'Off hand', 'Head', 'Body', 'Accessory'))
            else:
                hit = True
            if hit:
                found.append(cid)
                break
    return found


def play_checkpoint(data, setup, cid, runs):
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)

    def party():
        return scenario.reference_party(data, setup, cp['Chapter'], level, gear, int(cp['Crown bonus'] or 0),
                                        cp['Floor'])

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    return level, summary(scenario.play(data, setup, party, enemies, runs=runs))


def check_change(data, setup, changes, checkpoints=None, runs=None):
    """[(checkpoint, vanilla figures, changed figures, [the windows it leaves])] for the checkpoints the change
    touches (or those given). changes: the list GameData.with_changes takes."""
    runs = int(runs or setup.settings['check_runs'])
    changed = data.with_changes(changes)
    windows = {key: float(setup.settings[f'check_{key}_window']) for key in ('won', 'time', 'lowest_hp', 'pressure')}
    rows = []
    for cid in checkpoints or touched(data, setup, changes):
        level_a, before = play_checkpoint(data, setup, cid, runs)
        level_b, after = play_checkpoint(changed, setup, cid, runs)
        out = []
        for key, width in windows.items():
            a, b = before[key], after[key]
            if a is None or b is None:
                if (a is None) != (b is None):
                    out.append(key)
                continue
            relative = key in ('time', 'pressure')                 # these windows are shares of the vanilla figure
            if abs(b - a) > (width * a if relative else width):
                out.append(key)
        before['level'], after['level'] = level_a, level_b
        rows.append((cid, before, after, out))
    return rows

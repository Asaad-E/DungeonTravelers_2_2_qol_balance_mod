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
from sim.units import PARTY


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
                    party = [u for u in scenario.reference_party(data, setup, cp['Chapter'], levels[cid][0], 0)
                             if u.kind == 'member']
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


def random_group(data, zone, rng):
    """One random battle of a floor zone: a formation drawn by its chance (docs/FORMULAS.md 14), on a plain cell."""
    formations = [f for f in zone['formations'] if all(e in data.enemies for e, _ in f['enemies'])]
    pick = rng.choices(formations, weights=[max(1, f['chance']) for f in formations])[0]
    group = scenario.Group(scenario.build_enemy(data, e, front) for e, front in pick['enemies'])
    for unit, slot in zip(group, pick.get('slots', ())):
        unit.slot = slot
    return group


def expedition(data, setup, floor, level, cid, roles=None, battles=None, runs=None, kit=None):
    """Random battles in a row on one floor zone (its 'floor' name as in data.floors), HP and TP carried over and the
    recovery after each battle applied, until the party falls or the limit of battles. The party has the gear and the
    forged enchantments of checkpoint cid and its chapter. roles: the composition to use
    instead of the sheet Composition; kit: the item count of the bag (setting kit_count when None). Returns the mean
    battles won, the share of runs that reached the limit, and the mean TP share left after each of the first
    battles."""
    import random
    zone = next(z for z in data.floors if z['name'] == floor)
    cp = setup.checkpoint(cid)
    gear = scenario.checkpoint_gear(data, setup, cid)
    battles = int(battles or setup.settings['expedition_battles'])
    runs = int(runs or setup.settings['expedition_runs'])
    saved_comp, saved_kit = setup.composition, setup.settings.get('kit_count')
    if roles is not None:
        setup.composition = list(roles)
    if kit is not None:
        setup.settings['kit_count'] = kit
    try:
        won, full, tp_curve = [], 0, [0.0] * battles
        for k in range(runs):
            rng = random.Random(int(setup.settings['seed']) + k)
            result = scenario.play(data, setup,
                                   lambda: scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0,
                                                                    cp['Floor']),
                                   lambda: [random_group(data, zone, rng) for _ in range(battles)],
                                   runs=1, seed=int(setup.settings['seed']) + k,
                                   battle_setup={'random_battle': True})[0]
            parts = result['parts']
            n = sum(1 for p in parts if p['won'])
            won.append(n)
            full += n == battles
            for i, p in enumerate(parts):
                tp_curve[i] += p['tp_left'] / runs
        return {'won': sum(won) / runs, 'reached_limit': full / runs,
                'tp_after': [round(x, 2) for x in tp_curve[:min(battles, 8)]]}
    finally:
        setup.composition = saved_comp
        setup.settings['kit_count'] = saved_kit


def weapon_band(data, setup, cid, role_name, character, weapons, level=None, songs=()):
    """For one member of a role at a checkpoint (its level, gear upgrade and forge), each weapon of the list worn in
    turn: the expected damage per unit of time of her plain attack and of her best damage action against the first
    boss of the checkpoint (Battle.expected_damage over Policy.time_of, hits, accuracy and critical rate at their
    means; TP is not counted). songs: statuses (effect, value) put on the member first, as a song would. Returns
    {weapon: {'plain', 'best', 'skill', 'wait', 'def'}}."""
    import random
    from sim.battle import Action, Battle
    from sim.policy import Policy, load_rules, options
    from sim.units import Status
    cp = setup.checkpoint(cid)
    level = level or scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    char = next(c for c in data.characters if c['name'] == character)
    policy = Policy(load_rules(setup.policies), setup.settings)
    boss = scenario.fixed_battle(data, cp['Floor'], scenario.battle_numbers(cp)[0])
    saved = setup.roles[role_name]
    out = {}
    try:
        for weapon in weapons:
            role = dict(saved)
            role['Weapon'] = weapon
            setup.roles[role_name] = role
            member = scenario.build_role_member(data, setup, role_name, char, level, gear, 0,
                                                scenario.forge_open(setup, cp['Floor']))
            if member.weapon is None or member.weapon['name'] != weapon:
                continue                                    # the class cannot wear it
            for effect, value in songs:
                member.statuses[effect] = Status(effect, value, 0, member, 'song', 'song')
            battle = Battle(data, [member], list(boss), random.Random(0))
            target = max(boss, key=lambda e: e.max_hp)
            plain = Action(member, 'attack', target=target)
            rate = lambda a: battle.expected_damage(a, target) / policy.time_of(battle, a)
            best, name = rate(plain), 'Attack'
            for skill, lv in options(battle, member):
                action = Action(member, 'skill', skill, lv, target=target)
                if action.physical or action.magic:
                    value = rate(action)
                    if value > best:
                        best, name = value, skill.name
            out[weapon] = {'plain': rate(plain), 'best': best, 'skill': name,
                           'wait': policy.time_of(battle, plain), 'def': member.stat('def')}
    finally:
        setup.roles[role_name] = saved
    return out


def slot_share(data, setup, cid, slot_role, other_role, runs=None):
    """The boss fights of a checkpoint played twice by the reference party, the role slot_role of the composition
    replaced by other_role the second time: the share of the party's damage made by the member of that slot (her
    dolls and arrows counted as hers), the win share and the mean length. Returns {role: figures} and the ratio of
    the two shares (other over slot)."""
    runs = int(runs or setup.settings['check_runs'])
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    saved = setup.composition
    out = {}
    try:
        for role in (slot_role, other_role):
            swapped = list(saved)
            if role == other_role:
                swapped[saved.index(slot_role)] = other_role      # the first slot of that role only
            setup.composition = swapped
            res = scenario.play(data, setup,
                                lambda: scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor']),
                                lambda: [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)],
                                runs=runs)
            share = 0.0
            for r in res:
                for part in r['parts']:
                    dmg = part['record'].damage
                    total = sum(v for u, v in dmg.items() if u.side == PARTY) or 1
                    mine = sum(v for u, v in dmg.items() if u.side == PARTY and
                               getattr(getattr(u, 'owner', None) or u, 'role', None) == role)
                    share += mine / total / len(r['parts'])
            out[role] = {'share': share / runs, 'won': sum(r['won'] for r in res) / runs,
                         'time': sum(r['time'] for r in res) / runs}
    finally:
        setup.composition = saved
    ratio = out[other_role]['share'] / out[slot_role]['share'] if out[slot_role]['share'] else 0.0
    return out, ratio


def check_change(data, setup, changes, checkpoints=None, runs=None, changed=None):
    """[(checkpoint, vanilla figures, changed figures, [the windows it leaves])] for the checkpoints the change
    touches (or those given). changes: the list GameData.with_changes takes; or changed, data already changed (the
    whole variant, sim/variant.py), with the checkpoints given."""
    runs = int(runs or setup.settings['check_runs'])
    changed = changed if changed is not None else data.with_changes(changes)
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

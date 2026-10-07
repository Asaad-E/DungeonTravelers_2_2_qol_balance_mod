"""
A fight to play: a party built from the sheets Roles, Composition and Joins of data_tables/sim_setup.xlsx and the
enemies of a fixed battle or of a random formation.

    party, enemies = checkpoint_fight(data, setup, 'C10')
"""
import random

from sim.battle import Battle
from sim.policy import Policy, load_rules
from sim.units import build_member, build_enemy

STAGES = ((30, 'Lv30 class'), (15, 'Lv15 class'), (1, 'Base class'))


def class_id(data, name):
    return next(k for k, v in data.class_names.items() if v == name)


def level_of_exp(data, exp):
    """The level a total of EXP gives: ExpCurve holds the EXP of each step from the level below, so the steps are
    added up (the starting levels of docs/generated/BALANCE_BASELINE.md come out the same way)."""
    level, total = 1, 0
    for lv in sorted(data.exp_curve):
        total += data.exp_curve[lv]
        if total <= exp:
            level = lv
    return level


def class_path(data, role, level):
    """(class id, previous class id) the role has at this level: its Lv30 class from 30, its Lv15 class from 15."""
    path = [role['Base class'], role['Lv15 class'], role['Lv30 class']]
    if level >= 30:
        return class_id(data, path[2]), class_id(data, path[1])
    if level >= 15:
        return class_id(data, path[1]), class_id(data, path[0])
    return class_id(data, path[0]), None


def classes_so_far(data, role, level):
    names = [role['Base class']] + ([role['Lv15 class']] if level >= 15 else []) + ([role['Lv30 class']] if level >= 30 else [])
    return [class_id(data, n) for n in names]


def sp_total(data, level):
    return sum(data.sp_curve.get(lv, 0) for lv in range(1, level + 1))


def allocate_skills(data, role, level):
    """Skill points of the level spent on the role's priority list (A14: skills of earlier classes are kept): first
    every listed skill to level 1 in order, then each to its maximum in order, as far as the points go."""
    learnable = set(classes_so_far(data, role, level))
    by_name = {}
    for skill in data.skills.values():
        if set(skill.classes) & learnable:
            by_name.setdefault(skill.name, skill)
    wanted = [by_name[n.strip()] for n in str(role['Skill priority']).split(';') if n.strip() in by_name]
    budget = sp_total(data, level)
    levels = {}

    def raise_to(skill, target):
        nonlocal budget
        while levels.get(skill, 0) < min(target, skill.levels):
            cost = skill.sp[levels.get(skill, 0)] if skill.sp else 1
            if cost > budget:
                return
            budget -= cost
            levels[skill] = levels.get(skill, 0) + 1

    for skill in wanted:
        raise_to(skill, 1)
    for skill in wanted:
        raise_to(skill, skill.levels)
    return {skill.id: lv for skill, lv in levels.items()}


def piece_by_name(data, name, class_id_):
    for option in str(name).split('|'):
        for piece in data.equipment.values():
            if piece['name'] == option.strip() and piece['classes'] >> class_id_ & 1:
                return piece
    return None


def gear_level(data, floor_name, level, min_formations, margin):
    """A12: the highest upgrade level a random-battle zone (at least min_formations formations) of this dungeon or an
    earlier one can give, over every kind of drop, among the zones whose strongest enemy is at most margin levels above
    the party (a zone of the postgame in the same folder is left out by its enemies)."""
    dungeon = int(floor_name[2:4])
    levels = []
    for floor in data.floors:
        if int(floor['dungeon'][2:]) > dungeon or len(floor['formations']) < min_formations:
            continue
        strongest = max(data.enemies[e]['level'] for f in floor['formations'] for e, _ in f['enemies'])
        if strongest > level + margin:
            continue
        levels += [hi for piece in floor['equipment'] for lo, hi in piece['levels'].values()]
    return max(levels, default=0)


def checkpoint_gear(data, setup, cid):
    """The gear level of a checkpoint: gear_level at its floor, and never below the one of an earlier checkpoint."""
    best = 0
    for cp in setup.checkpoints:
        enemies = [e for number in battle_numbers(cp) for b in data.fixed
                   if b['floor'] == cp['Floor'] and b['number'] == number for e in b['enemies']]
        level = max(data.enemies[e]['level'] for e, _ in enemies)
        best = max(best, gear_level(data, cp['Floor'], level, int(setup.settings['gear_min_formations']),
                                    int(setup.settings['gear_level_margin'])))
        if cp['ID'] == cid:
            return best
    raise KeyError(cid)


def build_role_member(data, setup, role_name, character, level, upgrade, crown=0):
    role = setup.roles[role_name]
    cls, previous = class_path(data, role, level)
    equipment = []
    for slot, column in ((0, 'Weapon'), (1, 'Off hand'), (2, 'Head'), (3, 'Body'), (4, 'Accessory')):
        if not role[column]:
            continue
        piece = piece_by_name(data, role[column], cls)
        if piece is not None:
            if slot == 1 and equipment and data.equipment[equipment[0][1]]['two_handed']:
                continue
            equipment.append((slot, piece['id'], upgrade))
    skills = allocate_skills(data, role, level)
    unit = build_member(data, character, cls, level, previous, equipment, skills, crown_bonus=crown,
                        front=role['Row'] == 'front')
    unit.role = role_name
    unit.shield = any(slot == 1 and data.equipment[i]['category'] == 1 for slot, i, _ in equipment)
    return unit


def available(setup, chapter):
    names = []
    for joined_in, chars in setup.joins:
        names += chars
        if chapter.startswith(joined_in) or (joined_in == 'Prologue' and chapter == 'Prologue'):
            break
    return names


def reference_party(data, setup, chapter, level, upgrade, crown=0):
    chars = {c['name']: c for c in data.characters}
    pool = available(setup, chapter)
    size = int(setup.settings.get('party_size', 5))
    taken, party = set(), []
    for role_name in setup.composition:
        if len(party) >= size:
            break
        role = setup.roles[role_name]
        base = class_id(data, role['Base class'])
        for name in str(role['Characters (order of preference)']).split(';'):
            name = name.strip()
            c = chars.get(name)
            if name in pool and name not in taken and c and c['base_class'] == base:
                join_level = level_of_exp(data, c['start_exp'] or 0)
                party.append(build_role_member(data, setup, role_name, c, max(level, join_level), upgrade, crown))
                taken.add(name)
                break
    # a role with nobody: any member left, in the role of her base class
    for name in pool:
        if len(party) >= size:
            break
        c = chars.get(name)
        if name in taken or not c:
            continue
        for role_name, role in setup.roles.items():
            if class_id(data, role['Base class']) == c['base_class']:
                join_level = level_of_exp(data, c['start_exp'] or 0)
                party.append(build_role_member(data, setup, role_name, c, max(level, join_level), upgrade, crown))
                taken.add(name)
                break
    front = int(setup.settings.get('front_size', 3))
    if sum(u.front for u in party) > front:
        for u in sorted((u for u in party if u.front), key=lambda u: u.max_hp)[:sum(u.front for u in party) - front]:
            u.front = False
    if not any(u.front for u in party) and party:
        max(party, key=lambda u: u.max_hp).front = True
    return party


class Group(list):
    """The enemies of one battle, with the zone of the cell it is fought on (Battle's zone argument)."""
    zone = None


def fixed_battle(data, floor, number):
    battle = next(b for b in data.fixed if b['floor'] == floor and b['number'] == number)
    group = Group(build_enemy(data, enemy, front) for enemy, front in battle['enemies'])
    group.zone = battle_zone(data, floor, number)
    return group


def battle_zone(data, floor, number):
    """The zone slots of the event cell that starts a fixed battle and the factors of its floor zone (docs/FORMULAS.md
    2.5, 16.2); None when the battle is started away from a cell of the floor."""
    cells = data.battle_cells.get((floor, number))
    if not cells:
        return None
    cell = cells[0]
    return {'slots': tuple(v for v in cell['slots'] if v), 'factors': data.zone_factors.get((floor, cell['zone']), {}),
            'no_magic': NO_MAGIC in cell['slots']}


NO_MAGIC = 2                 # zone value that forbids magic (docs/FORMULAS.md 16.2)


def battle_numbers(cp):
    """The fixed battles of a checkpoint: one number, or several joined by + that are fought in a row."""
    return [int(n) for n in str(cp['Battle (several joined by + are fought in a row)']).split('+')]


def zone_level(data, floor, number, share):
    """The level of the random enemies of the floor zone whose cell starts a fixed battle: the lowest level L such that
    the formations whose strongest enemy is at most L make up the share of the encounters (chance of each formation;
    floor_data). None when the battle is started away from a cell of the floor or the zone has no formations."""
    cells = data.battle_cells.get((floor, number))
    if not cells:
        return None
    zone = cells[0]['zone']
    formations = [(max(data.enemies[e]['level'] for e, _ in f['enemies']), f['chance'])
                  for z in data.floors if z['floor'] == floor and z['zone'] == zone for f in z['formations']
                  if all(e in data.enemies for e, _ in f['enemies'])]
    if not formations:
        return None
    total, covered = sum(c for _, c in formations), 0
    for level, chance in sorted(formations):
        covered += chance
        if covered >= share * total:
            return level
    return max(level for level, _ in formations)


def reference_levels(data, setup):
    """{checkpoint: (level, where it comes from)} in the order of the sheet (A15, the user's decision of 2026-10-07):
    the guides' level, else the level of the random enemies of the zone where the boss stands, else the level of the
    checkpoint before; never below the level of the checkpoint before, since a party does not lose levels."""
    share = float(setup.settings['zone_level_share'])
    found, previous = {}, 0
    for cp in setup.checkpoints:
        guide = setup.guide_levels.get(cp['ID'])
        zone = zone_level(data, cp['Floor'], battle_numbers(cp)[0], share)
        if guide is not None and guide['Level'] is not None:
            level, source = int(guide['Level']), 'guide'
        elif zone is not None:
            level, source = zone, 'zone'
        else:
            level, source = previous, 'before'
        if level < previous:
            level, source = previous, source + ', held'
        found[cp['ID']] = (level, source)
        previous = level
    return found


def checkpoint_fight(data, setup, cid, level=None, crown=None):
    """The party and the enemy groups of a checkpoint: [enemies of the first battle, of the next ...]. The party is at
    the reference level of the checkpoint unless a level is given."""
    cp = setup.checkpoint(cid)
    groups = [fixed_battle(data, cp['Floor'], n) for n in battle_numbers(cp)]
    level = level if level is not None else reference_levels(data, setup)[cid][0]               # A15
    party = reference_party(data, setup, cp['Chapter'], level, checkpoint_gear(data, setup, cid),
                            crown if crown is not None else int(cp['Crown bonus'] or 0))
    return party, groups


def play(data, setup, party_factory, enemy_factory, runs=None, seed=None, battle_setup=None):
    """Plays runs battles; party_factory and enemy_factory build fresh units for each. Returns the results."""
    runs = int(runs if runs is not None else setup.settings['runs'])
    seed = int(seed if seed is not None else setup.settings['seed'])
    policy = Policy(load_rules(setup.policies), setup.settings)
    options = dict(setup.settings)
    options.update(battle_setup or {})
    results = []
    for k in range(runs):
        rng = random.Random(seed + k)
        party, groups = party_factory(), enemy_factory()
        if groups and not isinstance(groups[0], list):
            groups = [groups]
        result = None
        for enemies in groups:
            for unit in party:                       # a battle that follows another: HP and TP carry over
                unit.statuses, unit.chant, unit.song, unit.dance = {}, None, [], []
            party = [u for u in party if u.kind == 'member']
            battle = Battle(data, party, enemies, rng, choose_member=policy, setup=options,
                            zone=getattr(enemies, 'zone', None), max_time=float(setup.settings.get('max_time', 400)))
            part = battle.run()
            if result is None:
                result = part
                result['parts'] = [part]
            else:
                result['parts'].append(part)
                result.update({'won': part['won'], 'lost': part['lost'], 'time': result['time'] + part['time'],
                               'actions': result['actions'] + part['actions'], 'hp_left': part['hp_left'],
                               'tp_left': part['tp_left'], 'alive': part['alive']})
            if not part['won']:
                break
        results.append(result)
    return results

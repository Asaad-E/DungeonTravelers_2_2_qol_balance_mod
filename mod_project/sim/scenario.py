"""
A fight to play: a party built from the sheets Roles, Composition and Joins of data_tables/sim_setup.xlsx and the
enemies of a fixed battle or of a random formation.

    party, enemies = checkpoint_fight(data, setup, 'C10')
"""
import random

from sim import progression
from sim.battle import Battle
from sim.policy import Policy, load_rules
from sim.units import build_member, build_enemy, build_summon, DUAL_WIELD

STAGES = ((30, 'Lv30 class'), (15, 'Lv15 class'), (1, 'Base class'))


ONE_PER_PIECE = (6, 9, 12, 15, 18, 21)       # ATK to AGI UP: one a piece (atwiki dt2-2 page 214)


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

    plan = role.get('Skill plan')
    if plan:
        # the order of a guide: each entry 'Name:target' (a level or 'max') is raised in turn, as far as the points go
        for entry in str(plan).split(';'):
            name, _, target = entry.strip().partition(':')
            skill = by_name.get(name.strip())
            if skill is not None:
                raise_to(skill, skill.levels if target.strip() in ('', 'max') else int(target))
        return {skill.id: lv for skill, lv in levels.items()}
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


def enchant_slots(setup, upgrade):
    """Enchantment slots of a piece at an upgrade level (sheet EnchantSlots)."""
    return max((int(r['Slots']) for r in setup.enchant_slots if upgrade >= int(r['Least upgrade'])), default=0)


def forge_enchants(data, setup, role_name, equipment):
    """A31: the enchantments a reference member has forged onto her gear: enchant_fill of the slots of her pieces,
    filled in the order of the sheet EnchantPlan for her role; a stat enchantment (ATK to AGI UP) at most once a
    piece. Returns {enchantment id: pieces that carry it}."""
    plan = sorted((r for r in setup.enchant_plan if r['Role'] == role_name), key=lambda r: r['Order'])
    pieces = [{'kind': 'weapon' if data.equipment[i]['category'] == 0 else 'armour', 'upgrade': up,
               'free': enchant_slots(setup, up), 'has': set()} for _, i, up in equipment]
    budget = int(round(float(setup.settings.get('enchant_fill', 0) or 0) * sum(p['free'] for p in pieces)))
    found = {}
    for row in plan:
        eid, placed = int(row['Enchant_ID']), 0
        for piece in pieces:
            while budget > 0 and placed < int(row['Most per member']) and piece['free'] > 0                     and row['Slot'] in ('any', piece['kind']) and piece['upgrade'] >= int(row['Least upgrade of the piece'] or 0)                     and not (eid in piece['has'] and eid in ONE_PER_PIECE):
                piece['free'] -= 1
                piece['has'].add(eid)
                found[eid] = found.get(eid, 0) + 1
                placed += 1
                budget -= 1
    return found


def forge_open(setup, floor):
    """Whether the blacksmith has been met by the dungeon of this floor (setting forge_from_dungeon)."""
    return floor is not None and int(floor[2:4]) >= int(setup.settings.get('forge_from_dungeon', 99))


def build_role_member(data, setup, role_name, character, level, upgrade, crown=0, forge=False, extra_skills=None,
                      party_enchants=()):
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
    skills.update(extra_skills or {})                # skills given on top of the plan (tools/sim_audit.py);
    skills = {k: v for k, v in skills.items() if v > 0}   # level 0 takes a skill away
    # a weapon goes in the off hand only with Dual Wield (atwiki dt2-2 page 142: it takes the place of the shield)
    dual = any(e == DUAL_WIELD for sid in skills for e, _, _ in getattr(data.skills.get(('Passive', sid)), 'effects', []))
    equipment = [(slot, i, u) for slot, i, u in equipment
                 if not (slot == 1 and data.equipment[i]['category'] == 0 and not dual)]
    forged = forge_enchants(data, setup, role_name, equipment) if forge else None
    unit = build_member(data, character, cls, level, previous, equipment, skills, crown_bonus=crown,
                        front=role['Row'] == 'front', forged=forged, party_enchants=party_enchants)
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


def grand_sealbook(setup, chapter, floor=None):
    """The grand sealbook the party carries at a checkpoint (sheet GrandSealbooks: the last row whose checkpoint is not
    after it), as the id of the enemy it seals; None before the first."""
    order = [c['ID'] for c in setup.checkpoints]
    here = [k for k, c in enumerate(setup.checkpoints) if c['Chapter'] == chapter and (floor is None or c['Floor'] == floor)]
    if not here:
        here = [k for k, c in enumerate(setup.checkpoints) if c['Chapter'] == chapter]
    if not here:
        return None
    at = here[-1] if floor is None else here[0]
    found = None
    for r in setup.grand_sealbooks:
        if r['From checkpoint'] in order and order.index(r['From checkpoint']) <= at:
            found = int(r['Sealbook'])
    return found


def sealbook_summon(data, setup, sealbook, party):
    """The summon of the grand sealbook (docs/FORMULAS.md 11): the last form of its family whose level is not above
    the average level of the party."""
    members = [u for u in party if u.kind == 'member']
    average = sum(u.level for u in members) / max(1, len(members))
    forms = sorted((f for f in data.summons if f['family'] == sealbook and f['level'] <= average), key=lambda f: f['level'])
    if not forms:
        return None
    unit = build_summon(data, forms[-1], members, int(setup.settings['summon_hp']))
    unit.level = forms[-1]['level']
    return unit


def reference_party(data, setup, chapter, level, upgrade, crown=0, floor=None):
    chars = {c['name']: c for c in data.characters}
    pool = available(setup, chapter)
    sealbook = grand_sealbook(setup, chapter, floor)
    book = data.sealbooks.get(sealbook) if sealbook is not None else None
    party_enchants = tuple(book['enchants']) if book else ()
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
                party.append(build_role_member(data, setup, role_name, c, max(level, join_level), upgrade, crown,
                                               forge_open(setup, floor), party_enchants=party_enchants))
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
                party.append(build_role_member(data, setup, role_name, c, max(level, join_level), upgrade, crown,
                                               forge_open(setup, floor), party_enchants=party_enchants))
                taken.add(name)
                break
    front = int(setup.settings.get('front_size', 3))
    if sum(u.front for u in party) > front:
        for u in sorted((u for u in party if u.front), key=lambda u: u.max_hp)[:sum(u.front for u in party) - front]:
            u.front = False
    if not any(u.front for u in party) and party:
        max(party, key=lambda u: u.max_hp).front = True
    # one bag for the whole party, as in the game: the items of the sheet Kit, kit_count of each times its share
    count = int(setup.settings.get('kit_count', 0) or 0)
    bag = {int(r['Item_ID']): int(round(count * float(r['Share'] or 1))) for r in setup.kit}
    for u in party:
        u.items = bag
    if sealbook is not None:            # the summon of the grand sealbook fights beside the party (not a member)
        summon = sealbook_summon(data, setup, sealbook, party)
        if summon is not None:
            summon.items = {}
            party.append(summon)
    return party


class Group(list):
    """The enemies of one battle, with the zone of the cell it is fought on (Battle's zone argument)."""
    zone = None
    floor = number = None


def fixed_battle(data, floor, number):
    battle = next(b for b in data.fixed if b['floor'] == floor and b['number'] == number)
    group = Group(build_enemy(data, enemy, front) for enemy, front in battle['enemies'])
    for unit, slot in zip(group, battle.get('slots', ())):
        unit.slot = slot
    group.zone = battle_zone(data, floor, number)
    group.floor, group.number = floor, number
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
                            crown if crown is not None else int(cp['Crown bonus'] or 0), cp['Floor'])
    return party, groups


def prepare(setup, party, enemies):
    """The resistances a player raises for a battle the guides warn about (sheet Preparation): each member's
    resistance is brought up to the value of the row, never lowered."""
    for row in setup.preparation:
        if row['Floor'] == getattr(enemies, 'floor', None) and int(row['Battle']) == getattr(enemies, 'number', None):
            index, value = int(row['Resistance index']), int(row['Value'])
            for unit in party:
                unit.resist_base[index] = max(unit.resist_base[index], value)
    # the altar or shrine of the map a player uses before a boss the guides warn about (sheet ZoneChanges): a zone
    # slot of the cell removed, or changed into another (an element slot 7 - 11)
    for row in setup.zone_changes:
        zone = getattr(enemies, 'zone', None)
        if zone and row['Floor'] == getattr(enemies, 'floor', None) and int(row['Battle']) == getattr(enemies, 'number', None):
            slots = list(zone['slots'])
            if int(row['Slot']) in slots:
                k = slots.index(int(row['Slot']))
                if row['New slot'] in (None, ''):
                    slots.pop(k)
                else:
                    slots[k] = int(row['New slot'])
            enemies.zone = dict(zone, slots=tuple(slots))


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
            party = [u for u in party if u.kind in ('member', 'summon')]
            prepare(setup, party, enemies)
            battle = Battle(data, party, enemies, rng, choose_member=policy, setup=options,
                            zone=getattr(enemies, 'zone', None), max_time=float(setup.settings.get('max_time', 400)))
            battle.fixed = getattr(enemies, 'number', None) is not None      # a fixed battle of the story
            part = battle.run()
            if result is None:
                result = dict(part)
                result['parts'] = [part]
            else:
                result['parts'].append(part)
                result.update({'won': part['won'], 'lost': part['lost'], 'time': result['time'] + part['time'],
                               'actions': result['actions'] + part['actions'], 'hp_left': part['hp_left'],
                               'lowest_hp': min(result['lowest_hp'], part['lowest_hp']),
                               'enemy_damage': result['enemy_damage'] + part['enemy_damage'],
                               'enemy_actions': result['enemy_actions'] + part['enemy_actions'],
                               'tp_left': part['tp_left'], 'alive': part['alive']})
            if not part['won']:
                break
            recover_after_battle(party)
        results.append(result)
    return results


def recover_after_battle(party):
    """docs/FORMULAS.md 12.14 (0x43d6a7 - 0x43d8b4): the living members with Generous Heart (272 HP, 273 TP; each
    value raised by the member's Maid Mastery, getter 0x48a8f0) give the party a share capped at 0.30, plus Maximum
    Maid (353) outside the cap; every living member recovers int(max * share), all its HP with a piece of 193."""
    living = [u for u in party if u.alive and u.kind == 'member']
    for effect, attr, top in ((272, 'hp', 'max_hp'), (273, 'tp', 'max_tp')):
        givers = [u for u in living if u.passives.get(effect)]
        share = progression.after_battle_fraction([u.passives[effect] + u.passives.get(278, 0.0) for u in givers],
                                                  [u.passives.get(353, 0.0) for u in givers])
        for u in living:
            full = effect == 272 and u.pieces(193) > 0
            gain = progression.after_battle_recovery(getattr(u, top), share, full)
            setattr(u, attr, min(getattr(u, top), getattr(u, attr) + gain))

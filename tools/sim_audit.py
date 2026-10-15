"""
Audit of the simulator: does every rule it holds actually act? Generated: docs/generated/SIM_AUDIT.md.

    python tools/sim_audit.py passives [k/n]   every passive skill, with and without, in the same fights
                                                          (k/n: the k-th of n slices, one process each)
    python tools/sim_audit.py usage [k/n]   the skills of each role's plan it never uses, and why
    python tools/sim_audit.py report        joins the parts written so far into SIM_AUDIT.md
    python tools/sim_audit.py passives-engine | usage-engine | actives-engine [k/n]
                                            the same phases played by the C# engine (engine_cs/) in one call

Each phase writes its part to docs/generated/sim_audit/<phase>.md and runs in its own process, so memory is freed
between phases. A check that comes out "no effect seen" is not a verdict: it is a row to read by hand, and its reading
is written in the sheet AuditReadings of data_tables/sim_setup.xlsx (ID, Result, Reading). The audit is done when every
flagged row has a reading.

Passives: for each passive skill, a member of a class that learns it (the role of that class in the sheet Roles, its
plan, at the top of its tier) fights a boss of her tier in the reference party of that checkpoint (she takes the place
of the member of her role, else of the last member), once with the passive at its top level and once without, on the
same seeds. The fights are compared figure by figure (who won, the length, the number of
actions, the damage of each unit, HP and TP left): if every figure of every seed is the same, the passive did nothing
there. Passives that act outside battle (the list handles('outside battle') of sim/battle.py) are reported apart.

Usage: each role of the sheet Roles, at the top of each tier and late (LATE), in the same fights as above: the skills
of its plan that can be used in battle and that it never used in any seed. A skill never used is a row to read: the
policy of the role may lack a rule for it, or the fight may give it no use (a revive when nobody falls).

Actives (python tools/sim_audit.py actives [k/n]): every technique and spell that can be used in battle,
at its top level, performed by a member of a class that learns it (role and character of that class at level 90, or
a member of the reference party wearing it) into a prepared battle: the reference party of P24 at 90 with every
member at half HP and TP, one fallen, one poisoned and asleep; two enemies of level 90 (ACTIVES_ENEMY) with no
immunity and no resistance, carrying a buff. The skill is performed ACTIVE_TRIES times, each on a fresh battle and
seed, and what changed is compared with what its effects say it does:
    damage      an effect 0 or 1 of kind 4, or a fixed or special damage: a unit loses HP
    ailment     an effect of the ailment list: a unit gets it (stun: its next turn is pushed back; death: it falls)
    status      an effect of kind 5: some unit gets a status of that effect
    anything    the rest: some figure of some unit changes (HP, TP, a status, a unit made or gone, the order of turns)
A skill whose expectation is never met is a row to read.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'sim_audit')
REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'SIM_AUDIT.md')

from sim import scenario                                 # noqa: E402
from sim import setup as setup_mod                       # noqa: E402
from sim.battle import HANDLED                           # noqa: E402
from sim.data import game_data                           # noqa: E402

TIERS = (('Base class', 14, 'C11'), ('Lv15 class', 29, 'C18'), ('Lv30 class', 62, 'C38'))
LATE = (90, 'P24')
SEEDS = 6


def role_for(setup, data, class_id):
    """The first role whose path passes through the class, with the column and level of that tier."""
    name = data.class_names.get(class_id)
    for column, level, cid in TIERS:
        for role, row in setup.roles.items():
            if row[column] == name:
                return role, level, cid
    return None


def fingerprint(results):
    out = []
    for r in results:
        dmg = tuple(sorted((u.name, v) for u, v in r['record'].damage.items()))
        out.append((r['won'], round(r['time'], 6), r['actions'], dmg, round(r['hp_left'], 6), round(r['tp_left'], 6)))
    return out


def fights(data, setup, role, character, level, cid, extra):
    party, enemies = factories(data, setup, role, character, level, cid, extra)
    return scenario.play(data, setup, party, enemies, runs=SEEDS)


def factories(data, setup, role, character, level, cid, extra):
    """The builders of the party (the reference party of the checkpoint with the tested member in it) and of the
    enemies of its fights."""
    cp = setup.checkpoint(cid)
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}

    def party():
        tested = scenario.build_role_member(data, setup, role, chars[character], level, gear, 0,
                                            scenario.forge_open(setup, cp['Floor']), extra)
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        summons = [u for u in whole if u.kind != 'member']
        members = [u for u in whole if u.kind == 'member' and u.name != character]
        same = next((k for k, u in enumerate(members) if u.role == role), None)
        if same is not None:
            members[same] = tested
        else:
            members = members[:int(setup.settings.get('party_size', 5)) - 1] + [tested]
        for u in members:
            u.items = members[0].items
        return members + summons

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    return party, enemies


def passives(part='1/1'):
    """part 'k/n': the k-th of n slices of the passive skills, each run in its own process (passives_k.md)."""
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    outside = {e for e, where in HANDLED.items() if where.startswith('outside battle')}
    rows = []
    every = [(cat, sid) for (cat, sid) in sorted(data.skills, key=lambda x: x[1]) if cat == 'Passive']
    mine = set(every[(k - 1) * len(every) // n: k * len(every) // n])
    for (cat, sid), skill in sorted(data.skills.items(), key=lambda x: x[0][1]):
        if cat != 'Passive' or (cat, sid) not in mine:
            continue
        effects = [e for e, _, _ in skill.effects]
        if effects and all(e in outside for e in effects):
            rows.append((sid, skill.name, effects, '-', 'outside battle'))
            continue
        found = None
        for class_id in skill.classes or []:
            found = role_for(setup, data, class_id)
            if found:
                break
        if not found:
            rows.append((sid, skill.name, effects, '-', 'no role learns it'))
            continue
        role, level, cid = found
        names = [n.strip() for n in str(setup.roles[role]['Characters (order of preference)']).split(';')]
        character = names[0]
        top = skill.levels or 1
        base = {sid: 0}
        with_it = fights(data, setup, role, character, level, cid, {sid: top})
        without = fights(data, setup, role, character, level, cid, base)
        same = fingerprint(with_it) == fingerprint(without)
        rows.append((sid, skill.name, effects, f'{role} ({character}, {level}, {cid})',
                     'no effect seen' if same else 'acts'))
        print(sid, skill.name, rows[-1][-1], flush=True)
    write('passives' if n == 1 else f'passives_{k}', ['| Passive | Effects | Tested as | Result |', '|---|---|---|---|'] +
          [f'| {sid} {name} | {", ".join(map(str, eff))} | {how} | {res} |' for sid, name, eff, how, res in rows],
          f'{sum(r[-1] == "acts" for r in rows)} act, {sum(r[-1] == "no effect seen" for r in rows)} no effect seen, '
          f'{sum(r[-1] == "outside battle" for r in rows)} outside battle, {sum(r[-1] == "no role learns it" for r in rows)} '
          f'with no role, of {len(rows)} passive skills')


def fights_job(data, setup, role, character, level, cid, extra, name):
    """The job of the C# engine that plays what fights() plays: factories(), then six seeds."""
    import engine_client as engine
    cp = setup.checkpoint(cid)
    recipe = {'name_not': character, 'place': 'replace_role', 'items': 'all_first',
              'tested': [{'role': role, 'character': character, 'level': level, 'forge': bool(scenario.forge_open(setup, cp['Floor'])),
                          'extra_skills': {str(k): v for k, v in (extra or {}).items()}}]}
    return engine.make_job(engine.side_of(data), cid, runs=SEEDS, level=level, crown=0, record=True, setup=engine.setup_of(setup),
                           recipe=recipe, name=name)


def fights_engine(data, setup, requests):
    """fights() for each request (role, character, level, cid, extra), played by the C# engine in one call."""
    import engine_client as engine
    jobs = [fights_job(data, setup, *request, name=f'fights{k}') for k, request in enumerate(requests)]
    return [d['runs'] for d in engine.run_jobs(jobs)]


def passives_engine(part='1/1'):
    """passives(), played by the C# engine in one call."""
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    outside = {e for e, where in HANDLED.items() if where.startswith('outside battle')}
    every = [(cat, sid) for (cat, sid) in sorted(data.skills, key=lambda x: x[1]) if cat == 'Passive']
    mine = set(every[(k - 1) * len(every) // n: k * len(every) // n])
    plan, requests = [], []
    for (cat, sid), skill in sorted(data.skills.items(), key=lambda x: x[0][1]):
        if cat != 'Passive' or (cat, sid) not in mine:
            continue
        effects = [e for e, _, _ in skill.effects]
        if effects and all(e in outside for e in effects):
            plan.append((sid, skill.name, effects, '-', 'outside battle', None))
            continue
        found = None
        for class_id in skill.classes or []:
            found = role_for(setup, data, class_id)
            if found:
                break
        if not found:
            plan.append((sid, skill.name, effects, '-', 'no role learns it', None))
            continue
        role, level, cid = found
        names = [n.strip() for n in str(setup.roles[role]['Characters (order of preference)']).split(';')]
        character = names[0]
        top = skill.levels or 1
        requests += [(role, character, level, cid, {sid: top}), (role, character, level, cid, {sid: 0})]
        plan.append((sid, skill.name, effects, f'{role} ({character}, {level}, {cid})', None, len(requests) - 2))
    played = fights_engine(data, setup, requests)
    rows = []
    for sid, name, effects, how, result, at in plan:
        if at is not None:
            result = 'no effect seen' if fingerprint(played[at]) == fingerprint(played[at + 1]) else 'acts'
        rows.append((sid, name, effects, how, result))
        print(sid, name, rows[-1][-1], flush=True)
    write('passives' if n == 1 else f'passives_{k}', ['| Passive | Effects | Tested as | Result |', '|---|---|---|---|'] +
          [f'| {sid} {name} | {", ".join(map(str, eff))} | {how} | {res} |' for sid, name, eff, how, res in rows],
          f'{sum(r[-1] == "acts" for r in rows)} act, {sum(r[-1] == "no effect seen" for r in rows)} no effect seen, '
          f'{sum(r[-1] == "outside battle" for r in rows)} outside battle, {sum(r[-1] == "no role learns it" for r in rows)} '
          f'with no role, of {len(rows)} passive skills')


def usage_engine(part='1/1'):
    """usage(), played by the C# engine: the fights in one call, the scores of the options in another."""
    import engine_client as engine
    from sim.policy import usable_in_battle, weapon_allows, puts, EVERY_ROLE
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    chars = {c['name']: c for c in data.characters}
    roles = list(setup.roles.items())[(k - 1) * len(setup.roles) // n: k * len(setup.roles) // n]
    cells = []
    for role, row in roles:
        character = [x.strip() for x in str(row['Characters (order of preference)']).split(';')][0]
        if character not in chars:
            continue
        for level, cid in [(lv, c) for _, lv, c in TIERS] + [LATE]:
            cells.append((role, character, level, cid))
    requests = [(role, character, level, cid, None) for role, character, level, cid in cells]
    fought = fights_engine(data, setup, requests)
    items = []
    for k_, (role, character, level, cid) in enumerate(cells):
        cp = setup.checkpoint(cid)
        items.append({'side': engine.side_of(data), 'setup': engine.setup_of(setup), 'job': fights_job(data, setup, *requests[k_], name=f'scores{k_}'),
                      'contexts': [{'kind': 'fixed', 'floor': cp['Floor'], 'number': scenario.battle_numbers(cp)[0]}],
                      'zone': False, 'attack_first': True})
    scored = engine.skill_scores(items)
    rows = []
    at = 0
    for role, row in roles:
        character = [x.strip() for x in str(row['Characters (order of preference)']).split(';')][0]
        if character not in chars:
            continue
        rules = [r for r in setup.policies if r['Role'] in (role, EVERY_ROLE)]
        status_rules = {int(str(r['Action']).split(':')[1]) for r in rules if str(r['Action']).startswith('status:')}
        for level, cid in [(lv, c) for _, lv, c in TIERS] + [LATE]:
            res = fought[at]
            used = set()
            for r in res:
                for p in r['parts']:
                    for (u, name), _ in p['record'].skill_uses.items():
                        if getattr(u, 'role', None) == role and u.name == character:
                            used.add(name)
            party_fn, enemies_fn = factories(data, setup, role, character, level, cid, None)
            party = party_fn()
            member = next(u for u in party if getattr(u, 'role', None) == role and u.name == character)
            scores = dict(scored[at]['contexts'][0])
            at += 1
            best_name = max(scores, key=scores.get) if scores else None
            for sid, lv in member.skills.items():
                skill = data.skill_by_id.get(sid)
                if skill is None or not usable_in_battle(skill) or skill.name in used:
                    continue
                effects = {e for e, _, _ in skill.effects}
                if not weapon_allows(member, skill):
                    why = 'not usable with the weapon of the role'
                elif skill.name in scores:
                    share = scores[skill.name] / scores[best_name] if scores.get(best_name) else 0.0
                    why = f'dominated: {share:.0%} of the best ({best_name}) at the start of the fight'
                elif effects & {104, 105}:
                    why = 'situational: a revive'
                elif effects & {103, 9, 128, 130, 131, 132, 133}:
                    why = 'situational: a heal (another heal or the songs come first)'
                elif effects & {106, 235}:
                    why = 'situational: a cure'
                elif effects & {129, 426}:
                    why = 'situational: TP'
                elif 74 in effects:
                    why = 'situational: a dispel'
                elif any(puts(skill, e) for e in effects):
                    kept = sorted(e for e in effects if puts(skill, e) and e in status_rules)
                    why = (f'a rule keeps effect {kept[0]} up: another skill gives it first' if kept
                           else 'no rule of the role uses it')
                else:
                    why = 'other'
                rows.append((role, character, level, cid, skill.name, why))
            print(role, level, cid, 'unused', sum(1 for r in rows if r[:4] == (role, character, level, cid)), flush=True)
    counts = {}
    for r in rows:
        key = r[-1].split(':')[0]
        counts[key] = counts.get(key, 0) + 1
    write('usage' if n == 1 else f'usage_{k}', ['| Role | Level | Fight | Skill never used | Why |', '|---|---|---|---|---|'] +
          [f'| {role} ({who}) | {lv} | {cid} | {name} | {why} |' for role, who, lv, cid, name, why in rows],
          f'{len(rows)} skills of a plan never used: ' + ', '.join(f'{v} {k}' for k, v in sorted(counts.items())))


def usage(part='1/1'):
    """part 'k/n': the k-th of n slices of the roles (usage_k.md)."""
    import random
    from sim.battle import Battle, Action
    from sim.policy import (usable_in_battle, options, weapon_allows, damage_value, puts, load_rules, Policy,
                            EVERY_ROLE, RANDOM_MOVES)
    from sim.data import SINGLE, RANDOM, ROW, PIERCE, ALL, EVERYONE
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    chars = {c['name']: c for c in data.characters}
    policy = Policy(load_rules(setup.policies), setup.settings)
    roles = list(setup.roles.items())[(k - 1) * len(setup.roles) // n: k * len(setup.roles) // n]
    rows = []
    for role, row in roles:
        character = [x.strip() for x in str(row['Characters (order of preference)']).split(';')][0]
        if character not in chars:
            continue
        rules = [r for r in setup.policies if r['Role'] in (role, EVERY_ROLE)]
        status_rules = {int(str(r['Action']).split(':')[1]) for r in rules if str(r['Action']).startswith('status:')}
        for level, cid in [(lv, c) for _, lv, c in TIERS] + [LATE]:
            res = fights(data, setup, role, character, level, cid, None)
            used = set()
            for r in res:
                for p in r['parts']:
                    for (u, name), _ in p['record'].skill_uses.items():
                        if getattr(u, 'role', None) == role and u.name == character:
                            used.add(name)
            party_fn, enemies_fn = factories(data, setup, role, character, level, cid, None)
            party = party_fn()
            member = next(u for u in party if getattr(u, 'role', None) == role and u.name == character)
            b = Battle(data, party, enemies_fn()[0], random.Random(0), setup=setup.settings)
            member.tp = member.max_tp
            scores = {}
            for skill, lv in [(None, 0)] + options(b, member):
                act = Action(member, 'attack') if skill is None else Action(member, 'skill', skill, lv)
                hits = act.target_code in (SINGLE, RANDOM, ROW, PIERCE, ALL, EVERYONE) and (
                    act.physical or act.magic or b.special(act)) or any(act.has(e) for e in RANDOM_MOVES)
                if skill is None or hits:
                    total, _ = damage_value(b, act)
                    scores[getattr(skill, 'name', 'Attack')] = total / policy.time_of(b, act) / policy.tp_penalty(member, act)
            best_name = max(scores, key=scores.get) if scores else None
            for sid, lv in member.skills.items():
                skill = data.skill_by_id.get(sid)
                if skill is None or not usable_in_battle(skill) or skill.name in used:
                    continue
                effects = {e for e, _, _ in skill.effects}
                if not weapon_allows(member, skill):
                    why = 'not usable with the weapon of the role'
                elif skill.name in scores:
                    share = scores[skill.name] / scores[best_name] if scores.get(best_name) else 0.0
                    why = f'dominated: {share:.0%} of the best ({best_name}) at the start of the fight'
                elif effects & {104, 105}:
                    why = 'situational: a revive'
                elif effects & {103, 9, 128, 130, 131, 132, 133}:
                    why = 'situational: a heal (another heal or the songs come first)'
                elif effects & {106, 235}:
                    why = 'situational: a cure'
                elif effects & {129, 426}:
                    why = 'situational: TP'
                elif 74 in effects:
                    why = 'situational: a dispel'
                elif any(puts(skill, e) for e in effects):
                    kept = sorted(e for e in effects if puts(skill, e) and e in status_rules)
                    why = (f'a rule keeps effect {kept[0]} up: another skill gives it first' if kept
                           else 'no rule of the role uses it')
                else:
                    why = 'other'
                rows.append((role, character, level, cid, skill.name, why))
            print(role, level, cid, 'unused', sum(1 for r in rows if r[:4] == (role, character, level, cid)), flush=True)
    counts = {}
    for r in rows:
        key = r[-1].split(':')[0]
        counts[key] = counts.get(key, 0) + 1
    write('usage' if n == 1 else f'usage_{k}', ['| Role | Level | Fight | Skill never used | Why |', '|---|---|---|---|---|'] +
          [f'| {role} ({who}) | {lv} | {cid} | {name} | {why} |' for role, who, lv, cid, name, why in rows],
          f'{len(rows)} skills of a plan never used: ' + ', '.join(f'{v} {k}' for k, v in sorted(counts.items())))


ACTIVES_ENEMY = 510          # Meta-Kindra (level 90, no passive): the dummy of the actives phase
ACTIVE_TRIES = 30           # a 12% roll is missed 30 times in a row about 2 times in a hundred
ACTIVES_FALLBACK = 'papillon'   # the role that performs a hidden skill of no class


def snapshot(battle):
    return [(id(u), u.alive, u.hp, u.tp, tuple(sorted(u.statuses)), round(u.next_time, 6), len(getattr(u, 'items', {}) or {}),
             getattr(u, 'stolen', False)) for u in battle.units]


def actives(part='1/1'):
    import random
    from sim.battle import Battle, Action, AILMENTS, Status
    from sim.policy import usable_in_battle
    from sim.units import build_enemy
    from sim.data import ALLY, ALLY_ROW
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    chars = {c['name']: c for c in data.characters}
    cp = setup.checkpoint(LATE[1])
    gear = scenario.checkpoint_gear(data, setup, LATE[1])
    every = sorted((s for (cat, _), s in data.skills.items() if cat in ('Technique', 'Magic') and usable_in_battle(s)),
                   key=lambda s: s.id)
    mine = every[(k - 1) * len(every) // n: k * len(every) // n]

    def user_for(skill):
        for class_id in skill.classes or []:
            found = role_for(setup, data, class_id)
            if found:
                role = found[0]
                who = [x.strip() for x in str(setup.roles[role]['Characters (order of preference)']).split(';')][0]
                return scenario.build_role_member(data, setup, role, chars[who], LATE[0], gear, 0, False)
        # a hidden skill (the action of a doll, a result of a random skill) belongs to no class: any member performs it
        who = [x.strip() for x in str(setup.roles[ACTIVES_FALLBACK]['Characters (order of preference)']).split(';')][0]
        return scenario.build_role_member(data, setup, ACTIVES_FALLBACK, chars[who], LATE[0], gear, 0, False)

    def battle_for(user, seed):
        party = [u for u in scenario.reference_party(data, setup, cp['Chapter'], LATE[0], gear, 0, cp['Floor'])
                 if u.kind == 'member' and u.name != user.name][:4] + [user]
        for u in party:
            u.hp, u.tp = max(1, u.max_hp // 2), max(u.tp // 2, 0)
        user.max_tp, user.tp = 9999, 4999
        party[0].alive, party[0].hp = False, 0
        party[1].statuses[113] = Status(113, 0, 3)
        party[1].statuses[116] = Status(116, 0, 3)
        foes = [build_enemy(data, ACTIVES_ENEMY, True), build_enemy(data, ACTIVES_ENEMY, False)]
        for f in foes:
            f.immune, f.resist_base = set(), [0] * 8
            f.statuses[161] = Status(161, 0.2, 3, f)
        b = Battle(data, party, foes, random.Random(seed), setup=setup.settings)
        for u in b.units:
            u.next_time = 0.5           # so that a stun (gauge to 0, next turn at time + 1) shows as a change
        return b, foes

    rows = []
    for skill in mine:
        user = user_for(skill)
        if user is None:
            rows.append((skill, '-', 'no role learns it'))
            continue
        level = skill.levels or 1
        kinds = {(e, kind) for e, kind, _ in skill.effects}
        expect = {}
        if any((e in (0, 1) and kind == 4) or e in (8, 12, 138, 140, 141, 142, 434, 435) for e, kind in kinds):
            expect['damage'] = False
        for e, kind in kinds:
            if kind == 4 and e in AILMENTS:
                expect[f'ailment {e}'] = False
            if kind == 5:
                expect[f'status {e}'] = False
        if not expect:
            expect['anything'] = False
        for seed in range(ACTIVE_TRIES):
            b, foes = battle_for(user, seed)
            before = snapshot(b)
            hp_before = {id(u): u.hp for u in b.units}
            action = Action(user, 'skill', skill, level)
            if action.target_code in (ALLY, ALLY_ROW):
                action.target = b.units[2]                # a living member at half HP and TP
            try:
                b.perform(action)
            except Exception as ex:                                      # noqa: BLE001 - a crash is a finding
                expect = {f'crash {type(ex).__name__}: {ex}': False}
                break
            if 'damage' in expect and any(u.hp < hp_before.get(id(u), u.hp) for u in b.units):
                expect['damage'] = True
            for key in expect:
                if key.startswith('ailment '):
                    e = int(key.split()[1])
                    # stun is no status: the gauge goes to 0 (Battle.stun); instant death leaves no status either
                    others = [u for u in b.units if u is not b.units[0]]          # the fallen member aside
                    seen = (any(e in u.statuses for u in others) or (e == 118 and any(u.next_time > 0.5 for u in others))
                            or (e == 119 and any(not u.alive and hp_before.get(id(u)) for u in others)))
                    expect[key] = expect[key] or seen
                elif key.startswith('status '):
                    e = int(key.split()[1])
                    expect[key] = expect[key] or any(e in u.statuses for u in b.units)
            user.tp += action.tp_cost                     # the cost paid is no effect of the skill
            if 'anything' in expect and snapshot(b) != before:
                expect['anything'] = True
            if all(expect.values()):
                break
        missed = [key for key, ok in expect.items() if not ok]
        rows.append((skill, user.role, 'acts' if not missed else 'not seen: ' + ', '.join(missed)))
        print(skill.id, skill.name, rows[-1][-1], flush=True)
    flagged = sum(1 for r in rows if r[-1] != 'acts')
    write('actives' if n == 1 else f'actives_{k}', ['| Skill | Effects | Performed by | Result |', '|---|---|---|---|'] +
          [f'| {s.id} {s.name} | {", ".join(f"{e}/{kd}" for e, kd, _ in s.effects)} | {role} | {res} |'
           for s, role, res in rows],
          f'{len(rows) - flagged} act as their effects say, {flagged} to read, of {len(rows)} active skills')


def actives_engine(part='1/1'):
    """actives(), played by the C# engine in one call: the engine performs each skill on the prepared battles, this tool says what it expects."""
    import engine_client as engine
    from sim.battle import AILMENTS
    from sim.policy import usable_in_battle
    k, n = (int(x) for x in part.split('/'))
    data, setup = game_data(), setup_mod.load()
    chars = {c['name']: c for c in data.characters}
    cp = setup.checkpoint(LATE[1])
    every = sorted((s for (cat, _), s in data.skills.items() if cat in ('Technique', 'Magic') and usable_in_battle(s)),
                   key=lambda s: s.id)
    mine = every[(k - 1) * len(every) // n: k * len(every) // n]
    side, setup_name = engine.side_of(data), engine.setup_of(setup)
    prelude = {'halve': True, 'user_max_tp': 9999, 'user_tp': 4999, 'fallen': 0, 'statuses': [[1, 113, 0, 3], [1, 116, 0, 3]],
               'foes': [[ACTIVES_ENEMY, True], [ACTIVES_ENEMY, False]], 'foe_status': [161, 0.2, 3], 'next_time': 0.5}
    party_job = engine.make_job(side, LATE[1], runs=1, level=LATE[0], crown=0, setup=setup_name, name='actives')
    plan = []
    for skill in mine:
        role = who = None
        for class_id in skill.classes or []:
            found = role_for(setup, data, class_id)
            if found:
                role = found[0]
                who = [x.strip() for x in str(setup.roles[role]['Characters (order of preference)']).split(';')][0]
                break
        if role is None:
            # a hidden skill (the action of a doll, a result of a random skill) belongs to no class: any member performs it
            role = ACTIVES_FALLBACK
            who = [x.strip() for x in str(setup.roles[role]['Characters (order of preference)']).split(';')][0]
        kinds = {(e, kind) for e, kind, _ in skill.effects}
        expect = {}
        if any((e in (0, 1) and kind == 4) or e in (8, 12, 138, 140, 141, 142, 434, 435) for e, kind in kinds):
            expect['damage'] = False
        for e, kind in kinds:
            if kind == 4 and e in AILMENTS:
                expect[f'ailment {e}'] = False
            if kind == 5:
                expect[f'status {e}'] = False
        if not expect:
            expect['anything'] = False
        tests = []
        for key in expect:
            if key == 'damage':
                tests.append({'key': key, 'test': 'hp_lost'})
            elif key == 'anything':
                tests.append({'key': key, 'test': 'changed'})
            else:
                e = int(key.split()[1])
                test = {'key': key, 'test': 'ailment' if key.startswith('ailment') else 'status', 'effect': e}
                if key.startswith('ailment'):
                    # stun is no status: the gauge goes to 0 (Battle.stun); instant death leaves no status either
                    test.update({'gauge_above': prelude['next_time'] if e == 118 else None, 'fell': e == 119})
                tests.append(test)
        user = {'role': role, 'character': who, 'level': LATE[0], 'forge': False}
        plan.append((skill, role, expect, {'side': side, 'setup': setup_name, 'job': party_job, 'user': user, 'skill': skill.id,
                                           'level': skill.levels or 1, 'expect': tests, 'tries': ACTIVE_TRIES, 'prelude': prelude}))
    played = engine.probe([item for *_, item in plan])
    rows = []
    for (skill, role, expect, _), done in zip(plan, played):
        if done['crash'] is not None:
            expect = {'crash ' + done['crash']: False}
            missed = list(expect)
        else:
            missed = [key for key in expect if key in set(done['missed'])]
        rows.append((skill, role, 'acts' if not missed else 'not seen: ' + ', '.join(missed)))
        print(skill.id, skill.name, rows[-1][-1], flush=True)
    flagged = sum(1 for r in rows if r[-1] != 'acts')
    write('actives' if n == 1 else f'actives_{k}', ['| Skill | Effects | Performed by | Result |', '|---|---|---|---|'] +
          [f'| {s.id} {s.name} | {", ".join(f"{e}/{kd}" for e, kd, _ in s.effects)} | {role} | {res} |'
           for s, role, res in rows],
          f'{len(rows) - flagged} act as their effects say, {flagged} to read, of {len(rows)} active skills')


def write(phase, lines, summary):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, phase + '.md'), 'w', encoding='utf-8') as f:
        f.write(f'## {phase}\n\n{summary}.\n\n' + '\n'.join(lines) + '\n')
    print(summary)


def report():
    parts = sorted(p for p in os.listdir(OUT_DIR) if p.endswith('.md')) if os.path.isdir(OUT_DIR) else []
    text = ['# Audit of the simulator (generated)', '',
            'Generated by `tools/sim_audit.py`. Do not edit: run the phases again, then `report`.', '']
    flagged = []
    for p in parts:
        with open(os.path.join(OUT_DIR, p), encoding='utf-8') as f:
            body = f.read()
        text.append(body)
        if p.startswith('passives'):
            flagged += [line.split('|')[1].strip() for line in body.splitlines() if line.endswith('| no effect seen |')]
        if p.startswith('usage'):
            for line in body.splitlines():
                cells = [c.strip() for c in line.split('|')]
                if len(cells) > 5 and (cells[5].startswith('no rule') or cells[5].startswith('not usable')):
                    flagged.append(f"usage {cells[1].split(' (')[0]} | {cells[4]}")
        if p.startswith('actives'):
            flagged += [line.split('|')[1].strip() for line in body.splitlines()
                        if line.startswith('| ') and '| not seen' in line]
    readings = {str(r['ID']).strip(): r for r in setup_mod.load().audit_readings}
    unread = [x for x in flagged if x not in readings]
    text[4:4] = [f'**Checklist: {len(flagged) - len(unread)} of {len(flagged)} passives, active skills and skills never used have a reading** '
                 f'(sheet AuditReadings of data_tables/sim_setup.xlsx){": unread " + ", ".join(unread) if unread else ""}.', '',
                 '| Skill or point | Result | Reading |', '|---|---|---|'] + \
        [f'| {k} | {r["Result"]} | {r["Reading"]} |' for k, r in readings.items()] + ['']
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print('written', REPORT)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'passives': passives, 'usage': usage, 'actives': actives, 'report': report, 'passives-engine': passives_engine,
     'usage-engine': usage_engine, 'actives-engine': actives_engine}[sys.argv[1]](*sys.argv[2:])

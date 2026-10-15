"""
What each skill that deals no damage adds to a fight. Generated: docs/generated/SKILL_VALUE.md.

    python tools/skill_value.py all [k]    every such skill, in k processes at once (parallel_workers)
    python tools/skill_value.py report
    python tools/skill_value.py engine [k/n]              the passes of `run` (k/n: a slice of the skills), played by the C# engine
    python tools/skill_value.py engine-ailments [k/n]     the passes of `ailments`, played by the C# engine

For each technique or spell usable in battle that deals no damage (none of the attacking options of
tools/skill_worth.py), a role whose path passes through a class that learns it, at the first stage of the sheet
ClassStages where that class is played, on the first skill_value_checkpoints checkpoints of that stage (0: all of them). On the Balance
variant, the reference party plays the boss fights with that member in the last place twice: once without the skill,
and once with it at its top level and a rule, placed just before the role's damage rule, that makes her use it when it can serve (a status it puts and the
target lacks, an ailment, a cure or a heal when someone needs it, else every turn). The difference of wins and of the
mean length of the won fights is the worth of the skill there. A skill worth less than skill_value_floor of length and
nothing in wins is a row to read: dead, or useful where the fights of the audit do not show it.
"""
import json
import os
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'skill_value')
REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'SKILL_VALUE.md')

from sim import scenario, measures                       # noqa: E402
from sim import setup as setup_mod                       # noqa: E402
from sim import policy as P                              # noqa: E402
from sim.battle import AILMENTS                          # noqa: E402
from sim.data import game_data                           # noqa: E402
from sim.variant import balance_data                     # noqa: E402
import class_stages                                      # noqa: E402

HEALS = {103, 9, 104, 128, 130, 131, 132, 133}


def rule_for(skill):
    """(condition, action) of the rule that makes a member use the skill where it serves."""
    effects = [(e, k) for e, k, _ in skill.effects]
    if any(e in (105,) for e, _ in effects):
        return 'ally_down', 'revive'
    if any(e in (106, 235) for e, _ in effects):
        return 'ally_ailing', 'cure'
    if any(e in HEALS for e, _ in effects):
        return 'ally_hp_below:0.7', 'heal:0.7'
    if any(e in (129, 426) for e, _ in effects):
        return 'ally_tp_below:0.5', 'tp:0.5'
    ailment = next((e for e, k in effects if e in AILMENTS and k != 2), None)
    if ailment is not None:
        return 'always', f'ailment:{ailment}'
    status = next((e for e, k in effects if k in (4, 5) and e not in AILMENTS), None)
    if status is not None and P.puts(skill, status):
        return 'always', f'status:{status}'
    return 'always', f'skill:{skill.name}'


def place(data, setup, skill):
    """(role, stage row) where the skill is first played, or None."""
    names = {data.class_names.get(c) for c in skill.classes or []}
    for st in class_stages.stages(setup):
        col = {'base': 'Base class', 'intermediate': 'Lv15 class'}.get(st['Stage'], 'Lv30 class')
        for role, row in setup.roles.items():
            if row[col] in names:
                return role, st
    return None


def candidates(data):
    import skill_worth                                    # noqa: F401  (the attacking ones are left out)
    out = []
    for (cat, sid), s in sorted(data.skills.items(), key=lambda x: x[0][1]):
        if cat not in ('Technique', 'Magic') or not s.classes or not P.usable_in_battle(s):
            continue
        attacking = any(e in (0, 1, 8, 12, 138, 140, 141, 142, 434, 435) and k in (2, 4) for e, k, _ in s.effects) \
            or any(e in P.RANDOM_MOVES for e, _, _ in s.effects)
        if not attacking:
            out.append(s)
    return out


def play(data, setup, role, cid, skill, use, chain=0):
    """chain > 0: a row of that many random battles of the floor (HP and TP carried over) instead of the boss fights."""
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}
    names = [n.strip() for n in str(setup.roles[role]['Characters (order of preference)']).split(';')]
    extra = {skill.id: (skill.levels or 1) if use else 0}

    def party():
        whole = scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
        kept = [u for u in whole if u.kind == 'member'][:-1]
        who = next(n for n in names if n in chars and n not in {u.name for u in kept})
        tested = scenario.build_role_member(data, setup, role, chars[who], level, gear, 0,
                                            scenario.forge_open(setup, cp['Floor']), extra,
                                            pieces=scenario.unique_pieces(setup, role, cp['Chapter'], cp['Floor']),
                                            sealbook=scenario.personal_sealbook(setup, role, cp['Chapter'], cp['Floor']))
        tested.items = kept[0].items if kept else {}
        return kept + [tested] + [u for u in whole if u.kind != 'member']

    zones = scenario.walked_zones(data, setup, cp['Floor'], level)
    rng = random.Random(7)

    def enemies():
        if chain and zones:
            return [measures.random_group(data, rng.choice(zones), rng) for _ in range(chain)]
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    saved = setup.policies
    if use:
        # the rule goes just before the role's own damage rule: revives, heals and its usual buffs keep their place
        cond, act = rule_for(skill)
        mine = sorted((r for r in saved if r['Role'] == role), key=lambda r: r['Order'])
        cut = next((r['Order'] for r in mine if str(r['Action']).startswith('damage')), max([r['Order'] for r in mine] or [0]) + 1)
        if chain and act.startswith('ailment:'):
            # on random battles an ailment is an opening move: after revives, heals and cures, before the buffs a
            # short fight never reaches the end of (placed before the damage rule, a Sage cast it 5 times in 80 fights)
            cut = next((r['Order'] for r in mine if not str(r['Action']).startswith(('revive', 'heal', 'cure'))), cut)
        moved = [dict(r, Order=r['Order'] + 1) if r['Role'] == role and r['Order'] >= cut else r for r in saved]
        setup.policies = moved + [{'Role': role, 'Order': cut, 'Condition': cond, 'Action': act}]
    try:
        res = scenario.play(data, setup, party, enemies, runs=int(setup.settings['check_runs']))
    finally:
        setup.policies = saved
    won = [r for r in res if r['won']]
    return {'won': len(won) / len(res), 'time_won': sum(r['time'] for r in won) / len(won) if won else None,
            'hp_left': sum(r['hp_left'] for r in res) / len(res)}


def engine_job(data, setup, role, cid, skill, use, chain=0):
    """The job of the C# engine that plays what play() plays."""
    import engine_client as engine
    cp = setup.checkpoint(cid)
    level = scenario.reference_levels(data, setup)[cid][0]
    extra = {skill.id: (skill.levels or 1) if use else 0}
    zones = scenario.walked_zones(data, setup, cp['Floor'], level)
    enemies = {'kind': 'chain', 'zones': [z['name'] for z in zones], 'seed': 7, 'battles': chain} if chain and zones else None
    rows = None
    if use:
        saved = setup.policies
        cond, act = rule_for(skill)
        mine = sorted((r for r in saved if r['Role'] == role), key=lambda r: r['Order'])
        cut = next((r['Order'] for r in mine if str(r['Action']).startswith('damage')), max([r['Order'] for r in mine] or [0]) + 1)
        if chain and act.startswith('ailment:'):
            cut = next((r['Order'] for r in mine if not str(r['Action']).startswith(('revive', 'heal', 'cure'))), cut)
        moved = [dict(r, Order=r['Order'] + 1) if r['Role'] == role and r['Order'] >= cut else r for r in saved]
        rows = moved + [{'Role': role, 'Order': cut, 'Condition': cond, 'Action': act}]
    recipe = {'drop_last': True, 'items': 'first_kept',
              'tested': [{'role': role, 'forge': bool(scenario.forge_open(setup, cp['Floor'])), 'unique_pieces': True,
                          'extra_skills': {str(k): v for k, v in extra.items()}}]}
    return engine.make_job(engine.side_of(data), cid, runs=int(setup.settings['check_runs']), crown=0, setup=engine.setup_of(setup),
                           recipe=recipe, enemies=enemies, policy_rows=rows, name=f'{skill.name}|{role}|{cid}|{int(use)}|{chain}')


def engine_figures(done):
    res = done['runs']
    won = [r for r in res if r['won']]
    return {'won': len(won) / len(res), 'time_won': sum(r['time'] for r in won) / len(won) if won else None,
            'hp_left': sum(r['hp_left'] for r in res) / len(res)}


def play_engine(data, setup, role, cid, skill, use, chain=0):
    """play(), played by the C# engine."""
    import engine_client as engine
    return engine_figures(engine.run_jobs([engine_job(data, setup, role, cid, skill, use, chain)])[0])


def run_engine(part='1/1'):
    """run(), played by the C# engine in one call."""
    import time
    import engine_client as engine
    started = time.time()
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    every = candidates(data)
    mine = every[(k - 1) * len(every) // n: k * len(every) // n]
    count = int(setup.settings['skill_value_checkpoints'])
    plan = []
    for skill in mine:
        found = place(data, setup, skill)
        if found is None:
            plan.append((skill, None, None, []))
            continue
        role, st = found
        cids = [c.strip() for c in str(st['Checkpoints']).split(';')]
        plan.append((skill, role, st, cids[:count] if count else cids))
    jobs = [engine_job(data, setup, role, cid, skill, use) for skill, role, st, cids in plan if role is not None
            for cid in cids for use in (False, True)]
    done = iter(engine.run_jobs(jobs))
    rows = []
    for skill, role, st, cids in plan:
        if role is None:
            rows.append({'skill': skill.name, 'role': None})
            continue
        cells = []
        for cid in cids:
            without = engine_figures(next(done))
            with_it = engine_figures(next(done))
            cells.append({'checkpoint': cid, 'without': without, 'with': with_it})
        rows.append({'skill': skill.name, 'role': role, 'stage': st['Stage'], 'rule': ' / '.join(rule_for(skill)), 'cells': cells})
        print(skill.name, role, flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    if part == '1/1':
        for name in os.listdir(OUT_DIR):
            os.remove(os.path.join(OUT_DIR, name))
    with open(os.path.join(OUT_DIR, f'part_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f)
    print(f'{len(rows)} skills in {time.time() - started:.0f} s')


def run(part='1/1'):
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    every = candidates(data)
    mine = every[(k - 1) * len(every) // n: k * len(every) // n]
    count = int(setup.settings['skill_value_checkpoints'])
    rows = []
    for skill in mine:
        found = place(data, setup, skill)
        if found is None:
            rows.append({'skill': skill.name, 'role': None})
            continue
        role, st = found
        cids = [c.strip() for c in str(st['Checkpoints']).split(';')]
        cids = cids[:count] if count else cids
        cells = []
        for cid in cids:
            without = play(data, setup, role, cid, skill, False)
            with_it = play(data, setup, role, cid, skill, True)
            cells.append({'checkpoint': cid, 'without': without, 'with': with_it})
        rows.append({'skill': skill.name, 'role': role, 'stage': st['Stage'], 'rule': ' / '.join(rule_for(skill)),
                     'cells': cells})
        print(skill.name, role, flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f'part_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f)


def hostile_skills(data):
    """The skills of theme T07: an ailment on enemies, or a status that lowers them (a negative value on a target of
    the other side)."""
    from sim.data import SINGLE, RANDOM, ROW, PIERCE, ALL
    out = []
    for s in candidates(data):
        enemy = s.target in (SINGLE, RANDOM, ROW, PIERCE, ALL)
        ailment = any(e in AILMENTS and k != 2 for e, k, _ in s.effects)
        debuff = enemy and any(k == 5 and min(v) < 0 for e, k, v in s.effects)
        if enemy and (ailment or debuff):
            out.append(s)
    return out


def ailments(part='1/1'):
    """T07: each hostile skill on the boss fights and on rows of random battles (ailment_chain) of the stage where it
    is first played, with it (the rule of rule_for) and without."""
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    every = hostile_skills(data)
    chain = int(setup.settings['ailment_chain'])
    rows = []
    for skill in every[(k - 1) * len(every) // n: k * len(every) // n]:
        found = place(data, setup, skill)
        if found is None:
            continue
        role, st = found
        cells = []
        for cid in [c.strip() for c in str(st['Checkpoints']).split(';')]:
            for context, length in (('boss', 0), ('random', chain)):
                cells.append({'checkpoint': cid, 'context': context,
                              'without': play(data, setup, role, cid, skill, False, length),
                              'with': play(data, setup, role, cid, skill, True, length)})
        rows.append({'skill': skill.name, 'role': role, 'stage': st['Stage'], 'rule': ' / '.join(rule_for(skill)),
                     'cells': cells})
        print(skill.name, role, flush=True)
    out = os.path.join(BASE_DIR, 'docs', 'generated', 'skill_ailments')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f'part_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f)


def run_engine_ailments(part='1/1'):
    """ailments(), played by the C# engine in one call."""
    import time
    import engine_client as engine
    started = time.time()
    k, n = (int(x) for x in part.split('/'))
    data, setup = balance_data(game_data()), setup_mod.load()
    every = hostile_skills(data)
    chain = int(setup.settings['ailment_chain'])
    plan = []
    for skill in every[(k - 1) * len(every) // n: k * len(every) // n]:
        found = place(data, setup, skill)
        if found is None:
            continue
        role, st = found
        plan.append((skill, role, st, [c.strip() for c in str(st['Checkpoints']).split(';')]))
    jobs = [engine_job(data, setup, role, cid, skill, use, length) for skill, role, st, cids in plan
            for cid in cids for context, length in (('boss', 0), ('random', chain)) for use in (False, True)]
    done = iter(engine.run_jobs(jobs))
    rows = []
    for skill, role, st, cids in plan:
        cells = []
        for cid in cids:
            for context, length in (('boss', 0), ('random', chain)):
                without = engine_figures(next(done))
                with_it = engine_figures(next(done))
                cells.append({'checkpoint': cid, 'context': context, 'without': without, 'with': with_it})
        rows.append({'skill': skill.name, 'role': role, 'stage': st['Stage'], 'rule': ' / '.join(rule_for(skill)), 'cells': cells})
        print(skill.name, role, flush=True)
    out = os.path.join(BASE_DIR, 'docs', 'generated', 'skill_ailments')
    os.makedirs(out, exist_ok=True)
    if part == '1/1':
        for name in os.listdir(out):
            os.remove(os.path.join(out, name))
    with open(os.path.join(out, f'part_{k}.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f)
    print(f'{len(rows)} skills in {time.time() - started:.0f} s')


def ailments_report():
    out = os.path.join(BASE_DIR, 'docs', 'generated', 'skill_ailments')
    rows = []
    for name in sorted(os.listdir(out)) if os.path.isdir(out) else []:
        with open(os.path.join(out, name), encoding='utf-8') as f:
            rows += json.load(f)
    lines = []
    for r in sorted(rows, key=lambda r: r['skill']):
        figs = []
        for context in ('boss', 'random'):
            cells = [c for c in r['cells'] if c['context'] == context]
            wins = sum(c['with']['won'] - c['without']['won'] for c in cells) / max(1, len(cells))
            gains = [1 - c['with']['time_won'] / c['without']['time_won'] for c in cells
                     if c['with']['time_won'] and c['without']['time_won']]
            hp = sum(c['with']['hp_left'] - c['without']['hp_left'] for c in cells) / max(1, len(cells))
            figs.append(f"{wins:+.0%} / {(sum(gains) / len(gains) if gains else 0):+.0%} / {hp:+.0%}")
        lines.append(f"| {r['skill']} | {r['role']} ({r['stage']}) | {r['rule']} | {figs[0]} | {figs[1]} |")
    text = ['# Ailments and debuffs: what each adds (generated)', '',
            'Generated by `tools/skill_value.py ailments`. Do not edit. Balance variant. Each hostile skill at the '
            'stage where it is first played, used by its role before attacking where it can land (an ailment on random '
            'rows: as the opening move, after revives, heals and cures), against the role '
            'without it. Cells: wins / length of the won fights (shorter is +) / party HP left at the end. Boss: the '
            'boss fights of the stage; random: rows of ailment_chain random battles of each floor, HP and TP carried.',
            '', '| Skill | Played as | Rule | Boss | Random rows |', '|---|---|---|---|---|'] + lines
    with open(os.path.join(BASE_DIR, 'docs', 'generated', 'SKILL_AILMENTS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print(len(rows), 'skills')


def run_all(n=None):
    import subprocess
    import time
    setup = setup_mod.load()
    n = int(n or setup.settings.get('parallel_workers', 1))
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'run', f'{k}/{n}'],
                              stdout=subprocess.DEVNULL) for k in range(1, n + 1)]
    started = time.time()
    for p in procs:
        p.wait()
    print(f'{n} parts in {time.time() - started:.0f} s')


def report():
    setup = setup_mod.load()
    floor = float(setup.settings['skill_value_floor'])
    rows = []
    for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
        with open(os.path.join(OUT_DIR, name), encoding='utf-8') as f:
            rows += json.load(f)
    lines, flagged = [], 0
    for r in sorted(rows, key=lambda r: r['skill']):
        if r['role'] is None:
            lines.append(f"| {r['skill']} | - | - | - | - | no role plays a class that learns it |")
            continue
        wins = sum(c['with']['won'] - c['without']['won'] for c in r['cells']) / len(r['cells'])
        gains = [1 - c['with']['time_won'] / c['without']['time_won'] for c in r['cells']
                 if c['with']['time_won'] and c['without']['time_won']]
        gain = sum(gains) / len(gains) if gains else 0.0
        verdict = 'to read' if gain < floor and wins <= 0 else 'serves'
        flagged += verdict == 'to read'
        lines.append(f"| {r['skill']} | {r['role']} ({r['stage']}) | {r['rule']} | {wins:+.0%} | {gain:+.0%} | {verdict} |")
    text = ['# What each skill that deals no damage adds (generated)', '',
            'Generated by `tools/skill_value.py`. Do not edit. Balance variant; boss fights of the first stage where '
            'the class is played; the member with the skill used first where it serves, against the member without '
            f'it. Wins: the change of the share of wins. Length: how much shorter the won fights are. Below {floor:.0%} '
            'of length and no wins gained: to read.', '',
            f'**{len(rows) - flagged} of {len(rows)} skills serve in the fights of the audit; {flagged} to read.**', '',
            '| Skill | Played as | Rule | Wins | Length | Verdict |', '|---|---|---|---|---|---|'] + lines
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print(text[5])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'run': run, 'all': run_all, 'report': report, 'ailments': ailments, 'ailments_report': ailments_report,
     'engine': run_engine, 'engine-ailments': run_engine_ailments}[sys.argv[1]](*sys.argv[2:])

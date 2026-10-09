"""
What each attacking skill is worth beside the best one of its own class, at the stages where the class is played.
Generated: docs/generated/SKILL_WORTH.md.

    python mod_project/tools/skill_worth.py all        every stage of the sheet ClassStages, one process each
    python mod_project/tools/skill_worth.py report     joins them

On the Balance variant, at each checkpoint of a stage, for each role of the sheet Roles: the member of that role (the
class its path gives at the reference level) knows every technique and spell of the classes of her path so far at
its top level, and stands in the last place of the reference party. Two contexts: the boss fight of the checkpoint,
and skill_worth_groups random battles of the floor of the checkpoint (sim/measures.py random_group). For each option
that deals damage, its value (policy.damage_value: the damage over its targets, each capped at its HP) per time and per
TP (policy: time_of, tp_penalty), against the best option of the same member in the same context. A skill is worth its
best figure over every context, checkpoint and role where it can be used; below skill_dead_ratio (Settings) it is dead
for damage. Skills that deal no damage are listed apart: their worth is read by hand.
"""
import json
import os
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# SKILL_WORTH_SPEC='Skill:field:factor;...': a trial of changes, written to scratch_skill_worth (not the report)
OUT_DIR = os.path.join(BASE_DIR, 'docs', 'generated', 'skill_worth' if not os.environ.get('SKILL_WORTH_SPEC')
                       else 'skill_worth_trial')
REPORT = os.path.join(BASE_DIR, 'docs', 'generated', 'SKILL_WORTH.md')

from sim import scenario, measures                       # noqa: E402
from sim import setup as setup_mod                       # noqa: E402
from sim import policy as P                              # noqa: E402
from sim.battle import Battle, Action                    # noqa: E402
from sim.data import game_data, SINGLE, RANDOM, ROW, PIERCE, ALL, EVERYONE   # noqa: E402
from sim.variant import balance_data                     # noqa: E402
import class_stages                                      # noqa: E402


def full_member(data, setup, role, level, gear, cp):
    """The role's member at the level, with every active skill of her classes so far at its top level."""
    chars = {c['name']: c for c in data.characters}
    row = setup.roles[role]
    who = [n.strip() for n in str(row['Characters (order of preference)']).split(';')][0]
    learnable = set(scenario.classes_so_far(data, row, level))
    extra = {s.id: s.levels or 1 for s in data.skills.values()
             if s.category in ('Technique', 'Magic') and set(s.classes or []) & learnable and P.usable_in_battle(s)}
    return scenario.build_role_member(data, setup, role, chars[who], level, gear, 0,
                                      scenario.forge_open(setup, cp['Floor']), extra,
                                      pieces=scenario.unique_pieces(setup, role, cp['Chapter'], cp['Floor']),
                                      sealbook=scenario.personal_sealbook(setup, role, cp['Chapter'], cp['Floor']))


def scores(data, setup, member, party, enemies, policy):
    """{skill name: value per time and TP} of every damaging option, and the class of each skill."""
    b = Battle(data, party, enemies, random.Random(0), setup=setup.settings, zone=getattr(enemies, 'zone', None))
    member.tp = member.max_tp
    out = {}
    for skill, level in P.options(b, member):
        act = Action(member, 'skill', skill, level)
        hits = act.target_code in (SINGLE, RANDOM, ROW, PIERCE, ALL, EVERYONE) and (
            act.physical or act.magic or b.special(act)) or any(act.has(e) for e in P.RANDOM_MOVES)
        if not hits:
            continue
        total, _ = P.damage_value(b, act)
        out[skill.name] = total / policy.time_of(b, act) / policy.tp_penalty(member, act)
    attack = Action(member, 'attack')
    total, _ = P.damage_value(b, attack)
    out['(plain attack)'] = total / policy.time_of(b, attack)
    return out


def changed(data, spec):
    """spec 'Skill:field:factor;...' (field e<effect id> or tp): a trial on top of the variant, for proposals."""
    changes = []
    for part in [p for p in (spec or '').split(';') if p]:
        name, field, factor = part.split(':')
        for (cat, sid), s in data.skills.items():
            if s.name != name:
                continue
            if field == 'tp':
                changes.append(('skills', (cat, sid), 'tp', [max(1, int(t * float(factor))) for t in s.tp]))
            elif field.endswith('+'):                          # e26+: added to every level, not multiplied
                eid = int(field[1:-1])
                changes.append(('skills', (cat, sid), 'effects', [(e, k, [round(v + float(factor), 3) for v in vals]
                                                                   if e == eid else vals) for e, k, vals in s.effects]))
            else:
                eid = int(field[1:])
                changes.append(('skills', (cat, sid), 'effects', [(e, k, [v * float(factor) for v in vals] if e == eid
                                                                   else vals) for e, k, vals in s.effects]))
    return data.with_changes(changes) if changes else data


def run(stage):
    data, setup = changed(balance_data(game_data()), os.environ.get('SKILL_WORTH_SPEC')), setup_mod.load()
    policy = P.Policy(P.load_rules(setup.policies), setup.settings)
    st = next(s for s in class_stages.stages(setup) if s['Stage'] == stage)
    groups = int(setup.settings['skill_worth_groups'])
    rows = []
    for cid in [c.strip() for c in str(st['Checkpoints']).split(';')]:
        cp = setup.checkpoint(cid)
        level = scenario.reference_levels(data, setup)[cid][0]
        gear = scenario.checkpoint_gear(data, setup, cid)
        boss = scenario.fixed_battle(data, cp['Floor'], scenario.battle_numbers(cp)[-1])
        zones = [z for z in data.floors if z['name'].split(' zone')[0] == cp['Floor'] and z['formations']] or \
                [z for z in data.floors if z['name'][:4] == cp['Floor'][:4] and z['formations']]
        rng = random.Random(1)
        randoms = [measures.random_group(data, rng.choice(zones), rng) for _ in range(groups)] if zones else []
        for role in setup.roles:
            member = full_member(data, setup, role, level, gear, cp)
            base = [u for u in scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
                    if u.kind == 'member' and u.name != member.name][:4]
            party = base + [member]
            cls = data.class_names.get(scenario.class_path(data, setup.roles[role], level)[0])
            contexts = [('boss', scores(data, setup, member, party, boss, policy))]
            for k, g in enumerate(randoms):
                contexts.append((f'random {k}', scores(data, setup, member, party, g, policy)))
            for name, sc in contexts:
                best = max(sc.values()) if sc else 0.0
                for skill, value in sc.items():
                    rows.append({'checkpoint': cid, 'role': role, 'class': cls, 'context': name.split()[0],
                                 'skill': skill, 'ratio': value / best if best else 0.0,
                                 'best': max(sc, key=sc.get)})
        print(stage, cid, 'done', flush=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, f'{stage}.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f)


def run_all():
    import subprocess
    setup = setup_mod.load()
    procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), 'run', st['Stage']])
             for st in class_stages.stages(setup)]
    for p in procs:
        p.wait()


def report():
    data, setup = game_data(), setup_mod.load()
    dead = float(setup.settings['skill_dead_ratio'])
    best = {}
    for name in sorted(os.listdir(OUT_DIR)) if os.path.isdir(OUT_DIR) else []:
        with open(os.path.join(OUT_DIR, name), encoding='utf-8') as f:
            for r in json.load(f):
                if r['skill'] == '(plain attack)':
                    continue
                key = r['skill']
                if key not in best or r['ratio'] > best[key]['ratio']:
                    best[key] = r
    attacking = sorted(best.items(), key=lambda x: x[1]['ratio'])
    damaging = set(best)
    others = sorted({s.name for s in data.skills.values() if s.category in ('Technique', 'Magic') and s.classes
                     and P.usable_in_battle(s)} - damaging)
    n_dead = sum(1 for _, r in attacking if r['ratio'] < dead)
    text = ['# What each attacking skill is worth (generated)', '',
            'Generated by `tools/skill_worth.py`. Do not edit. Balance variant. Worth: the best share, over every '
            'checkpoint of its stages, role and context (the boss fight or a random battle of the floor), of the '
            'value per time and TP of the best attacking option of the same member, every skill at its top level. '
            f'Below {dead:.0%} (Settings skill_dead_ratio) a skill is dead for damage.', '',
            f'**{len(attacking) - n_dead} of {len(attacking)} attacking skills worth at least {dead:.0%} of the best of '
            f'their class somewhere; {n_dead} dead for damage. {len(others)} skills deal no damage (read by hand).**', '',
            '| Skill | Worth | Where (checkpoint, role, class, context) | Best there |', '|---|---|---|---|']
    for skill, r in attacking:
        flag = ' **dead**' if r['ratio'] < dead else ''
        text.append(f"| {skill} | {r['ratio']:.0%}{flag} | {r['checkpoint']}, {r['role']}, {r['class']}, {r['context']} | "
                     f"{r['best']} |")
    text += ['', '## Skills that deal no damage (read by hand)', '', ', '.join(others), '']
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print(text[6])


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'run': run, 'all': run_all, 'report': report}[sys.argv[1]](*sys.argv[2:])

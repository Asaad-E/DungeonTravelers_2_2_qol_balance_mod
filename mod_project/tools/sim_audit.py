"""
Audit of the simulator: does every rule it holds actually act? Generated: docs/generated/SIM_AUDIT.md.

    python mod_project/tools/sim_audit.py passives [k/n]   every passive skill, with and without, in the same fights
                                                          (k/n: the k-th of n slices, one process each)
    python mod_project/tools/sim_audit.py usage         the skills of each role's plan it never uses in its fights
    python mod_project/tools/sim_audit.py report        joins the parts written so far into SIM_AUDIT.md

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
    cp = setup.checkpoint(cid)
    gear = scenario.checkpoint_gear(data, setup, cid)
    chars = {c['name']: c for c in data.characters}

    def party():
        tested = scenario.build_role_member(data, setup, role, chars[character], level, gear, 0,
                                            scenario.forge_open(setup, cp['Floor']), extra)
        members = [u for u in scenario.reference_party(data, setup, cp['Chapter'], level, gear, 0, cp['Floor'])
                   if u.name != character]
        same = next((k for k, u in enumerate(members) if u.role == role), None)
        if same is not None:
            members[same] = tested
        else:
            members = members[:int(setup.settings.get('party_size', 5)) - 1] + [tested]
        for u in members:
            u.items = members[0].items
        return members

    def enemies():
        return [scenario.fixed_battle(data, cp['Floor'], n) for n in scenario.battle_numbers(cp)]

    return scenario.play(data, setup, party, enemies, runs=SEEDS)


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


def usage():
    from sim.policy import usable_in_battle
    data, setup = game_data(), setup_mod.load()
    chars = {c['name']: c for c in data.characters}
    rows = []
    for role, row in setup.roles.items():
        character = [n.strip() for n in str(row['Characters (order of preference)']).split(';')][0]
        if character not in chars:
            continue
        for level, cid in [(lv, c) for _, lv, c in TIERS] + [LATE]:
            res = fights(data, setup, role, character, level, cid, None)
            known = {}
            used = set()
            for r in res:
                for part in r['parts']:
                    for (u, name), n in part['record'].skill_uses.items():
                        if getattr(u, 'role', None) == role and u.name == character:
                            used.add(name)
            member = scenario.build_role_member(data, setup, role, chars[character], level, 0)
            for sid, lv in member.skills.items():
                skill = data.skill_by_id.get(sid)
                if skill is not None and usable_in_battle(skill):
                    known[skill.name] = lv
            unused = sorted(n for n in known if n not in used)
            won = sum(r['won'] for r in res) / len(res)
            rows.append((role, character, level, cid, won, len(known), unused))
            print(role, level, cid, f'won {won:.0%}', 'unused:', unused, flush=True)
    flagged = sum(1 for r in rows if r[-1])
    write('usage', ['| Role | Level | Fight | Won | Skills | Never used |', '|---|---|---|---|---|---|'] +
          [f'| {role} ({who}) | {lv} | {cid} | {won:.0%} | {n} | {", ".join(unused) or "-"} |'
           for role, who, lv, cid, won, n, unused in rows],
          f'{flagged} of {len(rows)} role and level rows leave a skill of their plan unused')


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
    readings = {str(r['ID']).strip(): r for r in setup_mod.load().audit_readings}
    unread = [x for x in flagged if x not in readings]
    text[4:4] = [f'**Checklist: {len(flagged) - len(unread)} of {len(flagged)} passives seen doing nothing have a reading** '
                 f'(sheet AuditReadings of data_tables/sim_setup.xlsx){": unread " + ", ".join(unread) if unread else ""}.', '',
                 '| Passive | Result | Reading |', '|---|---|---|'] + \
        [f'| {k} | {r["Result"]} | {r["Reading"]} |' for k, r in readings.items()] + ['']
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(text) + '\n')
    print('written', REPORT)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    {'passives': passives, 'usage': usage, 'report': report}[sys.argv[1]](*sys.argv[2:])

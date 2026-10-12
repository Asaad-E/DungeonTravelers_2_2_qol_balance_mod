"""Who actually stands in each of the 5 battery parties at each of the 17 checkpoints (vanilla and variant): number
of members, the role each fills, class, level. A party the battery calls 'Juggernaut' may hold fewer than five members
or members in the wrong role when the characters of a base class have not joined yet."""
import os
import sys
import collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from sim import scenario, setup as setup_mod
from sim.data import game_data
from sim.variant import balance_data
import parallel_party_battery as B

data = game_data()
setup = setup_mod.load()
variant = balance_data(data)
which = sys.argv[1] if len(sys.argv) > 1 else 'table'

if which == 'roles':
    for name, role in setup.roles.items():
        print(name, '|', {k: v for k, v in role.items() if k in ('Base class', 'Characters (order of preference)', 'Row', 'Weapon', 'Class path', 'Classes')})
    print('joins:', setup.joins)
    sys.exit()

problems = collections.Counter()
for pname, info in B.PARTIES.items():
    print(f'===== {pname}: roles asked {info["roles"]}')
    for cid in B.CHECKPOINTS:
        row = []
        for label, d in (('van', data), ('mod', variant)):
            party = B.build_party_complete(d, setup, info['roles'], cid)
            members = [u for u in party if u.kind == 'member']
            got = [u.role for u in members]
            row.append((label, members, got, [u for u in party if u.kind != 'member']))
        label, members, got, extra = row[0]
        missing = [r for r in info['roles'] if r not in got]
        dup = [r for r, c in collections.Counter(got).items() if c > 1]
        flag = ''
        if len(members) < 5:
            flag += f'  <-- ONLY {len(members)} MEMBERS'
            problems[(pname, 'short')] += 1
        if missing:
            flag += f'  <-- roles not filled: {missing}'
            problems[(pname, 'missing role')] += 1
        if dup:
            flag += f'  <-- duplicated: {dup}'
        desc = ', '.join(f"{u.name}:{data.class_names.get(getattr(u, 'class_id', None), getattr(u, 'role', '?'))}/{u.role} L{u.level}{'f' if u.front else 'b'}"
                         for u in members)
        same = [u.role for u in row[1][1]] == got
        print(f'  {cid}: {len(members)} members{" + " + extra[0].name if extra else ""} | {desc}{flag}{"" if same else "  (variant differs)"}')
print('problems:', dict(problems))

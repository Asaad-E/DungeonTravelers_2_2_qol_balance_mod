"""One-off (2026-10-16, before sim/ was removed): data_tables/engine_coverage.json, what tools/sim_coverage.py read from the
Python simulator: the effects the battle acts on (HANDLED, with where) and those it assumes (ASSUMED), and the commands,
sources and target kinds of the enemy AI it has a branch for. The C# engine was proven equal to sim/ on that day, so these
are the coverage of the engine; the checklist reads them from the JSON from now on."""
import ast
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'tools')]
import enemy_ai                                             # noqa: E402
from sim import ai, battle                                  # noqa: E402

tree = ast.parse(open(ai.__file__, encoding='utf-8').read())
commands, sources, targets = set(), set(), set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ('passes', 'source_value', 'pick_by_kind'):
        found = {'passes': commands, 'source_value': sources, 'pick_by_kind': targets}[node.name]
        for sub in ast.walk(node):
            if isinstance(sub, ast.Compare):
                for comp in sub.comparators:
                    if isinstance(comp, ast.Constant) and isinstance(comp.value, int):
                        found.add(comp.value)
                    if isinstance(comp, ast.Tuple):
                        found.update(e.value for e in comp.elts if isinstance(e, ast.Constant))
commands |= {enemy_ai.SET, enemy_ai.TARGET}
out = {
    'about': 'What the battle engine acts on: the effects it handles (and where), those it assumes, and the commands, sources and '
             'target kinds of the enemy AI it has a branch for. Taken on 2026-10-16 from the Python simulator, proven equal to '
             'the C# engine that day; read by tools/sim_coverage.py. A change of the engine that handles more updates it.',
    'handled': {str(e): where for e, where in sorted(battle.HANDLED.items())},
    'assumed': {str(e): text for e, text in sorted(battle.ASSUMED.items())},
    'ai': {'commands': sorted(commands), 'sources': sorted(sources), 'targets': sorted(targets)},
    'check_change': True,
}
with open(os.path.join(ROOT, 'data_tables', 'engine_coverage.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
    f.write('\n')
print(len(out['handled']), 'handled,', len(out['assumed']), 'assumed')

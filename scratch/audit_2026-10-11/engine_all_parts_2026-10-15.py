"""One-off edit: the measures split in parts get `engine` (no part, or 'all') that plays every part at once on the engine."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NAMES = ['mercenaries', 'party_skills', 'postgame_compare', 'unique_skills', 'skill_value_contested']

for name in NAMES:
    path = os.path.join(ROOT, 'measures', name + '.py')
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    i = next(n for n, line in enumerate(lines) if line.startswith('def run_engine(part'))
    if "'all'" in lines[i + 2]:
        continue
    lines[i] = lines[i].replace('def run_engine(part', "def run_engine(part='all'", 1)
    # skill_value_contested has no docstring there: edited by hand the same way
    assert lines[i + 1].strip().startswith('"""') and lines[i + 1].strip().endswith('"""'), (name, lines[i + 1])
    rest = lines[i][len("def run_engine(part='all'"):].rstrip(':').rstrip(')').lstrip(',').strip()
    extra = [x.split('=')[0].strip() for x in rest.split(',') if x.strip()]
    lines[i + 1:i + 1] = []
    lines.insert(i + 2, "    if part == 'all':                          # every part at once, one process each")
    lines.insert(i + 3, '        import engine_client')
    lines.insert(i + 4, '        engine_client.all_parts(__file__, extra=(' + ''.join(x + ', ' for x in extra) + '))')
    lines.insert(i + 5, '        return')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))
    print(name, 'extra', extra)

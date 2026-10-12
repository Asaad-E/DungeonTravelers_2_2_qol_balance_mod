import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'mod_project')
from tools.pck_handler import PckArchive, ClassDataHelper

pck = PckArchive('mod_project/backups/ClassData.pck')
print(f"Total entries in ClassData.pck: {len(pck.files)}")
for idx, (fname, b) in enumerate(pck.files):
    data = ClassDataHelper.read_class(b)
    name = data.get('name', '')
    desc = data.get('desc', '')
    code = data.get('code', '')
    if name:
        print(f"\n[{idx:>2}] ({code}) {name} (file: {fname}):")
        for line_no, line in enumerate(desc.splitlines(), 1):
            print(f"   Line {line_no} ({len(line):>2} chars): {line}")
